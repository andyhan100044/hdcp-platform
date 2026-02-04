# HDCP Platform Scenarios Guide

The HDCP Platform supports 4 data-driven scenarios. Each scenario includes pre-configured models, API endpoints, frontend components, and tests.

## Scenario 1: Stock Price Monitoring 📈

Monitor real-time stock prices, historical data, and technical indicators.

### Use Cases
- Financial data platforms
- Investment tracking applications
- Market analysis dashboards
- Trading signal systems
- Portfolio monitoring

### Quick Start

1. **Activate Scenario**
   ```python
   # apps/api/app/config/settings.py
   ACTIVE_SCENARIO = "stock"
   ```

2. **Restart Services**
   ```bash
   docker-compose restart api
   ```

3. **Test API**
   ```bash
   curl http://localhost:8000/api/v1/stocks/AAPL
   ```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/stocks/` | Create stock price |
| GET | `/api/v1/stocks/{symbol}` | Get latest price |
| GET | `/api/v1/stocks/{symbol}/history` | Get price history |
| GET | `/api/v1/stocks/{symbol}/summary` | Get summary stats |
| GET | `/api/v1/stocks/{symbol}/indicators` | Get technical indicators |
| PUT | `/api/v1/stocks/{symbol}` | Update price |
| DELETE | `/api/v1/stocks/{symbol}` | Delete price |

### Data Model

```python
StockPrice:
  - id (int, primary key)
  - symbol (str, index)        # AAPL, GOOGL, etc.
  - price (decimal)           # Current price
  - volume (int)               # Trading volume
  - price_change (decimal)    # Price change
  - price_change_percent (%)   # Percentage change
  - timestamp (datetime)       # Price timestamp
  - source (str)               # Data source
```

### Example Usage

```python
# Create stock price
import requests

data = {
    "symbol": "AAPL",
    "price": "150.25",
    "volume": 1000000,
    "timestamp": "2024-01-01T12:00:00Z"
}

response = requests.post(
    "http://localhost:8000/api/v1/stocks/",
    json=data
)

# Get latest price
response = requests.get(
    "http://localhost:8000/api/v1/stocks/AAPL"
)
stock = response.json()
print(f"AAPL: ${stock['price']}")
```

### Frontend Components

Available in `apps/web/src/components/dashboard/`:
- `StockChart.tsx` - Price chart visualization
- `StockTable.tsx` - Stock list table
- `StockSummary.tsx` - Key metrics display
- `PriceAlert.tsx` - Alert configuration

## Scenario 2: IoT Sensor Data 🌡️

Monitor IoT sensors with real-time alerts and historical analysis.

### Use Cases
- Smart building management
- Industrial monitoring
- Environmental sensing
- Agriculture monitoring
- Cold chain tracking

### Quick Start

1. **Activate Scenario**
   ```python
   # apps/api/app/config/settings.py
   ACTIVE_SCENARIO = "iot"
   ```

2. **Restart Services**
   ```bash
   docker-compose restart api
   ```

3. **Test API**
   ```bash
   curl http://localhost:8000/api/v1/sensors/TEMP_001
   ```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/sensors/readings` | Create sensor reading |
| GET | `/api/v1/sensors/{sensor_id}` | Get sensor status |
| GET | `/api/v1/sensors/{sensor_id}/readings` | Get sensor history |
| GET | `/api/v1/sensors/{sensor_id}/stats` | Get sensor statistics |
| GET | `/api/v1/sensors/alerts` | Get active alerts |
| POST | `/api/v1/sensors/alerts` | Create alert |

### Data Model

```python
SensorReading:
  - id (int, primary key)
  - sensor_id (str, index)     # TEMP_001, HUM_002, etc.
  - location (str)             # Room, zone, etc.
  - temperature (decimal)      # Temperature (°C)
  - humidity (decimal)          # Humidity (%)
  - battery_level (int)        # Battery level (0-100)
  - signal_strength (int)     # Signal strength (dBm)
  - timestamp (datetime)       # Reading timestamp
  - status (str)               # online, offline, error
```

### Example Usage

```python
# Create sensor reading
data = {
    "sensor_id": "TEMP_001",
    "location": "Room 101",
    "temperature": "22.5",
    "humidity": "65.0",
    "battery_level": 85,
    "timestamp": "2024-01-01T12:00:00Z"
}

response = requests.post(
    "http://localhost:8000/api/v1/sensors/readings/",
    json=data
)

# Get sensor readings
response = requests.get(
    "http://localhost:8000/api/v1/sensors/TEMP_001/readings"
)
readings = response.json()
```

### Frontend Components

