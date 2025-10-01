"""
Liquidity mining and swap farming
Port: 8057
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Swap Farming Service",
    description="Liquidity mining and swap farming",
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
        "service": "swap-farming-service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ['Liquidity provision', 'Farming rewards', 'APY calculation']
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "swap-farming-service",
        "description": "Liquidity mining and swap farming",
        "version": "1.0.0",
        "features": ['Liquidity provision', 'Farming rewards', 'APY calculation']
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8057)
