"""
Test Configuration
Pytest configuration and fixtures
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import text

from app.config.settings import settings
from app.database import Base, get_db
from app.main import app

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://hdcp_user:hdcp_password@localhost:5432/hdcp_test_db"

# Create test database engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,
    echo=False,
    future=True,
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db():
    """Create test database tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(test_db) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    connection = await test_engine.connect()
    transaction = await connection.begin()
    session = TestSessionLocal(bind=connection)

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()


@pytest.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with overridden database dependency."""
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_stock_data():
    """Sample stock data for testing."""
    return {
        "symbol": "AAPL",
        "price": 150.25,
        "volume": 1000000,
        "price_change": 2.50,
        "price_change_percent": 1.67,
        "source": "TEST"
    }


@pytest.fixture
def sample_sensor_data():
    """Sample sensor data for testing."""
    return {
        "sensor_id": "SENSOR_001",
        "location": "Test Location",
        "temperature": 25.5,
        "humidity": 60.0,
        "battery_level": 85,
        "signal_strength": -70,
        "status": "online"
    }


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return {
        "product_id": "PROD_001",
        "product_name": "Test Product",
        "price": 99.99,
        "currency": "USD",
        "source": "test-source",
        "availability": "in_stock",
        "category": "test-category"
    }


@pytest.fixture
def sample_carbon_project_data():
    """Sample carbon project data for testing."""
    return {
        "project_id": "PROJ_001",
        "project_name": "Test Carbon Project",
        "standard": "VCS",
        "location": "Test Location",
        "project_type": "Forestry",
        "additionality_score": 85.0,
        "co_benefits_score": 90.0,
        "total_credits": 10000.0
    }


@pytest.fixture
async def create_test_data(db_session):
    """Helper fixture to create test data."""
    from app.models.stock import StockPrice
    from app.models.iot import SensorReading
    from app.models.ecommerce import ProductPrice
    from app.models.carbon import CarbonCreditProject

    # Create sample stock data
    stock = StockPrice(
        symbol="AAPL",
        price=150.25,
        volume=1000000,
        price_change=2.50,
        price_change_percent=1.67,
        source="TEST",
        timestamp=__import__('datetime').datetime.utcnow()
    )
    db_session.add(stock)

    # Create sample sensor data
    sensor = SensorReading(
        sensor_id="SENSOR_001",
        location="Test Location",
        temperature=25.5,
        humidity=60.0,
        battery_level=85,
        signal_strength=-70,
        status="online",
        timestamp=__import__('datetime').datetime.utcnow()
    )
    db_session.add(sensor)

    # Create sample product data
    product = ProductPrice(
        product_id="PROD_001",
        product_name="Test Product",
        price=99.99,
        currency="USD",
        source="test-source",
        availability="in_stock",
        category="test-category",
        timestamp=__import__('datetime').datetime.utcnow()
    )
    db_session.add(product)

    # Create sample carbon project
    project = CarbonCreditProject(
        project_id="PROJ_001",
        project_name="Test Carbon Project",
        standard="VCS",
        location="Test Location",
        project_type="Forestry",
        additionality_score=85.0,
        co_benefits_score=90.0,
        total_credits=10000.0
    )
    db_session.add(project)

    await db_session.commit()
    return {
        "stock": stock,
        "sensor": sensor,
        "product": product,
        "project": project
    }
