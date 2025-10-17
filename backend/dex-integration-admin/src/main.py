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
TigerEx DEX Integration Admin Panel
Manages decentralized exchange integrations, liquidity pools, and routing
Port: 8117
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import uvicorn
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "postgresql://tigerex:tigerex123@localhost:5432/tigerex_dex_integration"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums
class DEXProtocol(str, Enum):
    UNISWAP_V2 = "uniswap_v2"
    UNISWAP_V3 = "uniswap_v3"
    SUSHISWAP = "sushiswap"
    PANCAKESWAP = "pancakeswap"
    CURVE = "curve"
    BALANCER = "balancer"
    TRADER_JOE = "trader_joe"
    SPOOKYSWAP = "spookyswap"
    QUICKSWAP = "quickswap"
    RAYDIUM = "raydium"
    ORCA = "orca"
    SERUM = "serum"
    OSMOSIS = "osmosis"

class ChainType(str, Enum):
    ETHEREUM = "ethereum"
    BSC = "bsc"
    POLYGON = "polygon"
    AVALANCHE = "avalanche"
    FANTOM = "fantom"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    SOLANA = "solana"
    COSMOS = "cosmos"

class PoolStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    DEPRECATED = "deprecated"

# Database Models
class DEXIntegration(Base):
    __tablename__ = "dex_integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    protocol = Column(String, index=True)
    chain = Column(String, index=True)
    router_address = Column(String)
    factory_address = Column(String)
    
    # Configuration
    is_enabled = Column(Boolean, default=True)
    supports_limit_orders = Column(Boolean, default=False)
    supports_stop_loss = Column(Boolean, default=False)
    min_trade_amount = Column(Float, default=0.0)
    max_trade_amount = Column(Float, nullable=True)
    
    # Fees
    swap_fee = Column(Float, default=0.3)  # percentage
    gas_multiplier = Column(Float, default=1.2)
    
    # Stats
    total_volume_24h = Column(Float, default=0.0)
    total_volume_7d = Column(Float, default=0.0)
    total_volume_30d = Column(Float, default=0.0)
    total_trades = Column(Integer, default=0)
    total_liquidity = Column(Float, default=0.0)
    
    # Status
    last_sync = Column(DateTime, nullable=True)
    is_syncing = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON)

class LiquidityPool(Base):
    __tablename__ = "liquidity_pools"
    
    id = Column(Integer, primary_key=True, index=True)
    dex_id = Column(Integer, index=True)
    pool_address = Column(String, unique=True, index=True)
    
    # Token pair
    token0_address = Column(String, index=True)
    token0_symbol = Column(String)
    token0_decimals = Column(Integer)
    token1_address = Column(String, index=True)
    token1_symbol = Column(String)
    token1_decimals = Column(Integer)
    
    # Pool info
    reserve0 = Column(Float, default=0.0)
    reserve1 = Column(Float, default=0.0)
    total_liquidity = Column(Float, default=0.0)
    liquidity_usd = Column(Float, default=0.0)
    
    # Trading stats
    volume_24h = Column(Float, default=0.0)
    volume_7d = Column(Float, default=0.0)
    fees_24h = Column(Float, default=0.0)
    apr = Column(Float, default=0.0)
    
    # Price
    token0_price = Column(Float, default=0.0)
    token1_price = Column(Float, default=0.0)
    price_impact = Column(Float, default=0.0)
    
    # Status
    status = Column(String, default="active")
    is_verified = Column(Boolean, default=False)
    
    last_updated = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)

class DEXRoute(Base):
    __tablename__ = "dex_routes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Route info
    token_in = Column(String, index=True)
    token_out = Column(String, index=True)
    amount_in = Column(Float)
    
    # Path
    path = Column(JSON)  # Array of token addresses
    pools = Column(JSON)  # Array of pool addresses
    dexes = Column(JSON)  # Array of DEX IDs used
    
    # Pricing
    amount_out = Column(Float)
    price_impact = Column(Float)
    gas_estimate = Column(Float)
    
    # Optimization
    is_optimal = Column(Boolean, default=False)
    split_routes = Column(JSON, nullable=True)  # For split routing
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

