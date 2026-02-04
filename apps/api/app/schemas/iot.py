"""
IoT Sensor Schemas
Pydantic models for IoT sensor API
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class SensorReadingBase(BaseModel):
    """
    Base schema for sensor reading
    """
    sensor_id: str = Field(..., min_length=1, max_length=50, description="Sensor ID")
    location: Optional[str] = Field(None, max_length=100, description="Sensor location")
    temperature: Optional[Decimal] = Field(None, description="Temperature (°C)")
    humidity: Optional[Decimal] = Field(None, description="Humidity (%)")
    battery_level: Optional[int] = Field(None, ge=0, le=100, description="Battery level (%)")
    signal_strength: Optional[int] = Field(None, description="Signal strength (dBm)")
    metadata: Optional[str] = Field(None, description="Additional sensor data")
    timestamp: datetime = Field(..., description="Reading timestamp")
    status: str = Field(default="online", description="Sensor status")


class SensorReadingCreate(SensorReadingBase):
    """
    Schema for creating sensor reading
    """
    pass


class SensorReadingUpdate(BaseModel):
    """
    Schema for updating sensor reading
    """
    temperature: Optional[Decimal] = None
    humidity: Optional[Decimal] = None
    battery_level: Optional[int] = Field(None, ge=0, le=100)
    signal_strength: Optional[int] = None
    metadata: Optional[str] = None
    status: Optional[str] = None


class SensorReadingResponse(SensorReadingBase):
    """
    Schema for sensor reading response
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SensorAlertBase(BaseModel):
    """
    Base schema for sensor alerts
    """
    sensor_id: str
    alert_type: str  # high_temp, low_battery, offline
    severity: str  # low, medium, high, critical
    message: str = Field(..., max_length=255)
    value: Optional[Decimal] = None
    threshold: Optional[Decimal] = None


class SensorAlertResponse(SensorAlertBase):
    """
    Schema for sensor alert response
    """
    id: int
    resolved: bool
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SensorStats(BaseModel):
    """
    Schema for sensor statistics
    """
    sensor_id: str
    location: Optional[str]
    total_readings: int
    last_reading: Optional[datetime]
    avg_temperature: Optional[Decimal]
    avg_humidity: Optional[Decimal]
    avg_battery: Optional[int]
    uptime_percent: Optional[Decimal]
    alerts_count: int
