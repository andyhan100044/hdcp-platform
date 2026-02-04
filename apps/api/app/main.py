"""
HDCP Platform API
FastAPI application main entry point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config.settings import settings
from app.config.security import security_config
from app.database import init_db, close_db

# Import security middleware
from app.middleware.security import (
    SecurityHeadersMiddleware,
    CSRFProtectionMiddleware,
    SQLInjectionProtectionMiddleware,
    RateLimitByUserMiddleware,
    InputValidationMiddleware,
)

# Import monitoring middleware
from app.core.monitoring import (
    StructuredLoggingMiddleware,
    MetricsMiddleware,
    get_logger
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await init_db()
    from app.core.performance import init_cache
    await init_cache()
    yield
    # Shutdown
    from app.core.performance import close_cache
    await close_cache()
    await close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Universal data platform template with multi-language support",
    lifespan=lifespan,
    debug=settings.debug,
)

# Add CORS middleware with security configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=security_config.get_allowed_origins(),
    allow_credentials=security_config.settings.CORS_CREDENTIALS,
    allow_methods=security_config.settings.CORS_METHODS,
    allow_headers=security_config.settings.CORS_HEADERS,
)

# Add monitoring middleware (should be first to capture all requests)
app.add_middleware(StructuredLoggingMiddleware)
app.add_middleware(MetricsMiddleware)

# Add security middleware (order matters - added in reverse execution order)
if security_config.settings.SECURITY_HEADERS_ENABLED:
    app.add_middleware(SecurityHeadersMiddleware)

if security_config.settings.CSRF_PROTECTION_ENABLED:
    app.add_middleware(CSRFProtectionMiddleware)

app.add_middleware(SQLInjectionProtectionMiddleware)
app.add_middleware(InputValidationMiddleware)

# Add rate limiting middleware with configured limits
app.add_middleware(
    RateLimitByUserMiddleware,
    requests_per_minute=security_config.settings.RATE_LIMIT_PER_MINUTE
)

# Include routers based on active scenario
@app.on_event("startup")
async def include_routes():
    """Include routers based on active scenario"""
    from app.routers import stock, iot, ecommerce, carbon, monitoring, graphql

    # Always include monitoring routes
    app.include_router(monitoring.router, prefix="/api/v1")

    # Include scenario-specific routes
    if settings.active_scenario == "stock":
        app.include_router(stock.router, prefix="/api/v1")
    elif settings.active_scenario == "iot":
        app.include_router(iot.router, prefix="/api/v1")
    elif settings.active_scenario == "ecommerce":
        app.include_router(ecommerce.router, prefix="/api/v1")
    elif settings.active_scenario == "carbon":
        app.include_router(carbon.router, prefix="/api/v1")
    elif settings.active_scenario == "all":
        # Include all routes for development/testing
        app.include_router(stock.router, prefix="/api/v1/stocks")
        app.include_router(iot.router, prefix="/api/v1/sensors")
        app.include_router(ecommerce.router, prefix="/api/v1/products")
        app.include_router(carbon.router, prefix="/api/v1/carbon-credits")

    # Always include GraphQL
    app.include_router(graphql.router, prefix="/graphql")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "scenario": settings.active_scenario
    }


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "scenario": settings.active_scenario,
        "docs": "/docs",
        "health": "/health"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": str(exc) if settings.debug else "An error occurred",
            "path": str(request.url.path)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
