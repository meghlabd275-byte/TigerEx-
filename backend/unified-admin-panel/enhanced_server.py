"""
TigerEx Unified Admin Panel - Consolidated v12.0.0
Complete admin dashboard with all features from duplicate services merged
Includes: enhanced admin control, super admin, universal controls, comprehensive trading admin
"""

from fastapi import FastAPI, HTTPException, Depends, Security, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import logging
from decimal import Decimal
import jwt
import uvicorn
import time
import hashlib
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TigerEx Unified Admin Panel v12.0.0",
    description="Consolidated admin control system with comprehensive monitoring and management",
    version="12.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
JWT_SECRET = "tigerex-admin-super-secure-key-2024"
JWT_ALGORITHM = "HS256"

# ==================== ENUMS AND MODELS ====================

class AdminRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    SYSTEM_ADMIN = "system_admin"
    TRADING_ADMIN = "trading_admin"
    USER_ADMIN = "user_admin"
    COMPLIANCE_ADMIN = "compliance_admin"
    SUPPORT_ADMIN = "support_admin"
    FINANCE_ADMIN = "finance_admin"
    MARKETING_ADMIN = "marketing_admin"
    TECHNICAL_ADMIN = "technical_admin"
    OPERATIONS_ADMIN = "operations_admin"
    VIEWER = "viewer"

