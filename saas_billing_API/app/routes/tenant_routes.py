from fastapi import APIRouter,Query
from saas_billing_API.app.models.tenants_model import TenantCreate,TenantOut,UsageRecord,PlanUpdate,TenantDeleteResponse,UsageSummary,Invoice,TenantNotification
from saas_billing_API.app.services.tenants_service import create_tenant,record_usage,generate_invoice,get_tenant,update_tenant_plan,deactivate_tenant,get_tenant_usage,get_invoice_by_tenant,get_all_tenants,reactivate_tenant,search_tenant_by_name_or_id,get_notifications
from typing import List
from saas_billing_API.app.utils.decorators import log_execution_time


router = APIRouter()

@router.post("/", response_model=TenantOut)
@log_execution_time
async def add_tenant(tenant: TenantCreate):
    """Create a new tenant."""
    created_tenant = await create_tenant(tenant)
    return created_tenant


@router.get("/", response_model=List[TenantOut])
@log_execution_time
async def list_tenants():
    """Retrieve all tenants."""
    tenants = await get_all_tenants()
    return tenants


@router.get("/search", response_model=List[TenantOut])
@log_execution_time
async def search_tenants(query: str = Query(..., description="Search by tenant name or ID")):
    """Search tenants by name or ID."""
    return await search_tenant_by_name_or_id(query)



@router.get("/{tenant_id}", response_model=TenantOut)
@log_execution_time
async def fetch_tenant(tenant_id: int):
    """Fetch tenant details by ID."""
    return await get_tenant(tenant_id)


@router.post("/{tenant_id}/usage")
@log_execution_time
async def add_usage(tenant_id: int, usage: UsageRecord):
    """Record usage for a tenant."""
    usage_record = await record_usage(tenant_id, usage)
    return usage_record

@router.get("/{tenant_id}/billing")
@log_execution_time
async def get_billing(tenant_id: int):
    """Generate billing invoice for a tenant."""
    invoice = await generate_invoice(tenant_id)
    return invoice



@router.put("/{tenant_id}/plan", response_model=TenantOut)
@log_execution_time
async def change_plan(tenant_id: int, new_plan:PlanUpdate ):
    """Update tenant's subscription plan."""
    return await update_tenant_plan(tenant_id, new_plan.new_plan)


@router.delete("/{tenant_id}", response_model=TenantDeleteResponse)
@log_execution_time
async def delete_tenant(tenant_id: int):
    """Deactivate a tenant account."""
    return await deactivate_tenant(tenant_id)


@router.get("/{tenant_id}/usage", response_model=UsageSummary)
@log_execution_time
async def fetch_tenant_usage(tenant_id: int):
    """Fetch usage summary for a tenant."""
    return await get_tenant_usage(tenant_id)

@router.post("/{tenant_id}/invoices", response_model=Invoice)
@log_execution_time
async def create_invoice(tenant_id: int):
    """Create a new invoice for a tenant."""
    return await generate_invoice(tenant_id)

@router.get("/{tenant_id}/invoices", response_model=Invoice)
@log_execution_time
async def fetch_invoice_by_tenant(tenant_id: int):
    """Fetch latest invoice for a tenant."""
    return await get_invoice_by_tenant(tenant_id)

@router.post("/{tenant_id}/reactivate", response_model=TenantOut)
@log_execution_time
async def reactivate_tenant_route(tenant_id: int):
    """Reactivate a deactivated tenant."""
    return await reactivate_tenant(tenant_id)

@router.get("/{tenant_id}/notifications", response_model=List[TenantNotification])
@log_execution_time
async def fetch_notifications(tenant_id: int):
    """Fetch notifications for a tenant."""
    return await get_notifications(tenant_id)