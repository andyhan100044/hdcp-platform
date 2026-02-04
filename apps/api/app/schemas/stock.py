"""
Stock Price Schemas
Pydantic models for stock price API
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal


class StockPriceBase(BaseModel):
    """
    Base schema for stock price data
    """
    symbol: str = Field(..., min_length=1, max_length=20, description="Stock symbol")
    price: Decimal = Field(..., ge=0, description="Stock price")
    volume: int = Field(default=0, ge=0, description="Trading volume")
    price_change: Optional[Decimal] = Field(None, description="Price change")
    price_change_percent: Optional[Decimal] = Field(None, description="Price change percentage")
    timestamp: datetime = Field(..., description="Price timestamp")
    source: Optional[str] = Field(None, max_length=50, description="Data source")


class StockPriceCreate(StockPriceBase):
    """
    Schema for creating stock price
    """
    pass


class StockPriceUpdate(BaseModel):
    """
    Schema for updating stock price
    """
    price: Optional[Decimal] = Field(None, ge=0)
    volume: Optional[int] = Field(None, ge=0)
    price_change: Optional[Decimal] = None
    price_change_percent: Optional[Decimal] = None


class StockPriceResponse(StockPriceBase):
    """
    Schema for stock price response
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StockSummary(BaseModel):
    """
    Schema for stock summary data
    """
    symbol: str
    current_price: Decimal
    price_change: Optional[Decimal] = None
    price_change_percent: Optional[Decimal] = None
    volume: int = 0
    market_cap: Optional[Decimal] = None
    high_52w: Optional[Decimal] = None
    low_52w: Optional[Decimal] = None
    last_updated: datetime


class StockHistoryRequest(BaseModel):
    """
    Schema for stock history request
    """
    symbol: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    interval: str = Field(default="1d", description="Data interval (1h, 1d, 1w)")

    @validator('interval')
    def validate_interval(cls, v):
        allowed = ['1h', '1d', '1w', '1mo']
        if v not in allowed:
            raise ValueError(f'Interval must be one of: {allowed}')
        return v


class StockIndicatorBase(BaseModel):
    """
    Base schema for stock indicators
    """
    symbol: str
    indicator_type: str  # rsi, ma, bb, etc.
    period: int = 14
    value: Decimal
    timestamp: datetime


class StockIndicatorResponse(StockIndicatorBase):
    """
    Schema for stock indicator response
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
