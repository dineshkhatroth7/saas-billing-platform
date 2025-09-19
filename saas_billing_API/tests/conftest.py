
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture(scope="session")
def client():
    """Test client for synchronous tests."""
    with TestClient(app) as c:
        yield c

@pytest.fixture
def admin_credentials():
    return {"email": "admin@example.com", "password": "Stonass123"}

@pytest.fixture
def admin_token(client, admin_credentials):
    """Register/login admin and return JWT."""
    # Register
    response = client.post("/admin/register", json=admin_credentials)
    # Ignore error if already exists
    # Login
    response = client.post("/admin/login", json=admin_credentials)
    return response.json()["access_token"]


