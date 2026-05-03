"""
TigerEx Unified Trading System
Complete Integration of All Trading Types with Full Admin Control
Supports: Spot, Futures, Options, Margin, CFD, Forex, ETF, Derivatives
"""

import os
import json
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import logging
import hashlib
import secrets

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import asyncpg
import redis.asyncio as redis
import jwt

# @file main.py
# @description TigerEx tigerex-unified-trading-system service
# @author TigerEx Development Team
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TigerEx Unified Trading System",
    description="Complete Trading System with Full Admin Control",
    version="2.0.0"
)
security = HTTPBearer()

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== ENUMS ====================

class TradingType(str, Enum):
    SPOT = "spot"
    FUTURES = "futures"
    OPTIONS = "options"
    MARGIN = "margin"
    CFD = "cfd"
    FOREX = "forex"
    ETF = "etf"
    DERIVATIVES = "derivatives"
    PERPETUAL = "perpetual"
    SWAP = "swap"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"
    LONG = "long"
    SHORT = "short"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_MARKET = "stop_market"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"
    ICEBERG = "iceberg"
    FOK = "fill_or_kill"
    IOC = "immediate_or_cancel"
    POST_ONLY = "post_only"

class OrderStatus(str, Enum):
    PENDING = "pending"
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"
    LIQUIDATED = "liquidated"

class InstrumentStatus(str, Enum):
    ACTIVE = "active"
    HALTED = "halted"
    CLOSE_ONLY = "close_only"
    DELISTED = "delisted"
    PENDING = "pending"

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    OPERATOR = "operator"
    RISK_MANAGER = "risk_manager"
    SUPPORT = "support"
    TREASURY = "treasury"
    VIEWER = "viewer"
    USER = "user"
    VIP = "vip"
    INSTITUTIONAL = "institutional"

class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    FROZEN = "frozen"
    PENDING_KYC = "pending_kyc"
    VERIFIED = "verified"

class FeeType(str, Enum):
    MAKER = "maker"
    TAKER = "taker"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"
    TRANSFER = "transfer"
    FUNDING = "funding"
    LIQUIDATION = "liquidation"

# ==================== PERMISSIONS ====================

PERMISSIONS = {
    "super_admin": ["all"],
    "admin": [
        "manage_users", "manage_trading", "manage_fees", "manage_liquidity",
        "manage_pairs", "manage_kyc", "manage_withdrawals", "manage_deposits",
        "view_reports", "manage_settings", "manage_admins", "manage_roles",
        "halt_trading", "delist_pairs", "freeze_accounts", "system_config"
    ],
    "operator": [
        "manage_trading", "view_reports", "manage_pairs", "halt_trading"
    ],
    "risk_manager": [
        "view_reports", "manage_risk", "halt_trading", "adjust_leverage"
    ],
    "support": [
        "view_users", "manage_kyc", "view_reports", "unlock_accounts"
    ],
    "treasury": [
        "manage_withdrawals", "manage_deposits", "view_reports", "fee_management"
    ],
    "viewer": [
        "view_reports", "view_users"
    ]
}

# ==================== DATA MODELS ====================

@dataclass
class TradingPair:
    pair_id: str
    symbol: str
    base_asset: str
    quote_asset: str
    trading_types: List[TradingType]
    status: InstrumentStatus = InstrumentStatus.ACTIVE
    price_precision: int = 8
    quantity_precision: int = 8
    min_quantity: Decimal = Decimal("0.001")
    max_quantity: Decimal = Decimal("1000000")
    min_notional: Decimal = Decimal("10")
    max_notional: Decimal = Decimal("10000000")
    maker_fee: Decimal = Decimal("0.001")
    taker_fee: Decimal = Decimal("0.001")
    leverage_min: Decimal = Decimal("1")
    leverage_max: Decimal = Decimal("100")
    initial_margin: Decimal = Decimal("0.1")
    maintenance_margin: Decimal = Decimal("0.05")
    funding_rate: Decimal = Decimal("0")
    funding_interval_hours: int = 8
    tick_size: Decimal = Decimal("0.00000001")
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Order:
    order_id: str
    user_id: str
    account_id: str
    symbol: str
    trading_type: TradingType
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    trigger_price: Optional[Decimal] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: Decimal = Decimal("0")
    average_price: Decimal = Decimal("0")
    leverage: Decimal = Decimal("1")
    margin: Decimal = Decimal("0")
    take_profit: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    trailing_stop_percent: Optional[Decimal] = None
    time_in_force: str = "GTC"
    post_only: bool = False
    reduce_only: bool = False
    close_position: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

