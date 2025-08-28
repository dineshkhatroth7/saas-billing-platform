from datetime import datetime, timezone,timedelta
from app.db.mongo import tenants_collection,invoices_collection,notifications_collection
from app.models.tenants_model import TenantCreate, TenantOut,UsageRecord,UsageSummary,Invoice
from app.utils.logger import logger
from app.utils.plans import plans
from bson import ObjectId
from typing import List
from app.utils.exceptions import TenantNotFoundError,TenantAlreadyExistsError,InvalidPlanError,FeatureNotInPlanError,InvoiceNotFoundError


async def create_tenant(tenant: TenantCreate) -> TenantOut:
    try:
        existing = await tenants_collection.find_one({"name": tenant.name})
        if existing:
            logger.warning(f"Tenant creation failed: {tenant.name} already exists.")
            raise TenantAlreadyExistsError(tenant.name)

        plan = plans.get(tenant.subscription_plan)
        if not plan:
            logger.warning(f"Invalid plan: {tenant.subscription_plan}")
            raise InvalidPlanError(tenant.subscription_plan)

        counter = await tenants_collection.database.counters.find_one_and_update(
            {"_id": "tenant_id"},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=True
        )
        tenant_id = counter["seq"]

        now = datetime.now(timezone.utc)
        
        if tenant.subscription_plan in ["premium", "enterprise"]:
            subscription_start = now
            subscription_end = now + timedelta(days=30)
        else:
            subscription_start = None
            subscription_end = None
        
        tenant_doc = tenant.model_dump()
        tenant_doc.update({
            "tenant_id": tenant_id,
            "active": True,
            "features": plan["features"],
            "quotas": plan["quotas"],
            "pricing": plan.get("pricing", {}),
            "base_price": plan["price"],
            "usage": [{"feature": feature, "count": 0} for feature in plan["features"]],
            "created_at": now,
            "updated_at": now,
            "subscription_start": subscription_start,
            "subscription_end": subscription_end
        })

        result = await tenants_collection.insert_one(tenant_doc)
        logger.info(f"Tenant created: {tenant.name} (tenant_id={tenant_id}, id={result.inserted_id})")

        saved = await tenants_collection.find_one({"_id": result.inserted_id})


        return TenantOut(
            id=str(saved["_id"]),
            tenant_id=saved["tenant_id"],
            name=saved["name"],
            subscription_plan=saved["subscription_plan"],
            active=saved["active"],
            features=saved["features"],
            quotas=saved["quotas"],
            pricing=saved["pricing"],
            base_price=saved["base_price"],
            created_at=saved["created_at"]
        )

    except Exception as e:
        logger.error(f"Unexpected error during tenant creation: {e}")
        raise



async def record_usage(tenant_id: int, usage: UsageRecord):
    tenant = await tenants_collection.find_one({"tenant_id": tenant_id})
    if not tenant:
        logger.warning(f"Tenant {tenant_id} not found.")
        raise TenantNotFoundError(tenant_id)

    if usage.feature not in tenant["features"]:
        logger.error(
        f"Tenant {tenant['tenant_id']} attempted to use feature '{usage.feature}' "
        f"which is not included in plan '{tenant['subscription_plan']}'.")
        raise FeatureNotInPlanError(usage.feature, tenant["subscription_plan"])

    if isinstance(tenant["usage"], dict):
        new_usage = tenant["usage"].get(usage.feature, 0) + usage.count
        tenant["usage"][usage.feature] = new_usage

    elif isinstance(tenant["usage"], list):
        existing = next((u for u in tenant["usage"] if u["feature"] == usage.feature), None)
        if existing:
            existing["count"] += usage.count
            new_usage = existing["count"]
        else:
            tenant["usage"].append({"feature": usage.feature, "count": usage.count})
            new_usage = usage.count
    else:
        raise ValueError("Invalid usage format in DB (must be dict or list)")

    tenant["updated_at"] = datetime.now(timezone.utc)

    await tenants_collection.update_one(
        {"tenant_id": tenant_id},
        {"$set": {"usage": tenant["usage"], "updated_at": tenant["updated_at"]}}
    )

    return {
        "tenant_id": tenant_id,
        "feature": usage.feature,
        "usage": new_usage
    }



async def generate_invoice(tenant_id: int) -> dict:
    tenant = await tenants_collection.find_one({"tenant_id": tenant_id})
    if not tenant:
        logger.warning(f"Tenant {tenant_id} not found.")
        raise TenantNotFoundError(tenant_id)
        
    
    base_price = tenant.get("base_price", 0)
    usage = tenant.get("usage", {})
    quotas = tenant.get("quotas", {})
    pricing = tenant.get("pricing", {})

    if isinstance(usage, list):
        usage = {u["feature"]: u["count"] for u in usage}

    usage_charges = 0.0
    usage_details = {}

    for feature, used in usage.items():
        limit = quotas.get(feature)
        feature_price = pricing.get(feature, 0)
        if limit is not None and used > limit:
            overage = (used - limit) * feature_price
            usage_charges += overage
            usage_details[feature] = {
                "used": used,
                "quota": limit,
                "unit_price": feature_price,
                "overage": overage
            }

    total_due = base_price + usage_charges

    invoice = {
        "tenant_id": tenant_id,
        "tenant_name": tenant["name"],
        "billing_date": datetime.now(timezone.utc).isoformat(), 
        "plan": tenant["subscription_plan"],
        "base_price": base_price,
        "usage_charges": usage_charges,
        "usage_details": usage_details,
        "total_due": total_due,
        "usage_snapshot": usage
    }

    result = await invoices_collection.insert_one(invoice)
    invoice["_id"] = str(result.inserted_id)  

    logger.info(f"Invoice stored with id {result.inserted_id} for tenant {tenant_id}")
    return invoice

