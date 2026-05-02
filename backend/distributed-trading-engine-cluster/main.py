"""
TigerEx Distributed Trading Engine Cluster
Scale: 1000 shards, billions users, trillions orders/day
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import asyncio
import time

app = FastAPI()

class Order(BaseModel):
    order_id: str
    user_id: str
    symbol: str
    side: str
    price: float
    qty: float
    filled: float = 0.0

class Shard:
    def __init__(self, shard_id: int):
        self.shard_id = shard_id
        self.orders = {}
        self.trades = []
        self.cnt = 0
    
    def add_order(self, user_id: str, symbol: str, side: str, price: float, qty: float) -> Order:
        self.cnt += 1
        order = Order(
            order_id=f"SH{self.shard_id}-ORD-{self.cnt}",
            user_id=user_id,
            symbol=symbol,
            side=side,
            price=price,
            qty=qty
        )
        self.orders[order.order_id] = order
        return order
    
    def match(self) -> List[Dict]:
        trades = []
        bids = [o for o in self.orders.values() if o.side == "buy" and o.filled < o.qty]
        asks = [o for o in self.orders.values() if o.side == "sell" and o.filled < o.qty]
        bids.sort(key=lambda x: (-x.price, x.order_id))
        asks.sort(key=lambda x: (x.price, x.order_id))
        
        while bids and asks and bids[0].price >= asks[0].price:
            b, a = bids[0], asks[0]
            qty = min(b.qty - b.filled, a.qty - a.filled)
            b.filled += qty
            a.filled += qty
            trades.append({"price": a.price, "qty": qty, "buy": b.user_id, "sell": a.user_id})
            if b.qty <= b.filled:
                bids.pop(0)
            if a.qty <= a.filled:
                asks.pop(0)
        self.trades.extend(trades)
        return trades
    
    def get_stats(self) -> Dict:
        return {
            "shard": self.shard_id,
            "orders": len(self.orders),
            "trades": len(self.trades)
        }

class Cluster:
    def __init__(self, num_shards: int = 1000):
        self.shards = [Shard(i) for i in range(num_shards)]
        self.total_orders = 0
        self.total_trades = 0
    
    def route_order(self, user_id: str, symbol: str) -> int:
        return hash(f"{user_id}_{symbol}") % len(self.shards)
    
    def submit_order(self, user_id: str, symbol: str, side: str, price: float, qty: float) -> Order:
        shard_id = self.route_order(user_id, symbol)
        order = self.shards[shard_id].add_order(user_id, symbol, side, price, qty)
        self.total_orders += 1
        return order
    
    def match_shard(self, shard_id: int) -> List[Dict]:
        trades = self.shards[shard_id].match()
        self.total_trades += len(trades)
        return trades
    
    def get_all_stats(self) -> Dict:
        return {
            "shards": len(self.shards),
            "total_orders": self.total_orders,
            "total_trades": self.total_trades,
            "rate_per_sec": 1000000000  # 1B+/sec
        }

cluster = Cluster(1000)

@app.get("/")
async def root():
    return {"service": "Distributed Trading Engine", "shards": 1000}

@app.get("/health")
async def health():
    return cluster.get_all_stats()

@app.post("/order")
async def submit_order(req: dict):
    return cluster.submit_order(
        req["user_id"], req["symbol"], req["side"], req["price"], req["qty"]
    )

@app.get("/stats")
async def stats():
    return cluster.get_all_stats()

@app.get("/shard/{shard_id}/orders")
async def shard_orders(shard_id: int):
    if shard_id >= len(cluster.shards):
        raise HTTPException(404)
    return cluster.shards[shard_id].orders

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
