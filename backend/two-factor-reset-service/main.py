"""TigerEx 2FA Reset Service"""
from fastapi import FastAPI
import uuid
import time

app = FastAPI()

class Reset:
    def __init__(self):
        self.requests = {}
    
    def request(self, user_id):
        token = str(uuid.uuid4())
        self.requests[token] = {"user": user_id, "time": time.time()}
        return token
    
    def verify(self, token):
        return token in self.requests

r = Reset()

@app.get("/health")
async def h():
    return {"s": "ok"}

@app.post("/request")
async def req(d: dict):
    return {"token": r.request(d["user_id"])}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
