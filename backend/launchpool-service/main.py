"""TigerEx Service"""
from fastapi import FastAPI
from typing import Dict, Any
import asyncio, random, uuid
from datetime import datetime

app = FastAPI()

class ServiceStore:
    def __init__(self):
        self.data = {}
        self.tx = []
    
    def add_tx(self, tx_type: str, data: Dict) -> Dict:
        tx = {"id": str(uuid.uuid4()), "type": tx_type, "data": data, "time": datetime.now().isoformat()}
        self.tx.append(tx)
        return tx
    
    def get_txs(self, limit: int = 50) -> list:
        return self.tx[-limit:]

store = ServiceStore()

@app.get("/health")
async def health():
    return {"status": "ok", "service": "active"}

@app.get("/api/v1/txs")
async def getTxs(limit: int = 50):
    return store.get_txs(limit)

@app.post("/api/v1/tx")
async def createTx(tx_type: str, data: Dict):
    return store.add_tx(tx_type, data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
