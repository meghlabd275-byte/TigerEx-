"""
Institutional custody solutions
Port: 8078
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Custody Solutions Service",
    description="Institutional custody solutions",
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
        "service": "custody-solutions-service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ['Cold storage', 'Multi-sig', 'Insurance']
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "custody-solutions-service",
        "description": "Institutional custody solutions",
        "version": "1.0.0",
        "features": ['Cold storage', 'Multi-sig', 'Insurance']
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8078)
