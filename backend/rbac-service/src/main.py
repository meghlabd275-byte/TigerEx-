"""
TigerEx Role-Based Access Control (RBAC) Service
Complete implementation with all roles, permissions, and admin control
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from dataclasses import dataclass, field
from functools import wraps

import asyncpg
import redis.asyncio as aioredis
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import jwt

# @file main.py
# @description TigerEx src service
# @author TigerEx Development Team
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="TigerEx RBAC Service",
    description="Role-Based Access Control Service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/tigerex")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "tigerex-secret-key")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24

config = Config()
security = HTTPBearer()


class UserRole(str, Enum):
    """User roles with hierarchical permissions"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    COMPLIANCE_OFFICER = "compliance_officer"
    RISK_MANAGER = "risk_manager"
    TECHNICAL_ADMIN = "technical_admin"
    SUPPORT_MANAGER = "support_manager"
    SUPPORT_AGENT = "support_agent"
    LISTING_MANAGER = "listing_manager"
    PARTNER = "partner"
    WHITE_LABEL_CLIENT = "white_label_client"
    INSTITUTIONAL_CLIENT = "institutional_client"
    MARKET_MAKER = "market_maker"
    LIQUIDITY_PROVIDER = "liquidity_provider"
    AFFILIATE = "affiliate"
    TRADER_PRO = "trader_pro"
    TRADER = "trader"
    USER = "user"


