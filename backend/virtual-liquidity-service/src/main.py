/*
 * TigerEx Exchange Platform
 * Version: 7.0.0 - Consolidated Production Release
 * 
 * Complete cryptocurrency exchange platform with:
 * - CEX/DEX hybrid functionality
 * - 105+ exchange features
 * - Multi-platform support (Web, Mobile, Desktop)
 * - Enterprise-grade security
 * - White-label deployment ready
 * 
 * Production-ready implementation
 */

"""
TigerEx Virtual Liquidity Management Service
Manages virtual asset reserves, liquidity pools, and IOU tokens
Port: 8150
"""

from fastapi import FastAPI
from admin.admin_routes import router as admin_router
from fastapi import HTTPException, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
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
from contextlib import asynccontextmanager

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

# Global connections
db_pool = None
redis_client = None

# Enums
class AssetType(str, Enum):
    STABLECOIN = "stablecoin"
    CRYPTO = "crypto"
    FIAT = "fiat"

class PoolType(str, Enum):
    AMM = "amm"
    ORDERBOOK = "orderbook"
    HYBRID = "hybrid"

class RebalanceType(str, Enum):
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    EMERGENCY = "emergency"

class IOUStatus(str, Enum):
    ACTIVE = "active"
    CONVERTING = "converting"
    CONVERTED = "converted"
    EXPIRED = "expired"

# Pydantic Models
class VirtualReserveCreate(BaseModel):
    asset_symbol: str = Field(..., min_length=1, max_length=10)
    asset_name: str = Field(..., min_length=1, max_length=100)
    asset_type: AssetType
    total_reserve: Decimal = Field(..., gt=0)
    max_allocation_per_pool: Decimal = Field(..., gt=0)
    min_reserve_threshold: Decimal = Field(..., gt=0)
    backing_ratio: Decimal = Field(default=Decimal("1.0"), ge=0, le=1)
    real_asset_backing: Decimal = Field(default=Decimal("0"))
    auto_rebalance_enabled: bool = True

class VirtualReserveUpdate(BaseModel):
    total_reserve: Optional[Decimal] = Field(None, gt=0)
    available_reserve: Optional[Decimal] = Field(None, ge=0)
    max_allocation_per_pool: Optional[Decimal] = Field(None, gt=0)
    min_reserve_threshold: Optional[Decimal] = Field(None, gt=0)
    backing_ratio: Optional[Decimal] = Field(None, ge=0, le=1)
    real_asset_backing: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None
    auto_rebalance_enabled: Optional[bool] = None

class LiquidityPoolCreate(BaseModel):
    pool_name: str = Field(..., min_length=1, max_length=100)
    pool_type: PoolType
    base_asset: str = Field(..., min_length=1, max_length=10)
    quote_asset: str = Field(..., min_length=1, max_length=10)
    base_reserve: Decimal = Field(..., ge=0)
    quote_reserve: Decimal = Field(..., ge=0)
    virtual_base_liquidity: Decimal = Field(default=Decimal("0"), ge=0)
    virtual_quote_liquidity: Decimal = Field(default=Decimal("0"), ge=0)
    fee_rate: Decimal = Field(default=Decimal("0.003"), ge=0, le=1)
    protocol_fee_rate: Decimal = Field(default=Decimal("0.0005"), ge=0, le=1)
    is_public: bool = True

class IOUTokenCreate(BaseModel):
    token_symbol: str = Field(..., min_length=1, max_length=10)
    token_name: str = Field(..., min_length=1, max_length=100)
    underlying_asset: str = Field(..., min_length=1, max_length=10)
    total_supply: Decimal = Field(..., gt=0)
    conversion_ratio: Decimal = Field(default=Decimal("1.0"), gt=0)
    is_convertible: bool = False
    conversion_start_date: Optional[datetime] = None
    conversion_end_date: Optional[datetime] = None
    description: Optional[str] = None
    launch_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None

class LiquidityAllocationCreate(BaseModel):
    reserve_id: int
    pool_id: int
    allocated_amount: Decimal = Field(..., gt=0)
    asset_symbol: str = Field(..., min_length=1, max_length=10)

