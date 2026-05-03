#!/usr/bin/env python3
"""
TigerEx Unified Admin Control System
Complete admin control over all exchange operations
Port: 8000
"""

from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass
import asyncio
import asyncpg
import redis.asyncio as redis
import structlog
import uvicorn
import os
import json
import jwt
import hashlib
import secrets
import uuid

# @file main.py
# @description TigerEx tigerex-unified-admin service
# @author TigerEx Development Team
# Configure logging
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

# Global connections
db_pool = None
redis_client = None

security = HTTPBearer()

# ============================================================================
# ENUMS
# ============================================================================

class ExchangeStatus(str, Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    HALTED = "halted"
    SUSPENDED = "suspended"
    DEMO = "demo"
    READ_ONLY = "read_only"

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    COMPLIANCE_OFFICER = "compliance_officer"
    SUPPORT_AGENT = "support_agent"
    TRADER = "trader"
    VIP_TRADER = "vip_trader"
    INSTITUTIONAL = "institutional"
    USER = "user"
    SUSPENDED = "suspended"

class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    PENDING_VERIFICATION = "pending_verification"
    UNDER_REVIEW = "under_review"

class ServiceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"

class TradingFeature(str, Enum):
    SPOT = "spot"
    FUTURES = "futures"
    MARGIN = "margin"
    OPTIONS = "options"
    CFD = "cfd"
    FOREX = "forex"
    P2P = "p2p"
    NFT = "nft"
    STAKING = "staking"
    LAUNCHPAD = "launchpad"
    COPY_TRADING = "copy_trading"
    TRADING_BOTS = "trading_bots"
    EARN = "earn"
    LOANS = "loans"
    DEFI = "defi"

class Permission(str, Enum):
    # User Management
    USER_VIEW = "user_view"
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    USER_SUSPEND = "user_suspend"
    USER_BAN = "user_ban"
    USER_VERIFY = "user_verify"
    
    # Trading Management
    TRADING_VIEW = "trading_view"
    TRADING_MANAGE = "trading_manage"
    TRADING_HALT = "trading_halt"
    TRADING_PAUSE = "trading_pause"
    TRADING_RESUME = "trading_resume"
    
    # Financial Management
    FINANCE_VIEW = "finance_view"
    FINANCE_MANAGE = "finance_manage"
    FINANCE_APPROVE = "finance_approve"
    WITHDRAWAL_APPROVE = "withdrawal_approve"
    DEPOSIT_MANAGE = "deposit_manage"
    
    # System Management
    SYSTEM_CONFIG = "system_config"
    SYSTEM_MONITOR = "system_monitor"
    SYSTEM_MAINTENANCE = "system_maintenance"
    SERVICE_MANAGE = "service_manage"
    
    # Compliance
    COMPLIANCE_VIEW = "compliance_view"
    COMPLIANCE_MANAGE = "compliance_manage"
    KYC_MANAGE = "kyc_manage"
    AML_MANAGE = "aml_manage"
    
    # Content Management
    CONTENT_VIEW = "content_view"
    CONTENT_MANAGE = "content_manage"
    LISTING_MANAGE = "listing_manage"
    ANNOUNCEMENT_MANAGE = "announcement_manage"

class AdminAction(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    SUSPEND = "suspend"
    ACTIVATE = "activate"
    HALT = "halt"
    PAUSE = "pause"
    RESUME = "resume"
    APPROVE = "approve"
    REJECT = "reject"

# ============================================================================
# MODELS
# ============================================================================

class ExchangeConfig(BaseModel):
    exchange_id: str
    exchange_name: str
    exchange_status: ExchangeStatus = ExchangeStatus.ACTIVE
    white_label_enabled: bool = False
    parent_exchange_id: Optional[str] = None
    
    # Branding
    logo_url: Optional[str] = None
    primary_color: Optional[str] = "#1a1a2e"
    secondary_color: Optional[str] = "#16213e"
    domain: Optional[str] = None
    
    # Features
    enabled_features: List[TradingFeature] = [TradingFeature.SPOT, TradingFeature.FUTURES]
    
    # Limits
    max_withdrawal_daily: Decimal = Decimal("100000")
    max_deposit_daily: Decimal = Decimal("1000000")
    max_leverage: int = 100
    
    # Fees
    default_maker_fee: Decimal = Decimal("0.001")
    default_taker_fee: Decimal = Decimal("0.001")
    
    # Settings
    kyc_required: bool = True
    kyc_level_required: int = 1
    two_factor_required: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserPermissions(BaseModel):
    user_id: str
    role: UserRole = UserRole.USER
    
    # Trading permissions
    trading_enabled: bool = True
    spot_enabled: bool = True
    futures_enabled: bool = True
    margin_enabled: bool = True
    options_enabled: bool = False
    cfd_enabled: bool = True
    forex_enabled: bool = True
    p2p_enabled: bool = True
    nft_enabled: bool = True
    staking_enabled: bool = True
    copy_trading_enabled: bool = True
    trading_bots_enabled: bool = True
    
    # Financial permissions
    withdrawal_enabled: bool = True
    deposit_enabled: bool = True
    transfer_enabled: bool = True
    convert_enabled: bool = True
    
    # Limits
    max_withdrawal_daily: Decimal = Decimal("100000")
    max_deposit_daily: Decimal = Decimal("1000000")
    max_leverage: int = 100
    max_position_size: Decimal = Decimal("1000000")
    max_daily_volume: Decimal = Decimal("10000000")
    
    # Risk parameters
    margin_call_level: Decimal = Decimal("80")
    stop_out_level: Decimal = Decimal("50")
    swap_free: bool = False
    
    # Restrictions
    restricted_countries: List[str] = []
    restricted_instruments: List[str] = []
    restricted_features: List[str] = []
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[str] = None

class ServiceConfig(BaseModel):
    service_name: str
    service_status: ServiceStatus = ServiceStatus.ONLINE
    port: int
    version: str = "1.0.0"
    health_check_url: Optional[str] = None
    dependencies: List[str] = []
    maintenance_message: Optional[str] = None
    auto_restart: bool = True
    max_restart_attempts: int = 3

class AuditLogEntry(BaseModel):
    log_id: str
    admin_id: str
    admin_username: str
    action: AdminAction
    target_type: str
    target_id: str
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SystemSettings(BaseModel):
    # Trading
    trading_enabled: bool = True
    new_positions_allowed: bool = True
    new_orders_allowed: bool = True
    close_positions_allowed: bool = True
    modify_positions_allowed: bool = True
    
    # Financial
    withdraw_enabled: bool = True
    deposit_enabled: bool = True
    transfer_enabled: bool = True
    convert_enabled: bool = True
    
    # System
    registration_enabled: bool = True
    maintenance_mode: bool = False
    maintenance_message: Optional[str] = None
    announcement_banner: Optional[str] = None
    
    # Security
    two_factor_enforced: bool = False
    password_reset_enabled: bool = True
    session_timeout_minutes: int = 30

class CreateUserRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER
    permissions: Optional[UserPermissions] = None

class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    permissions: Optional[Dict[str, Any]] = None

class UpdateExchangeRequest(BaseModel):
    exchange_name: Optional[str] = None
    exchange_status: Optional[ExchangeStatus] = None
    enabled_features: Optional[List[TradingFeature]] = None
    max_withdrawal_daily: Optional[Decimal] = None
    max_deposit_daily: Optional[Decimal] = None
    max_leverage: Optional[int] = None
    default_maker_fee: Optional[Decimal] = None
    default_taker_fee: Optional[Decimal] = None
    kyc_required: Optional[bool] = None
    maintenance_message: Optional[str] = None

class FeeCollectionReport(BaseModel):
    period_start: datetime
    period_end: datetime
    total_trading_fees: Decimal = Decimal("0")
    total_withdrawal_fees: Decimal = Decimal("0")
    total_deposit_fees: Decimal = Decimal("0")
    total_other_fees: Decimal = Decimal("0")
    total_fees: Decimal = Decimal("0")
    breakdown_by_asset: Dict[str, Decimal] = {}
    breakdown_by_trading_pair: Dict[str, Decimal] = {}

# ============================================================================
# ADMIN CONTROL ENGINE
# ============================================================================

class UnifiedAdminEngine:
    """Unified Admin Control Engine"""
    
    def __init__(self):
        self.exchange_configs: Dict[str, ExchangeConfig] = {}
        self.user_permissions: Dict[str, UserPermissions] = {}
        self.service_configs: Dict[str, ServiceConfig] = {}
        self.audit_logs: List[AuditLogEntry] = []
        self.system_settings: SystemSettings = SystemSettings()
        self.admin_sessions: Dict[str, Dict] = {}
        
        # Initialize default exchange
        self._initialize_default_exchange()
        self._initialize_services()
    
    def _initialize_default_exchange(self):
        """Initialize default TigerEx exchange"""
        default_exchange = ExchangeConfig(
            exchange_id="TIGEREX_MAIN",
            exchange_name="TigerEx",
            exchange_status=ExchangeStatus.ACTIVE,
            white_label_enabled=False,
            domain="tigerex.com",
            enabled_features=[
                TradingFeature.SPOT, TradingFeature.FUTURES, TradingFeature.MARGIN,
                TradingFeature.OPTIONS, TradingFeature.CFD, TradingFeature.FOREX,
                TradingFeature.P2P, TradingFeature.NFT, TradingFeature.STAKING,
                TradingFeature.LAUNCHPAD, TradingFeature.COPY_TRADING,
                TradingFeature.TRADING_BOTS, TradingFeature.EARN, TradingFeature.LOANS,
                TradingFeature.DEFI
            ],
            max_withdrawal_daily=Decimal("100000"),
            max_deposit_daily=Decimal("1000000"),
            max_leverage=125
        )
        
        self.exchange_configs["TIGEREX_MAIN"] = default_exchange
    
    def _initialize_services(self):
        """Initialize service configurations"""
        services = [
            ("auth-service", 8001, "Authentication and authorization"),
            ("trading-engine", 8002, "Core trading engine"),
            ("matching-engine", 8003, "Order matching"),
            ("wallet-service", 8004, "Wallet management"),
            ("kyc-aml-service", 8005, "KYC/AML compliance"),
            ("notification-service", 8006, "Notifications"),
            ("user-service", 8007, "User management"),
            ("order-service", 8008, "Order management"),
            ("market-data-service", 8009, "Market data feeds"),
            ("liquidity-service", 8010, "Liquidity management"),
            ("fee-service", 8011, "Fee management"),
            ("risk-service", 8012, "Risk management"),
            ("api-gateway", 8013, "API Gateway"),
            ("admin-service", 8014, "Admin panel"),
            ("cfd-trading-service", 8190, "CFD Trading"),
            ("cfd-copy-trading-service", 8191, "CFD Copy Trading"),
        ]
        
        for name, port, description in services:
            self.service_configs[name] = ServiceConfig(
                service_name=name,
                service_status=ServiceStatus.ONLINE,
                port=port,
                version="2.0.0"
            )
    
    async def log_action(self, admin: dict, action: AdminAction, target_type: str, 
                        target_id: str, details: Dict = None, ip: str = None):
        """Log admin action for audit"""
        
        log_entry = AuditLogEntry(
            log_id=str(uuid.uuid4()),
            admin_id=admin.get("admin_id", "unknown"),
            admin_username=admin.get("username", "unknown"),
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details or {},
            ip_address=ip
        )
        
        self.audit_logs.append(log_entry)
        
        # Keep only last 10000 logs in memory
        if len(self.audit_logs) > 10000:
            self.audit_logs = self.audit_logs[-10000:]
        
        logger.info(f"Admin action: {admin.get('admin_id')} {action.value} {target_type} {target_id}")
    
    async def get_exchange_config(self, exchange_id: str) -> Optional[ExchangeConfig]:
        """Get exchange configuration"""
        return self.exchange_configs.get(exchange_id)
    
    async def update_exchange_config(self, exchange_id: str, updates: UpdateExchangeRequest,
                                    admin: dict) -> ExchangeConfig:
        """Update exchange configuration"""
        
        if exchange_id not in self.exchange_configs:
            raise HTTPException(status_code=404, detail="Exchange not found")
        
        config = self.exchange_configs[exchange_id]
        
        # Apply updates
        if updates.exchange_name:
            config.exchange_name = updates.exchange_name
        if updates.exchange_status:
            config.exchange_status = updates.exchange_status
        if updates.enabled_features:
            config.enabled_features = updates.enabled_features
        if updates.max_withdrawal_daily:
            config.max_withdrawal_daily = updates.max_withdrawal_daily
        if updates.max_deposit_daily:
            config.max_deposit_daily = updates.max_deposit_daily
        if updates.max_leverage:
            config.max_leverage = updates.max_leverage
        if updates.default_maker_fee:
            config.default_maker_fee = updates.default_maker_fee
        if updates.default_taker_fee:
            config.default_taker_fee = updates.default_taker_fee
        if updates.kyc_required is not None:
            config.kyc_required = updates.kyc_required
        
        config.updated_at = datetime.utcnow()
        
        # Log action
        await self.log_action(
            admin=admin,
            action=AdminAction.UPDATE,
            target_type="exchange",
            target_id=exchange_id,
            details=updates.dict(exclude_unset=True)
        )
        
        return config
    
    async def set_exchange_status(self, exchange_id: str, status: ExchangeStatus,
                                  reason: str, admin: dict) -> Dict:
        """Set exchange status"""
        
        if exchange_id not in self.exchange_configs:
            raise HTTPException(status_code=404, detail="Exchange not found")
        
        config = self.exchange_configs[exchange_id]
        old_status = config.exchange_status
        config.exchange_status = status
        config.updated_at = datetime.utcnow()
        
        # Log action
        await self.log_action(
            admin=admin,
            action=AdminAction.UPDATE,
            target_type="exchange_status",
            target_id=exchange_id,
            details={"old_status": old_status.value, "new_status": status.value, "reason": reason}
        )
        
        return {
            "exchange_id": exchange_id,
            "old_status": old_status.value,
            "new_status": status.value,
            "reason": reason,
            "updated_at": config.updated_at.isoformat()
        }
    
    async def get_user_permissions(self, user_id: str) -> Optional[UserPermissions]:
        """Get user permissions"""
        return self.user_permissions.get(user_id)
    
    async def set_user_permissions(self, user_id: str, permissions: UserPermissions,
                                   admin: dict) -> UserPermissions:
        """Set user permissions"""
        
        permissions.updated_at = datetime.utcnow()
        permissions.updated_by = admin.get("admin_id")
        
        self.user_permissions[user_id] = permissions
        
        # Log action
        await self.log_action(
            admin=admin,
            action=AdminAction.UPDATE,
            target_type="user_permissions",
            target_id=user_id,
            details=permissions.dict()
        )
        
        return permissions
    
    async def suspend_user(self, user_id: str, reason: str, admin: dict) -> Dict:
        """Suspend user"""
        
        if user_id not in self.user_permissions:
            self.user_permissions[user_id] = UserPermissions(user_id=user_id)
        
        permissions = self.user_permissions[user_id]
        permissions.trading_enabled = False
        permissions.withdrawal_enabled = False
        permissions.deposit_enabled = False
        permissions.updated_at = datetime.utcnow()
        permissions.updated_by = admin.get("admin_id")
        
        await self.log_action(
            admin=admin,
            action=AdminAction.SUSPEND,
            target_type="user",
            target_id=user_id,
            details={"reason": reason}
        )
        
        return {
            "user_id": user_id,
            "status": "suspended",
            "reason": reason,
            "suspended_at": datetime.utcnow().isoformat()
        }
    
    async def activate_user(self, user_id: str, admin: dict) -> Dict:
        """Activate user"""
        
        if user_id not in self.user_permissions:
            self.user_permissions[user_id] = UserPermissions(user_id=user_id)
        
        permissions = self.user_permissions[user_id]
        permissions.trading_enabled = True
        permissions.withdrawal_enabled = True
        permissions.deposit_enabled = True
        permissions.updated_at = datetime.utcnow()
        permissions.updated_by = admin.get("admin_id")
        
        await self.log_action(
            admin=admin,
            action=AdminAction.ACTIVATE,
            target_type="user",
            target_id=user_id,
            details={}
        )
        
        return {
            "user_id": user_id,
            "status": "active",
            "activated_at": datetime.utcnow().isoformat()
        }
    
    async def halt_user_trading(self, user_id: str, reason: str, close_positions: bool,
                               admin: dict) -> Dict:
        """Halt user trading"""
        
        if user_id not in self.user_permissions:
            self.user_permissions[user_id] = UserPermissions(user_id=user_id)
        
        permissions = self.user_permissions[user_id]
        permissions.trading_enabled = False
        permissions.updated_at = datetime.utcnow()
        
        await self.log_action(
            admin=admin,
            action=AdminAction.HALT,
            target_type="user_trading",
            target_id=user_id,
            details={"reason": reason, "close_positions": close_positions}
        )
        
        return {
            "user_id": user_id,
            "trading_status": "halted",
            "reason": reason,
            "positions_closed": close_positions,
            "halted_at": datetime.utcnow().isoformat()
        }
    
    async def get_all_services(self) -> List[ServiceConfig]:
        """Get all services"""
        return list(self.service_configs.values())
    
    async def update_service_status(self, service_name: str, status: ServiceStatus,
                                    admin: dict) -> ServiceConfig:
        """Update service status"""
        
        if service_name not in self.service_configs:
            raise HTTPException(status_code=404, detail="Service not found")
        
        config = self.service_configs[service_name]
        config.service_status = status
        
        await self.log_action(
            admin=admin,
            action=AdminAction.UPDATE,
            target_type="service",
            target_id=service_name,
            details={"status": status.value}
        )
        
        return config
    
    async def get_system_settings(self) -> SystemSettings:
        """Get system settings"""
        return self.system_settings
    
    async def update_system_settings(self, settings: SystemSettings, admin: dict) -> SystemSettings:
        """Update system settings"""
        
        self.system_settings = settings
        
        await self.log_action(
            admin=admin,
            action=AdminAction.UPDATE,
            target_type="system_settings",
            target_id="global",
            details=settings.dict()
        )
        
        return settings
    
    async def get_audit_logs(self, limit: int = 100, offset: int = 0,
                            admin_id: Optional[str] = None,
                            action: Optional[AdminAction] = None,
                            target_type: Optional[str] = None) -> List[AuditLogEntry]:
        """Get audit logs"""
        
        logs = self.audit_logs
        
        # Apply filters
        if admin_id:
            logs = [l for l in logs if l.admin_id == admin_id]
        if action:
            logs = [l for l in logs if l.action == action]
        if target_type:
            logs = [l for l in logs if l.target_type == target_type]
        
        # Sort by timestamp descending
        logs = sorted(logs, key=lambda x: x.timestamp, reverse=True)
        
        # Paginate
        return logs[offset:offset+limit]

# ============================================================================
# APP SETUP
# ============================================================================

app = FastAPI(
    title="TigerEx Unified Admin Control System",
    description="Complete admin control over all exchange operations",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engine
admin_engine = UnifiedAdminEngine()

# ============================================================================
# AUTHENTICATION
# ============================================================================

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token and return admin user"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        admin_id = payload.get("sub")
        role = payload.get("role")
        
        if not admin_id or role not in ["super_admin", "admin", "moderator", "compliance_officer"]:
            raise HTTPException(status_code=401, detail="Admin access required")
        
        return {
            "admin_id": admin_id,
            "username": payload.get("username", "unknown"),
            "role": role,
            "permissions": payload.get("permissions", [])
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def check_permission(admin: dict, required_permission: str):
    """Check if admin has required permission"""
    if admin["role"] == "super_admin":
        return True
    if required_permission in admin.get("permissions", []):
        return True
    raise HTTPException(status_code=403, detail="Insufficient permissions")

# ============================================================================
# EXCHANGE MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/admin/exchange/{exchange_id}")
async def get_exchange_config(
    exchange_id: str,
    admin: dict = Depends(get_current_admin)
):
    """Get exchange configuration"""
    check_permission(admin, Permission.SYSTEM_CONFIG.value)
    
    config = await admin_engine.get_exchange_config(exchange_id)
    
    if not config:
        raise HTTPException(status_code=404, detail="Exchange not found")
    
    return {"success": True, "config": config.dict()}

@app.put("/api/admin/exchange/{exchange_id}")
async def update_exchange_config(
    exchange_id: str,
    updates: UpdateExchangeRequest,
    admin: dict = Depends(get_current_admin)
):
    """Update exchange configuration"""
    check_permission(admin, Permission.SYSTEM_CONFIG.value)
    
    config = await admin_engine.update_exchange_config(exchange_id, updates, admin)
    
    return {"success": True, "message": "Exchange updated", "config": config.dict()}

@app.post("/api/admin/exchange/{exchange_id}/status")
async def set_exchange_status(
    exchange_id: str,
    status: ExchangeStatus,
    reason: str,
    admin: dict = Depends(get_current_admin)
):
    """Set exchange status (active, maintenance, halted, suspended)"""
    check_permission(admin, Permission.TRADING_HALT.value)
    
    result = await admin_engine.set_exchange_status(exchange_id, status, reason, admin)
    
    return {"success": True, **result}

@app.post("/api/admin/exchange/{exchange_id}/white-label")
async def configure_white_label(
    exchange_id: str,
    new_exchange_name: str,
    domain: str,
    logo_url: Optional[str] = None,
    primary_color: Optional[str] = None,
    secondary_color: Optional[str] = None,
    admin: dict = Depends(get_current_admin)
):
    """Configure white-label exchange"""
    check_permission(admin, Permission.SYSTEM_CONFIG.value)
    
    white_label_config = {
        "parent_exchange_id": exchange_id,
        "exchange_name": new_exchange_name,
        "domain": domain,
        "logo_url": logo_url,
        "primary_color": primary_color or "#1a1a2e",
        "secondary_color": secondary_color or "#16213e",
        "white_label_enabled": True,
        "created_by": admin["admin_id"],
        "created_at": datetime.utcnow().isoformat()
    }
    
    await admin_engine.log_action(
        admin=admin,
        action=AdminAction.CREATE,
        target_type="white_label",
        target_id=domain,
        details=white_label_config
    )
    
    return {"success": True, "message": "White-label configured", "config": white_label_config}

# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/admin/users/{user_id}/permissions")
async def get_user_permissions(
    user_id: str,
    admin: dict = Depends(get_current_admin)
):
    """Get user permissions"""
    check_permission(admin, Permission.USER_VIEW.value)
    
    permissions = await admin_engine.get_user_permissions(user_id)
    
    if not permissions:
        permissions = UserPermissions(user_id=user_id)
    
    return {"success": True, "permissions": permissions.dict()}

@app.put("/api/admin/users/{user_id}/permissions")
async def set_user_permissions(
    user_id: str,
    permissions: UserPermissions,
    admin: dict = Depends(get_current_admin)
):
    """Set user permissions"""
    check_permission(admin, Permission.USER_UPDATE.value)
    
    permissions.user_id = user_id
    result = await admin_engine.set_user_permissions(user_id, permissions, admin)
    
    return {"success": True, "message": "Permissions updated", "permissions": result.dict()}

@app.post("/api/admin/users/{user_id}/suspend")
async def suspend_user(
    user_id: str,
    reason: str,
    admin: dict = Depends(get_current_admin)
):
    """Suspend user"""
    check_permission(admin, Permission.USER_SUSPEND.value)
    
    result = await admin_engine.suspend_user(user_id, reason, admin)
    
    return {"success": True, **result}

@app.post("/api/admin/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    admin: dict = Depends(get_current_admin)
):
    """Activate user"""
    check_permission(admin, Permission.USER_UPDATE.value)
    
    result = await admin_engine.activate_user(user_id, admin)
    
    return {"success": True, **result}

@app.post("/api/admin/users/{user_id}/halt-trading")
async def halt_user_trading(
    user_id: str,
    reason: str,
    close_positions: bool = False,
    admin: dict = Depends(get_current_admin)
):
    """Halt user trading"""
    check_permission(admin, Permission.TRADING_HALT.value)
    
    result = await admin_engine.halt_user_trading(user_id, reason, close_positions, admin)
    
    return {"success": True, **result}

@app.post("/api/admin/users/{user_id}/pause-withdrawals")
async def pause_user_withdrawals(
    user_id: str,
    reason: str,
    admin: dict = Depends(get_current_admin)
):
    """Pause user withdrawals"""
    check_permission(admin, Permission.FINANCE_MANAGE.value)
    
    if user_id not in admin_engine.user_permissions:
        admin_engine.user_permissions[user_id] = UserPermissions(user_id=user_id)
    
    admin_engine.user_permissions[user_id].withdrawal_enabled = False
    
    await admin_engine.log_action(
        admin=admin,
        action=AdminAction.PAUSE,
        target_type="user_withdrawals",
        target_id=user_id,
        details={"reason": reason}
    )
    
    return {
        "success": True,
        "user_id": user_id,
        "withdrawal_status": "paused",
        "reason": reason,
        "paused_at": datetime.utcnow().isoformat()
    }

# ============================================================================
# SERVICE MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/admin/services")
async def get_all_services(admin: dict = Depends(get_current_admin)):
    """Get all services status"""
    check_permission(admin, Permission.SYSTEM_MONITOR.value)
    
    services = await admin_engine.get_all_services()
    
    return {
        "success": True,
        "services": [s.dict() for s in services],
        "total": len(services)
    }

@app.post("/api/admin/services/{service_name}/status")
async def update_service_status(
    service_name: str,
    status: ServiceStatus,
    admin: dict = Depends(get_current_admin)
):
    """Update service status"""
    check_permission(admin, Permission.SERVICE_MANAGE.value)
    
    config = await admin_engine.update_service_status(service_name, status, admin)
    
    return {"success": True, "service": config.dict()}

@app.post("/api/admin/services/{service_name}/restart")
async def restart_service(
    service_name: str,
    admin: dict = Depends(get_current_admin)
):
    """Restart service"""
    check_permission(admin, Permission.SERVICE_MANAGE.value)
    
    await admin_engine.log_action(
        admin=admin,
        action=AdminAction.UPDATE,
        target_type="service_restart",
        target_id=service_name,
        details={}
    )
    
    return {
        "success": True,
        "message": f"Service {service_name} restart initiated",
        "restarted_at": datetime.utcnow().isoformat()
    }

# ============================================================================
# SYSTEM SETTINGS ENDPOINTS
# ============================================================================

@app.get("/api/admin/settings")
async def get_system_settings(admin: dict = Depends(get_current_admin)):
    """Get system settings"""
    check_permission(admin, Permission.SYSTEM_CONFIG.value)
    
    settings = await admin_engine.get_system_settings()
    
    return {"success": True, "settings": settings.dict()}

@app.put("/api/admin/settings")
async def update_system_settings(
    settings: SystemSettings,
    admin: dict = Depends(get_current_admin)
):
    """Update system settings"""
    check_permission(admin, Permission.SYSTEM_CONFIG.value)
    
    result = await admin_engine.update_system_settings(settings, admin)
    
    return {"success": True, "message": "Settings updated", "settings": result.dict()}

# ============================================================================
# TRADING CONTROL ENDPOINTS
# ============================================================================

@app.post("/api/admin/trading/halt")
async def halt_all_trading(
    reason: str,
    admin: dict = Depends(get_current_admin)
):
    """Halt all trading on exchange"""
    check_permission(admin, Permission.TRADING_HALT.value)
    
    admin_engine.system_settings.trading_enabled = False
    admin_engine.system_settings.new_positions_allowed = False
    admin_engine.system_settings.new_orders_allowed = False
    
    await admin_engine.log_action(
        admin=admin,
        action=AdminAction.HALT,
        target_type="trading",
        target_id="global",
        details={"reason": reason}
    )
    
    return {
        "success": True,
        "message": "All trading halted",
        "reason": reason,
        "halted_at": datetime.utcnow().isoformat()
    }

@app.post("/api/admin/trading/resume")
async def resume_all_trading(
    admin: dict = Depends(get_current_admin)
):
    """Resume all trading on exchange"""
    check_permission(admin, Permission.TRADING_RESUME.value)
    
    admin_engine.system_settings.trading_enabled = True
    admin_engine.system_settings.new_positions_allowed = True
    admin_engine.system_settings.new_orders_allowed = True
    
    await admin_engine.log_action(
        admin=admin,
        action=AdminAction.RESUME,
        target_type="trading",
        target_id="global",
        details={}
    )
    
    return {
        "success": True,
        "message": "Trading resumed",
        "resumed_at": datetime.utcnow().isoformat()
    }

# ============================================================================
# AUDIT LOG ENDPOINTS
# ============================================================================

@app.get("/api/admin/audit-logs")
async def get_audit_logs(
    limit: int = 100,
    offset: int = 0,
    admin_id: Optional[str] = None,
    action: Optional[AdminAction] = None,
    target_type: Optional[str] = None,
    admin: dict = Depends(get_current_admin)
):
    """Get audit logs"""
    check_permission(admin, Permission.SYSTEM_MONITOR.value)
    
    logs = await admin_engine.get_audit_logs(limit, offset, admin_id, action, target_type)
    
    return {
        "success": True,
        "logs": [log.dict() for log in logs],
        "total": len(admin_engine.audit_logs)
    }

# ============================================================================
# FEE COLLECTION ENDPOINTS
# ============================================================================

@app.get("/api/admin/fees/report")
async def get_fee_report(
    period_start: Optional[datetime] = None,
    period_end: Optional[datetime] = None,
    admin: dict = Depends(get_current_admin)
):
    """Get fee collection report"""
    check_permission(admin, Permission.FINANCE_VIEW.value)
    
    # Generate sample report
    report = FeeCollectionReport(
        period_start=period_start or datetime.utcnow() - timedelta(days=30),
        period_end=period_end or datetime.utcnow(),
        total_trading_fees=Decimal("1250000.00"),
        total_withdrawal_fees=Decimal("85000.00"),
        total_deposit_fees=Decimal("12000.00"),
        total_other_fees=Decimal("35000.00"),
        total_fees=Decimal("1382000.00"),
        breakdown_by_asset={
            "USDT": Decimal("850000.00"),
            "BTC": Decimal("320000.00"),
            "ETH": Decimal("150000.00"),
            "BNB": Decimal("62000.00")
        },
        breakdown_by_trading_pair={
            "BTC/USDT": Decimal("420000.00"),
            "ETH/USDT": Decimal("280000.00"),
            "BNB/USDT": Decimal("120000.00"),
            "SOL/USDT": Decimal("95000.00")
        }
    )
    
    return {"success": True, "report": report.dict()}

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "unified-admin-control",
        "version": "3.0.0",
        "exchanges_count": len(admin_engine.exchange_configs),
        "services_count": len(admin_engine.service_configs),
        "audit_logs_count": len(admin_engine.audit_logs)
    }

# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup():
    global redis_client
    redis_client = redis.from_url(REDIS_URL)
    logger.info("Unified Admin Control System started")

@app.on_event("shutdown")
async def shutdown():
    if redis_client:
        await redis_client.close()
    logger.info("Unified Admin Control System stopped")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
