import schedule
import time
import threading
import asyncio
from datetime import datetime
import httpx
import os
from dotenv import load_dotenv

from .database import get_db
from .blockchain_service import blockchain_service
from .ai_service import ai_service
from ..models.weather import WeatherData, WeatherAlert

load_dotenv()

class WeatherScheduler:
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the scheduler in a separate thread"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_scheduler)
            self.thread.daemon = True
            self.thread.start()
            print("Weather scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("Weather scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        # Schedule tasks
        schedule.every(5).minutes.do(self._collect_weather_data)
        schedule.every(15).minutes.do(self._analyze_weather_patterns)
        schedule.every(30).minutes.do(self._generate_predictions)
        schedule.every(1).hours.do(self._check_alert_conditions)
        schedule.every(6).hours.do(self._sync_blockchain_data)
        
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _collect_weather_data(self):
        """Collect weather data from external APIs"""
        try:
            print(f"[{datetime.now()}] Collecting weather data...")
            
            # List of major cities to monitor
            cities = [
                "New York,US", "Los Angeles,US", "Chicago,US", "Houston,US",
                "Miami,US", "Seattle,US", "Denver,US", "Atlanta,US"
            ]
            
            asyncio.run(self._fetch_weather_for_cities(cities))
            
        except Exception as e:
            print(f"Error collecting weather data: {e}")
    
    async def _fetch_weather_for_cities(self, cities):
        """Fetch weather data for multiple cities"""
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            print("OpenWeather API key not configured")
            return
        
        async with httpx.AsyncClient() as client:
            for city in cities:
                try:
                    response = await client.get(
                        "http://api.openweathermap.org/data/2.5/weather",
                        params={"q": city, "appid": api_key, "units": "metric"}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        await self._store_weather_data(data)
                        
                except Exception as e:
                    print(f"Error fetching weather for {city}: {e}")
    
    async def _store_weather_data(self, api_data):
        """Store weather data in database"""
        try:
            db = next(get_db())
            
            weather_data = WeatherData(
                location=f"{api_data['name']}, {api_data['sys']['country']}",
                latitude=api_data["coord"]["lat"],
                longitude=api_data["coord"]["lon"],
                temperature=api_data["main"]["temp"],
                humidity=api_data["main"]["humidity"],
                pressure=api_data["main"]["pressure"],
                wind_speed=api_data.get("wind", {}).get("speed", 0) * 3.6,
                wind_direction=api_data.get("wind", {}).get("deg"),
                precipitation=api_data.get("rain", {}).get("1h", 0) + api_data.get("snow", {}).get("1h", 0),
                weather_type=api_data["weather"][0]["main"].lower(),
                weather_description=api_data["weather"][0]["description"],
                cloud_cover=api_data.get("clouds", {}).get("all", 0),
                visibility=api_data.get("visibility", 0) / 1000,
                timestamp=datetime.utcnow(),
                data_source="scheduler_api"
            )
            
            db.add(weather_data)
            db.commit()
            
            # Submit to blockchain if connected
            if blockchain_service.is_connected():
                blockchain_service.submit_weather_data(
                    weather_data.location,
                    weather_data.temperature,
                    weather_data.humidity,
                    weather_data.pressure,
                    weather_data.wind_speed,
                    weather_data.precipitation,
                    weather_data.weather_type
                )
            
            db.close()
            
        except Exception as e:
            print(f"Error storing weather data: {e}")
    
    def _analyze_weather_patterns(self):
        """Analyze weather patterns for anomalies"""
        try:
            print(f"[{datetime.now()}] Analyzing weather patterns...")
            
            asyncio.run(self._perform_pattern_analysis())
            
        except Exception as e:
            print(f"Error analyzing weather patterns: {e}")
    
    async def _perform_pattern_analysis(self):
        """Perform AI-based pattern analysis"""
        try:
            db = next(get_db())
            
            # Get recent weather data (last 24 hours)
            from datetime import timedelta
            start_time = datetime.utcnow() - timedelta(hours=24)
            
            recent_data = db.query(WeatherData).filter(
                WeatherData.timestamp >= start_time
            ).all()
            
            if len(recent_data) > 10:
                # Convert to format for AI analysis
                data_list = [
                    {
                        "location": w.location,
                        "temperature": w.temperature,
                        "humidity": w.humidity,
                        "pressure": w.pressure,
                        "wind_speed": w.wind_speed,
                        "precipitation": w.precipitation,
                        "weather_type": w.weather_type,
                        "timestamp": w.timestamp.isoformat()
                    }
                    for w in recent_data
                ]
                
                # Perform AI analysis
                analysis = await ai_service.analyze_weather_patterns(data_list)
                
                # Check for high-risk conditions
                risk_assessment = analysis.get("risk_assessment", {})
                await self._check_risk_thresholds(risk_assessment, db)
            
            db.close()
            
        except Exception as e:
            print(f"Error in pattern analysis: {e}")
    
    async def _check_risk_thresholds(self, risk_assessment, db):
        """Check if risk thresholds are exceeded and create alerts"""
        try:
            high_risk_threshold = 0.7
            
            for risk_type, risk_value in risk_assessment.items():
                if risk_value > high_risk_threshold:
                    # Create alert
                    alert_data = {
                        "alert_type": risk_type.replace("_risk", ""),
                        "severity": "high" if risk_value > 0.8 else "medium",
                        "location": "Multiple Areas",
                        "conditions": {"risk_score": risk_value},
                        "risk_level": risk_value
                    }
                    
                    alert_content = await ai_service.generate_weather_alert(alert_data)
                    
                    # Store alert in database
                    new_alert = WeatherAlert(
                        alert_type=alert_data["alert_type"],
                        severity=alert_data["severity"],
                        location=alert_data["location"],
                        title=alert_content.get("title", f"{alert_data['alert_type'].title()} Alert"),
                        description=alert_content.get("description", "High risk conditions detected"),
                        instructions=alert_content.get("instructions", "Monitor conditions closely"),
                        start_time=datetime.utcnow(),
                        is_active=True,
                        ai_confidence=risk_value
                    )
                    
                    db.add(new_alert)
                    db.commit()
                    
                    print(f"Created {alert_data['alert_type']} alert with risk score {risk_value}")
        
        except Exception as e:
            print(f"Error checking risk thresholds: {e}")
    
    def _generate_predictions(self):
        """Generate weather predictions"""
        try:
            print(f"[{datetime.now()}] Generating weather predictions...")
            
            asyncio.run(self._create_predictions())
            
        except Exception as e:
            print(f"Error generating predictions: {e}")
    
    async def _create_predictions(self):
        """Create AI-based weather predictions"""
        try:
            db = next(get_db())
            
            # Get unique locations from recent data
            from datetime import timedelta
            start_time = datetime.utcnow() - timedelta(days=7)
            
            locations = db.query(WeatherData.location).filter(
                WeatherData.timestamp >= start_time
            ).distinct().all()
            
            for (location,) in locations[:5]:  # Limit to 5 locations per run
                # Get historical data for this location
                historical_data = db.query(WeatherData).filter(
                    WeatherData.location == location,
                    WeatherData.timestamp >= start_time
                ).order_by(WeatherData.timestamp.desc()).limit(100).all()
                
                if len(historical_data) >= 10:
                    data_list = [
                        {
                            "location": w.location,
                            "temperature": w.temperature,
                            "humidity": w.humidity,
                            "pressure": w.pressure,
                            "wind_speed": w.wind_speed,
                            "precipitation": w.precipitation,
                            "weather_type": w.weather_type,
                            "timestamp": w.timestamp.isoformat()
                        }
                        for w in historical_data
                    ]
                    
                    # Generate prediction
                    prediction = await ai_service.generate_weather_prediction(location, data_list)
                    
                    # Store prediction (implementation would go here)
                    print(f"Generated prediction for {location}")
            
            db.close()
            
        except Exception as e:
            print(f"Error creating predictions: {e}")
    
    def _check_alert_conditions(self):
        """Check for alert conditions"""
        try:
            print(f"[{datetime.now()}] Checking alert conditions...")
            
            # Implementation for checking various alert conditions
            # This would integrate with emergency management systems
            
        except Exception as e:
            print(f"Error checking alert conditions: {e}")
    
    def _sync_blockchain_data(self):
        """Sync data with blockchain"""
        try:
            print(f"[{datetime.now()}] Syncing blockchain data...")
            
            if blockchain_service.is_connected():
                # Get recent blockchain data
                recent_data_ids = blockchain_service.get_recent_weather_data()
                print(f"Found {len(recent_data_ids)} recent blockchain entries")
            
        except Exception as e:
            print(f"Error syncing blockchain data: {e}")

# Global scheduler instance
weather_scheduler = WeatherScheduler()

def start_scheduler():
    """Start the weather data collection scheduler"""
    weather_scheduler.start()

def stop_scheduler():
    """Stop the weather data collection scheduler"""
    weather_scheduler.stop()
