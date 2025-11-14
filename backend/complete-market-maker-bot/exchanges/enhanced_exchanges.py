"""
Enhanced Exchange Integrations for Market Maker Bot
Support for all major crypto exchanges with advanced features
"""

import asyncio
import aiohttp
import json
import logging
import hmac
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import ccxt.async_support as ccxt
from decimal import Decimal
import websockets
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExchangeType(Enum):
    BINANCE = "binance"
    COINBASEPRO = "coinbasepro"
    KRAKEN = "kraken"
    HUOBI = "huobi"
    BYBIT = "bybit"
    KUCOIN = "kucoin"
    OKX = "okx"
    GATEIO = "gateio"

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    CANCELED = "canceled"
    REJECTED = "rejected"

@dataclass
class OrderBookEntry:
    price: float
    quantity: float
    timestamp: datetime

@dataclass
class Order:
    id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.OPEN
    filled_quantity: float = 0.0
    remaining_quantity: float = 0.0
    average_price: Optional[float] = None
    timestamp: datetime = None
    exchange: str = None
    fee: Optional[float] = None

@dataclass
class Ticker:
    symbol: str
    bid: float
    ask: float
    bid_volume: float
    ask_volume: float
    last_price: float
    volume_24h: float
    high_24h: float
    low_24h: float
    timestamp: datetime

