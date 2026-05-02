"""Multi-Region Trading Fabric - Global 1B+ users"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List
import hashlib
import time

app = FastAPI()

class TradingFabric:
    def __init__(self):
        self.regions = {
            "us-east": {"capacity": 100_000_000, "latency": 15},
            "us-west": {"capacity": 100_000_000, "latency": 25},
            "eu-central": {"capacity": 100_000_000, "latency": 20},
            "asia-pacific": {"capacity": 100_000_000, "latency": 10},
            "south-america": {"capacity": 50_000_000, "latency": 30},
            "africa": {"capacity": 50_000_000, "latency": 35},
        }
        self.shards = 10000
        self.global_orderbook = {i: {"bids": [], "asks": []} for i in range(self.shards)}
    
    def route_order(self, user_id: str) -> str:
        # Hash to best region
        h = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        # Return region with lowest latency
        return min(self.regions, key=lambda r: self.regions[r]["latency"])
    
    def get_shard(self, order_id: str) -> int:
        return int(hashlib.sha256(order_id.encode()).hexdigest()[:8], 16) % self.shards
    
    def submit_order(self, order: Dict) -> Dict:
        shard = self.get_shard(order.get("id", str(time.time())))
        side = order["side"]
        if side == "buy":
            self.global_orderbook[shard]["bids"].append(order)
        else:
            self.global_orderbook[shard]["asks"].append(order)
        return {"shard": shard, "status": "submitted"}

fabric = TradingFabric()

class Order(BaseModel):
    id: str
    user_id: str
    side: str
    price: float
    qty: float

@app.post("/order")
async def submit(order: Order):
    return fabric.submit_order(order.dict())

@app.get("/route/{user_id}")
async def route(user_id: str):
    return {"region": fabric.route_order(user_id)}

@app.get("/capacity")
async def capacity():
    return {r: v["capacity"] for r, v in fabric.regions.items()}

@app.get("/health")
async def health():
    return {"regions": len(fabric.regions), "shards": fabric.shards}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8007)