class RebalanceRequest(BaseModel):
    reserve_id: int
    rebalance_type: RebalanceType
    amount_to_add: Optional[Decimal] = Field(None, ge=0)
    amount_to_remove: Optional[Decimal] = Field(None, ge=0)
    trigger_reason: Optional[str] = None
    notes: Optional[str] = None

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global db_pool, redis_client
    
    logger.info("Starting Virtual Liquidity Service...")
    
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
    
    # Start background tasks
    asyncio.create_task(auto_rebalance_task())
    asyncio.create_task(update_pool_metrics_task())
    
    logger.info("Virtual Liquidity Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Virtual Liquidity Service...")
    
    if db_pool:
        await db_pool.close()
    if redis_client:
        await redis_client.close()
    
    logger.info("Virtual Liquidity Service shut down")

# Initialize FastAPI app
app = FastAPI(

# Include admin router
app.include_router(admin_router)
    title="TigerEx Virtual Liquidity Management Service",
    description="Manages virtual asset reserves, liquidity pools, and IOU tokens",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper functions
async def get_db():
    async with db_pool.acquire() as conn:
        yield conn

# Background Tasks
async def auto_rebalance_task():
    """Automatically rebalance reserves based on utilization"""
    while True:
        try:
            await asyncio.sleep(3600)  # Run every hour
            
            async with db_pool.acquire() as conn:
                # Get reserves that need rebalancing
                reserves = await conn.fetch("""
                    SELECT id, reserve_id, asset_symbol, total_reserve, 
                           available_reserve, allocated_to_pools,
                           min_reserve_threshold, auto_rebalance_enabled
                    FROM virtual_asset_reserves
                    WHERE is_active = true AND auto_rebalance_enabled = true
                """)
                
                for reserve in reserves:
                    utilization = float(reserve['allocated_to_pools']) / float(reserve['total_reserve'])
                    
                    # If utilization > 80%, add more reserves
                    if utilization > 0.8:
                        amount_to_add = float(reserve['total_reserve']) * 0.2  # Add 20%
                        
                        await conn.execute("""
                            INSERT INTO reserve_rebalancing_history (
                                rebalance_id, reserve_id, rebalance_type, trigger_reason,
                                before_total_reserve, before_available, before_allocated,
                                after_total_reserve, after_available, after_allocated,
                                amount_added, executed_by
                            ) VALUES (
                                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12
                            )
                        """, 
                        f"REBAL_{reserve['reserve_id']}_{int(datetime.now().timestamp())}",
                        reserve['id'], 'automatic', 'High utilization detected',
                        reserve['total_reserve'], reserve['available_reserve'], 
                        reserve['allocated_to_pools'],
                        reserve['total_reserve'] + Decimal(str(amount_to_add)),
                        reserve['available_reserve'] + Decimal(str(amount_to_add)),
                        reserve['allocated_to_pools'],
                        Decimal(str(amount_to_add)), 'system')
                        
                        await conn.execute("""
                            UPDATE virtual_asset_reserves
                            SET total_reserve = total_reserve + $1,
                                available_reserve = available_reserve + $1,
                                last_rebalanced_at = NOW()
                            WHERE id = $2
                        """, Decimal(str(amount_to_add)), reserve['id'])
                        
                        logger.info(f"Auto-rebalanced reserve {reserve['reserve_id']}", 
                                  amount_added=amount_to_add)
                
        except Exception as e:
            logger.error(f"Error in auto_rebalance_task: {str(e)}")

async def update_pool_metrics_task():
    """Update liquidity pool metrics"""
    while True:
        try:
            await asyncio.sleep(300)  # Run every 5 minutes
            
            async with db_pool.acquire() as conn:
                # Update pool metrics
                await conn.execute("""
                    UPDATE liquidity_pools
                    SET total_liquidity_usd = (base_reserve * current_price) + quote_reserve,
                        virtual_liquidity_percentage = 
                            CASE 
                                WHEN (base_reserve + quote_reserve) > 0 
                                THEN (virtual_base_liquidity + virtual_quote_liquidity) / 
                                     (base_reserve + quote_reserve)
                                ELSE 0
                            END,
                        updated_at = NOW()
                    WHERE is_active = true
                """)
                
                logger.info("Updated pool metrics")
                
        except Exception as e:
            logger.error(f"Error in update_pool_metrics_task: {str(e)}")

# API Endpoints

# Health Check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "virtual-liquidity-service",
        "timestamp": datetime.utcnow().isoformat()
    }

# Virtual Asset Reserves Endpoints