class EnhancedExchange:
    def __init__(self, exchange_type: ExchangeType, config: Dict[str, Any]):
        self.exchange_type = exchange_type
        self.config = config
        self.exchange = None
        self.ws_connection = None
        self.orderbooks = {}
        self.tickers = {}
        self.fees = {}
        self.rate_limits = {}
        self.last_request_time = {}
        
    async def initialize(self):
        """Initialize exchange connection and authenticate"""
        try:
            if self.exchange_type == ExchangeType.BINANCE:
                self.exchange = ccxt.binance({
                    'apiKey': self.config.get('api_key'),
                    'secret': self.config.get('secret'),
                    'sandbox': self.config.get('sandbox', False),
                    'enableRateLimit': True,
                    'options': {
                        'defaultType': 'spot',
                        'adjustForTimeDifference': True,
                    }
                })
            elif self.exchange_type == ExchangeType.COINBASEPRO:
                self.exchange = ccxt.coinbasepro({
                    'apiKey': self.config.get('api_key'),
                    'secret': self.config.get('secret'),
                    'passphrase': self.config.get('passphrase'),
                    'sandbox': self.config.get('sandbox', False),
                    'enableRateLimit': True,
                })
            elif self.exchange_type == ExchangeType.KRAKEN:
                self.exchange = ccxt.kraken({
                    'apiKey': self.config.get('api_key'),
                    'secret': self.config.get('secret'),
                    'sandbox': self.config.get('sandbox', False),
                    'enableRateLimit': True,
                })
            elif self.exchange_type == ExchangeType.HUOBI:
                self.exchange = ccxt.huobi({
                    'apiKey': self.config.get('api_key'),
                    'secret': self.config.get('secret'),
                    'sandbox': self.config.get('sandbox', False),
                    'enableRateLimit': True,
                })
            elif self.exchange_type == ExchangeType.BYBIT:
                self.exchange = ccxt.bybit({
                    'apiKey': self.config.get('api_key'),
                    'secret': self.config.get('secret'),
                    'sandbox': self.config.get('sandbox', False),
                    'enableRateLimit': True,
                })
            elif self.exchange_type == ExchangeType.KUCOIN:
                self.exchange = ccxt.kucoin({
                    'apiKey': self.config.get('api_key'),
                    'secret': self.config.get('secret'),
                    'passphrase': self.config.get('passphrase'),
                    'sandbox': self.config.get('sandbox', False),
                    'enableRateLimit': True,
                })
            elif self.exchange_type == ExchangeType.OKX:
                self.exchange = ccxt.okx({
                    'apiKey': self.config.get('api_key'),
                    'secret': self.config.get('secret'),
                    'password': self.config.get('password'),
                    'sandbox': self.config.get('sandbox', False),
                    'enableRateLimit': True,
                })
            elif self.exchange_type == ExchangeType.GATEIO:
                self.exchange = ccxt.gateio({
                    'apiKey': self.config.get('api_key'),
                    'secret': self.config.get('secret'),
                    'sandbox': self.config.get('sandbox', False),
                    'enableRateLimit': True,
                })
            
            # Load markets
            await self.exchange.load_markets()
            
            # Get trading fees
            await self.load_trading_fees()
            
            # Start websocket connection
            await self.start_websocket()
            
            logger.info(f"Initialized {self.exchange_type.value} exchange")
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.exchange_type.value}: {e}")
            raise
    
    async def load_trading_fees(self):
        """Load trading fees for the exchange"""
        try:
            fees = await self.exchange.fetch_trading_fees()
            self.fees = fees
            logger.info(f"Loaded trading fees for {self.exchange_type.value}")
        except Exception as e:
            logger.error(f"Failed to load trading fees: {e}")
    
    async def start_websocket(self):
        """Start websocket connection for real-time data"""
        try:
            if self.exchange_type == ExchangeType.BINANCE:
                await self.start_binance_websocket()
            elif self.exchange_type == ExchangeType.COINBASEPRO:
                await self.start_coinbasepro_websocket()
            # Add other exchange websockets as needed
        except Exception as e:
            logger.error(f"Failed to start websocket: {e}")
    
    async def start_binance_websocket(self):
        """Start Binance websocket connection"""
        uri = "wss://stream.binance.com:9443/ws"
        self.ws_connection = await websockets.connect(uri)
        
        # Subscribe to ticker and orderbook for all symbols
        symbols = list(self.exchange.markets.keys())
        ticker_params = []
        depth_params = []
        
        for symbol in symbols[:20]:  # Limit to first 20 symbols
            ticker_params.append(f"{symbol.lower()}@ticker")
            depth_params.append(f"{symbol.lower()}@depth5")
        
        subscribe_msg = {
            "method": "SUBSCRIBE",
            "params": ticker_params + depth_params,
            "id": 1
        }
        
        await self.ws_connection.send(json.dumps(subscribe_msg))
        
        # Start listening loop
        asyncio.create_task(self.listen_websocket())
    
    async def listen_websocket(self):
        """Listen for websocket messages"""
        try:
            async for message in self.ws_connection:
                data = json.loads(message)
                await self.handle_websocket_message(data)
        except Exception as e:
            logger.error(f"Websocket error: {e}")
            # Attempt to reconnect
            await asyncio.sleep(5)
            await self.start_websocket()
    
    async def handle_websocket_message(self, data: Dict):
        """Handle incoming websocket messages"""
        try:
            if 'stream' in data:
                stream = data['stream']
                if '@ticker' in stream:
                    await self.handle_ticker_update(data['data'])
                elif '@depth' in stream:
                    await self.handle_orderbook_update(data['data'])
        except Exception as e:
            logger.error(f"Error handling websocket message: {e}")
    
    async def handle_ticker_update(self, data: Dict):
        """Handle ticker update"""
        try:
            symbol = data['s']
            ticker = Ticker(
                symbol=symbol,
                bid=float(data['b']),
                ask=float(data['a']),
                bid_volume=float(data['B']),
                ask_volume=float(data['A']),
                last_price=float(data['c']),
                volume_24h=float(data['v']),
                high_24h=float(data['h']),
                low_24h=float(data['l']),
                timestamp=datetime.now()
            )
            self.tickers[symbol] = ticker
        except Exception as e:
            logger.error(f"Error handling ticker update: {e}")
    
    async def handle_orderbook_update(self, data: Dict):
        """Handle orderbook update"""
        try:
            symbol = data['s']
            bids = [OrderBookEntry(float(bid), float(bid_qty), datetime.now()) 
                   for bid, bid_qty in data['b']]
            asks = [OrderBookEntry(float(ask), float(ask_qty), datetime.now()) 
                   for ask, ask_qty in data['a']]
            
            self.orderbooks[symbol] = {
                'bids': bids,
                'asks': asks,
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"Error handling orderbook update: {e}")
    
    async def place_order(self, order: Order) -> Order:
        """Place an order on the exchange"""
        try:
            # Rate limiting
            await self.check_rate_limit()
            
            # Prepare order parameters
            params = {
                'symbol': order.symbol,
                'type': order.order_type.value,
                'side': order.side.value,
                'amount': order.quantity,
            }
            
            if order.price:
                params['price'] = order.price
            if order.stop_price:
                params['stopPrice'] = order.stop_price
            
            # Place order
            result = await self.exchange.create_order(**params)
            
            # Update order with exchange data
            order.id = result['id']
            order.status = OrderStatus.OPEN
            order.timestamp = datetime.now()
            order.exchange = self.exchange_type.value
            
            logger.info(f"Placed order {order.id} on {self.exchange_type.value}")
            return order
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            order.status = OrderStatus.REJECTED
            return order
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order"""
        try:
            await self.check_rate_limit()
            await self.exchange.cancel_order(order_id, symbol)
            logger.info(f"Cancelled order {order_id} on {self.exchange_type.value}")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            return False
    
    async def get_order_status(self, order_id: str, symbol: str) -> OrderStatus:
        """Get order status"""
        try:
            await self.check_rate_limit()
            result = await self.exchange.fetch_order(order_id, symbol)
            
            if result['status'] == 'open':
                return OrderStatus.OPEN
            elif result['status'] == 'closed':
                return OrderStatus.CLOSED
            elif result['status'] == 'canceled':
                return OrderStatus.CANCELED
            else:
                return OrderStatus.REJECTED
                
        except Exception as e:
            logger.error(f"Failed to get order status: {e}")
            return OrderStatus.REJECTED
    
    async def get_balance(self) -> Dict[str, float]:
        """Get account balance"""
        try:
            await self.check_rate_limit()
            balance = await self.exchange.fetch_balance()
            return balance['free']
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return {}
    
    async def get_orderbook(self, symbol: str, limit: int = 20) -> Dict:
        """Get orderbook"""
        try:
            # Check if we have real-time orderbook
            if symbol in self.orderbooks:
                return self.orderbooks[symbol]
            
            # Fetch from REST API
            await self.check_rate_limit()
            orderbook = await self.exchange.fetch_order_book(symbol, limit)
            
            bids = [OrderBookEntry(float(bid['price']), float(bid['amount']), datetime.now()) 
                   for bid in orderbook['bids']]
            asks = [OrderBookEntry(float(ask['price']), float(ask['amount']), datetime.now()) 
                   for ask in orderbook['asks']]
            
            return {
                'bids': bids,
                'asks': asks,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Failed to get orderbook: {e}")
            return {'bids': [], 'asks': [], 'timestamp': datetime.now()}
    
    async def get_ticker(self, symbol: str) -> Optional[Ticker]:
        """Get ticker for symbol"""
        try:
            # Check if we have real-time ticker
            if symbol in self.tickers:
                return self.tickers[symbol]
            
            # Fetch from REST API
            await self.check_rate_limit()
            ticker_data = await self.exchange.fetch_ticker(symbol)
            
            ticker = Ticker(
                symbol=symbol,
                bid=ticker_data['bid'],
                ask=ticker_data['ask'],
                bid_volume=ticker_data['bidVolume'],
                ask_volume=ticker_data['askVolume'],
                last_price=ticker_data['last'],
                volume_24h=ticker_data['baseVolume'],
                high_24h=ticker_data['high'],
                low_24h=ticker_data['low'],
                timestamp=datetime.now()
            )
            
            return ticker
            
        except Exception as e:
            logger.error(f"Failed to get ticker: {e}")
            return None
    
    async def check_rate_limit(self):
        """Check and enforce rate limiting"""
        now = time.time()
        last_time = self.last_request_time.get(self.exchange_type.value, 0)
        
        # Wait if necessary to respect rate limits
        min_interval = 0.1  # 100ms between requests (adjust per exchange)
        if now - last_time < min_interval:
            await asyncio.sleep(min_interval - (now - last_time))
        
        self.last_request_time[self.exchange_type.value] = time.time()
    
    async def get_trading_fees(self, symbol: str) -> Dict[str, float]:
        """Get trading fees for symbol"""
        try:
            if 'trading' in self.fees:
                return self.fees['trading']
            return {'maker': 0.001, 'taker': 0.001}  # Default 0.1% fees
        except Exception as e:
            logger.error(f"Failed to get trading fees: {e}")
            return {'maker': 0.001, 'taker': 0.001}

class ExchangeManager:
    def __init__(self):
        self.exchanges = {}
        self.symbols = set()
    
    async def add_exchange(self, exchange_type: ExchangeType, config: Dict[str, Any]) -> str:
        """Add a new exchange"""
        exchange_id = f"{exchange_type.value}_{len(self.exchanges)}"
        
        exchange = EnhancedExchange(exchange_type, config)
        await exchange.initialize()
        
        self.exchanges[exchange_id] = exchange
        
        # Update symbols set
        for symbol in exchange.exchange.markets.keys():
            self.symbols.add(symbol)
        
        logger.info(f"Added exchange {exchange_id}")
        return exchange_id
    
    async def remove_exchange(self, exchange_id: str) -> bool:
        """Remove an exchange"""
        if exchange_id in self.exchanges:
            # Close websocket connection
            if self.exchanges[exchange_id].ws_connection:
                await self.exchanges[exchange_id].ws_connection.close()
            
            del self.exchanges[exchange_id]
            logger.info(f"Removed exchange {exchange_id}")
            return True
        return False
    
    async def place_order(self, exchange_id: str, order: Order) -> Order:
        """Place order on specific exchange"""
        if exchange_id not in self.exchanges:
            raise ValueError(f"Exchange {exchange_id} not found")
        
        return await self.exchanges[exchange_id].place_order(order)
    
    async def cancel_order(self, exchange_id: str, order_id: str, symbol: str) -> bool:
        """Cancel order on specific exchange"""
        if exchange_id not in self.exchanges:
            raise ValueError(f"Exchange {exchange_id} not found")
        
        return await self.exchanges[exchange_id].cancel_order(order_id, symbol)
    
    async def get_best_price(self, symbol: str, side: OrderSide) -> Tuple[float, str]:
        """Get best price across all exchanges for a symbol"""
        best_price = None
        best_exchange = None
        
        for exchange_id, exchange in self.exchanges.items():
            ticker = await exchange.get_ticker(symbol)
            if ticker:
                if side == OrderSide.BUY and ticker.ask:
                    if best_price is None or ticker.ask < best_price:
                        best_price = ticker.ask
                        best_exchange = exchange_id
                elif side == OrderSide.SELL and ticker.bid:
                    if best_price is None or ticker.bid > best_price:
                        best_price = ticker.bid
                        best_exchange = exchange_id
        
        return best_price, best_exchange
    
    async def get_arbitrage_opportunities(self, symbol: str) -> List[Dict]:
        """Find arbitrage opportunities across exchanges"""
        opportunities = []
        
        for exchange1_id, exchange1 in self.exchanges.items():
            for exchange2_id, exchange2 in self.exchanges.items():
                if exchange1_id == exchange2_id:
                    continue
                
                ticker1 = await exchange1.get_ticker(symbol)
                ticker2 = await exchange2.get_ticker(symbol)
                
                if ticker1 and ticker2 and ticker1.bid and ticker2.ask:
                    spread = ticker1.bid - ticker2.ask
                    if spread > 0:
                        profit_pct = (spread / ticker2.ask) * 100
                        
                        opportunities.append({
                            'buy_exchange': exchange2_id,
                            'sell_exchange': exchange1_id,
                            'buy_price': ticker2.ask,
                            'sell_price': ticker1.bid,
                            'spread': spread,
                            'profit_pct': profit_pct,
                            'symbol': symbol
                        })
        
        # Sort by profit percentage
        opportunities.sort(key=lambda x: x['profit_pct'], reverse=True)
        return opportunities

# Utility functions
async def create_exchange_manager() -> ExchangeManager:
    """Create and initialize exchange manager"""
    manager = ExchangeManager()
    
    # Example: Add multiple exchanges (in production, load from config)
    # await manager.add_exchange(ExchangeType.BINANCE, {
    #     'api_key': 'your_binance_api_key',
    #     'secret': 'your_binance_secret',
    #     'sandbox': True
    # })
    
    return manager

if __name__ == "__main__":
    async def main():
        manager = await create_exchange_manager()
        logger.info("Enhanced Exchange Manager started")
        
        # Keep running
        while True:
            await asyncio.sleep(1)
    
    asyncio.run(main())