"""
TigerEx Advanced Trading Engine v10.0
High-frequency trading with AI signals
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional
import asyncio
import random
import time
from datetime import datetime

app = FastAPI()

class TradingEngine:
    def __init__(self):
        self.orders = {}
        self.order_id = 0
        self.order_book = {"buy": [], "sell": []}
    
    async def place_order(self, side: str, symbol: str, price: float, amount: float):
        self.order_id += 1
        order = {
            "id": self.order_id,
            "side": side,
            "symbol": symbol,
            "price": price,
            "amount": amount,
            "status": "open",
            "timestamp": datetime.now().isoformat()
        }
        self.orders[self.order_id] = order
        if side == "buy":
            self.order_book["buy"].append(order)
        else:
            self.order_book["sell"].append(order)
        return order
    
    async def match_orders(self, symbol: str):
        matched = []
        buy_orders = sorted([o for o in self.order_book["buy"] if o["symbol"] == symbol], key=lambda x: x["price"], reverse=True)
        sell_orders = sorted([o for o in self.order_book["sell"] if o["symbol"] == symbol], key=lambda x: x["price"])
        
        for buy in buy_orders:
            for sell in sell_orders:
                if buy["price"] >= sell["price"] and buy["amount"] > 0 and sell["amount"] > 0:
                    trade_amount = min(buy["amount"], sell["amount"])
                    matched.append({
                        "symbol": symbol,
                        "price": sell["price"],
                        "amount": trade_amount,
                        "buyer": buy["id"],
                        "seller": sell["id"],
                        "time": datetime.now().isoformat()
                    })
                    buy["amount"] -= trade_amount
                    sell["amount"] -= trade_amount
        return matched
    
    async def get_ticker(self, symbol: str) -> Dict:
        return {
            "symbol": symbol,
            "last": random.uniform(1000, 50000),
            "change": random.uniform(-5, 5),
            "volume": random.uniform(100, 10000),
            "high": random.uniform(1000, 50000),
            "low": random.uniform(1000, 50000)
        }

engine = TradingEngine()

@app.websocket("/ws/market")
async def market_websocket(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            msg = data.json()
            if msg.get("action") == "subscribe":
                symbol = msg.get("symbol", "BTC/USDT")
                while True:
                    ticker = await engine.get_ticker(symbol)
                    await ws.send_json(ticker)
                    await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass

@app.post("/api/v1/order")
async def place_order(side: str, symbol: str, price: float, amount: float):
    return await engine.place_order(side, symbol, price, amount)

@app.get("/api/v1/ticker/{symbol}")
async def get_ticker(symbol: str):
    return await engine.get_ticker(symbol)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
