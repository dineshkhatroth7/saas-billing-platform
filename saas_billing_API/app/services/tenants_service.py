from app.db.mongo import tenants_collection
from app.models.tenants_model import TenantCreate, TenantOut
from app.utils.logger import logger

async def create_tenant(tenant: TenantCreate) -> TenantOut | None:
    try:
        existing = await tenants_collection.find_one({"name": tenant.name})
        if existing:
            logger.warning(f"Tenant creation failed: {tenant.name} already exists.")
            return None

        # 👇 Simple auto-increment id
        tenant_count = await tenants_collection.count_documents({})
        tenant_id = tenant_count + 1  

        tenant_doc = tenant.model_dump()
        tenant_doc["id"] = tenant_id
        tenant_doc["active"] = True

        await tenants_collection.insert_one(tenant_doc)

        logger.info(f"Tenant created successfully: {tenant.name} (id={tenant_id})")

        return TenantOut(
            id=tenant_id,
            name=tenant.name,
            subscription_plan=tenant.subscription_plan,
            active=True
        )
    except Exception as e:
        logger.error(f"Unexpected error during tenant creation: {e}")
        raise
