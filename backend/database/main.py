#!/usr/bin/env python3
"""
TigerEx database Service
"""

from fastapi import FastAPI
import uvicorn
import os

app = FastAPI(
    title="TigerEx database",
    description="Backend service for database",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "database"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8003))
    uvicorn.run(app, host="0.0.0.0", port=port)
