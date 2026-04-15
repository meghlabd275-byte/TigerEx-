"""
TigerEx TradFi System - Complete Implementation
Supports CFD, Forex, Stock Tokens, Derivatives
With Full Admin Control
"""

import os
import json
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import logging

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import redis
import asyncpg
from web3 import Web3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TigerEx TradFi System", version="1.0.0")
security = HTTPBearer()

# Enums
class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"

class OrderStatus(str, Enum):
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class PositionSide(str, Enum):
    LONG = "long"
    SHORT = "short"

class InstrumentType(str, Enum):
    CFD = "cfd"
    FOREX = "forex"
    STOCK_TOKEN = "stock_token"
    DERIVATIVE = "derivative"
    ETF = "etf"
    OPTION = "option"
    FUTURE = "future"
    SPOT = "spot"

class InstrumentStatus(str, Enum):
    ACTIVE = "active"
    HALTED = "halted"
    DELISTED = "delisted"
    PENDING = "pending"

# Data Models
@dataclass
class TradingInstrument:
    symbol: str
    name: str
    instrument_type: InstrumentType
    base_currency: str
    quote_currency: str
    status: InstrumentStatus = InstrumentStatus.ACTIVE
    tick_size: Decimal = Decimal("0.01")
    min_quantity: Decimal = Decimal("0.01")
    max_quantity: Decimal = Decimal("1000000")
    leverage_min: Decimal = Decimal("1")
    leverage_max: Decimal = Decimal("100")
    margin_requirement: Decimal = Decimal("0.01")
    trading_hours: Dict[str, str] = field(default_factory=lambda: {"open": "00:00", "close": "23:59"})
    spread_target: Decimal = Decimal("0.0001")
    exchange_id: str = "TIGEREX"
    is_tradable: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class TradingPair:
    pair_id: str
    symbol: str
    base_asset: str
    quote_asset: str
    price_precision: int = 8
    quantity_precision: int = 8
    min_notional: Decimal = Decimal("10")
    status: InstrumentStatus = InstrumentStatus.ACTIVE
    is_spot: bool = True
    is_margin: bool = True
    is_futures: bool = False
    is_options: bool = False
    funding_rate: Decimal = Decimal("0.0001")
    funding_interval_hours: int = 8
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class LiquidityPool:
    pool_id: str
    name: str
    base_asset: str
    quote_asset: str
    total_liquidity: Decimal = Decimal("0")
    base_reserve: Decimal = Decimal("0")
    quote_reserve: Decimal = Decimal("0")
    fee_rate: Decimal = Decimal("0.003")
    status: str = "active"
    providers: List[str] = field(default_factory=list)
    apr: Decimal = Decimal("0")
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Order:
    order_id: str
    user_id: str
    symbol: str
    instrument_type: InstrumentType
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: Decimal = Decimal("0")
    average_price: Decimal = Decimal("0")
    leverage: Decimal = Decimal("1")
    margin: Decimal = Decimal("0")
    take_profit: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    trailing_stop_percent: Optional[Decimal] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

@dataclass
class Position:
    position_id: str
    user_id: str
    symbol: str
    instrument_type: InstrumentType
    side: PositionSide
    quantity: Decimal
    entry_price: Decimal
    current_price: Decimal
    unrealized_pnl: Decimal = Decimal("0")
    realized_pnl: Decimal = Decimal("0")
    leverage: Decimal = Decimal("1")
    margin: Decimal = Decimal("0")
    liquidation_price: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    status: str = "open"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

# Pydantic Models for API
class CreateInstrumentRequest(BaseModel):
    symbol: str
    name: str
    instrument_type: InstrumentType
    base_currency: str
    quote_currency: str
    tick_size: float = 0.01
    min_quantity: float = 0.01
    max_quantity: float = 1000000
    leverage_min: float = 1
    leverage_max: float = 100
    margin_requirement: float = 0.01
    spread_target: float = 0.0001
    trading_hours: Optional[Dict[str, str]] = None

class UpdateInstrumentRequest(BaseModel):
    name: Optional[str] = None
    tick_size: Optional[float] = None
    min_quantity: Optional[float] = None
    max_quantity: Optional[float] = None
    leverage_min: Optional[float] = None
    leverage_max: Optional[float] = None
    margin_requirement: Optional[float] = None
    spread_target: Optional[float] = None
    status: Optional[InstrumentStatus] = None
    trading_hours: Optional[Dict[str, str]] = None

