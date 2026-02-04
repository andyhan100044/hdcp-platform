import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_read_main():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "HDCP Platform" in response.json()["message"]

def test_health_check():
    """Test health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_read_docs():
    """Test API documentation"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_read_openapi():
    """Test OpenAPI schema"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()
