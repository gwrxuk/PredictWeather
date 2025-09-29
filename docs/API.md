# WeatherGuard API Documentation

## Base URL
- Development: `http://localhost:8000/api/v1`
- Production: `https://your-domain.com/api/v1`

## Authentication
Most endpoints require API authentication. Include your API key in the header:
```
Authorization: Bearer your_api_key
```

## Weather Endpoints

### Get Current Weather
```http
GET /weather/current/{location}
```

**Parameters:**
- `location` (string): Location name (e.g., "New York, NY")

**Response:**
```json
{
  "location": "New York, NY",
  "temperature": 22.5,
  "humidity": 65,
  "pressure": 1013.25,
  "wind_speed": 15.2,
  "wind_direction": 180,
  "precipitation": 0.0,
  "weather_type": "sunny",
  "weather_description": "Clear sky",
  "timestamp": "2024-01-01T12:00:00Z",
  "source": "api"
}
```

### Submit Weather Data
```http
POST /weather/data
```

**Request Body:**
```json
{
  "location": "New York, NY",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "temperature": 22.5,
  "humidity": 65,
  "pressure": 1013.25,
  "wind_speed": 15.2,
  "precipitation": 0.0,
  "weather_type": "sunny",
  "data_source": "iot"
}
```

### Get Weather History
```http
GET /weather/history/{location}?days=7
```

**Parameters:**
- `location` (string): Location name
- `days` (integer, optional): Number of days (default: 7)

### Get Weather Analysis
```http
GET /weather/analysis/{location}
```

**Response:**
```json
{
  "location": "New York, NY",
  "analysis_time": "2024-01-01T12:00:00Z",
  "data_points": 168,
  "analysis": {
    "summary": {
      "total_records": 168,
      "date_range": {
        "start": "2023-12-25T12:00:00Z",
        "end": "2024-01-01T12:00:00Z"
      }
    },
    "risk_assessment": {
      "flood_risk": 0.2,
      "drought_risk": 0.1,
      "storm_risk": 0.3,
      "extreme_temperature_risk": 0.15
    }
  }
}
```

### Get Weather Prediction
```http
GET /weather/prediction/{location}
```

### Get Weather Alerts
```http
GET /weather/alerts?location={location}
```

## Blockchain Endpoints

### Get Blockchain Status
```http
GET /blockchain/status
```

**Response:**
```json
{
  "connected": true,
  "network": "http://localhost:8545",
  "account": "0x1234567890123456789012345678901234567890",
  "balance": 10.5,
  "contracts": {
    "weather_data_registry": true,
    "weather_insurance": true,
    "emergency_resource": true
  }
}
```

### Submit Weather Data to Blockchain
```http
POST /blockchain/weather/submit
```

**Request Body:**
```json
{
  "location": "New York, NY",
  "temperature": 22.5,
  "humidity": 65,
  "pressure": 1013.25,
  "wind_speed": 15.2,
  "precipitation": 0.0,
  "weather_type": "sunny",
  "ipfs_hash": ""
}
```

### Get Weather Data from Blockchain
```http
GET /blockchain/weather/{data_id}
```

### Verify Weather Data
```http
POST /blockchain/weather/{data_id}/verify
```

## Insurance Endpoints

### Get Insurance Quote
```http
POST /insurance/quote
```

**Request Body:**
```json
{
  "location": "Miami, FL",
  "coverage_amount": 100000,
  "event_type": "flood",
  "duration_days": 365,
  "risk_factors": {
    "proximity_to_water": true,
    "elevation": 5
  }
}
```

**Response:**
```json
{
  "success": true,
  "quote": {
    "policy_type": "flood_protection",
    "location": "Miami, FL",
    "coverage_amount": 100000,
    "premium": 7500,
    "duration_days": 365,
    "risk_assessment": {
      "base_rate": 0.05,
      "event_multiplier": 1.5,
      "overall_risk": "high"
    }
  }
}
```

### Create Insurance Policy
```http
POST /insurance/policies
```

### Get User Policies
```http
GET /insurance/policies/{user_address}
```

### Submit Insurance Claim
```http
POST /insurance/claims
```

