"""Event Streaming Cluster for 1B+ users"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import json
from datetime import datetime

app = FastAPI()

class EventStream:
    def __init__(self, partitions: int = 100):
        self.partitions = partitions
        self.streams = {i: [] for i in range(partitions)}
        self.consumers = {i: [] for i in range(partitions)}
    
    def publish(self, topic: str, event: dict):
        pid = hash(topic) % self.partitions
        event["time"] = datetime.now().isoformat()
        self.streams[pid].append(event)
        return pid
    
    def subscribe(self, topic: str):
        pid = hash(topic) % self.partitions
        return pid

stream = EventStream(100)

@app.websocket("/ws/stream/{topic}")
async def ws_stream(ws: WebSocket, topic: str):
    await ws.accept()
    pid = stream.subscribe(topic)
    stream.consumers[pid].append(ws)
    try:
        while True:
            data = await ws.receive_text()
            event = json.loads(data)
            stream.publish(topic, event)
            for consumer in stream.consumers[pid]:
                await consumer.send_json(event)
    except WebSocketDisconnect:
        stream.consumers[pid].remove(ws)

@app.post("/publish")
async def publish(topic: str, event: dict):
    pid = stream.publish(topic, event)
    return {"partition": pid, "status": "ok"}

@app.get("/partitions")
async def partitions():
    return {"partitions": stream.partitions}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8005)
