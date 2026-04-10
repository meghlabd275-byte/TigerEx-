#!/usr/bin/env python3
"""
Multi-Exchange Liquidity Aggregator for TigerEx
Aggregates liquidity from multiple exchanges for best execution
Features: Smart order routing, arbitrage detection, TWAP/VWAP execution
"""

import asyncio
import aiohttp
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TigerEx Liquidity Aggregator")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis for caching
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# === Enums ===

class Exchange(str, Enum):
    BINANCE = "binance"
    COINBASE = "coinbase"
    KRAKEN = "kraken"
    BITFINEX = "bitfinex"
    OKX = "okx"
    BYBIT = "bybit"
    HUOBI = "huobi"
    KUCOIN = "kucoin"
    GATE = "gate"
    BITGET = "bitget"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    TWAP = "twap"
    VWAP = "vwap"
    ICEBERG = "iceberg"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class ExecutionAlgorithm(str, Enum):
    BEST_PRICE = "best_price"
    VWAP = "vwap"
    TWAP = "twap"
    IMPLEMENTATION_SHORTFALL = "implementation_shortfall"
    PARTICIPATION_RATE = "participation_rate"

# === Data Models ===

@dataclass
class OrderBookLevel:
    price: Decimal
    quantity: Decimal
    exchange: str

@dataclass
class AggregatedOrderBook:
    symbol: str
    timestamp: str
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    total_bid_volume: Decimal
    total_ask_volume: Decimal
    best_bid: Decimal
    best_ask: Decimal
    spread: Decimal
    mid_price: Decimal

@dataclass
class ExchangeOrderBook:
    exchange: str
    symbol: str
    bids: List[Tuple[Decimal, Decimal]]
    asks: List[Tuple[Decimal, Decimal]]
    timestamp: str
    last_update_id: Optional[int] = None

class SmartOrder(BaseModel):
    symbol: str
    side: OrderSide
    quantity: float
    order_type: OrderType = OrderType.MARKET
    price: Optional[float] = None
    algorithm: ExecutionAlgorithm = ExecutionAlgorithm.BEST_PRICE
    time_horizon: Optional[int] = None  # For TWAP/VWAP (in seconds)
    participation_rate: Optional[float] = None  # For participation rate algorithm
    max_slippage: Optional[float] = None

class ExecutionPlan(BaseModel):
    plan_id: str
    symbol: str
    side: OrderSide
    total_quantity: float
    algorithm: ExecutionAlgorithm
    child_orders: List[Dict[str, Any]]
    estimated_avg_price: float
    estimated_slippage: float
    estimated_completion_time: int
    created_at: str

class ArbitrageOpportunity(BaseModel):
    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    spread_percent: float
    estimated_profit: float
    quantity_available: float
    timestamp: str

# === Exchange Connectors ===

