
import json,csv
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
    plan_info = data["plans"].get(plan, {})
    allowed_features =  plan_info.get("features", [])
    quotas = plan_info.get("quotas", {})
    
    if feature not in allowed_features:
        return {"error": f"Feature '{feature}' is not allowed for plan '{plan}'."}

    limit = quotas.get(feature, None)
    current_usage = sum(
        u["count"] for u in data["usage"]
        if u["tenant_id"] == tenant_id and u["feature"] == feature
    )
    
    if limit is not None:
        projected = current_usage + count
        if projected > limit:
            print(f"Tenant {tenant_id} exceeded quota for '{feature}'. Limit={limit}, Used={projected}")
        elif projected > 0.8 * limit:
            print(f"Tenant {tenant_id} nearing quota for '{feature}' ({projected}/{limit})")
       
                       
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
    plan_info = data["plans"].get(plan, {})
    quotas = plan_info.get("quotas", {})
    pricing = plan_info.get("pricing", {})
    base_price = plan_info.get("price", 0)

    billing = base_price  

    usage_list = [u for u in data["usage"] if u["tenant_id"] == tenant_id]

    usage_by_feature = {}
    for u in usage_list:
        usage_by_feature[u["feature"]] = usage_by_feature.get(u["feature"], 0) + u["count"]

    for feature, total_count in usage_by_feature.items():
        quota = quotas.get(feature, None)
        price_per_unit = pricing.get(feature, 0)

        if quota is None:
            continue

        if total_count > quota:
            extra = total_count - quota
            billing += extra * price_per_unit

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


def get_cycle_info(tenant_id):
    data = load_data()
    sub = next((s for s in data["subscriptions"] if s["tenant_id"] == tenant_id), None)
    if not sub:
         raise ValueError(f"No subscription found for tenant_id={tenant_id}")
    
    start = sub.get("billing_cycle_start") or sub.get("start_date")
    start_dt = datetime.fromisoformat(start)
    next_dt = start_dt + timedelta(days=30)
    return start_dt, next_dt

def export_usage_report(tenant_id, format="csv"):
    data = load_data()
    usage_list = [u for u in data["usage"] if u["tenant_id"] == tenant_id]

    if not usage_list:
        return {"error": "No usage recorded."}
    
    
    filename = f"usage_tenant_{tenant_id}.{format}"

    if format == "csv":
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "tenant_id", "feature", "count", "timestamp"])
            writer.writeheader()
            writer.writerows(usage_list)
    
    elif format == "json":
        with open(filename, "w") as f:
            json.dump(usage_list, f, indent=4)
    
    return {"message": f"Report exported to {filename}"}