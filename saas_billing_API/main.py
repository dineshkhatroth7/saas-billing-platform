from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from saas_billing_API.app.routes import tenant_routes,admin_routes
from saas_billing_API.app.utils.exceptions import (
    TenantNotFoundError,
    TenantAlreadyExistsError,
    InvalidPlanError,
    FeatureNotInPlanError,
    InvoiceNotFoundError
)

app = FastAPI(title="Multi-Tenant SaaS Billing & Usage Analytics Platform")
"""Main FastAPI application for SaaS billing and analytics."""


app.include_router(tenant_routes.router, prefix="/tenants", tags=["Tenants"])
app.include_router(admin_routes.router,tags=["Admin"])



@app.exception_handler(TenantNotFoundError)
async def tenant_not_found_handler(request: Request, exc: TenantNotFoundError):
    """Handle tenant not found errors with 404 response."""
    return JSONResponse(status_code=404, content={"detail": exc.message})

@app.exception_handler(TenantAlreadyExistsError)
async def tenant_exists_handler(request: Request, exc: TenantAlreadyExistsError):
    """Handle duplicate tenant creation errors with 400 response."""
    return JSONResponse(status_code=400, content={"detail": exc.message})

@app.exception_handler(InvalidPlanError)
async def invalid_plan_handler(request: Request, exc: InvalidPlanError):
    """Handle invalid subscription plan errors with 400 response."""
    return JSONResponse(status_code=400, content={"detail": exc.message})

@app.exception_handler(FeatureNotInPlanError)
async def feature_not_in_plan_handler(request: Request, exc: FeatureNotInPlanError):
    """Handle feature access outside plan errors with 403 response."""
    return JSONResponse(status_code=403, content={"detail": exc.message})

@app.exception_handler(InvoiceNotFoundError)
async def invoice_not_found_handler(request: Request, exc: InvoiceNotFoundError):
    """Handle missing invoice errors with 404 response."""
    return JSONResponse(status_code=404, content={"detail": exc.message})



@app.get("/", tags=["Health"])
async def health_check():
    """Health check endpoint to verify the app is running."""
    return {"status": "ok", "message": "SaaS Billing API is up and running"}
