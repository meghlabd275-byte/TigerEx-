"""
TigerEx Admin Control Template v3.0.0
=====================================
This template provides comprehensive admin controls for all backend services.
Apply this template to any service that needs admin functionality.

Features:
- Role-Based Access Control (RBAC)
- Complete admin operations
- Audit logging
- Security controls
- Feature parity with major exchanges
"""

from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import jwt
import logging
from functools import wraps

# Version
VERSION = "3.0.0"

# Security
security = HTTPBearer()
SECRET_KEY = "your-secret-key-here"  # Should be in environment variables
ALGORITHM = "HS256"

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# ENUMS
# ============================================================================

class UserRole(str, Enum):
    """User roles for RBAC"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    SUPPORT = "support"
    COMPLIANCE = "compliance"
    RISK_MANAGER = "risk_manager"
    TRADER = "trader"
    USER = "user"

class Permission(str, Enum):
    """Granular permissions"""
    # User Management
    USER_VIEW = "user:view"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_SUSPEND = "user:suspend"
    USER_VERIFY = "user:verify"
    
    # Financial Controls
    WITHDRAWAL_APPROVE = "withdrawal:approve"
    WITHDRAWAL_REJECT = "withdrawal:reject"
    DEPOSIT_MONITOR = "deposit:monitor"
    TRANSACTION_REVIEW = "transaction:review"
    FEE_MANAGE = "fee:manage"
    
    # Trading Controls
    TRADING_HALT = "trading:halt"
    TRADING_RESUME = "trading:resume"
    PAIR_MANAGE = "pair:manage"
    LIQUIDITY_MANAGE = "liquidity:manage"
    
    # Risk Management
    RISK_CONFIGURE = "risk:configure"
    POSITION_MONITOR = "position:monitor"
    LIQUIDATION_MANAGE = "liquidation:manage"
    
    # System Controls
    SYSTEM_CONFIG = "system:config"
    FEATURE_FLAG = "feature:flag"
    MAINTENANCE_MODE = "maintenance:mode"
    
    # Compliance
    KYC_APPROVE = "kyc:approve"
    KYC_REJECT = "kyc:reject"
    AML_MONITOR = "aml:monitor"
    COMPLIANCE_REPORT = "compliance:report"
    
    # Content Management
    ANNOUNCEMENT_CREATE = "announcement:create"
    ANNOUNCEMENT_UPDATE = "announcement:update"
    ANNOUNCEMENT_DELETE = "announcement:delete"
    
    # Analytics
    ANALYTICS_VIEW = "analytics:view"
    REPORT_GENERATE = "report:generate"
    AUDIT_LOG_VIEW = "audit:view"

class ActionType(str, Enum):
    """Audit log action types"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    REJECT = "reject"
    SUSPEND = "suspend"
    ACTIVATE = "activate"
    CONFIG = "config"

# ============================================================================
# MODELS
# ============================================================================

class AdminUser(BaseModel):
    """Admin user model"""
    user_id: str
    username: str
    email: str
    role: UserRole
    permissions: List[Permission]
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

class AuditLog(BaseModel):
    """Audit log entry"""
    log_id: str
    admin_id: str
    admin_username: str
    action: ActionType
    resource_type: str
    resource_id: str
    details: Dict[str, Any]
    ip_address: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    success: bool = True
    error_message: Optional[str] = None

class AdminAction(BaseModel):
    """Generic admin action request"""
    action: str
    target_id: str
    reason: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class AdminResponse(BaseModel):
    """Generic admin response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# ============================================================================
# ROLE PERMISSIONS MAPPING
# ============================================================================

ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: [p for p in Permission],  # All permissions
    UserRole.ADMIN: [
        Permission.USER_VIEW, Permission.USER_CREATE, Permission.USER_UPDATE,
        Permission.USER_SUSPEND, Permission.USER_VERIFY,
        Permission.WITHDRAWAL_APPROVE, Permission.WITHDRAWAL_REJECT,
        Permission.DEPOSIT_MONITOR, Permission.TRANSACTION_REVIEW,
        Permission.FEE_MANAGE, Permission.TRADING_HALT, Permission.TRADING_RESUME,
        Permission.PAIR_MANAGE, Permission.RISK_CONFIGURE, Permission.POSITION_MONITOR,
        Permission.SYSTEM_CONFIG, Permission.KYC_APPROVE, Permission.KYC_REJECT,
        Permission.ANNOUNCEMENT_CREATE, Permission.ANNOUNCEMENT_UPDATE,
        Permission.ANALYTICS_VIEW, Permission.REPORT_GENERATE, Permission.AUDIT_LOG_VIEW
    ],
    UserRole.MODERATOR: [
        Permission.USER_VIEW, Permission.USER_SUSPEND,
        Permission.TRANSACTION_REVIEW, Permission.KYC_APPROVE,
        Permission.ANNOUNCEMENT_CREATE, Permission.ANALYTICS_VIEW
    ],
    UserRole.SUPPORT: [
        Permission.USER_VIEW, Permission.TRANSACTION_REVIEW,
        Permission.ANALYTICS_VIEW
    ],
    UserRole.COMPLIANCE: [
        Permission.USER_VIEW, Permission.USER_VERIFY,
        Permission.WITHDRAWAL_APPROVE, Permission.WITHDRAWAL_REJECT,
        Permission.TRANSACTION_REVIEW, Permission.KYC_APPROVE, Permission.KYC_REJECT,
        Permission.AML_MONITOR, Permission.COMPLIANCE_REPORT,
        Permission.AUDIT_LOG_VIEW
    ],
    UserRole.RISK_MANAGER: [
        Permission.POSITION_MONITOR, Permission.RISK_CONFIGURE,
        Permission.LIQUIDATION_MANAGE, Permission.TRADING_HALT,
        Permission.ANALYTICS_VIEW, Permission.REPORT_GENERATE
    ],
    UserRole.TRADER: [],
    UserRole.USER: []
}

# ============================================================================
# AUTHENTICATION & AUTHORIZATION
# ============================================================================

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict:
    """Verify JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def get_current_admin(token_data: Dict = Depends(verify_token)) -> AdminUser:
    """Get current admin user from token"""
    # In production, fetch from database
    role = UserRole(token_data.get("role", "user"))
    permissions = ROLE_PERMISSIONS.get(role, [])
    
    return AdminUser(
        user_id=token_data["user_id"],
        username=token_data["username"],
        email=token_data.get("email", ""),
        role=role,
        permissions=permissions
    )

