import sys
import os
import pytest
from fastapi.testclient import TestClient
from saas_billing_API.main import app

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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
    # Attempt registration (ignore if already exists)
    client.post("/admin/register", json=admin_credentials)
    
    # Login
    response = client.post("/admin/login", json=admin_credentials)
    if response.status_code != 200:
        raise Exception(f"Admin login failed: {response.status_code}, {response.text}")
    
    token = response.json().get("access_token")
    if not token:
        raise Exception("Admin login did not return access_token")
    
    return token
