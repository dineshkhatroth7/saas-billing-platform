from fastapi import APIRouter, HTTPException
from app.models.tenants_model import TenantCreate,TenantOut,UsageRecord
from app.services.tenants_service import create_tenant,record_usage,generate_invoice



router = APIRouter()

@router.post("/", response_model=TenantOut)
async def add_tenant(tenant: TenantCreate):
    created_tenant = await create_tenant(tenant)
    if not created_tenant:
        raise HTTPException(status_code=400, detail="Tenant already exists")
    return created_tenant


@router.post("/{tenant_id}/usage")
async def add_usage(tenant_id: int, usage: UsageRecord):
    usage_record = await record_usage(tenant_id, usage)
    return usage_record

@router.get("/{tenant_id}/billing")
async def get_billing(tenant_id: int):
    invoice = await generate_invoice(tenant_id)
    return invoice
