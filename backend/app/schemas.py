from pydantic import BaseModel, EmailStr
from typing import List, Optional

class Vendor(BaseModel):
    vendor_id: Optional[str]
    name: str
    email: EmailStr
    logo_url: Optional[str] = None

class Distributor(BaseModel):
    _id: Optional[str]
    name: str
    email: EmailStr
    password: Optional[str] = None
    vendors: Optional[List[Vendor]] = []
