from pydantic import BaseModel,Field
from typing import Dict, Any, List,Literal,Optional
from datetime import datetime

class TenantCreate(BaseModel):
    """Schema for creating a new tenant."""
    name: str
    subscription_plan: Literal["free", "premium", "enterprise"]


class TenantOut(BaseModel):
    """Schema for returning tenant details."""
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
    execution_time_ms: Optional[int] = None


class UsageRecord(BaseModel):
    """Schema for recording feature usage by a tenant."""
    feature: str
    count: int

class PlanUpdate(BaseModel):
    """Schema for updating a tenant’s subscription plan."""
    new_plan: Literal["free", "premium", "enterprise"]


class TenantDeleteResponse(BaseModel):
    """Response schema after deactivating a tenant."""
    tenant_id: int
    name: str
    active: bool
    deleted_at: datetime
    message: str

class UsageSummary(BaseModel):
    """Schema summarizing a tenant’s usage across features."""
    tenant_id: int
    usage: List[UsageRecord]

class Invoice(BaseModel):
    """Schema representing a generated invoice for a tenant."""
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

class TenantNotification(BaseModel):
    """Schema representing a notification for a tenant."""
    tenant_id: int
    tenant_name: str
    message: str
    status: str   
