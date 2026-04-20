import os
import json
import logging
import secrets
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import jwt
from fastapi import Body, Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

# @file main.py
# @author TigerEx Development Team
JWT_SECRET = os.getenv("JWT_SECRET", "tigerex-ultra-secure-admin-secret-2024")
JWT_ALGORITHM = "HS256"
ADMIN_DB_PATH = os.getenv("ADMIN_DB_PATH", "/tmp/tigerex_admin_db.json")

app = FastAPI(title="TigerEx Unified Admin Control")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
security = HTTPBearer()

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    USER = "user"

class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"

class User(BaseModel):
    user_id: str
    username: str
    email: str
    role: str
    status: str

db_data = {
    "users": {
        "admin_001": {
            "user_id": "admin_001",
            "username": "tigerex_admin",
            "email": "admin@tigerex.com",
            "role": "super_admin",
            "status": "active"
        }
    },
    "system_config": {"trading_status": "active"}
}

@app.get("/health")
async def health(): return {"status": "healthy"}

@app.post("/auth/login")
async def login(req: Dict[str, Any]):
    if (req.get("username") == "tigerex_admin" or req.get("email") == "admin@tigerex.com") and req.get("password") == "tigerex123":
        token = jwt.encode({"user_id": "admin_001", "exp": datetime.utcnow() + timedelta(hours=24)}, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return {"access_token": token, "user": db_data["users"]["admin_001"]}
    raise HTTPException(401, "Invalid credentials")

@app.get("/tigerex/admin/dashboard")
async def dashboard(): return {"trading_status": db_data["system_config"]["trading_status"]}

@app.get("/tigerex/admin/users")
async def list_users(): return {"users": list(db_data["users"].values())}

@app.post("/tigerex/admin/users")
async def create_user(req: Dict[str, Any]):
    uid = f"user_{secrets.token_hex(4)}"
    db_data["users"][uid] = {"user_id": uid, **req, "status": "active"}
    return {"user_id": uid}

@app.post("/users/{uid}/suspend")
async def suspend_user(uid: str):
    if uid in db_data["users"]: db_data["users"][uid]["status"] = "suspended"
    return {"message": "ok"}

@app.post("/trading/halt")
async def halt_trading():
    db_data["system_config"]["trading_status"] = "halted"
    return {"message": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
