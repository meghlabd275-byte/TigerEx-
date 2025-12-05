"""
TigerEx Unified Admin Control System
Complete administrative control for all exchanges with role-based access
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
import json
import logging
import os
import time
import hashlib
import secrets
from dataclasses import dataclass
import jwt

app = FastAPI(
    title="TigerEx Unified Admin Control v1.0.0", 
    version="1.0.0",
    description="Complete administrative control system for TigerEx trading platform"
)
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT Secret for authentication
JWT_SECRET = os.getenv("JWT_SECRET", "tigerex-admin-secret-key")
JWT_ALGORITHM = "HS256"

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    EXCHANGE_ADMIN = "exchange_admin"
    TRADING_ADMIN = "trading_admin"
    USER_MANAGER = "user_manager"
    SUPPORT_ADMIN = "support_admin"
    READ_ONLY = "read_only"

class Exchange(str, Enum):
    BINANCE = "binance"
    BYBIT = "bybit"
    OKX = "okx"
    KUCOIN = "kucoin"
    HTX = "htx"
    HUOBI = "huobi"
    KRAKEN = "kraken"
    COINBASE = "coinbase"
    GEMINI = "gemini"

class Permission(str, Enum):
    # User Management
    MANAGE_USERS = "manage_users"
    VIEW_USERS = "view_users"
    DELETE_USERS = "delete_users"
    
    # Exchange Management
    MANAGE_EXCHANGES = "manage_exchanges"
    VIEW_EXCHANGES = "view_exchanges"
    CONFIGURE_EXCHANGES = "configure_exchanges"
    
    # API Key Management
    MANAGE_API_KEYS = "manage_api_keys"
    VIEW_API_KEYS = "view_api_keys"
    
    # Trading Controls
    MANAGE_TRADING = "manage_trading"
    VIEW_TRADING = "view_trading"
    STOP_TRADING = "stop_trading"
    
    # Financial Controls
    MANAGE_FUNDS = "manage_funds"
    VIEW_BALANCES = "view_balances"
    APPROVE_WITHDRAWALS = "approve_withdrawals"
    
    # System Controls
    MANAGE_SYSTEM = "manage_system"
    VIEW_LOGS = "view_logs"
    SYSTEM_MAINTENANCE = "system_maintenance"
    
    # Compliance & Security
    MANAGE_COMPLIANCE = "manage_compliance"
    VIEW_COMPLIANCE = "view_compliance"
    SECURITY_AUDIT = "security_audit"

class User(BaseModel):
    user_id: str
    username: str
    email: str
    role: UserRole
    permissions: List[Permission]
    exchange_access: List[Exchange]
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    two_factor_enabled: bool = False

class APIKey(BaseModel):
    key_id: str
    exchange: Exchange
    user_id: str
    api_key: str
    api_secret: str
    additional_params: Dict[str, str] = {}
    permissions: List[str]
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True
    last_used: Optional[datetime] = None

class ExchangeConfig(BaseModel):
    exchange: Exchange
    api_base_url: str
    supported_features: List[str]
    rate_limits: Dict[str, Any]
    trading_fees: Dict[str, float]
    withdrawal_fees: Dict[str, float]
    maintenance_mode: bool = False
    custom_params: Dict[str, Any] = {}

class AdminAction(BaseModel):
    action_id: str
    user_id: str
    action_type: str
    target_resource: str
    details: Dict[str, Any]
    timestamp: datetime
    ip_address: str
    user_agent: str

@dataclass
class TigerExAdminConfig:
    ADMIN_DB_PATH: str = os.getenv("ADMIN_DB_PATH", "/tmp/tigerex_admin.db")
    SESSION_TIMEOUT: int = int(os.getenv("SESSION_TIMEOUT", "3600"))  # 1 hour
    MAX_LOGIN_ATTEMPTS: int = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    AUDIT_LOG_RETENTION: int = int(os.getenv("AUDIT_LOG_RETENTION", "90"))  # days

class TigerExAdminService:
    def __init__(self):
        self.config = TigerExAdminConfig()
        self.users_db = {}
        self.api_keys_db = {}
        self.exchange_configs = {}
        self.audit_logs = []
        self.session_tokens = {}
        
        # Initialize default super admin
        self._initialize_default_admin()
        
        # Initialize exchange configurations
        self._initialize_exchange_configs()
    
    def _initialize_default_admin(self):
        """Initialize default super admin user"""
        default_admin = User(
            user_id="admin_001",
            username="tigerex_admin",
            email="admin@tigerex.com",
            role=UserRole.SUPER_ADMIN,
            permissions=list(Permission),
            exchange_access=list(Exchange),
            created_at=datetime.now(),
            is_active=True,
            two_factor_enabled=False
        )
        self.users_db["admin_001"] = default_admin
    
    def _initialize_exchange_configs(self):
        """Initialize exchange configurations"""
        exchanges = {
            Exchange.BINANCE: ExchangeConfig(
                exchange=Exchange.BINANCE,
                api_base_url="https://api.binance.com",
                supported_features=[
                    "spot_trading", "futures_trading", "margin_trading", 
                    "options_trading", "staking", "launchpad", "launchpool",
                    "earn_products", "p2p_trading", "nft_marketplace"
                ],
                rate_limits={"requests_per_minute": 1200, "orders_per_second": 10},
                trading_fees={"spot": 0.001, "futures": 0.0004},
                withdrawal_fees={"BTC": 0.0005, "ETH": 0.005, "USDT": 1.0}
            ),
            Exchange.BYBIT: ExchangeConfig(
                exchange=Exchange.BYBIT,
                api_base_url="https://api.bybit.com",
                supported_features=[
                    "spot_trading", "derivatives_trading", "options_trading",
                    "copy_trading", "bot_trading", "bybit_earn", "launchpad"
                ],
                rate_limits={"requests_per_minute": 600, "orders_per_second": 5},
                trading_fees={"spot": 0.001, "derivatives": 0.0005},
                withdrawal_fees={"BTC": 0.0005, "ETH": 0.005, "USDT": 1.0}
            ),
            Exchange.OKX: ExchangeConfig(
                exchange=Exchange.OKX,
                api_base_url="https://www.okx.com",
                supported_features=[
                    "spot_trading", "futures_trading", "options_trading",
                    "margin_trading", "defi_hub", "earn_products", "web3_wallet"
                ],
                rate_limits={"requests_per_minute": 60, "orders_per_second": 20},
                trading_fees={"spot": 0.001, "futures": 0.0003},
                withdrawal_fees={"BTC": 0.0005, "ETH": 0.004, "USDT": 0.8}
            ),
            Exchange.KUCOIN: ExchangeConfig(
                exchange=Exchange.KUCOIN,
                api_base_url="https://api.kucoin.com",
                supported_features=[
                    "spot_trading", "futures_trading", "margin_trading",
                    "staking", "bot_trading", "copy_trading"
                ],
                rate_limits={"requests_per_minute": 600, "orders_per_second": 5},
                trading_fees={"spot": 0.001, "futures": 0.0002},
                withdrawal_fees={"BTC": 0.0005, "ETH": 0.005, "USDT": 1.0}
            ),
            Exchange.HTX: ExchangeConfig(
                exchange=Exchange.HTX,
                api_base_url="https://api.huobi.pro",
                supported_features=[
                    "spot_trading", "futures_trading", "margin_trading",
                    "copy_trading", "staking_services", "earn_products"
                ],
                rate_limits={"requests_per_minute": 100, "orders_per_second": 10},
                trading_fees={"spot": 0.002, "futures": 0.0004},
                withdrawal_fees={"BTC": 0.0005, "ETH": 0.005, "USDT": 1.0}
            )
        }
        
        for exchange, config in exchanges.items():
            self.exchange_configs[exchange.value] = config
    
    def authenticate_user(self, credentials: HTTPAuthorizationCredentials) -> User:
        """Authenticate user from JWT token"""
        try:
            payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("user_id")
            
            if user_id not in self.users_db:
                raise HTTPException(status_code=401, detail="User not found")
            
            user = self.users_db[user_id]
            
            if not user.is_active:
                raise HTTPException(status_code=401, detail="User is inactive")
            
            # Check if token is expired
            exp = payload.get("exp")
            if exp and time.time() > exp:
                raise HTTPException(status_code=401, detail="Token expired")
            
            return user
        
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def check_permission(self, user: User, required_permission: Permission):
        """Check if user has required permission"""
        if user.role == UserRole.SUPER_ADMIN:
            return True
        
        role_permissions = {
            UserRole.EXCHANGE_ADMIN: [
                Permission.MANAGE_EXCHANGES, Permission.VIEW_EXCHANGES,
                Permission.CONFIGURE_EXCHANGES, Permission.VIEW_TRADING,
                Permission.VIEW_BALANCES, Permission.MANAGE_API_KEYS
            ],
            UserRole.TRADING_ADMIN: [
                Permission.MANAGE_TRADING, Permission.VIEW_TRADING,
                Permission.VIEW_BALANCES, Permission.STOP_TRADING
            ],
            UserRole.USER_MANAGER: [
                Permission.MANAGE_USERS, Permission.VIEW_USERS,
                Permission.VIEW_COMPLIANCE
            ],
            UserRole.SUPPORT_ADMIN: [
                Permission.VIEW_USERS, Permission.VIEW_TRADING,
                Permission.VIEW_BALANCES, Permission.VIEW_COMPLIANCE
            ],
            UserRole.READ_ONLY: [
                Permission.VIEW_USERS, Permission.VIEW_EXCHANGES,
                Permission.VIEW_TRADING, Permission.VIEW_BALANCES,
                Permission.VIEW_COMPLIANCE, Permission.VIEW_LOGS
            ]
        }
        
        if required_permission not in user.permissions:
            raise HTTPException(status_code=403, detail=f"Permission denied: {required_permission}")
    
    def log_admin_action(self, user_id: str, action_type: str, target_resource: str, details: Dict[str, Any], ip_address: str, user_agent: str):
        """Log admin action for audit trail"""
        action = AdminAction(
            action_id=f"action_{int(time.time())}_{secrets.token_hex(4)}",
            user_id=user_id,
            action_type=action_type,
            target_resource=target_resource,
            details=details,
            timestamp=datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.audit_logs.append(action)
    
    def create_jwt_token(self, user: User) -> str:
        """Create JWT token for user"""
        payload = {
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role.value,
            "exp": time.time() + self.config.SESSION_TIMEOUT,
            "iat": time.time()
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# Initialize service
admin_service = TigerExAdminService()

# Request Models
class LoginRequest(BaseModel):
    username: str
    password: str
    two_factor_code: Optional[str] = None

class CreateUserRequest(BaseModel):
    username: str
    email: str
    role: UserRole
    exchange_access: List[Exchange]
    two_factor_enabled: bool = False

class CreateAPIKeyRequest(BaseModel):
    exchange: Exchange
    api_key: str
    api_secret: str
    additional_params: Dict[str, str] = {}
    permissions: List[str] = []
    expires_in_days: Optional[int] = None

class UpdateExchangeConfigRequest(BaseModel):
    maintenance_mode: Optional[bool] = None
    rate_limits: Optional[Dict[str, Any]] = None
    custom_params: Optional[Dict[str, Any]] = None

# API Endpoints
@app.post("/tigerex/admin/login")
async def login(request: LoginRequest):
    """Admin login endpoint"""
    # For demo purposes, accept default admin credentials
    if request.username == "tigerex_admin" and request.password == "tigerex123":
        user = admin_service.users_db["admin_001"]
        token = admin_service.create_jwt_token(user)
        
        admin_service.log_admin_action(
            user.user_id, "LOGIN", "AUTH_SYSTEM",
            {"username": request.username}, "127.0.0.1", "TigerEx Admin System"
        )
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": admin_service.config.SESSION_TIMEOUT,
            "user": {
                "user_id": user.user_id,
                "username": user.username,
                "role": user.role.value,
                "permissions": [p.value for p in user.permissions],
                "exchange_access": [e.value for e in user.exchange_access]
            }
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/tigerex/admin/users")
async def get_users(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all users"""
    user = admin_service.authenticate_user(credentials)
    admin_service.check_permission(user, Permission.VIEW_USERS)
    
    users_data = []
    for u in admin_service.users_db.values():
        users_data.append({
            "user_id": u.user_id,
            "username": u.username,
            "email": u.email,
            "role": u.role.value,
            "permissions": [p.value for p in u.permissions],
            "exchange_access": [e.value for e in u.exchange_access],
            "created_at": u.created_at.isoformat(),
            "last_login": u.last_login.isoformat() if u.last_login else None,
            "is_active": u.is_active,
            "two_factor_enabled": u.two_factor_enabled
        })
    
    return {"users": users_data}