Available in `apps/web/src/components/dashboard/`:
- `SensorDashboard.tsx` - Main sensor dashboard
- `ReadingChart.tsx` - Time-series chart
- `AlertList.tsx` - Active alerts
- `SensorMap.tsx` - Sensor location map

### Alert Configuration

```python
# High temperature alert
{
  "sensor_id": "TEMP_001",
  "alert_type": "high_temp",
  "severity": "high",
  "threshold": 30.0,
  "email": "admin@example.com"
}
```

## Scenario 3: E-commerce Price Tracking 🛒

Track product prices across multiple platforms with smart alerts.

### Use Cases
- Price comparison tools
- Competitor monitoring
- Deal finding applications
- Purchase optimization
- Market research

### Quick Start

1. **Activate Scenario**
   ```python
   # apps/api/app/config/settings.py
   ACTIVE_SCENARIO = "ecommerce"
   ```

2. **Restart Services**
   ```bash
   docker-compose restart api
   ```

3. **Test API**
   ```bash
   curl http://localhost:8000/api/v1/products/PROD_123
   ```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/products/prices` | Create price record |
| GET | `/api/v1/products/{product_id}` | Get latest price |
| GET | `/api/v1/products/{product_id}/history` | Get price history |
| GET | `/api/v1/products/{product_id}/compare` | Compare prices |
| POST | `/api/v1/products/alerts` | Create price alert |
| GET | `/api/v1/products/alerts` | Get price alerts |

### Data Model

```python
ProductPrice:
  - id (int, primary key)
  - product_id (str, index)     # Product identifier
  - product_name (str)           # Product name
  - price (decimal)             # Product price
  - currency (str)              # Currency code (USD)
  - price_usd (decimal)         # Price in USD
  - source (str)                # Platform (Amazon, eBay, etc.)
  - source_url (str)            # Product URL
  - availability (str)           # in_stock, out_of_stock
  - stock_count (int)           # Stock quantity
  - category (str)              # Product category
  - timestamp (datetime)        # Price timestamp
```

### Example Usage

```python
# Create product price
data = {
    "product_id": "PROD_123",
    "product_name": "iPhone 15",
    "price": "999.99",
    "currency": "USD",
    "source": "Amazon",
    "source_url": "https://amazon.com/iphone-15",
    "availability": "in_stock",
    "timestamp": "2024-01-01T12:00:00Z"
}

response = requests.post(
    "http://localhost:8000/api/v1/products/prices/",
    json=data
)

# Compare prices across sources
response = requests.get(
    "http://localhost:8000/api/v1/products/PROD_123/compare"
)
comparison = response.json()
print(f"Lowest: ${comparison['lowest_price']}")
```

### Frontend Components

Available in `apps/web/src/components/dashboard/`:
- `PriceTracker.tsx` - Price tracking dashboard
- `ProductComparison.tsx` - Price comparison table
- `PriceChart.tsx` - Price trend chart
- `DealAlerts.tsx` - Price drop notifications

### Price Alerts

```python
# Price drop alert
{
  "product_id": "PROD_123",
  "target_price": 899.99,
  "email": "user@example.com"
}
```

## Scenario 4: Carbon Credit Tracking 🌱

Track carbon credit projects with environmental impact metrics.

### Use Cases
- ESG tracking platforms
- Carbon offset marketplaces
- Environmental impact dashboards
- Sustainability reporting
- Green investment tools

### Quick Start

1. **Activate Scenario**
   ```python
   # apps/api/app/config/settings.py
   ACTIVE_SCENARIO = "carbon"
   ```

2. **Restart Services**
   ```bash
   docker-compose restart api
   ```

3. **Test API**
   ```bash
   curl http://localhost:8000/api/v1/carbon-credits/projects/CC_001
   ```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/carbon-credits/projects` | Create project |
| GET | `/api/v1/carbon-credits/projects` | List projects |
| GET | `/api/v1/carbon-credits/projects/{project_id}` | Get project |
| POST | `/api/v1/carbon-credits/prices` | Create price |
| GET | `/api/v1/carbon-credits/projects/{project_id}/impact` | Get impact |
| GET | `/api/v1/carbon-credits/market/overview` | Market overview |

### Data Model