async def downgrade_expired_plans():

    now = datetime.now(timezone.utc)

    query = {
        "subscription_end": {"$lte": now},
        "subscription_plan": {"$in": ["premium", "enterprise"]}
    }

    updated = 0
    downgraded_tenants = []

    async for tenant in tenants_collection.find(query):
        tenant_id = tenant["tenant_id"]
        tenant_name = tenant.get("name") 

        downgrade_fields = {
            "subscription_plan": "free",
            "features": plans["free"]["features"],
            "quotas": plans["free"]["quotas"],
            "pricing": plans["free"]["pricing"],
            "base_price": plans["free"]["price"],
            "subscription_start": None,
            "subscription_end": None,
            "updated_at": now,
        }

        await tenants_collection.update_one(
            {"tenant_id": tenant_id},
            {"$set": downgrade_fields}
        )
        updated += 1
        downgraded_tenants.append({
            "tenant_id": tenant_id,
            "tenant_name": tenant_name
        })

        logger.info(f"Tenant {tenant['name']} (tenant_id={tenant_id}) downgraded to Free plan.")
    
    return {
        "message": f"{updated} tenants downgraded to free plan.",
        "downgraded_tenants": downgraded_tenants
    }


async def get_tenant(tenant_id: int) -> TenantOut:
    tenant = await tenants_collection.find_one({"tenant_id": tenant_id})
    if not tenant:
        logger.warning(f"Tenant {tenant_id} not found.")
        raise TenantNotFoundError(tenant_id)
    
    tenant["id"] = str(tenant["_id"])
    logger.info(f"Fetched tenant {tenant_id} successfully.")

    return TenantOut(**tenant)



async def update_tenant_plan(tenant_id: int, new_plan: str):

    now = datetime.now(timezone.utc)

    if new_plan not in plans:
        logger.error(f"Invalid plan '{new_plan}' for tenant {tenant_id}.")
        raise InvalidPlanError(new_plan)

    tenant = await tenants_collection.find_one({"tenant_id": tenant_id})
    if not tenant:
        logger.warning(f"Tenant {tenant_id} not found for plan update.")
        raise TenantNotFoundError(tenant_id)

    if new_plan in ["premium", "enterprise"]:
        subscription_start = now
        subscription_end = now + timedelta(days=30)
    else:
        subscription_start = None
        subscription_end = None

    update_data = {
        "subscription_plan": new_plan,
        "features": plans[new_plan]["features"],
        "quotas": plans[new_plan]["quotas"],
        "pricing": plans[new_plan]["pricing"],
        "base_price": plans[new_plan]["price"],
        "subscription_start": subscription_start,
        "subscription_end": subscription_end,
        "updated_at": now
    }

    await tenants_collection.update_one(
        {"tenant_id": tenant_id},
        {"$set": update_data}
    )

    tenant.update(update_data)
    tenant["id"] = str(tenant["_id"])
    logger.info(f"Tenant {tenant_id} updated to plan '{new_plan}'.")
    return TenantOut(**tenant)

async def deactivate_tenant(tenant_id: int):
    tenant = await tenants_collection.find_one({"tenant_id": tenant_id})
    if not tenant:
        logger.warning(f"Tried to deactivate non-existent tenant {tenant_id}.")
        raise TenantNotFoundError(tenant_id)

    now = datetime.now(timezone.utc)

    update_data = {
        "active": False,
        "deleted_at": now,
        "updated_at": now
    }

    await tenants_collection.update_one(
        {"tenant_id": tenant_id},
        {"$set": update_data}
    )

    tenant.update(update_data)
    logger.info(f"Tenant {tenant_id} deactivated successfully.")
    return {
        "tenant_id": tenant["tenant_id"],
        "name": tenant["name"],
        "active": tenant["active"],
        "deleted_at": tenant["deleted_at"],
        "message": f"Tenant {tenant['tenant_id']} deactivated successfully"
    }