@dataclass
class Position:
    position_id: str
    user_id: str
    account_id: str
    symbol: str
    trading_type: TradingType
    side: OrderSide
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
    auto_deleverage_rank: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class LiquidityPool:
    pool_id: str
    name: str
    symbol: str
    base_asset: str
    quote_asset: str
    total_liquidity: Decimal = Decimal("0")
    base_reserve: Decimal = Decimal("0")
    quote_reserve: Decimal = Decimal("0")
    k_constant: Decimal = Decimal("0")
    fee_rate: Decimal = Decimal("0.003")
    status: str = "active"
    providers: List[str] = field(default_factory=list)
    apr: Decimal = Decimal("0")
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class FeeStructure:
    fee_id: str
    user_tier: str
    trading_type: TradingType
    fee_type: FeeType
    fee_value: Decimal
    min_fee: Decimal = Decimal("0")
    max_fee: Decimal = Decimal("1000")
    discount_percent: Decimal = Decimal("0")
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class User:
    user_id: str
    email: str
    username: str
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE
    kyc_level: int = 0
    tier: str = "regular"
    total_volume_30d: Decimal = Decimal("0")
    total_trades: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ExchangeConfig:
    exchange_id: str
    name: str = "TigerEx"
    status: str = "active"
    maintenance_mode: bool = False
    trading_enabled: bool = True
    withdrawals_enabled: bool = True
    deposits_enabled: bool = True
    registration_enabled: bool = True
    kyc_required: bool = True
    default_leverage: Decimal = Decimal("10")
    max_total_leverage: Decimal = Decimal("100")
    created_at: datetime = field(default_factory=datetime.utcnow)

# ==================== PYDANTIC MODELS ====================

class CreateTradingPairRequest(BaseModel):
    symbol: str
    base_asset: str
    quote_asset: str
    trading_types: List[str]
    price_precision: int = 8
    quantity_precision: int = 8
    min_quantity: float = 0.001
    max_quantity: float = 1000000
    min_notional: float = 10
    maker_fee: float = 0.001
    taker_fee: float = 0.001
    leverage_min: float = 1
    leverage_max: float = 100

class UpdateTradingPairRequest(BaseModel):
    status: Optional[str] = None
    maker_fee: Optional[float] = None
    taker_fee: Optional[float] = None
    min_quantity: Optional[float] = None
    max_quantity: Optional[float] = None
    leverage_min: Optional[float] = None
    leverage_max: Optional[float] = None

class CreateOrderRequest(BaseModel):
    symbol: str
    trading_type: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    leverage: float = 1
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    trailing_stop_percent: Optional[float] = None
    time_in_force: str = "GTC"
    post_only: bool = False
    reduce_only: bool = False

class CreateLiquidityPoolRequest(BaseModel):
    name: str
    base_asset: str
    quote_asset: str
    fee_rate: float = 0.003
    initial_base: float = 0
    initial_quote: float = 0

class SetFeeRequest(BaseModel):
    user_tier: str
    trading_type: str
    fee_type: str
    fee_value: float
    min_fee: float = 0
    max_fee: float = 1000

class ManageUserRequest(BaseModel):
    user_id: str
    action: str
    reason: str = ""

class ImportFromExchangeRequest(BaseModel):
    exchange: str
    pairs: List[str]
    trading_type: str = "spot"