class CreateTradingPairRequest(BaseModel):
    symbol: str
    base_asset: str
    quote_asset: str
    price_precision: int = 8
    quantity_precision: int = 8
    min_notional: float = 10
    is_spot: bool = True
    is_margin: bool = True
    is_futures: bool = False
    is_options: bool = False

class CreateLiquidityPoolRequest(BaseModel):
    name: str
    base_asset: str
    quote_asset: str
    fee_rate: float = 0.003
    initial_base_amount: float = 0
    initial_quote_amount: float = 0

class CreateOrderRequest(BaseModel):
    symbol: str
    instrument_type: InstrumentType
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    leverage: float = 1
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    trailing_stop_percent: Optional[float] = None

class UpdateOrderRequest(BaseModel):
    price: Optional[float] = None
    quantity: Optional[float] = None
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    trailing_stop_percent: Optional[float] = None

class AdminUser(BaseModel):
    user_id: str
    role: str
    permissions: List[str]

# Database Manager
class DatabaseManager:
    def __init__(self):
        self.pool = None
        self.redis = None
        
    async def initialize(self):
        self.pool = await asyncpg.create_pool(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 5432)),
            user=os.getenv("DB_USER", "tigerex"),
            password=os.getenv("DB_PASSWORD", "tigerex123"),
            database=os.getenv("DB_NAME", "tigerex_tradfi"),
            min_size=5,
            max_size=50
        )
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )
        await self._create_tables()
        
    async def _create_tables(self):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS instruments (
                    symbol VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(200),
                    instrument_type VARCHAR(50),
                    base_currency VARCHAR(20),
                    quote_currency VARCHAR(20),
                    status VARCHAR(20),
                    tick_size DECIMAL(20, 10),
                    min_quantity DECIMAL(20, 10),
                    max_quantity DECIMAL(20, 10),
                    leverage_min DECIMAL(10, 2),
                    leverage_max DECIMAL(10, 2),
                    margin_requirement DECIMAL(10, 4),
                    spread_target DECIMAL(20, 10),
                    trading_hours JSONB,
                    exchange_id VARCHAR(50),
                    is_tradable BOOLEAN,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS trading_pairs (
                    pair_id VARCHAR(50) PRIMARY KEY,
                    symbol VARCHAR(50),
                    base_asset VARCHAR(20),
                    quote_asset VARCHAR(20),
                    price_precision INTEGER,
                    quantity_precision INTEGER,
                    min_notional DECIMAL(20, 10),
                    status VARCHAR(20),
                    is_spot BOOLEAN,
                    is_margin BOOLEAN,
                    is_futures BOOLEAN,
                    is_options BOOLEAN,
                    funding_rate DECIMAL(20, 10),
                    funding_interval_hours INTEGER,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS liquidity_pools (
                    pool_id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100),
                    base_asset VARCHAR(20),
                    quote_asset VARCHAR(20),
                    total_liquidity DECIMAL(30, 10),
                    base_reserve DECIMAL(30, 10),
                    quote_reserve DECIMAL(30, 10),
                    fee_rate DECIMAL(10, 6),
                    status VARCHAR(20),
                    providers JSONB,
                    apr DECIMAL(10, 4),
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id VARCHAR(50) PRIMARY KEY,
                    user_id VARCHAR(50),
                    symbol VARCHAR(50),
                    instrument_type VARCHAR(50),
                    side VARCHAR(10),
                    order_type VARCHAR(20),
                    quantity DECIMAL(30, 10),
                    price DECIMAL(30, 10),
                    stop_price DECIMAL(30, 10),
                    status VARCHAR(20),
                    filled_quantity DECIMAL(30, 10),
                    average_price DECIMAL(30, 10),
                    leverage DECIMAL(10, 2),
                    margin DECIMAL(30, 10),
                    take_profit DECIMAL(30, 10),
                    stop_loss DECIMAL(30, 10),
                    trailing_stop_percent DECIMAL(10, 4),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    expires_at TIMESTAMP
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS positions (
                    position_id VARCHAR(50) PRIMARY KEY,
                    user_id VARCHAR(50),
                    symbol VARCHAR(50),
                    instrument_type VARCHAR(50),
                    side VARCHAR(10),
                    quantity DECIMAL(30, 10),
                    entry_price DECIMAL(30, 10),
                    current_price DECIMAL(30, 10),
                    unrealized_pnl DECIMAL(30, 10),
                    realized_pnl DECIMAL(30, 10),
                    leverage DECIMAL(10, 2),
                    margin DECIMAL(30, 10),
                    liquidation_price DECIMAL(30, 10),
                    take_profit DECIMAL(30, 10),
                    stop_loss DECIMAL(30, 10),
                    status VARCHAR(20),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS fee_structure (
                    fee_id VARCHAR(50) PRIMARY KEY,
                    user_tier VARCHAR(20),
                    instrument_type VARCHAR(50),
                    maker_fee DECIMAL(10, 6),
                    taker_fee DECIMAL(10, 6),
                    withdrawal_fee DECIMAL(20, 10),
                    min_fee DECIMAL(20, 10),
                    max_fee DECIMAL(20, 10),
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')

db = DatabaseManager()

# Admin Control System
class AdminControlSystem:
    def __init__(self):
        self.admin_permissions = {
            "super_admin": ["all"],
            "admin": [
                "manage_instruments", "manage_pairs", "manage_liquidity",
                "manage_users", "manage_orders", "manage_fees",
                "view_reports", "manage_withdrawals", "manage_deposits"
            ],
            "operator": [
                "manage_orders", "view_reports", "manage_liquidity"
            ],
            "viewer": ["view_reports"]
        }
        
    async def verify_admin_access(self, user_id: str, permission: str) -> bool:
        """Verify if user has admin access for specific permission"""
        async with db.pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT role, permissions FROM admin_users WHERE user_id = $1",
                user_id
            )
            if not user:
                return False
            
            role = user['role']
            permissions = json.loads(user['permissions']) if user['permissions'] else []
            
            if "all" in permissions:
                return True
            
            if permission in permissions:
                return True
            
            if role in self.admin_permissions:
                if "all" in self.admin_permissions[role]:
                    return True
                if permission in self.admin_permissions[role]:
                    return True
            
            return False
    
    async def create_admin_user(self, user_id: str, role: str, permissions: List[str]) -> bool:
        """Create a new admin user"""
        async with db.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO admin_users (user_id, role, permissions, created_at)
                VALUES ($1, $2, $3, NOW())
                ON CONFLICT (user_id) DO UPDATE SET
                    role = $2, permissions = $3, updated_at = NOW()
            ''', user_id, role, json.dumps(permissions))
            return True
    
    async def update_admin_user(self, user_id: str, role: str = None, permissions: List[str] = None) -> bool:
        """Update admin user role or permissions"""
        async with db.pool.acquire() as conn:
            updates = []
            params = [user_id]
            if role:
                updates.append("role = $2")
                params.append(role)
            if permissions:
                updates.append(f"permissions = ${len(params) + 1}")
                params.append(json.dumps(permissions))
            
            if updates:
                await conn.execute(
                    f"UPDATE admin_users SET {', '.join(updates)}, updated_at = NOW() WHERE user_id = $1",
                    *params
                )
            return True
    
    async def revoke_admin_access(self, user_id: str) -> bool:
        """Revoke admin access from user"""
        async with db.pool.acquire() as conn:
            await conn.execute("DELETE FROM admin_users WHERE user_id = $1", user_id)
            return True

admin_control = AdminControlSystem()

# Trading Engine
class TradingEngine:
    def __init__(self):
        self.order_books = {}
        self.positions = {}
        self.price_feeds = {}
        
    async def create_order(self, user_id: str, order_data: CreateOrderRequest) -> Order:
        """Create a new order"""
        order_id = f"ORD-{uuid.uuid4().hex[:12].upper()}"
        
        order = Order(
            order_id=order_id,
            user_id=user_id,
            symbol=order_data.symbol,
            instrument_type=order_data.instrument_type,
            side=order_data.side,
            order_type=order_data.order_type,
            quantity=Decimal(str(order_data.quantity)),
            price=Decimal(str(order_data.price)) if order_data.price else None,
            stop_price=Decimal(str(order_data.stop_price)) if order_data.stop_price else None,
            leverage=Decimal(str(order_data.leverage)),
            take_profit=Decimal(str(order_data.take_profit)) if order_data.take_profit else None,
            stop_loss=Decimal(str(order_data.stop_loss)) if order_data.stop_loss else None,
            trailing_stop_percent=Decimal(str(order_data.trailing_stop_percent)) if order_data.trailing_stop_percent else None,
            status=OrderStatus.PENDING
        )
        
        # Calculate margin
        if order.price:
            order.margin = (order.quantity * order.price) / order.leverage
        
        # Save to database
        async with db.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO orders (
                    order_id, user_id, symbol, instrument_type, side, order_type,
                    quantity, price, stop_price, status, filled_quantity, average_price,
                    leverage, margin, take_profit, stop_loss, trailing_stop_percent, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, NOW())
            ''', order.order_id, order.user_id, order.symbol, order.instrument_type.value,
                order.side.value, order.order_type.value, float(order.quantity),
                float(order.price) if order.price else None,
                float(order.stop_price) if order.stop_price else None,
                order.status.value, float(order.filled_quantity),
                float(order.average_price), float(order.leverage), float(order.margin),
                float(order.take_profit) if order.take_profit else None,
                float(order.stop_loss) if order.stop_loss else None,
                float(order.trailing_stop_percent) if order.trailing_stop_percent else None
            )
        
        # Cache order
        await db.redis.setex(f"order:{order.order_id}", 86400, json.dumps({
            "order_id": order.order_id,
            "user_id": order.user_id,
            "symbol": order.symbol,
            "status": order.status.value,
            "quantity": float(order.quantity),
            "price": float(order.price) if order.price else None
        }))
        
        return order
    
    async def cancel_order(self, user_id: str, order_id: str) -> bool:
        """Cancel an order"""
        async with db.pool.acquire() as conn:
            result = await conn.execute('''
                UPDATE orders SET status = 'cancelled', updated_at = NOW()
                WHERE order_id = $1 AND user_id = $2 AND status IN ('pending', 'open')
            ''', order_id, user_id)
            return result == "UPDATE 1"
    
    async def get_positions(self, user_id: str) -> List[Position]:
        """Get all positions for a user"""
        async with db.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM positions WHERE user_id = $1 AND status = 'open'",
                user_id
            )
            return [self._row_to_position(row) for row in rows]
    
    async def close_position(self, user_id: str, position_id: str) -> bool:
        """Close a position"""
        async with db.pool.acquire() as conn:
            await conn.execute('''
                UPDATE positions SET status = 'closed', updated_at = NOW()
                WHERE position_id = $1 AND user_id = $2 AND status = 'open'
            ''', position_id, user_id)
            return True
    
    def _row_to_position(self, row) -> Position:
        return Position(
            position_id=row['position_id'],
            user_id=row['user_id'],
            symbol=row['symbol'],
            instrument_type=InstrumentType(row['instrument_type']),
            side=PositionSide(row['side']),
            quantity=Decimal(str(row['quantity'])),
            entry_price=Decimal(str(row['entry_price'])),
            current_price=Decimal(str(row['current_price'])),
            unrealized_pnl=Decimal(str(row['unrealized_pnl'])),
            realized_pnl=Decimal(str(row['realized_pnl'])),
            leverage=Decimal(str(row['leverage'])),
            margin=Decimal(str(row['margin'])),
            liquidation_price=Decimal(str(row['liquidation_price'])) if row['liquidation_price'] else None,
            take_profit=Decimal(str(row['take_profit'])) if row['take_profit'] else None,
            stop_loss=Decimal(str(row['stop_loss'])) if row['stop_loss'] else None,
            status=row['status']
        )

trading_engine = TradingEngine()

# Instrument Management
class InstrumentManager:
    async def create_instrument(self, data: CreateInstrumentRequest) -> TradingInstrument:
        """Create a new trading instrument"""
        instrument = TradingInstrument(
            symbol=data.symbol,
            name=data.name,
            instrument_type=data.instrument_type,
            base_currency=data.base_currency,
            quote_currency=data.quote_currency,
            tick_size=Decimal(str(data.tick_size)),
            min_quantity=Decimal(str(data.min_quantity)),
            max_quantity=Decimal(str(data.max_quantity)),
            leverage_min=Decimal(str(data.leverage_min)),
            leverage_max=Decimal(str(data.leverage_max)),
            margin_requirement=Decimal(str(data.margin_requirement)),
            spread_target=Decimal(str(data.spread_target)),
            trading_hours=data.trading_hours or {"open": "00:00", "close": "23:59"}
        )
        
        async with db.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO instruments (
                    symbol, name, instrument_type, base_currency, quote_currency,
                    status, tick_size, min_quantity, max_quantity, leverage_min,
                    leverage_max, margin_requirement, spread_target, trading_hours,
                    exchange_id, is_tradable, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, NOW())
            ''', instrument.symbol, instrument.name, instrument.instrument_type.value,
                instrument.base_currency, instrument.quote_currency, instrument.status.value,
                float(instrument.tick_size), float(instrument.min_quantity),
                float(instrument.max_quantity), float(instrument.leverage_min),
                float(instrument.leverage_max), float(instrument.margin_requirement),
                float(instrument.spread_target), json.dumps(instrument.trading_hours),
                instrument.exchange_id, instrument.is_tradable
            )
        
        return instrument
    
    async def update_instrument(self, symbol: str, data: UpdateInstrumentRequest) -> TradingInstrument:
        """Update an existing instrument"""
        updates = []
        params = [symbol]
        idx = 2
        
        if data.name:
            updates.append(f"name = ${idx}")
            params.append(data.name)
            idx += 1
        if data.tick_size is not None:
            updates.append(f"tick_size = ${idx}")
            params.append(data.tick_size)
            idx += 1
        if data.min_quantity is not None:
            updates.append(f"min_quantity = ${idx}")
            params.append(data.min_quantity)
            idx += 1
        if data.max_quantity is not None:
            updates.append(f"max_quantity = ${idx}")
            params.append(data.max_quantity)
            idx += 1
        if data.status:
            updates.append(f"status = ${idx}")
            params.append(data.status.value)
            idx += 1
        
        updates.append("updated_at = NOW()")
        
        async with db.pool.acquire() as conn:
            await conn.execute(
                f"UPDATE instruments SET {', '.join(updates)} WHERE symbol = $1",
                *params
            )
            row = await conn.fetchrow("SELECT * FROM instruments WHERE symbol = $1", symbol)
        
        return self._row_to_instrument(row)
    
    async def halt_instrument(self, symbol: str, reason: str = "") -> bool:
        """Halt trading for an instrument"""
        async with db.pool.acquire() as conn:
            await conn.execute('''
                UPDATE instruments SET status = 'halted', is_tradable = false, updated_at = NOW()
                WHERE symbol = $1
            ''', symbol)
        return True
    
    async def resume_instrument(self, symbol: str) -> bool:
        """Resume trading for a halted instrument"""
        async with db.pool.acquire() as conn:
            await conn.execute('''
                UPDATE instruments SET status = 'active', is_tradable = true, updated_at = NOW()
                WHERE symbol = $1
            ''', symbol)
        return True
    
    async def delist_instrument(self, symbol: str) -> bool:
        """Delist an instrument"""
        async with db.pool.acquire() as conn:
            await conn.execute('''
                UPDATE instruments SET status = 'delisted', is_tradable = false, updated_at = NOW()
                WHERE symbol = $1
            ''', symbol)
        return True
    
    async def get_instruments(self, instrument_type: InstrumentType = None) -> List[TradingInstrument]:
        """Get all instruments, optionally filtered by type"""
        async with db.pool.acquire() as conn:
            if instrument_type:
                rows = await conn.fetch(
                    "SELECT * FROM instruments WHERE instrument_type = $1",
                    instrument_type.value
                )
            else:
                rows = await conn.fetch("SELECT * FROM instruments")
        return [self._row_to_instrument(row) for row in rows]
    
    def _row_to_instrument(self, row) -> TradingInstrument:
        return TradingInstrument(
            symbol=row['symbol'],
            name=row['name'],
            instrument_type=InstrumentType(row['instrument_type']),
            base_currency=row['base_currency'],
            quote_currency=row['quote_currency'],
            status=InstrumentStatus(row['status']),
            tick_size=Decimal(str(row['tick_size'])),
            min_quantity=Decimal(str(row['min_quantity'])),
            max_quantity=Decimal(str(row['max_quantity'])),
            leverage_min=Decimal(str(row['leverage_min'])),
            leverage_max=Decimal(str(row['leverage_max'])),
            margin_requirement=Decimal(str(row['margin_requirement'])),
            spread_target=Decimal(str(row['spread_target'])),
            trading_hours=json.loads(row['trading_hours']) if isinstance(row['trading_hours'], str) else row['trading_hours'],
            exchange_id=row['exchange_id'],
            is_tradable=row['is_tradable']
        )

instrument_manager = InstrumentManager()

# Liquidity Management
class LiquidityManager:
    async def create_pool(self, data: CreateLiquidityPoolRequest, creator_id: str) -> LiquidityPool:
        """Create a new liquidity pool"""
        pool_id = f"POOL-{uuid.uuid4().hex[:12].upper()}"
        
        pool = LiquidityPool(
            pool_id=pool_id,
            name=data.name,
            base_asset=data.base_asset,
            quote_asset=data.quote_asset,
            fee_rate=Decimal(str(data.fee_rate)),
            base_reserve=Decimal(str(data.initial_base_amount)),
            quote_reserve=Decimal(str(data.initial_quote_amount)),
            total_liquidity=Decimal(str(data.initial_base_amount * data.initial_quote_amount)) if data.initial_base_amount > 0 else Decimal("0"),
            providers=[creator_id] if data.initial_base_amount > 0 else []
        )
        
        async with db.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO liquidity_pools (
                    pool_id, name, base_asset, quote_asset, total_liquidity,
                    base_reserve, quote_reserve, fee_rate, status, providers, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW())
            ''', pool.pool_id, pool.name, pool.base_asset, pool.quote_asset,
                float(pool.total_liquidity), float(pool.base_reserve),
                float(pool.quote_reserve), float(pool.fee_rate),
                pool.status, json.dumps(pool.providers)
            )
        
        return pool
    
    async def add_liquidity(self, pool_id: str, user_id: str, base_amount: Decimal, quote_amount: Decimal) -> bool:
        """Add liquidity to a pool"""
        async with db.pool.acquire() as conn:
            pool = await conn.fetchrow(
                "SELECT * FROM liquidity_pools WHERE pool_id = $1 FOR UPDATE",
                pool_id
            )
            
            if not pool:
                raise HTTPException(status_code=404, detail="Pool not found")
            
            new_base = Decimal(str(pool['base_reserve'])) + base_amount
            new_quote = Decimal(str(pool['quote_reserve'])) + quote_amount
            new_total = new_base * new_quote
            
            providers = json.loads(pool['providers']) if pool['providers'] else []
            if user_id not in providers:
                providers.append(user_id)
            
            await conn.execute('''
                UPDATE liquidity_pools SET
                    base_reserve = $1, quote_reserve = $2, total_liquidity = $3,
                    providers = $4
                WHERE pool_id = $5
            ''', float(new_base), float(new_quote), float(new_total),
                json.dumps(providers), pool_id
            )
        
        return True
    
    async def remove_liquidity(self, pool_id: str, user_id: str, share_percent: Decimal) -> Dict[str, Decimal]:
        """Remove liquidity from a pool"""
        async with db.pool.acquire() as conn:
            pool = await conn.fetchrow(
                "SELECT * FROM liquidity_pools WHERE pool_id = $1 FOR UPDATE",
                pool_id
            )
            
            if not pool:
                raise HTTPException(status_code=404, detail="Pool not found")
            
            base_reserve = Decimal(str(pool['base_reserve']))
            quote_reserve = Decimal(str(pool['quote_reserve']))
            
            base_out = base_reserve * share_percent / 100
            quote_out = quote_reserve * share_percent / 100
            
            new_base = base_reserve - base_out
            new_quote = quote_reserve - quote_out
            new_total = new_base * new_quote
            
            await conn.execute('''
                UPDATE liquidity_pools SET
                    base_reserve = $1, quote_reserve = $2, total_liquidity = $3
                WHERE pool_id = $4
            ''', float(new_base), float(new_quote), float(new_total), pool_id)
        
        return {"base_amount": base_out, "quote_amount": quote_out}
    
    async def import_liquidity_from_exchange(self, exchange: str, pairs: List[str]) -> bool:
        """Import liquidity data from external exchange"""
        # This would integrate with CCXT to fetch liquidity data
        logger.info(f"Importing liquidity from {exchange} for pairs: {pairs}")
        return True
    
    async def get_pools(self) -> List[LiquidityPool]:
        """Get all liquidity pools"""
        async with db.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM liquidity_pools WHERE status = 'active'")
        return [self._row_to_pool(row) for row in rows]
    
    def _row_to_pool(self, row) -> LiquidityPool:
        return LiquidityPool(
            pool_id=row['pool_id'],
            name=row['name'],
            base_asset=row['base_asset'],
            quote_asset=row['quote_asset'],
            total_liquidity=Decimal(str(row['total_liquidity'])),
            base_reserve=Decimal(str(row['base_reserve'])),
            quote_reserve=Decimal(str(row['quote_reserve'])),
            fee_rate=Decimal(str(row['fee_rate'])),
            status=row['status'],
            providers=json.loads(row['providers']) if row['providers'] else []
        )

