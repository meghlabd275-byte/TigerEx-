"""
TigerEx ETF Trading Admin Panel Service
Comprehensive admin panel for managing ETF products, rebalancing, and monitoring
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
from enum import Enum

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from sqlalchemy import create_engine, Column, String, DECIMAL, DateTime, Boolean, Integer, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TigerEx ETF Trading Admin Panel",
    description="Admin panel for ETF product management and monitoring",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = "postgresql://postgres:password@localhost/tigerex_etf_admin"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Enums
class ETFStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELISTED = "delisted"
    PENDING = "pending"

class RebalanceStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

# Database Models
class ETFProductDB(Base):
    __tablename__ = "etf_products"
    
    id = Column(String, primary_key=True)
    symbol = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    leverage = Column(DECIMAL(10, 2), default=1.0)
    management_fee = Column(DECIMAL(10, 4), default=0.0)
    creation_fee = Column(DECIMAL(10, 4), default=0.0)
    redemption_fee = Column(DECIMAL(10, 4), default=0.0)
    min_creation_amount = Column(DECIMAL(20, 8), default=0.0)
    min_redemption_amount = Column(DECIMAL(20, 8), default=0.0)
    total_supply = Column(DECIMAL(30, 8), default=0.0)
    nav = Column(DECIMAL(20, 8), default=0.0)  # Net Asset Value
    status = Column(String, default="active")
    underlying_assets = Column(JSON)  # List of assets and weights
    rebalance_frequency = Column(String, default="daily")  # daily, weekly, monthly
    last_rebalance = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RebalanceHistoryDB(Base):
    __tablename__ = "rebalance_history"
    
    id = Column(String, primary_key=True)
    etf_id = Column(String, nullable=False)
    rebalance_date = Column(DateTime, default=datetime.utcnow)
    old_composition = Column(JSON)
    new_composition = Column(JSON)
    trades_executed = Column(JSON)
    status = Column(String, default="scheduled")
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class ETFSubscriptionDB(Base):
    __tablename__ = "etf_subscriptions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    etf_id = Column(String, nullable=False)
    subscription_type = Column(String, nullable=False)  # creation, redemption
    amount = Column(DECIMAL(20, 8), nullable=False)
    nav_price = Column(DECIMAL(20, 8), nullable=False)
    fee = Column(DECIMAL(20, 8), default=0.0)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

class ETFPerformanceDB(Base):
    __tablename__ = "etf_performance"
    
    id = Column(String, primary_key=True)
    etf_id = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    nav = Column(DECIMAL(20, 8), nullable=False)
    total_supply = Column(DECIMAL(30, 8), nullable=False)
    daily_return = Column(DECIMAL(10, 4))
    volume_24h = Column(DECIMAL(30, 8), default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models
class ETFProductCreate(BaseModel):
    symbol: str
    name: str
    description: Optional[str]
    leverage: Decimal = Decimal("1.0")
    management_fee: Decimal = Decimal("0.0")
    creation_fee: Decimal = Decimal("0.0")
    redemption_fee: Decimal = Decimal("0.0")
    min_creation_amount: Decimal = Decimal("0.0")
    min_redemption_amount: Decimal = Decimal("0.0")
    underlying_assets: List[Dict]
    rebalance_frequency: str = "daily"

class ETFProductUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    management_fee: Optional[Decimal]
    creation_fee: Optional[Decimal]
    redemption_fee: Optional[Decimal]
    status: Optional[ETFStatus]
    rebalance_frequency: Optional[str]

class ETFProductResponse(BaseModel):
    id: str
    symbol: str
    name: str
    description: Optional[str]
    leverage: Decimal
    management_fee: Decimal
    creation_fee: Decimal
    redemption_fee: Decimal
    total_supply: Decimal
    nav: Decimal
    status: str
    underlying_assets: List[Dict]
    rebalance_frequency: str
    last_rebalance: Optional[datetime]
    created_at: datetime

class RebalanceRequest(BaseModel):
    etf_id: str
    new_composition: List[Dict]
    reason: Optional[str]

class ETFStatistics(BaseModel):
    total_etfs: int
    active_etfs: int
    total_aum: Decimal  # Assets Under Management
    total_volume_24h: Decimal
    pending_rebalances: int
    pending_subscriptions: int

# API Endpoints

@app.post("/admin/etf/products", response_model=ETFProductResponse)
async def create_etf_product(product: ETFProductCreate, db: Session = Depends(get_db)):
    """Create a new ETF product"""
    import uuid
    
    # Check if symbol already exists
    existing = db.query(ETFProductDB).filter(ETFProductDB.symbol == product.symbol).first()
    if existing:
        raise HTTPException(status_code=400, detail="ETF symbol already exists")
    
    # Validate underlying assets weights sum to 100%
    total_weight = sum(asset.get('weight', 0) for asset in product.underlying_assets)
    if abs(total_weight - 100.0) > 0.01:
        raise HTTPException(status_code=400, detail="Asset weights must sum to 100%")
    
    etf_id = str(uuid.uuid4())
    db_etf = ETFProductDB(
        id=etf_id,
        symbol=product.symbol,
        name=product.name,
        description=product.description,
        leverage=product.leverage,
        management_fee=product.management_fee,
        creation_fee=product.creation_fee,
        redemption_fee=product.redemption_fee,
        min_creation_amount=product.min_creation_amount,
        min_redemption_amount=product.min_redemption_amount,
        underlying_assets=product.underlying_assets,
        rebalance_frequency=product.rebalance_frequency,
        status="pending",
        created_at=datetime.utcnow()
    )
    
    db.add(db_etf)
    db.commit()
    db.refresh(db_etf)
    
    logger.info(f"Created ETF product: {product.symbol}")
    
    return ETFProductResponse(
        id=db_etf.id,
        symbol=db_etf.symbol,
        name=db_etf.name,
        description=db_etf.description,
        leverage=db_etf.leverage,
        management_fee=db_etf.management_fee,
        creation_fee=db_etf.creation_fee,
        redemption_fee=db_etf.redemption_fee,
        total_supply=db_etf.total_supply,
        nav=db_etf.nav,
        status=db_etf.status,
        underlying_assets=db_etf.underlying_assets,
        rebalance_frequency=db_etf.rebalance_frequency,
        last_rebalance=db_etf.last_rebalance,
        created_at=db_etf.created_at
    )

@app.get("/admin/etf/products", response_model=List[ETFProductResponse])
async def list_etf_products(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all ETF products"""
    query = db.query(ETFProductDB)
    
    if status:
        query = query.filter(ETFProductDB.status == status)
    
    etfs = query.offset(skip).limit(limit).all()
    
    return [ETFProductResponse(
        id=etf.id,
        symbol=etf.symbol,
        name=etf.name,
        description=etf.description,
        leverage=etf.leverage,
        management_fee=etf.management_fee,
        creation_fee=etf.creation_fee,
        redemption_fee=etf.redemption_fee,
        total_supply=etf.total_supply,
        nav=etf.nav,
        status=etf.status,
        underlying_assets=etf.underlying_assets,
        rebalance_frequency=etf.rebalance_frequency,
        last_rebalance=etf.last_rebalance,
        created_at=etf.created_at
    ) for etf in etfs]

