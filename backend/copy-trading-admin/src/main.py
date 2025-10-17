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
TigerEx Copy Trading Admin Panel
Manages copy trading traders, followers, and performance tracking
Port: 8116
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
DATABASE_URL = "postgresql://tigerex:tigerex123@localhost:5432/tigerex_copy_trading"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums
class TraderStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    UNDER_REVIEW = "under_review"

class TraderTier(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"

class CopyMode(str, Enum):
    FIXED_AMOUNT = "fixed_amount"
    FIXED_RATIO = "fixed_ratio"
    PROPORTIONAL = "proportional"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

# Database Models
class MasterTrader(Base):
    __tablename__ = "master_traders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    display_name = Column(String)
    bio = Column(Text)
    avatar_url = Column(String)
    status = Column(String, default="active")
    tier = Column(String, default="bronze")
    risk_level = Column(String)
    
    # Performance metrics
    total_followers = Column(Integer, default=0)
    total_aum = Column(Float, default=0.0)  # Assets Under Management
    roi_30d = Column(Float, default=0.0)
    roi_90d = Column(Float, default=0.0)
    roi_1y = Column(Float, default=0.0)
    roi_all_time = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    avg_trade_duration = Column(Integer, default=0)  # in hours
    total_trades = Column(Integer, default=0)
    profitable_trades = Column(Integer, default=0)
    
    # Trading stats
    total_profit = Column(Float, default=0.0)
    total_loss = Column(Float, default=0.0)
    avg_profit_per_trade = Column(Float, default=0.0)
    avg_loss_per_trade = Column(Float, default=0.0)
    largest_win = Column(Float, default=0.0)
    largest_loss = Column(Float, default=0.0)
    
    # Settings
    profit_sharing = Column(Float, default=10.0)  # percentage
    min_copy_amount = Column(Float, default=100.0)
    max_followers = Column(Integer, default=1000)
    allow_new_followers = Column(Boolean, default=True)
    
    # Verification
    is_verified = Column(Boolean, default=False)
    kyc_verified = Column(Boolean, default=False)
    
    # Timestamps
    joined_date = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    last_trade = Column(DateTime, nullable=True)
    
    metadata = Column(JSON)

class Follower(Base):
    __tablename__ = "followers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    trader_id = Column(Integer, index=True)
    
    # Copy settings
    copy_mode = Column(String, default="fixed_amount")
    copy_amount = Column(Float)  # for fixed_amount mode
    copy_ratio = Column(Float)  # for fixed_ratio mode (e.g., 0.1 = 10%)
    
    # Risk management
    stop_loss_percentage = Column(Float, nullable=True)
    take_profit_percentage = Column(Float, nullable=True)
    max_open_positions = Column(Integer, default=10)
    
    # Performance
    total_invested = Column(Float, default=0.0)
    current_value = Column(Float, default=0.0)
    total_profit_loss = Column(Float, default=0.0)
    roi = Column(Float, default=0.0)
    
    # Status
    is_active = Column(Boolean, default=True)
    auto_copy = Column(Boolean, default=True)
    
    # Timestamps
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    
    metadata = Column(JSON)

class CopyTrade(Base):
    __tablename__ = "copy_trades"
    
    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, index=True)
    follower_id = Column(Integer, index=True)
    master_trade_id = Column(Integer, index=True)
    
    # Trade details
    symbol = Column(String, index=True)
    side = Column(String)  # buy, sell
    order_type = Column(String)  # market, limit
    quantity = Column(Float)
    entry_price = Column(Float)
    exit_price = Column(Float, nullable=True)
    
    # P&L
    profit_loss = Column(Float, default=0.0)
    profit_loss_percentage = Column(Float, default=0.0)
    
    # Status
    status = Column(String, default="open")  # open, closed, cancelled
    
    # Timestamps
    opened_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    
    metadata = Column(JSON)

class TraderPerformance(Base):
    __tablename__ = "trader_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, index=True)
    date = Column(DateTime, index=True)
    
    # Daily metrics
    daily_return = Column(Float)
    cumulative_return = Column(Float)
    trades_count = Column(Integer)
    win_rate = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    
    # Portfolio
    portfolio_value = Column(Float)
    aum = Column(Float)
    followers_count = Column(Integer)
    
    metadata = Column(JSON)

