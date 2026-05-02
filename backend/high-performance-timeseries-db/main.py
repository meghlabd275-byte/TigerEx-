"""High-Performance Time-Series DB for Order History"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import time
import asyncio

app = FastAPI()

class TimeSeriesDB:
    def __init__(self):
        self.data = []
        self.index = {}
    
    def write(self, metric: str, value: float, tags: Dict = None) -> Dict:
        ts = time.time()
        record = {"ts": ts, "metric": metric, "value": value, "tags": tags or {}}
        self.data.append(record)
        key = f"{metric}"
        if key not in self.index:
            self.index[key] = []
        self.index[key].append(record)
        return record
    
    def read(self, metric: str, limit: int = 100) -> List[Dict]:
        return self.index.get(metric, [])[-limit:]
    
    def aggregate(self, metric: str, window: str = "1m") -> Dict:
        records = self.index.get(metric, [])
        if not records:
            return {}
        values = [r["value"] for r in records]
        return {
            "count": len(values),
            "sum": sum(values),
            "avg": sum(values)/len(values),
            "min": min(values),
            "max": max(values)
        }

tsdb = TimeSeriesDB()

class Metric(BaseModel):
    metric: str
    value: float
    tags: Dict = {}

@app.post("/write")
async def write(m: Metric):
    return tsdb.write(m.metric, m.value, m.tags)

@app.get("/read/{metric}")
async def read(metric: str, limit: int = 100):
    return tsdb.read(metric, limit)

@app.get("/agg/{metric}")
async def agg(metric: str):
    return tsdb.aggregate(metric)

@app.get("/health")
async def health():
    return {"records": len(tsdb.data), "status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8010)
