from fastapi import APIRouter
from app.models.tenants_model import TenantCreate,TenantOut,UsageRecord
from app.services.tenants_service import create_tenant,record_usage,generate_invoice,downgrade_expired_plans



router = APIRouter()

@router.post("/", response_model=TenantOut)
async def add_tenant(tenant: TenantCreate):
    created_tenant = await create_tenant(tenant)
    return created_tenant


@router.post("/{tenant_id}/usage")
async def add_usage(tenant_id: int, usage: UsageRecord):
    usage_record = await record_usage(tenant_id, usage)
    return usage_record

@router.get("/{tenant_id}/billing")
async def get_billing(tenant_id: int):
    invoice = await generate_invoice(tenant_id)
    return invoice


@router.post("/downgrade-expired")
async def downgrade_expired():
    return await downgrade_expired_plans()