"""TigerEx Service"""
from fastapi import FastAPI
from typing import Dict, List
import uuid
from datetime import datetime

app = FastAPI()

class Store:
    def __init__(self): self.data = {}
    def add(self, item: Dict) -> Dict:
        id = str(uuid.uuid4())
        self.data[id] = {**item, "id": id, "created": datetime.now().isoformat()}
        return self.data[id]
    def get(self, id: str) -> Dict:
        return self.data.get(id)
    def all(self) -> List[Dict]:
        return list(self.data.values())

store = Store()

@app.get("/health")
async def health(): return {"status": "ok"}

@app.get("/api/v1/list")
async def list_items(): return store.all()

@app.post("/api/v1/add")
async def add(item: Dict): return store.add(item)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
