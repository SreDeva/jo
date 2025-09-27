from fastapi import APIRouter, HTTPException, Body
from app.services import db_service

router = APIRouter(prefix="/distributors", tags=["distributors"])

@router.get("/")
def list_distributors():
    return db_service.get_distributors()

@router.get("/{distributor_id}")
def get_distributor(distributor_id: str):
    dist = db_service.get_distributor_by_id(distributor_id)
    if not dist:
        raise HTTPException(status_code=404, detail="Distributor not found")
    return dist

@router.get("/email/{email}")
def get_distributor_by_email(email: str):
    dist = db_service.get_distributor_by_email(email)
    if not dist:
        raise HTTPException(status_code=404, detail="Distributor not found")
    # Remove password from response
    dist.pop("password", None)
    return dist

@router.put("/{distributor_id}")
def update_distributor_profile(distributor_id: str, update_data: dict = Body(...)):
    db_service.update_distributor(distributor_id, update_data)
    return {"message": "Profile updated successfully"}
