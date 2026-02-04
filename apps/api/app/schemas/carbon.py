"""
Carbon Credit Schemas
Pydantic models for carbon credit API
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class CarbonCreditProjectBase(BaseModel):
    """
    Base schema for carbon credit project
    """
    project_id: str = Field(..., min_length=1, max_length=50, description="Project ID")
    name: str = Field(..., max_length=255, description="Project name")
    standard: Optional[str] = Field(None, max_length=20, description="Certification standard")
    location: Optional[str] = Field(None, max_length=100, description="Project location")
    project_type: Optional[str] = Field(None, max_length=50, description="Project type")
    methodology: Optional[str] = Field(None, max_length=100, description="Verification methodology")
    additionality_score: Optional[Decimal] = Field(None, ge=0, le=1, description="Additionality score")
    permanence_years: Optional[int] = Field(None, ge=0, description="Permanence (years)")
    co_benefits_score: Optional[Decimal] = Field(None, ge=0, le=1, description="Co-benefits score")
    status: str = Field(default='active', description="Project status")
    description: Optional[str] = Field(None, description="Project description")
    url: Optional[str] = Field(None, description="Project website")
    total_credits_issued: Optional[Decimal] = Field(None, ge=0, description="Total credits (tCO2e)")


class CarbonCreditProjectCreate(CarbonCreditProjectBase):
    """
    Schema for creating carbon credit project
    """
    pass


class CarbonCreditProjectResponse(CarbonCreditProjectBase):
    """
    Schema for carbon credit project response
    """
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CarbonCreditPriceBase(BaseModel):
    """
    Base schema for carbon credit price
    """
    project_id: str = Field(..., description="Project ID")
    standard: Optional[str] = Field(None, max_length=20, description="Certification standard")
    price_usd: Decimal = Field(..., ge=0, description="Price (USD/tCO2)")
    volume_tons: Optional[Decimal] = Field(None, ge=0, description="Volume (tons CO2)")
    source: Optional[str] = Field(None, max_length=50, description="Data source")
    confidence: Optional[Decimal] = Field(None, ge=0, le=1, description="Data confidence")
    timestamp: datetime = Field(..., description="Price timestamp")


class CarbonCreditPriceCreate(CarbonCreditPriceBase):
    """
    Schema for creating carbon credit price
    """
    pass


class CarbonCreditPriceResponse(CarbonCreditPriceBase):
    """
    Schema for carbon credit price response
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EnvironmentalImpactBase(BaseModel):
    """
    Base schema for environmental impact
    """
    project_id: str = Field(..., description="Project ID")
    co2_equivalent_tons: Decimal = Field(..., ge=0, description="CO2 equivalent (tons)")
    forest_area_hectares: Optional[Decimal] = Field(None, ge=0, description="Forest area (hectares)")
    communities_benefited: Optional[int] = Field(None, ge=0, description="Communities benefited")
    biodiversity_score: Optional[Decimal] = Field(None, ge=0, le=1, description="Biodiversity score")
    sdg_contributions: Optional[str] = Field(None, description="SDG contributions (JSON)")
    water_saved_liters: Optional[Decimal] = Field(None, ge=0, description="Water saved (liters)")
    renewable_energy_mwh: Optional[Decimal] = Field(None, ge=0, description="Renewable energy (MWh)")
    timestamp: datetime = Field(..., description="Impact timestamp")


class EnvironmentalImpactResponse(EnvironmentalImpactBase):
    """
    Schema for environmental impact response
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CarbonMarketOverview(BaseModel):
    """
    Schema for carbon market overview
    """
    total_projects: int
    active_projects: int
    total_credits_issued: Decimal
    average_price_usd: Decimal
    price_change_24h: Optional[Decimal] = None
    price_change_7d: Optional[Decimal] = None
    total_volume_24h: Optional[Decimal] = None
    top_performers: list[dict]
    market_trend: str  # bullish, bearish, neutral
