from datetime import datetime,timezone
from app.db.mongo import tenants_collection
from app.models.tenants_model import TenantCreate, TenantOut
from app.utils.logger import logger
from app.utils.plans import plans


async def create_tenant(tenant: TenantCreate) -> TenantOut | None:
    try:
        existing = await tenants_collection.find_one({"name": tenant.name})
        if existing:
            logger.warning(f"Tenant creation failed: {tenant.name} already exists.")
            return None

        plan = plans.get(tenant.subscription_plan)
        if not plan:
            logger.warning(f"Invalid plan: {tenant.subscription_plan}")
            return None

        tenant_count = await tenants_collection.count_documents({})
        tenant_id = tenant_count + 1

        now = datetime.now(timezone.utc)
        tenant_doc = tenant.model_dump()
        tenant_doc["tenant_id"] = tenant_id
        tenant_doc["active"] = True
        tenant_doc["features"] = plan["features"]
        tenant_doc["quotas"] = plan["quotas"]
        tenant_doc["pricing"] = plan.get("pricing", {})
        tenant_doc["base_price"] = plan["price"]
        tenant_doc["usage"] = {feature: 0 for feature in plan["features"]}
        tenant_doc["created_at"] = now
        tenant_doc["updated_at"] = now

        result = await tenants_collection.insert_one(tenant_doc)

        logger.info(
            f"Tenant created successfully: {tenant.name} "
            f"(tenant_id={tenant_id}, mongo_id={result.inserted_id})"
        )

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
            created_at=saved["created_at"],
            updated_at=saved["updated_at"],
        )

    except Exception as e:
        logger.error(f"Unexpected error during tenant creation: {e}")
        raise
