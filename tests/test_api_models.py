"""
Unit tests for API models.
"""
import pytest
from backend.api.models import AircraftResponse, HealthResponse


def test_aircraft_response_model():
    """Test AircraftResponse model creation and validation."""
    # Test minimal valid response
    data = {
        "n_number": "N12345",
        "registrant_name": "John Doe",
        "city": "Los Angeles",
        "state": "CA"
    }
    response = AircraftResponse(**data)
    assert response.n_number == "N12345"
    assert response.registrant_name == "John Doe"
    assert response.city == "Los Angeles"
    assert response.state == "CA"


def test_aircraft_response_optional_fields():
    """Test AircraftResponse with optional fields."""
    data = {
        "n_number": "N67890",
        "aircraft_manufacturer_name": "Cessna",
        "aircraft_model_name": "172",
        "year_mfr": 2020,
        "horsepower": 180
    }
    response = AircraftResponse(**data)
    assert response.aircraft_manufacturer_name == "Cessna"
    assert response.aircraft_model_name == "172"
    assert response.year_mfr == 2020
    assert response.horsepower == 180


def test_health_response_model():
    """Test HealthResponse model."""
    response = HealthResponse(
        status="healthy",
        database="connected",
        timestamp="2024-01-01T00:00:00"
    )
    assert response.status == "healthy"
    assert response.database == "connected"
    assert response.timestamp == "2024-01-01T00:00:00"

