"""TigerEx Trading Signals Service"""
from fastapi import FastAPI
from typing import List
import time

app = FastAPI()

class Signal:
    def __init__(self, sid, symbol, action, price, confidence):
        self.sid, self.symbol = sid, symbol
        self.action, self.price = action, price
        self.confidence = confidence
        self.time = time.time()

class SignalStore:
    def __init__(self):
        self.signals = {}
        self.cnt = 0
    
    def create(self, symbol, action, price, confidence):
        self.cnt += 1
        s = Signal(f"SIG-{self.cnt}", symbol, action, price, confidence)
        self.signals[s.sid] = s
        return s
    
    def get_recent(self, symbol=None, limit=10):
        sigs = list(self.signals.values())
        if symbol:
            sigs = [s for s in sigs if s.symbol == symbol]
        return sigs[-limit:]

store = SignalStore()

@app.get("/health")
async def h():
    return {"s": "ok", "signals": len(store.signals)}

@app.post("/signal")
async def signal(d: dict):
    return store.create(d["symbol"], d["action"], d["price"], d["confidence"])

@app.get("/signals")
async def signals(s: str = None):
    return store.get_recent(s)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
