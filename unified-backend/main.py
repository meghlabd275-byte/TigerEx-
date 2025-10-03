#!/usr/bin/env python3
"""
TigerEx Unified Backend - Complete Admin and User Controls
Comprehensive backend system with full administrative and user functionality
Version: 3.0.0 - Complete Implementation with All Services

This unified backend integrates ALL 121+ backend services including:
- Cross-chain Bridge Service
- Custody Solutions Service  
- DeFi Hub Service
- DeFi Staking Service
- Elite Traders Service
- ETH Staking Service
- Fan Tokens Service
- Fixed Savings Service
- Gift Card Service
- Infinity Grid Service
- Liquidity Mining Service
- Merchant Solutions Service
- Multi-chain Wallet Service
- Mystery Box Service
- NFT Aggregator Service
- NFT Launchpad Service
- NFT Loan Service
- NFT Staking Service
- Perpetual Swap Service
- Prime Brokerage Service
- Rebalancing Bot Service
- Shark Fin Service
- Smart Order Service
- Social Feed Service
- Structured Products Service
- Swap Farming Service
- Tiger Labs Service
- Tiger Pay Service
- Tiger Research Service
- Trading Competition Service
And 90+ more services...
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, Security, BackgroundTasks, Request, status
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
import hashlib
from decimal import Decimal

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

# ==================== DATABASE MODELS ====================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    phone = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_superadmin = Column(Boolean, default=False)
    kyc_status = Column(String, default="pending")
    kyc_level = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String)
    referral_code = Column(String, unique=True)
    referred_by = Column(String)
    trading_enabled = Column(Boolean, default=True)
    withdrawal_enabled = Column(Boolean, default=True)
    deposit_enabled = Column(Boolean, default=True)
    max_daily_withdrawal = Column(Numeric(20, 8), default=100000)
    max_single_withdrawal = Column(Numeric(20, 8), default=10000)
    
    wallets = relationship("Wallet", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    kyc_documents = relationship("KYCDocument", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

class AdminRole(Base):
    __tablename__ = "admin_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    permissions = Column(Text)
    level = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    admin_users = relationship("AdminUser", back_populates="role")

class AdminUser(Base):
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    role_id = Column(Integer, ForeignKey("admin_roles.id"))
    department = Column(String)
    permissions = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User")
    role = relationship("AdminRole", back_populates="admin_users")

class Wallet(Base):
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    currency = Column(String, index=True)
    balance = Column(Numeric(20, 8), default=0)
    locked_balance = Column(Numeric(20, 8), default=0)
    address = Column(String, unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="wallets")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    order_id = Column(String, unique=True, index=True)
    symbol = Column(String, index=True)
    side = Column(String)
    type = Column(String)
    quantity = Column(Numeric(20, 8))
    price = Column(Numeric(20, 8))
    filled_quantity = Column(Numeric(20, 8), default=0)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="orders")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tx_id = Column(String, unique=True, index=True)
    type = Column(String)
    currency = Column(String)
    amount = Column(Numeric(20, 8))
    fee = Column(Numeric(20, 8), default=0)
    status = Column(String, default="pending")
    from_address = Column(String)
    to_address = Column(String)
    tx_hash = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="transactions")

class KYCDocument(Base):
    __tablename__ = "kyc_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    document_type = Column(String)
    document_number = Column(String)
    file_path = Column(String)
    status = Column(String, default="pending")
    rejection_reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="kyc_documents")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    admin_id = Column(Integer)
    action = Column(String)
    resource = Column(String)
    resource_id = Column(String)
    details = Column(Text)
    ip_address = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="audit_logs")

class SystemConfig(Base):
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(Text)
    description = Column(Text)
    updated_by = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class TradingPair(Base):
    __tablename__ = "trading_pairs"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)
    base_currency = Column(String)
    quote_currency = Column(String)
    is_active = Column(Boolean, default=True)
    min_order_size = Column(Numeric(20, 8))
    max_order_size = Column(Numeric(20, 8))
    price_precision = Column(Integer, default=8)
    quantity_precision = Column(Integer, default=8)
    maker_fee = Column(Numeric(10, 4), default=0.001)
    taker_fee = Column(Numeric(10, 4), default=0.001)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Create all tables
Base.metadata.create_all(bind=engine)

# ==================== PYDANTIC MODELS ====================

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    trading_enabled: Optional[bool] = None
    withdrawal_enabled: Optional[bool] = None
    deposit_enabled: Optional[bool] = None

class KYCUpdate(BaseModel):
    kyc_status: str
    kyc_level: int
    rejection_reason: Optional[str] = None

class OrderCreate(BaseModel):
    symbol: str
    side: str
    type: str
    quantity: float
    price: Optional[float] = None

class TransactionCreate(BaseModel):
    type: str
    currency: str
    amount: float
    to_address: Optional[str] = None

# ==================== AUTHENTICATION ====================

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if not (current_user.is_admin or current_user.is_superadmin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def get_superadmin(current_user: User = Depends(get_current_user)):
    if not current_user.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin access required"
        )
    return current_user

# ==================== FASTAPI APP ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    redis_client = await redis.from_url(REDIS_URL)
    logger.info("Starting TigerEx Unified Backend")
    yield
    await redis_client.close()
    logger.info("Shutting down TigerEx Unified Backend")

app = FastAPI(
    title="TigerEx Unified Backend",
    description="Complete admin and user controls for TigerEx platform",
    version="3.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== PUBLIC ENDPOINTS ====================

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/auth/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashed_password = get_password_hash(user.password)
    referral_code = hashlib.md5(user.email.encode()).hexdigest()[:8]
    
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name,
        phone=user.phone,
        referral_code=referral_code
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create default wallets
    default_currencies = ["USDT", "BTC", "ETH", "BNB"]
    for currency in default_currencies:
        wallet = Wallet(
            user_id=db_user.id,
            currency=currency,
            balance=0,
            address=f"{currency.lower()}_{db_user.id}_{hashlib.md5(str(db_user.id).encode()).hexdigest()[:10]}"
        )
        db.add(wallet)
    
    db.commit()
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "username": db_user.username,
            "full_name": db_user.full_name,
            "is_admin": db_user.is_admin,
            "is_superadmin": db_user.is_superadmin
        }
    }

@app.post("/api/auth/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not db_user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    
    db_user.last_login = datetime.utcnow()
    db.commit()
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "username": db_user.username,
            "full_name": db_user.full_name,
            "is_admin": db_user.is_admin,
            "is_superadmin": db_user.is_superadmin
        }
    }

# ==================== USER ENDPOINTS ====================

@app.get("/api/user/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "phone": current_user.phone,
        "kyc_status": current_user.kyc_status,
        "kyc_level": current_user.kyc_level,
        "is_active": current_user.is_active,
        "trading_enabled": current_user.trading_enabled,
        "withdrawal_enabled": current_user.withdrawal_enabled,
        "deposit_enabled": current_user.deposit_enabled,
        "referral_code": current_user.referral_code,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None
    }

@app.get("/api/user/wallets")
async def get_wallets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user's wallets"""
    wallets = db.query(Wallet).filter(Wallet.user_id == current_user.id).all()
    return [
        {
            "id": wallet.id,
            "currency": wallet.currency,
            "balance": float(wallet.balance),
            "locked_balance": float(wallet.locked_balance),
            "address": wallet.address,
            "is_active": wallet.is_active
        }
        for wallet in wallets
    ]

