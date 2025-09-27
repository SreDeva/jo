from app.config import db
from bson import ObjectId

# Distributor CRUD
def get_distributors():
    return list(db.distributors.find({}, {"_id": 1, "name": 1, "email": 1, "vendors": 1}))

def get_distributor_by_id(distributor_id):
    return db.distributors.find_one({"_id": distributor_id})

def get_distributor_by_email(email):
    return db.distributors.find_one({"email": email})

def add_distributor(distributor_data):
    return db.distributors.insert_one(distributor_data)

def update_distributor(distributor_id, update_data):
    db.distributors.update_one({"_id": distributor_id}, {"$set": update_data})

# Vendor CRUD
def add_vendor(distributor_id, vendor_data):
    # Generate a unique vendor_id if not provided
    if "vendor_id" not in vendor_data or not vendor_data["vendor_id"]:
        vendor_data["vendor_id"] = str(ObjectId())
    return db.distributors.update_one(
        {"_id": distributor_id},
        {"$push": {"vendors": vendor_data}}
    )

def get_vendors(distributor_id):
    distributor = db.distributors.find_one({"_id": distributor_id})
    if distributor:
        return distributor.get("vendors", [])
    return []

def update_vendor(distributor_id, vendor_id, vendor_data):
    """Update a specific vendor for a distributor"""
    return db.distributors.update_one(
        {"_id": distributor_id, "vendors.vendor_id": vendor_id},
        {"$set": {"vendors.$": vendor_data}}
    )

def delete_vendor(distributor_id, vendor_id):
    """Delete a specific vendor from distributor's vendor list"""
    return db.distributors.update_one(
        {"_id": distributor_id},
        {"$pull": {"vendors": {"vendor_id": vendor_id}}}
    )

def get_vendor_by_id(distributor_id, vendor_id):
    """Get a specific vendor by ID for a distributor"""
    distributor = db.distributors.find_one(
        {"_id": distributor_id, "vendors.vendor_id": vendor_id},
        {"vendors.$": 1}
    )
    if distributor and distributor.get("vendors"):
        return distributor["vendors"][0]
    return None
