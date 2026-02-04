# HDCP Platform - Quick Start Guide

> **Get your data platform running in 5 minutes!**

## 🚀 Super Quick Start (Automated)

```bash
# 1. Clone
git clone <your-repo> my-platform
cd my-platform

# 2. Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# 3. Choose scenario when prompted
# 1) stock     2) iot     3) ecommerce     4) carbon     5) all

# 4. Done! 🎉
# Visit http://localhost:3000
```

That's it! Your platform is running.

---

## ⚡ Manual Quick Start

If you prefer manual setup:

### Step 1: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit key settings
nano .env

# Set your scenario (required!)
ACTIVE_SCENARIO=stock  # Options: stock, iot, ecommerce, carbon
```

### Step 2: Update Scenario Config

```bash
# Edit the settings file
nano apps/api/app/config/settings.py

# Change this line:
ACTIVE_SCENARIO = "stock"
```

### Step 3: Start Services

```bash
# Build and start
docker-compose up -d

# Check status
docker-compose ps
```

### Step 4: Verify

```bash
# API health
curl http://localhost:8000/health
# Expected: {"status": "healthy", ...}

# Frontend
curl http://localhost:3000
# Expected: HTML page

# CMS Admin
# Visit: http://localhost:1337/admin
```

---

## 📖 What Just Happened?

The setup script automatically:

1. ✅ Checked prerequisites (Docker, Docker Compose)
2. ✅ Created `.env` file from template
3. ✅ Configured scenario (stock/iot/ecommerce/carbon)
4. ✅ Built Docker images
5. ✅ Started all services (API, Web, CMS, Database, Redis)
6. ✅ Verified installation

**Services Started:**
- **API** (FastAPI): http://localhost:8000
- **Web** (Next.js): http://localhost:3000
- **CMS** (Strapi): http://localhost:1337/admin
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

---

## 🎯 Choose Your Scenario

### Scenario 1: Stock Price Monitoring 📈

Perfect for financial data platforms, investment tracking, market analysis.

**Activate:**
```python
# apps/api/app/config/settings.py
ACTIVE_SCENARIO = "stock"
```

**Test:**
```bash
curl -X POST http://localhost:8000/api/v1/stocks/ \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "price": 150.25, "volume": 1000000}'

curl http://localhost:8000/api/v1/stocks/AAPL
```

**What you get:**
- Stock price API endpoints
- Historical data queries
- Technical indicators support
- Stock summary statistics

---

### Scenario 2: IoT Sensor Data 🌡️

Perfect for smart buildings, industrial monitoring, environmental sensing.

**Activate:**
```python
# apps/api/app/config/settings.py
ACTIVE_SCENARIO = "iot"
```

**Test:**
```bash
curl -X POST http://localhost:8000/api/v1/sensors/readings \
  -H "Content-Type: application/json" \
  -d '{"sensor_id": "TEMP_001", "temperature": 22.5, "humidity": 65}'

curl http://localhost:8000/api/v1/sensors/TEMP_001
```

**What you get:**
- Sensor reading API endpoints
- Real-time monitoring support
- Alert configuration
- Battery and signal tracking

---

### Scenario 3: E-commerce Price Tracking 🛒

Perfect for price comparison tools, competitor monitoring, deal finding.

**Activate:**
```python
# apps/api/app/config/settings.py
ACTIVE_SCENARIO = "ecommerce"
```

**Test:**
```bash
curl -X POST http://localhost:8000/api/v1/products/prices \
  -H "Content-Type: application/json" \
  -d '{"product_id": "PROD_123", "product_name": "iPhone 15", "price": 999.99}'

