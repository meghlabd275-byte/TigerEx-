#!/usr/bin/env python3
"""
TigerEx CFD Trading Service
Complete CFD trading with MT5 integration, Stock Tokens, and TradFi features
Based on TigerEx/Bybit CFD trading systems
Port: 8190
"""

from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import asyncio
import asyncpg
import redis.asyncio as redis
import structlog
import uvicorn
import os
import json
import jwt
import hashlib
import secrets
import uuid
import numpy as np
from collections import defaultdict

# @file main.py
# @author TigerEx Development Team
# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/tigerex")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "tigerex-super-secret-jwt-key-2024")
JWT_ALGORITHM = "HS256"

# Global connections
db_pool = None
redis_client = None

security = HTTPBearer()

# ============================================================================
# ENUMS
# ============================================================================

class CFDType(str, Enum):
    STOCK = "stock"
    INDEX = "index"
    COMMODITY = "commodity"
    FOREX = "forex"
    METAL = "metal"
    CRYPTO = "crypto"
    ETF = "etf"
    BOND = "bond"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"
    OCO = "oco"  # One-Cancels-Other
    IFD = "ifd"  # If-Done
    IFO = "ifo"  # If-Done + OCO

class PositionSide(str, Enum):
    LONG = "long"
    SHORT = "short"

class OrderStatus(str, Enum):
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class PositionStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    LIQUIDATED = "liquidated"
    MARGIN_CALL = "margin_call"

class MT5AccountType(str, Enum):
    STANDARD = "standard"
    ECN = "ecn"
    CENT = "cent"
    DEMO = "demo"

class TradingSession(str, Enum):
    ASIAN = "asian"
    EUROPEAN = "european"
    AMERICAN = "american"
    TWENTY_FOUR_SEVEN = "24/7"

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class CFDInstrument(BaseModel):
    symbol: str
    name: str
    cfd_type: CFDType
    base_currency: str = "USD"
    quote_currency: str = "USD"
    tick_size: Decimal = Decimal("0.00001")
    tick_value: Decimal = Decimal("1.0")
    contract_size: Decimal = Decimal("100")
    min_lot: Decimal = Decimal("0.01")
    max_lot: Decimal = Decimal("100")
    lot_step: Decimal = Decimal("0.01")
    leverage_max: int = 500
    margin_requirement: Decimal = Decimal("0.002")
    spread_type: str = "floating"  # floating, fixed
    typical_spread: Decimal = Decimal("0.0001")
    swap_long: Decimal = Decimal("-0.001")
    swap_short: Decimal = Decimal("-0.001")
    swap_enabled: bool = True
    trading_sessions: List[TradingSession] = [TradingSession.TWENTY_FOUR_SEVEN]
    is_active: bool = True
    description: Optional[str] = None
    exchange: Optional[str] = None  # For stocks

class CFDOrder(BaseModel):
    order_id: str
    user_id: str
    mt5_account_id: Optional[str] = None
    symbol: str
    order_type: OrderType
    position_side: PositionSide
    lots: Decimal
    entry_price: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    trailing_stop: Optional[Decimal] = None
    trailing_step: Optional[Decimal] = None
    leverage: int = 100
    status: OrderStatus
    filled_lots: Decimal = Decimal("0")
    average_price: Optional[Decimal] = None
    commission: Decimal = Decimal("0")
    swap: Decimal = Decimal("0")
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

class CFDPosition(BaseModel):
    position_id: str
    user_id: str
    mt5_account_id: Optional[str] = None
    symbol: str
    position_side: PositionSide
    lots: Decimal
    entry_price: Decimal
    current_price: Decimal
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    trailing_stop: Optional[Decimal] = None
    unrealized_pnl: Decimal = Decimal("0")
    realized_pnl: Decimal = Decimal("0")
    swap: Decimal = Decimal("0")
    commission: Decimal = Decimal("0")
    margin: Decimal = Decimal("0")
    leverage: int
    status: PositionStatus
    opened_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MT5Account(BaseModel):
    account_id: str
    user_id: str
    account_number: str
    account_type: MT5AccountType
    broker_name: str = "TigerEx"
    server_name: str = "TigerEx-Live"
    balance: Decimal = Decimal("0")
    equity: Decimal = Decimal("0")
    margin: Decimal = Decimal("0")
    free_margin: Decimal = Decimal("0")
    margin_level: Decimal = Decimal("0")
    unrealized_pnl: Decimal = Decimal("0")
    currency: str = "USD"
    leverage: int = 100
    is_active: bool = True
    is_demo: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_trade_at: Optional[datetime] = None

