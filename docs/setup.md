# HDCP Platform Setup Guide

This guide walks you through setting up the HDCP Platform template.

## Prerequisites

- **Docker 20.10+** - Container platform
- **Docker Compose 2.0+** - Multi-container orchestration
- **Git** - Version control
- **4GB+ RAM** - Minimum memory requirement
- **10GB+ Disk** - Minimum disk space

## Step 1: Clone the Template

```bash
# Clone the repository
git clone <your-template-repo-url> my-data-platform
cd my-data-platform

# Verify files
ls -la
# You should see: apps/, templates/, docs/, docker-compose.yml
```

## Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env  # or your preferred editor
```

Key settings to configure:

```bash
# Database (default is fine for development)
DATABASE_URL=postgresql+asyncpg://hdcp_user:hdcp_password@postgres:5432/hdcp_db
POSTGRES_DB=hdcp_db
POSTGRES_USER=hdcp_user
POSTGRES_PASSWORD=hdcp_password

# Redis (default is fine)
REDIS_URL=redis://redis:6379/0

# Choose your scenario (REQUIRED)
ACTIVE_SCENARIO=stock  # Options: stock, iot, ecommerce, carbon

# Security (CHANGE IN PRODUCTION)
SECRET_KEY=your-super-secret-key-change-this
JWT_SECRET=your-jwt-secret-change-this
```

## Step 3: Choose Your Scenario

Edit `apps/api/app/config/settings.py`:

```python
# Scenario options:
# - "stock"     : Stock price monitoring
# - "iot"       : IoT sensor data
# - "ecommerce" : E-commerce price tracking
# - "carbon"    : Carbon credit tracking
# - "all"       : All scenarios (development only)

ACTIVE_SCENARIO = "stock"
```

## Step 4: Start Services

```bash
# Build and start all services
docker-compose up -d

# View logs (optional)
docker-compose logs -f
```

Expected output:
```
Creating network "hdcp-template_hdcp-network" ... done
Creating postgres ... done
Creating redis    ... done
Creating api      ... done
Creating web      ... done
Creating cms      ... done
```

## Step 5: Verify Installation

### Check API Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "HDCP Platform API",
  "version": "1.0.0",
  "environment": "development",
  "scenario": "stock"
}
```

### Check Frontend

```bash
curl http://localhost:3000
```

You should see HTML output from Next.js.

### Check CMS Admin

1. Open browser: http://localhost:1337/admin
2. Create admin account (first time only)
3. Login with your credentials

## Step 6: Test the API

### Using curl

```bash
# Test stock endpoint (if using stock scenario)
curl -X POST http://localhost:8000/api/v1/stocks/ \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "price": "150.25",
    "volume": 1000000,
    "timestamp": "2024-01-01T12:00:00Z"
  }'

# Get stock data
curl http://localhost:8000/api/v1/stocks/AAPL
```

### Using Swagger UI

1. Open: http://localhost:8000/docs
2. Test endpoints interactively
3. Authenticate if required

## Step 7: Initialize Database (First Time)

If you need to create tables:

```bash
# Run database migrations
docker-compose exec api alembic upgrade head

# Or manually create tables (development only)
docker-compose exec api python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
```

## Development Mode

For active development:

### Backend (FastAPI)

```bash
# Terminal 1: Start API
cd apps/api
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Next.js)

```bash
# Terminal 2: Start Web
cd apps/web
npm run dev
```

### CMS (Strapi)

```bash
# Terminal 3: Start CMS
cd apps/cms
npm run develop
```

## Troubleshooting

### Port Already in Use

If you get "port already in use" errors:

```bash
# Check what's using the port
netstat -tuln | grep 8000

# Stop conflicting services
docker-compose down
```

### Database Connection Failed

```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Verify credentials in .env
cat .env | grep DATABASE
```

### Permission Denied

```bash
# Fix Docker permissions (Linux)
sudo usermod -aG docker $USER
newgrp docker

# Or run with sudo
sudo docker-compose up -d
```

### Service Not Starting

```bash
# Check logs for specific service
docker-compose logs api
docker-compose logs web
docker-compose logs cms

# Rebuild images
docker-compose build --no-cache
```

## Next Steps

Once setup is complete:

1. **Read the [Scenarios Guide](scenarios.md)** - Learn about each scenario
2. **Check [API Documentation](api.md)** - Understand available endpoints
3. **See [Customization Guide](customization.md)** - Learn how to customize
4. **Read [Deployment Guide](deployment.md)** - Learn production deployment

## Common Issues

### Issue: "module not found" errors

**Solution**: Rebuild containers
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Issue: CORS errors

**Solution**: Update CORS settings in `apps/api/app/main.py`
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Slow performance

**Solution**: Increase Docker resources
- Docker Desktop: Settings → Resources → Increase RAM to 4GB+
- Docker Engine: Edit `/etc/docker/daemon.json`

## Support

Need help? Check:
- 📚 [Documentation](README.md)
- 🐛 [GitHub Issues](https://github.com/your-org/hdcp-template/issues)
- 💬 [GitHub Discussions](https://github.com/your-org/hdcp-template/discussions)

## What's Next?

- ✅ Platform is running
- ✅ Services are healthy
- ✅ API is responding

**Next**: [Choose and configure your scenario](scenarios.md)
