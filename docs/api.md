# HDCP Platform API Documentation

The HDCP Platform provides RESTful APIs for all supported scenarios. This documentation covers all available endpoints, request/response formats, and examples.

## Base URL

```
Development: http://localhost:8000
Production:  https://api.yourdomain.com
```

## API Versioning

All APIs are versioned. Current version: `v1`

```
http://localhost:8000/api/v1/
```

## Authentication

Currently, the API does not require authentication for development. Authentication will be added in future versions.

```bash
# Future: Include API key in header
curl -H "X-API-Key: your-api-key" \
     http://localhost:8000/api/v1/stocks/AAPL
```

## Response Format

All API responses follow a standard format:

### Success Response

```json
{
  "success": true,
  "message": "Success",
  "data": { ... },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Error Response

```json
{
  "success": false,
  "error": "ValidationError",
  "message": "Invalid input data",
  "error_details": {
    "field": "price",
    "message": "Price must be greater than 0"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Paginated Response

```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 100,
    "total_pages": 5,
    "has_next": true,
    "has_previous": false
  }
}
```

## Stock Price Endpoints 📈

### Create Stock Price

Create a new stock price record.

**Endpoint:** `POST /api/v1/stocks/`

**Request Body:**

```json
{
  "symbol": "AAPL",
  "price": 150.25,
  "volume": 1000000,
  "price_change": 2.50,
  "price_change_percent": 1.69,
  "timestamp": "2024-01-01T12:00:00Z",
  "source": "Yahoo Finance"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "symbol": "AAPL",
    "price": 150.25,
    "volume": 1000000,
    "price_change": 2.50,
    "price_change_percent": 1.69,
    "timestamp": "2024-01-01T12:00:00Z",
    "source": "Yahoo Finance",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
}
```

**Example:**

```bash
curl -X POST http://localhost:8000/api/v1/stocks/ \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "price": 150.25,
    "volume": 1000000,
    "timestamp": "2024-01-01T12:00:00Z"
  }'
```

---

### Get Stock Price

Get the latest stock price for a symbol.

**Endpoint:** `GET /api/v1/stocks/{symbol}`

**Parameters:**
- `symbol` (path, string): Stock symbol (e.g., AAPL, GOOGL)

**Response:**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "symbol": "AAPL",
    "price": 150.25,
    "volume": 1000000,
    "timestamp": "2024-01-01T12:00:00Z",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
}
```

**Example:**

```bash
curl http://localhost:8000/api/v1/stocks/AAPL
```

---

### Get Stock History

Get historical stock prices.

**Endpoint:** `GET /api/v1/stocks/{symbol}/history`

**Parameters:**
- `symbol` (path, string): Stock symbol
- `start_date` (query, datetime, optional): Start date
- `end_date` (query, datetime, optional): End date
- `limit` (query, integer, optional): Number of records (default: 100, max: 1000)

**Response:**

```json
{
  "success": true,
  "data": [
    {
      "id": 100,
      "symbol": "AAPL",
      "price": 150.25,
      "volume": 1000000,
      "timestamp": "2024-01-01T12:00:00Z"
    },
    ...
  ]
}
```

**Example:**

```bash
curl "http://localhost:8000/api/v1/stocks/AAPL/history?limit=10"
```

---

### Get Stock Summary

Get stock summary with statistics.

**Endpoint:** `GET /api/v1/stocks/{symbol}/summary`

**Parameters:**
- `symbol` (path, string): Stock symbol

**Response:**

```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "current_price": 150.25,
    "price_change": 2.50,
    "price_change_percent": 1.69,
    "volume": 1000000,
    "market_cap": null,
    "high_52w": 182.50,
    "low_52w": 124.75,
    "last_updated": "2024-01-01T12:00:00Z"
  }
}
```

**Example:**

```bash
curl http://localhost:8000/api/v1/stocks/AAPL/summary
```

---

### List Stock Prices

List stock prices with pagination and filtering.

**Endpoint:** `GET /api/v1/stocks/`

**Parameters:**
- `page` (query, integer, optional): Page number (default: 1)
- `size` (query, integer, optional): Page size (default: 20, max: 100)
- `symbol` (query, string, optional): Filter by symbol

**Response:**

```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 100,
    "total_pages": 5,
    "has_next": true,
    "has_previous": false
  }
}
```

**Example:**

```bash
curl "http://localhost:8000/api/v1/stocks/?page=1&size=10"
```

---

## IoT Sensor Endpoints 🌡️

### Create Sensor Reading

Create a new sensor reading.

**Endpoint:** `POST /api/v1/sensors/readings`

**Request Body:**

```json
{
  "sensor_id": "TEMP_001",
  "location": "Room 101",
  "temperature": 22.5,
  "humidity": 65.0,
  "battery_level": 85,
  "timestamp": "2024-01-01T12:00:00Z",
  "status": "online"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "sensor_id": "TEMP_001",
    "location": "Room 101",
    "temperature": 22.5,
    "humidity": 65.0,
    "battery_level": 85,
    "timestamp": "2024-01-01T12:00:00Z",
    "status": "online",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
}
```

**Example:**

```bash
curl -X POST http://localhost:8000/api/v1/sensors/readings \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "TEMP_001",
    "temperature": 22.5,
    "humidity": 65.0,
    "timestamp": "2024-01-01T12:00:00Z"
  }'
