from datetime import datetime, timezone
from fastapi import HTTPException
from app.db.mongo import tenants_collection
from app.models.tenants_model import TenantCreate, TenantOut,UsageRecord
from app.utils.logger import logger
from app.utils.plans import plans


async def create_tenant(tenant: TenantCreate) -> TenantOut:
    try:
        existing = await tenants_collection.find_one({"name": tenant.name})
        if existing:
            logger.warning(f"Tenant creation failed: {tenant.name} already exists.")
            raise HTTPException(status_code=400, detail="Tenant already exists")

        plan = plans.get(tenant.subscription_plan)
        if not plan:
            logger.warning(f"Invalid plan: {tenant.subscription_plan}")
            raise HTTPException(status_code=400, detail="Invalid subscription plan")

        counter = await tenants_collection.database.counters.find_one_and_update(
            {"_id": "tenant_id"},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=True
        )
        tenant_id = counter["seq"]

        now = datetime.now(timezone.utc)
        tenant_doc = tenant.model_dump()
        tenant_doc.update({
            "tenant_id": tenant_id,
            "active": True,
            "features": plan["features"],
            "quotas": plan["quotas"],
            "pricing": plan.get("pricing", {}),
            "base_price": plan["price"],
            "usage": {feature: 0 for feature in plan["features"]},
            "created_at": now,
            "updated_at": now
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
        raise HTTPException(status_code=404, detail="Tenant not found")

    if usage.feature not in tenant["features"]:
        raise HTTPException(status_code=400, detail="Feature not in plan")

    new_usage = tenant["usage"].get(usage.feature, 0) + usage.count
    tenant["usage"][usage.feature] = new_usage
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