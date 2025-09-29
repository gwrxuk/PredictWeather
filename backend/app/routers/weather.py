from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import httpx
import os

from ..services.database import get_db
from ..services.blockchain_service import blockchain_service
from ..services.ai_service import ai_service
from ..models.weather import WeatherData, WeatherStation, WeatherAlert, WeatherPrediction
from pydantic import BaseModel

router = APIRouter()

# Pydantic models for request/response
class WeatherDataCreate(BaseModel):
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    temperature: float
    humidity: float
    pressure: float
    wind_speed: float
    wind_direction: Optional[float] = None
    precipitation: float
    visibility: Optional[float] = None
    uv_index: Optional[float] = None
    weather_type: str
    weather_description: Optional[str] = None
    cloud_cover: Optional[float] = None
    data_source: str = "api"

class WeatherStationCreate(BaseModel):
    name: str
    location: str
    latitude: float
    longitude: float
    blockchain_address: str

class WeatherAlertCreate(BaseModel):
    alert_type: str
    severity: str
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    title: str
    description: str
    instructions: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None

@router.get("/current/{location}")
async def get_current_weather(location: str, db: Session = Depends(get_db)):
    """Get current weather for a location"""
    try:
        # First try to get from database (most recent data)
        latest_data = db.query(WeatherData).filter(
            WeatherData.location.ilike(f"%{location}%")
        ).order_by(WeatherData.timestamp.desc()).first()
        
        if latest_data and (datetime.utcnow() - latest_data.timestamp).seconds < 3600:  # Less than 1 hour old
            return {
                "location": latest_data.location,
                "temperature": latest_data.temperature,
                "humidity": latest_data.humidity,
                "pressure": latest_data.pressure,
                "wind_speed": latest_data.wind_speed,
                "wind_direction": latest_data.wind_direction,
                "precipitation": latest_data.precipitation,
                "weather_type": latest_data.weather_type,
                "weather_description": latest_data.weather_description,
                "timestamp": latest_data.timestamp,
                "source": "database"
            }
        
        # If no recent data, fetch from external API
        weather_data = await fetch_external_weather(location)
        
        if weather_data:
            # Store in database
            new_weather = WeatherData(
                location=weather_data["location"],
                latitude=weather_data.get("latitude"),
                longitude=weather_data.get("longitude"),
                temperature=weather_data["temperature"],
                humidity=weather_data["humidity"],
                pressure=weather_data["pressure"],
                wind_speed=weather_data["wind_speed"],
                wind_direction=weather_data.get("wind_direction"),
                precipitation=weather_data["precipitation"],
                weather_type=weather_data["weather_type"],
                weather_description=weather_data.get("weather_description"),
                timestamp=datetime.utcnow(),
                data_source="api"
            )
            
            db.add(new_weather)
            db.commit()
            db.refresh(new_weather)
            
            return weather_data
        
        raise HTTPException(status_code=404, detail="Weather data not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching weather data: {str(e)}")