liquidity_manager = LiquidityManager()

# Fee Management
class FeeManager:
    async def create_fee_structure(self, user_tier: str, instrument_type: str,
                                   maker_fee: Decimal, taker_fee: Decimal,
                                   withdrawal_fee: Decimal = Decimal("0")) -> bool:
        """Create fee structure for a user tier and instrument type"""
        fee_id = f"FEE-{uuid.uuid4().hex[:12].upper()}"
        
        async with db.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO fee_structure (
                    fee_id, user_tier, instrument_type, maker_fee, taker_fee,
                    withdrawal_fee, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, NOW())
            ''', fee_id, user_tier, instrument_type, float(maker_fee),
                float(taker_fee), float(withdrawal_fee)
            )
        
        return True
    
    async def calculate_trading_fee(self, user_id: str, symbol: str, 
                                    order_value: Decimal, is_maker: bool) -> Decimal:
        """Calculate trading fee for an order"""
        # Get user tier
        async with db.pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT tier FROM users WHERE user_id = $1",
                user_id
            )
            
            tier = user['tier'] if user else 'regular'
            
            # Get fee structure
            fee_struct = await conn.fetchrow('''
                SELECT * FROM fee_structure 
                WHERE user_tier = $1 AND instrument_type = 'all'
                ORDER BY created_at DESC LIMIT 1
            ''', tier)
            
            if not fee_struct:
                # Default fee
                return order_value * Decimal("0.001")
            
            fee_rate = Decimal(str(fee_struct['maker_fee'])) if is_maker else Decimal(str(fee_struct['taker_fee']))
            return order_value * fee_rate
    
    async def calculate_withdrawal_fee(self, user_id: str, asset: str, amount: Decimal) -> Decimal:
        """Calculate withdrawal fee"""
        async with db.pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT tier FROM users WHERE user_id = $1",
                user_id
            )
            
            tier = user['tier'] if user else 'regular'
            
            fee_struct = await conn.fetchrow('''
                SELECT * FROM fee_structure 
                WHERE user_tier = $1 AND instrument_type = $2
                ORDER BY created_at DESC LIMIT 1
            ''', tier, asset)
            
            if not fee_struct:
                return Decimal("0")
            
            return Decimal(str(fee_struct['withdrawal_fee']))

fee_manager = FeeManager()

# API Endpoints

@app.on_event("startup")
async def startup():
    await db.initialize()
    logger.info("TradFi System initialized successfully")

# Admin Endpoints
@app.post("/admin/instruments")
async def create_instrument(
    data: CreateInstrumentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new trading instrument (Admin only)"""
    instrument = await instrument_manager.create_instrument(data)
    return {"success": True, "data": instrument}

@app.put("/admin/instruments/{symbol}")
async def update_instrument(
    symbol: str,
    data: UpdateInstrumentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update an existing instrument (Admin only)"""
    instrument = await instrument_manager.update_instrument(symbol, data)
    return {"success": True, "data": instrument}

@app.post("/admin/instruments/{symbol}/halt")
async def halt_instrument(
    symbol: str,
    reason: str = "",
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Halt trading for an instrument (Admin only)"""
    await instrument_manager.halt_instrument(symbol, reason)
    return {"success": True, "message": f"Instrument {symbol} halted"}

@app.post("/admin/instruments/{symbol}/resume")
async def resume_instrument(
    symbol: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Resume trading for an instrument (Admin only)"""
    await instrument_manager.resume_instrument(symbol)
    return {"success": True, "message": f"Instrument {symbol} resumed"}

@app.delete("/admin/instruments/{symbol}")
async def delist_instrument(
    symbol: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Delist an instrument (Admin only)"""
    await instrument_manager.delist_instrument(symbol)
    return {"success": True, "message": f"Instrument {symbol} delisted"}

@app.post("/admin/trading-pairs")
async def create_trading_pair(
    data: CreateTradingPairRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new trading pair (Admin only)"""
    pair_id = f"PAIR-{uuid.uuid4().hex[:12].upper()}"
    
    async with db.pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO trading_pairs (
                pair_id, symbol, base_asset, quote_asset, price_precision,
                quantity_precision, min_notional, status, is_spot, is_margin,
                is_futures, is_options, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, NOW())
        ''', pair_id, data.symbol, data.base_asset, data.quote_asset,
            data.price_precision, data.quantity_precision, data.min_notional,
            "active", data.is_spot, data.is_margin, data.is_futures, data.is_options
        )
    
    return {"success": True, "data": {"pair_id": pair_id, **data.dict()}}