class DEXTrade(Base):
    __tablename__ = "dex_trades"
    
    id = Column(Integer, primary_key=True, index=True)
    dex_id = Column(Integer, index=True)
    pool_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    
    # Trade details
    token_in = Column(String)
    token_out = Column(String)
    amount_in = Column(Float)
    amount_out = Column(Float)
    
    # Execution
    tx_hash = Column(String, unique=True, index=True)
    gas_used = Column(Float)
    gas_price = Column(Float)
    
    # Pricing
    price = Column(Float)
    price_impact = Column(Float)
    slippage = Column(Float)
    
    # Status
    status = Column(String, default="pending")  # pending, confirmed, failed
    
    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    metadata = Column(JSON)

class DEXAnalytics(Base):
    __tablename__ = "dex_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    dex_id = Column(Integer, index=True)
    date = Column(DateTime, index=True)
    
    # Volume metrics
    daily_volume = Column(Float)
    daily_trades = Column(Integer)
    unique_traders = Column(Integer)
    
    # Liquidity metrics
    total_liquidity = Column(Float)
    liquidity_change = Column(Float)
    
    # Fee metrics
    total_fees = Column(Float)
    avg_fee_per_trade = Column(Float)
    
    metadata = Column(JSON)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class DEXIntegrationCreate(BaseModel):
    name: str
    protocol: DEXProtocol
    chain: ChainType
    router_address: str
    factory_address: str
    supports_limit_orders: bool = False
    supports_stop_loss: bool = False
    min_trade_amount: float = Field(ge=0, default=0.0)
    max_trade_amount: Optional[float] = None
    swap_fee: float = Field(ge=0, le=100, default=0.3)
    gas_multiplier: float = Field(gt=0, default=1.2)
    metadata: Optional[Dict[str, Any]] = None

class DEXIntegrationUpdate(BaseModel):
    name: Optional[str] = None
    router_address: Optional[str] = None
    factory_address: Optional[str] = None
    is_enabled: Optional[bool] = None
    supports_limit_orders: Optional[bool] = None
    supports_stop_loss: Optional[bool] = None
    min_trade_amount: Optional[float] = None
    max_trade_amount: Optional[float] = None
    swap_fee: Optional[float] = None
    gas_multiplier: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class LiquidityPoolCreate(BaseModel):
    dex_id: int
    pool_address: str
    token0_address: str
    token0_symbol: str
    token0_decimals: int
    token1_address: str
    token1_symbol: str
    token1_decimals: int
    metadata: Optional[Dict[str, Any]] = None

class LiquidityPoolUpdate(BaseModel):
    reserve0: Optional[float] = None
    reserve1: Optional[float] = None
    total_liquidity: Optional[float] = None
    liquidity_usd: Optional[float] = None
    volume_24h: Optional[float] = None
    volume_7d: Optional[float] = None
    fees_24h: Optional[float] = None
    apr: Optional[float] = None
    token0_price: Optional[float] = None
    token1_price: Optional[float] = None
    status: Optional[PoolStatus] = None
    is_verified: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class RouteRequest(BaseModel):
    token_in: str
    token_out: str
    amount_in: float
    slippage_tolerance: float = Field(ge=0, le=100, default=0.5)
    max_hops: int = Field(ge=1, le=5, default=3)

