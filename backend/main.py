from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import os
from dotenv import load_dotenv

from app.routers import weather, blockchain, ai, emergency, insurance
from app.services.database import engine, Base
from app.services.scheduler import start_scheduler
from app.services.websocket_manager import websocket_manager

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="WeatherGuard API",
    description="Blockchain-powered extreme weather protection system API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(weather.router, prefix="/api/v1/weather", tags=["Weather"])
app.include_router(blockchain.router, prefix="/api/v1/blockchain", tags=["Blockchain"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI & Predictions"])
app.include_router(emergency.router, prefix="/api/v1/emergency", tags=["Emergency"])
app.include_router(insurance.router, prefix="/api/v1/insurance", tags=["Insurance"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 Starting WeatherGuard API...")
    
    # Start background scheduler for weather data collection
    start_scheduler()
    
    # Initialize WebSocket manager
    await websocket_manager.start()
    
    print("✅ WeatherGuard API started successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Shutting down WeatherGuard API...")
    await websocket_manager.stop()
    print("✅ WeatherGuard API shutdown complete!")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "WeatherGuard API",
        "version": "1.0.0",
        "description": "Blockchain-powered extreme weather protection system",
        "docs": "/docs",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {
            "database": "connected",
            "blockchain": "connected",
            "ai_service": "operational",
            "weather_apis": "operational"
        }
    }

@app.get("/api/v1/status")
async def api_status():
    """Detailed API status"""
    return {
        "api_version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "features": {
            "weather_monitoring": True,
            "ai_predictions": True,
            "blockchain_integration": True,
            "emergency_response": True,
            "parametric_insurance": True
        },
        "endpoints": {
            "weather": "/api/v1/weather",
            "blockchain": "/api/v1/blockchain", 
            "ai": "/api/v1/ai",
            "emergency": "/api/v1/emergency",
            "insurance": "/api/v1/insurance"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
