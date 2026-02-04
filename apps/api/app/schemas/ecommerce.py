"""
E-commerce Schemas
Pydantic models for e-commerce price tracking API
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProductPriceBase(BaseModel):
    """
    Base schema for product price
    """
    product_id: str = Field(..., min_length=1, max_length=100, description="Product ID")
    product_name: Optional[str] = Field(None, max_length=255, description="Product name")
    price: Decimal = Field(..., ge=0, description="Product price")
    currency: str = Field(default="USD", max_length=3, description="Currency code")
    price_usd: Optional[Decimal] = Field(None, ge=0, description="Price in USD")
    exchange_rate: Optional[Decimal] = Field(None, ge=0, description="Exchange rate")
    source: str = Field(..., max_length=50, description="E-commerce platform")
    source_url: Optional[str] = Field(None, description="Product URL")
    availability: str = Field(default="in_stock", description="Availability status")
    stock_count: Optional[int] = Field(None, ge=0, description="Stock quantity")
    category: Optional[str] = Field(None, max_length=100, description="Product category")
    timestamp: datetime = Field(..., description="Price timestamp")


class ProductPriceCreate(ProductPriceBase):
    """
    Schema for creating product price
    """
    pass


class ProductPriceResponse(ProductPriceBase):
    """
    Schema for product price response
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PriceAlertBase(BaseModel):
    """
    Base schema for price alerts
    """
    product_id: str
    target_price: Decimal = Field(..., ge=0, description="Target price")
    current_price: Decimal = Field(..., ge=0, description="Current price")
    price_drop_percent: Decimal = Field(..., description="Drop percentage")
    email: str = Field(..., description="Alert email")


class PriceAlertResponse(PriceAlertBase):
    """
    Schema for price alert response
    """
    id: int
    sent: bool
    sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PriceHistoryRequest(BaseModel):
    """
    Schema for price history request
    """
    product_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    source: Optional[str] = None


class ProductComparison(BaseModel):
    """
    Schema for product price comparison
    """
    product_id: str
    product_name: Optional[str]
    prices: list[ProductPriceResponse]
    lowest_price: Decimal
    highest_price: Decimal
    average_price: Decimal
    price_range: Decimal
    savings_amount: Decimal
    savings_percent: Decimal
