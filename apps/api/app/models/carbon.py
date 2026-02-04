"""
Carbon Credit Model
For carbon credit tracking scenario
"""
from sqlalchemy import Column, String, DECIMAL, Integer, DateTime, Index, Text
from app.core.base import TimestampedModel


class CarbonCreditProject(TimestampedModel):
    """
    Carbon credit project model
    Stores information about carbon offset projects
    """
    __tablename__ = "carbon_credit_projects"

    # Unique project identifier
    project_id = Column(String(50), primary_key=True, comment="Project ID")

    # Project name
    name = Column(String(255), nullable=False, comment="Project name")

    # Certification standard
    standard = Column(String(20), nullable=True, comment="Certification standard")

    # Project location
    location = Column(String(100), nullable=True, comment="Project location")

    # Project type (forestry, renewable, efficiency, etc.)
    project_type = Column(String(50), nullable=True, comment="Project type")

    # Methodology used
    methodology = Column(String(100), nullable=True, comment="Verification methodology")

    # Additionality score (0-1)
    additionality_score = Column(DECIMAL(3, 2), nullable=True, comment="Additionality score")

    # Permanence years
    permanence_years = Column(Integer, nullable=True, comment="Permanence (years)")

    # Co-benefits score (0-1)
    co_benefits_score = Column(DECIMAL(3, 2), nullable=True, comment="Co-benefits score")

    # Project status
    status = Column(String(20), default='active', comment="Project status")

    # Project description
    description = Column(Text, nullable=True, comment="Project description")

    # Project URL
    url = Column(String(255), nullable=True, comment="Project website")

    # Total credits issued
    total_credits_issued = Column(DECIMAL(12, 2), nullable=True, comment="Total credits (tCO2e)")

    # Create indexes
    __table_args__ = (
        Index('idx_project_standard', 'standard'),
        Index('idx_project_type', 'project_type'),
        Index('idx_project_status', 'status'),
    )


class CarbonCreditPrice(TimestampedModel):
    """
    Carbon credit price model
    Stores price history for carbon credits
    """
    __tablename__ = "carbon_credit_prices"

    # Reference to project
    project_id = Column(String(50), nullable=False, index=True, comment="Project ID")

    # Certification standard
    standard = Column(String(20), nullable=True, comment="Certification standard")

    # Price in USD per ton CO2
    price_usd = Column(DECIMAL(10, 2), nullable=False, comment="Price (USD/tCO2)")

    # Volume traded
    volume_tons = Column(DECIMAL(12, 2), nullable=True, comment="Volume (tons CO2)")

    # Data source (registry, exchange, otc)
    source = Column(String(50), nullable=True, comment="Data source")

    # Confidence level (0-1)
    confidence = Column(DECIMAL(3, 2), nullable=True, comment="Data confidence")

    # Timestamp of the price
    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Price timestamp"
    )

    # Create indexes
    __table_args__ = (
        Index('idx_price_project_timestamp', 'project_id', 'timestamp'),
        Index('idx_price_standard', 'standard'),
    )


class EnvironmentalImpact(TimestampedModel):
    """
    Environmental impact metrics
    """
    __tablename__ = "environmental_impacts"

    project_id = Column(String(50), nullable=False, index=True)

    # Total CO2 equivalent
    co2_equivalent_tons = Column(DECIMAL(12, 2), nullable=False)

    # Forest area affected
    forest_area_hectares = Column(DECIMAL(10, 2), nullable=True)

    # Communities benefited
    communities_benefited = Column(Integer, nullable=True)

    # Biodiversity score
    biodiversity_score = Column(DECIMAL(3, 2), nullable=True)

    # SDG contributions (stored as JSON)
    sdg_contributions = Column(String, nullable=True)

    # Water saved (liters)
    water_saved_liters = Column(DECIMAL(15, 2), nullable=True)

    # Renewable energy generated (MWh)
    renewable_energy_mwh = Column(DECIMAL(10, 2), nullable=True)

    timestamp = Column(DateTime(timezone=True), index=True)

    __table_args__ = (
        Index('idx_impact_project_timestamp', 'project_id', 'timestamp'),
    )
