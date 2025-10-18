"""
TigerEx Universal Admin Control Service
Complete admin control system for all trading operations across all exchanges
Includes full CRUD operations for all trading types with user access management
"""

from fastapi import FastAPI, HTTPException, Depends, Security, Query, Body, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import jwt
import hashlib
import logging
from decimal import Decimal
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TigerEx Universal Admin Control Service",
    version="2.0.0",
    description="Complete admin control system with full user access management"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
JWT_SECRET = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"

# ==================== ENUMS ====================

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    TRADER = "trader"
    VIEWER = "viewer"
    SUSPENDED = "suspended"

class Permission(str, Enum):
    # Trading Permissions
    SPOT_TRADING = "spot_trading"
    FUTURES_TRADING = "futures_trading"
    OPTIONS_TRADING = "options_trading"
    MARGIN_TRADING = "margin_trading"
    DERIVATIVES_TRADING = "derivatives_trading"
    COPY_TRADING = "copy_trading"
    ETF_TRADING = "etf_trading"
    
    # Wallet Permissions
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    TRANSFER = "transfer"
    
    # Admin Permissions
    CREATE_CONTRACT = "create_contract"
    LAUNCH_CONTRACT = "launch_contract"
    PAUSE_CONTRACT = "pause_contract"
    RESUME_CONTRACT = "resume_contract"
    DELETE_CONTRACT = "delete_contract"
    UPDATE_CONTRACT = "update_contract"
    
    # User Management Permissions
    CREATE_USER = "create_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    MANAGE_ROLES = "manage_roles"
    MANAGE_PERMISSIONS = "manage_permissions"
    
    # System Permissions
    VIEW_ANALYTICS = "view_analytics"
    VIEW_AUDIT_LOG = "view_audit_log"
    SYSTEM_CONFIG = "system_config"
    EMERGENCY_STOP = "emergency_stop"

class TradingType(str, Enum):
    SPOT = "spot"
    FUTURES_PERPETUAL = "futures_perpetual"
    FUTURES_CROSS = "futures_cross"
    FUTURES_DELIVERY = "futures_delivery"
    MARGIN = "margin"
    MARGIN_CROSS = "margin_cross"
    MARGIN_ISOLATED = "margin_isolated"
    OPTIONS = "options"
    DERIVATIVES = "derivatives"
    COPY_TRADING = "copy_trading"
    ETF = "etf"

class Exchange(str, Enum):
    BINANCE = "binance"
    KUCOIN = "kucoin"
    BYBIT = "bybit"
    OKX = "okx"
    MEXC = "mexc"
    BITGET = "bitget"
    BITFINEX = "bitfinex"

class ContractStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    DELISTED = "delisted"
    PENDING = "pending"

class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    PENDING_VERIFICATION = "pending_verification"

class KYCStatus(str, Enum):
    NOT_SUBMITTED = "not_submitted"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

# ==================== MODELS ====================

class User(BaseModel):
    user_id: str
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: UserRole
    permissions: List[Permission]
    status: UserStatus
    kyc_status: KYCStatus
    kyc_level: int = 0
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    two_factor_enabled: bool = False
    trading_enabled: bool = True
    withdrawal_enabled: bool = True
    deposit_enabled: bool = True
    max_daily_withdrawal: float = 100000
    max_single_withdrawal: float = 10000
    referral_code: Optional[str] = None
    referred_by: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class UserCreateRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.TRADER
    permissions: Optional[List[Permission]] = None
    referral_code: Optional[str] = None

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    permissions: Optional[List[Permission]] = None
    status: Optional[UserStatus] = None
    kyc_status: Optional[KYCStatus] = None
    kyc_level: Optional[int] = None
    trading_enabled: Optional[bool] = None
    withdrawal_enabled: Optional[bool] = None
    deposit_enabled: Optional[bool] = None
    max_daily_withdrawal: Optional[float] = None
    max_single_withdrawal: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class TradingPermissionUpdate(BaseModel):
    user_id: str
    trading_type: TradingType
    enabled: bool
    max_leverage: Optional[int] = None
    max_position_size: Optional[float] = None
    reason: Optional[str] = None

