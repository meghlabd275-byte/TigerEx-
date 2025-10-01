"""
Trading competitions and contests
Port: 8082
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Trading Competition Service",
    description="Trading competitions and contests",
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
        "service": "trading-competition-service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ['Competitions', 'Prizes', 'Leaderboards']
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "trading-competition-service",
        "description": "Trading competitions and contests",
        "version": "1.0.0",
        "features": ['Competitions', 'Prizes', 'Leaderboards']
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8082)
