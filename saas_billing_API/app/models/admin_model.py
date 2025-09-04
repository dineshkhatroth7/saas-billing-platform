from pydantic import BaseModel, EmailStr

class AdminCreate(BaseModel):
    """Schema for creating a new admin account."""
    email: EmailStr
    password: str

class AdminLogin(BaseModel):
    """Schema for admin login credentials."""
    email: EmailStr
    password: str

class NotificationRequest(BaseModel):
    """Schema for sending a notification to a tenant."""
    message: str