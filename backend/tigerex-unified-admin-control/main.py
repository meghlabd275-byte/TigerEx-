"""
TigerEx Unified Admin Control System v3.0
Complete administrative control for all exchanges with role-based access and persistence.
Aligned with TigerEx Frontend and all requested features.
"""

import json
import logging
import os
import secrets
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import jwt
from fastapi import Body, Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

# @file main.py
# @description TigerEx tigerex-unified-admin-control service
# @author TigerEx Development Team
# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "tigerex-ultra-secure-admin-secret-2024")
JWT_ALGORITHM = "HS256"
ADMIN_DB_PATH = os.getenv("ADMIN_DB_PATH", "/tmp/tigerex_admin_db.json")

app = FastAPI(
    title="TigerEx Unified Admin Control v3.0.0",
    version="3.0.0",
    description="Advanced administrative control system for TigerEx ecosystem"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Enums
class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    EXCHANGE_ADMIN = "exchange_admin"
    TRADING_ADMIN = "trading_admin"
    USER_MANAGER = "user_manager"
    SUPPORT_ADMIN = "support_admin"
    READ_ONLY = "read_only"
    USER = "user"

class Exchange(str, Enum):
    BINANCE = "binance"
    BYBIT = "bybit"
    OKX = "okx"
    BITGET = "bitget"
    BITFINEX = "bitfinex"
    MEXC = "mexc"
    KRAKEN = "kraken"
    ROBINHOOD = "robinhood"
    HUOBI = "huobi"
    HTX = "htx"
    COINBASE = "coinbase"
    GATEIO = "gateio"
    WHITEBIT = "whitebit"

class Permission(str, Enum):
    MANAGE_USERS = "manage_users"
    VIEW_USERS = "view_users"
    DELETE_USERS = "delete_users"
    MANAGE_EXCHANGES = "manage_exchanges"
    VIEW_EXCHANGES = "view_exchanges"
    CONFIGURE_EXCHANGES = "configure_exchanges"
    MANAGE_API_KEYS = "manage_api_keys"
    VIEW_API_KEYS = "view_api_keys"
    MANAGE_TRADING = "manage_trading"
    VIEW_TRADING = "view_trading"
    STOP_TRADING = "stop_trading"
    MANAGE_FUNDS = "manage_funds"
    VIEW_BALANCES = "view_balances"
    APPROVE_WITHDRAWALS = "approve_withdrawns"
    MANAGE_SYSTEM = "manage_system"
    VIEW_LOGS = "view_logs"
    SYSTEM_MAINTENANCE = "system_maintenance"
    MANAGE_COMPLIANCE = "manage_compliance"
    VIEW_COMPLIANCE = "view_compliance"
    SECURITY_AUDIT = "security_audit"

class UserStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    HALTED = "halted"
    STOPPED = "stopped"
    BANNED = "banned"

class ControlAction(str, Enum):
    PAUSE = "pause"
    RESUME = "resume"
    HALT = "halt"
    STOP = "stop"
    BAN = "ban"
    UNBAN = "unban"

# Models
class User(BaseModel):
    user_id: str
    username: str
    email: str
    role: UserRole
    permissions: List[Permission]
    exchange_access: List[Exchange]
    created_at: str
    last_login: Optional[str] = None
    status: UserStatus = UserStatus.ACTIVE
    is_active: bool = True
    two_factor_enabled: bool = False
    is_email_verified: bool = True
    is_kyc_verified: bool = False
    trading_enabled: bool = True
    withdrawal_enabled: bool = True

class CreateUserRequest(BaseModel):
    username: str
    email: str
    role: UserRole
    exchange_access: List[Exchange]
    permissions: Optional[List[Permission]] = None

class UpdateUserRequest(BaseModel):
    email: Optional[str] = None
    role: Optional[UserRole] = None
    exchange_access: Optional[List[Exchange]] = None
    permissions: Optional[List[Permission]] = None
    status: Optional[UserStatus] = None
    trading_enabled: Optional[bool] = None
    withdrawal_enabled: Optional[bool] = None

class UpdateExchangeRequest(BaseModel):
    api_base_url: Optional[str] = None
    supported_features: Optional[List[str]] = None
    maintenance_mode: Optional[bool] = None
    status: Optional[str] = None

# Database Service
class AdminDB:
    def __init__(self, path: str):
        self.path = path
        self.data = {
            "users": {},
            "exchanges": {},
            "audit_logs": [],
            "api_keys": {},
            "system_config": {
                "trading_status": "active",
                "maintenance_mode": False,
                "global_halt": False
            }
        }
        self.load()
        if not self.data["users"]:
            self._init_default_admin()
        if not self.data["exchanges"]:
            self._init_exchanges()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r') as f:
                    self.data = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load DB: {e}")

    def save(self):
        try:
            with open(self.path, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save DB: {e}")

    def _init_default_admin(self):
        uid = "admin_001"
        self.data["users"][uid] = {
            "user_id": uid,
            "username": "tigerex_admin",
            "email": "admin@tigerex.com",
            "role": UserRole.SUPER_ADMIN,
            "permissions": [p.value for p in Permission],
            "exchange_access": [e.value for e in Exchange],
            "created_at": datetime.now().isoformat(),
            "status": UserStatus.ACTIVE,
            "is_active": True,
            "two_factor_enabled": False,
            "is_email_verified": True,
            "is_kyc_verified": True,
            "trading_enabled": True,
            "withdrawal_enabled": True
        }
        self.save()

    def _init_exchanges(self):
        for ex in Exchange:
            self.data["exchanges"][ex.value] = {
                "exchange": ex.value,
                "api_base_url": f"https://api.{ex.value}.com",
                "supported_features": ["spot", "futures", "margin", "earn"],
                "rate_limits": {"requests_per_min": 1000},
                "trading_fees": {"maker": 0.001, "taker": 0.001},
                "maintenance_mode": False,
                "status": "operational"
            }
        self.save()

db = AdminDB(ADMIN_DB_PATH)

# Auth Helpers
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id or user_id not in db.data["users"]:
            raise HTTPException(status_code=401, detail="Invalid token or user")
        user_dict = db.data["users"][user_id]
        if user_dict["status"] == UserStatus.BANNED:
             raise HTTPException(status_code=403, detail="User is banned")
        return User(**user_dict)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication")

def check_perm(user: User, perm: Permission):
    if user.role == UserRole.SUPER_ADMIN:
        return True
    user_perms = [p.value if isinstance(p, Permission) else p for p in user.permissions]
    if perm.value not in user_perms:
        raise HTTPException(status_code=403, detail=f"Missing permission: {perm}")

def log_audit(user_id: str, action: str, target: str, details: Dict[str, Any], request: Request = None):
    db.data["audit_logs"].append({
        "id": secrets.token_hex(8),
        "user_id": user_id,
        "action": action,
        "resource": target,
        "details": details,
        "timestamp": datetime.now().isoformat(),
        "ip_address": request.client.host if request else "system"
    })
    db.save()

# --- AUTH ENDPOINTS ---

@app.post("/auth/login")
@app.post("/tigerex/admin/login")
async def login(req_data: Dict[str, Any], request: Request):
    login_id = req_data.get("username") or req_data.get("email")
    password = req_data.get("password")

    # In a real app, verify against password hashes.
    # For this environment, we use the requested credentials.
    if (login_id == "tigerex_admin" or login_id == "admin@tigerex.com") and password == "tigerex123":
        user_id = "admin_001"
        user_dict = db.data["users"][user_id]
        token = jwt.encode({
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        user_dict["last_login"] = datetime.now().isoformat()
        db.save()
        
        log_audit(user_id, "LOGIN", "auth_system", {"method": "password"}, request)
        return {"access_token": token, "user": user_dict}

    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/auth/me")
@app.get("/tigerex/admin/me")
async def get_me(user: User = Depends(get_current_user)):
    return user

@app.post("/auth/logout")
async def logout(user: User = Depends(get_current_user), request: Request = None):
    log_audit(user.user_id, "LOGOUT", "auth_system", {}, request)
    return {"message": "Logged out"}

# --- SYSTEM & DASHBOARD ENDPOINTS ---

@app.get("/system/status")
@app.get("/tigerex/admin/dashboard")
async def get_system_status(user: User = Depends(get_current_user)):
    check_perm(user, Permission.VIEW_EXCHANGES)
    return {
        "trading_status": db.data["system_config"]["trading_status"],
        "server_time": datetime.now().isoformat(),
        "total_users": len(db.data["users"]),
        "active_users": len([u for u in db.data["users"].values() if u["status"] == UserStatus.ACTIVE]),
        "suspended_users": len([u for u in db.data["users"].values() if u["status"] == UserStatus.SUSPENDED]),
        "banned_users": len([u for u in db.data["users"].values() if u["status"] == UserStatus.BANNED]),
        "exchanges": db.data["exchanges"],
        "system_config": db.data["system_config"]
    }

# --- USER MANAGEMENT ENDPOINTS ---

@app.get("/users")
@app.get("/tigerex/admin/users")
async def list_users(user: User = Depends(get_current_user)):
    check_perm(user, Permission.VIEW_USERS)
    return {"users": list(db.data["users"].values())}

@app.post("/tigerex/admin/users")
async def create_user(req: CreateUserRequest, user: User = Depends(get_current_user), request: Request = None):
    check_perm(user, Permission.MANAGE_USERS)
    uid = f"user_{secrets.token_hex(4)}"
    new_user = {
        "user_id": uid,
        "username": req.username,
        "email": req.email,
        "role": req.role.value,
        "permissions": [p.value for p in (req.permissions or [])],
        "exchange_access": [e.value for e in req.exchange_access],
        "created_at": datetime.now().isoformat(),
        "status": UserStatus.ACTIVE.value,
        "is_active": True,
        "two_factor_enabled": False,
        "is_email_verified": True,
        "is_kyc_verified": False,
        "trading_enabled": True,
        "withdrawal_enabled": True
    }
    db.data["users"][uid] = new_user
    db.save()
    log_audit(user.user_id, "CREATE_USER", f"user:{uid}", {"username": req.username}, request)
    return new_user

@app.patch("/tigerex/admin/users/{uid}")
async def update_user(uid: str, req: UpdateUserRequest, user: User = Depends(get_current_user), request: Request = None):
    check_perm(user, Permission.MANAGE_USERS)
    if uid not in db.data["users"]:
        raise HTTPException(404, "User not found")
    
    target = db.data["users"][uid]
    update_data = req.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        if k == "permissions":
            target[k] = [p.value if isinstance(p, Permission) else p for p in v]
        elif k == "exchange_access":
            target[k] = [e.value if isinstance(e, Exchange) else e for e in v]
        elif isinstance(v, Enum):
            target[k] = v.value
        else:
            target[k] = v
    
    db.save()
    log_audit(user.user_id, "UPDATE_USER", f"user:{uid}", update_data, request)
    return target

@app.delete("/tigerex/admin/users/{uid}")
async def delete_user(uid: str, user: User = Depends(get_current_user), request: Request = None):
    check_perm(user, Permission.DELETE_USERS)
    if uid == "admin_001":
        raise HTTPException(400, "Cannot delete root admin")
    if uid in db.data["users"]:
        username = db.data["users"][uid]["username"]
        del db.data["users"][uid]
        db.save()
        log_audit(user.user_id, "DELETE_USER", f"user:{uid}", {"username": username}, request)
        return {"message": "User deleted"}
    raise HTTPException(status_code=404, detail="User not found")

# User Control Aliases (Frontend compatibility)
@app.post("/users/{uid}/suspend")
async def suspend_user(uid: str, body: Dict[str, Any] = Body(...), user: User = Depends(get_current_user), request: Request = None):
    check_perm(user, Permission.MANAGE_USERS)
    if uid not in db.data["users"]: raise HTTPException(404, "User not found")
    db.data["users"][uid]["status"] = UserStatus.SUSPENDED.value
    db.save()
    log_audit(user.user_id, "SUSPEND_USER", f"user:{uid}", body, request)
    return {"message": "User suspended"}

@app.post("/users/{uid}/activate")
async def activate_user(uid: str, user: User = Depends(get_current_user), request: Request = None):
    check_perm(user, Permission.MANAGE_USERS)
    if uid not in db.data["users"]: raise HTTPException(404, "User not found")
    db.data["users"][uid]["status"] = UserStatus.ACTIVE.value
    db.save()
    log_audit(user.user_id, "ACTIVATE_USER", f"user:{uid}", {}, request)
    return {"message": "User activated"}

@app.post("/users/{uid}/ban")
async def ban_user(uid: str, body: Dict[str, Any] = Body(...), user: User = Depends(get_current_user), request: Request = None):
    check_perm(user, Permission.MANAGE_USERS)
    if uid not in db.data["users"]: raise HTTPException(404, "User not found")
    db.data["users"][uid]["status"] = UserStatus.BANNED.value
    db.save()
    log_audit(user.user_id, "BAN_USER", f"user:{uid}", body, request)
    return {"message": "User banned"}

# --- SERVICE & EXCHANGE MANAGEMENT ---

@app.patch("/tigerex/admin/exchanges/{exchange_id}")
async def update_exchange(exchange_id: str, req: UpdateExchangeRequest, user: User = Depends(get_current_user), request: Request = None):
    check_perm(user, Permission.CONFIGURE_EXCHANGES)
    if exchange_id not in db.data["exchanges"]:
        raise HTTPException(status_code=404, detail="Exchange not found")
    
    cfg = db.data["exchanges"][exchange_id]
    update_data = req.model_dump(exclude_unset=True)
    cfg.update(update_data)
    db.save()
    log_audit(user.user_id, "UPDATE_EXCHANGE", f"exchange:{exchange_id}", update_data, request)
    return cfg

@app.post("/trading/halt")
async def halt_trading(body: Dict[str, Any] = Body(...), user: User = Depends(get_current_user), request: Request = None):
    check_perm(user, Permission.MANAGE_SYSTEM)
    db.data["system_config"]["trading_status"] = "halted"
    db.save()
    log_audit(user.user_id, "HALT_TRADING", "global", body, request)
    return {"message": "Trading halted"}

@app.post("/trading/resume")
async def resume_trading(user: User = Depends(get_current_user), request: Request = None):
    check_perm(user, Permission.MANAGE_SYSTEM)
    db.data["system_config"]["trading_status"] = "active"
    db.save()
    log_audit(user.user_id, "RESUME_TRADING", "global", {}, request)
    return {"message": "Trading resumed"}

@app.post("/emergency/stop")
async def emergency_stop(body: Dict[str, Any] = Body(...), user: User = Depends(get_current_user), request: Request = None):
    check_perm(user, Permission.MANAGE_SYSTEM)
    db.data["system_config"]["trading_status"] = "emergency_stopped"
    db.data["system_config"]["global_halt"] = True
    # Suspend all non-admin users
    for uid, udata in db.data["users"].items():
        if udata["role"] not in [UserRole.SUPER_ADMIN.value, UserRole.ADMIN.value]:
            udata["status"] = UserStatus.SUSPENDED.value
            udata["trading_enabled"] = False
    db.save()
    log_audit(user.user_id, "EMERGENCY_STOP", "global", body, request)
    return {"message": "Emergency stop executed. All non-admin users suspended."}

# --- AUDIT & LOGGING ---

@app.get("/audit/logs")
@app.get("/tigerex/admin/audit-log")
async def get_audit_logs(limit: int = 100, user: User = Depends(get_current_user)):
    check_perm(user, Permission.VIEW_LOGS)
    logs = db.data["audit_logs"][-limit:]
    return {"logs": logs, "audit_logs": logs} # Duplicate for compatibility

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "TigerEx-Unified-Admin",
        "version": "3.0.0",
        "db_connected": True,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
