"""
TigerEx insurance-fund-service
Insurance Fund Service
"""

from fastapi import FastAPI
from admin.admin_routes import router as admin_router
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum
import uvicorn
import os

app = FastAPI(
    title="TigerEx insurance-fund-service",
    description="Insurance Fund Service",
    version="1.0.0"
)

# Include admin router
app.include_router(admin_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ServiceStatus(BaseModel):
    status: str
    service: str
    version: str = "1.0.0"
    features: List[str]

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "insurance-fund-service"}

@app.get("/api/status", response_model=ServiceStatus)
async def get_status():
    """Get service status and features"""
    return ServiceStatus(
        status="operational",
        service="insurance-fund-service",
        features=['Fund management', 'Risk coverage', 'Claim processing']
    )

@app.get("/api/info")
async def get_info():
    """Get service information"""
    return {
        "name": "insurance-fund-service",
        "description": "Insurance Fund Service",
        "version": "1.0.0",
        "port": 8036,
        "features": ['Fund management', 'Risk coverage', 'Claim processing']
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8036))
    uvicorn.run(app, host="0.0.0.0", port=port)
