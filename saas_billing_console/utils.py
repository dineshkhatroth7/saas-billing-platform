
import json
from datetime import datetime,timedelta

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
        "start_date": str(datetime.now()),
        "billing_cycle_start": str(datetime.now())
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


def calculate_billing(tenant_id):
    data = load_data()
    subscription = next((s for s in data["subscriptions"] if s["tenant_id"] == tenant_id), None)
    if not subscription:
         return 0.0
    
    plan = subscription["plan"]
    usage_list = [u for u in data["usage"] if u["tenant_id"] == tenant_id]

    billing = 0.0
    for u in usage_list:
        if plan == "free":
            if u["feature"] == "api_calls":
                billing += max(0, u["count"] - 100) * 0.01

        elif plan == "premium":
            if u["feature"] == "api_calls":
                billing += u["count"] * 0.01
            elif u["feature"] == "storage":
                billing += u["count"] * 0.05
        elif plan == "enterprise":
            billing = 100  
            break

    return round(billing, 2)

def reset_monthly_usage():
    data = load_data()
    now = datetime.now()
    reset_tenants = []

    for sub in data["subscriptions"]:
        cycle_str = sub.get("start_date")

        if not cycle_str:
            continue  

        start_date = datetime.fromisoformat(cycle_str)

        if (now - start_date).days >= 30:
            tenant_id = sub["tenant_id"]

            tenant_name = next(
                (t["name"] for t in data["tenants"] if t["id"] == tenant_id),
                "Unknown"
            )
            data["usage"] = [u for u in data["usage"] if u["tenant_id"] != tenant_id]
            sub["billing_cycle_start"] = now.isoformat()
            reset_tenants.append({
                "id": tenant_id,
                "name": tenant_name,
                "new_cycle_start": now.isoformat()
            })
    
    save_data(data)
    return reset_tenants