@app.post("/api/reserves", status_code=201)
async def create_reserve(reserve: VirtualReserveCreate):
    """Create a new virtual asset reserve"""
    try:
        async with db_pool.acquire() as conn:
            reserve_id = f"V{reserve.asset_symbol}_RESERVE_{int(datetime.now().timestamp())}"
            
            result = await conn.fetchrow("""
                INSERT INTO virtual_asset_reserves (
                    reserve_id, asset_symbol, asset_name, asset_type,
                    total_reserve, available_reserve, max_allocation_per_pool,
                    min_reserve_threshold, backing_ratio, real_asset_backing,
                    is_virtual, auto_rebalance_enabled, created_by
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                RETURNING *
            """, reserve_id, reserve.asset_symbol, reserve.asset_name, 
            reserve.asset_type.value, reserve.total_reserve, reserve.total_reserve,
            reserve.max_allocation_per_pool, reserve.min_reserve_threshold,
            reserve.backing_ratio, reserve.real_asset_backing, True,
            reserve.auto_rebalance_enabled, 'admin')
            
            logger.info(f"Created virtual reserve: {reserve_id}")
            return dict(result)
            
    except Exception as e:
        logger.error(f"Error creating reserve: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reserves")
async def get_reserves(
    asset_symbol: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
):
    """Get all virtual asset reserves"""
    try:
        async with db_pool.acquire() as conn:
            query = "SELECT * FROM virtual_asset_reserves WHERE 1=1"
            params = []
            param_count = 0
            
            if asset_symbol:
                param_count += 1
                query += f" AND asset_symbol = ${param_count}"
                params.append(asset_symbol)
            
            if is_active is not None:
                param_count += 1
                query += f" AND is_active = ${param_count}"
                params.append(is_active)
            
            query += f" ORDER BY created_at DESC OFFSET ${param_count + 1} LIMIT ${param_count + 2}"
            params.extend([skip, limit])
            
            reserves = await conn.fetch(query, *params)
            total = await conn.fetchval(
                "SELECT COUNT(*) FROM virtual_asset_reserves WHERE 1=1" + 
                (f" AND asset_symbol = '{asset_symbol}'" if asset_symbol else "") +
                (f" AND is_active = {is_active}" if is_active is not None else "")
            )
            
            return {
                "total": total,
                "reserves": [dict(r) for r in reserves]
            }
            
    except Exception as e:
        logger.error(f"Error fetching reserves: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reserves/{reserve_id}")
async def get_reserve(reserve_id: str):
    """Get a specific virtual asset reserve"""
    try:
        async with db_pool.acquire() as conn:
            reserve = await conn.fetchrow("""
                SELECT * FROM virtual_asset_reserves WHERE reserve_id = $1
            """, reserve_id)
            
            if not reserve:
                raise HTTPException(status_code=404, detail="Reserve not found")
            
            return dict(reserve)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching reserve: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/reserves/{reserve_id}")
async def update_reserve(reserve_id: str, update: VirtualReserveUpdate):
    """Update a virtual asset reserve"""
    try:
        async with db_pool.acquire() as conn:
            # Build update query dynamically
            updates = []
            params = []
            param_count = 0
            
            for field, value in update.dict(exclude_unset=True).items():
                if value is not None:
                    param_count += 1
                    updates.append(f"{field} = ${param_count}")
                    params.append(value)
            
            if not updates:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            param_count += 1
            params.append(reserve_id)
            
            query = f"""
                UPDATE virtual_asset_reserves
                SET {', '.join(updates)}, updated_at = NOW()
                WHERE reserve_id = ${param_count}
                RETURNING *
            """
            
            result = await conn.fetchrow(query, *params)
            
            if not result:
                raise HTTPException(status_code=404, detail="Reserve not found")
            
            logger.info(f"Updated reserve: {reserve_id}")
            return dict(result)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating reserve: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reserves/{reserve_id}/rebalance")
