"""
TigerEx Unified Admin Dashboard Service
Complete admin control panel for all exchange operations
Version: 2.0.0 - Production Ready
"""

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import jwt
import logging
import asyncio
import json
import asyncpg
import aioredis
from dataclasses import dataclass
import uuid
import hashlib

# @file unified_admin_dashboard.py
# @author TigerEx Development Team
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DATABASE_URL = "postgresql://tigerex:password@localhost/tigerex"
REDIS_URL = "redis://localhost:6379"
SECRET_KEY = "your-super-secret-key-change-in-production"
ALGORITHM = "HS256"

# FastAPI App
app = FastAPI(
    title="TigerEx Unified Admin Dashboard",
    version="2.0.0",
    description="Complete admin control panel for all exchange operations"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# ============================================================================
# ENUMS
# ============================================================================

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    SUPPORT = "support"
    COMPLIANCE = "compliance"
    RISK_MANAGER = "risk_manager"
    TRADER = "trader"
    USER = "user"

class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    PENDING = "pending"

class ServiceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    DEGRADED = "degraded"

class TradingStatus(str, Enum):
    OPEN = "open"
    HALTED = "halted"
    PAUSED = "paused"
    CLOSED = "closed"

class WithdrawalStatus(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    MANUAL_REVIEW = "manual_review"

class DepositStatus(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"

class KYCStatus(str, Enum):
    NOT_SUBMITTED = "not_submitted"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class AdminUser(BaseModel):
    user_id: str
    username: str
    email: str
    role: UserRole
    permissions: List[str] = []
    is_active: bool = True
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None

class SystemConfig(BaseModel):
    maintenance_mode: bool = False
    registration_enabled: bool = True
    trading_enabled: bool = True
    withdrawals_enabled: bool = True
    deposits_enabled: bool = True
    kyc_required: bool = True
    max_withdrawal_daily: float = 100000.0
    max_deposit_daily: float = 1000000.0
    min_trade_amount: float = 0.001
    trading_fee: float = 0.001

class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    kyc_status: Optional[KYCStatus] = None
    is_active: Optional[bool] = None

class TradingPairUpdate(BaseModel):
    pair_id: str
    status: Optional[TradingStatus] = None
    trading_enabled: Optional[bool] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    maker_fee: Optional[float] = None
    taker_fee: Optional[float] = None

class WithdrawalApproval(BaseModel):
    withdrawal_id: str
    action: str  # approve, reject
    reason: Optional[str] = None

class AnnouncementCreate(BaseModel):
    title: str
    content: str
    category: str = "general"
    priority: str = "normal"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class AuditLogFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: Optional[str] = None
    action: Optional[str] = None
    category: Optional[str] = None
    limit: int = 100

# ============================================================================
# DATABASE MANAGER
# ============================================================================

class DatabaseManager:
    """Database connection manager"""
    
    _pool: Optional[asyncpg.Pool] = None
    _redis: Optional[aioredis.Redis] = None
    
    @classmethod
    async def get_pool(cls) -> asyncpg.Pool:
        if cls._pool is None:
            cls._pool = await asyncpg.create_pool(DATABASE_URL, min_size=5, max_size=50)
        return cls._pool
    
    @classmethod
    async def get_redis(cls) -> aioredis.Redis:
        if cls._redis is None:
            cls._redis = await aioredis.from_url(REDIS_URL)
        return cls._redis
    
    @classmethod
    async def close(cls):
        if cls._pool:
            await cls._pool.close()
        if cls._redis:
            await cls._redis.close()

# ============================================================================
# AUTHENTICATION & AUTHORIZATION
# ============================================================================

async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> AdminUser:
    """Verify admin token and return admin user"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        role = payload.get("role")
        
        if not user_id or role not in [r.value for r in UserRole]:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Check if user is admin
        if role not in [UserRole.SUPER_ADMIN.value, UserRole.ADMIN.value, 
                        UserRole.MODERATOR.value, UserRole.SUPPORT.value,
                        UserRole.COMPLIANCE.value, UserRole.RISK_MANAGER.value]:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        return AdminUser(
            user_id=user_id,
            username=payload.get("username", ""),
            email=payload.get("email", ""),
            role=UserRole(role),
            permissions=payload.get("permissions", []),
            is_active=True
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_permission(permission: str):
    """Decorator to check if admin has required permission"""
    async def permission_checker(admin: AdminUser = Depends(get_current_admin)):
        if admin.role == UserRole.SUPER_ADMIN:
            return admin
        if permission not in admin.permissions and admin.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail=f"Permission '{permission}' required")
        return admin
    return permission_checker

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def log_audit(admin_id: str, action: str, category: str, details: Dict):
    """Log admin action to audit trail"""
    try:
        pool = await DatabaseManager.get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO admin_audit_log 
                   (log_id, admin_id, action, category, details, timestamp)
                   VALUES ($1, $2, $3, $4, $5, $6)""",
                str(uuid.uuid4()), admin_id, action, category, json.dumps(details), datetime.utcnow()
            )
    except Exception as e:
        logger.error(f"Error logging audit: {e}")

async def cache_get(key: str) -> Optional[Any]:
    """Get value from cache"""
    try:
        redis = await DatabaseManager.get_redis()
        value = await redis.get(key)
        return json.loads(value) if value else None
    except Exception as e:
        logger.error(f"Cache get error: {e}")
        return None

async def cache_set(key: str, value: Any, expire: int = 300):
    """Set value in cache"""
    try:
        redis = await DatabaseManager.get_redis()
        await redis.setex(key, expire, json.dumps(value, default=str))
    except Exception as e:
        logger.error(f"Cache set error: {e}")

async def cache_delete(key: str):
    """Delete value from cache"""
    try:
        redis = await DatabaseManager.get_redis()
        await redis.delete(key)
    except Exception as e:
        logger.error(f"Cache delete error: {e}")

# ============================================================================
# DASHBOARD OVERVIEW ENDPOINTS
# ============================================================================

@app.get("/api/admin/dashboard/overview")
async def get_dashboard_overview(admin: AdminUser = Depends(get_current_admin)):
    """Get comprehensive dashboard overview"""
    try:
        pool = await DatabaseManager.get_pool()
        
        # Check cache first
        cache_key = f"admin_dashboard:{admin.user_id}"
        cached = await cache_get(cache_key)
        if cached:
            return cached
        
        async with pool.acquire() as conn:
            # Get all statistics in parallel
            stats = {}
            
            # User statistics
            stats['users'] = {
                'total': await conn.fetchval("SELECT COUNT(*) FROM users"),
                'active': await conn.fetchval("SELECT COUNT(*) FROM users WHERE is_active = TRUE"),
                'verified': await conn.fetchval("SELECT COUNT(*) FROM users WHERE email_verified = TRUE"),
                'new_today': await conn.fetchval(
                    "SELECT COUNT(*) FROM users WHERE created_at >= CURRENT_DATE"
                ),
            }
            
            # Trading statistics
            stats['trading'] = {
                'total_volume_24h': float(await conn.fetchval(
                    "SELECT COALESCE(SUM(volume), 0) FROM trades WHERE created_at >= NOW() - INTERVAL '24 hours'"
                ) or 0),
                'total_trades_24h': await conn.fetchval(
                    "SELECT COUNT(*) FROM trades WHERE created_at >= NOW() - INTERVAL '24 hours'"
                ),
                'active_pairs': await conn.fetchval(
                    "SELECT COUNT(*) FROM trading_pairs WHERE status = 'active'"
                ),
                'open_orders': await conn.fetchval(
                    "SELECT COUNT(*) FROM orders WHERE status IN ('pending', 'open')"
                ),
            }
            
            # Financial statistics
            stats['financial'] = {
                'total_balances': float(await conn.fetchval(
                    "SELECT COALESCE(SUM(balance), 0) FROM user_balances"
                ) or 0),
                'pending_withdrawals': await conn.fetchval(
                    "SELECT COUNT(*) FROM withdrawals WHERE status = 'pending'"
                ),
                'pending_deposits': await conn.fetchval(
                    "SELECT COUNT(*) FROM deposits WHERE status = 'pending'"
                ),
                'total_fees_24h': float(await conn.fetchval(
                    "SELECT COALESCE(SUM(fee), 0) FROM trades WHERE created_at >= NOW() - INTERVAL '24 hours'"
                ) or 0),
            }
            
            # KYC statistics
            stats['kyc'] = {
                'pending': await conn.fetchval(
                    "SELECT COUNT(*) FROM users WHERE kyc_status = 'pending'"
                ),
                'approved': await conn.fetchval(
                    "SELECT COUNT(*) FROM users WHERE kyc_status = 'approved'"
                ),
                'rejected': await conn.fetchval(
                    "SELECT COUNT(*) FROM users WHERE kyc_status = 'rejected'"
                ),
            }
            
            # System health
            services = await conn.fetch(
                """SELECT service_name, status, last_check FROM service_health"""
            )
            stats['services'] = [dict(s) for s in services]
            
            # Recent activities
            recent_activities = await conn.fetch(
                """SELECT * FROM admin_audit_log ORDER BY timestamp DESC LIMIT 10"""
            )
            stats['recent_activities'] = [dict(a) for a in recent_activities]
            
            result = {
                "success": True,
                "timestamp": datetime.utcnow().isoformat(),
                "statistics": stats
            }
            
            # Cache for 30 seconds
            await cache_set(cache_key, result, 30)
            
            return result
            
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/admin/users")
async def get_users(
    skip: int = 0,
    limit: int = 50,
    status: Optional[UserStatus] = None,
    role: Optional[UserRole] = None,
    search: Optional[str] = None,
    admin: AdminUser = Depends(require_permission("user:view"))
):
    """Get list of users with filtering"""
    try:
        pool = await DatabaseManager.get_pool()
        
        query = "SELECT * FROM users WHERE 1=1"
        params = []
        
        if status:
            query += f" AND status = ${len(params)+1}"
            params.append(status.value)
        
        if role:
            query += f" AND role = ${len(params)+1}"
            params.append(role.value)
        
        if search:
            query += f" AND (email ILIKE ${len(params)+1} OR username ILIKE ${len(params)+1})"
            params.append(f"%{search}%")
        
        query += f" ORDER BY created_at DESC LIMIT ${len(params)+1} OFFSET ${len(params)+2}"
        params.extend([limit, skip])
        
        async with pool.acquire() as conn:
            users = await conn.fetch(query, *params)
            total = await conn.fetchval("SELECT COUNT(*) FROM users")
        
        await log_audit(admin.user_id, "VIEW_USERS", "user_management", {
            "filters": {"status": status, "role": role, "search": search}
        })
        
        return {
            "success": True,
            "users": [dict(u) for u in users],
            "pagination": {
                "total": total,
                "skip": skip,
                "limit": limit
            }
        }
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/users/{user_id}")
async def get_user_detail(
    user_id: str,
    admin: AdminUser = Depends(require_permission("user:view"))
):
    """Get detailed user information"""
    try:
        pool = await DatabaseManager.get_pool()
        
        async with pool.acquire() as conn:
            user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get user balances
            balances = await conn.fetch(
                "SELECT * FROM user_balances WHERE user_id = $1", user_id
            )
            
            # Get user orders
            orders = await conn.fetch(
                """SELECT * FROM orders WHERE user_id = $1 
                   ORDER BY created_at DESC LIMIT 20""", user_id
            )
            
            # Get user trades
            trades = await conn.fetch(
                """SELECT * FROM trades WHERE buyer_id = $1 OR seller_id = $1 
                   ORDER BY created_at DESC LIMIT 20""", user_id
            )
            
            # Get user KYC info
            kyc = await conn.fetchrow(
                "SELECT * FROM kyc_documents WHERE user_id = $1", user_id
            )
            
            # Get user sessions
            sessions = await conn.fetch(
                """SELECT * FROM user_sessions WHERE user_id = $1 
                   ORDER BY created_at DESC LIMIT 10""", user_id
            )
            
            await log_audit(admin.user_id, "VIEW_USER_DETAIL", "user_management", {
                "target_user_id": user_id
            })
            
            return {
                "success": True,
                "user": dict(user),
                "balances": [dict(b) for b in balances],
                "orders": [dict(o) for o in orders],
                "trades": [dict(t) for t in trades],
                "kyc": dict(kyc) if kyc else None,
                "sessions": [dict(s) for s in sessions]
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/admin/users/{user_id}")
async def update_user(
    user_id: str,
    update_data: UserUpdate,
    admin: AdminUser = Depends(require_permission("user:update"))
):
    """Update user information"""
    try:
        pool = await DatabaseManager.get_pool()
        
        async with pool.acquire() as conn:
            user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Build update query
            updates = []
            params = []
            
            if update_data.email:
                updates.append(f"email = ${len(params)+1}")
                params.append(update_data.email)
            
            if update_data.username:
                updates.append(f"username = ${len(params)+1}")
                params.append(update_data.username)
            
            if update_data.role:
                updates.append(f"role = ${len(params)+1}")
                params.append(update_data.role.value)
            
            if update_data.status:
                updates.append(f"status = ${len(params)+1}")
                params.append(update_data.status.value)
            
            if update_data.kyc_status:
                updates.append(f"kyc_status = ${len(params)+1}")
                params.append(update_data.kyc_status.value)
            
            if update_data.is_active is not None:
                updates.append(f"is_active = ${len(params)+1}")
                params.append(update_data.is_active)
            
            if updates:
                updates.append(f"updated_at = ${len(params)+1}")
                params.append(datetime.utcnow())
                params.append(user_id)
                
                await conn.execute(
                    f"UPDATE users SET {', '.join(updates)} WHERE id = ${len(params)}",
                    *params
                )
        
        await log_audit(admin.user_id, "UPDATE_USER", "user_management", {
            "target_user_id": user_id,
            "updates": update_data.dict()
        })
        
        return {
            "success": True,
            "message": f"User {user_id} updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/users/{user_id}/suspend")
async def suspend_user(
    user_id: str,
    reason: str = "No reason provided",
    duration: Optional[int] = None,  # Duration in hours
    admin: AdminUser = Depends(require_permission("user:suspend"))
):
    """Suspend user account"""
    try:
        pool = await DatabaseManager.get_pool()
        
        async with pool.acquire() as conn:
            user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Calculate suspension end time
            suspended_until = None
            if duration:
                suspended_until = datetime.utcnow() + timedelta(hours=duration)
            
            await conn.execute(
                """UPDATE users SET status = 'suspended', suspended_at = $1, 
                    suspended_until = $2, suspension_reason = $3 WHERE id = $4""",
                datetime.utcnow(), suspended_until, reason, user_id
            )
            
            # Invalidate all user sessions
            await conn.execute(
                "UPDATE user_sessions SET is_active = FALSE WHERE user_id = $1", user_id
            )
        
        await log_audit(admin.user_id, "SUSPEND_USER", "user_management", {
            "target_user_id": user_id,
            "reason": reason,
            "duration": duration
        })
        
        return {
            "success": True,
            "message": f"User {user_id} suspended successfully",
            "suspended_until": suspended_until.isoformat() if suspended_until else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error suspending user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    admin: AdminUser = Depends(require_permission("user:update"))
):
    """Activate user account"""
    try:
        pool = await DatabaseManager.get_pool()
        
        async with pool.acquire() as conn:
            user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            await conn.execute(
                """UPDATE users SET status = 'active', suspended_at = NULL, 
                    suspended_until = NULL, suspension_reason = NULL WHERE id = $1""",
                user_id
            )
        
        await log_audit(admin.user_id, "ACTIVATE_USER", "user_management", {
            "target_user_id": user_id
        })
        
        return {
            "success": True,
            "message": f"User {user_id} activated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    admin: AdminUser = Depends(require_permission("user:delete"))
):
    """Delete user account (soft delete)"""
    try:
        pool = await DatabaseManager.get_pool()
        
        async with pool.acquire() as conn:
            user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Soft delete - mark as deleted instead of removing
            await conn.execute(
                """UPDATE users SET status = 'deleted', deleted_at = $1, 
                    email = 'deleted_' || email, username = 'deleted_' || username 
                    WHERE id = $2""",
                datetime.utcnow(), user_id
            )
            
            # Invalidate sessions
            await conn.execute(
                "UPDATE user_sessions SET is_active = FALSE WHERE user_id = $1", user_id
            )
        
        await log_audit(admin.user_id, "DELETE_USER", "user_management", {
            "target_user_id": user_id
        })
        
        return {
            "success": True,
            "message": f"User {user_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TRADING MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/admin/trading/pairs")
async def get_trading_pairs(
    status: Optional[TradingStatus] = None,
    admin: AdminUser = Depends(require_permission("trading:view"))
):
    """Get all trading pairs"""
    try:
        pool = await DatabaseManager.get_pool()
        
        async with pool.acquire() as conn:
            query = "SELECT * FROM trading_pairs"
            if status:
                query += f" WHERE status = '{status.value}'"
            query += " ORDER BY symbol"
            
            pairs = await conn.fetch(query)
        
        return {
            "success": True,
            "pairs": [dict(p) for p in pairs]
        }
    except Exception as e:
        logger.error(f"Error getting trading pairs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/admin/trading/pairs/{pair_id}")
async def update_trading_pair(
    pair_id: str,
    update_data: TradingPairUpdate,
    admin: AdminUser = Depends(require_permission("trading:manage"))
):
    """Update trading pair settings"""
    try:
        pool = await DatabaseManager.get_pool()
        
        async with pool.acquire() as conn:
            pair = await conn.fetchrow(
                "SELECT * FROM trading_pairs WHERE pair_id = $1", pair_id
            )
            if not pair:
                raise HTTPException(status_code=404, detail="Trading pair not found")
            
            # Build update query
            updates = ["updated_at = $1"]
            params = [datetime.utcnow()]
            
            if update_data.status:
                updates.append(f"status = ${len(params)+1}")
                params.append(update_data.status.value)
            
            if update_data.trading_enabled is not None:
                updates.append(f"trading_enabled = ${len(params)+1}")
                params.append(update_data.trading_enabled)
            
            if update_data.min_price:
                updates.append(f"min_price = ${len(params)+1}")
                params.append(update_data.min_price)
            
            if update_data.max_price:
                updates.append(f"max_price = ${len(params)+1}")
                params.append(update_data.max_price)
            
            if update_data.maker_fee:
                updates.append(f"maker_fee = ${len(params)+1}")
                params.append(update_data.maker_fee)
            
            if update_data.taker_fee:
                updates.append(f"taker_fee = ${len(params)+1}")
                params.append(update_data.taker_fee)
            
            params.append(pair_id)
            
            await conn.execute(
                f"UPDATE trading_pairs SET {', '.join(updates)} WHERE pair_id = ${len(params)}",
                *params
            )
        
        await log_audit(admin.user_id, "UPDATE_TRADING_PAIR", "trading", {
            "pair_id": pair_id,
            "updates": update_data.dict()
        })
        
        return {
            "success": True,
            "message": f"Trading pair {pair_id} updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating trading pair: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/trading/halt")
async def halt_trading(
    reason: str = "No reason provided",
    pairs: Optional[List[str]] = None,  # If None, halt all
    admin: AdminUser = Depends(require_permission("trading:halt"))
):
    """Halt trading for specific pairs or all pairs"""
    try:
        pool = await DatabaseManager.get_pool()
        
        async with pool.acquire() as conn:
            if pairs:
                # Halt specific pairs
                await conn.execute(
                    f"""UPDATE trading_pairs SET status = 'halted', halted_at = $1, 
                        halt_reason = $2 WHERE pair_id = ANY($3)""",
                    datetime.utcnow(), reason, pairs
                )
            else:
                # Halt all pairs
                await conn.execute(
                    """UPDATE trading_pairs SET status = 'halted', halted_at = $1, 
                        halt_reason = $2 WHERE status = 'active'""",
                    datetime.utcnow(), reason
                )
        
        await log_audit(admin.user_id, "HALT_TRADING", "trading", {
            "reason": reason,
            "pairs": pairs
        })
        
        return {
            "success": True,
            "message": "Trading halted successfully",
            "halted_pairs": pairs if pairs else "all"
        }
    except Exception as e:
        logger.error(f"Error halting trading: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/trading/resume")
async def resume_trading(
    pairs: Optional[List[str]] = None,  # If None, resume all halted
    admin: AdminUser = Depends(require_permission("trading:halt"))
):
    """Resume trading for halted pairs"""
    try:
        pool = await DatabaseManager.get_pool()
        
        async with pool.acquire() as conn:
            if pairs:
                await conn.execute(
                    """UPDATE trading_pairs SET status = 'active', halted_at = NULL, 
                        halt_reason = NULL WHERE pair_id = ANY($1)""",
                    pairs
                )
            else:
                await conn.execute(
                    """UPDATE trading_pairs SET status = 'active', halted_at = NULL, 
                        halt_reason = NULL WHERE status = 'halted'"""
                )
        
        await log_audit(admin.user_id, "RESUME_TRADING", "trading", {
            "pairs": pairs
        })
        
        return {
            "success": True,
            "message": "Trading resumed successfully"
        }
    except Exception as e:
        logger.error(f"Error resuming trading: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# WITHDRAWAL MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/admin/withdrawals/pending")
async def get_pending_withdrawals(
    limit: int = 100,
    admin: AdminUser = Depends(require_permission("withdrawal:approve"))
):
    """Get pending withdrawals for approval"""
    try:
        pool = await DatabaseManager.get_pool()
        
        async with pool.acquire() as conn:
            withdrawals = await conn.fetch(
                """SELECT w.*, u.email, u.username FROM withdrawals w 
                   JOIN users u ON w.user_id = u.id 
                   WHERE w.status = 'pending' 
                   ORDER BY w.created_at ASC LIMIT $1""",
                limit
            )
        
        return {
            "success": True,
            "withdrawals": [dict(w) for w in withdrawals]
        }
    except Exception as e:
        logger.error(f"Error getting pending withdrawals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/withdrawals/approve")
async def approve_withdrawal(
    approval: WithdrawalApproval,
    admin: AdminUser = Depends(require_permission("withdrawal:approve"))
):
    """Approve or reject a withdrawal"""
    try:
        pool = await DatabaseManager.get_pool()
        
        async with pool.acquire() as conn:
            withdrawal = await conn.fetchrow(
                "SELECT * FROM withdrawals WHERE id = $1", approval.withdrawal_id
            )
            if not withdrawal:
                raise HTTPException(status_code=404, detail="Withdrawal not found")
            
            if withdrawal['status'] != 'pending':
                raise HTTPException(status_code=400, detail="Withdrawal already processed")
            
            new_status = 'approved' if approval.action == 'approve' else 'rejected'
            
            await conn.execute(
                """UPDATE withdrawals SET status = $1, processed_by = $2, 
                    processed_at = $3, process_reason = $4 WHERE id = $5""",
                new_status, admin.user_id, datetime.utcnow(), 
                approval.reason, approval.withdrawal_id
            )
            
            if approval.action == 'approve':
                # Trigger withdrawal processing
                await conn.execute(
                    """INSERT INTO withdrawal_queue (withdrawal_id, status, created_at)
                       VALUES ($1, 'pending', $2)""",
                    approval.withdrawal_id, datetime.utcnow()
                )
        
        await log_audit(admin.user_id, f"WITHDRAWAL_{approval.action.upper()}", "withdrawals", {
            "withdrawal_id": approval.withdrawal_id,
            "reason": approval.reason
        })
        
        return {
            "success": True,
            "message": f"Withdrawal {approval.action}d successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing withdrawal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/withdrawals/toggle")
async def toggle_withdrawals(
    enabled: bool,
    asset: Optional[str] = None,  # If None, toggle all
    admin: AdminUser = Depends(require_permission("withdrawal:manage"))
):
    """Enable or disable withdrawals"""
    try:
        pool = await DatabaseManager.get_pool()
        
        async with pool.acquire() as conn:
            if asset:
                await conn.execute(
                    """UPDATE asset_settings SET withdrawals_enabled = $1, 
                        updated_at = $2 WHERE asset = $3""",
                    enabled, datetime.utcnow(), asset
                )
            else:
                await conn.execute(
                    """UPDATE asset_settings SET withdrawals_enabled = $1, updated_at = $2""",
                    enabled, datetime.utcnow()
                )
        
        await log_audit(admin.user_id, "TOGGLE_WITHDRAWALS", "withdrawals", {
            "enabled": enabled,
            "asset": asset
        })
        
        return {
            "success": True,
            "message": f"Withdrawals {'enabled' if enabled else 'disabled'} successfully"
        }
    except Exception as e:
        logger.error(f"Error toggling withdrawals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DEPOSIT MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/admin/deposits/pending")
async def get_pending_deposits(
    limit: int = 100,
    admin: AdminUser = Depends(require_permission("deposit:monitor"))
):
    """Get pending deposits"""
    try:
        pool = await DatabaseManager.get_pool()
        
        async with pool.acquire() as conn:
            deposits = await conn.fetch(
                """SELECT d.*, u.email, u.username FROM deposits d 
                   JOIN users u ON d.user_id = u.id 
                   WHERE d.status = 'pending' 
                   ORDER BY d.created_at ASC LIMIT $1""",
                limit
            )
        
        return {
            "success": True,
            "deposits": [dict(d) for d in deposits]
        }
    except Exception as e:
        logger.error(f"Error getting pending deposits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/deposits/{deposit_id}/confirm")
async def confirm_deposit(
    deposit_id: str,
    admin: AdminUser = Depends(require_permission("deposit:monitor"))
):
    """Manually confirm a deposit"""
    try:
        pool = await DatabaseManager.get_pool()
        
        async with pool.acquire() as conn:
            deposit = await conn.fetchrow(
                "SELECT * FROM deposits WHERE id = $1", deposit_id
            )
            if not deposit:
                raise HTTPException(status_code=404, detail="Deposit not found")
            
            if deposit['status'] != 'pending':
                raise HTTPException(status_code=400, detail="Deposit already processed")
            
            # Update deposit status
            await conn.execute(
                """UPDATE deposits SET status = 'confirmed', confirmed_by = $1, 
                    confirmed_at = $2 WHERE id = $3""",
                admin.user_id, datetime.utcnow(), deposit_id
            )
            
            # Credit user balance
            await conn.execute(
                """INSERT INTO user_balances (user_id, asset, balance, available)
                   VALUES ($1, $2, $3, $3)
                   ON CONFLICT (user_id, asset) 
                   DO UPDATE SET balance = user_balances.balance + $3,
                                 available = user_balances.available + $3""",
                deposit['user_id'], deposit['asset'], deposit['amount']
            )
            
            # Create transaction record
            await conn.execute(
                """INSERT INTO transactions (id, user_id, type, asset, amount, status, created_at)
                   VALUES ($1, $2, 'deposit', $3, $4, 'completed', $5)""",
                str(uuid.uuid4()), deposit['user_id'], deposit['asset'], 
                deposit['amount'], datetime.utcnow()
            )
        
        await log_audit(admin.user_id, "CONFIRM_DEPOSIT", "deposits", {
            "deposit_id": deposit_id
        })
        
        return {
            "success": True,
            "message": f"Deposit {deposit_id} confirmed successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming deposit: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# KYC MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/admin/kyc/pending")
async def get_pending_kyc(
    limit: int = 100,
    admin: AdminUser = Depends(require_permission("kyc:approve"))
):
    """Get pending KYC applications"""
    try:
        pool = await DatabaseManager.get_pool()
        
        async with pool.acquire() as conn:
            applications = await conn.fetch(
                """SELECT k.*, u.email, u.username FROM kyc_documents k 
                   JOIN users u ON k.user_id = u.id 
                   WHERE k.status = 'pending' 
                   ORDER BY k.submitted_at ASC LIMIT $1""",
                limit
            )
        
        return {
            "success": True,
            "applications": [dict(a) for a in applications]
        }
    except Exception as e:
        logger.error(f"Error getting pending KYC: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/kyc/{kyc_id}/approve")
async def approve_kyc(
    kyc_id: str,
    tier: int = 1,  # KYC tier level
    notes: Optional[str] = None,
    admin: AdminUser = Depends(require_permission("kyc:approve"))
):
    """Approve KYC application"""
    try:
        pool = await DatabaseManager.get_pool()
        
        async with pool.acquire() as conn:
            kyc = await conn.fetchrow(
                "SELECT * FROM kyc_documents WHERE id = $1", kyc_id
            )
            if not kyc:
                raise HTTPException(status_code=404, detail="KYC application not found")
            
            # Update KYC status
            await conn.execute(
                """UPDATE kyc_documents SET status = 'approved', reviewed_by = $1, 
                    reviewed_at = $2, notes = $3 WHERE id = $4""",
                admin.user_id, datetime.utcnow(), notes, kyc_id
            )
            
            # Update user KYC level
            await conn.execute(
                """UPDATE users SET kyc_status = 'approved', kyc_tier = $1 
                   WHERE id = $2""",
                tier, kyc['user_id']
            )
        
        await log_audit(admin.user_id, "APPROVE_KYC", "kyc", {
            "kyc_id": kyc_id,
            "tier": tier,
            "notes": notes
        })
        
        return {
            "success": True,
            "message": f"KYC application {kyc_id} approved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving KYC: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/kyc/{kyc_id}/reject")
async def reject_kyc(
    kyc_id: str,
    reason: str,
    admin: AdminUser = Depends(require_permission("kyc:reject"))
):
    """Reject KYC application"""
    try:
        pool = await DatabaseManager.get_pool()
        
        async with pool.acquire() as conn:
            kyc = await conn.fetchrow(
                "SELECT * FROM kyc_documents WHERE id = $1", kyc_id
            )
            if not kyc:
                raise HTTPException(status_code=404, detail="KYC application not found")
            
            # Update KYC status
            await conn.execute(
                """UPDATE kyc_documents SET status = 'rejected', reviewed_by = $1, 
                    reviewed_at = $2, rejection_reason = $3 WHERE id = $4""",
                admin.user_id, datetime.utcnow(), reason, kyc_id
            )
            
            # Update user KYC status
            await conn.execute(
                """UPDATE users SET kyc_status = 'rejected' WHERE id = $1""",
                kyc['user_id']
            )
        
        await log_audit(admin.user_id, "REJECT_KYC", "kyc", {
            "kyc_id": kyc_id,
            "reason": reason
        })
        
        return {
            "success": True,
            "message": f"KYC application {kyc_id} rejected"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting KYC: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SYSTEM CONFIGURATION ENDPOINTS
# ============================================================================

@app.get("/api/admin/system/config")
async def get_system_config(
    admin: AdminUser = Depends(require_permission("system:config"))
):
    """Get system configuration"""
    try:
        pool = await DatabaseManager.get_pool()
        
        async with pool.acquire() as conn:
            config = await conn.fetchrow("SELECT * FROM system_config LIMIT 1")
        
        return {
            "success": True,
            "config": dict(config) if config else {}
        }
    except Exception as e:
        logger.error(f"Error getting system config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/admin/system/config")
async def update_system_config(
    config: SystemConfig,
    admin: AdminUser = Depends(require_permission("system:config"))
):
    """Update system configuration"""
    try:
        pool = await DatabaseManager.get_pool()
        
        async with pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO system_config 
                   (maintenance_mode, registration_enabled, trading_enabled, 
                    withdrawals_enabled, deposits_enabled, kyc_required,
                    max_withdrawal_daily, max_deposit_daily, min_trade_amount, 
                    trading_fee, updated_at, updated_by)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                   ON CONFLICT (id) DO UPDATE SET
                   maintenance_mode = $1, registration_enabled = $2, trading_enabled = $3,
                   withdrawals_enabled = $4, deposits_enabled = $5, kyc_required = $6,
                   max_withdrawal_daily = $7, max_deposit_daily = $8, min_trade_amount = $9,
                   trading_fee = $10, updated_at = $11, updated_by = $12""",
                config.maintenance_mode, config.registration_enabled, config.trading_enabled,
                config.withdrawals_enabled, config.deposits_enabled, config.kyc_required,
                config.max_withdrawal_daily, config.max_deposit_daily, config.min_trade_amount,
                config.trading_fee, datetime.utcnow(), admin.user_id
            )
            
            # Clear system config cache
            await cache_delete("system_config")
        
        await log_audit(admin.user_id, "UPDATE_SYSTEM_CONFIG", "system", {
            "config": config.dict()
        })
        
        return {
            "success": True,
            "message": "System configuration updated successfully"
        }
    except Exception as e:
        logger.error(f"Error updating system config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/system/maintenance")
async def toggle_maintenance_mode(
    enabled: bool,
    message: Optional[str] = None,
    admin: AdminUser = Depends(require_permission("maintenance:mode"))
):
    """Toggle maintenance mode"""
    try:
        pool = await DatabaseManager.get_pool()
        
        async with pool.acquire() as conn:
            await conn.execute(
                """UPDATE system_config SET maintenance_mode = $1, 
                    maintenance_message = $2, updated_at = $3""",
                enabled, message, datetime.utcnow()
            )
        
        await log_audit(admin.user_id, "TOGGLE_MAINTENANCE", "system", {
            "enabled": enabled,
            "message": message
        })
        
        return {
            "success": True,
            "message": f"Maintenance mode {'enabled' if enabled else 'disabled'}"
        }
    except Exception as e:
        logger.error(f"Error toggling maintenance mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ANNOUNCEMENT MANAGEMENT
# ============================================================================

@app.post("/api/admin/announcements")
async def create_announcement(
    announcement: AnnouncementCreate,
    admin: AdminUser = Depends(require_permission("announcement:create"))
):
    """Create new announcement"""
    try:
        pool = await DatabaseManager.get_pool()
        
        announcement_id = str(uuid.uuid4())
        
        async with pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO announcements 
                   (id, title, content, category, priority, start_time, end_time, 
                    created_by, created_at, status)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, 'active')""",
                announcement_id, announcement.title, announcement.content,
                announcement.category, announcement.priority,
                announcement.start_time, announcement.end_time,
                admin.user_id, datetime.utcnow()
            )
        
        await log_audit(admin.user_id, "CREATE_ANNOUNCEMENT", "announcements", {
            "announcement_id": announcement_id,
            "title": announcement.title
        })
        
        return {
            "success": True,
            "message": "Announcement created successfully",
            "announcement_id": announcement_id
        }
    except Exception as e:
        logger.error(f"Error creating announcement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/announcements")
async def get_announcements(
    status: Optional[str] = None,
    admin: AdminUser = Depends(require_permission("announcement:create"))
):
    """Get all announcements"""
    try:
        pool = await DatabaseManager.get_pool()
        
        async with pool.acquire() as conn:
            query = "SELECT * FROM announcements"
            if status:
                query += f" WHERE status = '{status}'"
            query += " ORDER BY created_at DESC"
            
            announcements = await conn.fetch(query)
        
        return {
            "success": True,
            "announcements": [dict(a) for a in announcements]
        }
    except Exception as e:
        logger.error(f"Error getting announcements: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/admin/announcements/{announcement_id}")
async def delete_announcement(
    announcement_id: str,
    admin: AdminUser = Depends(require_permission("announcement:delete"))
):
    """Delete announcement"""
    try:
        pool = await DatabaseManager.get_pool()
        
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE announcements SET status = 'deleted' WHERE id = $1",
                announcement_id
            )
        
        await log_audit(admin.user_id, "DELETE_ANNOUNCEMENT", "announcements", {
            "announcement_id": announcement_id
        })
        
        return {
            "success": True,
            "message": "Announcement deleted successfully"
        }
    except Exception as e:
        logger.error(f"Error deleting announcement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# AUDIT LOG ENDPOINTS
# ============================================================================

@app.get("/api/admin/audit-logs")
async def get_audit_logs(
    filter: AuditLogFilter = Depends(),
    admin: AdminUser = Depends(require_permission("audit:view"))
):
    """Get audit logs with filtering"""
    try:
        pool = await DatabaseManager.get_pool()
        
        query = "SELECT * FROM admin_audit_log WHERE 1=1"
        params = []
        
        if filter.start_date:
            query += f" AND timestamp >= ${len(params)+1}"
            params.append(filter.start_date)
        
        if filter.end_date:
            query += f" AND timestamp <= ${len(params)+1}"
            params.append(filter.end_date)
        
        if filter.user_id:
            query += f" AND admin_id = ${len(params)+1}"
            params.append(filter.user_id)
        
        if filter.action:
            query += f" AND action ILIKE ${len(params)+1}"
            params.append(f"%{filter.action}%")
        
        if filter.category:
            query += f" AND category = ${len(params)+1}"
            params.append(filter.category)
        
        query += f" ORDER BY timestamp DESC LIMIT ${len(params)+1}"
        params.append(filter.limit)
        
        async with pool.acquire() as conn:
            logs = await conn.fetch(query, *params)
        
        return {
            "success": True,
            "logs": [dict(l) for l in logs]
        }
    except Exception as e:
        logger.error(f"Error getting audit logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SERVICE MANAGEMENT
# ============================================================================

@app.get("/api/admin/services")
async def get_services_status(
    admin: AdminUser = Depends(require_permission("system:config"))
):
    """Get status of all services"""
    try:
        pool = await DatabaseManager.get_pool()
        
        async with pool.acquire() as conn:
            services = await conn.fetch(
                """SELECT service_name, status, last_check, 
                          error_count, uptime_percentage 
                   FROM service_health ORDER BY service_name"""
            )
        
        return {
            "success": True,
            "services": [dict(s) for s in services]
        }
    except Exception as e:
        logger.error(f"Error getting services: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/services/{service_name}/restart")
async def restart_service(
    service_name: str,
    admin: AdminUser = Depends(require_permission("system:config"))
):
    """Restart a service"""
    try:
        # In production, this would trigger actual service restart
        pool = await DatabaseManager.get_pool()
        redis = await DatabaseManager.get_redis()
        
        await redis.publish("service_control", json.dumps({
            "action": "restart",
            "service": service_name,
            "initiated_by": admin.user_id,
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        await log_audit(admin.user_id, "RESTART_SERVICE", "services", {
            "service_name": service_name
        })
        
        return {
            "success": True,
            "message": f"Service {service_name} restart initiated"
        }
    except Exception as e:
        logger.error(f"Error restarting service: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        pool = await DatabaseManager.get_pool()
        redis = await DatabaseManager.get_redis()
        
        # Check database
        async with pool.acquire() as conn:
            db_status = await conn.fetchval("SELECT 1")
        
        # Check Redis
        redis_status = await redis.ping()
        
        return {
            "status": "healthy",
            "service": "unified-admin-dashboard",
            "version": "2.0.0",
            "database": "connected" if db_status else "error",
            "redis": "connected" if redis_status else "error",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    logger.info("Starting Unified Admin Dashboard...")
    try:
        await DatabaseManager.get_pool()
        await DatabaseManager.get_redis()
        logger.info("Database and Redis connections established")
    except Exception as e:
        logger.error(f"Failed to establish connections: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Unified Admin Dashboard...")
    await DatabaseManager.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
