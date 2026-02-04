import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

from app.main import app
from app.database import Base, get_db

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_hdcp"

# Create test database engine
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db():
    """Create test database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def db_session(test_db):
    """Create test database session"""
    connection = await engine.connect()
    transaction = await connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()

@pytest.fixture
def client(db_session):
    """Create test client"""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

class TestStockAPI:
    """Test stock price endpoints"""

    def test_create_stock(self, client: TestClient):
        """Test creating a stock"""
        stock_data = {
            "symbol": "AAPL",
            "price": 150.25,
            "volume": 1000000,
            "change": 2.5,
            "change_percent": 1.69,
            "source": "Yahoo Finance"
        }
        response = client.post("/api/stocks", json=stock_data)
        assert response.status_code == 201
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert data["price"] == 150.25
        assert data["volume"] == 1000000
        assert "id" in data

    def test_get_stocks(self, client: TestClient):
        """Test getting all stocks"""
        # First create a stock
        stock_data = {
            "symbol": "GOOGL",
            "price": 2750.50,
            "volume": 500000,
            "change": -10.25,
            "change_percent": -0.37,
            "source": "Alpha Vantage"
        }
        client.post("/api/stocks", json=stock_data)

        # Get all stocks
        response = client.get("/api/stocks")
        assert response.status_code == 200
        stocks = response.json()
        assert len(stocks) > 0
        assert stocks[0]["symbol"] == "GOOGL"

    def test_get_stock(self, client: TestClient):
        """Test getting a specific stock"""
        # Create a stock
        stock_data = {
            "symbol": "MSFT",
            "price": 300.00,
            "volume": 750000,
            "change": 5.00,
            "change_percent": 1.67,
            "source": "IEX Cloud"
        }
        create_response = client.post("/api/stocks", json=stock_data)
        stock_id = create_response.json()["id"]

        # Get the stock
        response = client.get(f"/api/stocks/{stock_id}")
        assert response.status_code == 200
        stock = response.json()
        assert stock["symbol"] == "MSFT"
        assert stock["price"] == 300.00

    def test_update_stock(self, client: TestClient):
        """Test updating a stock"""
        # Create a stock
        stock_data = {
            "symbol": "TSLA",
            "price": 800.00,
            "volume": 2000000,
            "change": 20.00,
            "change_percent": 2.56,
            "source": "Yahoo Finance"
        }
        create_response = client.post("/api/stocks", json=stock_data)
        stock_id = create_response.json()["id"]

        # Update the stock
        update_data = {"price": 850.00, "volume": 2500000}
        response = client.put(f"/api/stocks/{stock_id}", json=update_data)
        assert response.status_code == 200
        updated_stock = response.json()
        assert updated_stock["price"] == 850.00
        assert updated_stock["volume"] == 2500000

    def test_delete_stock(self, client: TestClient):
        """Test deleting a stock"""
        # Create a stock
        stock_data = {
            "symbol": "AMZN",
            "price": 3200.00,
            "volume": 300000,
            "change": 50.00,
            "change_percent": 1.59,
            "source": "Alpha Vantage"
        }
        create_response = client.post("/api/stocks", json=stock_data)
        stock_id = create_response.json()["id"]

        # Delete the stock
        response = client.delete(f"/api/stocks/{stock_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Stock deleted successfully"

        # Verify it's deleted
        get_response = client.get(f"/api/stocks/{stock_id}")
        assert get_response.status_code == 404

class TestSensorAPI:
    """Test sensor reading endpoints"""

    def test_create_sensor_reading(self, client: TestClient):
        """Test creating a sensor reading"""
        sensor_data = {
            "sensor_id": "TEMP_001",
            "location": "Building A - Floor 1",
            "temperature": 22.5,
            "humidity": 45.0,
            "battery": 85,
            "signal": 90,
            "status": "online"
        }
        response = client.post("/api/sensors", json=sensor_data)
        assert response.status_code == 201
        data = response.json()
        assert data["sensor_id"] == "TEMP_001"
        assert data["temperature"] == 22.5
        assert data["battery"] == 85

    def test_get_sensors(self, client: TestClient):
        """Test getting all sensor readings"""
        sensor_data = {
            "sensor_id": "TEMP_002",
            "location": "Building B - Floor 2",
            "temperature": 24.0,
            "humidity": 50.0,
            "battery": 75,
            "signal": 85,
            "status": "online"
        }
        client.post("/api/sensors", json=sensor_data)

        response = client.get("/api/sensors")
        assert response.status_code == 200
        sensors = response.json()
        assert len(sensors) > 0
        assert sensors[0]["sensor_id"] == "TEMP_002"

class TestProductAPI:
    """Test product price endpoints"""

    def test_create_product_price(self, client: TestClient):
        """Test creating a product price"""
        product_data = {
            "product_id": "PROD_123",
            "product_name": "Wireless Headphones",
            "price": 99.99,
            "currency": "USD",
            "availability": "in_stock",
            "source": "Amazon"
        }
        response = client.post("/api/products", json=product_data)
        assert response.status_code == 201
        data = response.json()
        assert data["product_id"] == "PROD_123"
        assert data["price"] == 99.99

    def test_get_products(self, client: TestClient):
        """Test getting all product prices"""
        product_data = {
            "product_id": "PROD_456",
            "product_name": "Smart Watch",
            "price": 199.99,
            "currency": "USD",
            "availability": "in_stock",
            "source": "Best Buy"
        }
        client.post("/api/products", json=product_data)

        response = client.get("/api/products")
        assert response.status_code == 200
        products = response.json()
        assert len(products) > 0

class TestCarbonCreditAPI:
    """Test carbon credit endpoints"""

    def test_create_carbon_project(self, client: TestClient):
        """Test creating a carbon credit project"""
        project_data = {
            "project_id": "CC_001",
            "project_name": "Amazon Rainforest Conservation",
            "standard": "VCS",
            "location": "Brazil",
            "project_type": "Forestry",
            "total_credits": 100000,
            "co2_offset": 50000.0,
            "forest_area": 500.5,
            "communities": 25
        }
        response = client.post("/api/carbon-credits", json=project_data)
        assert response.status_code == 201
        data = response.json()
        assert data["project_id"] == "CC_001"
        assert data["total_credits"] == 100000

    def test_get_carbon_projects(self, client: TestClient):
        """Test getting all carbon credit projects"""
        project_data = {
            "project_id": "CC_002",
            "project_name": "Solar Energy Project",
            "standard": "Gold Standard",
            "location": "India",
            "project_type": "Renewable Energy",
            "total_credits": 50000,
            "co2_offset": 25000.0
        }
        client.post("/api/carbon-credits", json=project_data)

        response = client.get("/api/carbon-credits")
        assert response.status_code == 200
        projects = response.json()
        assert len(projects) > 0

class TestGraphQLAPI:
    """Test GraphQL endpoints"""

    def test_graphql_stocks_query(self, client: TestClient):
        """Test GraphQL stock query"""
        query = {
            "query": """
                query {
                    stocks {
                        id
                        symbol
                        price
                    }
                }
            """
        }
        response = client.post("/graphql", json=query)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "stocks" in data["data"]

    def test_graphql_create_stock_mutation(self, client: TestClient):
        """Test GraphQL stock creation mutation"""
        mutation = {
            "query": """
                mutation {
                    createStock(input: {
                        symbol: "NVDA"
                        price: 500.00
                        volume: 1000000
                        change: 10.00
                        change_percent: 2.04
                        source: "Yahoo Finance"
                    }) {
                        id
                        symbol
                        price
                    }
                }
            """
        }
        response = client.post("/graphql", json=mutation)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "createStock" in data["data"]

class TestHealthCheck:
    """Test health check endpoints"""

    def test_health_check(self, client: TestClient):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "redis" in data

    def test_metrics_endpoint(self, client: TestClient):
        """Test Prometheus metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "hdcp_requests_total" in response.text

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
