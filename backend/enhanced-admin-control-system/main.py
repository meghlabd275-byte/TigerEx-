"""
TigerEx Enhanced Admin Control System v11.0.0
Complete admin dashboard with full system control, monitoring, and management
Includes user management, system monitoring, trading controls, and comprehensive analytics
"""

from fastapi import FastAPI, HTTPException, Depends, Security, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import logging
from decimal import Decimal
import jwt
import uvicorn
import time
import hashlib
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TigerEx Enhanced Admin Control System v11.0.0",
    description="Complete admin control system with comprehensive monitoring and management",
    version="11.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
JWT_SECRET = "tigerex-admin-super-secure-key-2024"
JWT_ALGORITHM = "HS256"

# ==================== ENUMS AND MODELS ====================

class AdminRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    SYSTEM_ADMIN = "system_admin"
    TRADING_ADMIN = "trading_admin"
    SUPPORT_ADMIN = "support_admin"
    COMPLIANCE_ADMIN = "compliance_admin"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
    BANNED = "banned"

class SystemStatus(str, Enum):
    ONLINE = "online"
    MAINTENANCE = "maintenance"
    CRITICAL = "critical"
    DEGRADED = "degraded"

class TradingStatus(str, Enum):
    TRADING_ENABLED = "trading_enabled"
    TRADING_DISABLED = "trading_disabled"
    EMERGENCY_STOP = "emergency_stop"

class User(BaseModel):
    user_id: str
    username: str
    email: str
    role: str
    status: UserStatus
    balance: Decimal
    created_at: datetime
    last_login: Optional[datetime]
    kyc_status: str
    trading_volume: Decimal
    country: str

class SystemAlert(BaseModel):
    alert_id: str
    type: str
    severity: str
    message: str
    timestamp: datetime
    resolved: bool = False

class TradingControl(BaseModel):
    exchange: str
    symbol: str
    action: str  # enable/disable
    reason: str
    admin_id: str

class AdminAction(BaseModel):
    action_id: str
    admin_id: str
    action_type: str
    target_user: Optional[str]
    details: Dict[str, Any]
    timestamp: datetime
    ip_address: str

# ==================== ADMIN SYSTEM CORE ====================

class EnhancedAdminSystem:
    """Enhanced admin system with comprehensive control capabilities"""
    
    def __init__(self):
        self.admin_users = {
            "superadmin": {
                "password": self._hash_password("TigerEx2024!"),
                "role": AdminRole.SUPER_ADMIN,
                "permissions": ["full_access"],
                "last_login": None,
                "active_sessions": []
            },
            "trading_admin": {
                "password": self._hash_password("TradingAdmin2024!"),
                "role": AdminRole.TRADING_ADMIN,
                "permissions": ["trading_control", "user_management"],
                "last_login": None,
                "active_sessions": []
            },
            "support_admin": {
                "password": self._hash_password("SupportAdmin2024!"),
                "role": AdminRole.SUPPORT_ADMIN,
                "permissions": ["support_tickets", "user_inquiries"],
                "last_login": None,
                "active_sessions": []
            }
        }
        
        self.system_metrics = {
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "disk_usage": 38.1,
            "network_latency": 12.5,
            "api_response_time": 85.3,
            "database_connections": 125,
            "active_sessions": 3420,
            "concurrent_traders": 1250
        }
        
        self.system_status = SystemStatus.ONLINE
        self.trading_status = TradingStatus.TRADING_ENABLED
        self.active_alerts = []
        self.admin_actions = []
        self.system_settings = {
            "maintenance_mode": False,
            "new_registrations": True,
            "api_rate_limit": 1000,
            "max_withdrawal_per_hour": 10000,
            "max_leverage": 100,
            "emergency_contacts": ["admin@tigerex.com", "security@tigerex.com"]
        }
        
    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_admin(self, username: str, password: str) -> bool:
        if username in self.admin_users:
            stored_hash = self.admin_users[username]["password"]
            input_hash = self._hash_password(password)
            return stored_hash == input_hash
        return False
    
    def log_admin_action(self, admin_id: str, action_type: str, target_user: str = None, details: Dict[str, Any] = None, ip_address: str = "0.0.0.0"):
        action = AdminAction(
            action_id=f"action_{int(time.time())}",
            admin_id=admin_id,
            action_type=action_type,
            target_user=target_user,
            details=details or {},
            timestamp=datetime.now(),
            ip_address=ip_address
        )
        self.admin_actions.append(action)
        logger.info(f"Admin action logged: {action_type} by {admin_id}")
    
    def update_system_metrics(self):
        """Simulate real-time system metrics updates"""
        import random
        self.system_metrics.update({
            "cpu_usage": max(0, min(100, self.system_metrics["cpu_usage"] + random.uniform(-5, 5))),
            "memory_usage": max(0, min(100, self.system_metrics["memory_usage"] + random.uniform(-3, 3))),
            "network_latency": max(1, self.system_metrics["network_latency"] + random.uniform(-2, 2)),
            "api_response_time": max(10, min(500, self.system_metrics["api_response_time"] + random.uniform(-10, 10))),
            "active_sessions": max(100, self.system_metrics["active_sessions"] + random.randint(-50, 50)),
            "concurrent_traders": max(50, self.system_metrics["concurrent_traders"] + random.randint(-20, 20))
        })

