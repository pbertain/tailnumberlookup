"""
Integration tests for API endpoints (requires database).
"""
import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

# Create test client
client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code in [200, 503]  # 503 if DB not initialized
    
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "timestamp" in data


def test_aircraft_json_endpoint_missing():
    """Test aircraft JSON endpoint with non-existent tail number."""
    response = client.get("/api/v1/aircraft/N99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_aircraft_curl_endpoint_missing():
    """Test aircraft cURL endpoint with non-existent tail number."""
    response = client.get("/api/v1/curl/aircraft/N99999")
    assert response.status_code == 404


def test_swagger_docs_endpoint():
    """Test Swagger documentation endpoint."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_openapi_json_endpoint():
    """Test OpenAPI schema endpoint."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data or "swagger" in data
    assert "paths" in data


def test_tail_number_validation():
    """Test tail number format validation."""
    # Test various formats
    test_tail_numbers = ["N12345", "12345", "n12345", "N1", "N123456789"]
    
    for tail_num in test_tail_numbers:
        response = client.get(f"/api/v1/aircraft/{tail_num}")
        # Should not return 400 (bad request) - should normalize and return 404 if not found
        assert response.status_code != 400

