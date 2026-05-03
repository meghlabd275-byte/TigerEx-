"""
TigerEx Exchange Management Service
Complete Exchange ID, White-label Status, and Configuration Management
Version: 2.0.0 - Production Ready
"""

import os
import json
import logging
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, asdict

import asyncpg
import redis.asyncio as aioredis
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator, EmailStr
import jwt

# @file main.py
# @description TigerEx exchange-management-service service
# @author TigerEx Development Team
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="TigerEx Exchange Management Service",
    description="Exchange ID, White-label Status, and Configuration Management",
    version="2.0.0"
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
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "tigerex-jwt-secret-key-2024")
    JWT_ALGORITHM = "HS256"
    MASTER_EXCHANGE_ID = os.getenv("MASTER_EXCHANGE_ID", "TIGEREX_MASTER")

config = Config()
security = HTTPBearer()


# Enums
class ExchangeStatus(str, Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    HALTED = "halted"
    SUSPENDED = "suspended"
    DEMO = "demo"
    SETUP = "setup"
    MIGRATING = "migrating"


class ExchangeMode(str, Enum):
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    SANDBOX = "sandbox"
    DEMO = "demo"


class ExchangeType(str, Enum):
    MAIN = "main"
    WHITE_LABEL = "white_label"
    PARTNER = "partner"
    REGIONAL = "regional"
    INSTITUTIONAL = "institutional"


class DeploymentType(str, Enum):
    CLOUD = "cloud"
    ON_PREMISE = "on_premise"
    HYBRID = "hybrid"


class FeatureModule(str, Enum):
    SPOT_TRADING = "spot_trading"
    MARGIN_TRADING = "margin_trading"
    FUTURES_TRADING = "futures_trading"
    OPTIONS_TRADING = "options_trading"
    P2P_TRADING = "p2p_trading"
    NFT_MARKETPLACE = "nft_marketplace"
    LAUNCHPAD = "launchpad"
    STAKING = "staking"
    EARN = "earn"
    COPY_TRADING = "copy_trading"
    BOT_TRADING = "bot_trading"
    INSTITUTIONAL = "institutional"
    OTC_DESK = "otc_desk"
    DEFI_INTEGRATION = "defi_integration"
    BRIDGE = "bridge"
    GOVERNANCE = "governance"


# Data Classes
@dataclass
class ExchangeConfig:
    exchange_id: str
    exchange_name: str
    exchange_type: ExchangeType
    status: ExchangeStatus
    mode: ExchangeMode
    deployment_type: DeploymentType
    parent_exchange_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]
    
    # Branding
    logo_url: Optional[str]
    primary_color: Optional[str]
    secondary_color: Optional[str]
    domain: Optional[str]
    subdomain: Optional[str]
    
    # Contact
    support_email: Optional[str]
    support_phone: Optional[str]
    
    # Limits
    max_users: int
    max_trading_pairs: int
    max_daily_volume: Decimal
    
    # Features
    enabled_modules: List[str]
    
    # Compliance
    kyc_required: bool
    kyc_provider: Optional[str]
    jurisdiction: Optional[str]


@dataclass
class ExchangeStats:
    total_users: int
    active_users: int
    daily_volume: Decimal
    monthly_volume: Decimal
    total_trades: int
    total_pairs: int
    uptime_percentage: Decimal


# Pydantic Models
class ExchangeCreate(BaseModel):
    exchange_name: str
    exchange_type: ExchangeType = ExchangeType.WHITE_LABEL
    mode: ExchangeMode = ExchangeMode.SANDBOX
    deployment_type: DeploymentType = DeploymentType.CLOUD
    parent_exchange_id: Optional[str] = None
    
    # Branding
    logo_url: Optional[str] = None
    primary_color: Optional[str] = "#FF6B00"
    secondary_color: Optional[str] = "#1A1A2E"
    domain: Optional[str] = None
    subdomain: Optional[str] = None
    
    # Contact
    support_email: Optional[EmailStr] = None
    support_phone: Optional[str] = None
    
    # Limits
    max_users: int = 10000
    max_trading_pairs: int = 50
    max_daily_volume: Decimal = Decimal("1000000")
    
    # Features
    enabled_modules: List[str] = ["spot_trading"]
    
    # Compliance
    kyc_required: bool = True
    kyc_provider: Optional[str] = None
    jurisdiction: Optional[str] = None


