"""
TigerEx Complete Unified Admin Control System
Comprehensive admin system with full control over all trading operations
Version: 4.0.0 - Complete Implementation with All Admin Controls
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import json
from pathlib import Path
from enum import Enum
import hashlib
from decimal import Decimal

from fastapi import FastAPI, HTTPException, Depends, Security, BackgroundTasks, Request, status, Query, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, Index, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, EmailStr, Field, validator
import jwt
from passlib.context import CryptContext
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, generate_latest
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tigerex:tigerex123@localhost:5432/tigerex_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-this-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database setup
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis client
redis_client = None

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
security = HTTPBearer()

# Metrics
REQUEST_COUNT = Counter('requests_total', 'Total requests')
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration')

# ==================== ENUMS ====================

class Exchange(str, Enum):
    BINANCE = "binance"
    KUCOIN = "kucoin"
    BYBIT = "bybit"
    OKX = "okx"
    MEXC = "mexc"
    BITGET = "bitget"
    BITFINEX = "bitfinex"

class TradingType(str, Enum):
    SPOT = "spot"
    FUTURES_PERPETUAL = "futures_perpetual"
    FUTURES_CROSS = "futures_cross"
    FUTURES_DELIVERY = "futures_delivery"
    MARGIN = "margin"
    MARGIN_CROSS = "margin_cross"
    MARGIN_ISOLATED = "margin_isolated"
    OPTIONS = "options"
    DERIVATIVES = "derivatives"
    COPY_TRADING = "copy_trading"
    ETF = "etf"
    LEVERAGED_TOKENS = "leveraged_tokens"
    STRUCTURED_PRODUCTS = "structured_products"

class ContractStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    DELISTED = "delisted"

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    TRADER = "trader"
    VIEWER = "viewer"
    SUSPENDED = "suspended"

class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    PENDING_VERIFICATION = "pending_verification"

class AdminAction(str, Enum):
    CREATE = "create"
    LAUNCH = "launch"
    PAUSE = "pause"
    RESUME = "resume"
    DELETE = "delete"
    UPDATE = "update"
    SUSPEND = "suspend"
    ACTIVATE = "activate"

# ==================== DATABASE MODELS ====================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    phone = Column(String)
    role = Column(String, default="trader")
    status = Column(String, default="active")
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_superadmin = Column(Boolean, default=False)
    kyc_status = Column(String, default="pending")
    kyc_level = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    two_factor_enabled = Column(Boolean, default=False)
    trading_enabled = Column(Boolean, default=True)
    withdrawal_enabled = Column(Boolean, default=True)
    deposit_enabled = Column(Boolean, default=True)
    max_daily_withdrawal = Column(Numeric(20, 8), default=100000)
    permissions = Column(Text)  # JSON string of permissions
    metadata = Column(Text)  # JSON string of additional data

class TradingContract(Base):
    __tablename__ = "trading_contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(String, unique=True, index=True, nullable=False)
    exchange = Column(String, nullable=False)
    trading_type = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    base_asset = Column(String, nullable=False)
    quote_asset = Column(String, nullable=False)
    status = Column(String, default="pending")
    leverage_available = Column(Text)  # JSON array
    min_order_size = Column(Numeric(20, 8), default=0.001)
    max_order_size = Column(Numeric(20, 8), default=1000000)
    price_precision = Column(Integer, default=8)
    quantity_precision = Column(Integer, default=8)
    maker_fee = Column(Numeric(10, 6), default=0.001)
    taker_fee = Column(Numeric(10, 6), default=0.001)
    funding_rate = Column(Numeric(10, 6))
    funding_interval = Column(Integer)
    settlement_date = Column(DateTime(timezone=True))
    strike_price = Column(Numeric(20, 8))
    expiry_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String)
    metadata = Column(Text)  # JSON string

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(String, unique=True, index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    admin_id = Column(String, nullable=False)
    admin_username = Column(String)
    action = Column(String, nullable=False)
    target_type = Column(String, nullable=False)
    target_id = Column(String, nullable=False)
    details = Column(Text)  # JSON string
    ip_address = Column(String)
    user_agent = Column(String)

# ==================== PYDANTIC MODELS ====================

class ContractCreateRequest(BaseModel):
    exchange: Exchange
    trading_type: TradingType
    symbol: str
    base_asset: str
    quote_asset: str
    leverage_available: Optional[List[int]] = [1, 2, 3, 5, 10, 20, 50, 100, 125]
    min_order_size: float = 0.001
    max_order_size: float = 1000000
    price_precision: int = 8
    quantity_precision: int = 8
    maker_fee: float = 0.001
    taker_fee: float = 0.001
    funding_rate: Optional[float] = 0.0001
    funding_interval: Optional[int] = 8
    settlement_date: Optional[datetime] = None
    strike_price: Optional[float] = None
    expiry_date: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class ContractUpdateRequest(BaseModel):
    status: Optional[ContractStatus] = None
    leverage_available: Optional[List[int]] = None
    min_order_size: Optional[float] = None
    max_order_size: Optional[float] = None
    maker_fee: Optional[float] = None
    taker_fee: Optional[float] = None
    funding_rate: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class UserCreateRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.TRADER
    permissions: Optional[List[str]] = None

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    trading_enabled: Optional[bool] = None
    withdrawal_enabled: Optional[bool] = None
    deposit_enabled: Optional[bool] = None
    max_daily_withdrawal: Optional[float] = None
    permissions: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class AdminResponse(BaseModel):
    message: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# ==================== HELPER FUNCTIONS ====================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_admin_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
    """Verify admin JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        if not payload.get("is_admin") and payload.get("role") not in ["super_admin", "admin", "moderator"]:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def generate_contract_id(exchange: str, trading_type: str, symbol: str) -> str:
    """Generate unique contract ID"""
    data = f"{exchange}_{trading_type}_{symbol}_{datetime.now().isoformat()}"
    return hashlib.sha256(data.encode()).hexdigest()[:16].upper()

