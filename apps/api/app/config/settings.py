"""
HDCP Platform Settings
Configuration management for the FastAPI backend
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    app_name: str = "HDCP Platform API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str
    database_echo: bool = False

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl: int = 300  # 5 minutes

    # Security
    secret_key: str
    api_key_header_name: str = "X-API-Key"
    access_token_expire_minutes: int = 30

    # CORS
    cors_origins: List[AnyHttpUrl] = []

    # Rate Limiting
    rate_limit_per_minute: int = 100
    rate_limit_per_hour: int = 1000

    # Multi-language
    default_locale: str = "en"
    supported_locales: List[str] = [
        "en", "zh-CN", "es", "fr", "de", "ja", "ko", "ar"
    ]

    # Scenarios
    # Change this to activate a scenario: "stock", "iot", "ecommerce", "carbon"
    active_scenario: str = "stock"

    # Scenario configurations
    scenario_configs: dict = {
        "stock": {
            "name": "Stock Price Monitoring",
            "enabled": True,
            "features": ["real-time-prices", "historical-data", "charts"]
        },
        "iot": {
            "name": "IoT Sensor Data",
            "enabled": True,
            "features": ["real-time-monitoring", "alerts", "battery-status"]
        },
        "ecommerce": {
            "name": "E-commerce Price Tracking",
            "enabled": True,
            "features": ["price-comparison", "market-analysis", "alerts"]
        },
        "carbon": {
            "name": "Carbon Credit Tracking",
            "enabled": True,
            "features": ["environmental-impact", "certifications", "market-prices"]
        }
    }

    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 8001

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
