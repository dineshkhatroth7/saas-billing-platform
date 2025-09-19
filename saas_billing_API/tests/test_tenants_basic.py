import pytest
import uuid

def test_add_tenant(client):
    tenant_payload = {
        "name": f"Tenant_{uuid.uuid4().hex[:8]}",
        "subscription_plan": "premium"
    }
    response = client.post("/tenants/", json=tenant_payload)
    assert response.status_code == 200

    data = response.json()
    # Support APIs returning 'tenant_id' or 'id'
    tenant_id = data.get("tenant_id") or data.get("id")
    assert tenant_id is not None
    assert data["name"] == tenant_payload["name"]
    assert data["subscription_plan"] == tenant_payload["subscription_plan"]

def test_list_tenants(client):
    # Create a unique tenant to ensure at least one exists
    tenant_payload = {
        "name": f"Tenant_{uuid.uuid4().hex[:8]}",
        "subscription_plan": "premium"
    }
    tenant_resp = client.post("/tenants/", json=tenant_payload)
    assert tenant_resp.status_code == 200
    tenant_data = tenant_resp.json()
    tenant_id = tenant_data.get("tenant_id") or tenant_data.get("id")

    # Fetch all tenants
    response = client.get("/tenants/")
    assert response.status_code == 200

    tenants = response.json()
    assert isinstance(tenants, list)
    assert len(tenants) > 0  # At least one tenant exists

    # Check that expected fields exist in the first tenant
    tenant = tenants[0]
    expected_fields = [
        "id", "tenant_id", "name", "subscription_plan",
        "active", "features", "quotas", "pricing",
        "base_price", "created_at"
    ]
    for field in expected_fields:
        assert field in tenant
