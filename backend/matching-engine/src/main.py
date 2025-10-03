"""
matching-engine Service
Version: 3.0.0
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import admin router
from admin.admin_routes import router as admin_router

app = FastAPI(
    title="matching-engine",
    version="3.0.0",
    description="TigerEx matching-engine with complete admin controls"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include admin router
app.include_router(admin_router)

@app.get("/")
async def root():
    return {
        "service": "matching-engine",
        "version": "3.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "matching-engine",
        "version": "3.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
