"""
Unified Admin Control System - Complete Admin Controls
Global, Liquidity, Cryptocurrency, Blockchain Management
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

app = FastAPI(title="Unified Admin Control System", version="1.0.0")
security = HTTPBearer()

class AdminRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    GLOBAL_ADMIN = "global_admin"
    LIQUIDITY_ADMIN = "liquidity_admin"
    CRYPTO_ADMIN = "crypto_admin"
    BLOCKCHAIN_ADMIN = "blockchain_admin"
    SUPPORT_ADMIN = "support_admin"

class SystemStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    DEGRADED = "degraded"

class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AdminPermission(BaseModel):
    permission_id: str
    name: str
    description: str
    category: str
    is_sensitive: bool

class AdminUser(BaseModel):
    user_id: str
    username: str
    email: str
    role: AdminRole
    permissions: List[str]
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime
    two_factor_enabled: bool

class SystemConfiguration(BaseModel):
    config_key: str
    config_value: Any
    category: str
    description: str
    is_sensitive: bool
    requires_restart: bool
    updated_by: str
    updated_at: datetime

class SecurityEvent(BaseModel):
    event_id: str
    user_id: str
    action: str
    resource: str
    ip_address: str
    user_agent: str
    timestamp: datetime
    success: bool
    risk_level: str

class SystemMetrics(BaseModel):
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    category: str

class Alert(BaseModel):
    alert_id: str
    title: str
    description: str
    severity: str
    category: str
    is_resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime]
    resolved_by: Optional[str]

class UnifiedAdminSystem:
    def __init__(self):
        self.users: Dict[str, AdminUser] = {}
        self.permissions: Dict[str, AdminPermission] = {}
        self.configurations: Dict[str, SystemConfiguration] = {}
        self.security_events: List[SecurityEvent] = []
        self.system_metrics: Dict[str, List[SystemMetrics]] = {}
        self.alerts: Dict[str, Alert] = {}
        
        self.role_permissions = {
            AdminRole.SUPER_ADMIN: ["*"],  # All permissions
            AdminRole.GLOBAL_ADMIN: [
                "system_config", "user_management", "monitoring", "global_settings"
            ],
            AdminRole.LIQUIDITY_ADMIN: [
                "liquidity_management", "pool_management", "market_making", "rebalancing"
            ],
            AdminRole.CRYPTO_ADMIN: [
                "crypto_management", "trading_pairs", "asset_listing", "fee_management"
            ],
            AdminRole.BLOCKCHAIN_ADMIN: [
                "blockchain_management", "network_config", "bridge_management", "smart_contracts"
            ],
            AdminRole.SUPPORT_ADMIN: [
                "user_support", "ticket_management", "dispute_resolution", "compliance"
            ]
        }
        
        self.initialize_system()
    
    def initialize_system(self):
        """Initialize the admin system"""
        # Create permissions
        self.create_permissions()
        
        # Create super admin
        self.create_super_admin()
        
        # Initialize default configurations
        self.initialize_configurations()
        
        # Start monitoring
        asyncio.create_task(self.monitoring_loop())
    
    def create_permissions(self):
        """Create all admin permissions"""
        permission_data = [
            # System permissions
            {"id": "system_config", "name": "System Configuration", "category": "system", "is_sensitive": True},
            {"id": "user_management", "name": "User Management", "category": "system", "is_sensitive": True},
            {"id": "monitoring", "name": "System Monitoring", "category": "system", "is_sensitive": False},
            {"id": "global_settings", "name": "Global Settings", "category": "system", "is_sensitive": True},
            
            # Liquidity permissions
            {"id": "liquidity_management", "name": "Liquidity Management", "category": "liquidity", "is_sensitive": True},
            {"id": "pool_management", "name": "Pool Management", "category": "liquidity", "is_sensitive": True},
            {"id": "market_making", "name": "Market Making", "category": "liquidity", "is_sensitive": True},
            {"id": "rebalancing", "name": "Pool Rebalancing", "category": "liquidity", "is_sensitive": True},
            
            # Crypto permissions
            {"id": "crypto_management", "name": "Cryptocurrency Management", "category": "crypto", "is_sensitive": True},
            {"id": "trading_pairs", "name": "Trading Pair Management", "category": "crypto", "is_sensitive": True},
            {"id": "asset_listing", "name": "Asset Listing", "category": "crypto", "is_sensitive": True},
            {"id": "fee_management", "name": "Fee Management", "category": "crypto", "is_sensitive": True},
            
            # Blockchain permissions
            {"id": "blockchain_management", "name": "Blockchain Management", "category": "blockchain", "is_sensitive": True},
            {"id": "network_config", "name": "Network Configuration", "category": "blockchain", "is_sensitive": True},
            {"id": "bridge_management", "name": "Bridge Management", "category": "blockchain", "is_sensitive": True},
            {"id": "smart_contracts", "name": "Smart Contract Management", "category": "blockchain", "is_sensitive": True},
            
            # Support permissions
            {"id": "user_support", "name": "User Support", "category": "support", "is_sensitive": False},
            {"id": "ticket_management", "name": "Ticket Management", "category": "support", "is_sensitive": False},
            {"id": "dispute_resolution", "name": "Dispute Resolution", "category": "support", "is_sensitive": False},
            {"id": "compliance", "name": "Compliance Management", "category": "support", "is_sensitive": True}
        ]
        
        for perm_data in permission_data:
            permission = AdminPermission(
                permission_id=perm_data["id"],
                name=perm_data["name"],
                description=f"Access to {perm_data['name']} functionality",
                category=perm_data["category"],
                is_sensitive=perm_data["is_sensitive"]
            )
            self.permissions[permission.permission_id] = permission
    
    def create_super_admin(self):
        """Create super admin user"""
        super_admin = AdminUser(
            user_id="super_admin_001",
            username="superadmin",
            email="admin@tigerex.com",
            role=AdminRole.SUPER_ADMIN,
            permissions=["*"],
            is_active=True,
            last_login=None,
            created_at=datetime.utcnow(),
            two_factor_enabled=True
        )
        
        self.users[super_admin.user_id] = super_admin
    
    def initialize_configurations(self):
        """Initialize system configurations"""
        config_data = [
            {
                "key": "system.maintenance_mode",
                "value": False,
                "category": "system",
                "description": "Enable/disable maintenance mode",
                "is_sensitive": False,
                "requires_restart": False
            },
            {
                "key": "system.debug_mode",
                "value": False,
                "category": "system",
                "description": "Enable debug logging",
                "is_sensitive": False,
                "requires_restart": False
            },
            {
                "key": "liquidity.default_fee_tier",
                "value": "0.003",
                "category": "liquidity",
                "description": "Default liquidity pool fee tier",
                "is_sensitive": False,
                "requires_restart": False
            },
            {
                "key": "crypto.max_withdrawal_limit",
                "value": 100000,
                "category": "crypto",
                "description": "Maximum withdrawal limit per transaction",
                "is_sensitive": True,
                "requires_restart": False
            },
            {
                "key": "blockchain.rpc_timeout",
                "value": 30,
                "category": "blockchain",
                "description": "RPC request timeout in seconds",
                "is_sensitive": False,
                "requires_restart": True
            },
            {
                "key": "security.session_timeout",
                "value": 3600,
                "category": "security",
                "description": "User session timeout in seconds",
                "is_sensitive": True,
                "requires_restart": False
            }
        ]
        
        for config in config_data:
            system_config = SystemConfiguration(
                config_key=config["key"],
                config_value=config["value"],
                category=config["category"],
                description=config["description"],
                is_sensitive=config["is_sensitive"],
                requires_restart=config["requires_restart"],
                updated_by="system",
                updated_at=datetime.utcnow()
            )
            self.configurations[config["key"]] = system_config
    
    def check_permission(self, user: AdminUser, permission: str) -> bool:
        """Check if user has permission"""
        if "*" in user.permissions:
            return True
        
        return permission in user.permissions
    
    def log_security_event(self, user_id: str, action: str, resource: str, 
                          ip_address: str, user_agent: str, success: bool, risk_level: str = "low"):
        """Log security event"""
        event = SecurityEvent(
            event_id=f"event_{int(datetime.utcnow().timestamp())}_{len(self.security_events)}",
            user_id=user_id,
            action=action,
            resource=resource,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow(),
            success=success,
            risk_level=risk_level
        )
        
        self.security_events.append(event)
        
        # Keep only last 10000 events
        if len(self.security_events) > 10000:
            self.security_events = self.security_events[-10000:]
    
    async def monitoring_loop(self):
        """Background monitoring loop"""
        while True:
            try:
                # Collect system metrics
                await self.collect_metrics()
                
                # Check for alerts
                await self.check_alerts()
                
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                print(f"Monitoring error: {e}")
                await asyncio.sleep(300)
    
    async def collect_metrics(self):
        """Collect system metrics"""
        import random
        import psutil
        
        current_time = datetime.utcnow()
        
        # System metrics
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        metrics = [
            SystemMetrics("cpu_usage", cpu_percent, "%", current_time, "system"),
            SystemMetrics("memory_usage", memory.percent, "%", current_time, "system"),
            SystemMetrics("disk_usage", disk.percent, "%", current_time, "system"),
            SystemMetrics("active_users", len([u for u in self.users.values() if u.is_active]), "count", current_time, "system"),
            SystemMetrics("total_configs", len(self.configurations), "count", current_time, "system"),
            SystemMetrics("security_events_24h", len([e for e in self.security_events if (datetime.utcnow() - e.timestamp).days < 1]), "count", current_time, "security")
        ]
        
        for metric in metrics:
            if metric.metric_name not in self.system_metrics:
                self.system_metrics[metric.metric_name] = []
            
            self.system_metrics[metric.metric_name].append(metric)
            
            # Keep only last 1000 data points per metric
            if len(self.system_metrics[metric.metric_name]) > 1000:
                self.system_metrics[metric.metric_name] = self.system_metrics[metric.metric_name][-1000:]
    
    async def check_alerts(self):
        """Check for system alerts"""
        import random
        
        current_time = datetime.utcnow()
        
        # Check CPU usage
        cpu_metrics = self.system_metrics.get("cpu_usage", [])
        if cpu_metrics:
            latest_cpu = cpu_metrics[-1].value
            if latest_cpu > 80:
                await self.create_alert("High CPU Usage", f"CPU usage is at {latest_cpu:.1f}%", "high", "system")
        
        # Check memory usage
        memory_metrics = self.system_metrics.get("memory_usage", [])
        if memory_metrics:
            latest_memory = memory_metrics[-1].value
            if latest_memory > 85:
                await self.create_alert("High Memory Usage", f"Memory usage is at {latest_memory:.1f}%", "high", "system")
        
        # Check security events
        recent_failed = len([e for e in self.security_events if not e.success and (current_time - e.timestamp).seconds < 300])
        if recent_failed > 10:
            await self.create_alert("Security Alert", f"{recent_failed} failed security events in last 5 minutes", "critical", "security")
    
    async def create_alert(self, title: str, description: str, severity: str, category: str):
        """Create system alert"""
        alert_id = f"alert_{int(datetime.utcnow().timestamp())}"
        
        alert = Alert(
            alert_id=alert_id,
            title=title,
            description=description,
            severity=severity,
            category=category,
            is_resolved=False,
            created_at=datetime.utcnow(),
            resolved_at=None,
            resolved_by=None
        )
        
        self.alerts[alert_id] = alert

admin_system = UnifiedAdminSystem()

def get_current_admin(credentials: HTTPAuthorizationCredentials = Security(security)) -> AdminUser:
    """Get current admin from token (simplified)"""
    user_id = "super_admin_001"  # Mock user
    user = admin_system.users.get(user_id)
    
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    return user

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def dependency(user: AdminUser = Depends(get_current_admin)):
        if not admin_system.check_permission(user, permission):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return dependency

@app.get("/")
async def root():
    return {
        "service": "Unified Admin Control System",
        "roles": [role.value for role in AdminRole],
        "permissions": len(admin_system.permissions),
        "status": "operational"
    }

@app.get("/dashboard")
async def get_dashboard(user: AdminUser = Depends(get_current_admin)):
    """Get admin dashboard"""
    # Get system overview
    total_users = len(admin_system.users)
    active_users = len([u for u in admin_system.users.values() if u.is_active])
    total_configs = len(admin_system.configurations)
    unresolved_alerts = len([a for a in admin_system.alerts.values() if not a.is_resolved])
    
    # Get recent metrics
    recent_metrics = {}
    for metric_name, metrics in admin_system.system_metrics.items():
        if metrics:
            recent_metrics[metric_name] = metrics[-1]
    
    return {
        "overview": {
            "total_users": total_users,
            "active_users": active_users,
            "total_configurations": total_configs,
            "unresolved_alerts": unresolved_alerts,
            "user_role": user.role.value
        },
        "recent_metrics": recent_metrics,
        "recent_alerts": [
            {"id": alert.alert_id, "title": alert.title, "severity": alert.severity, "created_at": alert.created_at}
            for alert in sorted(admin_system.alerts.values(), key=lambda x: x.created_at, reverse=True)[:5]
        ]
    }

# User Management Endpoints
@app.get("/users")
async def get_users(user: AdminUser = Depends(require_permission("user_management"))):
    """Get all admin users"""
    users = list(admin_system.users.values())
    return {"users": users}

@app.post("/users")
async def create_user(
    username: str,
    email: str,
    role: AdminRole,
    user: AdminUser = Depends(require_permission("user_management"))
):
    """Create new admin user"""
    try:
        user_id = f"admin_{int(datetime.utcnow().timestamp())}"
        permissions = admin_system.role_permissions.get(role, [])
        
        new_user = AdminUser(
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
        
        admin_system.users[user_id] = new_user
        
        admin_system.log_security_event(
            user.user_id, "create_user", user_id, "127.0.0.1", "admin_system", True
        )
        
        return {
            "user_id": user_id,
            "username": username,
            "email": email,
            "role": role.value,
            "message": "User created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Configuration Management Endpoints
@app.get("/configurations")
async def get_configurations(category: Optional[str] = None, user: AdminUser = Depends(get_current_admin)):
    """Get system configurations"""
    configs = list(admin_system.configurations.values())
    
    if category:
        configs = [c for c in configs if c.category == category]
    
    # Hide sensitive configs for non-super admins
    if user.role != AdminRole.SUPER_ADMIN:
        configs = [c for c in configs if not c.is_sensitive]
    
    return {"configurations": configs}

@app.put("/configurations/{config_key}")
async def update_configuration(
    config_key: str,
    config_value: Any,
    user: AdminUser = Depends(require_permission("system_config"))
):
    """Update system configuration"""
    try:
        config = admin_system.configurations.get(config_key)
        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")
        
        old_value = config.config_value
        config.config_value = config_value
        config.updated_by = user.user_id
        config.updated_at = datetime.utcnow()
        
        admin_system.log_security_event(
            user.user_id, "update_config", config_key, "127.0.0.1", "admin_system", True
        )
        
        return {
            "config_key": config_key,
            "old_value": old_value,
            "new_value": config_value,
            "requires_restart": config.requires_restart,
            "message": "Configuration updated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Security and Monitoring Endpoints
@app.get("/security/events")
async def get_security_events(
    limit: int = 100,
    risk_level: Optional[str] = None,
    user: AdminUser = Depends(require_permission("monitoring"))
):
    """Get security events"""
    events = admin_system.security_events.copy()
    
    if risk_level:
        events = [e for e in events if e.risk_level == risk_level]
    
    # Sort by timestamp and limit
    events.sort(key=lambda x: x.timestamp, reverse=True)
    events = events[:limit]
    
    return {"security_events": events}

@app.get("/metrics")
async def get_system_metrics(
    metric_name: Optional[str] = None,
    hours: int = 24,
    user: AdminUser = Depends(require_permission("monitoring"))
):
    """Get system metrics"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    if metric_name:
        metrics = admin_system.system_metrics.get(metric_name, [])
        filtered_metrics = [m for m in metrics if m.timestamp >= cutoff_time]
        return {"metric_name": metric_name, "metrics": filtered_metrics}
    
    result = {}
    for name, metrics in admin_system.system_metrics.items():
        filtered_metrics = [m for m in metrics if m.timestamp >= cutoff_time]
        if filtered_metrics:
            result[name] = filtered_metrics
    
    return {"metrics": result}