class ContractManagement(BaseModel):
    contract_id: str
    exchange: Exchange
    trading_type: TradingType
    symbol: str
    status: ContractStatus
    created_by: str
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None

class SystemConfig(BaseModel):
    config_id: str
    category: str
    key: str
    value: Any
    description: Optional[str] = None
    updated_by: str
    updated_at: datetime

class AuditLog(BaseModel):
    log_id: str
    timestamp: datetime
    admin_id: str
    admin_username: str
    action: str
    target_type: str
    target_id: str
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class EmergencyAction(BaseModel):
    action_type: str
    target: Optional[str] = None
    reason: str
    executed_by: str
    executed_at: datetime

# ==================== IN-MEMORY STORAGE ====================

users_db: Dict[str, User] = {}
contracts_db: Dict[str, ContractManagement] = {}
system_config_db: Dict[str, SystemConfig] = {}
audit_logs: List[AuditLog] = []
emergency_actions: List[EmergencyAction] = []

# Default role permissions
ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: list(Permission),
    UserRole.ADMIN: [
        Permission.CREATE_CONTRACT, Permission.LAUNCH_CONTRACT,
        Permission.PAUSE_CONTRACT, Permission.RESUME_CONTRACT,
        Permission.UPDATE_CONTRACT, Permission.CREATE_USER,
        Permission.UPDATE_USER, Permission.MANAGE_PERMISSIONS,
        Permission.VIEW_ANALYTICS, Permission.VIEW_AUDIT_LOG
    ],
    UserRole.MODERATOR: [
        Permission.PAUSE_CONTRACT, Permission.UPDATE_USER,
        Permission.VIEW_ANALYTICS, Permission.VIEW_AUDIT_LOG
    ],
    UserRole.TRADER: [
        Permission.SPOT_TRADING, Permission.FUTURES_TRADING,
        Permission.OPTIONS_TRADING, Permission.MARGIN_TRADING,
        Permission.DERIVATIVES_TRADING, Permission.COPY_TRADING,
        Permission.ETF_TRADING, Permission.DEPOSIT,
        Permission.WITHDRAW, Permission.TRANSFER
    ],
    UserRole.VIEWER: [Permission.VIEW_ANALYTICS],
    UserRole.SUSPENDED: []
}

# ==================== HELPER FUNCTIONS ====================

