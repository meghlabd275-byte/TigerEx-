#!/usr/bin/env python3
"""
TigerEx institutional-trading Service
"""

from fastapi import FastAPI
import uvicorn
import os

app = FastAPI(
    title="TigerEx institutional-trading",
    description="Backend service for institutional-trading",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "institutional-trading"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8006))
    uvicorn.run(app, host="0.0.0.0", port=port)
