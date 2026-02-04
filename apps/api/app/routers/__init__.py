"""
HDCP Platform API Routers
API route handlers for all scenarios
"""

from app.routers import stock, iot, ecommerce, carbon, monitoring, graphql  # noqa

__all__ = [
    "stock",
    "iot",
    "ecommerce",
    "carbon",
    "monitoring",
    "graphql"
]
