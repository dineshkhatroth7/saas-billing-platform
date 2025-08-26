from fastapi import APIRouter, Depends
from app.models.admin_model import AdminCreate, AdminLogin
from app.services.admin_service import register_admin, login_admin
from app.services.tenants_service import get_analytics, downgrade_expired_plans
from app.utils.jwt import admin_required
from app.utils.logger import logger  

router = APIRouter()

@router.post("/admin/register")
async def register(admin: AdminCreate):
    result = await register_admin(admin.email, admin.password)
    if not result:
        logger.warning(f"Admin registration failed: {admin.email} already exists")  
        return {"error": "Admin already exists"}
    logger.info(f"New admin registered: {admin.email}")  
    return result


@router.post("/admin/login")
async def login(admin: AdminLogin):
    token = await login_admin(admin.email, admin.password)
    if not token:
        logger.warning(f"Admin login failed: {admin.email}")  
        return {"error": "Invalid credentials"}
    logger.info(f"Admin logged in successfully: {admin.email}")  
    return {"access_token": token, "token_type": "bearer"}


@router.get("/admin/analytics")
async def analytics(admin=Depends(admin_required)):
    logger.info(f"Admin [{admin}] requested analytics")  
    return await get_analytics()


@router.post("/admin/downgrade-expired")
async def downgrade_expired(admin=Depends(admin_required)):
    logger.info(f"Admin [{admin}] triggered downgrade of expired plans")  
    return await downgrade_expired_plans()
