"""TigerEx SERVICE"""
from fastapi import FastAPI
from typing import Dict, List
import uuid
from datetime import datetime

app = FastAPI()

class Manager:
    def __init__(self):
        self.items = {}
    
    def add(self, data: Dict) -> Dict:
        item = {**data, "id": str(uuid.uuid4()), "created": datetime.now().isoformat()}
        self.items[item["id"]] = item
        return item
    
    def get(self, id: str) -> Dict:
        return self.items.get(id)
    
    def all(self) -> List[Dict]:
        return list(self.items.values())

mgr = Manager()

@app.get("/health")
async def health():
    return {"status": "ok", "service": "active"}

@app.get("/api/v1/list")
async def list_items():
    return mgr.all()

@app.post("/api/v1/add")
async def add(data: Dict):
    return mgr.add(data)

@app.get("/api/v1/get/{id}")
async def get(id: str):
    return mgr.get(id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
