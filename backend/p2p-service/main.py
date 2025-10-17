#!/usr/bin/env python3
"""
TigerEx p2p-service Service
"""

from fastapi import FastAPI
from admin.admin_routes import router as admin_router

import uvicorn
import os

app = FastAPI(
    title="TigerEx p2p-service",
    description="Backend service for p2p-service",
    version="1.0.0"
)

# Include admin router
app.include_router(admin_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "p2p-service"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8008))
    uvicorn.run(app, host="0.0.0.0", port=port)
