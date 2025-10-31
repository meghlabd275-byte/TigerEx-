"""
Comprehensive Admin Control System - 6-Role User Management
Complete admin controls with full system management capabilities
"""

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import asyncio
import json
import logging

app = FastAPI(title="Comprehensive Admin Control System", version="1.0.0")
security = HTTPBearer()

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    EXCHANGE_ADMIN = "exchange_admin"
    LIQUIDITY_ADMIN = "liquidity_admin"
    SUPPORT_ADMIN = "support_admin"
    COMPLIANCE_ADMIN = "compliance_admin"
    TRADING_ADMIN = "trading_admin"
    INSTITUTIONAL_ADMIN = "institutional_admin"
    USER = "user"

class Permission(str, Enum):
    # System permissions
    SYSTEM_CONFIG = "system_config"
    USER_MANAGEMENT = "user_management"
    ROLE_ASSIGNMENT = "role_assignment"
    
    # Trading permissions
    TRADING_PAIR_MANAGEMENT = "trading_pair_management"
    ORDER_MANAGEMENT = "order_management"
    TRADING_ANALYTICS = "trading_analytics"
    
    # Liquidity permissions
    LIQUIDITY_MANAGEMENT = "liquidity_management"
    POOL_MANAGEMENT = "pool_management"
    YIELD_FARMING = "yield_farming"
    
    # Exchange permissions
    EXCHANGE_INTEGRATION = "exchange_integration"
    API_MANAGEMENT = "api_management"
    MARKET_DATA = "market_data"
    
    # Support permissions
    TICKET_MANAGEMENT = "ticket_management"
    USER_SUPPORT = "user_support"
    DISPUTE_RESOLUTION = "dispute_resolution"
    
    # Compliance permissions
    KYC_MANAGEMENT = "kyc_management"
    AML_MONITORING = "aml_monitoring"
    COMPLIANCE_REPORTING = "compliance_reporting"
    
    # Financial permissions
    WITHDRAWAL_APPROVAL = "withdrawal_approval"
    DEPOSIT_MANAGEMENT = "deposit_management"
    FINANCIAL_REPORTING = "financial_reporting"

class User(BaseModel):
    user_id: str
    username: str
    email: str
    role: UserRole
    permissions: List[Permission]
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime
    two_factor_enabled: bool

class TradingPair(BaseModel):
    pair_id: str
    symbol: str
    base_currency: str
    quote_currency: str
    status: str
    min_order_size: float
    max_order_size: float
    fee_rate: float
    created_at: datetime

class SystemConfiguration(BaseModel):
    config_key: str
    config_value: str
    category: str
    description: str
    is_sensitive: bool
    updated_by: str
    updated_at: datetime

class SecurityAudit(BaseModel):
    audit_id: str
    user_id: str
    action: str
    resource: str
    ip_address: str
    user_agent: str
    timestamp: datetime
    success: bool

class LiquidityPool(BaseModel):
    pool_id: str
    token_a: str
    token_b: str
    total_liquidity: float
    apr: float
    fee_tier: float
    status: str

