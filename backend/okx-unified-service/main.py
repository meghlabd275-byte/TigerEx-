# @file main.py
# @description TigerEx backend service
# @author TigerEx Development Team

from fastapi import FastAPI
app = FastAPI(title="TigerEx okx-unified-service")
@app.get("/")
async def index(): return {"message": "TigerEx okx-unified-service Operational"}
@app.get("/health")
async def health(): return {"status": "healthy"}
