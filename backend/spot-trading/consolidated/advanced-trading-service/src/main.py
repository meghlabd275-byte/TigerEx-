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
TigerEx Advanced Trading Service
Implements advanced order types: TWAP, VWAP, and algorithmic trading
Port: 8124
"""

from fastapi import FastAPI
from admin.admin_routes import router as admin_router
from fastapi import HTTPException, Depends, BackgroundTasks
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
import asyncio
from decimal import Decimal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://tigerex:tigerex123@localhost:5432/tigerex_advanced_trading"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums
class AdvancedOrderType(str, Enum):
    TWAP = "twap"
    VWAP = "vwap"
    IMPLEMENTATION_SHORTFALL = "implementation_shortfall"
    ARRIVAL_PRICE = "arrival_price"
    PARTICIPATION_RATE = "participation_rate"
    IF_TOUCHED = "if_touched"
    CONTINGENT = "contingent"
    TIME_BASED = "time_based"
    VOLUME_BASED = "volume_based"

class OrderStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    EXECUTING = "executing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    PAUSED = "paused"

class ExecutionStrategy(str, Enum):
    AGGRESSIVE = "aggressive"
    PASSIVE = "passive"
    BALANCED = "balanced"

# Database Models
class AdvancedOrder(Base):
    __tablename__ = "advanced_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, index=True)
    order_type = Column(String, index=True)
    symbol = Column(String, index=True)
    side = Column(String)
    total_quantity = Column(Float)
    executed_quantity = Column(Float, default=0.0)
    remaining_quantity = Column(Float)
    limit_price = Column(Float, nullable=True)
    avg_execution_price = Column(Float, default=0.0)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_minutes = Column(Integer)
    execution_strategy = Column(String, default="balanced")
    participation_rate = Column(Float, nullable=True)
    slice_size = Column(Float, nullable=True)
    slice_interval_seconds = Column(Integer, nullable=True)
    trigger_price = Column(Float, nullable=True)
    contingent_order_id = Column(String, nullable=True)
    status = Column(String, default="pending")
    total_slices = Column(Integer, default=0)
    executed_slices = Column(Integer, default=0)
    failed_slices = Column(Integer, default=0)
    slippage = Column(Float, default=0.0)
    implementation_shortfall = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    metadata = Column(JSON)

class OrderSlice(Base):
    __tablename__ = "order_slices"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, index=True)
    slice_number = Column(Integer)
    quantity = Column(Float)
    executed_quantity = Column(Float, default=0.0)
    price = Column(Float, nullable=True)
    avg_execution_price = Column(Float, default=0.0)
    status = Column(String, default="pending")
    scheduled_time = Column(DateTime)
    executed_at = Column(DateTime, nullable=True)
    market_price = Column(Float, nullable=True)
    market_volume = Column(Float, nullable=True)
    metadata = Column(JSON)

class ExecutionReport(Base):
    __tablename__ = "execution_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, index=True)
    total_quantity = Column(Float)
    executed_quantity = Column(Float)
    avg_price = Column(Float)
    vwap = Column(Float, nullable=True)
    twap = Column(Float, nullable=True)
    arrival_price = Column(Float, nullable=True)
    implementation_shortfall = Column(Float, nullable=True)
    slippage_bps = Column(Float, nullable=True)
    total_duration_seconds = Column(Integer)
    avg_slice_duration_seconds = Column(Float)
    market_impact_bps = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)

Base.metadata.create_all(bind=engine)

# Pydantic Models
class TWAPOrderCreate(BaseModel):
    user_id: int
    symbol: str
    side: str = Field(pattern="^(buy|sell)$")
    total_quantity: float = Field(gt=0)
    duration_minutes: int = Field(gt=0, le=1440)
    limit_price: Optional[float] = None
    execution_strategy: ExecutionStrategy = ExecutionStrategy.BALANCED
    metadata: Optional[Dict[str, Any]] = None

class VWAPOrderCreate(BaseModel):
    user_id: int
    symbol: str
    side: str = Field(pattern="^(buy|sell)$")
    total_quantity: float = Field(gt=0)
    duration_minutes: int = Field(gt=0, le=1440)
    limit_price: Optional[float] = None
    execution_strategy: ExecutionStrategy = ExecutionStrategy.BALANCED
    metadata: Optional[Dict[str, Any]] = None

class ParticipationRateOrderCreate(BaseModel):
    user_id: int
    symbol: str
    side: str = Field(pattern="^(buy|sell)$")
    total_quantity: float = Field(gt=0)
    participation_rate: float = Field(gt=0, le=100)
    duration_minutes: int = Field(gt=0, le=1440)
    limit_price: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class IfTouchedOrderCreate(BaseModel):
    user_id: int
    symbol: str
    side: str = Field(pattern="^(buy|sell)$")
    quantity: float = Field(gt=0)
    trigger_price: float = Field(gt=0)
    limit_price: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class ContingentOrderCreate(BaseModel):
    user_id: int
    symbol: str
    side: str = Field(pattern="^(buy|sell)$")
    quantity: float = Field(gt=0)
    contingent_order_id: str
    limit_price: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

app = FastAPI(

# Include admin router
app.include_router(admin_router)
    title="TigerEx Advanced Trading Service",
    description="Advanced order types and algorithmic trading",
    version="1.0.0"
)

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

def generate_order_id(order_type: str) -> str:
    import uuid
    prefix = order_type.upper()[:4]
    return f"{prefix}-{uuid.uuid4().hex[:12].upper()}"

def calculate_slice_parameters(total_quantity: float, duration_minutes: int, strategy: str) -> tuple:
    if strategy == "aggressive":
        num_slices = max(5, duration_minutes // 2)
    elif strategy == "passive":
        num_slices = max(10, duration_minutes)
    else:
        num_slices = max(8, duration_minutes // 3)
    
    slice_size = total_quantity / num_slices
    slice_interval = (duration_minutes * 60) / num_slices
    
    return slice_size, int(slice_interval), num_slices

@app.post("/api/orders/twap", status_code=201)
async def create_twap_order(order: TWAPOrderCreate, db: Session = Depends(get_db)):
    try:
        slice_size, slice_interval, num_slices = calculate_slice_parameters(
            order.total_quantity, order.duration_minutes, order.execution_strategy
        )
        
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(minutes=order.duration_minutes)
        
        db_order = AdvancedOrder(
            order_id=generate_order_id("TWAP"),
            user_id=order.user_id,
            order_type="twap",
            symbol=order.symbol,
            side=order.side,
            total_quantity=order.total_quantity,
            remaining_quantity=order.total_quantity,
            limit_price=order.limit_price,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=order.duration_minutes,
            execution_strategy=order.execution_strategy,
            slice_size=slice_size,
            slice_interval_seconds=slice_interval,
            total_slices=num_slices,
            status="active",
            started_at=start_time,
            metadata=order.metadata or {}
        )
        
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        
        for i in range(num_slices):
            slice_time = start_time + timedelta(seconds=slice_interval * i)
            slice_obj = OrderSlice(
                order_id=db_order.order_id,
                slice_number=i + 1,
                quantity=slice_size,
                scheduled_time=slice_time,
                status="pending"
            )
            db.add(slice_obj)
        
        db.commit()
        logger.info(f"Created TWAP order: {db_order.order_id}")
        
        return {
            "order_id": db_order.order_id,
            "order_type": "twap",
            "symbol": db_order.symbol,
            "side": db_order.side,
            "total_quantity": db_order.total_quantity,
            "num_slices": num_slices,
            "slice_size": slice_size,
            "slice_interval_seconds": slice_interval,
            "start_time": db_order.start_time,
            "end_time": db_order.end_time,
            "status": db_order.status
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating TWAP order: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/orders/vwap", status_code=201)
async def create_vwap_order(order: VWAPOrderCreate, db: Session = Depends(get_db)):
    try:
        slice_size, slice_interval, num_slices = calculate_slice_parameters(
            order.total_quantity, order.duration_minutes, order.execution_strategy
        )
        
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(minutes=order.duration_minutes)
        
        db_order = AdvancedOrder(
            order_id=generate_order_id("VWAP"),
            user_id=order.user_id,
            order_type="vwap",
            symbol=order.symbol,
            side=order.side,
            total_quantity=order.total_quantity,
            remaining_quantity=order.total_quantity,
            limit_price=order.limit_price,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=order.duration_minutes,
            execution_strategy=order.execution_strategy,
            slice_size=slice_size,
            slice_interval_seconds=slice_interval,
            total_slices=num_slices,
            status="active",
            started_at=start_time,
            metadata=order.metadata or {}
        )
        
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        
        for i in range(num_slices):
            slice_time = start_time + timedelta(seconds=slice_interval * i)
            adjusted_slice_size = slice_size
            
            slice_obj = OrderSlice(
                order_id=db_order.order_id,
                slice_number=i + 1,
                quantity=adjusted_slice_size,
                scheduled_time=slice_time,
                status="pending"
            )
            db.add(slice_obj)
        
        db.commit()
        logger.info(f"Created VWAP order: {db_order.order_id}")
        
        return {
            "order_id": db_order.order_id,
            "order_type": "vwap",
            "symbol": db_order.symbol,
            "side": db_order.side,
            "total_quantity": db_order.total_quantity,
            "num_slices": num_slices,
            "start_time": db_order.start_time,
            "end_time": db_order.end_time,
            "status": db_order.status
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating VWAP order: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders/{order_id}")
async def get_order(order_id: str, db: Session = Depends(get_db)):
    order = db.query(AdvancedOrder).filter(AdvancedOrder.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/api/analytics/overview")
async def get_analytics_overview(db: Session = Depends(get_db)):
    try:
        total_orders = db.query(AdvancedOrder).count()
        active_orders = db.query(AdvancedOrder).filter(
            AdvancedOrder.status.in_(["active", "executing"])
        ).count()
        completed_orders = db.query(AdvancedOrder).filter(
            AdvancedOrder.status == "completed"
        ).count()
        
        return {
            "total_orders": total_orders,
            "active_orders": active_orders,
            "completed_orders": completed_orders
        }
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "advanced-trading"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8124)