**Request Body:**
```json
{
  "policy_id": "policy_001",
  "event_type": "flood",
  "damage_description": "Basement flooding due to heavy rainfall",
  "estimated_damage": 15000,
  "supporting_data": {
    "weather_data_id": 123,
    "photos": ["photo1.jpg", "photo2.jpg"]
  }
}
```

## AI Endpoints

### Analyze Weather Patterns
```http
POST /ai/analyze/patterns
```

**Request Body:**
```json
{
  "weather_data": [
    {
      "location": "New York, NY",
      "temperature": 22.5,
      "humidity": 65,
      "timestamp": "2024-01-01T12:00:00Z"
    }
  ]
}
```

### Generate Weather Prediction
```http
POST /ai/predict/weather
```

**Request Body:**
```json
{
  "location": "New York, NY",
  "historical_data": [...]
}
```

### Generate Weather Alert
```http
POST /ai/generate/alert
```

**Request Body:**
```json
{
  "alert_type": "flood",
  "severity": "high",
  "location": "Houston, TX",
  "conditions": {
    "precipitation": 75.5,
    "river_level": 8.2
  },
  "risk_level": 0.85
}
```

### Analyze Social Sentiment
```http
POST /ai/analyze/sentiment
```

**Request Body:**
```json
{
  "social_posts": [
    "Heavy rain in downtown, streets are flooding!",
    "Beautiful sunny day in the park",
    "Storm warning issued for our area"
  ]
}
```

## Emergency Endpoints

### Create Emergency Event
```http
POST /emergency/events
```

**Request Body:**
```json
{
  "event_type": "flood",
  "location": "Houston, TX",
  "severity": "high",
  "description": "Major flooding in downtown area",
  "affected_population": 50000,
  "coordinates": {
    "latitude": 29.7604,
    "longitude": -95.3698
  }
}
```

### Get Active Emergency Events
```http
GET /emergency/events/active
```

### Allocate Emergency Resources
```http
POST /emergency/resources/allocate
```

### Get Resource Status
```http
GET /emergency/resources/status
```

## Error Responses

All endpoints return errors in the following format:

```json
{
  "detail": "Error message description",
  "status_code": 400,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Common Error Codes

- `400` - Bad Request: Invalid parameters
- `401` - Unauthorized: Missing or invalid API key
- `404` - Not Found: Resource not found
- `429` - Too Many Requests: Rate limit exceeded
- `500` - Internal Server Error: Server error
- `503` - Service Unavailable: External service unavailable

## Rate Limits

- **Weather Data**: 100 requests per minute
- **AI Services**: 50 requests per minute
- **Blockchain Operations**: 20 requests per minute
- **General API**: 200 requests per minute

## WebSocket API

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/dashboard');
```

### Subscribe to Updates
```json
{
  "type": "subscribe",
  "subscription_type": "weather_updates"
}
```

### Available Subscriptions
- `weather_updates` - Real-time weather data
- `alerts` - Weather alerts and warnings
- `predictions` - AI predictions
- `blockchain_events` - Blockchain transactions
- `emergency_events` - Emergency notifications

### Message Format
```json
{
  "type": "weather_update",
  "data": {
    "location": "New York, NY",
    "temperature": 23.1,
    "timestamp": "2024-01-01T12:05:00Z"
  },
  "subscription_type": "weather_updates",
  "timestamp": "2024-01-01T12:05:00Z"
}
```

## SDK Examples

### Python SDK
```python
import requests

class WeatherGuardAPI:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    def get_current_weather(self, location):
        response = requests.get(
            f"{self.base_url}/weather/current/{location}",
            headers=self.headers
        )
        return response.json()

# Usage
api = WeatherGuardAPI("http://localhost:8000/api/v1", "your_api_key")
weather = api.get_current_weather("New York, NY")
```

### JavaScript SDK
```javascript
class WeatherGuardAPI {
    constructor(baseUrl, apiKey) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        };
    }

    async getCurrentWeather(location) {
        const response = await fetch(
            `${this.baseUrl}/weather/current/${location}`,
            { headers: this.headers }
        );
        return response.json();
    }
}

// Usage
const api = new WeatherGuardAPI('http://localhost:8000/api/v1', 'your_api_key');
const weather = await api.getCurrentWeather('New York, NY');
```

## Testing

### Health Check
```http
GET /health
```

### API Status
```http
GET /api/v1/status
```

For more detailed examples and integration guides, see the `/docs` directory in the repository.
