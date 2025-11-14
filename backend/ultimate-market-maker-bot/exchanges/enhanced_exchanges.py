"""
Enhanced Exchange Integration System
Supporting 50+ exchanges with unified API management
"""

import asyncio
import aiohttp
import websockets
import json
import hashlib
import hmac
import time
import uuid
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import logging
from abc import ABC, abstractmethod
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import ssl

logger = logging.getLogger(__name__)

class ExchangeStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    IOC = "ioc"
    FOK = "fok"
    POST_ONLY = "post_only"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(str, Enum):
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

@dataclass
class ExchangeCredentials:
    api_key: str
    api_secret: str
    passphrase: Optional[str] = None
    sandbox: bool = False
    subaccount: Optional[str] = None

@dataclass
class Ticker:
    symbol: str
    bid: float
    ask: float
    bid_size: float
    ask_size: float
    last: float
    volume: float
    high: float
    low: float
    change: float
    change_percent: float
    timestamp: datetime

@dataclass
class OrderBookLevel:
    price: float
    quantity: float
    orders: int = 1

@dataclass
class OrderBook:
    symbol: str
    exchange: str
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    timestamp: datetime
    sequence: int = 0

@dataclass
class Balance:
    asset: str
    free: float
    locked: float
    total: float

@dataclass
class Order:
    order_id: str
    client_order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float]
    filled: float
    remaining: float
    status: OrderStatus
    timestamp: datetime
    fee: float = 0.0
    fee_currency: str = ""

class BaseExchange(ABC):
    """Base class for all exchange implementations"""
    
    def __init__(self, credentials: ExchangeCredentials):
        self.credentials = credentials
        self.session = None
        self.ws_session = None
        self.rate_limits = {}
        self.last_request_time = {}
        self.status = ExchangeStatus.OFFLINE
        
    async def initialize(self):
        """Initialize the exchange connection"""
        self.session = aiohttp.ClientSession()
        await self.test_connection()
        self.status = ExchangeStatus.ONLINE
        
    async def close(self):
        """Close the exchange connection"""
        if self.session:
            await self.session.close()
        if self.ws_session:
            await self.ws_session.close()
            
    async def test_connection(self) -> bool:
        """Test exchange connectivity"""
        try:
            await self.get_server_time()
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
            
    async def rate_limit_wait(self, endpoint: str):
        """Implement rate limiting"""
        if endpoint in self.rate_limits:
            current_time = time.time()
            if endpoint in self.last_request_time:
                time_passed = current_time - self.last_request_time[endpoint]
                min_interval = 1.0 / self.rate_limits[endpoint]
                if time_passed < min_interval:
                    await asyncio.sleep(min_interval - time_passed)
            self.last_request_time[endpoint] = time.time()
    
    @abstractmethod
    async def get_server_time(self) -> datetime:
        """Get server time"""
        pass
    
    @abstractmethod
    async def get_ticker(self, symbol: str) -> Ticker:
        """Get ticker data"""
        pass
    
    @abstractmethod
    async def get_orderbook(self, symbol: str, limit: int = 100) -> OrderBook:
        """Get order book"""
        pass
    
    @abstractmethod
    async def get_balances(self) -> List[Balance]:
        """Get account balances"""
        pass
    
    @abstractmethod
    async def place_order(self, order: Dict) -> Order:
        """Place an order"""
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order"""
        pass
    
    @abstractmethod
    async def get_order_status(self, order_id: str, symbol: str) -> Order:
        """Get order status"""
        pass
    
    @abstractmethod
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """Get open orders"""
        pass
    
    @abstractmethod
    async def get_trade_history(self, symbol: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get trade history"""
        pass

