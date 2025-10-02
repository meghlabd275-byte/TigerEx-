#!/usr/bin/env python3
"""
TigerEx staking-service Service
"""

from fastapi import FastAPI
import uvicorn
import os

app = FastAPI(
    title="TigerEx staking-service",
    description="Backend service for staking-service",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "staking-service"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8005))
    uvicorn.run(app, host="0.0.0.0", port=port)