class StockToken(BaseModel):
    token_symbol: str
    underlying_symbol: str
    underlying_name: str
    token_type: str = "stock"  # stock, etf, index
    price_per_token: Decimal
    tokens_issued: Decimal
    min_purchase: Decimal = Decimal("0.01")
    trading_enabled: bool = True
    dividend_enabled: bool = True
    voting_rights: bool = False
    is_active: bool = True

class CreateMT5AccountRequest(BaseModel):
    account_type: MT5AccountType = MT5AccountType.STANDARD
    currency: str = "USD"
    leverage: int = 100

class CreateCFDOrderRequest(BaseModel):
    symbol: str
    order_type: OrderType
    position_side: PositionSide
    lots: Decimal
    entry_price: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    trailing_stop: Optional[Decimal] = None
    leverage: int = 100
    comment: Optional[str] = None

class UpdatePositionRequest(BaseModel):
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    trailing_stop: Optional[Decimal] = None

class ClosePositionRequest(BaseModel):
    lots: Optional[Decimal] = None  # Partial close, None for full close

# ============================================================================
# CFD TRADING ENGINE
# ============================================================================

class CFDTradingEngine:
    """Advanced CFD Trading Engine with MT5 Integration"""
    
    def __init__(self):
        self.instruments: Dict[str, CFDInstrument] = {}
        self.prices: Dict[str, Dict[str, Decimal]] = {}  # symbol -> {bid, ask}
        self.positions: Dict[str, CFDPosition] = {}
        self.orders: Dict[str, CFDOrder] = {}
        self.mt5_accounts: Dict[str, MT5Account] = {}
        self.user_positions: Dict[str, List[str]] = defaultdict(list)
        self.user_orders: Dict[str, List[str]] = defaultdict(list)
        self.user_mt5_accounts: Dict[str, List[str]] = defaultdict(list)
        self.stock_tokens: Dict[str, StockToken] = {}
        self.websockets: List[WebSocket] = []
        
        # Initialize default instruments
        self._initialize_instruments()
        self._initialize_stock_tokens()
        self._start_price_feeds()
    
    def _initialize_instruments(self):
        """Initialize CFD instruments"""
        
        # Stock CFDs
        stocks = [
            ("AAPL", "Apple Inc.", 185.50, 20),
            ("TSLA", "Tesla Inc.", 245.30, 20),
            ("GOOGL", "Alphabet Inc.", 140.20, 20),
            ("AMZN", "Amazon.com Inc.", 178.50, 20),
            ("MSFT", "Microsoft Corp.", 415.80, 20),
            ("META", "Meta Platforms Inc.", 505.60, 20),
            ("NVDA", "NVIDIA Corp.", 875.40, 20),
            ("AMD", "AMD Inc.", 165.30, 20),
            ("NFLX", "Netflix Inc.", 628.90, 20),
            ("DIS", "Walt Disney Co.", 112.40, 20),
        ]
        
        for symbol, name, price, max_leverage in stocks:
            self.instruments[symbol] = CFDInstrument(
                symbol=symbol,
                name=name,
                cfd_type=CFDType.STOCK,
                base_currency="USD",
                quote_currency="USD",
                tick_size=Decimal("0.01"),
                contract_size=Decimal("1"),
                min_lot=Decimal("1"),
                max_lot=Decimal("10000"),
                leverage_max=max_leverage,
                margin_requirement=Decimal("0.05"),
                typical_spread=Decimal("0.02"),
                trading_sessions=[TradingSession.AMERICAN],
                exchange="NASDAQ/NYSE"
            )
            self.prices[symbol] = {
                "bid": Decimal(str(price)) - Decimal("0.02"),
                "ask": Decimal(str(price)) + Decimal("0.02")
            }
        
        # Index CFDs
        indices = [
            ("SPX500", "S&P 500", 5250.50, 100),
            ("NAS100", "Nasdaq 100", 18350.75, 100),
            ("DJI30", "Dow Jones 30", 39500.25, 100),
            ("UK100", "FTSE 100", 8150.50, 100),
            ("GER40", "DAX 40", 18250.75, 100),
            ("FRA40", "CAC 40", 8050.30, 100),
            ("JPN225", "Nikkei 225", 40250.50, 100),
            ("AUS200", "ASX 200", 7650.25, 100),
            ("HK50", "Hang Seng 50", 17250.50, 100),
            ("CN50", "China A50", 12250.75, 100),
        ]
        
        for symbol, name, price, max_leverage in indices:
            self.instruments[symbol] = CFDInstrument(
                symbol=symbol,
                name=name,
                cfd_type=CFDType.INDEX,
                base_currency="USD",
                quote_currency="USD",
                tick_size=Decimal("0.25"),
                contract_size=Decimal("1"),
                min_lot=Decimal("0.1"),
                max_lot=Decimal("1000"),
                leverage_max=max_leverage,
                margin_requirement=Decimal("0.01"),
                typical_spread=Decimal("0.5"),
                trading_sessions=[TradingSession.ASIAN, TradingSession.EUROPEAN, TradingSession.AMERICAN]
            )
            self.prices[symbol] = {
                "bid": Decimal(str(price)) - Decimal("0.5"),
                "ask": Decimal(str(price)) + Decimal("0.5")
            }
        
        # Metals
        metals = [
            ("XAU/USD", "Gold", 2350.50, 400),
            ("XAG/USD", "Silver", 28.50, 300),
            ("XPT/USD", "Platinum", 985.50, 100),
            ("XPD/USD", "Palladium", 1025.30, 100),
        ]
        
        for symbol, name, price, max_leverage in metals:
            self.instruments[symbol] = CFDInstrument(
                symbol=symbol,
                name=name,
                cfd_type=CFDType.METAL,
                base_currency="USD",
                quote_currency="USD",
                tick_size=Decimal("0.01"),
                contract_size=Decimal("100"),
                min_lot=Decimal("0.01"),
                max_lot=Decimal("500"),
                leverage_max=max_leverage,
                margin_requirement=Decimal("0.005"),
                typical_spread=Decimal("0.30"),
                trading_sessions=[TradingSession.TWENTY_FOUR_SEVEN]
            )
            self.prices[symbol] = {
                "bid": Decimal(str(price)) - Decimal("0.30"),
                "ask": Decimal(str(price)) + Decimal("0.30")
            }
        
        # Forex
        forex = [
            ("EUR/USD", "Euro/US Dollar", 1.0850, 500),
            ("GBP/USD", "British Pound/US Dollar", 1.2720, 500),
            ("USD/JPY", "US Dollar/Japanese Yen", 154.50, 500),
            ("USD/CHF", "US Dollar/Swiss Franc", 0.9050, 500),
            ("AUD/USD", "Australian Dollar/US Dollar", 0.6580, 500),
            ("USD/CAD", "US Dollar/Canadian Dollar", 1.3650, 500),
            ("NZD/USD", "New Zealand Dollar/US Dollar", 0.6050, 500),
            ("EUR/GBP", "Euro/British Pound", 0.8530, 500),
            ("EUR/JPY", "Euro/Japanese Yen", 167.50, 500),
            ("GBP/JPY", "British Pound/Japanese Yen", 196.50, 500),
        ]
        
        for symbol, name, price, max_leverage in forex:
            pip = Decimal("0.0001") if "JPY" not in symbol else Decimal("0.01")
            self.instruments[symbol] = CFDInstrument(
                symbol=symbol,
                name=name,
                cfd_type=CFDType.FOREX,
                base_currency=symbol.split("/")[0],
                quote_currency=symbol.split("/")[1],
                tick_size=pip,
                contract_size=Decimal("100000"),
                min_lot=Decimal("0.01"),
                max_lot=Decimal("1000"),
                leverage_max=max_leverage,
                margin_requirement=Decimal("0.002"),
                typical_spread=pip * Decimal("1.5"),
                trading_sessions=[TradingSession.TWENTY_FOUR_SEVEN]
            )
            self.prices[symbol] = {
                "bid": Decimal(str(price)) - pip,
                "ask": Decimal(str(price)) + pip
            }
        
        # Commodities
        commodities = [
            ("OIL/USD", "Crude Oil WTI", 78.50, 200),
            ("BRENT/USD", "Brent Crude Oil", 82.50, 200),
            ("NATGAS/USD", "Natural Gas", 2.15, 150),
            ("COPPER/USD", "Copper", 4.25, 100),
        ]
        
        for symbol, name, price, max_leverage in commodities:
            self.instruments[symbol] = CFDInstrument(
                symbol=symbol,
                name=name,
                cfd_type=CFDType.COMMODITY,
                base_currency="USD",
                quote_currency="USD",
                tick_size=Decimal("0.01"),
                contract_size=Decimal("1000"),
                min_lot=Decimal("0.1"),
                max_lot=Decimal("500"),
                leverage_max=max_leverage,
                margin_requirement=Decimal("0.02"),
                typical_spread=Decimal("0.03"),
                trading_sessions=[TradingSession.AMERICAN]
            )
            self.prices[symbol] = {
                "bid": Decimal(str(price)) - Decimal("0.03"),
                "ask": Decimal(str(price)) + Decimal("0.03")
            }
        
        # Crypto CFDs
        crypto = [
            ("BTC/USD", "Bitcoin", 67500.00, 100),
            ("ETH/USD", "Ethereum", 3450.00, 100),
            ("BNB/USD", "BNB", 605.50, 50),
            ("XRP/USD", "Ripple", 0.5250, 50),
            ("SOL/USD", "Solana", 175.50, 50),
        ]
        
        for symbol, name, price, max_leverage in crypto:
            self.instruments[symbol] = CFDInstrument(
                symbol=symbol,
                name=name,
                cfd_type=CFDType.CRYPTO,
                base_currency=symbol.split("/")[0],
                quote_currency="USD",
                tick_size=Decimal("0.01"),
                contract_size=Decimal("1"),
                min_lot=Decimal("0.001"),
                max_lot=Decimal("1000"),
                leverage_max=max_leverage,
                margin_requirement=Decimal("0.01"),
                typical_spread=Decimal("0.5"),
                trading_sessions=[TradingSession.TWENTY_FOUR_SEVEN]
            )
            self.prices[symbol] = {
                "bid": Decimal(str(price)) - Decimal("10"),
                "ask": Decimal(str(price)) + Decimal("10")
            }
    
    def _initialize_stock_tokens(self):
        """Initialize stock tokens for tokenized stock trading"""
        
        stock_tokens_data = [
            ("AAPL", "Apple Inc.", Decimal("185.50")),
            ("TSLA", "Tesla Inc.", Decimal("245.30")),
            ("GOOGL", "Alphabet Inc.", Decimal("140.20")),
            ("AMZN", "Amazon.com Inc.", Decimal("178.50")),
            ("MSFT", "Microsoft Corp.", Decimal("415.80")),
            ("META", "Meta Platforms Inc.", Decimal("505.60")),
            ("NVDA", "NVIDIA Corp.", Decimal("875.40")),
            ("MSTR", "MicroStrategy Inc.", Decimal("1625.50")),
            ("COIN", "Coinbase Global", Decimal("245.80")),
            ("TSLA", "Tesla Inc.", Decimal("245.30")),
        ]
        
        for symbol, name, price in stock_tokens_data:
            token_symbol = f"{symbol}UDT"
            self.stock_tokens[token_symbol] = StockToken(
                token_symbol=token_symbol,
                underlying_symbol=symbol,
                underlying_name=name,
                price_per_token=price,
                tokens_issued=Decimal("1000000"),
                min_purchase=Decimal("0.01")
            )
    
    def _start_price_feeds(self):
        """Start price feed simulation"""
        asyncio.create_task(self._update_prices())
    
    async def _update_prices(self):
        """Simulate real-time price updates"""
        while True:
            try:
                for symbol in self.prices:
                    if symbol in self.instruments:
                        instrument = self.instruments[symbol]
                        current = self.prices[symbol]
                        
                        # Random price movement
                        tick_size = instrument.tick_size
                        change = np.random.normal(0, float(tick_size) * 5)
                        
                        mid_price = (current["bid"] + current["ask"]) / 2
                        new_mid = mid_price + Decimal(str(change))
                        spread = instrument.typical_spread
                        
                        self.prices[symbol] = {
                            "bid": new_mid - spread / 2,
                            "ask": new_mid + spread / 2
                        }
                
                # Broadcast price updates
                await self._broadcast_prices()
                
                await asyncio.sleep(0.5)  # Update every 0.5 seconds
                
            except Exception as e:
                logger.error(f"Price update error: {e}")
                await asyncio.sleep(1)
    
    async def _broadcast_prices(self):
        """Broadcast price updates to WebSocket clients"""
        if self.websockets:
            message = {
                "type": "price_update",
                "data": {symbol: {"bid": str(price["bid"]), "ask": str(price["ask"])} 
                        for symbol, price in self.prices.items()},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            for ws in self.websockets:
                try:
                    await ws.send_json(message)
                except:
                    pass
    
    async def create_mt5_account(self, user_id: str, account_type: MT5AccountType, 
                                  currency: str = "USD", leverage: int = 100) -> MT5Account:
        """Create MT5 trading account"""
        
        account_id = str(uuid.uuid4())
        account_number = f"8{secrets.randbelow(9000000) + 1000000}"  # 8-digit account number
        
        account = MT5Account(
            account_id=account_id,
            user_id=user_id,
            account_number=account_number,
            account_type=account_type,
            currency=currency,
            leverage=leverage,
            is_demo=(account_type == MT5AccountType.DEMO)
        )
        
        self.mt5_accounts[account_id] = account
        self.user_mt5_accounts[user_id].append(account_id)
        
        return account
    
    async def get_instruments(self, cfd_type: Optional[CFDType] = None) -> List[CFDInstrument]:
        """Get all CFD instruments"""
        if cfd_type:
            return [inst for inst in self.instruments.values() if inst.cfd_type == cfd_type]
        return list(self.instruments.values())
    
    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current quote for symbol"""
        if symbol not in self.prices or symbol not in self.instruments:
            return None
        
        price = self.prices[symbol]
        instrument = self.instruments[symbol]
        
        return {
            "symbol": symbol,
            "bid": str(price["bid"]),
            "ask": str(price["ask"]),
            "spread": str(price["ask"] - price["bid"]),
            "tick_size": str(instrument.tick_size),
            "contract_size": str(instrument.contract_size),
            "leverage_max": instrument.leverage_max,
            "min_lot": str(instrument.min_lot),
            "max_lot": str(instrument.max_lot),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def place_order(self, user_id: str, request: CreateCFDOrderRequest) -> CFDOrder:
        """Place CFD order"""
        
        if request.symbol not in self.instruments:
            raise HTTPException(status_code=400, detail="Invalid symbol")
        
        instrument = self.instruments[request.symbol]
        price = self.prices[request.symbol]
        
        # Validate lots
        if request.lots < instrument.min_lot or request.lots > instrument.max_lot:
            raise HTTPException(status_code=400, detail=f"Lot size must be between {instrument.min_lot} and {instrument.max_lot}")
        
        # Validate leverage
        if request.leverage > instrument.leverage_max:
            raise HTTPException(status_code=400, detail=f"Maximum leverage is {instrument.leverage_max}")
        
        # Determine execution price
        if request.order_type == OrderType.MARKET:
            if request.position_side == PositionSide.LONG:
                execution_price = price["ask"]
            else:
                execution_price = price["bid"]
        else:
            if not request.entry_price:
                raise HTTPException(status_code=400, detail="Entry price required for limit orders")
            execution_price = request.entry_price
        
        order_id = str(uuid.uuid4())
        
        order = CFDOrder(
            order_id=order_id,
            user_id=user_id,
            symbol=request.symbol,
            order_type=request.order_type,
            position_side=request.position_side,
            lots=request.lots,
            entry_price=execution_price,
            stop_loss=request.stop_loss,
            take_profit=request.take_profit,
            trailing_stop=request.trailing_stop,
            leverage=request.leverage,
            status=OrderStatus.OPEN if request.order_type == OrderType.MARKET else OrderStatus.PENDING
        )
        
        self.orders[order_id] = order
        self.user_orders[user_id].append(order_id)
        
        # Execute market orders immediately
        if request.order_type == OrderType.MARKET:
            await self._execute_order(order)
        
        return order
    
    async def _execute_order(self, order: CFDOrder):
        """Execute order and create position"""
        
        instrument = self.instruments[order.symbol]
        price = self.prices[order.symbol]
        
        # Calculate margin
        position_value = order.entry_price * order.lots * instrument.contract_size
        margin = position_value / order.leverage
        
        # Calculate commission
        commission = position_value * Decimal("0.00005")  # 0.005% commission
        
        position_id = str(uuid.uuid4())
        
        position = CFDPosition(
            position_id=position_id,
            user_id=order.user_id,
            symbol=order.symbol,
            position_side=order.position_side,
            lots=order.lots,
            entry_price=order.entry_price,
            current_price=order.entry_price,
            stop_loss=order.stop_loss,
            take_profit=order.take_profit,
            trailing_stop=order.trailing_stop,
            leverage=order.leverage,
            margin=margin,
            commission=commission,
            status=PositionStatus.OPEN
        )
        
        self.positions[position_id] = position
        self.user_positions[order.user_id].append(position_id)
        
        # Update order status
        order.status = OrderStatus.FILLED
        order.filled_lots = order.lots
        order.average_price = order.entry_price
        order.commission = commission
    
    async def get_positions(self, user_id: str) -> List[CFDPosition]:
        """Get all open positions for user"""
        position_ids = self.user_positions.get(user_id, [])
        return [self.positions[pid] for pid in position_ids if pid in self.positions and self.positions[pid].status == PositionStatus.OPEN]
    
    async def get_orders(self, user_id: str, status: Optional[OrderStatus] = None) -> List[CFDOrder]:
        """Get orders for user"""
        order_ids = self.user_orders.get(user_id, [])
        orders = [self.orders[oid] for oid in order_ids if oid in self.orders]
        
        if status:
            orders = [o for o in orders if o.status == status]
        
        return orders
    
    async def close_position(self, user_id: str, position_id: str, lots: Optional[Decimal] = None) -> Dict[str, Any]:
        """Close position"""
        
        if position_id not in self.positions:
            raise HTTPException(status_code=404, detail="Position not found")
        
        position = self.positions[position_id]
        
        if position.user_id != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        if position.status != PositionStatus.OPEN:
            raise HTTPException(status_code=400, detail="Position already closed")
        
        price = self.prices[position.symbol]
        
        # Determine exit price
        if position.position_side == PositionSide.LONG:
            exit_price = price["bid"]
            pnl = (exit_price - position.entry_price) * position.lots
        else:
            exit_price = price["ask"]
            pnl = (position.entry_price - exit_price) * position.lots
        
        # Calculate final P&L
        commission = position.lots * Decimal("0.00005") * exit_price
        final_pnl = pnl - commission - position.swap
        
        position.status = PositionStatus.CLOSED
        position.realized_pnl = final_pnl
        position.updated_at = datetime.utcnow()
        
        return {
            "position_id": position_id,
            "exit_price": str(exit_price),
            "gross_pnl": str(pnl),
            "commission": str(commission),
            "swap": str(position.swap),
            "net_pnl": str(final_pnl),
            "status": "closed"
        }

# ============================================================================
# APP SETUP
# ============================================================================

app = FastAPI(
    title="TigerEx CFD Trading Service",
    description="Complete CFD trading with MT5 integration, Stock Tokens, and TradFi features",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize trading engine
trading_engine = CFDTradingEngine()

# ============================================================================
# AUTHENTICATION
# ============================================================================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token and return user"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {"user_id": user_id, "role": payload.get("role", "user"), "permissions": payload.get("permissions", [])}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token and return admin user"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        admin_id = payload.get("sub")
        role = payload.get("role")
        
        if not admin_id or role not in ["super_admin", "admin", "moderator"]:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {"admin_id": admin_id, "role": role, "permissions": payload.get("permissions", [])}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============================================================================
# MT5 ACCOUNT ENDPOINTS
# ============================================================================

@app.post("/api/cfd/mt5/create-account")
async def create_mt5_account(
    request: CreateMT5AccountRequest,
    user: dict = Depends(get_current_user)
):
    """Create MT5 trading account"""
    account = await trading_engine.create_mt5_account(
        user["user_id"],
        request.account_type,
        request.currency,
        request.leverage
    )
    
    return {
        "success": True,
        "message": "MT5 account created successfully",
        "account": {
            "account_id": account.account_id,
            "account_number": account.account_number,
            "account_type": account.account_type.value,
            "currency": account.currency,
            "leverage": account.leverage,
            "is_demo": account.is_demo
        }
    }

@app.get("/api/cfd/mt5/accounts")
async def get_mt5_accounts(user: dict = Depends(get_current_user)):
    """Get user's MT5 accounts"""
    account_ids = trading_engine.user_mt5_accounts.get(user["user_id"], [])
    accounts = [trading_engine.mt5_accounts[aid] for aid in account_ids if aid in trading_engine.mt5_accounts]
    
    return {
        "success": True,
        "accounts": [
            {
                "account_id": acc.account_id,
                "account_number": acc.account_number,
                "account_type": acc.account_type.value,
                "balance": str(acc.balance),
                "equity": str(acc.equity),
                "margin": str(acc.margin),
                "free_margin": str(acc.free_margin),
                "currency": acc.currency,
                "leverage": acc.leverage,
                "is_demo": acc.is_demo
            }
            for acc in accounts
        ]
    }

# ============================================================================
# CFD INSTRUMENT ENDPOINTS
# ============================================================================

@app.get("/api/cfd/instruments")
async def get_instruments(
    cfd_type: Optional[CFDType] = None,
    user: dict = Depends(get_current_user)
):
    """Get all CFD instruments"""
    instruments = await trading_engine.get_instruments(cfd_type)
    
    return {
        "success": True,
        "instruments": [
            {
                "symbol": inst.symbol,
                "name": inst.name,
                "type": inst.cfd_type.value,
                "base_currency": inst.base_currency,
                "quote_currency": inst.quote_currency,
                "tick_size": str(inst.tick_size),
                "contract_size": str(inst.contract_size),
                "min_lot": str(inst.min_lot),
                "max_lot": str(inst.max_lot),
                "leverage_max": inst.leverage_max,
                "margin_requirement": str(inst.margin_requirement),
                "trading_sessions": [s.value for s in inst.trading_sessions]
            }
            for inst in instruments
        ]
    }

@app.get("/api/cfd/quote/{symbol}")
async def get_quote(symbol: str, user: dict = Depends(get_current_user)):
    """Get quote for symbol"""
    quote = await trading_engine.get_quote(symbol)
    
    if not quote:
        raise HTTPException(status_code=404, detail="Symbol not found")
    
    return {"success": True, "quote": quote}

# ============================================================================
# CFD TRADING ENDPOINTS
# ============================================================================

@app.post("/api/cfd/order")
async def place_order(
    request: CreateCFDOrderRequest,
    user: dict = Depends(get_current_user)
):
    """Place CFD order"""
    order = await trading_engine.place_order(user["user_id"], request)
    
    return {
        "success": True,
        "message": "Order placed successfully",
        "order": {
            "order_id": order.order_id,
            "symbol": order.symbol,
            "type": order.order_type.value,
            "side": order.position_side.value,
            "lots": str(order.lots),
            "entry_price": str(order.entry_price),
            "status": order.status.value,
            "leverage": order.leverage
        }
    }

@app.get("/api/cfd/positions")
async def get_positions(user: dict = Depends(get_current_user)):
    """Get open positions"""
    positions = await trading_engine.get_positions(user["user_id"])
    
    return {
        "success": True,
        "positions": [
            {
                "position_id": pos.position_id,
                "symbol": pos.symbol,
                "side": pos.position_side.value,
                "lots": str(pos.lots),
                "entry_price": str(pos.entry_price),
                "current_price": str(pos.current_price),
                "unrealized_pnl": str(pos.unrealized_pnl),
                "margin": str(pos.margin),
                "leverage": pos.leverage,
                "stop_loss": str(pos.stop_loss) if pos.stop_loss else None,
                "take_profit": str(pos.take_profit) if pos.take_profit else None,
                "opened_at": pos.opened_at.isoformat()
            }
            for pos in positions
        ]
    }

@app.post("/api/cfd/position/{position_id}/close")
async def close_position(
    position_id: str,
    request: ClosePositionRequest = None,
    user: dict = Depends(get_current_user)
):
    """Close position"""
    lots = request.lots if request else None
    result = await trading_engine.close_position(user["user_id"], position_id, lots)
    
    return {"success": True, "result": result}

@app.get("/api/cfd/orders")
async def get_orders(
    status: Optional[OrderStatus] = None,
    user: dict = Depends(get_current_user)
):
    """Get orders"""
    orders = await trading_engine.get_orders(user["user_id"], status)
    
    return {
        "success": True,
        "orders": [
            {
                "order_id": order.order_id,
                "symbol": order.symbol,
                "type": order.order_type.value,
                "side": order.position_side.value,
                "lots": str(order.lots),
                "filled_lots": str(order.filled_lots),
                "entry_price": str(order.entry_price),
                "average_price": str(order.average_price) if order.average_price else None,
                "status": order.status.value,
                "created_at": order.created_at.isoformat()
            }
            for order in orders
        ]
    }

# ============================================================================
# STOCK TOKENS ENDPOINTS
# ============================================================================

@app.get("/api/cfd/stock-tokens")
async def get_stock_tokens(user: dict = Depends(get_current_user)):
    """Get all stock tokens"""
    tokens = list(trading_engine.stock_tokens.values())
    
    return {
        "success": True,
        "tokens": [
            {
                "token_symbol": token.token_symbol,
                "underlying_symbol": token.underlying_symbol,
                "underlying_name": token.underlying_name,
                "price_per_token": str(token.price_per_token),
                "min_purchase": str(token.min_purchase),
                "trading_enabled": token.trading_enabled
            }
            for token in tokens
        ]
    }

# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.post("/api/cfd/admin/instrument")
async def create_instrument(
    instrument: CFDInstrument,
    admin: dict = Depends(get_current_admin)
):
    """Create new CFD instrument (Admin only)"""
    trading_engine.instruments[instrument.symbol] = instrument
    
    return {"success": True, "message": f"Instrument {instrument.symbol} created"}

@app.put("/api/cfd/admin/instrument/{symbol}")
async def update_instrument(
    symbol: str,
    updates: Dict[str, Any],
    admin: dict = Depends(get_current_admin)
):
    """Update CFD instrument (Admin only)"""
    if symbol not in trading_engine.instruments:
        raise HTTPException(status_code=404, detail="Instrument not found")
    
    instrument = trading_engine.instruments[symbol]
    
    for key, value in updates.items():
        if hasattr(instrument, key):
            setattr(instrument, key, value)
    
    return {"success": True, "message": f"Instrument {symbol} updated"}

@app.delete("/api/cfd/admin/instrument/{symbol}")
async def delete_instrument(
    symbol: str,
    admin: dict = Depends(get_current_admin)
):
    """Delete CFD instrument (Admin only)"""
    if symbol in trading_engine.instruments:
        del trading_engine.instruments[symbol]
    
    return {"success": True, "message": f"Instrument {symbol} deleted"}

@app.post("/api/cfd/admin/fees/config")
async def configure_cfd_fees(
    symbol: str,
    maker_fee: Decimal,
    taker_fee: Decimal,
    swap_long: Decimal,
    swap_short: Decimal,
    admin: dict = Depends(get_current_admin)
):
    """Configure CFD fees (Admin only)"""
    if symbol in trading_engine.instruments:
        # Store fee configuration
        fee_config = {
            "symbol": symbol,
            "maker_fee": str(maker_fee),
            "taker_fee": str(taker_fee),
            "swap_long": str(swap_long),
            "swap_short": str(swap_short),
            "updated_at": datetime.utcnow().isoformat(),
            "updated_by": admin["admin_id"]
        }
        
        if redis_client:
            await redis_client.set(f"cfd:fees:{symbol}", json.dumps(fee_config))
        
        return {"success": True, "message": f"Fees configured for {symbol}", "config": fee_config}
    
    raise HTTPException(status_code=404, detail="Instrument not found")

# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@app.websocket("/ws/cfd/prices")
async def websocket_prices(websocket: WebSocket):
    """WebSocket for real-time prices"""
    await websocket.accept()
    trading_engine.websockets.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            # Handle subscription requests
            try:
                message = json.loads(data)
                if message.get("type") == "subscribe":
                    symbols = message.get("symbols", [])
                    # Send current prices for subscribed symbols
                    for symbol in symbols:
                        if symbol in trading_engine.prices:
                            await websocket.send_json({
                                "type": "quote",
                                "symbol": symbol,
                                "data": await trading_engine.get_quote(symbol)
                            })
            except:
                pass
    except WebSocketDisconnect:
        trading_engine.websockets.remove(websocket)

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "cfd-trading-service",
        "version": "2.0.0",
        "instruments_count": len(trading_engine.instruments),
        "stock_tokens_count": len(trading_engine.stock_tokens)
    }

# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup():
    global redis_client
    redis_client = redis.from_url(REDIS_URL)
    logger.info("CFD Trading Service started")

@app.on_event("shutdown")
async def shutdown():
    if redis_client:
        await redis_client.close()
    logger.info("CFD Trading Service stopped")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8190)