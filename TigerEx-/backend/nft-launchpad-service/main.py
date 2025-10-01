"""
NFT project launchpad
Port: 8066
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Nft Launchpad Service",
    description="NFT project launchpad",
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
        "service": "nft-launchpad-service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ['NFT launches', 'Whitelist', 'Fair distribution']
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "nft-launchpad-service",
        "description": "NFT project launchpad",
        "version": "1.0.0",
        "features": ['NFT launches', 'Whitelist', 'Fair distribution']
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8066)