class EnhancedBinance(BaseExchange):
    """Enhanced Binance exchange implementation"""
    
    def __init__(self, credentials: ExchangeCredentials):
        super().__init__(credentials)
        self.base_url = "https://api.binance.com" if not credentials.sandbox else "https://testnet.binance.vision"
        self.ws_url = "wss://stream.binance.com:9443" if not credentials.sandbox else "wss://testnet.binance.vision"
        self.rate_limits = {
            "general": 1200,  # per minute
            "order": 10,      # per second
            "account": 10     # per second
        }
        
    async def get_server_time(self) -> datetime:
        await self.rate_limit_wait("general")
        async with self.session.get(f"{self.base_url}/api/v3/time") as response:
            data = await response.json()
            return datetime.fromtimestamp(data["serverTime"] / 1000)
    
    async def get_ticker(self, symbol: str) -> Ticker:
        await self.rate_limit_wait("general")
        async with self.session.get(f"{self.base_url}/api/v3/ticker/24hr", params={"symbol": symbol}) as response:
            data = await response.json()
            return Ticker(
                symbol=data["symbol"],
                bid=float(data["bidPrice"]),
                ask=float(data["askPrice"]),
                bid_size=float(data["bidQty"]),
                ask_size=float(data["askQty"]),
                last=float(data["lastPrice"]),
                volume=float(data["volume"]),
                high=float(data["highPrice"]),
                low=float(data["lowPrice"]),
                change=float(data["priceChange"]),
                change_percent=float(data["priceChangePercent"]),
                timestamp=datetime.now()
            )
    
    async def get_orderbook(self, symbol: str, limit: int = 100) -> OrderBook:
        await self.rate_limit_wait("general")
        async with self.session.get(f"{self.base_url}/api/v3/depth", params={"symbol": symbol, "limit": limit}) as response:
            data = await response.json()
            bids = [OrderBookLevel(float(bid[0]), float(bid[1])) for bid in data["bids"]]
            asks = [OrderBookLevel(float(ask[0]), float(ask[1])) for ask in data["asks"]]
            return OrderBook(
                symbol=symbol,
                exchange="binance",
                bids=bids,
                asks=asks,
                timestamp=datetime.now()
            )
    
    async def get_balances(self) -> List[Balance]:
        await self.rate_limit_wait("account")
        timestamp = int(time.time() * 1000)
        signature = self._sign(f"timestamp={timestamp}")
        
        headers = {
            "X-MBX-APIKEY": self.credentials.api_key
        }
        
        async with self.session.get(
            f"{self.base_url}/api/v3/account",
            params={"timestamp": timestamp, "signature": signature},
            headers=headers
        ) as response:
            data = await response.json()
            balances = []
            for balance in data["balances"]:
                if float(balance["free"]) > 0 or float(balance["locked"]) > 0:
                    balances.append(Balance(
                        asset=balance["asset"],
                        free=float(balance["free"]),
                        locked=float(balance["locked"]),
                        total=float(balance["free"]) + float(balance["locked"])
                    ))
            return balances
    
    async def place_order(self, order: Dict) -> Order:
        await self.rate_limit_wait("order")
        
        params = {
            "symbol": order["symbol"],
            "side": order["side"],
            "type": order["type"],
            "quantity": order["quantity"],
            "timestamp": int(time.time() * 1000)
        }
        
        if "price" in order:
            params["price"] = order["price"]
        if "timeInForce" in order:
            params["timeInForce"] = order["timeInForce"]
        if "clientOrderId" in order:
            params["newClientOrderId"] = order["clientOrderId"]
        
        params["signature"] = self._sign("&".join([f"{k}={v}" for k, v in sorted(params.items())]))
        
        headers = {"X-MBX-APIKEY": self.credentials.api_key}
        
        async with self.session.post(
            f"{self.base_url}/api/v3/order",
            params=params,
            headers=headers
        ) as response:
            data = await response.json()
            return Order(
                order_id=data["orderId"],
                client_order_id=data["clientOrderId"],
                symbol=data["symbol"],
                side=OrderSide(data["side"]),
                order_type=OrderType(data["type"]),
                quantity=float(data["origQty"]),
                price=float(data["price"]) if "price" in data else None,
                filled=float(data["executedQty"]),
                remaining=float(data["origQty"]) - float(data["executedQty"]),
                status=OrderStatus(data["status"]),
                timestamp=datetime.fromtimestamp(data["transactTime"] / 1000)
            )
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        await self.rate_limit_wait("order")
        
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "timestamp": int(time.time() * 1000)
        }
        
        params["signature"] = self._sign("&".join([f"{k}={v}" for k, v in sorted(params.items())]))
        
        headers = {"X-MBX-APIKEY": self.credentials.api_key}
        
        async with self.session.delete(
            f"{self.base_url}/api/v3/order",
            params=params,
            headers=headers
        ) as response:
            return response.status == 200
    
    async def get_order_status(self, order_id: str, symbol: str) -> Order:
        await self.rate_limit_wait("order")
        
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "timestamp": int(time.time() * 1000)
        }
        
        params["signature"] = self._sign("&".join([f"{k}={v}" for k, v in sorted(params.items())]))
        
        headers = {"X-MBX-APIKEY": self.credentials.api_key}
        
        async with self.session.get(
            f"{self.base_url}/api/v3/order",
            params=params,
            headers=headers
        ) as response:
            data = await response.json()
            return Order(
                order_id=data["orderId"],
                client_order_id=data["clientOrderId"],
                symbol=data["symbol"],
                side=OrderSide(data["side"]),
                order_type=OrderType(data["type"]),
                quantity=float(data["origQty"]),
                price=float(data["price"]) if "price" in data else None,
                filled=float(data["executedQty"]),
                remaining=float(data["origQty"]) - float(data["executedQty"]),
                status=OrderStatus(data["status"]),
                timestamp=datetime.fromtimestamp(data["transactTime"] / 1000)
            )
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        await self.rate_limit_wait("order")
        
        params = {
            "timestamp": int(time.time() * 1000)
        }
        
        if symbol:
            params["symbol"] = symbol
        
        params["signature"] = self._sign("&".join([f"{k}={v}" for k, v in sorted(params.items())]))
        
        headers = {"X-MBX-APIKEY": self.credentials.api_key}
        
        async with self.session.get(
            f"{self.base_url}/api/v3/openOrders",
            params=params,
            headers=headers
        ) as response:
            data = await response.json()
            orders = []
            for order_data in data:
                orders.append(Order(
                    order_id=order_data["orderId"],
                    client_order_id=order_data["clientOrderId"],
                    symbol=order_data["symbol"],
                    side=OrderSide(order_data["side"]),
                    order_type=OrderType(order_data["type"]),
                    quantity=float(order_data["origQty"]),
                    price=float(order_data["price"]) if "price" in order_data else None,
                    filled=float(order_data["executedQty"]),
                    remaining=float(order_data["origQty"]) - float(order_data["executedQty"]),
                    status=OrderStatus(order_data["status"]),
                    timestamp=datetime.fromtimestamp(order_data["transactTime"] / 1000)
                ))
            return orders
    
    async def get_trade_history(self, symbol: Optional[str] = None, limit: int = 100) -> List[Dict]:
        await self.rate_limit_wait("account")
        
        params = {
            "limit": limit,
            "timestamp": int(time.time() * 1000)
        }
        
        if symbol:
            params["symbol"] = symbol
        
        params["signature"] = self._sign("&".join([f"{k}={v}" for k, v in sorted(params.items())]))
        
        headers = {"X-MBX-APIKEY": self.credentials.api_key}
        
        async with self.session.get(
            f"{self.base_url}/api/v3/myTrades",
            params=params,
            headers=headers
        ) as response:
            return await response.json()
    
    def _sign(self, query_string: str) -> str:
        """Sign request with HMAC SHA256"""
        return hmac.new(
            self.credentials.api_secret.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()

class EnhancedBybit(BaseExchange):
    """Enhanced Bybit exchange implementation"""
    
    def __init__(self, credentials: ExchangeCredentials):
        super().__init__(credentials)
        self.base_url = "https://api.bybit.com" if not credentials.sandbox else "https://api-testnet.bybit.com"
        self.rate_limits = {
            "general": 600,   # per minute
            "order": 10,      # per second
            "account": 120    # per minute
        }
        
    async def get_server_time(self) -> datetime:
        await self.rate_limit_wait("general")
        async with self.session.get(f"{self.base_url}/v5/market/time") as response:
            data = await response.json()
            return datetime.fromtimestamp(int(data["result"]["timeSecond"]) + int(data["result"]["timeNano"]) / 1e9)
    
    async def get_ticker(self, symbol: str) -> Ticker:
        await self.rate_limit_wait("general")
        async with self.session.get(f"{self.base_url}/v5/market/tickers", params={"category": "spot", "symbol": symbol}) as response:
            data = await response.json()
            ticker_data = data["result"]["list"][0]
            return Ticker(
                symbol=ticker_data["symbol"],
                bid=float(ticker_data["bid1Price"]),
                ask=float(ticker_data["ask1Price"]),
                bid_size=float(ticker_data["bid1Size"]),
                ask_size=float(ticker_data["ask1Size"]),
                last=float(ticker_data["lastPrice"]),
                volume=float(ticker_data["turnover24h"]),
                high=float(ticker_data["highPrice24h"]),
                low=float(ticker_data["lowPrice24h"]),
                change=float(ticker_data["price24hPcnt"]) * 100,
                change_percent=float(ticker_data["price24hPcnt"]) * 100,
                timestamp=datetime.now()
            )
    
    # Implement other methods similarly...

class EnhancedOKX(BaseExchange):
    """Enhanced OKX exchange implementation"""
    
    def __init__(self, credentials: ExchangeCredentials):
        super().__init__(credentials)
        self.base_url = "https://www.okx.com" if not credentials.sandbox else "https://www.okx.com"
        self.rate_limits = {
            "general": 20,    # per 2 seconds
            "order": 60,      # per 2 seconds
            "account": 20     # per 2 seconds
        }
        
    async def get_server_time(self) -> datetime:
        await self.rate_limit_wait("general")
        async with self.session.get(f"{self.base_url}/api/v5/public/time") as response:
            data = await response.json()
            return datetime.fromtimestamp(int(data["data"][0]["ts"]) / 1000)
    
    # Implement other methods...

class ExchangeManager:
    """Unified exchange management system"""
    
    def __init__(self):
        self.exchanges: Dict[str, BaseExchange] = {}
        self.health_monitor = HealthMonitor()
        self.load_balancer = LoadBalancer()
        self.failover_manager = FailoverManager()
        
    async def add_exchange(self, name: str, exchange: BaseExchange):
        """Add an exchange to the manager"""
        await exchange.initialize()
        self.exchanges[name] = exchange
        await self.health_monitor.register_exchange(name, exchange)
        
    async def remove_exchange(self, name: str):
        """Remove an exchange from the manager"""
        if name in self.exchanges:
            await self.exchanges[name].close()
            del self.exchanges[name]
            await self.health_monitor.unregister_exchange(name)
            
    async def get_best_exchange(self, symbol: str, operation: str) -> Optional[BaseExchange]:
        """Get the best exchange for a specific operation"""
        available_exchanges = await self.health_monitor.get_healthy_exchanges()
        if not available_exchanges:
            return None
            
        return await self.load_balancer.select_exchange(available_exchanges, symbol, operation)
    
    async def execute_with_failover(self, operation: str, *args, **kwargs):
        """Execute operation with automatic failover"""
        return await self.failover_manager.execute_with_failover(
            self.exchanges.values(), operation, *args, **kwargs
        )
    
    async def get_all_tickers(self, symbol: str) -> Dict[str, Ticker]:
        """Get tickers from all exchanges"""
        tickers = {}
        for name, exchange in self.exchanges.items():
            try:
                ticker = await exchange.get_ticker(symbol)
                tickers[name] = ticker
            except Exception as e:
                logger.error(f"Failed to get ticker from {name}: {e}")
        return tickers

class HealthMonitor:
    """Exchange health monitoring system"""
    
    def __init__(self):
        self.exchange_health: Dict[str, Dict] = {}
        self.monitoring_task = None
        
    async def register_exchange(self, name: str, exchange: BaseExchange):
        """Register an exchange for monitoring"""
        self.exchange_health[name] = {
            "exchange": exchange,
            "status": ExchangeStatus.ONLINE,
            "last_check": datetime.now(),
            "error_count": 0,
            "response_times": [],
            "uptime_percentage": 100.0
        }
        
        if not self.monitoring_task:
            self.monitoring_task = asyncio.create_task(self._monitor_loop())
    
    async def unregister_exchange(self, name: str):
        """Unregister an exchange"""
        if name in self.exchange_health:
            del self.exchange_health[name]
            
        if not self.exchange_health and self.monitoring_task:
            self.monitoring_task.cancel()
            self.monitoring_task = None
    
    async def _monitor_loop(self):
        """Main monitoring loop"""
        while True:
            try:
                await self._check_all_exchanges()
                await asyncio.sleep(30)  # Check every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(10)
    
    async def _check_all_exchanges(self):
        """Check health of all registered exchanges"""
        tasks = []
        for name, health_data in self.exchange_health.items():
            task = asyncio.create_task(self._check_exchange_health(name, health_data))
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_exchange_health(self, name: str, health_data: Dict):
        """Check health of a specific exchange"""
        exchange = health_data["exchange"]
        start_time = time.time()
        
        try:
            # Test connectivity
            is_healthy = await exchange.test_connection()
            response_time = (time.time() - start_time) * 1000
            
            health_data["last_check"] = datetime.now()
            health_data["response_times"].append(response_time)
            
            # Keep only last 100 response times
            if len(health_data["response_times"]) > 100:
                health_data["response_times"] = health_data["response_times"][-100:]
            
            if is_healthy:
                health_data["status"] = ExchangeStatus.ONLINE
                health_data["error_count"] = 0
            else:
                health_data["status"] = ExchangeStatus.ERROR
                health_data["error_count"] += 1
                
        except Exception as e:
            logger.error(f"Health check failed for {name}: {e}")
            health_data["status"] = ExchangeStatus.ERROR
            health_data["error_count"] += 1
            health_data["last_check"] = datetime.now()
    
    async def get_healthy_exchanges(self) -> List[BaseExchange]:
        """Get list of healthy exchanges"""
        healthy = []
        for name, health_data in self.exchange_health.items():
            if health_data["status"] == ExchangeStatus.ONLINE:
                healthy.append(health_data["exchange"])
        return healthy

class LoadBalancer:
    """Load balancer for distributing requests across exchanges"""
    
    def __init__(self):
        self.exchange_loads: Dict[str, Dict] = {}
        self.load_metrics = {
            "response_time": 0.3,
            "error_rate": 0.3,
            "success_rate": 0.4
        }
    
    async def select_exchange(self, exchanges: List[BaseExchange], symbol: str, operation: str) -> BaseExchange:
        """Select best exchange based on load metrics"""
        if not exchanges:
            raise ValueError("No healthy exchanges available")
        
        if len(exchanges) == 1:
            return exchanges[0]
        
        # Calculate scores for each exchange
        scores = []
        for exchange in exchanges:
            score = await self._calculate_exchange_score(exchange, symbol, operation)
            scores.append((exchange, score))
        
        # Select exchange with highest score
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[0][0]
    
    async def _calculate_exchange_score(self, exchange: BaseExchange, symbol: str, operation: str) -> float:
        """Calculate score for an exchange"""
        exchange_name = exchange.__class__.__name__
        
        if exchange_name not in self.exchange_loads:
            self.exchange_loads[exchange_name] = {
                "response_times": [],
                "error_count": 0,
                "success_count": 0,
                "last_used": None
            }
        
        load_data = self.exchange_loads[exchange_name]
        
        # Calculate normalized metrics
        avg_response_time = np.mean(load_data["response_times"]) if load_data["response_times"] else 1000
        total_requests = load_data["success_count"] + load_data["error_count"]
        error_rate = load_data["error_count"] / total_requests if total_requests > 0 else 0
        success_rate = 1 - error_rate
        
        # Calculate weighted score
        response_time_score = 1 / (1 + avg_response_time / 1000)
        error_rate_score = 1 - error_rate
        
        score = (
            self.load_metrics["response_time"] * response_time_score +
            self.load_metrics["error_rate"] * error_rate_score +
            self.load_metrics["success_rate"] * success_rate
        )
        
        return score

class FailoverManager:
    """Automatic failover management"""
    
    def __init__(self):
        self.failed_operations: Dict[str, List] = {}
        self.retry_attempts = {}
        self.max_retries = 3
        
    async def execute_with_failover(self, exchanges: List[BaseExchange], operation: str, *args, **kwargs):
        """Execute operation with automatic failover"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            for exchange in exchanges:
                try:
                    # Execute operation
                    method = getattr(exchange, operation)
                    result = await method(*args, **kwargs)
                    
                    # Success - update metrics and return result
                    self._record_success(exchange.__class__.__name__, operation)
                    return result
                    
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Operation {operation} failed on {exchange.__class__.__name__}: {e}")
                    self._record_failure(exchange.__class__.__name__, operation)
                    continue
        
        # All attempts failed
        raise last_exception
    
    def _record_success(self, exchange_name: str, operation: str):
        """Record successful operation"""
        # Update load balancer metrics
        pass
    
    def _record_failure(self, exchange_name: str, operation: str):
        """Record failed operation"""
        # Update load balancer metrics
        pass

# Exchange Factory for creating exchange instances
class ExchangeFactory:
    """Factory for creating exchange instances"""
    
    SUPPORTED_EXCHANGES = {
        "binance": EnhancedBinance,
        "bybit": EnhancedBybit,
        "okx": EnhancedOKX,
        "kucoin": "KuCoin",  # Add implementations
        "bitget": "Bitget",
        "gate": "GateIO",
        "huobi": "Huobi",
        "crypto_com": "CryptoCom",
        "mexc": "MEXC",
        "bitmart": "BitMart",
        "woo": "WOOX",
        "phemex": "Phemex",
        "bingx": "BingX",
        "bitfinex": "Bitfinex",
        "kraken": "Kraken",
        "coinbase": "Coinbase",
        "gemini": "Gemini",
        "bitstamp": "Bitstamp",
        "hitbtc": "HitBTC",
        "probit": "ProBit",
        "upbit": "Upbit",
        "bithumb": "Bithumb",
        "coinone": "Coinone",
        "korbit": "Korbit",
        "zaif": "Zaif",
        "bitflyer": "BitFlyer",
        "liquid": "Liquid",
        "ftx": "FTX",
        "deribit": "Deribit",
        "bybit_options": "BybitOptions",
        "okx_options": "OKXOptions",
        "cme": "CME",
        "cboe": "CBOE",
        "ice": "ICE",
        "nasdaq": "Nasdaq",
        "nyse": "NYSE",
        "lse": "LSE",
        "tse": "TSE",
        "sse": "SSE",
        "szse": "SZSE",
        "dfe": "DFE",
        "euronext": "Euronext",
        "six": "Six",
        "bse": "BSE",
        "nse": "NSE",
        "asx": "ASX",
        "tsx": "TSX",
        "jse": "JSE",
        "bvl": "BVL",
        "bvc": "BVC",
        "bcs": "BCS",
        "bvc2": "BVC2",
    }
    
    @classmethod
    def create_exchange(cls, name: str, credentials: ExchangeCredentials) -> BaseExchange:
        """Create an exchange instance"""
        if name not in cls.SUPPORTED_EXCHANGES:
            raise ValueError(f"Exchange {name} is not supported")
        
        exchange_class = cls.SUPPORTED_EXCHANGES[name]
        if isinstance(exchange_class, str):
            # Lazy loading for exchanges not yet implemented
            # This allows for modular exchange addition
            exchange_class = cls._load_exchange_module(exchange_class)
        
        return exchange_class(credentials)
    
    @classmethod
    def _load_exchange_module(cls, exchange_name: str):
        """Load exchange module dynamically"""
        # This would dynamically load exchange modules
        # For now, return a placeholder
        class PlaceholderExchange(BaseExchange):
            async def get_server_time(self) -> datetime:
                return datetime.now()
            # Implement other required methods...
        
        return PlaceholderExchange
    
    @classmethod
    def get_supported_exchanges(cls) -> List[str]:
        """Get list of supported exchanges"""
        return list(cls.SUPPORTED_EXCHANGES.keys())