@app.get("/admin/etf/products/{etf_id}", response_model=ETFProductResponse)
async def get_etf_product(etf_id: str, db: Session = Depends(get_db)):
    """Get ETF product details"""
    etf = db.query(ETFProductDB).filter(ETFProductDB.id == etf_id).first()
    if not etf:
        raise HTTPException(status_code=404, detail="ETF not found")
    
    return ETFProductResponse(
        id=etf.id,
        symbol=etf.symbol,
        name=etf.name,
        description=etf.description,
        leverage=etf.leverage,
        management_fee=etf.management_fee,
        creation_fee=etf.creation_fee,
        redemption_fee=etf.redemption_fee,
        total_supply=etf.total_supply,
        nav=etf.nav,
        status=etf.status,
        underlying_assets=etf.underlying_assets,
        rebalance_frequency=etf.rebalance_frequency,
        last_rebalance=etf.last_rebalance,
        created_at=etf.created_at
    )

@app.put("/admin/etf/products/{etf_id}", response_model=ETFProductResponse)
async def update_etf_product(
    etf_id: str,
    update: ETFProductUpdate,
    db: Session = Depends(get_db)
):
    """Update ETF product"""
    etf = db.query(ETFProductDB).filter(ETFProductDB.id == etf_id).first()
    if not etf:
        raise HTTPException(status_code=404, detail="ETF not found")
    
    if update.name:
        etf.name = update.name
    if update.description:
        etf.description = update.description
    if update.management_fee:
        etf.management_fee = update.management_fee
    if update.creation_fee:
        etf.creation_fee = update.creation_fee
    if update.redemption_fee:
        etf.redemption_fee = update.redemption_fee
    if update.status:
        etf.status = update.status
    if update.rebalance_frequency:
        etf.rebalance_frequency = update.rebalance_frequency
    
    etf.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(etf)
    
    logger.info(f"Updated ETF product: {etf.symbol}")
    
    return ETFProductResponse(
        id=etf.id,
        symbol=etf.symbol,
        name=etf.name,
        description=etf.description,
        leverage=etf.leverage,
        management_fee=etf.management_fee,
        creation_fee=etf.creation_fee,
        redemption_fee=etf.redemption_fee,
        total_supply=etf.total_supply,
        nav=etf.nav,
        status=etf.status,
        underlying_assets=etf.underlying_assets,
        rebalance_frequency=etf.rebalance_frequency,
        last_rebalance=etf.last_rebalance,
        created_at=etf.created_at
    )

