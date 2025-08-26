import os
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Header

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour


def create_access_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    """
    Generate JWT access token with expiry.
    `data` should include identifying info like {"sub": user_id, "role": "admin"}.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {**data, "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(token: str) -> dict:
    """
    Decode and validate JWT token.
    Raises HTTPException if token is expired or invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def admin_required(authorization: str = Header(...)) -> dict:
    """
    Dependency for FastAPI routes.
    Validates JWT and checks if role is admin.
    Use in routes with `Depends(admin_required)`.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing Bearer token")
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized as admin")
    return payload