class UserManager:
    """User management system"""
    
    def __init__(self):
        self.users = self._generate_sample_users()
        self.suspended_users = []
        self.pending_verifications = []
    
    def _generate_sample_users(self) -> List[User]:
        users = []
        countries = ["US", "UK", "Japan", "Germany", "Canada", "Australia", "Singapore", "India"]
        
        for i in range(100):
            user = User(
                user_id=f"user_{i+1:04d}",
                username=f"trader_{i+1}",
                email=f"trader{i+1}@email.com",
                role="user",
                status=UserStatus.ACTIVE if i < 90 else (UserStatus.INACTIVE if i < 95 else UserStatus.PENDING_VERIFICATION),
                balance=Decimal(f"{i * 125.50:.2f}"),
                created_at=datetime.now() - timedelta(days=i),
                last_login=datetime.now() - timedelta(hours=i % 24),
                kyc_status="verified" if i < 80 else "pending",
                trading_volume=Decimal(f"{i * 2500.75:.2f}"),
                country=countries[i % len(countries)]
            )
            users.append(user)
        
        return users
    
    def get_user_stats(self) -> Dict[str, Any]:
        total_users = len(self.users)
        active_users = len([u for u in self.users if u.status == UserStatus.ACTIVE])
        verified_users = len([u for u in self.users if u.kyc_status == "verified"])
        total_balance = sum(u.balance for u in self.users)
        total_volume = sum(u.trading_volume for u in self.users)
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "verified_users": verified_users,
            "total_balance": float(total_balance),
            "total_trading_volume": float(total_volume),
            "new_users_today": 5,
            "new_users_this_week": 23,
            "user_retention_rate": 78.5
        }
    
    def suspend_user(self, user_id: str, reason: str, admin_id: str) -> bool:
        for user in self.users:
            if user.user_id == user_id:
                user.status = UserStatus.SUSPENDED
                self.suspended_users.append(user_id)
                return True
        return False
    
    def unsuspend_user(self, user_id: str, admin_id: str) -> bool:
        for user in self.users:
            if user.user_id == user_id:
                user.status = UserStatus.ACTIVE
                if user_id in self.suspended_users:
                    self.suspended_users.remove(user_id)
                return True
        return False

