"""
Response Models
Standardized response schemas for all API endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')


class BaseResponse(BaseModel):
    """
    Base response model with common fields
    All API responses should inherit from this
    """
    success: bool = True
    message: str = "Success"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseResponse):
    """
    Error response model
    Used when an operation fails
    """
    success: bool = False
    error_code: Optional[str] = None
    error_details: Optional[dict] = None
    trace_id: Optional[str] = None


class SuccessResponse(BaseResponse):
    """
    Success response with data
    Used for successful operations with data
    """
    data: Optional[dict] = None


class PaginatedResponse(BaseResponse, Generic[T]):
    """
    Paginated response model
    Used for list endpoints with pagination
    """
    data: List[T] = Field(default_factory=list)
    pagination: dict = Field(default_factory=lambda: {
        "page": 1,
        "page_size": 20,
        "total": 0,
        "total_pages": 0,
        "has_next": False,
        "has_previous": False
    })

    @classmethod
    def create(
        cls,
        data: List[T],
        page: int,
        page_size: int,
        total: int
    ) -> "PaginatedResponse[T]":
        """Helper to create paginated response"""
        total_pages = (total + page_size - 1) // page_size

        return cls(
            data=data,
            pagination={
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
        )