def verify_admin_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> User:
    """Verify admin JWT token and return user"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        
        if user_id not in users_db:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = users_db[user_id]
        
        if user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MODERATOR]:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        if user.status != UserStatus.ACTIVE:
            raise HTTPException(status_code=403, detail="User account is not active")
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def check_permission(user: User, required_permission: Permission):
    """Check if user has required permission"""
    if user.role == UserRole.SUPER_ADMIN:
        return True
    
    if required_permission not in user.permissions:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied. Required permission: {required_permission.value}"
        )
    return True

def generate_user_id() -> str:
    """Generate unique user ID"""
    return hashlib.sha256(f"{datetime.now().isoformat()}{len(users_db)}".encode()).hexdigest()[:16].upper()

def generate_audit_log_id() -> str:
    """Generate unique audit log ID"""
    return hashlib.sha256(f"{datetime.now().isoformat()}{len(audit_logs)}".encode()).hexdigest()[:16].upper()

def log_audit(admin: User, action: str, target_type: str, target_id: str, details: Dict[str, Any]):
    """Log admin action for audit trail"""
    log = AuditLog(
        log_id=generate_audit_log_id(),
        timestamp=datetime.now(),
        admin_id=admin.user_id,
        admin_username=admin.username,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details
    )
    audit_logs.append(log)
    logger.info(f"Audit log created: {action} by {admin.username} on {target_type} {target_id}")

# ==================== USER MANAGEMENT ENDPOINTS ====================

@app.post("/api/v1/admin/users/create", response_model=User)
async def create_user(
    request: UserCreateRequest,
    admin: User = Depends(verify_admin_token)
):
    """Admin: Create a new user account"""
    check_permission(admin, Permission.CREATE_USER)
    
    # Check if email or username already exists
    for user in users_db.values():
        if user.email == request.email:
            raise HTTPException(status_code=400, detail="Email already registered")
        if user.username == request.username:
            raise HTTPException(status_code=400, detail="Username already taken")
    
    user_id = generate_user_id()
    
    # Set default permissions based on role
    permissions = request.permissions if request.permissions else ROLE_PERMISSIONS.get(request.role, [])
    
    user = User(
        user_id=user_id,
        email=request.email,
        username=request.username,
        full_name=request.full_name,
        role=request.role,
        permissions=permissions,
        status=UserStatus.ACTIVE,
        kyc_status=KYCStatus.NOT_SUBMITTED,
        kyc_level=0,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        referral_code=hashlib.sha256(user_id.encode()).hexdigest()[:8].upper(),
        referred_by=request.referral_code
    )
    
    users_db[user_id] = user
    
    log_audit(
        admin=admin,
        action="CREATE_USER",
        target_type="user",
        target_id=user_id,
        details={
            "email": request.email,
            "username": request.username,
            "role": request.role.value
        }
    )
    
    logger.info(f"User created: {user_id} - {request.username} by admin {admin.username}")
    return user

@app.get("/api/v1/admin/users", response_model=List[User])
async def list_users(
    admin: User = Depends(verify_admin_token),
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None,
    kyc_status: Optional[KYCStatus] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Admin: List all users with optional filters"""
    users = list(users_db.values())
    
    if role:
        users = [u for u in users if u.role == role]
    if status:
        users = [u for u in users if u.status == status]
    if kyc_status:
        users = [u for u in users if u.kyc_status == kyc_status]
    
    return users[offset:offset + limit]

