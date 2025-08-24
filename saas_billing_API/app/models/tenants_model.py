from pydantic import BaseModel
from typing import Dict, Any, List,Literal
from datetime import datetime

class TenantCreate(BaseModel):
    name: str
    subscription_plan: Literal["free", "premium", "enterprise"]

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


class UsageRecord(BaseModel):
    feature: str
    count: int

class PlanUpdate(BaseModel):
    new_plan: Literal["free", "premium", "enterprise"]


class TenantDeleteResponse(BaseModel):
    tenant_id: int
    name: str
    active: bool
    deleted_at: datetime
    message: str

class UsageSummary(BaseModel):
    tenant_id: int
    usage: List[UsageRecord]