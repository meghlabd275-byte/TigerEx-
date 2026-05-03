"""TigerEx Earn Service - Staking & Savings"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

app = FastAPI()

class EarnProduct(BaseModel):
    product_id: str
    coin: str
    apy: float
    duration_days: int
    min_amount: float

class EarnPosition(BaseModel):
    user_id: str
    product_id: str
    amount: float

products = [
    {"product_id": "eth-staking", "coin": "ETH", "apy": 5.2, "duration_days": 30, "min_amount": 0.1},
    {"product_id": "btc-saver", "coin": "BTC", "apy": 3.8, "duration_days": 60, "min_amount": 0.01},
    {"product_id": "usdt-fixed", "coin": "USDT", "apy": 8.5, "duration_days": 90, "min_amount": 100},
]

positions = {}

@app.get("/earn/products")
async def getProducts():
    return products

@app.post("/earn/subscribe")
async def subscribe(p: EarnPosition):
    for prod in products:
        if prod["product_id"] == p.product_id:
            if p.amount < prod["min_amount"]:
                raise HTTPException(status_code=400, detail="Below minimum")
            pos = {
                "product": p.product_id,
                "amount": p.amount,
                "start": datetime.now().isoformat(),
                "apy": prod["apy"],
            }
            positions[f"{p.user_id}_{p.product_id}"] = pos
            return pos
    raise HTTPException(status_code=404, detail="Product not found")

@app.get("/earn/positions/{user_id}")
async def getPositions(user_id: str):
    return [v for k, v in positions.items() if k.startswith(user_id)]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8004)
def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
