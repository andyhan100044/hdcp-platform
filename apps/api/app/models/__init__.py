"""
HDCP Platform Models
All database models for the platform
"""

# Import all models to ensure they're registered with SQLAlchemy
from app.core.base import Base  # noqa

# Stock Price Models
from app.models.stock import StockPrice  # noqa

# IoT Sensor Models
from app.models.iot import SensorReading  # noqa

# E-commerce Models
from app.models.ecommerce import ProductPrice  # noqa

# Carbon Credit Models
from app.models.carbon import (
    CarbonCreditProject,
    CarbonCreditPrice
)  # noqa

__all__ = [
    "Base",
    "StockPrice",
    "SensorReading",
    "ProductPrice",
    "CarbonCreditProject",
    "CarbonCreditPrice",
]
