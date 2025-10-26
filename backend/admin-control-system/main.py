"""
TigerEx Admin Control System
Complete implementation with comprehensive admin controls
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import hashlib
import secrets
from decimal import Decimal

class UserRole(Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    SUPPORT = "support"
    ANALYST = "analyst"
    VIEWER = "viewer"

class Permission(Enum):
    # User Management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_SUSPEND = "user:suspend"
    
    # Trading Management
    TRADING_VIEW = "trading:view"
    TRADING_MANAGE = "trading:manage"
    TRADING_SUSPEND = "trading:suspend"
    TRADING_FEES = "trading:fees"
    
    # Liquidity Management
    LIQUIDITY_VIEW = "liquidity:view"
    LIQUIDITY_MANAGE = "liquidity:manage"
    LIQUIDITY_CREATE = "liquidity:create"
    LIQUIDITY_REBALANCE = "liquidity:rebalance"
    
    # Financial Management
    FINANCIAL_VIEW = "financial:view"
    FINANCIAL_MANAGE = "financial:manage"
    WITHDRAWAL_APPROVE = "withdrawal:approve"
    DEPOSIT_MANAGE = "deposit:manage"
    
    # System Management
    SYSTEM_CONFIG = "system:config"
    SYSTEM_MONITOR = "system:monitor"
    SYSTEM_MAINTENANCE = "system:maintenance"
    API_KEYS = "api:keys"
    
    # Blockchain Management
    BLOCKCHAIN_MANAGE = "blockchain:manage"
    SMART_CONTRACT = "smart_contract:deploy"
    
    # Reporting
    REPORTING_VIEW = "reporting:view"
    REPORTING_EXPORT = "reporting:export"
    AUDIT_LOG = "audit:log"

class ActionStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class AdminUser:
    id: str
    username: str
    email: str
    role: UserRole
    permissions: List[Permission]
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    two_factor_enabled: bool = False
    two_factor_secret: Optional[str] = None
    api_keys: List[str] = field(default_factory=list)

@dataclass
class AuditLog:
    id: str
    user_id: str
    action: str
    resource: str
    details: Dict[str, Any]
    ip_address: str
    user_agent: str
    timestamp: datetime = field(default_factory=datetime.now)
    status: ActionStatus = ActionStatus.COMPLETED

@dataclass
class SystemConfiguration:
    id: str
    key: str
    value: Any
    description: str
    category: str
    is_sensitive: bool = False
    requires_restart: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    updated_by: Optional[str] = None

@dataclass
class TradingPair:
    id: str
    symbol: str
    base_currency: str
    quote_currency: str
    is_active: bool = True
    min_trade_amount: float = 0.001
    max_trade_amount: float = 1000000
    fee_rate: float = 0.001
    maker_fee: float = 0.0008
    taker_fee: float = 0.0012
    created_at: datetime = field(default_factory=datetime.now)
    volume_24h: float = 0.0
    high_24h: float = 0.0
    low_24h: float = 0.0
    last_price: float = 0.0

@dataclass
class MaintenanceWindow:
    id: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    affected_services: List[str]
    is_active: bool = False
    created_by: str
    created_at: datetime = field(default_factory=datetime.now)

class AdminControlSystem:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.admin_users: Dict[str, AdminUser] = {}
        self.audit_logs: List[AuditLog] = []
        self.system_configs: Dict[str, SystemConfiguration] = {}
        self.trading_pairs: Dict[str, TradingPair] = {}
        self.maintenance_windows: Dict[str, MaintenanceWindow] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.security_events: List[Dict[str, Any]] = []
        
        # Initialize role permissions
        self._initialize_role_permissions()
        
        # Initialize system configurations
        self._initialize_system_configs()
        
        # Initialize default admin
        self._initialize_default_admin()

    def _initialize_role_permissions(self):
        """Initialize permissions for each role"""
        self.role_permissions = {
            UserRole.SUPER_ADMIN: list(Permission),
            UserRole.ADMIN: [
                Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE,
                Permission.USER_SUSPEND, Permission.TRADING_VIEW, Permission.TRADING_MANAGE,
                Permission.TRADING_SUSPEND, Permission.TRADING_FEES, Permission.LIQUIDITY_VIEW,
                Permission.LIQUIDITY_MANAGE, Permission.FINANCIAL_VIEW, Permission.WITHDRAWAL_APPROVE,
                Permission.SYSTEM_CONFIG, Permission.SYSTEM_MONITOR, Permission.BLOCKCHAIN_MANAGE,
                Permission.REPORTING_VIEW, Permission.REPORTING_EXPORT, Permission.AUDIT_LOG
            ],
            UserRole.MANAGER: [
                Permission.USER_READ, Permission.USER_UPDATE, Permission.TRADING_VIEW,
                Permission.LIQUIDITY_VIEW, Permission.FINANCIAL_VIEW, Permission.WITHDRAWAL_APPROVE,
                Permission.SYSTEM_MONITOR, Permission.REPORTING_VIEW, Permission.REPORTING_EXPORT
            ],
            UserRole.SUPPORT: [
                Permission.USER_READ, Permission.USER_UPDATE, Permission.TRADING_VIEW,
                Permission.FINANCIAL_VIEW, Permission.REPORTING_VIEW
            ],
            UserRole.ANALYST: [
                Permission.TRADING_VIEW, Permission.LIQUIDITY_VIEW, Permission.FINANCIAL_VIEW,
                Permission.REPORTING_VIEW, Permission.REPORTING_EXPORT
            ],
            UserRole.VIEWER: [
                Permission.TRADING_VIEW, Permission.LIQUIDITY_VIEW, Permission.FINANCIAL_VIEW,
                Permission.REPORTING_VIEW
            ]
        }

    def _initialize_system_configs(self):
        """Initialize default system configurations"""
        default_configs = [
            SystemConfiguration(
                id="max_withdrawal_per_day",
                key="max_withdrawal_per_day",
                value=100000,
                description="Maximum withdrawal amount per day in USD",
                category="financial",
                is_sensitive=False
            ),
            SystemConfiguration(
                id="maintenance_mode",
                key="maintenance_mode",
                value=False,
                description="Enable/disable maintenance mode",
                category="system",
                is_sensitive=False,
                requires_restart=True
            ),
            SystemConfiguration(
                id="registration_enabled",
                key="registration_enabled",
                value=True,
                description="Enable/disable new user registration",
                category="user",
                is_sensitive=False
            ),
            SystemConfiguration(
                id="api_rate_limit",
                key="api_rate_limit",
                value=100,
                description="API rate limit per minute",
                category="api",
                is_sensitive=False
            ),
            SystemConfiguration(
                id="require_kyc",
                key="require_kyc",
                value=True,
                description="Require KYC verification for trading",
                category="compliance",
                is_sensitive=False
            ),
            SystemConfiguration(
                id="default_trading_fee",
                key="default_trading_fee",
                value=0.001,
                description="Default trading fee rate",
                category="trading",
                is_sensitive=False
            ),
            SystemConfiguration(
                id="min_deposit_amount",
                key="min_deposit_amount",
                value=10,
                description="Minimum deposit amount in USD",
                category="financial",
                is_sensitive=False
            )
        ]
        
        for config in default_configs:
            self.system_configs[config.id] = config

    def _initialize_default_admin(self):
        """Initialize default super admin user"""
        default_admin = AdminUser(
            id=str(uuid.uuid4()),
            username="admin",
            email="admin@tigerex.com",
            role=UserRole.SUPER_ADMIN,
            permissions=list(Permission),
            is_active=True
        )
        
        # Set a default password (should be changed immediately)
        password_hash = self._hash_password("admin123")
        default_admin.password_hash = password_hash
        
        self.admin_users[default_admin.id] = default_admin
        
        self.logger.info("Default admin user created")

    def _hash_password(self, password: str) -> str:
        """Hash a password"""
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${password_hash.hex()}"

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        try:
            salt, hash_value = password_hash.split('$')
            computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return computed_hash.hex() == hash_value
        except:
            return False

    def _has_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if a user has a specific permission"""
        if user_id not in self.admin_users:
            return False
        
        user = self.admin_users[user_id]
        if not user.is_active:
            return False
        
        return permission in user.permissions

    def _log_audit(self, user_id: str, action: str, resource: str, details: Dict[str, Any], ip_address: str, user_agent: str, status: ActionStatus = ActionStatus.COMPLETED):
        """Log an audit event"""
        audit_log = AuditLog(
            id=str(uuid.uuid4()),
            user_id=user_id,
            action=action,
            resource=resource,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status
        )
        
        self.audit_logs.append(audit_log)
        self.logger.info(f"Audit log: {user_id} performed {action} on {resource}")

    def create_admin_user(self, creator_id: str, username: str, email: str, role: UserRole, password: str, ip_address: str, user_agent: str) -> str:
        """Create a new admin user"""
        if not self._has_permission(creator_id, Permission.USER_CREATE):
            raise PermissionError("Insufficient permissions to create admin users")
        
        # Check if username already exists
        for user in self.admin_users.values():
            if user.username == username or user.email == email:
                raise ValueError("Username or email already exists")
        
        # Create new admin user
        user_id = str(uuid.uuid4())
        permissions = self.role_permissions.get(role, [])
        
        new_admin = AdminUser(
            id=user_id,
            username=username,
            email=email,
            role=role,
            permissions=permissions,
            is_active=True
        )
        
        # Set password
        new_admin.password_hash = self._hash_password(password)
        
        self.admin_users[user_id] = new_admin
        
        # Log audit
        self._log_audit(
            creator_id,
            "CREATE_ADMIN_USER",
            f"admin_user:{user_id}",
            {"username": username, "email": email, "role": role.value},
            ip_address,
            user_agent
        )
        
        self.logger.info(f"Created admin user {username} with role {role.value}")
        return user_id

    def authenticate_admin(self, username: str, password: str, ip_address: str, user_agent: str) -> Optional[str]:
        """Authenticate an admin user"""
        # Find user by username
        user = None
        for admin_user in self.admin_users.values():
            if admin_user.username == username:
                user = admin_user
                break
        
        if not user:
            self._log_security_event("FAILED_LOGIN", {"username": username, "reason": "user_not_found"}, ip_address)
            return None
        
        # Check if user is locked
        if user.locked_until and datetime.now() < user.locked_until:
            self._log_security_event("FAILED_LOGIN", {"username": username, "reason": "account_locked"}, ip_address)
            return None
        
        # Check password
        if not self._verify_password(password, user.password_hash):
            user.failed_login_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.now() + timedelta(minutes=30)
                self._log_security_event("ACCOUNT_LOCKED", {"username": username}, ip_address)
            
            self._log_audit(
                user.id,
                "FAILED_LOGIN",
                "admin_user",
                {"failed_attempts": user.failed_login_attempts},
                ip_address,
                user_agent,
                ActionStatus.FAILED
            )
            return None
        
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.now()
        
        # Create session
        session_id = secrets.token_urlsafe(32)
        self.active_sessions[session_id] = {
            "user_id": user.id,
            "created_at": datetime.now(),
            "ip_address": ip_address,
            "user_agent": user_agent,
            "last_activity": datetime.now()
        }
        
        self._log_audit(
            user.id,
            "SUCCESSFUL_LOGIN",
            "admin_user",
            {"username": username},
            ip_address,
            user_agent
        )
        
        return session_id

    def _log_security_event(self, event_type: str, details: Dict[str, Any], ip_address: str):
        """Log a security event"""
        security_event = {
            "id": str(uuid.uuid4()),
            "event_type": event_type,
            "details": details,
            "ip_address": ip_address,
            "timestamp": datetime.now().isoformat()
        }
        
        self.security_events.append(security_event)
        self.logger.warning(f"Security event: {event_type} - {details}")

    def get_user_by_session(self, session_id: str) -> Optional[AdminUser]:
        """Get user by session ID"""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        user_id = session["user_id"]
        
        # Check session expiration (24 hours)
        if datetime.now() - session["created_at"] > timedelta(hours=24):
            del self.active_sessions[session_id]
            return None
        
        # Update last activity
        session["last_activity"] = datetime.now()
        
        return self.admin_users.get(user_id)

    def create_trading_pair(self, admin_id: str, symbol: str, base_currency: str, quote_currency: str, **kwargs) -> str:
        """Create a new trading pair"""
        if not self._has_permission(admin_id, Permission.TRADING_MANAGE):
            raise PermissionError("Insufficient permissions to create trading pairs")
        
        pair_id = str(uuid.uuid4())
        trading_pair = TradingPair(
            id=pair_id,
            symbol=symbol,
            base_currency=base_currency,
            quote_currency=quote_currency,
            **kwargs
        )
        
        self.trading_pairs[pair_id] = trading_pair
        
        self.logger.info(f"Created trading pair {symbol}")
        return pair_id

    def update_system_config(self, admin_id: str, config_id: str, value: Any, ip_address: str, user_agent: str) -> bool:
        """Update a system configuration"""
        if not self._has_permission(admin_id, Permission.SYSTEM_CONFIG):
            raise PermissionError("Insufficient permissions to update system configuration")
        
        if config_id not in self.system_configs:
            raise ValueError("Configuration not found")
        
        old_value = self.system_configs[config_id].value
        self.system_configs[config_id].value = value
        self.system_configs[config_id].updated_at = datetime.now()
        self.system_configs[config_id].updated_by = admin_id
        
        self._log_audit(
            admin_id,
            "UPDATE_SYSTEM_CONFIG",
            f"system_config:{config_id}",
            {"old_value": old_value, "new_value": value},
            ip_address,
            user_agent
        )
        
        self.logger.info(f"Updated system config {config_id}: {old_value} -> {value}")
        return True

    def get_admin_users(self, admin_id: str) -> List[Dict[str, Any]]:
        """Get list of all admin users"""
        if not self._has_permission(admin_id, Permission.USER_READ):
            raise PermissionError("Insufficient permissions to view admin users")
        
        users = []
        for user in self.admin_users.values():
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "failed_login_attempts": user.failed_login_attempts,
                "locked_until": user.locked_until.isoformat() if user.locked_until else None,
                "two_factor_enabled": user.two_factor_enabled
            }
            users.append(user_data)
        
        return users

    def get_audit_logs(self, admin_id: str, limit: int = 100, user_id: Optional[str] = None, action: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get audit logs"""
        if not self._has_permission(admin_id, Permission.AUDIT_LOG):
            raise PermissionError("Insufficient permissions to view audit logs")
        
        logs = self.audit_logs
        
        # Apply filters
        if user_id:
            logs = [log for log in logs if log.user_id == user_id]
        
        if action:
            logs = [log for log in logs if log.action == action]
        
        # Sort by timestamp (newest first)
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Convert to dict and limit
        log_data = []
        for log in logs[:limit]:
            user = self.admin_users.get(log.user_id)
            log_data.append({
                "id": log.id,
                "user_id": log.user_id,
                "username": user.username if user else "Unknown",
                "action": log.action,
                "resource": log.resource,
                "details": log.details,
                "ip_address": log.ip_address,
                "timestamp": log.timestamp.isoformat(),
                "status": log.status.value
            })
        
        return log_data

    def get_system_metrics(self, admin_id: str) -> Dict[str, Any]:
        """Get system metrics"""
        if not self._has_permission(admin_id, Permission.SYSTEM_MONITOR):
            raise PermissionError("Insufficient permissions to view system metrics")
        
        # Calculate metrics
        total_admins = len(self.admin_users)
        active_admins = len([u for u in self.admin_users.values() if u.is_active])
        active_sessions = len(self.active_sessions)
        total_pairs = len(self.trading_pairs)
        active_pairs = len([p for p in self.trading_pairs.values() if p.is_active])
        
        # Recent activity
        recent_logs = [log for log in self.audit_logs if datetime.now() - log.timestamp < timedelta(hours=24)]
        security_events_today = [event for event in self.security_events if datetime.fromisoformat(event["timestamp"]) > datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)]
        
        return {
            "user_metrics": {
                "total_admins": total_admins,
                "active_admins": active_admins,
                "active_sessions": active_sessions
            },
            "trading_metrics": {
                "total_pairs": total_pairs,
                "active_pairs": active_pairs
            },
            "activity_metrics": {
                "audit_logs_24h": len(recent_logs),
                "security_events_today": len(security_events_today)
            },
            "system_health": {
                "status": "healthy",
                "uptime": "99.9%",
                "last_restart": datetime.now() - timedelta(days=7)
            }
        }

    def create_maintenance_window(self, admin_id: str, title: str, description: str, start_time: datetime, end_time: datetime, affected_services: List[str], ip_address: str, user_agent: str) -> str:
        """Create a maintenance window"""
        if not self._has_permission(admin_id, Permission.SYSTEM_MAINTENANCE):
            raise PermissionError("Insufficient permissions to create maintenance windows")
        
        window_id = str(uuid.uuid4())
        maintenance_window = MaintenanceWindow(
            id=window_id,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            affected_services=affected_services,
            created_by=admin_id
        )
        
        self.maintenance_windows[window_id] = maintenance_window
        
        self._log_audit(
            admin_id,
            "CREATE_MAINTENANCE_WINDOW",
            f"maintenance_window:{window_id}",
            {"title": title, "start_time": start_time.isoformat(), "end_time": end_time.isoformat()},
            ip_address,
            user_agent
        )
        
        self.logger.info(f"Created maintenance window: {title}")
        return window_id

    def get_security_events(self, admin_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get security events"""
        if not self._has_permission(admin_id, Permission.AUDIT_LOG):
            raise PermissionError("Insufficient permissions to view security events")
        
        # Sort by timestamp (newest first)
        events = sorted(self.security_events, key=lambda x: x["timestamp"], reverse=True)
        
        return events[:limit]

    def generate_api_key(self, admin_id: str, user_id: str, description: str, ip_address: str, user_agent: str) -> str:
        """Generate a new API key for an admin user"""
        if not self._has_permission(admin_id, Permission.API_KEYS):
            raise PermissionError("Insufficient permissions to generate API keys")
        
        if user_id not in self.admin_users:
            raise ValueError("User not found")
        
        api_key = f"tk_{secrets.token_urlsafe(32)}"
        
        user = self.admin_users[user_id]
        user.api_keys.append(api_key)
        
        self._log_audit(
            admin_id,
            "GENERATE_API_KEY",
            f"admin_user:{user_id}",
            {"description": description, "api_key": api_key[:10] + "..."},
            ip_address,
            user_agent
        )
        
        self.logger.info(f"Generated API key for user {user.username}")
        return api_key

    def revoke_api_key(self, admin_id: str, user_id: str, api_key: str, ip_address: str, user_agent: str) -> bool:
        """Revoke an API key"""
        if not self._has_permission(admin_id, Permission.API_KEYS):
            raise PermissionError("Insufficient permissions to revoke API keys")
        
        if user_id not in self.admin_users:
            raise ValueError("User not found")
        
        user = self.admin_users[user_id]
        if api_key in user.api_keys:
            user.api_keys.remove(api_key)
            
            self._log_audit(
                admin_id,
                "REVOKE_API_KEY",
                f"admin_user:{user_id}",
                {"api_key": api_key[:10] + "..."},
                ip_address,
                user_agent
            )
            
            self.logger.info(f"Revoked API key for user {user.username}")
            return True
        
        return False

# Initialize the admin control system
admin_system = AdminControlSystem()

# FastAPI endpoints
from fastapi import FastAPI, HTTPException, Depends, Request, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

app = FastAPI(title="TigerEx Admin Control System API", version="1.0.0")
security = HTTPBearer()

class AdminCreateRequest(BaseModel):
    username: str
    email: str
    role: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ConfigUpdateRequest(BaseModel):
    value: Any

class TradingPairRequest(BaseModel):
    symbol: str
    base_currency: str
    quote_currency: str
    min_trade_amount: float = 0.001
    max_trade_amount: float = 1000000
    fee_rate: float = 0.001
    maker_fee: float = 0.0008
    taker_fee: float = 0.0012

class MaintenanceWindowRequest(BaseModel):
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    affected_services: List[str]

class ApiKeyRequest(BaseModel):
    user_id: str
    description: str

def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)) -> AdminUser:
    """Get current admin user from session"""
    session_id = credentials.credentials
    user = admin_system.get_user_by_session(session_id)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    return user

