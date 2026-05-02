"""High Availability Load Balancer"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
from typing import List

app = FastAPI()

class LoadBalancer:
    def __init__(self):
        self.backends = []
        self.healthy = {}
        self.weights = {}
    
    def register(self, host: str, weight: int = 100):
        self.backends.append(host)
        self.healthy[host] = True
        self.weights[host] = weight
    
    def route(self) -> str:
        available = [h for h in self.backends if self.healthy.get(h, False)]
        if not available:
            raise HTTPException(503, "No healthy backends")
        # Weighted round-robin
        total = sum(self.weights[h] for h in available)
        r = random.randint(0, total)
        cum = 0
        for h in available:
            cum += self.weights[h]
            if r <= cum:
                return h
        return available[0]
    
    def health_check(self, host: str, healthy: bool):
        self.healthy[host] = healthy

lb = LoadBalancer()

class Backend(BaseModel):
    host: str
    weight: int = 100

@app.post("/register")
async def register(b: Backend):
    lb.register(b.host, b.weight)
    return {"status": "registered", "host": b.host}

@app.get("/route")
async def route():
    return {"backend": lb.route()}

@app.post("/health")
async def health_check(host: str, healthy: bool):
    lb.health_check(host, healthy)
    return {"status": "ok"}

@app.get("/backends")
async def backends():
    return {"backends": lb.backends, "healthy": lb.healthy}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8004)
