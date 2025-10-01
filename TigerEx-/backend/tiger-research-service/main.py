"""
Market research and insights
Port: 8084
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Tiger Research Service",
    description="Market research and insights",
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
        "service": "tiger-research-service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ['Market reports', 'Analysis', 'Insights']
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "tiger-research-service",
        "description": "Market research and insights",
        "version": "1.0.0",
        "features": ['Market reports', 'Analysis', 'Insights']
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8084)
