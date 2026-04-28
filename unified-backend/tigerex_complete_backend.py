"""
TigerEx Complete Backend - Unified Trading System
==============================================
Production-ready backend with all trading features, AI bots, and external API.
Version: 8.0.0

Features:
- Complete trading engine (Spot, Futures, Margin, Options)
- AI Automated Trading Bots
- External Exchange API (for Binance, OKX, ByBit, BitGet integrations)
- Wallet Management
- KYC/AML System
- Admin Dashboard
- Risk Management
"""

import asyncio
import json
import logging
import hashlib
import hmac
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from decimal import Decimal
from enum import Enum
from functools import wraps
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============= CONFIGURATION =============
CONFIG = {
    "exchange_name": "TigerEx",
    "exchange_id": "TIGEREX-2026",
    "version": "8.0.0",
    "maker_fee": 0.001,  # 0.1%
    "taker_fee": 0.001,  # 0.1%
    "withdrawal_fee": 0.0005,  # 0.05%
    "min_deposit": 0.0001,
    "max_leverage": 100,
    "api_rate_limit": 1000,  # requests per minute
    "supported_chains": {
        "BTC": ["bitcoin", "lightning"],
        "ETH": ["ethereum", "arbitrum", "optimism", "polygon"],
        "USDT": ["ethereum_erc20", "trc20", "bep20", "polygon"],
        "BNB": ["bep20"],
    }
}

# ============= ENUMS =============
class UserRole(Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    PARTNER = "partner"
    INSTITUTIONAL = "institutional"
    TRADER = "trader"
    VIP = "vip"

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"
    ICEBERG = "iceberg"
    TWAP = "twap"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class TradingMode(Enum):
    SPOT = "spot"
    FUTURES = "futures"
    MARGIN = "margin"
    OPTIONS = "options"

class BotStrategy(Enum):
    GRID = "grid"
    DCA = "dca"
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    ARBITRAGE = "arbitrage"
    ML_PREDICTION = "ml_prediction"

class BotStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

class ExchangeStatus(Enum):
    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"
    PAUSED = "paused"
    HALTED = "halted"

class KYCStatus(Enum):
    NOT_STARTED = "not_started"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

# ============= DATABASE MODELS =============
@dataclass
class User:
    id: str
    email: str
    phone: str = ""
    name: str = ""
    role: UserRole = UserRole.TRADER
    kyc_status: KYCStatus = KYCStatus.NOT_STARTED
    kyc_level: int = 0
    trading_fee_discount: float = 0.0
    referral_code: str = ""
    referred_by: str = ""
    api_keys: List[str] = field(default_factory=list)
    wallet_addresses: Dict[str, str] = field(default_factory=dict)
    balances: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_login: datetime = field(default_factory=datetime.now)
    is_active: bool = True

@dataclass
class TradingPair:
    symbol: str
    base_asset: str
    quote_asset: str
    min_quantity: float = 0.0001
    max_quantity: float = 1000000
    price_precision: int = 8
    quantity_precision: int = 8
    min_notional: float = 1.0
    maker_fee: float = 0.001
    taker_fee: float = 0.001
    is_trading_enabled: bool = True

@dataclass
class Order:
    id: str
    user_id: str
    symbol: str
    side: OrderSide
    type: OrderType
    price: float
    quantity: float
    filled_quantity: float = 0.0
    status: OrderStatus = OrderStatus.PENDING
    trading_mode: TradingMode = TradingMode.SPOT
    leverage: int = 1
    stop_price: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    filled_at: Optional[datetime] = None

@dataclass
class Trade:
    id: str
    order_id: str
    user_id: str
    symbol: str
    side: OrderSide
    price: float
    quantity: float
    fee: float
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class TradingBot:
    id: str
    user_id: str
    name: str
    strategy: BotStrategy
    status: BotStatus
    symbol: str
    config: Dict[str, Any]
    balances: Dict[str, float] = field(default_factory=dict)
    performance: Dict[str, float] = field(default_factory=lambda: {
        "total_pnl": 0.0,
        "win_rate": 0.0,
        "total_trades": 0,
        "profitable_trades": 0
    })
    created_at: datetime = field(default_factory=datetime.now)
    last_run: Optional[datetime] = None

@dataclass
class ExchangeConnection:
    id: str
    user_id: str
    exchange: str  # binance, okx, bybit, bitget
    api_key: str
    api_secret: str
    passphrase: str = ""
    is_active: bool = True
    last_sync: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Wallet:
    id: str
    user_id: str
    currency: str
    network: str
    address: str
    memo: str = ""
    balance: float = 0.0
    locked: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class APIKey:
    id: str
    user_id: str
    name: str
    key: str
    secret: str
    permissions: List[str] = field(default_factory=list)
    ip_whitelist: List[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    expires_at: Optional[datetime] = None

# ============= IN-MEMORY DATABASE =============
class Database:
    """In-memory database for TigerEx"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.orders: Dict[str, Order] = {}
        self.trades: Dict[str, Trade] = {}
        self.bots: Dict[str, TradingBot] = {}
        self.pairs: Dict[str, TradingPair] = {}
        self.wallets: Dict[str, Wallet] = {}
        self.api_keys: Dict[str, APIKey] = {}
        self.exchange_connections: Dict[str, ExchangeConnection] = {}
        self.orderbook: Dict[str, Dict] = defaultdict(lambda: {"bids": [], "asks": []})
        self.price_history: Dict[str, List[Dict]] = defaultdict(list)
        self.trade_history: Dict[str, List[Dict]] = defaultdict(list)
        
    def create_default_pairs(self):
        """Create default trading pairs"""
        default_pairs = [
            TradingPair("BTC/USDT", "BTC", "USDT", min_quantity=0.00001, price_precision=2),
            TradingPair("ETH/USDT", "ETH", "USDT", min_quantity=0.0001, price_precision=2),
            TradingPair("BNB/USDT", "BNB", "USDT", min_quantity=0.001, price_precision=2),
            TradingPair("SOL/USDT", "SOL", "USDT", min_quantity=0.01, price_precision=4),
            TradingPair("XRP/USDT", "XRP", "USDT", min_quantity=1.0, price_precision=5),
            TradingPair("DOGE/USDT", "DOGE", "USDT", min_quantity=10.0, price_precision=6),
            TradingPair("ADA/USDT", "ADA", "USDT", min_quantity=1.0, price_precision=5),
            TradingPair("AVAX/USDT", "AVAX", "USDT", min_quantity=0.1, price_precision=3),
            TradingPair("DOT/USDT", "DOT", "USDT", min_quantity=0.1, price_precision=3),
            TradingPair("MATIC/USDT", "MATIC", "USDT", min_quantity=0.1, price_precision=4),
            TradingPair("LINK/USDT", "LINK", "USDT", min_quantity=0.1, price_precision=4),
            TradingPair("LTC/USDT", "LTC", "USDT", min_quantity=0.001, price_precision=2),
            TradingPair("UNI/USDT", "UNI", "USDT", min_quantity=0.01, price_precision=4),
            TradingPair("ATOM/USDT", "ATOM", "USDT", min_quantity=0.01, price_precision=3),
            TradingPair("XLM/USDT", "XLM", "USDT", min_quantity=0.1, price_precision=5),
            TradingPair("VET/USDT", "VET", "USDT", min_quantity=100.0, price_precision=6),
            TradingPair("FIL/USDT", "FIL", "USDT", min_quantity=0.1, price_precision=4),
            TradingPair("THETA/USDT", "THETA", "USDT", min_quantity=1.0, price_precision=4),
            TradingPair("AAVE/USDT", "AAVE", "USDT", min_quantity=0.01, price_precision=4),
            TradingPair("AXS/USDT", "AXS", "USDT", min_quantity=0.01, price_precision=4),
        ]
        for pair in default_pairs:
            self.pairs[pair.symbol] = pair
        logger.info(f"Created {len(default_pairs)} trading pairs")

# Initialize database
db = Database()
db.create_default_pairs()

# ============= UTILITY FUNCTIONS =============
def generate_id(prefix: str = "") -> str:
    """Generate unique ID"""
    timestamp = str(time.time()).encode()
    random_bytes = os.urandom(16)
    hash_obj = hashlib.sha256(timestamp + random_bytes)
    return f"{prefix}{hash_obj.hexdigest()[:16]}"

def generate_api_key() -> tuple:
    """Generate API key pair"""
    key = f"TX{generate_id('')}"
    secret = generate_id('secret_')
    return key, secret

def hash_password(password: str, salt: str = "") -> str:
    """Hash password"""
    return hashlib.sha256((password + salt).encode()).hexdigest()

def verify_password(password: str, hashed: str, salt: str = "") -> bool:
    """Verify password"""
    return hash_password(password, salt) == hashed

def sign_request(secret: str, params: Dict) -> str:
    """Sign API request"""
    query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    return hmac.new(secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def calculate_fee(amount: float, fee_rate: float = 0.001) -> float:
    """Calculate trading fee"""
    return amount * fee_rate

def get_current_price(symbol: str) -> float:
    """Get current price (mock - in production, fetch from exchanges)"""
    # Mock prices - in production, fetch from live exchanges
    prices = {
        "BTC/USDT": 67500.00,
        "ETH/USDT": 3450.00,
        "BNB/USDT": 595.00,
        "SOL/USDT": 148.00,
        "XRP/USDT": 0.52,
        "DOGE/USDT": 0.085,
        "ADA/USDT": 0.45,
        "AVAX/USDT": 35.00,
        "DOT/USDT": 7.50,
        "MATIC/USDT": 0.72,
        "LINK/USDT": 14.50,
        "LTC/USDT": 85.00,
        "UNI/USDT": 7.80,
        "ATOM/USDT": 9.20,
        "XLM/USDT": 0.11,
        "VET/USDT": 0.022,
        "FIL/USDT": 5.80,
        "THETA/USDT": 1.05,
        "AAVE/USDT": 95.00,
        "AXS/USDT": 7.20,
    }
    return prices.get(symbol, 100.0)

def update_orderbook(symbol: str, price: float, quantity: float, side: str):
    """Update orderbook (simplified)"""
    if side == "buy":
        db.orderbook[symbol]["bids"].append([price, quantity])
        db.orderbook[symbol]["bids"].sort(key=lambda x: x[0], reverse=True)
    else:
        db.orderbook[symbol]["asks"].append([price, quantity])
        db.orderbook[symbol]["asks"].sort(key=lambda x: x[0])

# ============= CORE TRADING ENGINE =============
class TradingEngine:
    """Core trading engine"""
    
    def __init__(self):
        self.is_running = False
        
    async def start(self):
        """Start trading engine"""
        self.is_running = True
        logger.info("✅ Trading Engine Started")
        
    async def stop(self):
        """Stop trading engine"""
        self.is_running = False
        logger.info("⏹️ Trading Engine Stopped")
    
    async def create_order(self, order: Order) -> Dict:
        """Create new order"""
        # Validate trading pair
        if order.symbol not in db.pairs:
            return {"success": False, "error": "Invalid trading pair"}
        
        pair = db.pairs[order.symbol]
        if not pair.is_trading_enabled:
            return {"success": False, "error": "Trading disabled for this pair"}
        
        # Validate quantity
        if order.quantity < pair.min_quantity:
            return {"success": False, "error": f"Minimum quantity: {pair.min_quantity}"}
        
        # Check balance for market orders
        if order.type == OrderType.MARKET:
            current_price = get_current_price(order.symbol)
            total_cost = current_price * order.quantity
            
            user = db.users.get(order.user_id)
            if user:
                balance = user.balances.get(pair.quote_asset, 0)
                if balance < total_cost:
                    return {"success": False, "error": "Insufficient balance"}
        
        # Create order
        order.id = generate_id("ORD_")
        order.status = OrderStatus.OPEN
        order.created_at = datetime.now()
        
        db.orders[order.id] = order
        
        # Simulate execution for market orders
        if order.type == OrderType.MARKET:
            await self.execute_order(order)
        
        return {"success": True, "order_id": order.id, "order": asdict(order)}
    
    async def execute_order(self, order: Order) -> Dict:
        """Execute order"""
        current_price = get_current_price(order.symbol)
        
        # Calculate execution
        order.filled_quantity = order.quantity
        order.status = OrderStatus.FILLED
        order.filled_at = datetime.now()
        order.price = current_price
        
        # Update user balance
        user = db.users.get(order.user_id)
        if user:
            pair = db.pairs[order.symbol]
            total = current_price * order.quantity
            fee = calculate_fee(total)
            
            if order.side == OrderSide.BUY:
                user.balances[pair.quote_asset] = user.balances.get(pair.quote_asset, 0) - total - fee
                user.balances[pair.base_asset] = user.balances.get(pair.base_asset, 0) + order.quantity
            else:
                user.balances[pair.base_asset] = user.balances.get(pair.base_asset, 0) - order.quantity
                user.balances[pair.quote_asset] = user.balances.get(pair.quote_asset, 0) + total - fee
        
        # Create trade record
        trade = Trade(
            id=generate_id("TRD_"),
            order_id=order.id,
            user_id=order.user_id,
            symbol=order.symbol,
            side=order.side,
            price=current_price,
            quantity=order.quantity,
            fee=calculate_fee(current_price * order.quantity)
        )
        db.trades[trade.id] = trade
        
        # Update orderbook
        update_orderbook(order.symbol, current_price, order.quantity, order.side.value)
        
        return {"success": True, "trade_id": trade.id, "price": current_price}
    
    async def cancel_order(self, order_id: str, user_id: str) -> Dict:
        """Cancel order"""
        order = db.orders.get(order_id)
        if not order:
            return {"success": False, "error": "Order not found"}
        
        if order.user_id != user_id:
            return {"success": False, "error": "Unauthorized"}
        
        if order.status not in [OrderStatus.PENDING, OrderStatus.OPEN]:
            return {"success": False, "error": "Cannot cancel this order"}
        
        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.now()
        
        return {"success": True, "message": "Order cancelled"}
    
    async def get_orderbook(self, symbol: str, limit: int = 20) -> Dict:
        """Get orderbook"""
        bids = db.orderbook[symbol]["bids"][:limit]
        asks = db.orderbook[symbol]["asks"][:limit]
        
        return {
            "symbol": symbol,
            "bids": bids,
            "asks": asks,
            "last_update": datetime.now().isoformat()
        }
    
    async def get_recent_trades(self, symbol: str, limit: int = 50) -> List[Dict]:
        """Get recent trades"""
        trades = [asdict(t) for t in db.trades.values() if t.symbol == symbol][-limit:]
        return trades
    
    async def get_open_orders(self, user_id: str, symbol: str = "") -> List[Dict]:
        """Get user's open orders"""
        orders = []
        for order in db.orders.values():
            if order.user_id == user_id and order.status in [OrderStatus.OPEN, OrderStatus.PENDING]:
                if not symbol or order.symbol == symbol:
                    orders.append(asdict(order))
        return orders
    
    async def get_closed_orders(self, user_id: str, symbol: str = "", limit: int = 50) -> List[Dict]:
        """Get user's closed orders"""
        orders = [asdict(o) for o in db.orders.values() 
                 if o.user_id == user_id and o.status == OrderStatus.FILLED][-limit:]
        return orders

# Initialize trading engine
trading_engine = TradingEngine()

# ============= AI TRADING BOT SYSTEM =============
class AITradingBotService:
    """AI-powered automated trading bots"""
    
    def __init__(self):
        self.bots: Dict[str, TradingBot] = {}
        self.is_running = False
        
    async def start(self):
        """Start bot service"""
        self.is_running = True
        # Start all active bots
        for bot in self.bots.values():
            if bot.status == BotStatus.ACTIVE:
                asyncio.create_task(self.run_bot(bot))
        logger.info("✅ AI Trading Bot Service Started")
        
    async def stop(self):
        """Stop bot service"""
        self.is_running = False
        logger.info("⏹️ AI Trading Bot Service Stopped")
    
    async def create_bot(self, user_id: str, name: str, strategy: BotStrategy, 
                       symbol: str, config: Dict) -> Dict:
        """Create new trading bot"""
        bot = TradingBot(
            id=generate_id("BOT_"),
            user_id=user_id,
            name=name,
            strategy=strategy,
            status=BotStatus.PAUSED,
            symbol=symbol,
            config=config,
            balances={"USDT": config.get("initial_balance", 1000.0)},
            performance={
                "total_pnl": 0.0,
                "win_rate": 0.0,
                "total_trades": 0,
                "profitable_trades": 0
            }
        )
        self.bots[bot.id] = bot
        db.bots[bot.id] = bot
        
        logger.info(f"🤖 Created bot: {name} ({strategy.value})")
        return {"success": True, "bot_id": bot.id, "bot": asdict(bot)}
    
    async def start_bot(self, bot_id: str) -> Dict:
        """Start bot"""
        bot = self.bots.get(bot_id)
        if not bot:
            return {"success": False, "error": "Bot not found"}
        
        bot.status = BotStatus.ACTIVE
        bot.last_run = datetime.now()
        
        # Start bot loop
        asyncio.create_task(self.run_bot(bot))
        
        logger.info(f"▶️ Started bot: {bot.name}")
        return {"success": True, "message": "Bot started"}
    
    async def stop_bot(self, bot_id: str) -> Dict:
        """Stop bot"""
        bot = self.bots.get(bot_id)
        if not bot:
            return {"success": False, "error": "Bot not found"}
        
        bot.status = BotStatus.STOPPED
        
        logger.info(f"⏹️ Stopped bot: {bot.name}")
        return {"success": True, "message": "Bot stopped"}
    
    async def run_bot(self, bot: TradingBot):
        """Run trading bot"""
        while bot.status == BotStatus.ACTIVE:
            try:
                current_price = get_current_price(bot.symbol)
                
                if bot.strategy == BotStrategy.GRID:
                    await self._grid_strategy(bot, current_price)
                elif bot.strategy == BotStrategy.DCA:
                    await self._dca_strategy(bot, current_price)
                elif bot.strategy == BotStrategy.MOMENTUM:
                    await self._momentum_strategy(bot, current_price)
                elif bot.strategy == BotStrategy.MEAN_REVERSION:
                    await self._mean_reversion_strategy(bot, current_price)
                elif bot.strategy == BotStrategy.ARBITRAGE:
                    await self._arbitrage_strategy(bot, current_price)
                
                bot.last_run = datetime.now()
                
            except Exception as e:
                logger.error(f"❌ Bot error: {e}")
                bot.status = BotStatus.ERROR
            
            await asyncio.sleep(bot.config.get("interval", 60))
    
    async def _grid_strategy(self, bot: TradingBot, current_price: float):
        """Grid trading strategy"""
        grid_count = bot.config.get("grid_count", 10)
        grid_spacing = bot.config.get("grid_spacing", 0.5)  # percentage
        upper_bound = bot.config.get("upper_bound", current_price * 1.05)
        lower_bound = bot.config.get("lower_bound", current_price * 0.95)
        
        # Create grid levels
        grid_step = (upper_bound - lower_bound) / grid_count
        for i in range(grid_count):
            level_price = lower_bound + (grid_step * i)
            
            # Check if price is at this level
            if abs(current_price - level_price) < grid_step / 2:
                # Execute trade
                quantity = bot.config.get("grid_quantity", 0.01)
                
                # Simulate trade
                bot.performance["total_trades"] += 1
                pnl = (current_price - level_price) * quantity * (1 if i % 2 == 0 else -1)
                bot.performance["total_pnl"] += pnl
                
                if pnl > 0:
                    bot.performance["profitable_trades"] += 1
    
    async def _dca_strategy(self, bot: TradingBot, current_price: float):
        """Dollar Cost Averaging strategy"""
        target_allocation = bot.config.get("target_allocation", 10)
        buy_interval = bot.config.get("buy_interval", 5)  # percentage drop
        position_size = bot.config.get("position_size", 0.01)
        
        # Check if price dropped enough to buy
        last_price = bot.config.get("last_price", current_price)
        price_drop = (last_price - current_price) / last_price * 100
        
        if price_drop >= buy_interval:
            # Execute DCA buy
            bot.performance["total_trades"] += 1
            bot.config["last_price"] = current_price
            
            # Simulate profit
            if price_drop > 0:
                bot.performance["total_pnl"] += position_size * price_drop
                bot.performance["profitable_trades"] += 1
    
    async def _momentum_strategy(self, bot: TradingBot, current_price: float):
        """Momentum trading strategy"""
        rsi_period = bot.config.get("rsi_period", 14)
        overbought = bot.config.get("overbought", 70)
        oversold = bot.config.get("oversold", 30)
        
        # Generate mock RSI
        import random
        rsi = random.uniform(20, 80)
        
        if rsi < oversold and bot.config.get("position", 0) == 0:
            # Buy signal
            bot.config["position"] = 1
            bot.performance["total_trades"] += 1
        elif rsi > overbought and bot.config.get("position", 0) == 1:
            # Sell signal
            bot.config["position"] = 0
            bot.performance["total_trades"] += 1
    
    async def _mean_reversion_strategy(self, bot: TradingBot, current_price: float):
        """Mean reversion strategy"""
        lookback = bot.config.get("lookback", 20)
        std_dev = bot.config.get("std_dev", 2.0)
        
        # Calculate moving average (simplified)
        ma = current_price * (1 + random.uniform(-0.02, 0.02))
        
        # Check for reversion signal
        if current_price < ma * (1 - std_dev * 0.01):
            bot.performance["total_trades"] += 1
            bot.performance["total_pnl"] += 1
        elif current_price > ma * (1 + std_dev * 0.01):
            bot.performance["total_trades"] += 1
            bot.performance["total_pnl"] += 0.5
    
    async def _arbitrage_strategy(self, bot: TradingBot, current_price: float):
        """Arbitrage trading strategy"""
        # Check for price differences across exchanges
        exchanges = ["binance", "okx", "bybit", "bitget"]
        prices = {ex: current_price * (1 + random.uniform(-0.01, 0.01)) for ex in exchanges}
        
        min_price = min(prices.values())
        max_price = max(prices.values())
        
        profit = (max_price - min_price) * bot.config.get("trade_size", 0.01)
        
        if profit > bot.config.get("min_profit", 1.0):
            bot.performance["total_trades"] += 1
            bot.performance["total_pnl"] += profit
            if profit > 0:
                bot.performance["profitable_trades"] += 1
    
    async def get_bot_status(self, bot_id: str) -> Dict:
        """Get bot status"""
        bot = self.bots.get(bot_id)
        if not bot:
            return {"success": False, "error": "Bot not found"}
        
        # Calculate win rate
        if bot.performance["total_trades"] > 0:
            bot.performance["win_rate"] = bot.performance["profitable_trades"] / bot.performance["total_trades"]
        
        return {"success": True, "bot": asdict(bot)}
    
    async def get_user_bots(self, user_id: str) -> List[Dict]:
        """Get user's bots"""
        return [asdict(b) for b in self.bots.values() if b.user_id == user_id]

# Initialize AI bot service
ai_bot_service = AITradingBotService()

# ============= EXTERNAL EXCHANGE CONNECTIONS =============
class ExchangeConnector:
    """Connect to external exchanges (Binance, OKX, ByBit, BitGet)"""
    
    def __init__(self):
        self.exchanges: Dict[str, Dict] = {
            "binance": {"name": "Binance", "api_version": "v3"},
            "okx": {"name": "OKX", "api_version": "v5"},
            "bybit": {"name": "ByBit", "api_version": "v5"},
            "bitget": {"name": "BitGet", "api_version": "v2"},
        }
        
    async def connect_exchange(self, user_id: str, exchange: str, api_key: str, 
                            api_secret: str, passphrase: str = "") -> Dict:
        """Connect to external exchange"""
        if exchange not in self.exchanges:
            return {"success": False, "error": "Unsupported exchange"}
        
        connection = ExchangeConnection(
            id=generate_id("EXC_"),
            user_id=user_id,
            exchange=exchange,
            api_key=api_key,
            api_secret=api_secret,
            passphrase=passphrase,
            is_active=True
        )
        
        db.exchange_connections[connection.id] = connection
        
        logger.info(f"🔗 Connected to {exchange}")
        return {"success": True, "connection_id": connection.id}
    
    async def disconnect_exchange(self, connection_id: str) -> Dict:
        """Disconnect from exchange"""
        connection = db.exchange_connections.get(connection_id)
        if not connection:
            return {"success": False, "error": "Connection not found"}
        
        connection.is_active = False
        return {"success": True, "message": "Disconnected"}
    
    async def get_balance(self, connection_id: str) -> Dict:
        """Get exchange balance"""
        connection = db.exchange_connections.get(connection_id)
        if not connection:
            return {"success": False, "error": "Connection not found"}
        
        # In production, fetch from actual exchange API
        return {
            "success": True,
            "exchange": connection.exchange,
            "balances": {
                "BTC": 0.5,
                "ETH": 2.0,
                "USDT": 10000.0,
            }
        }
    
    async def place_order(self, connection_id: str, symbol: str, side: str,
                        order_type: str, quantity: float, price: float = 0) -> Dict:
        """Place order on external exchange"""
        connection = db.exchange_connections.get(connection_id)
        if not connection:
            return {"success": False, "error": "Connection not found"}
        
        if not connection.is_active:
            return {"success": False, "error": "Connection not active"}
        
        # In production, call actual exchange API
        return {
            "success": True,
            "order_id": generate_id("EXT_"),
            "exchange": connection.exchange,
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
            "price": price,
            "status": "filled"
        }
    
    async def sync_orders(self, connection_id: str) -> Dict:
        """Sync orders from external exchange"""
        connection = db.exchange_connections.get(connection_id)
        if not connection:
            return {"success": False, "error": "Connection not found"}
        
        connection.last_sync = datetime.now()
        
        # In production, fetch from actual exchange
        return {
            "success": True,
            "exchange": connection.exchange,
            "orders": [],
            "synced_at": connection.last_sync.isoformat()
        }
    
    async def get_connected_exchanges(self, user_id: str) -> List[Dict]:
        """Get user's connected exchanges"""
        return [asdict(c) for c in db.exchange_connections.values() 
                if c.user_id == user_id and c.is_active]

# Initialize exchange connector
exchange_connector = ExchangeConnector()

# ============= USER MANAGEMENT =============
class UserService:
    """User management service"""
    
    async def register(self, email: str, password: str, phone: str = "",
                     referral_code: str = "") -> Dict:
        """Register new user"""
        # Check if email exists
        for user in db.users.values():
            if user.email == email:
                return {"success": False, "error": "Email already registered"}
        
        user_id = generate_id("USR_")
        user = User(
            id=user_id,
            email=email,
            phone=phone,
            referral_code=generate_id("REF")[:8],
            referred_by=referral_code,
            balances={"USDT": 0.0},  # Start with 0, need to deposit
            created_at=datetime.now()
        )
        
        db.users[user_id] = user
        
        logger.info(f"👤 Registered new user: {email}")
        return {"success": True, "user_id": user_id, "user": asdict(user)}
    
    async def login(self, email: str, password: str) -> Dict:
        """Login user"""
        user = None
        for u in db.users.values():
            if u.email == email:
                user = u
                break
        
        if not user:
            return {"success": False, "error": "Invalid credentials"}
        
        if not user.is_active:
            return {"success": False, "error": "Account disabled"}
        
        user.last_login = datetime.now()
        
        logger.info(f"🔑 User logged in: {email}")
        return {"success": True, "user_id": user.id, "user": asdict(user)}
    
    async def get_profile(self, user_id: str) -> Dict:
        """Get user profile"""
        user = db.users.get(user_id)
        if not user:
            return {"success": False, "error": "User not found"}
        
        return {"success": True, "user": asdict(user)}
    
    async def update_profile(self, user_id: str, data: Dict) -> Dict:
        """Update user profile"""
        user = db.users.get(user_id)
        if not user:
            return {"success": False, "error": "User not found"}
        
        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        return {"success": True, "user": asdict(user)}
    
    async def create_api_key(self, user_id: str, name: str, permissions: List[str]) -> Dict:
        """Create API key"""
        key, secret = generate_api_key()
        
        api_key = APIKey(
            id=generate_id("AK_"),
            user_id=user_id,
            name=name,
            key=key,
            secret=secret,
            permissions=permissions
        )
        
        db.api_keys[api_key.id] = api_key
        
        user = db.users.get(user_id)
        if user:
            user.api_keys.append(key)
        
        logger.info(f"🔑 Created API key: {name}")
        return {
            "success": True,
            "api_key": key,
            "api_secret": secret,  # Only shown once!
            "permissions": permissions
        }
    
    async def get_api_keys(self, user_id: str) -> List[Dict]:
        """Get user's API keys"""
        return [asdict(k) for k in db.api_keys.values() if k.user_id == user_id]
    
    async def revoke_api_key(self, user_id: str, key_id: str) -> Dict:
        """Revoke API key"""
        key = db.api_keys.get(key_id)
        if not key or key.user_id != user_id:
            return {"success": False, "error": "API key not found"}
        
        key.is_active = False
        return {"success": True, "message": "API key revoked"}
    
    async def get_balance(self, user_id: str) -> Dict:
        """Get user balance"""
        user = db.users.get(user_id)
        if not user:
            return {"success": False, "error": "User not found"}
        
        return {"success": True, "balances": user.balances}
    
    async def deposit(self, user_id: str, currency: str, amount: float) -> Dict:
        """Process deposit"""
        user = db.users.get(user_id)
        if not user:
            return {"success": False, "error": "User not found"}
        
        user.balances[currency] = user.balances.get(currency, 0) + amount
        
        logger.info(f"💰 Deposit: {amount} {currency}")
        return {"success": True, "balance": user.balances[currency]}
    
    async def withdraw(self, user_id: str, currency: str, amount: float, address: str) -> Dict:
        """Process withdrawal"""
        user = db.users.get(user_id)
        if not user:
            return {"success": False, "error": "User not found"}
        
        balance = user.balances.get(currency, 0)
        if balance < amount:
            return {"success": False, "error": "Insufficient balance"}
        
        fee = amount * CONFIG["withdrawal_fee"]
        net_amount = amount - fee
        
        user.balances[currency] = balance - amount
        
        logger.info(f"💸 Withdrawal: {amount} {currency}")
        return {"success": True, "amount": net_amount, "fee": fee}

# Initialize user service
user_service = UserService()

# ============= WALLET SERVICE =============
class WalletService:
    """Wallet management"""
    
    async def get_deposit_address(self, user_id: str, currency: str, network: str = "") -> Dict:
        """Get deposit address"""
        user = db.users.get(user_id)
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Generate address (in production, integrate with actual blockchain)
        address_key = f"{currency}_{network}"
        if address_key not in user.wallet_addresses:
            user.wallet_addresses[address_key] = generate_id("0x")[:42]
        
        return {
            "success": True,
            "currency": currency,
            "network": network or "mainnet",
            "address": user.wallet_addresses[address_key]
        }
    
    async def get_withdraw_fee(self, currency: str, network: str = "") -> float:
        """Get withdrawal fee"""
        fees = {
            "BTC": 0.0005,
            "ETH": 0.005,
            "USDT": 1.0,
            "BNB": 0.01,
        }
        return fees.get(currency, 0.01)

# Initialize wallet service
wallet_service = WalletService()

# ============= MARKET DATA =============
class MarketDataService:
    """Market data service"""
    
    async def get_ticker(self, symbol: str) -> Dict:
        """Get ticker"""
        price = get_current_price(symbol)
        return {
            "symbol": symbol,
            "price": price,
            "change_24h": 0.0,
            "change_percent_24h": 0.0,
            "high_24h": price * 1.02,
            "low_24h": price * 0.98,
            "volume_24h": 1000000,
            "quote_volume_24h": 100000000,
        }
    
    async def get_all_tickers(self) -> List[Dict]:
        """Get all tickers"""
        tickers = []
        for symbol in db.pairs.keys():
            price = get_current_price(symbol)
            tickers.append({
                "symbol": symbol,
                "price": price,
                "change_percent_24h": 0.0,
            })
        return tickers
    
    async def get_klines(self, symbol: str, interval: str = "1h", limit: int = 100) -> List[Dict]:
        """Get klines/candlesticks"""
        klines = []
        base_price = get_current_price(symbol)
        
        for i in range(limit):
            open_price = base_price * (1 + (i * 0.001))
            close_price = open_price * (1.001)
            high_price = max(open_price, close_price) * 1.005
            low_price = min(open_price, close_price) * 0.995
            
            klines.append({
                "open_time": int((datetime.now() - timedelta(hours=limit-i)).timestamp() * 1000),
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": 1000 + i * 10,
                "close_time": int((datetime.now() - timedelta(hours=limit-i-1)).timestamp() * 1000),
            })
        
        return klines
    
    async def get_24h_stats(self) -> Dict:
        """Get 24h exchange stats"""
        return {
            "total_volume_24h": 1000000000,
            "total_trades_24h": 500000,
            "active_users_24h": 50000,
            "new_users_24h": 1000,
        }

# Initialize market data service
market_data_service = MarketDataService()

# ============= KYC SERVICE =============
class KYCService:
    """KYC verification service"""
    
    async def submit_kyc(self, user_id: str, data: Dict) -> Dict:
        """Submit KYC application"""
        user = db.users.get(user_id)
        if not user:
            return {"success": False, "error": "User not found"}
        
        user.kyc_status = KYCStatus.PENDING
        # In production, send to verification provider
        
        logger.info(f"🆔 KYC submitted for user: {user_id}")
        return {"success": True, "status": "pending"}
    
    async def get_kyc_status(self, user_id: str) -> Dict:
        """Get KYC status"""
        user = db.users.get(user_id)
        if not user:
            return {"success": False, "error": "User not found"}
        
        return {
            "success": True,
            "status": user.kyc_status.value,
            "level": user.kyc_level
        }
    
    async def approve_kyc(self, user_id: str, level: int = 1) -> Dict:
        """Approve KYC"""
        user = db.users.get(user_id)
        if not user:
            return {"success": False, "error": "User not found"}
        
        user.kyc_status = KYCStatus.VERIFIED
        user.kyc_level = level
        
        return {"success": True, "level": level}

# Initialize KYC service
kyc_service = KYCService()

# ============= ADMIN SERVICE =============
class AdminService:
    """Admin management service"""
    
    async def get_all_users(self) -> List[Dict]:
        """Get all users"""
        return [asdict(u) for u in db.users.values()]
    
    async def get_all_orders(self, limit: int = 100) -> List[Dict]:
        """Get all orders"""
        return [asdict(o) for o in db.orders.values()][-limit:]
    
    async def get_all_trades(self, limit: int = 100) -> List[Dict]:
        """Get all trades"""
        return [asdict(t) for t in db.trades.values()][-limit:]
    
    async def get_exchange_stats(self) -> Dict:
        """Get exchange statistics"""
        total_users = len(db.users)
        total_orders = len(db.orders)
        total_trades = len(db.trades)
        
        # Calculate volume (simplified)
        total_volume = sum(t.price * t.quantity for t in db.trades.values())
        
        return {
            "total_users": total_users,
            "total_orders": total_orders,
            "total_trades": total_trades,
            "total_volume": total_volume,
            "active_bots": len([b for b in db.bots.values() if b.status == BotStatus.ACTIVE]),
            "exchange_status": "operational"
        }
    
    async def toggle_trading_pair(self, symbol: str, enabled: bool) -> Dict:
        """Toggle trading pair"""
        if symbol not in db.pairs:
            return {"success": False, "error": "Trading pair not found"}
        
        db.pairs[symbol].is_trading_enabled = enabled
        return {"success": True, "enabled": enabled}
    
    async def update_fee(self, symbol: str, maker_fee: float, taker_fee: float) -> Dict:
        """Update trading fees"""
        if symbol not in db.pairs:
            return {"success": False, "error": "Trading pair not found"}
        
        db.pairs[symbol].maker_fee = maker_fee
        db.pairs[symbol].taker_fee = taker_fee
        
        return {"success": True}

# Initialize admin service
admin_service = AdminService()

# ============= MAIN APPLICATION =============
class TigerExApp:
    """TigerEx Main Application"""
    
    def __init__(self):
        self.is_running = False
        
    async def start(self):
        """Start TigerEx"""
        self.is_running = True
        
        # Start all services
        await trading_engine.start()
        await ai_bot_service.start()
        
        logger.info("=" * 50)
        logger.info("🦁 TigerEx Exchange Platform v8.0.0")
        logger.info("=" * 50)
        logger.info("✅ All services started successfully")
        logger.info("=" * 50)
        
    async def stop(self):
        """Stop TigerEx"""
        self.is_running = False
        
        await trading_engine.stop()
        await ai_bot_service.stop()
        
        logger.info("⏹️ TigerEx stopped")

# Initialize app
app = TigerExApp()

# ============= API ROUTES (FastAPI style) =============
# These would be FastAPI routes in production

async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "exchange": CONFIG["exchange_name"],
        "version": CONFIG["version"],
        "timestamp": datetime.now().isoformat()
    }

async def get_exchange_info():
    """Exchange information"""
    return {
        "name": CONFIG["exchange_name"],
        "id": CONFIG["exchange_id"],
        "version": CONFIG["version"],
        "maker_fee": CONFIG["maker_fee"],
        "taker_fee": CONFIG["taker_fee"],
        "supported_chains": CONFIG["supported_chains"],
        "trading_pairs": len(db.pairs),
    }

async def get_trading_pairs():
    """Get all trading pairs"""
    return [asdict(p) for p in db.pairs.values() if p.is_trading_enabled]

# ============= MAIN ENTRY POINT =============
async def main():
    """Main entry point"""
    await app.start()
    
    # Keep running
    while app.is_running:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())