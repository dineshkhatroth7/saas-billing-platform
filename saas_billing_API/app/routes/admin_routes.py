from fastapi import APIRouter, Depends,HTTPException,Query
from app.models.admin_model import AdminCreate, AdminLogin,NotificationRequest
from app.services.admin_service import register_admin, login_admin,send_notification
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

@router.post("/admin/notify/{tenant_id}")
async def notify_tenant(
    tenant_id: int,
    req: NotificationRequest,
    admin=Depends(admin_required)):
    try:
        await send_notification(tenant_id, req.message)
        logger.info(f"Admin {admin['sub']} sent notification to tenant {tenant_id}: {req.message}")
        return {"status": "success", "tenant_id": tenant_id, "message": req.message}
    except HTTPException as e:
        logger.error(f"Failed to notify tenant {tenant_id}: {e.detail}")
        raise