async def rebalance_reserve(reserve_id: str, request: RebalanceRequest):
    """Manually rebalance a virtual asset reserve"""
    try:
        async with db_pool.acquire() as conn:
            # Get current reserve state
            reserve = await conn.fetchrow("""
                SELECT * FROM virtual_asset_reserves WHERE reserve_id = $1
            """, reserve_id)
            
            if not reserve:
                raise HTTPException(status_code=404, detail="Reserve not found")
            
            # Calculate new amounts
            amount_added = request.amount_to_add or Decimal("0")
            amount_removed = request.amount_to_remove or Decimal("0")
            
            new_total = reserve['total_reserve'] + amount_added - amount_removed
            new_available = reserve['available_reserve'] + amount_added - amount_removed
            
            if new_total < 0 or new_available < 0:
                raise HTTPException(status_code=400, detail="Invalid rebalance amounts")
            
            # Record rebalancing history
            rebalance_id = f"REBAL_{reserve_id}_{int(datetime.now().timestamp())}"
            
            await conn.execute("""
                INSERT INTO reserve_rebalancing_history (
                    rebalance_id, reserve_id, rebalance_type, trigger_reason,
                    before_total_reserve, before_available, before_allocated,
                    after_total_reserve, after_available, after_allocated,
                    amount_added, amount_removed, executed_by, notes
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
            """, rebalance_id, reserve['id'], request.rebalance_type.value,
            request.trigger_reason, reserve['total_reserve'], 
            reserve['available_reserve'], reserve['allocated_to_pools'],
            new_total, new_available, reserve['allocated_to_pools'],
            amount_added, amount_removed, 'admin', request.notes)
            
            # Update reserve
            updated_reserve = await conn.fetchrow("""
                UPDATE virtual_asset_reserves
                SET total_reserve = $1,
                    available_reserve = $2,
                    last_rebalanced_at = NOW(),
                    updated_at = NOW()
                WHERE reserve_id = $3
                RETURNING *
            """, new_total, new_available, reserve_id)
            
            logger.info(f"Rebalanced reserve: {reserve_id}", 
                       amount_added=float(amount_added),
                       amount_removed=float(amount_removed))
            
            return dict(updated_reserve)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rebalancing reserve: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Liquidity Pool Endpoints

@app.post("/api/pools", status_code=201)
async def create_pool(pool: LiquidityPoolCreate):
    """Create a new liquidity pool"""
    try:
        async with db_pool.acquire() as conn:
            trading_pair = f"{pool.base_asset}{pool.quote_asset}"
            pool_id = f"POOL_{trading_pair}_{int(datetime.now().timestamp())}"
            
            # Calculate virtual liquidity percentage
            total_liquidity = pool.base_reserve + pool.quote_reserve
            virtual_liquidity = pool.virtual_base_liquidity + pool.virtual_quote_liquidity
            virtual_percentage = virtual_liquidity / total_liquidity if total_liquidity > 0 else Decimal("0")
            
            result = await conn.fetchrow("""
                INSERT INTO liquidity_pools (
                    pool_id, pool_name, pool_type, base_asset, quote_asset, trading_pair,
                    base_reserve, quote_reserve, virtual_base_liquidity, virtual_quote_liquidity,
                    virtual_liquidity_percentage, fee_rate, protocol_fee_rate,
                    is_active, is_public, created_by
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                RETURNING *
            """, pool_id, pool.pool_name, pool.pool_type.value, pool.base_asset,
            pool.quote_asset, trading_pair, pool.base_reserve, pool.quote_reserve,
            pool.virtual_base_liquidity, pool.virtual_quote_liquidity,
            virtual_percentage, pool.fee_rate, pool.protocol_fee_rate,
            True, pool.is_public, 'admin')
            
            logger.info(f"Created liquidity pool: {pool_id}")
            return dict(result)
            
    except Exception as e:
        logger.error(f"Error creating pool: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pools")
async def get_pools(
    trading_pair: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
):
    """Get all liquidity pools"""
    try:
        async with db_pool.acquire() as conn:
            query = "SELECT * FROM liquidity_pools WHERE 1=1"
            params = []
            param_count = 0
            
            if trading_pair:
                param_count += 1
                query += f" AND trading_pair = ${param_count}"
                params.append(trading_pair)
            
            if is_active is not None:
                param_count += 1
                query += f" AND is_active = ${param_count}"
                params.append(is_active)
            
            query += f" ORDER BY created_at DESC OFFSET ${param_count + 1} LIMIT ${param_count + 2}"
            params.extend([skip, limit])
            
            pools = await conn.fetch(query, *params)
            total = await conn.fetchval(
                "SELECT COUNT(*) FROM liquidity_pools WHERE 1=1" +
                (f" AND trading_pair = '{trading_pair}'" if trading_pair else "") +
                (f" AND is_active = {is_active}" if is_active is not None else "")
            )
            
            return {
                "total": total,
                "pools": [dict(p) for p in pools]
            }
            
    except Exception as e:
        logger.error(f"Error fetching pools: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pools/{pool_id}")
