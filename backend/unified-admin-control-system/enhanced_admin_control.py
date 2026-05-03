"""
TigerEx Enhanced Unified Admin Control System
Complete admin control with all features for exchange management
Port: 8170
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
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
import jwt
import secrets
import hashlib
from contextlib import asynccontextmanager

# @file enhanced_admin_control.py
# @author TigerEx Development Team
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

# Global connections
db_pool = None
redis_client = None

# Security
security = HTTPBearer()

# ============================================================================
# ENUMS
# ============================================================================

class AdminAction(str, Enum):
    # User Actions
    VIEW_USER = "view_user"
    CREATE_USER = "create_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    SUSPEND_USER = "suspend_user"
    BAN_USER = "ban_user"
    UNSUSPEND_USER = "unsuspend_user"
    UNBAN_USER = "unban_user"
    RESET_PASSWORD = "reset_password"
    MODIFY_BALANCE = "modify_balance"
    FREEZE_BALANCE = "freeze_balance"
    UNFREEZE_BALANCE = "unfreeze_balance"
    
    # Trading Actions
    PAUSE_TRADING = "pause_trading"
    RESUME_TRADING = "resume_trading"
    HALT_ALL_TRADING = "halt_all_trading"
    PAUSE_PAIR = "pause_pair"
    RESUME_PAIR = "resume_pair"
    CANCEL_ORDERS = "cancel_orders"
    FORCE_CLOSE_POSITIONS = "force_close_positions"
    ADJUST_LEVERAGE = "adjust_leverage"
    MODIFY_FEES = "modify_fees"
    
    # Financial Actions
    APPROVE_WITHDRAWAL = "approve_withdrawal"
    REJECT_WITHDRAWAL = "reject_withdrawal"
    PROCESS_DEPOSIT = "process_deposit"
    MANUAL_DEPOSIT = "manual_deposit"
    MANUAL_WITHDRAWAL = "manual_withdrawal"
    SETTLE_FUNDS = "settle_funds"
    
    # System Actions
    SYSTEM_MAINTENANCE = "system_maintenance"
    CLEAR_CACHE = "clear_cache"
    RESTART_SERVICE = "restart_service"
    UPDATE_CONFIG = "update_config"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    EXPORT_DATA = "export_data"

class SystemStatus(str, Enum):
    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"
    DEGRADED = "degraded"
    HALTED = "halted"

class TradingStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    HALTED = "halted"

# ============================================================================
# MODELS
# ============================================================================

class AdminUserCreate(BaseModel):
    email: str
    username: str
    password: str
    role: str
    permissions: List[str] = []

class AdminUserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None

class UserActionRequest(BaseModel):
    user_id: str
    action: AdminAction
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class BalanceAdjustmentRequest(BaseModel):
    user_id: str
    asset: str
    amount: Decimal
    adjustment_type: str  # "add", "subtract", "set"
    reason: str

class TradingControlRequest(BaseModel):
    action: str  # "pause", "resume", "halt"
    trading_type: Optional[str] = None  # "spot", "futures", "margin", "all"
    trading_pair: Optional[str] = None
    reason: str

class FeeUpdateRequest(BaseModel):
    trading_pair: Optional[str] = None
    maker_fee: Optional[Decimal] = None
    taker_fee: Optional[Decimal] = None
    vip_level: Optional[int] = None
    reason: str

class SystemConfigUpdate(BaseModel):
    config_key: str
    config_value: Any
    reason: str

class AuditLogQuery(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    admin_id: Optional[str] = None
    action: Optional[AdminAction] = None
    user_id: Optional[str] = None
    limit: int = 100

# ============================================================================
# LIFESPAN
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool, redis_client
    
    logger.info("Starting Enhanced Admin Control System...")
    
    # Initialize database pool
    db_pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=10,
        max_size=50,
        command_timeout=60
    )
    logger.info("Database pool created")
    
    # Initialize Redis
    redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
    logger.info("Redis client connected")
    
    logger.info("Enhanced Admin Control System started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Enhanced Admin Control System...")
    if db_pool:
        await db_pool.close()
    if redis_client:
        await redis_client.close()

# ============================================================================
# APP
# ============================================================================

app = FastAPI(
    title="TigerEx Enhanced Admin Control System",
    description="Complete admin control with all features",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# AUTHENTICATION & AUTHORIZATION
# ============================================================================

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return admin user"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        admin_id = payload.get("sub")
        role = payload.get("role")
        
        if not admin_id or role not in ["super_admin", "admin", "compliance_officer", "risk_manager", "support_manager"]:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {"admin_id": admin_id, "role": role, "permissions": payload.get("permissions", [])}
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

async def log_audit(admin_id: str, action: AdminAction, target_id: str = None, details: dict = None):
    """Log admin action for audit trail"""
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO admin_audit_log (admin_id, action, target_id, details, created_at)
            VALUES ($1, $2, $3, $4, $5)
        """, admin_id, action.value, target_id, json.dumps(details or {}), datetime.utcnow())

