
class TenantError(Exception):
    """Base exception for tenant-related errors."""
    pass


class TenantNotFoundError(TenantError):
    def __init__(self, tenant_id: int):
        self.tenant_id = tenant_id
        self.message = f"Tenant with id {tenant_id} not found."
        super().__init__(self.message)



class TenantAlreadyExistsError(TenantError):
    def __init__(self, tenant_name: str):
        self.tenant_name = tenant_name
        self.message = f"Tenant '{tenant_name}' already exists."
        super().__init__(self.message)


class InvalidPlanError(TenantError):
    def __init__(self, plan: str):
        self.plan = plan
        self.message = f"Invalid subscription plan: {plan}"
        super().__init__(self.message)

class FeatureNotInPlanError(TenantError):
    def __init__(self, feature: str, plan: str):
        self.feature = feature
        self.plan = plan
        self.message = f"Feature '{feature}' is not included in plan '{plan}'."
        super().__init__(self.message)

class InvoiceNotFoundError(TenantError):
    def __init__(self, tenant_id: int):
        self.tenant_id = tenant_id
        self.message = f"No invoice found for tenant {tenant_id}"
        super().__init__(self.message)
