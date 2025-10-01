"""
Crypto gift cards
Port: 8073
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Gift Card Service",
    description="Crypto gift cards",
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
        "service": "gift-card-service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ['Gift cards', 'Redemption', 'Multiple denominations']
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "gift-card-service",
        "description": "Crypto gift cards",
        "version": "1.0.0",
        "features": ['Gift cards', 'Redemption', 'Multiple denominations']
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8073)
