from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from pydantic import BaseModel
from app.services import db_service
from app.services.file_processor import extract_vendors_from_document, validate_extracted_vendors
import hashlib
import uuid

router = APIRouter(prefix="/auth", tags=["authentication"])

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str

def hash_password(password: str) -> str:
    """Simple password hashing using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/login")
def login(request: LoginRequest):
    try:
        distributor = db_service.get_distributor_by_email(request.email)
        if not distributor:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        hashed_password = hash_password(request.password)
        if distributor.get("password") != hashed_password:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Remove password from response
        distributor.pop("password", None)
        return {
            "success": True,
            "message": "Login successful",
            "user": distributor
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/signup")
async def signup(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    distributorDocument: UploadFile = File(...)
):
    try:
        # Check if user already exists
        existing_user = db_service.get_distributor_by_email(email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Validate file type
        allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.csv', '.xlsx']
        file_extension = '.' + distributorDocument.filename.split('.')[-1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload PDF, DOC, DOCX, TXT, CSV, or XLSX files.")
        
        # Read and process the distributor document
        file_content = await distributorDocument.read()
        extracted_vendors = await extract_vendors_from_document(file_content, distributorDocument.filename)
        
        # Validate extracted vendor data
        validate_extracted_vendors(extracted_vendors)
        
        # Create new distributor with extracted vendors
        hashed_password = hash_password(password)
        distributor_data = {
            "_id": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "password": hashed_password,
            "vendors": extracted_vendors
        }
        
        result = db_service.add_distributor(distributor_data)
        if result.inserted_id:
            # Remove password from response
            distributor_data.pop("password", None)
            return {
                "success": True,
                "message": f"Account created successfully with {len(extracted_vendors)} vendors extracted",
                "user": distributor_data
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create account")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
