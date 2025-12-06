"""
TigerEx Consolidated Liquidity Aggregator v8.0.0
Merges all liquidity services: liquidity-aggregator, enhanced-liquidity-aggregator,
multi-exchange-liquidity-service, virtual-liquidity-service, own-liquidity-system
Complete liquidity management with multi-exchange integration and advanced features
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import logging
import aiohttp
import hashlib
import time
from decimal import Decimal
from dataclasses import dataclass
import redis
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TigerEx Consolidated Liquidity Aggregator v8.0.0",
    description="Complete liquidity management system with multi-exchange integration",
    version="8.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# ==================== ENUMS AND MODELS ====================

class Exchange(str, Enum):
    BINANCE = "binance"
    BYBIT = "bybit"
    OKX = "okx"
    KUCOIN = "kucoin"
    MEXC = "mexc"
    COINW = "coinw"
    COINBASE = "coinbase"
    KRAKEN = "kraken"
    BITFINEX = "bitfinex"
    HUOBI = "huobi"
    HTX = "htx"
    BITGET = "bitget"
    GEMINI = "gemini"
    WHITEBIT = "whitebit"
    TIGEREX = "tigerex"

class LiquiditySource(str, Enum):
    EXCHANGE_API = "exchange_api"
    MARKET_MAKER = "market_maker"
    INTERNAL_POOL = "internal_pool"
    DARK_POOL = "dark_pool"
    OTC_DESK = "otc_desk"
    WHALE_POOL = "whale_pool"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    IOC = "ioc"
    FOK = "fok"

class LiquidityStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"

@dataclass
class LiquidityProvider:
    id: str
    exchange: Exchange
    source_type: LiquiditySource
    status: LiquidityStatus
    api_endpoint: str
    api_key: Optional[str]
    api_secret: Optional[str]
    fee_rate: Decimal
    min_order_size: Decimal
    max_order_size: Decimal
    supported_pairs: List[str]
    latency_ms: float
    reliability_score: float
    last_updated: datetime

@dataclass
class LiquidityDepth:
    exchange: Exchange
    symbol: str
    bids: List[Tuple[Decimal, Decimal]]  # (price, quantity)
    asks: List[Tuple[Decimal, Decimal]]  # (price, quantity)
    timestamp: datetime
    spread: Decimal
    total_bid_depth: Decimal
    total_ask_depth: Decimal

@dataclass
class ConsolidatedOrderBook:
    symbol: str
    bids: List[Tuple[Decimal, Decimal, List[str]]]  # (price, quantity, sources)
    asks: List[Tuple[Decimal, Decimal, List[str]]]  # (price, quantity, sources)
    total_liquidity: Decimal
    best_bid: Decimal
    best_ask: Decimal
    spread: Decimal
    sources_count: int
    timestamp: datetime

@dataclass
class LiquidityMetrics:
    symbol: str
    total_bid_liquidity: Decimal
    total_ask_liquidity: Decimal
    spread_weighted: Decimal
    depth_at_spread: Decimal
    depth_1_percent: Decimal
    depth_5_percent: Decimal
    sources_active: int
    average_latency: float
    reliability_score: float
    timestamp: datetime

# ==================== PYDANTIC MODELS ====================

class LiquidityProviderConfig(BaseModel):
    exchange: Exchange
    source_type: LiquiditySource
    api_endpoint: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    fee_rate: Decimal = Field(..., ge=0, le=1)
    min_order_size: Decimal = Field(..., gt=0)
    max_order_size: Decimal = Field(..., gt=0)
    supported_pairs: List[str]

class LiquidityRequest(BaseModel):
    symbol: str
    side: str = Field(..., regex="^(buy|sell)$")
    quantity: Decimal = Field(..., gt=0)
    order_type: OrderType = OrderType.MARKET
    max_sources: Optional[int] = Field(None, ge=1, le=10)
    exclude_sources: Optional[List[Exchange]] = None
    preferred_sources: Optional[List[Exchange]] = None

class ArbitrageOpportunity(BaseModel):
    symbol: str
    buy_exchange: Exchange
    sell_exchange: Exchange
    buy_price: Decimal
    sell_price: Decimal
    spread: Decimal
    spread_percentage: Decimal
    volume: Decimal
    profit: Decimal
    timestamp: datetime

class LiquidityAnalysisResponse(BaseModel):
    symbol: str
    metrics: LiquidityMetrics
    top_liquidity_sources: List[Dict[str, Any]]
    arbitrage_opportunities: List[ArbitrageOpportunity]
    recommendations: List[str]

# ==================== CONSOLIDATED LIQUIDITY AGGREGATOR ====================

class ConsolidatedLiquidityAggregator:
    def __init__(self):
        self.providers: Dict[str, LiquidityProvider] = {}
        self.order_books: Dict[str, ConsolidatedOrderBook] = {}
        self.liquidity_metrics: Dict[str, LiquidityMetrics] = {}
        self.arbitrage_opportunities: List[ArbitrageOpportunity] = []
        
        # Performance metrics
        self.metrics = {
            'total_liquidity': Decimal('0'),
            'active_providers': 0,
            'total_api_calls': 0,
            'average_latency': 0.0,
            'arbitrage_opportunities': 0,
            'liquidity_updates': 0
        }
        
        # Initialize default providers
        self._initialize_providers()
        
        # Start background tasks
        asyncio.create_task(self._liquidity_updater())
        asyncio.create_task(self._arbitrage_scanner())
        asyncio.create_task(self._metrics_updater())
        asyncio.create_task(self._health_monitor())
    
    def _initialize_providers(self):
        """Initialize default liquidity providers"""
        default_providers = [
            {
                "id": "binance_spot",
                "exchange": Exchange.BINANCE,
                "source_type": LiquiditySource.EXCHANGE_API,
                "api_endpoint": "https://api.binance.com/api/v3",
                "fee_rate": Decimal("0.001"),
                "min_order_size": Decimal("10"),
                "max_order_size": Decimal("1000000"),
                "supported_pairs": ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
            },
            {
                "id": "bybit_spot",
                "exchange": Exchange.BYBIT,
                "source_type": LiquiditySource.EXCHANGE_API,
                "api_endpoint": "https://api.bybit.com/v5/market",
                "fee_rate": Decimal("0.001"),
                "min_order_size": Decimal("10"),
                "max_order_size": Decimal("1000000"),
                "supported_pairs": ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
            },
            {
                "id": "okx_spot",
                "exchange": Exchange.OKX,
                "source_type": LiquiditySource.EXCHANGE_API,
                "api_endpoint": "https://www.okx.com/api/v5/market",
                "fee_rate": Decimal("0.001"),
                "min_order_size": Decimal("10"),
                "max_order_size": Decimal("1000000"),
                "supported_pairs": ["BTC/USDT", "ETH/USDT", "ADA/USDT"]
            },
            {
                "id": "tigerex_mm",
                "exchange": Exchange.TIGEREX,
                "source_type": LiquiditySource.MARKET_MAKER,
                "api_endpoint": "internal://market-maker",
                "fee_rate": Decimal("0.0005"),
                "min_order_size": Decimal("1"),
                "max_order_size": Decimal("100000"),
                "supported_pairs": ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT"]
            }
        ]
        
        for provider_config in default_providers:
            provider = LiquidityProvider(
                id=provider_config["id"],
                exchange=provider_config["exchange"],
                source_type=provider_config["source_type"],
                status=LiquidityStatus.ACTIVE,
                api_endpoint=provider_config["api_endpoint"],
                api_key=provider_config.get("api_key"),
                api_secret=provider_config.get("api_secret"),
                fee_rate=provider_config["fee_rate"],
                min_order_size=provider_config["min_order_size"],
                max_order_size=provider_config["max_order_size"],
                supported_pairs=provider_config["supported_pairs"],
                latency_ms=50.0,
                reliability_score=0.95,
                last_updated=datetime.now()
            )
            self.providers[provider.id] = provider
    
    async def add_liquidity_provider(self, config: LiquidityProviderConfig) -> LiquidityProvider:
        """Add a new liquidity provider"""
        provider_id = f"{config.exchange.value}_{config.source_type.value}_{int(time.time())}"
        
        provider = LiquidityProvider(
            id=provider_id,
            exchange=config.exchange,
            source_type=config.source_type,
            status=LiquidityStatus.ACTIVE,
            api_endpoint=config.api_endpoint,
            api_key=config.api_key,
            api_secret=config.api_secret,
            fee_rate=config.fee_rate,
            min_order_size=config.min_order_size,
            max_order_size=config.max_order_size,
            supported_pairs=config.supported_pairs,
            latency_ms=100.0,
            reliability_score=0.90,
            last_updated=datetime.now()
        )
        
        self.providers[provider_id] = provider
        logger.info(f"Added liquidity provider: {provider_id}")
        return provider
    
    async def _fetch_order_book(self, provider: LiquidityProvider, symbol: str) -> Optional[LiquidityDepth]:
        """Fetch order book from a provider"""
        try:
            start_time = time.time()
            
            if provider.source_type == LiquiditySource.EXCHANGE_API:
                # Simulate API call
                await asyncio.sleep(0.05)  # Simulate network latency
                
                # Mock order book data
                bids = [
                    (Decimal('50000') - Decimal(i) * 10, Decimal('10') + Decimal(i))
                    for i in range(10)
                ]
                asks = [
                    (Decimal('50100') + Decimal(i) * 10, Decimal('10') + Decimal(i))
                    for i in range(10)
                ]
            else:
                # Internal market maker
                bids = [
                    (Decimal('49999') - Decimal(i) * 5, Decimal('5') + Decimal(i) * 2)
                    for i in range(20)
                ]
                asks = [
                    (Decimal('50101') + Decimal(i) * 5, Decimal('5') + Decimal(i) * 2)
                    for i in range(20)
                ]
            
            latency = (time.time() - start_time) * 1000
            provider.latency_ms = latency
            
            # Calculate spread and depth
            best_bid = bids[0][0] if bids else Decimal('0')
            best_ask = asks[0][0] if asks else Decimal('0')
            spread = best_ask - best_bid
            
            total_bid_depth = sum(quantity for _, quantity in bids)
            total_ask_depth = sum(quantity for _, quantity in asks)
            
            return LiquidityDepth(
                exchange=provider.exchange,
                symbol=symbol,
                bids=bids,
                asks=asks,
                timestamp=datetime.now(),
                spread=spread,
                total_bid_depth=total_bid_depth,
                total_ask_depth=total_ask_depth
            )
            
        except Exception as e:
            logger.error(f"Error fetching order book from {provider.id}: {e}")
            provider.status = LiquidityStatus.ERROR
            return None
    
    async def _consolidate_liquidity(self, symbol: str) -> ConsolidatedOrderBook:
        """Consolidate liquidity from all providers"""
        all_bids = []
        all_asks = []
        sources = set()
        
        # Fetch order books from all active providers
        tasks = []
        for provider in self.providers.values():
            if (provider.status == LiquidityStatus.ACTIVE and 
                symbol in provider.supported_pairs):
                tasks.append(self._fetch_order_book(provider, symbol))
        
        if tasks:
            depths = await asyncio.gather(*tasks, return_exceptions=True)
            
            for depth in depths:
                if isinstance(depth, LiquidityDepth):
                    sources.add(depth.exchange.value)
                    all_bids.extend([(price, quantity, [depth.exchange.value]) for price, quantity in depth.bids])
                    all_asks.extend([(price, quantity, [depth.exchange.value]) for price, quantity in depth.asks])
        
        # Sort and consolidate
        all_bids.sort(key=lambda x: x[0], reverse=True)  # Highest bid first
        all_asks.sort(key=lambda x: x[0])  # Lowest ask first
        
        # Consolidate same price levels
        consolidated_bids = self._consolidate_price_levels(all_bids)
        consolidated_asks = self._consolidate_price_levels(all_asks)
        
        # Calculate metrics
        best_bid = consolidated_bids[0][0] if consolidated_bids else Decimal('0')
        best_ask = consolidated_asks[0][0] if consolidated_asks else Decimal('0')
        spread = best_ask - best_bid
        
        total_liquidity = sum(quantity for _, quantity, _ in consolidated_bids) + \
                         sum(quantity for _, quantity, _ in consolidated_asks)
        
        return ConsolidatedOrderBook(
            symbol=symbol,
            bids=consolidated_bids[:100],  # Top 100 levels
            asks=consolidated_asks[:100],  # Top 100 levels
            total_liquidity=total_liquidity,
            best_bid=best_bid,
            best_ask=best_ask,
            spread=spread,
            sources_count=len(sources),
            timestamp=datetime.now()
        )
    
    def _consolidate_price_levels(self, price_levels: List[Tuple[Decimal, Decimal, List[str]]]) -> List[Tuple[Decimal, Decimal, List[str]]]:
        """Consolidate price levels from multiple sources"""
        if not price_levels:
            return []
        
        consolidated = {}
        for price, quantity, sources in price_levels:
            if price in consolidated:
                consolidated[price] = (
                    consolidated[price][0] + quantity,
                    list(set(consolidated[price][1] + sources))
                )
            else:
                consolidated[price] = (quantity, sources)
        
        return [(price, qty, srcs) for price, (qty, srcs) in consolidated.items()]
    
    async def get_liquidity_analysis(self, symbol: str) -> LiquidityAnalysisResponse:
        """Get comprehensive liquidity analysis for a symbol"""
        # Get consolidated order book
        order_book = await self._consolidate_liquidity(symbol)
        self.order_books[symbol] = order_book
        
        # Calculate liquidity metrics
        metrics = self._calculate_liquidity_metrics(symbol, order_book)
        self.liquidity_metrics[symbol] = metrics
        
        # Get top liquidity sources
        top_sources = self._get_top_liquidity_sources(symbol)
        
        # Get arbitrage opportunities
        opportunities = self._get_arbitrage_opportunities(symbol)
        
        # Generate recommendations
        recommendations = self._generate_liquidity_recommendations(metrics, opportunities)
        
        return LiquidityAnalysisResponse(
            symbol=symbol,
            metrics=metrics,
            top_liquidity_sources=top_sources,
            arbitrage_opportunities=opportunities,
            recommendations=recommendations
        )
    
    def _calculate_liquidity_metrics(self, symbol: str, order_book: ConsolidatedOrderBook) -> LiquidityMetrics:
        """Calculate liquidity metrics"""
        total_bid_liquidity = sum(quantity for _, quantity, _ in order_book.bids)
        total_ask_liquidity = sum(quantity for _, quantity, _ in order_book.asks)
        
        # Weighted spread
        if order_book.bids and order_book.asks:
            total_volume = total_bid_liquidity + total_ask_liquidity
            spread_weighted = order_book.spread * (total_bid_liquidity / total_volume)
        else:
            spread_weighted = Decimal('0')
        
        # Depth at spread (within 0.1% of mid price)
        if order_book.best_bid > 0 and order_book.best_ask > 0:
            mid_price = (order_book.best_bid + order_book.best_ask) / 2
            spread_threshold = mid_price * Decimal('0.001')
            
            depth_at_spread = sum(
                quantity for price, quantity, _ in order_book.bids + order_book.asks
                if abs(price - mid_price) <= spread_threshold
            )
            
            # Depth at 1% and 5%
            threshold_1_percent = mid_price * Decimal('0.01')
            threshold_5_percent = mid_price * Decimal('0.05')
            
            depth_1_percent = sum(
                quantity for price, quantity, _ in order_book.bids + order_book.asks
                if abs(price - mid_price) <= threshold_1_percent
            )
            
            depth_5_percent = sum(
                quantity for price, quantity, _ in order_book.bids + order_book.asks
                if abs(price - mid_price) <= threshold_5_percent
            )
        else:
            depth_at_spread = depth_1_percent = depth_5_percent = Decimal('0')
        
        # Active providers and average latency
        active_providers = [
            p for p in self.providers.values()
            if p.status == LiquidityStatus.ACTIVE and symbol in p.supported_pairs
        ]
        
        average_latency = sum(p.latency_ms for p in active_providers) / len(active_providers) if active_providers else 0
        reliability_score = sum(p.reliability_score for p in active_providers) / len(active_providers) if active_providers else 0
        
        return LiquidityMetrics(
            symbol=symbol,
            total_bid_liquidity=total_bid_liquidity,
            total_ask_liquidity=total_ask_liquidity,
            spread_weighted=spread_weighted,
            depth_at_spread=depth_at_spread,
            depth_1_percent=depth_1_percent,
            depth_5_percent=depth_5_percent,
            sources_active=len(active_providers),
            average_latency=average_latency,
            reliability_score=reliability_score,
            timestamp=datetime.now()
        )
    
    def _get_top_liquidity_sources(self, symbol: str) -> List[Dict[str, Any]]:
        """Get top liquidity sources for a symbol"""
        source_metrics = []
        
        for provider in self.providers.values():
            if provider.status == LiquidityStatus.ACTIVE and symbol in provider.supported_pairs:
                source_metrics.append({
                    "exchange": provider.exchange.value,
                    "source_type": provider.source_type.value,
                    "fee_rate": str(provider.fee_rate),
                    "latency_ms": provider.latency_ms,
                    "reliability_score": provider.reliability_score,
                    "max_order_size": str(provider.max_order_size)
                })
        
        # Sort by reliability score and latency
        source_metrics.sort(key=lambda x: (x["reliability_score"], -x["latency_ms"]), reverse=True)
        
        return source_metrics[:10]
    
    def _get_arbitrage_opportunities(self, symbol: str) -> List[ArbitrageOpportunity]:
        """Get arbitrage opportunities for a symbol"""
        opportunities = []
        
        # Get prices from all sources
        source_prices = {}
        for provider in self.providers.values():
            if (provider.status == LiquidityStatus.ACTIVE and 
                symbol in provider.supported_pairs):
                # Simulate price fetching
                base_price = Decimal('50000')
                price_variation = (hash(provider.id) % 1000 - 500) / 10000
                source_prices[provider.exchange] = base_price * (1 + price_variation)
        
        # Find arbitrage opportunities
        exchanges = list(source_prices.keys())
        for i in range(len(exchanges)):
            for j in range(i + 1, len(exchanges)):
                exchange1, exchange2 = exchanges[i], exchanges[j]
                price1, price2 = source_prices[exchange1], source_prices[exchange2]
                
                if price1 < price2:
                    spread = price2 - price1
                    spread_percentage = (spread / price1) * 100
                    
                    if spread_percentage > 0.1:  # Threshold for arbitrage
                        opportunities.append(ArbitrageOpportunity(
                            symbol=symbol,
                            buy_exchange=exchange1,
                            sell_exchange=exchange2,
                            buy_price=price1,
                            sell_price=price2,
                            spread=spread,
                            spread_percentage=spread_percentage,
                            volume=Decimal('100'),  # Default volume
                            profit=spread * Decimal('100'),
                            timestamp=datetime.now()
                        ))
        
        return sorted(opportunities, key=lambda x: x.spread_percentage, reverse=True)[:5]
    
    def _generate_liquidity_recommendations(self, metrics: LiquidityMetrics, opportunities: List[ArbitrageOpportunity]) -> List[str]:
        """Generate liquidity recommendations"""
        recommendations = []
        
        if metrics.average_latency > 100:
            recommendations.append("Consider optimizing network connections to reduce latency")
        
        if metrics.reliability_score < 0.9:
            recommendations.append("Some liquidity sources have low reliability scores")
        
        if metrics.spread_weighted > Decimal('0.01'):
            recommendations.append("Spread is relatively high, consider adding more liquidity sources")
        
        if len(opportunities) > 0:
            recommendations.append(f"Found {len(opportunities)} arbitrage opportunities")
        
        if metrics.sources_active < 3:
            recommendations.append("Consider adding more liquidity providers for better depth")
        
        if not recommendations:
            recommendations.append("Liquidity conditions are optimal")
        
        return recommendations
    
    async def _liquidity_updater(self):
        """Background task to update liquidity data"""
        while True:
            try:
                symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT"]
                
                for symbol in symbols:
                    await self._consolidate_liquidity(symbol)
                    self.metrics['liquidity_updates'] += 1
                
                await asyncio.sleep(1)  # Update every second
            except Exception as e:
                logger.error(f"Error in liquidity updater: {e}")
                await asyncio.sleep(5)
    
    async def _arbitrage_scanner(self):
        """Background task to scan for arbitrage opportunities"""
        while True:
            try:
                symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
                
                all_opportunities = []
                for symbol in symbols:
                    opportunities = self._get_arbitrage_opportunities(symbol)
                    all_opportunities.extend(opportunities)
                
                self.arbitrage_opportunities = all_opportunities
                self.metrics['arbitrage_opportunities'] = len(all_opportunities)
                
                await asyncio.sleep(5)  # Scan every 5 seconds
            except Exception as e:
                logger.error(f"Error in arbitrage scanner: {e}")
                await asyncio.sleep(10)
    
    async def _metrics_updater(self):
        """Background task to update performance metrics"""
        while True:
            try:
                # Calculate total liquidity
                total_liquidity = sum(
                    ob.total_liquidity for ob in self.order_books.values()
                )
                self.metrics['total_liquidity'] = total_liquidity
                
                # Count active providers
                active_providers = sum(
                    1 for p in self.providers.values()
                    if p.status == LiquidityStatus.ACTIVE
                )
                self.metrics['active_providers'] = active_providers
                
                # Calculate average latency
                if self.providers:
                    avg_latency = sum(p.latency_ms for p in self.providers.values()) / len(self.providers)
                    self.metrics['average_latency'] = avg_latency
                
                await asyncio.sleep(10)  # Update every 10 seconds
            except Exception as e:
                logger.error(f"Error in metrics updater: {e}")
                await asyncio.sleep(30)
    
    async def _health_monitor(self):
        """Background task to monitor provider health"""
        while True:
            try:
                for provider in self.providers.values():
                    if provider.status == LiquidityStatus.ERROR:
                        # Try to recover
                        provider.status = LiquidityStatus.ACTIVE
                        provider.last_updated = datetime.now()
                        logger.info(f"Recovered provider: {provider.id}")
                
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in health monitor: {e}")
                await asyncio.sleep(60)

# Initialize liquidity aggregator
liquidity_aggregator = ConsolidatedLiquidityAggregator()

# ==================== API ENDPOINTS ====================

@app.post("/providers", response_model=Dict[str, Any])
async def add_liquidity_provider(
    config: LiquidityProviderConfig,
    credentials: str = Depends(security)
):
    """Add a new liquidity provider"""
    try:
        provider = await liquidity_aggregator.add_liquidity_provider(config)
        return {
            "provider_id": provider.id,
            "status": "success",
            "message": f"Liquidity provider {provider.id} added successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/analysis/{symbol}", response_model=LiquidityAnalysisResponse)
async def get_liquidity_analysis(symbol: str):
    """Get comprehensive liquidity analysis for a symbol"""
    try:
        return await liquidity_aggregator.get_liquidity_analysis(symbol)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/orderbook/{symbol}")
async def get_consolidated_orderbook(symbol: str, depth: int = 20):
    """Get consolidated order book"""
    try:
        order_book = await liquidity_aggregator._consolidate_liquidity(symbol)
        
        return {
            "symbol": symbol,
            "bids": [[str(price), str(quantity), sources] for price, quantity, sources in order_book.bids[:depth]],
            "asks": [[str(price), str(quantity), sources] for price, quantity, sources in order_book.asks[:depth]],
            "total_liquidity": str(order_book.total_liquidity),
            "best_bid": str(order_book.best_bid),
            "best_ask": str(order_book.best_ask),
            "spread": str(order_book.spread),
            "sources_count": order_book.sources_count,
            "timestamp": order_book.timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/providers")
async def get_liquidity_providers():
    """Get all liquidity providers"""
    providers = []
    for provider in liquidity_aggregator.providers.values():
        providers.append({
            "id": provider.id,
            "exchange": provider.exchange.value,
            "source_type": provider.source_type.value,
            "status": provider.status.value,
            "fee_rate": str(provider.fee_rate),
            "latency_ms": provider.latency_ms,
            "reliability_score": provider.reliability_score,
            "supported_pairs": provider.supported_pairs,
            "last_updated": provider.last_updated
        })
    
    return {"providers": providers}

@app.get("/arbitrage")
async def get_arbitrage_opportunities():
    """Get current arbitrage opportunities"""
    opportunities = []
    for opp in liquidity_aggregator.arbitrage_opportunities:
        opportunities.append({
            "symbol": opp.symbol,
            "buy_exchange": opp.buy_exchange.value,
            "sell_exchange": opp.sell_exchange.value,
            "buy_price": str(opp.buy_price),
            "sell_price": str(opp.sell_price),
            "spread": str(opp.spread),
            "spread_percentage": str(opp.spread_percentage),
            "volume": str(opp.volume),
            "profit": str(opp.profit),
            "timestamp": opp.timestamp
        })
    
    return {"opportunities": opportunities}

@app.get("/metrics")
async def get_aggregator_metrics():
    """Get liquidity aggregator metrics"""
    return {
        "total_liquidity": str(liquidity_aggregator.metrics['total_liquidity']),
        "active_providers": liquidity_aggregator.metrics['active_providers'],
        "total_api_calls": liquidity_aggregator.metrics['total_api_calls'],
        "average_latency": liquidity_aggregator.metrics['average_latency'],
        "arbitrage_opportunities": liquidity_aggregator.metrics['arbitrage_opportunities'],
        "liquidity_updates": liquidity_aggregator.metrics['liquidity_updates'],
        "symbols_tracked": list(liquidity_aggregator.order_books.keys())
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "consolidated-liquidity-aggregator",
        "version": "8.0.0",
        "timestamp": datetime.now().isoformat(),
        "metrics": liquidity_aggregator.metrics
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "consolidated_main:app",
        host="0.0.0.0",
        port=3002,
        reload=True,
        log_level="info"
    )