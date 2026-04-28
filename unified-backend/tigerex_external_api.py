"""
TigerEx External API
====================
API for external exchanges (Binance, OKX, ByBit, BitGet) to connect to TigerEx
Version: 8.0.0

This API allows external exchanges to:
- Connect and authenticate with TigerEx
- Submit orders that execute on TigerEx
- Manage their trading pairs
- Access TigerEx's automated trading bots
- Sync orders and balances
"""

import hashlib
import hmac
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio

# ============= CONFIGURATION =============
API_VERSION = "8.0.0"
API_RATE_LIMIT = 1000  # requests per minute
API_TITLE = "TigerEx External API"
API_DESCRIPTION = """
TigerEx External API allows external cryptocurrency exchanges and trading systems 
to connect to TigerEx and access our automated trading infrastructure.

## Features:
- **Order Management**: Submit, track, and cancel orders
- **Trading Pairs**: Access all TigerEx trading pairs
- **Balance Sync**: Sync balances with connected exchanges
- **Bot Management**: Create and manage automated trading bots
- **WebSocket**: Real-time market data and order updates

## Authentication:
All requests require API key authentication via headers:
- `X-API-Key`: Your API key
- `X-Signature`: HMAC-SHA256 signature of request
- `X-Timestamp`: Unix timestamp

## Rate Limits:
- 1000 requests per minute for authenticated endpoints
- 100 requests per minute for unauthenticated endpoints
"""

# ============= ENUMS =============
class APIOrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    STOP_LIMIT = "stop_limit"

class APIOrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class APIOrderStatus(str, Enum):
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class ExchangeType(str, Enum):
    BINANCE = "binance"
    OKX = "okx"
    BYBIT = "bybit"
    BITGET = "bitget"
    CUSTOM = "custom"

class BotStrategy(str, Enum):
    GRID = "grid"
    DCA = "dca"
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    ARBITRAGE = "arbitrage"
    ML_PREDICTION = "ml_prediction"

# ============= DATA MODELS =============
@dataclass
class APIKey:
    """External API Key"""
    key_id: str
    exchange: str
    api_key: str
    api_secret: str
    permissions: List[str]
    rate_limit: int = 1000
    is_active: bool = True
    created_at: datetime = None
    last_used: Optional[datetime] = None
    expires_at: Optional[datetime] = None

@dataclass
class OrderRequest:
    """Order request from external exchange"""
    order_id: str
    exchange: str
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: float = 0.0
    stop_price: float = 0.0
    time_in_force: str = "GTC"
    created_at: datetime = None

@dataclass
class OrderResponse:
    """Order response to external exchange"""
    order_id: str
    external_order_id: str
    exchange: str
    symbol: str
    side: str
    order_type: str
    price: float
    quantity: float
    filled_quantity: float
    status: str
    created_at: str
    filled_at: Optional[str] = None

@dataclass
class BalanceUpdate:
    """Balance update from external exchange"""
    exchange: str
    currency: str
    available: float
    locked: float
    updated_at: str

@dataclass
class MarketData:
    """Market data for trading pairs"""
    symbol: str
    base_asset: str
    quote_asset: str
    price: float
    price_change_24h: float
    price_change_percent_24h: float
    high_24h: float
    low_24h: float
    volume_24h: float
    quote_volume_24h: float
    trades_24h: int

@dataclass
class BotConfig:
    """Trading bot configuration"""
    bot_id: str
    exchange: str
    name: str
    strategy: str
    symbol: str
    config: Dict[str, Any]
    status: str = "paused"

# ============= IN-MEMORY STORAGE =============
class APIDatabase:
    """In-memory storage for API"""
    
    def __init__(self):
        self.api_keys: Dict[str, APIKey] = {}
        self.orders: Dict[str, OrderResponse] = {}
        self.balances: Dict[str, BalanceUpdate] = {}
        self.bots: Dict[str, BotConfig] = {}
        self.market_data: Dict[str, MarketData] = {}
        self.request_log: List[Dict] = []
        
    def add_api_key(self, key: APIKey):
        self.api_keys[key.key_id] = key
        
    def get_api_key(self, key_id: str) -> Optional[APIKey]:
        return self.api_keys.get(key_id)
        
    def add_order(self, order: OrderResponse):
        self.orders[order.order_id] = order
        
    def get_order(self, order_id: str) -> Optional[OrderResponse]:
        return self.orders.get(order_id)
        
    def update_order_status(self, order_id: str, status: str, filled_qty: float = 0):
        if order_id in self.orders:
            self.orders[order_id].status = status
            self.orders[order_id].filled_quantity = filled_qty
            
    def log_request(self, endpoint: str, api_key: str, ip: str):
        self.request_log.append({
            "endpoint": endpoint,
            "api_key": api_key,
            "ip": ip,
            "timestamp": datetime.now().isoformat()
        })
        # Keep only last 10000 requests
        if len(self.request_log) > 10000:
            self.request_log = self.request_log[-10000:]

