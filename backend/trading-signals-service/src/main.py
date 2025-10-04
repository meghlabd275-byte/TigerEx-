"""
TigerEx trading-signals-service
Trading Signals and Analysis
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
    title="TigerEx trading-signals-service",
    description="Trading Signals and Analysis",
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
    return {"status": "healthy", "service": "trading-signals-service"}

@app.get("/api/status", response_model=ServiceStatus)
async def get_status():
    """Get service status and features"""
    return ServiceStatus(
        status="operational",
        service="trading-signals-service",
        features=['Technical signals', 'AI predictions', 'Market analysis', 'Alerts']
    )

@app.get("/api/info", response_model=ServiceInfo)
async def get_info():
    """Get service information"""
    return ServiceInfo(
        name="trading-signals-service",
        description="Trading Signals and Analysis",
        port=8047,
        features=['Technical signals', 'AI predictions', 'Market analysis', 'Alerts'],
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
        "service": "trading-signals-service",
        "features": ['Technical signals', 'AI predictions', 'Market analysis', 'Alerts'],
        "version": "1.0.0"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8047))
    uvicorn.run(app, host="0.0.0.0", port=port)
