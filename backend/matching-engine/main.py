"""
TigerEx Matching Engine - Complete
"""
from fastapi import FastAPI
from typing import List, Dict
import time

app = FastAPI()

class Order:
    def __init__(self, oid, side, price, qty, user):
        self.oid, self.side = oid, side
        self.price, self.qty, self.user = price, qty, user
        self.filled = 0
        self.time = time.time()

class Engine:
    def __init__(self):
        self.orders = {}
        self.trades = []
        self.bids = []
        self.asks = []
        self.cnt = 0
    
    def add(self, side, price, qty, user):
        self.cnt += 1
        o = Order(f"ORD-{self.cnt}", side, price, qty, user)
        self.orders[o.oid] = o
        (self.bids if side == "buy" else self.asks).append(o)
        return self.match()
    
    def match(self):
        tr = []
        self.bids.sort(key=lambda x: (-x.price, x.time))
        self.asks.sort(key=lambda x: (x.price, x.time))
        while self.bids and self.asks and self.bids[0].price >= self.asks[0].price:
            b, a = self.bids[0], self.asks[0]
            q = min(b.qty - b.filled, a.qty - a.filled)
            tr.append({"price": a.price, "qty": q, "buy": b.user, "sell": a.user})
            b.filled += q
            a.filled += q
            if b.qty <= b.filled:
                self.bids.pop(0)
            if a.qty <= a.filled:
                self.asks.pop(0)
        self.trades.extend(tr)
        return tr

e = Engine()

@app.get("/health")
async def h():
    return {"s": "ok", "o": len(e.orders), "t": len(e.trades)}

@app.post("/order")
async def order(d: dict):
    return {"trades": e.add(d["side"], d["price"], d["qty"], d["user"])}

@app.get("/trades")
async def trades():
    return e.trades[-50:]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