class TradingControlManager:
    """Trading control system"""
    
    def __init__(self):
        self.exchange_controls = {
            "binance": {"enabled": True, "reason": ""},
            "kraken": {"enabled": True, "reason": ""},
            "bybit": {"enabled": True, "reason": ""},
            "okx": {"enabled": True, "reason": ""},
            "coinbase": {"enabled": True, "reason": ""},
            "kucoin": {"enabled": True, "reason": ""},
            "gemini": {"enabled": True, "reason": ""}
        }
        
        self.symbol_controls = {}
        self.trading_stats = {
            "total_trades_24h": 15234,
            "volume_24h": 84567890.50,
            "active_traders": 1250,
            "pending_orders": 3456,
            "margin_positions": 567
        }
    
    def control_exchange(self, exchange: str, enabled: bool, reason: str) -> bool:
        if exchange in self.exchange_controls:
            self.exchange_controls[exchange]["enabled"] = enabled
            self.exchange_controls[exchange]["reason"] = reason
            return True
        return False
    
    def control_symbol(self, exchange: str, symbol: str, enabled: bool, reason: str) -> bool:
        key = f"{exchange}:{symbol}"
        self.symbol_controls[key] = {"enabled": enabled, "reason": reason}
        return True

# Global instances
admin_system = EnhancedAdminSystem()
user_manager = UserManager()
trading_control = TradingControlManager()

# ==================== API ENDPOINTS ====================

def create_jwt_token(username: str, role: str) -> str:
    payload = {
        "sub": username,
        "role": role,
        "exp": datetime.now() + timedelta(hours=24),
        "iat": datetime.now()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_admin_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        
        if username not in admin_system.admin_users:
            raise HTTPException(status_code=401, detail="Invalid admin credentials")
        
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/admin/login")
async def admin_login(username: str, password: str):
    """Admin login endpoint"""
    if admin_system.verify_admin(username, password):
        admin_data = admin_system.admin_users[username]
        token = create_jwt_token(username, admin_data["role"].value)
        
        admin_system.log_admin_action(
            admin_id=username,
            action_type="login",
            ip_address="0.0.0.0"
        )
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": admin_data["role"].value,
            "permissions": admin_data["permissions"]
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/admin/dashboard")
async def get_admin_dashboard(payload: Dict[str, Any] = Depends(verify_admin_token)):
    """Get comprehensive admin dashboard"""
    admin_system.update_system_metrics()
    
    return {
        "system_status": admin_system.system_status.value,
        "trading_status": admin_system.trading_status.value,
        "system_metrics": admin_system.system_metrics,
        "system_settings": admin_system.system_settings,
        "user_stats": user_manager.get_user_stats(),
        "trading_stats": trading_control.trading_stats,
        "active_alerts": len(admin_system.active_alerts),
        "last_update": datetime.now()
    }

@app.get("/admin/users")
async def get_users(
    page: int = 1,
    limit: int = 50,
    status: Optional[UserStatus] = None,
    payload: Dict[str, Any] = Depends(verify_admin_token)
):
    """Get users with pagination and filtering"""
    users = user_manager.users
    
    if status:
        users = [u for u in users if u.status == status]
    
    start = (page - 1) * limit
    end = start + limit
    
    return {
        "users": [u.__dict__ for u in users[start:end]],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": len(users),
            "pages": (len(users) + limit - 1) // limit
        }
    }

