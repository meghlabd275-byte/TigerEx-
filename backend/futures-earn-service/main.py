#!/usr/bin/env python3
"""
TigerEx futures-earn-service Service
"""

from fastapi import FastAPI
import uvicorn
import os

app = FastAPI(
    title="TigerEx futures-earn-service",
    description="Backend service for futures-earn-service",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "futures-earn-service"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8010))
    uvicorn.run(app, host="0.0.0.0", port=port)
