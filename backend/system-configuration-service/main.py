import os
"""
TigerEx System Configuration Service
Manages platform-wide settings, fees, limits, and configurations
"""

from fastapi import FastAPI
from admin.admin_routes import router as admin_router
, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
import asyncpg
import structlog
from enum import Enum
import json

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

app = FastAPI(title="TigerEx System Configuration Service", version="1.0.0")

# Include admin router
app.include_router(admin_router)

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
class ConfigCategory(str, Enum):
    TRADING = "trading"
    FEES = "fees"
    LIMITS = "limits"
    SECURITY = "security"
    BLOCKCHAIN = "blockchain"
    NOTIFICATION = "notification"
    GENERAL = "general"

class FeeType(str, Enum):
    MAKER = "maker"
    TAKER = "taker"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"

# Models
class SystemConfig(BaseModel):
    config_id: int
    category: str
    key: str
    value: Any
    description: Optional[str]
    is_active: bool
    updated_by: Optional[int]
    updated_at: datetime

class ConfigUpdateRequest(BaseModel):
    category: ConfigCategory
    key: str
    value: Any
    description: Optional[str] = None
    admin_id: int

class TradingFeeConfig(BaseModel):
    pair: str
    maker_fee: Decimal = Field(..., ge=0, le=1)
    taker_fee: Decimal = Field(..., ge=0, le=1)
    min_order_size: Decimal = Field(..., gt=0)
    max_order_size: Optional[Decimal] = None

class WithdrawalFeeConfig(BaseModel):
    currency: str
    blockchain: str
    fixed_fee: Decimal = Field(..., ge=0)
    percentage_fee: Decimal = Field(..., ge=0, le=1)
    min_withdrawal: Decimal = Field(..., gt=0)
    max_withdrawal: Optional[Decimal] = None
    daily_limit: Optional[Decimal] = None

class BlockchainConfig(BaseModel):
    blockchain: str
    is_enabled: bool
    min_confirmations: int = Field(..., ge=1)
    node_url: str
    explorer_url: str
    supports_memo: bool = False

class MaintenanceMode(BaseModel):
    is_enabled: bool
    message: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    affected_services: List[str] = []

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
        database="tigerex_config",
        min_size=10,
        max_size=50
    )
    
    async with db_pool.acquire() as conn:
        # Create system configurations table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS system_configs (
                config_id SERIAL PRIMARY KEY,
                category VARCHAR(50) NOT NULL,
                key VARCHAR(255) NOT NULL,
                value JSONB NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                updated_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, key),
                INDEX idx_category (category),
                INDEX idx_key (key)
            )
        """)
        
        # Create trading fees table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS trading_fees (
                fee_id SERIAL PRIMARY KEY,
                pair VARCHAR(50) NOT NULL UNIQUE,
                maker_fee DECIMAL(10, 8) NOT NULL,
                taker_fee DECIMAL(10, 8) NOT NULL,
                min_order_size DECIMAL(36, 18) NOT NULL,
                max_order_size DECIMAL(36, 18),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_pair (pair)
            )
        """)
        
        # Create withdrawal fees table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS withdrawal_fees (
                fee_id SERIAL PRIMARY KEY,
                currency VARCHAR(20) NOT NULL,
                blockchain VARCHAR(50) NOT NULL,
                fixed_fee DECIMAL(36, 18) NOT NULL,
                percentage_fee DECIMAL(10, 8) NOT NULL,
                min_withdrawal DECIMAL(36, 18) NOT NULL,
                max_withdrawal DECIMAL(36, 18),
                daily_limit DECIMAL(36, 18),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(currency, blockchain),
                INDEX idx_currency (currency)
            )
        """)
        
        # Create blockchain configurations table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS blockchain_configs (
                blockchain_id SERIAL PRIMARY KEY,
                blockchain VARCHAR(50) NOT NULL UNIQUE,
                is_enabled BOOLEAN DEFAULT TRUE,
                min_confirmations INTEGER NOT NULL,
                node_url VARCHAR(500),
                explorer_url VARCHAR(500),
                supports_memo BOOLEAN DEFAULT FALSE,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_blockchain (blockchain)
            )
        """)
        
        # Create maintenance schedules table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS maintenance_schedules (
                maintenance_id SERIAL PRIMARY KEY,
                is_enabled BOOLEAN DEFAULT FALSE,
                message TEXT NOT NULL,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                affected_services JSONB,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create config change log
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS config_change_log (
                log_id SERIAL PRIMARY KEY,
                category VARCHAR(50) NOT NULL,
                key VARCHAR(255) NOT NULL,
                old_value JSONB,
                new_value JSONB,
                changed_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_category_key (category, key),
                INDEX idx_changed_by (changed_by)
            )
        """)
        
        # Insert default configurations
        await conn.execute("""
            INSERT INTO system_configs (category, key, value, description)
            VALUES 
                ('general', 'platform_name', '"TigerEx"', 'Platform name'),
                ('general', 'support_email', '"support@tigerex.com"', 'Support email'),
                ('security', 'max_login_attempts', '5', 'Maximum login attempts before lockout'),
                ('security', 'lockout_duration_minutes', '30', 'Account lockout duration'),
                ('security', 'session_timeout_minutes', '60', 'Session timeout duration'),
                ('trading', 'max_open_orders', '100', 'Maximum open orders per user'),
                ('trading', 'order_expiry_days', '30', 'Order expiry in days'),
                ('limits', 'default_daily_withdrawal_limit', '10000', 'Default daily withdrawal limit'),
                ('limits', 'default_monthly_withdrawal_limit', '100000', 'Default monthly withdrawal limit')
            ON CONFLICT (category, key) DO NOTHING
        """)
        
        logger.info("Database initialized successfully")

# API Endpoints
@app.get("/api/v1/config/all")
async def get_all_configs(
    category: Optional[ConfigCategory] = None,
    is_active: Optional[bool] = None,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get all system configurations"""
    try:
        query = "SELECT * FROM system_configs WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = $1"
            params.append(category.value)
        
        if is_active is not None:
            query += f" AND is_active = ${len(params) + 1}"
            params.append(is_active)
        
        query += " ORDER BY category, key"
        
        configs = await db.fetch(query, *params)
        
        return [
            {
                "config_id": c['config_id'],
                "category": c['category'],
                "key": c['key'],
                "value": c['value'],
                "description": c['description'],
                "is_active": c['is_active'],
                "updated_at": c['updated_at'].isoformat()
            }
            for c in configs
        ]
        
    except Exception as e:
        logger.error("get_configs_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/config/{category}/{key}")
