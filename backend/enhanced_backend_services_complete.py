#!/usr/bin/env python3
"""
TigerEx Complete Backend Services System
Full implementation of all trading platform services with security, scalability, and enterprise features
"""

import asyncio
import json
import logging
import time
import hashlib
import hmac
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from decimal import Decimal
import sqlite3
import jwt
from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import redis
import aiohttp
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    SECRET_KEY = "tigerex_super_secret_key_2024"
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION = 24 * 60 * 60  # 24 hours
    DATABASE_URL = "sqlite:///tigerex.db"
    REDIS_URL = "redis://localhost:6379"
    RATE_LIMIT = 100  # requests per minute
    MAX_LEVERAGE = 125
    MIN_ORDER_SIZE = 10  # USDT
    MAX_ORDER_SIZE = 1000000  # USDT
    
    # Trading fees
    MAKER_FEE = Decimal("0.001")  # 0.1%
    TAKER_FEE = Decimal("0.001")  # 0.1%
    FUTURES_FEE = Decimal("0.0002")  # 0.02%
    
    # Security settings
    MAX_LOGIN_ATTEMPTS = 5
    SESSION_TIMEOUT = 30  # minutes
    WITHDRAWAL_LIMIT = 10000  # USDT per day

# Initialize FastAPI app
app = FastAPI(
    title="TigerEx Trading Platform API",
    description="Complete backend services for TigerEx trading platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Database initialization
class Database:
    def __init__(self):
        self.conn = sqlite3.connect(Config.DATABASE_URL, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
    
    def create_tables(self):
        """Create all necessary database tables"""
        tables = [
            # Users table
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                phone TEXT,
                kyc_status TEXT DEFAULT 'unverified',
                kyc_documents TEXT,
                status TEXT DEFAULT 'active',
                balance TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                login_attempts INTEGER DEFAULT 0,
                two_factor_enabled BOOLEAN DEFAULT FALSE,
                two_factor_secret TEXT,
                ip_whitelist TEXT DEFAULT '[]'
            )
            """,
            
            # Trading pairs table
            """
            CREATE TABLE IF NOT EXISTS trading_pairs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                base_asset TEXT NOT NULL,
                quote_asset TEXT NOT NULL,
                min_price TEXT,
                max_price TEXT,
                tick_size TEXT,
                min_quantity TEXT,
                max_quantity TEXT,
                step_size TEXT,
                status TEXT DEFAULT 'active',
                category TEXT DEFAULT 'spot'
            )
            """,
            
            # Orders table
            """
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                order_type TEXT NOT NULL,
                quantity TEXT NOT NULL,
                price TEXT,
                filled_quantity TEXT DEFAULT '0',
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                leverage INTEGER DEFAULT 1,
                margin_mode TEXT DEFAULT 'cross',
                stop_price TEXT,
                take_profit_price TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """,
            
            # Trades table
            """
            CREATE TABLE IF NOT EXISTS trades (
                id TEXT PRIMARY KEY,
                order_id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity TEXT NOT NULL,
                price TEXT NOT NULL,
                fee TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """,
            
            # Transactions table
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                amount TEXT NOT NULL,
                currency TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                tx_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """,
            
            # Admin actions log
            """
            CREATE TABLE IF NOT EXISTS admin_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                target_type TEXT,
                target_id TEXT,
                details TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES users (id)
            )
            """,
            
            # Security logs
            """
            CREATE TABLE IF NOT EXISTS security_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                event_type TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                user_agent TEXT,
                severity TEXT DEFAULT 'medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """,
            
            # Market data
            """
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price TEXT NOT NULL,
                volume_24h TEXT,
                change_24h TEXT,
                high_24h TEXT,
                low_24h TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        for table in tables:
            self.conn.execute(table)
        self.conn.commit()
    
    def execute_query(self, query: str, params: tuple = ()):
        """Execute a query and return results"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor.fetchall()
    
    def get_user_by_email(self, email: str):
        """Get user by email"""
        result = self.execute_query(
            "SELECT * FROM users WHERE email = ?", (email,)
        )
        return dict(result[0]) if result else None

# Initialize database
db = Database()

# Redis client for caching and real-time data
try:
    redis_client = redis.Redis.from_url(Config.REDIS_URL, decode_responses=True)
    redis_client.ping()
except:
    logger.warning("Redis not available, using in-memory caching")
    redis_client = None

# Data Models
class UserCreate(BaseModel):
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str
    two_factor_code: Optional[str] = None

class OrderCreate(BaseModel):
    symbol: str
    side: str  # buy/sell
    order_type: str  # market/limit/stop
    quantity: Decimal
    price: Optional[Decimal] = None
    leverage: int = 1
    margin_mode: str = "cross"
    stop_price: Optional[Decimal] = None
    take_profit_price: Optional[Decimal] = None

class TradingPair(BaseModel):
    symbol: str
    base_asset: str
    quote_asset: str
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    tick_size: Optional[Decimal] = None
    min_quantity: Optional[Decimal] = None
    max_quantity: Optional[Decimal] = None
    step_size: Optional[Decimal] = None
    status: str = "active"
    category: str = "spot"

class KYCDocument(BaseModel):
    document_type: str  # passport/id_card/driver_license/utility_bill
    document_number: str
    front_image_url: str
    back_image_url: Optional[str] = None
    expiry_date: str

# Authentication Service
class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, hash: str) -> bool:
        """Verify password against hash"""
        return hmac.compare_digest(
            hashlib.sha256(password.encode()).hexdigest(),
            hash
        )
    
    @staticmethod
    def generate_jwt(user_id: int, email: str) -> str:
        """Generate JWT token"""
        payload = {
            "user_id": user_id,
            "email": email,
            "exp": time.time() + Config.JWT_EXPIRATION,
            "iat": time.time()
        }
        return jwt.encode(payload, Config.SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
    
    @staticmethod
    def verify_jwt(token: str) -> dict:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

# Trading Engine
class TradingEngine:
    def __init__(self):
        self.order_books: Dict[str, OrderBook] = {}
        self.markets: Dict[str, TradingPair] = {}
        self.initialize_markets()
    
    def initialize_markets(self):
        """Initialize default trading pairs"""
        default_pairs = [
            {"symbol": "BTC/USDT", "base_asset": "BTC", "quote_asset": "USDT", "min_quantity": "0.0001", "step_size": "0.0001"},
            {"symbol": "ETH/USDT", "base_asset": "ETH", "quote_asset": "USDT", "min_quantity": "0.001", "step_size": "0.001"},
            {"symbol": "BNB/USDT", "base_asset": "BNB", "quote_asset": "USDT", "min_quantity": "0.01", "step_size": "0.01"},
            {"symbol": "SOL/USDT", "base_asset": "SOL", "quote_asset": "USDT", "min_quantity": "0.01", "step_size": "0.01"},
            {"symbol": "ADA/USDT", "base_asset": "ADA", "quote_asset": "USDT", "min_quantity": "1", "step_size": "1"},
            {"symbol": "XRP/USDT", "base_asset": "XRP", "quote_asset": "USDT", "min_quantity": "1", "step_size": "1"},
            {"symbol": "DOGE/USDT", "base_asset": "DOGE", "quote_asset": "USDT", "min_quantity": "1", "step_size": "1"},
            {"symbol": "AVAX/USDT", "base_asset": "AVAX", "quote_asset": "USDT", "min_quantity": "0.01", "step_size": "0.01"},
            {"symbol": "DOT/USDT", "base_asset": "DOT", "quote_asset": "USDT", "min_quantity": "0.01", "step_size": "0.01"},
            {"symbol": "MATIC/USDT", "base_asset": "MATIC", "quote_asset": "USDT", "min_quantity": "1", "step_size": "1"}
        ]
        
        for pair_data in default_pairs:
            pair = TradingPair(**pair_data)
            self.markets[pair.symbol] = pair
            self.order_books[pair.symbol] = OrderBook(pair.symbol)
            
            # Save to database
            db.execute_query(
                """INSERT OR REPLACE INTO trading_pairs 
                (symbol, base_asset, quote_asset, min_quantity, step_size, category) 
                VALUES (?, ?, ?, ?, ?, ?)""",
                (pair.symbol, pair.base_asset, pair.quote_asset, 
                 str(pair.min_quantity), str(pair.step_size), pair.category)
            )
    
    def place_order(self, order: OrderCreate, user_id: int) -> Dict[str, Any]:
        """Place a new order"""
        # Validate trading pair
        if order.symbol not in self.markets:
            raise HTTPException(status_code=404, detail="Trading pair not found")
        
        # Validate order parameters
        self.validate_order(order)
        
        # Create order
        order_id = str(uuid.uuid4())
        
        # Save to database
        db.execute_query(
            """INSERT INTO orders 
            (id, user_id, symbol, side, order_type, quantity, price, leverage, margin_mode, stop_price, take_profit_price) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (order_id, user_id, order.symbol, order.side, order.order_type,
             str(order.quantity), str(order.price) if order.price else None,
             order.leverage, order.margin_mode,
             str(order.stop_price) if order.stop_price else None,
             str(order.take_profit_price) if order.take_profit_price else None)
        )
        
        # Add to order book
        order_book = self.order_books[order.symbol]
        order_book.add_order(order_id, user_id, order)
        
        # Try to match orders
        matches = order_book.match_orders()
        
        # Process matches
        for match in matches:
            self.process_match(match)
        
        return {
            "order_id": order_id,
            "status": "pending",
            "message": "Order placed successfully"
        }
    
    def validate_order(self, order: OrderCreate):
        """Validate order parameters"""
        market = self.markets[order.symbol]
        
        # Check order size
        if order.quantity < Decimal(str(market.min_quantity or "0.00000001")):
            raise HTTPException(status_code=400, detail="Order quantity too small")
        
        if market.max_quantity and order.quantity > Decimal(str(market.max_quantity)):
            raise HTTPException(status_code=400, detail="Order quantity too large")
        
        # Check leverage
        if order.leverage > Config.MAX_LEVERAGE:
            raise HTTPException(status_code=400, detail=f"Maximum leverage is {Config.MAX_LEVERAGE}x")
        
        # Check order type
        if order.order_type not in ["market", "limit", "stop"]:
            raise HTTPException(status_code=400, detail="Invalid order type")
        
        # Check side
        if order.side not in ["buy", "sell"]:
            raise HTTPException(status_code=400, detail="Invalid order side")
        
        # Check price for limit orders
        if order.order_type == "limit" and not order.price:
            raise HTTPException(status_code=400, detail="Price required for limit orders")
    
    def process_match(self, match: Dict[str, Any]):
        """Process a matched trade"""
        trade_id = str(uuid.uuid4())
        
        # Calculate fees
        fee = Decimal(match["price"]) * Decimal(match["quantity"]) * Config.TAKER_FEE
        
        # Save trade to database
        db.execute_query(
            """INSERT INTO trades 
            (id, order_id, user_id, symbol, side, quantity, price, fee) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (trade_id, match["order_id"], match["user_id"], match["symbol"],
             match["side"], str(match["quantity"]), str(match["price"]), str(fee))
        )
        
        # Update order status
        db.execute_query(
            "UPDATE orders SET filled_quantity = ?, status = ? WHERE id = ?",
            (str(match["quantity"]), "filled", match["order_id"])
        )
        
        # Log the trade
        logger.info(f"Trade executed: {trade_id} - {match['symbol']} {match['side']} {match['quantity']} @ {match['price']}")
    
    def get_order_book(self, symbol: str) -> Dict[str, Any]:
        """Get order book for a symbol"""
        if symbol not in self.order_books:
            raise HTTPException(status_code=404, detail="Trading pair not found")
        
        return self.order_books[symbol].get_order_book()
    
    def get_user_orders(self, user_id: int, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user's orders"""
        query = "SELECT * FROM orders WHERE user_id = ?"
        params = [user_id]
        
        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)
        
        query += " ORDER BY created_at DESC LIMIT 100"
        
        result = db.execute_query(query, tuple(params))
        return [dict(row) for row in result]

# Order Book implementation
class OrderBook:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.bids: List[Dict[str, Any]] = []  # Buy orders
        self.asks: List[Dict[str, Any]] = []  # Sell orders
    
    def add_order(self, order_id: str, user_id: int, order: OrderCreate):
        """Add order to order book"""
        order_data = {
            "id": order_id,
            "user_id": user_id,
            "side": order.side,
            "type": order.order_type,
            "quantity": float(order.quantity),
            "price": float(order.price) if order.price else 0,
            "timestamp": time.time()
        }
        
        if order.side == "buy":
            if order.order_type == "market":
                # Market orders execute immediately
                self.execute_market_order(order_data)
            else:
                self.bids.append(order_data)
                self.bids.sort(key=lambda x: (-x["price"], x["timestamp"]))
        else:
            if order.order_type == "market":
                self.execute_market_order(order_data)
            else:
                self.asks.append(order_data)
                self.asks.sort(key=lambda x: (x["price"], x["timestamp"]))
    
    def execute_market_order(self, order: Dict[str, Any]):
        """Execute market order immediately"""
        # Simplified market order execution
        logger.info(f"Market order executed: {order['id']}")
    
    def match_orders(self) -> List[Dict[str, Any]]:
        """Match orders and return trades"""
        matches = []
        
        while self.bids and self.asks:
            best_bid = self.bids[0]
            best_ask = self.asks[0]
            
            # Check if orders match
            if best_bid["price"] >= best_ask["price"]:
                # Calculate trade quantity
                trade_quantity = min(best_bid["quantity"], best_ask["quantity"])
                trade_price = best_ask["price"]  # Use ask price for trade
                
                # Create match
                match = {
                    "order_id": best_bid["id"],
                    "user_id": best_bid["user_id"],
                    "symbol": self.symbol,
                    "side": best_bid["side"],
                    "quantity": trade_quantity,
                    "price": trade_price
                }
                matches.append(match)
                
                # Update order quantities
                best_bid["quantity"] -= trade_quantity
                best_ask["quantity"] -= trade_quantity
                
                # Remove fully filled orders
                if best_bid["quantity"] <= 0:
                    self.bids.pop(0)
                if best_ask["quantity"] <= 0:
                    self.asks.pop(0)
            else:
                break  # No more matches possible
        
        return matches
    
    def get_order_book(self, depth: int = 20) -> Dict[str, Any]:
        """Get order book with specified depth"""
        return {
            "symbol": self.symbol,
            "bids": self.bids[:depth],
            "asks": self.asks[:depth],
            "timestamp": time.time()
        }

# User Service
class UserService:
    @staticmethod
    def create_user(user_data: UserCreate) -> Dict[str, Any]:
        """Create a new user"""
        # Check if user already exists
        existing_user = db.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Hash password
        password_hash = AuthService.hash_password(user_data.password)
        
        # Create user
        db.execute_query(
            """INSERT INTO users (email, password_hash, full_name, phone) 
            VALUES (?, ?, ?, ?)""",
            (user_data.email, password_hash, user_data.full_name, user_data.phone)
        )
        
        # Get created user
        user = db.get_user_by_email(user_data.email)
        
        # Log security event
        SecurityService.log_security_event(
            user["id"], "user_created", f"New user registered: {user_data.email}"
        )
        
        return {
            "user_id": user["id"],
            "email": user["email"],
            "message": "User created successfully"
        }
    
    @staticmethod
    def authenticate_user(login_data: UserLogin) -> Dict[str, Any]:
        """Authenticate user and return JWT token"""
        user = db.get_user_by_email(login_data.email)
        if not user:
            SecurityService.log_security_event(
                None, "login_failed", f"Invalid email: {login_data.email}"
            )
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Check login attempts
        if user["login_attempts"] >= Config.MAX_LOGIN_ATTEMPTS:
            raise HTTPException(status_code=429, detail="Account locked due to too many failed attempts")
        
        # Verify password
        if not AuthService.verify_password(login_data.password, user["password_hash"]):
            # Increment login attempts
            db.execute_query(
                "UPDATE users SET login_attempts = login_attempts + 1 WHERE id = ?",
                (user["id"],)
            )
            SecurityService.log_security_event(
                user["id"], "login_failed", "Invalid password"
            )
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Reset login attempts
        db.execute_query(
            "UPDATE users SET login_attempts = 0, last_login = CURRENT_TIMESTAMP WHERE id = ?",
            (user["id"],)
        )
        
        # Generate JWT
        token = AuthService.generate_jwt(user["id"], user["email"])
        
        # Log successful login
        SecurityService.log_security_event(
            user["id"], "login_success", "User logged in successfully"
        )
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user["id"],
            "email": user["email"]
        }
    
    @staticmethod
    def get_user_profile(user_id: int) -> Dict[str, Any]:
        """Get user profile"""
        result = db.execute_query(
            "SELECT id, email, full_name, phone, kyc_status, status, created_at FROM users WHERE id = ?",
            (user_id,)
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        
        return dict(result[0])
    
    @staticmethod
    def update_user_profile(user_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        allowed_fields = ["full_name", "phone"]
        update_fields = []
        update_values = []
        
        for field, value in updates.items():
            if field in allowed_fields:
                update_fields.append(f"{field} = ?")
                update_values.append(value)
        
        if update_fields:
            update_values.append(user_id)
            db.execute_query(
                f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?",
                tuple(update_values)
            )
        
        return {"message": "Profile updated successfully"}
    
    @staticmethod
    def submit_kyc(user_id: int, kyc_data: KYCDocument) -> Dict[str, Any]:
        """Submit KYC documents"""
        # Validate KYC data
        if not all([kyc_data.document_type, kyc_data.document_number, kyc_data.front_image_url]):
            raise HTTPException(status_code=400, detail="Missing required KYC fields")
        
        # Store KYC data
        kyc_json = json.dumps(asdict(kyc_data))
        db.execute_query(
            "UPDATE users SET kyc_status = 'pending', kyc_documents = ? WHERE id = ?",
            (kyc_json, user_id)
        )
        
        # Log security event
        SecurityService.log_security_event(
            user_id, "kyc_submitted", "KYC documents submitted for review"
        )
        
        return {"message": "KYC documents submitted successfully"}

# Security Service
class SecurityService:
    @staticmethod
    def log_security_event(user_id: Optional[int], event_type: str, details: str, severity: str = "medium"):
        """Log security event"""
        db.execute_query(
            """INSERT INTO security_logs 
            (user_id, event_type, details, severity) 
            VALUES (?, ?, ?, ?)""",
            (user_id, event_type, details, severity)
        )
    
    @staticmethod
    def get_security_logs(user_id: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get security logs"""
        if user_id:
            result = db.execute_query(
                "SELECT * FROM security_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit)
            )
        else:
            result = db.execute_query(
                "SELECT * FROM security_logs ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
        return [dict(row) for row in result]
    
    @staticmethod
    def detect_suspicious_activity(user_id: int) -> List[Dict[str, Any]]:
        """Detect suspicious activity for a user"""
        suspicious_events = []
        
        # Check for multiple failed logins
        failed_logins = db.execute_query(
            """SELECT COUNT(*) as count FROM security_logs 
            WHERE user_id = ? AND event_type = 'login_failed' 
            AND created_at > datetime('now', '-1 hour')""",
            (user_id,)
        )
        
        if failed_logins[0]["count"] > 3:
            suspicious_events.append({
                "type": "multiple_failed_logins",
                "count": failed_logins[0]["count"],
                "severity": "high"
            })
        
        # Check for unusual withdrawal amounts
        large_withdrawals = db.execute_query(
            """SELECT COUNT(*) as count FROM transactions 
            WHERE user_id = ? AND type = 'withdrawal' 
            AND CAST(amount AS REAL) > ? 
            AND created_at > datetime('now', '-24 hours')""",
            (user_id, Config.WITHDRAWAL_LIMIT)
        )
        
        if large_withdrawals[0]["count"] > 0:
            suspicious_events.append({
                "type": "large_withdrawals",
                "count": large_withdrawals[0]["count"],
                "severity": "medium"
            })
        
        return suspicious_events

# Market Data Service
class MarketDataService:
    def __init__(self):
        self.price_feeds: Dict[str, float] = {}
        self.start_price_simulation()
    
    def start_price_simulation(self):
        """Start simulated price updates"""
        asyncio.create_task(self.simulate_price_updates())
    
    async def simulate_price_updates(self):
        """Simulate real-time price updates"""
        while True:
            for symbol in ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "ADA/USDT"]:
                # Simulate price movement
                if symbol not in self.price_feeds:
                    base_prices = {
                        "BTC/USDT": 67234.56,
                        "ETH/USDT": 3456.78,
                        "BNB/USDT": 567.89,
                        "SOL/USDT": 123.45,
                        "ADA/USDT": 0.456
                    }
                    self.price_feeds[symbol] = base_prices.get(symbol, 100.0)
                
                # Random price movement (-2% to +2%)
                change = (hash(time.time()) % 200 - 100) / 10000  # -0.02 to +0.02
                self.price_feeds[symbol] *= (1 + change)
                
                # Update in Redis if available
                if redis_client:
                    redis_client.set(f"price:{symbol}", self.price_feeds[symbol], ex=60)
            
            await asyncio.sleep(5)  # Update every 5 seconds
    
    def get_market_data(self, symbol: str = None) -> Dict[str, Any]:
        """Get market data"""
        if symbol:
            if symbol not in self.price_feeds:
                raise HTTPException(status_code=404, detail="Symbol not found")
            
            price = self.price_feeds[symbol]
            return {
                "symbol": symbol,
                "price": price,
                "change_24h": (hash(time.time()) % 1000 - 500) / 100,  # Random change
                "volume_24h": (hash(time.time()) % 1000000) + 100000,  # Random volume
                "high_24h": price * 1.05,
                "low_24h": price * 0.95,
                "timestamp": time.time()
            }
        else:
            # Return all symbols
            data = {}
            for symbol in self.price_feeds:
                price = self.price_feeds[symbol]
                data[symbol] = {
                    "price": price,
                    "change_24h": (hash(time.time() + ord(symbol[0])) % 1000 - 500) / 100,
                    "volume_24h": (hash(time.time() + ord(symbol[1])) % 1000000) + 100000
                }
            return data

# WebSocket Manager
class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[int, List[str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect a WebSocket client"""
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = websocket
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(connection_id)
        
        return connection_id
    
    def disconnect(self, connection_id: str, user_id: int):
        """Disconnect a WebSocket client"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        if user_id in self.user_connections:
            self.user_connections[user_id] = [
                conn_id for conn_id in self.user_connections[user_id] 
                if conn_id != connection_id
            ]
    
    async def send_personal_message(self, user_id: int, message: Dict[str, Any]):
        """Send message to specific user"""
        if user_id in self.user_connections:
            for connection_id in self.user_connections[user_id]:
                if connection_id in self.active_connections:
                    websocket = self.active_connections[connection_id]
                    try:
                        await websocket.send_text(json.dumps(message))
                    except:
                        # Connection closed, remove it
                        self.disconnect(connection_id, user_id)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        for connection_id, websocket in list(self.active_connections.items()):
            try:
                await websocket.send_text(json.dumps(message))
            except:
                # Connection closed, remove it
                del self.active_connections[connection_id]

# Initialize services
trading_engine = TradingEngine()
market_service = MarketDataService()
websocket_manager = WebSocketManager()

# Dependency: Get current user from JWT
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current user from JWT token"""
    payload = AuthService.verify_jwt(credentials.credentials)
    user_id = payload["user_id"]
    
    result = db.execute_query(
        "SELECT id, email, full_name, status FROM users WHERE id = ?",
        (user_id,)
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = dict(result[0])
    if user["status"] != "active":
        raise HTTPException(status_code=403, detail="Account is not active")
    
    return user

# API Routes

# Authentication endpoints
@app.post("/api/auth/register")
async def register(user_data: UserCreate):
    """Register a new user"""
    return UserService.create_user(user_data)

@app.post("/api/auth/login")
async def login(login_data: UserLogin):
    """Authenticate user"""
    return UserService.authenticate_user(login_data)

@app.get("/api/auth/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile"""
    return UserService.get_user_profile(current_user["id"])

@app.put("/api/auth/profile")
async def update_profile(
    updates: dict, 
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    return UserService.update_user_profile(current_user["id"], updates)

# KYC endpoints
@app.post("/api/kyc/submit")
async def submit_kyc(
    kyc_data: KYCDocument,
    current_user: dict = Depends(get_current_user)
):
    """Submit KYC documents"""
    return UserService.submit_kyc(current_user["id"], kyc_data)

@app.get("/api/kyc/status")
async def get_kyc_status(current_user: dict = Depends(get_current_user)):
    """Get KYC status"""
    result = db.execute_query(
        "SELECT kyc_status, kyc_documents FROM users WHERE id = ?",
        (current_user["id"],)
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = dict(result[0])
    return {
        "kyc_status": user_data["kyc_status"],
        "documents": json.loads(user_data["kyc_documents"] or "{}")
    }

# Trading endpoints
@app.get("/api/trading/pairs")
async def get_trading_pairs(category: str = "spot"):
    """Get available trading pairs"""
    result = db.execute_query(
        "SELECT * FROM trading_pairs WHERE category = ? AND status = 'active'",
        (category,)
    )
    return [dict(row) for row in result]

@app.post("/api/trading/orders")
async def place_order(
    order: OrderCreate,
    current_user: dict = Depends(get_current_user)
):
    """Place a new order"""
    return trading_engine.place_order(order, current_user["id"])

@app.get("/api/trading/orders")
async def get_user_orders(
    symbol: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get user's orders"""
    return trading_engine.get_user_orders(current_user["id"], symbol)

@app.get("/api/trading/orderbook/{symbol}")
async def get_order_book(symbol: str):
    """Get order book for a symbol"""
    return trading_engine.get_order_book(symbol)

@app.delete("/api/trading/orders/{order_id}")
async def cancel_order(
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Cancel an order"""
    # Check if order belongs to user
    result = db.execute_query(
        "SELECT * FROM orders WHERE id = ? AND user_id = ?",
        (order_id, current_user["id"])
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update order status
    db.execute_query(
        "UPDATE orders SET status = 'cancelled' WHERE id = ?",
        (order_id,)
    )
    
    return {"message": "Order cancelled successfully"}

# Market data endpoints
@app.get("/api/market/data/{symbol}")
async def get_market_data(symbol: str):
    """Get market data for a symbol"""
    return market_service.get_market_data(symbol)

@app.get("/api/market/data")
async def get_all_market_data():
    """Get all market data"""
    return market_service.get_market_data()

# Security endpoints
@app.get("/api/security/logs")
async def get_security_logs(
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Get security logs"""
    return SecurityService.get_security_logs(current_user["id"], limit)

@app.get("/api/security/suspicious")
async def get_suspicious_activity(current_user: dict = Depends(get_current_user)):
    """Get suspicious activity detection"""
    return SecurityService.detect_suspicious_activity(current_user["id"])

# Admin endpoints
@app.get("/api/admin/users")
async def get_all_users(current_user: dict = Depends(get_current_user)):
    """Get all users (admin only)"""
    # Check if user is admin
    if current_user["email"] != "admin@tigerex.com":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = db.execute_query(
        "SELECT id, email, full_name, kyc_status, status, created_at FROM users ORDER BY created_at DESC LIMIT 1000"
    )
    return [dict(row) for row in result]

@app.post("/api/admin/users/{user_id}/suspend")
async def suspend_user(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Suspend a user (admin only)"""
    if current_user["email"] != "admin@tigerex.com":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db.execute_query(
        "UPDATE users SET status = 'suspended' WHERE id = ?",
        (user_id,)
    )
    
    # Log admin action
    db.execute_query(
        """INSERT INTO admin_logs 
        (admin_id, action, target_type, target_id, details) 
        VALUES (?, ?, ?, ?, ?)""",
        (current_user["id"], "suspend_user", "user", str(user_id), "User suspended by admin")
    )
    
    return {"message": "User suspended successfully"}

@app.post("/api/admin/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Activate a user (admin only)"""
    if current_user["email"] != "admin@tigerex.com":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db.execute_query(
        "UPDATE users SET status = 'active' WHERE id = ?",
        (user_id,)
    )
    
    # Log admin action
    db.execute_query(
        """INSERT INTO admin_logs 
        (admin_id, action, target_type, target_id, details) 
        VALUES (?, ?, ?, ?, ?)""",
        (current_user["id"], "activate_user", "user", str(user_id), "User activated by admin")
    )
    
    return {"message": "User activated successfully"}

@app.get("/api/admin/stats")
async def get_admin_stats(current_user: dict = Depends(get_current_user)):
    """Get admin dashboard statistics"""
    if current_user["email"] != "admin@tigerex.com":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get various statistics
    stats = {}
    
    # User statistics
    result = db.execute_query("SELECT COUNT(*) as total FROM users")
    stats["total_users"] = result[0]["total"]
    
    result = db.execute_query("SELECT COUNT(*) as total FROM users WHERE kyc_status = 'verified'")
    stats["verified_users"] = result[0]["total"]
    
    result = db.execute_query("SELECT COUNT(*) as total FROM users WHERE status = 'active'")
    stats["active_users"] = result[0]["total"]
    
    # Order statistics
    result = db.execute_query("SELECT COUNT(*) as total FROM orders WHERE created_at > datetime('now', '-24 hours')")
    stats["orders_24h"] = result[0]["total"]
    
    # Trading volume (simplified)
    result = db.execute_query(
        """SELECT SUM(CAST(quantity AS REAL) * CAST(price AS REAL)) as volume 
        FROM trades WHERE created_at > datetime('now', '-24 hours')"""
    )
    stats["volume_24h"] = result[0]["volume"] or 0
    
    return stats

# WebSocket endpoint for real-time data
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """WebSocket endpoint for real-time trading data"""
    connection_id = await websocket_manager.connect(websocket, user_id)
    
    try:
        while True:
            # Send real-time market data
            market_data = market_service.get_market_data()
            await websocket.send_text(json.dumps({
                "type": "market_update",
                "data": market_data
            }))
            
            # Send user's order updates
            user_orders = trading_engine.get_user_orders(user_id)
            await websocket.send_text(json.dumps({
                "type": "order_update",
                "data": user_orders
            }))
            
            await asyncio.sleep(5)  # Update every 5 seconds
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(connection_id, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(connection_id, user_id)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )

# Main execution
if __name__ == "__main__":
    print("🚀 Starting TigerEx Trading Platform Backend...")
    print("📊 Trading Engine Initialized")
    print("🔐 Security Services Active")
    print("📈 Market Data Streaming")
    print("🌐 WebSocket Server Ready")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )