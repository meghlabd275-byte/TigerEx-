"""
TigerEx User Management Admin Service
Complete admin interface for managing users, permissions, and accounts
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from decimal import Decimal
import asyncpg
import structlog
from enum import Enum
import bcrypt

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

app = FastAPI(title="TigerEx User Management Admin Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection pool
db_pool: Optional[asyncpg.Pool] = None

# Enums
class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    PENDING_VERIFICATION = "pending_verification"
    CLOSED = "closed"

class KYCLevel(str, Enum):
    LEVEL_0 = "level_0"  # No KYC
    LEVEL_1 = "level_1"  # Basic KYC
    LEVEL_2 = "level_2"  # Intermediate KYC
    LEVEL_3 = "level_3"  # Advanced KYC

class UserRole(str, Enum):
    USER = "user"
    VIP = "vip"
    INSTITUTIONAL = "institutional"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class ActionType(str, Enum):
    SUSPEND = "suspend"
    UNSUSPEND = "unsuspend"
    BAN = "ban"
    UNBAN = "unban"
    RESET_PASSWORD = "reset_password"
    UPDATE_KYC = "update_kyc"
    UPDATE_LIMITS = "update_limits"
    ADD_NOTE = "add_note"

# Models
class UserProfile(BaseModel):
    user_id: int
    email: str
    username: Optional[str]
    full_name: Optional[str]
    phone: Optional[str]
    country: Optional[str]
    status: str
    kyc_level: str
    role: str
    is_2fa_enabled: bool
    email_verified: bool
    phone_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

class UserSearchRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    user_id: Optional[int] = None
    status: Optional[UserStatus] = None
    kyc_level: Optional[KYCLevel] = None
    country: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None

class UserUpdateRequest(BaseModel):
    user_id: int
    status: Optional[UserStatus] = None
    kyc_level: Optional[KYCLevel] = None
    role: Optional[UserRole] = None
    email_verified: Optional[bool] = None
    phone_verified: Optional[bool] = None

class UserLimitsUpdate(BaseModel):
    user_id: int
    daily_withdrawal_limit: Optional[Decimal] = None
    monthly_withdrawal_limit: Optional[Decimal] = None
    daily_trading_limit: Optional[Decimal] = None
    max_open_orders: Optional[int] = None

class UserActionRequest(BaseModel):
    user_id: int
    action: ActionType
    reason: str
    admin_id: int
    duration_days: Optional[int] = None  # For temporary suspensions

class UserNoteRequest(BaseModel):
    user_id: int
    admin_id: int
    note: str
    is_important: bool = False

class UserStatsResponse(BaseModel):
    total_users: int
    active_users: int
    suspended_users: int
    banned_users: int
    pending_verification: int
    kyc_level_0: int
    kyc_level_1: int
    kyc_level_2: int
    kyc_level_3: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int

class UserActivityLog(BaseModel):
    log_id: int
    user_id: int
    action: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

# Database functions
async def get_db():
    return db_pool

async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(
        host="localhost",
        port=5432,
        user="tigerex",
        password="tigerex_secure_password",
        database="tigerex_admin",
        min_size=10,
        max_size=50
    )
    
    async with db_pool.acquire() as conn:
        # Create users table (if not exists from auth service)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(100) UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                phone VARCHAR(50),
                country VARCHAR(100),
                status VARCHAR(50) DEFAULT 'active',
                kyc_level VARCHAR(20) DEFAULT 'level_0',
                role VARCHAR(50) DEFAULT 'user',
                is_2fa_enabled BOOLEAN DEFAULT FALSE,
                email_verified BOOLEAN DEFAULT FALSE,
                phone_verified BOOLEAN DEFAULT FALSE,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_email (email),
                INDEX idx_username (username),
                INDEX idx_status (status),
                INDEX idx_kyc_level (kyc_level)
            )
        """)
        
        # Create user limits table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_limits (
                limit_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id),
                daily_withdrawal_limit DECIMAL(36, 18),
                monthly_withdrawal_limit DECIMAL(36, 18),
                daily_trading_limit DECIMAL(36, 18),
                max_open_orders INTEGER DEFAULT 100,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id)
            )
        """)
        
        # Create user actions log
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_actions_log (
                action_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id),
                admin_id INTEGER,
                action VARCHAR(50) NOT NULL,
                reason TEXT,
                duration_days INTEGER,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_actions (user_id, created_at DESC),
                INDEX idx_admin_actions (admin_id, created_at DESC)
            )
        """)
        
        # Create user notes
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_notes (
                note_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id),
                admin_id INTEGER,
                note TEXT NOT NULL,
                is_important BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_notes (user_id, created_at DESC)
            )
        """)
        
        # Create user activity log
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_activity_log (
                log_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id),
                action VARCHAR(100) NOT NULL,
                ip_address VARCHAR(50),
                user_agent TEXT,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_activity (user_id, created_at DESC),
                INDEX idx_action (action)
            )
        """)
        
        # Create user security events
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_security_events (
                event_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id),
                event_type VARCHAR(50) NOT NULL,
                severity VARCHAR(20) NOT NULL,
                description TEXT,
                ip_address VARCHAR(50),
                resolved BOOLEAN DEFAULT FALSE,
                resolved_by INTEGER,
                resolved_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_security (user_id, created_at DESC),
                INDEX idx_unresolved (resolved, created_at DESC)
            )
        """)
        
        logger.info("Database initialized successfully")

# API Endpoints
@app.post("/api/v1/admin/users/search", response_model=List[UserProfile])
async def search_users(
    request: UserSearchRequest,
    limit: int = Query(50, le=100),
    offset: int = 0,
    db: asyncpg.Pool = Depends(get_db)
):
    """Search users with filters"""
    try:
        query = "SELECT * FROM users WHERE 1=1"
        params = []
        param_count = 1
        
        if request.email:
            query += f" AND email ILIKE ${param_count}"
            params.append(f"%{request.email}%")
            param_count += 1
        
        if request.username:
            query += f" AND username ILIKE ${param_count}"
            params.append(f"%{request.username}%")
            param_count += 1
        
        if request.user_id:
            query += f" AND user_id = ${param_count}"
            params.append(request.user_id)
            param_count += 1
        
        if request.status:
            query += f" AND status = ${param_count}"
            params.append(request.status.value)
            param_count += 1
        
        if request.kyc_level:
            query += f" AND kyc_level = ${param_count}"
            params.append(request.kyc_level.value)
            param_count += 1
        
        if request.country:
            query += f" AND country = ${param_count}"
            params.append(request.country)
            param_count += 1
        
        if request.created_after:
            query += f" AND created_at >= ${param_count}"
            params.append(request.created_after)
            param_count += 1
        
        if request.created_before:
            query += f" AND created_at <= ${param_count}"
            params.append(request.created_before)
            param_count += 1
        
        query += f" ORDER BY created_at DESC LIMIT ${param_count} OFFSET ${param_count + 1}"
        params.extend([limit, offset])
        
        users = await db.fetch(query, *params)
        
        return [
            UserProfile(
                user_id=u['user_id'],
                email=u['email'],
                username=u['username'],
                full_name=u['full_name'],
                phone=u['phone'],
                country=u['country'],
                status=u['status'],
                kyc_level=u['kyc_level'],
                role=u['role'],
                is_2fa_enabled=u['is_2fa_enabled'],
                email_verified=u['email_verified'],
                phone_verified=u['phone_verified'],
                created_at=u['created_at'],
                last_login=u['last_login']
            )
            for u in users
        ]
        
    except Exception as e:
        logger.error("search_users_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/admin/users/{user_id}", response_model=UserProfile)
async def get_user_details(
    user_id: int,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get detailed user information"""
    try:
        user = await db.fetchrow("""
            SELECT * FROM users WHERE user_id = $1
        """, user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserProfile(
            user_id=user['user_id'],
            email=user['email'],
            username=user['username'],
            full_name=user['full_name'],
            phone=user['phone'],
            country=user['country'],
            status=user['status'],
            kyc_level=user['kyc_level'],
            role=user['role'],
            is_2fa_enabled=user['is_2fa_enabled'],
            email_verified=user['email_verified'],
            phone_verified=user['phone_verified'],
            created_at=user['created_at'],
            last_login=user['last_login']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_user_details_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/admin/users/update")
async def update_user(
    request: UserUpdateRequest,
    admin_id: int = Query(...),
    db: asyncpg.Pool = Depends(get_db)
):
    """Update user information"""
    try:
        updates = []
        params = [request.user_id]
        param_count = 2
        
        if request.status:
            updates.append(f"status = ${param_count}")
            params.append(request.status.value)
            param_count += 1
        
        if request.kyc_level:
            updates.append(f"kyc_level = ${param_count}")
            params.append(request.kyc_level.value)
            param_count += 1
        
        if request.role:
            updates.append(f"role = ${param_count}")
            params.append(request.role.value)
            param_count += 1
        
        if request.email_verified is not None:
            updates.append(f"email_verified = ${param_count}")
            params.append(request.email_verified)
            param_count += 1
        
        if request.phone_verified is not None:
            updates.append(f"phone_verified = ${param_count}")
            params.append(request.phone_verified)
            param_count += 1
        
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        
        query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = $1"
        result = await db.execute(query, *params)
        
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="User not found")
        
        # Log the action
        await db.execute("""
            INSERT INTO user_actions_log (user_id, admin_id, action, reason)
            VALUES ($1, $2, $3, $4)
        """, request.user_id, admin_id, "update_user", "Admin updated user information")
        
        logger.info("user_updated", user_id=request.user_id, admin_id=admin_id)
        return {"message": "User updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_user_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/admin/users/action")
async def perform_user_action(
    request: UserActionRequest,
    db: asyncpg.Pool = Depends(get_db)
):
    """Perform administrative action on user"""
    try:
        expires_at = None
        
        if request.action == ActionType.SUSPEND:
            new_status = UserStatus.SUSPENDED
            if request.duration_days:
                expires_at = datetime.utcnow() + timedelta(days=request.duration_days)
        elif request.action == ActionType.UNSUSPEND:
            new_status = UserStatus.ACTIVE
        elif request.action == ActionType.BAN:
            new_status = UserStatus.BANNED
        elif request.action == ActionType.UNBAN:
            new_status = UserStatus.ACTIVE
        else:
            new_status = None
        
        # Update user status if applicable
        if new_status:
            result = await db.execute("""
                UPDATE users SET status = $2, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = $1
            """, request.user_id, new_status.value)
            
            if result == "UPDATE 0":
                raise HTTPException(status_code=404, detail="User not found")
        
        # Log the action
        await db.execute("""
            INSERT INTO user_actions_log (
                user_id, admin_id, action, reason, duration_days, expires_at
            ) VALUES ($1, $2, $3, $4, $5, $6)
        """, request.user_id, request.admin_id, request.action.value,
            request.reason, request.duration_days, expires_at)
        
        logger.info("user_action_performed",
                   user_id=request.user_id,
                   admin_id=request.admin_id,
                   action=request.action.value)
        
        return {
            "message": f"Action '{request.action.value}' performed successfully",
            "expires_at": expires_at.isoformat() if expires_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("user_action_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/admin/users/limits")
async def update_user_limits(
    request: UserLimitsUpdate,
    admin_id: int = Query(...),
    db: asyncpg.Pool = Depends(get_db)
):
    """Update user trading and withdrawal limits"""
    try:
        # Check if limits exist
        existing = await db.fetchrow("""
            SELECT limit_id FROM user_limits WHERE user_id = $1
        """, request.user_id)
        
        if existing:
            # Update existing limits
            updates = []
            params = [request.user_id]
            param_count = 2
            
            if request.daily_withdrawal_limit is not None:
                updates.append(f"daily_withdrawal_limit = ${param_count}")
                params.append(request.daily_withdrawal_limit)
                param_count += 1
            
            if request.monthly_withdrawal_limit is not None:
                updates.append(f"monthly_withdrawal_limit = ${param_count}")
                params.append(request.monthly_withdrawal_limit)
                param_count += 1
            
            if request.daily_trading_limit is not None:
                updates.append(f"daily_trading_limit = ${param_count}")
                params.append(request.daily_trading_limit)
                param_count += 1
            
            if request.max_open_orders is not None:
                updates.append(f"max_open_orders = ${param_count}")
                params.append(request.max_open_orders)
                param_count += 1
            
            if updates:
                updates.append("updated_at = CURRENT_TIMESTAMP")
                query = f"UPDATE user_limits SET {', '.join(updates)} WHERE user_id = $1"
                await db.execute(query, *params)
        else:
            # Create new limits
            await db.execute("""
                INSERT INTO user_limits (
                    user_id, daily_withdrawal_limit, monthly_withdrawal_limit,
                    daily_trading_limit, max_open_orders
                ) VALUES ($1, $2, $3, $4, $5)
            """, request.user_id, request.daily_withdrawal_limit,
                request.monthly_withdrawal_limit, request.daily_trading_limit,
                request.max_open_orders)
        
        # Log the action
        await db.execute("""
            INSERT INTO user_actions_log (user_id, admin_id, action, reason)
            VALUES ($1, $2, $3, $4)
        """, request.user_id, admin_id, ActionType.UPDATE_LIMITS.value,
            "Admin updated user limits")
        
        logger.info("user_limits_updated", user_id=request.user_id, admin_id=admin_id)
        return {"message": "User limits updated successfully"}
        
    except Exception as e:
        logger.error("update_limits_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/admin/users/note")
async def add_user_note(
    request: UserNoteRequest,
    db: asyncpg.Pool = Depends(get_db)
):
    """Add a note to user account"""
    try:
        await db.execute("""
            INSERT INTO user_notes (user_id, admin_id, note, is_important)
            VALUES ($1, $2, $3, $4)
        """, request.user_id, request.admin_id, request.note, request.is_important)
        
        logger.info("user_note_added", user_id=request.user_id, admin_id=request.admin_id)
        return {"message": "Note added successfully"}
        
    except Exception as e:
        logger.error("add_note_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/admin/users/{user_id}/notes")
async def get_user_notes(
    user_id: int,
    limit: int = 50,
    offset: int = 0,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get all notes for a user"""
    try:
        notes = await db.fetch("""
            SELECT * FROM user_notes
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
        """, user_id, limit, offset)
        
        return [dict(note) for note in notes]
        
    except Exception as e:
        logger.error("get_notes_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/admin/users/{user_id}/activity", response_model=List[UserActivityLog])
async def get_user_activity(
    user_id: int,
    limit: int = 100,
    offset: int = 0,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get user activity log"""
    try:
        activities = await db.fetch("""
            SELECT * FROM user_activity_log
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
        """, user_id, limit, offset)
        
        return [
            UserActivityLog(
                log_id=a['log_id'],
                user_id=a['user_id'],
                action=a['action'],
                ip_address=a['ip_address'],
                user_agent=a['user_agent'],
                created_at=a['created_at']
            )
            for a in activities
        ]
        
    except Exception as e:
        logger.error("get_activity_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/admin/users/stats", response_model=UserStatsResponse)
async def get_user_statistics(db: asyncpg.Pool = Depends(get_db)):
    """Get user statistics"""
    try:
        stats = await db.fetchrow("""
            SELECT
                COUNT(*) as total_users,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_users,
                COUNT(CASE WHEN status = 'suspended' THEN 1 END) as suspended_users,
                COUNT(CASE WHEN status = 'banned' THEN 1 END) as banned_users,
                COUNT(CASE WHEN status = 'pending_verification' THEN 1 END) as pending_verification,
                COUNT(CASE WHEN kyc_level = 'level_0' THEN 1 END) as kyc_level_0,
                COUNT(CASE WHEN kyc_level = 'level_1' THEN 1 END) as kyc_level_1,
                COUNT(CASE WHEN kyc_level = 'level_2' THEN 1 END) as kyc_level_2,
                COUNT(CASE WHEN kyc_level = 'level_3' THEN 1 END) as kyc_level_3,
                COUNT(CASE WHEN created_at >= CURRENT_DATE THEN 1 END) as new_users_today,
                COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as new_users_this_week,
                COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END) as new_users_this_month
            FROM users
        """)
        
        return UserStatsResponse(**dict(stats))
        
    except Exception as e:
        logger.error("get_stats_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "user-management-admin-service",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.on_event("startup")
async def startup():
    """Initialize service on startup"""
    await init_db()
    logger.info("User Management Admin Service started")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    if db_pool:
        await db_pool.close()
    logger.info("User Management Admin Service stopped")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8240)