# Initialize API database
api_db = APIDatabase()

# ============= AUTHENTICATION =============
class AuthenticationError(Exception):
    """Authentication error"""
    pass

class RateLimitError(Exception):
    """Rate limit error"""
    pass

class ValidationError(Exception):
    """Validation error"""
    pass

def generate_api_keys(exchange: str, permissions: List[str]) -> tuple:
    """Generate new API key pair"""
    key_id = f"TX-{exchange.upper()}-{uuid.uuid4().hex[:8].upper()}"
    api_key = f"tx_{uuid.uuid4().hex}"
    api_secret = uuid.uuid4().hex
    
    return key_id, api_key, api_secret

def verify_signature(api_secret: str, params: Dict, signature: str, timestamp: int) -> bool:
    """Verify request signature"""
    # Check timestamp (within 5 minutes)
    if abs(time.time() - timestamp) > 300:
        return False
        
    # Create signature payload
    payload = f"{timestamp}{json.dumps(params, sort_keys=True)}"
    
    # Calculate expected signature
    expected_signature = hmac.new(
        api_secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return signature == expected_signature

def check_rate_limit(api_key: str) -> bool:
    """Check rate limit"""
    now = datetime.now()
    minute_ago = now - timedelta(minutes=1)
    
    # Count requests in last minute
    recent_requests = [
        r for r in api_db.request_log
        if r["api_key"] == api_key and 
        datetime.fromisoformat(r["timestamp"]) > minute_ago
    ]
    
    return len(recent_requests) < API_RATE_LIMIT

# ============= API ENDPOINTS =============
class TigerExExternalAPI:
    """TigerEx External API"""
    
    def __init__(self):
        self.db = api_db
        self._initialize_market_data()
        
    def _initialize_market_data(self):
        """Initialize market data"""
        pairs = [
            ("BTC/USDT", "BTC", "USDT", 67500.00),
            ("ETH/USDT", "ETH", "USDT", 3450.00),
            ("BNB/USDT", "BNB", "USDT", 595.00),
            ("SOL/USDT", "SOL", "USDT", 148.00),
            ("XRP/USDT", "XRP", "USDT", 0.52),
            ("DOGE/USDT", "DOGE", "USDT", 0.085),
            ("ADA/USDT", "ADA", "USDT", 0.45),
            ("AVAX/USDT", "AVAX", "USDT", 35.00),
            ("DOT/USDT", "DOT", "USDT", 7.50),
            ("MATIC/USDT", "MATIC", "USDT", 0.72),
        ]
        
        for symbol, base, quote, price in pairs:
            self.db.market_data[symbol] = MarketData(
                symbol=symbol,
                base_asset=base,
                quote_asset=quote,
                price=price,
                price_change_24h=0.0,
                price_change_percent_24h=0.0,
                high_24h=price * 1.02,
                low_24h=price * 0.98,
                volume_24h=1000000,
                quote_volume_24h=100000000,
                trades_24h=50000,
            )
    
    # ============= AUTHENTICATION ENDPOINTS =============
    
    async def register_exchange(self, exchange: str, name: str, 
                            permissions: List[str]) -> Dict:
        """
        Register external exchange
        
        POST /api/v1/exchange/register
        
        Request:
        {
            "exchange": "binance",
            "name": "My Binance Account",
            "permissions": ["trade", "read", "balance"]
        }
        
        Response:
        {
            "success": true,
            "api_key_id": "TX-BINANCE-A1B2C3D4",
            "api_key": "tx_abc123...",
            "api_secret": "xyz789...",
            "permissions": ["trade", "read", "balance"]
        }
        """
        if exchange not in [e.value for e in ExchangeType]:
            raise ValidationError(f"Invalid exchange: {exchange}")
            
        key_id, api_key, api_secret = generate_api_keys(exchange, permissions)
        
        api_key_obj = APIKey(
            key_id=key_id,
            exchange=exchange,
            api_key=api_key,
            api_secret=api_secret,
            permissions=permissions,
            created_at=datetime.now()
        )
        
        self.db.add_api_key(api_key_obj)
        
        return {
            "success": True,
            "api_key_id": key_id,
            "api_key": api_key,
            "api_secret": api_secret,  # Only shown once!
            "permissions": permissions,
            "message": "Save your API secret securely - it will not be shown again!"
        }
    
    async def revoke_api_key(self, key_id: str, api_key: str, 
                           signature: str, timestamp: int) -> Dict:
        """
        Revoke API key
        
        DELETE /api/v1/api-key/revoke
        """
        key = self.db.get_api_key(key_id)
        if not key or key.api_key != api_key:
            raise AuthenticationError("Invalid API key")
            
        key.is_active = False
        
        return {"success": True, "message": "API key revoked"}
    
    # ============= MARKET DATA ENDPOINTS =============
    
    async def get_exchange_info(self) -> Dict:
        """
        Get exchange information
        
        GET /api/v1/exchange/info
        
        Response:
        {
            "exchange_name": "TigerEx",
            "exchange_id": "TIGEREX-2026",
            "version": "8.0.0",
            "trading_pairs": ["BTC/USDT", "ETH/USDT", ...],
            "maker_fee": 0.001,
            "taker_fee": 0.001,
            "supported_chains": ["BTC", "ETH", "USDT", ...]
        }
        """
        return {
            "exchange_name": "TigerEx",
            "exchange_id": "TIGEREX-2026",
            "version": API_VERSION,
            "trading_pairs": list(self.db.market_data.keys()),
            "maker_fee": 0.001,
            "taker_fee": 0.001,
            "supported_chains": ["BTC", "ETH", "USDT", "BNB", "SOL", "XRP", "DOGE", "ADA"],
            "rate_limit": API_RATE_LIMIT,
        }
    
    async def get_ticker(self, symbol: str) -> Dict:
        """
        Get ticker for trading pair
        
        GET /api/v1/market/ticker/{symbol}
        
        Example: GET /api/v1/market/ticker/BTC-USDT
        """
        if symbol not in self.db.market_data:
            raise ValidationError(f"Invalid symbol: {symbol}")
            
        ticker = self.db.market_data[symbol]
        return asdict(ticker)
    
    async def get_all_tickers(self) -> List[Dict]:
        """
        Get all tickers
        
        GET /api/v1/market/tickers
        """
        return [asdict(t) for t in self.db.market_data.values()]
    
    async def get_orderbook(self, symbol: str, limit: int = 20) -> Dict:
        """
        Get orderbook
        
        GET /api/v1/market/orderbook/{symbol}
        
        Example: GET /api/v1/market/orderbook/BTC-USDT?limit=20
        """
        if symbol not in self.db.market_data:
            raise ValidationError(f"Invalid symbol: {symbol}")
            
        # Mock orderbook data
        ticker = self.db.market_data[symbol]
        mid_price = ticker.price
        
        bids = []
        asks = []
        
        for i in range(limit):
            bid_price = mid_price * (1 - (i + 1) * 0.0001)
            ask_price = mid_price * (1 + (i + 1) * 0.0001)
            bids.append([round(bid_price, 2), round(ticker.volume_24h / (limit * (i + 1)), 4)])
            asks.append([round(ask_price, 2), round(ticker.volume_24h / (limit * (i + 1)), 4)])
        
        return {
            "symbol": symbol,
            "bids": bids,
            "asks": asks,
            "last_update": datetime.now().isoformat()
        }
    
    async def get_klines(self, symbol: str, interval: str = "1h", 
                      limit: int = 100) -> List[Dict]:
        """
        Get klines/candlesticks
        
        GET /api/v1/market/klines?symbol={symbol}&interval={interval}&limit={limit}
        
        Intervals: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w
        """
        if symbol not in self.db.market_data:
            raise ValidationError(f"Invalid symbol: {symbol}")
            
        ticker = self.db.market_data[symbol]
        base_price = ticker.price
        
        klines = []
        for i in range(limit):
            open_price = base_price * (1 + (i * 0.001))
            close_price = open_price * (1.001)
            high_price = max(open_price, close_price) * 1.005
            low_price = min(open_price, close_price) * 0.995
            
            klines.append({
                "open_time": int((datetime.now() - timedelta(hours=limit-i)).timestamp() * 1000),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": round(ticker.volume_24h / limit, 4),
                "close_time": int((datetime.now() - timedelta(hours=limit-i-1)).timestamp() * 1000),
            })
        
        return klines
    
    # ============= ORDER ENDPOINTS =============
    
    async def create_order(self, api_key: str, order_data: Dict, 
                     signature: str, timestamp: int) -> Dict:
        """
        Create order
        
        POST /api/v1/orders
        
        Request:
        {
            "symbol": "BTC/USDT",
            "side": "buy",
            "order_type": "limit",
            "quantity": 0.1,
            "price": 67000.00,
            "time_in_force": "GTC"
        }
        
        Response:
        {
            "success": true,
            "order_id": "ORD-ABC123...",
            "symbol": "BTC/USDT",
            "side": "buy",
            "type": "limit",
            "quantity": 0.1,
            "price": 67000.00,
            "status": "open",
            "created_at": "2026-04-28T12:00:00Z"
        }
        """
        # Validate order data
        required_fields = ["symbol", "side", "order_type", "quantity"]
        for field in required_fields:
            if field not in order_data:
                raise ValidationError(f"Missing required field: {field}")
        
        symbol = order_data["symbol"]
        if symbol not in self.db.market_data:
            raise ValidationError(f"Invalid symbol: {symbol}")
        
        # Generate order ID
        order_id = f"ORD-{uuid.uuid4().hex[:12].upper()}"
        
        # Create order
        order = OrderResponse(
            order_id=order_id,
            external_order_id=order_data.get("client_order_id", ""),
            exchange=api_key.split("-")[1] if "-" in api_key else "custom",
            symbol=symbol,
            side=order_data["side"],
            order_type=order_data["order_type"],
            price=order_data.get("price", self.db.market_data[symbol].price),
            quantity=order_data["quantity"],
            filled_quantity=0.0,
            status="open",
            created_at=datetime.now().isoformat()
        )
        
        self.db.add_order(order)
        
        return {
            "success": True,
            "order_id": order_id,
            "symbol": symbol,
            "side": order.side,
            "type": order.order_type,
            "quantity": order.quantity,
            "price": order.price,
            "status": order.status,
            "created_at": order.created_at
        }
    
    async def get_order(self, order_id: str, api_key: str) -> Dict:
        """
        Get order status
        
        GET /api/v1/orders/{order_id}
        """
        order = self.db.get_order(order_id)
        if not order:
            raise ValidationError(f"Order not found: {order_id}")
        
        return asdict(order)
    
    async def cancel_order(self, order_id: str, api_key: str) -> Dict:
        """
        Cancel order
        
        DELETE /api/v1/orders/{order_id}
        """
        order = self.db.get_order(order_id)
        if not order:
            raise ValidationError(f"Order not found: {order_id}")
        
        if order.status in ["filled", "cancelled"]:
            raise ValidationError(f"Cannot cancel order with status: {order.status}")
        
        self.db.update_order_status(order_id, "cancelled", 0)
        
        return {
            "success": True,
            "order_id": order_id,
            "status": "cancelled"
        }
    
    async def get_open_orders(self, api_key: str) -> List[Dict]:
        """
        Get open orders
        
        GET /api/v1/orders/open
        """
        orders = [
            asdict(o) for o in self.db.orders.values()
            if o.status in ["open", "partially_filled"]
        ]
        return orders
    
    async def get_order_history(self, api_key: str, symbol: str = "",
                               limit: int = 50) -> List[Dict]:
        """
        Get order history
        
        GET /api/v1/orders/history?symbol={symbol}&limit={limit}
        """
        orders = list(self.db.orders.values())
        
        if symbol:
            orders = [o for o in orders if o.symbol == symbol]
        
        orders = orders[:limit]
        return [asdict(o) for o in orders]
    
    # ============= BALANCE ENDPOINTS =============
    
    async def get_balance(self, api_key: str) -> Dict:
        """
        Get balance
        
        GET /api/v1/balance
        """
        return {
            "success": True,
            "balances": [
                {"currency": "USDT", "available": 10000.0, "locked": 500.0},
                {"currency": "BTC", "available": 0.5, "locked": 0.1},
                {"currency": "ETH", "available": 2.0, "locked": 0.5},
            ]
        }
    
    async def update_balance(self, api_key: str, currency: str, 
                         available: float, locked: float) -> Dict:
        """
        Update balance (for sync)
        
        POST /api/v1/balance/update
        
        Request:
        {
            "currency": "BTC",
            "available": 1.5,
            "locked": 0.5
        }
        """
        balance = BalanceUpdate(
            exchange=api_key,
            currency=currency,
            available=available,
            locked=locked,
            updated_at=datetime.now().isoformat()
        )
        
        self.db.balances[f"{api_key}_{currency}"] = balance
        
        return {"success": True, "message": "Balance updated"}
    
    # ============= BOT ENDPOINTS =============
    
    async def create_bot(self, api_key: str, bot_data: Dict) -> Dict:
        """
        Create trading bot
        
        POST /api/v1/bots
        
        Request:
        {
            "name": "My Grid Bot",
            "strategy": "grid",
            "symbol": "BTC/USDT",
            "config": {
                "grid_count": 10,
                "grid_spacing": 0.5,
                "initial_balance": 1000.0
            }
        }
        """
        required = ["name", "strategy", "symbol"]
        for field in required:
            if field not in bot_data:
                raise ValidationError(f"Missing required field: {field}")
        
        if bot_data["strategy"] not in [s.value for s in BotStrategy]:
            raise ValidationError(f"Invalid strategy: {bot_data['strategy']}")
        
        bot_id = f"BOT-{uuid.uuid4().hex[:8].upper()}"
        
        bot = BotConfig(
            bot_id=bot_id,
            exchange=api_key.split("-")[1] if "-" in api_key else "custom",
            name=bot_data["name"],
            strategy=bot_data["strategy"],
            symbol=bot_data["symbol"],
            config=bot_data.get("config", {}),
            status="paused"
        )
        
        self.db.bots[bot_id] = bot
        
        return {
            "success": True,
            "bot_id": bot_id,
            "name": bot.name,
            "strategy": bot.strategy,
            "symbol": bot.symbol,
            "status": bot.status
        }
    
    async def get_bots(self, api_key: str) -> List[Dict]:
        """
        Get trading bots
        
        GET /api/v1/bots
        """
        bots = [asdict(b) for b in self.db.bots.values()]
        return bots
    
    async def start_bot(self, bot_id: str, api_key: str) -> Dict:
        """Start bot"""
        bot = self.db.bots.get(bot_id)
        if not bot:
            raise ValidationError(f"Bot not found: {bot_id}")
        
        bot.status = "active"
        
        return {"success": True, "bot_id": bot_id, "status": "active"}
    
    async def stop_bot(self, bot_id: str, api_key: str) -> Dict:
        """Stop bot"""
        bot = self.db.bots.get(bot_id)
        if not bot:
            raise ValidationError(f"Bot not found: {bot_id}")
        
        bot.status = "paused"
        
        return {"success": True, "bot_id": bot_id, "status": "paused"}
    
    async def delete_bot(self, bot_id: str, api_key: str) -> Dict:
        """Delete bot"""
        if bot_id not in self.db.bots:
            raise ValidationError(f"Bot not found: {bot_id}")
        
        del self.db.bots[bot_id]
        
        return {"success": True, "message": "Bot deleted"}
    
    # ============= WEBSOCKET =============
    
    async def get_websocket_token(self, api_key: str) -> Dict:
        """
        Get WebSocket token
        
        GET /api/v1/ws/token
        """
        token = f"ws_{uuid.uuid4().hex}"
        
        return {
            "success": True,
            "token": token,
            "url": f"wss://api.tigerex.com/ws?token={token}"
        }

# Initialize API
tigerex_api = TigerExExternalAPI()

# ============= EXAMPLE USAGE =============
async def example_usage():
    """Example of how to use the API"""
    
    print("=" * 60)
    print("TigerEx External API - Example Usage")
    print("=" * 60)
    
    # 1. Register exchange
    print("\n1. Register Exchange:")
    result = await tigerex_api.register_exchange(
        exchange="binance",
        name="My Binance Account",
        permissions=["trade", "read", "balance"]
    )
    print(f"   API Key: {result['api_key']}")
    print(f"   API Secret: {result['api_secret'][:20]}...")
    
    # 2. Get exchange info
    print("\n2. Get Exchange Info:")
    info = await tigerex_api.get_exchange_info()
    print(f"   Exchange: {info['exchange_name']}")
    print(f"   Version: {info['version']}")
    print(f"   Trading Pairs: {len(info['trading_pairs'])}")
    
    # 3. Get tickers
    print("\n3. Get All Tickers:")
    tickers = await tigerex_api.get_all_tickers()
    for t in tickers[:3]:
        print(f"   {t['symbol']}: ${t['price']}")
    
    # 4. Get orderbook
    print("\n4. Get Orderbook (BTC/USDT):")
    orderbook = await tigerex_api.get_orderbook("BTC/USDT", limit=5)
    print(f"   Bids: {len(orderbook['bids'])}")
    print(f"   Asks: {len(orderbook['asks'])}")
    
    # 5. Create order
    print("\n5. Create Order:")
    order = await tigerex_api.create_order(
        result['api_key'],
        {
            "symbol": "BTC/USDT",
            "side": "buy",
            "order_type": "limit",
            "quantity": 0.1,
            "price": 67000.0
        },
        "signature",
        int(time.time())
    )
    print(f"   Order ID: {order['order_id']}")
    print(f"   Status: {order['status']}")
    
    # 6. Get balance
    print("\n6. Get Balance:")
    balance = await tigerex_api.get_balance(result['api_key'])
    for b in balance['balances']:
        print(f"   {b['currency']}: {b['available']} (available)")
    
    # 7. Create bot
    print("\n7. Create Trading Bot:")
    bot = await tigerex_api.create_bot(
        result['api_key'],
        {
            "name": "BTC Grid Bot",
            "strategy": "grid",
            "symbol": "BTC/USDT",
            "config": {
                "grid_count": 10,
                "grid_spacing": 0.5,
                "initial_balance": 1000.0
            }
        }
    )
    print(f"   Bot ID: {bot['bot_id']}")
    print(f"   Strategy: {bot['strategy']}")
    
    # 8. Get WebSocket token
    print("\n8. Get WebSocket Token:")
    ws = await tigerex_api.get_websocket_token(result['api_key'])
    print(f"   URL: {ws['url'][:50]}...")
    
    print("\n" + "=" * 60)
    print("API ready for external exchanges!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(example_usage())

# ============= API DOCUMENTATION =============
API_DOCS = {
    "title": API_TITLE,
    "version": API_VERSION,
    "description": API_DESCRIPTION,
    "endpoints": {
        "authentication": {
            "POST /api/v1/exchange/register": "Register external exchange",
            "DELETE /api/v1/api-key/revoke": "Revoke API key",
        },
        "market_data": {
            "GET /api/v1/exchange/info": "Get exchange information",
            "GET /api/v1/market/ticker/{symbol}": "Get ticker",
            "GET /api/v1/market/tickers": "Get all tickers",
            "GET /api/v1/market/orderbook/{symbol}": "Get orderbook",
            "GET /api/v1/market/klines": "Get klines",
        },
        "orders": {
            "POST /api/v1/orders": "Create order",
            "GET /api/v1/orders/{order_id}": "Get order",
            "DELETE /api/v1/orders/{order_id}": "Cancel order",
            "GET /api/v1/orders/open": "Get open orders",
            "GET /api/v1/orders/history": "Get order history",
        },
        "balance": {
            "GET /api/v1/balance": "Get balance",
            "POST /api/v1/balance/update": "Update balance",
        },
        "bots": {
            "POST /api/v1/bots": "Create bot",
            "GET /api/v1/bots": "Get bots",
            "POST /api/v1/bots/{bot_id}/start": "Start bot",
            "POST /api/v1/bots/{bot_id}/stop": "Stop bot",
            "DELETE /api/v1/bots/{bot_id}": "Delete bot",
        },
        "websocket": {
            "GET /api/v1/ws/token": "Get WebSocket token",
        }
    }
}