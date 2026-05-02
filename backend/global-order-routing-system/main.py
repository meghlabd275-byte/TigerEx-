"""Global Order Routing System - Routes orders to nearest shard"""
from fastapi import FastAPI
from typing import Dict
import hashlib
import geoip2.database

app = FastAPI()

class Router:
    def __init__(self):
        self.regions = {
            "us-east": {"shards": 250, "latency": 20},
            "us-west": {"shards": 250, "latency": 35},
            "eu-west": {"shards": 250, "latency": 25},
            "asia-east": {"shards": 250, "latency": 15},
        }
        self.shard_map = {}
    
    def route(self, user_id: str, region: str = "us-east") -> Dict:
        shard = int(hashlib.md5(user_id.encode()).hexdigest()[:8], 16) % self.regions[region]["shards"]
        return {"shard": shard, "region": region, "latency": self.regions[region]["latency"]}
    
    def get_best_region(self, latency: int) -> str:
        return min(self.regions, key=lambda x: self.regions[x]["latency"])

router = Router()

@app.get("/route/{user_id}")
async def route(user_id: str, region: str = "us-east"):
    return router.route(user_id, region)

@app.get("/health")
async def health():
    return {"regions": len(router.regions), "status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8002)
