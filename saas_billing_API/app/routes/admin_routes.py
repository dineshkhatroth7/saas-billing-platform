from fastapi import APIRouter, Depends,HTTPException
from saas_billing_API.app.models.admin_model import AdminCreate, AdminLogin,NotificationRequest
from saas_billing_API.app.services.admin_service import register_admin, login_admin,send_notification
from saas_billing_API.app.services.tenants_service import get_analytics, downgrade_expired_plans
from saas_billing_API.app.utils.jwt import admin_required
from saas_billing_API.app.utils.logger import logger  
from saas_billing_API.app.utils.decorators import log_execution_time

router = APIRouter()

@router.post("/admin/register", summary="Register a new admin")
@log_execution_time
async def register(admin: AdminCreate):
    """Registers a new admin. Fails if the email already exists."""
    result = await register_admin(admin.email, admin.password)
    if not result:
        logger.warning(f"Admin registration failed: {admin.email} already exists")  
        return {"error": "Admin already exists"}
    logger.info(f"New admin registered: {admin.email}")  
    return result


@router.post("/admin/login", summary="Admin login")
@log_execution_time
async def login(admin: AdminLogin):
    """Authenticate admin and return JWT access token."""
    token = await login_admin(admin.email, admin.password)
    if not token:
        logger.warning(f"Admin login failed: {admin.email}")  
        return {"error": "Invalid credentials"}
    logger.info(f"Admin logged in successfully: {admin.email}")  
    return {"access_token": token, "token_type": "bearer"}


@router.get("/admin/analytics", summary="Get platform analytics")
@log_execution_time
async def analytics(admin=Depends(admin_required)):
    """Return overall analytics for the platform (admin-only)."""
    logger.info(f"Admin [{admin}] requested analytics")  
    return await get_analytics()


@router.post("/admin/downgrade-expired", summary="Downgrade expired tenants")
@log_execution_time
@log_execution_time
async def downgrade_expired(admin=Depends(admin_required)):
    """Force downgrade of tenants whose plans have expired (admin-only)."""
    logger.info(f"Admin [{admin}] triggered downgrade of expired plans")  
    return await downgrade_expired_plans()

@router.post("/admin/notify/{tenant_id}", summary="Send notification to tenant")
@log_execution_time
@log_execution_time
async def notify_tenant(
    tenant_id: int,
    req: NotificationRequest,
    admin=Depends(admin_required)):
    """Send a custom notification to a specific tenant (admin-only)."""
    try:
        await send_notification(tenant_id, req.message)
        logger.info(f"Admin {admin['sub']} sent notification to tenant {tenant_id}: {req.message}")
        return {"status": "success", "tenant_id": tenant_id, "message": req.message}
    except HTTPException as e:
        logger.error(f"Failed to notify tenant {tenant_id}: {e.detail}")
        raise