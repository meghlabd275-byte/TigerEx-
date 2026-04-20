#!/usr/bin/env python3
"""
TigerEx Complete Backend Services API
Full Admin Control with Role-Based Access
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

app = FastAPI(title="TigerEx API", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= ENUMS =============
class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    PARTNER = "partner"
    WHITE_LEVEL = "white_level"
    INSTITUTIONAL = "institutional"
    LISTING_MANAGER = "listing_manager"
    TRADING_MANAGER = "trading_manager"
    COMPLIANCE = "compliance"
    SUPPORT = "support"
    VIP = "vip"
    TRADER = "trader"

class ExchangeStatus(str, Enum):
    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"
    PAUSED = "paused"
    HALTED = "halted"

class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    BANNED = "banned"

# ============= MODELS =============
class User(BaseModel):
    id: str
    email: str
    name: str
    role: UserRole
    status: UserStatus
    verification: VerificationStatus
    trading_fee: float = 0.1
    withdrawal_fee: float = 0.5
    kyc_level: int = 0
    created_at: datetime = datetime.now()

class ExchangeSettings(BaseModel):
    name: str = "TigerEx"
    exchange_id: str = "TIGEREX-2026"
    status: ExchangeStatus = ExchangeStatus.OPERATIONAL
    white_label: bool = False
    maker_fee: float = 0.1
    taker_fee: float = 0.1

class TradingFees(BaseModel):
    maker_fee: float = 0.1
    taker_fee: float = 0.1
    withdrawal_fee: float = 0.5
    deposit_fee: float = 0.0
    role_fees: dict = {
        "super_admin": 0.0,
        "admin": 0.0,
        "moderator": 0.0,
        "partner": 0.05,
        "white_level": 0.08,
        "institutional": 0.07,
        "listing_manager": 0.0,
        "trading_manager": 0.0,
        "compliance": 0.0,
        "support": 0.0,
        "vip": 0.09,
        "trader": 0.1,
    }

# ============= DATABASE =============
users_db = {}
exchange_settings = ExchangeSettings()
trading_fees = TradingFees()

# ============= PERMISSIONS =============
PERMISSIONS = {
    "super_admin": [
        "all_users", "manage_admins", "manage_exchange", "set_fees", "view_logs",
        "manage_markets", "manage_pair", "withdraw", "kyc_approve", "block_user"
    ],
    "admin": [
        "all_users", "manage_users", "view_logs", "manage_markets", "kyc_approve"
    ],
    "moderator": [
        "view_users", "kyc_review", "edit_limits"
    ],
    "partner": [
        "view_dashboard", "refer_users", "manage_team"
    ],
    "white_level": [
        "whitelabel", "custom_brand", "custom_fees"
    ],
    "institutional": [
        "institutional_api", "otc_trading", "bulk_trading"
    ],
    "listing_manager": [
        "list_token", "delist_token", "manage_pair"
    ],
    "trading_manager": [
        "manage_markets", "adjust_fees", "view_analytics"
    ],
    "compliance": [
        "kyc_approve", "view_audit", "generate_report"
    ],
    "support": [
        "view_tickets", "reset_user", "edit_limits"
    ],
    "vip": [
        "vip_dashboard", "reduced_fees", "priority_support"
    ],
    "trader": [
        "trade", "view_markets", "view_history"
    ],
}

def check_permission(role: str, permission: str) -> bool:
    """Check if role has permission"""
    if role == "super_admin":
        return True
    return permission in PERMISSIONS.get(role, [])

# ============= AUTH =============
class Auth:
    @staticmethod
    def get_current_user(token: str = None):
        # In production, verify JWT token
        return {"id": "admin1", "role": UserRole.SUPER_ADMIN}

# ============= ROUTES =============

# Health
@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ============= ADMIN ROUTES =============

# Dashboard Stats
@app.get("/api/admin/stats")
def admin_stats(user: dict = Depends(Auth.get_current_user)):
    if not check_permission(user["role"], "view_dashboard"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "total_users": len(users_db),
        "active_users": sum(1 for u in users_db.values() if u.status == "active"),
        "verified_users": sum(1 for u in users_db.values() if u.verification == "verified"),
        "trading_volume_24h": 1200000000,
        "fees_collected": 4500000,
        "exchange_status": exchange_settings.status.value,
    }

# ============= USER MANAGEMENT =============

@app.get("/api/users")
def list_users(
    page: int = 1, 
    limit: int = 50,
    role: Optional[str] = None,
    status: Optional[str] = None,
    user: dict = Depends(Auth.get_current_user)
):
    if not check_permission(user["role"], "all_users"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    users = list(users_db.values())
    if role:
        users = [u for u in users if u.role == role]
    if status:
        users = [u for u in users if u.status == status]
    
    return {
        "users": users[(page-1)*limit:page*limit],
        "total": len(users),
        "page": page,
    }

@app.post("/api/users")
def create_user(user_data: User, admin: dict = Depends(Auth.get_current_user)):
    if not check_permission(admin["role"], "manage_users"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    users_db[user_data.id] = user_data
    return {"id": user_data.id, "status": "created"}

@app.put("/api/users/{user_id}")
def update_user(user_id: str, user_data: User, admin: dict = Depends(Auth.get_current_user)):
    if not check_permission(admin["role"], "manage_users"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    users_db[user_id] = user_data
    return {"id": user_id, "status": "updated"}

@app.delete("/api/users/{user_id}")
def delete_user(user_id: str, admin: dict = Depends(Auth.get_current_user)):
    if admin["role"] != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can delete users")
    
    if user_id in users_db:
        del users_db[user_id]
    return {"status": "deleted"}

@app.post("/api/users/{user_id}/block")
def block_user(user_id: str, admin: dict = Depends(Auth.get_current_user)):
    if not check_permission(admin["role"], "block_user"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if user_id in users_db:
        users_db[user_id].status = UserStatus.BANNED
    return {"status": "blocked"}

@app.post("/api/users/{user_id}/unblock")
def unblock_user(user_id: str, admin: dict = Depends(Auth.get_current_user)):
    if not check_permission(admin["role"], "block_user"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if user_id in users_db:
        users_db[user_id].status = UserStatus.ACTIVE
    return {"status": "unblocked"}

# ============= ROLES =============

@app.get("/api/roles")
def list_roles(user: dict = Depends(Auth.get_current_user)):
    return {
        "roles": list(UserRole),
        "permissions": PERMISSIONS
    }

@app.put("/api/users/{user_id}/role")
def update_user_role(
    user_id: str, 
    new_role: UserRole,
    admin: dict = Depends(Auth.get_current_user)
):
    if not check_permission(admin["role"], "manage_admins"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if user_id in users_db:
        users_db[user_id].role = new_role
    return {"status": "role_updated"}

# ============= EXCHANGE SETTINGS =============

@app.get("/api/exchange/settings")
def get_exchange_settings(user: dict = Depends(Auth.get_current_user)):
    if admin["role"] not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Access denied")
    return exchange_settings

@app.put("/api/exchange/settings")
def update_exchange_settings(
    settings: ExchangeSettings,
    admin: dict = Depends(Auth.get_current_user)
):
    if not check_permission(admin["role"], "manage_exchange"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    global exchange_settings
    exchange_settings = settings
    return {"status": "updated"}

@app.post("/api/exchange/status")
def update_exchange_status(
    status: ExchangeStatus,
    admin: dict = Depends(Auth.get_current_user)
):
    if not check_permission(admin["role"], "manage_exchange"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    exchange_settings.status = status
    return {"status": status.value}

# ============= TRADING FEES =============

@app.get("/api/fees")
def get_fees(user: dict = Depends(Auth.get_current_user)):
    return trading_fees

@app.put("/api/fees")
def update_fees(
    fees: TradingFees,
    admin: dict = Depends(Auth.get_current_user)
):
    if not check_permission(admin["role"], "set_fees"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    global trading_fees
    trading_fees = fees
    return {"status": "updated"}

# ============= KYC =============

@app.get("/api/kyc/pending")
def get_pending_kyc(admin: dict = Depends(Auth.get_current_user)):
    if not check_permission(admin["role"], "kyc_approve"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "users": [u for u in users_db.values() if u.verification == VerificationStatus.PENDING]
    }

@app.post("/api/kyc/{user_id}/approve")
def approve_kyc(user_id: str, admin: dict = Depends(Auth.get_current_user)):
    if not check_permission(admin["role"], "kyc_approve"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if user_id in users_db:
        users_db[user_id].verification = VerificationStatus.VERIFIED
        users_db[user_id].kyc_level = 2
    return {"status": "approved"}

@app.post("/api/kyc/{user_id}/reject")
def reject_kyc(user_id: str, admin: dict = Depends(Auth.get_current_user)):
    if not check_permission(admin["role"], "kyc_approve"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if user_id in users_db:
        users_db[user_id].verification = VerificationStatus.REJECTED
    return {"status": "rejected"}

# ============= MARKET MANAGEMENT =============

@app.get("/api/markets")
def list_markets(user: dict = Depends(Auth.get_current_user)):
    return {"markets": []}

@app.post("/api/markets")
def create_market(data: dict, admin: dict = Depends(Auth.get_current_user)):
    if not check_permission(admin["role"], "manage_markets"):
        raise HTTPException(status_code=403, detail="Access denied")
    return {"status": "created"}

# ============= LOGS =============

@app.get("/api/logs")
def get_logs(
    limit: int = 100,
    user: dict = Depends(Auth.get_current_user)
):
    if not check_permission(user["role"], "view_logs"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {"logs": []}

# ============= AUDIT =============

@app.get("/api/audit")
def get_audit(
    user_id: Optional[str] = None,
    admin: dict = Depends(Auth.get_current_user)
):
    if not check_permission(admin["role"], "view_audit"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {"audit": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)