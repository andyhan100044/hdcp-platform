"""
Stock Price Model
For stock price monitoring scenario
"""
from sqlalchemy import Column, String, DECIMAL, BigInteger, DateTime, Index, Integer
from app.core.base import TimestampedModel


class StockPrice(TimestampedModel):
    """
    Stock price data model
    Stores real-time and historical stock prices
    """
    __tablename__ = "stock_prices"

    # Stock symbol (e.g., AAPL, GOOGL)
    symbol = Column(String(20), nullable=False, index=True, comment="Stock symbol")

    # Current price
    price = Column(DECIMAL(10, 4), nullable=False, comment="Stock price")

    # Trading volume
    volume = Column(BigInteger, default=0, comment="Trading volume")

    # Price change from previous close
    price_change = Column(DECIMAL(10, 4), nullable=True, comment="Price change")

    # Percentage change
    price_change_percent = Column(DECIMAL(5, 2), nullable=True, comment="Price change %")

    # Timestamp of the price
    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Price timestamp"
    )

    # Market data source
    source = Column(String(50), nullable=True, comment="Data source")

    # Create indexes
    __table_args__ = (
        Index('idx_stock_symbol_timestamp', 'symbol', 'timestamp'),
    )


class StockIndicator(TimestampedModel):
    """
    Technical indicators for stocks
    RSI, Moving Averages, etc.
    """
    __tablename__ = "stock_indicators"

    symbol = Column(String(20), nullable=False, index=True)
    indicator_type = Column(String(50), nullable=False)  # rsi, ma, bb, etc.
    period = Column(Integer, default=14)  # Period for calculation
    value = Column(DECIMAL(10, 4), nullable=False)
    timestamp = Column(DateTime(timezone=True), index=True)

    __table_args__ = (
        Index('idx_indicator_symbol_type', 'symbol', 'indicator_type', 'timestamp'),
    )
