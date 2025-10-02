#!/usr/bin/env python3
"""
TigerEx perpetual-swap-service Service
"""

from fastapi import FastAPI
import uvicorn
import os

app = FastAPI(
    title="TigerEx perpetual-swap-service",
    description="Backend service for perpetual-swap-service",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "perpetual-swap-service"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8004))
    uvicorn.run(app, host="0.0.0.0", port=port)
