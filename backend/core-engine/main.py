"""TigerEx Core Trading Engine"""
from fastapi import FastAPI, WebSocket
from typing import Dict, Any
import asyncio
import random
from datetime import datetime

app = FastAPI()

class OrderBook:
    def __init__(self):
        self.bids = []
        self.asks = []
    
    def add_order(self, order_type: str, price: float, amount: float, user_id: str):
        order = {"type": order_type, "price": price, "amount": amount, "user": user_id, "time": datetime.now().isoformat()}
        if order_type == "bid":
            self.bids.append(order)
            self.bids.sort(key=lambda x: x["price"], reverse=True)
        else:
            self.asks.append(order)
            self.asks.sort(key=lambda x: x["price"])
        return order
    
    def match(self) -> list:
        trades = []
        while self.bids and self.asks and self.bids[0]["price"] >= self.asks[0]["price"]:
            bid = self.bids[0]
            ask = self.asks[0]
            qty = min(bid["amount"], ask["amount"])
            trades.append({"price": ask["price"], "qty": qty, "buyer": bid["user"], "seller": ask["user"]})
            bid["amount"] -= qty
            ask["amount"] -= qty
            if bid["amount"] <= 0:
                self.bids.pop(0)
            if ask["amount"] <= 0:
                self.asks.pop(0)
        return trades

orderbook = OrderBook()

@app.websocket("/ws/orderbook/{symbol}")
async def ws_orderbook(ws: WebSocket, symbol: str):
    await ws.accept()
    while True:
        data = await ws.receive_json()
        if data.get("type") in ["bid", "ask"]:
            orderbook.add_order(data["type"], data["price"], data["amount"], data.get("user", "anon"))
            trades = orderbook.match()
            if trades:
                await ws.send_json({"trades": trades})

@app.get("/api/v1/orderbook/{symbol}")
async def get_orderbook(symbol: str):
    return {"bids": orderbook.bids[:10], "asks": orderbook.asks[:10]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8002)
def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