async def get_pool(pool_id: str):
    """Get a specific liquidity pool"""
    try:
        async with db_pool.acquire() as conn:
            pool = await conn.fetchrow("""
                SELECT * FROM liquidity_pools WHERE pool_id = $1
            """, pool_id)
            
            if not pool:
                raise HTTPException(status_code=404, detail="Pool not found")
            
            return dict(pool)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching pool: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# IOU Token Endpoints

@app.post("/api/iou-tokens", status_code=201)
async def create_iou_token(token: IOUTokenCreate):
    """Create a new IOU token"""
    try:
        async with db_pool.acquire() as conn:
            iou_id = f"IOU_{token.token_symbol}_{int(datetime.now().timestamp())}"
            
            result = await conn.fetchrow("""
                INSERT INTO iou_tokens (
                    iou_id, token_symbol, token_name, underlying_asset,
                    total_supply, circulating_supply, conversion_ratio,
                    is_convertible, conversion_start_date, conversion_end_date,
                    is_tradable, status, description, launch_date, expiry_date,
                    created_by
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                RETURNING *
            """, iou_id, token.token_symbol, token.token_name, token.underlying_asset,
            token.total_supply, Decimal("0"), token.conversion_ratio,
            token.is_convertible, token.conversion_start_date, token.conversion_end_date,
            True, 'active', token.description, token.launch_date, token.expiry_date,
            'admin')
            
            logger.info(f"Created IOU token: {iou_id}")
            return dict(result)
            
    except Exception as e:
        logger.error(f"Error creating IOU token: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/iou-tokens")
async def get_iou_tokens(
    status: Optional[IOUStatus] = None,
    skip: int = 0,
    limit: int = 100
):
    """Get all IOU tokens"""
    try:
        async with db_pool.acquire() as conn:
            query = "SELECT * FROM iou_tokens WHERE 1=1"
            params = []
            param_count = 0
            
            if status:
                param_count += 1
                query += f" AND status = ${param_count}"
                params.append(status.value)
            
            query += f" ORDER BY created_at DESC OFFSET ${param_count + 1} LIMIT ${param_count + 2}"
            params.extend([skip, limit])
            
            tokens = await conn.fetch(query, *params)
            total = await conn.fetchval(
                "SELECT COUNT(*) FROM iou_tokens WHERE 1=1" +
                (f" AND status = '{status.value}'" if status else "")
            )
            
            return {
                "total": total,
                "tokens": [dict(t) for t in tokens]
            }
            
    except Exception as e:
        logger.error(f"Error fetching IOU tokens: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/iou-tokens/{iou_id}")
async def get_iou_token(iou_id: str):
    """Get a specific IOU token"""
    try:
        async with db_pool.acquire() as conn:
            token = await conn.fetchrow("""
                SELECT * FROM iou_tokens WHERE iou_id = $1
            """, iou_id)
            
            if not token:
                raise HTTPException(status_code=404, detail="IOU token not found")
            
            return dict(token)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching IOU token: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Virtual Liquidity Allocation Endpoints

@app.post("/api/allocations", status_code=201)
async def create_allocation(allocation: LiquidityAllocationCreate):
    """Allocate virtual liquidity to a pool"""
    try:
        async with db_pool.acquire() as conn:
            # Verify reserve has enough available liquidity
            reserve = await conn.fetchrow("""
                SELECT * FROM virtual_asset_reserves WHERE id = $1
            """, allocation.reserve_id)
            
            if not reserve:
                raise HTTPException(status_code=404, detail="Reserve not found")
            
            if reserve['available_reserve'] < allocation.allocated_amount:
                raise HTTPException(status_code=400, detail="Insufficient available reserve")
            
            # Create allocation
            allocation_id = f"ALLOC_{allocation.asset_symbol}_{int(datetime.now().timestamp())}"
            
            result = await conn.fetchrow("""
                INSERT INTO virtual_liquidity_allocations (
                    allocation_id, reserve_id, pool_id, allocated_amount,
                    asset_symbol, is_active
                ) VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
            """, allocation_id, allocation.reserve_id, allocation.pool_id,
            allocation.allocated_amount, allocation.asset_symbol, True)
            
            # Update reserve
            await conn.execute("""
                UPDATE virtual_asset_reserves
                SET available_reserve = available_reserve - $1,
                    allocated_to_pools = allocated_to_pools + $1,
                    updated_at = NOW()
                WHERE id = $2
            """, allocation.allocated_amount, allocation.reserve_id)
            
            logger.info(f"Created liquidity allocation: {allocation_id}")
            return dict(result)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating allocation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/allocations")
