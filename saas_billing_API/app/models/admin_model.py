from pydantic import BaseModel, EmailStr

class AdminCreate(BaseModel):
    email: EmailStr
    password: str

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class NotificationRequest(BaseModel):
    message: str