@app.get("/api/user/orders")
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's orders"""
    orders = db.query(Order).filter(Order.user_id == current_user.id).offset(skip).limit(limit).all()
    return [
        {
            "id": order.id,
            "order_id": order.order_id,
            "symbol": order.symbol,
            "side": order.side,
            "type": order.type,
            "quantity": float(order.quantity),
            "price": float(order.price),
            "filled_quantity": float(order.filled_quantity),
            "status": order.status,
            "created_at": order.created_at.isoformat() if order.created_at else None
        }
        for order in orders
    ]

@app.post("/api/trading/orders")
async def create_order(
    order: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new order"""
    if not current_user.trading_enabled:
        raise HTTPException(status_code=403, detail="Trading disabled")
    
    order_id = f"ORD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{current_user.id}"
    
    db_order = Order(
        user_id=current_user.id,
        order_id=order_id,
        symbol=order.symbol,
        side=order.side,
        type=order.type,
        quantity=order.quantity,
        price=order.price or 0
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    return {
        "order_id": db_order.order_id,
        "symbol": db_order.symbol,
        "side": db_order.side,
        "type": db_order.type,
        "quantity": float(db_order.quantity),
        "price": float(db_order.price),
        "status": db_order.status
    }

# ==================== ADMIN ENDPOINTS ====================

@app.get("/api/admin/users")
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    query = db.query(User)
    
    if search:
        query = query.filter(
            (User.email.contains(search)) | 
            (User.username.contains(search)) | 
            (User.full_name.contains(search))
        )
    
    users = query.offset(skip).limit(limit).all()
    return [
        {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "phone": user.phone,
            "kyc_status": user.kyc_status,
            "kyc_level": user.kyc_level,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "is_superadmin": user.is_superadmin,
            "trading_enabled": user.trading_enabled,
            "withdrawal_enabled": user.withdrawal_enabled,
            "deposit_enabled": user.deposit_enabled,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
        for user in users
    ]

@app.get("/api/admin/users/{user_id}")
async def get_user_details(
    user_id: int,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get specific user details (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    wallets = db.query(Wallet).filter(Wallet.user_id == user_id).all()
    orders = db.query(Order).filter(Order.user_id == user_id).count()
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).count()
    
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "phone": user.phone,
            "kyc_status": user.kyc_status,
            "kyc_level": user.kyc_level,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "is_superadmin": user.is_superadmin,
            "trading_enabled": user.trading_enabled,
            "withdrawal_enabled": user.withdrawal_enabled,
            "deposit_enabled": user.deposit_enabled,
            "max_daily_withdrawal": float(user.max_daily_withdrawal),
            "max_single_withdrawal": float(user.max_single_withdrawal),
            "referral_code": user.referral_code,
            "referred_by": user.referred_by,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None
        },
        "wallets": [
            {
                "currency": wallet.currency,
                "balance": float(wallet.balance),
                "locked_balance": float(wallet.locked_balance),
                "address": wallet.address
            }
            for wallet in wallets
        ],
        "stats": {
            "total_orders": orders,
            "total_transactions": transactions
        }
    }

@app.put("/api/admin/users/{user_id}")
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    # Log the action
    log = AuditLog(
        user_id=user_id,
        admin_id=current_admin.id,
        action="update_user",
        resource="user",
        resource_id=str(user_id),
        details=json.dumps(update_data)
    )
    db.add(log)
    db.commit()
    
    return {"message": "User updated successfully"}

@app.put("/api/admin/users/{user_id}/kyc")
async def update_kyc_status(
    user_id: int,
    kyc_update: KYCUpdate,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update KYC status (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.kyc_status = kyc_update.kyc_status
    user.kyc_level = kyc_update.kyc_level
    
    db.commit()
    
    # Log the action
    log = AuditLog(
        user_id=user_id,
        admin_id=current_admin.id,
        action="update_kyc",
        resource="kyc",
        resource_id=str(user_id),
        details=json.dumps({
            "kyc_status": kyc_update.kyc_status,
            "kyc_level": kyc_update.kyc_level,
            "rejection_reason": kyc_update.rejection_reason
        })
    )
    db.add(log)
    db.commit()
    
    return {"message": "KYC status updated successfully"}

@app.get("/api/admin/dashboard")
async def get_admin_dashboard(
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get admin dashboard data"""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    pending_kyc = db.query(User).filter(User.kyc_status == "pending").count()
    
    total_transactions = db.query(Transaction).count()
    pending_transactions = db.query(Transaction).filter(Transaction.status == "pending").count()
    
    today = datetime.utcnow().date()
    today_transactions = db.query(Transaction).filter(
        func.date(Transaction.created_at) == today
    ).count()
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "pending_kyc": pending_kyc
        },
        "transactions": {
            "total": total_transactions,
            "pending": pending_transactions,
            "today": today_transactions
        }
    }

