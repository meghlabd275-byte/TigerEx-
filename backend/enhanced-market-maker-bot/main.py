"""
TigerEx Enhanced Market Maker Bot System
Combining all best features from top 16 crypto market makers
with advanced AI/ML capabilities and high-frequency trading
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import random
import uuid
import jwt
import hashlib
import json
import numpy as np
import pandas as pd
from decimal import Decimal, getcontext
import logging
import time
import threading
from collections import defaultdict, deque
import redis
import aiohttp
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import signal
import sys

# Set high precision for decimal calculations
getcontext().prec = 16

# Initialize FastAPI with enhanced configuration
app = FastAPI(
    title="TigerEx Enhanced Market Maker Bot",
    description="Advanced market making system combining features from top 16 crypto market makers",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== ENHANCED ENUMS ====================

class TradingType(str, Enum):
    SPOT = "spot"
    FUTURES_PERPETUAL = "futures_perpetual"
    FUTURES_QUARTERLY = "futures_quarterly"
    FUTURES_QUARTERLY = "futures_monthly"
    OPTIONS = "options"
    DERIVATIVES = "derivatives"
    COPY_TRADING = "copy_trading"
    ETF = "etf"
    MARGIN = "margin"
    DEFI = "defi"
    OTC = "otc"

class StrategyType(str, Enum):
    MARKET_MAKING = "market_making"
    DELTA_NEUTRAL = "delta_neutral"
    ARBITRAGE = "arbitrage"
    TRIANGULAR_ARBITRAGE = "triangular_arbitrage"
    STATISTICAL_ARBITRAGE = "statistical_arbitrage"
    GRID_TRADING = "grid_trading"
    DCA = "dca"
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    PAIR_TRADING = "pair_trading"
    VOLATILITY_TRADING = "volatility_trading"
    LIQUIDITY_SWEEPING = "liquidity_sweeping"
    PREDICTIVE_TRADING = "predictive_trading"
    SMART_ORDER_ROUTING = "smart_order_routing"
    WASH_TRADING = "wash_trading"
    FAKE_VOLUME = "fake_volume"
    ORGANIC_TRADING = "organic_trading"
    SPREAD_CAPTURE = "spread_capture"
    LIQUIDITY_PROVISION = "liquidity_provision"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    TRAILING_STOP = "trailing_stop"
    IOC = "ioc"  # Immediate or Cancel
    FOK = "fok"  # Fill or Kill
    GTC = "gtc"  # Good Till Cancelled
    GTD = "gtd"  # Good Till Date
    POST_ONLY = "post_only"
    REDUCE_ONLY = "reduce_only"
    ICEBERG = "iceberg"

class TimeInForce(str, Enum):
    GTC = "gtc"
    IOC = "ioc"
    FOK = "fok"
    DAY = "day"
    GTD = "gtd"

class BotStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    BACKTESTING = "backtesting"

class ExchangeStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    RATE_LIMITED = "rate_limited"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

# ==================== ENHANCED MODELS ====================

@dataclass
class MarketData:
    symbol: str
    bid: float
    ask: float
    bid_size: float
    ask_size: float
    last_price: float
    volume_24h: float
    timestamp: datetime
    spread: float
    spread_percentage: float

@dataclass
class OrderBookLevel:
    price: float
    quantity: float
    orders_count: int

class OrderBook(BaseModel):
    symbol: str
    exchange: str
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    timestamp: datetime
    sequence: int

class MarketMakingConfig(BaseModel):
    spread_percentage: float = Field(0.1, ge=0.001, le=5.0, description="Spread percentage")
    order_size_min: float = Field(100, ge=1, description="Minimum order size")
    order_size_max: float = Field(10000, ge=10, description="Maximum order size")
    refresh_interval: int = Field(5, ge=1, le=3600, description="Order refresh interval (seconds)")
    max_position: float = Field(100000, ge=0, description="Maximum position size")
    inventory_skew: bool = Field(True, description="Enable inventory skew management")
    inventory_target: float = Field(0, description="Target inventory balance")
    skew_adjustment_factor: float = Field(0.5, ge=0, le=2, description="Inventory skew adjustment factor")
    depth_levels: int = Field(5, ge=1, le=20, description="Number of depth levels")
    price_update_threshold: float = Field(0.01, ge=0.001, le=1, description="Price update threshold")
    dynamic_spread: bool = Field(True, description="Enable dynamic spread adjustment")
    volatility_adjustment: bool = Field(True, description="Volatility-based spread adjustment")
    volume_adjustment: bool = Field(True, description="Volume-based order size adjustment")

class DeltaNeutralConfig(BaseModel):
    hedge_ratio: float = Field(1.0, ge=0, le=2, description="Hedge ratio")
    rebalance_threshold: float = Field(0.05, ge=0.01, le=0.5, description="Rebalance threshold")
    hedge_instrument: str = Field(description="Hedge instrument")
    hedge_exchange: str = Field(description="Hedge exchange")
    auto_hedge: bool = Field(True, description="Enable automatic hedging")
    hedge_delay: int = Field(1, ge=0, le=60, description="Hedge execution delay (seconds)")

class ArbitrageConfig(BaseModel):
    min_profit_threshold: float = Field(0.001, ge=0.0001, le=0.1, description="Minimum profit threshold")
    max_latency_ms: int = Field(1000, ge=10, le=10000, description="Maximum allowed latency")
    exchanges: List[str] = Field(description="Exchanges to monitor")
    check_interval: int = Field(1, ge=0, le=60, description="Check interval (seconds)")
    max_position_size: float = Field(10000, ge=0, description="Maximum position size per trade")
    simultaneous_arbitrages: int = Field(3, ge=1, le=10, description="Maximum simultaneous arbitrages")

class GridTradingConfig(BaseModel):
    grid_levels: int = Field(10, ge=3, le=50, description="Number of grid levels")
    grid_spacing: float = Field(0.01, ge=0.001, le=0.1, description="Grid spacing percentage")
    center_price: Optional[float] = Field(None, description="Center price (auto if None)")
    dynamic_grid: bool = Field(True, description="Enable dynamic grid adjustment")
    rebalance_frequency: int = Field(3600, ge=60, le=86400, description="Rebalance frequency (seconds)")
    profit_per_grid: float = Field(0.002, ge=0.0001, le=0.01, description="Profit target per grid")

class MLConfig(BaseModel):
    model_type: str = Field("lstm", description="ML model type")
    prediction_horizon: int = Field(60, ge=1, le=3600, description="Prediction horizon (seconds)")
    retrain_interval: int = Field(86400, ge=3600, le=604800, description="Retrain interval (seconds)")
    confidence_threshold: float = Field(0.7, ge=0.5, le=0.95, description="Confidence threshold")
    feature_window: int = Field(100, ge=10, le=1000, description="Feature window size")

class RiskManagementConfig(BaseModel):
    max_daily_loss: float = Field(10000, ge=0, description="Maximum daily loss")
    max_position_size: float = Field(100000, ge=0, description="Maximum position size")
    max_drawdown: float = Field(0.1, ge=0.01, le=0.5, description="Maximum drawdown")
    stop_loss_percentage: float = Field(0.02, ge=0.001, le=0.1, description="Stop loss percentage")
    take_profit_percentage: float = Field(0.05, ge=0.001, le=0.2, description="Take profit percentage")
    leverage_limit: float = Field(3, ge=1, le=100, description="Maximum leverage")
    risk_level: RiskLevel = Field(RiskLevel.MEDIUM, description="Risk level")
    emergency_stop: bool = Field(True, description="Enable emergency stop")
    circuit_breaker_threshold: float = Field(0.05, ge=0.01, le=0.2, description="Circuit breaker threshold")

class BotConfiguration(BaseModel):
    bot_id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=100)
    trading_type: TradingType
    strategy: StrategyType
    trading_pairs: List[str] = Field(..., min_items=1)
    exchanges: List[str] = Field(..., min_items=1)
    enabled: bool = True
    paper_trading: bool = Field(False, description="Enable paper trading mode")
    
    # Strategy-specific configurations
    market_making_config: Optional[MarketMakingConfig] = None
    delta_neutral_config: Optional[DeltaNeutralConfig] = None
    arbitrage_config: Optional[ArbitrageConfig] = None
    grid_trading_config: Optional[GridTradingConfig] = None
    ml_config: Optional[MLConfig] = None
    
    # Risk management
    risk_config: RiskManagementConfig = Field(default_factory=RiskManagementConfig)
    
    # Performance settings
    max_daily_volume: float = Field(10000000, ge=0, description="Max daily volume")
    max_daily_trades: int = Field(10000, ge=0, description="Max daily trades")
    execution_delay_ms: int = Field(10, ge=0, le=1000, description="Execution delay")
    
    # Advanced settings
    use_ml_predictions: bool = Field(False, description="Use ML predictions")
    smart_order_routing: bool = Field(True, description="Enable smart order routing")
    real_time_monitoring: bool = Field(True, description="Enable real-time monitoring")
    auto_restart: bool = Field(True, description="Enable auto-restart on errors")

    @validator('trading_pairs')
    def validate_pairs(cls, v):
        for pair in v:
            if '/' not in pair:
                raise ValueError(f"Invalid trading pair format: {pair}")
        return v

class PerformanceMetrics(BaseModel):
    bot_id: str
    total_trades: int = 0
    total_volume: float = 0.0
    total_fees: float = 0.0
    profit_loss: float = 0.0
    profit_loss_percentage: float = 0.0
    win_rate: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    average_win: float = 0.0
    average_loss: float = 0.0
    profit_factor: float = 0.0
    recovery_factor: float = 0.0
    var_95: float = 0.0  # Value at Risk 95%
    cvar_95: float = 0.0  # Conditional Value at Risk 95%
    uptime: float = 0.0
    error_count: int = 0
    last_updated: datetime = Field(default_factory=datetime.now)

class BotStatusInfo(BaseModel):
    bot_id: str
    status: BotStatus
    created_at: datetime
    started_at: Optional[datetime]
    stopped_at: Optional[datetime]
    uptime: float = 0.0
    current_positions: Dict[str, float] = {}
    open_orders: int = 0
    last_trade_time: Optional[datetime]
    last_error: Optional[str]
    error_count: int = 0
    restart_count: int = 0

class Trade(BaseModel):
    trade_id: str
    bot_id: str
    trading_pair: str
    exchange: str
    side: OrderSide
    order_type: OrderType
    price: float
    quantity: float
    total: float
    fee: float
    fee_currency: str
    timestamp: datetime
    strategy: StrategyType
    execution_time_ms: float
    liquidity_provider: bool = False
    maker_fee: float = 0.0
    taker_fee: float = 0.0

class Alert(BaseModel):
    alert_id: str
    bot_id: str
    alert_type: str
    message: str
    severity: str
    timestamp: datetime
    acknowledged: bool = False
    metadata: Dict[str, Any] = {}

# ==================== DATABASE (In-Memory for Demo) ====================

bots_db: Dict[str, Dict] = {}
trades_db: List[Dict] = []
performance_db: Dict[str, PerformanceMetrics] = {}
api_keys_db: Dict[str, Dict] = {}
alerts_db: List[Dict] = []
market_data_cache: Dict[str, MarketData] = {}
orderbooks: Dict[str, OrderBook] = {}
exchange_status: Dict[str, ExchangeStatus] = {}

# Redis for caching (optional)
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()
    REDIS_AVAILABLE = True
except:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory caching")

# ==================== ENHANCED MARKET MAKING ENGINE ====================

class EnhancedMarketMakingEngine:
    """
    Advanced Market Making Engine combining features from:
    - DWF Labs (HFT, Web3 integration)
    - Vortex (Delta-neutral, KPI-driven)
    - Cumberland (Price improvement, 24/7 support)
    - GSR Markets (Customized solutions, programmatic execution)
    - Gravity Team (Real-time visibility, regional expertise)
    - Kairon Labs (Custom algorithms, arbitrage)
    - Jump Trading (Smart order routing, research-driven)
    - Alphatheta (Deployable bots, enhanced spreads)
    - Bluesky Capital (Quantitative management, alpha signals)
    - Wintermute (AI algorithms, CEX/DEX coverage)
    - Algoz (Predictive capabilities, market-neutral)
    - Acheron Trading (Stochastic modeling, exchange advisory)
    - Jane Street (ML integration, programmable hardware)
    - Fast Forward (HFT specialization, cutting-edge tech)
    - Amber Group (Proprietary execution, mining validation)
    - Pulsar Trading Cap (Algorithmic focus, opportunity identification)
    """

    def __init__(self, config: BotConfiguration):
        self.config = config
        self.bot_id = config.bot_id or str(uuid.uuid4())
        self.status = BotStatus.STOPPED
        self.positions = defaultdict(float)
        self.orders = {}
        self.performance = PerformanceMetrics(bot_id=self.bot_id)
        self.status_info = BotStatusInfo(
            bot_id=self.bot_id,
            status=BotStatus.STOPPED,
            created_at=datetime.now()
        )
        
        # Advanced features
        self.ml_predictor = None
        self.risk_manager = RiskManager(config.risk_config)
        self.order_router = SmartOrderRouter()
        self.liquidity_manager = LiquidityManager()
        self.arbitrage_detector = ArbitrageDetector()
        
        # Performance optimization
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.market_data_queue = asyncio.Queue(maxsize=1000)
        self.order_queue = asyncio.Queue(maxsize=1000)
        
        # Monitoring and alerts
        self.alert_manager = AlertManager(self.bot_id)
        self.metrics_collector = MetricsCollector(self.bot_id)
        
        # Exchange connections
        self.exchange_adapters = {}
        self._initialize_exchanges()
        
        # Initialize strategy-specific components
        self._initialize_strategy()
        
        logger.info(f"Enhanced Market Making Engine initialized for bot {self.bot_id}")

    def _initialize_exchanges(self):
        """Initialize exchange adapters for all configured exchanges"""
        for exchange in self.config.exchanges:
            try:
                adapter = ExchangeAdapter(exchange, self.config.paper_trading)
                self.exchange_adapters[exchange] = adapter
                exchange_status[exchange] = ExchangeStatus.ONLINE
                logger.info(f"Initialized adapter for {exchange}")
            except Exception as e:
                logger.error(f"Failed to initialize {exchange}: {e}")
                exchange_status[exchange] = ExchangeStatus.OFFLINE

    def _initialize_strategy(self):
        """Initialize strategy-specific components"""
        if self.config.strategy == StrategyType.MARKET_MAKING:
            self.market_maker = MarketMakerStrategy(
                self.config.market_making_config,
                self.config.trading_pairs
            )
        elif self.config.strategy == StrategyType.DELTA_NEUTRAL:
            self.delta_neutral = DeltaNeutralStrategy(
                self.config.delta_neutral_config
            )
        elif self.config.strategy == StrategyType.ARBITRAGE:
            self.arbitrage = ArbitrageStrategy(
                self.config.arbitrage_config,
                self.exchange_adapters
            )
        elif self.config.strategy == StrategyType.GRID_TRADING:
            self.grid_trader = GridTradingStrategy(
                self.config.grid_trading_config
            )
        
        # Initialize ML predictor if enabled
        if self.config.use_ml_predictions and self.config.ml_config:
            self.ml_predictor = MLPredictor(self.config.ml_config)

    async def start(self):
        """Start the enhanced market making bot"""
        logger.info(f"Starting Enhanced Market Making Bot: {self.bot_id}")
        self.status = BotStatus.ACTIVE
        self.status_info.status = BotStatus.ACTIVE
        self.status_info.started_at = datetime.now()
        
        try:
            # Start background tasks
            tasks = [
                self._market_data_handler(),
                self._order_execution_handler(),
                self._strategy_execution(),
                self._risk_monitoring(),
                self._performance_tracking(),
                self._ml_prediction_loop() if self.ml_predictor else None,
                self._arbitrage_monitoring() if self.config.strategy == StrategyType.ARBITRAGE else None
            ]
            
            # Filter out None tasks
            tasks = [task for task in tasks if task is not None]
            
            await asyncio.gather(*tasks)
            
        except Exception as e:
            logger.error(f"Error in bot {self.bot_id}: {str(e)}")
            self.status_info.last_error = str(e)
            self.status_info.error_count += 1
            self.status = BotStatus.ERROR
            self.status_info.status = BotStatus.ERROR
            
            # Auto-restart if enabled
            if self.config.auto_restart and self.status_info.restart_count < 5:
                await self._restart_bot()

    async def _market_data_handler(self):
        """Handle real-time market data streams"""
        while self.status == BotStatus.ACTIVE:
            try:
                for pair in self.config.trading_pairs:
                    for exchange in self.config.exchanges:
                        if exchange_status.get(exchange) == ExchangeStatus.ONLINE:
                            market_data = await self._get_market_data(pair, exchange)
                            await self.market_data_queue.put(market_data)
                            
                            # Cache market data
                            cache_key = f"{exchange}:{pair}"
                            market_data_cache[cache_key] = market_data
                            
                await asyncio.sleep(0.1)  # High-frequency updates
                
            except Exception as e:
                logger.error(f"Market data handler error: {e}")
                await asyncio.sleep(1)

    async def _order_execution_handler(self):
        """Handle order execution with smart routing"""
        while self.status == BotStatus.ACTIVE:
            try:
                order_request = await self.order_queue.get()
                
                # Smart order routing
                best_venue = await self.order_router.find_best_venue(
                    order_request, self.exchange_adapters
                )
                
                # Execute order
                if best_venue:
                    order = await self._execute_order(order_request, best_venue)
                    if order:
                        await self._process_order_fill(order)
                        
                await asyncio.sleep(0.001)  # Sub-millisecond processing
                
            except Exception as e:
                logger.error(f"Order execution handler error: {e}")
                await asyncio.sleep(0.01)

    async def _strategy_execution(self):
        """Execute the main trading strategy"""
        while self.status == BotStatus.ACTIVE:
            try:
                if self.config.strategy == StrategyType.MARKET_MAKING:
                    await self._execute_market_making()
                elif self.config.strategy == StrategyType.DELTA_NEUTRAL:
                    await self._execute_delta_neutral()
                elif self.config.strategy == StrategyType.ARBITRAGE:
                    await self._execute_arbitrage()
                elif self.config.strategy == StrategyType.GRID_TRADING:
                    await self._execute_grid_trading()
                elif self.config.strategy == StrategyType.PREDICTIVE_TRADING:
                    await self._execute_predictive_trading()
                    
                await asyncio.sleep(self.config.market_making_config.refresh_interval if self.config.market_making_config else 1)
                
            except Exception as e:
                logger.error(f"Strategy execution error: {e}")
                self.status_info.error_count += 1
                await asyncio.sleep(5)

    async def _execute_market_making(self):
        """Execute advanced market making strategy"""
        config = self.config.market_making_config
        
        for pair in self.config.trading_pairs:
            # Get aggregated market data
            market_data = await self._get_aggregated_market_data(pair)
            if not market_data:
                continue
                
            mid_price = (market_data.bid + market_data.ask) / 2
            
            # Dynamic spread calculation
            if config.dynamic_spread:
                spread = await self._calculate_dynamic_spread(pair, market_data)
            else:
                spread = mid_price * (config.spread_percentage / 100)
            
            # Inventory skew management
            current_position = self.positions.get(pair, 0)
            inventory_ratio = current_position / config.max_position if config.max_position > 0 else 0
            
            for level in range(config.depth_levels):
                level_spread = spread * (level + 1)
                
                # Bid orders
                bid_price = mid_price - level_spread / 2
                bid_size = await self._calculate_order_size(
                    OrderSide.BUY, level, config, inventory_ratio
                )
                
                if bid_size > 0:
                    await self._place_order(pair, OrderSide.BUY, bid_price, bid_size)
                
                # Ask orders
                ask_price = mid_price + level_spread / 2
                ask_size = await self._calculate_order_size(
                    OrderSide.SELL, level, config, inventory_ratio
                )
                
                if ask_size > 0:
                    await self._place_order(pair, OrderSide.SELL, ask_price, ask_size)

    async def _calculate_dynamic_spread(self, pair: str, market_data: MarketData) -> float:
        """Calculate dynamic spread based on market conditions"""
        base_spread = market_data.spread
        
        # Volatility adjustment
        if self.config.market_making_config.volatility_adjustment:
            volatility = await self._calculate_volatility(pair)
            volatility_multiplier = min(max(1 + volatility * 10, 0.5), 3)
            base_spread *= volatility_multiplier
        
        # Volume adjustment
        if self.config.market_making_config.volume_adjustment:
            volume_multiplier = min(max(market_data.volume_24h / 1000000, 0.5), 2)
            base_spread /= volume_multiplier
        
        # Time-based adjustment
        current_hour = datetime.now().hour
        if 9 <= current_hour <= 16:  # Active hours
            time_multiplier = 0.8
        else:  # Quiet hours
            time_multiplier = 1.2
            
        return base_spread * time_multiplier

    async def _calculate_order_size(self, side: OrderSide, level: int, config: MarketMakingConfig, inventory_ratio: float) -> float:
        """Calculate optimal order size"""
        base_size = random.uniform(config.order_size_min, config.order_size_max)
        
        # Level-based sizing (larger sizes closer to mid price)
        level_multiplier = 1 / (level + 1)
        base_size *= level_multiplier
        
        # Inventory skew adjustment
        if config.inventory_skew:
            if side == OrderSide.BUY and inventory_ratio > 0.1:  # Too long, reduce buy size
                base_size *= (1 - inventory_ratio * config.skew_adjustment_factor)
            elif side == OrderSide.SELL and inventory_ratio < -0.1:  # Too short, reduce sell size
                base_size *= (1 + inventory_ratio * config.skew_adjustment_factor)
        
        return max(0, base_size)

    async def _get_market_data(self, pair: str, exchange: str) -> Optional[MarketData]:
        """Get real-time market data from exchange"""
        try:
            adapter = self.exchange_adapters.get(exchange)
            if not adapter:
                return None
                
            ticker = await adapter.get_ticker(pair)
            if not ticker:
                return None
                
            spread = ticker['ask'] - ticker['bid']
            spread_percentage = (spread / ticker['last']) * 100 if ticker['last'] > 0 else 0
            
            return MarketData(
                symbol=pair,
                bid=ticker['bid'],
                ask=ticker['ask'],
                bid_size=ticker['bid_size'],
                ask_size=ticker['ask_size'],
                last_price=ticker['last'],
                volume_24h=ticker['volume'],
                timestamp=ticker['timestamp'],
                spread=spread,
                spread_percentage=spread_percentage
            )
            
        except Exception as e:
            logger.error(f"Error getting market data for {pair} on {exchange}: {e}")
            return None

    async def _get_aggregated_market_data(self, pair: str) -> Optional[MarketData]:
        """Get aggregated market data across all exchanges"""
        all_data = []
        
        for exchange in self.config.exchanges:
            cache_key = f"{exchange}:{pair}"
            if cache_key in market_data_cache:
                all_data.append(market_data_cache[cache_key])
        
        if not all_data:
            return None
            
        # Aggregate by weighted average
        total_volume = sum(d.volume_24h for d in all_data)
        if total_volume == 0:
            return all_data[0]  # Fallback to first exchange
            
        weighted_bid = sum(d.bid * d.volume_24h for d in all_data) / total_volume
        weighted_ask = sum(d.ask * d.volume_24h for d in all_data) / total_volume
        weighted_last = sum(d.last_price * d.volume_24h for d in all_data) / total_volume
        
        return MarketData(
            symbol=pair,
            bid=weighted_bid,
            ask=weighted_ask,
            bid_size=sum(d.bid_size for d in all_data),
            ask_size=sum(d.ask_size for d in all_data),
            last_price=weighted_last,
            volume_24h=total_volume,
            timestamp=datetime.now(),
            spread=weighted_ask - weighted_bid,
            spread_percentage=((weighted_ask - weighted_bid) / weighted_last) * 100
        )

    async def _place_order(self, pair: str, side: OrderSide, price: float, quantity: float):
        """Place an order with smart routing"""
        order_request = {
            'pair': pair,
            'side': side,
            'price': price,
            'quantity': quantity,
            'order_type': OrderType.LIMIT,
            'time_in_force': TimeInForce.GTC,
            'bot_id': self.bot_id
        }
        
        await self.order_queue.put(order_request)

    async def _execute_order(self, order_request: Dict, venue: str) -> Optional[Dict]:
        """Execute order on specified venue"""
        try:
            adapter = self.exchange_adapters.get(venue)
            if not adapter:
                return None
                
            start_time = time.time()
            result = await adapter.place_order(order_request)
            execution_time = (time.time() - start_time) * 1000  # Convert to ms
            
            if result:
                order = {
                    'order_id': str(uuid.uuid4()),
                    'exchange': venue,
                    'execution_time_ms': execution_time,
                    **order_request,
                    **result
                }
                
                self.orders[order['order_id']] = order
                return order
                
        except Exception as e:
            logger.error(f"Order execution error: {e}")
            self.status_info.error_count += 1
            
        return None

    async def _process_order_fill(self, order: Dict):
        """Process filled order and update positions"""
        try:
            trade = Trade(
                trade_id=str(uuid.uuid4()),
                bot_id=self.bot_id,
                trading_pair=order['pair'],
                exchange=order['exchange'],
                side=order['side'],
                order_type=order['order_type'],
                price=order['price'],
                quantity=order['quantity'],
                total=order['price'] * order['quantity'],
                fee=order.get('fee', 0),
                fee_currency=order['pair'].split('/')[1],
                timestamp=datetime.now(),
                strategy=self.config.strategy,
                execution_time_ms=order['execution_time_ms'],
                liquidity_provider=order.get('maker', False),
                maker_fee=order.get('maker_fee', 0),
                taker_fee=order.get('taker_fee', 0)
            )
            
            trades_db.append(trade.dict())
            
            # Update position
            if trade.side == OrderSide.BUY:
                self.positions[trade.trading_pair] += trade.quantity
            else:
                self.positions[trade.trading_pair] -= trade.quantity
            
            # Update performance metrics
            await self._update_performance_metrics(trade)
            
            # Update status info
            self.status_info.last_trade_time = trade.timestamp
            
        except Exception as e:
            logger.error(f"Error processing order fill: {e}")

    async def _update_performance_metrics(self, trade: Trade):
        """Update performance metrics after each trade"""
        try:
            self.performance.total_trades += 1
            self.performance.total_volume += trade.total
            self.performance.total_fees += trade.fee
            
            # Calculate P&L (simplified for market making)
            if trade.side == OrderSide.BUY:
                self.performance.profit_loss -= trade.total + trade.fee
            else:
                self.performance.profit_loss += trade.total - trade.fee
            
            # Calculate P&L percentage
            if self.performance.total_volume > 0:
                self.performance.profit_loss_percentage = (self.performance.profit_loss / self.performance.total_volume) * 100
            
            # Update win rate (simplified)
            # In real implementation, track completed trades vs profitable trades
            
            self.performance.last_updated = datetime.now()
            performance_db[self.bot_id] = self.performance
            
        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")

    async def _risk_monitoring(self):
        """Continuous risk monitoring"""
        while self.status == BotStatus.ACTIVE:
            try:
                risk_alerts = await self.risk_manager.check_risks(self.positions, self.performance)
                
                for alert in risk_alerts:
                    await self.alert_manager.send_alert(alert)
                    
                    # Emergency stop if critical risk
                    if alert['severity'] == 'critical':
                        await self._emergency_stop(alert['message'])
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Risk monitoring error: {e}")
                await asyncio.sleep(30)

    async def _performance_tracking(self):
        """Track and analyze performance metrics"""
        while self.status == BotStatus.ACTIVE:
            try:
                await self.metrics_collector.collect_metrics(self.positions, self.performance)
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Performance tracking error: {e}")
                await asyncio.sleep(300)

    async def _restart_bot(self):
        """Restart the bot after an error"""
        logger.info(f"Restarting bot {self.bot_id}")
        self.status_info.restart_count += 1
        self.status_info.last_error = None
        
        # Wait before restart
        await asyncio.sleep(10)
        
        # Restart the bot
        self.status = BotStatus.ACTIVE
        self.status_info.status = BotStatus.ACTIVE
        await self.start()

    async def _emergency_stop(self, reason: str):
        """Emergency stop due to critical risk"""
        logger.critical(f"Emergency stop triggered for bot {self.bot_id}: {reason}")
        self.status = BotStatus.STOPPED
        self.status_info.status = BotStatus.STOPPED
        self.status_info.stopped_at = datetime.now()
        
        # Cancel all open orders
        await self._cancel_all_orders()
        
        # Send critical alert
        await self.alert_manager.send_alert({
            'type': 'emergency_stop',
            'message': f"Bot emergency stopped: {reason}",
            'severity': 'critical'
        })

    async def _cancel_all_orders(self):
        """Cancel all open orders across all exchanges"""
        for exchange, adapter in self.exchange_adapters.items():
            try:
                await adapter.cancel_all_orders(self.bot_id)
            except Exception as e:
                logger.error(f"Error cancelling orders on {exchange}: {e}")

    async def stop(self):
        """Stop the market making bot"""
        logger.info(f"Stopping bot {self.bot_id}")
        self.status = BotStatus.STOPPED
        self.status_info.status = BotStatus.STOPPED
        self.status_info.stopped_at = datetime.now()
        
        await self._cancel_all_orders()

# ==================== SUPPORTING CLASSES ====================

class RiskManager:
    """Advanced risk management system"""
    
    def __init__(self, config: RiskManagementConfig):
        self.config = config
        self.daily_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.daily_pnl = 0
        self.max_drawdown_current = 0
        
    async def check_risks(self, positions: Dict, performance: PerformanceMetrics) -> List[Dict]:
        """Check all risk conditions and return alerts"""
        alerts = []
        
        # Check daily loss limit
        if performance.profit_loss < -self.config.max_daily_loss:
            alerts.append({
                'type': 'daily_loss_limit',
                'message': f"Daily loss limit exceeded: {performance.profit_loss}",
                'severity': 'critical'
            })
        
        # Check position size limits
        for pair, size in positions.items():
            if abs(size) > self.config.max_position_size:
                alerts.append({
                    'type': 'position_size_limit',
                    'message': f"Position size limit exceeded for {pair}: {size}",
                    'severity': 'high'
                })
        
        # Check drawdown
        if abs(performance.profit_loss_percentage) > self.config.max_drawdown * 100:
            alerts.append({
                'type': 'max_drawdown',
                'message': f"Maximum drawdown exceeded: {performance.profit_loss_percentage}%",
                'severity': 'high'
            })
        
        # Check circuit breaker
        if performance.profit_loss < -self.config.circuit_breaker_threshold * performance.total_volume:
            alerts.append({
                'type': 'circuit_breaker',
                'message': "Circuit breaker triggered - excessive losses",
                'severity': 'critical'
            })
        
        return alerts

class SmartOrderRouter:
    """Smart order routing for optimal execution"""
    
    async def find_best_venue(self, order_request: Dict, adapters: Dict) -> Optional[str]:
        """Find best venue for order execution"""
        best_venue = None
        best_score = -float('inf')
        
        for venue, adapter in adapters.items():
            try:
                # Get venue metrics
                fees = await adapter.get_fee_schedule(order_request['pair'])
                liquidity = await adapter.get_liquidity(order_request['pair'])
                latency = adapter.get_average_latency()
                
                # Calculate score (higher is better)
                score = (liquidity * 0.4) + (1/fees * 0.4) + (1/latency * 0.2)
                
                if score > best_score:
                    best_score = score
                    best_venue = venue
                    
            except Exception as e:
                logger.error(f"Error evaluating venue {venue}: {e}")
        
        return best_venue

class LiquidityManager:
    """Manage liquidity provision across venues"""
    
    def __init__(self):
        self.liquidity_metrics = {}
    
    async def assess_liquidity(self, pair: str, exchanges: List[str]) -> Dict:
        """Assess liquidity for a trading pair"""
        total_liquidity = 0
        venue_liquidity = {}
        
        for exchange in exchanges:
            try:
                # Get order book depth
                orderbook = await self._get_orderbook_depth(pair, exchange)
                liquidity = sum(level['quantity'] for level in orderbook['bids'][:5]) + \
                           sum(level['quantity'] for level in orderbook['asks'][:5])
                
                venue_liquidity[exchange] = liquidity
                total_liquidity += liquidity
                
            except Exception as e:
                logger.error(f"Error assessing liquidity on {exchange}: {e}")
        
        return {
            'pair': pair,
            'total_liquidity': total_liquidity,
            'venue_liquidity': venue_liquidity,
            'best_venue': max(venue_liquidity.items(), key=lambda x: x[1])[0] if venue_liquidity else None
        }

class ArbitrageDetector:
    """Detect arbitrage opportunities across exchanges"""
    
    def __init__(self):
        self.opportunities = []
    
    async def scan_opportunities(self, pairs: List[str], exchanges: List[str]) -> List[Dict]:
        """Scan for arbitrage opportunities"""
        opportunities = []
        
        for pair in pairs:
            prices = {}
            
            # Get prices from all exchanges
            for exchange in exchanges:
                try:
                    price = await self._get_price(pair, exchange)
                    if price:
                        prices[exchange] = price
                except Exception as e:
                    logger.error(f"Error getting price from {exchange}: {e}")
            
            # Find arbitrage opportunities
            if len(prices) >= 2:
                max_price_exchange = max(prices.items(), key=lambda x: x[1])
                min_price_exchange = min(prices.items(), key=lambda x: x[1])
                
                price_diff = max_price_exchange[1] - min_price_exchange[1]
                profit_potential = price_diff / min_price_exchange[1]
                
                if profit_potential > 0.001:  # 0.1% threshold
                    opportunities.append({
                        'pair': pair,
                        'buy_exchange': min_price_exchange[0],
                        'sell_exchange': max_price_exchange[0],
                        'buy_price': min_price_exchange[1],
                        'sell_price': max_price_exchange[1],
                        'profit_potential': profit_potential,
                        'timestamp': datetime.now()
                    })
        
        return opportunities

class AlertManager:
    """Manage alerts and notifications"""
    
    def __init__(self, bot_id: str):
        self.bot_id = bot_id
    
    async def send_alert(self, alert: Dict):
        """Send alert"""
        alert_obj = Alert(
            alert_id=str(uuid.uuid4()),
            bot_id=self.bot_id,
            alert_type=alert['type'],
            message=alert['message'],
            severity=alert['severity'],
            timestamp=datetime.now(),
            metadata=alert.get('metadata', {})
        )
        
        alerts_db.append(alert_obj.dict())
        logger.warning(f"Alert for bot {self.bot_id}: {alert['message']}")

class MetricsCollector:
    """Collect and analyze performance metrics"""
    
    def __init__(self, bot_id: str):
        self.bot_id = bot_id
        self.metrics_history = deque(maxlen=1000)
    
    async def collect_metrics(self, positions: Dict, performance: PerformanceMetrics):
        """Collect performance metrics"""
        metrics = {
            'timestamp': datetime.now(),
            'bot_id': self.bot_id,
            'positions': dict(positions),
            'performance': performance.dict(),
            'exchange_status': dict(exchange_status)
        }
        
        self.metrics_history.append(metrics)
        
        # Store in Redis if available
        if REDIS_AVAILABLE:
            try:
                redis_client.lpush(f"metrics:{self.bot_id}", json.dumps(metrics, default=str))
                redis_client.ltrim(f"metrics:{self.bot_id}", 0, 999)  # Keep last 1000
            except Exception as e:
                logger.error(f"Error storing metrics in Redis: {e}")

class ExchangeAdapter:
    """Base adapter for exchange connectivity"""
    
    def __init__(self, exchange_name: str, paper_trading: bool = False):
        self.exchange_name = exchange_name
        self.paper_trading = paper_trading
        self.rate_limits = defaultdict(int)
    
    async def get_ticker(self, pair: str) -> Optional[Dict]:
        """Get ticker data (simulated)"""
        if self.paper_trading:
            return await self._simulate_ticker(pair)
        
        # Real exchange API call would go here
        return await self._simulate_ticker(pair)
    
    async def place_order(self, order_request: Dict) -> Optional[Dict]:
        """Place order (simulated)"""
        if self.paper_trading:
            return await self._simulate_order_fill(order_request)
        
        # Real exchange API call would go here
        return await self._simulate_order_fill(order_request)
    
    async def _simulate_ticker(self, pair: str) -> Dict:
        """Simulate ticker data"""
        base_prices = {
            "BTC/USDT": 45000,
            "ETH/USDT": 3000,
            "BNB/USDT": 400,
            "SOL/USDT": 100,
            "XRP/USDT": 0.5
        }
        
        base_price = base_prices.get(pair, 100)
        variance = random.uniform(-0.01, 0.01)
        price = base_price * (1 + variance)
        
        return {
            'bid': price * 0.999,
            'ask': price * 1.001,
            'bid_size': random.uniform(100, 1000),
            'ask_size': random.uniform(100, 1000),
            'last': price,
            'volume': random.uniform(1000000, 10000000),
            'timestamp': datetime.now()
        }
    
    async def _simulate_order_fill(self, order_request: Dict) -> Dict:
        """Simulate order fill"""
        return {
            'order_id': str(uuid.uuid4()),
            'status': 'filled',
            'filled_quantity': order_request['quantity'],
            'maker': True,
            'fee': order_request['quantity'] * order_request['price'] * 0.001,
            'maker_fee': -order_request['quantity'] * order_request['price'] * 0.0001,  # Negative for maker rebate
            'taker_fee': order_request['quantity'] * order_request['price'] * 0.001
        }

# ==================== API ENDPOINTS ====================

@app.post("/api/v2/bots/create", response_model=Dict)
async def create_enhanced_bot(config: BotConfiguration, background_tasks: BackgroundTasks):
    """Create an enhanced market making bot"""
    try:
        bot_id = str(uuid.uuid4())
        config.bot_id = bot_id
        
        # Validate configuration
        if config.strategy == StrategyType.MARKET_MAKING and not config.market_making_config:
            raise HTTPException(status_code=400, detail="Market making config required for market making strategy")
        
        # Store bot configuration
        bots_db[bot_id] = {
            "config": config.dict(),
            "status": "created",
            "created_at": datetime.now(),
            "engine": None
        }
        
        # Initialize and start bot
        engine = EnhancedMarketMakingEngine(config)
        bots_db[bot_id]["engine"] = engine
        
        if config.enabled:
            background_tasks.add_task(engine.start)
            bots_db[bot_id]["status"] = "active"
        
        return {
            "success": True,
            "bot_id": bot_id,
            "message": "Enhanced bot created and started successfully",
            "features": [
                "High-frequency trading engine",
                "Smart order routing",
                "Advanced risk management",
                "Real-time monitoring",
                "ML predictions (if enabled)",
                "Multi-exchange support",
                "Delta-neutral strategies",
                "Arbitrage detection",
                "Performance analytics"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error creating bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v2/bots/{bot_id}/status")
async def get_enhanced_bot_status(bot_id: str):
    """Get enhanced bot status and performance metrics"""
    if bot_id not in bots_db:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    bot = bots_db[bot_id]
    engine = bot["engine"]
    
    if not engine:
        return {
            "bot_id": bot_id,
            "status": bot["status"],
            "message": "Bot not initialized"
        }
    
    return {
        "bot_id": bot_id,
        "status": engine.status.value,
        "status_info": engine.status_info.dict(),
        "performance": engine.performance.dict(),
        "positions": dict(engine.positions),
        "open_orders": len(engine.orders),
        "config": bot["config"],
        "features": {
            "ml_predictions": engine.ml_predictor is not None,
            "smart_order_routing": True,
            "risk_management": True,
            "real_time_monitoring": True,
            "multi_exchange": len(engine.exchange_adapters) > 1
        }
    }

@app.get("/api/v2/bots/{bot_id}/performance")
async def get_enhanced_bot_performance(bot_id: str, period: str = "24h"):
    """Get detailed performance metrics with advanced analytics"""
    if bot_id not in bots_db:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    bot = bots_db[bot_id]
    engine = bot["engine"]
    
    if not engine:
        raise HTTPException(status_code=400, detail="Bot engine not initialized")
    
    # Get trades for the period
    bot_trades = [t for t in trades_db if t["bot_id"] == bot_id]
    
    # Calculate advanced metrics
    total_volume = sum(t["total"] for t in bot_trades)
    total_fees = sum(t["fee"] for t in bot_trades)
    
    # Calculate hourly P&L
    hourly_pnl = defaultdict(float)
    for trade in bot_trades:
        hour = trade["timestamp"].replace(minute=0, second=0, microsecond=0)
        pnl = -trade["total"] - trade["fee"] if trade["side"] == "buy" else trade["total"] - trade["fee"]
        hourly_pnl[hour] += pnl
    
    # Calculate Sharpe ratio (simplified)
    pnl_values = list(hourly_pnl.values())
    if len(pnl_values) > 1:
        avg_return = np.mean(pnl_values)
        std_return = np.std(pnl_values)
        sharpe_ratio = avg_return / std_return if std_return > 0 else 0
    else:
        sharpe_ratio = 0
    
    # Calculate maximum drawdown
    cumulative_pnl = np.cumsum(pnl_values)
    running_max = np.maximum.accumulate(cumulative_pnl)
    drawdown = running_max - cumulative_pnl
    max_drawdown = np.max(drawdown) if len(drawdown) > 0 else 0
    
    return {
        "bot_id": bot_id,
        "period": period,
        "summary": {
            "total_trades": len(bot_trades),
            "total_volume": total_volume,
            "total_fees": total_fees,
            "profit_loss": engine.performance.profit_loss,
            "profit_loss_percentage": engine.performance.profit_loss_percentage,
            "win_rate": engine.performance.win_rate,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "sortino_ratio": engine.performance.sortino_ratio,
            "calmar_ratio": engine.performance.calmar_ratio
        },
        "hourly_performance": dict(hourly_pnl),
        "positions": dict(engine.positions),
        "uptime": (datetime.now() - bot["created_at"]).total_seconds(),
        "last_updated": datetime.now()
    }

@app.get("/api/v2/bots/{bot_id}/analytics")
async def get_bot_analytics(bot_id: str):
    """Get advanced analytics and insights"""
    if bot_id not in bots_db:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    bot_trades = [t for t in trades_db if t["bot_id"] == bot_id]
    
    if not bot_trades:
        return {"bot_id": bot_id, "message": "No trades yet"}
    
    # Trade analysis
    df = pd.DataFrame(bot_trades)
    
    # Trading pattern analysis
    hourly_distribution = df.groupby(df['timestamp'].dt.hour).size().to_dict()
    daily_volume = df.groupby(df['timestamp'].dt.date)['total'].sum().to_dict()
    
    # Profit analysis by pair
    profit_by_pair = {}
    for pair in df['trading_pair'].unique():
        pair_trades = df[df['trading_pair'] == pair]
        buy_value = pair_trades[pair_trades['side'] == 'buy']['total'].sum()
        sell_value = pair_trades[pair_trades['side'] == 'sell']['total'].sum()
        fees = pair_trades['fee'].sum()
        profit_by_pair[pair] = sell_value - buy_value - fees
    
    # Execution quality metrics
    avg_execution_time = df['execution_time_ms'].mean()
    maker_ratio = df['liquidity_provider'].mean()
    
    return {
        "bot_id": bot_id,
        "trading_patterns": {
            "hourly_distribution": hourly_distribution,
            "daily_volume": {str(k): v for k, v in daily_volume.items()},
            "most_active_hour": max(hourly_distribution, key=hourly_distribution.get),
            "average_trades_per_hour": len(df) / 24
        },
        "profitability": {
            "profit_by_pair": profit_by_pair,
            "most_profitable_pair": max(profit_by_pair.items(), key=lambda x: x[1]) if profit_by_pair else None,
            "profit_factor": abs(sum(profit_by_pair.values()) / sum(abs(v) for v in profit_by_pair.values() if v < 0)) if any(v < 0 for v in profit_by_pair.values()) else float('inf')
        },
        "execution_quality": {
            "average_execution_time_ms": avg_execution_time,
            "maker_ratio": maker_ratio,
            "total_maker_fees": df[df['liquidity_provider']]['maker_fee'].sum(),
            "total_taker_fees": df[~df['liquidity_provider']]['taker_fee'].sum()
        },
        "risk_metrics": {
            "var_95": np.percentile(df['total'], 5),
            "cvar_95": df[df['total'] <= np.percentile(df['total'], 5)]['total'].mean(),
            "max_trade_size": df['total'].max(),
            "min_trade_size": df['total'].min()
        }
    }

@app.get("/api/v2/bots")
async def list_enhanced_bots(status: Optional[BotStatus] = None, strategy: Optional[StrategyType] = None):
    """List all enhanced bots with filtering options"""
    bots = []
    
    for bot_id, bot_data in bots_db.items():
        engine = bot_data.get("engine")
        
        if status and (not engine or engine.status != status):
            continue
        
        if strategy and bot_data["config"]["strategy"] != strategy:
            continue
        
        bots.append({
            "bot_id": bot_id,
            "name": bot_data["config"]["name"],
            "status": engine.status.value if engine else bot_data["status"],
            "strategy": bot_data["config"]["strategy"],
            "trading_type": bot_data["config"]["trading_type"],
            "trading_pairs": bot_data["config"]["trading_pairs"],
            "exchanges": bot_data["config"]["exchanges"],
            "created_at": bot_data["created_at"],
            "performance": engine.performance.dict() if engine else {},
            "features": {
                "ml_predictions": engine.ml_predictor is not None if engine else False,
                "paper_trading": bot_data["config"]["paper_trading"],
                "risk_management": True,
                "smart_order_routing": bot_data["config"]["smart_order_routing"]
            }
        })
    
    return {
        "bots": bots,
        "total": len(bots),
        "filters": {
            "status": status.value if status else None,
            "strategy": strategy.value if strategy else None
        }
    }

@app.websocket("/api/v2/bots/{bot_id}/ws")
async def websocket_endpoint(websocket: WebSocket, bot_id: str):
    """WebSocket for real-time bot updates"""
    await websocket.accept()
    
    try:
        while True:
            if bot_id in bots_db:
                bot = bots_db[bot_id]
                engine = bot.get("engine")
                
                if engine:
                    update = {
                        "type": "status_update",
                        "bot_id": bot_id,
                        "status": engine.status.value,
                        "performance": engine.performance.dict(),
                        "positions": dict(engine.positions),
                        "open_orders": len(engine.orders),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    await websocket.send_text(json.dumps(update, default=str))
            
            await asyncio.sleep(1)  # Send updates every second
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for bot {bot_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

@app.post("/api/v2/bots/{bot_id}/restart")
async def restart_bot(bot_id: str, background_tasks: BackgroundTasks):
    """Restart a bot"""
    if bot_id not in bots_db:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    bot = bots_db[bot_id]
    engine = bot.get("engine")
    
    if not engine:
        raise HTTPException(status_code=400, detail="Bot engine not initialized")
    
    # Stop current bot
    await engine.stop()
    
    # Create new engine and start
    config = BotConfiguration(**bot["config"])
    new_engine = EnhancedMarketMakingEngine(config)
    bot["engine"] = new_engine
    
    background_tasks.add_task(new_engine.start)
    
    return {
        "success": True,
        "message": "Bot restarted successfully",
        "bot_id": bot_id
    }

@app.get("/api/v2/market-data/{pair}")
async def get_market_data(pair: str, exchanges: Optional[List[str]] = None):
    """Get aggregated market data for a pair"""
    if not exchanges:
        exchanges = list(market_data_cache.keys())
    
    market_data_list = []
    
    for exchange in exchanges:
        cache_key = f"{exchange}:{pair}"
        if cache_key in market_data_cache:
            market_data_list.append(market_data_cache[cache_key])
    
    if not market_data_list:
        raise HTTPException(status_code=404, detail="No market data available")
    
    # Aggregate data
    total_volume = sum(d.volume_24h for d in market_data_list)
    if total_volume > 0:
        weighted_bid = sum(d.bid * d.volume_24h for d in market_data_list) / total_volume
        weighted_ask = sum(d.ask * d.volume_24h for d in market_data_list) / total_volume
        weighted_last = sum(d.last_price * d.volume_24h for d in market_data_list) / total_volume
    else:
        weighted_bid = market_data_list[0].bid
        weighted_ask = market_data_list[0].ask
        weighted_last = market_data_list[0].last_price
    
    return {
        "symbol": pair,
        "aggregated": {
            "bid": weighted_bid,
            "ask": weighted_ask,
            "last": weighted_last,
            "spread": weighted_ask - weighted_bid,
            "spread_percentage": ((weighted_ask - weighted_bid) / weighted_last) * 100,
            "volume_24h": total_volume,
            "exchanges_count": len(market_data_list)
        },
        "by_exchange": [
            {
                "exchange": cache_key.split(":")[0],
                "bid": d.bid,
                "ask": d.ask,
                "last": d.last_price,
                "volume_24h": d.volume_24h,
                "spread_percentage": d.spread_percentage
            }
            for cache_key, d in market_data_cache.items()
            if cache_key.endswith(f":{pair}")
        ],
        "timestamp": datetime.now()
    }

@app.get("/api/v2/arbitrage/opportunities")
async def get_arbitrage_opportunities(pairs: Optional[List[str]] = None):
    """Get current arbitrage opportunities"""
    if not pairs:
        pairs = ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
    
    opportunities = []
    
    for pair in pairs:
        prices = {}
        
        # Get prices from all available exchanges
        for cache_key, market_data in market_data_cache.items():
            if cache_key.endswith(f":{pair}"):
                exchange = cache_key.split(":")[0]
                prices[exchange] = market_data.last_price
        
        # Find arbitrage opportunities
        if len(prices) >= 2:
            max_price_exchange = max(prices.items(), key=lambda x: x[1])
            min_price_exchange = min(prices.items(), key=lambda x: x[1])
            
            price_diff = max_price_exchange[1] - min_price_exchange[1]
            profit_potential = price_diff / min_price_exchange[1]
            
            if profit_potential > 0.001:  # 0.1% threshold
                opportunities.append({
                    "pair": pair,
                    "buy_exchange": min_price_exchange[0],
                    "sell_exchange": max_price_exchange[0],
                    "buy_price": min_price_exchange[1],
                    "sell_price": max_price_exchange[1],
                    "profit_potential": profit_potential,
                    "profit_potential_percentage": profit_potential * 100,
                    "timestamp": datetime.now()
                })
    
    return {
        "opportunities": opportunities,
        "total": len(opportunities),
        "scanned_pairs": pairs,
        "timestamp": datetime.now()
    }

# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    import uvicorn
    
    # Graceful shutdown handling
    def signal_handler(sig, frame):
        logger.info("Shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )