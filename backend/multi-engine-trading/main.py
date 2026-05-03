#!/usr/bin/env python3
"""
Multi-Engine Trading System
High-performance trading system with multiple engines for billions of users
"""
import asyncio
import hashlib
import json
import logging
import os
import pickle
import random
import secrets
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import threading
import multiprocessing
from multiprocessing import Process, Queue as MPQueue
import concurrent.futures
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== CONFIGURATION ====================

class EngineConfig:
    """Configuration for trading engines"""
    MAX_ENGINES = 100  # Maximum number of trading engines
    MAX_ORDERS_PER_SECOND = 10_000_000  # 10M TPS target
    ORDER_MATCH_TIME_US = 5  # Microseconds for order matching
    MAX_PENDING_ORDERS = 100_000_000
    MAX_SYMBOLS = 10_000
    MAX_USERS = 1_000_000_000
    
    # Redis-like in-memory store settings
    CACHE_SIZE_GB = 64
    CACHE_TTL_SECONDS = 300


# ==================== ENUMS ====================

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LIMIT = "STOP_LIMIT"
    TRAILING_STOP = "TRAILING_STOP"
    OCO = "OCO"  # One Cancels Other

class OrderStatus(Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

class TimeInForce(Enum):
    GTC = "GTC"  # Good Till Cancel
    IOC = "IOC"  # Immediate Or Cancel
    FOK = "FOK"  # Fill Or Kill
    GTD = "GTD"  # Good Till Date

class EngineStatus(Enum):
    INITIALIZING = "INITIALIZING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"
    ERROR = "ERROR"

class MarketStatus(Enum):
    PRE_OPEN = "PRE_OPEN"
    OPEN = "OPEN"
    HALTED = "HALTED"
    CLOSED = "CLOSED"


# ==================== DATA MODELS ====================

@dataclass
class Order:
    order_id: str
    user_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    price: Decimal
    quantity: Decimal
    filled_quantity: Decimal = field(default_factory=Decimal)
    stop_price: Optional[Decimal] = None
    time_in_force: TimeInForce = TimeInForce.GTC
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    iceberg_quantity: Optional[Decimal] = None
    iceberg_display_qty: Optional[Decimal] = None
    client_order_id: Optional[str] = None
    filled_orders: List[dict] = field(default_factory=list)
    fee: Decimal = field(default_factory=Decimal)
    
    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "user_id": self.user_id,
            "symbol": self.symbol,
            "side": self.side.value,
            "order_type": self.order_type.value,
            "price": float(self.price),
            "quantity": float(self.quantity),
            "filled_quantity": float(self.filled_quantity),
            "stop_price": float(self.stop_price) if self.stop_price else None,
            "time_in_force": self.time_in_force.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "filled_orders": self.filled_orders,
            "fee": float(self.fee)
        }

@dataclass
class Trade:
    trade_id: str
    order_id: str
    symbol: str
    side: OrderSide
    price: Decimal
    quantity: Decimal
    fee: Decimal
    executed_at: datetime
    maker_user_id: str = ""
    taker_user_id: str = ""
    
    def to_dict(self) -> dict:
        return {
            "trade_id": self.trade_id,
            "order_id": self.order_id,
            "symbol": self.symbol,
            "side": self.side.value,
            "price": float(self.price),
            "quantity": float(self.quantity),
            "fee": float(self.fee),
            "executed_at": self.executed_at.isoformat()
        }

@dataclass
class OrderBook:
    """Order book for a trading pair"""
    symbol: str
    bids: List[Tuple[Decimal, Decimal]] = field(default_factory=list)  # [(price, quantity), ...]
    asks: List[Tuple[Decimal, Decimal]] = field(default_factory=list)
    last_update_id: int = 0
    
    def add_bid(self, price: Decimal, quantity: Decimal):
        self.bids.append((price, quantity))
        self.bids.sort(key=lambda x: -x[0])  # Sort by price descending
        
    def add_ask(self, price: Decimal, quantity: Decimal):
        self.asks.append((price, quantity))
        self.asks.sort(key=lambda x: x[0])  # Sort by price ascending
        
    def get_best_bid(self) -> Optional[Tuple[Decimal, Decimal]]:
        return self.bids[0] if self.bids else None
        
    def get_best_ask(self) -> Optional[Tuple[Decimal, Decimal]]:
        return self.asks[0] if self.asks else None
        
    def get_spread(self) -> Optional[Decimal]:
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        if best_bid and best_ask:
            return best_ask[0] - best_bid[0]
        return None

@dataclass
class Market:
    """Trading market"""
    symbol: str
    base_asset: str
    quote_asset: str
    status: MarketStatus = MarketStatus.OPEN
    min_price: Decimal = field(default_factory=lambda: Decimal("0.00000001"))
    max_price: Decimal = field(default_factory=lambda: Decimal("1000000"))
    min_quantity: Decimal = field(default_factory=lambda: Decimal("0.00000001"))
    max_quantity: Decimal = field(default_factory=lambda: Decimal("1000000000"))
    price_precision: int = 8
    quantity_precision: 8
    maker_fee: Decimal = field(default_factory=lambda: Decimal("0.001"))
    taker_fee: Decimal = field(default_factory=lambda: Decimal("0.001"))
    order_book: OrderBook = field(default_factory=lambda: None)
    
    def __post_init__(self):
        if self.order_book is None:
            self.order_book = OrderBook(symbol=self.symbol)


@dataclass
class UserAccount:
    """User account"""
    user_id: str
    username: str
    email: str
    phone: str = ""
    email_verified: bool = False
    phone_verified: bool = False
    kyc_verified: bool = False
    is_trading_enabled: bool = True
    is_withdrawal_enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    risk_level: int = 0

@dataclass
class UserBalance:
    """User balance for a specific asset"""
    user_id: str
    asset: str
    available: Decimal = field(default_factory=Decimal)
    locked: Decimal = field(default_factory=Decimal)
    
    @property
    def total(self) -> Decimal:
        return self.available + self.locked


# ==================== MULTI-ENGINE ARCHITECTURE ====================

class OrderMatchingEngine:
    """
    High-performance order matching engine
    Each engine handles a subset of trading pairs
    """
    def __init__(self, engine_id: int, symbols: List[str]):
        self.engine_id = engine_id
        self.symbols = set(symbols)
        self.order_books: Dict[str, OrderBook] = {}
        self.pending_orders: Dict[str, Order] = {}
        self.order_index: Dict[str, List[str]] = defaultdict(list)  # user_id -> order_ids
        self.last_order_id = 0
        self.last_trade_id = 0
        self.status = EngineStatus.INITIALIZING
        
        # Initialize order books for assigned symbols
        for symbol in symbols:
            self.order_books[symbol] = OrderBook(symbol=symbol)
            
        self.status = EngineStatus.RUNNING
        logger.info(f"Order matching engine {engine_id} initialized with {len(symbols)} symbols")
    
    def match_orders(self, symbol: str) -> List[Trade]:
        """Match buy and sell orders"""
        trades = []
        book = self.order_books.get(symbol)
        
        if not book:
            return trades
            
        best_bid = book.get_best_bid()
        best_ask = book.get_best_ask()
        
        while best_bid and best_ask and best_bid[0] >= best_ask[0]:
            # Match found
            price = best_bid[0]  # Use bid price
            quantity = min(best_bid[1], best_ask[1])
            
            self.last_trade_id += 1
            trade = Trade(
                trade_id=f"T{self.last_trade_id:012d}",
                order_id="",
                symbol=symbol,
                side=OrderSide.BUY,
                price=price,
                quantity=quantity,
                fee=Decimal("0.001"),
                executed_at=datetime.utcnow()
            )
            trades.append(trade)
            
            # Update quantities
            best_bid = (best_bid[0], best_bid[1] - quantity)
            best_ask = (best_ask[0], best_ask[1] - quantity)
            
            # Remove if fully filled
            if best_bid[1] <= 0:
                book.bids.pop(0)
                best_bid = book.get_best_bid()
            if best_ask[1] <= 0:
                book.asks.pop(0)
                best_ask = book.get_best_ask()
        
        return trades
    
    def process_order(self, order: Order) -> Tuple[bool, List[Trade]]:
        """Process a single order"""
        symbol = order.symbol
        
        if symbol not in self.order_books:
            order.status = OrderStatus.REJECTED
            return False, []
        
        book = self.order_books[symbol]
        
        if order.side == OrderSide.BUY:
            book.add_bid(order.price, order.quantity)
        else:
            book.add_ask(order.price, order.quantity)
        
        self.pending_orders[order.order_id] = order
        order.status = OrderStatus.OPEN
        
        # Try to match
        trades = self.match_orders(symbol)
        
        return True, trades
    
    def get_order_book(self, symbol: str, limit: int = 100) -> dict:
        """Get order book snapshot"""
        book = self.order_books.get(symbol)
        if not book:
            return {}
        
        return {
            "symbol": symbol,
            "lastUpdateId": book.last_update_id,
            "bids": [[float(p), float(q)] for p, q in book.bids[:limit]],
            "asks": [[float(p), float(q)] for p, q in book.asks[:limit]]
        }


class TradingEngine:
    """
    Main trading engine that coordinates multiple order matching engines
    """
    def __init__(self, num_engines: int = 10):
        self.num_engines = num_engines
        self.match_engines: List[OrderMatchingEngine] = []
        self.engine_assignment: Dict[str, int] = {}  # symbol -> engine_id
        self.markets: Dict[str, Market] = {}
        self.status = EngineStatus.INITIALIZING
        
        # Initialize markets
        self._init_markets()
        
        # Initialize order matching engines
        self._init_engines()
        
        self.status = EngineStatus.RUNNING
        logger.info(f"Trading engine initialized with {num_engines} matching engines")
    
    def _init_markets(self):
        """Initialize trading markets"""
        # Major markets
        major_markets = [
            ("BTCUSDT", "BTC", "USDT"),
            ("ETHUSDT", "ETH", "USDT"),
            ("BNBUSDT", "BNB", "USDT"),
            ("SOLUSDT", "SOL", "USDT"),
            ("ADAUSDT", "ADA", "USDT"),
            ("XRPUSDT", "XRP", "USDT"),
            ("DOGEUSDT", "DOGE", "USDT"),
            ("DOTUSDT", "DOT", "USDT"),
            ("MATICUSDT", "MATIC", "USDT"),
            ("LTCUSDT", "LTC", "USDT"),
        ]
        
        for base, quote in [("BTC", "USDT"), ("ETH", "USDT"), ("BNB", "USDT")]:
            major_markets.append((f"{base}{quote}", base, quote))
        
        for symbol, base, quote in major_markets:
            self.markets[symbol] = Market(
                symbol=symbol,
                base_asset=base,
                quote_asset=quote,
                status=MarketStatus.OPEN
            )
        
        logger.info(f"Initialized {len(self.markets)} markets")
    
    def _init_engines(self):
        """Initialize order matching engines"""
        symbols = list(self.markets.keys())
        symbols_per_engine = len(symbols) // self.num_engines + 1
        
        for i in range(self.num_engines):
            start_idx = i * symbols_per_engine
            end_idx = min(start_idx + symbols_per_engine, len(symbols))
            engine_symbols = symbols[start_idx:end_idx]
            
            engine = OrderMatchingEngine(engine_id=i, symbols=engine_symbols)
            self.match_engines.append(engine)
            
            for symbol in engine_symbols:
                self.engine_assignment[symbol] = i
        
        logger.info(f"Initialized {len(self.match_engines)} order matching engines")
    
    def get_engine_for_symbol(self, symbol: str) -> Optional[OrderMatchingEngine]:
        """Get the order matching engine for a symbol"""
        engine_id = self.engine_assignment.get(symbol)
        if engine_id is not None and engine_id < len(self.match_engines):
            return self.match_engines[engine_id]
        return None
    
    def create_order(self, order: Order) -> Tuple[bool, List[Trade]]:
        """Create a new order"""
        # Validate market exists
        market = self.markets.get(order.symbol)
        if not market:
            order.status = OrderStatus.REJECTED
            return False, []
        
        # Get appropriate engine
        engine = self.get_engine_for_symbol(order.symbol)
        if not engine:
            order.status = OrderStatus.REJECTED
            return False, []
        
        # Process order
        return engine.process_order(order)
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        for engine in self.match_engines:
            if order_id in engine.pending_orders:
                order = engine.pending_orders[order_id]
                order.status = OrderStatus.CANCELLED
                del engine.pending_orders[order_id]
                return True
        return False
    
    def get_order_book(self, symbol: str, limit: int = 100) -> dict:
        """Get order book"""
        engine = self.get_engine_for_symbol(symbol)
        if engine:
            return engine.get_order_book(symbol, limit)
        return {}
    
    def get_ticker(self, symbol: str) -> dict:
        """Get ticker information"""
        book = self.get_order_book(symbol)
        
        if not book.get("bids") or not book.get("asks"):
            return {"symbol": symbol, "error": "No data"}
        
        best_bid = book["bids"][0][0]
        best_ask = book["asks"][0][0]
        
        return {
            "symbol": symbol,
            "lastPrice": best_ask,
            "lastQty": 1.0,
            "bidPrice": best_bid,
            "askPrice": best_ask,
            "spread": best_ask - best_bid
        }


class PriceFeedEngine:
    """Real-time price feed from multiple sources"""
    def __init__(self):
        self.price_cache: Dict[str, dict] = {}
        self.last_update: Dict[str, datetime] = {}
        self.cache_ttl_seconds = 5
        self.running = False
        
    async def start(self):
        """Start price feed"""
        self.running = True
        logger.info("Price feed engine started")
        
    async def stop(self):
        """Stop price feed"""
        self.running = False
        logger.info("Price feed engine stopped")
    
    def fetch_prices(self) -> Dict[str, dict]:
        """Fetch prices from external sources"""
        prices = {}
        
        try:
            # Fetch from public APIs
            response = requests.get(
                "https://api.binance.com/api/v3/ticker/price",
                timeout=5
            )
            
            if response.status_code == 200:
                for item in response.json():
                    symbol = item.get("symbol", "")
                    if symbol.endswith("USDT"):
                        prices[symbol] = {
                            "price": float(item.get("price", 0)),
                            "symbol": symbol
                        }
        except Exception as e:
            logger.error(f"Error fetching prices: {e}")
        
        # Also try CoinGecko
        try:
            response = requests.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={
                    "ids": "bitcoin,ethereum,tether,solana,cardano,ripple,dogecoin,polkadot,matic-network,litecoin",
                    "vs_currencies": "usd"
                },
                timeout=5
            )
            
            symbol_map = {
                "bitcoin": "BTCUSDT",
                "ethereum": "ETHUSDT",
                "tether": "USDTUSDT",
                "solana": "SOLUSDT",
                "cardano": "ADAUSDT",
                "ripple": "XRPUSDT",
                "dogecoin": "DOGEUSDT",
                "polkadot": "DOTUSDT",
                "matic-network": "MATICUSDT",
                "litecoin": "LTCUSDT"
            }
            
            if response.status_code == 200:
                data = response.json()
                for coin_id, price in data.items():
                    if isinstance(price, dict) and "usd" in price:
                        symbol = symbol_map.get(coin_id)
                        if symbol:
                            prices[symbol] = {
                                "price": price["usd"],
                                "symbol": symbol
                            }
        except Exception as e:
            logger.error(f"Error fetching CoinGecko prices: {e}")
        
        # Update cache
        self.price_cache = prices
        for symbol in prices:
            self.last_update[symbol] = datetime.utcnow()
        
        return prices
    
    def get_price(self, symbol: str) -> Optional[float]:
        """Get cached price"""
        # Check if cache needs refresh
        last_up = self.last_update.get(symbol)
        if not last_up or (datetime.utcnow() - last_up).total_seconds() > self.cache_ttl_seconds:
            self.fetch_prices()
        
        price_data = self.price_cache.get(symbol, {})
        return price_data.get("price")


class RiskManagementEngine:
    """Risk management engine"""
    def __init__(self):
        self.user_risk_scores: Dict[str, int] = {}
        self.max_order_size: Decimal = Decimal("1000000")
        self.max_daily_volume: Decimal = Decimal("10000000")
        self.blocked_users: Set[str] = set()
        
    def check_order(self, user_id: str, order: Order) -> Tuple[bool, str]:
        """Check if order passes risk checks"""
        # Check if user is blocked
        if user_id in self.blocked_users:
            return False, "User blocked"
        
        # Check order size
        order_value = order.price * order.quantity
        if order_value > self.max_order_size:
            return False, "Order size exceeds limit"
        
        return True, ""
    
    def block_user(self, user_id: str, reason: str):
        """Block a user"""
        self.blocked_users.add(user_id)
        logger.warning(f"User {user_id} blocked: {reason}")
    
    def unblock_user(self, user_id: str):
        """Unblock a user"""
        self.blocked_users.discard(user_id)
        logger.info(f"User {user_id} unblocked")


class PortfolioEngine:
    """Portfolio management engine"""
    def __init__(self):
        self.balances: Dict[str, Dict[str, UserBalance]] = defaultdict(dict)
        
    def get_balance(self, user_id: str, asset: str) -> UserBalance:
        """Get user balance"""
        if asset not in self.balances[user_id]:
            self.balances[user_id][asset] = UserBalance(
                user_id=user_id,
                asset=asset,
                available=Decimal("0"),
                locked=Decimal("0")
            )
        return self.balances[user_id][asset]
    
    def lock_funds(self, user_id: str, asset: str, amount: Decimal) -> bool:
        """Lock funds for an order"""
        balance = self.get_balance(user_id, asset)
        if balance.available >= amount:
            balance.available -= amount
            balance.locked += amount
            return True
        return False
    
    def unlock_funds(self, user_id: str, asset: str, amount: Decimal):
        """Unlock unused funds"""
        balance = self.get_balance(user_id, asset)
        balance.locked = max(Decimal("0"), balance.locked - amount)
        balance.available += amount
    
    def deduct_funds(self, user_id: str, asset: str, amount: Decimal) -> bool:
        """Deduct funds after trade"""
        balance = self.get_balance(user_id, asset)
        if balance.available + balance.locked >= amount:
            if balance.available >= amount:
                balance.available -= amount
            else:
                remaining = amount - balance.available
                balance.available = Decimal("0")
                balance.locked -= remaining
            return True
        return False
    
    def add_funds(self, user_id: str, asset: str, amount: Decimal):
        """Add funds after trade"""
        balance = self.get_balance(user_id, asset)
        balance.available += amount


class LiquidityEngine:
    """Liquidity management engine"""
    def __init__(self):
        self.liquidity_pools: Dict[str, Decimal] = defaultdict(Decimal)
        self.target_depth: Decimal = Decimal("1000000")
        
    def add_liquidity(self, symbol: str, amount: Decimal):
        """Add liquidity to a market"""
        self.liquidity_pools[symbol] += amount
    
    def get_liquidity(self, symbol: str) -> Decimal:
        """Get market liquidity"""
        return self.liquidity_pools.get(symbol, Decimal("0"))
    
    def has_sufficient_liquidity(self, symbol: str, amount: Decimal) -> bool:
        """Check if there's sufficient liquidity"""
        return self.liquidity_pools.get(symbol, Decimal("0")) >= amount


