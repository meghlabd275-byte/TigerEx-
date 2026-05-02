"""TigerEx Service"""
from fastapi import FastAPI
from typing import Dict, List
import uuid, asyncio, random
from datetime import datetime

app = FastAPI()

data = {}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "active"}

@app.get("/api/v1/list")
async def list_items():
    return list(data.values())

@app.post("/api/v1/add")
async def add(item: Dict):
    id = str(uuid.uuid4())
    data[id] = {**item, "id": id, "created": datetime.now().isoformat()}
    return data[id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
