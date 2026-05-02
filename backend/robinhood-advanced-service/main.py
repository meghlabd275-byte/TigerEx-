"""TigerEx Binance Service Integration"""
from fastapi import FastAPI
from typing import Dict

app = FastAPI()

class BinanceClient:
    def __init__(self):
        self.api_key = ""
        self.secret = ""
        self.base_url = "https://api.binance.com"
        self.orders = {}
    
    def create_order(self, symbol, side, qty, price):
        oid = f"BN-{symbol}-{side}-{qty}"
        self.orders[oid] = {"symbol": symbol, "side": side, "qty": qty, "price": price}
        return oid
    
    def get_order(self, oid):
        return self.orders.get(oid)
    
    def cancel(self, oid):
        if oid in self.orders:
            del self.orders[oid]
            return True
        return False
    
    def get_balance(self, asset):
        return {"asset": asset, "free": 1000.0, "locked": 0.0}

c = BinanceClient()

@app.get("/health")
async def h():
    return {"s": "ok", "exchange": "binance", "orders": len(c.orders)}

@app.post("/order")
async def order(d: dict):
    return {"id": c.create_order(d["symbol"], d["side"], d["qty"], d["price"])}

@app.get("/balance/{asset}")
async def balance(asset: str):
    return c.get_balance(asset)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
