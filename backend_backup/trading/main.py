#!/usr/bin/env python3
"""
TigerEx trading Service
"""

from fastapi import FastAPI
from admin.admin_routes import router as admin_router

import uvicorn
import os

app = FastAPI(

# Include admin router
app.include_router(admin_router)
    title="TigerEx trading",
    description="Backend service for trading",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "trading"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8009))
    uvicorn.run(app, host="0.0.0.0", port=port)
