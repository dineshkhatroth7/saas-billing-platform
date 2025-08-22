from pydantic import BaseModel
from typing import Dict, Any, List
from datetime import datetime

class TenantCreate(BaseModel):
    name: str
    subscription_plan: str

class TenantOut(BaseModel):
    id: str 
    tenant_id: int 
    name: str
    subscription_plan: str
    active: bool
    features: List[str]
    quotas: Dict[str, Any]
    pricing: Dict[str, Any]
    base_price: float
    created_at: datetime
    updated_at: datetime