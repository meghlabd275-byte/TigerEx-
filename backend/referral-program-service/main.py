"""TigerEx Referral Program"""
from fastapi import FastAPI

app = FastAPI()

class Program:
    def __init__(self):
        self.referrals = {}
        self.rewards = {}

@app.get("/health")
async def h():
    return {"s": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
