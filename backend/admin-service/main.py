#!/usr/bin/env python3
from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

# Complete RBAC System for admin-service
class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    SUPPORT = "support"
    COMPLIANCE = "compliance"
    RISK_MANAGER = "risk_manager"
    TRADER = "trader"
    USER = "user"

class Permission(str, Enum):
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

class AdminUser(BaseModel):
    user_id: str
    username: str
    email: str
    role: UserRole
    permissions: List[Permission]
    is_active: bool = True
    created_at: datetime = None
    last_login: Optional[datetime] = None

# Role-based permission mapping
ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: [
        Permission.USER_VIEW, Permission.USER_CREATE, Permission.USER_UPDATE,
        Permission.USER_DELETE, Permission.USER_SUSPEND, Permission.USER_VERIFY,
        Permission.WITHDRAWAL_APPROVE, Permission.WITHDRAWAL_REJECT,
        Permission.DEPOSIT_MONITOR, Permission.TRANSACTION_REVIEW, Permission.FEE_MANAGE,
        Permission.TRADING_HALT, Permission.TRADING_RESUME, Permission.PAIR_MANAGE,
        Permission.LIQUIDITY_MANAGE, Permission.RISK_CONFIGURE, Permission.POSITION_MONITOR,
        Permission.LIQUIDATION_MANAGE, Permission.SYSTEM_CONFIG, Permission.FEATURE_FLAG,
        Permission.MAINTENANCE_MODE, Permission.KYC_APPROVE, Permission.KYC_REJECT,
        Permission.AML_MONITOR, Permission.COMPLIANCE_REPORT,
        Permission.ANNOUNCEMENT_CREATE, Permission.ANNOUNCEMENT_UPDATE, Permission.ANNOUNCEMENT_DELETE,
        Permission.ANALYTICS_VIEW, Permission.REPORT_GENERATE, Permission.AUDIT_LOG_VIEW
    ],
    UserRole.ADMIN: [
        Permission.USER_VIEW, Permission.USER_CREATE, Permission.USER_UPDATE,
        Permission.USER_SUSPEND, Permission.USER_VERIFY,
        Permission.WITHDRAWAL_APPROVE, Permission.WITHDRAWAL_REJECT,
        Permission.DEPOSIT_MONITOR, Permission.TRANSACTION_REVIEW, Permission.FEE_MANAGE,
        Permission.TRADING_HALT, Permission.TRADING_RESUME, Permission.PAIR_MANAGE,
        Permission.RISK_CONFIGURE, Permission.POSITION_MONITOR,
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

# RBAC Helper Functions
def get_current_admin():
    """Get current admin user (mock implementation)"""
    return AdminUser(
        user_id="admin_001",
        username="admin",
        email="admin@tigerex.com",
        role=UserRole.ADMIN,
        permissions=ROLE_PERMISSIONS[UserRole.ADMIN]
    )

def require_permission(permission: Permission):
    """Decorator to require specific permission"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            from fastapi import HTTPException, status
            admin = get_current_admin()
            if permission not in admin.permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Permission denied. Required: " + str(permission)
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(roles: List[UserRole]):
    """Decorator to require specific role(s)"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            from fastapi import HTTPException, status
            admin = get_current_admin()
            if admin.role not in roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Role denied. Required: " + str(roles)
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


"""
TigerEx admin-service Service
"""

from fastapi import FastAPI
import uvicorn
import os

app = FastAPI(
    title="TigerEx Admin Service",
    description="Administrative control panel for TigerEx Exchange",
    version="1.0.0"
)

# RBAC Helper Functions
def get_current_admin():
    """Get current admin user (mock implementation)"""
    return AdminUser(
        user_id="admin_001",
        username="admin",
        email="admin@tigerex.com",
        role=UserRole.ADMIN,
        permissions=ROLE_PERMISSIONS[UserRole.ADMIN]
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "admin-service"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
