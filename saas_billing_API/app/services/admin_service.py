from app.db.mongo import admins_collection
from passlib.hash import bcrypt
from app.utils.jwt import create_access_token
from app.utils.logger import logger  

async def register_admin(email: str, password: str):
    existing = await admins_collection.find_one({"email": email})
    if existing:
        logger.warning(f"Admin registration failed: {email} already exists")  
        return None

    hashed_password = bcrypt.hash(password)
    result = await admins_collection.insert_one({
        "email": email,
        "password": hashed_password
    })
    logger.info(f"Admin registered successfully: {email}")  
    return {"id": str(result.inserted_id), "email": email}


async def login_admin(email: str, password: str):
    admin = await admins_collection.find_one({"email": email})
    if not admin or not bcrypt.verify(password, admin["password"]):
        logger.warning(f"Admin login failed: {email}")  
        return None

    token = create_access_token({"sub": str(admin["_id"]), "role": "admin"})
    logger.info(f"Admin logged in: {email}")  
    return token
