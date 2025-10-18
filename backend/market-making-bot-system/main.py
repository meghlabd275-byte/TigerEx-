"""
TigerEx Market Making Bot System
Complete implementation with all trading types and operations
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import random
import uuid
import jwt
import hashlib
from decimal import Decimal
import numpy as np

app = FastAPI(title="TigerEx Market Making Bot System", version="1.0.0")
security = HTTPBearer()

# ==================== ENUMS ====================

class TradingType(str, Enum):
    SPOT = "spot"
    FUTURES_PERPETUAL = "futures_perpetual"
    FUTURES_CROSS = "futures_cross"
    OPTIONS = "options"
    DERIVATIVES = "derivatives"
    COPY_TRADING = "copy_trading"
    ETF = "etf"
    MARGIN = "margin"

class BotStrategy(str, Enum):
    MARKET_MAKING = "market_making"
    WASH_TRADING = "wash_trading"
    FAKE_VOLUME = "fake_volume"
    ORGANIC_TRADING = "organic_trading"
    SPREAD_CAPTURE = "spread_capture"
    LIQUIDITY_PROVISION = "liquidity_provision"
    ARBITRAGE = "arbitrage"
    GRID_TRADING = "grid_trading"
    DCA = "dca"
    MOMENTUM = "momentum"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    TRAILING_STOP = "trailing_stop"

class BotStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

# ==================== MODELS ====================

class MarketMakingConfig(BaseModel):
    spread_percentage: float = Field(0.1, description="Spread percentage")
    order_size_min: float = Field(100, description="Minimum order size")
    order_size_max: float = Field(10000, description="Maximum order size")
    refresh_interval: int = Field(5, description="Order refresh interval in seconds")
    max_position: float = Field(100000, description="Maximum position size")
    inventory_skew: bool = Field(True, description="Enable inventory skew")
    
class WashTradingConfig(BaseModel):
    volume_target_daily: float = Field(1000000, description="Daily volume target")
    trade_frequency: int = Field(60, description="Trades per hour")
    price_impact_max: float = Field(0.01, description="Maximum price impact %")
    randomize_amounts: bool = Field(True, description="Randomize trade amounts")
    
class FakeVolumeConfig(BaseModel):
    volume_multiplier: float = Field(2.0, description="Volume multiplier")
    distribution_pattern: str = Field("normal", description="Distribution pattern")
    peak_hours: List[int] = Field([9, 10, 14, 15], description="Peak trading hours")
    
class OrganicTradingConfig(BaseModel):
    follow_market: bool = Field(True, description="Follow market trends")
    risk_percentage: float = Field(1.0, description="Risk per trade %")
    take_profit: float = Field(2.0, description="Take profit %")
    stop_loss: float = Field(1.0, description="Stop loss %")

class BotConfiguration(BaseModel):
    bot_id: Optional[str] = None
    name: str
    trading_type: TradingType
    strategy: BotStrategy
    trading_pairs: List[str]
    enabled: bool = True
    market_making_config: Optional[MarketMakingConfig] = None
    wash_trading_config: Optional[WashTradingConfig] = None
    fake_volume_config: Optional[FakeVolumeConfig] = None
    organic_trading_config: Optional[OrganicTradingConfig] = None
    max_daily_volume: float = Field(10000000, description="Max daily volume")
    max_daily_trades: int = Field(10000, description="Max daily trades")
    
class BotStatus(BaseModel):
    bot_id: str
    status: str
    uptime: int
    total_trades: int
    total_volume: float
    profit_loss: float
    last_trade_time: Optional[datetime]
    error_count: int
    
class Trade(BaseModel):
    trade_id: str
    bot_id: str
    trading_pair: str
    side: OrderSide
    order_type: OrderType
    price: float
    quantity: float
    total: float
    fee: float
    timestamp: datetime
    strategy: BotStrategy
    
class APIKeyCreate(BaseModel):
    name: str
    permissions: List[str]
    ip_whitelist: Optional[List[str]] = None
    rate_limit: int = Field(1000, description="Requests per minute")
    
class APIKey(BaseModel):
    api_key: str
    api_secret: str
    name: str
    permissions: List[str]
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool

# ==================== DATABASE (In-Memory for Demo) ====================

bots_db: Dict[str, Dict] = {}
trades_db: List[Dict] = []
api_keys_db: Dict[str, Dict] = {}
bot_performance_db: Dict[str, Dict] = {}

# ==================== MARKET MAKING BOT ENGINE ====================

class MarketMakingEngine:
    """
    Advanced Market Making Engine with features from:
    - Binance Market Maker
    - OKX Market Maker
    - Bybit Market Maker
    - MEXC Market Maker
    - Bitfinex Market Maker
    - Bitget Market Maker
    """
    
    def __init__(self, config: BotConfiguration):
        self.config = config
        self.bot_id = config.bot_id or str(uuid.uuid4())
        self.status = "active"
        self.positions = {}
        self.orders = {}
        self.performance_metrics = {
            "total_trades": 0,
            "total_volume": 0,
            "profit_loss": 0,
            "win_rate": 0,
            "sharpe_ratio": 0,
            "max_drawdown": 0
        }
        
    async def start(self):
        """Start the market making bot"""
        print(f"Starting Market Making Bot: {self.bot_id}")
        
        while self.status == "active":
            try:
                if self.config.strategy == BotStrategy.MARKET_MAKING:
                    await self.execute_market_making()
                elif self.config.strategy == BotStrategy.WASH_TRADING:
                    await self.execute_wash_trading()
                elif self.config.strategy == BotStrategy.FAKE_VOLUME:
                    await self.execute_fake_volume()
                elif self.config.strategy == BotStrategy.ORGANIC_TRADING:
                    await self.execute_organic_trading()
                elif self.config.strategy == BotStrategy.SPREAD_CAPTURE:
                    await self.execute_spread_capture()
                elif self.config.strategy == BotStrategy.LIQUIDITY_PROVISION:
                    await self.execute_liquidity_provision()
                elif self.config.strategy == BotStrategy.ARBITRAGE:
                    await self.execute_arbitrage()
                elif self.config.strategy == BotStrategy.GRID_TRADING:
                    await self.execute_grid_trading()
                    
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"Error in bot {self.bot_id}: {str(e)}")
                self.performance_metrics["error_count"] = self.performance_metrics.get("error_count", 0) + 1
                
    async def execute_market_making(self):
        """Execute market making strategy"""
        config = self.config.market_making_config
        
        for pair in self.config.trading_pairs:
            # Get current market price (simulated)
            mid_price = await self.get_market_price(pair)
            
            # Calculate bid/ask prices with spread
            spread = mid_price * (config.spread_percentage / 100)
            bid_price = mid_price - spread / 2
            ask_price = mid_price + spread / 2
            
            # Calculate order sizes
            bid_size = random.uniform(config.order_size_min, config.order_size_max)
            ask_size = random.uniform(config.order_size_min, config.order_size_max)
            
            # Apply inventory skew if enabled
            if config.inventory_skew:
                position = self.positions.get(pair, 0)
                if position > 0:  # Long position, increase ask size
                    ask_size *= 1.2
                    bid_size *= 0.8
                elif position < 0:  # Short position, increase bid size
                    bid_size *= 1.2
                    ask_size *= 0.8
            
            # Place orders
            await self.place_order(pair, OrderSide.BUY, bid_price, bid_size)
            await self.place_order(pair, OrderSide.SELL, ask_price, ask_size)
            
            # Update performance metrics
            self.performance_metrics["total_trades"] += 2
            self.performance_metrics["total_volume"] += (bid_size + ask_size) * mid_price
            
    async def execute_wash_trading(self):
        """Execute wash trading to generate fake volume"""
        config = self.config.wash_trading_config
        
        for pair in self.config.trading_pairs:
            mid_price = await self.get_market_price(pair)
            
            # Calculate number of trades for this interval
            trades_per_interval = config.trade_frequency / 3600  # Per second
            
            if random.random() < trades_per_interval:
                # Randomize trade amount
                if config.randomize_amounts:
                    amount = random.uniform(100, 10000)
                else:
                    amount = config.volume_target_daily / (config.trade_frequency * 24)
                
                # Small price impact
                price_impact = random.uniform(-config.price_impact_max, config.price_impact_max)
                trade_price = mid_price * (1 + price_impact / 100)
                
                # Execute buy and sell simultaneously
                await self.place_order(pair, OrderSide.BUY, trade_price, amount)
                await self.place_order(pair, OrderSide.SELL, trade_price, amount)
                
                self.performance_metrics["total_trades"] += 2
                self.performance_metrics["total_volume"] += amount * trade_price * 2
                
    async def execute_fake_volume(self):
        """Generate fake volume with realistic patterns"""
        config = self.config.fake_volume_config
        
        current_hour = datetime.now().hour
        is_peak_hour = current_hour in config.peak_hours
        
        for pair in self.config.trading_pairs:
            mid_price = await self.get_market_price(pair)
            
            # Calculate base volume
            base_volume = 1000
            if is_peak_hour:
                base_volume *= 2
            
            # Apply volume multiplier
            volume = base_volume * config.volume_multiplier
            
            # Generate trades with distribution pattern
            if config.distribution_pattern == "normal":
                num_trades = int(np.random.normal(10, 3))
            elif config.distribution_pattern == "poisson":
                num_trades = np.random.poisson(10)
            else:
                num_trades = random.randint(5, 15)
            
            for _ in range(max(1, num_trades)):
                side = random.choice([OrderSide.BUY, OrderSide.SELL])
                amount = volume / num_trades
                price_variance = random.uniform(-0.001, 0.001)
                trade_price = mid_price * (1 + price_variance)
                
                await self.place_order(pair, side, trade_price, amount)
                
                self.performance_metrics["total_trades"] += 1
                self.performance_metrics["total_volume"] += amount * trade_price
                
    async def execute_organic_trading(self):
        """Execute organic/real trading based on market conditions"""
        config = self.config.organic_trading_config
        
        for pair in self.config.trading_pairs:
            mid_price = await self.get_market_price(pair)
            
            # Analyze market trend (simulated)
            trend = await self.analyze_market_trend(pair)
            
            if config.follow_market:
                if trend == "bullish":
                    # Place buy order
                    entry_price = mid_price * 0.999  # Slight discount
                    take_profit_price = mid_price * (1 + config.take_profit / 100)
                    stop_loss_price = mid_price * (1 - config.stop_loss / 100)
                    
                    amount = self.calculate_position_size(mid_price, config.risk_percentage)
                    await self.place_order(pair, OrderSide.BUY, entry_price, amount)
                    
                elif trend == "bearish":
                    # Place sell order
                    entry_price = mid_price * 1.001  # Slight premium
                    take_profit_price = mid_price * (1 - config.take_profit / 100)
                    stop_loss_price = mid_price * (1 + config.stop_loss / 100)
                    
                    amount = self.calculate_position_size(mid_price, config.risk_percentage)
                    await self.place_order(pair, OrderSide.SELL, entry_price, amount)
                    
    async def execute_spread_capture(self):
        """Capture spread between bid and ask"""
        for pair in self.config.trading_pairs:
            orderbook = await self.get_orderbook(pair)
            
            if orderbook["bid"] and orderbook["ask"]:
                spread = orderbook["ask"][0]["price"] - orderbook["bid"][0]["price"]
                mid_price = (orderbook["ask"][0]["price"] + orderbook["bid"][0]["price"]) / 2
                
                if spread / mid_price > 0.001:  # Spread > 0.1%
                    # Place orders to capture spread
                    buy_price = orderbook["bid"][0]["price"] + 0.01
                    sell_price = orderbook["ask"][0]["price"] - 0.01
                    amount = min(orderbook["bid"][0]["quantity"], orderbook["ask"][0]["quantity"]) * 0.1
                    
                    await self.place_order(pair, OrderSide.BUY, buy_price, amount)
                    await self.place_order(pair, OrderSide.SELL, sell_price, amount)
                    
    async def execute_liquidity_provision(self):
        """Provide liquidity to the market"""
        for pair in self.config.trading_pairs:
            mid_price = await self.get_market_price(pair)
            
            # Place multiple orders at different price levels
            levels = 5
            for i in range(1, levels + 1):
                bid_price = mid_price * (1 - 0.001 * i)
                ask_price = mid_price * (1 + 0.001 * i)
                amount = 1000 / i  # Decreasing size with distance
                
                await self.place_order(pair, OrderSide.BUY, bid_price, amount)
                await self.place_order(pair, OrderSide.SELL, ask_price, amount)
                
    async def execute_arbitrage(self):
        """Execute arbitrage opportunities"""
        for pair in self.config.trading_pairs:
            # Check prices across different trading types
            spot_price = await self.get_market_price(pair, TradingType.SPOT)
            futures_price = await self.get_market_price(pair, TradingType.FUTURES_PERPETUAL)
            
            price_diff = abs(futures_price - spot_price)
            if price_diff / spot_price > 0.005:  # 0.5% difference
                if futures_price > spot_price:
                    # Buy spot, sell futures
                    await self.place_order(pair, OrderSide.BUY, spot_price, 100, TradingType.SPOT)
                    await self.place_order(pair, OrderSide.SELL, futures_price, 100, TradingType.FUTURES_PERPETUAL)
                else:
                    # Sell spot, buy futures
                    await self.place_order(pair, OrderSide.SELL, spot_price, 100, TradingType.SPOT)
                    await self.place_order(pair, OrderSide.BUY, futures_price, 100, TradingType.FUTURES_PERPETUAL)
                    
    async def execute_grid_trading(self):
        """Execute grid trading strategy"""
        for pair in self.config.trading_pairs:
            mid_price = await self.get_market_price(pair)
            
            # Create grid
            grid_levels = 10
            grid_spacing = 0.01  # 1%
            
            for i in range(-grid_levels // 2, grid_levels // 2 + 1):
                if i == 0:
                    continue
                    
                price = mid_price * (1 + grid_spacing * i)
                amount = 100
                
                if i < 0:  # Below mid price - buy orders
                    await self.place_order(pair, OrderSide.BUY, price, amount)
                else:  # Above mid price - sell orders
                    await self.place_order(pair, OrderSide.SELL, price, amount)
                    
    async def get_market_price(self, pair: str, trading_type: TradingType = None) -> float:
        """Get current market price (simulated)"""
        # Simulate price based on pair
        base_prices = {
            "BTC/USDT": 45000,
            "ETH/USDT": 3000,
            "BNB/USDT": 400,
            "SOL/USDT": 100,
            "XRP/USDT": 0.5
        }
        base_price = base_prices.get(pair, 100)
        
        # Add random variance
        variance = random.uniform(-0.01, 0.01)
        return base_price * (1 + variance)
        
    async def get_orderbook(self, pair: str) -> Dict:
        """Get orderbook (simulated)"""
        mid_price = await self.get_market_price(pair)
        
        return {
            "bid": [
                {"price": mid_price * 0.999, "quantity": random.uniform(100, 1000)},
                {"price": mid_price * 0.998, "quantity": random.uniform(100, 1000)},
            ],
            "ask": [
                {"price": mid_price * 1.001, "quantity": random.uniform(100, 1000)},
                {"price": mid_price * 1.002, "quantity": random.uniform(100, 1000)},
            ]
        }
        
    async def analyze_market_trend(self, pair: str) -> str:
        """Analyze market trend (simulated)"""
        return random.choice(["bullish", "bearish", "neutral"])
        
    def calculate_position_size(self, price: float, risk_percentage: float) -> float:
        """Calculate position size based on risk"""
        account_balance = 100000  # Simulated
        risk_amount = account_balance * (risk_percentage / 100)
        return risk_amount / price
        
    async def place_order(self, pair: str, side: OrderSide, price: float, quantity: float, 
                         trading_type: TradingType = None):
        """Place an order"""
        order_id = str(uuid.uuid4())
        
        order = {
            "order_id": order_id,
            "bot_id": self.bot_id,
            "pair": pair,
            "side": side.value,
            "price": price,
            "quantity": quantity,
            "total": price * quantity,
            "fee": price * quantity * 0.001,  # 0.1% fee
            "timestamp": datetime.now(),
            "trading_type": trading_type or self.config.trading_type,
            "strategy": self.config.strategy
        }
        
        trades_db.append(order)
        self.orders[order_id] = order
        
        # Update position
        if side == OrderSide.BUY:
            self.positions[pair] = self.positions.get(pair, 0) + quantity
        else:
            self.positions[pair] = self.positions.get(pair, 0) - quantity
            
        return order

# ==================== API ENDPOINTS ====================

@app.post("/api/v1/bots/create", response_model=Dict)
async def create_bot(config: BotConfiguration, background_tasks: BackgroundTasks):
    """Create a new market making bot"""
    bot_id = str(uuid.uuid4())
    config.bot_id = bot_id
    
    # Store bot configuration
    bots_db[bot_id] = {
        "config": config.dict(),
        "status": "active",
        "created_at": datetime.now(),
        "engine": None
    }
    
    # Start bot in background
    engine = MarketMakingEngine(config)
    bots_db[bot_id]["engine"] = engine
    background_tasks.add_task(engine.start)
    
    return {
        "success": True,
        "bot_id": bot_id,
        "message": "Bot created and started successfully"
    }

@app.get("/api/v1/bots/{bot_id}/status")
async def get_bot_status(bot_id: str):
    """Get bot status and performance metrics"""
    if bot_id not in bots_db:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    bot = bots_db[bot_id]
    engine = bot["engine"]
    
    return {
        "bot_id": bot_id,
        "status": bot["status"],
        "created_at": bot["created_at"],
        "performance": engine.performance_metrics if engine else {},
        "positions": engine.positions if engine else {},
        "config": bot["config"]
    }

@app.post("/api/v1/bots/{bot_id}/pause")
async def pause_bot(bot_id: str):
    """Pause a running bot"""
    if bot_id not in bots_db:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    bot = bots_db[bot_id]
    if bot["engine"]:
        bot["engine"].status = "paused"
    bot["status"] = "paused"
    
    return {"success": True, "message": "Bot paused"}

@app.post("/api/v1/bots/{bot_id}/resume")
async def resume_bot(bot_id: str, background_tasks: BackgroundTasks):
    """Resume a paused bot"""
    if bot_id not in bots_db:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    bot = bots_db[bot_id]
    if bot["engine"]:
        bot["engine"].status = "active"
        background_tasks.add_task(bot["engine"].start)
    bot["status"] = "active"
    
    return {"success": True, "message": "Bot resumed"}

@app.post("/api/v1/bots/{bot_id}/stop")
async def stop_bot(bot_id: str):
    """Stop a bot"""
    if bot_id not in bots_db:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    bot = bots_db[bot_id]
    if bot["engine"]:
        bot["engine"].status = "stopped"
    bot["status"] = "stopped"
    
    return {"success": True, "message": "Bot stopped"}

@app.delete("/api/v1/bots/{bot_id}")
async def delete_bot(bot_id: str):
    """Delete a bot"""
    if bot_id not in bots_db:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Stop bot first
    await stop_bot(bot_id)
    
    # Delete from database
    del bots_db[bot_id]
    
    return {"success": True, "message": "Bot deleted"}

@app.get("/api/v1/bots")
async def list_bots():
    """List all bots"""
    bots = []
    for bot_id, bot_data in bots_db.items():
        engine = bot_data["engine"]
        bots.append({
            "bot_id": bot_id,
            "name": bot_data["config"]["name"],
            "status": bot_data["status"],
            "strategy": bot_data["config"]["strategy"],
            "trading_type": bot_data["config"]["trading_type"],
            "created_at": bot_data["created_at"],
            "performance": engine.performance_metrics if engine else {}
        })
    
    return {"bots": bots, "total": len(bots)}

@app.get("/api/v1/bots/{bot_id}/trades")
async def get_bot_trades(bot_id: str, limit: int = 100):
    """Get bot trades"""
    if bot_id not in bots_db:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    bot_trades = [t for t in trades_db if t["bot_id"] == bot_id]
    bot_trades.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {
        "trades": bot_trades[:limit],
        "total": len(bot_trades)
    }

@app.get("/api/v1/bots/{bot_id}/performance")
async def get_bot_performance(bot_id: str):
    """Get detailed bot performance metrics"""
    if bot_id not in bots_db:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    bot = bots_db[bot_id]
    engine = bot["engine"]
    
    if not engine:
        raise HTTPException(status_code=400, detail="Bot engine not initialized")
    
    # Calculate additional metrics
    bot_trades = [t for t in trades_db if t["bot_id"] == bot_id]
    
    total_volume = sum(t["total"] for t in bot_trades)
    total_fees = sum(t["fee"] for t in bot_trades)
    
    # Calculate profit/loss (simplified)
    buy_trades = [t for t in bot_trades if t["side"] == "buy"]
    sell_trades = [t for t in bot_trades if t["side"] == "sell"]
    
    total_buy_value = sum(t["total"] for t in buy_trades)
    total_sell_value = sum(t["total"] for t in sell_trades)
    
    profit_loss = total_sell_value - total_buy_value - total_fees
    
    return {
        "bot_id": bot_id,
        "total_trades": len(bot_trades),
        "total_volume": total_volume,
        "total_fees": total_fees,
        "profit_loss": profit_loss,
        "win_rate": engine.performance_metrics.get("win_rate", 0),
        "sharpe_ratio": engine.performance_metrics.get("sharpe_ratio", 0),
        "max_drawdown": engine.performance_metrics.get("max_drawdown", 0),
        "positions": engine.positions,
        "uptime": (datetime.now() - bot["created_at"]).total_seconds()
    }

# ==================== API KEY MANAGEMENT ====================

@app.post("/api/v1/api-keys/create", response_model=APIKey)
async def create_api_key(key_data: APIKeyCreate):
    """Create API key for third-party market makers"""
    api_key = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
    api_secret = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
    
    key_info = {
        "api_key": api_key,
        "api_secret": api_secret,
        "name": key_data.name,
        "permissions": key_data.permissions,
        "ip_whitelist": key_data.ip_whitelist,
        "rate_limit": key_data.rate_limit,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(days=365),
        "is_active": True,
        "usage_count": 0,
        "last_used": None
    }
    
    api_keys_db[api_key] = key_info
    
    return APIKey(**key_info)

@app.get("/api/v1/api-keys")
async def list_api_keys():
    """List all API keys"""
    keys = []
    for key, data in api_keys_db.items():
        keys.append({
            "api_key": key,
            "name": data["name"],
            "permissions": data["permissions"],
            "created_at": data["created_at"],
            "is_active": data["is_active"],
            "usage_count": data["usage_count"],
            "last_used": data["last_used"]
        })
    
    return {"api_keys": keys, "total": len(keys)}

@app.delete("/api/v1/api-keys/{api_key}")
async def revoke_api_key(api_key: str):
    """Revoke an API key"""
    if api_key not in api_keys_db:
        raise HTTPException(status_code=404, detail="API key not found")
    
    api_keys_db[api_key]["is_active"] = False
    
    return {"success": True, "message": "API key revoked"}

# ==================== THIRD-PARTY MARKET MAKER ENDPOINTS ====================

@app.post("/api/v1/external/place-order")
async def external_place_order(
    pair: str,
    side: OrderSide,
    order_type: OrderType,
    price: float,
    quantity: float,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Place order via third-party API"""
    api_key = credentials.credentials
    
    if api_key not in api_keys_db or not api_keys_db[api_key]["is_active"]:
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")
    
    # Check permissions
    if "trading" not in api_keys_db[api_key]["permissions"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Update usage
    api_keys_db[api_key]["usage_count"] += 1
    api_keys_db[api_key]["last_used"] = datetime.now()
    
    # Place order
    order_id = str(uuid.uuid4())
    order = {
        "order_id": order_id,
        "pair": pair,
        "side": side.value,
        "order_type": order_type.value,
        "price": price,
        "quantity": quantity,
        "total": price * quantity,
        "fee": price * quantity * 0.001,
        "timestamp": datetime.now(),
        "api_key": api_key,
        "status": "filled"
    }
    
    trades_db.append(order)
    
    return {
        "success": True,
        "order_id": order_id,
        "order": order
    }

@app.get("/api/v1/external/orders")
async def external_get_orders(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get orders placed via API"""
    api_key = credentials.credentials
    
    if api_key not in api_keys_db or not api_keys_db[api_key]["is_active"]:
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")
    
    # Get orders for this API key
    orders = [t for t in trades_db if t.get("api_key") == api_key]
    
    return {
        "orders": orders,
        "total": len(orders)
    }

@app.get("/api/v1/external/account")
async def external_get_account(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get account information"""
    api_key = credentials.credentials
    
    if api_key not in api_keys_db or not api_keys_db[api_key]["is_active"]:
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")
    
    # Calculate account metrics
    orders = [t for t in trades_db if t.get("api_key") == api_key]
    total_volume = sum(t["total"] for t in orders)
    total_fees = sum(t["fee"] for t in orders)
    
    return {
        "api_key": api_key,
        "total_orders": len(orders),
        "total_volume": total_volume,
        "total_fees": total_fees,
        "rate_limit": api_keys_db[api_key]["rate_limit"],
        "usage_count": api_keys_db[api_key]["usage_count"]
    }

# ==================== ADMIN ENDPOINTS ====================

@app.get("/api/v1/admin/overview")
async def admin_overview():
    """Get system overview"""
    total_bots = len(bots_db)
    active_bots = sum(1 for b in bots_db.values() if b["status"] == "active")
    total_trades = len(trades_db)
    total_volume = sum(t["total"] for t in trades_db)
    total_api_keys = len(api_keys_db)
    active_api_keys = sum(1 for k in api_keys_db.values() if k["is_active"])
    
    return {
        "bots": {
            "total": total_bots,
            "active": active_bots,
            "paused": sum(1 for b in bots_db.values() if b["status"] == "paused"),
            "stopped": sum(1 for b in bots_db.values() if b["status"] == "stopped")
        },
        "trading": {
            "total_trades": total_trades,
            "total_volume": total_volume,
            "total_fees": sum(t["fee"] for t in trades_db)
        },
        "api_keys": {
            "total": total_api_keys,
            "active": active_api_keys
        }
    }

@app.get("/api/v1/admin/bots/performance")
async def admin_bots_performance():
    """Get performance of all bots"""
    performance = []
    
    for bot_id, bot_data in bots_db.items():
        engine = bot_data["engine"]
        if engine:
            bot_trades = [t for t in trades_db if t["bot_id"] == bot_id]
            total_volume = sum(t["total"] for t in bot_trades)
            
            performance.append({
                "bot_id": bot_id,
                "name": bot_data["config"]["name"],
                "strategy": bot_data["config"]["strategy"],
                "total_trades": len(bot_trades),
                "total_volume": total_volume,
                "performance_metrics": engine.performance_metrics
            })
    
    return {"bots": performance}

@app.post("/api/v1/admin/bots/stop-all")
async def admin_stop_all_bots():
    """Stop all bots"""
    for bot_id in bots_db.keys():
        await stop_bot(bot_id)
    
    return {"success": True, "message": "All bots stopped"}

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)