class Permission(str, Enum):
    """Granular permissions for all system operations"""
    
    # User Management
    VIEW_USERS = "view_users"
    CREATE_USERS = "create_users"
    EDIT_USERS = "edit_users"
    DELETE_USERS = "delete_users"
    SUSPEND_USERS = "suspend_users"
    BAN_USERS = "ban_users"
    VIEW_USER_DETAILS = "view_user_details"
    MODIFY_USER_BALANCE = "modify_user_balance"
    RESET_USER_PASSWORD = "reset_user_password"
    IMPERSONATE_USER = "impersonate_user"
    
    # KYC Management
    VIEW_KYC = "view_kyc"
    APPROVE_KYC = "approve_kyc"
    REJECT_KYC = "reject_kyc"
    REQUEST_KYC_INFO = "request_kyc_info"
    
    # Trading Control
    VIEW_TRADING = "view_trading"
    CONTROL_TRADING = "control_trading"
    PAIR_MANAGEMENT = "pair_management"
    PAUSE_TRADING = "pause_trading"
    RESUME_TRADING = "resume_trading"
    HALT_ALL_TRADING = "halt_all_trading"
    MODIFY_FEES = "modify_fees"
    SET_LEVERAGE = "set_leverage"
    ADJUST_SPREADS = "adjust_spreads"
    SET_TRADING_LIMITS = "set_trading_limits"
    
    # Order Management
    VIEW_ORDERS = "view_orders"
    CANCEL_ORDERS = "cancel_orders"
    MODIFY_ORDERS = "modify_orders"
    BATCH_CANCEL_ORDERS = "batch_cancel_orders"
    
    # Position Management
    VIEW_POSITIONS = "view_positions"
    CLOSE_POSITIONS = "close_positions"
    FORCE_CLOSE_POSITIONS = "force_close_positions"
    ADJUST_MARGIN = "adjust_margin"
    
    # Financial Control
    VIEW_FINANCIALS = "view_financials"
    PROCESS_WITHDRAWALS = "process_withdrawals"
    APPROVE_WITHDRAWALS = "approve_withdrawals"
    REJECT_WITHDRAWALS = "reject_withdrawals"
    PROCESS_DEPOSITS = "process_deposits"
    MANAGE_FUNDS = "manage_funds"
    VIEW_REVENUE = "view_revenue"
    SETTLE_FUNDS = "settle_funds"
    MANAGE_FEE_STRUCTURE = "manage_fee_structure"
    
    # Wallet Management
    VIEW_WALLETS = "view_wallets"
    MANAGE_WALLETS = "manage_wallets"
    GENERATE_ADDRESSES = "generate_addresses"
    COLD_WALLET_ACCESS = "cold_wallet_access"
    HOT_WALLET_ACCESS = "hot_wallet_access"
    
    # System Control
    SYSTEM_CONFIG = "system_config"
    API_MANAGEMENT = "api_management"
    DATABASE_ACCESS = "database_access"
    SERVER_MANAGEMENT = "server_management"
    BACKUP_RESTORE = "backup_restore"
    SYSTEM_MAINTENANCE = "system_maintenance"
    CACHE_MANAGEMENT = "cache_management"
    
    # Security
    VIEW_SECURITY = "view_security"
    MANAGE_SECURITY = "manage_security"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    EXPORT_AUDIT_LOGS = "export_audit_logs"
    MANAGE_API_KEYS = "manage_api_keys"
    IP_WHITELIST = "ip_whitelist"
    SECURITY_ALERTS = "security_alerts"
    
    # Monitoring
    VIEW_LOGS = "view_logs"
    MONITOR_PERFORMANCE = "monitor_performance"
    ANALYTICS_ACCESS = "analytics_access"
    REPORT_GENERATION = "report_generation"
    REAL_TIME_MONITORING = "real_time_monitoring"
    
    # Compliance
    COMPLIANCE_MONITORING = "compliance_monitoring"
    AML_CHECKS = "aml_checks"
    REGULATORY_REPORTING = "regulatory_reporting"
    SUSPICIOUS_ACTIVITY_REPORTS = "suspicious_activity_reports"
    SANCTIONS_SCREENING = "sanctions_screening"
    
    # Business Operations
    WHITE_LABEL_MANAGEMENT = "white_label_management"
    INSTITUTIONAL_SERVICES = "institutional_services"
    PARTNER_MANAGEMENT = "partner_management"
    AFFILIATE_MANAGEMENT = "affiliate_management"
    LIQUIDITY_MANAGEMENT = "liquidity_management"
    
    # Market Operations
    LIST_TOKENS = "list_tokens"
    DELIST_TOKENS = "delist_tokens"
    MARKET_MAKING = "market_making"
    PRICE_ORACLE_MANAGEMENT = "price_oracle_management"
    
    # NFT Operations
    NFT_MANAGEMENT = "nft_management"
    NFT_MINTING = "nft_minting"
    NFT_MARKETPLACE_CONTROL = "nft_marketplace_control"
    
    # Communication
    SEND_ANNOUNCEMENTS = "send_announcements"
    MANAGE_NOTIFICATIONS = "manage_notifications"
    EMAIL_TEMPLATES = "email_templates"
    
    # Support
    VIEW_SUPPORT_TICKETS = "view_support_tickets"
    RESPOND_TICKETS = "respond_tickets"
    CLOSE_TICKETS = "close_tickets"
    ESCALATE_TICKETS = "escalate_tickets"


