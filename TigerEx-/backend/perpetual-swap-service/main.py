"""
Perpetual swap contracts with funding rates
Port: 8055
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Perpetual Swap Service",
    description="Perpetual swap contracts with funding rates",
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
        "service": "perpetual-swap-service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ['Perpetual swaps', 'Funding rates', 'Mark price', 'Index price']
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "perpetual-swap-service",
        "description": "Perpetual swap contracts with funding rates",
        "version": "1.0.0",
        "features": ['Perpetual swaps', 'Funding rates', 'Mark price', 'Index price']
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8055)