def require_permission(required_permission: Permission):
    """Decorator to require specific permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, admin: AdminUser = Depends(get_current_admin), **kwargs):
            if required_permission not in admin.permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied. Required: {required_permission}"
                )
            return await func(*args, admin=admin, **kwargs)
        return wrapper
    return decorator

def require_role(required_roles: List[UserRole]):
    """Decorator to require specific role(s)"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, admin: AdminUser = Depends(get_current_admin), **kwargs):
            if admin.role not in required_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role denied. Required: {required_roles}"
                )
            return await func(*args, admin=admin, **kwargs)
        return wrapper
    return decorator

# ============================================================================
# AUDIT LOGGING
# ============================================================================

class AuditLogger:
    """Audit logging service"""
    
    @staticmethod
    async def log_action(
        admin: AdminUser,
        action: ActionType,
        resource_type: str,
        resource_id: str,
        details: Dict[str, Any],
        ip_address: str,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Log admin action"""
        log_entry = AuditLog(
            log_id=f"audit_{datetime.utcnow().timestamp()}",
            admin_id=admin.user_id,
            admin_username=admin.username,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            success=success,
            error_message=error_message
        )
        
        # In production, save to database
        logger.info(f"AUDIT: {log_entry.dict()}")
        return log_entry

# ============================================================================
# ADMIN ENDPOINTS TEMPLATE
# ============================================================================

def create_admin_router(app: FastAPI, service_name: str):
    """
    Create admin router for a service
    
    Usage:
        app = FastAPI()
        create_admin_router(app, "trading-service")
    """
    
    @app.get("/admin/health")
    async def admin_health():
        """Admin health check"""
        return {
            "service": service_name,
            "version": VERSION,
            "status": "healthy",
            "timestamp": datetime.utcnow()
        }
    
    @app.get("/admin/permissions")
    async def get_permissions(admin: AdminUser = Depends(get_current_admin)):
        """Get current admin permissions"""
        return {
            "user_id": admin.user_id,
            "username": admin.username,
            "role": admin.role,
            "permissions": admin.permissions
        }
    
    # ========================================================================
    # USER MANAGEMENT ENDPOINTS
    # ========================================================================
    
    @app.get("/admin/users")
    @require_permission(Permission.USER_VIEW)
    async def list_users(
        admin: AdminUser = Depends(get_current_admin),
        page: int = 1,
        limit: int = 50
    ):
        """List all users"""
        # Implementation here
        return {"users": [], "total": 0, "page": page, "limit": limit}
    
    @app.get("/admin/users/{user_id}")
    @require_permission(Permission.USER_VIEW)
    async def get_user(
        user_id: str,
        admin: AdminUser = Depends(get_current_admin)
    ):
        """Get user details"""
        # Implementation here
        return {"user_id": user_id, "details": {}}
    
    @app.post("/admin/users/{user_id}/suspend")
    @require_permission(Permission.USER_SUSPEND)
    async def suspend_user(
        user_id: str,
        action: AdminAction,
        admin: AdminUser = Depends(get_current_admin)
    ):
        """Suspend user account"""
        await AuditLogger.log_action(
            admin=admin,
            action=ActionType.SUSPEND,
            resource_type="user",
            resource_id=user_id,
            details={"reason": action.reason},
            ip_address="0.0.0.0"
        )
        return AdminResponse(success=True, message=f"User {user_id} suspended")
    
    @app.post("/admin/users/{user_id}/activate")
    @require_permission(Permission.USER_UPDATE)
    async def activate_user(
        user_id: str,
        admin: AdminUser = Depends(get_current_admin)
    ):
        """Activate user account"""
        await AuditLogger.log_action(
            admin=admin,
            action=ActionType.ACTIVATE,
            resource_type="user",
            resource_id=user_id,
            details={},
            ip_address="0.0.0.0"
        )
        return AdminResponse(success=True, message=f"User {user_id} activated")
    
    # ========================================================================
    # FINANCIAL CONTROL ENDPOINTS
    # ========================================================================
    
    @app.get("/admin/withdrawals/pending")
    @require_permission(Permission.WITHDRAWAL_APPROVE)
    async def get_pending_withdrawals(
        admin: AdminUser = Depends(get_current_admin)
    ):
        """Get pending withdrawals"""
        # Implementation here
        return {"withdrawals": [], "total": 0}
    
    @app.post("/admin/withdrawals/{withdrawal_id}/approve")
    @require_permission(Permission.WITHDRAWAL_APPROVE)
    async def approve_withdrawal(
        withdrawal_id: str,
        action: AdminAction,
        admin: AdminUser = Depends(get_current_admin)
    ):
        """Approve withdrawal"""
        await AuditLogger.log_action(
            admin=admin,
            action=ActionType.APPROVE,
            resource_type="withdrawal",
            resource_id=withdrawal_id,
            details=action.dict(),
            ip_address="0.0.0.0"
        )
        return AdminResponse(success=True, message=f"Withdrawal {withdrawal_id} approved")
    
    @app.post("/admin/withdrawals/{withdrawal_id}/reject")
    @require_permission(Permission.WITHDRAWAL_REJECT)
    async def reject_withdrawal(
        withdrawal_id: str,
        action: AdminAction,
        admin: AdminUser = Depends(get_current_admin)
    ):
        """Reject withdrawal"""
        await AuditLogger.log_action(
            admin=admin,
            action=ActionType.REJECT,
            resource_type="withdrawal",
            resource_id=withdrawal_id,
            details=action.dict(),
            ip_address="0.0.0.0"
        )
        return AdminResponse(success=True, message=f"Withdrawal {withdrawal_id} rejected")
    
    # ========================================================================
    # TRADING CONTROL ENDPOINTS
    # ========================================================================
    
    @app.post("/admin/trading/halt")
    @require_permission(Permission.TRADING_HALT)
    async def halt_trading(
        action: AdminAction,
        admin: AdminUser = Depends(get_current_admin)
    ):
        """Halt trading"""
        await AuditLogger.log_action(
            admin=admin,
            action=ActionType.UPDATE,
            resource_type="trading",
            resource_id="global",
            details={"action": "halt", "reason": action.reason},
            ip_address="0.0.0.0"
        )
        return AdminResponse(success=True, message="Trading halted")
    
    @app.post("/admin/trading/resume")
    @require_permission(Permission.TRADING_RESUME)
    async def resume_trading(
        admin: AdminUser = Depends(get_current_admin)
    ):
        """Resume trading"""
        await AuditLogger.log_action(
            admin=admin,
            action=ActionType.UPDATE,
            resource_type="trading",
            resource_id="global",
            details={"action": "resume"},
            ip_address="0.0.0.0"
        )
        return AdminResponse(success=True, message="Trading resumed")
    
    # ========================================================================
    # SYSTEM CONFIGURATION ENDPOINTS
    # ========================================================================
    
    @app.get("/admin/config")
    @require_permission(Permission.SYSTEM_CONFIG)
    async def get_config(
        admin: AdminUser = Depends(get_current_admin)
    ):
        """Get system configuration"""
        return {"config": {}, "version": VERSION}
    
    @app.put("/admin/config")
    @require_permission(Permission.SYSTEM_CONFIG)
    async def update_config(
        config: Dict[str, Any],
        admin: AdminUser = Depends(get_current_admin)
    ):
        """Update system configuration"""
        await AuditLogger.log_action(
            admin=admin,
            action=ActionType.CONFIG,
            resource_type="system",
            resource_id="config",
            details=config,
            ip_address="0.0.0.0"
        )
        return AdminResponse(success=True, message="Configuration updated")
    
    # ========================================================================
    # ANALYTICS & REPORTING ENDPOINTS
    # ========================================================================
    
    @app.get("/admin/analytics/dashboard")
    @require_permission(Permission.ANALYTICS_VIEW)
    async def get_dashboard(
        admin: AdminUser = Depends(get_current_admin)
    ):
        """Get admin dashboard analytics"""
        return {
            "total_users": 0,
            "active_users": 0,
            "total_volume": 0,
            "pending_withdrawals": 0,
            "pending_kyc": 0
        }
    
    @app.get("/admin/audit-logs")
    @require_permission(Permission.AUDIT_LOG_VIEW)
    async def get_audit_logs(
        admin: AdminUser = Depends(get_current_admin),
        page: int = 1,
        limit: int = 50
    ):
        """Get audit logs"""
        return {"logs": [], "total": 0, "page": page, "limit": limit}
    
    return app

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example: Create a service with admin controls
    app = FastAPI(title="TigerEx Service with Admin Controls", version=VERSION)
    create_admin_router(app, "example-service")
    
    print(f"Admin Control Template v{VERSION} loaded successfully")
    print(f"Total Permissions: {len(Permission)}")
    print(f"Total Roles: {len(UserRole)}")