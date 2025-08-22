from fastapi import FastAPI
from app.routes import tenant_routes

app = FastAPI(title="Multi-Tenant SaaS Billing & Usage Analytics Platform")

# Register routes
app.include_router(tenant_routes.router, prefix="/tenants", tags=["Tenants"])