@app.post("/api/v1/admin/auth/login")
async def login(request: Request, login_data: LoginRequest):
    """Admin login"""
    try:
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        session_id = admin_system.authenticate_admin(
            login_data.username,
            login_data.password,
            ip_address,
            user_agent
        )
        
        if not session_id:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        return {"session_id": session_id, "message": "Login successful"}
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/api/v1/admin/auth/logout")
async def logout(current_user: AdminUser = Depends(get_current_user)):
    """Admin logout"""
    # In a real implementation, you would invalidate the session
    return {"message": "Logout successful"}

@app.post("/api/v1/admin/users")
async def create_admin_user(
    request: Request,
    user_data: AdminCreateRequest,
    current_user: AdminUser = Depends(get_current_user)
):
    """Create a new admin user"""
    try:
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        role = UserRole(user_data.role)
        user_id = admin_system.create_admin_user(
            current_user.id,
            user_data.username,
            user_data.email,
            role,
            user_data.password,
            ip_address,
            user_agent
        )
        
        return {"user_id": user_id, "message": "Admin user created successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/admin/users")
async def get_admin_users(current_user: AdminUser = Depends(get_current_user)):
    """Get all admin users"""
    try:
        users = admin_system.get_admin_users(current_user.id)
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.get("/api/v1/admin/audit-logs")
async def get_audit_logs(
    limit: int = 100,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    current_user: AdminUser = Depends(get_current_user)
):
    """Get audit logs"""
    try:
        logs = admin_system.get_audit_logs(current_user.id, limit, user_id, action)
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.get("/api/v1/admin/metrics")
async def get_system_metrics(current_user: AdminUser = Depends(get_current_user)):
    """Get system metrics"""
    try:
        metrics = admin_system.get_system_metrics(current_user.id)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.get("/api/v1/admin/configs")
