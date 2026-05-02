"""TigerEx Admin Control"""
from fastapi import FastAPI
from typing import List

app = FastAPI()

class Admin:
    def __init__(self):
        self.users = {}
        self.logs = []
    
    def add_user(self, uid, role):
        self.users[uid] = {"role": role, "active": True}
    
    def get_user(self, uid):
        return self.users.get(uid)
    
    def log(self, action):
        self.logs.append(action)

a = Admin()

@app.get("/health")
async def h():
    return {"s": "ok"}

@app.post("/user")
async def user(d: dict):
    a.add_user(d["user_id"], d["role"])
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