@app.post("/admin/users/{user_id}/suspend")
async def suspend_user(
    user_id: str,
    reason: str,
    payload: Dict[str, Any] = Depends(verify_admin_token)
):
    """Suspend a user"""
    success = user_manager.suspend_user(user_id, reason, payload["sub"])
    
    if success:
        admin_system.log_admin_action(
            admin_id=payload["sub"],
            action_type="suspend_user",
            target_user=user_id,
            details={"reason": reason}
        )
        return {"message": "User suspended successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.post("/admin/users/{user_id}/unsuspend")
async def unsuspend_user(
    user_id: str,
    payload: Dict[str, Any] = Depends(verify_admin_token)
):
    """Unsuspend a user"""
    success = user_manager.unsuspend_user(user_id, payload["sub"])
    
    if success:
        admin_system.log_admin_action(
            admin_id=payload["sub"],
            action_type="unsuspend_user",
            target_user=user_id
        )
        return {"message": "User unsuspended successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.get("/admin/trading/controls")
async def get_trading_controls(payload: Dict[str, Any] = Depends(verify_admin_token)):
    """Get trading controls"""
    return {
        "exchange_controls": trading_control.exchange_controls,
        "symbol_controls": trading_control.symbol_controls,
        "trading_status": admin_system.trading_status.value
    }

@app.post("/admin/trading/controls/exchange")
async def control_exchange_trading(
    control: TradingControl,
    payload: Dict[str, Any] = Depends(verify_admin_token)
):
    """Control trading for an exchange"""
    success = trading_control.control_exchange(
        control.exchange,
        control.action == "enable",
        control.reason
    )
    
    if success:
        admin_system.log_admin_action(
            admin_id=payload["sub"],
            action_type="control_exchange_trading",
            details={
                "exchange": control.exchange,
                "action": control.action,
                "reason": control.reason
            }
        )
        return {"message": f"Trading {control.action}d for {control.exchange}"}
    else:
        raise HTTPException(status_code=400, detail="Invalid exchange")

@app.get("/admin/system/metrics")
async def get_system_metrics(payload: Dict[str, Any] = Depends(verify_admin_token)):
    """Get detailed system metrics"""
    admin_system.update_system_metrics()
    
    return {
        "metrics": admin_system.system_metrics,
        "status": admin_system.system_status.value,
        "timestamp": datetime.now()
    }

@app.post("/admin/system/maintenance")
async def toggle_maintenance_mode(
    enabled: bool,
    reason: str,
    payload: Dict[str, Any] = Depends(verify_admin_token)
):
    """Toggle maintenance mode"""
    admin_system.system_settings["maintenance_mode"] = enabled
    
    admin_system.log_admin_action(
        admin_id=payload["sub"],
        action_type="toggle_maintenance",
        details={"enabled": enabled, "reason": reason}
    )
    
    return {"message": f"Maintenance mode {'enabled' if enabled else 'disabled'}"}

@app.get("/admin/audit/log")
async def get_audit_log(
    page: int = 1,
    limit: int = 50,
    payload: Dict[str, Any] = Depends(verify_admin_token)
):
    """Get admin action audit log"""
    actions = admin_system.admin_actions
    
    # Sort by timestamp descending
    actions.sort(key=lambda x: x.timestamp, reverse=True)
    
    start = (page - 1) * limit
    end = start + limit
    
    return {
        "actions": [action.__dict__ for action in actions[start:end]],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": len(actions),
            "pages": (len(actions) + limit - 1) // limit
        }
    }

@app.get("/admin/alerts")
async def get_system_alerts(payload: Dict[str, Any] = Depends(verify_admin_token)):
    """Get system alerts"""
    return {
        "active_alerts": admin_system.active_alerts,
        "total_alerts": len(admin_system.active_alerts)
    }

@app.post("/admin/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    payload: Dict[str, Any] = Depends(verify_admin_token)
):
    """Resolve a system alert"""
    for alert in admin_system.active_alerts:
        if alert.alert_id == alert_id:
            alert.resolved = True
            admin_system.log_admin_action(
                admin_id=payload["sub"],
                action_type="resolve_alert",
                details={"alert_id": alert_id}
            )
            return {"message": "Alert resolved"}
    
    raise HTTPException(status_code=404, detail="Alert not found")

@app.get("/")
async def root():
    return {
        "service": "TigerEx Enhanced Admin Control System v11.0.0",
        "status": "operational",
        "features": [
            "User Management",
            "Trading Controls",
            "System Monitoring",
            "Audit Logging",
            "Alert Management",
            "Maintenance Controls"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)