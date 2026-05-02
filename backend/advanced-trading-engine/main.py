"""TigerEx Advanced Trading Engine"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from collections import defaultdict
from enum import Enum
import time

app = FastAPI()

class Status(Enum):
    OPEN = "open"
    FILLED = "filled"
    CANCELLED = "cancelled"

class Order:
    def __init__(self, oid, user, side, sym, price, qty):
        self.oid, self.user, self.side = oid, user, side
        self.sym, self.price, self.qty = sym, price, qty
        self.filled = 0
        self.status = Status.OPEN
        self.time = time.time()

class Engine:
    def __init__(self):
        self.orders = {}
        self.ob = defaultdict(lambda: {"bids": [], "asks": []})
        self.cnt = 0
    
    def new_id(self):
        self.cnt += 1
        return f"ORD-{self.cnt}"
    
    def create(self, user, side, sym, price, qty):
        o = Order(self.new_id(), user, side, sym, price, qty)
        self.orders[o.oid] = o
        self.ob[sym]["bids" if side == "buy" else "asks"].append(o)
        self.sort(sym)
        return o, self.match(sym)
    
    def sort(self, sym):
        self.ob[sym]["bids"].sort(key=lambda x: (-x.price, x.time))
        self.ob[sym]["asks"].sort(key=lambda x: (x.price, x.time))
    
    def match(self, sym):
        tr = []
        b, a = self.ob[sym]["bids"], self.ob[sym]["asks"]
        while b and a and b[0].price >= a[0].price:
            q = min(b[0].qty - b[0].filled, a[0].qty - a[0].filled)
            tr.append({"p": a[0].price, "q": q, "buy": b[0].user, "sell": a[0].user})
            b[0].filled += q
            a[0].filled += q
            if b[0].qty <= b[0].filled:
                b.pop(0)
            if a[0].qty <= a[0].filled:
                a.pop(0)
        return tr

engine = Engine()

class R(BaseModel):
    user_id: str
    side: str
    symbol: str
    price: float
    qty: float

@app.get("/health") 
async def h():
    return {"s": "ok", "o": len(engine.orders)}

@app.post("/o")
async def c(r: R):
    o, t = engine.create(r.user_id, r.side, r.symbol, r.price, r.qty)
    return {"id": o.oid, "st": o.status.value, "tr": t}

@app.get("/ob/{s}")
async def ob(s: str):
    b = [{"p": x.price, "q": x.qty - x.filled} for x in engine.ob[s]["bids"][:10]]
    a = [{"p": x.price, "q": x.qty - x.filled} for x in engine.ob[s]["asks"][:10]]
    return {"b": b, "a": a}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8001)