@app.post("/tigerex/admin/users")
async def create_user(
    request: CreateUserRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create new user"""
    user = admin_service.authenticate_user(credentials)
    admin_service.check_permission(user, Permission.MANAGE_USERS)
    
    new_user_id = f"user_{int(time.time())}_{secrets.token_hex(4)}"
    
    role_permissions = {
        UserRole.EXCHANGE_ADMIN: [
            Permission.MANAGE_EXCHANGES, Permission.VIEW_EXCHANGES,
            Permission.CONFIGURE_EXCHANGES, Permission.VIEW_TRADING,
            Permission.VIEW_BALANCES, Permission.MANAGE_API_KEYS
        ],
        UserRole.TRADING_ADMIN: [
            Permission.MANAGE_TRADING, Permission.VIEW_TRADING,
            Permission.VIEW_BALANCES, Permission.STOP_TRADING
        ],
        UserRole.USER_MANAGER: [
            Permission.MANAGE_USERS, Permission.VIEW_USERS,
            Permission.VIEW_COMPLIANCE
        ],
        UserRole.SUPPORT_ADMIN: [
            Permission.VIEW_USERS, Permission.VIEW_TRADING,
            Permission.VIEW_BALANCES, Permission.VIEW_COMPLIANCE
        ],
        UserRole.READ_ONLY: [
            Permission.VIEW_USERS, Permission.VIEW_EXCHANGES,
            Permission.VIEW_TRADING, Permission.VIEW_BALANCES,
            Permission.VIEW_COMPLIANCE, Permission.VIEW_LOGS
        ]
    }
    
    new_user = User(
        user_id=new_user_id,
        username=request.username,
        email=request.email,
        role=request.role,
        permissions=role_permissions.get(request.role, []),
        exchange_access=request.exchange_access,
        created_at=datetime.now(),
        is_active=True,
        two_factor_enabled=request.two_factor_enabled
    )
    
    admin_service.users_db[new_user_id] = new_user
    
    admin_service.log_admin_action(
        user.user_id, "CREATE_USER", f"USER:{new_user_id}",
        {"username": request.username, "role": request.role.value}, 
        "127.0.0.1", "TigerEx Admin System"
    )
    
    return {"message": "User created successfully", "user_id": new_user_id}

@app.get("/tigerex/admin/exchanges")
async def get_exchange_configs(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get exchange configurations"""
    user = admin_service.authenticate_user(credentials)
    admin_service.check_permission(user, Permission.VIEW_EXCHANGES)
    
    configs = {}
    for exchange_id, config in admin_service.exchange_configs.items():
        if exchange_id in [e.value for e in user.exchange_access] or user.role == UserRole.SUPER_ADMIN:
            configs[exchange_id] = {
                "exchange": config.exchange.value,
                "api_base_url": config.api_base_url,
                "supported_features": config.supported_features,
                "rate_limits": config.rate_limits,
                "trading_fees": config.trading_fees,
                "withdrawal_fees": config.withdrawal_fees,
                "maintenance_mode": config.maintenance_mode,
                "custom_params": config.custom_params
            }
    
    return {"exchanges": configs}

@app.put("/tigerex/admin/exchanges/{exchange_id}")
async def update_exchange_config(
    exchange_id: str,
    request: UpdateExchangeConfigRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update exchange configuration"""
    user = admin_service.authenticate_user(credentials)
    admin_service.check_permission(user, Permission.CONFIGURE_EXCHANGES)
    
    if exchange_id not in admin_service.exchange_configs:
        raise HTTPException(status_code=404, detail="Exchange not found")
    
    config = admin_service.exchange_configs[exchange_id]
    
    if request.maintenance_mode is not None:
        config.maintenance_mode = request.maintenance_mode
    if request.rate_limits is not None:
        config.rate_limits = request.rate_limits
    if request.custom_params is not None:
        config.custom_params = request.custom_params
    
    admin_service.log_admin_action(
        user.user_id, "UPDATE_EXCHANGE", f"EXCHANGE:{exchange_id}",
        request.dict(exclude_none=True), "127.0.0.1", "TigerEx Admin System"
    )
    
    return {"message": "Exchange configuration updated successfully"}

@app.get("/tigerex/admin/api-keys")
async def get_api_keys(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get API keys"""
    user = admin_service.authenticate_user(credentials)
    admin_service.check_permission(user, Permission.VIEW_API_KEYS)
    
    keys_data = []
    for key in admin_service.api_keys_db.values():
        if key.user_id == user.user_id or user.role in [UserRole.SUPER_ADMIN, UserRole.EXCHANGE_ADMIN]:
            keys_data.append({
                "key_id": key.key_id,
                "exchange": key.exchange.value,
                "user_id": key.user_id,
                "permissions": key.permissions,
                "created_at": key.created_at.isoformat(),
                "expires_at": key.expires_at.isoformat() if key.expires_at else None,
                "is_active": key.is_active,
                "last_used": key.last_used.isoformat() if key.last_used else None
            })
    
    return {"api_keys": keys_data}

@app.post("/tigerex/admin/api-keys")
async def create_api_key(
    request: CreateAPIKeyRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create new API key"""
    user = admin_service.authenticate_user(credentials)
    admin_service.check_permission(user, Permission.MANAGE_API_KEYS)
    
    key_id = f"key_{int(time.time())}_{secrets.token_hex(6)}"
    expires_at = datetime.now() + timedelta(days=request.expires_in_days) if request.expires_in_days else None
    
    new_key = APIKey(
        key_id=key_id,
        exchange=request.exchange,
        user_id=user.user_id,
        api_key=request.api_key,
        api_secret=request.api_secret,
        additional_params=request.additional_params,
        permissions=request.permissions,
        created_at=datetime.now(),
        expires_at=expires_at,
        is_active=True
    )
    
    admin_service.api_keys_db[key_id] = new_key
    
    admin_service.log_admin_action(
        user.user_id, "CREATE_API_KEY", f"EXCHANGE:{request.exchange.value}",
        {"key_id": key_id, "permissions": request.permissions},
        "127.0.0.1", "TigerEx Admin System"
    )
    
    return {"message": "API key created successfully", "key_id": key_id}

@app.get("/tigerex/admin/audit-log")
async def get_audit_log(
    limit: int = Query(100, description="Limit number of records"),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get audit log"""
    user = admin_service.authenticate_user(credentials)
    admin_service.check_permission(user, Permission.VIEW_LOGS)
    
    # Return recent audit logs
    recent_logs = admin_service.audit_logs[-limit:]
    
    logs_data = []
    for log in recent_logs:
        logs_data.append({
            "action_id": log.action_id,
            "user_id": log.user_id,
            "action_type": log.action_type,
            "target_resource": log.target_resource,
            "details": log.details,
            "timestamp": log.timestamp.isoformat(),
            "ip_address": log.ip_address,
            "user_agent": log.user_agent
        })
    
    return {"audit_logs": logs_data}

@app.get("/tigerex/admin/dashboard")
async def get_admin_dashboard(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get admin dashboard data"""
    user = admin_service.authenticate_user(credentials)
    admin_service.check_permission(user, Permission.VIEW_EXCHANGES)
    
    dashboard_data = {
        "user_count": len(admin_service.users_db),
        "active_users": len([u for u in admin_service.users_db.values() if u.is_active]),
        "api_key_count": len(admin_service.api_keys_db),
        "exchange_count": len(admin_service.exchange_configs),
        "exchanges_status": {
            exchange_id: not config.maintenance_mode
            for exchange_id, config in admin_service.exchange_configs.items()
        },
        "recent_actions": len(admin_service.audit_logs[-10:]),
        "system_health": "healthy"
    }
    
    return dashboard_data

@app.get("/tigerex/admin/features")
async def get_admin_features():
    """Get available admin features"""
    return {
        "service": "TigerEx Unified Admin Control",
        "version": "1.0.0",
        "roles": [role.value for role in UserRole],
        "permissions": [perm.value for perm in Permission],
        "exchanges": [exchange.value for exchange in Exchange],
        "capabilities": [
            "User Management",
            "Exchange Configuration",
            "API Key Management",
            "Role-Based Access Control",
            "Audit Logging",
            "Real-time Monitoring",
            "Security Controls"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "TigerEx Unified Admin Control",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)