async def get_tenant_usage(tenant_id: int) -> UsageSummary:
    logger.info(f"Fetching usage for tenant_id={tenant_id}") 
    tenant = await tenants_collection.find_one({"tenant_id": tenant_id})
    if not tenant:
        logger.warning(f"Tenant {tenant_id} not found while fetching usage")
        raise TenantNotFoundError(tenant_id)
    
    usage_data = tenant.get("usage", {})

    if isinstance(usage_data, dict):
        usage_records = [UsageRecord(feature=f, count=c) for f, c in usage_data.items()]
    elif isinstance(usage_data, list):
        usage_records = [UsageRecord(feature=u["feature"], count=u["count"]) for u in usage_data]
    else:
        usage_records = []


    logger.debug(f"Tenant {tenant_id} usage data: {usage_records}") 
    return UsageSummary(tenant_id=tenant_id, usage=usage_records)


async def get_invoice_by_tenant(tenant_id: int) -> Invoice:
    invoice_doc = await invoices_collection.find_one(
        {"tenant_id": tenant_id}, sort=[("billing_date", -1)]
    )
    
    if not invoice_doc:
        logger.warning(f"No invoice found for tenant {tenant_id}")
        raise InvoiceNotFoundError(tenant_id)

    invoice_doc["id"] = str(invoice_doc["_id"])
    del invoice_doc["_id"]  

    logger.info(f"Fetched latest invoice for tenant {tenant_id}")
    return Invoice(**invoice_doc)


async def get_all_tenants() -> List[TenantOut]:
    try:
        tenants_cursor = tenants_collection.find()
        tenants = await tenants_cursor.to_list(length=None)

        if not tenants:
            logger.info("No tenants found in database.")
            return []

        result = [
            TenantOut(
                id=str(t["_id"]),
                tenant_id=t["tenant_id"],
                name=t["name"],
                subscription_plan=t["subscription_plan"],
                active=t["active"],
                features=t["features"],
                quotas=t["quotas"],
                pricing=t["pricing"],
                base_price=t["base_price"],
                created_at=t["created_at"],
            )
            for t in tenants
        ]

        logger.info(f"Fetched {len(result)} tenants from database.")
        return result

    except Exception as e:
        logger.error(f"Error fetching tenants: {e}")
        raise

async def get_analytics():
    logger.info("Fetching analytics data...")

    total_tenants = await tenants_collection.count_documents({})
    active_tenants = await tenants_collection.count_documents({"active": True})
    inactive_tenants = await tenants_collection.count_documents({"active": False})


    plan_counts = {
        "free": await tenants_collection.count_documents({"subscription_plan": "free"}),
        "premium": await tenants_collection.count_documents({"subscription_plan": "premium"}),
        "enterprise": await tenants_collection.count_documents({"subscription_plan": "enterprise"}),
    }

    total_invoices = await invoices_collection.count_documents({})
  
  
    analytics_data = {
        "tenants": {
            "total": total_tenants,
            "active": active_tenants,
            "inactive": inactive_tenants,
            "by_plan": plan_counts
        },
        "billing": {
            "total_invoices": total_invoices,
        }
    }

    logger.info(f"Analytics generated successfully: {analytics_data}")
    return analytics_data

async def reactivate_tenant(tenant_id: int) -> TenantOut:
    tenant = await tenants_collection.find_one({"tenant_id": tenant_id})
    if not tenant:
        logger.error(f"Tenant {tenant_id} not found for reactivation")
        raise TenantNotFoundError(tenant_id)
    
    if tenant.get("active", True):
        logger.info(f"Tenant {tenant_id} is already active")
        tenant["id"] = str(tenant["_id"])
        return TenantOut(**tenant)
    
    await tenants_collection.update_one(
        {"tenant_id": tenant_id},
        {"$set": {"active": True}}
    )

    updated = await tenants_collection.find_one({"tenant_id": tenant_id})
    updated["id"] = str(updated["_id"])
    logger.info(f"Tenant {tenant_id} reactivated successfully")
    return TenantOut(**updated)

async def search_tenant_by_name_or_id(query: str):
    filters = []
    filters.append({"name": {"$regex": query, "$options": "i"}})

    if query.isdigit():
        filters.append({"tenant_id": int(query)}) 
        
    logger.info(f"Searching tenants with query: {query}, filters: {filters}")
    tenants = await tenants_collection.find({"$or": filters}).to_list(length=None)
    for tenant in tenants:
        tenant["id"] = str(tenant["_id"])
        del tenant["_id"]

    logger.info(f"Found {len(tenants)} tenants for query '{query}'")

    return tenants

async def get_notifications(tenant_id: int):
    logger.info(f"Fetching notifications for tenant_id={tenant_id}")

    try:
        cursor = notifications_collection.find({"tenant_id": tenant_id})
        notifications = await cursor.to_list(length=100)

        if not notifications:
            logger.warning(f"No notifications found for tenant_id={tenant_id}")
        else:
            logger.info(f"Fetched {len(notifications)} notifications for tenant_id={tenant_id}")

        return [
            {
                "id": str(n["_id"]),
                "tenant_id": n["tenant_id"],
                "tenant_name": n["tenant_name"],
                "message": n["message"],
                "status": n["status"],
            }
            for n in notifications
        ]

    except Exception as e:
        logger.error(f"Error fetching notifications for tenant_id={tenant_id}: {e}")
        raise