async def get_config(
    category: ConfigCategory,
    key: str,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get specific configuration"""
    try:
        config = await db.fetchrow("""
            SELECT * FROM system_configs
            WHERE category = $1 AND key = $2
        """, category.value, key)
        
        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")
        
        return {
            "config_id": config['config_id'],
            "category": config['category'],
            "key": config['key'],
            "value": config['value'],
            "description": config['description'],
            "is_active": config['is_active'],
            "updated_at": config['updated_at'].isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_config_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/config/update")
async def update_config(
    request: ConfigUpdateRequest,
    db: asyncpg.Pool = Depends(get_db)
):
    """Update system configuration"""
    try:
        # Get old value for logging
        old_config = await db.fetchrow("""
            SELECT value FROM system_configs
            WHERE category = $1 AND key = $2
        """, request.category.value, request.key)
        
        old_value = old_config['value'] if old_config else None
        
        # Update or insert configuration
        await db.execute("""
            INSERT INTO system_configs (category, key, value, description, updated_by)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (category, key)
            DO UPDATE SET
                value = $3,
                description = COALESCE($4, system_configs.description),
                updated_by = $5,
                updated_at = CURRENT_TIMESTAMP
        """, request.category.value, request.key, json.dumps(request.value),
            request.description, request.admin_id)
        
        # Log the change
        await db.execute("""
            INSERT INTO config_change_log (category, key, old_value, new_value, changed_by)
            VALUES ($1, $2, $3, $4, $5)
        """, request.category.value, request.key, old_value,
            json.dumps(request.value), request.admin_id)
        
        logger.info("config_updated",
                   category=request.category.value,
                   key=request.key,
                   admin_id=request.admin_id)
        
        return {"message": "Configuration updated successfully"}
        
    except Exception as e:
        logger.error("update_config_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/config/fees/trading")
async def set_trading_fees(
    request: TradingFeeConfig,
    admin_id: int = Query(...),
    db: asyncpg.Pool = Depends(get_db)
):
    """Set trading fees for a pair"""
    try:
        await db.execute("""
            INSERT INTO trading_fees (
                pair, maker_fee, taker_fee, min_order_size, max_order_size
            ) VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (pair)
            DO UPDATE SET
                maker_fee = $2,
                taker_fee = $3,
                min_order_size = $4,
                max_order_size = $5,
                updated_at = CURRENT_TIMESTAMP
        """, request.pair, request.maker_fee, request.taker_fee,
            request.min_order_size, request.max_order_size)
        
        logger.info("trading_fees_updated", pair=request.pair, admin_id=admin_id)
        return {"message": "Trading fees updated successfully"}
        
    except Exception as e:
        logger.error("set_trading_fees_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/config/fees/trading/{pair}")
async def get_trading_fees(
    pair: str,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get trading fees for a pair"""
    try:
        fees = await db.fetchrow("""
            SELECT * FROM trading_fees WHERE pair = $1 AND is_active = TRUE
        """, pair)
        
        if not fees:
            raise HTTPException(status_code=404, detail="Trading fees not found for this pair")
        
        return dict(fees)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_trading_fees_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/config/fees/withdrawal")
async def set_withdrawal_fees(
    request: WithdrawalFeeConfig,
    admin_id: int = Query(...),
    db: asyncpg.Pool = Depends(get_db)
):
    """Set withdrawal fees for a currency"""
    try:
        await db.execute("""
            INSERT INTO withdrawal_fees (
                currency, blockchain, fixed_fee, percentage_fee,
                min_withdrawal, max_withdrawal, daily_limit
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (currency, blockchain)
            DO UPDATE SET
                fixed_fee = $3,
                percentage_fee = $4,
                min_withdrawal = $5,
                max_withdrawal = $6,
                daily_limit = $7,
                updated_at = CURRENT_TIMESTAMP
        """, request.currency, request.blockchain, request.fixed_fee,
            request.percentage_fee, request.min_withdrawal,
            request.max_withdrawal, request.daily_limit)
        
        logger.info("withdrawal_fees_updated",
                   currency=request.currency,
                   blockchain=request.blockchain,
                   admin_id=admin_id)
        
        return {"message": "Withdrawal fees updated successfully"}
        
    except Exception as e:
        logger.error("set_withdrawal_fees_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/config/fees/withdrawal/{currency}")
async def get_withdrawal_fees(
    currency: str,
    blockchain: Optional[str] = None,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get withdrawal fees for a currency"""
    try:
        if blockchain:
            fees = await db.fetchrow("""
                SELECT * FROM withdrawal_fees
                WHERE currency = $1 AND blockchain = $2 AND is_active = TRUE
            """, currency, blockchain)
            
            if not fees:
                raise HTTPException(status_code=404, detail="Withdrawal fees not found")
            
            return dict(fees)
        else:
            fees = await db.fetch("""
                SELECT * FROM withdrawal_fees
                WHERE currency = $1 AND is_active = TRUE
            """, currency)
            
            return [dict(f) for f in fees]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_withdrawal_fees_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/config/blockchain")
async def set_blockchain_config(
    request: BlockchainConfig,
    admin_id: int = Query(...),
    db: asyncpg.Pool = Depends(get_db)
):
    """Set blockchain configuration"""
    try:
        await db.execute("""
            INSERT INTO blockchain_configs (
                blockchain, is_enabled, min_confirmations,
                node_url, explorer_url, supports_memo
            ) VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (blockchain)
            DO UPDATE SET
                is_enabled = $2,
                min_confirmations = $3,
                node_url = $4,
                explorer_url = $5,
                supports_memo = $6,
                updated_at = CURRENT_TIMESTAMP
        """, request.blockchain, request.is_enabled, request.min_confirmations,
            request.node_url, request.explorer_url, request.supports_memo)
        
        logger.info("blockchain_config_updated",
                   blockchain=request.blockchain,
                   admin_id=admin_id)
        
        return {"message": "Blockchain configuration updated successfully"}
        
    except Exception as e:
        logger.error("set_blockchain_config_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/config/blockchain")
async def get_blockchain_configs(
    is_enabled: Optional[bool] = None,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get all blockchain configurations"""
    try:
        if is_enabled is not None:
            configs = await db.fetch("""
                SELECT * FROM blockchain_configs WHERE is_enabled = $1
            """, is_enabled)
        else:
            configs = await db.fetch("SELECT * FROM blockchain_configs")
        
        return [dict(c) for c in configs]
        
    except Exception as e:
        logger.error("get_blockchain_configs_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/config/maintenance")
async def set_maintenance_mode(
    request: MaintenanceMode,
    admin_id: int = Query(...),
    db: asyncpg.Pool = Depends(get_db)
):
    """Set maintenance mode"""
    try:
        await db.execute("""
            INSERT INTO maintenance_schedules (
                is_enabled, message, start_time, end_time,
                affected_services, created_by
            ) VALUES ($1, $2, $3, $4, $5, $6)
        """, request.is_enabled, request.message, request.start_time,
            request.end_time, json.dumps(request.affected_services), admin_id)
        
        logger.info("maintenance_mode_set",
                   is_enabled=request.is_enabled,
                   admin_id=admin_id)
        
        return {"message": "Maintenance mode updated successfully"}
        
    except Exception as e:
        logger.error("set_maintenance_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/config/maintenance/current")
async def get_current_maintenance(db: asyncpg.Pool = Depends(get_db)):
    """Get current maintenance status"""
    try:
        maintenance = await db.fetchrow("""
            SELECT * FROM maintenance_schedules
            WHERE is_enabled = TRUE
            AND (end_time IS NULL OR end_time > CURRENT_TIMESTAMP)
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        if not maintenance:
            return {"is_enabled": False}
        
        return dict(maintenance)
        
    except Exception as e:
        logger.error("get_maintenance_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/config/changelog")
async def get_config_changelog(
    category: Optional[ConfigCategory] = None,
    limit: int = 100,
    offset: int = 0,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get configuration change log"""
    try:
        if category:
            logs = await db.fetch("""
                SELECT * FROM config_change_log
                WHERE category = $1
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3
            """, category.value, limit, offset)
        else:
            logs = await db.fetch("""
                SELECT * FROM config_change_log
                ORDER BY created_at DESC
                LIMIT $1 OFFSET $2
            """, limit, offset)
        
        return [dict(log) for log in logs]
        
    except Exception as e:
        logger.error("get_changelog_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "system-configuration-service",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.on_event("startup")
async def startup():
    """Initialize service on startup"""
    await init_db()
    logger.info("System Configuration Service started")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    if db_pool:
        await db_pool.close()
    logger.info("System Configuration Service stopped")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8250)