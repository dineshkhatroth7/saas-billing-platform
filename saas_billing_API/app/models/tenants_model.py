from pydantic import BaseModel
from typing import Optional

class TenantCreate(BaseModel):
    name: str
    subscription_plan: str

class TenantOut(BaseModel):
    id: int 
    name: str
    subscription_plan: str
    active: bool = True