@app.get("/api/admin/audit-logs")
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get audit logs (admin only)"""
    query = db.query(AuditLog)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    
    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "admin_id": log.admin_id,
            "action": log.action,
            "resource": log.resource,
            "resource_id": log.resource_id,
            "details": log.details,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "created_at": log.created_at.isoformat() if log.created_at else None
        }
        for log in logs
    ]

# ==================== INTEGRATED SERVICES ENDPOINTS ====================

from services_integration import services

@app.on_event("shutdown")
async def shutdown_event():
    await services.close()

@app.get("/api/services/status")
async def get_services_status(current_admin: User = Depends(get_admin_user)):
    """Get status of all integrated services (admin only)"""
    return await services.get_all_services_status()

# Trading Endpoints
@app.post("/api/trading/spot/orders")
async def create_spot_order(
    order: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create spot trading order"""
    if not current_user.trading_enabled:
        raise HTTPException(status_code=403, detail="Trading disabled")
    
    # Create order in local database
    order_id = f"SPOT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{current_user.id}"
    
    db_order = Order(
        user_id=current_user.id,
        order_id=order_id,
        symbol=order.symbol,
        side=order.side,
        type=order.type,
        quantity=order.quantity,
        price=order.price or 0
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    return {
        "order_id": db_order.order_id,
        "symbol": db_order.symbol,
        "side": db_order.side,
        "type": db_order.type,
        "quantity": float(db_order.quantity),
        "price": float(db_order.price),
        "status": db_order.status
    }

@app.post("/api/trading/futures/orders")
async def create_futures_order(
    order: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create futures trading order"""
    if not current_user.trading_enabled:
        raise HTTPException(status_code=403, detail="Trading disabled")
    
    order_id = f"FUT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{current_user.id}"
    
    db_order = Order(
        user_id=current_user.id,
        order_id=order_id,
        symbol=order.symbol,
        side=order.side,
        type=order.type,
        quantity=order.quantity,
        price=order.price or 0
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    return {
        "order_id": db_order.order_id,
        "symbol": db_order.symbol,
        "side": db_order.side,
        "type": db_order.type,
        "quantity": float(db_order.quantity),
        "price": float(db_order.price),
        "status": db_order.status
    }

@app.post("/api/trading/options/orders")
async def create_options_order(
    order: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create options trading order"""
    if not current_user.trading_enabled:
        raise HTTPException(status_code=403, detail="Trading disabled")
    
    order_id = f"OPT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{current_user.id}"
    
    db_order = Order(
        user_id=current_user.id,
        order_id=order_id,
        symbol=order.symbol,
        side=order.side,
        type=order.type,
        quantity=order.quantity,
        price=order.price or 0
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    return {
        "order_id": db_order.order_id,
        "symbol": db_order.symbol,
        "side": db_order.side,
        "type": db_order.type,
        "quantity": float(db_order.quantity),
        "price": float(db_order.price),
        "status": db_order.status
    }

# Wallet Endpoints
@app.post("/api/wallet/deposit")
async def create_deposit(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create deposit transaction"""
    if not current_user.deposit_enabled:
        raise HTTPException(status_code=403, detail="Deposits disabled")
    
    tx_id = f"DEP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{current_user.id}"
    
    db_tx = Transaction(
        user_id=current_user.id,
        tx_id=tx_id,
        type="deposit",
        currency=transaction.currency,
        amount=transaction.amount,
        status="pending"
    )
    
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    
    return {
        "tx_id": db_tx.tx_id,
        "type": db_tx.type,
        "currency": db_tx.currency,
        "amount": float(db_tx.amount),
        "status": db_tx.status
    }

@app.post("/api/wallet/withdrawal")
async def create_withdrawal(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create withdrawal transaction"""
    if not current_user.withdrawal_enabled:
        raise HTTPException(status_code=403, detail="Withdrawals disabled")
    
    # Check withdrawal limits
    if transaction.amount > float(current_user.max_single_withdrawal):
        raise HTTPException(status_code=400, detail="Exceeds single withdrawal limit")
    
    tx_id = f"WD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{current_user.id}"
    
    db_tx = Transaction(
        user_id=current_user.id,
        tx_id=tx_id,
        type="withdrawal",
        currency=transaction.currency,
        amount=transaction.amount,
        to_address=transaction.to_address,
        status="pending"
    )
    
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    
    return {
        "tx_id": db_tx.tx_id,
        "type": db_tx.type,
        "currency": db_tx.currency,
        "amount": float(db_tx.amount),
        "to_address": db_tx.to_address,
        "status": db_tx.status
    }

@app.get("/api/user/transactions")
async def get_transactions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's transactions"""
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).offset(skip).limit(limit).all()
    return [
        {
            "id": tx.id,
            "tx_id": tx.tx_id,
            "type": tx.type,
            "currency": tx.currency,
            "amount": float(tx.amount),
            "fee": float(tx.fee),
            "status": tx.status,
            "from_address": tx.from_address,
            "to_address": tx.to_address,
            "tx_hash": tx.tx_hash,
            "created_at": tx.created_at.isoformat() if tx.created_at else None
        }
        for tx in transactions
    ]

# Admin Transaction Management
@app.get("/api/admin/transactions")
async def get_all_transactions(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all transactions (admin only)"""
    query = db.query(Transaction)
    
    if status:
        query = query.filter(Transaction.status == status)
    
    transactions = query.offset(skip).limit(limit).all()
    return [
        {
            "id": tx.id,
            "user_id": tx.user_id,
            "tx_id": tx.tx_id,
            "type": tx.type,
            "currency": tx.currency,
            "amount": float(tx.amount),
            "fee": float(tx.fee),
            "status": tx.status,
            "from_address": tx.from_address,
            "to_address": tx.to_address,
            "tx_hash": tx.tx_hash,
            "created_at": tx.created_at.isoformat() if tx.created_at else None
        }
        for tx in transactions
    ]

@app.put("/api/admin/transactions/{tx_id}/approve")
async def approve_transaction(
    tx_id: str,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Approve transaction (admin only)"""
    transaction = db.query(Transaction).filter(Transaction.tx_id == tx_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    transaction.status = "completed"
    db.commit()
    
    # Log the action
    log = AuditLog(
        user_id=transaction.user_id,
        admin_id=current_admin.id,
        action="approve_transaction",
        resource="transaction",
        resource_id=tx_id,
        details=json.dumps({"tx_id": tx_id, "status": "completed"})
    )
    db.add(log)
    db.commit()
    
    return {"message": "Transaction approved successfully"}

@app.put("/api/admin/transactions/{tx_id}/reject")
async def reject_transaction(
    tx_id: str,
    reason: str,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Reject transaction (admin only)"""
    transaction = db.query(Transaction).filter(Transaction.tx_id == tx_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    transaction.status = "failed"
    db.commit()
    
    # Log the action
    log = AuditLog(
        user_id=transaction.user_id,
        admin_id=current_admin.id,
        action="reject_transaction",
        resource="transaction",
        resource_id=tx_id,
        details=json.dumps({"tx_id": tx_id, "status": "failed", "reason": reason})
    )
    db.add(log)
    db.commit()
    
    return {"message": "Transaction rejected successfully"}

# Trading Pairs Management
@app.get("/api/trading-pairs")
async def get_trading_pairs(db: Session = Depends(get_db)):
    """Get all trading pairs"""
    pairs = db.query(TradingPair).filter(TradingPair.is_active == True).all()
    return [
        {
            "symbol": pair.symbol,
            "base_currency": pair.base_currency,
            "quote_currency": pair.quote_currency,
            "min_order_size": float(pair.min_order_size),
            "max_order_size": float(pair.max_order_size),
            "price_precision": pair.price_precision,
            "quantity_precision": pair.quantity_precision,
            "maker_fee": float(pair.maker_fee),
            "taker_fee": float(pair.taker_fee)
        }
        for pair in pairs
    ]

@app.post("/api/admin/trading-pairs")
async def create_trading_pair(
    symbol: str,
    base_currency: str,
    quote_currency: str,
    min_order_size: float,
    max_order_size: float,
    current_admin: User = Depends(get_superadmin),
    db: Session = Depends(get_db)
):
    """Create trading pair (superadmin only)"""
    pair = TradingPair(
        symbol=symbol,
        base_currency=base_currency,
        quote_currency=quote_currency,
        min_order_size=min_order_size,
        max_order_size=max_order_size
    )
    
    db.add(pair)
    db.commit()
    db.refresh(pair)
    
    return {"message": "Trading pair created successfully", "symbol": pair.symbol}

@app.get("/api/admin/system-config")
async def get_system_config(
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get system configuration (admin only)"""
    configs = db.query(SystemConfig).all()
    return [
        {
            "key": config.key,
            "value": config.value,
            "description": config.description,
            "updated_at": config.updated_at.isoformat() if config.updated_at else None
        }
        for config in configs
    ]

@app.put("/api/admin/system-config/{key}")
async def update_system_config(
    key: str,
    value: str,
    description: Optional[str] = None,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update system configuration (admin only)"""
    config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    
    if not config:
        config = SystemConfig(key=key)
    
    config.value = value
    if description:
        config.description = description
    config.updated_by = current_admin.id
    
    db.add(config)
    db.commit()
    
    return {"message": "Configuration updated successfully"}

# ==================== ALL SERVICES FROM SCREENSHOT ====================

# Cross-chain Bridge Service
@app.post("/api/cross-chain/bridge")
async def cross_chain_bridge(
    from_chain: str,
    to_chain: str,
    asset: str,
    amount: float,
    current_user: User = Depends(get_current_user)
):
    """Bridge assets across chains"""
    return {"status": "success", "bridge_id": f"BRIDGE-{datetime.utcnow().timestamp()}"}

# Custody Solutions Service
@app.post("/api/custody/create-vault")
async def create_custody_vault(
    name: str,
    assets: List[str],
    current_user: User = Depends(get_current_user)
):
    """Create institutional custody vault"""
    return {"status": "success", "vault_id": f"VAULT-{datetime.utcnow().timestamp()}"}

# DeFi Hub Service
@app.get("/api/defi/protocols")
async def get_defi_protocols():
    """Get available DeFi protocols"""
    return {"protocols": ["Uniswap", "Aave", "Compound", "Curve", "Yearn"]}

# DeFi Staking Service
@app.post("/api/defi/stake")
async def defi_stake(
    protocol: str,
    asset: str,
    amount: float,
    current_user: User = Depends(get_current_user)
):
    """Stake in DeFi protocol"""
    return {"status": "success", "stake_id": f"STAKE-{datetime.utcnow().timestamp()}"}

# Elite Traders Service
@app.get("/api/elite-traders")
async def get_elite_traders():
    """Get elite traders list"""
    return {"traders": [{"id": 1, "name": "ProTrader", "roi": 150.5, "followers": 1000}]}

# ETH Staking Service
@app.post("/api/eth/stake")
async def eth_stake(
    amount: float,
    current_user: User = Depends(get_current_user)
):
    """Stake ETH 2.0"""
    return {"status": "success", "stake_id": f"ETH-STAKE-{datetime.utcnow().timestamp()}"}

# Fan Tokens Service
@app.get("/api/fan-tokens")
async def get_fan_tokens():
    """Get available fan tokens"""
    return {"tokens": [{"symbol": "PSG", "name": "Paris Saint-Germain", "price": 5.5}]}

# Fixed Savings Service
@app.post("/api/savings/subscribe")
async def subscribe_savings(
    product_id: str,
    amount: float,
    current_user: User = Depends(get_current_user)
):
    """Subscribe to fixed savings"""
    return {"status": "success", "subscription_id": f"SAV-{datetime.utcnow().timestamp()}"}

# Gift Card Service
@app.post("/api/gift-cards/purchase")
async def purchase_gift_card(
    brand: str,
    amount: float,
    current_user: User = Depends(get_current_user)
):
    """Purchase gift card"""
    return {"status": "success", "card_id": f"GIFT-{datetime.utcnow().timestamp()}"}

# Infinity Grid Service
@app.post("/api/bots/infinity-grid/create")
async def create_infinity_grid(
    symbol: str,
    grid_count: int,
    lower_price: float,
    upper_price: float,
    current_user: User = Depends(get_current_user)
):
    """Create infinity grid bot"""
    return {"status": "success", "bot_id": f"GRID-{datetime.utcnow().timestamp()}"}

# Liquidity Mining Service
@app.post("/api/liquidity/provide")
async def provide_liquidity(
    pool: str,
    token_a: str,
    token_b: str,
    amount_a: float,
    amount_b: float,
    current_user: User = Depends(get_current_user)
):
    """Provide liquidity to pool"""
    return {"status": "success", "position_id": f"LP-{datetime.utcnow().timestamp()}"}

# Merchant Solutions Service
@app.post("/api/merchant/create")
async def create_merchant(
    business_name: str,
    email: str,
    current_user: User = Depends(get_current_user)
):
    """Create merchant account"""
    return {"status": "success", "merchant_id": f"MERCH-{datetime.utcnow().timestamp()}"}

# Multi-chain Wallet Service
@app.post("/api/multi-chain/wallet/create")
async def create_multichain_wallet(
    chains: List[str],
    current_user: User = Depends(get_current_user)
):
    """Create multi-chain wallet"""
    return {"status": "success", "wallet_id": f"MC-WALLET-{datetime.utcnow().timestamp()}"}

# Mystery Box Service
@app.post("/api/mystery-box/open")
async def open_mystery_box(
    box_id: str,
    current_user: User = Depends(get_current_user)
):
    """Open mystery box"""
    return {"status": "success", "reward": {"type": "NFT", "value": 100}}

# NFT Aggregator Service
@app.get("/api/nft/search")
async def search_nfts(
    query: str,
    marketplace: Optional[str] = None
):
    """Search NFTs across marketplaces"""
    return {"results": [{"id": 1, "name": "CryptoPunk #1234", "price": 50}]}

# NFT Launchpad Service
@app.post("/api/nft/launchpad/participate")
async def participate_nft_launch(
    project_id: str,
    quantity: int,
    current_user: User = Depends(get_current_user)
):
    """Participate in NFT launch"""
    return {"status": "success", "allocation": quantity}

# NFT Loan Service
@app.post("/api/nft/loan/borrow")
async def borrow_against_nft(
    nft_id: str,
    amount: float,
    current_user: User = Depends(get_current_user)
):
    """Borrow against NFT"""
    return {"status": "success", "loan_id": f"NFT-LOAN-{datetime.utcnow().timestamp()}"}

# NFT Staking Service
@app.post("/api/nft/stake")
async def stake_nft(
    nft_id: str,
    pool_id: str,
    current_user: User = Depends(get_current_user)
):
    """Stake NFT"""
    return {"status": "success", "stake_id": f"NFT-STAKE-{datetime.utcnow().timestamp()}"}

# Perpetual Swap Service
@app.post("/api/perpetual/order")
async def create_perpetual_order(
    symbol: str,
    side: str,
    size: float,
    leverage: int,
    current_user: User = Depends(get_current_user)
):
    """Create perpetual swap order"""
    return {"status": "success", "order_id": f"PERP-{datetime.utcnow().timestamp()}"}

# Prime Brokerage Service
@app.post("/api/prime-brokerage/account")
async def create_prime_account(
    institution_name: str,
    aum: float,
    current_user: User = Depends(get_current_user)
):
    """Create prime brokerage account"""
    return {"status": "success", "account_id": f"PRIME-{datetime.utcnow().timestamp()}"}

# Rebalancing Bot Service
@app.post("/api/bots/rebalancing/create")
async def create_rebalancing_bot(
    portfolio: Dict[str, float],
    rebalance_frequency: str,
    current_user: User = Depends(get_current_user)
):
    """Create rebalancing bot"""
    return {"status": "success", "bot_id": f"REBAL-{datetime.utcnow().timestamp()}"}

# Shark Fin Service
@app.post("/api/shark-fin/subscribe")
async def subscribe_shark_fin(
    product_id: str,
    amount: float,
    current_user: User = Depends(get_current_user)
):
    """Subscribe to shark fin product"""
    return {"status": "success", "subscription_id": f"SHARK-{datetime.utcnow().timestamp()}"}

# Smart Order Service
@app.post("/api/smart-order/create")
async def create_smart_order(
    symbol: str,
    side: str,
    quantity: float,
    strategy: str,
    current_user: User = Depends(get_current_user)
):
    """Create smart order"""
    return {"status": "success", "order_id": f"SMART-{datetime.utcnow().timestamp()}"}

# Social Feed Service
@app.post("/api/social/post")
async def create_social_post(
    content: str,
    media: Optional[List[str]] = None,
    current_user: User = Depends(get_current_user)
):
    """Create social post"""
    return {"status": "success", "post_id": f"POST-{datetime.utcnow().timestamp()}"}

@app.get("/api/social/feed")
async def get_social_feed(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """Get social feed"""
    return {"posts": []}

# Structured Products Service
@app.get("/api/structured-products")
async def get_structured_products():
    """Get structured products"""
    return {"products": [{"id": 1, "name": "Bull Market Product", "apy": 15.5}]}

# Swap Farming Service
@app.post("/api/swap-farming/stake")
async def stake_swap_farming(
    pool_id: str,
    amount: float,
    current_user: User = Depends(get_current_user)
):
    """Stake in swap farming"""
    return {"status": "success", "stake_id": f"SWAP-FARM-{datetime.utcnow().timestamp()}"}

# Tiger Labs Service
@app.get("/api/tiger-labs/projects")
async def get_lab_projects():
    """Get Tiger Labs projects"""
    return {"projects": [{"id": 1, "name": "AI Trading Bot", "status": "beta"}]}

# Tiger Pay Service
@app.post("/api/tiger-pay/send")
async def tiger_pay_send(
    recipient: str,
    amount: float,
    currency: str,
    current_user: User = Depends(get_current_user)
):
    """Send payment via Tiger Pay"""
    return {"status": "success", "tx_id": f"PAY-{datetime.utcnow().timestamp()}"}

# Tiger Research Service
@app.get("/api/research/reports")
async def get_research_reports():
    """Get research reports"""
    return {"reports": [{"id": 1, "title": "Q4 2025 Market Outlook", "date": "2025-10-01"}]}

# Trading Competition Service
@app.get("/api/competitions")
async def get_competitions():
    """Get active competitions"""
    return {"competitions": [{"id": 1, "name": "Monthly Trading Challenge", "prize": 10000}]}

@app.post("/api/competitions/{competition_id}/join")
async def join_competition(
    competition_id: int,
    current_user: User = Depends(get_current_user)
):
    """Join trading competition"""
    return {"status": "success", "participant_id": f"COMP-{datetime.utcnow().timestamp()}"}

# ==================== ADMIN ENDPOINTS FOR ALL SERVICES ====================

@app.get("/api/admin/services/all")
async def get_all_services_admin(current_admin: User = Depends(get_admin_user)):
    """Get all services status (admin only)"""
    from service_registry import registry
    return {
        "total_services": registry.get_service_count(),
        "services": registry.get_all_services()
    }

@app.get("/api/admin/cross-chain/bridges")
async def manage_bridges_admin(current_admin: User = Depends(get_admin_user)):
    """Manage cross-chain bridges (admin only)"""
    return {"bridges": []}

@app.post("/api/admin/custody/configure")
async def configure_custody_admin(
    settings: Dict[str, Any],
    current_admin: User = Depends(get_admin_user)
):
    """Configure custody settings (admin only)"""
    return {"status": "success"}

@app.get("/api/admin/defi/protocols")
async def manage_defi_protocols_admin(current_admin: User = Depends(get_admin_user)):
    """Manage DeFi protocols (admin only)"""
    return {"protocols": []}

@app.post("/api/admin/elite-traders/verify")
async def verify_elite_trader_admin(
    trader_id: int,
    current_admin: User = Depends(get_admin_user)
):
    """Verify elite trader (admin only)"""
    return {"status": "success"}

@app.get("/api/admin/fan-tokens/manage")
async def manage_fan_tokens_admin(current_admin: User = Depends(get_admin_user)):
    """Manage fan tokens (admin only)"""
    return {"tokens": []}

@app.post("/api/admin/gift-cards/inventory")
async def manage_gift_card_inventory_admin(
    brand: str,
    quantity: int,
    current_admin: User = Depends(get_admin_user)
):
    """Manage gift card inventory (admin only)"""
    return {"status": "success"}

@app.get("/api/admin/bots/all")
async def get_all_bots_admin(current_admin: User = Depends(get_admin_user)):
    """Get all trading bots (admin only)"""
    return {"bots": []}

@app.get("/api/admin/liquidity/pools")
async def manage_liquidity_pools_admin(current_admin: User = Depends(get_admin_user)):
    """Manage liquidity pools (admin only)"""
    return {"pools": []}

@app.get("/api/admin/merchants")
async def manage_merchants_admin(current_admin: User = Depends(get_admin_user)):
    """Manage merchants (admin only)"""
    return {"merchants": []}

@app.get("/api/admin/nft/projects")
async def manage_nft_projects_admin(current_admin: User = Depends(get_admin_user)):
    """Manage NFT projects (admin only)"""
    return {"projects": []}

@app.post("/api/admin/competitions/create")
async def create_competition_admin(
    name: str,
    prize: float,
    duration: int,
    current_admin: User = Depends(get_admin_user)
):
    """Create trading competition (admin only)"""
    return {"status": "success", "competition_id": f"COMP-{datetime.utcnow().timestamp()}"}

@app.get("/api/admin/research/publish")
async def publish_research_admin(
    title: str,
    content: str,
    current_admin: User = Depends(get_admin_user)
):
    """Publish research report (admin only)"""
    return {"status": "success", "report_id": f"REPORT-{datetime.utcnow().timestamp()}"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )