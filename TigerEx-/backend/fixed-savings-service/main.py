"""
Fixed-term savings products
Port: 8060
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Fixed Savings Service",
    description="Fixed-term savings products",
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
        "service": "fixed-savings-service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ['Fixed terms', 'Guaranteed APY', 'Auto-renewal']
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "fixed-savings-service",
        "description": "Fixed-term savings products",
        "version": "1.0.0",
        "features": ['Fixed terms', 'Guaranteed APY', 'Auto-renewal']
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8060)