```python
CarbonCreditProject:
  - project_id (str, primary key)  # CC_001
  - name (str)                     # Project name
  - standard (str)                 # VCS, Gold Standard, etc.
  - location (str)                # Project location
  - project_type (str)            # forestry, renewable, etc.
  - methodology (str)              # Verification methodology
  - additionality_score (decimal) # 0-1
  - permanence_years (int)         # Years
  - co_benefits_score (decimal)    # 0-1
  - status (str)                   # active, retired
  - total_credits_issued (decimal) # tCO2e

CarbonCreditPrice:
  - id (int, primary key)
  - project_id (str, index)        # Reference to project
  - standard (str)                 # Certification standard
  - price_usd (decimal)            # Price per ton CO2
  - volume_tons (decimal)           # Volume traded
  - source (str)                   # registry, exchange, otc
  - confidence (decimal)            # 0-1
  - timestamp (datetime)            # Price timestamp

EnvironmentalImpact:
  - id (int, primary key)
  - project_id (str, index)        # Reference to project
  - co2_equivalent_tons (decimal)   # CO2 offset
  - forest_area_hectares (decimal)  # Forest area
  - communities_benefited (int)     # Number of communities
  - biodiversity_score (decimal)     # 0-1
  - sdg_contributions (str)         # JSON array of SDGs
  - water_saved_liters (decimal)     # Water saved
  - renewable_energy_mwh (decimal)   # Renewable energy
```

### Example Usage

```python
# Create carbon project
data = {
    "project_id": "CC_001",
    "name": "Amazon Rainforest Conservation",
    "standard": "VCS",
    "location": "Brazil",
    "project_type": "forestry",
    "additionality_score": 0.85,
    "co_benefits_score": 0.90,
    "status": "active"
}

response = requests.post(
    "http://localhost:8000/api/v1/carbon-credits/projects/",
    json=data
)

# Get environmental impact
response = requests.get(
    "http://localhost:8000/api/v1/carbon-credits/projects/CC_001/impact"
)
impact = response.json()
print(f"CO2 Offset: {impact['co2_equivalent_tons']} tons")
```

### Frontend Components

Available in `apps/web/src/components/dashboard/`:
- `ProjectMap.tsx` - Project location map
- `ImpactDashboard.tsx` - Environmental impact dashboard
- `PriceChart.tsx` - Carbon credit price trends
- `ProjectList.tsx` - Project catalog

## Multi-Scenario Development

### Activate All Scenarios

For development or testing all scenarios:

```python
# apps/api/app/config/settings.py
ACTIVE_SCENARIO = "all"
```

This will expose all endpoints:
- `/api/v1/stocks/*`
- `/api/v1/sensors/*`
- `/api/v1/products/*`
- `/api/v1/carbon-credits/*`

### Switching Scenarios

1. Update `ACTIVE_SCENARIO` in settings
2. Restart API: `docker-compose restart api`
3. Clear cache: `docker-compose exec api redis-cli FLUSHALL`
4. Test new endpoints

## Custom Scenarios

To add your own scenario:

1. **Create Models**
   ```python
   # apps/api/app/models/custom.py
   class CustomData(TimestampedModel):
       __tablename__ = "custom_data"
       # Your fields
   ```

2. **Create Schemas**
   ```python
   # apps/api/app/schemas/custom.py
   class CustomDataCreate(BaseModel):
       # Your fields
   ```

3. **Create Router**
   ```python
   # apps/api/app/routers/custom.py
   router = APIRouter(prefix="/custom")
   ```

4. **Include Router**
   ```python
   # apps/api/app/main.py
   from app.routers import custom
   app.include_router(custom.router, prefix="/api/v1/custom")
   ```

5. **Update Models Import**
   ```python
   # apps/api/app/models/__init__.py
   from app.models.custom import CustomData
   ```

## Testing Scenarios

Each scenario has test files:

```bash
# Stock tests
cd apps/api
pytest tests/test_stock.py -v

# IoT tests
pytest tests/test_iot.py -v

# E-commerce tests
pytest tests/test_ecommerce.py -v

# Carbon tests
pytest tests/test_carbon.py -v

# All tests
pytest tests/ -v
```

## Scenario Templates

Pre-configured templates are in `templates/` directory:

```
templates/
├── stock/              # Stock template
│   ├── api/           # API config
│   ├── web/           # Frontend config
│   ├── cms/           # CMS config
│   └── data/          # Sample data
├── iot/
├── ecommerce/
└── carbon/
```

To use a template:
```bash
# Copy template files
cp -r templates/stock/* apps/api/
cp -r templates/stock/web/* apps/web/

# Restart services
docker-compose restart
```

## Performance Optimization

### Stock Scenario
- Enable Redis caching for price queries
- Use time-series database for large datasets
- Implement data aggregation for historical data

### IoT Scenario
- Use message queues for high-frequency readings
- Implement data compression for storage
- Use real-time WebSocket connections

### E-commerce Scenario
- Cache product data and prices
- Implement async price checking
- Use CDN for product images

### Carbon Scenario
- Cache project data
- Implement bulk data imports
- Use geospatial indexes for location queries

## Next Steps

- ✅ Understand scenarios
- ✅ Choose your scenario
- ✅ Test API endpoints
- ✅ Review [Customization Guide](customization.md)
- ✅ Read [API Documentation](api.md)
