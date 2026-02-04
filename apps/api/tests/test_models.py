"""
Model Tests
Test database models
"""
import pytest
from datetime import datetime
from sqlalchemy import inspect

from app.models.stock import StockPrice, StockIndicator
from app.models.iot import SensorReading, SensorAlert
from app.models.ecommerce import ProductPrice, PriceAlert
from app.models.carbon import CarbonCreditProject, CarbonCreditPrice


class TestStockPriceModel:
    """Test StockPrice model"""

    @pytest.mark.unit
    def test_stock_price_creation(self, db_session):
        """Test creating a stock price"""
        stock = StockPrice(
            symbol="AAPL",
            price=150.25,
            volume=1000000,
            price_change=2.50,
            price_change_percent=1.67,
            source="TEST",
            timestamp=datetime.utcnow()
        )
        db_session.add(stock)
        db_session.commit()

        assert stock.id is not None
        assert stock.symbol == "AAPL"
        assert stock.price == 150.25
        assert stock.volume == 1000000
        assert stock.created_at is not None
        assert stock.updated_at is not None

    @pytest.mark.unit
    def test_stock_price_indexes(self, db_session):
        """Test stock price indexes"""
        stock = StockPrice(
            symbol="GOOGL",
            price=2500.00,
            volume=500000,
            timestamp=datetime.utcnow()
        )
        db_session.add(stock)
        db_session.commit()

        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes('stock_prices')
        index_names = [idx['name'] for idx in indexes]

        assert 'idx_stock_symbol_timestamp' in index_names

    @pytest.mark.unit
    def test_stock_price_required_fields(self, db_session):
        """Test required fields validation"""
        stock = StockPrice(
            timestamp=datetime.utcnow()
        )
        db_session.add(stock)

        with pytest.raises(Exception):
            db_session.commit()

    @pytest.mark.unit
    def test_stock_price_optional_fields(self, db_session):
        """Test optional fields"""
        stock = StockPrice(
            symbol="MSFT",
            price=300.00,
            timestamp=datetime.utcnow()
        )
        db_session.add(stock)
        db_session.commit()

        assert stock.price_change is None
        assert stock.price_change_percent is None
        assert stock.source is None


class TestStockIndicatorModel:
    """Test StockIndicator model"""

    @pytest.mark.unit
    def test_stock_indicator_creation(self, db_session):
        """Test creating a stock indicator"""
        indicator = StockIndicator(
            symbol="AAPL",
            indicator_type="RSI",
            period=14,
            value=65.5,
            timestamp=datetime.utcnow()
        )
        db_session.add(indicator)
        db_session.commit()

        assert indicator.id is not None
        assert indicator.symbol == "AAPL"
        assert indicator.indicator_type == "RSI"
        assert indicator.period == 14
        assert indicator.value == 65.5

    @pytest.mark.unit
    def test_stock_indicator_indexes(self, db_session):
        """Test indicator indexes"""
        indicator = StockIndicator(
            symbol="TSLA",
            indicator_type="MA",
            value=200.0,
            timestamp=datetime.utcnow()
        )
        db_session.add(indicator)
        db_session.commit()

        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes('stock_indicators')
        index_names = [idx['name'] for idx in indexes]

        assert 'idx_indicator_symbol_type' in index_names