class AdminControl:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.trading_pairs: Dict[str, TradingPair] = {}
        self.system_configs: Dict[str, SystemConfiguration] = {}
        self.security_audits: List[SecurityAudit] = []
        self.liquidity_pools: Dict[str, LiquidityPool] = {}
        
        # Role permissions mapping
        self.role_permissions = {
            UserRole.SUPER_ADMIN: list(Permission),
            UserRole.EXCHANGE_ADMIN: [
                Permission.EXCHANGE_INTEGRATION,
                Permission.API_MANAGEMENT,
                Permission.MARKET_DATA,
                Permission.TRADING_ANALYTICS,
                Permission.SYSTEM_CONFIG
            ],
            UserRole.LIQUIDITY_ADMIN: [
                Permission.LIQUIDITY_MANAGEMENT,
                Permission.POOL_MANAGEMENT,
                Permission.YIELD_FARMING,
                Permission.TRADING_ANALYTICS
            ],
            UserRole.SUPPORT_ADMIN: [
                Permission.TICKET_MANAGEMENT,
                Permission.USER_SUPPORT,
                Permission.DISPUTE_RESOLUTION,
                Permission.USER_MANAGEMENT
            ],
            UserRole.COMPLIANCE_ADMIN: [
                Permission.KYC_MANAGEMENT,
                Permission.AML_MONITORING,
                Permission.COMPLIANCE_REPORTING,
                Permission.WITHDRAWAL_APPROVAL
            ],
            UserRole.TRADING_ADMIN: [
                Permission.TRADING_PAIR_MANAGEMENT,
                Permission.ORDER_MANAGEMENT,
                Permission.TRADING_ANALYTICS,
                Permission.MARKET_DATA
            ],
            UserRole.USER: []  # No admin permissions
        }
        
        self.initialize_system()
    
    def initialize_system(self):
        """Initialize system with default admin and configurations"""
        # Create super admin
        super_admin = User(
            user_id="admin_001",
            username="superadmin",
            email="admin@tigerex.com",
            role=UserRole.SUPER_ADMIN,
            permissions=self.role_permissions[UserRole.SUPER_ADMIN],
            is_active=True,
            last_login=None,
            created_at=datetime.utcnow(),
            two_factor_enabled=True
        )
        
        self.users[super_admin.user_id] = super_admin
        
        # Default system configurations
        default_configs = [
            SystemConfiguration(
                config_key="maintenance_mode",
                config_value="false",
                category="system",
                description="Enable/disable maintenance mode",
                is_sensitive=False,
                updated_by="system",
                updated_at=datetime.utcnow()
            ),
            SystemConfiguration(
                config_key="max_withdrawal_limit",
                config_value="100000",
                category="financial",
                description="Maximum withdrawal limit per transaction",
                is_sensitive=True,
                updated_by="system",
                updated_at=datetime.utcnow()
            ),
            SystemConfiguration(
                config_key="trading_fee_percentage",
                config_value="0.001",
                category="trading",
                description="Default trading fee percentage",
                is_sensitive=False,
                updated_by="system",
                updated_at=datetime.utcnow()
            )
        ]
        
        for config in default_configs:
            self.system_configs[config.config_key] = config
    
    def check_permission(self, user: User, permission: Permission) -> bool:
        """Check if user has specific permission"""
        return permission in user.permissions
    
    def log_security_audit(self, user_id: str, action: str, resource: str, 
                          ip_address: str, user_agent: str, success: bool):
        """Log security audit event"""
        audit = SecurityAudit(
            audit_id=f"audit_{int(datetime.utcnow().timestamp())}_{len(self.security_audits)}",
            user_id=user_id,
            action=action,
            resource=resource,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow(),
            success=success
        )
        
        self.security_audits.append(audit)
        
        # Keep only last 10000 audit logs
        if len(self.security_audits) > 10000:
            self.security_audits = self.security_audits[-10000:]

admin_control = AdminControl()

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> User:
    """Get current user from token (simplified)"""
    # In production, would validate JWT token and fetch user from database
    user_id = "admin_001"  # Mock user
    user = admin_control.users.get(user_id)
    
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    return user

def require_permission(permission: Permission):
    """Decorator to require specific permission"""
    def dependency(user: User = Depends(get_current_user)):
        if not admin_control.check_permission(user, permission):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return dependency

@app.get("/")
async def root():
    return {
        "service": "Comprehensive Admin Control System",
        "roles": [role.value for role in UserRole],
        "permissions": [perm.value for perm in Permission],
        "status": "operational"
    }

