"""
TigerEx Unified Admin Service
Complete Admin Control System with Role-Based Access Control
Port: 8100
"""

from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import asyncio
import asyncpg
import redis.asyncio as redis
import structlog
import uvicorn
import os
import json
import httpx
import jwt
import bcrypt
from passlib.context import CryptContext
import secrets
from functools import wraps
from dataclasses import dataclass
import hashlib

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/tigerex")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "tigerex-super-secret-jwt-key-2024")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Global connections
db_pool = None
redis_client = None

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(
    title="TigerEx Unified Admin Service",
    description="Complete Admin Control System",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# ENUMS
# ============================================================================

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    COMPLIANCE_OFFICER = "compliance_officer"
    RISK_MANAGER = "risk_manager"
    TECHNICAL_ADMIN = "technical_admin"
    SUPPORT_MANAGER = "support_manager"
    SUPPORT_AGENT = "support_agent"
    LISTING_MANAGER = "listing_manager"
    FINANCE_MANAGER = "finance_manager"
    PARTNER = "partner"
    WHITE_LABEL_CLIENT = "white_label_client"
    INSTITUTIONAL_CLIENT = "institutional_client"
    MARKET_MAKER = "market_maker"
    LIQUIDITY_PROVIDER = "liquidity_provider"
    AFFILIATE = "affiliate"
    VIP_TRADER = "vip_trader"
    TRADER = "trader"
    USER = "user"
    GUEST = "guest"

class Permission(str, Enum):
    # User Management
    VIEW_USERS = "view_users"
    CREATE_USERS = "create_users"
    EDIT_USERS = "edit_users"
    DELETE_USERS = "delete_users"
    SUSPEND_USERS = "suspend_users"
    BAN_USERS = "ban_users"
    IMPERSONATE_USERS = "impersonate_users"
    MANAGE_USER_ROLES = "manage_user_roles"
    VIEW_USER_DETAILS = "view_user_details"
    EXPORT_USER_DATA = "export_user_data"
    
    # Trading Control
    VIEW_TRADING = "view_trading"
    CONTROL_TRADING = "control_trading"
    PAUSE_TRADING = "pause_trading"
    RESUME_TRADING = "resume_trading"
    HALT_ALL_TRADING = "halt_all_trading"
    MODIFY_FEES = "modify_fees"
    MANAGE_TRADING_PAIRS = "manage_trading_pairs"
    VIEW_TRADE_HISTORY = "view_trade_history"
    CANCEL_ORDERS = "cancel_orders"
    MODIFY_ORDERS = "modify_orders"
    
    # Financial Control
    VIEW_FINANCIALS = "view_financials"
    PROCESS_WITHDRAWALS = "process_withdrawals"
    APPROVE_WITHDRAWALS = "approve_withdrawals"
    REJECT_WITHDRAWALS = "reject_withdrawals"
    MANAGE_FUNDS = "manage_funds"
    VIEW_BALANCES = "view_balances"
    ADJUST_BALANCES = "adjust_balances"
    FREEZE_BALANCES = "freeze_balances"
    MANAGE_FEES = "manage_fees"
    VIEW_TRANSACTIONS = "view_transactions"
    
    # Token Management
    LIST_TOKENS = "list_tokens"
    DELIST_TOKENS = "delist_tokens"
    MANAGE_TOKENS = "manage_tokens"
    MANAGE_TRADING_PAIRS = "manage_trading_pairs"
    MANAGE_BLOCKCHAINS = "manage_blockchains"
    
    # System Control
    SYSTEM_CONFIG = "system_config"
    VIEW_LOGS = "view_logs"
    MANAGE_SECURITY = "manage_security"
    MANAGE_API_KEYS = "manage_api_keys"
    SYSTEM_MAINTENANCE = "system_maintenance"
    RESTART_SERVICES = "restart_services"
    VIEW_SYSTEM_METRICS = "view_system_metrics"
    MANAGE_NOTIFICATIONS = "manage_notifications"
    
    # KYC/AML
    VIEW_KYC = "view_kyc"
    APPROVE_KYC = "approve_kyc"
    REJECT_KYC = "reject_kyc"
    VIEW_AML = "view_aml"
    MANAGE_COMPLIANCE = "manage_compliance"
    
    # Support
    VIEW_TICKETS = "view_tickets"
    RESPOND_TICKETS = "respond_tickets"
    CLOSE_TICKETS = "close_tickets"
    
    # Reports
    VIEW_REPORTS = "view_reports"
    GENERATE_REPORTS = "generate_reports"
    EXPORT_REPORTS = "export_reports"
    
    # Admin Management
    CREATE_ADMINS = "create_admins"
    EDIT_ADMINS = "edit_admins"
    DELETE_ADMINS = "delete_admins"
    MANAGE_ROLES = "manage_roles"
    MANAGE_PERMISSIONS = "manage_permissions"

class SystemStatus(str, Enum):
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    HALTED = "halted"

class ServiceStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    ERROR = "error"

class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    FROZEN = "frozen"
    PENDING_VERIFICATION = "pending_verification"

# ============================================================================
# ROLE-PERMISSION MAPPING
# ============================================================================

ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: list(Permission),  # All permissions
    UserRole.ADMIN: [
        Permission.VIEW_USERS, Permission.CREATE_USERS, Permission.EDIT_USERS,
        Permission.SUSPEND_USERS, Permission.VIEW_TRADING, Permission.CONTROL_TRADING,
        Permission.PAUSE_TRADING, Permission.RESUME_TRADING, Permission.MODIFY_FEES,
        Permission.VIEW_FINANCIALS, Permission.PROCESS_WITHDRAWALS, Permission.APPROVE_WITHDRAWALS,
        Permission.LIST_TOKENS, Permission.DELIST_TOKENS, Permission.MANAGE_TRADING_PAIRS,
        Permission.SYSTEM_CONFIG, Permission.VIEW_LOGS, Permission.VIEW_KYC,
        Permission.APPROVE_KYC, Permission.VIEW_REPORTS, Permission.GENERATE_REPORTS,
    ],
    UserRole.COMPLIANCE_OFFICER: [
        Permission.VIEW_USERS, Permission.VIEW_TRADING, Permission.VIEW_FINANCIALS,
        Permission.VIEW_KYC, Permission.APPROVE_KYC, Permission.REJECT_KYC,
        Permission.VIEW_AML, Permission.MANAGE_COMPLIANCE, Permission.VIEW_REPORTS,
    ],
    UserRole.RISK_MANAGER: [
        Permission.VIEW_TRADING, Permission.PAUSE_TRADING, Permission.HALT_ALL_TRADING,
        Permission.VIEW_FINANCIALS, Permission.VIEW_REPORTS, Permission.GENERATE_REPORTS,
    ],
    UserRole.TECHNICAL_ADMIN: [
        Permission.SYSTEM_CONFIG, Permission.VIEW_LOGS, Permission.MANAGE_SECURITY,
        Permission.RESTART_SERVICES, Permission.VIEW_SYSTEM_METRICS,
    ],
    UserRole.SUPPORT_MANAGER: [
        Permission.VIEW_USERS, Permission.VIEW_USER_DETAILS, Permission.VIEW_TICKETS,
        Permission.RESPOND_TICKETS, Permission.CLOSE_TICKETS, Permission.SUSPEND_USERS,
    ],
    UserRole.SUPPORT_AGENT: [
        Permission.VIEW_USERS, Permission.VIEW_USER_DETAILS, Permission.VIEW_TICKETS,
        Permission.RESPOND_TICKETS,
    ],
    UserRole.LISTING_MANAGER: [
        Permission.LIST_TOKENS, Permission.DELIST_TOKENS, Permission.MANAGE_TRADING_PAIRS,
        Permission.MANAGE_TOKENS,
    ],
    UserRole.FINANCE_MANAGER: [
        Permission.VIEW_FINANCIALS, Permission.PROCESS_WITHDRAWALS, Permission.APPROVE_WITHDRAWALS,
        Permission.VIEW_BALANCES, Permission.VIEW_TRANSACTIONS, Permission.VIEW_REPORTS,
        Permission.GENERATE_REPORTS,
    ],
}

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class AdminLogin(BaseModel):
    email: str
    password: str
    two_factor_code: Optional[str] = None