class TestSensorReadingModel:
    """Test SensorReading model"""

    @pytest.mark.unit
    def test_sensor_reading_creation(self, db_session):
        """Test creating a sensor reading"""
        reading = SensorReading(
            sensor_id="SENSOR_001",
            location="Lab A",
            temperature=23.5,
            humidity=55.0,
            battery_level=90,
            signal_strength=-65,
            status="online",
            timestamp=datetime.utcnow()
        )
        db_session.add(reading)
        db_session.commit()

        assert reading.id is not None
        assert reading.sensor_id == "SENSOR_001"
        assert reading.location == "Lab A"
        assert reading.temperature == 23.5
        assert reading.humidity == 55.0
        assert reading.battery_level == 90
        assert reading.signal_strength == -65
        assert reading.status == "online"

    @pytest.mark.unit
    def test_sensor_reading_indexes(self, db_session):
        """Test sensor reading indexes"""
        reading = SensorReading(
            sensor_id="SENSOR_002",
            timestamp=datetime.utcnow()
        )
        db_session.add(reading)
        db_session.commit()

        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes('sensor_readings')
        index_names = [idx['name'] for idx in indexes]

        assert 'idx_sensor_id_timestamp' in index_names
        assert 'idx_sensor_location' in index_names

    @pytest.mark.unit
    def test_sensor_reading_metadata_field(self, db_session):
        """Test sensor metadata field (renamed from 'metadata')"""
        reading = SensorReading(
            sensor_id="SENSOR_003",
            timestamp=datetime.utcnow(),
            sensor_metadata='{"custom": "data"}'
        )
        db_session.add(reading)
        db_session.commit()

        assert reading.sensor_metadata == '{"custom": "data"}'


class TestSensorAlertModel:
    """Test SensorAlert model"""

    @pytest.mark.unit
    def test_sensor_alert_creation(self, db_session):
        """Test creating a sensor alert"""
        alert = SensorAlert(
            sensor_id="SENSOR_001",
            alert_type="high_temp",
            severity="high",
            message="Temperature exceeded threshold",
            value=30.0,
            threshold=25.0,
            resolved=False
        )
        db_session.add(alert)
        db_session.commit()

        assert alert.id is not None
        assert alert.sensor_id == "SENSOR_001"
        assert alert.alert_type == "high_temp"
        assert alert.severity == "high"
        assert alert.resolved is False
        assert alert.resolved_at is None
        assert alert.resolved_by is None

    @pytest.mark.unit
    def test_sensor_alert_resolution(self, db_session):
        """Test resolving an alert"""
        alert = SensorAlert(
            sensor_id="SENSOR_001",
            alert_type="low_battery",
            severity="medium",
            message="Battery level low",
            value=15.0,
            threshold=20.0,
            resolved=False
        )
        db_session.add(alert)
        db_session.commit()

        # Resolve the alert
        alert.resolved = True
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = "admin"
        db_session.commit()

        assert alert.resolved is True
        assert alert.resolved_at is not None
        assert alert.resolved_by == "admin"


class TestProductPriceModel:
    """Test ProductPrice model"""

    @pytest.mark.unit
    def test_product_price_creation(self, db_session):
        """Test creating a product price"""
        product = ProductPrice(
            product_id="PROD_001",
            product_name="Test Product",
            price=99.99,
            currency="USD",
            source="test-source",
            availability="in_stock",
            category="electronics",
            timestamp=datetime.utcnow()
        )
        db_session.add(product)
        db_session.commit()

        assert product.id is not None
        assert product.product_id == "PROD_001"
        assert product.product_name == "Test Product"
        assert product.price == 99.99
        assert product.currency == "USD"
        assert product.source == "test-source"
        assert product.availability == "in_stock"
        assert product.category == "electronics"

    @pytest.mark.unit
    def test_product_price_indexes(self, db_session):
        """Test product price indexes"""
        product = ProductPrice(
            product_id="PROD_002",
            price=199.99,
            currency="EUR",
            source="test-source-2",
            timestamp=datetime.utcnow()
        )
        db_session.add(product)
        db_session.commit()

        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes('product_prices')
        index_names = [idx['name'] for idx in indexes]

        assert 'idx_product_id_timestamp' in index_names
        assert 'idx_product_source' in index_names
        assert 'idx_product_category' in index_names


