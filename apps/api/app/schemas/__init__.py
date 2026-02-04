"""
HDCP Platform Schemas
Pydantic models for request/response validation
"""

# Response schemas
from app.schemas.response import (
    BaseResponse,
    ErrorResponse,
    PaginatedResponse,
    SuccessResponse
)  # noqa

__all__ = [
    "BaseResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "SuccessResponse",
]
