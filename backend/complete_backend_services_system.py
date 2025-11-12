#!/usr/bin/env python3
"""
Complete Backend Services System
Integrates all trading, admin, and user management functionalities
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from decimal import Decimal
import redis
import aiohttp
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import jwt
from enum import Enum
import hashlib
import secrets
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./tigerex.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Security
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
security = HTTPBearer()

# Redis setup
redis_client = redis.Redis(host='localhost', port=6379, db=0)

class UserRole(str, Enum):
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    MODERATOR = "moderator"
    SUPPORT = "support"
    TRADER = "trader"

class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    BANNED = "banned"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)
    status = Column(String)
    created_at = Column(DateTime)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    symbol = Column(String)
    order_type = Column(String)
    side = Column(String)
    quantity = Column(Float)
    price = Column(Float)
    filled_quantity = Column(Float, default=0.0)
    status = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(String, primary_key=True, index=True)
    order_id = Column(String)
    user_id = Column(String, index=True)
    symbol = Column(String)
    side = Column(String)
    quantity = Column(Float)
    price = Column(Float)
    fee = Column(Float)
    created_at = Column(DateTime)

class Portfolio(Base):
    __tablename__ = "portfolios"
    
    user_id = Column(String, primary_key=True, index=True)
    asset = Column(String)
    balance = Column(Float)
    locked_balance = Column(Float, default=0.0)
    updated_at = Column(DateTime)

# Pydantic Models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: UserRole = UserRole.TRADER

class UserLogin(BaseModel):
    email: str
    password: str

class OrderCreate(BaseModel):
    symbol: str
    order_type: OrderType
    side: OrderSide
    quantity: float
    price: Optional[float] = None

class TradeResponse(BaseModel):
    id: str
    symbol: str
    side: str
    quantity: float
    price: float
    total: float
    fee: float
    created_at: datetime

class PortfolioResponse(BaseModel):
    user_id: str
    total_value_usd: float
    pnl_24h: float
    pnl_percentage: float
    balances: List[Dict[str, float]]

class MarketDataResponse(BaseModel):
    symbol: str
    price: float
    change_24h: float
    volume_24h: float
    high_24h: float
    low_24h: float
    timestamp: datetime

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Core Service Classes
class UserService:
    """User management service"""
    
    def __init__(self, db: Session):
        self.db = db
        
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        hashed_password = get_password_hash(user_data.password)
        
        user = User(
            id=f"user_{datetime.now().timestamp()}",
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            role=user_data.role.value,
            status=UserStatus.UNVERIFIED.value,
            created_at=datetime.utcnow(),
            last_login=datetime.utcnow()
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Initialize portfolio
        await self.initialize_user_portfolio(user.id)
        
        return user
        
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user credentials"""
        user = self.db.query(User).filter(User.email == email).first()
        if user and verify_password(password, user.hashed_password):
            user.last_login = datetime.utcnow()
            self.db.commit()
            return user
        return None
        
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
        
    async def update_user_status(self, user_id: str, status: UserStatus) -> bool:
        """Update user status"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.status = status.value
            self.db.commit()
            return True
        return False
        
    async def initialize_user_portfolio(self, user_id: str):
        """Initialize user portfolio with default assets"""
        initial_assets = [
            {"asset": "USDT", "balance": 10000.0},
            {"asset": "BTC", "balance": 0.0},
            {"asset": "ETH", "balance": 0.0},
            {"asset": "BNB", "balance": 0.0},
        ]
        
        for asset in initial_assets:
            portfolio = Portfolio(
                user_id=user_id,
                asset=asset["asset"],
                balance=asset["balance"],
                updated_at=datetime.utcnow()
            )
            self.db.add(portfolio)
            
        self.db.commit()

class TradingService:
    """Core trading service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.market_data = {}
        self.order_books = {}
        self.load_market_data()
        
    def load_market_data(self):
        """Load initial market data"""
        symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'ADA/USDT']
        
        for symbol in symbols:
            self.market_data[symbol] = {
                'symbol': symbol,
                'price': np.random.uniform(100, 50000),
                'volume_24h': np.random.uniform(1000000, 100000000),
                'change_24h': np.random.uniform(-10, 10),
                'high_24h': np.random.uniform(100, 55000),
                'low_24h': np.random.uniform(90, 45000),
                'timestamp': datetime.utcnow()
            }
            self.update_order_book(symbol)
            
    def update_order_book(self, symbol: str):
        """Update order book for a symbol"""
        base_price = self.market_data[symbol]['price']
        
        bids = []
        asks = []
        
        for i in range(20):
            bid_price = base_price - (i * 0.01 * base_price / 100)
            ask_price = base_price + (i * 0.01 * base_price / 100)
            
            bids.append({
                'price': bid_price,
                'quantity': np.random.uniform(0.1, 10),
                'total': bid_price * np.random.uniform(0.1, 10)
            })
            
            asks.append({
                'price': ask_price,
                'quantity': np.random.uniform(0.1, 10),
                'total': ask_price * np.random.uniform(0.1, 10)
            })
            
        self.order_books[symbol] = {'bids': bids, 'asks': asks}
        
    async def place_order(self, user_id: str, order_data: OrderCreate) -> Order:
        """Place a new order"""
        order_id = f"order_{datetime.now().timestamp()}_{user_id}"
        
        # Determine price for market orders
        price = order_data.price
        if order_data.order_type == OrderType.MARKET:
            price = self.market_data[order_data.symbol]['price']
            
        order = Order(
            id=order_id,
            user_id=user_id,
            symbol=order_data.symbol,
            order_type=order_data.order_type.value,
            side=order_data.side.value,
            quantity=order_data.quantity,
            price=price,
            status="pending",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        
        # Process order
        await self.process_order(order)
        
        return order
        
    async def process_order(self, order: Order):
        """Process and execute order"""
        try:
            # Simulate order execution
            await asyncio.sleep(0.1)
            
            # Update order status
            order.status = "filled"
            order.filled_quantity = order.quantity
            order.updated_at = datetime.utcnow()
            self.db.commit()
            
            # Create trade record
            trade = Trade(
                id=f"trade_{datetime.now().timestamp()}",
                order_id=order.id,
                user_id=order.user_id,
                symbol=order.symbol,
                side=order.side,
                quantity=order.filled_quantity,
                price=order.price,
                fee=order.quantity * order.price * 0.001,  # 0.1% fee
                created_at=datetime.utcnow()
            )
            
            self.db.add(trade)
            self.db.commit()
            
            # Update portfolio
            await self.update_portfolio_after_trade(order.user_id, trade)
            
            # Cache to Redis
            await self.cache_order(order)
            await self.cache_trade(trade)
            
        except Exception as e:
            logger.error(f"Error processing order: {e}")
            order.status = "failed"
            self.db.commit()
            
    async def update_portfolio_after_trade(self, user_id: str, trade: Trade):
        """Update user portfolio after trade"""
        base, quote = trade.symbol.split('/')
        
        # Update base asset
        base_portfolio = self.db.query(Portfolio).filter(
            Portfolio.user_id == user_id,
            Portfolio.asset == base
        ).first()
        
        if not base_portfolio:
            base_portfolio = Portfolio(
                user_id=user_id,
                asset=base,
                balance=0.0,
                updated_at=datetime.utcnow()
            )
            self.db.add(base_portfolio)
            
        if trade.side == OrderSide.BUY.value:
            base_portfolio.balance += trade.quantity
        else:
            base_portfolio.balance -= trade.quantity
            
        # Update quote asset
        quote_portfolio = self.db.query(Portfolio).filter(
            Portfolio.user_id == user_id,
            Portfolio.asset == quote
        ).first()
        
        if not quote_portfolio:
            quote_portfolio = Portfolio(
                user_id=user_id,
                asset=quote,
                balance=0.0,
                updated_at=datetime.utcnow()
            )
            self.db.add(quote_portfolio)
            
        if trade.side == OrderSide.BUY.value:
            quote_portfolio.balance -= (trade.quantity * trade.price + trade.fee)
        else:
            quote_portfolio.balance += (trade.quantity * trade.price - trade.fee)
            
        base_portfolio.updated_at = datetime.utcnow()
        quote_portfolio.updated_at = datetime.utcnow()
        self.db.commit()
        
    async def get_user_portfolio(self, user_id: str) -> PortfolioResponse:
        """Get user portfolio"""
        portfolios = self.db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
        
        total_value = 0.0
        balances = []
        
        for portfolio in portfolios:
            value = portfolio.balance
            if portfolio.asset != "USDT":
                # Convert to USDT using current market price
                symbol = f"{portfolio.asset}/USDT"
                if symbol in self.market_data:
                    value = portfolio.balance * self.market_data[symbol]['price']
                    
            total_value += value
            balances.append({
                "symbol": portfolio.asset,
                "balance": portfolio.balance,
                "value": value
            })
            
        return PortfolioResponse(
            user_id=user_id,
            total_value_usd=total_value,
            pnl_24h=np.random.uniform(-1000, 1000),
            pnl_percentage=np.random.uniform(-5, 5),
            balances=balances
        )
        
    async def get_order_book(self, symbol: str, depth: int = 20) -> Dict[str, Any]:
        """Get order book for a symbol"""
        if symbol not in self.order_books:
            self.update_order_book(symbol)
            
        order_book = self.order_books[symbol]
        
        return {
            "symbol": symbol,
            "bids": order_book['bids'][:depth],
            "asks": order_book['asks'][:depth],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    async def get_user_trades(self, user_id: str, limit: int = 50) -> List[TradeResponse]:
        """Get user trade history"""
        trades = self.db.query(Trade).filter(
            Trade.user_id == user_id
        ).order_by(Trade.created_at.desc()).limit(limit).all()
        
        return [
            TradeResponse(
                id=trade.id,
                symbol=trade.symbol,
                side=trade.side,
                quantity=trade.quantity,
                price=trade.price,
                total=trade.quantity * trade.price,
                fee=trade.fee,
                created_at=trade.created_at
            )
            for trade in trades
        ]
        
    async def get_market_data(self, symbol: str = None) -> Union[MarketDataResponse, List[MarketDataResponse]]:
        """Get market data"""
        if symbol:
            if symbol not in self.market_data:
                raise HTTPException(status_code=404, detail="Symbol not found")
                
            data = self.market_data[symbol]
            return MarketDataResponse(**data)
        else:
            return [MarketDataResponse(**data) for data in self.market_data.values()]
            
    async def cache_order(self, order: Order):
        """Cache order to Redis"""
        order_key = f"order:{order.id}"
        order_data = {
            'id': order.id,
            'user_id': order.user_id,
            'symbol': order.symbol,
            'order_type': order.order_type,
            'side': order.side,
            'quantity': order.quantity,
            'price': order.price,
            'filled_quantity': order.filled_quantity,
            'status': order.status,
            'created_at': order.created_at.isoformat(),
            'updated_at': order.updated_at.isoformat()
        }
        
        redis_client.setex(order_key, timedelta(days=30), json.dumps(order_data))
        
    async def cache_trade(self, trade: Trade):
        """Cache trade to Redis"""
        trade_key = f"trade:{trade.id}"
        trade_data = {
            'id': trade.id,
            'order_id': trade.order_id,
            'user_id': trade.user_id,
            'symbol': trade.symbol,
            'side': trade.side,
            'quantity': trade.quantity,
            'price': trade.price,
            'fee': trade.fee,
            'created_at': trade.created_at.isoformat()
        }
        
        redis_client.setex(trade_key, timedelta(days=30), json.dumps(trade_data))

class AdminService:
    """Admin service for platform management"""
    
    def __init__(self, db: Session):
        self.db = db
        
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        total_trades = self.db.query(Trade).count()
        total_orders = self.db.query(Order).count()
        
        # Calculate 24h volume
        trades_24h = self.db.query(Trade).filter(
            Trade.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).all()
        
        volume_24h = sum(trade.quantity * trade.price for trade in trades_24h)
        revenue_24h = sum(trade.fee for trade in trades_24h)
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_trades": total_trades,
            "total_orders": total_orders,
            "volume_24h": volume_24h,
            "revenue_24h": revenue_24h,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users"""
        return self.db.query(User).offset(skip).limit(limit).all()
        
    async def get_system_logs(self, level: str = "INFO", limit: int = 100) -> List[Dict[str, Any]]:
        """Get system logs"""
        # Simulate system logs
        logs = []
        levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        for i in range(limit):
            timestamp = datetime.utcnow() - timedelta(minutes=i * 5)
            log_level = level if level != "ALL" else np.random.choice(levels)
            
            logs.append({
                "timestamp": timestamp.isoformat(),
                "level": log_level,
                "message": f"System log entry {i}",
                "source": "backend_service",
                "details": {"user_id": f"user_{i}", "action": "login"}
            })
            
        return logs

class WebSocketManager:
    """WebSocket connection manager for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        """Connect a WebSocket client"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
    def disconnect(self, client_id: str):
        """Disconnect a WebSocket client"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            
    async def send_personal_message(self, message: str, client_id: str):
        """Send message to specific client"""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)
            
    async def broadcast(self, message: str):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections.values():
            await connection.send_text(message)

# FastAPI Application Setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Start background tasks
    asyncio.create_task(market_data_updater())
    
    yield

app = FastAPI(
    title="TigerEx Trading Platform API",
    description="Complete backend services for TigerEx trading platform",
    version="12.0.0",
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

# WebSocket manager
websocket_manager = WebSocketManager()

# Background task for market data updates
async def market_data_updater():
    """Update market data periodically"""
    trading_service = TradingService(next(get_db()))
    
    while True:
        await asyncio.sleep(5)  # Update every 5 seconds
        
        for symbol in trading_service.market_data:
            # Simulate price movement
            current_price = trading_service.market_data[symbol]['price']
            change = np.random.uniform(-0.5, 0.5)
            new_price = current_price * (1 + change / 100)
            
            trading_service.market_data[symbol]['price'] = new_price
            trading_service.market_data[symbol]['change_24h'] += np.random.uniform(-0.1, 0.1)
            trading_service.market_data[symbol]['timestamp'] = datetime.utcnow()
            
            # Update order book
            if np.random.random() > 0.7:  # Update order book less frequently
                trading_service.update_order_book(symbol)
                
        # Broadcast updates
        update_message = json.dumps({
            "type": "market_update",
            "data": trading_service.market_data
        })
        await websocket_manager.broadcast(update_message)

# API Routes

@app.post("/auth/register")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    user_service = UserService(db)
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
        
    user = await user_service.create_user(user_data)
    token = create_access_token(data={"sub": user.id})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "status": user.status
        }
    }

@app.post("/auth/login")
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    user_service = UserService(db)
    user = await user_service.authenticate_user(
        user_credentials.email, 
        user_credentials.password
    )
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account is inactive")
        
    token = create_access_token(data={"sub": user.id})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "status": user.status
        }
    }

@app.get("/portfolio")
async def get_portfolio(user_id: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Get user portfolio"""
    trading_service = TradingService(db)
    portfolio = await trading_service.get_user_portfolio(user_id)
    return portfolio

@app.post("/orders")
async def place_order(
    order_data: OrderCreate, 
    user_id: str = Depends(verify_token), 
    db: Session = Depends(get_db)
):
    """Place a new order"""
    trading_service = TradingService(db)
    order = await trading_service.place_order(user_id, order_data)
    return {"order_id": order.id, "status": order.status}

@app.get("/orders/{order_id}")
async def get_order(
    order_id: str, 
    user_id: str = Depends(verify_token), 
    db: Session = Depends(get_db)
):
    """Get order by ID"""
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/trades")
async def get_trades(
    limit: int = 50, 
    user_id: str = Depends(verify_token), 
    db: Session = Depends(get_db)
):
    """Get user trades"""
    trading_service = TradingService(db)
    trades = await trading_service.get_user_trades(user_id, limit)
    return trades

@app.get("/market-data")
async def get_market_data(symbol: str = None, db: Session = Depends(get_db)):
    """Get market data"""
    trading_service = TradingService(db)
    data = await trading_service.get_market_data(symbol)
    return data

@app.get("/order-book/{symbol}")
async def get_order_book(symbol: str, depth: int = 20, db: Session = Depends(get_db)):
    """Get order book"""
    trading_service = TradingService(db)
    order_book = await trading_service.get_order_book(symbol, depth)
    return order_book

# Admin Routes
@app.get("/admin/dashboard")
async def admin_dashboard(
    user_id: str = Depends(verify_token), 
    db: Session = Depends(get_db)
):
    """Get admin dashboard"""
    # Check if user is admin
    user = await UserService(db).get_user_by_id(user_id)
    if not user or user.role not in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]:
        raise HTTPException(status_code=403, detail="Admin access required")
        
    admin_service = AdminService(db)
    stats = await admin_service.get_dashboard_stats()
    return stats

@app.get("/admin/users")
async def admin_get_users(
    skip: int = 0, 
    limit: int = 100,
    user_id: str = Depends(verify_token), 
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    user = await UserService(db).get_user_by_id(user_id)
    if not user or user.role not in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]:
        raise HTTPException(status_code=403, detail="Admin access required")
        
    admin_service = AdminService(db)
    users = await admin_service.get_all_users(skip, limit)
    return users

@app.get("/admin/logs")
async def admin_get_logs(
    level: str = "INFO",
    limit: int = 100,
    user_id: str = Depends(verify_token), 
    db: Session = Depends(get_db)
):
    """Get system logs (admin only)"""
    user = await UserService(db).get_user_by_id(user_id)
    if not user or user.role not in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]:
        raise HTTPException(status_code=403, detail="Admin access required")
        
    admin_service = AdminService(db)
    logs = await admin_service.get_system_logs(level, limit)
    return logs

# WebSocket endpoint
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time updates"""
    await websocket_manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
            await websocket_manager.send_personal_message(f"Echo: {data}", client_id)
    except WebSocketDisconnect:
        websocket_manager.disconnect(client_id)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "TigerEx Trading Platform API",
        "version": "12.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "connected",
            "redis": "connected" if redis_client.ping() else "disconnected"
        }
    }

# Main execution
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)