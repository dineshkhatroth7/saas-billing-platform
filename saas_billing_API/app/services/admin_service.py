from fastapi import HTTPException
from app.db.mongo import  tenants_collection,notifications_collection,admins_collection
from passlib.hash import bcrypt
from app.utils.jwt import create_access_token
from app.utils.logger import logger  

async def register_admin(email: str, password: str):
    """
    Register a new admin with hashed password.
    Raises HTTPException if the admin already exists.
    """
    existing = await admins_collection.find_one({"email": email})
    if existing:
        logger.warning(f"Admin registration failed: {email} already exists")  
        raise HTTPException(status_code=400, detail="Admin already exists")

    hashed_password = bcrypt.hash(password)
    result = await admins_collection.insert_one({
        "email": email,
        "password": hashed_password
    })
    logger.info(f"Admin registered successfully: {email}")  
    return {"id": str(result.inserted_id), "email": email}


async def login_admin(email: str, password: str):
    """
    Authenticate an admin and return a JWT token.
    Raises HTTPException if credentials are invalid.
    """
    admin = await admins_collection.find_one({"email": email})
    if not admin or not bcrypt.verify(password, admin["password"]):
        logger.warning(f"Admin login failed: {email}")  
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(admin["_id"]), "role": "admin"})
    logger.info(f"Admin logged in: {email}")  
    return token



async def send_notification(tenant_id: int, message: str):
    """
    Send a notification to a tenant.
    Raises HTTPException if tenant does not exist.
    """
    tenant = await tenants_collection.find_one({"tenant_id": tenant_id})
    if not tenant:
        logger.warning(f"Tried to send notification to non-existent tenant {tenant_id}")
        raise HTTPException(status_code=404, detail="Tenant not found")
    await notifications_collection.insert_one({
        "tenant_id": tenant_id,
        "tenant_name": tenant["name"],
        "message": message,
        "status": "sent"
    })

    logger.info(f"Notification to {tenant['name']} (ID: {tenant_id}): {message}")
    return {"status": "success", "tenant_id": tenant_id, "message": message}