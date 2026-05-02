"""TigerEx Exchange Unified Service"""
from fastapi import FastAPI
from typing import Dict, List
import time

app = FastAPI()

class ExchangeClient:
    def __init__(self, name):
        self.name = name
        self.base_url = f"https://api.{name}.com"
        self.orders = {}
        self.balances = {}
    
    def create_order(self, symbol, side, qty, price, order_type="limit"):
        oid = f"{self.name[:2].upper()}-{int(time.time())}"
        self.orders[oid] = {"symbol": symbol, "side": side, "qty": qty, "price": price, "type": order_type}
        return oid
    
    def get_order(self, oid):
        return self.orders.get(oid)
    
    def cancel(self, oid):
        return oid in self.orders and self.orders.pop(oid, None)
    
    def get_balance(self, asset):
        return self.balances.get(asset, {"free": 0, "locked": 0})

c = ExchangeClient("exchange")

@app.get("/health")
async def h():
    return {"s": "ok", "exchange": c.name, "orders": len(c.orders)}

@app.post("/order")
async def order(d: dict):
    return {"id": c.create_order(d["symbol"], d["side"], d["qty"], d["price"])}

@app.get("/order/{oid}")
async def get(oid: str):
    return c.get_order(oid)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
