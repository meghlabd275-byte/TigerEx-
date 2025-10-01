"""
Liquidity mining rewards
Port: 8063
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Liquidity Mining Service",
    description="Liquidity mining rewards",
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
        "service": "liquidity-mining-service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ['LP rewards', 'Multiple pools', 'Impermanent loss tracking']
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "liquidity-mining-service",
        "description": "Liquidity mining rewards",
        "version": "1.0.0",
        "features": ['LP rewards', 'Multiple pools', 'Impermanent loss tracking']
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8063)