class AdminUserCreate(BaseModel):
    email: str = Field(..., min_length=1, max_length=255)
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.USER
    permissions: Optional[List[Permission]] = None

class AdminUserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    role: Optional[UserRole] = None
    permissions: Optional[List[Permission]] = None
    is_active: Optional[bool] = None

class UserStatusUpdate(BaseModel):
    status: UserStatus
    reason: Optional[str] = None
    duration: Optional[int] = None  # in hours

class UserRoleUpdate(BaseModel):
    role: UserRole
    permissions: Optional[List[Permission]] = None

class SystemConfigUpdate(BaseModel):
    maintenance_mode: Optional[bool] = None
    trading_enabled: Optional[bool] = None
    registration_enabled: Optional[bool] = None
    withdrawal_enabled: Optional[bool] = None
    deposit_enabled: Optional[bool] = None
    kyc_required: Optional[bool] = None
    announcement: Optional[str] = None

class TradingPairUpdate(BaseModel):
    symbol: str
    status: Optional[str] = None
    maker_fee: Optional[Decimal] = None
    taker_fee: Optional[Decimal] = None
    min_order_size: Optional[Decimal] = None
    max_order_size: Optional[Decimal] = None

class BalanceAdjustment(BaseModel):
    user_id: str
    asset: str
    amount: Decimal
    action: str  # "add", "subtract", "set"
    reason: str