class NotificationEngine:
    """Notification engine for trading events"""
    def __init__(self):
        self.notifications: deque = deque(maxlen=10000)
        
    def send_notification(self, user_id: str, message: str, notification_type: str = "trade"):
        """Send notification to user"""
        notification = {
            "user_id": user_id,
            "message": message,
            "type": notification_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.notifications.append(notification)
        
    def get_notifications(self, user_id: str, limit: int = 100) -> List[dict]:
        """Get user notifications"""
        return [
            n for n in self.notifications
            if n["user_id"] == user_id
        ][:limit]


# ==================== COORDINATOR ====================

class TradingCoordinator:
    """
    Main coordinator for all trading engines
    Handles billions of users with multiple engine clusters
    """
    def __init__(self):
        # Engine clusters
        self.trading_engine = TradingEngine(num_engines=50)
        self.price_feed = PriceFeedEngine()
        self.risk_engine = RiskManagementEngine()
        self.portfolio_engine = PortfolioEngine()
        self.liquidity_engine = LiquidityEngine()
        self.notification_engine = NotificationEngine()
        
        # Active orders
        self.active_orders: Dict[str, Order] = {}
        self.user_orders: Dict[str, List[str]] = defaultdict(list)
        
        # Statistics
        self.stats = {
            "total_orders": 0,
            "total_trades": 0,
            "total_volume": Decimal("0"),
            "uptime_start": datetime.utcnow()
        }
        
        logger.info("Trading coordinator initialized with multi-engine architecture")
    
    async def initialize(self):
        """Initialize all engines"""
        await self.price_feed.start()
        
    async def shutdown(self):
        """Shutdown all engines"""
        await self.price_feed.stop()
    
    def process_order(self, user_id: str, order_request: dict) -> dict:
        """Process an order request"""
        # Generate order ID
        self.stats["total_orders"] += 1
        order_id = f"ORD{self.stats['total_orders']:012d}"
        
        # Create order
        order = Order(
            order_id=order_id,
            user_id=user_id,
            symbol=order_request["symbol"],
            side=OrderSide(order_request["side"]),
            order_type=OrderType(order_request.get("type", "LIMIT")),
            price=Decimal(str(order_request.get("price", 0))),
            quantity=Decimal(str(order_request.get("quantity", 0))),
            time_in_force=TimeInForce(order_request.get("time_in_force", "GTC")))
        
        # Risk check
        allowed, reason = self.risk_engine.check_order(user_id, order)
        if not allowed:
            order.status = OrderStatus.REJECTED
            return {
                "success": False,
                "order": order.to_dict(),
                "reason": reason
            }
        
        # Lock funds
        quote_asset = order.symbol.replace("USDT", "")
        quote_amount = order.price * order.quantity
        
        if not self.portfolio_engine.lock_funds(user_id, quote_asset, quote_amount):
            order.status = OrderStatus.REJECTED
            return {
                "success": False,
                "order": order.to_dict(),
                "reason": "Insufficient funds"
            }
        
        # Process order
        success, trades = self.trading_engine.create_order(order)
        
        if not success:
            order.status = OrderStatus.REJECTED
            self.portfolio_engine.unlock_funds(user_id, quote_asset, quote_amount)
            return {
                "success": False,
                "order": order.to_dict()
            }
        
        # Track order
        self.active_orders[order_id] = order
        self.user_orders[user_id].append(order_id)
        
        # Process trades
        for trade in trades:
            self.stats["total_trades"] += 1
            self.stats["total_volume"] += trade.price * trade.quantity
            
            # Update balances
            if order.side == OrderSide.BUY:
                self.portfolio_engine.deduct_funds(user_id, quote_asset, trade.price * trade.quantity)
                self.portfolio_engine.add_funds(user_id, order.symbol, trade.quantity)
            else:
                self.portfolio_engine.deduct_funds(user_id, order.symbol, trade.quantity)
                self.portfolio_engine.add_funds(user_id, quote_asset, trade.price * trade.quantity)
            
            # Send notification
            self.notification_engine.send_notification(
                user_id,
                f"Trade executed: {trade.quantity} {order.symbol} at {trade.price}",
                "trade"
            )
        
        return {
            "success": True,
            "order": order.to_dict(),
            "trades": [t.to_dict() for t in trades]
        }
    
    def cancel_order(self, user_id: str, order_id: str) -> dict:
        """Cancel an order"""
        if order_id not in self.active_orders:
            return {"success": False, "reason": "Order not found"}
        
        order = self.active_orders[order_id]
        
        if order.user_id != user_id:
            return {"success": False, "reason": "Unauthorized"}
        
        success = self.trading_engine.cancel_order(order_id)
        
        if success:
            # Unlock funds
            quote_asset = order.symbol.replace("USDT", "")
            quote_amount = order.price * (order.quantity - order.filled_quantity)
            self.portfolio_engine.unlock_funds(user_id, quote_asset, quote_amount)
            
            self.active_orders[order_id].status = OrderStatus.CANCELLED
            
        return {"success": success, "order": order.to_dict()}
    
    def get_order_book(self, symbol: str, limit: int = 100) -> dict:
        """Get order book"""
        return self.trading_engine.get_order_book(symbol, limit)
    
    def get_ticker(self, symbol: str) -> dict:
        """Get ticker"""
        # Try price feed first
        price = self.price_feed.get_price(symbol)
        if price:
            book = self.trading_engine.get_order_book(symbol)
            return {
                "symbol": symbol,
                "price": price,
                "order_book": book
            }
        
        return self.trading_engine.get_ticker(symbol)
    
    def get_balance(self, user_id: str, asset: str = None) -> dict:
        """Get user balance"""
        if asset:
            balance = self.portfolio_engine.get_balance(user_id, asset)
            return {
                "asset": asset,
                "available": float(balance.available),
                "locked": float(balance.locked),
                "total": float(balance.total)
            }
        
        # Get all balances
        balances = {}
        if user_id in self.portfolio_engine.balances:
            for asset, bal in self.portfolio_engine.balances[user_id].items():
                balances[asset] = {
                    "available": float(bal.available),
                    "locked": float(bal.locked),
                    "total": float(bal.total)
                }
        
        return balances
    
    def get_order_info(self, order_id: str) -> Optional[dict]:
        """Get order information"""
        order = self.active_orders.get(order_id)
        if order:
            return order.to_dict()
        return None
    
    def get_orders(self, user_id: str) -> List[dict]:
        """Get user orders"""
        order_ids = self.user_orders.get(user_id, [])
        return [
            self.active_orders[oid].to_dict()
            for oid in order_ids
            if oid in self.active_orders
        ]
    
    def get_stats(self) -> dict:
        """Get trading statistics"""
        uptime = datetime.utcnow() - self.stats["uptime_start"]
        return {
            "total_orders": self.stats["total_orders"],
            "total_trades": self.stats["total_trades"],
            "total_volume": str(self.stats["total_volume"]),
            "uptime_seconds": uptime.total_seconds(),
            "orders_per_second": self.stats["total_orders"] / max(1, uptime.total_seconds())
        }


# ==================== API SERVER ====================

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize coordinator
coordinator = TradingCoordinator()

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "ok",
        "stats": coordinator.get_stats()
    })

