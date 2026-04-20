"""
TigerEx Comprehensive Admin Dashboard
Complete Admin Control System with Role-Based Access
Controls all trading, users, fees, liquidity, and system settings
"""

import os
import json
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import logging

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import asyncpg
import redis
import jwt

# @file main.py
# @description TigerEx comprehensive-admin-dashboard service
# @author TigerEx Development Team
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TigerEx Admin Dashboard", version="1.0.0")
security = HTTPBearer()

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    OPERATOR = "operator"
    SUPPORT = "support"
    VIEWER = "viewer"
    CUSTOM = "custom"

class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    PENDING = "pending"
    VERIFIED = "verified"
    FROZEN = "frozen"

class ServiceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    DEGRADED = "degraded"

class TradingPairStatus(str, Enum):
    ACTIVE = "active"
    HALTED = "halted"
    DELISTED = "delisted"
    PENDING = "pending"

class FeeType(str, Enum):
    MAKER = "maker"
    TAKER = "taker"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"
    TRANSFER = "transfer"
    CONVERSION = "conversion"

# Permission Constants
PERMISSIONS = {
    "super_admin": ["all"],
    "admin": [
        "manage_users", "manage_trading", "manage_fees", "manage_liquidity",
        "manage_pairs", "manage_kyc", "manage_withdrawals", "manage_deposits",
        "view_reports", "manage_settings", "manage_admins", "manage_roles"
    ],
    "operator": [
        "manage_trading", "view_reports", "manage_pairs"
    ],
    "support": [
        "view_users", "manage_kyc", "view_reports"
    ],
    "viewer": [
        "view_reports", "view_users"
    ]
}

# Pydantic Models
class CreateAdminUserRequest(BaseModel):
    user_id: str
    username: str
    email: str
    role: UserRole
    permissions: List[str] = []

class UpdateAdminUserRequest(BaseModel):
    role: Optional[UserRole] = None
    permissions: Optional[List[str]] = None
    status: Optional[UserStatus] = None

class CreateTradingPairRequest(BaseModel):
    symbol: str
    base_asset: str
    quote_asset: str
    price_precision: int = 8
    quantity_precision: int = 8
    min_notional: float = 10
    max_notional: float = 1000000
    maker_fee: float = 0.001
    taker_fee: float = 0.001
    is_spot: bool = True
    is_margin: bool = False
    is_futures: bool = False

class UpdateTradingPairRequest(BaseModel):
    status: Optional[TradingPairStatus] = None
    maker_fee: Optional[float] = None
    taker_fee: Optional[float] = None
    min_notional: Optional[float] = None
    max_notional: Optional[float] = None

class SetFeeRequest(BaseModel):
    user_tier: str
    fee_type: FeeType
    fee_value: float
    instrument_type: str = "all"
    min_fee: float = 0
    max_fee: float = 1000

class ManageUserRequest(BaseModel):
    user_id: str
    action: str  # suspend, ban, freeze, verify, activate
    reason: str = ""

class CreateUserTierRequest(BaseModel):
    tier_name: str
    min_volume_30d: float = 0
    max_volume_30d: float = 1000000
    maker_fee_discount: float = 0
    taker_fee_discount: float = 0
    withdrawal_limit_daily: float = 100000
    features: List[str] = []

class SystemConfigRequest(BaseModel):
    key: str
    value: str
    description: str = ""
    is_encrypted: bool = False

class AnnouncementRequest(BaseModel):
    title: str
    content: str
    type: str = "info"  # info, warning, critical
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    target: str = "all"  # all, vip, kyc_verified

