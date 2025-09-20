from motor.motor_asyncio import AsyncIOMotorClient
import os

# Load MongoDB connection URI from environment, default to local MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# Use environment variable for DB name, default to test DB
DB_NAME = os.getenv("DB_NAME", "saas_billing_test")

# Initialize async MongoDB client
client = AsyncIOMotorClient(MONGO_URI)

# Database for the SaaS Billing platform
db = client[DB_NAME]

# Collections
tenants_collection = db["Tenants"]
invoices_collection = db["invoices"]
admins_collection = db["admins"]
notifications_collection = db["notifications"]