def generate_user_id() -> str:
    """Generate unique user ID"""
    return hashlib.sha256(f"{datetime.now().isoformat()}{os.urandom(16)}".encode()).hexdigest()[:16].upper()

def generate_audit_log_id() -> str:
    """Generate unique audit log ID"""
    return hashlib.sha256(f"{datetime.now().isoformat()}{os.urandom(8)}".encode()).hexdigest()[:16].upper()

def log_admin_action(db: Session, admin: Dict[str, Any], action: str, target_type: str, target_id: str, details: Dict[str, Any]):
    """Log admin action for audit trail"""
    audit_log = AuditLog(
        log_id=generate_audit_log_id(),
        admin_id=admin.get("user_id", "unknown"),
        admin_username=admin.get("username", "unknown"),
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=json.dumps(details)
    )
    db.add(audit_log)
    db.commit()
    logger.info(f"Admin action logged: {action} by {admin.get('username')} on {target_type} {target_id}")

# ==================== FASTAPI APP ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global redis_client
    redis_client = redis.from_url(REDIS_URL)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    logger.info("TigerEx Complete Admin System started")
    yield
    
    # Shutdown
    if redis_client:
        await redis_client.close()
    logger.info("TigerEx Complete Admin System stopped")

app = FastAPI(
    title="TigerEx Complete Admin Control System",
    version="4.0.0",
    description="Complete admin control system for all trading operations",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== TRADING CONTRACT ADMIN ENDPOINTS ====================

@app.post("/api/admin/contracts/create", response_model=AdminResponse)
async def create_trading_contract(
    request: ContractCreateRequest,
    admin: Dict[str, Any] = Depends(verify_admin_token),
    db: Session = Depends(get_db)
):
    """
    Admin: Create a new trading contract for any exchange and trading type
    Supports: Spot, Futures (Perpetual/Cross/Delivery), Options, Derivatives, Copy Trading, ETF
    """
    try:
        contract_id = generate_contract_id(request.exchange.value, request.trading_type.value, request.symbol)
        
        # Check if contract already exists
        existing = db.query(TradingContract).filter(
            TradingContract.exchange == request.exchange.value,
            TradingContract.trading_type == request.trading_type.value,
            TradingContract.symbol == request.symbol
        ).first()
        
        if existing and existing.status != ContractStatus.DELISTED.value:
            raise HTTPException(status_code=400, detail="Contract already exists for this symbol and trading type")
        
        contract = TradingContract(
            contract_id=contract_id,
            exchange=request.exchange.value,
            trading_type=request.trading_type.value,
            symbol=request.symbol,
            base_asset=request.base_asset,
            quote_asset=request.quote_asset,
            status=ContractStatus.PENDING.value,
            leverage_available=json.dumps(request.leverage_available),
            min_order_size=request.min_order_size,
            max_order_size=request.max_order_size,
            price_precision=request.price_precision,
            quantity_precision=request.quantity_precision,
            maker_fee=request.maker_fee,
            taker_fee=request.taker_fee,
            funding_rate=request.funding_rate,
            funding_interval=request.funding_interval,
            settlement_date=request.settlement_date,
            strike_price=request.strike_price,
            expiry_date=request.expiry_date,
            created_by=admin.get("user_id"),
            metadata=json.dumps(request.metadata) if request.metadata else None
        )
        
        db.add(contract)
        db.commit()
        db.refresh(contract)
        
        log_admin_action(
            db=db,
            admin=admin,
            action=AdminAction.CREATE.value,
            target_type="contract",
            target_id=contract_id,
            details={
                "exchange": request.exchange.value,
                "trading_type": request.trading_type.value,
                "symbol": request.symbol
            }
        )
        
        logger.info(f"Contract created: {contract_id} - {request.symbol} on {request.exchange.value}")
        
        return AdminResponse(
            message="Trading contract created successfully",
            success=True,
            data={
                "contract_id": contract_id,
                "symbol": request.symbol,
                "exchange": request.exchange.value,
                "trading_type": request.trading_type.value,
                "status": ContractStatus.PENDING.value
            }
        )
        
    except Exception as e:
        logger.error(f"Error creating contract: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create contract: {str(e)}")

@app.post("/api/admin/contracts/{contract_id}/launch", response_model=AdminResponse)
async def launch_trading_contract(
    contract_id: str,
    admin: Dict[str, Any] = Depends(verify_admin_token),
    db: Session = Depends(get_db)
):
    """Admin: Launch a pending contract to make it active for trading"""
    try:
        contract = db.query(TradingContract).filter(TradingContract.contract_id == contract_id).first()
        
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        if contract.status != ContractStatus.PENDING.value:
            raise HTTPException(status_code=400, detail=f"Contract is not in pending status. Current status: {contract.status}")
        
        contract.status = ContractStatus.ACTIVE.value
        contract.updated_at = datetime.now()
        
        db.commit()
        
        log_admin_action(
            db=db,
            admin=admin,
            action=AdminAction.LAUNCH.value,
            target_type="contract",
            target_id=contract_id,
            details={"symbol": contract.symbol, "exchange": contract.exchange}
        )
        
        logger.info(f"Contract launched: {contract_id} - {contract.symbol}")
        
        return AdminResponse(
            message="Contract launched successfully",
            success=True,
            data={
                "contract_id": contract_id,
                "symbol": contract.symbol,
                "status": ContractStatus.ACTIVE.value
            }
        )
        
    except Exception as e:
        logger.error(f"Error launching contract: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to launch contract: {str(e)}")

@app.post("/api/admin/contracts/{contract_id}/pause", response_model=AdminResponse)
async def pause_trading_contract(
    contract_id: str,
    reason: str = Body(..., embed=True),
    admin: Dict[str, Any] = Depends(verify_admin_token),
    db: Session = Depends(get_db)
):
    """Admin: Pause an active contract temporarily"""
    try:
        contract = db.query(TradingContract).filter(TradingContract.contract_id == contract_id).first()
        
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        if contract.status != ContractStatus.ACTIVE.value:
            raise HTTPException(status_code=400, detail="Only active contracts can be paused")
        
        contract.status = ContractStatus.PAUSED.value
        contract.updated_at = datetime.now()
        
        db.commit()
        
        log_admin_action(
            db=db,
            admin=admin,
            action=AdminAction.PAUSE.value,
            target_type="contract",
            target_id=contract_id,
            details={"symbol": contract.symbol, "reason": reason}
        )
        
        logger.info(f"Contract paused: {contract_id} - {contract.symbol}. Reason: {reason}")
        
        return AdminResponse(
            message="Contract paused successfully",
            success=True,
            data={
                "contract_id": contract_id,
                "symbol": contract.symbol,
                "status": ContractStatus.PAUSED.value,
                "reason": reason
            }
        )
        
    except Exception as e:
        logger.error(f"Error pausing contract: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to pause contract: {str(e)}")

@app.post("/api/admin/contracts/{contract_id}/resume", response_model=AdminResponse)
async def resume_trading_contract(
    contract_id: str,
    admin: Dict[str, Any] = Depends(verify_admin_token),
    db: Session = Depends(get_db)
):
    """Admin: Resume a paused contract"""
    try:
        contract = db.query(TradingContract).filter(TradingContract.contract_id == contract_id).first()
        
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        if contract.status != ContractStatus.PAUSED.value:
            raise HTTPException(status_code=400, detail="Only paused contracts can be resumed")
        
        contract.status = ContractStatus.ACTIVE.value
        contract.updated_at = datetime.now()
        
        db.commit()
        
        log_admin_action(
            db=db,
            admin=admin,
            action=AdminAction.RESUME.value,
            target_type="contract",
            target_id=contract_id,
            details={"symbol": contract.symbol}
        )
        
        logger.info(f"Contract resumed: {contract_id} - {contract.symbol}")
        
        return AdminResponse(
            message="Contract resumed successfully",
            success=True,
            data={
                "contract_id": contract_id,
                "symbol": contract.symbol,
                "status": ContractStatus.ACTIVE.value
            }
        )
        
    except Exception as e:
        logger.error(f"Error resuming contract: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to resume contract: {str(e)}")

@app.delete("/api/admin/contracts/{contract_id}", response_model=AdminResponse)
async def delete_trading_contract(
    contract_id: str,
    reason: str = Body(..., embed=True),
    admin: Dict[str, Any] = Depends(verify_admin_token),
    db: Session = Depends(get_db)
):
    """Admin: Delete a contract (soft delete by marking as delisted)"""
    try:
        contract = db.query(TradingContract).filter(TradingContract.contract_id == contract_id).first()
        
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        contract.status = ContractStatus.DELISTED.value
        contract.updated_at = datetime.now()
        
        db.commit()
        
        log_admin_action(
            db=db,
            admin=admin,
            action=AdminAction.DELETE.value,
            target_type="contract",
            target_id=contract_id,
            details={"symbol": contract.symbol, "reason": reason}
        )
        
        logger.info(f"Contract deleted: {contract_id} - {contract.symbol}. Reason: {reason}")
        
        return AdminResponse(
            message="Contract deleted successfully",
            success=True,
            data={
                "contract_id": contract_id,
                "symbol": contract.symbol,
                "status": ContractStatus.DELISTED.value,
                "reason": reason
            }
        )
        
    except Exception as e:
        logger.error(f"Error deleting contract: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete contract: {str(e)}")

@app.put("/api/admin/contracts/{contract_id}", response_model=AdminResponse)
async def update_trading_contract(
    contract_id: str,
    update_request: ContractUpdateRequest,
    admin: Dict[str, Any] = Depends(verify_admin_token),
    db: Session = Depends(get_db)
):
    """Admin: Update contract parameters"""
    try:
        contract = db.query(TradingContract).filter(TradingContract.contract_id == contract_id).first()
        
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        updates = {}
        
        if update_request.status is not None:
            contract.status = update_request.status.value
            updates["status"] = update_request.status.value
        
        if update_request.leverage_available is not None:
            contract.leverage_available = json.dumps(update_request.leverage_available)
            updates["leverage_available"] = update_request.leverage_available
        
        if update_request.min_order_size is not None:
            contract.min_order_size = update_request.min_order_size
            updates["min_order_size"] = update_request.min_order_size
        
        if update_request.max_order_size is not None:
            contract.max_order_size = update_request.max_order_size
            updates["max_order_size"] = update_request.max_order_size
        
        if update_request.maker_fee is not None:
            contract.maker_fee = update_request.maker_fee
            updates["maker_fee"] = update_request.maker_fee
        
        if update_request.taker_fee is not None:
            contract.taker_fee = update_request.taker_fee
            updates["taker_fee"] = update_request.taker_fee
        
        if update_request.funding_rate is not None:
            contract.funding_rate = update_request.funding_rate
            updates["funding_rate"] = update_request.funding_rate
        
        if update_request.metadata is not None:
            contract.metadata = json.dumps(update_request.metadata)
            updates["metadata"] = update_request.metadata
        
        contract.updated_at = datetime.now()
        
        db.commit()
        
        log_admin_action(
            db=db,
            admin=admin,
            action=AdminAction.UPDATE.value,
            target_type="contract",
            target_id=contract_id,
            details={"symbol": contract.symbol, "updates": updates}
        )
        
        logger.info(f"Contract updated: {contract_id} - {contract.symbol}")
        
        return AdminResponse(
            message="Contract updated successfully",
            success=True,
            data={
                "contract_id": contract_id,
                "symbol": contract.symbol,
                "updates": updates
            }
        )
        
    except Exception as e:
        logger.error(f"Error updating contract: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update contract: {str(e)}")

@app.get("/api/admin/contracts")
async def list_trading_contracts(
    admin: Dict[str, Any] = Depends(verify_admin_token),
    db: Session = Depends(get_db),
    exchange: Optional[Exchange] = None,
    trading_type: Optional[TradingType] = None,
    status: Optional[ContractStatus] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Admin: List all trading contracts with optional filters"""
    try:
        query = db.query(TradingContract)
        
        if exchange:
            query = query.filter(TradingContract.exchange == exchange.value)
        if trading_type:
            query = query.filter(TradingContract.trading_type == trading_type.value)
        if status:
            query = query.filter(TradingContract.status == status.value)
        
        total = query.count()
        contracts = query.offset(offset).limit(limit).all()
        
        contract_list = []
        for contract in contracts:
            contract_data = {
                "contract_id": contract.contract_id,
                "exchange": contract.exchange,
                "trading_type": contract.trading_type,
                "symbol": contract.symbol,
                "base_asset": contract.base_asset,
                "quote_asset": contract.quote_asset,
                "status": contract.status,
                "leverage_available": json.loads(contract.leverage_available) if contract.leverage_available else None,
                "min_order_size": float(contract.min_order_size),
                "max_order_size": float(contract.max_order_size),
                "maker_fee": float(contract.maker_fee),
                "taker_fee": float(contract.taker_fee),
                "created_at": contract.created_at.isoformat(),
                "updated_at": contract.updated_at.isoformat() if contract.updated_at else None,
                "created_by": contract.created_by
            }
            contract_list.append(contract_data)
        
        return {
            "contracts": contract_list,
            "total": total,
            "limit": limit,
            "offset": offset,
            "filters": {
                "exchange": exchange.value if exchange else None,
                "trading_type": trading_type.value if trading_type else None,
                "status": status.value if status else None
            }
        }
        
    except Exception as e:
        logger.error(f"Error listing contracts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list contracts: {str(e)}")

# ==================== USER MANAGEMENT ENDPOINTS ====================

@app.post("/api/admin/users/create", response_model=AdminResponse)
async def create_user(
    request: UserCreateRequest,
    admin: Dict[str, Any] = Depends(verify_admin_token),
    db: Session = Depends(get_db)
):
    """Admin: Create a new user account"""
    try:
        # Check if email or username already exists
        existing_email = db.query(User).filter(User.email == request.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        existing_username = db.query(User).filter(User.username == request.username).first()
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already taken")
        
        user_id = generate_user_id()
        hashed_password = pwd_context.hash(request.password)
        
        user = User(
            user_id=user_id,
            email=request.email,
            username=request.username,
            hashed_password=hashed_password,
            full_name=request.full_name,
            role=request.role.value,
            status=UserStatus.ACTIVE.value,
            is_admin=request.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MODERATOR],
            is_superadmin=request.role == UserRole.SUPER_ADMIN,
            permissions=json.dumps(request.permissions) if request.permissions else None
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        log_admin_action(
            db=db,
            admin=admin,
            action="CREATE_USER",
            target_type="user",
            target_id=user_id,
            details={
                "email": request.email,
                "username": request.username,
                "role": request.role.value
            }
        )
        
        logger.info(f"User created: {user_id} - {request.username} by admin {admin.get('username')}")
        
        return AdminResponse(
            message="User created successfully",
            success=True,
            data={
                "user_id": user_id,
                "username": request.username,
                "email": request.email,
                "role": request.role.value
            }
        )
        
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

@app.get("/api/admin/users")
async def list_users(
    admin: Dict[str, Any] = Depends(verify_admin_token),
    db: Session = Depends(get_db),
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Admin: List all users with optional filters"""
    try:
        query = db.query(User)
        
        if role:
            query = query.filter(User.role == role.value)
        if status:
            query = query.filter(User.status == status.value)
        
        total = query.count()
        users = query.offset(offset).limit(limit).all()
        
        user_list = []
        for user in users:
            user_data = {
                "user_id": user.user_id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role,
                "status": user.status,
                "kyc_status": user.kyc_status,
                "kyc_level": user.kyc_level,
                "trading_enabled": user.trading_enabled,
                "withdrawal_enabled": user.withdrawal_enabled,
                "deposit_enabled": user.deposit_enabled,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "permissions": json.loads(user.permissions) if user.permissions else []
            }
            user_list.append(user_data)
        
        return {
            "users": user_list,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list users: {str(e)}")

@app.put("/api/admin/users/{user_id}", response_model=AdminResponse)
async def update_user(
    user_id: str,
    request: UserUpdateRequest,
    admin: Dict[str, Any] = Depends(verify_admin_token),
    db: Session = Depends(get_db)
):
    """Admin: Update user account"""
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        updates = {}
        
        if request.full_name is not None:
            user.full_name = request.full_name
            updates["full_name"] = request.full_name
        
        if request.role is not None:
            user.role = request.role.value
            user.is_admin = request.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MODERATOR]
            user.is_superadmin = request.role == UserRole.SUPER_ADMIN
            updates["role"] = request.role.value
        
        if request.status is not None:
            user.status = request.status.value
            updates["status"] = request.status.value
        
        if request.trading_enabled is not None:
            user.trading_enabled = request.trading_enabled
            updates["trading_enabled"] = request.trading_enabled
        
        if request.withdrawal_enabled is not None:
            user.withdrawal_enabled = request.withdrawal_enabled
            updates["withdrawal_enabled"] = request.withdrawal_enabled
        
        if request.deposit_enabled is not None:
            user.deposit_enabled = request.deposit_enabled
            updates["deposit_enabled"] = request.deposit_enabled
        
        if request.max_daily_withdrawal is not None:
            user.max_daily_withdrawal = request.max_daily_withdrawal
            updates["max_daily_withdrawal"] = request.max_daily_withdrawal
        
        if request.permissions is not None:
            user.permissions = json.dumps(request.permissions)
            updates["permissions"] = request.permissions
        
        if request.metadata is not None:
            user.metadata = json.dumps(request.metadata)
            updates["metadata"] = request.metadata
        
        user.updated_at = datetime.now()
        
        db.commit()
        
        log_admin_action(
            db=db,
            admin=admin,
            action="UPDATE_USER",
            target_type="user",
            target_id=user_id,
            details={"username": user.username, "updates": updates}
        )
        
        logger.info(f"User updated: {user_id} by admin {admin.get('username')}")
        
        return AdminResponse(
            message="User updated successfully",
            success=True,
            data={
                "user_id": user_id,
                "username": user.username,
                "updates": updates
            }
        )
        
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")

@app.post("/api/admin/users/{user_id}/suspend", response_model=AdminResponse)
async def suspend_user(
    user_id: str,
    reason: str = Body(..., embed=True),
    admin: Dict[str, Any] = Depends(verify_admin_token),
    db: Session = Depends(get_db)
):
    """Admin: Suspend user account"""
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.status = UserStatus.SUSPENDED.value
        user.trading_enabled = False
        user.updated_at = datetime.now()
        
        db.commit()
        
        log_admin_action(
            db=db,
            admin=admin,
            action=AdminAction.SUSPEND.value,
            target_type="user",
            target_id=user_id,
            details={"username": user.username, "reason": reason}
        )
        
        logger.info(f"User suspended: {user_id} by admin {admin.get('username')}. Reason: {reason}")
        
        return AdminResponse(
            message="User suspended successfully",
            success=True,
            data={
                "user_id": user_id,
                "username": user.username,
                "status": UserStatus.SUSPENDED.value,
                "reason": reason
            }
        )
        
    except Exception as e:
        logger.error(f"Error suspending user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to suspend user: {str(e)}")

@app.post("/api/admin/users/{user_id}/activate", response_model=AdminResponse)
async def activate_user(
    user_id: str,
    admin: Dict[str, Any] = Depends(verify_admin_token),
    db: Session = Depends(get_db)
):
    """Admin: Activate suspended user account"""
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.status = UserStatus.ACTIVE.value
        user.trading_enabled = True
        user.updated_at = datetime.now()
        
        db.commit()
        
        log_admin_action(
            db=db,
            admin=admin,
            action=AdminAction.ACTIVATE.value,
            target_type="user",
            target_id=user_id,
            details={"username": user.username}
        )
        
        logger.info(f"User activated: {user_id} by admin {admin.get('username')}")
        
        return AdminResponse(
            message="User activated successfully",
            success=True,
            data={
                "user_id": user_id,
                "username": user.username,
                "status": UserStatus.ACTIVE.value
            }
        )
        
    except Exception as e:
        logger.error(f"Error activating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to activate user: {str(e)}")

# ==================== EMERGENCY CONTROLS ====================

@app.post("/api/admin/emergency/halt-trading", response_model=AdminResponse)
async def emergency_halt_trading(
    reason: str = Body(..., embed=True),
    admin: Dict[str, Any] = Depends(verify_admin_token),
    db: Session = Depends(get_db)
):
    """Admin: Emergency halt all trading activities"""
    try:
        # Disable trading for all users except admins
        users = db.query(User).filter(User.role.notin_(["super_admin", "admin"])).all()
        
        for user in users:
            user.trading_enabled = False
        
        db.commit()
        
        log_admin_action(
            db=db,
            admin=admin,
            action="EMERGENCY_HALT_TRADING",
            target_type="system",
            target_id="all",
            details={"reason": reason, "affected_users": len(users)}
        )
        
        logger.warning(f"EMERGENCY: Trading halted by {admin.get('username')}. Reason: {reason}")
        
        return AdminResponse(
            message="Trading halted for all users",
            success=True,
            data={
                "reason": reason,
                "affected_users": len(users),
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error halting trading: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to halt trading: {str(e)}")

@app.post("/api/admin/emergency/resume-trading", response_model=AdminResponse)
async def emergency_resume_trading(
    admin: Dict[str, Any] = Depends(verify_admin_token),
    db: Session = Depends(get_db)
):
    """Admin: Resume trading after emergency halt"""
    try:
        # Re-enable trading for active users
        users = db.query(User).filter(
            User.status == UserStatus.ACTIVE.value,
            User.role.notin_(["suspended"])
        ).all()
        
        for user in users:
            user.trading_enabled = True
        
        db.commit()
        
        log_admin_action(
            db=db,
            admin=admin,
            action="EMERGENCY_RESUME_TRADING",
            target_type="system",
            target_id="all",
            details={"affected_users": len(users)}
        )
        
        logger.info(f"Trading resumed by {admin.get('username')}")
        
        return AdminResponse(
            message="Trading resumed for all active users",
            success=True,
            data={
                "affected_users": len(users),
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error resuming trading: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to resume trading: {str(e)}")

# ==================== AUDIT & ANALYTICS ====================

@app.get("/api/admin/audit-logs")
async def get_audit_logs(
    admin: Dict[str, Any] = Depends(verify_admin_token),
    db: Session = Depends(get_db),
    action: Optional[str] = None,
    target_type: Optional[str] = None,
    admin_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Admin: Get audit logs with optional filters"""
    try:
        query = db.query(AuditLog)
        
        if action:
            query = query.filter(AuditLog.action == action)
        if target_type:
            query = query.filter(AuditLog.target_type == target_type)
        if admin_id:
            query = query.filter(AuditLog.admin_id == admin_id)
        
        total = query.count()
        logs = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()
        
        log_list = []
        for log in logs:
            log_data = {
                "log_id": log.log_id,
                "timestamp": log.timestamp.isoformat(),
                "admin_id": log.admin_id,
                "admin_username": log.admin_username,
                "action": log.action,
                "target_type": log.target_type,
                "target_id": log.target_id,
                "details": json.loads(log.details) if log.details else {}
            }
            log_list.append(log_data)
        
        return {
            "audit_logs": log_list,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error getting audit logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get audit logs: {str(e)}")

@app.get("/api/admin/statistics")
async def get_system_statistics(
    admin: Dict[str, Any] = Depends(verify_admin_token),
    db: Session = Depends(get_db)
):
    """Admin: Get system statistics"""
    try:
        # User statistics
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.status == UserStatus.ACTIVE.value).count()
        suspended_users = db.query(User).filter(User.status == UserStatus.SUSPENDED.value).count()
        
        # Contract statistics
        total_contracts = db.query(TradingContract).count()
        active_contracts = db.query(TradingContract).filter(TradingContract.status == ContractStatus.ACTIVE.value).count()
        paused_contracts = db.query(TradingContract).filter(TradingContract.status == ContractStatus.PAUSED.value).count()
        
        # Audit statistics
        total_audit_logs = db.query(AuditLog).count()
        recent_actions = db.query(AuditLog).filter(
            AuditLog.timestamp >= datetime.now() - timedelta(days=1)
        ).count()
        
        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "suspended": suspended_users
            },
            "contracts": {
                "total": total_contracts,
                "active": active_contracts,
                "paused": paused_contracts
            },
            "audit": {
                "total_logs": total_audit_logs,
                "recent_actions_24h": recent_actions
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

# ==================== HEALTH CHECK ====================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "4.0.0",
        "service": "TigerEx Complete Admin Control System"
    }

# ==================== STARTUP ====================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)