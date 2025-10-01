"""
Social trading feed
Port: 8081
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Social Feed Service",
    description="Social trading feed",
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
        "service": "social-feed-service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ['Trading feed', 'Social interactions', 'Content sharing']
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "social-feed-service",
        "description": "Social trading feed",
        "version": "1.0.0",
        "features": ['Trading feed', 'Social interactions', 'Content sharing']
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)
