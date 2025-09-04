from motor.motor_asyncio import AsyncIOMotorClient
import os


# Load MongoDB connection URI from environment
MONGO_URI = os.getenv("MONGO_URI") 


# Initialize async MongoDB client
client = AsyncIOMotorClient(MONGO_URI)

# Database for the SaaS Billing platform
db = client["sass_billing_model"]

# Collections
tenants_collection = db["Tenants"]
invoices_collection = db["invoices"]
admins_collection = db["admins"]
notifications_collection=db["notifications"]