@app.get("/alerts")
async def get_alerts(
    resolved: Optional[bool] = None,
    severity: Optional[str] = None,
    user: AdminUser = Depends(require_permission("monitoring"))
):
    """Get system alerts"""
    alerts = list(admin_system.alerts.values())
    
    if resolved is not None:
        alerts = [a for a in alerts if a.is_resolved == resolved]
    
    if severity:
        alerts = [a for a in alerts if a.severity == severity]
    
    # Sort by created_at
    alerts.sort(key=lambda x: x.created_at, reverse=True)
    
    return {"alerts": alerts}

@app.put("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    user: AdminUser = Depends(require_permission("monitoring"))
):
    """Resolve system alert"""
    try:
        alert = admin_system.alerts.get(alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.is_resolved = True
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = user.user_id
        
        return {
            "alert_id": alert_id,
            "resolved_at": alert.resolved_at,
            "resolved_by": user.user_id,
            "message": "Alert resolved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Liquidity Admin Endpoints
@app.get("/liquidity/overview")
async def get_liquidity_overview(user: AdminUser = Depends(require_permission("liquidity_management"))):
    """Get liquidity management overview"""
    # Mock liquidity data
    liquidity_overview = {
        "total_pools": 25,
        "active_pools": 23,
        "total_liquidity": 150000000,
        "daily_volume": 5000000,
        "total_positions": 1250,
        "apr_average": 8.5,
        "top_pools": [
            {"symbol": "BTC/USDT", "liquidity": 45000000, "apr": 6.2},
            {"symbol": "ETH/USDT", "liquidity": 35000000, "apr": 7.8},
            {"symbol": "ETH/BTC", "liquidity": 20000000, "apr": 5.5}
        ]
    }
    
    return {"liquidity_overview": liquidity_overview}

@app.get("/crypto/overview")
async def get_crypto_overview(user: AdminUser = Depends(require_permission("crypto_management"))):
    """Get cryptocurrency management overview"""
    # Mock crypto data
    crypto_overview = {
        "total_assets": 200,
        "active_trading_pairs": 450,
        "daily_trading_volume": 250000000,
        "total_market_cap": 2000000000000,
        "listed_cryptos": 185,
        "pending_listings": 8,
        "top_volume_pairs": [
            {"symbol": "BTC/USDT", "volume": 50000000, "change_24h": 2.1},
            {"symbol": "ETH/USDT", "volume": 35000000, "change_24h": 1.8},
            {"symbol": "BNB/USDT", "volume": 15000000, "change_24h": 3.2}
        ]
    }
    
    return {"crypto_overview": crypto_overview}

@app.get("/blockchain/overview")
async def get_blockchain_overview(user: AdminUser = Depends(require_permission("blockchain_management"))):
    """Get blockchain management overview"""
    # Mock blockchain data
    blockchain_overview = {
        "total_blockchains": 100,
        "active_blockchains": 98,
        "layer_1_count": 45,
        "layer_2_count": 25,
        "total_tvl": 50000000000,
        "daily_transactions": 5000000,
        "active_bridges": 15,
        "smart_contracts_deployed": 1250,
        "top_blockchains": [
            {"name": "Ethereum", "tvl": 25000000000, "transactions": 2000000},
            {"name": "Binance Smart Chain", "tvl": 12000000000, "transactions": 1500000},
            {"name": "Polygon", "tvl": 5000000000, "transactions": 800000}
        ]
    }
    
    return {"blockchain_overview": blockchain_overview}

@app.get("/permissions")
async def get_permissions():
    """Get all available permissions"""
    permissions = list(admin_system.permissions.values())
    return {"permissions": permissions}

@app.get("/roles/{role}/permissions")
async def get_role_permissions(role: AdminRole):
    """Get permissions for specific role"""
    permissions = admin_system.role_permissions.get(role, [])
    return {"role": role.value, "permissions": permissions}

if __name__ == "__main__":
    import uvicorn
    import psutil
    from datetime import timedelta
    uvicorn.run(app, host="0.0.0.0", port=8013)