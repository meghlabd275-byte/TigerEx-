"""
TigerEx Complete Affiliate System
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

app = FastAPI()

class Affiliate(BaseModel):
    code: str
    user_id: str
    commission: float = 0.05

class Referral(BaseModel):
    affiliate_code: str
    referred_id: str
    tier: int = 1

class Store:
    def __init__(self):
        self.affiliates = {}
        self.referrals = {}
        self.commissions = {}
    
    def register(self, code: str, user_id: str) -> Affiliate:
        af = Affiliate(code=code, user_id=user_id)
        self.affiliates[code] = af
        return af
    
    def add_referral(self, code: str, user_id: str):
        if code not in self.affiliates:
            raise HTTPException(404, "Affiliate not found")
        ref = Referral(affiliate_code=code, referred_id=user_id)
        self.referrals[user_id] = ref
        self.affiliates[code].referred_count = getattr(self.affiliates[code], 'referred_count', 0) + 1
    
    def track_commission(self, code: str, amount: float):
        if code in self.commissions:
            self.commissions[code] += amount * 0.05
        else:
            self.commissions[code] = amount * 0.05
    
    def get_stats(self, code: str):
        if code not in self.affiliates:
            return {}
        a = self.affiliates[code]
        return {
            "code": a.code,
            "user_id": a.user_id,
            "referred": getattr(a, 'referred_count', 0),
            "commission": self.commissions.get(code, 0)
        }

store = Store()

@app.post("/register")
async def register(req: dict):
    return store.register(req["code"], req["user_id"])

@app.post("/referral")
async def add_ref(req: dict):
    store.add_referral(req["code"], req["user_id"])
    return {"status": "ok"}

@app.get("/stats/{code}")
async def stats(code: str):
    return store.get_stats(code)

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
