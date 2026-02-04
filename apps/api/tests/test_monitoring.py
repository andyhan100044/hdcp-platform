"""
Monitoring Tests
Test health checks, metrics, and alerting
"""
import pytest
import json
from unittest.mock import patch, MagicMock

from app.core.monitoring import (
    health_checker,
    alert_manager,
    Logger,
    get_logger,
    REQUEST_COUNT,
    MEMORY_USAGE
)


class TestHealthChecks:
    """Test health check functionality"""

    @pytest.mark.monitoring
    @pytest.mark.asyncio
    async def test_register_health_check(self):
        """Test registering a custom health check"""
        async def custom_check():
            return {
                "status": "healthy",
                "message": "Custom check OK"
            }

        health_checker.register_check("custom", custom_check)
        assert "custom" in health_checker.checks

        result = await health_checker.check_all()
        assert "custom" in result["checks"]
        assert result["checks"]["custom"]["status"] == "healthy"

    @pytest.mark.monitoring
    @pytest.mark.asyncio
    async def test_database_health_check(self):
        """Test database health check"""
        result = await health_checker.checks["database"]()
        assert "status" in result
        assert "message" in result
        assert result["status"] in ["healthy", "degraded", "unhealthy"]

    @pytest.mark.monitoring
    @pytest.mark.asyncio
    async def test_memory_health_check(self):
        """Test memory health check"""
        result = await health_checker.checks["memory"]()
        assert "status" in result
        assert "message" in result
        assert "details" in result
        assert "percent" in result["details"]

    @pytest.mark.monitoring
    @pytest.mark.asyncio
    async def test_disk_health_check(self):
        """Test disk health check"""
        result = await health_checker.checks["disk"]()
        assert "status" in result
        assert "message" in result
        assert "details" in result

    @pytest.mark.monitoring
    @pytest.mark.asyncio
    async def test_comprehensive_health_check(self):
        """Test running all health checks"""
        from app.core.monitoring import get_health_check

        result = await get_health_check()

        assert "status" in result
        assert "timestamp" in result
        assert "checks" in result

        # Should have all built-in checks
        expected_checks = ["database", "redis", "memory", "disk"]
        for check in expected_checks:
            assert check in result["checks"]


class TestStructuredLogging:
    """Test structured logging functionality"""

    @pytest.mark.monitoring
    def test_get_logger(self):
        """Test getting a logger"""
        logger = get_logger("test_logger")
        assert logger is not None
        assert logger.logger.name == "test_logger"

    @pytest.mark.monitoring
    def test_logger_info(self):
        """Test logger info method"""
        logger = Logger("test")
        # Should not raise exception
        logger.info("Test message", extra={"key": "value"})

    @pytest.mark.monitoring
    def test_logger_error(self):
        """Test logger error method"""
        logger = Logger("test")
        # Should not raise exception
        logger.error("Error message", extra={"key": "value"})


class TestAlertManager:
    """Test alert management"""

    @pytest.mark.monitoring
    @pytest.mark.asyncio
    async def test_add_alert_rule(self):
        """Test adding an alert rule"""
        async def test_condition():
            return True

        alert_manager.add_rule("test_alert", test_condition, "warning")
        assert len(alert_manager.rules) > 0

        # Find the rule
        rule = next(r for r in alert_manager.rules if r["name"] == "test_alert")
        assert rule is not None
        assert rule["severity"] == "warning"

    @pytest.mark.monitoring
    @pytest.mark.asyncio
    async def test_check_alerts(self):
        """Test checking alert rules"""
        # Clear existing alerts
        alert_manager.active_alerts = {}

        alerts = await alert_manager.check_all()

        # Should return a list
        assert isinstance(alerts, list)

    @pytest.mark.monitoring
    @pytest.mark.asyncio
    async def test_high_memory_alert(self):
        """Test high memory alert rule"""
        result = await alert_manager.rules[0]["condition"]()
        # Should return boolean
        assert isinstance(result, bool)


class TestMetrics:
    """Test Prometheus metrics"""

    @pytest.mark.monitoring
    @pytest.mark.asyncio
    async def test_get_metrics(self):
        """Test getting Prometheus metrics"""
        from app.core.monitoring import get_metrics

        metrics = await get_metrics()
        assert metrics is not None
        assert isinstance(metrics, str)

    @pytest.mark.monitoring
    def test_request_count_metric(self):
        """Test request counter metric"""
        # Increment the counter
        REQUEST_COUNT.labels(
            method="GET",
            endpoint="/test",
            status_code=200
        ).inc()

        # Check that the metric exists
        assert REQUEST_COUNT._value._value > 0

    @pytest.mark.monitoring
    def test_memory_usage_gauge(self):
        """Test memory usage gauge"""
        # Set a value
        MEMORY_USAGE.set(1024 * 1024 * 100)  # 100 MB

        # Check that the gauge was set
        assert MEMORY_USAGE._value._value == 1024 * 1024 * 100


class TestMonitoringIntegration:
    """Integration tests for monitoring"""

    @pytest.mark.monitoring
    @pytest.mark.asyncio
    async def test_monitoring_endpoint(self, client):
        """Test monitoring endpoints"""
        # Test health endpoint
        response = await client.get("/monitoring/health")
        assert response.status_code in [200, 503]

        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "checks" in data

        # Test metrics endpoint
        response = await client.get("/monitoring/metrics")
        assert response.status_code == 200
        assert "python_" in response.text or "http_requests" in response.text

        # Test alerts endpoint
        response = await client.get("/monitoring/alerts")
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data

        # Test info endpoint
        response = await client.get("/monitoring/info")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data

    @pytest.mark.monitoring
    @pytest.mark.asyncio
    async def test_readiness_liveness(self, client):
        """Test readiness and liveness probes"""
        # Test readiness
        response = await client.get("/monitoring/ready")
        assert response.status_code in [200, 503]
        if response.status_code == 200:
            assert response.json()["status"] == "ready"

        # Test liveness
        response = await client.get("/monitoring/live")
        assert response.status_code == 200
        assert response.json()["status"] == "alive"

    @pytest.mark.monitoring
    @pytest.mark.asyncio
    async def test_specific_health_check(self, client):
        """Test getting health check for specific component"""
        response = await client.get("/monitoring/health/memory")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "message" in data

    @pytest.mark.monitoring
    @pytest.mark.asyncio
    async def test_status_endpoint(self, client):
        """Test comprehensive status endpoint"""
        response = await client.get("/monitoring/status")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "status" in data
        assert "links" in data


class TestMonitoringMiddleware:
    """Test monitoring middleware integration"""

    @pytest.mark.monitoring
    @pytest.mark.asyncio
    async def test_structured_logging_middleware(self, client, caplog):
        """Test that structured logging middleware is working"""
        response = await client.get("/health")

        assert response.status_code == 200

        # Check that logs were created
        assert len(caplog.records) > 0

        # Check for request logs
        log_messages = [r.message for r in caplog.records]
        assert any("Request started" in msg or "Request completed" in msg for msg in log_messages)