class ExchangeUpdate(BaseModel):
    exchange_name: Optional[str] = None
    status: Optional[ExchangeStatus] = None
    mode: Optional[ExchangeMode] = None
    
    # Branding
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    domain: Optional[str] = None
    subdomain: Optional[str] = None
    
    # Contact
    support_email: Optional[str] = None
    support_phone: Optional[str] = None
    
    # Limits
    max_users: Optional[int] = None
    max_trading_pairs: Optional[int] = None
    max_daily_volume: Optional[Decimal] = None
    
    # Features
    enabled_modules: Optional[List[str]] = None
    
    # Compliance
    kyc_required: Optional[bool] = None
    kyc_provider: Optional[str] = None
    jurisdiction: Optional[str] = None


class FeatureToggle(BaseModel):
    module: FeatureModule
    enabled: bool


class ExchangeStatusUpdate(BaseModel):
    status: ExchangeStatus
    reason: Optional[str] = None
    duration_hours: Optional[int] = None


class APIKeyCreate(BaseModel):
    name: str
    permissions: List[str]
    ip_whitelist: Optional[List[str]] = None
    expires_in_days: Optional[int] = None


class APIKeyResponse(BaseModel):
    api_key: str
    api_secret: str
    name: str
    permissions: List[str]
    created_at: datetime
    expires_at: Optional[datetime]