```

---

### Get Sensor Readings

Get sensor readings history.

**Endpoint:** `GET /api/v1/sensors/{sensor_id}/readings`

**Parameters:**
- `sensor_id` (path, string): Sensor ID
- `start_date` (query, datetime, optional): Start date
- `end_date` (query, datetime, optional): End date
- `limit` (query, integer, optional): Number of records (default: 100)

**Response:**

```json
{
  "success": true,
  "data": [
    {
      "id": 100,
      "sensor_id": "TEMP_001",
      "temperature": 22.5,
      "humidity": 65.0,
      "timestamp": "2024-01-01T12:00:00Z"
    },
    ...
  ]
}
```

**Example:**

```bash
curl "http://localhost:8000/api/v1/sensors/TEMP_001/readings?limit=50"
```

---

### Get Sensor Statistics

Get sensor statistics.

**Endpoint:** `GET /api/v1/sensors/{sensor_id}/stats`

**Parameters:**
- `sensor_id` (path, string): Sensor ID

**Response:**

```json
{
  "success": true,
  "data": {
    "sensor_id": "TEMP_001",
    "location": "Room 101",
    "total_readings": 1000,
    "last_reading": "2024-01-01T12:00:00Z",
    "avg_temperature": 22.5,
    "avg_humidity": 65.0,
    "avg_battery": 85,
    "uptime_percent": 99.5,
    "alerts_count": 2
  }
}
```

**Example:**

```bash
curl http://localhost:8000/api/v1/sensors/TEMP_001/stats
```

---

## E-commerce Endpoints 🛒

### Create Product Price

Create a new product price record.

**Endpoint:** `POST /api/v1/products/prices`

**Request Body:**

```json
{
  "product_id": "PROD_123",
  "product_name": "iPhone 15",
  "price": 999.99,
  "currency": "USD",
  "price_usd": 999.99,
  "source": "Amazon",
  "source_url": "https://amazon.com/iphone-15",
  "availability": "in_stock",
  "stock_count": 50,
  "category": "Electronics",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "product_id": "PROD_123",
    "product_name": "iPhone 15",
    "price": 999.99,
    "currency": "USD",
    "source": "Amazon",
    "availability": "in_stock",
    "timestamp": "2024-01-01T12:00:00Z",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
}
```

**Example:**

```bash
curl -X POST http://localhost:8000/api/v1/products/prices \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "PROD_123",
    "product_name": "iPhone 15",
    "price": 999.99,
    "currency": "USD",
    "source": "Amazon",
    "timestamp": "2024-01-01T12:00:00Z"
  }'
```

---

### Compare Product Prices

Compare prices across different sources.

**Endpoint:** `GET /api/v1/products/{product_id}/compare`

**Parameters:**
- `product_id` (path, string): Product ID

**Response:**

```json
{
  "success": true,
  "data": {
    "product_id": "PROD_123",
    "product_name": "iPhone 15",
    "prices": [
      {
        "source": "Amazon",
        "price": 999.99,
        "currency": "USD",
        "availability": "in_stock",
        "timestamp": "2024-01-01T12:00:00Z"
      },
      {
        "source": "Best Buy",
        "price": 979.99,
        "currency": "USD",
        "availability": "in_stock",
        "timestamp": "2024-01-01T12:00:00Z"
      }
    ],
    "lowest_price": 979.99,
    "highest_price": 1029.99,
    "average_price": 999.99,
    "price_range": 50.00,
    "savings_amount": 20.00,
    "savings_percent": 2.0
  }
}
```

**Example:**

```bash
curl http://localhost:8000/api/v1/products/PROD_123/compare
```

---

## Carbon Credit Endpoints 🌱

### Create Carbon Project

Create a new carbon credit project.

**Endpoint:** `POST /api/v1/carbon-credits/projects`

**Request Body:**

```json
{
  "project_id": "CC_001",
  "name": "Amazon Rainforest Conservation",
  "standard": "VCS",
  "location": "Brazil",
  "project_type": "forestry",
  "methodology": "VM0007",
  "additionality_score": 0.85,
  "co_benefits_score": 0.90,
  "status": "active",
  "description": "Forest conservation project in the Amazon",
  "total_credits_issued": 100000.00
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "project_id": "CC_001",
    "name": "Amazon Rainforest Conservation",
    "standard": "VCS",
    "location": "Brazil",
    "project_type": "forestry",
    "status": "active",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
}
```

**Example:**

```bash
curl -X POST http://localhost:8000/api/v1/carbon-credits/projects \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "CC_001",
    "name": "Amazon Rainforest Conservation",
    "standard": "VCS",
    "location": "Brazil",
    "project_type": "forestry"
  }'