@app.get("/api/v1/admin/users/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    admin: User = Depends(verify_admin_token)
):
    """Admin: Get user details"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    return users_db[user_id]

@app.put("/api/v1/admin/users/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    request: UserUpdateRequest,
    admin: User = Depends(verify_admin_token)
):
    """Admin: Update user account"""
    check_permission(admin, Permission.UPDATE_USER)
    
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_db[user_id]
    updates = {}
    
    if request.full_name is not None:
        user.full_name = request.full_name
        updates["full_name"] = request.full_name
    
    if request.role is not None:
        if admin.role != UserRole.SUPER_ADMIN and request.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
            raise HTTPException(status_code=403, detail="Only super admin can assign admin roles")
        user.role = request.role
        updates["role"] = request.role.value
    
    if request.permissions is not None:
        check_permission(admin, Permission.MANAGE_PERMISSIONS)
        user.permissions = request.permissions
        updates["permissions"] = [p.value for p in request.permissions]
    
    if request.status is not None:
        user.status = request.status
        updates["status"] = request.status.value
    
    if request.kyc_status is not None:
        user.kyc_status = request.kyc_status
        updates["kyc_status"] = request.kyc_status.value
    
    if request.kyc_level is not None:
        user.kyc_level = request.kyc_level
        updates["kyc_level"] = request.kyc_level
    
    if request.trading_enabled is not None:
        user.trading_enabled = request.trading_enabled
        updates["trading_enabled"] = request.trading_enabled
    
    if request.withdrawal_enabled is not None:
        user.withdrawal_enabled = request.withdrawal_enabled
        updates["withdrawal_enabled"] = request.withdrawal_enabled
    
    if request.deposit_enabled is not None:
        user.deposit_enabled = request.deposit_enabled
        updates["deposit_enabled"] = request.deposit_enabled
    
    if request.max_daily_withdrawal is not None:
        user.max_daily_withdrawal = request.max_daily_withdrawal
        updates["max_daily_withdrawal"] = request.max_daily_withdrawal
    
    if request.max_single_withdrawal is not None:
        user.max_single_withdrawal = request.max_single_withdrawal
        updates["max_single_withdrawal"] = request.max_single_withdrawal
    
    if request.metadata is not None:
        user.metadata = request.metadata
        updates["metadata"] = request.metadata
    
    user.updated_at = datetime.now()
    
    log_audit(
        admin=admin,
        action="UPDATE_USER",
        target_type="user",
        target_id=user_id,
        details=updates
    )
    
    logger.info(f"User updated: {user_id} by admin {admin.username}")
    return user

@app.delete("/api/v1/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    admin: User = Depends(verify_admin_token)
):
    """Admin: Delete user account (soft delete by suspending)"""
    check_permission(admin, Permission.DELETE_USER)
    
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_db[user_id]
    
    if user.role == UserRole.SUPER_ADMIN and admin.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can delete super admin accounts")
    
    user.status = UserStatus.BANNED
    user.trading_enabled = False
    user.withdrawal_enabled = False
    user.deposit_enabled = False
    user.updated_at = datetime.now()
    
    log_audit(
        admin=admin,
        action="DELETE_USER",
        target_type="user",
        target_id=user_id,
        details={"username": user.username, "email": user.email}
    )
    
    logger.info(f"User deleted: {user_id} by admin {admin.username}")
    return {"message": "User account deleted successfully", "user_id": user_id}

@app.post("/api/v1/admin/users/{user_id}/suspend")
async def suspend_user(
    user_id: str,
    reason: str = Body(..., embed=True),
    admin: User = Depends(verify_admin_token)
):
    """Admin: Suspend user account"""
    check_permission(admin, Permission.UPDATE_USER)
    
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_db[user_id]
    user.status = UserStatus.SUSPENDED
    user.trading_enabled = False
    user.updated_at = datetime.now()
    
    log_audit(
        admin=admin,
        action="SUSPEND_USER",
        target_type="user",
        target_id=user_id,
        details={"reason": reason, "username": user.username}
    )
    
    logger.info(f"User suspended: {user_id} by admin {admin.username}. Reason: {reason}")
    return {"message": "User suspended successfully", "user_id": user_id}

@app.post("/api/v1/admin/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    admin: User = Depends(verify_admin_token)
):
    """Admin: Activate suspended user account"""
    check_permission(admin, Permission.UPDATE_USER)
    
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_db[user_id]
    user.status = UserStatus.ACTIVE
    user.trading_enabled = True
    user.updated_at = datetime.now()
    
    log_audit(
        admin=admin,
        action="ACTIVATE_USER",
        target_type="user",
        target_id=user_id,
        details={"username": user.username}
    )
    
    logger.info(f"User activated: {user_id} by admin {admin.username}")
    return {"message": "User activated successfully", "user_id": user_id}

@app.post("/api/v1/admin/users/{user_id}/trading-permission")
async def update_trading_permission(
    user_id: str,
    request: TradingPermissionUpdate,
    admin: User = Depends(verify_admin_token)
):
    """Admin: Update user's trading permissions for specific trading type"""
    check_permission(admin, Permission.MANAGE_PERMISSIONS)
    
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_db[user_id]
    
    # Map trading type to permission
    permission_map = {
        TradingType.SPOT: Permission.SPOT_TRADING,
        TradingType.FUTURES_PERPETUAL: Permission.FUTURES_TRADING,
        TradingType.FUTURES_CROSS: Permission.FUTURES_TRADING,
        TradingType.FUTURES_DELIVERY: Permission.FUTURES_TRADING,
        TradingType.MARGIN: Permission.MARGIN_TRADING,
        TradingType.MARGIN_CROSS: Permission.MARGIN_TRADING,
        TradingType.MARGIN_ISOLATED: Permission.MARGIN_TRADING,
        TradingType.OPTIONS: Permission.OPTIONS_TRADING,
        TradingType.DERIVATIVES: Permission.DERIVATIVES_TRADING,
        TradingType.COPY_TRADING: Permission.COPY_TRADING,
        TradingType.ETF: Permission.ETF_TRADING
    }
    
    permission = permission_map.get(request.trading_type)
    
    if request.enabled:
        if permission not in user.permissions:
            user.permissions.append(permission)
    else:
        if permission in user.permissions:
            user.permissions.remove(permission)
    
    user.updated_at = datetime.now()
    
    log_audit(
        admin=admin,
        action="UPDATE_TRADING_PERMISSION",
        target_type="user",
        target_id=user_id,
        details={
            "trading_type": request.trading_type.value,
            "enabled": request.enabled,
            "reason": request.reason
        }
    )
    
    logger.info(f"Trading permission updated for user {user_id}: {request.trading_type.value} = {request.enabled}")
    return {"message": "Trading permission updated successfully", "user": user}