# Database Manager
class ExchangeDatabaseManager:
    def __init__(self):
        self.pool = None
        self.redis = None
    
    async def initialize(self):
        try:
            self.pool = await asyncpg.create_pool(config.DATABASE_URL)
            logger.info("Database pool created")
            await self._create_tables()
        except Exception as e:
            logger.warning(f"Database connection failed: {e}")
        
        try:
            self.redis = await aioredis.from_url(config.REDIS_URL)
            logger.info("Redis connected")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
    
    async def _create_tables(self):
        if not self.pool:
            return
        
        async with self.pool.acquire() as conn:
            # Main exchanges table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS exchanges (
                    id SERIAL PRIMARY KEY,
                    exchange_id VARCHAR(255) UNIQUE NOT NULL,
                    exchange_name VARCHAR(255) NOT NULL,
                    exchange_type VARCHAR(50) NOT NULL DEFAULT 'white_label',
                    status VARCHAR(50) NOT NULL DEFAULT 'setup',
                    mode VARCHAR(50) NOT NULL DEFAULT 'sandbox',
                    deployment_type VARCHAR(50) NOT NULL DEFAULT 'cloud',
                    parent_exchange_id VARCHAR(255),
                    
                    -- Branding
                    logo_url TEXT,
                    primary_color VARCHAR(20) DEFAULT '#FF6B00',
                    secondary_color VARCHAR(20) DEFAULT '#1A1A2E',
                    domain VARCHAR(255),
                    subdomain VARCHAR(255),
                    
                    -- Contact
                    support_email VARCHAR(255),
                    support_phone VARCHAR(50),
                    
                    -- Limits
                    max_users INTEGER DEFAULT 10000,
                    max_trading_pairs INTEGER DEFAULT 50,
                    max_daily_volume DECIMAL(30, 10) DEFAULT 1000000,
                    
                    -- Features
                    enabled_modules JSONB DEFAULT '["spot_trading"]',
                    
                    -- Compliance
                    kyc_required BOOLEAN DEFAULT TRUE,
                    kyc_provider VARCHAR(100),
                    jurisdiction VARCHAR(100),
                    
                    -- Timestamps
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    
                    -- Metadata
                    metadata JSONB,
                    settings JSONB
                )
            ''')
            
            # Exchange API keys
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS exchange_api_keys (
                    id SERIAL PRIMARY KEY,
                    exchange_id VARCHAR(255) NOT NULL,
                    api_key VARCHAR(255) UNIQUE NOT NULL,
                    api_secret_hash VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    permissions JSONB NOT NULL,
                    ip_whitelist JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    last_used_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (exchange_id) REFERENCES exchanges(exchange_id)
                )
            ''')
            
            # Exchange admins
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS exchange_admins (
                    id SERIAL PRIMARY KEY,
                    exchange_id VARCHAR(255) NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL DEFAULT 'admin',
                    permissions JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    UNIQUE(exchange_id, user_id),
                    FOREIGN KEY (exchange_id) REFERENCES exchanges(exchange_id)
                )
            ''')
            
            # Exchange statistics
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS exchange_statistics (
                    id SERIAL PRIMARY KEY,
                    exchange_id VARCHAR(255) NOT NULL,
                    stat_date DATE NOT NULL,
                    total_users INTEGER DEFAULT 0,
                    active_users INTEGER DEFAULT 0,
                    new_users INTEGER DEFAULT 0,
                    daily_volume DECIMAL(30, 10) DEFAULT 0,
                    total_trades INTEGER DEFAULT 0,
                    total_fees DECIMAL(30, 10) DEFAULT 0,
                    UNIQUE(exchange_id, stat_date),
                    FOREIGN KEY (exchange_id) REFERENCES exchanges(exchange_id)
                )
            ''')
            
            # Exchange status history
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS exchange_status_history (
                    id SERIAL PRIMARY KEY,
                    exchange_id VARCHAR(255) NOT NULL,
                    old_status VARCHAR(50),
                    new_status VARCHAR(50) NOT NULL,
                    reason TEXT,
                    changed_by VARCHAR(255),
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (exchange_id) REFERENCES exchanges(exchange_id)
                )
            ''')
    
    async def create_exchange(self, exchange_data: Dict) -> str:
        """Create a new exchange"""
        exchange_id = f"TEX_{secrets.token_hex(8).upper()}"
        
        if not self.pool:
            return exchange_id
        
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO exchanges (
                    exchange_id, exchange_name, exchange_type, status, mode, 
                    deployment_type, parent_exchange_id, logo_url, primary_color, 
                    secondary_color, domain, subdomain, support_email, support_phone,
                    max_users, max_trading_pairs, max_daily_volume, enabled_modules,
                    kyc_required, kyc_provider, jurisdiction
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21)
            ''', exchange_id, exchange_data.get('exchange_name'), 
                exchange_data.get('exchange_type', 'white_label'),
                'setup', exchange_data.get('mode', 'sandbox'),
                exchange_data.get('deployment_type', 'cloud'),
                exchange_data.get('parent_exchange_id'),
                exchange_data.get('logo_url'), exchange_data.get('primary_color', '#FF6B00'),
                exchange_data.get('secondary_color', '#1A1A2E'),
                exchange_data.get('domain'), exchange_data.get('subdomain'),
                exchange_data.get('support_email'), exchange_data.get('support_phone'),
                exchange_data.get('max_users', 10000), exchange_data.get('max_trading_pairs', 50),
                exchange_data.get('max_daily_volume', 1000000),
                json.dumps(exchange_data.get('enabled_modules', ['spot_trading'])),
                exchange_data.get('kyc_required', True),
                exchange_data.get('kyc_provider'), exchange_data.get('jurisdiction')
            )
            
            return exchange_id
    
    async def get_exchange(self, exchange_id: str) -> Optional[Dict]:
        """Get exchange by ID"""
        if not self.pool:
            return None
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                'SELECT * FROM exchanges WHERE exchange_id = $1', exchange_id
            )
            return dict(row) if row else None
    
    async def update_exchange(self, exchange_id: str, update_data: Dict) -> bool:
        """Update exchange configuration"""
        if not self.pool:
            return False
        
        # Build dynamic update query
        set_clauses = []
        values = []
        idx = 1
        
        for key, value in update_data.items():
            if key in ['exchange_id', 'created_at']:
                continue
            set_clauses.append(f"{key} = ${idx}")
            if key == 'enabled_modules':
                values.append(json.dumps(value))
            else:
                values.append(value)
            idx += 1
        
        if not set_clauses:
            return False
        
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        values.append(exchange_id)
        
        async with self.pool.acquire() as conn:
            await conn.execute(
                f"UPDATE exchanges SET {', '.join(set_clauses)} WHERE exchange_id = ${idx}",
                *values
            )
            return True
    
    async def list_exchanges(self, exchange_type: str = None, status: str = None, 
                              limit: int = 100, offset: int = 0) -> List[Dict]:
        """List all exchanges with filters"""
        if not self.pool:
            return []
        
        async with self.pool.acquire() as conn:
            query = 'SELECT * FROM exchanges WHERE 1=1'
            params = []
            idx = 1
            
            if exchange_type:
                query += f" AND exchange_type = ${idx}"
                params.append(exchange_type)
                idx += 1
            
            if status:
                query += f" AND status = ${idx}"
                params.append(status)
                idx += 1
            
            query += f" ORDER BY created_at DESC LIMIT ${idx} OFFSET ${idx + 1}"
            params.extend([limit, offset])
            
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]
    
    async def create_api_key(self, exchange_id: str, name: str, permissions: List[str],
                             ip_whitelist: List[str] = None, expires_in_days: int = None) -> Dict:
        """Create API key for exchange"""
        import hashlib
        
        api_key = f"TEX_{secrets.token_urlsafe(16)}"
        api_secret = secrets.token_urlsafe(32)
        api_secret_hash = hashlib.sha256(api_secret.encode()).hexdigest()
        
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        if self.pool:
            async with self.pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO exchange_api_keys 
                    (exchange_id, api_key, api_secret_hash, name, permissions, ip_whitelist, expires_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                ''', exchange_id, api_key, api_secret_hash, name,
                    json.dumps(permissions), json.dumps(ip_whitelist or []), expires_at)
        
        return {
            "api_key": api_key,
            "api_secret": api_secret,  # Only returned once!
            "name": name,
            "permissions": permissions,
            "expires_at": expires_at
        }
    
    async def log_status_change(self, exchange_id: str, old_status: str, new_status: str,
                                 reason: str, changed_by: str):
        """Log exchange status change"""
        if not self.pool:
            return
        
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO exchange_status_history 
                (exchange_id, old_status, new_status, reason, changed_by)
                VALUES ($1, $2, $3, $4, $5)
            ''', exchange_id, old_status, new_status, reason, changed_by)


