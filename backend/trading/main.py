#!/usr/bin/env python3
"""
TigerEx trading Service
"""

from fastapi import FastAPI
from admin.admin_routes import router as admin_router

import uvicorn
import os

# @file main.py
# @description TigerEx trading service
# @author TigerEx Development Team
app = FastAPI(
    title="TigerEx trading",
    description="Backend service for trading",
    version="1.0.0"
)

# Include admin router
app.include_router(admin_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "trading"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8009))
    uvicorn.run(app, host="0.0.0.0", port=port)
def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