# ==================== ROLE MANAGEMENT ENDPOINTS ====================

@app.post("/api/v1/admin/roles/{user_id}/assign")
async def assign_role(
    user_id: str,
    role: UserRole = Body(..., embed=True),
    admin: User = Depends(verify_admin_token)
):
    """Admin: Assign role to user"""
    check_permission(admin, Permission.MANAGE_ROLES)
    
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    if admin.role != UserRole.SUPER_ADMIN and role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only super admin can assign admin roles")
    
    user = users_db[user_id]
    old_role = user.role
    user.role = role
    user.permissions = ROLE_PERMISSIONS.get(role, [])
    user.updated_at = datetime.now()
    
    log_audit(
        admin=admin,
        action="ASSIGN_ROLE",
        target_type="user",
        target_id=user_id,
        details={"old_role": old_role.value, "new_role": role.value}
    )
    
    logger.info(f"Role assigned to user {user_id}: {old_role.value} -> {role.value}")
    return {"message": "Role assigned successfully", "user": user}

@app.get("/api/v1/admin/roles")
async def list_roles(admin: User = Depends(verify_admin_token)):
    """Admin: List all available roles and their permissions"""
    return {
        "roles": [
            {
                "role": role.value,
                "permissions": [p.value for p in perms]
            }
            for role, perms in ROLE_PERMISSIONS.items()
        ]
    }

# ==================== AUDIT LOG ENDPOINTS ====================

