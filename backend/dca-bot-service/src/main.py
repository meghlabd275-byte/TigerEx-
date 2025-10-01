"""
TigerEx dca-bot-service
Dollar Cost Averaging Bot Service
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
    title="TigerEx dca-bot-service",
    description="Dollar Cost Averaging Bot Service",
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
    return {"status": "healthy", "service": "dca-bot-service"}

@app.get("/api/status", response_model=ServiceStatus)
async def get_status():
    """Get service status and features"""
    return ServiceStatus(
        status="operational",
        service="dca-bot-service",
        features=['Automated DCA strategies', 'Flexible scheduling', 'Multi-asset support']
    )

@app.get("/api/info")
async def get_info():
    """Get service information"""
    return {
        "name": "dca-bot-service",
        "description": "Dollar Cost Averaging Bot Service",
        "version": "1.0.0",
        "port": 8032,
        "features": ['Automated DCA strategies', 'Flexible scheduling', 'Multi-asset support']
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8032))
    uvicorn.run(app, host="0.0.0.0", port=port)