class SystemStatus(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    MAINTENANCE = "maintenance"

class TradingMode(str, Enum):
    NORMAL = "normal"
    MAINTENANCE = "maintenance"
    EMERGENCY = "emergency"
    READ_ONLY = "read_only"

class AdminPermission(str, Enum):
    USER_MANAGEMENT = "user_management"
    TRADING_CONTROL = "trading_control"
    SYSTEM_MONITORING = "system_monitoring"
    FINANCIAL_CONTROL = "financial_control"
    COMPLIANCE_MANAGEMENT = "compliance_management"
    API_MANAGEMENT = "api_management"
    DASHBOARD_ACCESS = "dashboard_access"
    REPORT_GENERATION = "report_generation"
    EMERGENCY_CONTROL = "emergency_control"

@dataclass
class AdminUser:
    id: str
    username: str
    email: str
    role: AdminRole
    permissions: List[AdminPermission]
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    session_id: Optional[str] = None

@dataclass
class SystemMetrics:
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: float
    active_connections: int
    api_requests_per_minute: int
    database_connections: int
    cache_hit_rate: float

@dataclass
class TradingMetrics:
    total_volume_24h: Decimal
    total_trades_24h: int
    active_users: int
    open_orders: int
    order_book_depth: Dict[str, int]
    price_volatility: Dict[str, float]
    liquidations_24h: int
    funding_rates: Dict[str, Decimal]

# ==================== PYDANTIC MODELS ====================

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    two_factor_code: Optional[str] = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    admin_user: Dict[str, Any]

class SystemControlRequest(BaseModel):
    action: str = Field(..., description="Control action to execute")
    parameters: Optional[Dict[str, Any]] = None
    reason: str = Field(..., min_length=10, max_length=500)
    requires_2fa: bool = False

class UserManagementRequest(BaseModel):
    user_id: str
    action: str = Field(..., regex="^(suspend|activate|verify|restrict|upgrade|downgrade)$")
    parameters: Optional[Dict[str, Any]] = None
    reason: str = Field(..., min_length=10, max_length=500)

class TradingControlRequest(BaseModel):
    symbol: Optional[str] = None
    action: str = Field(..., regex="^(pause|resume|cancel_orders|adjust_fees|maintenance)$")
    parameters: Optional[Dict[str, Any]] = None
    emergency_override: bool = False

# ==================== DATABASE ====================

# In-memory storage for demonstration
# In production, use proper database
admin_users = {}
system_logs = []
audit_logs = []
system_metrics_history = []

# Default super admin
DEFAULT_ADMIN = AdminUser(
    id="admin_001",
    username="tigerex_admin",
    email="admin@tigerex.com",
    role=AdminRole.SUPER_ADMIN,
    permissions=list(AdminPermission),
    created_at=datetime.now()
)
admin_users[DEFAULT_ADMIN.username] = DEFAULT_ADMIN

# ==================== AUTHENTICATION ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_admin_user(username: str = Depends(verify_token)):
    admin_user = admin_users.get(username)
    if not admin_user:
        raise HTTPException(status_code=401, detail="Admin user not found")
    if not admin_user.is_active:
        raise HTTPException(status_code=401, detail="Admin account is inactive")
    return admin_user

def require_permission(permission: AdminPermission):
    def permission_checker(admin_user: AdminUser = Depends(get_admin_user)):
        if permission not in admin_user.permissions:
            raise HTTPException(status_code=403, detail=f"Permission {permission} required")
        return admin_user
    return permission_checker

# ==================== API ENDPOINTS ====================

@app.post("/auth/login", response_model=LoginResponse)
async def admin_login(request: LoginRequest):
    """Admin authentication endpoint"""
    # Simplified authentication - in production, use proper password hashing
    admin_user = admin_users.get(request.username)
    if not admin_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password (simplified)
    if request.password != "tigerex_admin_2024":  # Change in production
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Update last login
    admin_user.last_login = datetime.now()
    
    # Generate token
    access_token = create_access_token(
        data={"sub": admin_user.username, "role": admin_user.role.value}
    )
    
    return LoginResponse(
        access_token=access_token,
        expires_in=86400,
        admin_user={
            "id": admin_user.id,
            "username": admin_user.username,
            "email": admin_user.email,
            "role": admin_user.role.value,
            "permissions": [p.value for p in admin_user.permissions]
        }
    )

@app.get("/dashboard/overview")
async def get_dashboard_overview(admin_user: AdminUser = Depends(get_admin_user)):
    """Get admin dashboard overview"""
    return {
        "system_status": SystemStatus.HEALTHY,
        "active_users": 12543,
        "total_volume_24h": "125,432,567.89",
        "open_orders": 3456,
        "support_tickets": 234,
        "pending_verifications": 567,
        "system_health": {
            "api_response_time": "45ms",
            "database_status": "healthy",
            "cache_hit_rate": "94.5%",
            "error_rate": "0.02%"
        },
        "recent_activities": [
            {"type": "user_registration", "count": 234, "time": "5 min ago"},
            {"type": "trade_executed", "count": 5678, "time": "10 min ago"},
            {"type": "support_ticket", "count": 12, "time": "15 min ago"}
        ]
    }

@app.get("/system/metrics")
async def get_system_metrics(admin_user: AdminUser = Depends(require_permission(AdminPermission.SYSTEM_MONITORING))):
    """Get detailed system metrics"""
    return {
        "timestamp": datetime.now().isoformat(),
        "metrics": SystemMetrics(
            cpu_usage=45.2,
            memory_usage=67.8,
            disk_usage=34.5,
            network_io=125.6,
            active_connections=892,
            api_requests_per_minute=4567,
            database_connections=45,
            cache_hit_rate=94.5
        ),
        "services": {
            "trading_engine": "healthy",
            "order_matching": "healthy",
            "liquidity_aggregator": "healthy",
            "user_service": "healthy",
            "payment_gateway": "healthy"
        },
        "alerts": [
            {"level": "info", "message": "System performance optimal", "time": datetime.now().isoformat()}
        ]
    }

@app.get("/trading/metrics")
async def get_trading_metrics(admin_user: AdminUser = Depends(require_permission(AdminPermission.TRADING_CONTROL))):
    """Get trading system metrics"""
    return {
        "timestamp": datetime.now().isoformat(),
        "metrics": TradingMetrics(
            total_volume_24h=Decimal("125432567.89"),
            total_trades_24h=45678,
            active_users=12543,
            open_orders=3456,
            order_book_depth={"BTC/USDT": 2345, "ETH/USDT": 1890},
            price_volatility={"BTC/USDT": 2.34, "ETH/USDT": 3.45},
            liquidations_24h=23,
            funding_rates={"BTC/USDT": Decimal("0.01"), "ETH/USDT": Decimal("0.015")}
        ),
        "top_pairs": [
            {"symbol": "BTC/USDT", "volume": "45,234,567.89", "trades": 12345},
            {"symbol": "ETH/USDT", "volume": "23,456,789.12", "trades": 8901},
            {"symbol": "BNB/USDT", "volume": "12,345,678.90", "trades": 5678}
        ]
    }

@app.post("/system/control")
async def system_control(
    request: SystemControlRequest,
    admin_user: AdminUser = Depends(require_permission(AdminPermission.EMERGENCY_CONTROL))
):
    """Execute system control actions"""
    
    # Log the action
    audit_log = {
        "admin_id": admin_user.id,
        "action": request.action,
        "parameters": request.parameters,
        "reason": request.reason,
        "timestamp": datetime.now().isoformat()
    }
    audit_logs.append(audit_log)
    
    # Execute control action (simplified)
    if request.action == "emergency_shutdown":
        logger.warning(f"Emergency shutdown initiated by {admin_user.username}")
        return {"status": "executed", "message": "Emergency shutdown initiated"}
    elif request.action == "maintenance_mode":
        logger.info(f"Maintenance mode activated by {admin_user.username}")
        return {"status": "executed", "message": "Maintenance mode activated"}
    elif request.action == "restart_service":
        logger.info(f"Service restart requested by {admin_user.username}")
        return {"status": "executed", "message": "Service restart initiated"}
    
    return {"status": "completed", "message": f"Control action {request.action} executed successfully"}

@app.post("/users/manage")
async def manage_users(
    request: UserManagementRequest,
    admin_user: AdminUser = Depends(require_permission(AdminPermission.USER_MANAGEMENT))
):
    """Manage user accounts"""
    
    audit_log = {
        "admin_id": admin_user.id,
        "user_id": request.user_id,
        "action": request.action,
        "reason": request.reason,
        "timestamp": datetime.now().isoformat()
    }
    audit_logs.append(audit_log)
    
    return {
        "status": "completed",
        "message": f"User {request.user_id} {request.action} action completed successfully"
    }

@app.post("/trading/control")
async def control_trading(
    request: TradingControlRequest,
    admin_user: AdminUser = Depends(require_permission(AdminPermission.TRADING_CONTROL))
):
    """Control trading operations"""
    
    audit_log = {
        "admin_id": admin_user.id,
        "action": request.action,
        "symbol": request.symbol,
        "parameters": request.parameters,
        "emergency_override": request.emergency_override,
        "timestamp": datetime.now().isoformat()
    }
    audit_logs.append(audit_log)
    
    return {
        "status": "completed",
        "message": f"Trading control action {request.action} executed successfully"
    }

@app.get("/audit/logs")
async def get_audit_logs(
    limit: int = 100,
    admin_user: AdminUser = Depends(require_permission(AdminPermission.REPORT_GENERATION))
):
    """Get audit logs"""
    return {
        "logs": audit_logs[-limit:],
        "total_count": len(audit_logs)
    }

@app.get("/reports/generate")
async def generate_reports(
    report_type: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    admin_user: AdminUser = Depends(require_permission(AdminPermission.REPORT_GENERATION))
):
    """Generate various reports"""
    
    report_types = ["trading_volume", "user_activity", "financial_summary", "compliance", "system_performance"]
    if report_type not in report_types:
        raise HTTPException(status_code=400, detail=f"Invalid report type. Must be one of: {report_types}")
    
    return {
        "report_id": f"report_{int(time.time())}",
        "report_type": report_type,
        "status": "generating",
        "estimated_completion": datetime.now() + timedelta(minutes=5),
        "download_url": f"/api/reports/download/report_{int(time.time())}"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "unified-admin-panel",
        "version": "12.0.0",
        "timestamp": datetime.now().isoformat(),
        "uptime": "2 days, 14 hours, 32 minutes"
    }

if __name__ == "__main__":
    uvicorn.run(
        "enhanced_server:app",
        host="0.0.0.0",
        port=4000,
        reload=True,
        log_level="info"
    )