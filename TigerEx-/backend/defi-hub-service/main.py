"""
Centralized DeFi protocol hub
Port: 8075
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Defi Hub Service",
    description="Centralized DeFi protocol hub",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "defi-hub-service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ['Protocol aggregation', 'Yield comparison', 'One-click access']
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "defi-hub-service",
        "description": "Centralized DeFi protocol hub",
        "version": "1.0.0",
        "features": ['Protocol aggregation', 'Yield comparison', 'One-click access']
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8075)