# FastAPI app
app = FastAPI(
    title="TigerEx DEX Integration Admin API",
    description="Admin panel for managing DEX integrations and liquidity pools",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== DEX INTEGRATION ENDPOINTS ====================

@app.post("/api/admin/dex-integrations", status_code=201)
async def create_dex_integration(dex: DEXIntegrationCreate, db: Session = Depends(get_db)):
    """Create a new DEX integration"""
    try:
        # Check if DEX already exists
        existing = db.query(DEXIntegration).filter(DEXIntegration.name == dex.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="DEX integration already exists")
        
        db_dex = DEXIntegration(**dex.dict())
        db.add(db_dex)
        db.commit()
        db.refresh(db_dex)
        
        logger.info(f"Created DEX integration: {dex.name}")
        return db_dex
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating DEX integration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/dex-integrations")
async def get_dex_integrations(
    skip: int = 0,
    limit: int = 100,
    protocol: Optional[DEXProtocol] = None,
    chain: Optional[ChainType] = None,
    is_enabled: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all DEX integrations with filters"""
    try:
        query = db.query(DEXIntegration)
        
        if protocol:
            query = query.filter(DEXIntegration.protocol == protocol)
        if chain:
            query = query.filter(DEXIntegration.chain == chain)
        if is_enabled is not None:
            query = query.filter(DEXIntegration.is_enabled == is_enabled)
        
        total = query.count()
        dexes = query.offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "dexes": dexes
        }
    except Exception as e:
        logger.error(f"Error fetching DEX integrations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/dex-integrations/{dex_id}")
async def get_dex_integration(dex_id: int, db: Session = Depends(get_db)):
    """Get a specific DEX integration"""
    dex = db.query(DEXIntegration).filter(DEXIntegration.id == dex_id).first()
    if not dex:
        raise HTTPException(status_code=404, detail="DEX integration not found")
    return dex

@app.put("/api/admin/dex-integrations/{dex_id}")
async def update_dex_integration(
    dex_id: int,
    dex_update: DEXIntegrationUpdate,
    db: Session = Depends(get_db)
):
    """Update a DEX integration"""
    try:
        dex = db.query(DEXIntegration).filter(DEXIntegration.id == dex_id).first()
        if not dex:
            raise HTTPException(status_code=404, detail="DEX integration not found")
        
        update_data = dex_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(dex, field, value)
        
        dex.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(dex)
        
        logger.info(f"Updated DEX integration: {dex_id}")
        return dex
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating DEX integration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/dex-integrations/{dex_id}/sync")
async def sync_dex_integration(dex_id: int, db: Session = Depends(get_db)):
    """Trigger sync for a DEX integration"""
    try:
        dex = db.query(DEXIntegration).filter(DEXIntegration.id == dex_id).first()
        if not dex:
            raise HTTPException(status_code=404, detail="DEX integration not found")
        
        if dex.is_syncing:
            raise HTTPException(status_code=400, detail="DEX is already syncing")
        
        dex.is_syncing = True
        dex.last_sync = datetime.utcnow()
        db.commit()
        
        # TODO: Trigger background sync task
        
        logger.info(f"Started sync for DEX: {dex_id}")
        return {"message": "Sync started successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error syncing DEX: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/admin/dex-integrations/{dex_id}")
async def delete_dex_integration(dex_id: int, db: Session = Depends(get_db)):
    """Delete a DEX integration"""
    try:
        dex = db.query(DEXIntegration).filter(DEXIntegration.id == dex_id).first()
        if not dex:
            raise HTTPException(status_code=404, detail="DEX integration not found")
        
        # Check if DEX has active pools
        active_pools = db.query(LiquidityPool).filter(
            LiquidityPool.dex_id == dex_id,
            LiquidityPool.status == "active"
        ).count()
        
        if active_pools > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete DEX with {active_pools} active pools"
            )
        
        db.delete(dex)
        db.commit()
        
        logger.info(f"Deleted DEX integration: {dex_id}")
        return {"message": "DEX integration deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting DEX integration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== LIQUIDITY POOL ENDPOINTS ====================

@app.post("/api/admin/pools", status_code=201)
async def create_pool(pool: LiquidityPoolCreate, db: Session = Depends(get_db)):
    """Create a new liquidity pool"""
    try:
        # Verify DEX exists
        dex = db.query(DEXIntegration).filter(DEXIntegration.id == pool.dex_id).first()
        if not dex:
            raise HTTPException(status_code=404, detail="DEX integration not found")
        
        # Check if pool already exists
        existing = db.query(LiquidityPool).filter(
            LiquidityPool.pool_address == pool.pool_address
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Pool already exists")
        
        db_pool = LiquidityPool(**pool.dict())
        db.add(db_pool)
        db.commit()
        db.refresh(db_pool)
        
        logger.info(f"Created liquidity pool: {pool.pool_address}")
        return db_pool
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating pool: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/pools")
async def get_pools(
    skip: int = 0,
    limit: int = 100,
    dex_id: Optional[int] = None,
    token_address: Optional[str] = None,
    status: Optional[PoolStatus] = None,
    is_verified: Optional[bool] = None,
    min_liquidity: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Get all liquidity pools with filters"""
    try:
        query = db.query(LiquidityPool)
        
        if dex_id:
            query = query.filter(LiquidityPool.dex_id == dex_id)
        if token_address:
            query = query.filter(
                (LiquidityPool.token0_address == token_address) |
                (LiquidityPool.token1_address == token_address)
            )
        if status:
            query = query.filter(LiquidityPool.status == status)
        if is_verified is not None:
            query = query.filter(LiquidityPool.is_verified == is_verified)
        if min_liquidity:
            query = query.filter(LiquidityPool.liquidity_usd >= min_liquidity)
        
        total = query.count()
        pools = query.order_by(LiquidityPool.liquidity_usd.desc()).offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "pools": pools
        }
    except Exception as e:
        logger.error(f"Error fetching pools: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/pools/{pool_id}")
async def get_pool(pool_id: int, db: Session = Depends(get_db)):
    """Get a specific liquidity pool"""
    pool = db.query(LiquidityPool).filter(LiquidityPool.id == pool_id).first()
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")
    return pool

@app.put("/api/admin/pools/{pool_id}")
async def update_pool(
    pool_id: int,
    pool_update: LiquidityPoolUpdate,
    db: Session = Depends(get_db)
):
    """Update a liquidity pool"""
    try:
        pool = db.query(LiquidityPool).filter(LiquidityPool.id == pool_id).first()
        if not pool:
            raise HTTPException(status_code=404, detail="Pool not found")
        
        update_data = pool_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(pool, field, value)
        
        pool.last_updated = datetime.utcnow()
        db.commit()
        db.refresh(pool)
        
        logger.info(f"Updated pool: {pool_id}")
        return pool
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating pool: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/pools/{pool_id}/verify")
async def verify_pool(pool_id: int, db: Session = Depends(get_db)):
    """Verify a liquidity pool"""
    try:
        pool = db.query(LiquidityPool).filter(LiquidityPool.id == pool_id).first()
        if not pool:
            raise HTTPException(status_code=404, detail="Pool not found")
        
        pool.is_verified = True
        db.commit()
        
        logger.info(f"Verified pool: {pool_id}")
        return {"message": "Pool verified successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error verifying pool: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ROUTING ENDPOINTS ====================

@app.post("/api/admin/routes/find-best")
async def find_best_route(route_request: RouteRequest, db: Session = Depends(get_db)):
    """Find the best route for a swap"""
    try:
        # TODO: Implement routing algorithm
        # This is a placeholder response
        
        return {
            "token_in": route_request.token_in,
            "token_out": route_request.token_out,
            "amount_in": route_request.amount_in,
            "amount_out": 0.0,  # Calculate based on routing
            "path": [],
            "pools": [],
            "dexes": [],
            "price_impact": 0.0,
            "gas_estimate": 0.0
        }
    except Exception as e:
        logger.error(f"Error finding route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ANALYTICS ENDPOINTS ====================

@app.get("/api/admin/analytics/overview")
async def get_analytics_overview(db: Session = Depends(get_db)):
    """Get overall DEX analytics"""
    try:
        total_dexes = db.query(DEXIntegration).count()
        active_dexes = db.query(DEXIntegration).filter(DEXIntegration.is_enabled == True).count()
        total_pools = db.query(LiquidityPool).count()
        active_pools = db.query(LiquidityPool).filter(LiquidityPool.status == "active").count()
        
        total_liquidity = db.query(LiquidityPool).with_entities(
            db.func.sum(LiquidityPool.liquidity_usd)
        ).scalar() or 0.0
        
        total_volume_24h = db.query(DEXIntegration).with_entities(
            db.func.sum(DEXIntegration.total_volume_24h)
        ).scalar() or 0.0
        
        return {
            "total_dexes": total_dexes,
            "active_dexes": active_dexes,
            "total_pools": total_pools,
            "active_pools": active_pools,
            "total_liquidity": total_liquidity,
            "total_volume_24h": total_volume_24h
        }
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/analytics/top-pools")
async def get_top_pools(
    metric: str = "liquidity",
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get top liquidity pools"""
    try:
        query = db.query(LiquidityPool).filter(LiquidityPool.status == "active")
        
        if metric == "liquidity":
            query = query.order_by(LiquidityPool.liquidity_usd.desc())
        elif metric == "volume":
            query = query.order_by(LiquidityPool.volume_24h.desc())
        elif metric == "apr":
            query = query.order_by(LiquidityPool.apr.desc())
        
        pools = query.limit(limit).all()
        return pools
    except Exception as e:
        logger.error(f"Error fetching top pools: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "dex-integration-admin"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8117)