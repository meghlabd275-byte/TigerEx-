"""
Automated portfolio rebalancing
Port: 8056
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Rebalancing Bot Service",
    description="Automated portfolio rebalancing",
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
        "service": "rebalancing-bot-service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ['Auto-rebalancing', 'Portfolio optimization', 'Risk management']
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "rebalancing-bot-service",
        "description": "Automated portfolio rebalancing",
        "version": "1.0.0",
        "features": ['Auto-rebalancing', 'Portfolio optimization', 'Risk management']
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8056)