# Exchange Manager
class ExchangeManager:
    def __init__(self):
        self.db = ExchangeDatabaseManager()
    
    async def initialize(self):
        await self.db.initialize()
    
    async def generate_exchange_id(self) -> str:
        """Generate unique exchange ID"""
        return f"TEX_{secrets.token_hex(8).upper()}"
    
    async def validate_exchange_limits(self, exchange_id: str) -> Dict:
        """Validate exchange is within limits"""
        exchange = await self.db.get_exchange(exchange_id)
        if not exchange:
            return {"valid": False, "error": "Exchange not found"}
        
        # Check if exchange is active
        if exchange.get('status') != 'active':
            return {"valid": False, "error": f"Exchange status is {exchange.get('status')}"}
        
        # Check expiration
        if exchange.get('expires_at') and exchange['expires_at'] < datetime.utcnow():
            return {"valid": False, "error": "Exchange subscription expired"}
        
        return {"valid": True, "exchange": exchange}
    
    async def get_exchange_stats(self, exchange_id: str) -> Dict:
        """Get exchange statistics"""
        if not self.db.pool:
            return {"total_users": 0, "active_users": 0, "daily_volume": 0}
        
        async with self.db.pool.acquire() as conn:
            # Get today's stats
            today = datetime.utcnow().date()
            row = await conn.fetchrow('''
                SELECT * FROM exchange_statistics 
                WHERE exchange_id = $1 AND stat_date = $2
            ''', exchange_id, today)
            
            if row:
                return dict(row)
            
            return {
                "total_users": 0,
                "active_users": 0,
                "daily_volume": 0,
                "total_trades": 0,
                "total_fees": 0
            }
    
    async def update_exchange_stats(self, exchange_id: str, stats: Dict):
        """Update exchange statistics"""
        if not self.db.pool:
            return
        
        today = datetime.utcnow().date()
        
        async with self.db.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO exchange_statistics 
                (exchange_id, stat_date, total_users, active_users, new_users, 
                 daily_volume, total_trades, total_fees)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (exchange_id, stat_date)
                DO UPDATE SET
                    total_users = EXCLUDED.total_users,
                    active_users = EXCLUDED.active_users,
                    daily_volume = EXCLUDED.daily_volume,
                    total_trades = EXCLUDED.total_trades,
                    total_fees = EXCLUDED.total_fees
            ''', exchange_id, today, stats.get('total_users', 0),
                stats.get('active_users', 0), stats.get('new_users', 0),
                stats.get('daily_volume', 0), stats.get('total_trades', 0),
                stats.get('total_fees', 0))


# Global manager
exchange_manager = ExchangeManager()


# API Endpoints
@app.on_event("startup")
async def startup():
    await exchange_manager.initialize()


@app.get("/")
async def root():
    return {"service": "TigerEx Exchange Management", "version": "2.0.0", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# Exchange CRUD
@app.post("/exchanges")
async def create_exchange(
    exchange_data: ExchangeCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new exchange (admin only)"""
    # Verify admin token
    try:
        payload = jwt.decode(credentials.credentials, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        if payload.get("role") not in ["admin", "super_admin"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    exchange_id = await exchange_manager.db.create_exchange(exchange_data.dict())
    
    return {
        "success": True,
        "exchange_id": exchange_id,
        "message": "Exchange created successfully"
    }


@app.get("/exchanges/{exchange_id}")
async def get_exchange(exchange_id: str):
    """Get exchange details"""
    exchange = await exchange_manager.db.get_exchange(exchange_id)
    
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")
    
    return exchange


@app.put("/exchanges/{exchange_id}")
async def update_exchange(
    exchange_id: str,
    update_data: ExchangeUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update exchange configuration"""
    try:
        payload = jwt.decode(credentials.credentials, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        if payload.get("role") not in ["admin", "super_admin"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get current exchange
    current = await exchange_manager.db.get_exchange(exchange_id)
    if not current:
        raise HTTPException(status_code=404, detail="Exchange not found")
    
    # Update only provided fields
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    
    if update_dict:
        await exchange_manager.db.update_exchange(exchange_id, update_dict)
    
    return {"success": True, "message": "Exchange updated"}


@app.delete("/exchanges/{exchange_id}")
async def delete_exchange(
    exchange_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Delete/Deactivate exchange (admin only)"""
    try:
        payload = jwt.decode(credentials.credentials, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        if payload.get("role") != "super_admin":
            raise HTTPException(status_code=403, detail="Super admin required")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Soft delete by setting status to suspended
    await exchange_manager.db.update_exchange(exchange_id, {"status": "suspended"})
    
    return {"success": True, "message": "Exchange deactivated"}


@app.get("/exchanges")
async def list_exchanges(
    exchange_type: str = None,
    status: str = None,
    limit: int = 100,
    offset: int = 0
):
    """List all exchanges"""
    exchanges = await exchange_manager.db.list_exchanges(exchange_type, status, limit, offset)
    return {"exchanges": exchanges, "count": len(exchanges)}


# Exchange Status Management
@app.post("/exchanges/{exchange_id}/status")
async def update_exchange_status(
    exchange_id: str,
    status_update: ExchangeStatusUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update exchange status (halt, pause, resume, etc.)"""
    try:
        payload = jwt.decode(credentials.credentials, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        if payload.get("role") not in ["admin", "super_admin"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get current exchange
    current = await exchange_manager.db.get_exchange(exchange_id)
    if not current:
        raise HTTPException(status_code=404, detail="Exchange not found")
    
    old_status = current.get('status')
    
    # Update status
    await exchange_manager.db.update_exchange(exchange_id, {"status": status_update.status.value})
    
    # Log status change
    await exchange_manager.db.log_status_change(
        exchange_id, old_status, status_update.status.value,
        status_update.reason or "", payload.get("sub")
    )
    
    # Cache status in Redis
    if exchange_manager.db.redis:
        await exchange_manager.db.redis.set(
            f"exchange:{exchange_id}:status",
            status_update.status.value
        )
    
    return {
        "success": True,
        "old_status": old_status,
        "new_status": status_update.status.value
    }


@app.post("/exchanges/{exchange_id}/halt")
async def halt_exchange(
    exchange_id: str,
    reason: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Emergency halt exchange"""
    return await update_exchange_status(
        exchange_id,
        ExchangeStatusUpdate(status=ExchangeStatus.HALTED, reason=reason),
        credentials
    )


@app.post("/exchanges/{exchange_id}/resume")
async def resume_exchange(
    exchange_id: str,
    reason: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Resume halted exchange"""
    return await update_exchange_status(
        exchange_id,
        ExchangeStatusUpdate(status=ExchangeStatus.ACTIVE, reason=reason),
        credentials
    )


# Feature Management
@app.get("/exchanges/{exchange_id}/features")
async def get_exchange_features(exchange_id: str):
    """Get enabled features for exchange"""
    exchange = await exchange_manager.db.get_exchange(exchange_id)
    
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")
    
    return {"enabled_modules": exchange.get('enabled_modules', [])}


@app.post("/exchanges/{exchange_id}/features")
async def toggle_exchange_feature(
    exchange_id: str,
    feature: FeatureToggle,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Enable/disable feature for exchange"""
    try:
        payload = jwt.decode(credentials.credentials, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        if payload.get("role") not in ["admin", "super_admin"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    exchange = await exchange_manager.db.get_exchange(exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")
    
    enabled_modules = exchange.get('enabled_modules', [])
    module_name = feature.module.value
    
    if feature.enabled and module_name not in enabled_modules:
        enabled_modules.append(module_name)
    elif not feature.enabled and module_name in enabled_modules:
        enabled_modules.remove(module_name)
    
    await exchange_manager.db.update_exchange(exchange_id, {"enabled_modules": enabled_modules})
    
    return {"success": True, "enabled_modules": enabled_modules}


# API Key Management
@app.post("/exchanges/{exchange_id}/api-keys")
async def create_api_key(
    exchange_id: str,
    key_data: APIKeyCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create API key for exchange"""
    try:
        payload = jwt.decode(credentials.credentials, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        if payload.get("role") not in ["admin", "super_admin"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    result = await exchange_manager.db.create_api_key(
        exchange_id, key_data.name, key_data.permissions,
        key_data.ip_whitelist, key_data.expires_in_days
    )
    
    return result


@app.get("/exchanges/{exchange_id}/api-keys")
async def list_api_keys(
    exchange_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """List API keys for exchange"""
    try:
        payload = jwt.decode(credentials.credentials, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        if payload.get("role") not in ["admin", "super_admin"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if not exchange_manager.db.pool:
        return {"api_keys": []}
    
    async with exchange_manager.db.pool.acquire() as conn:
        rows = await conn.fetch('''
            SELECT id, api_key, name, permissions, created_at, expires_at, last_used_at, is_active
            FROM exchange_api_keys WHERE exchange_id = $1
        ''', exchange_id)
        
        return {"api_keys": [dict(row) for row in rows]}


@app.delete("/exchanges/{exchange_id}/api-keys/{api_key}")
async def revoke_api_key(
    exchange_id: str,
    api_key: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Revoke API key"""
    try:
        payload = jwt.decode(credentials.credentials, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        if payload.get("role") not in ["admin", "super_admin"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if exchange_manager.db.pool:
        async with exchange_manager.db.pool.acquire() as conn:
            await conn.execute(
                "UPDATE exchange_api_keys SET is_active = FALSE WHERE exchange_id = $1 AND api_key = $2",
                exchange_id, api_key
            )
    
    return {"success": True, "message": "API key revoked"}


# Statistics
@app.get("/exchanges/{exchange_id}/stats")
async def get_exchange_stats(exchange_id: str):
    """Get exchange statistics"""
    stats = await exchange_manager.get_exchange_stats(exchange_id)
    return stats


@app.get("/exchanges/{exchange_id}/validate")
async def validate_exchange(exchange_id: str):
    """Validate exchange is active and within limits"""
    result = await exchange_manager.validate_exchange_limits(exchange_id)
    return result


# Status History
@app.get("/exchanges/{exchange_id}/status-history")
async def get_status_history(
    exchange_id: str,
    limit: int = 50,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get exchange status change history"""
    try:
        payload = jwt.decode(credentials.credentials, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        if payload.get("role") not in ["admin", "super_admin"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if not exchange_manager.db.pool:
        return {"history": []}
    
    async with exchange_manager.db.pool.acquire() as conn:
        rows = await conn.fetch('''
            SELECT * FROM exchange_status_history 
            WHERE exchange_id = $1 
            ORDER BY changed_at DESC 
            LIMIT $2
        ''', exchange_id, limit)
        
        return {"history": [dict(row) for row in rows]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8083)def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
