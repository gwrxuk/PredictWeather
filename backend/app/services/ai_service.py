import openai
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv
import httpx
from transformers import pipeline
import torch

load_dotenv()

class AIWeatherService:
    def __init__(self):
        # Initialize OpenAI
        self.openai_client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize Hugging Face models
        self.sentiment_analyzer = None
        self.text_generator = None
        self._load_hf_models()
        
        # Weather prediction model parameters
        self.prediction_models = {}
        self._initialize_prediction_models()
    
    def _load_hf_models(self):
        """Load Hugging Face models"""
        try:
            # Sentiment analysis for social media weather reports
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            # Text generation for alerts and reports
            self.text_generator = pipeline(
                "text-generation",
                model="microsoft/DialoGPT-medium"
            )
        except Exception as e:
            print(f"Warning: Could not load HuggingFace models: {e}")
    
    def _initialize_prediction_models(self):
        """Initialize weather prediction models"""
        # Simple ML models for different weather events
        self.prediction_models = {
            "flood": {
                "threshold_precipitation": 50.0,  # mm in 24h
                "threshold_river_level": 5.0,    # meters
                "soil_saturation_factor": 0.8
            },
            "drought": {
                "threshold_precipitation": 5.0,   # mm in 30 days
                "threshold_temperature": 35.0,   # Celsius
                "humidity_threshold": 30.0       # percentage
            },
            "storm": {
                "threshold_wind_speed": 60.0,    # km/h
                "threshold_pressure_drop": 20.0, # hPa in 3h
                "temperature_gradient": 10.0     # Celsius change
            },
            "extreme_temperature": {
                "heat_threshold": 40.0,          # Celsius
                "cold_threshold": -20.0,         # Celsius
                "duration_hours": 6              # consecutive hours
            }
        }
    
    async def analyze_weather_patterns(self, weather_data: List[Dict]) -> Dict[str, Any]:
        """Analyze weather patterns using AI"""
        if not weather_data:
            return {"error": "No weather data provided"}
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(weather_data)
        
        # Basic statistical analysis
        analysis = {
            "summary": {
                "total_records": len(df),
                "date_range": {
                    "start": df['timestamp'].min() if 'timestamp' in df.columns else None,
                    "end": df['timestamp'].max() if 'timestamp' in df.columns else None
                },
                "locations": df['location'].unique().tolist() if 'location' in df.columns else []
            },
            "statistics": {},
            "trends": {},
            "anomalies": [],
            "risk_assessment": {}
        }
        
        # Calculate statistics for numerical columns
        numerical_columns = ['temperature', 'humidity', 'pressure', 'wind_speed', 'precipitation']
        for col in numerical_columns:
            if col in df.columns:
                analysis["statistics"][col] = {
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "std": float(df[col].std()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max())
                }
        
        # Trend analysis
        analysis["trends"] = await self._analyze_trends(df)
        
        # Anomaly detection
        analysis["anomalies"] = await self._detect_anomalies(df)
        
        # Risk assessment
        analysis["risk_assessment"] = await self._assess_risks(df)
        
        return analysis
    
    async def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze weather trends"""
        trends = {}
        
        if 'timestamp' in df.columns and len(df) > 1:
            # Sort by timestamp
            df_sorted = df.sort_values('timestamp')
            
            # Temperature trend
            if 'temperature' in df.columns:
                temp_trend = np.polyfit(range(len(df_sorted)), df_sorted['temperature'], 1)[0]
                trends["temperature"] = {
                    "direction": "increasing" if temp_trend > 0 else "decreasing",
                    "rate": float(temp_trend),
                    "significance": "high" if abs(temp_trend) > 0.5 else "low"
                }
            
            # Precipitation trend
            if 'precipitation' in df.columns:
                precip_trend = np.polyfit(range(len(df_sorted)), df_sorted['precipitation'], 1)[0]
                trends["precipitation"] = {
                    "direction": "increasing" if precip_trend > 0 else "decreasing",
                    "rate": float(precip_trend),
                    "significance": "high" if abs(precip_trend) > 1.0 else "low"
                }
        
        return trends
    
    async def _detect_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect weather anomalies"""
        anomalies = []
        
        numerical_columns = ['temperature', 'humidity', 'pressure', 'wind_speed', 'precipitation']
        
        for col in numerical_columns:
            if col in df.columns:
                # Use IQR method for anomaly detection
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Find anomalies
                anomaly_indices = df[(df[col] < lower_bound) | (df[col] > upper_bound)].index
                
                for idx in anomaly_indices:
                    anomalies.append({
                        "type": f"{col}_anomaly",
                        "value": float(df.loc[idx, col]),
                        "expected_range": [float(lower_bound), float(upper_bound)],
                        "severity": "high" if (df.loc[idx, col] < lower_bound - IQR) or (df.loc[idx, col] > upper_bound + IQR) else "medium",
                        "timestamp": df.loc[idx, 'timestamp'] if 'timestamp' in df.columns else None,
                        "location": df.loc[idx, 'location'] if 'location' in df.columns else None
                    })
        
        return anomalies
    
    async def _assess_risks(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess weather-related risks"""
        risks = {
            "flood_risk": 0.0,
            "drought_risk": 0.0,
            "storm_risk": 0.0,
            "extreme_temperature_risk": 0.0
        }
        
        if len(df) == 0:
            return risks
        
        # Flood risk assessment
        if 'precipitation' in df.columns:
            recent_precip = df['precipitation'].tail(24).sum()  # Last 24 hours
            flood_threshold = self.prediction_models["flood"]["threshold_precipitation"]
            risks["flood_risk"] = min(1.0, recent_precip / flood_threshold)
        
        # Drought risk assessment
        if 'precipitation' in df.columns and 'temperature' in df.columns:
            avg_precip = df['precipitation'].tail(720).mean()  # Last 30 days (24*30)
            avg_temp = df['temperature'].tail(720).mean()
            drought_precip_threshold = self.prediction_models["drought"]["threshold_precipitation"]
            drought_temp_threshold = self.prediction_models["drought"]["threshold_temperature"]
            
            precip_risk = 1.0 - min(1.0, avg_precip / drought_precip_threshold)
            temp_risk = min(1.0, max(0.0, avg_temp - 25.0) / (drought_temp_threshold - 25.0))
            risks["drought_risk"] = (precip_risk + temp_risk) / 2
        
        # Storm risk assessment
        if 'wind_speed' in df.columns and 'pressure' in df.columns:
            max_wind = df['wind_speed'].tail(6).max()  # Last 6 hours
            pressure_drop = df['pressure'].tail(3).iloc[0] - df['pressure'].tail(3).iloc[-1]
            
            wind_risk = min(1.0, max_wind / self.prediction_models["storm"]["threshold_wind_speed"])
            pressure_risk = min(1.0, max(0.0, pressure_drop) / self.prediction_models["storm"]["threshold_pressure_drop"])
            risks["storm_risk"] = max(wind_risk, pressure_risk)
        
        # Extreme temperature risk
        if 'temperature' in df.columns:
            recent_temps = df['temperature'].tail(6)  # Last 6 hours
            heat_threshold = self.prediction_models["extreme_temperature"]["heat_threshold"]
            cold_threshold = self.prediction_models["extreme_temperature"]["cold_threshold"]
            
            heat_risk = (recent_temps > heat_threshold).sum() / len(recent_temps)
            cold_risk = (recent_temps < cold_threshold).sum() / len(recent_temps)
            risks["extreme_temperature_risk"] = max(heat_risk, cold_risk)
        
        return risks
    
    async def generate_weather_prediction(self, location: str, historical_data: List[Dict]) -> Dict[str, Any]:
        """Generate weather predictions using AI"""
        if not historical_data:
            return {"error": "No historical data provided"}
        
        # Prepare data for prediction
        df = pd.DataFrame(historical_data)
        
        # Simple prediction model (in production, use more sophisticated ML models)
        prediction = {
            "location": location,
            "prediction_time": datetime.utcnow().isoformat(),
            "forecast_hours": 24,
            "predictions": {},
            "confidence": 0.75,
            "model_version": "v1.0"
        }
        
        # Predict weather parameters
        if len(df) >= 3:
            # Use simple moving average with trend
            for param in ['temperature', 'humidity', 'pressure', 'wind_speed', 'precipitation']:
                if param in df.columns:
                    recent_values = df[param].tail(3).values
                    trend = (recent_values[-1] - recent_values[0]) / len(recent_values)
                    predicted_value = recent_values[-1] + trend
                    
                    prediction["predictions"][param] = {
                        "value": float(predicted_value),
                        "trend": "increasing" if trend > 0 else "decreasing",
                        "confidence": 0.7 + 0.2 * (1 - abs(trend) / (np.std(recent_values) + 1e-6))
                    }
        
        # Risk predictions
        risk_assessment = await self._assess_risks(df)
        prediction["risk_assessment"] = risk_assessment
        
        return prediction
    
    async def generate_weather_alert(self, alert_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate weather alert using LLM"""
        try:
            # Prepare prompt for GPT
            prompt = f"""
            Generate a weather alert based on the following data:
            
            Alert Type: {alert_data.get('alert_type', 'Unknown')}
            Severity: {alert_data.get('severity', 'Medium')}
            Location: {alert_data.get('location', 'Unknown')}
            Weather Conditions: {json.dumps(alert_data.get('conditions', {}), indent=2)}
            Risk Level: {alert_data.get('risk_level', 0.5)}
            
            Please generate:
            1. A clear, concise title for the alert
            2. A detailed description of the weather threat
            3. Specific safety instructions for the public
            4. Estimated duration and timeline
            
            Keep the language clear, urgent but not panic-inducing, and actionable.
            """
            
            response = await self.openai_client.chat.completions.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional meteorologist and emergency management expert. Generate clear, accurate weather alerts."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            alert_text = response.choices[0].message.content
            
            # Parse the response into structured format
            lines = alert_text.strip().split('\n')
            
            result = {
                "title": "Weather Alert",
                "description": alert_text,
                "instructions": "Follow local emergency guidelines.",
                "duration": "Monitor conditions closely."
            }
            
            # Try to extract structured information
            for i, line in enumerate(lines):
                if "title" in line.lower() or i == 0:
                    result["title"] = line.strip().replace("Title:", "").replace("1.", "").strip()
                elif "description" in line.lower() or "threat" in line.lower():
                    result["description"] = line.strip().replace("Description:", "").replace("2.", "").strip()
                elif "instruction" in line.lower() or "safety" in line.lower():
                    result["instructions"] = line.strip().replace("Instructions:", "").replace("3.", "").strip()
                elif "duration" in line.lower() or "timeline" in line.lower():
                    result["duration"] = line.strip().replace("Duration:", "").replace("4.", "").strip()
            
            return result
            
        except Exception as e:
            print(f"Error generating alert with OpenAI: {e}")
            
            # Fallback to template-based alert
            return self._generate_template_alert(alert_data)
    
    def _generate_template_alert(self, alert_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate alert using templates as fallback"""
        alert_type = alert_data.get('alert_type', 'weather').lower()
        severity = alert_data.get('severity', 'medium').lower()
        location = alert_data.get('location', 'the area')
        
        templates = {
            "flood": {
                "title": f"Flood {severity.title()} Alert for {location}",
                "description": f"Heavy rainfall and rising water levels pose a flood risk in {location}. Monitor local conditions and be prepared to evacuate if necessary.",
                "instructions": "Move to higher ground, avoid flooded roads, and stay informed through official channels.",
                "duration": "Alert remains in effect until water levels recede."
            },
            "drought": {
                "title": f"Drought {severity.title()} Alert for {location}",
                "description": f"Extended dry conditions and high temperatures are creating drought conditions in {location}. Water conservation measures are recommended.",
                "instructions": "Conserve water, avoid outdoor burning, and monitor local water restrictions.",
                "duration": "Alert continues until significant precipitation occurs."
            },
            "storm": {
                "title": f"Severe Storm {severity.title()} Alert for {location}",
                "description": f"Dangerous weather conditions including high winds and heavy precipitation are expected in {location}.",
                "instructions": "Secure outdoor objects, avoid travel if possible, and stay indoors during the storm.",
                "duration": "Storm conditions expected for the next 6-12 hours."
            }
        }
        
        return templates.get(alert_type, templates["storm"])
    
    async def analyze_social_sentiment(self, social_posts: List[str]) -> Dict[str, Any]:
        """Analyze social media sentiment about weather conditions"""
        if not self.sentiment_analyzer or not social_posts:
            return {"error": "Sentiment analyzer not available or no posts provided"}
        
        try:
            # Analyze sentiment for each post
            sentiments = []
            for post in social_posts:
                result = self.sentiment_analyzer(post[:512])  # Limit text length
                sentiments.append(result[0])
            
            # Aggregate results
            positive_count = sum(1 for s in sentiments if s['label'] == 'POSITIVE')
            negative_count = sum(1 for s in sentiments if s['label'] == 'NEGATIVE')
            neutral_count = len(sentiments) - positive_count - negative_count
            
            avg_confidence = sum(s['score'] for s in sentiments) / len(sentiments)
            
            return {
                "total_posts": len(social_posts),
                "sentiment_distribution": {
                    "positive": positive_count,
                    "negative": negative_count,
                    "neutral": neutral_count
                },
                "average_confidence": avg_confidence,
                "overall_sentiment": "positive" if positive_count > negative_count else "negative" if negative_count > positive_count else "neutral"
            }
            
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {"error": str(e)}

# Global AI service instance
ai_service = AIWeatherService()
