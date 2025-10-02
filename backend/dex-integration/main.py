#!/usr/bin/env python3
"""
TigerEx dex-integration Service
"""

from fastapi import FastAPI
import uvicorn
import os

app = FastAPI(
    title="TigerEx dex-integration",
    description="Backend service for dex-integration",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "dex-integration"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8005))
    uvicorn.run(app, host="0.0.0.0", port=port)
