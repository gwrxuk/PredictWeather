from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class WeatherStation(Base):
    __tablename__ = "weather_stations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    blockchain_address = Column(String(42), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    reputation_score = Column(Integer, default=100)
    total_reports = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    weather_data = relationship("WeatherData", back_populates="station")

class WeatherData(Base):
    __tablename__ = "weather_data"
    
    id = Column(Integer, primary_key=True, index=True)
    blockchain_id = Column(Integer, unique=True, nullable=True)  # ID from blockchain
    station_id = Column(Integer, ForeignKey("weather_stations.id"), nullable=False)
    location = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Weather measurements
    temperature = Column(Float, nullable=False)  # Celsius
    humidity = Column(Float, nullable=False)     # Percentage
    pressure = Column(Float, nullable=False)     # hPa
    wind_speed = Column(Float, nullable=False)   # km/h
    wind_direction = Column(Float, nullable=True) # Degrees
    precipitation = Column(Float, nullable=False) # mm
    visibility = Column(Float, nullable=True)     # km
    uv_index = Column(Float, nullable=True)
    
    # Weather conditions
    weather_type = Column(String(50), nullable=False)
    weather_description = Column(String(255), nullable=True)
    cloud_cover = Column(Float, nullable=True)   # Percentage
    
    # Metadata
    timestamp = Column(DateTime, nullable=False)
    data_source = Column(String(50), nullable=False)  # 'api', 'iot', 'manual'
    is_verified = Column(Boolean, default=False)
    verification_count = Column(Integer, default=0)
    ipfs_hash = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    station = relationship("WeatherStation", back_populates="weather_data")
    predictions = relationship("WeatherPrediction", back_populates="source_data")

class WeatherAlert(Base):
    __tablename__ = "weather_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False)  # 'flood', 'drought', 'storm', etc.
    severity = Column(String(20), nullable=False)    # 'low', 'medium', 'high', 'critical'
    location = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    instructions = Column(Text, nullable=True)
    
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # AI-generated content
    ai_confidence = Column(Float, nullable=True)  # 0-1 confidence score
    ai_model_version = Column(String(50), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WeatherPrediction(Base):
    __tablename__ = "weather_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    source_data_id = Column(Integer, ForeignKey("weather_data.id"), nullable=True)
    location = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Prediction timeframe
    prediction_date = Column(DateTime, nullable=False)
    forecast_hours = Column(Integer, nullable=False)  # Hours into the future
    
    # Predicted weather
    predicted_temperature = Column(Float, nullable=True)
    predicted_humidity = Column(Float, nullable=True)
    predicted_pressure = Column(Float, nullable=True)
    predicted_wind_speed = Column(Float, nullable=True)
    predicted_precipitation = Column(Float, nullable=True)
    predicted_weather_type = Column(String(50), nullable=True)
    
    # Risk assessments
    flood_risk = Column(Float, nullable=True)      # 0-1 probability
    drought_risk = Column(Float, nullable=True)    # 0-1 probability
    storm_risk = Column(Float, nullable=True)      # 0-1 probability
    extreme_temp_risk = Column(Float, nullable=True) # 0-1 probability
    
    # AI model information
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    confidence_score = Column(Float, nullable=False)  # 0-1
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    source_data = relationship("WeatherData", back_populates="predictions")

class HistoricalWeatherEvent(Base):
    __tablename__ = "historical_weather_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False)
    event_name = Column(String(255), nullable=True)
    location = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    
    # Impact metrics
    severity_score = Column(Float, nullable=True)    # 1-10 scale
    affected_population = Column(Integer, nullable=True)
    economic_damage = Column(Float, nullable=True)   # USD
    casualties = Column(Integer, nullable=True)
    
    # Weather data during event
    max_wind_speed = Column(Float, nullable=True)
    total_precipitation = Column(Float, nullable=True)
    min_temperature = Column(Float, nullable=True)
    max_temperature = Column(Float, nullable=True)
    
    description = Column(Text, nullable=True)
    data_sources = Column(Text, nullable=True)  # JSON array of sources
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
