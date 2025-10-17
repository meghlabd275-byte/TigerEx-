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
TigerEx Lending & Borrowing Admin Panel
Manages lending pools, borrowing positions, and interest rates
Port: 8121
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uvicorn
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://tigerex:tigerex123@localhost:5432/tigerex_lending_borrowing"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PoolStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"

class LendingPool(Base):
    __tablename__ = "lending_pools"
    
    id = Column(Integer, primary_key=True, index=True)
    asset = Column(String, unique=True, index=True)
    total_supplied = Column(Float, default=0.0)
    total_borrowed = Column(Float, default=0.0)
    available_liquidity = Column(Float, default=0.0)
    utilization_rate = Column(Float, default=0.0)
    supply_apy = Column(Float, default=0.0)
    borrow_apy = Column(Float, default=0.0)
    ltv_ratio = Column(Float, default=0.75)
    liquidation_threshold = Column(Float, default=0.85)
    liquidation_penalty = Column(Float, default=0.05)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)

class LendingPosition(Base):
    __tablename__ = "lending_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    pool_id = Column(Integer, index=True)
    amount = Column(Float)
    apy = Column(Float)
    accrued_interest = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)

class BorrowingPosition(Base):
    __tablename__ = "borrowing_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    pool_id = Column(Integer, index=True)
    borrowed_amount = Column(Float)
    collateral_amount = Column(Float)
    collateral_asset = Column(String)
    apy = Column(Float)
    accrued_interest = Column(Float, default=0.0)
    health_factor = Column(Float, default=1.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    liquidated_at = Column(DateTime, nullable=True)
    metadata = Column(JSON)

Base.metadata.create_all(bind=engine)

class LendingPoolCreate(BaseModel):
    asset: str
    supply_apy: float = Field(ge=0, le=100, default=5.0)
    borrow_apy: float = Field(ge=0, le=100, default=8.0)
    ltv_ratio: float = Field(ge=0, le=1, default=0.75)
    liquidation_threshold: float = Field(ge=0, le=1, default=0.85)
    liquidation_penalty: float = Field(ge=0, le=1, default=0.05)
    metadata: Optional[Dict[str, Any]] = None

class LendingPoolUpdate(BaseModel):
    supply_apy: Optional[float] = None
    borrow_apy: Optional[float] = None
    ltv_ratio: Optional[float] = None
    liquidation_threshold: Optional[float] = None
    liquidation_penalty: Optional[float] = None
    status: Optional[PoolStatus] = None
    metadata: Optional[Dict[str, Any]] = None

app = FastAPI(title="TigerEx Lending & Borrowing Admin API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/admin/pools", status_code=201)
async def create_pool(pool: LendingPoolCreate, db: Session = Depends(get_db)):
    """Create a new lending pool"""
    try:
        existing = db.query(LendingPool).filter(LendingPool.asset == pool.asset).first()
        if existing:
            raise HTTPException(status_code=400, detail="Pool already exists")
        
        db_pool = LendingPool(**pool.dict())
        db.add(db_pool)
        db.commit()
        db.refresh(db_pool)
        
        logger.info(f"Created lending pool: {pool.asset}")
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
    status: Optional[PoolStatus] = None,
    db: Session = Depends(get_db)
):
    """Get all lending pools"""
    try:
        query = db.query(LendingPool)
        
        if status:
            query = query.filter(LendingPool.status == status)
        
        total = query.count()
        pools = query.order_by(LendingPool.total_supplied.desc()).offset(skip).limit(limit).all()
        
        return {"total": total, "pools": pools}
    except Exception as e:
        logger.error(f"Error fetching pools: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/admin/pools/{pool_id}")
async def update_pool(
    pool_id: int,
    pool_update: LendingPoolUpdate,
    db: Session = Depends(get_db)
):
    """Update a lending pool"""
    try:
        pool = db.query(LendingPool).filter(LendingPool.id == pool_id).first()
        if not pool:
            raise HTTPException(status_code=404, detail="Pool not found")
        
        update_data = pool_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(pool, field, value)
        
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

@app.get("/api/admin/analytics/overview")
async def get_analytics_overview(db: Session = Depends(get_db)):
    """Get lending & borrowing analytics"""
    try:
        total_pools = db.query(LendingPool).count()
        active_pools = db.query(LendingPool).filter(LendingPool.status == "active").count()
        total_supplied = db.query(LendingPool).with_entities(
            db.func.sum(LendingPool.total_supplied)
        ).scalar() or 0.0
        total_borrowed = db.query(LendingPool).with_entities(
            db.func.sum(LendingPool.total_borrowed)
        ).scalar() or 0.0
        avg_utilization = db.query(LendingPool).filter(
            LendingPool.status == "active"
        ).with_entities(db.func.avg(LendingPool.utilization_rate)).scalar() or 0.0
        
        return {
            "total_pools": total_pools,
            "active_pools": active_pools,
            "total_supplied": total_supplied,
            "total_borrowed": total_borrowed,
            "avg_utilization": avg_utilization
        }
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "lending-borrowing-admin"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8121)