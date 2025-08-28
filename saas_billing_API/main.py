from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.routes import tenant_routes, admin_routes
from app.utils.exceptions import (
    TenantNotFoundError,
    TenantAlreadyExistsError,
    InvalidPlanError,
    FeatureNotInPlanError,
    InvoiceNotFoundError
)

app = FastAPI(title="Multi-Tenant SaaS Billing & Usage Analytics Platform")


app.include_router(tenant_routes.router, prefix="/tenants", tags=["Tenants"])
app.include_router(admin_routes.router)



@app.exception_handler(TenantNotFoundError)
async def tenant_not_found_handler(request: Request, exc: TenantNotFoundError):
    return JSONResponse(status_code=404, content={"detail": exc.message})

@app.exception_handler(TenantAlreadyExistsError)
async def tenant_exists_handler(request: Request, exc: TenantAlreadyExistsError):
    return JSONResponse(status_code=400, content={"detail": exc.message})

@app.exception_handler(InvalidPlanError)
async def invalid_plan_handler(request: Request, exc: InvalidPlanError):
    return JSONResponse(status_code=400, content={"detail": exc.message})

@app.exception_handler(FeatureNotInPlanError)
async def feature_not_in_plan_handler(request: Request, exc: FeatureNotInPlanError):
    return JSONResponse(status_code=403, content={"detail": exc.message})

@app.exception_handler(InvoiceNotFoundError)
async def invoice_not_found_handler(request: Request, exc: InvoiceNotFoundError):
    return JSONResponse(status_code=404, content={"detail": exc.message})
