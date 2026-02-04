"""
Monitoring and Observability
Structured logging, metrics, and health checks
"""
import time
import logging
import json
import psutil
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import Request, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse


# Prometheus Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_active',
    'Number of active HTTP requests'
)

DB_POOL_CONNECTIONS = Gauge(
    'db_pool_connections',
    'Database pool connections',
    ['state']
)

MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    'Memory usage in bytes'
)

CPU_USAGE = Gauge(
    'cpu_usage_percent',
    'CPU usage percentage'
)


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured logging"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request
        logger = get_logger("http_requests")
        logger.info(
            "Request started",
            extra={
                "event_type": "request_start",
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )

        ACTIVE_REQUESTS.inc()

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # Log response
            logger.info(
                "Request completed",
                extra={
                    "event_type": "request_end",
                    "method": request.method,
                    "url": str(request.url),
                    "status_code": response.status_code,
                    "duration": process_time,
                }
            )

            # Record metrics
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code
            ).inc()

            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(process_time)

            return response

        except Exception as e:
            process_time = time.time() - start_time

            # Log error
            logger.error(
                "Request failed",
                extra={
                    "event_type": "request_error",
                    "method": request.method,
                    "url": str(request.url),
                    "error": str(e),
                    "duration": process_time,
                },
                exc_info=True
            )

            raise

        finally:
            ACTIVE_REQUESTS.dec()


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting system metrics"""

    async def dispatch(self, request: Request, call_next):
        # Update system metrics
        MEMORY_USAGE.set(psutil.virtual_memory().used)
        CPU_USAGE.set(psutil.cpu_percent())

        response = await call_next(request)
        return response


class HealthChecker:
    """Health check manager"""

    def __init__(self):
        self.checks = {}

    def register_check(self, name: str, check_func):
        """Register a health check function"""
        self.checks[name] = check_func

    async def check_all(self) -> Dict[str, Any]:
        """Run all registered health checks"""
        results = {}
        overall_status = "healthy"

        for name, check_func in self.checks.items():
            try:
                result = await check_func()
                results[name] = result
                if result["status"] != "healthy":
                    overall_status = "degraded"
            except Exception as e:
                results[name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                overall_status = "unhealthy"

        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": results
        }


# Global health checker instance
health_checker = HealthChecker()


# Built-in health checks
async def check_database():
    """Check database health"""
    try:
        from app.database import engine
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }


async def check_redis():
    """Check Redis health"""
    try:
        from app.core.performance import cache_manager
        if not cache_manager.redis_client:
            return {
                "status": "degraded",
                "message": "Redis client not initialized"
            }
        await cache_manager.redis_client.ping()
        return {
            "status": "healthy",
            "message": "Redis connection successful"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Redis connection failed: {str(e)}"
        }


async def check_memory():
    """Check memory usage"""
    memory = psutil.virtual_memory()
    percent = memory.percent

    if percent > 90:
        status = "unhealthy"
    elif percent > 80:
        status = "degraded"
    else:
        status = "healthy"

    return {
        "status": status,
        "message": f"Memory usage: {percent}%",
        "details": {
            "total": memory.total,
            "used": memory.used,
            "free": memory.free,
            "percent": percent
        }
    }


async def check_disk():
    """Check disk usage"""
    disk = psutil.disk_usage('/')
    percent = disk.percent

    if percent > 95:
        status = "unhealthy"
    elif percent > 85:
        status = "degraded"
    else:
        status = "healthy"

    return {
        "status": status,
        "message": f"Disk usage: {percent}%",
        "details": {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": percent
        }
    }


# Register built-in checks
health_checker.register_check("database", check_database)
health_checker.register_check("redis", check_redis)
health_checker.register_check("memory", check_memory)
health_checker.register_check("disk", check_disk)


class Logger:
    """Structured logger with JSON output"""

    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Create handler if not exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _log(self, level: str, message: str, extra: Optional[Dict] = None):
        """Internal log method"""
        if extra:
            # Add structured data to log record
            self.logger.log(
                getattr(logging, level.upper()),
                message,
                extra=extra
            )
        else:
            getattr(self.logger, level.lower())(message)

    def info(self, message: str, extra: Optional[Dict] = None):
        self._log("INFO", message, extra)

    def warning(self, message: str, extra: Optional[Dict] = None):
        self._log("WARNING", message, extra)

    def error(self, message: str, extra: Optional[Dict] = None, exc_info: bool = False):
        self._log("ERROR", message, extra)
        if exc_info:
            self.logger.exception(message)

    def debug(self, message: str, extra: Optional[Dict] = None):
        self._log("DEBUG", message, extra)


# Global loggers cache
_loggers: Dict[str, Logger] = {}


def get_logger(name: str, level: str = "INFO") -> Logger:
    """Get or create a logger"""
    if name not in _loggers:
        _loggers[name] = Logger(name, level)
    return _loggers[name]


class AlertManager:
    """Alert management for monitoring"""

    def __init__(self):
        self.rules = []
        self.active_alerts = {}

    def add_rule(self, name: str, condition: callable, severity: str = "warning"):
        """Add an alert rule"""
        self.rules.append({
            "name": name,
            "condition": condition,
            "severity": severity
        })

    async def check_all(self):
        """Check all alert rules"""
        alerts = []
        for rule in self.rules:
            try:
                triggered = await rule["condition"]()
                if triggered:
                    alert = {
                        "name": rule["name"],
                        "severity": rule["severity"],
                        "timestamp": datetime.utcnow().isoformat(),
                        "status": "firing"
                    }
                    alerts.append(alert)

                    # Store active alert
                    self.active_alerts[rule["name"]] = alert
            except Exception as e:
                logger = get_logger("alerts")
                logger.error(f"Alert rule check failed: {rule['name']}", extra={
                    "error": str(e)
                })

        return alerts

    async def resolve_alerts(self, alert_names: list):
        """Resolve active alerts"""
        for name in alert_names:
            if name in self.active_alerts:
                self.active_alerts[name]["status"] = "resolved"
                self.active_alerts[name]["resolved_at"] = datetime.utcnow().isoformat()


# Global alert manager
alert_manager = AlertManager()


# Pre-defined alert rules
async def high_memory_alert():
    """Alert when memory usage > 85%"""
    memory = psutil.virtual_memory()
    return memory.percent > 85


async def high_cpu_alert():
    """Alert when CPU usage > 80%"""
    return psutil.cpu_percent(interval=1) > 80


async def low_disk_alert():
    """Alert when disk usage > 90%"""
    disk = psutil.disk_usage('/')
    return disk.percent > 90


# Register default alert rules
alert_manager.add_rule("high_memory", high_memory_alert, "critical")
alert_manager.add_rule("high_cpu", high_cpu_alert, "warning")
alert_manager.add_rule("low_disk", low_disk_alert, "critical")


async def get_metrics() -> str:
    """Get Prometheus metrics"""
    return generate_latest()


async def get_health_check() -> Dict[str, Any]:
    """Get comprehensive health check"""
    return await health_checker.check_all()


async def get_alerts() -> Dict[str, Any]:
    """Get active alerts"""
    await alert_manager.check_all()
    return {
        "alerts": list(alert_manager.active_alerts.values()),
        "count": len(alert_manager.active_alerts)
    }