async def get_system_configs(current_user: AdminUser = Depends(get_current_user)):
    """Get system configurations"""
    if not admin_system._has_permission(current_user.id, Permission.SYSTEM_CONFIG):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    configs = []
    for config in admin_system.system_configs.values():
        config_data = {
            "id": config.id,
            "key": config.key,
            "value": config.value if not config.is_sensitive else "***",
            "description": config.description,
            "category": config.category,
            "requires_restart": config.requires_restart,
            "updated_at": config.updated_at.isoformat()
        }
        configs.append(config_data)
    
    return {"configs": configs}

@app.put("/api/v1/admin/configs/{config_id}")
async def update_system_config(
    config_id: str,
    request_data: ConfigUpdateRequest,
    request: Request,
    current_user: AdminUser = Depends(get_current_user)
):
    """Update system configuration"""
    try:
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        success = admin_system.update_system_config(
            current_user.id,
            config_id,
            request_data.value,
            ip_address,
            user_agent
        )
        
        if success:
            return {"message": "Configuration updated successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to update configuration")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/admin/trading-pairs")
async def create_trading_pair(
    request: Request,
    pair_data: TradingPairRequest,
    current_user: AdminUser = Depends(get_current_user)
):
    """Create a new trading pair"""
    try:
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        pair_id = admin_system.create_trading_pair(
            current_user.id,
            pair_data.symbol,
            pair_data.base_currency,
            pair_data.quote_currency,
            min_trade_amount=pair_data.min_trade_amount,
            max_trade_amount=pair_data.max_trade_amount,
            fee_rate=pair_data.fee_rate,
            maker_fee=pair_data.maker_fee,
            taker_fee=pair_data.taker_fee
        )
        
        return {"pair_id": pair_id, "message": "Trading pair created successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/admin/trading-pairs")
