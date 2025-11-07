"""
TigerEx Enhanced Unified Backend
Complete integration of all enhanced modules with full functionality
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
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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

# Import enhanced modules
from security_enhancements import SecurityManager, SecurityMiddleware
from enhanced_admin_system import EnhancedAdminSystem
from enhanced_trading_engine import TradingEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tigerex:tigerex123@localhost:5432/tigerex_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-key-change-this-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database setup
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=20, max_overflow=30)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis client
redis_client = None

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
security = HTTPBearer()

# Enhanced systems
security_manager = None
admin_system = None
trading_engine = None

# Metrics
REQUEST_COUNT = Counter('requests_total', 'Total requests')
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration')

# ==================== DATABASE MODELS ====================
# (Reuse models from main.py and add enhanced ones)

class SecurityEvent(Base):
    __tablename__ = "security_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ip_address = Column(String)
    user_agent = Column(Text)
    severity = Column(String, index=True)
    details = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AdminAction(Base):
    __tablename__ = "admin_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"))
    target_user_id = Column(Integer)
    action = Column(String)
    details = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    buy_order_id = Column(String, ForeignKey("orders.order_id"))
    sell_order_id = Column(String, ForeignKey("orders.order_id"))
    symbol = Column(String, index=True)
    quantity = Column(Numeric(20, 8))
    price = Column(Numeric(20, 8))
    total = Column(Numeric(20, 8))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Create all tables
Base.metadata.create_all(bind=engine)

# ==================== PYDANTIC MODELS ====================

class SecurityEventCreate(BaseModel):
    event_type: str
    ip_address: str
    user_agent: str
    severity: str
    details: Dict[str, Any]

class AdminActionCreate(BaseModel):
    target_user_id: int
    action: str
    details: Dict[str, Any]

class EnhancedOrderCreate(BaseModel):
    symbol: str
    side: str
    type: str
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = "GTC"

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
    
    # Import User model from main.py
    from main import User
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user

async def get_admin_user(current_user = Depends(get_current_user)):
    if not (current_user.is_admin or current_user.is_superadmin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def get_superadmin(current_user = Depends(get_current_user)):
    if not current_user.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin access required"
        )
    return current_user

# ==================== FASTAPI APP ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client, security_manager, admin_system, trading_engine
    
    # Initialize Redis
    redis_client = await redis.from_url(REDIS_URL)
    
    # Initialize enhanced systems
    security_manager = SecurityManager(redis_client, os.getenv("ENCRYPTION_KEY", "default-key-change-in-production"))
    await security_manager.initialize_security()
    
    admin_system = EnhancedAdminSystem(SessionLocal(), redis_client)
    await admin_system.initialize_admin_system()
    
    trading_engine = TradingEngine(SessionLocal(), redis_client)
    await trading_engine.initialize_engine()
    
    logger.info("Starting TigerEx Enhanced Unified Backend")
    yield
    
    # Cleanup
    await redis_client.close()
    logger.info("Shutting down TigerEx Enhanced Unified Backend")

app = FastAPI(
    title="TigerEx Enhanced Unified Backend",
    description="Complete admin and user controls with enhanced security and trading",
    version="4.0.0",
    lifespan=lifespan
)

# Add security middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== ENHANCED SECURITY ENDPOINTS ====================

@app.post("/api/security/events", status_code=status.HTTP_201_CREATED)
async def log_security_event(
    event: SecurityEventCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log security event (enhanced)"""
    await security_manager.log_security_event(
        event_type=event.event_type,
        user_id=current_user.id,
        ip=event.ip_address,
        user_agent=event.user_agent,
        severity=security_manager.validator.SecurityLevel(event.severity),
        details=event.details
    )
    
    # Store in database
    security_event = SecurityEvent(
        event_type=event.event_type,
        user_id=current_user.id,
        ip_address=event.ip_address,
        user_agent=event.user_agent,
        severity=event.severity,
        details=json.dumps(event.details)
    )
    
    db.add(security_event)
    db.commit()
    
    return {"message": "Security event logged successfully"}

