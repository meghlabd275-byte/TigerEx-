"""
TigerEx leveraged-tokens-service
Leveraged Tokens Service
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
    title="TigerEx leveraged-tokens-service",
    description="Leveraged Tokens Service",
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
    return {"status": "healthy", "service": "leveraged-tokens-service"}

@app.get("/api/status", response_model=ServiceStatus)
async def get_status():
    """Get service status and features"""
    return ServiceStatus(
        status="operational",
        service="leveraged-tokens-service",
        features=['Leveraged ETF tokens', 'Auto-rebalancing', '3x leverage', 'Risk management']
    )

@app.get("/api/info", response_model=ServiceInfo)
async def get_info():
    """Get service information"""
    return ServiceInfo(
        name="leveraged-tokens-service",
        description="Leveraged Tokens Service",
        port=8044,
        features=['Leveraged ETF tokens', 'Auto-rebalancing', '3x leverage', 'Risk management'],
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
        "service": "leveraged-tokens-service",
        "features": ['Leveraged ETF tokens', 'Auto-rebalancing', '3x leverage', 'Risk management'],
        "version": "1.0.0"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8044))
    uvicorn.run(app, host="0.0.0.0", port=port)