class TraderRanking(Base):
    __tablename__ = "trader_rankings"
    
    id = Column(Integer, primary_key=True, index=True)
    trader_id = Column(Integer, unique=True, index=True)
    
    # Rankings
    overall_rank = Column(Integer)
    roi_rank = Column(Integer)
    followers_rank = Column(Integer)
    aum_rank = Column(Integer)
    win_rate_rank = Column(Integer)
    
    # Scores
    overall_score = Column(Float)
    consistency_score = Column(Float)
    risk_score = Column(Float)
    
    updated_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class MasterTraderCreate(BaseModel):
    user_id: int
    username: str
    display_name: str
    bio: str
    risk_level: RiskLevel
    profit_sharing: float = Field(ge=0, le=50, default=10.0)
    min_copy_amount: float = Field(gt=0, default=100.0)
    max_followers: int = Field(gt=0, default=1000)
    metadata: Optional[Dict[str, Any]] = None

class MasterTraderUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    status: Optional[TraderStatus] = None
    tier: Optional[TraderTier] = None
    risk_level: Optional[RiskLevel] = None
    profit_sharing: Optional[float] = None
    min_copy_amount: Optional[float] = None
    max_followers: Optional[int] = None
    allow_new_followers: Optional[bool] = None
    is_verified: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class FollowerCreate(BaseModel):
    user_id: int
    trader_id: int
    copy_mode: CopyMode
    copy_amount: Optional[float] = None
    copy_ratio: Optional[float] = None
    stop_loss_percentage: Optional[float] = None
    take_profit_percentage: Optional[float] = None
    max_open_positions: int = Field(gt=0, default=10)
    metadata: Optional[Dict[str, Any]] = None

class FollowerUpdate(BaseModel):
    copy_mode: Optional[CopyMode] = None
    copy_amount: Optional[float] = None
    copy_ratio: Optional[float] = None
    stop_loss_percentage: Optional[float] = None
    take_profit_percentage: Optional[float] = None
    max_open_positions: Optional[int] = None
    is_active: Optional[bool] = None
    auto_copy: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

