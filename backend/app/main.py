from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import distributor, vendor, auth

app = FastAPI(title="Distributor Vendor Contract API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth.router)
app.include_router(distributor.router)
app.include_router(vendor.router)

@app.get("/")
def root():
    return {"message": "Distributor Backend API running"}