# Database Manager
class DatabaseManager:
    def __init__(self):
        self.pool = None
        self.redis = None
        
    async def initialize(self):
        self.pool = await asyncpg.create_pool(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 5432)),
            user=os.getenv("DB_USER", "tigerex"),
            password=os.getenv("DB_PASSWORD", "tigerex123"),
            database=os.getenv("DB_NAME", "tigerex_admin"),
            min_size=5,
            max_size=50
        )
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )
        await self._create_tables()
        
    async def _create_tables(self):
        async with self.pool.acquire() as conn:
            # Admin Users
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS admin_users (
                    admin_id VARCHAR(50) PRIMARY KEY,
                    user_id VARCHAR(50) UNIQUE,
                    username VARCHAR(100),
                    email VARCHAR(200),
                    role VARCHAR(20),
                    permissions JSONB,
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    last_login TIMESTAMP
                )
            ''')
            
            # User Management
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id VARCHAR(50) PRIMARY KEY,
                    email VARCHAR(200),
                    username VARCHAR(100),
                    tier VARCHAR(20) DEFAULT 'regular',
                    kyc_level INTEGER DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'active',
                    total_volume_30d DECIMAL(30, 10) DEFAULT 0,
                    total_trades INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # User Tiers
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS user_tiers (
                    tier_id VARCHAR(50) PRIMARY KEY,
                    tier_name VARCHAR(50),
                    min_volume_30d DECIMAL(30, 10),
                    max_volume_30d DECIMAL(30, 10),
                    maker_fee_discount DECIMAL(10, 6),
                    taker_fee_discount DECIMAL(10, 6),
                    withdrawal_limit_daily DECIMAL(30, 10),
                    features JSONB,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # Trading Pairs
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS trading_pairs (
                    pair_id VARCHAR(50) PRIMARY KEY,
                    symbol VARCHAR(50),
                    base_asset VARCHAR(20),
                    quote_asset VARCHAR(20),
                    price_precision INTEGER,
                    quantity_precision INTEGER,
                    min_notional DECIMAL(20, 10),
                    max_notional DECIMAL(20, 10),
                    maker_fee DECIMAL(10, 6),
                    taker_fee DECIMAL(10, 6),
                    status VARCHAR(20) DEFAULT 'active',
                    is_spot BOOLEAN DEFAULT true,
                    is_margin BOOLEAN DEFAULT false,
                    is_futures BOOLEAN DEFAULT false,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # Fee Structure
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS fee_structure (
                    fee_id VARCHAR(50) PRIMARY KEY,
                    user_tier VARCHAR(50),
                    fee_type VARCHAR(20),
                    instrument_type VARCHAR(50),
                    fee_value DECIMAL(10, 6),
                    min_fee DECIMAL(20, 10),
                    max_fee DECIMAL(20, 10),
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # System Configuration
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS system_config (
                    config_id VARCHAR(50) PRIMARY KEY,
                    key VARCHAR(100) UNIQUE,
                    value TEXT,
                    description TEXT,
                    is_encrypted BOOLEAN DEFAULT false,
                    updated_at TIMESTAMP DEFAULT NOW(),
                    updated_by VARCHAR(50)
                )
            ''')
            
            # Announcements
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS announcements (
                    announcement_id VARCHAR(50) PRIMARY KEY,
                    title VARCHAR(200),
                    content TEXT,
                    type VARCHAR(20),
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    target VARCHAR(20),
                    status VARCHAR(20) DEFAULT 'active',
                    created_by VARCHAR(50),
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # Audit Log
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    log_id VARCHAR(50) PRIMARY KEY,
                    admin_id VARCHAR(50),
                    action VARCHAR(100),
                    entity_type VARCHAR(50),
                    entity_id VARCHAR(50),
                    old_value JSONB,
                    new_value JSONB,
                    ip_address VARCHAR(50),
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # Service Status
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS service_status (
                    service_id VARCHAR(50) PRIMARY KEY,
                    service_name VARCHAR(100),
                    status VARCHAR(20),
                    last_heartbeat TIMESTAMP,
                    metadata JSONB
                )
            ''')
            
            # Withdrawal Limits
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS withdrawal_limits (
                    limit_id VARCHAR(50) PRIMARY KEY,
                    user_tier VARCHAR(50),
                    asset VARCHAR(20),
                    daily_limit DECIMAL(30, 10),
                    monthly_limit DECIMAL(30, 10),
                    min_withdrawal DECIMAL(30, 10),
                    fee DECIMAL(20, 10),
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # API Keys Management
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    key_id VARCHAR(50) PRIMARY KEY,
                    user_id VARCHAR(50),
                    api_key VARCHAR(100),
                    api_secret VARCHAR(200),
                    permissions JSONB,
                    ip_whitelist JSONB,
                    rate_limit INTEGER DEFAULT 1000,
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT NOW(),
                    expires_at TIMESTAMP
                )
            ''')

