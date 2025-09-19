# tests/test_admin.py
import uuid

def test_admin_register(client, admin_credentials):
    response = client.post("/admin/register", json=admin_credentials)
    json_resp = response.json()
    if response.status_code == 400:
        # Admin already exists
        assert json_resp.get("detail") == "Admin already exists"
    elif response.status_code == 200:
        assert json_resp["email"] == admin_credentials["email"]

def test_admin_login(client, admin_credentials, admin_token):
    assert admin_token is not None

def test_admin_analytics(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/admin/analytics", headers=headers)
    assert response.status_code == 200

def test_admin_notify_tenant(client, admin_token):
    # Step 1: Create a unique tenant first
    tenant_payload = {
        "name": f"Tenant_{uuid.uuid4().hex[:8]}",
        "subscription_plan": "premium"
    }
    tenant_resp = client.post("/tenants/", json=tenant_payload)
    assert tenant_resp.status_code == 200  # ensure creation succeeded

    tenant_data = tenant_resp.json()
    # Support APIs that return 'tenant_id' or 'id'
    tenant_id = tenant_data.get("tenant_id") or tenant_data.get("id")

    # Step 2: Send notification
    payload = {"message": "Test notification"}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.post(f"/admin/notify/{tenant_id}", json=payload, headers=headers)

    # Step 3: Assertions
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["status"] == "success"
