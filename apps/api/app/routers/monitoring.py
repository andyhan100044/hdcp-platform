"""
Monitoring Routes
Health checks, metrics, and alerts
"""
from fastapi import APIRouter, Response, Request
from fastapi.responses import PlainTextResponse
from typing import Dict, Any
import json

from app.core.monitoring import (
    get_metrics,
    get_health_check,
    get_alerts,
    health_checker,
    alert_manager,
    Logger
)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

logger = Logger("monitoring")


@router.get("/health", response_model=Dict[str, Any])
async def health_endpoint():
    """
    Comprehensive health check endpoint
    Returns status of all components
    """
    try:
        result = await get_health_check()
        status_code = 200

        # Determine status code based on health
        if result["status"] == "unhealthy":
            status_code = 503
        elif result["status"] == "degraded":
            status_code = 200

        return Response(content=json.dumps(result), status_code=status_code)
    except Exception as e:
        logger.error("Health check failed", extra={"error": str(e)})
        return Response(
            content=json.dumps({
                "status": "error",
                "message": str(e)
            }),
            status_code=500
        )


@router.get("/health/{check_name}")
async def health_check_specific(check_name: str):
    """
    Get health check for a specific component
    """
    if check_name not in health_checker.checks:
        return {
            "status": "error",
            "message": f"Health check '{check_name}' not found"
        }

    try:
        result = await health_checker.checks[check_name]()
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@router.get("/metrics")
async def metrics_endpoint():
    """
    Prometheus metrics endpoint
    """
    try:
        metrics = await get_metrics()
        return Response(
            content=metrics,
            media_type=CONTENT_TYPE_LATEST
        )
    except Exception as e:
        logger.error("Metrics collection failed", extra={"error": str(e)})
        return Response(
            content=f"# Error collecting metrics: {str(e)}",
            status_code=500
        )


@router.get("/alerts", response_model=Dict[str, Any])
async def alerts_endpoint():
    """
    Get active alerts
    """
    try:
        result = await get_alerts()
        return result
    except Exception as e:
        logger.error("Alert check failed", extra={"error": str(e)})
        return {
            "error": str(e),
            "alerts": []
        }


@router.get("/info")
async def info_endpoint():
    """
    System information endpoint
    """
    import platform
    import sys
    import psutil

    return {
        "service": "HDCP API",
        "version": "1.0.0",
        "python_version": sys.version,
        "platform": platform.platform(),
        "architecture": platform.architecture(),
        "cpu_count": psutil.cpu_count(),
        "memory_total": psutil.virtual_memory().total,
        "disk_total": psutil.disk_usage('/').total,
    }


@router.post("/alerts/check")
async def check_alerts():
    """
    Manually trigger alert checks
    """
    try:
        alerts = await alert_manager.check_all()
        return {
            "status": "ok",
            "alerts_triggered": len(alerts),
            "alerts": alerts
        }
    except Exception as e:
        logger.error("Manual alert check failed", extra={"error": str(e)})
        return {
            "status": "error",
            "message": str(e)
        }


@router.get("/ready")
async def readiness_check():
    """
    Kubernetes readiness probe
    """
    # Check if service is ready to receive traffic
    try:
        # Quick database check
        from app.database import engine
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")

        return {"status": "ready"}
    except Exception:
        return Response(
            content=json.dumps({"status": "not_ready"}),
            status_code=503
        )


@router.get("/live")
async def liveness_check():
    """
    Kubernetes liveness probe
    """
    # Service is alive if this endpoint is reachable
    return {"status": "alive"}


@router.get("/status")
async def status_endpoint():
    """
    Detailed status page with all monitoring information
    """
    try:
        health = await get_health_check()
        alerts = await get_alerts()

        return {
            "service": "HDCP API",
            "status": health["status"],
            "timestamp": health["timestamp"],
            "health_checks": health["checks"],
            "alerts": alerts,
            "links": {
                "health": "/monitoring/health",
                "metrics": "/monitoring/metrics",
                "alerts": "/monitoring/alerts",
                "info": "/monitoring/info"
            }
        }
    except Exception as e:
        logger.error("Status endpoint failed", extra={"error": str(e)})
        return {
            "status": "error",
            "message": str(e)
        }
