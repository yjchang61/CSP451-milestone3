"""
CloudMart — API Tests
Run with: pytest tests/ -v
"""
import os
import pytest
from fastapi.testclient import TestClient

# Set dummy env vars for testing (prevents Cosmos DB connection)
os.environ["COSMOS_ENDPOINT"] = ""
os.environ["COSMOS_KEY"] = ""

from app.main import app  # noqa: E402

client = TestClient(app)


def test_homepage_returns_html():
    """Test that the homepage serves HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "CloudMart" in response.text


def test_health_endpoint():
    """Test the health check endpoint returns JSON."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "timestamp" in data
    # DB should be disconnected in test mode
    assert data["database"] == "disconnected"


def test_health_endpoint_has_timestamp():
    """Test that health endpoint includes a valid timestamp."""
    response = client.get("/health")
    data = response.json()
    assert data["timestamp"] is not None
    assert len(data["timestamp"]) > 0
