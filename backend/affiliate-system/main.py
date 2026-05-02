"""TigerEx Affiliate System"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

app = FastAPI()

class AffiliateStore:
    def __init__(self):
        self.affiliates = {}
        self.referrals = {}
    
    def register(self, code: str, user_id: str):
        self.affiliates[code] = {"user": user_id, "referrals": 0, "earnings": 0, "joined": datetime.now().isoformat()}
        return self.affiliates[code]
    
    def track_referral(self, code: str):
        if code in self.affiliates:
            self.affiliates[code]["referrals"] += 1
            return True
        return False
    
    def add_earnings(self, code: str, amount: float):
        if code in self.affiliates:
            self.affiliates[code]["earnings"] += amount
            return True
        return False
    
    def get_stats(self, code: str):
        return self.affiliates.get(code, {})

store = AffiliateStore()

class ReferralModel(BaseModel):
    code: str
    user_id: str

@app.post("/affiliate/register")
async def registerAffiliate(r: ReferralModel):
    return store.register(r.code, r.user_id)

@app.post("/affiliate/referral")
async def trackReferral(code: str):
    if store.track_referral(code):
        return {"status": "ok", "referrals": store.affiliates[code]["referrals"]}
    raise HTTPException(status_code=404, detail="Code not found")

@app.get("/affiliate/stats/{code}")
async def getStats(code: str):
    stats = store.get_stats(code)
    if not stats:
        raise HTTPException(status_code=404)
    return stats

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8003)