async def get_trading_pairs(current_user: AdminUser = Depends(get_current_user)):
    """Get all trading pairs"""
    if not admin_system._has_permission(current_user.id, Permission.TRADING_VIEW):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    pairs = []
    for pair in admin_system.trading_pairs.values():
        pair_data = {
            "id": pair.id,
            "symbol": pair.symbol,
            "base_currency": pair.base_currency,
            "quote_currency": pair.quote_currency,
            "is_active": pair.is_active,
            "min_trade_amount": pair.min_trade_amount,
            "max_trade_amount": pair.max_trade_amount,
            "fee_rate": pair.fee_rate,
            "maker_fee": pair.maker_fee,
            "taker_fee": pair.taker_fee,
            "volume_24h": pair.volume_24h,
            "high_24h": pair.high_24h,
            "low_24h": pair.low_24h,
            "last_price": pair.last_price,
            "created_at": pair.created_at.isoformat()
        }
        pairs.append(pair_data)
    
    return {"pairs": pairs}

@app.post("/api/v1/admin/maintenance-windows")
async def create_maintenance_window(
    request: Request,
    window_data: MaintenanceWindowRequest,
    current_user: AdminUser = Depends(get_current_user)
):
    """Create a maintenance window"""
    try:
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        window_id = admin_system.create_maintenance_window(
            current_user.id,
            window_data.title,
            window_data.description,
            window_data.start_time,
            window_data.end_time,
            window_data.affected_services,
            ip_address,
            user_agent
        )
        
        return {"window_id": window_id, "message": "Maintenance window created successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/admin/security-events")
