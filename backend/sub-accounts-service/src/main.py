"""
TigerEx sub-accounts-service
Sub-Accounts Management
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum
import uvicorn
import os

app = FastAPI(
    title="TigerEx sub-accounts-service",
    description="Sub-Accounts Management",
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
    return {"status": "healthy", "service": "sub-accounts-service"}

@app.get("/api/status", response_model=ServiceStatus)
async def get_status():
    """Get service status and features"""
    return ServiceStatus(
        status="operational",
        service="sub-accounts-service",
        features=['Multiple sub-accounts', 'Permission management', 'Fund allocation', 'Reporting']
    )

@app.get("/api/info", response_model=ServiceInfo)
async def get_info():
    """Get service information"""
    return ServiceInfo(
        name="sub-accounts-service",
        description="Sub-Accounts Management",
        port=8050,
        features=['Multiple sub-accounts', 'Permission management', 'Fund allocation', 'Reporting'],
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
        "service": "sub-accounts-service",
        "features": ['Multiple sub-accounts', 'Permission management', 'Fund allocation', 'Reporting'],
        "version": "1.0.0"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8050))
    uvicorn.run(app, host="0.0.0.0", port=port)
