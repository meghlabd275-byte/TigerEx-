"""
ETH 2.0 staking service
Port: 8061
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Eth Staking Service",
    description="ETH 2.0 staking service",
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
        "service": "eth-staking-service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ['ETH staking', 'Validator management', 'Rewards distribution']
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "eth-staking-service",
        "description": "ETH 2.0 staking service",
        "version": "1.0.0",
        "features": ['ETH staking', 'Validator management', 'Rewards distribution']
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8061)