class ExchangeConnector:
    """Base class for exchange connectors"""
    
    def __init__(self, exchange: Exchange):
        self.exchange = exchange
        self.base_url = self._get_base_url()
        self.session = aiohttp.ClientSession()
    
    def _get_base_url(self) -> str:
        urls = {
            Exchange.BINANCE: "https://api.binance.com",
            Exchange.COINBASE: "https://api.exchange.coinbase.com",
            Exchange.KRAKEN: "https://api.kraken.com",
            Exchange.BITFINEX: "https://api.bitfinex.com",
            Exchange.OKX: "https://www.okx.com",
            Exchange.BYBIT: "https://api.bybit.com",
            Exchange.HUOBI: "https://api.huobi.pro",
            Exchange.KUCOIN: "https://api.kucoin.com",
            Exchange.GATE: "https://api.gate.io",
            Exchange.BITGET: "https://api.bitget.com"
        }
        return urls.get(self.exchange, "")
    
    async def get_orderbook(self, symbol: str) -> Optional[ExchangeOrderBook]:
        """Fetch order book from exchange"""
        try:
            if self.exchange == Exchange.BINANCE:
                return await self._get_binance_orderbook(symbol)
            elif self.exchange == Exchange.COINBASE:
                return await self._get_coinbase_orderbook(symbol)
            elif self.exchange == Exchange.KRAKEN:
                return await self._get_kraken_orderbook(symbol)
            elif self.exchange == Exchange.BYBIT:
                return await self._get_bybit_orderbook(symbol)
            elif self.exchange == Exchange.OKX:
                return await self._get_okx_orderbook(symbol)
            else:
                return await self._get_generic_orderbook(symbol)
        except Exception as e:
            logger.error(f"Error fetching {self.exchange} orderbook: {e}")
            return None
    
    async def _get_binance_orderbook(self, symbol: str) -> ExchangeOrderBook:
        """Binance order book"""
        # Convert symbol format (BTCUSDT)
        url = f"{self.base_url}/api/v3/depth?symbol={symbol}&limit=100"
        
        async with self.session.get(url) as response:
            data = await response.json()
            
            bids = [(Decimal(b[0]), Decimal(b[1])) for b in data.get("bids", [])]
            asks = [(Decimal(a[0]), Decimal(a[1])) for a in data.get("asks", [])]
            
            return ExchangeOrderBook(
                exchange=self.exchange.value,
                symbol=symbol,
                bids=bids,
                asks=asks,
                timestamp=datetime.utcnow().isoformat(),
                last_update_id=data.get("lastUpdateId")
            )
    
    async def _get_coinbase_orderbook(self, symbol: str) -> ExchangeOrderBook:
        """Coinbase order book"""
        # Convert symbol format (BTC-USD)
        formatted_symbol = symbol.replace("USDT", "-USD")
        url = f"{self.base_url}/products/{formatted_symbol}/book?level=2"
        
        async with self.session.get(url) as response:
            data = await response.json()
            
            bids = [(Decimal(b[0]), Decimal(b[1])) for b in data.get("bids", [])]
            asks = [(Decimal(a[0]), Decimal(a[1])) for a in data.get("asks", [])]
            
            return ExchangeOrderBook(
                exchange=self.exchange.value,
                symbol=symbol,
                bids=bids,
                asks=asks,
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def _get_kraken_orderbook(self, symbol: str) -> ExchangeOrderBook:
        """Kraken order book"""
        # Convert symbol format (XBTUSDT -> XBTUSDT)
        url = f"{self.base_url}/0/public/Depth?pair={symbol}&count=100"
        
        async with self.session.get(url) as response:
            data = await response.json()
            
            result = data.get("result", {})
            pair_data = list(result.values())[0] if result else {}
            
            bids = [(Decimal(b[0]), Decimal(b[1])) for b in pair_data.get("bids", [])]
            asks = [(Decimal(a[0]), Decimal(a[1])) for a in pair_data.get("asks", [])]
            
            return ExchangeOrderBook(
                exchange=self.exchange.value,
                symbol=symbol,
                bids=bids,
                asks=asks,
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def _get_bybit_orderbook(self, symbol: str) -> ExchangeOrderBook:
        """Bybit order book"""
        url = f"{self.base_url}/v5/market/orderbook?category=spot&symbol={symbol}&limit=100"
        
        async with self.session.get(url) as response:
            data = await response.json()
            
            result = data.get("result", {})
            
            bids = [(Decimal(b[0]), Decimal(b[1])) for b in result.get("b", [])]
            asks = [(Decimal(a[0]), Decimal(a[1])) for a in result.get("a", [])]
            
            return ExchangeOrderBook(
                exchange=self.exchange.value,
                symbol=symbol,
                bids=bids,
                asks=asks,
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def _get_okx_orderbook(self, symbol: str) -> ExchangeOrderBook:
        """OKX order book"""
        # Convert symbol format (BTC-USDT)
        formatted_symbol = symbol.replace("USDT", "-USDT")
        url = f"{self.base_url}/api/v5/market/books?instId={formatted_symbol}"
        
        async with self.session.get(url) as response:
            data = await response.json()
            
            result = data.get("data", [{}])[0]
            
            bids = [(Decimal(b[0]), Decimal(b[1])) for b in result.get("bids", [])]
            asks = [(Decimal(a[0]), Decimal(a[1])) for a in result.get("asks", [])]
            
            return ExchangeOrderBook(
                exchange=self.exchange.value,
                symbol=symbol,
                bids=bids,
                asks=asks,
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def _get_generic_orderbook(self, symbol: str) -> ExchangeOrderBook:
        """Generic order book fetcher (placeholder)"""
        # Generate simulated data for exchanges without specific implementation
        base_price = 50000 if "BTC" in symbol else 3000
        
        bids = []
        asks = []
        
        for i in range(20):
            bid_price = Decimal(str(base_price * (1 - 0.0001 * (i + 1))))
            ask_price = Decimal(str(base_price * (1 + 0.0001 * (i + 1))))
            quantity = Decimal(str(np.random.uniform(0.1, 5)))
            
            bids.append((bid_price, quantity))
            asks.append((ask_price, quantity))
        
        return ExchangeOrderBook(
            exchange=self.exchange.value,
            symbol=symbol,
            bids=bids,
            asks=asks,
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def close(self):
        await self.session.close()


# === Liquidity Aggregator ===

class LiquidityAggregator:
    """
    Multi-exchange liquidity aggregator
    Provides unified order book and smart order routing
    """
    
    def __init__(self, exchanges: List[Exchange] = None):
        self.exchanges = exchanges or [
            Exchange.BINANCE,
            Exchange.COINBASE,
            Exchange.KRAKEN,
            Exchange.BYBIT,
            Exchange.OKX
        ]
        self.connectors = {ex: ExchangeConnector(ex) for ex in self.exchanges}
        self.orderbook_cache: Dict[str, AggregatedOrderBook] = {}
        self.cache_ttl = 1  # seconds
    
    async def aggregate_orderbook(self, symbol: str) -> AggregatedOrderBook:
        """Aggregate order books from all exchanges"""
        
        # Check cache
        cache_key = f"aggregated_orderbook:{symbol}"
        cached = redis_client.get(cache_key)
        
        if cached:
            data = json.loads(cached)
            # Reconstruct from cache
            # For now, fetch fresh data
        
        # Fetch from all exchanges concurrently
        tasks = [
            connector.get_orderbook(symbol)
            for connector in self.connectors.values()
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Aggregate bids and asks
        all_bids = []
        all_asks = []
        
        for result in results:
            if result:
                for price, qty in result.bids:
                    all_bids.append(OrderBookLevel(
                        price=price,
                        quantity=qty,
                        exchange=result.exchange
                    ))
                for price, qty in result.asks:
                    all_asks.append(OrderBookLevel(
                        price=price,
                        quantity=qty,
                        exchange=result.exchange
                    ))
        
        # Sort: bids by price descending, asks by price ascending
        all_bids.sort(key=lambda x: x.price, reverse=True)
        all_asks.sort(key=lambda x: x.price)
        
        # Calculate totals
        total_bid_volume = sum(b.quantity for b in all_bids)
        total_ask_volume = sum(a.quantity for a in all_asks)
        
        best_bid = all_bids[0].price if all_bids else Decimal("0")
        best_ask = all_asks[0].price if all_asks else Decimal("0")
        spread = best_ask - best_bid if all_bids and all_asks else Decimal("0")
        mid_price = (best_bid + best_ask) / 2 if all_bids and all_asks else Decimal("0")
        
        aggregated = AggregatedOrderBook(
            symbol=symbol,
            timestamp=datetime.utcnow().isoformat(),
            bids=all_bids[:100],  # Top 100 levels
            asks=all_asks[:100],
            total_bid_volume=total_bid_volume,
            total_ask_volume=total_ask_volume,
            best_bid=best_bid,
            best_ask=best_ask,
            spread=spread,
            mid_price=mid_price
        )
        
        # Cache result
        # Note: Would need custom serialization for OrderBookLevel
        
        return aggregated
    
    async def find_best_execution(self, symbol: str, side: OrderSide,
                                   quantity: Decimal) -> List[Dict]:
        """
        Find best execution path across exchanges
        Returns list of orders to place on each exchange
        """
        
        orderbook = await self.aggregate_orderbook(symbol)
        
        remaining_qty = quantity
        execution_plan = []
        total_cost = Decimal("0")
        
        if side == OrderSide.BUY:
            # Execute against asks (sorted by price ascending)
            for level in orderbook.asks:
                if remaining_qty <= 0:
                    break
                
                fill_qty = min(remaining_qty, level.quantity)
                cost = fill_qty * level.price
                
                execution_plan.append({
                    "exchange": level.exchange,
                    "side": "buy",
                    "price": float(level.price),
                    "quantity": float(fill_qty),
                    "cost": float(cost)
                })
                
                remaining_qty -= fill_qty
                total_cost += cost
        else:
            # Execute against bids (sorted by price descending)
            for level in orderbook.bids:
                if remaining_qty <= 0:
                    break
                
                fill_qty = min(remaining_qty, level.quantity)
                proceeds = fill_qty * level.price
                
                execution_plan.append({
                    "exchange": level.exchange,
                    "side": "sell",
                    "price": float(level.price),
                    "quantity": float(fill_qty),
                    "proceeds": float(proceeds)
                })
                
                remaining_qty -= fill_qty
                total_cost += proceeds
        
        return {
            "symbol": symbol,
            "side": side.value,
            "total_quantity": float(quantity),
            "filled_quantity": float(quantity - remaining_qty),
            "unfilled_quantity": float(remaining_qty),
            "execution_plan": execution_plan,
            "average_price": float(total_cost / (quantity - remaining_qty)) if quantity != remaining_qty else 0
        }
    
    async def detect_arbitrage(self, symbol: str) -> List[ArbitrageOpportunity]:
        """Detect arbitrage opportunities across exchanges"""
        
        # Fetch order books
        tasks = [
            connector.get_orderbook(symbol)
            for connector in self.connectors.values()
        ]
        
        results = await asyncio.gather(*tasks)
        
        opportunities = []
        
        # Compare best bid/ask across exchanges
        exchange_prices = {}
        
        for result in results:
            if result and result.bids and result.asks:
                best_bid = result.bids[0][0]
                best_ask = result.asks[0][0]
                
                exchange_prices[result.exchange] = {
                    "best_bid": float(best_bid),
                    "best_ask": float(best_ask),
                    "bid_qty": float(result.bids[0][1]),
                    "ask_qty": float(result.asks[0][1])
                }
        
        # Find arbitrage opportunities
        for buy_ex, buy_data in exchange_prices.items():
            for sell_ex, sell_data in exchange_prices.items():
                if buy_ex == sell_ex:
                    continue
                
                buy_price = buy_data["best_ask"]
                sell_price = sell_data["best_bid"]
                
                if sell_price > buy_price:
                    spread_percent = (sell_price - buy_price) / buy_price * 100
                    
                    # Account for fees (approximate 0.1% each side)
                    net_spread = spread_percent - 0.2
                    
                    if net_spread > 0:
                        quantity = min(buy_data["ask_qty"], sell_data["bid_qty"])
                        estimated_profit = (sell_price - buy_price) * quantity
                        
                        opportunities.append(ArbitrageOpportunity(
                            symbol=symbol,
                            buy_exchange=buy_ex,
                            sell_exchange=sell_ex,
                            buy_price=buy_price,
                            sell_price=sell_price,
                            spread_percent=round(spread_percent, 4),
                            estimated_profit=round(estimated_profit, 2),
                            quantity_available=round(quantity, 6),
                            timestamp=datetime.utcnow().isoformat()
                        ))
        
        # Sort by profit potential
        opportunities.sort(key=lambda x: x.estimated_profit, reverse=True)
        
        return opportunities[:10]  # Top 10 opportunities
    
    async def calculate_twap_execution(self, symbol: str, side: OrderSide,
                                        total_quantity: float, duration_minutes: int) -> ExecutionPlan:
        """Calculate TWAP (Time-Weighted Average Price) execution plan"""
        
        # Number of slices
        num_slices = min(duration_minutes, 60)  # Max 60 slices
        quantity_per_slice = total_quantity / num_slices
        
        child_orders = []
        
        for i in range(num_slices):
            child_orders.append({
                "slice_number": i + 1,
                "quantity": quantity_per_slice,
                "scheduled_time": i * (duration_minutes / num_slices),
                "status": "pending"
            })
        
        return ExecutionPlan(
            plan_id=str(uuid.uuid4()),
            symbol=symbol,
            side=side,
            total_quantity=total_quantity,
            algorithm=ExecutionAlgorithm.TWAP,
            child_orders=child_orders,
            estimated_avg_price=0,  # Would be calculated based on current market
            estimated_slippage=0.001,  # 0.1% estimated slippage
            estimated_completion_time=duration_minutes * 60,
            created_at=datetime.utcnow().isoformat()
        )
    
    async def calculate_vwap_execution(self, symbol: str, side: OrderSide,
                                        total_quantity: float, duration_minutes: int) -> ExecutionPlan:
        """Calculate VWAP (Volume-Weighted Average Price) execution plan"""
        
        # Get historical volume profile
        # For now, use simple distribution
        
        # Simulated volume profile (typically U-shaped through the day)
        num_slices = min(duration_minutes, 60)
        
        # Generate volume weights (higher at open/close)
        weights = []
        for i in range(num_slices):
            progress = i / num_slices
            # U-shaped weight
            weight = 1 + 0.5 * np.cos(progress * 2 * np.pi)
            weights.append(weight)
        
        # Normalize weights
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        # Calculate quantities per slice
        child_orders = []
        cumulative_qty = 0
        
        for i, weight in enumerate(normalized_weights):
            slice_qty = total_quantity * weight
            cumulative_qty += slice_qty
            
            child_orders.append({
                "slice_number": i + 1,
                "quantity": slice_qty,
                "weight": weight,
                "scheduled_time": i * (duration_minutes / num_slices),
                "status": "pending"
            })
        
        return ExecutionPlan(
            plan_id=str(uuid.uuid4()),
            symbol=symbol,
            side=side,
            total_quantity=total_quantity,
            algorithm=ExecutionAlgorithm.VWAP,
            child_orders=child_orders,
            estimated_avg_price=0,
            estimated_slippage=0.0005,
            estimated_completion_time=duration_minutes * 60,
            created_at=datetime.utcnow().isoformat()
        )
    
    async def close(self):
        """Close all connections"""
        for connector in self.connectors.values():
            await connector.close()


# Initialize aggregator
aggregator = LiquidityAggregator()

# === API Endpoints ===

@app.get("/")
async def root():
    return {"service": "TigerEx Liquidity Aggregator", "status": "active"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/orderbook/{symbol}")
async def get_aggregated_orderbook(symbol: str):
    """Get aggregated order book for a symbol"""
    orderbook = await aggregator.aggregate_orderbook(symbol)
    
    return {
        "symbol": orderbook.symbol,
        "timestamp": orderbook.timestamp,
        "best_bid": float(orderbook.best_bid),
        "best_ask": float(orderbook.best_ask),
        "spread": float(orderbook.spread),
        "mid_price": float(orderbook.mid_price),
        "total_bid_volume": float(orderbook.total_bid_volume),
        "total_ask_volume": float(orderbook.total_ask_volume),
        "bids": [
            {"price": float(b.price), "quantity": float(b.quantity), "exchange": b.exchange}
            for b in orderbook.bids[:20]
        ],
        "asks": [
            {"price": float(a.price), "quantity": float(a.quantity), "exchange": a.exchange}
            for a in orderbook.asks[:20]
        ]
    }

@app.post("/execution/best")
async def find_best_execution(order: SmartOrder):
    """Find best execution path for an order"""
    result = await aggregator.find_best_execution(
        symbol=order.symbol,
        side=order.side,
        quantity=Decimal(str(order.quantity))
    )
    return result

@app.get("/arbitrage/{symbol}")
async def find_arbitrage(symbol: str):
    """Find arbitrage opportunities for a symbol"""
    opportunities = await aggregator.detect_arbitrage(symbol)
    return [opp.dict() for opp in opportunities]

@app.post("/execution/twap")
async def create_twap_plan(order: SmartOrder):
    """Create TWAP execution plan"""
    if not order.time_horizon:
        raise HTTPException(status_code=400, detail="time_horizon required for TWAP")
    
    plan = await aggregator.calculate_twap_execution(
        symbol=order.symbol,
        side=order.side,
        total_quantity=order.quantity,
        duration_minutes=order.time_horizon // 60
    )
    return plan.dict()

@app.post("/execution/vwap")
async def create_vwap_plan(order: SmartOrder):
    """Create VWAP execution plan"""
    if not order.time_horizon:
        raise HTTPException(status_code=400, detail="time_horizon required for VWAP")
    
    plan = await aggregator.calculate_vwap_execution(
        symbol=order.symbol,
        side=order.side,
        total_quantity=order.quantity,
        duration_minutes=order.time_horizon // 60
    )
    return plan.dict()

@app.get("/exchanges")
async def list_exchanges():
    """List connected exchanges"""
    return {
        "exchanges": [ex.value for ex in aggregator.exchanges],
        "status": {ex.value: "connected" for ex in aggregator.exchanges}
    }

@app.get("/prices/{symbol}")
async def get_best_prices(symbol: str):
    """Get best bid/ask across all exchanges"""
    orderbook = await aggregator.aggregate_orderbook(symbol)
    
    # Get best prices per exchange
    exchange_prices = {}
    
    for level in orderbook.bids[:20]:
        if level.exchange not in exchange_prices:
            exchange_prices[level.exchange] = {"bid": None, "ask": None}
        if exchange_prices[level.exchange]["bid"] is None:
            exchange_prices[level.exchange]["bid"] = float(level.price)
    
    for level in orderbook.asks[:20]:
        if level.exchange not in exchange_prices:
            exchange_prices[level.exchange] = {"bid": None, "ask": None}
        if exchange_prices[level.exchange]["ask"] is None:
            exchange_prices[level.exchange]["ask"] = float(level.price)
    
    return {
        "symbol": symbol,
        "best_bid": float(orderbook.best_bid),
        "best_ask": float(orderbook.best_ask),
        "spread": float(orderbook.spread),
        "prices_by_exchange": exchange_prices,
        "timestamp": orderbook.timestamp
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8051)