db = DatabaseManager()

# Admin Manager
class AdminManager:
    async def create_admin(self, data: CreateAdminUserRequest, created_by: str) -> Dict:
        """Create a new admin user"""
        admin_id = f"ADM-{uuid.uuid4().hex[:12].upper()}"
        
        permissions = data.permissions or PERMISSIONS.get(data.role.value, [])
        
        async with db.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO admin_users (
                    admin_id, user_id, username, email, role, permissions, status, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
            ''', admin_id, data.user_id, data.username, data.email,
                data.role.value, json.dumps(permissions), UserStatus.ACTIVE.value
            )
            
            await self._log_action(created_by, "create_admin", "admin_user", admin_id, 
                                   None, {"username": data.username, "role": data.role.value})
        
        return {"admin_id": admin_id, "user_id": data.user_id, "role": data.role.value}
    
    async def update_admin(self, admin_id: str, data: UpdateAdminUserRequest, updated_by: str) -> Dict:
        """Update admin user"""
        updates = []
        params = [admin_id]
        idx = 2
        
        old_data = await self.get_admin(admin_id)
        
        if data.role:
            updates.append(f"role = ${idx}")
            params.append(data.role.value)
            idx += 1
        if data.permissions is not None:
            updates.append(f"permissions = ${idx}")
            params.append(json.dumps(data.permissions))
            idx += 1
        if data.status:
            updates.append(f"status = ${idx}")
            params.append(data.status.value)
            idx += 1
        
        updates.append("updated_at = NOW()")
        
        if updates:
            async with db.pool.acquire() as conn:
                await conn.execute(
                    f"UPDATE admin_users SET {', '.join(updates)} WHERE admin_id = $1",
                    *params
                )
            
            new_data = await self.get_admin(admin_id)
            await self._log_action(updated_by, "update_admin", "admin_user", admin_id, old_data, new_data)
        
        return await self.get_admin(admin_id)
    
    async def delete_admin(self, admin_id: str, deleted_by: str) -> bool:
        """Delete admin user"""
        old_data = await self.get_admin(admin_id)
        
        async with db.pool.acquire() as conn:
            await conn.execute("DELETE FROM admin_users WHERE admin_id = $1", admin_id)
        
        await self._log_action(deleted_by, "delete_admin", "admin_user", admin_id, old_data, None)
        return True
    
    async def get_admin(self, admin_id: str) -> Optional[Dict]:
        """Get admin by ID"""
        async with db.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM admin_users WHERE admin_id = $1",
                admin_id
            )
            if row:
                return dict(row)
            return None
    
    async def get_admin_by_user_id(self, user_id: str) -> Optional[Dict]:
        """Get admin by user ID"""
        async with db.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM admin_users WHERE user_id = $1",
                user_id
            )
            if row:
                return dict(row)
            return None
    
    async def get_all_admins(self) -> List[Dict]:
        """Get all admin users"""
        async with db.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM admin_users ORDER BY created_at DESC")
        return [dict(row) for row in rows]
    
    async def has_permission(self, admin_id: str, permission: str) -> bool:
        """Check if admin has a specific permission"""
        admin = await self.get_admin(admin_id)
        if not admin:
            return False
        
        permissions = json.loads(admin['permissions']) if admin['permissions'] else []
        
        if "all" in permissions:
            return True
        
        return permission in permissions
    
    async def _log_action(self, admin_id: str, action: str, entity_type: str, 
                         entity_id: str, old_value: Any, new_value: Any):
        """Log admin action"""
        log_id = f"LOG-{uuid.uuid4().hex[:12].upper()}"
        
        async with db.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO audit_log (
                    log_id, admin_id, action, entity_type, entity_id, old_value, new_value, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
            ''', log_id, admin_id, action, entity_type, entity_id,
                json.dumps(old_value) if old_value else None,
                json.dumps(new_value) if new_value else None
            )

admin_manager = AdminManager()

