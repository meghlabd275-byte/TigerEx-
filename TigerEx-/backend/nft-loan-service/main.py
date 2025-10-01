"""
NFT-collateralized loans
Port: 8068
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Nft Loan Service",
    description="NFT-collateralized loans",
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
        "service": "nft-loan-service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ['NFT collateral', 'Instant loans', 'Liquidation']
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "nft-loan-service",
        "description": "NFT-collateralized loans",
        "version": "1.0.0",
        "features": ['NFT collateral', 'Instant loans', 'Liquidation']
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8068)