class TestPriceAlertModel:
    """Test PriceAlert model"""

    @pytest.mark.unit
    def test_price_alert_creation(self, db_session):
        """Test creating a price alert"""
        alert = PriceAlert(
            product_id="PROD_001",
            target_price=89.99,
            current_price=99.99,
            price_drop_percent=10.0,
            email="test@example.com",
            sent=False
        )
        db_session.add(alert)
        db_session.commit()

        assert alert.id is not None
        assert alert.product_id == "PROD_001"
        assert alert.target_price == 89.99
        assert alert.current_price == 99.99
        assert alert.price_drop_percent == 10.0
        assert alert.email == "test@example.com"
        assert alert.sent is False
        assert alert.sent_at is None

    @pytest.mark.unit
    def test_price_alert_sent(self, db_session):
        """Test marking alert as sent"""
        alert = PriceAlert(
            product_id="PROD_002",
            target_price=49.99,
            current_price=59.99,
            price_drop_percent=16.67,
            email="user@example.com",
            sent=False
        )
        db_session.add(alert)
        db_session.commit()

        # Mark as sent
        alert.sent = True
        alert.sent_at = datetime.utcnow()
        db_session.commit()

        assert alert.sent is True
        assert alert.sent_at is not None


class TestCarbonCreditProjectModel:
    """Test CarbonCreditProject model"""

    @pytest.mark.unit
    def test_carbon_project_creation(self, db_session):
        """Test creating a carbon credit project"""
        project = CarbonCreditProject(
            project_id="PROJ_001",
            project_name="Test Forest Project",
            standard="VCS",
            location="Brazil",
            project_type="Forestry",
            additionality_score=85.0,
            co_benefits_score=90.0,
            total_credits=10000.0,
            verified_credits=8000.0,
            retired_credits=2000.0,
            description="Test project description"
        )
        db_session.add(project)
        db_session.commit()

        assert project.id is not None
        assert project.project_id == "PROJ_001"
        assert project.project_name == "Test Forest Project"
        assert project.standard == "VCS"
        assert project.location == "Brazil"
        assert project.project_type == "Forestry"
        assert project.additionality_score == 85.0
        assert project.co_benefits_score == 90.0
        assert project.total_credits == 10000.0
        assert project.verified_credits == 8000.0
        assert project.retired_credits == 2000.0

    @pytest.mark.unit
    def test_carbon_project_unique_id(self, db_session):
        """Test project ID uniqueness"""
        project1 = CarbonCreditProject(
            project_id="PROJ_002",
            project_name="Project 1",
            standard="Gold Standard",
            location="Kenya",
            project_type="Renewable Energy"
        )
        db_session.add(project1)
        db_session.commit()

        # Try to create duplicate
        project2 = CarbonCreditProject(
            project_id="PROJ_002",
            project_name="Project 2",
            standard="VCS",
            location="India",
            project_type="Solar"
        )
        db_session.add(project2)

        with pytest.raises(Exception):
            db_session.commit()


class TestCarbonCreditPriceModel:
    """Test CarbonCreditPrice model"""

    @pytest.mark.unit
    def test_carbon_price_creation(self, db_session):
        """Test creating a carbon credit price"""
        price = CarbonCreditPrice(
            project_id="PROJ_001",
            price_per_credit=15.50,
            currency="USD",
            timestamp=datetime.utcnow(),
            source="Carbon Exchange"
        )
        db_session.add(price)
        db_session.commit()

        assert price.id is not None
        assert price.project_id == "PROJ_001"
        assert price.price_per_credit == 15.50
        assert price.currency == "USD"
        assert price.source == "Carbon Exchange"

    @pytest.mark.unit
    def test_carbon_price_indexes(self, db_session):
        """Test carbon price indexes"""
        price = CarbonCreditPrice(
            project_id="PROJ_002",
            price_per_credit=20.00,
            currency="EUR",
            timestamp=datetime.utcnow(),
            source="Test Exchange"
        )
        db_session.add(price)
        db_session.commit()

        inspector = inspect(db_session.bind)
        indexes = inspector.get_indexes('carbon_credit_prices')
        index_names = [idx['name'] for idx in indexes]

        assert 'idx_carbon_price_project_timestamp' in index_names
        assert 'idx_carbon_price_timestamp' in index_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
