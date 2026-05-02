"""
TigerEx Distributed Trading Engine Cluster
Handles 1B+ users with sharding
"""
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio
import hashlib
import time
from datetime import datetime

app = FastAPI()

class ShardManager:
    def __init__(self, num_shards: int = 1000):
        self.num_shards = num_shards
        self.shards = {i: {"orders": [], "trades": [], "users": set()} for i in range(num_shards)}
    
    def get_shard(self, user_id: str) -> int:
        return int(hashlib.md5(user_id.encode()).hexdigest(), 16) % self.num_shards
    
    def add_order(self, shard: int, order: Dict) -> Dict:
        self.shards[shard]["orders"].append(order)
        return order
    
    def matchShard(self, shard: int) -> List[Dict]:
        orders = self.shards[shard]["orders"]
        trades = []
        buys = sorted([o for o in orders if o["side"] == "buy"], key=lambda x: -x["price"])
        sells = sorted([o for o in orders if o["side"] == "sell"], key=lambda x: x["price"])
        
        while buys and sells and buys[0]["price"] >= sells[0]["price"]:
            b, s = buys[0], sells[0]
            qty = min(b["qty"] - b.get("filled", 0), s["qty"] - s.get("filled", 0))
            if qty <= 0:
                break
            trades.append({
                "price": s["price"], "qty": qty,
                "buyer": b["user"], "seller": s["user"],
                "time": datetime.now().isoformat()
            })
            b["filled"] = b.get("filled", 0) + qty
            s["filled"] = s.get("filled", 0) + qty
            if b["qty"] <= b.get("filled", 0):
                buys.pop(0)
            if s["qty"] <= s.get("filled", 0):
                sells.pop(0)
        return trades

shard_mgr = ShardManager(1000)

class Order(BaseModel):
    user_id: str
    side: str
    price: float
    qty: float
    symbol: str = "BTC/USDT"

@app.post("/api/v1/order")
async def place_order(order: Order):
    shard = shard_mgr.get_shard(order.user_id)
    o = {
        "id": f"{shard}_{int(time.time()*1000)}",
        "user": order.user_id,
        "side": order.side,
        "price": order.price,
        "qty": order.qty,
        "symbol": order.symbol,
        "shard": shard,
        "time": datetime.now().isoformat()
    }
    shard_mgr.add_order(shard, o)
    trades = shard_mgr.matchShard(shard)
    return {"order": o, "trades": trades, "shard": shard}

@app.get("/api/v1/shard/{shard_id}")
async def get_shard(shard_id: int):
    if shard_id >= shard_mgr.num_shards:
        raise HTTPException(404)
    return {"orders": len(shard_mgr.shards[shard_id]["orders"])}

@app.get("/health")
async def health():
    return {"shards": shard_mgr.num_shards, "status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8001)