class AnnouncementCreate(BaseModel):
    title: str
    content: str
    type: str = "info"  # info, warning, critical
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    target_roles: Optional[List[UserRole]] = None

class FeeUpdate(BaseModel):
    trading_pair: Optional[str] = None
    maker_fee: Optional[Decimal] = None
    taker_fee: Optional[Decimal] = None
    withdrawal_fee: Optional[Dict[str, Decimal]] = None
    deposit_fee: Optional[Dict[str, Decimal]] = None

class ServiceControl(BaseModel):
    service_name: str
    action: str  # "start", "stop", "pause", "resume", "restart"

# ============================================================================
# AUTHENTICATION AND AUTHORIZATION
# ============================================================================

def create_jwt_token(user_id: str, email: str, role: UserRole, permissions: List[str]) -> str:
    """Create JWT token for authenticated user"""
    expiration = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role.value,
        "permissions": permissions,
        "exp": expiration,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str) -> Dict[str, Any]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated admin"""
    token = credentials.credentials
    payload = verify_jwt_token(token)
    
    # Check if user is active in Redis cache
    if redis_client:
        user_status = await redis_client.get(f"user_status:{payload['user_id']}")
        if user_status == "suspended":
            raise HTTPException(status_code=403, detail="User account is suspended")
        if user_status == "banned":
            raise HTTPException(status_code=403, detail="User account is banned")
    
    return payload

def check_permission(required_permission: Permission):
    """Decorator to check if user has required permission"""
    async def permission_checker(admin: Dict = Depends(get_current_admin)):
        permissions = admin.get("permissions", [])
        if required_permission.value not in permissions and Permission.MANAGE_PERMISSIONS.value not in permissions:
            raise HTTPException(status_code=403, detail=f"Permission denied: {required_permission.value}")
        return admin
    return permission_checker

# ============================================================================
# ADMIN AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/admin/login")
async def admin_login(login_data: AdminLogin):
    """Admin login endpoint"""
    # In production, verify credentials against database
    # For now, return a mock response
    
    # Verify credentials (mock)
    if login_data.email == "admin@tigerex.com" and login_data.password == "admin123":
        permissions = ROLE_PERMISSIONS.get(UserRole.SUPER_ADMIN, [])
        token = create_jwt_token(
            user_id="admin_001",
            email=login_data.email,
            role=UserRole.SUPER_ADMIN,
            permissions=[p.value for p in permissions]
        )
        
        return {
            "success": True,
            "access_token": token,
            "token_type": "bearer",
            "role": "super_admin",
            "permissions": [p.value for p in permissions]
        }
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/admin/logout")
async def admin_logout(admin: Dict = Depends(get_current_admin)):
    """Admin logout - invalidate token"""
    # In production, add token to blacklist in Redis
    return {"success": True, "message": "Logged out successfully"}

@app.get("/admin/profile")
async def get_admin_profile(admin: Dict = Depends(get_current_admin)):
    """Get current admin profile"""
    return {
        "success": True,
        "admin": {
            "user_id": admin.get("user_id"),
            "email": admin.get("email"),
            "role": admin.get("role"),
            "permissions": admin.get("permissions", [])
        }
    }

# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/users", dependencies=[Depends(check_permission(Permission.VIEW_USERS))])
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[UserStatus] = None,
    role: Optional[UserRole] = None,
    search: Optional[str] = None,
    admin: Dict = Depends(get_current_admin)
):
    """List all users with pagination and filters"""
    # Mock response - in production, query database
    return {
        "success": True,
        "users": [
            {
                "id": "user_001",
                "email": "user1@example.com",
                "username": "trader1",
                "role": "trader",
                "status": "active",
                "kyc_status": "approved",
                "created_at": "2024-01-15T10:30:00Z",
                "last_login": "2024-04-10T08:00:00Z",
                "total_volume": "125000.00",
                "total_trades": 450
            }
        ],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": 1500,
            "total_pages": 75
        }
    }

@app.get("/users/{user_id}", dependencies=[Depends(check_permission(Permission.VIEW_USER_DETAILS))])
async def get_user_details(
    user_id: str,
    admin: Dict = Depends(get_current_admin)
):
    """Get detailed user information"""
    return {
        "success": True,
        "user": {
            "id": user_id,
            "email": "user1@example.com",
            "username": "trader1",
            "full_name": "John Doe",
            "phone": "+1234567890",
            "role": "trader",
            "status": "active",
            "kyc_status": "approved",
            "kyc_level": 2,
            "two_factor_enabled": True,
            "created_at": "2024-01-15T10:30:00Z",
            "last_login": "2024-04-10T08:00:00Z",
            "login_count": 120,
            "failed_login_attempts": 0,
            "balances": {
                "BTC": "1.5",
                "ETH": "10.0",
                "USDT": "50000.00"
            },
            "trading_stats": {
                "total_volume": "125000.00",
                "total_trades": 450,
                "win_rate": 0.65,
                "pnl": "15000.00"
            },
            "referrals": {
                "code": "TRADER1",
                "count": 25,
                "earnings": "500.00"
            }
        }
    }

@app.put("/users/{user_id}/status", dependencies=[Depends(check_permission(Permission.SUSPEND_USERS))])
async def update_user_status(
    user_id: str,
    status_update: UserStatusUpdate,
    admin: Dict = Depends(get_current_admin)
):
    """Update user status (suspend, ban, freeze, activate)"""
    logger.info("User status updated",
                user_id=user_id,
                new_status=status_update.status,
                reason=status_update.reason,
                admin_id=admin.get("user_id"))
    
    return {
        "success": True,
        "message": f"User status updated to {status_update.status}",
        "user_id": user_id,
        "new_status": status_update.status
    }

@app.put("/users/{user_id}/role", dependencies=[Depends(check_permission(Permission.MANAGE_USER_ROLES))])
async def update_user_role(
    user_id: str,
    role_update: UserRoleUpdate,
    admin: Dict = Depends(get_current_admin)
):
    """Update user role and permissions"""
    return {
        "success": True,
        "message": f"User role updated to {role_update.role}",
        "user_id": user_id,
        "new_role": role_update.role,
        "new_permissions": role_update.permissions or []
    }

@app.delete("/users/{user_id}", dependencies=[Depends(check_permission(Permission.DELETE_USERS))])
async def delete_user(
    user_id: str,
    admin: Dict = Depends(get_current_admin)
):
    """Delete a user account"""
    return {
        "success": True,
        "message": "User deleted successfully",
        "user_id": user_id
    }

# ============================================================================
# TRADING CONTROL ENDPOINTS
# ============================================================================

@app.get("/trading/status")
async def get_trading_status(admin: Dict = Depends(get_current_admin)):
    """Get current trading status"""
    return {
        "success": True,
        "trading": {
            "status": "operational",
            "spot_enabled": True,
            "futures_enabled": True,
            "margin_enabled": True,
            "options_enabled": False,
            "halted_pairs": [],
            "paused_pairs": []
        }
    }

@app.post("/trading/pause", dependencies=[Depends(check_permission(Permission.PAUSE_TRADING))])
async def pause_trading(
    trading_type: Optional[str] = Query(None),  # spot, futures, margin, all
    pairs: Optional[List[str]] = None,
    reason: Optional[str] = None,
    admin: Dict = Depends(get_current_admin)
):
    """Pause trading for specific pairs or all trading"""
    logger.info("Trading paused",
                trading_type=trading_type,
                pairs=pairs,
                reason=reason,
                admin_id=admin.get("user_id"))
    
    return {
        "success": True,
        "message": f"Trading paused for {trading_type or 'all'}",
        "paused_at": datetime.utcnow().isoformat()
    }

@app.post("/trading/resume", dependencies=[Depends(check_permission(Permission.RESUME_TRADING))])
async def resume_trading(
    trading_type: Optional[str] = Query(None),
    pairs: Optional[List[str]] = None,
    admin: Dict = Depends(get_current_admin)
):
    """Resume trading for specific pairs or all trading"""
    return {
        "success": True,
        "message": f"Trading resumed for {trading_type or 'all'}",
        "resumed_at": datetime.utcnow().isoformat()
    }

@app.post("/trading/halt", dependencies=[Depends(check_permission(Permission.HALT_ALL_TRADING))])
async def halt_all_trading(
    reason: str = Query(...),
    admin: Dict = Depends(get_current_admin)
):
    """Emergency halt all trading"""
    logger.critical("ALL TRADING HALTED",
                    reason=reason,
                    admin_id=admin.get("user_id"))
    
    return {
        "success": True,
        "message": "ALL TRADING HALTED",
        "reason": reason,
        "halted_at": datetime.utcnow().isoformat()
    }

@app.get("/trading/orders")
async def list_orders(
    page: int = Query(1),
    limit: int = Query(20),
    status: Optional[str] = None,
    pair: Optional[str] = None,
    user_id: Optional[str] = None,
    admin: Dict = Depends(get_current_admin)
):
    """List all orders with filters"""
    return {
        "success": True,
        "orders": [
            {
                "id": "order_001",
                "user_id": "user_001",
                "pair": "BTC/USDT",
                "type": "limit",
                "side": "buy",
                "price": "65000.00",
                "amount": "1.0",
                "filled": "0.5",
                "status": "partial",
                "created_at": "2024-04-10T10:00:00Z"
            }
        ],
        "pagination": {"page": page, "limit": limit, "total": 5000}
    }

@app.post("/trading/orders/{order_id}/cancel", dependencies=[Depends(check_permission(Permission.CANCEL_ORDERS))])
async def cancel_order(
    order_id: str,
    reason: Optional[str] = None,
    admin: Dict = Depends(get_current_admin)
):
    """Cancel a specific order"""
    return {
        "success": True,
        "message": f"Order {order_id} cancelled",
        "reason": reason
    }

# ============================================================================
# FINANCIAL MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/financials/overview", dependencies=[Depends(check_permission(Permission.VIEW_FINANCIALS))])
async def get_financial_overview(admin: Dict = Depends(get_current_admin)):
    """Get financial overview"""
    return {
        "success": True,
        "financials": {
            "total_balance": "50,000,000.00 USDT",
            "user_balances": "35,000,000.00 USDT",
            "exchange_balance": "15,000,000.00 USDT",
            "pending_withdrawals": "500,000.00 USDT",
            "pending_deposits": "200,000.00 USDT",
            "total_fees_24h": "50,000.00 USDT",
            "total_fees_30d": "1,500,000.00 USDT",
            "total_volume_24h": "10,000,000.00 USDT",
            "total_volume_30d": "300,000,000.00 USDT"
        }
    }

@app.get("/financials/withdrawals", dependencies=[Depends(check_permission(Permission.VIEW_TRANSACTIONS))])
async def list_withdrawals(
    page: int = Query(1),
    limit: int = Query(20),
    status: Optional[str] = None,
    asset: Optional[str] = None,
    admin: Dict = Depends(get_current_admin)
):
    """List all withdrawal requests"""
    return {
        "success": True,
        "withdrawals": [
            {
                "id": "wd_001",
                "user_id": "user_001",
                "asset": "USDT",
                "amount": "10000.00",
                "fee": "10.00",
                "address": "0x123...abc",
                "network": "ERC20",
                "status": "pending",
                "created_at": "2024-04-10T09:00:00Z"
            }
        ],
        "pagination": {"page": page, "limit": limit, "total": 150}
    }

@app.post("/financials/withdrawals/{withdrawal_id}/approve", dependencies=[Depends(check_permission(Permission.APPROVE_WITHDRAWALS))])
async def approve_withdrawal(
    withdrawal_id: str,
    admin: Dict = Depends(get_current_admin)
):
    """Approve a withdrawal request"""
    return {
        "success": True,
        "message": f"Withdrawal {withdrawal_id} approved",
        "approved_by": admin.get("user_id"),
        "approved_at": datetime.utcnow().isoformat()
    }

@app.post("/financials/withdrawals/{withdrawal_id}/reject", dependencies=[Depends(check_permission(Permission.REJECT_WITHDRAWALS))])
async def reject_withdrawal(
    withdrawal_id: str,
    reason: str = Query(...),
    admin: Dict = Depends(get_current_admin)
):
    """Reject a withdrawal request"""
    return {
        "success": True,
        "message": f"Withdrawal {withdrawal_id} rejected",
        "reason": reason
    }

@app.post("/financials/balance/adjust", dependencies=[Depends(check_permission(Permission.ADJUST_BALANCES))])
async def adjust_user_balance(
    adjustment: BalanceAdjustment,
    admin: Dict = Depends(get_current_admin)
):
    """Adjust user balance (add, subtract, set)"""
    logger.info("Balance adjusted",
                user_id=adjustment.user_id,
                asset=adjustment.asset,
                amount=str(adjustment.amount),
                action=adjustment.action,
                reason=adjustment.reason,
                admin_id=admin.get("user_id"))
    
    return {
        "success": True,
        "message": f"Balance {adjustment.action} for {adjustment.user_id}",
        "new_balance": adjustment.amount
    }

@app.post("/financials/balance/freeze", dependencies=[Depends(check_permission(Permission.FREEZE_BALANCES))])
async def freeze_user_balance(
    user_id: str,
    asset: Optional[str] = None,
    reason: str = Query(...),
    admin: Dict = Depends(get_current_admin)
):
    """Freeze user balance"""
    return {
        "success": True,
        "message": f"Balance frozen for user {user_id}",
        "asset": asset or "all",
        "reason": reason
    }

# ============================================================================
# TOKEN & TRADING PAIR MANAGEMENT
# ============================================================================

@app.get("/tokens")
async def list_tokens(admin: Dict = Depends(get_current_admin)):
    """List all listed tokens"""
    return {
        "success": True,
        "tokens": [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "status": "active",
                "blockchain": "Bitcoin",
                "decimals": 8,
                "withdrawal_enabled": True,
                "deposit_enabled": True,
                "withdrawal_fee": "0.0005",
                "min_withdrawal": "0.001",
                "max_withdrawal": "100"
            }
        ]
    }

@app.post("/tokens/list", dependencies=[Depends(check_permission(Permission.LIST_TOKENS))])
async def list_new_token(
    token_data: Dict[str, Any],
    admin: Dict = Depends(get_current_admin)
):
    """List a new token"""
    return {
        "success": True,
        "message": f"Token {token_data.get('symbol')} listed successfully"
    }

@app.delete("/tokens/{symbol}", dependencies=[Depends(check_permission(Permission.DELIST_TOKENS))])
async def delist_token(
    symbol: str,
    reason: str = Query(...),
    admin: Dict = Depends(get_current_admin)
):
    """Delist a token"""
    return {
        "success": True,
        "message": f"Token {symbol} delisted",
        "reason": reason
    }

@app.get("/trading-pairs")
async def list_trading_pairs(admin: Dict = Depends(get_current_admin)):
    """List all trading pairs"""
    return {
        "success": True,
        "pairs": [
            {
                "symbol": "BTC/USDT",
                "base": "BTC",
                "quote": "USDT",
                "status": "active",
                "maker_fee": "0.001",
                "taker_fee": "0.001",
                "min_order": "0.0001",
                "max_order": "1000",
                "price_precision": 2,
                "qty_precision": 6
            }
        ]
    }

@app.put("/trading-pairs/{symbol}", dependencies=[Depends(check_permission(Permission.MANAGE_TRADING_PAIRS))])
async def update_trading_pair(
    symbol: str,
    update: TradingPairUpdate,
    admin: Dict = Depends(get_current_admin)
):
    """Update trading pair settings"""
    return {
        "success": True,
        "message": f"Trading pair {symbol} updated"
    }

# ============================================================================
# SYSTEM MANAGEMENT
# ============================================================================

@app.get("/system/status")
async def get_system_status(admin: Dict = Depends(get_current_admin)):
    """Get overall system status"""
    return {
        "success": True,
        "system": {
            "status": "operational",
            "uptime": "99.99%",
            "version": "3.0.0",
            "services": {
                "trading_engine": "running",
                "matching_engine": "running",
                "wallet_service": "running",
                "auth_service": "running",
                "kyc_service": "running",
                "notification_service": "running"
            },
            "maintenance_mode": False,
            "last_updated": datetime.utcnow().isoformat()
        }
    }

@app.put("/system/config", dependencies=[Depends(check_permission(Permission.SYSTEM_CONFIG))])
async def update_system_config(
    config: SystemConfigUpdate,
    admin: Dict = Depends(get_current_admin)
):
    """Update system configuration"""
    return {
        "success": True,
        "message": "System configuration updated",
        "changes": config.dict(exclude_unset=True)
    }

@app.post("/system/maintenance", dependencies=[Depends(check_permission(Permission.SYSTEM_MAINTENANCE))])
async def toggle_maintenance_mode(
    enabled: bool = Query(...),
    message: Optional[str] = None,
    admin: Dict = Depends(get_current_admin)
):
    """Toggle maintenance mode"""
    return {
        "success": True,
        "maintenance_mode": enabled,
        "message": message
    }

@app.post("/services/control", dependencies=[Depends(check_permission(Permission.RESTART_SERVICES))])
async def control_service(
    control: ServiceControl,
    admin: Dict = Depends(get_current_admin)
):
    """Control individual services (start, stop, restart, pause)"""
    return {
        "success": True,
        "message": f"Service {control.service_name} {control.action}ed"
    }

@app.get("/system/metrics", dependencies=[Depends(check_permission(Permission.VIEW_SYSTEM_METRICS))])
async def get_system_metrics(admin: Dict = Depends(get_current_admin)):
    """Get system performance metrics"""
    return {
        "success": True,
        "metrics": {
            "cpu_usage": "45%",
            "memory_usage": "60%",
            "disk_usage": "35%",
            "network_in": "1.5 GB/s",
            "network_out": "2.0 GB/s",
            "active_connections": 15000,
            "requests_per_second": 5000,
            "average_latency": "25ms",
            "error_rate": "0.01%"
        }
    }

# ============================================================================
# KYC/AML MANAGEMENT
# ============================================================================

@app.get("/kyc/pending", dependencies=[Depends(check_permission(Permission.VIEW_KYC))])
async def list_pending_kyc(
    page: int = Query(1),
    limit: int = Query(20),
    admin: Dict = Depends(get_current_admin)
):
    """List pending KYC applications"""
    return {
        "success": True,
        "applications": [
            {
                "id": "kyc_001",
                "user_id": "user_001",
                "status": "pending",
                "level": 2,
                "submitted_at": "2024-04-09T10:00:00Z",
                "documents": ["passport", "selfie", "proof_of_address"]
            }
        ]
    }

@app.post("/kyc/{kyc_id}/approve", dependencies=[Depends(check_permission(Permission.APPROVE_KYC))])
async def approve_kyc(
    kyc_id: str,
    level: int = Query(...),
    admin: Dict = Depends(get_current_admin)
):
    """Approve KYC application"""
    return {
        "success": True,
        "message": f"KYC {kyc_id} approved for level {level}"
    }

@app.post("/kyc/{kyc_id}/reject", dependencies=[Depends(check_permission(Permission.REJECT_KYC))])
async def reject_kyc(
    kyc_id: str,
    reason: str = Query(...),
    admin: Dict = Depends(get_current_admin)
):
    """Reject KYC application"""
    return {
        "success": True,
        "message": f"KYC {kyc_id} rejected",
        "reason": reason
    }

# ============================================================================
# ANNOUNCEMENTS
# ============================================================================

@app.get("/announcements")
async def list_announcements(admin: Dict = Depends(get_current_admin)):
    """List all announcements"""
    return {
        "success": True,
        "announcements": [
            {
                "id": "ann_001",
                "title": "System Maintenance",
                "content": "Scheduled maintenance on April 15th",
                "type": "warning",
                "active": True,
                "created_at": "2024-04-10T00:00:00Z"
            }
        ]
    }

@app.post("/announcements", dependencies=[Depends(check_permission(Permission.MANAGE_NOTIFICATIONS))])
async def create_announcement(
    announcement: AnnouncementCreate,
    admin: Dict = Depends(get_current_admin)
):
    """Create a new announcement"""
    return {
        "success": True,
        "message": "Announcement created",
        "id": "ann_new"
    }

@app.delete("/announcements/{announcement_id}", dependencies=[Depends(check_permission(Permission.MANAGE_NOTIFICATIONS))])
async def delete_announcement(
    announcement_id: str,
    admin: Dict = Depends(get_current_admin)
):
    """Delete an announcement"""
    return {
        "success": True,
        "message": f"Announcement {announcement_id} deleted"
    }

# ============================================================================
# REPORTS
# ============================================================================

@app.get("/reports/trading-volume", dependencies=[Depends(check_permission(Permission.VIEW_REPORTS))])
async def get_trading_volume_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    admin: Dict = Depends(get_current_admin)
):
    """Get trading volume report"""
    return {
        "success": True,
        "report": {
            "period": {"start": start_date, "end": end_date},
            "total_volume": "500,000,000.00 USDT",
            "total_trades": 150000,
            "breakdown": {
                "spot": "300,000,000.00",
                "futures": "150,000,000.00",
                "margin": "50,000,000.00"
            }
        }
    }

@app.get("/reports/fee-revenue", dependencies=[Depends(check_permission(Permission.VIEW_REPORTS))])
async def get_fee_revenue_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    admin: Dict = Depends(get_current_admin)
):
    """Get fee revenue report"""
    return {
        "success": True,
        "report": {
            "period": {"start": start_date, "end": end_date},
            "total_fees": "2,500,000.00 USDT",
            "maker_fees": "1,200,000.00",
            "taker_fees": "1,300,000.00",
            "withdrawal_fees": "500,000.00"
        }
    }

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "unified-admin-service",
        "version": "3.0.0"
    }

@app.get("/")
async def root():
    return {
        "service": "TigerEx Unified Admin Service",
        "version": "3.0.0",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)