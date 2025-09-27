from pydantic import BaseModel, EmailStr
from typing import List, Optional

class VendorModel(BaseModel):
    vendor_id: Optional[str]  # Can be auto-generated
    name: str
    email: EmailStr  # Used for Gmail API filtering
    logo_url: Optional[str] = None  # Optional placeholder

class DistributorModel(BaseModel):
    _id: Optional[str]
    name: str
    email: EmailStr
    password: Optional[str] = None  # hashed in production
    vendors: Optional[List[VendorModel]] = []