curl http://localhost:8000/api/v1/products/PROD_123
```

**What you get:**
- Product price API endpoints
- Multi-platform price tracking
- Price comparison features
- Alert system

---

### Scenario 4: Carbon Credit Tracking 🌱

Perfect for ESG platforms, carbon offset marketplaces, sustainability reporting.

**Activate:**
```python
# apps/api/app/config/settings.py
ACTIVE_SCENARIO = "carbon"
```

**Test:**
```bash
curl -X POST http://localhost:8000/api/v1/carbon-credits/projects \
  -H "Content-Type: application/json" \
  -d '{"project_id": "CC_001", "name": "Forest Conservation", "standard": "VCS"}'

curl http://localhost:8000/api/v1/carbon-credits/projects
```

**What you get:**
- Carbon project API endpoints
- Environmental impact tracking
- Price monitoring
- Market overview

---

## 🔄 Switching Scenarios

Want to try a different scenario?

```bash
# 1. Edit config
nano apps/api/app/config/settings.py
# Change: ACTIVE_SCENARIO = "iot"

# 2. Restart API
docker-compose restart api

# 3. Test new endpoints
curl http://localhost:8000/api/v1/sensors/
```

---

## 🛠️ Development Mode

For active development:

```bash
# Terminal 1: API
cd apps/api
uvicorn app.main:app --reload --port 8000

# Terminal 2: Web
cd apps/web
npm run dev

# Terminal 3: CMS
cd apps/cms
npm run develop
```

---

## 📊 Access Your Platform

### Frontend Dashboard
- **URL**: http://localhost:3000
- **Description**: User-facing dashboard
- **Features**: Charts, tables, forms

### API Documentation
- **URL**: http://localhost:8000/docs
- **Description**: Interactive API docs
- **Features**: Try endpoints, view schemas

### GraphQL Playground
- **URL**: http://localhost:8000/graphql
- **Description**: GraphQL query interface
- **Features**: Test queries, explore schema

### CMS Admin Panel
- **URL**: http://localhost:1337/admin
- **Description**: Content management
- **Features**: Create content, manage users

### API Health Check
- **URL**: http://localhost:8000/health
- **Description**: System health status
- **Features**: Verify all services running

---

## 🧪 Test the API

### Using curl

```bash
# Get API info
curl http://localhost:8000/

# Health check
curl http://localhost:8000/health

# Create data (based on active scenario)
# Stock scenario:
curl -X POST http://localhost:8000/api/v1/stocks/ \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "price": 150.25}'

# Get data
curl http://localhost:8000/api/v1/stocks/AAPL
```

### Using Swagger UI

1. Open: http://localhost:8000/docs
2. Click "Try it out"
3. Test endpoints interactively
4. View request/response formats

---

## 📱 Frontend Features

### Multi-Language Support

The frontend supports 8 languages:
- 🇺🇸 English
- 🇨🇳 Chinese (Simplified)
- 🇪🇸 Spanish
- 🇫🇷 French
- 🇩🇪 German
- 🇯🇵 Japanese
- 🇰🇷 Korean
- 🇸🇦 Arabic (RTL)

**Usage:**
- Automatic detection from browser
- Manual language switcher in navbar
- URL-based routing (e.g., `/en/`, `/zh-CN/`)

### Dashboard Components

Available components (based on scenario):
- **Stock**: Price charts, stock tables, summaries
- **IoT**: Sensor dashboards, alert lists, maps
- **E-commerce**: Price trackers, comparisons, charts
- **Carbon**: Project maps, impact dashboards, price trends

---

## 🎨 Customization

### Change Branding

Edit: `apps/web/src/app/layout.tsx`
```typescript
// Change app name
<title>Your Platform Name</title>
```

### Update Colors

Edit: `apps/web/tailwind.config.js`
```javascript
// Change color scheme
theme: {
  extend: {
    colors: {
      primary: {
        // Your brand colors
      }
    }
  }
}
```

### Add Translations

Edit: `apps/web/src/locales/en/`
```json
{
  "welcome": "Welcome to Your Platform"
}
```

---

## 🔧 Configuration

### Key Settings in `.env`

```bash
# REQUIRED: Choose scenario
ACTIVE_SCENARIO=stock