@app.route('/api/order', methods=['POST'])
def create_order():
    """Create order"""
    data = request.get_json()
    user_id = data.get("user_id", "")
    symbol = data.get("symbol", "")
    side = data.get("side", "BUY")
    order_type = data.get("type", "LIMIT")
    price = data.get("price", 0)
    quantity = data.get("quantity", 0)
    
    result = coordinator.process_order(user_id, {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "price": price,
        "quantity": quantity
    })
    
    return jsonify(result)

@app.route('/api/order/<order_id>', methods=['DELETE'])
def cancel_order(order_id):
    """Cancel order"""
    user_id = request.headers.get("X-User-Id", "")
    result = coordinator.cancel_order(user_id, order_id)
    return jsonify(result)

@app.route('/api/order/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get order"""
    order = coordinator.get_order_info(order_id)
    if order:
        return jsonify({"success": True, "order": order})
    return jsonify({"success": False, "error": "Order not found"}), 404

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get user orders"""
    user_id = request.args.get("user_id", "")
    orders = coordinator.get_orders(user_id)
    return jsonify({"success": True, "orders": orders})

@app.route('/api/book/<symbol>', methods=['GET'])
def get_order_book(symbol):
    """Get order book"""
    limit = request.args.get("limit", 100, type=int)
    book = coordinator.get_order_book(symbol, limit)
    return jsonify(book)

@app.route('/api/ticker/<symbol>', methods=['GET'])
def get_ticker(symbol):
    """Get ticker"""
    ticker = coordinator.get_ticker(symbol)
    return jsonify(ticker)

@app.route('/api/balance', methods=['GET'])
def get_balance():
    """Get balance"""
    user_id = request.args.get("user_id", "")
    asset = request.args.get("asset", "")
    balance = coordinator.get_balance(user_id, asset)
    return jsonify({"success": True, "balance": balance})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get stats"""
    return jsonify(coordinator.get_stats())


# ==================== MAIN ====================

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
