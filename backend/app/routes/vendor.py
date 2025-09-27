from fastapi import APIRouter
from app.services import db_service

router = APIRouter(prefix="/vendors", tags=["vendors"])

@router.post("/{distributor_id}/add")
def add_vendor(distributor_id: str, vendor: dict):
    db_service.add_vendor(distributor_id, vendor)
    return {"message": "Vendor added successfully"}

@router.get("/{distributor_id}")
def get_vendors(distributor_id: str):
    return db_service.get_vendors(distributor_id)