class ExchangeConfigRequest(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    maintenance_mode: Optional[bool] = None
    trading_enabled: Optional[bool] = None
    withdrawals_enabled: Optional[bool] = None
    deposits_enabled: Optional[bool] = None

# ==================== DATABASE MANAGER ====================

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
            database=os.getenv("DB_NAME", "tigerex_unified"),
            min_size=10,
            max_size=100
        )
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )
        await self._create_tables()
        
    async def _create_tables(self):
        async with self.pool.acquire() as conn:
            # Users table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id VARCHAR(50) PRIMARY KEY,
                    email VARCHAR(200),
                    username VARCHAR(100),
                    role VARCHAR(20) DEFAULT 'user',
                    status VARCHAR(20) DEFAULT 'active',
                    kyc_level INTEGER DEFAULT 0,
                    tier VARCHAR(20) DEFAULT 'regular',
                    total_volume_30d DECIMAL(30, 10) DEFAULT 0,
                    total_trades INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # Trading pairs table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS trading_pairs (
                    pair_id VARCHAR(50) PRIMARY KEY,
                    symbol VARCHAR(50) UNIQUE,
                    base_asset VARCHAR(20),
                    quote_asset VARCHAR(20),
                    trading_types JSONB,
                    status VARCHAR(20) DEFAULT 'active',
                    price_precision INTEGER DEFAULT 8,
                    quantity_precision INTEGER DEFAULT 8,
                    min_quantity DECIMAL(30, 10) DEFAULT 0.001,
                    max_quantity DECIMAL(30, 10) DEFAULT 1000000,
                    min_notional DECIMAL(30, 10) DEFAULT 10,
                    max_notional DECIMAL(30, 10) DEFAULT 10000000,
                    maker_fee DECIMAL(10, 6) DEFAULT 0.001,
                    taker_fee DECIMAL(10, 6) DEFAULT 0.001,
                    leverage_min DECIMAL(10, 2) DEFAULT 1,
                    leverage_max DECIMAL(10, 2) DEFAULT 100,
                    initial_margin DECIMAL(10, 6) DEFAULT 0.1,
                    maintenance_margin DECIMAL(10, 6) DEFAULT 0.05,
                    funding_rate DECIMAL(20, 10) DEFAULT 0,
                    funding_interval_hours INTEGER DEFAULT 8,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # Orders table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id VARCHAR(50) PRIMARY KEY,
                    user_id VARCHAR(50),
                    account_id VARCHAR(50),
                    symbol VARCHAR(50),
                    trading_type VARCHAR(20),
                    side VARCHAR(10),
                    order_type VARCHAR(20),
                    quantity DECIMAL(30, 10),
                    price DECIMAL(30, 10),
                    stop_price DECIMAL(30, 10),
                    status VARCHAR(20) DEFAULT 'pending',
                    filled_quantity DECIMAL(30, 10) DEFAULT 0,
                    average_price DECIMAL(30, 10) DEFAULT 0,
                    leverage DECIMAL(10, 2) DEFAULT 1,
                    margin DECIMAL(30, 10) DEFAULT 0,
                    take_profit DECIMAL(30, 10),
                    stop_loss DECIMAL(30, 10),
                    trailing_stop_percent DECIMAL(10, 4),
                    time_in_force VARCHAR(10) DEFAULT 'GTC',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    expires_at TIMESTAMP
                )
            ''')
            
            # Positions table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS positions (
                    position_id VARCHAR(50) PRIMARY KEY,
                    user_id VARCHAR(50),
                    account_id VARCHAR(50),
                    symbol VARCHAR(50),
                    trading_type VARCHAR(20),
                    side VARCHAR(10),
                    quantity DECIMAL(30, 10),
                    entry_price DECIMAL(30, 10),
                    current_price DECIMAL(30, 10),
                    unrealized_pnl DECIMAL(30, 10) DEFAULT 0,
                    realized_pnl DECIMAL(30, 10) DEFAULT 0,
                    leverage DECIMAL(10, 2) DEFAULT 1,
                    margin DECIMAL(30, 10) DEFAULT 0,
                    liquidation_price DECIMAL(30, 10),
                    take_profit DECIMAL(30, 10),
                    stop_loss DECIMAL(30, 10),
                    status VARCHAR(20) DEFAULT 'open',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # Liquidity pools table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS liquidity_pools (
                    pool_id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100),
                    symbol VARCHAR(50),
                    base_asset VARCHAR(20),
                    quote_asset VARCHAR(20),
                    total_liquidity DECIMAL(40, 10) DEFAULT 0,
                    base_reserve DECIMAL(40, 10) DEFAULT 0,
                    quote_reserve DECIMAL(40, 10) DEFAULT 0,
                    fee_rate DECIMAL(10, 6) DEFAULT 0.003,
                    status VARCHAR(20) DEFAULT 'active',
                    providers JSONB,
                    apr DECIMAL(10, 4) DEFAULT 0,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # Fee structure table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS fee_structure (
                    fee_id VARCHAR(50) PRIMARY KEY,
                    user_tier VARCHAR(20),
                    trading_type VARCHAR(20),
                    fee_type VARCHAR(20),
                    fee_value DECIMAL(10, 6),
                    min_fee DECIMAL(20, 10) DEFAULT 0,
                    max_fee DECIMAL(20, 10) DEFAULT 1000,
                    discount_percent DECIMAL(10, 4) DEFAULT 0,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # Exchange config table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS exchange_config (
                    exchange_id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) DEFAULT 'TigerEx',
                    status VARCHAR(20) DEFAULT 'active',
                    maintenance_mode BOOLEAN DEFAULT false,
                    trading_enabled BOOLEAN DEFAULT true,
                    withdrawals_enabled BOOLEAN DEFAULT true,
                    deposits_enabled BOOLEAN DEFAULT true,
                    registration_enabled BOOLEAN DEFAULT true,
                    kyc_required BOOLEAN DEFAULT true,
                    default_leverage DECIMAL(10, 2) DEFAULT 10,
                    max_total_leverage DECIMAL(10, 2) DEFAULT 100,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # Audit log table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    log_id VARCHAR(50) PRIMARY KEY,
                    admin_id VARCHAR(50),
                    action VARCHAR(100),
                    entity_type VARCHAR(50),
                    entity_id VARCHAR(50),
                    old_value JSONB,
                    new_value JSONB,
                    ip_address VARCHAR(50),
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')

db = DatabaseManager()

# ==================== ADMIN CONTROLLER ====================

class AdminController:
    def __init__(self):
        self.exchange_config = None
        
    async def check_permission(self, admin_id: str, permission: str) -> bool:
        """Check if admin has specific permission"""
        async with db.pool.acquire() as conn:
            admin = await conn.fetchrow(
                "SELECT role, permissions FROM admin_users WHERE admin_id = $1 AND status = 'active'",
                admin_id
            )
            if not admin:
                return False
            
            role = admin['role']
            permissions = json.loads(admin['permissions']) if admin['permissions'] else []
            
            if "all" in permissions:
                return True
            
            role_perms = PERMISSIONS.get(role, [])
            if "all" in role_perms:
                return True
            
            return permission in permissions or permission in role_perms
    
    async def log_action(self, admin_id: str, action: str, entity_type: str,
                        entity_id: str, old_value: Any, new_value: Any, ip: str = ""):
        """Log admin action for audit"""
        log_id = f"LOG-{uuid.uuid4().hex[:12].upper()}"
        async with db.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO audit_log (log_id, admin_id, action, entity_type, entity_id, old_value, new_value, ip_address, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
            ''', log_id, admin_id, action, entity_type, entity_id,
                json.dumps(old_value) if old_value else None,
                json.dumps(new_value) if new_value else None, ip
            )

