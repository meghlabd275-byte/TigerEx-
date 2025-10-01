"""
NFT mystery box system
Port: 8071
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Mystery Box Service",
    description="NFT mystery box system",
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
        "service": "mystery-box-service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ['Random NFTs', 'Rarity tiers', 'Opening mechanics']
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "mystery-box-service",
        "description": "NFT mystery box system",
        "version": "1.0.0",
        "features": ['Random NFTs', 'Rarity tiers', 'Opening mechanics']
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8071)
