"""
TigerEx block-trading-service
Block Trading Service for Large Orders
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

# Include admin router
app.include_router(admin_router)
    title="TigerEx block-trading-service",
    description="Block Trading Service for Large Orders",
    version="1.0.0"
)

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

class ServiceInfo(BaseModel):
    name: str
    description: str
    port: int
    features: List[str]
    endpoints: List[str]

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "block-trading-service"}

@app.get("/api/status", response_model=ServiceStatus)
async def get_status():
    """Get service status and features"""
    return ServiceStatus(
        status="operational",
        service="block-trading-service",
        features=['Large block trades', 'Negotiated pricing', 'Settlement', 'Privacy']
    )

@app.get("/api/info", response_model=ServiceInfo)
async def get_info():
    """Get service information"""
    return ServiceInfo(
        name="block-trading-service",
        description="Block Trading Service for Large Orders",
        port=8043,
        features=['Large block trades', 'Negotiated pricing', 'Settlement', 'Privacy'],
        endpoints=[
            "/health",
            "/api/status",
            "/api/info"
        ]
    )

@app.get("/api/features")
async def get_features():
    """Get available features"""
    return {
        "service": "block-trading-service",
        "features": ['Large block trades', 'Negotiated pricing', 'Settlement', 'Privacy'],
        "version": "1.0.0"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8043))
    uvicorn.run(app, host="0.0.0.0", port=port)
