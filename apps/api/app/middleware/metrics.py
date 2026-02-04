import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response as StarletteResponse

# Prometheus Metrics
REQUEST_COUNT = Counter(
    'hdcp_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'hdcp_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'hdcp_active_requests',
    'Number of active requests'
)

DB_CONNECTIONS = Gauge(
    'hdcp_db_connections',
    'Number of database connections',
    ['status']
)

CACHE_HITS = Counter(
    'hdcp_cache_hits_total',
    'Total number of cache hits',
    ['result']
)

class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.start_time = None

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        self.start_time = time.time()
        ACTIVE_REQUESTS.inc()

        try:
            response = await call_next(request)

            # Record metrics
            duration = time.time() - self.start_time
            method = request.method
            endpoint = request.url.path
            status_code = str(response.status_code)

            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()

            REQUEST_DURATION.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            return response
        finally:
            ACTIVE_REQUESTS.dec()

async def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return StarletteResponse(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

class DatabaseMetrics:
    def __init__(self):
        self.connection_count = 0

    def record_connection(self, status: str):
        """Record database connection status"""
        DB_CONNECTIONS.labels(status=status).inc()

    def record_disconnection(self, status: str):
        """Record database disconnection"""
        DB_CONNECTIONS.labels(status=status).dec()

db_metrics = DatabaseMetrics()
