from pydantic import BaseModel,Field
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

class Invoice(BaseModel):
    tenant_id: int
    tenant_name: str
    billing_date: datetime
    plan: str
    base_price: float
    usage_charges: float
    usage_details: Dict[str, Any]  
    total_due: float
    usage_snapshot: Dict[str, int] 
    id: str = Field(default=None, alias="_id")  