# FastAPI app
app = FastAPI(
    title="TigerEx Copy Trading Admin API",
    description="Admin panel for managing copy trading traders and followers",
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

# ==================== MASTER TRADER ENDPOINTS ====================

@app.post("/api/admin/traders", status_code=201)
async def create_trader(trader: MasterTraderCreate, db: Session = Depends(get_db)):
    """Create a new master trader"""
    try:
        # Check if user is already a trader
        existing = db.query(MasterTrader).filter(MasterTrader.user_id == trader.user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="User is already a master trader")
        
        # Check if username is taken
        username_taken = db.query(MasterTrader).filter(MasterTrader.username == trader.username).first()
        if username_taken:
            raise HTTPException(status_code=400, detail="Username already taken")
        
        db_trader = MasterTrader(**trader.dict())
        db.add(db_trader)
        db.commit()
        db.refresh(db_trader)
        
        logger.info(f"Created master trader: {trader.username}")
        return db_trader
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating trader: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/traders")
async def get_traders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[TraderStatus] = None,
    tier: Optional[TraderTier] = None,
    risk_level: Optional[RiskLevel] = None,
    is_verified: Optional[bool] = None,
    min_followers: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all master traders with filters"""
    try:
        query = db.query(MasterTrader)
        
        if status:
            query = query.filter(MasterTrader.status == status)
        if tier:
            query = query.filter(MasterTrader.tier == tier)
        if risk_level:
            query = query.filter(MasterTrader.risk_level == risk_level)
        if is_verified is not None:
            query = query.filter(MasterTrader.is_verified == is_verified)
        if min_followers:
            query = query.filter(MasterTrader.total_followers >= min_followers)
        
        total = query.count()
        traders = query.order_by(MasterTrader.total_aum.desc()).offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "traders": traders
        }
    except Exception as e:
        logger.error(f"Error fetching traders: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/traders/{trader_id}")
async def get_trader(trader_id: int, db: Session = Depends(get_db)):
    """Get a specific master trader"""
    trader = db.query(MasterTrader).filter(MasterTrader.id == trader_id).first()
    if not trader:
        raise HTTPException(status_code=404, detail="Trader not found")
    return trader

@app.put("/api/admin/traders/{trader_id}")
async def update_trader(
    trader_id: int,
    trader_update: MasterTraderUpdate,
    db: Session = Depends(get_db)
):
    """Update a master trader"""
    try:
        trader = db.query(MasterTrader).filter(MasterTrader.id == trader_id).first()
        if not trader:
            raise HTTPException(status_code=404, detail="Trader not found")
        
        update_data = trader_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(trader, field, value)
        
        trader.last_active = datetime.utcnow()
        db.commit()
        db.refresh(trader)
        
        logger.info(f"Updated trader: {trader_id}")
        return trader
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating trader: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/traders/{trader_id}/verify")
async def verify_trader(trader_id: int, db: Session = Depends(get_db)):
    """Verify a master trader"""
    try:
        trader = db.query(MasterTrader).filter(MasterTrader.id == trader_id).first()
        if not trader:
            raise HTTPException(status_code=404, detail="Trader not found")
        
        trader.is_verified = True
        trader.kyc_verified = True
        db.commit()
        
        logger.info(f"Verified trader: {trader_id}")
        return {"message": "Trader verified successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error verifying trader: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/traders/{trader_id}/suspend")
async def suspend_trader(trader_id: int, reason: str, db: Session = Depends(get_db)):
    """Suspend a master trader"""
    try:
        trader = db.query(MasterTrader).filter(MasterTrader.id == trader_id).first()
        if not trader:
            raise HTTPException(status_code=404, detail="Trader not found")
        
        trader.status = "suspended"
        trader.allow_new_followers = False
        
        # Store suspension reason in metadata
        if not trader.metadata:
            trader.metadata = {}
        trader.metadata["suspension_reason"] = reason
        trader.metadata["suspended_at"] = datetime.utcnow().isoformat()
        
        db.commit()
        
        logger.info(f"Suspended trader: {trader_id}")
        return {"message": "Trader suspended successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error suspending trader: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== FOLLOWER ENDPOINTS ====================

@app.post("/api/admin/followers", status_code=201)
async def create_follower(follower: FollowerCreate, db: Session = Depends(get_db)):
    """Create a new follower relationship"""
    try:
        # Verify trader exists
        trader = db.query(MasterTrader).filter(MasterTrader.id == follower.trader_id).first()
        if not trader:
            raise HTTPException(status_code=404, detail="Trader not found")
        
        # Check if trader accepts new followers
        if not trader.allow_new_followers:
            raise HTTPException(status_code=400, detail="Trader not accepting new followers")
        
        # Check if max followers reached
        if trader.total_followers >= trader.max_followers:
            raise HTTPException(status_code=400, detail="Trader has reached maximum followers")
        
        # Check if user is already following this trader
        existing = db.query(Follower).filter(
            Follower.user_id == follower.user_id,
            Follower.trader_id == follower.trader_id,
            Follower.is_active == True
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="User is already following this trader")
        
        # Validate copy settings
        if follower.copy_mode == "fixed_amount" and not follower.copy_amount:
            raise HTTPException(status_code=400, detail="Copy amount required for fixed_amount mode")
        if follower.copy_mode == "fixed_ratio" and not follower.copy_ratio:
            raise HTTPException(status_code=400, detail="Copy ratio required for fixed_ratio mode")
        
        # Check minimum copy amount
        if follower.copy_amount and follower.copy_amount < trader.min_copy_amount:
            raise HTTPException(
                status_code=400,
                detail=f"Minimum copy amount is {trader.min_copy_amount}"
            )
        
        db_follower = Follower(**follower.dict())
        db.add(db_follower)
        
        # Update trader stats
        trader.total_followers += 1
        if follower.copy_amount:
            trader.total_aum += follower.copy_amount
        
        db.commit()
        db.refresh(db_follower)
        
        logger.info(f"Created follower relationship: user {follower.user_id} -> trader {follower.trader_id}")
        return db_follower
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating follower: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/followers")
async def get_followers(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    trader_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all followers with filters"""
    try:
        query = db.query(Follower)
        
        if user_id:
            query = query.filter(Follower.user_id == user_id)
        if trader_id:
            query = query.filter(Follower.trader_id == trader_id)
        if is_active is not None:
            query = query.filter(Follower.is_active == is_active)
        
        total = query.count()
        followers = query.offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "followers": followers
        }
    except Exception as e:
        logger.error(f"Error fetching followers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/admin/followers/{follower_id}")
