"""TigerEx Token Listing Service"""
from fastapi import FastAPI
from typing import Optional
import time

app = FastAPI()

class Token:
    def __init__(self, symbol, name, decimals, total_supply):
        self.symbol, self.name = symbol, name
        self.decimals, self.supply = decimals, total_supply
        self.listed = False
        self.time = time.time()

class ListingStore:
    def __init__(self):
        self.tokens = {}
    
    def request(self, symbol, name, decimals, supply):
        t = Token(symbol, name, decimals, supply)
        self.tokens[symbol] = t
        return t
    
    def approve(self, symbol):
        if symbol in self.tokens:
            self.tokens[symbol].listed = True
            return True
        return False
    
    def get(self, symbol):
        return self.tokens.get(symbol)

store = ListingStore()

@app.get("/health")
async def h():
    return {"s": "ok", "tokens": len(store.tokens)}

@app.post("/request")
async def request(d: dict):
    return store.request(d["symbol"], d["name"], d["decimals"], d["supply"])

@app.post("/approve/{symbol}")
async def approve(symbol: str):
    return store.approve(symbol)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
