"""
IoT Sensor Model
For IoT sensor data monitoring scenario
"""
from sqlalchemy import Column, String, DECIMAL, Integer, DateTime, Index, Boolean
from app.core.base import TimestampedModel


class SensorReading(TimestampedModel):
    """
    IoT sensor reading data model
    Stores temperature, humidity, and other sensor data
    """
    __tablename__ = "sensor_readings"

    # Unique sensor identifier
    sensor_id = Column(String(50), nullable=False, index=True, comment="Sensor ID")

    # Sensor location
    location = Column(String(100), nullable=True, comment="Sensor location")

    # Temperature reading
    temperature = Column(DECIMAL(5, 2), nullable=True, comment="Temperature (°C)")

    # Humidity reading
    humidity = Column(DECIMAL(5, 2), nullable=True, comment="Humidity (%)")

    # Battery level (0-100)
    battery_level = Column(Integer, nullable=True, comment="Battery level (%)")

    # Signal strength
    signal_strength = Column(Integer, nullable=True, comment="Signal strength (dBm)")

    # Additional sensor data as JSON
    sensor_metadata = Column(String, nullable=True, comment="Additional sensor data")

    # Timestamp of the reading
    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Reading timestamp"
    )

    # Status (online, offline, error)
    status = Column(String(20), default="online", comment="Sensor status")

    # Create indexes
    __table_args__ = (
        Index('idx_sensor_id_timestamp', 'sensor_id', 'timestamp'),
        Index('idx_sensor_location', 'location'),
    )


class SensorAlert(TimestampedModel):
    """
    Alerts generated from sensor readings
    High temperature, low battery, etc.
    """
    __tablename__ = "sensor_alerts"

    sensor_id = Column(String(50), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)  # high_temp, low_battery, offline
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    message = Column(String(255), nullable=False)
    value = Column(DECIMAL(10, 4), nullable=True)  # Value that triggered alert
    threshold = Column(DECIMAL(10, 4), nullable=True)  # Threshold value
    resolved = Column(Boolean, default=False, nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(String(100), nullable=True)

    __table_args__ = (
        Index('idx_alert_sensor_resolved', 'sensor_id', 'resolved'),
        Index('idx_alert_severity', 'severity'),
    )
