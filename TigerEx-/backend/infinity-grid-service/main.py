"""
Infinity grid trading bot
Port: 8058
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Infinity Grid Service",
    description="Infinity grid trading bot",
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
        "service": "infinity-grid-service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ['Infinite grid', 'Dynamic ranges', 'Auto-adjustment']
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "infinity-grid-service",
        "description": "Infinity grid trading bot",
        "version": "1.0.0",
        "features": ['Infinite grid', 'Dynamic ranges', 'Auto-adjustment']
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8058)
