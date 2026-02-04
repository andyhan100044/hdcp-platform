"""
E-commerce Model
For e-commerce price tracking scenario
"""
from sqlalchemy import Column, String, DECIMAL, DateTime, Index, Text, Boolean, Integer
from app.core.base import TimestampedModel


class ProductPrice(TimestampedModel):
    """
    Product price tracking model
    Stores price history from various e-commerce platforms
    """
    __tablename__ = "product_prices"

    # Unique product identifier
    product_id = Column(String(100), nullable=False, index=True, comment="Product ID")

    # Product name/title
    product_name = Column(String(255), nullable=True, comment="Product name")

    # Current price
    price = Column(DECIMAL(10, 2), nullable=False, comment="Product price")

    # Currency (USD, EUR, etc.)
    currency = Column(String(3), default="USD", comment="Currency code")

    # Price in USD for comparison
    price_usd = Column(DECIMAL(10, 2), nullable=True, comment="Price in USD")

    # Exchange rate used
    exchange_rate = Column(DECIMAL(10, 6), nullable=True, comment="Exchange rate")

    # E-commerce platform source
    source = Column(String(50), nullable=False, comment="E-commerce platform")

    # Source product URL
    source_url = Column(Text, nullable=True, comment="Product URL")

    # Availability status
    availability = Column(String(20), default="in_stock", comment="Availability status")

    # Number of items in stock
    stock_count = Column(Integer, nullable=True, comment="Stock quantity")

    # Product category
    category = Column(String(100), nullable=True, comment="Product category")

    # Timestamp of the price
    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Price timestamp"
    )

    # Create indexes
    __table_args__ = (
        Index('idx_product_id_timestamp', 'product_id', 'timestamp'),
        Index('idx_product_source', 'source'),
        Index('idx_product_category', 'category'),
    )


class PriceAlert(TimestampedModel):
    """
    Price drop alerts for products
    """
    __tablename__ = "price_alerts"

    product_id = Column(String(100), nullable=False, index=True)
    target_price = Column(DECIMAL(10, 2), nullable=False, comment="Target price")
    current_price = Column(DECIMAL(10, 2), nullable=False, comment="Current price")
    price_drop_percent = Column(DECIMAL(5, 2), nullable=False, comment="Drop percentage")
    email = Column(String(255), nullable=False, comment="Alert email")
    sent = Column(Boolean, default=False, nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index('idx_alert_product_sent', 'product_id', 'sent'),
    )