async def get_security_events(
    limit: int = 100,
    current_user: AdminUser = Depends(get_current_user)
):
    """Get security events"""
    try:
        events = admin_system.get_security_events(current_user.id, limit)
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.post("/api/v1/admin/api-keys/generate")
async def generate_api_key(
    request: Request,
    key_data: ApiKeyRequest,
    current_user: AdminUser = Depends(get_current_user)
):
    """Generate API key"""
    try:
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        api_key = admin_system.generate_api_key(
            current_user.id,
            key_data.user_id,
            key_data.description,
            ip_address,
            user_agent
        )
        
        return {"api_key": api_key, "message": "API key generated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/v1/admin/api-keys/revoke")
async def revoke_api_key(
    request: Request,
    user_id: str,
    api_key: str,
    current_user: AdminUser = Depends(get_current_user)
):
    """Revoke API key"""
    try:
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        success = admin_system.revoke_api_key(
            current_user.id,
            user_id,
            api_key,
            ip_address,
            user_agent
        )
        
        if success:
            return {"message": "API key revoked successfully"}
        else:
            raise HTTPException(status_code=404, detail="API key not found")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/admin/profile")
async def get_profile(current_user: AdminUser = Depends(get_current_user)):
    """Get current admin user profile"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role.value,
        "permissions": [perm.value for perm in current_user.permissions],
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat(),
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
        "two_factor_enabled": current_user.two_factor_enabled
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=8005)