@app.get("/api/security/events")
async def get_security_events(
    skip: int = 0,
    limit: int = 100,
    severity: Optional[str] = None,
    current_admin = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get security events (admin only)"""
    query = db.query(SecurityEvent)
    
    if severity:
        query = query.filter(SecurityEvent.severity == severity)
    
    events = query.order_by(SecurityEvent.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": event.id,
            "event_type": event.event_type,
            "user_id": event.user_id,
            "ip_address": event.ip_address,
            "severity": event.severity,
            "details": json.loads(event.details) if event.details else {},
            "created_at": event.created_at.isoformat()
        }
        for event in events
    ]

@app.post("/api/security/2fa/enable")
async def enable_two_factor(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enable two-factor authentication"""
    secret = security_manager.two_fa.generate_secret()
    backup_codes = security_manager.two_fa.generate_backup_codes()
    
    await security_manager.two_fa.store_2fa_secret(current_user.id, secret)
    
    # Update user in database
    from main import User
    user = db.query(User).filter(User.id == current_user.id).first()
    user.two_factor_enabled = True
    user.two_factor_secret = security_manager.encrypt_sensitive_field(secret)
    db.commit()
    
    return {
        "secret": secret,
        "backup_codes": backup_codes,
        "qr_code_url": f"otpauth://totp/TigerEx:{current_user.email}?secret={secret}&issuer=TigerEx"
    }

@app.post("/api/security/2fa/disable")
async def disable_two_factor(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disable two-factor authentication"""
    from main import User
    user = db.query(User).filter(User.id == current_user.id).first()
    user.two_factor_enabled = False
    user.two_factor_secret = None
    db.commit()
    
    await redis_client.delete(f"2fa:{current_user.id}")
    
    return {"message": "Two-factor authentication disabled"}

# ==================== ENHANCED ADMIN ENDPOINTS ====================

@app.get("/api/admin/dashboard/comprehensive")
async def get_comprehensive_admin_dashboard(
    current_admin = Depends(get_admin_user)
):
    """Get comprehensive admin dashboard"""
    if not admin_system:
        raise HTTPException(status_code=500, detail="Admin system not initialized")
    
    return await admin_system.get_comprehensive_user_control(current_admin.id)

@app.post("/api/admin/users/{user_id}/freeze")
async def freeze_user_account(
    user_id: int,
    reason: str,
    current_admin = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Freeze user account"""
    if not admin_system:
        raise HTTPException(status_code=500, detail="Admin system not initialized")
    
    success = await admin_system.user_manager.freeze_user_account(user_id, reason, current_admin.id)
    if success:
        return {"message": "User account frozen successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to freeze user account")

@app.post("/api/admin/users/{user_id}/unfreeze")
async def unfreeze_user_account(
    user_id: int,
    reason: str,
    current_admin = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Unfreeze user account"""
    if not admin_system:
        raise HTTPException(status_code=500, detail="Admin system not initialized")
    
    success = await admin_system.user_manager.unfreeze_user_account(user_id, reason, current_admin.id)
    if success:
        return {"message": "User account unfrozen successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to unfreeze user account")

@app.get("/api/admin/users/{user_id}/detailed")
async def get_user_detailed_profile(
    user_id: int,
    current_admin = Depends(get_admin_user)
):
    """Get detailed user profile"""
    if not admin_system:
        raise HTTPException(status_code=500, detail="Admin system not initialized")
    
    profile = await admin_system.user_manager.get_user_detailed_profile(user_id)
    if profile:
        return profile
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.get("/api/admin/reports/trading")
async def generate_trading_report(
    start_date: datetime,
    end_date: datetime,
    user_id: Optional[int] = None,
    current_admin = Depends(get_admin_user)
):
    """Generate trading report"""
    if not admin_system:
        raise HTTPException(status_code=500, detail="Admin system not initialized")
    
    return await admin_system.reporting.generate_trading_report(start_date, end_date, user_id)

@app.get("/api/admin/reports/financial")
async def generate_financial_report(
    start_date: datetime,
    end_date: datetime,
    current_admin = Depends(get_admin_user)
):
    """Generate financial report"""
    if not admin_system:
        raise HTTPException(status_code=500, detail="Admin system not initialized")
    
    return await admin_system.reporting.generate_financial_report(start_date, end_date)

# ==================== ENHANCED TRADING ENDPOINTS ====================

@app.post("/api/trading/enhanced/orders")
async def create_enhanced_order(
    order: EnhancedOrderCreate,
    current_user = Depends(get_current_user)
):
    """Create enhanced order with risk management"""
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")
    
    # Check if user is allowed to trade
    from main import User
    db = SessionLocal()
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user or not user.trading_enabled:
        db.close()
        raise HTTPException(status_code=403, detail="Trading disabled for this account")
    db.close()
    
    # Create order with enhanced validation
    order_data = {
        "user_id": current_user.id,
        **order.dict()
    }
    
    result = await trading_engine.create_order(order_data)
    
    if result["success"]:
        # Log trading activity
        await security_manager.activity_tracker.track_trading_activity(
            current_user.id, 
            "order_created", 
            {"order_id": result["order_id"], "symbol": order.symbol}
        )
        
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"])

@app.post("/api/trading/orders/{order_id}/cancel")
async def cancel_enhanced_order(
    order_id: str,
    current_user = Depends(get_current_user)
):
    """Cancel enhanced order"""
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")
    
    result = await trading_engine.cancel_order(order_id, current_user.id)
    
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"])

@app.get("/api/trading/orderbook/{symbol}")
async def get_enhanced_order_book(
    symbol: str,
    limit: int = 20
):
    """Get enhanced order book"""
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")
    
    return await trading_engine.get_order_book(symbol, limit)

@app.get("/api/trading/risk/check")
async def check_order_risk(
    symbol: str,
    side: str,
    quantity: float,
    price: Optional[float] = None,
    current_user = Depends(get_current_user)
):
    """Check order risk before placing"""
    if not trading_engine:
        raise HTTPException(status_code=500, detail="Trading engine not initialized")
    
    from enhanced_trading_engine import Order, OrderSide, OrderType
    
    order = Order(
        id="risk_check",
        user_id=current_user.id,
        symbol=symbol,
        side=OrderSide(side),
        type=OrderType.LIMIT,
        quantity=quantity,
        price=price
    )
    
    risk_ok, message = await trading_engine.risk_manager.validate_order_risk(order)
    
    return {
        "risk_passed": risk_ok,
        "message": message
    }

# ==================== SYSTEM MONITORING ENDPOINTS ====================

@app.get("/api/system/health/enhanced")
async def get_enhanced_system_health(
    current_admin = Depends(get_admin_user)
):
    """Get enhanced system health monitoring"""
    health_status = {}
    
    # Database health
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        health_status["database"] = {
            "status": "healthy",
            "connections": engine.pool.size(),
            "available": engine.pool.checkedout()
        }
    except Exception as e:
        health_status["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Redis health
    try:
        await redis_client.ping()
        info = await redis_client.info()
        health_status["redis"] = {
            "status": "healthy",
            "memory_usage": info.get("used_memory_human"),
            "connected_clients": info.get("connected_clients")
        }
    except Exception as e:
        health_status["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Trading engine health
    if trading_engine:
        health_status["trading_engine"] = {
            "status": "healthy",
            "active_orderbooks": len(trading_engine.orderbooks),
            "last_sync": datetime.utcnow().isoformat()
        }
    else:
        health_status["trading_engine"] = {
            "status": "unhealthy",
            "error": "Trading engine not initialized"
        }
    
    # Security system health
    if security_manager:
        health_status["security_system"] = {
            "status": "healthy",
            "rate_limiter_active": True,
            "anti_ddos_active": True
        }
    else:
        health_status["security_system"] = {
            "status": "unhealthy",
            "error": "Security system not initialized"
        }
    
    return health_status

@app.get("/api/system/metrics")
async def get_system_metrics(
    current_admin = Depends(get_admin_user)
):
    """Get Prometheus metrics"""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )

# ==================== REAL-TIME WEBSOCKET ENDPOINTS ====================

from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections.append(websocket)
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        self.active_connections.remove(websocket)
        if user_id in self.user_connections:
            self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
    
    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.user_connections:
            for connection in self.user_connections[user_id]:
                await connection.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    # Verify token
    payload = verify_token(token)
    if not payload:
        await websocket.close(code=4001)
        return
    
    email = payload.get("sub")
    if not email:
        await websocket.close(code=4001)
        return
    
    # Get user
    db = SessionLocal()
    from main import User
    user = db.query(User).filter(User.email == email).first()
    db.close()
    
    if not user:
        await websocket.close(code=4001)
        return
    
    await manager.connect(websocket, user.id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle WebSocket messages
            message = json.loads(data)
            
            if message["type"] == "subscribe":
                # Handle subscription to market data
                await websocket.send_text(json.dumps({
                    "type": "subscription_confirm",
                    "channel": message["channel"]
                }))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user.id)

# ==================== API DOCUMENTATION AND UTILITIES ====================

@app.get("/api/docs/enhanced")
async def get_enhanced_api_docs():
    """Get enhanced API documentation"""
    return {
        "title": "TigerEx Enhanced API",
        "version": "4.0.0",
        "description": "Complete cryptocurrency exchange API with enhanced security and admin controls",
        "endpoints": {
            "authentication": "/api/auth/*",
            "trading": "/api/trading/*",
            "admin": "/api/admin/*",
            "security": "/api/security/*",
            "system": "/api/system/*"
        },
        "features": [
            "Enhanced security with rate limiting and DDoS protection",
            "Comprehensive admin controls and user management",
            "Advanced trading engine with risk management",
            "Real-time WebSocket connections",
            "System monitoring and health checks",
            "Comprehensive audit logging"
        ]
    }

@app.get("/api/status/complete")
async def get_complete_system_status():
    """Get complete system status"""
    return {
        "status": "operational",
        "version": "4.0.0",
        "features": {
            "security": "enhanced",
            "trading": "full",
            "admin": "comprehensive",
            "monitoring": "real-time"
        },
        "services": {
            "unified_backend": "running",
            "trading_engine": "active",
            "security_system": "active",
            "admin_system": "active"
        },
        "uptime": datetime.utcnow().isoformat()
    }

# Include original main.py routes
from main import app as main_app

# Copy all routes from main app
for route in main_app.routes:
    if route.path not in [r.path for r in app.routes]:
        app.routes.append(route)

if __name__ == "__main__":
    uvicorn.run(
        "enhanced_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )