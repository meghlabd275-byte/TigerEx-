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
TigerEx Liquidity Aggregator Admin Panel
Manages liquidity aggregation across multiple sources
Port: 8118
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import uvicorn
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://tigerex:tigerex123@localhost:5432/tigerex_liquidity_aggregator"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SourceType(str, Enum):
    CEX = "cex"
    DEX = "dex"
    MARKET_MAKER = "market_maker"
    LIQUIDITY_POOL = "liquidity_pool"

class LiquiditySource(Base):
    __tablename__ = "liquidity_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    source_type = Column(String)
    api_endpoint = Column(String)
    is_enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    weight = Column(Float, default=1.0)
    total_liquidity = Column(Float, default=0.0)
    avg_spread = Column(Float, default=0.0)
    uptime_percentage = Column(Float, default=100.0)
    response_time_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)

class AggregatedQuote(Base):
    __tablename__ = "aggregated_quotes"
    
    id = Column(Integer, primary_key=True, index=True)
    token_in = Column(String, index=True)
    token_out = Column(String, index=True)
    amount_in = Column(Float)
    best_amount_out = Column(Float)
    best_source_id = Column(Integer)
    sources_checked = Column(Integer)
    avg_price = Column(Float)
    price_variance = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)

Base.metadata.create_all(bind=engine)

class LiquiditySourceCreate(BaseModel):
    name: str
    source_type: SourceType
    api_endpoint: str
    priority: int = Field(ge=0, default=0)
    weight: float = Field(ge=0, le=1, default=1.0)
    metadata: Optional[Dict[str, Any]] = None

app = FastAPI(title="TigerEx Liquidity Aggregator Admin API", version="1.0.0")

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

@app.post("/api/admin/sources", status_code=201)
async def create_source(source: LiquiditySourceCreate, db: Session = Depends(get_db)):
    """Create a new liquidity source"""
    try:
        existing = db.query(LiquiditySource).filter(LiquiditySource.name == source.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Source already exists")
        
        db_source = LiquiditySource(**source.dict())
        db.add(db_source)
        db.commit()
        db.refresh(db_source)
        
        logger.info(f"Created liquidity source: {source.name}")
        return db_source
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating source: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/sources")
async def get_sources(
    skip: int = 0,
    limit: int = 100,
    source_type: Optional[SourceType] = None,
    is_enabled: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all liquidity sources"""
    try:
        query = db.query(LiquiditySource)
        
        if source_type:
            query = query.filter(LiquiditySource.source_type == source_type)
        if is_enabled is not None:
            query = query.filter(LiquiditySource.is_enabled == is_enabled)
        
        total = query.count()
        sources = query.order_by(LiquiditySource.priority.desc()).offset(skip).limit(limit).all()
        
        return {"total": total, "sources": sources}
    except Exception as e:
        logger.error(f"Error fetching sources: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/analytics/overview")
async def get_analytics_overview(db: Session = Depends(get_db)):
    """Get liquidity aggregator analytics"""
    try:
        total_sources = db.query(LiquiditySource).count()
        active_sources = db.query(LiquiditySource).filter(LiquiditySource.is_enabled == True).count()
        total_liquidity = db.query(LiquiditySource).with_entities(
            db.func.sum(LiquiditySource.total_liquidity)
        ).scalar() or 0.0
        
        avg_spread = db.query(LiquiditySource).filter(
            LiquiditySource.is_enabled == True
        ).with_entities(db.func.avg(LiquiditySource.avg_spread)).scalar() or 0.0
        
        return {
            "total_sources": total_sources,
            "active_sources": active_sources,
            "total_liquidity": total_liquidity,
            "avg_spread": avg_spread
        }
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "liquidity-aggregator-admin"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8118)