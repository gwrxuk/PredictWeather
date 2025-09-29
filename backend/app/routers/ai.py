from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel

from ..services.ai_service import ai_service

router = APIRouter()

class WeatherAnalysisRequest(BaseModel):
    weather_data: List[Dict[str, Any]]

class PredictionRequest(BaseModel):
    location: str
    historical_data: List[Dict[str, Any]]

class AlertGenerationRequest(BaseModel):
    alert_type: str
    severity: str
    location: str
    conditions: Dict[str, Any]
    risk_level: float

class SentimentAnalysisRequest(BaseModel):
    social_posts: List[str]

@router.post("/analyze/patterns")
async def analyze_weather_patterns(request: WeatherAnalysisRequest):
    """Analyze weather patterns using AI"""
    try:
        analysis = await ai_service.analyze_weather_patterns(request.weather_data)
        return {
            "success": True,
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing weather patterns: {str(e)}")

@router.post("/predict/weather")
async def predict_weather(request: PredictionRequest):
    """Generate weather predictions using AI"""
    try:
        prediction = await ai_service.generate_weather_prediction(
            request.location, 
            request.historical_data
        )
        return {
            "success": True,
            "prediction": prediction
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating weather prediction: {str(e)}")

@router.post("/generate/alert")
async def generate_weather_alert(request: AlertGenerationRequest):
    """Generate weather alert using LLM"""
    try:
        alert = await ai_service.generate_weather_alert({
            "alert_type": request.alert_type,
            "severity": request.severity,
            "location": request.location,
            "conditions": request.conditions,
            "risk_level": request.risk_level
        })
        return {
            "success": True,
            "alert": alert
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating weather alert: {str(e)}")

@router.post("/analyze/sentiment")
async def analyze_social_sentiment(request: SentimentAnalysisRequest):
    """Analyze social media sentiment about weather"""
    try:
        sentiment = await ai_service.analyze_social_sentiment(request.social_posts)
        return {
            "success": True,
            "sentiment_analysis": sentiment
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing sentiment: {str(e)}")

@router.get("/models/status")
async def get_ai_models_status():
    """Get status of AI models"""
    return {
        "models": {
            "weather_prediction": "operational",
            "pattern_analysis": "operational", 
            "alert_generation": "operational",
            "sentiment_analysis": "operational" if ai_service.sentiment_analyzer else "unavailable"
        },
        "capabilities": {
            "flood_prediction": True,
            "drought_assessment": True,
            "storm_tracking": True,
            "temperature_extremes": True,
            "natural_language_alerts": True,
            "social_media_monitoring": bool(ai_service.sentiment_analyzer)
        }
    }
