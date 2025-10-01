"""
DeFi protocol staking
Port: 8062
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Defi Staking Service",
    description="DeFi protocol staking",
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
        "service": "defi-staking-service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ['Multi-protocol', 'Auto-compounding', 'Yield optimization']
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "defi-staking-service",
        "description": "DeFi protocol staking",
        "version": "1.0.0",
        "features": ['Multi-protocol', 'Auto-compounding', 'Yield optimization']
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8062)