@app.post("/users")
async def create_user(
    username: str,
    email: str,
    role: UserRole,
    current_user: User = Depends(require_permission(Permission.USER_MANAGEMENT))
):
    """Create new user"""
    try:
        user_id = f"user_{int(datetime.utcnow().timestamp())}_{len(admin_control.users)}"
        
        permissions = admin_control.role_permissions.get(role, [])
        
        new_user = User(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            permissions=permissions,
            is_active=True,
            last_login=None,
            created_at=datetime.utcnow(),
            two_factor_enabled=False
        )
        
        admin_control.users[user_id] = new_user
        
        admin_control.log_security_audit(
            current_user.user_id, "create_user", user_id, "127.0.0.1", "admin_system", True
        )
        
        return {
            "user_id": user_id,
            "username": username,
            "email": email,
            "role": role.value,
            "permissions": [p.value for p in permissions],
            "message": "User created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users")
async def get_users(
    current_user: User = Depends(require_permission(Permission.USER_MANAGEMENT))
):
    """Get all users"""
    users = list(admin_control.users.values())
    return {"users": users}

@app.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    new_role: UserRole,
    current_user: User = Depends(require_permission(Permission.ROLE_ASSIGNMENT))
):
    """Update user role"""
    try:
        user = admin_control.users.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.role == UserRole.SUPER_ADMIN:
            raise HTTPException(status_code=400, detail="Cannot modify super admin role")
        
        old_role = user.role
        user.role = new_role
        user.permissions = admin_control.role_permissions[new_role]
        
        admin_control.log_security_audit(
            current_user.user_id, "update_role", user_id, "127.0.0.1", "admin_system", True
        )
        
        return {
            "user_id": user_id,
            "old_role": old_role.value,
            "new_role": new_role.value,
            "message": "User role updated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trading-pairs")
async def create_trading_pair(
    symbol: str,
    base_currency: str,
    quote_currency: str,
    min_order_size: float,
    max_order_size: float,
    fee_rate: float,
    current_user: User = Depends(require_permission(Permission.TRADING_PAIR_MANAGEMENT))
):
    """Create new trading pair"""
    try:
        pair_id = f"pair_{symbol.lower().replace('/', '_')}"
        
        trading_pair = TradingPair(
            pair_id=pair_id,
            symbol=symbol,
            base_currency=base_currency,
            quote_currency=quote_currency,
            status="active",
            min_order_size=min_order_size,
            max_order_size=max_order_size,
            fee_rate=fee_rate,
            created_at=datetime.utcnow()
        )
        
        admin_control.trading_pairs[pair_id] = trading_pair
        
        admin_control.log_security_audit(
            current_user.user_id, "create_trading_pair", pair_id, "127.0.0.1", "admin_system", True
        )
        
        return {
            "pair_id": pair_id,
            "symbol": symbol,
            "status": "active",
            "message": "Trading pair created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trading-pairs")
async def get_trading_pairs(
    current_user: User = Depends(require_permission(Permission.TRADING_ANALYTICS))
):
    """Get all trading pairs"""
    pairs = list(admin_control.trading_pairs.values())
    return {"trading_pairs": pairs}

@app.put("/trading-pairs/{pair_id}/status")
async def update_trading_pair_status(
    pair_id: str,
    status: str,
    current_user: User = Depends(require_permission(Permission.TRADING_PAIR_MANAGEMENT))
):
    """Update trading pair status"""
    try:
        pair = admin_control.trading_pairs.get(pair_id)
        if not pair:
            raise HTTPException(status_code=404, detail="Trading pair not found")
        
        old_status = pair.status
        pair.status = status
        
        admin_control.log_security_audit(
            current_user.user_id, "update_pair_status", pair_id, "127.0.0.1", "admin_system", True
        )
        
        return {
            "pair_id": pair_id,
            "old_status": old_status,
            "new_status": status,
            "message": "Trading pair status updated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/config")
async def get_system_config(
    category: Optional[str] = None,
    current_user: User = Depends(require_permission(Permission.SYSTEM_CONFIG))
):
    """Get system configuration"""
    configs = list(admin_control.system_configs.values())
    
    if category:
        configs = [c for c in configs if c.category == category]
    
    # Hide sensitive values for non-super admins
    if current_user.role != UserRole.SUPER_ADMIN:
        for config in configs:
            if config.is_sensitive:
                config.config_value = "***HIDDEN***"
    
    return {"configurations": configs}

