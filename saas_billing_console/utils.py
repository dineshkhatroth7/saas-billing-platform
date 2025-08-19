
import json
from datetime import datetime

DATA_FILE = "data.json"

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_tenant(name):
    data = load_data()
    if any(t["name"].lower() == name.lower() for t in data["tenants"]):
        return {"error": f"Tenant '{name}' already exists."}
    tenant_id = len(data["tenants"]) + 1
    tenant = {"id": tenant_id, "name": name, "created_at": str(datetime.now())}
    data["tenants"].append(tenant)
    save_data(data)
    return tenant