@app.post("/admin/etf/rebalance")
async def trigger_rebalance(
    request: RebalanceRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Trigger ETF rebalancing"""
    import uuid
    
    etf = db.query(ETFProductDB).filter(ETFProductDB.id == request.etf_id).first()
    if not etf:
        raise HTTPException(status_code=404, detail="ETF not found")
    
    # Create rebalance record
    rebalance_id = str(uuid.uuid4())
    rebalance = RebalanceHistoryDB(
        id=rebalance_id,
        etf_id=request.etf_id,
        old_composition=etf.underlying_assets,
        new_composition=request.new_composition,
        status="scheduled",
        created_at=datetime.utcnow()
    )
    
    db.add(rebalance)
    db.commit()
    
    # Schedule rebalancing in background
    background_tasks.add_task(execute_rebalance, rebalance_id, request.etf_id, request.new_composition)
    
    logger.info(f"Scheduled rebalance for ETF: {etf.symbol}")
    
    return {
        "message": "Rebalance scheduled",
        "rebalance_id": rebalance_id,
        "etf_id": request.etf_id
    }

async def execute_rebalance(rebalance_id: str, etf_id: str, new_composition: List[Dict]):
    """Execute ETF rebalancing (background task)"""
    db = SessionLocal()
    try:
        rebalance = db.query(RebalanceHistoryDB).filter(RebalanceHistoryDB.id == rebalance_id).first()
        etf = db.query(ETFProductDB).filter(ETFProductDB.id == etf_id).first()
        
        if not rebalance or not etf:
            return
        
        rebalance.status = "in_progress"
        db.commit()
        
        # Simulate rebalancing logic
        # In production, this would execute actual trades
        await asyncio.sleep(5)
        
        # Update ETF composition
        etf.underlying_assets = new_composition
        etf.last_rebalance = datetime.utcnow()
        
        rebalance.status = "completed"
        rebalance.trades_executed = [{"asset": "BTC", "amount": 1.0, "price": 45000}]  # Example
        
        db.commit()
        
        logger.info(f"Completed rebalance for ETF: {etf.symbol}")
        
    except Exception as e:
        logger.error(f"Rebalance failed: {str(e)}")
        rebalance.status = "failed"
        rebalance.error_message = str(e)
        db.commit()
    finally:
        db.close()

@app.get("/admin/etf/statistics", response_model=ETFStatistics)
async def get_etf_statistics(db: Session = Depends(get_db)):
    """Get ETF platform statistics"""
    total_etfs = db.query(ETFProductDB).count()
    active_etfs = db.query(ETFProductDB).filter(ETFProductDB.status == "active").count()
    
    # Calculate total AUM
    etfs = db.query(ETFProductDB).filter(ETFProductDB.status == "active").all()
    total_aum = sum(etf.total_supply * etf.nav for etf in etfs)
    
    # Calculate 24h volume
    yesterday = datetime.utcnow() - timedelta(days=1)
    performance_records = db.query(ETFPerformanceDB).filter(
        ETFPerformanceDB.date >= yesterday
    ).all()
    total_volume_24h = sum(record.volume_24h for record in performance_records)
    
    # Count pending items
    pending_rebalances = db.query(RebalanceHistoryDB).filter(
        RebalanceHistoryDB.status.in_(["scheduled", "in_progress"])
    ).count()
    
    pending_subscriptions = db.query(ETFSubscriptionDB).filter(
        ETFSubscriptionDB.status == "pending"
    ).count()
    
    return ETFStatistics(
        total_etfs=total_etfs,
        active_etfs=active_etfs,
        total_aum=Decimal(str(total_aum)),
        total_volume_24h=Decimal(str(total_volume_24h)),
        pending_rebalances=pending_rebalances,
        pending_subscriptions=pending_subscriptions
    )

@app.get("/admin/etf/subscriptions")
async def list_subscriptions(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List ETF subscriptions"""
    query = db.query(ETFSubscriptionDB)
    
    if status:
        query = query.filter(ETFSubscriptionDB.status == status)
    
    subscriptions = query.order_by(ETFSubscriptionDB.created_at.desc()).offset(skip).limit(limit).all()
    
    return [{
        "id": sub.id,
        "user_id": sub.user_id,
        "etf_id": sub.etf_id,
        "subscription_type": sub.subscription_type,
        "amount": float(sub.amount),
        "nav_price": float(sub.nav_price),
        "fee": float(sub.fee),
        "status": sub.status,
        "created_at": sub.created_at.isoformat(),
        "completed_at": sub.completed_at.isoformat() if sub.completed_at else None
    } for sub in subscriptions]

@app.get("/admin/etf/performance/{etf_id}")
async def get_etf_performance(
    etf_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get ETF performance history"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    performance = db.query(ETFPerformanceDB).filter(
        ETFPerformanceDB.etf_id == etf_id,
        ETFPerformanceDB.date >= start_date
    ).order_by(ETFPerformanceDB.date).all()
    
    return [{
        "date": perf.date.isoformat(),
        "nav": float(perf.nav),
        "total_supply": float(perf.total_supply),
        "daily_return": float(perf.daily_return) if perf.daily_return else None,
        "volume_24h": float(perf.volume_24h)
    } for perf in performance]

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "etf-trading-admin"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8113)