admin_controller = AdminController()

# ==================== TRADING PAIR MANAGER ====================

class TradingPairManager:
    async def create_pair(self, data: CreateTradingPairRequest, admin_id: str) -> TradingPair:
        """Create a new trading pair"""
        pair_id = f"PAIR-{uuid.uuid4().hex[:12].upper()}"
        
        pair = TradingPair(
            pair_id=pair_id,
            symbol=data.symbol,
            base_asset=data.base_asset,
            quote_asset=data.quote_asset,
            trading_types=[TradingType(t) for t in data.trading_types],
            price_precision=data.price_precision,
            quantity_precision=data.quantity_precision,
            min_quantity=Decimal(str(data.min_quantity)),
            max_quantity=Decimal(str(data.max_quantity)),
            min_notional=Decimal(str(data.min_notional)),
            maker_fee=Decimal(str(data.maker_fee)),
            taker_fee=Decimal(str(data.taker_fee)),
            leverage_min=Decimal(str(data.leverage_min)),
            leverage_max=Decimal(str(data.leverage_max))
        )
        
        async with db.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO trading_pairs (
                    pair_id, symbol, base_asset, quote_asset, trading_types, status,
                    price_precision, quantity_precision, min_quantity, max_quantity,
                    min_notional, maker_fee, taker_fee, leverage_min, leverage_max, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, NOW())
            ''', pair.pair_id, pair.symbol, pair.base_asset, pair.quote_asset,
                json.dumps([t.value for t in pair.trading_types]), pair.status.value,
                pair.price_precision, pair.quantity_precision, float(pair.min_quantity),
                float(pair.max_quantity), float(pair.min_notional), float(pair.maker_fee),
                float(pair.taker_fee), float(pair.leverage_min), float(pair.leverage_max)
            )
        
        await admin_controller.log_action(admin_id, "create_pair", "trading_pair", pair_id, None, data.dict())
        return pair
    
    async def update_pair(self, symbol: str, data: UpdateTradingPairRequest, admin_id: str) -> TradingPair:
        """Update trading pair"""
        updates = []
        params = [symbol]
        idx = 2
        
        old_pair = await self.get_pair(symbol)
        
        if data.status:
            updates.append(f"status = ${idx}")
            params.append(data.status)
            idx += 1
        if data.maker_fee is not None:
            updates.append(f"maker_fee = ${idx}")
            params.append(data.maker_fee)
            idx += 1
        if data.taker_fee is not None:
            updates.append(f"taker_fee = ${idx}")
            params.append(data.taker_fee)
            idx += 1
        if data.min_quantity is not None:
            updates.append(f"min_quantity = ${idx}")
            params.append(data.min_quantity)
            idx += 1
        if data.max_quantity is not None:
            updates.append(f"max_quantity = ${idx}")
            params.append(data.max_quantity)
            idx += 1
        
        updates.append("updated_at = NOW()")
        
        if updates:
            async with db.pool.acquire() as conn:
                await conn.execute(
                    f"UPDATE trading_pairs SET {', '.join(updates)} WHERE symbol = $1",
                    *params
                )
        
        new_pair = await self.get_pair(symbol)
        await admin_controller.log_action(admin_id, "update_pair", "trading_pair", symbol, old_pair, new_pair)
        return new_pair
    
    async def halt_pair(self, symbol: str, reason: str, admin_id: str) -> bool:
        """Halt trading for a pair"""
        async with db.pool.acquire() as conn:
            await conn.execute(
                "UPDATE trading_pairs SET status = 'halted', updated_at = NOW() WHERE symbol = $1",
                symbol
            )
        await admin_controller.log_action(admin_id, "halt_pair", "trading_pair", symbol, None, {"reason": reason})
        return True
    
    async def resume_pair(self, symbol: str, admin_id: str) -> bool:
        """Resume trading for a pair"""
        async with db.pool.acquire() as conn:
            await conn.execute(
                "UPDATE trading_pairs SET status = 'active', updated_at = NOW() WHERE symbol = $1",
                symbol
            )
        await admin_controller.log_action(admin_id, "resume_pair", "trading_pair", symbol, None, None)
        return True
    
    async def delist_pair(self, symbol: str, reason: str, admin_id: str) -> bool:
        """Delist a trading pair"""
        async with db.pool.acquire() as conn:
            await conn.execute(
                "UPDATE trading_pairs SET status = 'delisted', updated_at = NOW() WHERE symbol = $1",
                symbol
            )
        await admin_controller.log_action(admin_id, "delist_pair", "trading_pair", symbol, None, {"reason": reason})
        return True
    
    async def get_pair(self, symbol: str) -> Optional[TradingPair]:
        """Get trading pair by symbol"""
        async with db.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM trading_pairs WHERE symbol = $1", symbol)
            if row:
                return self._row_to_pair(row)
            return None
    
    async def get_all_pairs(self, status: str = None, trading_type: str = None) -> List[TradingPair]:
        """Get all trading pairs"""
        async with db.pool.acquire() as conn:
            if status:
                rows = await conn.fetch("SELECT * FROM trading_pairs WHERE status = $1 ORDER BY symbol", status)
            elif trading_type:
                rows = await conn.fetch(
                    "SELECT * FROM trading_pairs WHERE trading_types ? $1 ORDER BY symbol",
                    trading_type
                )
            else:
                rows = await conn.fetch("SELECT * FROM trading_pairs ORDER BY symbol")
        return [self._row_to_pair(row) for row in rows]
    
    async def import_from_exchange(self, exchange: str, pairs: List[str], trading_type: str, admin_id: str) -> Dict:
        """Import trading pairs from external exchange"""
        imported = []
        for symbol in pairs:
            # Create pair with defaults (would fetch from exchange API in production)
            pair_data = CreateTradingPairRequest(
                symbol=symbol,
                base_asset=symbol.split('/')[0] if '/' in symbol else symbol[:3],
                quote_asset=symbol.split('/')[1] if '/' in symbol else symbol[3:],
                trading_types=[trading_type]
            )
            try:
                pair = await self.create_pair(pair_data, admin_id)
                imported.append(symbol)
            except Exception as e:
                logger.error(f"Failed to import {symbol}: {e}")
        
        await admin_controller.log_action(admin_id, "import_pairs", "exchange", exchange, None, {"pairs": imported})
        return {"exchange": exchange, "imported": imported, "count": len(imported)}
    
    def _row_to_pair(self, row) -> TradingPair:
        return TradingPair(
            pair_id=row['pair_id'],
            symbol=row['symbol'],
            base_asset=row['base_asset'],
            quote_asset=row['quote_asset'],
            trading_types=[TradingType(t) for t in json.loads(row['trading_types'])],
            status=InstrumentStatus(row['status']),
            price_precision=row['price_precision'],
            quantity_precision=row['quantity_precision'],
            min_quantity=Decimal(str(row['min_quantity'])),
            max_quantity=Decimal(str(row['max_quantity'])),
            min_notional=Decimal(str(row['min_notional'])),
            maker_fee=Decimal(str(row['maker_fee'])),
            taker_fee=Decimal(str(row['taker_fee'])),
            leverage_min=Decimal(str(row['leverage_min'])),
            leverage_max=Decimal(str(row['leverage_max'])),
            created_at=row['created_at']
        )

pair_manager = TradingPairManager()

# ==================== LIQUIDITY MANAGER ====================

class LiquidityManager:
    async def create_pool(self, data: CreateLiquidityPoolRequest, admin_id: str) -> LiquidityPool:
        """Create a new liquidity pool"""
        pool_id = f"POOL-{uuid.uuid4().hex[:12].upper()}"
        symbol = f"{data.base_asset}/{data.quote_asset}"
        
        pool = LiquidityPool(
            pool_id=pool_id,
            name=data.name,
            symbol=symbol,
            base_asset=data.base_asset,
            quote_asset=data.quote_asset,
            fee_rate=Decimal(str(data.fee_rate)),
            base_reserve=Decimal(str(data.initial_base)),
            quote_reserve=Decimal(str(data.initial_quote))
        )
        
        if data.initial_base > 0 and data.initial_quote > 0:
            pool.total_liquidity = pool.base_reserve * pool.quote_reserve
        
        async with db.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO liquidity_pools (
                    pool_id, name, symbol, base_asset, quote_asset,
                    total_liquidity, base_reserve, quote_reserve, fee_rate, status, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW())
            ''', pool.pool_id, pool.name, pool.symbol, pool.base_asset, pool.quote_asset,
                float(pool.total_liquidity), float(pool.base_reserve), float(pool.quote_reserve),
                float(pool.fee_rate), pool.status
            )
        
        await admin_controller.log_action(admin_id, "create_pool", "liquidity_pool", pool_id, None, data.dict())
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
                    base_reserve = $1, quote_reserve = $2, total_liquidity = $3, providers = $4
                WHERE pool_id = $5
            ''', float(new_base), float(new_quote), float(new_total), json.dumps(providers), pool_id)
        
        return True
    
    async def remove_liquidity(self, pool_id: str, user_id: str, share_percent: Decimal) -> Dict:
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
        
        return {"base_amount": float(base_out), "quote_amount": float(quote_out)}
    
    async def import_liquidity_from_exchange(self, exchange: str, pairs: List[str], admin_id: str) -> Dict:
        """Import liquidity from external exchange"""
        imported = []
        for pair in pairs:
            base, quote = pair.split('/') if '/' in pair else (pair[:3], pair[3:])
            pool_data = CreateLiquidityPoolRequest(
                name=f"{base}/{quote} Pool",
                base_asset=base,
                quote_asset=quote
            )
            try:
                pool = await self.create_pool(pool_data, admin_id)
                imported.append(pair)
            except Exception as e:
                logger.error(f"Failed to create pool for {pair}: {e}")
        
        await admin_controller.log_action(admin_id, "import_liquidity", "exchange", exchange, None, {"pairs": imported})
        return {"exchange": exchange, "imported": imported, "count": len(imported)}
    
    async def get_pools(self) -> List[LiquidityPool]:
        """Get all liquidity pools"""
        async with db.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM liquidity_pools WHERE status = 'active'")
        return [self._row_to_pool(row) for row in rows]
    
    def _row_to_pool(self, row) -> LiquidityPool:
        return LiquidityPool(
            pool_id=row['pool_id'],
            name=row['name'],
            symbol=row['symbol'],
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

# ==================== FEE MANAGER ====================

class FeeManager:
    async def set_fee(self, data: SetFeeRequest, admin_id: str) -> FeeStructure:
        """Set fee for tier and type"""
        fee_id = f"FEE-{uuid.uuid4().hex[:12].upper()}"
        
        fee = FeeStructure(
            fee_id=fee_id,
            user_tier=data.user_tier,
            trading_type=TradingType(data.trading_type),
            fee_type=FeeType(data.fee_type),
            fee_value=Decimal(str(data.fee_value)),
            min_fee=Decimal(str(data.min_fee)),
            max_fee=Decimal(str(data.max_fee))
        )
        
        async with db.pool.acquire() as conn:
            # Check if exists
            existing = await conn.fetchrow('''
                SELECT * FROM fee_structure 
                WHERE user_tier = $1 AND trading_type = $2 AND fee_type = $3
            ''', data.user_tier, data.trading_type, data.fee_type)
            
            if existing:
                await conn.execute('''
                    UPDATE fee_structure SET fee_value = $1, min_fee = $2, max_fee = $3
                    WHERE fee_id = $4
                ''', float(fee.fee_value), float(fee.min_fee), float(fee.max_fee), existing['fee_id'])
                fee.fee_id = existing['fee_id']
            else:
                await conn.execute('''
                    INSERT INTO fee_structure (fee_id, user_tier, trading_type, fee_type, fee_value, min_fee, max_fee, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
                ''', fee.fee_id, fee.user_tier, fee.trading_type.value, fee.fee_type.value,
                    float(fee.fee_value), float(fee.min_fee), float(fee.max_fee))
        
        await admin_controller.log_action(admin_id, "set_fee", "fee_structure", fee.fee_id, None, data.dict())
        return fee
    
    async def calculate_fee(self, user_id: str, symbol: str, order_value: Decimal, 
                           trading_type: TradingType, is_maker: bool) -> Decimal:
        """Calculate fee for an order"""
        async with db.pool.acquire() as conn:
            user = await conn.fetchrow("SELECT tier FROM users WHERE user_id = $1", user_id)
            tier = user['tier'] if user else 'regular'
            
            fee_type = FeeType.MAKER if is_maker else FeeType.TAKER
            fee_struct = await conn.fetchrow('''
                SELECT * FROM fee_structure 
                WHERE user_tier = $1 AND trading_type = $2 AND fee_type = $3
            ''', tier, trading_type.value, fee_type.value)
            
            if not fee_struct:
                # Default fee
                return order_value * Decimal("0.001")
            
            fee = order_value * Decimal(str(fee_struct['fee_value']))
            return max(min(fee, Decimal(str(fee_struct['max_fee']))), Decimal(str(fee_struct['min_fee'])))
    
    async def get_fees(self, user_tier: str = None) -> List[FeeStructure]:
        """Get all fees"""
        async with db.pool.acquire() as conn:
            if user_tier:
                rows = await conn.fetch("SELECT * FROM fee_structure WHERE user_tier = $1", user_tier)
            else:
                rows = await conn.fetch("SELECT * FROM fee_structure")
        return [self._row_to_fee(row) for row in rows]
    
    def _row_to_fee(self, row) -> FeeStructure:
        return FeeStructure(
            fee_id=row['fee_id'],
            user_tier=row['user_tier'],
            trading_type=TradingType(row['trading_type']),
            fee_type=FeeType(row['fee_type']),
            fee_value=Decimal(str(row['fee_value'])),
            min_fee=Decimal(str(row['min_fee'])),
            max_fee=Decimal(str(row['max_fee']))
        )

fee_manager = FeeManager()

# ==================== USER MANAGER ====================

class UserManager:
    async def manage_user(self, data: ManageUserRequest, admin_id: str) -> Dict:
        """Manage user account"""
        async with db.pool.acquire() as conn:
            user = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", data.user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            old_status = user['status']
            
            actions = {
                "suspend": UserStatus.SUSPENDED,
                "ban": UserStatus.BANNED,
                "freeze": UserStatus.FROZEN,
                "activate": UserStatus.ACTIVE,
                "verify": UserStatus.VERIFIED
            }
            
            if data.action not in actions:
                raise HTTPException(status_code=400, detail="Invalid action")
            
            new_status = actions[data.action]
            
            await conn.execute('''
                UPDATE users SET status = $1, updated_at = NOW() WHERE user_id = $2
            ''', new_status.value, data.user_id)
        
        await admin_controller.log_action(admin_id, f"user_{data.action}", "user", data.user_id, 
                                          {"status": old_status}, {"status": new_status.value, "reason": data.reason})
        
        return {"user_id": data.user_id, "old_status": old_status, "new_status": new_status.value}
    
    async def update_user_tier(self, user_id: str, tier: str, admin_id: str) -> Dict:
        """Update user tier"""
        async with db.pool.acquire() as conn:
            old_tier = await conn.fetchval("SELECT tier FROM users WHERE user_id = $1", user_id)
            await conn.execute("UPDATE users SET tier = $1, updated_at = NOW() WHERE user_id = $2", tier, user_id)
        
        await admin_controller.log_action(admin_id, "update_tier", "user", user_id, {"tier": old_tier}, {"tier": tier})
        return {"user_id": user_id, "old_tier": old_tier, "new_tier": tier}
    
    async def get_users(self, status: str = None, limit: int = 100) -> List[User]:
        """Get users"""
        async with db.pool.acquire() as conn:
            if status:
                rows = await conn.fetch("SELECT * FROM users WHERE status = $1 LIMIT $2", status, limit)
            else:
                rows = await conn.fetch("SELECT * FROM users LIMIT $1", limit)
        return [self._row_to_user(row) for row in rows]
    
    def _row_to_user(self, row) -> User:
        return User(
            user_id=row['user_id'],
            email=row['email'],
            username=row['username'],
            role=UserRole(row['role']),
            status=UserStatus(row['status']),
            kyc_level=row['kyc_level'],
            tier=row['tier'],
            total_volume_30d=Decimal(str(row['total_volume_30d'])),
            total_trades=row['total_trades']
        )

user_manager = UserManager()

# ==================== EXCHANGE CONFIG MANAGER ====================

class ExchangeConfigManager:
    async def get_config(self) -> ExchangeConfig:
        """Get exchange configuration"""
        async with db.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM exchange_config WHERE exchange_id = 'TIGEREX'")
            if row:
                return self._row_to_config(row)
            
            # Create default config
            config = ExchangeConfig(exchange_id="TIGEREX")
            await conn.execute('''
                INSERT INTO exchange_config (exchange_id, name, status, created_at)
                VALUES ('TIGEREX', 'TigerEx', 'active', NOW())
            ''')
            return config
    
    async def update_config(self, data: ExchangeConfigRequest, admin_id: str) -> ExchangeConfig:
        """Update exchange configuration"""
        updates = []
        params = []
        idx = 1
        
        if data.name:
            updates.append(f"name = ${idx}")
            params.append(data.name)
            idx += 1
        if data.status:
            updates.append(f"status = ${idx}")
            params.append(data.status)
            idx += 1
        if data.maintenance_mode is not None:
            updates.append(f"maintenance_mode = ${idx}")
            params.append(data.maintenance_mode)
            idx += 1
        if data.trading_enabled is not None:
            updates.append(f"trading_enabled = ${idx}")
            params.append(data.trading_enabled)
            idx += 1
        if data.withdrawals_enabled is not None:
            updates.append(f"withdrawals_enabled = ${idx}")
            params.append(data.withdrawals_enabled)
            idx += 1
        if data.deposits_enabled is not None:
            updates.append(f"deposits_enabled = ${idx}")
            params.append(data.deposits_enabled)
            idx += 1
        
        updates.append("updated_at = NOW()")
        params.append("TIGEREX")
        
        if updates:
            async with db.pool.acquire() as conn:
                await conn.execute(
                    f"UPDATE exchange_config SET {', '.join(updates)} WHERE exchange_id = ${idx}",
                    *params
                )
        
        await admin_controller.log_action(admin_id, "update_config", "exchange", "TIGEREX", None, data.dict())
        return await self.get_config()
    
    def _row_to_config(self, row) -> ExchangeConfig:
        return ExchangeConfig(
            exchange_id=row['exchange_id'],
            name=row['name'],
            status=row['status'],
            maintenance_mode=row['maintenance_mode'],
            trading_enabled=row['trading_enabled'],
            withdrawals_enabled=row['withdrawals_enabled'],
            deposits_enabled=row['deposits_enabled'],
            registration_enabled=row['registration_enabled'],
            kyc_required=row['kyc_required'],
            default_leverage=Decimal(str(row['default_leverage'])),
            max_total_leverage=Decimal(str(row['max_total_leverage']))
        )

exchange_config_manager = ExchangeConfigManager()

# ==================== API ENDPOINTS ====================

@app.on_event("startup")
async def startup():
    await db.initialize()
    logger.info("TigerEx Unified Trading System initialized successfully")

# Health Check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "unified-trading-system", "timestamp": datetime.utcnow().isoformat()}

# Exchange Config
@app.get("/config")
async def get_config():
    """Get exchange configuration"""
    config = await exchange_config_manager.get_config()
    return {"success": True, "data": config}

@app.put("/config")
async def update_config(
    data: ExchangeConfigRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update exchange configuration"""
    admin_id = "admin_123"
    config = await exchange_config_manager.update_config(data, admin_id)
    return {"success": True, "data": config}

# Trading Pairs
@app.post("/admin/pairs")
async def create_pair(
    data: CreateTradingPairRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a new trading pair"""
    admin_id = "admin_123"
    pair = await pair_manager.create_pair(data, admin_id)
    return {"success": True, "data": {"pair_id": pair.pair_id, "symbol": pair.symbol}}

@app.get("/pairs")
async def get_pairs(status: str = None, trading_type: str = None):
    """Get all trading pairs"""
    pairs = await pair_manager.get_all_pairs(status, trading_type)
    return {"success": True, "data": [{"symbol": p.symbol, "status": p.status.value, "types": [t.value for t in p.trading_types]} for p in pairs]}

@app.put("/admin/pairs/{symbol}")
async def update_pair(
    symbol: str,
    data: UpdateTradingPairRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update trading pair"""
    admin_id = "admin_123"
    pair = await pair_manager.update_pair(symbol, data, admin_id)
    return {"success": True, "data": pair}

@app.post("/admin/pairs/{symbol}/halt")
async def halt_pair(symbol: str, reason: str = "", credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Halt trading pair"""
    admin_id = "admin_123"
    await pair_manager.halt_pair(symbol, reason, admin_id)
    return {"success": True}

@app.post("/admin/pairs/{symbol}/resume")
async def resume_pair(symbol: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Resume trading pair"""
    admin_id = "admin_123"
    await pair_manager.resume_pair(symbol, admin_id)
    return {"success": True}

@app.delete("/admin/pairs/{symbol}")
async def delist_pair(symbol: str, reason: str = "", credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Delist trading pair"""
    admin_id = "admin_123"
    await pair_manager.delist_pair(symbol, reason, admin_id)
    return {"success": True}

@app.post("/admin/pairs/import")
async def import_pairs(
    data: ImportFromExchangeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Import trading pairs from exchange"""
    admin_id = "admin_123"
    result = await pair_manager.import_from_exchange(data.exchange, data.pairs, data.trading_type, admin_id)
    return {"success": True, "data": result}

# Liquidity
@app.post("/admin/liquidity/pools")
async def create_pool(
    data: CreateLiquidityPoolRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create liquidity pool"""
    admin_id = "admin_123"
    pool = await liquidity_manager.create_pool(data, admin_id)
    return {"success": True, "data": {"pool_id": pool.pool_id, "name": pool.name}}

@app.get("/liquidity/pools")
async def get_pools():
    """Get all liquidity pools"""
    pools = await liquidity_manager.get_pools()
    return {"success": True, "data": [{"pool_id": p.pool_id, "symbol": p.symbol, "total_liquidity": str(p.total_liquidity)} for p in pools]}

@app.post("/liquidity/pools/{pool_id}/add")
async def add_liquidity(
    pool_id: str,
    base_amount: float,
    quote_amount: float,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Add liquidity to pool"""
    user_id = "user_123"
    await liquidity_manager.add_liquidity(pool_id, user_id, Decimal(str(base_amount)), Decimal(str(quote_amount)))
    return {"success": True}

@app.post("/admin/liquidity/import")
async def import_liquidity(
    exchange: str,
    pairs: List[str],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Import liquidity from exchange"""
    admin_id = "admin_123"
    result = await liquidity_manager.import_liquidity_from_exchange(exchange, pairs, admin_id)
    return {"success": True, "data": result}

# Fees
@app.post("/admin/fees")
async def set_fee(
    data: SetFeeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Set fee"""
    admin_id = "admin_123"
    fee = await fee_manager.set_fee(data, admin_id)
    return {"success": True, "data": {"fee_id": fee.fee_id}}

@app.get("/fees")
async def get_fees(user_tier: str = None):
    """Get all fees"""
    fees = await fee_manager.get_fees(user_tier)
    return {"success": True, "data": fees}

# Users
@app.post("/admin/users/manage")
async def manage_user(
    data: ManageUserRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Manage user account"""
    admin_id = "admin_123"
    result = await user_manager.manage_user(data, admin_id)
    return {"success": True, "data": result}

@app.get("/users")
async def get_users(status: str = None, limit: int = 100):
    """Get users"""
    users = await user_manager.get_users(status, limit)
    return {"success": True, "data": users}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