@app.put("/system/config/{config_key}")
async def update_system_config(
    config_key: str,
    config_value: str,
    current_user: User = Depends(require_permission(Permission.SYSTEM_CONFIG))
):
    """Update system configuration"""
    try:
        config = admin_control.system_configs.get(config_key)
        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")
        
        old_value = config.config_value
        config.config_value = config_value
        config.updated_by = current_user.user_id
        config.updated_at = datetime.utcnow()
        
        admin_control.log_security_audit(
            current_user.user_id, "update_config", config_key, "127.0.0.1", "admin_system", True
        )
        
        return {
            "config_key": config_key,
            "old_value": old_value,
            "new_value": config_value,
            "message": "Configuration updated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/liquidity/pools")
async def get_liquidity_pools(
    current_user: User = Depends(require_permission(Permission.LIQUIDITY_MANAGEMENT))
):
    """Get all liquidity pools"""
    pools = list(admin_control.liquidity_pools.values())
    return {"liquidity_pools": pools}

@app.post("/liquidity/pools")
async def create_liquidity_pool(
    token_a: str,
    token_b: str,
    fee_tier: float,
    current_user: User = Depends(require_permission(Permission.POOL_MANAGEMENT))
):
    """Create new liquidity pool"""
    try:
        pool_id = f"pool_{token_a.lower()}_{token_b.lower()}"
        
        pool = LiquidityPool(
            pool_id=pool_id,
            token_a=token_a,
            token_b=token_b,
            total_liquidity=0.0,
            apr=0.0,
            fee_tier=fee_tier,
            status="active"
        )
        
        admin_control.liquidity_pools[pool_id] = pool
        
        admin_control.log_security_audit(
            current_user.user_id, "create_liquidity_pool", pool_id, "127.0.0.1", "admin_system", True
        )
        
        return {
            "pool_id": pool_id,
            "token_a": token_a,
            "token_b": token_b,
            "status": "active",
            "message": "Liquidity pool created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/security/audit")
async def get_security_audit(
    limit: int = 100,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    current_user: User = Depends(require_permission(Permission.SYSTEM_CONFIG))
):
    """Get security audit logs"""
    audits = admin_control.security_audits.copy()
    
    if user_id:
        audits = [a for a in audits if a.user_id == user_id]
    
    if action:
        audits = [a for a in audits if a.action == action]
    
    # Return most recent logs
    audits = sorted(audits, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    return {"audit_logs": audits}

@app.get("/analytics/dashboard")
async def get_admin_dashboard(
    current_user: User = Depends(get_current_user)
):
    """Get admin dashboard analytics"""
    stats = {
        "total_users": len(admin_control.users),
        "active_users": len([u for u in admin_control.users.values() if u.is_active]),
        "total_trading_pairs": len(admin_control.trading_pairs),
        "active_trading_pairs": len([p for p in admin_control.trading_pairs.values() if p.status == "active"]),
        "total_liquidity_pools": len(admin_control.liquidity_pools),
        "total_audit_logs": len(admin_control.security_audits),
        "system_configs": len(admin_control.system_configs)
    }
    
    # Role-based statistics
    role_stats = {}
    for role in UserRole:
        role_stats[role.value] = len([u for u in admin_control.users.values() if u.role == role])
    
    stats["user_roles"] = role_stats
    
    return {"dashboard": stats}

@app.get("/permissions")
async def get_permissions():
    """Get all available permissions"""
    return {"permissions": [{"name": perm.value, "category": perm.value.split('_')[0]} for perm in Permission]}

@app.get("/roles/{role}/permissions")
async def get_role_permissions(role: UserRole):
    """Get permissions for specific role"""
    permissions = admin_control.role_permissions.get(role, [])
    return {"role": role.value, "permissions": [p.value for p in permissions]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)