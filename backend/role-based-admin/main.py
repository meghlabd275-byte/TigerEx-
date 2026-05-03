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
def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