# REQUIRED: Set secret keys
SECRET_KEY=your-secret-key-minimum-32-characters
JWT_SECRET=your-jwt-secret-minimum-32-characters

# Database
DATABASE_URL=postgresql+asyncpg://hdcp_user:password@postgres:5432/hdcp_db

# Redis
REDIS_URL=redis://redis:6379/0

# Multi-language
DEFAULT_LOCALE=en
SUPPORTED_LOCALES=en,zh-CN,es,fr,de,ja,ko,ar
```

### Advanced Configuration

Edit: `apps/api/app/config/settings.py`
```python
# Rate limiting
RATE_LIMIT_PER_MINUTE = 100

# Cache settings
CACHE_TTL = 300  # 5 minutes

# Enable features
ENABLE_METRICS = True
ENABLE_CACHING = True
```

---

## 🚦 Common Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f api
docker-compose logs -f web

# Restart a service
docker-compose restart api

# Run tests
./scripts/test.sh

# Build images
docker-compose build --no-cache

# Clean up
docker-compose down -v
docker system prune -a
```

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
lsof -i :8000

# Stop conflicting service
kill -9 <PID>

# Or change port in .env
API_PORT=8001
```

### Database Connection Failed

```bash
# Check PostgreSQL
docker-compose logs postgres

# Check if database exists
docker-compose exec postgres psql -U hdcp_user -l

# Recreate database
docker-compose down -v
docker-compose up -d
```

### API Not Responding

```bash
# Check API logs
docker-compose logs api

# Check health
curl http://localhost:8000/health

# Restart API
docker-compose restart api
```

### Frontend Not Loading

```bash
# Check web logs
docker-compose logs web

# Check Next.js build
docker-compose logs web | grep -i error

# Rebuild web
docker-compose build web --no-cache
```

---

## 📚 Next Steps

Now that your platform is running:

1. **📖 Read Documentation**
   - [Scenarios Guide](docs/scenarios.md) - Learn about each scenario
   - [API Documentation](docs/api.md) - Explore all endpoints
   - [Customization Guide](docs/customization.md) - Customize the platform

2. **🎨 Customize**
   - Change branding and colors
   - Add your data
   - Modify components
   - Add new features

3. **🚀 Deploy to Production**
   - Read [Deployment Guide](docs/deployment.md)
   - Configure SSL/TLS
   - Set up monitoring
   - Enable backups

4. **🧪 Test**
   - Run test suite: `./scripts/test.sh`
   - Test all endpoints
   - Verify functionality

---

## 💡 Tips

### Speed Up Development

```bash
# Use bind mounts for hot reload
# Edit: docker-compose.yml
volumes:
  - ./apps/api:/app  # Hot reload Python
  - ./apps/web:/app  # Hot reload Node
```

### Debug API

```bash
# Enable debug mode
# Edit: apps/api/app/config/settings.py
DEBUG = True

# View detailed logs
docker-compose logs -f api | grep -i detail
```

### Test Data

```bash
# Add sample data
curl -X POST http://localhost:8000/api/v1/stocks/ \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "price": 150.25, "volume": 1000000}'

# Create multiple records
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/v1/stocks/ \
    -H "Content-Type: application/json" \
    -d "{\"symbol\": \"STOCK$i\", \"price\": $((100 + i))}"
done
```

---

## 🎉 Success!

**You now have a:**
✅ Fully functional data platform
✅ REST API with CRUD operations
✅ Multi-language frontend
✅ Content management system
✅ Production-ready deployment
✅ Comprehensive documentation

**Ready to build your custom data platform!**

---

## 🆘 Need Help?

- 📚 **Documentation**: Check `docs/` folder
- 🐛 **Issues**: Open GitHub issue
- 💬 **Discussions**: GitHub Discussions
- 📧 **Email**: support@yourdomain.com

**Happy coding! 🚀**
