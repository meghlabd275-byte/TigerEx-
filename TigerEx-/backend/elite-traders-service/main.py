"""
Elite trader program
Port: 8080
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Elite Traders Service",
    description="Elite trader program",
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
        "service": "elite-traders-service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ['Trader verification', 'Performance tracking', 'Leaderboards']
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "elite-traders-service",
        "description": "Elite trader program",
        "version": "1.0.0",
        "features": ['Trader verification', 'Performance tracking', 'Leaderboards']
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
