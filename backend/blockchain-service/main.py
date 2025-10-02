#!/usr/bin/env python3
"""
TigerEx blockchain-service Service
"""

from fastapi import FastAPI
import uvicorn
import os

app = FastAPI(
    title="TigerEx blockchain-service",
    description="Backend service for blockchain-service",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "blockchain-service"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