async def get_allocations(
    reserve_id: Optional[int] = None,
    pool_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
):
    """Get all virtual liquidity allocations"""
    try:
        async with db_pool.acquire() as conn:
            query = "SELECT * FROM virtual_liquidity_allocations WHERE 1=1"
            params = []
            param_count = 0
            
            if reserve_id:
                param_count += 1
                query += f" AND reserve_id = ${param_count}"
                params.append(reserve_id)
            
            if pool_id:
                param_count += 1
                query += f" AND pool_id = ${param_count}"
                params.append(pool_id)
            
            if is_active is not None:
                param_count += 1
                query += f" AND is_active = ${param_count}"
                params.append(is_active)
            
            query += f" ORDER BY allocated_at DESC OFFSET ${param_count + 1} LIMIT ${param_count + 2}"
            params.extend([skip, limit])
            
            allocations = await conn.fetch(query, *params)
            total = await conn.fetchval(
                "SELECT COUNT(*) FROM virtual_liquidity_allocations WHERE 1=1" +
                (f" AND reserve_id = {reserve_id}" if reserve_id else "") +
                (f" AND pool_id = {pool_id}" if pool_id else "") +
                (f" AND is_active = {is_active}" if is_active is not None else "")
            )
            
            return {
                "total": total,
                "allocations": [dict(a) for a in allocations]
            }
            
    except Exception as e:
        logger.error(f"Error fetching allocations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics Endpoints

@app.get("/api/analytics/overview")
async def get_analytics_overview():
    """Get overall virtual liquidity analytics"""
    try:
        async with db_pool.acquire() as conn:
            # Reserve metrics
            reserve_metrics = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_reserves,
                    COUNT(*) FILTER (WHERE is_active = true) as active_reserves,
                    COALESCE(SUM(total_reserve), 0) as total_reserve_value,
                    COALESCE(SUM(available_reserve), 0) as total_available,
                    COALESCE(SUM(allocated_to_pools), 0) as total_allocated,
                    COALESCE(AVG(utilization_rate), 0) as avg_utilization
                FROM virtual_asset_reserves
            """)
            
            # Pool metrics
            pool_metrics = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_pools,
                    COUNT(*) FILTER (WHERE is_active = true) as active_pools,
                    COALESCE(SUM(total_liquidity_usd), 0) as total_liquidity_usd,
                    COALESCE(SUM(total_volume_24h), 0) as total_volume_24h,
                    COALESCE(AVG(virtual_liquidity_percentage), 0) as avg_virtual_percentage
                FROM liquidity_pools
            """)
            
            # IOU token metrics
            iou_metrics = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_iou_tokens,
                    COUNT(*) FILTER (WHERE status = 'active') as active_iou_tokens,
                    COALESCE(SUM(total_supply), 0) as total_iou_supply,
                    COALESCE(SUM(circulating_supply), 0) as total_iou_circulation
                FROM iou_tokens
            """)
            
            return {
                "reserves": dict(reserve_metrics),
                "pools": dict(pool_metrics),
                "iou_tokens": dict(iou_metrics),
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/reserves/{reserve_id}/performance")
async def get_reserve_performance(reserve_id: str):
    """Get performance metrics for a specific reserve"""
    try:
        async with db_pool.acquire() as conn:
            reserve = await conn.fetchrow("""
                SELECT * FROM virtual_asset_reserves WHERE reserve_id = $1
            """, reserve_id)
            
            if not reserve:
                raise HTTPException(status_code=404, detail="Reserve not found")
            
            # Get allocation performance
            allocations = await conn.fetch("""
                SELECT 
                    pool_id,
                    allocated_amount,
                    fees_generated,
                    volume_facilitated,
                    trades_facilitated,
                    utilization_rate
                FROM virtual_liquidity_allocations
                WHERE reserve_id = $1 AND is_active = true
            """, reserve['id'])
            
            # Get rebalancing history
            rebalances = await conn.fetch("""
                SELECT * FROM reserve_rebalancing_history
                WHERE reserve_id = $1
                ORDER BY executed_at DESC
                LIMIT 10
            """, reserve['id'])
            
            return {
                "reserve": dict(reserve),
                "allocations": [dict(a) for a in allocations],
                "recent_rebalances": [dict(r) for r in rebalances],
                "total_fees_generated": sum(float(a['fees_generated']) for a in allocations),
                "total_volume_facilitated": sum(float(a['volume_facilitated']) for a in allocations)
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching reserve performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8150)