@app.get("/api/v1/admin/audit-logs", response_model=List[AuditLog])
async def get_audit_logs(
    admin: User = Depends(verify_admin_token),
    action: Optional[str] = None,
    target_type: Optional[str] = None,
    admin_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Admin: Get audit logs with optional filters"""
    check_permission(admin, Permission.VIEW_AUDIT_LOG)
    
    logs = audit_logs.copy()
    
    if action:
        logs = [log for log in logs if log.action == action]
    if target_type:
        logs = [log for log in logs if log.target_type == target_type]
    if admin_id:
        logs = [log for log in logs if log.admin_id == admin_id]
    
    # Sort by timestamp descending
    logs.sort(key=lambda x: x.timestamp, reverse=True)
    
    return logs[offset:offset + limit]

# ==================== EMERGENCY CONTROLS ====================

@app.post("/api/v1/admin/emergency/halt-trading")
async def emergency_halt_trading(
    reason: str = Body(..., embed=True),
    admin: User = Depends(verify_admin_token)
):
    """Admin: Emergency halt all trading activities"""
    check_permission(admin, Permission.EMERGENCY_STOP)
    
    # Disable trading for all users
    for user in users_db.values():
        if user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
            user.trading_enabled = False
    
    emergency_action = EmergencyAction(
        action_type="HALT_TRADING",
        reason=reason,
        executed_by=admin.user_id,
        executed_at=datetime.now()
    )
    emergency_actions.append(emergency_action)
    
    log_audit(
        admin=admin,
        action="EMERGENCY_HALT_TRADING",
        target_type="system",
        target_id="all",
        details={"reason": reason}
    )
    
    logger.warning(f"EMERGENCY: Trading halted by {admin.username}. Reason: {reason}")
    return {"message": "Trading halted for all users", "action": emergency_action}

@app.post("/api/v1/admin/emergency/resume-trading")
async def emergency_resume_trading(
    admin: User = Depends(verify_admin_token)
):
    """Admin: Resume trading after emergency halt"""
    check_permission(admin, Permission.EMERGENCY_STOP)
    
    # Re-enable trading for active users
    for user in users_db.values():
        if user.status == UserStatus.ACTIVE and user.role not in [UserRole.SUSPENDED]:
            user.trading_enabled = True
    
    emergency_action = EmergencyAction(
        action_type="RESUME_TRADING",
        reason="Emergency resolved",
        executed_by=admin.user_id,
        executed_at=datetime.now()
    )
    emergency_actions.append(emergency_action)
    
    log_audit(
        admin=admin,
        action="EMERGENCY_RESUME_TRADING",
        target_type="system",
        target_id="all",
        details={}
    )
    
    logger.info(f"Trading resumed by {admin.username}")
    return {"message": "Trading resumed for all active users", "action": emergency_action}

@app.post("/api/v1/admin/emergency/halt-withdrawals")
async def emergency_halt_withdrawals(
    reason: str = Body(..., embed=True),
    admin: User = Depends(verify_admin_token)
):
    """Admin: Emergency halt all withdrawals"""
    check_permission(admin, Permission.EMERGENCY_STOP)
    
    for user in users_db.values():
        if user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
            user.withdrawal_enabled = False
    
    emergency_action = EmergencyAction(
        action_type="HALT_WITHDRAWALS",
        reason=reason,
        executed_by=admin.user_id,
        executed_at=datetime.now()
    )
    emergency_actions.append(emergency_action)
    
    log_audit(
        admin=admin,
        action="EMERGENCY_HALT_WITHDRAWALS",
        target_type="system",
        target_id="all",
        details={"reason": reason}
    )
    
    logger.warning(f"EMERGENCY: Withdrawals halted by {admin.username}. Reason: {reason}")
    return {"message": "Withdrawals halted for all users", "action": emergency_action}

@app.get("/api/v1/admin/emergency/actions", response_model=List[EmergencyAction])
async def get_emergency_actions(
    admin: User = Depends(verify_admin_token),
    limit: int = Query(50, ge=1, le=500)
):
    """Admin: Get history of emergency actions"""
    check_permission(admin, Permission.VIEW_AUDIT_LOG)
    
    return emergency_actions[-limit:]

# ==================== SYSTEM STATISTICS ====================

@app.get("/api/v1/admin/statistics")
async def get_system_statistics(admin: User = Depends(verify_admin_token)):
    """Admin: Get system statistics"""
    check_permission(admin, Permission.VIEW_ANALYTICS)
    
    total_users = len(users_db)
    active_users = len([u for u in users_db.values() if u.status == UserStatus.ACTIVE])
    suspended_users = len([u for u in users_db.values() if u.status == UserStatus.SUSPENDED])
    
    users_by_role = {}
    for role in UserRole:
        users_by_role[role.value] = len([u for u in users_db.values() if u.role == role])
    
    users_by_kyc = {}
    for kyc_status in KYCStatus:
        users_by_kyc[kyc_status.value] = len([u for u in users_db.values() if u.kyc_status == kyc_status])
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "suspended_users": suspended_users,
        "users_by_role": users_by_role,
        "users_by_kyc_status": users_by_kyc,
        "total_contracts": len(contracts_db),
        "total_audit_logs": len(audit_logs),
        "total_emergency_actions": len(emergency_actions),
        "timestamp": datetime.now()
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "2.0.0",
        "total_users": len(users_db),
        "total_audit_logs": len(audit_logs)
    }

# ==================== INITIALIZATION ====================

@app.on_event("startup")
async def startup_event():
    """Initialize system with default super admin"""
    super_admin_id = "SUPERADMIN001"
    
    if super_admin_id not in users_db:
        super_admin = User(
            user_id=super_admin_id,
            email="admin@tigerex.com",
            username="superadmin",
            full_name="Super Administrator",
            role=UserRole.SUPER_ADMIN,
            permissions=list(Permission),
            status=UserStatus.ACTIVE,
            kyc_status=KYCStatus.APPROVED,
            kyc_level=3,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            referral_code="SUPERADMIN"
        )
        users_db[super_admin_id] = super_admin
        logger.info("Default super admin created")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)