async def update_follower(
    follower_id: int,
    follower_update: FollowerUpdate,
    db: Session = Depends(get_db)
):
    """Update a follower relationship"""
    try:
        follower = db.query(Follower).filter(Follower.id == follower_id).first()
        if not follower:
            raise HTTPException(status_code=404, detail="Follower not found")
        
        update_data = follower_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(follower, field, value)
        
        db.commit()
        db.refresh(follower)
        
        logger.info(f"Updated follower: {follower_id}")
        return follower
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating follower: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/admin/followers/{follower_id}")
async def delete_follower(follower_id: int, db: Session = Depends(get_db)):
    """Stop following a trader"""
    try:
        follower = db.query(Follower).filter(Follower.id == follower_id).first()
        if not follower:
            raise HTTPException(status_code=404, detail="Follower not found")
        
        follower.is_active = False
        follower.end_date = datetime.utcnow()
        
        # Update trader stats
        trader = db.query(MasterTrader).filter(MasterTrader.id == follower.trader_id).first()
        if trader:
            trader.total_followers -= 1
            if follower.copy_amount:
                trader.total_aum -= follower.copy_amount
        
        db.commit()
        
        logger.info(f"Stopped following: {follower_id}")
        return {"message": "Stopped following trader successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting follower: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== COPY TRADE ENDPOINTS ====================

@app.get("/api/admin/copy-trades")
async def get_copy_trades(
    skip: int = 0,
    limit: int = 100,
    trader_id: Optional[int] = None,
    follower_id: Optional[int] = None,
    symbol: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all copy trades with filters"""
    try:
        query = db.query(CopyTrade)
        
        if trader_id:
            query = query.filter(CopyTrade.trader_id == trader_id)
        if follower_id:
            query = query.filter(CopyTrade.follower_id == follower_id)
        if symbol:
            query = query.filter(CopyTrade.symbol == symbol)
        if status:
            query = query.filter(CopyTrade.status == status)
        
        total = query.count()
        trades = query.order_by(CopyTrade.opened_at.desc()).offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "trades": trades
        }
    except Exception as e:
        logger.error(f"Error fetching copy trades: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ANALYTICS ENDPOINTS ====================

@app.get("/api/admin/analytics/overview")
async def get_analytics_overview(db: Session = Depends(get_db)):
    """Get overall copy trading analytics"""
    try:
        total_traders = db.query(MasterTrader).count()
        active_traders = db.query(MasterTrader).filter(MasterTrader.status == "active").count()
        verified_traders = db.query(MasterTrader).filter(MasterTrader.is_verified == True).count()
        total_followers = db.query(Follower).filter(Follower.is_active == True).count()
        total_aum = db.query(MasterTrader).with_entities(
            db.func.sum(MasterTrader.total_aum)
        ).scalar() or 0.0
        
        # Recent trades
        recent_trades = db.query(CopyTrade).filter(
            CopyTrade.opened_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        return {
            "total_traders": total_traders,
            "active_traders": active_traders,
            "verified_traders": verified_traders,
            "total_followers": total_followers,
            "total_aum": total_aum,
            "recent_trades_7d": recent_trades
        }
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/analytics/leaderboard")
async def get_leaderboard(
    metric: str = "roi",
    period: str = "30d",
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get trader leaderboard"""
    try:
        query = db.query(MasterTrader).filter(MasterTrader.status == "active")
        
        # Sort by metric
        if metric == "roi":
            if period == "30d":
                query = query.order_by(MasterTrader.roi_30d.desc())
            elif period == "90d":
                query = query.order_by(MasterTrader.roi_90d.desc())
            elif period == "1y":
                query = query.order_by(MasterTrader.roi_1y.desc())
            else:
                query = query.order_by(MasterTrader.roi_all_time.desc())
        elif metric == "followers":
            query = query.order_by(MasterTrader.total_followers.desc())
        elif metric == "aum":
            query = query.order_by(MasterTrader.total_aum.desc())
        elif metric == "win_rate":
            query = query.order_by(MasterTrader.win_rate.desc())
        
        traders = query.limit(limit).all()
        
        return traders
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/analytics/trader-performance/{trader_id}")
async def get_trader_performance(
    trader_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get trader performance history"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        performance = db.query(TraderPerformance).filter(
            TraderPerformance.trader_id == trader_id,
            TraderPerformance.date >= start_date
        ).order_by(TraderPerformance.date).all()
        
        return performance
    except Exception as e:
        logger.error(f"Error fetching trader performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "copy-trading-admin"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8116)