# Role-Permission Mapping
ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
    UserRole.SUPER_ADMIN: set(Permission),  # All permissions
    
    UserRole.ADMIN: {
        # User Management
        Permission.VIEW_USERS, Permission.CREATE_USERS, Permission.EDIT_USERS,
        Permission.SUSPEND_USERS, Permission.VIEW_USER_DETAILS, Permission.RESET_USER_PASSWORD,
        
        # KYC
        Permission.VIEW_KYC, Permission.APPROVE_KYC, Permission.REJECT_KYC,
        
        # Trading
        Permission.VIEW_TRADING, Permission.CONTROL_TRADING, Permission.PAIR_MANAGEMENT,
        Permission.PAUSE_TRADING, Permission.RESUME_TRADING, Permission.MODIFY_FEES,
        Permission.SET_LEVERAGE, Permission.SET_TRADING_LIMITS,
        
        # Orders & Positions
        Permission.VIEW_ORDERS, Permission.CANCEL_ORDERS, Permission.VIEW_POSITIONS,
        Permission.CLOSE_POSITIONS,
        
        # Financial
        Permission.VIEW_FINANCIALS, Permission.PROCESS_WITHDRAWALS, Permission.APPROVE_WITHDRAWALS,
        Permission.REJECT_WITHDRAWALS, Permission.PROCESS_DEPOSITS, Permission.VIEW_REVENUE,
        
        # Wallet
        Permission.VIEW_WALLETS, Permission.MANAGE_WALLETS,
        
        # System
        Permission.SYSTEM_CONFIG, Permission.API_MANAGEMENT, Permission.BACKUP_RESTORE,
        
        # Security
        Permission.VIEW_SECURITY, Permission.VIEW_AUDIT_LOGS, Permission.MANAGE_API_KEYS,
        
        # Monitoring
        Permission.VIEW_LOGS, Permission.MONITOR_PERFORMANCE, Permission.ANALYTICS_ACCESS,
        Permission.REPORT_GENERATION, Permission.REAL_TIME_MONITORING,
        
        # Communication
        Permission.SEND_ANNOUNCEMENTS, Permission.MANAGE_NOTIFICATIONS,
        
        # Support
        Permission.VIEW_SUPPORT_TICKETS, Permission.RESPOND_TICKETS, Permission.CLOSE_TICKETS,
    },
    
    UserRole.COMPLIANCE_OFFICER: {
        Permission.VIEW_USERS, Permission.VIEW_USER_DETAILS,
        Permission.VIEW_KYC, Permission.APPROVE_KYC, Permission.REJECT_KYC,
        Permission.VIEW_TRADING, Permission.VIEW_ORDERS, Permission.VIEW_POSITIONS,
        Permission.VIEW_FINANCIALS, Permission.VIEW_WALLETS,
        Permission.COMPLIANCE_MONITORING, Permission.AML_CHECKS,
        Permission.REGULATORY_REPORTING, Permission.SUSPICIOUS_ACTIVITY_REPORTS,
        Permission.SANCTIONS_SCREENING, Permission.VIEW_AUDIT_LOGS,
        Permission.EXPORT_AUDIT_LOGS, Permission.REPORT_GENERATION,
    },
    
    UserRole.RISK_MANAGER: {
        Permission.VIEW_TRADING, Permission.VIEW_ORDERS, Permission.VIEW_POSITIONS,
        Permission.VIEW_FINANCIALS, Permission.FORCE_CLOSE_POSITIONS,
        Permission.HALT_ALL_TRADING, Permission.SET_TRADING_LIMITS,
        Permission.ADJUST_MARGIN, Permission.VIEW_LOGS, Permission.MONITOR_PERFORMANCE,
        Permission.REAL_TIME_MONITORING, Permission.SECURITY_ALERTS,
    },
    
    UserRole.TECHNICAL_ADMIN: {
        Permission.SYSTEM_CONFIG, Permission.API_MANAGEMENT, Permission.DATABASE_ACCESS,
        Permission.SERVER_MANAGEMENT, Permission.BACKUP_RESTORE, Permission.SYSTEM_MAINTENANCE,
        Permission.CACHE_MANAGEMENT, Permission.VIEW_LOGS, Permission.MONITOR_PERFORMANCE,
        Permission.MANAGE_API_KEYS, Permission.IP_WHITELIST,
    },
    
    UserRole.SUPPORT_MANAGER: {
        Permission.VIEW_USERS, Permission.VIEW_USER_DETAILS, Permission.RESET_USER_PASSWORD,
        Permission.VIEW_SUPPORT_TICKETS, Permission.RESPOND_TICKETS, Permission.CLOSE_TICKETS,
        Permission.ESCALATE_TICKETS, Permission.SEND_ANNOUNCEMENTS,
    },
    
    UserRole.SUPPORT_AGENT: {
        Permission.VIEW_USERS, Permission.VIEW_USER_DETAILS,
        Permission.VIEW_SUPPORT_TICKETS, Permission.RESPOND_TICKETS,
    },
    
    UserRole.LISTING_MANAGER: {
        Permission.VIEW_TRADING, Permission.PAIR_MANAGEMENT,
        Permission.LIST_TOKENS, Permission.DELIST_TOKENS,
        Permission.VIEW_FINANCIALS,
    },
    
    UserRole.PARTNER: {
        Permission.VIEW_USERS, Permission.VIEW_TRADING, Permission.VIEW_FINANCIALS,
        Permission.AFFILIATE_MANAGEMENT, Permission.REPORT_GENERATION,
    },
    
    UserRole.WHITE_LABEL_CLIENT: {
        Permission.VIEW_USERS, Permission.VIEW_TRADING, Permission.VIEW_FINANCIALS,
        Permission.WHITE_LABEL_MANAGEMENT, Permission.MODIFY_FEES,
        Permission.REPORT_GENERATION,
    },
    
    UserRole.INSTITUTIONAL_CLIENT: {
        Permission.VIEW_TRADING, Permission.VIEW_ORDERS, Permission.VIEW_POSITIONS,
        Permission.VIEW_FINANCIALS, Permission.INSTITUTIONAL_SERVICES,
        Permission.VIEW_WALLETS, Permission.REPORT_GENERATION,
    },
    
    UserRole.MARKET_MAKER: {
        Permission.VIEW_TRADING, Permission.VIEW_ORDERS, Permission.VIEW_POSITIONS,
        Permission.MARKET_MAKING, Permission.ADJUST_SPREADS,
    },
    
    UserRole.LIQUIDITY_PROVIDER: {
        Permission.VIEW_TRADING, Permission.LIQUIDITY_MANAGEMENT,
        Permission.VIEW_FINANCIALS,
    },
    
    UserRole.AFFILIATE: {
        Permission.VIEW_USERS, Permission.AFFILIATE_MANAGEMENT,
        Permission.REPORT_GENERATION,
    },
    
    UserRole.TRADER_PRO: {
        Permission.VIEW_TRADING, Permission.VIEW_ORDERS, Permission.VIEW_POSITIONS,
        Permission.VIEW_FINANCIALS, Permission.VIEW_WALLETS,
        Permission.ANALYTICS_ACCESS, Permission.REPORT_GENERATION,
    },
    
    UserRole.TRADER: {
        Permission.VIEW_TRADING, Permission.VIEW_ORDERS, Permission.VIEW_POSITIONS,
        Permission.VIEW_FINANCIALS, Permission.VIEW_WALLETS,
    },
    
    UserRole.USER: {
        Permission.VIEW_TRADING, Permission.VIEW_ORDERS, Permission.VIEW_POSITIONS,
        Permission.VIEW_FINANCIALS, Permission.VIEW_WALLETS,
    },
}


