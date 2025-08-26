from fastapi import FastAPI
from app.routes import tenant_routes,admin_routes

app = FastAPI(title="Multi-Tenant SaaS Billing & Usage Analytics Platform")

# Register routes
app.include_router(tenant_routes.router, prefix="/tenants", tags=["Tenants"])
app.include_router(admin_routes.router)