# User Manager
class UserManager:
    async def get_users(self, status: str = None, tier: str = None, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get all users with filters"""
        async with db.pool.acquire() as conn:
            query = "SELECT * FROM users WHERE 1=1"
            params = []
            idx = 1
            
            if status:
                query += f" AND status = ${idx}"
                params.append(status)
                idx += 1
            if tier:
                query += f" AND tier = ${idx}"
                params.append(tier)
                idx += 1
            
            query += f" ORDER BY created_at DESC LIMIT ${idx} OFFSET ${idx+1}"
            params.extend([limit, offset])
            
            rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]
    
    async def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        async with db.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
            if row:
                return dict(row)
            return None
    
    async def manage_user(self, data: ManageUserRequest, admin_id: str) -> Dict:
        """Perform action on user"""
        user = await self.get_user(data.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        old_status = user['status']
        new_status = data.action
        
        status_map = {
            "suspend": UserStatus.SUSPENDED,
            "ban": UserStatus.BANNED,
            "freeze": UserStatus.FROZEN,
            "verify": UserStatus.VERIFIED,
            "activate": UserStatus.ACTIVE
        }
        
        if data.action not in status_map:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        async with db.pool.acquire() as conn:
            await conn.execute('''
                UPDATE users SET status = $1, updated_at = NOW()
                WHERE user_id = $2
            ''', status_map[data.action].value, data.user_id)
        
        await admin_manager._log_action(admin_id, f"user_{data.action}", "user", 
                                        data.user_id, {"status": old_status}, 
                                        {"status": status_map[data.action].value, "reason": data.reason})
        
        return {"user_id": data.user_id, "old_status": old_status, "new_status": status_map[data.action].value}
    
    async def update_user_tier(self, user_id: str, tier: str, admin_id: str) -> Dict:
        """Update user tier"""
        async with db.pool.acquire() as conn:
            old_tier = await conn.fetchval("SELECT tier FROM users WHERE user_id = $1", user_id)
            
            await conn.execute('''
                UPDATE users SET tier = $1, updated_at = NOW()
                WHERE user_id = $2
            ''', tier, user_id)
        
        await admin_manager._log_action(admin_id, "update_tier", "user", 
                                        user_id, {"tier": old_tier}, {"tier": tier})
        
        return {"user_id": user_id, "old_tier": old_tier, "new_tier": tier}
    
    async def get_user_statistics(self) -> Dict:
        """Get user statistics"""
        async with db.pool.acquire() as conn:
            total = await conn.fetchval("SELECT COUNT(*) FROM users")
            active = await conn.fetchval("SELECT COUNT(*) FROM users WHERE status = 'active'")
            verified = await conn.fetchval("SELECT COUNT(*) FROM users WHERE kyc_level >= 2")
            suspended = await conn.fetchval("SELECT COUNT(*) FROM users WHERE status = 'suspended'")
            
        return {
            "total_users": total,
            "active_users": active,
            "verified_users": verified,
            "suspended_users": suspended
        }

user_manager = UserManager()

# Trading Pair Manager
class TradingPairManager:
    async def create_pair(self, data: CreateTradingPairRequest, admin_id: str) -> Dict:
        """Create a new trading pair"""
        pair_id = f"PAIR-{uuid.uuid4().hex[:12].upper()}"
        
        async with db.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO trading_pairs (
                    pair_id, symbol, base_asset, quote_asset, price_precision,
                    quantity_precision, min_notional, max_notional, maker_fee, taker_fee,
                    status, is_spot, is_margin, is_futures, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, NOW())
            ''', pair_id, data.symbol, data.base_asset, data.quote_asset,
                data.price_precision, data.quantity_precision, data.min_notional,
                data.max_notional, data.maker_fee, data.taker_fee,
                TradingPairStatus.ACTIVE.value, data.is_spot, data.is_margin, data.is_futures
            )
        
        await admin_manager._log_action(admin_id, "create_pair", "trading_pair", 
                                        pair_id, None, data.dict())
        
        return {"pair_id": pair_id, "symbol": data.symbol}
    
    async def update_pair(self, pair_id: str, data: UpdateTradingPairRequest, admin_id: str) -> Dict:
        """Update trading pair"""
        updates = []
        params = [pair_id]
        idx = 2
        
        old_data = await self.get_pair(pair_id)
        
        if data.status:
            updates.append(f"status = ${idx}")
            params.append(data.status.value)
            idx += 1
        if data.maker_fee is not None:
            updates.append(f"maker_fee = ${idx}")
            params.append(data.maker_fee)
            idx += 1
        if data.taker_fee is not None:
            updates.append(f"taker_fee = ${idx}")
            params.append(data.taker_fee)
            idx += 1
        if data.min_notional is not None:
            updates.append(f"min_notional = ${idx}")
            params.append(data.min_notional)
            idx += 1
        if data.max_notional is not None:
            updates.append(f"max_notional = ${idx}")
            params.append(data.max_notional)
            idx += 1
        
        updates.append("updated_at = NOW()")
        
        if updates:
            async with db.pool.acquire() as conn:
                await conn.execute(
                    f"UPDATE trading_pairs SET {', '.join(updates)} WHERE pair_id = $1",
                    *params
                )
        
        new_data = await self.get_pair(pair_id)
        await admin_manager._log_action(admin_id, "update_pair", "trading_pair", 
                                        pair_id, old_data, new_data)
        
        return new_data
    
    async def halt_pair(self, pair_id: str, reason: str, admin_id: str) -> bool:
        """Halt trading for a pair"""
        async with db.pool.acquire() as conn:
            await conn.execute('''
                UPDATE trading_pairs SET status = 'halted', updated_at = NOW()
                WHERE pair_id = $1
            ''', pair_id)
        
        await admin_manager._log_action(admin_id, "halt_pair", "trading_pair", 
                                        pair_id, None, {"reason": reason})
        return True
    
    async def delist_pair(self, pair_id: str, reason: str, admin_id: str) -> bool:
        """Delist a trading pair"""
        async with db.pool.acquire() as conn:
            await conn.execute('''
                UPDATE trading_pairs SET status = 'delisted', updated_at = NOW()
                WHERE pair_id = $1
            ''', pair_id)
        
        await admin_manager._log_action(admin_id, "delist_pair", "trading_pair", 
                                        pair_id, None, {"reason": reason})
        return True
    
    async def get_pairs(self, status: str = None) -> List[Dict]:
        """Get all trading pairs"""
        async with db.pool.acquire() as conn:
            if status:
                rows = await conn.fetch(
                    "SELECT * FROM trading_pairs WHERE status = $1 ORDER BY symbol",
                    status
                )
            else:
                rows = await conn.fetch("SELECT * FROM trading_pairs ORDER BY symbol")
        return [dict(row) for row in rows]
    
    async def get_pair(self, pair_id: str) -> Optional[Dict]:
        """Get trading pair by ID"""
        async with db.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM trading_pairs WHERE pair_id = $1", pair_id)
            if row:
                return dict(row)
            return None

pair_manager = TradingPairManager()

# Fee Manager
class FeeManager:
    async def set_fee(self, data: SetFeeRequest, admin_id: str) -> Dict:
        """Set fee for a tier and type"""
        fee_id = f"FEE-{uuid.uuid4().hex[:12].upper()}"
        
        async with db.pool.acquire() as conn:
            # Check if fee exists for this combination
            existing = await conn.fetchrow('''
                SELECT * FROM fee_structure 
                WHERE user_tier = $1 AND fee_type = $2 AND instrument_type = $3
            ''', data.user_tier, data.fee_type.value, data.instrument_type)
            
            if existing:
                # Update existing
                await conn.execute('''
                    UPDATE fee_structure SET fee_value = $1, min_fee = $2, max_fee = $3
                    WHERE fee_id = $4
                ''', data.fee_value, data.min_fee, data.max_fee, existing['fee_id'])
                fee_id = existing['fee_id']
            else:
                # Create new
                await conn.execute('''
                    INSERT INTO fee_structure (
                        fee_id, user_tier, fee_type, instrument_type, fee_value, min_fee, max_fee, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
                ''', fee_id, data.user_tier, data.fee_type.value, data.instrument_type,
                    data.fee_value, data.min_fee, data.max_fee)
        
        await admin_manager._log_action(admin_id, "set_fee", "fee_structure", 
                                        fee_id, None, data.dict())
        
        return {"fee_id": fee_id, "user_tier": data.user_tier, "fee_type": data.fee_type.value, "fee_value": data.fee_value}
    
    async def get_fees(self, user_tier: str = None) -> List[Dict]:
        """Get all fees"""
        async with db.pool.acquire() as conn:
            if user_tier:
                rows = await conn.fetch(
                    "SELECT * FROM fee_structure WHERE user_tier = $1",
                    user_tier
                )
            else:
                rows = await conn.fetch("SELECT * FROM fee_structure")
        return [dict(row) for row in rows]

fee_manager = FeeManager()

# System Manager
class SystemManager:
    async def get_config(self, key: str) -> Optional[Dict]:
        """Get system configuration"""
        async with db.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM system_config WHERE key = $1",
                key
            )
            if row:
                return dict(row)
            return None
    
    async def set_config(self, data: SystemConfigRequest, admin_id: str) -> Dict:
        """Set system configuration"""
        config_id = f"CFG-{uuid.uuid4().hex[:12].upper()}"
        
        async with db.pool.acquire() as conn:
            existing = await conn.fetchrow(
                "SELECT * FROM system_config WHERE key = $1",
                data.key
            )
            
            if existing:
                await conn.execute('''
                    UPDATE system_config SET value = $1, description = $2, 
                    is_encrypted = $3, updated_at = NOW(), updated_by = $4
                    WHERE key = $5
                ''', data.value, data.description, data.is_encrypted, admin_id, data.key)
                config_id = existing['config_id']
            else:
                await conn.execute('''
                    INSERT INTO system_config (
                        config_id, key, value, description, is_encrypted, updated_at, updated_by
                    ) VALUES ($1, $2, $3, $4, $5, NOW(), $6)
                ''', config_id, data.key, data.value, data.description, 
                    data.is_encrypted, admin_id)
        
        await admin_manager._log_action(admin_id, "set_config", "system_config", 
                                        config_id, None, data.dict())
        
        return {"config_id": config_id, "key": data.key}
    
    async def get_all_configs(self) -> List[Dict]:
        """Get all system configurations"""
        async with db.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM system_config ORDER BY key")
        return [dict(row) for row in rows]
    
    async def create_announcement(self, data: AnnouncementRequest, admin_id: str) -> Dict:
        """Create system announcement"""
        announcement_id = f"ANN-{uuid.uuid4().hex[:12].upper()}"
        
        async with db.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO announcements (
                    announcement_id, title, content, type, start_time, end_time,
                    target, status, created_by, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW())
            ''', announcement_id, data.title, data.content, data.type,
                data.start_time, data.end_time, data.target, "active", admin_id
            )
        
        await admin_manager._log_action(admin_id, "create_announcement", "announcement", 
                                        announcement_id, None, data.dict())
        
        return {"announcement_id": announcement_id, "title": data.title}
    
    async def get_announcements(self, active_only: bool = False) -> List[Dict]:
        """Get all announcements"""
        async with db.pool.acquire() as conn:
            if active_only:
                rows = await conn.fetch('''
                    SELECT * FROM announcements 
                    WHERE status = 'active' 
                    AND (start_time IS NULL OR start_time <= NOW())
                    AND (end_time IS NULL OR end_time >= NOW())
                    ORDER BY created_at DESC
                ''')
            else:
                rows = await conn.fetch("SELECT * FROM announcements ORDER BY created_at DESC")
        return [dict(row) for row in rows]
    
    async def update_service_status(self, service_name: str, status: ServiceStatus, metadata: Dict = None) -> bool:
        """Update service status"""
        service_id = f"SVC-{service_name}"
        
        async with db.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO service_status (service_id, service_name, status, last_heartbeat, metadata)
                VALUES ($1, $2, $3, NOW(), $4)
                ON CONFLICT (service_id) DO UPDATE SET
                    status = $3, last_heartbeat = NOW(), metadata = $4
            ''', service_id, service_name, status.value, json.dumps(metadata or {}))
        
        return True
    
    async def get_service_status(self) -> List[Dict]:
        """Get all services status"""
        async with db.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM service_status ORDER BY service_name")
        return [dict(row) for row in rows]

system_manager = SystemManager()

# API Endpoints

@app.on_event("startup")
async def startup():
    await db.initialize()
    logger.info("Admin Dashboard initialized successfully")

# Health Check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "admin-dashboard", "timestamp": datetime.utcnow().isoformat()}

# Admin Management
@app.post("/admins")
async def create_admin(
    data: CreateAdminUserRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new admin user"""
    admin_id = "admin_123"  # Would be extracted from JWT
    result = await admin_manager.create_admin(data, admin_id)
    return {"success": True, "data": result}

@app.get("/admins")
async def get_admins(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all admin users"""
    admins = await admin_manager.get_all_admins()
    return {"success": True, "data": admins}

@app.put("/admins/{admin_id}")
async def update_admin(
    admin_id: str,
    data: UpdateAdminUserRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update admin user"""
    updater_id = "admin_123"
    result = await admin_manager.update_admin(admin_id, data, updater_id)
    return {"success": True, "data": result}

@app.delete("/admins/{admin_id}")
async def delete_admin(
    admin_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Delete admin user"""
    deleter_id = "admin_123"
    await admin_manager.delete_admin(admin_id, deleter_id)
    return {"success": True}

# User Management
@app.get("/users")
async def get_users(
    status: str = None,
    tier: str = None,
    limit: int = 100,
    offset: int = 0,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get all users"""
    users = await user_manager.get_users(status, tier, limit, offset)
    return {"success": True, "data": users}

@app.get("/users/{user_id}")
async def get_user(user_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get user by ID"""
    user = await user_manager.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True, "data": user}

@app.post("/users/manage")
async def manage_user(
    data: ManageUserRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Perform action on user"""
    admin_id = "admin_123"
    result = await user_manager.manage_user(data, admin_id)
    return {"success": True, "data": result}

@app.get("/users/statistics")
async def get_user_statistics(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get user statistics"""
    stats = await user_manager.get_user_statistics()
    return {"success": True, "data": stats}

# Trading Pair Management
@app.post("/trading-pairs")
async def create_trading_pair(
    data: CreateTradingPairRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new trading pair"""
    admin_id = "admin_123"
    result = await pair_manager.create_pair(data, admin_id)
    return {"success": True, "data": result}

@app.get("/trading-pairs")
async def get_trading_pairs(
    status: str = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get all trading pairs"""
    pairs = await pair_manager.get_pairs(status)
    return {"success": True, "data": pairs}

@app.put("/trading-pairs/{pair_id}")
async def update_trading_pair(
    pair_id: str,
    data: UpdateTradingPairRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update trading pair"""
    admin_id = "admin_123"
    result = await pair_manager.update_pair(pair_id, data, admin_id)
    return {"success": True, "data": result}

@app.post("/trading-pairs/{pair_id}/halt")
async def halt_trading_pair(
    pair_id: str,
    reason: str = "",
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Halt trading pair"""
    admin_id = "admin_123"
    await pair_manager.halt_pair(pair_id, reason, admin_id)
    return {"success": True}

@app.post("/trading-pairs/{pair_id}/delist")
async def delist_trading_pair(
    pair_id: str,
    reason: str = "",
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Delist trading pair"""
    admin_id = "admin_123"
    await pair_manager.delist_pair(pair_id, reason, admin_id)
    return {"success": True}

# Fee Management
@app.post("/fees")
async def set_fee(
    data: SetFeeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Set fee"""
    admin_id = "admin_123"
    result = await fee_manager.set_fee(data, admin_id)
    return {"success": True, "data": result}

@app.get("/fees")
async def get_fees(
    user_tier: str = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get all fees"""
    fees = await fee_manager.get_fees(user_tier)
    return {"success": True, "data": fees}

# System Configuration
@app.post("/config")
async def set_config(
    data: SystemConfigRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Set system configuration"""
    admin_id = "admin_123"
    result = await system_manager.set_config(data, admin_id)
    return {"success": True, "data": result}

@app.get("/config")
async def get_configs(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all configurations"""
    configs = await system_manager.get_all_configs()
    return {"success": True, "data": configs}

# Announcements
@app.post("/announcements")
async def create_announcement(
    data: AnnouncementRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create announcement"""
    admin_id = "admin_123"
    result = await system_manager.create_announcement(data, admin_id)
    return {"success": True, "data": result}

@app.get("/announcements")
async def get_announcements(active_only: bool = False):
    """Get all announcements"""
    announcements = await system_manager.get_announcements(active_only)
    return {"success": True, "data": announcements}

# Service Status
@app.get("/services/status")
async def get_service_status(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all services status"""
    status = await system_manager.get_service_status()
    return {"success": True, "data": status}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)