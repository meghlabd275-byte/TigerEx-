#!/usr/bin/env python3
"""
TigerEx analytics-service Service
"""

from fastapi import FastAPI
import uvicorn
import os

app = FastAPI(
    title="TigerEx analytics-service",
    description="Backend service for analytics-service",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "analytics-service"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
