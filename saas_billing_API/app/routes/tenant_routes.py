from fastapi import APIRouter, HTTPException
from app.models.tenants_model import TenantCreate,TenantOut
from app.services.tenants_service import create_tenant



router = APIRouter()

@router.post("/", response_model=TenantOut)
async def add_tenant(tenant: TenantCreate):
    created_tenant = await create_tenant(tenant)
    if not created_tenant:
        raise HTTPException(status_code=400, detail="Tenant already exists")
    return created_tenant