"""
TigerEx dual-investment-service
Dual Investment Service
"""

from fastapi import FastAPI
from admin.admin_routes import router as admin_router
, HTTPException
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
    title="TigerEx dual-investment-service",
    description="Dual Investment Service",
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

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "dual-investment-service"}

@app.get("/api/status", response_model=ServiceStatus)
async def get_status():
    """Get service status and features"""
    return ServiceStatus(
        status="operational",
        service="dual-investment-service",
        features=['Dual currency products', 'Yield generation', 'Settlement management']
    )

@app.get("/api/info")
async def get_info():
    """Get service information"""
    return {
        "name": "dual-investment-service",
        "description": "Dual Investment Service",
        "version": "1.0.0",
        "port": 8039,
        "features": ['Dual currency products', 'Yield generation', 'Settlement management']
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8039))
    uvicorn.run(app, host="0.0.0.0", port=port)
