"""
Merchant payment solutions
Port: 8074
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Merchant Solutions Service",
    description="Merchant payment solutions",
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
        "service": "merchant-solutions-service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ['Payment processing', 'Settlement', 'API integration']
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "merchant-solutions-service",
        "description": "Merchant payment solutions",
        "version": "1.0.0",
        "features": ['Payment processing', 'Settlement', 'API integration']
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8074)