@router.post("/data")
async def submit_weather_data(
    weather_data: WeatherDataCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Submit weather data to the system"""
    try:
        # Store in database
        new_weather = WeatherData(
            location=weather_data.location,
            latitude=weather_data.latitude,
            longitude=weather_data.longitude,
            temperature=weather_data.temperature,
            humidity=weather_data.humidity,
            pressure=weather_data.pressure,
            wind_speed=weather_data.wind_speed,
            wind_direction=weather_data.wind_direction,
            precipitation=weather_data.precipitation,
            visibility=weather_data.visibility,
            uv_index=weather_data.uv_index,
            weather_type=weather_data.weather_type,
            weather_description=weather_data.weather_description,
            cloud_cover=weather_data.cloud_cover,
            timestamp=datetime.utcnow(),
            data_source=weather_data.data_source
        )
        
        db.add(new_weather)
        db.commit()
        db.refresh(new_weather)
        
        # Submit to blockchain in background
        background_tasks.add_task(
            submit_to_blockchain,
            weather_data.location,
            weather_data.temperature,
            weather_data.humidity,
            weather_data.pressure,
            weather_data.wind_speed,
            weather_data.precipitation,
            weather_data.weather_type
        )
        
        return {
            "message": "Weather data submitted successfully",
            "id": new_weather.id,
            "timestamp": new_weather.timestamp
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting weather data: {str(e)}")

@router.get("/history/{location}")
async def get_weather_history(
    location: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get weather history for a location"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        weather_history = db.query(WeatherData).filter(
            WeatherData.location.ilike(f"%{location}%"),
            WeatherData.timestamp >= start_date
        ).order_by(WeatherData.timestamp.desc()).all()
        
        return {
            "location": location,
            "days": days,
            "total_records": len(weather_history),
            "data": [
                {
                    "id": w.id,
                    "temperature": w.temperature,
                    "humidity": w.humidity,
                    "pressure": w.pressure,
                    "wind_speed": w.wind_speed,
                    "precipitation": w.precipitation,
                    "weather_type": w.weather_type,
                    "timestamp": w.timestamp
                }
                for w in weather_history
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching weather history: {str(e)}")

@router.get("/analysis/{location}")
async def get_weather_analysis(location: str, db: Session = Depends(get_db)):
    """Get AI-powered weather analysis for a location"""
    try:
        # Get recent weather data (last 7 days)
        start_date = datetime.utcnow() - timedelta(days=7)
        weather_data = db.query(WeatherData).filter(
            WeatherData.location.ilike(f"%{location}%"),
            WeatherData.timestamp >= start_date
        ).order_by(WeatherData.timestamp.desc()).all()
        
        if not weather_data:
            raise HTTPException(status_code=404, detail="No weather data found for analysis")
        
        # Convert to list of dictionaries for AI analysis
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
            for w in weather_data
        ]
        
        # Perform AI analysis
        analysis = await ai_service.analyze_weather_patterns(data_list)
        
        return {
            "location": location,
            "analysis_time": datetime.utcnow().isoformat(),
            "data_points": len(data_list),
            "analysis": analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing weather analysis: {str(e)}")

@router.get("/prediction/{location}")
async def get_weather_prediction(location: str, db: Session = Depends(get_db)):
    """Get AI weather prediction for a location"""
    try:
        # Get historical data for prediction
        start_date = datetime.utcnow() - timedelta(days=30)
        historical_data = db.query(WeatherData).filter(
            WeatherData.location.ilike(f"%{location}%"),
            WeatherData.timestamp >= start_date
        ).order_by(WeatherData.timestamp.desc()).all()
        
        if len(historical_data) < 10:
            raise HTTPException(status_code=400, detail="Insufficient historical data for prediction")
        
        # Convert to list for AI service
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
        
        # Store prediction in database
        new_prediction = WeatherPrediction(
            location=location,
            prediction_date=datetime.utcnow(),
            forecast_hours=24,
            predicted_temperature=prediction.get("predictions", {}).get("temperature", {}).get("value"),
            predicted_humidity=prediction.get("predictions", {}).get("humidity", {}).get("value"),
            predicted_pressure=prediction.get("predictions", {}).get("pressure", {}).get("value"),
            predicted_wind_speed=prediction.get("predictions", {}).get("wind_speed", {}).get("value"),
            predicted_precipitation=prediction.get("predictions", {}).get("precipitation", {}).get("value"),
            flood_risk=prediction.get("risk_assessment", {}).get("flood_risk", 0.0),
            drought_risk=prediction.get("risk_assessment", {}).get("drought_risk", 0.0),
            storm_risk=prediction.get("risk_assessment", {}).get("storm_risk", 0.0),
            extreme_temp_risk=prediction.get("risk_assessment", {}).get("extreme_temperature_risk", 0.0),
            model_name="WeatherGuard AI",
            model_version=prediction.get("model_version", "v1.0"),
            confidence_score=prediction.get("confidence", 0.75)
        )
        
        db.add(new_prediction)
        db.commit()
        db.refresh(new_prediction)
        
        return prediction
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating weather prediction: {str(e)}")

@router.get("/alerts")
async def get_active_alerts(location: Optional[str] = None, db: Session = Depends(get_db)):
    """Get active weather alerts"""
    try:
        query = db.query(WeatherAlert).filter(
            WeatherAlert.is_active == True,
            WeatherAlert.end_time > datetime.utcnow()
        )
        
        if location:
            query = query.filter(WeatherAlert.location.ilike(f"%{location}%"))
        
        alerts = query.order_by(WeatherAlert.severity.desc(), WeatherAlert.start_time.desc()).all()
        
        return {
            "total_alerts": len(alerts),
            "alerts": [
                {
                    "id": alert.id,
                    "type": alert.alert_type,
                    "severity": alert.severity,
                    "location": alert.location,
                    "title": alert.title,
                    "description": alert.description,
                    "instructions": alert.instructions,
                    "start_time": alert.start_time,
                    "end_time": alert.end_time
                }
                for alert in alerts
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching alerts: {str(e)}")

@router.post("/alerts")
async def create_weather_alert(alert_data: WeatherAlertCreate, db: Session = Depends(get_db)):
    """Create a new weather alert"""
    try:
        new_alert = WeatherAlert(
            alert_type=alert_data.alert_type,
            severity=alert_data.severity,
            location=alert_data.location,
            latitude=alert_data.latitude,
            longitude=alert_data.longitude,
            title=alert_data.title,
            description=alert_data.description,
            instructions=alert_data.instructions,
            start_time=alert_data.start_time,
            end_time=alert_data.end_time,
            is_active=True
        )
        
        db.add(new_alert)
        db.commit()
        db.refresh(new_alert)
        
        return {
            "message": "Weather alert created successfully",
            "alert_id": new_alert.id,
            "alert": {
                "type": new_alert.alert_type,
                "severity": new_alert.severity,
                "location": new_alert.location,
                "title": new_alert.title
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating weather alert: {str(e)}")

@router.post("/stations")
async def register_weather_station(station_data: WeatherStationCreate, db: Session = Depends(get_db)):
    """Register a new weather station"""
    try:
        # Check if station already exists
        existing_station = db.query(WeatherStation).filter(
            WeatherStation.blockchain_address == station_data.blockchain_address
        ).first()
        
        if existing_station:
            raise HTTPException(status_code=400, detail="Weather station already registered")
        
        new_station = WeatherStation(
            name=station_data.name,
            location=station_data.location,
            latitude=station_data.latitude,
            longitude=station_data.longitude,
            blockchain_address=station_data.blockchain_address,
            is_active=True
        )
        
        db.add(new_station)
        db.commit()
        db.refresh(new_station)
        
        return {
            "message": "Weather station registered successfully",
            "station_id": new_station.id,
            "station": {
                "name": new_station.name,
                "location": new_station.location,
                "blockchain_address": new_station.blockchain_address
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registering weather station: {str(e)}")

@router.get("/stations")
async def get_weather_stations(db: Session = Depends(get_db)):
    """Get all registered weather stations"""
    try:
        stations = db.query(WeatherStation).filter(WeatherStation.is_active == True).all()
        
        return {
            "total_stations": len(stations),
            "stations": [
                {
                    "id": station.id,
                    "name": station.name,
                    "location": station.location,
                    "latitude": station.latitude,
                    "longitude": station.longitude,
                    "reputation_score": station.reputation_score,
                    "total_reports": station.total_reports,
                    "created_at": station.created_at
                }
                for station in stations
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching weather stations: {str(e)}")

# Helper functions
async def fetch_external_weather(location: str) -> Optional[Dict[str, Any]]:
    """Fetch weather data from external API (OpenWeatherMap)"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return None
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://api.openweathermap.org/data/2.5/weather",
                params={
                    "q": location,
                    "appid": api_key,
                    "units": "metric"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    "location": f"{data['name']}, {data['sys']['country']}",
                    "latitude": data["coord"]["lat"],
                    "longitude": data["coord"]["lon"],
                    "temperature": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"]["pressure"],
                    "wind_speed": data.get("wind", {}).get("speed", 0) * 3.6,  # Convert m/s to km/h
                    "wind_direction": data.get("wind", {}).get("deg"),
                    "precipitation": data.get("rain", {}).get("1h", 0) + data.get("snow", {}).get("1h", 0),
                    "weather_type": data["weather"][0]["main"].lower(),
                    "weather_description": data["weather"][0]["description"],
                    "cloud_cover": data.get("clouds", {}).get("all", 0),
                    "visibility": data.get("visibility", 0) / 1000,  # Convert m to km
                    "source": "openweathermap"
                }
    except Exception as e:
        print(f"Error fetching external weather data: {e}")
        return None

async def submit_to_blockchain(location: str, temperature: float, humidity: float,
                             pressure: float, wind_speed: float, precipitation: float,
                             weather_type: str):
    """Submit weather data to blockchain"""
    try:
        if blockchain_service.is_connected():
            tx_hash = blockchain_service.submit_weather_data(
                location, temperature, humidity, pressure,
                wind_speed, precipitation, weather_type
            )
            if tx_hash:
                print(f"Weather data submitted to blockchain: {tx_hash}")
            else:
                print("Failed to submit weather data to blockchain")
        else:
            print("Blockchain not connected, skipping submission")
    except Exception as e:
        print(f"Error submitting to blockchain: {e}")
