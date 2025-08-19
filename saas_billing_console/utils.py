
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


def add_subscription(tenant_id, plan):
    data = load_data()

    if not any(t["id"] == tenant_id for t in data["tenants"]):
      return {"error": f"Tenant ID {tenant_id} not found."}

    if any(s["tenant_id"] == tenant_id for s in data["subscriptions"]):
      return {"error": f"Tenant {tenant_id} already has a subscription."}

    sub_id = len(data["subscriptions"]) + 1
    subscription = {
        "id": sub_id,
        "tenant_id": tenant_id,
        "plan": plan,
        "start_date": str(datetime.now())
    }
    data["subscriptions"].append(subscription)
    save_data(data)
    return subscription


def record_usage(tenant_id, feature, count):
    data = load_data()

    tenant = next((t for t in data["tenants"] if t["id"] == tenant_id), None)
    
    if not tenant:
        return {"error": f"Tenant ID {tenant_id} not found."}

    subscription = next((s for s in data["subscriptions"] if s["tenant_id"] == tenant_id), None)
    if not subscription:
        return {"error": f"Tenant {tenant_id} has no active subscription."}

    plan = subscription["plan"]
    allowed_features = data["plans"].get(plan, [])
    if feature not in allowed_features:
        return {"error": f"Feature '{feature}' is not allowed for plan '{plan}'."}

    usage_id = len(data["usage"]) + 1
    usage = {
        "id": usage_id,
        "tenant_id": tenant_id,
        "feature": feature,
        "count": count,
        "timestamp": str(datetime.now())
    }
    data["usage"].append(usage)
    save_data(data)

    return usage

