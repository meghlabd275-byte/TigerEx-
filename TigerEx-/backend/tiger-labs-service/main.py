"""
TigerEx research and innovation lab
Port: 8083
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Tiger Labs Service",
    description="TigerEx research and innovation lab",
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
        "service": "tiger-labs-service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ['Research reports', 'Market analysis', 'Innovation projects']
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "tiger-labs-service",
        "description": "TigerEx research and innovation lab",
        "version": "1.0.0",
        "features": ['Research reports', 'Market analysis', 'Innovation projects']
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8083)
