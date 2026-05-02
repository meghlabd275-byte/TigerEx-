"""Edge Computing Network - Sub-millisecond execution"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import time

app = FastAPI()

class EdgeNode:
    def __init__(self, node_id: str, location: str, latency_us: int):
        self.node_id = node_id
        self.location = location
        self.latency_us = latency_us
        self.orders_executed = 0
    
    def execute(self, order: dict) -> dict:
        self.orders_executed += 1
        return {
            "order_id": order.get("id"),
            "executed_at": time.time(),
            "latency_us": self.latency_us,
            "node": self.node_id
        }

# Global edge nodes
nodes = [
    EdgeNode("edge-us-1", "New York", 500),
    EdgeNode("edge-us-2", "Los Angeles", 600),
    EdgeNode("edge-eu-1", "Frankfurt", 400),
    EdgeNode("edge-eu-2", "London", 450),
    EdgeNode("edge-as-1", "Tokyo", 300),
    EdgeNode("edge-as-2", "Singapore", 250),
    EdgeNode("edge-as-3", "Mumbai", 350),
    EdgeNode("edge-sa-1", "São Paulo", 500),
]

class Order(BaseModel):
    id: str
    user_id: str
    side: str
    price: float
    qty: float

@app.post("/execute")
async def execute(order: Order):
    # Find nearest edge
    node = min(nodes, key=lambda n: n.latency_us)
    result = node.execute(order.dict())
    return result

@app.get("/nodes")
async def get_nodes():
    return [{"id": n.node_id, "location": n.location, "latency": n.latency_us} for n in nodes]

@app.get("/health")
async def health():
    return {"nodes": len(nodes), "status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8008)