@dataclass
class User:
    """User model with RBAC"""
    user_id: str
    email: str
    username: str
    role: UserRole
    permissions: Set[Permission] = field(default_factory=set)
    is_active: bool = True
    is_verified: bool = False
    kyc_level: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has a specific permission"""
        return permission in self.permissions or permission in ROLE_PERMISSIONS.get(self.role, set())
    
    def has_any_permission(self, permissions: List[Permission]) -> bool:
        """Check if user has any of the specified permissions"""
        return any(self.has_permission(p) for p in permissions)
    
    def has_all_permissions(self, permissions: List[Permission]) -> bool:
        """Check if user has all of the specified permissions"""
        return all(self.has_permission(p) for p in permissions)


class RBACManager:
    """Role-Based Access Control Manager"""
    
    def __init__(self):
        self.redis_client = None
        self.db_pool = None
    
    async def initialize(self):
        """Initialize connections"""
        try:
            self.redis_client = await aioredis.from_url(
                config.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Redis connected for RBAC")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
        
        try:
            self.db_pool = await asyncpg.create_pool(config.DATABASE_URL)
            logger.info("Database pool created for RBAC")
        except Exception as e:
            logger.warning(f"Database connection failed: {e}")
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        # Try cache first
        if self.redis_client:
            cached = await self.redis_client.get(f"user:{user_id}")
            if cached:
                data = json.loads(cached)
                return User(**data)
        
        # Query database
        if self.db_pool:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM users WHERE user_id = $1", user_id
                )
                if row:
                    user = User(
                        user_id=row['user_id'],
                        email=row['email'],
                        username=row['username'],
                        role=UserRole(row['role']),
                        permissions=set(row.get('permissions', [])),
                        is_active=row['is_active'],
                        is_verified=row['is_verified'],
                        kyc_level=row['kyc_level'],
                        created_at=row['created_at'],
                        last_login=row['last_login'],
                    )
                    # Cache user
                    if self.redis_client:
                        await self.redis_client.setex(
                            f"user:{user_id}",
                            3600,
                            json.dumps(user.__dict__, default=str)
                        )
                    return user
        
        return None
    
    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create new user"""
        user = User(
            user_id=f"USER_{datetime.utcnow().timestamp()}_{hash(user_data['email']) % 10000}",
            email=user_data['email'],
            username=user_data['username'],
            role=UserRole(user_data.get('role', 'user')),
            permissions=set(),
            is_active=True,
            is_verified=False,
            kyc_level=0,
        )
        
        if self.db_pool:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO users (user_id, email, username, role, is_active, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    user.user_id, user.email, user.username, user.role.value,
                    user.is_active, user.created_at
                )
        
        return user
    
    async def update_user_role(self, user_id: str, new_role: UserRole) -> bool:
        """Update user role"""
        if self.db_pool:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE users SET role = $1 WHERE user_id = $2",
                    new_role.value, user_id
                )
        
        # Invalidate cache
        if self.redis_client:
            await self.redis_client.delete(f"user:{user_id}")
        
        return True
    
    async def add_permission(self, user_id: str, permission: Permission) -> bool:
        """Add permission to user"""
        user = await self.get_user(user_id)
        if not user:
            return False
        
        user.permissions.add(permission)
        
        if self.db_pool:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE users SET permissions = $1 WHERE user_id = $2",
                    list(user.permissions), user_id
                )
        
        # Invalidate cache
        if self.redis_client:
            await self.redis_client.delete(f"user:{user_id}")
        
        return True
    
    async def remove_permission(self, user_id: str, permission: Permission) -> bool:
        """Remove permission from user"""
        user = await self.get_user(user_id)
        if not user:
            return False
        
        user.permissions.discard(permission)
        
        if self.db_pool:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE users SET permissions = $1 WHERE user_id = $2",
                    list(user.permissions), user_id
                )
        
        # Invalidate cache
        if self.redis_client:
            await self.redis_client.delete(f"user:{user_id}")
        
        return True
    
    async def check_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has permission"""
        user = await self.get_user(user_id)
        if not user or not user.is_active:
            return False
        
        return user.has_permission(permission)
    
    async def get_role_permissions(self, role: UserRole) -> List[str]:
        """Get all permissions for a role"""
        permissions = ROLE_PERMISSIONS.get(role, set())
        return [p.value for p in permissions]


# Global RBAC Manager
rbac_manager = RBACManager()


# Dependency for checking permissions
def require_permission(permission: Permission):
    """Decorator to check permission"""
    async def dependency(
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        token = credentials.credentials
        
        try:
            payload = jwt.decode(
                token,
                config.JWT_SECRET_KEY,
                algorithms=[config.JWT_ALGORITHM]
            )
            user_id = payload.get("user_id")
            
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            has_permission = await rbac_manager.check_permission(user_id, permission)
            
            if not has_permission:
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: {permission.value}"
                )
            
            # Add user to request state
            request.state.user_id = user_id
            request.state.user = await rbac_manager.get_user(user_id)
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    return dependency


def require_role(role: UserRole):
    """Decorator to check role"""
    async def dependency(
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        token = credentials.credentials
        
        try:
            payload = jwt.decode(
                token,
                config.JWT_SECRET_KEY,
                algorithms=[config.JWT_ALGORITHM]
            )
            user_id = payload.get("user_id")
            user_role = payload.get("role")
            
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            # Check if user has required role or higher
            role_hierarchy = {
                UserRole.SUPER_ADMIN: 100,
                UserRole.ADMIN: 90,
                UserRole.COMPLIANCE_OFFICER: 80,
                UserRole.RISK_MANAGER: 75,
                UserRole.TECHNICAL_ADMIN: 70,
                UserRole.SUPPORT_MANAGER: 60,
                UserRole.SUPPORT_AGENT: 50,
                UserRole.LISTING_MANAGER: 50,
                UserRole.PARTNER: 40,
                UserRole.WHITE_LABEL_CLIENT: 40,
                UserRole.INSTITUTIONAL_CLIENT: 40,
                UserRole.MARKET_MAKER: 30,
                UserRole.LIQUIDITY_PROVIDER: 30,
                UserRole.AFFILIATE: 20,
                UserRole.TRADER_PRO: 15,
                UserRole.TRADER: 10,
                UserRole.USER: 1,
            }
            
            user_role_enum = UserRole(user_role) if user_role else UserRole.USER
            required_level = role_hierarchy.get(role, 0)
            user_level = role_hierarchy.get(user_role_enum, 0)
            
            if user_level < required_level:
                raise HTTPException(
                    status_code=403,
                    detail=f"Role {role.value} required"
                )
            
            request.state.user_id = user_id
            request.state.user = await rbac_manager.get_user(user_id)
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    return dependency


@app.on_event("startup")
async def startup_event():
    await rbac_manager.initialize()


# API Endpoints

@app.get("/api/v1/rbac/roles")
async def get_all_roles():
    """Get all available roles"""
    return {
        "roles": [
            {
                "name": role.value,
                "permissions": await rbac_manager.get_role_permissions(role)
            }
            for role in UserRole
        ]
    }


@app.get("/api/v1/rbac/permissions")
async def get_all_permissions():
    """Get all available permissions"""
    return {
        "permissions": [p.value for p in Permission]
    }


@app.get("/api/v1/rbac/user/{user_id}/permissions")
async def get_user_permissions(
    user_id: str,
    current_user: dict = Depends(require_permission(Permission.VIEW_USERS))
):
    """Get user permissions"""
    user = await rbac_manager.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    all_permissions = ROLE_PERMISSIONS.get(user.role, set()) | user.permissions
    
    return {
        "user_id": user_id,
        "role": user.role.value,
        "permissions": [p.value for p in all_permissions]
    }


@app.post("/api/v1/rbac/user/{user_id}/role")
async def update_user_role(
    user_id: str,
    role: str,
    current_user: dict = Depends(require_permission(Permission.EDIT_USERS))
):
    """Update user role"""
    try:
        new_role = UserRole(role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    success = await rbac_manager.update_user_role(user_id, new_role)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update role")
    
    return {"success": True, "message": f"Role updated to {role}"}


@app.post("/api/v1/rbac/user/{user_id}/permission")
async def add_user_permission(
    user_id: str,
    permission: str,
    current_user: dict = Depends(require_permission(Permission.EDIT_USERS))
):
    """Add permission to user"""
    try:
        perm = Permission(permission)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid permission")
    
    success = await rbac_manager.add_permission(user_id, perm)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add permission")
    
    return {"success": True, "message": f"Permission {permission} added"}


@app.delete("/api/v1/rbac/user/{user_id}/permission")
async def remove_user_permission(
    user_id: str,
    permission: str,
    current_user: dict = Depends(require_permission(Permission.EDIT_USERS))
):
    """Remove permission from user"""
    try:
        perm = Permission(permission)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid permission")
    
    success = await rbac_manager.remove_permission(user_id, perm)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to remove permission")
    
    return {"success": True, "message": f"Permission {permission} removed"}


@app.get("/api/v1/rbac/check")
async def check_user_permission(
    user_id: str,
    permission: str,
    current_user: dict = Depends(require_permission(Permission.VIEW_USERS))
):
    """Check if user has specific permission"""
    try:
        perm = Permission(permission)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid permission")
    
    has_permission = await rbac_manager.check_permission(user_id, perm)
    
    return {
        "user_id": user_id,
        "permission": permission,
        "has_permission": has_permission
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "rbac-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)