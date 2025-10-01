"""
Sports and entertainment fan tokens
Port: 8070
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Fan Tokens Service",
    description="Sports and entertainment fan tokens",
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
        "service": "fan-tokens-service",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ['Fan engagement', 'Voting rights', 'Exclusive benefits']
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "fan-tokens-service",
        "description": "Sports and entertainment fan tokens",
        "version": "1.0.0",
        "features": ['Fan engagement', 'Voting rights', 'Exclusive benefits']
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8070)
