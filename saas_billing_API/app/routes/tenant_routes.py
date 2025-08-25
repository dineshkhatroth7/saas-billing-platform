from fastapi import APIRouter
from app.models.tenants_model import TenantCreate,TenantOut,UsageRecord,PlanUpdate,TenantDeleteResponse,UsageSummary,Invoice
from app.services.tenants_service import create_tenant,record_usage,generate_invoice,downgrade_expired_plans,get_tenant,update_tenant_plan,deactivate_tenant,get_tenant_usage,get_invoice_by_tenant,get_all_tenants,get_analytics
from typing import List


router = APIRouter()

@router.post("/", response_model=TenantOut)
async def add_tenant(tenant: TenantCreate):
    created_tenant = await create_tenant(tenant)
    return created_tenant


@router.get("/", response_model=List[TenantOut])
async def list_tenants():
    tenants = await get_all_tenants()
    return tenants


@router.post("/downgrade-expired")
async def downgrade_expired():
    return await downgrade_expired_plans()



@router.get("/analytics")
async def analytics():
    return await get_analytics()



@router.get("/{tenant_id}", response_model=TenantOut)
async def fetch_tenant(tenant_id: int):
    return await get_tenant(tenant_id)


@router.post("/{tenant_id}/usage")
async def add_usage(tenant_id: int, usage: UsageRecord):
    usage_record = await record_usage(tenant_id, usage)
    return usage_record

@router.get("/{tenant_id}/billing")
async def get_billing(tenant_id: int):
    invoice = await generate_invoice(tenant_id)
    return invoice



@router.put("/{tenant_id}/plan", response_model=TenantOut)
async def change_plan(tenant_id: int, new_plan:PlanUpdate ):
    return await update_tenant_plan(tenant_id, new_plan.new_plan)


@router.delete("/{tenant_id}", response_model=TenantDeleteResponse)
async def delete_tenant(tenant_id: int):
    return await deactivate_tenant(tenant_id)


@router.get("/{tenant_id}/usage", response_model=UsageSummary)
async def fetch_tenant_usage(tenant_id: int):
    return await get_tenant_usage(tenant_id)

@router.post("/{tenant_id}/invoices", response_model=Invoice)
async def create_invoice(tenant_id: int):
    return await generate_invoice(tenant_id)

@router.get("/{tenant_id}/invoices", response_model=Invoice)
async def fetch_invoice_by_tenant(tenant_id: int):
    return await get_invoice_by_tenant(tenant_id)



