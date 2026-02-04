"""
Base Model Classes
Common base classes for all database models
"""
from sqlalchemy import Column, Integer, DateTime, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from typing import Optional

Base = declarative_base()


class TimestampedModel(Base):
    """
    Abstract base class with automatic timestamp columns
    All models should inherit from this
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class AuditLogModel(Base):
    """
    Abstract base class for models that need audit logging
    """
    __abstract__ = True

    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
    version = Column(Integer, default=1, nullable=False)
    notes = Column(Text, nullable=True)