# ============================================================================
# SYSTEM STATUS ENDPOINTS
# ============================================================================

@app.get("/api/admin/system/status")
async def get_system_status(admin: dict = Depends(get_current_admin)):
    """Get overall system status"""
    check_permission(admin, "view_system")
    
    # Get system metrics from Redis
    trading_status = await redis_client.get("system:trading_status") or "active"
    maintenance_mode = await redis_client.get("system:maintenance_mode") == "true"
    
    # Get service health
    services = {}
    service_keys = await redis_client.keys("service:*:health")
    for key in service_keys:
        service_name = key.split(":")[1]
        services[service_name] = await redis_client.get(key)
    
    return {
        "status": SystemStatus.MAINTENANCE if maintenance_mode else SystemStatus.OPERATIONAL,
        "trading_status": trading_status,
        "maintenance_mode": maintenance_mode,
        "services": services,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/admin/system/maintenance")
async def toggle_maintenance(
    enabled: bool,
    reason: str,
    admin: dict = Depends(get_current_admin)
):
    """Toggle system maintenance mode"""
    check_permission(admin, "system_maintenance")
    
    await redis_client.set("system:maintenance_mode", str(enabled).lower())
    await redis_client.set("system:maintenance_reason", reason)
    
    await log_audit(admin["admin_id"], AdminAction.SYSTEM_MAINTENANCE, details={
        "enabled": enabled,
        "reason": reason
    })
    
    return {"success": True, "maintenance_mode": enabled}

@app.post("/api/admin/system/halt")
async def halt_all_operations(
    reason: str,
    admin: dict = Depends(get_current_admin)
):
    """Emergency halt all operations"""
    check_permission(admin, "halt_all_trading")
    
    # Halt all trading
    await redis_client.set("system:trading_status", "halted")
    await redis_client.set("system:halt_reason", reason)
    await redis_client.set("system:halted_at", datetime.utcnow().isoformat())
    await redis_client.set("system:halted_by", admin["admin_id"])
    
    await log_audit(admin["admin_id"], AdminAction.HALT_ALL_TRADING, details={
        "reason": reason
    })
    
    return {
        "success": True,
        "message": "All operations halted",
        "reason": reason,
        "halted_at": datetime.utcnow().isoformat()
    }

# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/admin/users")
async def list_users(
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    status: Optional[str] = None,
    admin: dict = Depends(get_current_admin)
):
    """List all users with pagination and filters"""
    check_permission(admin, "view_users")
    
    offset = (page - 1) * limit
    
    async with db_pool.acquire() as conn:
        query = "SELECT id, email, username, status, kyc_status, created_at FROM users WHERE 1=1"
        params = []
        
        if search:
            query += " AND (email ILIKE $1 OR username ILIKE $1)"
            params.append(f"%{search}%")
        
        if status:
            query += f" AND status = ${len(params) + 1}"
            params.append(status)
        
        query += f" ORDER BY created_at DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
        params.extend([limit, offset])
        
        users = await conn.fetch(query, *params)
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM users WHERE 1=1"
        count_params = []
        if search:
            count_query += " AND (email ILIKE $1 OR username ILIKE $1)"
            count_params.append(f"%{search}%")
        if status:
            count_query += f" AND status = ${len(count_params) + 1}"
            count_params.append(status)
        
        total = await conn.fetchval(count_query, *count_params)
        
        return {
            "users": [dict(u) for u in users],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }

@app.get("/api/admin/users/{user_id}")
async def get_user_details(
    user_id: str,
    admin: dict = Depends(get_current_admin)
):
    """Get detailed user information"""
    check_permission(admin, "view_user_details")
    
    async with db_pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE id = $1", user_id
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get balances
        balances = await conn.fetch(
            "SELECT asset, available, frozen, total FROM balances WHERE user_id = $1", user_id
        )
        
        # Get recent orders
        orders = await conn.fetch(
            """SELECT * FROM orders WHERE user_id = $1 
               ORDER BY created_at DESC LIMIT 20""", user_id
        )
        
        # Get recent transactions
        transactions = await conn.fetch(
            """SELECT * FROM transactions WHERE user_id = $1 
               ORDER BY created_at DESC LIMIT 20""", user_id
        )
        
        return {
            "user": dict(user),
            "balances": [dict(b) for b in balances],
            "recent_orders": [dict(o) for o in orders],
            "recent_transactions": [dict(t) for t in transactions]
        }

@app.post("/api/admin/users/{user_id}/suspend")
async def suspend_user(
    user_id: str,
    reason: str,
    duration_hours: Optional[int] = None,
    admin: dict = Depends(get_current_admin)
):
    """Suspend a user account"""
    check_permission(admin, "suspend_users")
    
    async with db_pool.acquire() as conn:
        suspension_end = None
        if duration_hours:
            suspension_end = datetime.utcnow() + timedelta(hours=duration_hours)
        
        await conn.execute("""
            UPDATE users SET status = 'suspended', 
            suspension_reason = $1, 
            suspended_until = $2,
            suspended_at = $3,
            suspended_by = $4
            WHERE id = $5
        """, reason, suspension_end, datetime.utcnow(), admin["admin_id"], user_id)
        
        # Invalidate user sessions
        await redis_client.delete(f"user:session:{user_id}")
    
    await log_audit(admin["admin_id"], AdminAction.SUSPEND_USER, user_id, {
        "reason": reason,
        "duration_hours": duration_hours
    })
    
    return {"success": True, "message": "User suspended", "suspended_until": suspension_end}

@app.post("/api/admin/users/{user_id}/ban")
async def ban_user(
    user_id: str,
    reason: str,
    admin: dict = Depends(get_current_admin)
):
    """Ban a user account permanently"""
    check_permission(admin, "ban_users")
    
    async with db_pool.acquire() as conn:
        await conn.execute("""
            UPDATE users SET status = 'banned', 
            ban_reason = $1,
            banned_at = $2,
            banned_by = $3
            WHERE id = $4
        """, reason, datetime.utcnow(), admin["admin_id"], user_id)
        
        # Invalidate all user sessions
        await redis_client.delete(f"user:session:{user_id}")
    
    await log_audit(admin["admin_id"], AdminAction.BAN_USER, user_id, {
        "reason": reason
    })
    
    return {"success": True, "message": "User banned"}

@app.post("/api/admin/users/{user_id}/unsuspend")
async def unsuspend_user(
    user_id: str,
    admin: dict = Depends(get_current_admin)
):
    """Unsuspend a user account"""
    check_permission(admin, "unsuspend_user")
    
    async with db_pool.acquire() as conn:
        await conn.execute("""
            UPDATE users SET status = 'active', 
            suspension_reason = NULL,
            suspended_until = NULL,
            unsuspended_at = $1,
            unsuspended_by = $2
            WHERE id = $3
        """, datetime.utcnow(), admin["admin_id"], user_id)
    
    await log_audit(admin["admin_id"], AdminAction.UNSUSPEND_USER, user_id)
    
    return {"success": True, "message": "User unsuspended"}

# ============================================================================
# BALANCE MANAGEMENT
# ============================================================================

@app.post("/api/admin/balances/adjust")
async def adjust_user_balance(
    request: BalanceAdjustmentRequest,
    admin: dict = Depends(get_current_admin)
):
    """Adjust user balance"""
    check_permission(admin, "modify_balance")
    
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            # Get current balance
            current = await conn.fetchrow(
                "SELECT available, frozen, total FROM balances WHERE user_id = $1 AND asset = $2",
                request.user_id, request.asset
            )
            
            if not current:
                if request.adjustment_type == "add":
                    # Create new balance
                    await conn.execute("""
                        INSERT INTO balances (user_id, asset, available, frozen, total)
                        VALUES ($1, $2, $3, 0, $3)
                    """, request.user_id, request.asset, request.amount)
                else:
                    raise HTTPException(status_code=400, detail="Balance not found")
            else:
                new_available = current["available"]
                
                if request.adjustment_type == "add":
                    new_available += request.amount
                elif request.adjustment_type == "subtract":
                    if current["available"] < request.amount:
                        raise HTTPException(status_code=400, detail="Insufficient balance")
                    new_available -= request.amount
                elif request.adjustment_type == "set":
                    new_available = request.amount
                
                await conn.execute("""
                    UPDATE balances SET available = $1, total = $1 + frozen
                    WHERE user_id = $2 AND asset = $3
                """, new_available, request.user_id, request.asset)
            
            # Log transaction
            await conn.execute("""
                INSERT INTO admin_balance_adjustments 
                (admin_id, user_id, asset, amount, adjustment_type, reason, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, admin["admin_id"], request.user_id, request.asset, 
                request.amount, request.adjustment_type, request.reason, datetime.utcnow())
    
    await log_audit(admin["admin_id"], AdminAction.MODIFY_BALANCE, request.user_id, {
        "asset": request.asset,
        "amount": str(request.amount),
        "type": request.adjustment_type,
        "reason": request.reason
    })
    
    return {"success": True, "message": "Balance adjusted"}

@app.post("/api/admin/balances/freeze")
async def freeze_balance(
    user_id: str,
    asset: str,
    amount: Decimal,
    reason: str,
    admin: dict = Depends(get_current_admin)
):
    """Freeze user balance"""
    check_permission(admin, "freeze_balance")
    
    async with db_pool.acquire() as conn:
        result = await conn.execute("""
            UPDATE balances SET 
            available = available - $1,
            frozen = frozen + $1
            WHERE user_id = $2 AND asset = $3 AND available >= $1
        """, amount, user_id, asset)
        
        if result == "UPDATE 0":
            raise HTTPException(status_code=400, detail="Insufficient available balance")
    
    await log_audit(admin["admin_id"], AdminAction.FREEZE_BALANCE, user_id, {
        "asset": asset, "amount": str(amount), "reason": reason
    })
    
    return {"success": True, "message": "Balance frozen"}

# ============================================================================
# TRADING CONTROL
# ============================================================================

@app.post("/api/admin/trading/control")
async def control_trading(
    request: TradingControlRequest,
    admin: dict = Depends(get_current_admin)
):
    """Control trading operations"""
    action_map = {
        "pause": AdminAction.PAUSE_TRADING,
        "resume": AdminAction.RESUME_TRADING,
        "halt": AdminAction.HALT_ALL_TRADING
    }
    
    check_permission(admin, request.action + "_trading")
    
    if request.trading_pair:
        key = f"trading:pair:{request.trading_pair}:status"
    elif request.trading_type:
        key = f"trading:{request.trading_type}:status"
    else:
        key = "trading:global:status"
    
    await redis_client.set(key, request.action)
    await redis_client.set(f"{key}:reason", request.reason)
    await redis_client.set(f"{key}:updated_at", datetime.utcnow().isoformat())
    await redis_client.set(f"{key}:updated_by", admin["admin_id"])
    
    await log_audit(admin["admin_id"], action_map.get(request.action, AdminAction.CONTROL_TRADING), 
                    details={
                        "trading_type": request.trading_type,
                        "trading_pair": request.trading_pair,
                        "action": request.action,
                        "reason": request.reason
                    })
    
    return {"success": True, "message": f"Trading {request.action}ed"}

@app.post("/api/admin/trading/cancel-orders")
async def cancel_orders(
    user_id: Optional[str] = None,
    trading_pair: Optional[str] = None,
    order_type: Optional[str] = None,
    admin: dict = Depends(get_current_admin)
):
    """Cancel orders (batch or individual)"""
    check_permission(admin, "cancel_orders")
    
    cancelled_count = 0
    
    async with db_pool.acquire() as conn:
        query = "SELECT id, user_id, trading_pair FROM orders WHERE status = 'open'"
        params = []
        
        if user_id:
            query += f" AND user_id = ${len(params) + 1}"
            params.append(user_id)
        if trading_pair:
            query += f" AND trading_pair = ${len(params) + 1}"
            params.append(trading_pair)
        if order_type:
            query += f" AND order_type = ${len(params) + 1}"
            params.append(order_type)
        
        orders = await conn.fetch(query, *params)
        
        for order in orders:
            await conn.execute(
                "UPDATE orders SET status = 'cancelled', cancelled_at = $1, cancelled_by = $2 WHERE id = $3",
                datetime.utcnow(), admin["admin_id"], order["id"]
            )
            cancelled_count += 1
            
            # Publish cancellation event
            await redis_client.publish(f"order:cancelled:{order['user_id']}", order["id"])
    
    await log_audit(admin["admin_id"], AdminAction.CANCEL_ORDERS, details={
        "user_id": user_id,
        "trading_pair": trading_pair,
        "order_type": order_type,
        "cancelled_count": cancelled_count
    })
    
    return {"success": True, "cancelled_count": cancelled_count}

@app.post("/api/admin/trading/force-close-positions")
async def force_close_positions(
    user_id: Optional[str] = None,
    trading_pair: Optional[str] = None,
    admin: dict = Depends(get_current_admin)
):
    """Force close positions"""
    check_permission(admin, "force_close_positions")
    
    closed_count = 0
    
    async with db_pool.acquire() as conn:
        query = "SELECT id, user_id, trading_pair, size FROM positions WHERE status = 'open'"
        params = []
        
        if user_id:
            query += f" AND user_id = ${len(params) + 1}"
            params.append(user_id)
        if trading_pair:
            query += f" AND trading_pair = ${len(params) + 1}"
            params.append(trading_pair)
        
        positions = await conn.fetch(query, *params)
        
        for position in positions:
            # Create closing order
            await conn.execute("""
                UPDATE positions SET status = 'closed', closed_at = $1, closed_by = $2
                WHERE id = $3
            """, datetime.utcnow(), admin["admin_id"], position["id"])
            closed_count += 1
    
    await log_audit(admin["admin_id"], AdminAction.FORCE_CLOSE_POSITIONS, details={
        "user_id": user_id,
        "trading_pair": trading_pair,
        "closed_count": closed_count
    })
    
    return {"success": True, "closed_count": closed_count}

# ============================================================================
# FEE MANAGEMENT
# ============================================================================

@app.post("/api/admin/fees/update")
async def update_fees(
    request: FeeUpdateRequest,
    admin: dict = Depends(get_current_admin)
):
    """Update trading fees"""
    check_permission(admin, "modify_fees")
    
    async with db_pool.acquire() as conn:
        if request.vip_level:
            await conn.execute("""
                UPDATE vip_fee_tiers 
                SET maker_fee = $1, taker_fee = $2, updated_at = $3, updated_by = $4
                WHERE level = $5
            """, request.maker_fee, request.taker_fee, datetime.utcnow(), 
                admin["admin_id"], request.vip_level)
        elif request.trading_pair:
            await conn.execute("""
                UPDATE trading_pairs 
                SET maker_fee = $1, taker_fee = $2, updated_at = $3, updated_by = $4
                WHERE symbol = $5
            """, request.maker_fee, request.taker_fee, datetime.utcnow(),
                admin["admin_id"], request.trading_pair)
        else:
            # Update global fees
            await redis_client.set("fees:global:maker", str(request.maker_fee))
            await redis_client.set("fees:global:taker", str(request.taker_fee))
    
    await log_audit(admin["admin_id"], AdminAction.MODIFY_FEES, details={
        "trading_pair": request.trading_pair,
        "vip_level": request.vip_level,
        "maker_fee": str(request.maker_fee),
        "taker_fee": str(request.taker_fee),
        "reason": request.reason
    })
    
    return {"success": True, "message": "Fees updated"}

# ============================================================================
# AUDIT LOGS
# ============================================================================

@app.get("/api/admin/audit-logs")
async def get_audit_logs(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    admin_id: Optional[str] = None,
    action: Optional[str] = None,
    user_id: Optional[str] = None,
    page: int = 1,
    limit: int = 100,
    admin: dict = Depends(get_current_admin)
):
    """Get admin audit logs"""
    check_permission(admin, "view_audit_logs")
    
    offset = (page - 1) * limit
    
    async with db_pool.acquire() as conn:
        query = "SELECT * FROM admin_audit_log WHERE 1=1"
        params = []
        
        if start_date:
            query += f" AND created_at >= ${len(params) + 1}"
            params.append(start_date)
        if end_date:
            query += f" AND created_at <= ${len(params) + 1}"
            params.append(end_date)
        if admin_id:
            query += f" AND admin_id = ${len(params) + 1}"
            params.append(admin_id)
        if action:
            query += f" AND action = ${len(params) + 1}"
            params.append(action)
        if user_id:
            query += f" AND target_id = ${len(params) + 1}"
            params.append(user_id)
        
        query += f" ORDER BY created_at DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
        params.extend([limit, offset])
        
        logs = await conn.fetch(query, *params)
        
        return {
            "logs": [dict(l) for l in logs],
            "pagination": {
                "page": page,
                "limit": limit
            }
        }

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "enhanced-admin-control",
        "version": "2.0.0"
    }

@app.get("/")
async def root():
    return {
        "service": "TigerEx Enhanced Admin Control System",
        "version": "2.0.0",
        "endpoints": {
            "system": "/api/admin/system",
            "users": "/api/admin/users",
            "balances": "/api/admin/balances",
            "trading": "/api/admin/trading",
            "fees": "/api/admin/fees",
            "audit": "/api/admin/audit-logs"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8170)def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