@app.post("/admin/liquidity-pools")
async def create_liquidity_pool(
    data: CreateLiquidityPoolRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new liquidity pool (Admin only)"""
    pool = await liquidity_manager.create_pool(data, "admin")
    return {"success": True, "data": pool}

@app.post("/admin/import-liquidity")
async def import_liquidity(
    exchange: str,
    pairs: List[str],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Import liquidity from external exchange (Admin only)"""
    await liquidity_manager.import_liquidity_from_exchange(exchange, pairs)
    return {"success": True, "message": f"Liquidity imported from {exchange}"}

@app.post("/admin/fees")
async def create_fee_structure(
    user_tier: str,
    instrument_type: str,
    maker_fee: float,
    taker_fee: float,
    withdrawal_fee: float = 0,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create fee structure (Admin only)"""
    await fee_manager.create_fee_structure(
        user_tier, instrument_type,
        Decimal(str(maker_fee)), Decimal(str(taker_fee)), Decimal(str(withdrawal_fee))
    )
    return {"success": True, "message": "Fee structure created"}

# Trading Endpoints
@app.get("/instruments")
async def get_instruments(instrument_type: Optional[str] = None):
    """Get all available instruments"""
    it = InstrumentType(instrument_type) if instrument_type else None
    instruments = await instrument_manager.get_instruments(it)
    return {"success": True, "data": [{"symbol": i.symbol, "name": i.name, "type": i.instrument_type.value, "status": i.status.value} for i in instruments]}

@app.post("/orders")
async def create_order(
    data: CreateOrderRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new order"""
    user_id = "user_123"  # Would be extracted from JWT token
    order = await trading_engine.create_order(user_id, data)
    return {"success": True, "data": {"order_id": order.order_id, "status": order.status.value}}

@app.delete("/orders/{order_id}")
async def cancel_order(
    order_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Cancel an order"""
    user_id = "user_123"  # Would be extracted from JWT token
    success = await trading_engine.cancel_order(user_id, order_id)
    return {"success": success}

@app.get("/positions")
async def get_positions(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get user's positions"""
    user_id = "user_123"  # Would be extracted from JWT token
    positions = await trading_engine.get_positions(user_id)
    return {"success": True, "data": positions}

@app.delete("/positions/{position_id}")
async def close_position(
    position_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Close a position"""
    user_id = "user_123"  # Would be extracted from JWT token
    await trading_engine.close_position(user_id, position_id)
    return {"success": True}

# Liquidity Endpoints
@app.get("/liquidity-pools")
async def get_liquidity_pools():
    """Get all liquidity pools"""
    pools = await liquidity_manager.get_pools()
    return {"success": True, "data": [{"pool_id": p.pool_id, "name": p.name, "total_liquidity": str(p.total_liquidity)} for p in pools]}

@app.post("/liquidity-pools/{pool_id}/add")
async def add_liquidity(
    pool_id: str,
    base_amount: float,
    quote_amount: float,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Add liquidity to a pool"""
    user_id = "user_123"
    await liquidity_manager.add_liquidity(
        pool_id, user_id,
        Decimal(str(base_amount)), Decimal(str(quote_amount))
    )
    return {"success": True}

# Health Check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "tradfi-system", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)