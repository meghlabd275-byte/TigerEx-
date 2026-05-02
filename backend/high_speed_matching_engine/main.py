"""TigerEx High-Speed Matching Engine v10.0"""
from fastapi import FastAPI, WebSocket
from typing import Dict, List
import asyncio
import time
from collections import defaultdict
from datetime import datetime

app = FastAPI()

class Order:
    def __init__(self, oid: int, side: str, price: float, qty: float, user: str):
        self.id = oid
        self.side = side
        self.price = price
        self.qty = qty
        self.remain = qty
        self.user = user
        self.time = time.time()

class MatchingEngine:
    def __init__(self):
        self.oid = 0
        self.orders = []
        self.trades = []
        self.bids = []
        self.asks = []
    
    def add_order(self, side: str, price: float, qty: float, user: str) -> Order:
        self.oid += 1
        order = Order(self.oid, side, price, qty, user)
        self.orders.append(order)
        if side == "buy":
            self.bids.append(order)
            self.bids.sort(key=lambda x: (-x.price, x.time))
        else:
            self.asks.append(order)
            self.asks.sort(key=lambda x: (x.price, x.time))
        return order
    
    def match(self) -> List[Dict]:
        trades = []
        while self.bids and self.asks:
            bid = self.bids[0]
            ask = self.asks[0]
            if bid.price < ask.price:
                break
            price = ask.price
            qty = min(bid.remain, ask.remain)
            trades.append({
                "price": price,
                "qty": qty,
                "buyer": bid.user,
                "seller": ask.user,
                "time": datetime.now().isoformat()
            })
            bid.remain -= qty
            ask.remain -= qty
            if bid.remain <= 0:
                self.bids.pop(0)
            if ask.remain <= 0:
                self.asks.pop(0)
        self.trades.extend(trades)
        return trades

engine = MatchingEngine()

@app.websocket("/ws/match")
async def ws_match(ws: WebSocket):
    await ws.accept()
    while True:
        data = await ws.receive_json()
        side = data.get("side")
        price = float(data.get("price", 0))
        qty = float(data.get("qty", 0))
        user = data.get("user", "anon")
        
        if side in ["buy", "sell"]:
            order = engine.add_order(side, price, qty, user)
            trades = engine.match()
            await ws.send_json({
                "order": {"id": order.id, "side": side, "price": price, "qty": qty},
                "trades": trades
            })

@app.get("/api/v1/depth")
async def get_depth(limit: int = 10):
    return {
        "bids": [{"price": o.price, "qty": o.remain} for o in engine.bids[:limit]],
        "asks": [{"price": o.price, "qty": o.remain} for o in engine.asks[:limit]]
    }

@app.get("/api/v1/trades")
async def get_trades(limit: int = 50):
    return engine.trades[-limit:]

@app.get("/health")
async def health():
    return {"status": "ok", "orders": engine.oid, "trades": len(engine.trades)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
