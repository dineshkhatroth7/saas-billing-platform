from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = os.getenv("MONGO_URI") 

client = AsyncIOMotorClient(MONGO_URI)
db = client["sass_billing_model"]
tenants_collection = db["Tenants"]
invoices_collection = db["invoices"]
admins_collection = db["admins"]
notifications_collection=db["notifications"]