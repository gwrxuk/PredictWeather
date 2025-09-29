# WeatherGuard Deployment Guide

This guide provides step-by-step instructions for deploying the WeatherGuard platform.

## Prerequisites

### System Requirements
- Node.js 18+ and npm
- Python 3.8+
- PostgreSQL 12+ (optional, SQLite for development)
- Redis 6+ (optional for production)
- Git

### API Keys Required
- OpenWeatherMap API key
- OpenAI API key (for LLM features)
- NOAA API key (optional)
- NASA API key (optional)

## Quick Start (Development)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd weather
npm run setup
```

### 2. Environment Configuration

Copy the environment template:
```bash
cp env.example .env
```

Edit `.env` with your API keys:
```env
OPENWEATHER_API_KEY=your_openweather_api_key
OPENAI_API_KEY=your_openai_api_key
ETHEREUM_RPC_URL=http://localhost:8545
DATABASE_URL=sqlite:///./weatherguard.db
```

### 3. Start Local Blockchain

```bash
cd blockchain
npm install
npx hardhat node
```

### 4. Deploy Smart Contracts

In a new terminal:
```bash
cd blockchain
npm run deploy:local
```

### 5. Start Backend Services

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 6. Start Frontend

```bash
cd frontend
npm install
npm start
```

### 7. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Production Deployment

### 1. Infrastructure Setup

#### Option A: Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

#### Option B: Manual Deployment

##### Database Setup (PostgreSQL)
```sql
CREATE DATABASE weatherguard;
CREATE USER weatherguard WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE weatherguard TO weatherguard;
```

##### Redis Setup
```bash
# Install and start Redis
sudo systemctl start redis
sudo systemctl enable redis
```

### 2. Environment Configuration

Create production environment file:
```env
# API Keys
OPENWEATHER_API_KEY=your_production_key
OPENAI_API_KEY=your_production_key
NOAA_API_KEY=your_noaa_key
NASA_API_KEY=your_nasa_key

# Blockchain Configuration
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/your_project_id
PRIVATE_KEY=your_private_key
NETWORK_ID=1

# Database
DATABASE_URL=postgresql://weatherguard:password@localhost:5432/weatherguard
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your_very_secure_secret_key
DEBUG=false

# External Services
SENTRY_DSN=your_sentry_dsn
```

### 3. Backend Deployment

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 4. Frontend Deployment

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Serve with nginx or deploy to CDN
```

### 5. Smart Contract Deployment

#### Testnet Deployment (Goerli)
```bash
cd blockchain
npm run deploy:testnet
```

#### Mainnet Deployment
```bash
cd blockchain
npm run deploy:mainnet
```

### 6. Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /path/to/frontend/build;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## Monitoring and Maintenance

### 1. Health Checks

Monitor these endpoints:
- `GET /health` - Overall system health
- `GET /api/v1/status` - API status
- `GET /api/v1/blockchain/status` - Blockchain connectivity

### 2. Logging

Configure logging levels:
```python
# backend/main.py
import logging
logging.basicConfig(level=logging.INFO)
```

### 3. Backup Strategy

#### Database Backups
```bash
# Daily PostgreSQL backup
pg_dump weatherguard > backup_$(date +%Y%m%d).sql
```

#### Smart Contract Verification
Verify contracts on Etherscan for transparency.

### 4. Scaling Considerations

#### Horizontal Scaling
- Use load balancer for multiple backend instances
- Implement Redis for session management
- Use CDN for frontend assets

#### Performance Optimization
- Enable database connection pooling
- Implement caching for weather data
- Use background tasks for heavy computations

## Security Checklist

### Backend Security
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS properly
- [ ] Implement rate limiting
- [ ] Use environment variables for secrets
- [ ] Enable database SSL connections
- [ ] Implement proper authentication

### Smart Contract Security
- [ ] Audit smart contracts
- [ ] Use multi-signature wallets
- [ ] Implement emergency pause mechanisms
- [ ] Monitor for unusual transactions

### Infrastructure Security
- [ ] Configure firewall rules
- [ ] Enable fail2ban
- [ ] Regular security updates
- [ ] Monitor system logs
- [ ] Backup encryption

## Troubleshooting

### Common Issues

#### Blockchain Connection Issues
```bash
# Check network connectivity
curl -X POST -H "Content-Type: application/json" --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' $ETHEREUM_RPC_URL
```

#### Database Connection Issues
```bash
# Test PostgreSQL connection
psql -h localhost -U weatherguard -d weatherguard -c "SELECT 1;"
```

#### API Key Issues
- Verify API keys are correctly set in environment
- Check API rate limits and quotas
- Ensure API keys have necessary permissions

### Performance Issues

#### High Memory Usage
- Monitor Python memory usage
- Implement connection pooling
- Use Redis for caching

#### Slow API Responses
- Enable database query logging
- Implement API response caching
- Optimize database indexes

## Support

For deployment issues:
1. Check the logs in `/var/log/weatherguard/`
2. Review the troubleshooting section
3. Contact the development team

## Version Updates

### Backend Updates
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
systemctl restart weatherguard-backend
```

### Frontend Updates
```bash
cd frontend
npm install
npm run build
# Deploy new build
```

### Smart Contract Updates
- Deploy new contracts
- Update contract addresses in environment
- Migrate data if necessary
