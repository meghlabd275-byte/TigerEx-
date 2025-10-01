"""
Multi-marketplace NFT aggregator
Port: 8069
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Nft Aggregator Service",
    description="Multi-marketplace NFT aggregator",
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
        "service": "nft-aggregator-service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ['Cross-marketplace', 'Best prices', 'Unified interface']
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "nft-aggregator-service",
        "description": "Multi-marketplace NFT aggregator",
        "version": "1.0.0",
        "features": ['Cross-marketplace', 'Best prices', 'Unified interface']
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8069)