```

---

### Get Environmental Impact

Get environmental impact metrics for a project.

**Endpoint:** `GET /api/v1/carbon-credits/projects/{project_id}/impact`

**Parameters:**
- `project_id` (path, string): Project ID

**Response:**

```json
{
  "success": true,
  "data": {
    "project_id": "CC_001",
    "co2_equivalent_tons": 100000.00,
    "forest_area_hectares": 500.00,
    "communities_benefited": 25,
    "biodiversity_score": 0.95,
    "sdg_contributions": "[\"SDG 13\", \"SDG 15\"]",
    "water_saved_liters": 1000000.00,
    "renewable_energy_mwh": 0.00,
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

**Example:**

```bash
curl http://localhost:8000/api/v1/carbon-credits/projects/CC_001/impact
```

---

### Get Carbon Market Overview

Get carbon market overview.

**Endpoint:** `GET /api/v1/carbon-credits/market/overview`

**Response:**

```json
{
  "success": true,
  "data": {
    "total_projects": 150,
    "active_projects": 120,
    "total_credits_issued": 5000000.00,
    "average_price_usd": 15.50,
    "price_change_24h": 0.25,
    "price_change_7d": -1.50,
    "total_volume_24h": 50000.00,
    "top_performers": [
      {
        "project_id": "CC_001",
        "name": "Amazon Rainforest Conservation",
        "price_usd": 18.50,
        "price_change_24h": 2.0
      }
    ],
    "market_trend": "bullish"
  }
}
```

**Example:**

```bash
curl http://localhost:8000/api/v1/carbon-credits/market/overview
```

---

## Health Check

### Get Health Status

Get API health status.

**Endpoint:** `GET /health`

**Response:**

```json
{
  "status": "healthy",
  "service": "HDCP Platform API",
  "version": "1.0.0",
  "environment": "development",
  "scenario": "stock"
}
```

**Example:**

```bash
curl http://localhost:8000/health
```

---

## Root Endpoint

### Get API Information

Get API information and available endpoints.

**Endpoint:** `GET /`

**Response:**

```json
{
  "name": "HDCP Platform API",
  "version": "1.0.0",
  "environment": "development",
  "scenario": "stock",
  "docs": "/docs",
  "health": "/health"
}
```

**Example:**

```bash
curl http://localhost:8000/
```

---

## GraphQL Endpoint

The platform also provides a GraphQL endpoint for flexible data querying.

**Endpoint:** `POST /graphql`

**GraphQL Playground:** http://localhost:8000/graphql

### Example GraphQL Query

```graphql
query GetStockPrice($symbol: String!) {
  stock(symbol: $symbol) {
    id
    symbol
    price
    volume
    timestamp
  }
}
```

### Variables

```json
{
  "symbol": "AAPL"
}
```

**Example:**

```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { stocks { symbol price } }"
  }'
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |

## Rate Limiting

API requests are rate-limited:
- **Default:** 100 requests per minute
- **Production:** Configurable via `RATE_LIMIT_PER_MINUTE`

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Pagination

For list endpoints, use pagination parameters:

- `page`: Page number (default: 1)
- `size`: Items per page (default: 20, max: 100)

**Example:**

```bash
curl "http://localhost:8000/api/v1/stocks/?page=2&size=50"
```

## Filtering

Most list endpoints support filtering via query parameters:

```bash
# Filter by symbol
curl "http://localhost:8000/api/v1/stocks/?symbol=AAPL"

# Filter by date range
curl "http://localhost:8000/api/v1/stocks/AAPL/history?start_date=2024-01-01&end_date=2024-01-31"
```

## Sorting

Sort results using `sort` and `order` parameters:

```bash
# Sort by price descending
curl "http://localhost:8000/api/v1/stocks/?sort=price&order=desc"
```

## SDKs and Libraries

### Python

```python
import requests

# Install: pip install hdcp-client

from hdcp_client import HDCPClient

client = HDCPClient(base_url="http://localhost:8000")

# Get stock price
stock = client.stocks.get("AAPL")
print(stock.price)
```

### JavaScript

```javascript
// Install: npm install hdcp-client

import { HDCPClient } from 'hdcp-client';

const client = new HDCPClient({
  baseURL: 'http://localhost:8000'
});

// Get stock price
const stock = await client.stocks.get('AAPL');
console.log(stock.price);
```

## Testing

Use the interactive API documentation at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## SDKs

Official SDKs will be available soon for:
- Python
- JavaScript/TypeScript
- Go
- Java

## Support

- 📚 [Documentation](README.md)
- 🐛 [GitHub Issues](https://github.com/your-org/hdcp-template/issues)
- 💬 [GitHub Discussions](https://github.com/your-org/hdcp-template/discussions)
