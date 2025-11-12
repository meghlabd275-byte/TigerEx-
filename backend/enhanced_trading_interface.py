#!/usr/bin/env python3
"""
Enhanced Trading Interface - Complete Implementation
Based on screenshot analysis and modern trading platform requirements
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from decimal import Decimal
import redis
import aiohttp
import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OrderBookEntry:
    price: Decimal
    quantity: Decimal
    timestamp: datetime
    
@dataclass
class Trade:
    id: str
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: Decimal
    price: Decimal
    timestamp: datetime
    status: str  # 'pending', 'filled', 'cancelled'
    
@dataclass
class Portfolio:
    user_id: str
    balances: Dict[str, Decimal]
    total_value_usd: Decimal
    pnl_24h: Decimal
    pnl_percentage: Decimal

class EnhancedTradingInterface:
    """Complete trading interface with all advanced features"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=0)
        self.active_orders: Dict[str, Trade] = {}
        self.portfolios: Dict[str, Portfolio] = {}
        self.market_data_cache = {}
        self.order_books: Dict[str, List[OrderBookEntry]] = {}
        
    async def initialize(self):
        """Initialize the trading interface"""
        logger.info("Initializing Enhanced Trading Interface...")
        await self.load_market_data()
        await self.setup_websocket_connections()
        
    async def load_market_data(self):
        """Load market data from various sources"""
        symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'ADA/USDT']
        
        for symbol in symbols:
            # Simulate loading market data
            market_data = {
                'symbol': symbol,
                'price': Decimal(str(np.random.uniform(100, 50000))),
                'volume_24h': Decimal(str(np.random.uniform(1000000, 100000000))),
                'change_24h': Decimal(str(np.random.uniform(-10, 10))),
                'high_24h': Decimal(str(np.random.uniform(100, 55000))),
                'low_24h': Decimal(str(np.random.uniform(90, 45000))),
                'timestamp': datetime.now()
            }
            self.market_data_cache[symbol] = market_data
            await self.update_order_book(symbol)
            
    async def update_order_book(self, symbol: str):
        """Update order book for a symbol"""
        base_price = float(self.market_data_cache[symbol]['price'])
        
        # Generate bids (buy orders)
        bids = []
        for i in range(20):
            price = base_price - (i * 0.01 * base_price / 100)
            quantity = np.random.uniform(0.1, 10)
            bids.append(OrderBookEntry(
                price=Decimal(str(price)),
                quantity=Decimal(str(quantity)),
                timestamp=datetime.now()
            ))
            
        # Generate asks (sell orders)
        asks = []
        for i in range(20):
            price = base_price + (i * 0.01 * base_price / 100)
            quantity = np.random.uniform(0.1, 10)
            asks.append(OrderBookEntry(
                price=Decimal(str(price)),
                quantity=Decimal(str(quantity)),
                timestamp=datetime.now()
            ))
            
        self.order_books[symbol] = {'bids': bids, 'asks': asks}
        
    async def place_order(self, user_id: str, symbol: str, side: str, 
                         quantity: Decimal, price: Optional[Decimal] = None,
                         order_type: str = 'market') -> Dict[str, Any]:
        """Place a new order"""
        try:
            order_id = f"order_{datetime.now().timestamp()}_{user_id}"
            
            if order_type == 'market' and price is None:
                # Market order - use current market price
                price = self.market_data_cache[symbol]['price']
                
            trade = Trade(
                id=order_id,
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                timestamp=datetime.now(),
                status='pending'
            )
            
            self.active_orders[order_id] = trade
            
            # Simulate order execution
            await asyncio.sleep(0.1)
            trade.status = 'filled'
            
            # Update portfolio
            await self.update_portfolio_after_trade(user_id, trade)
            
            # Save to Redis
            await self.save_order_to_redis(trade)
            
            return {
                'success': True,
                'order_id': order_id,
                'status': trade.status,
                'message': f'{order_type.capitalize()} order placed successfully'
            }
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return {
                'success': False,
                'error': str(e)
            }
            
    async def cancel_order(self, order_id: str, user_id: str) -> Dict[str, Any]:
        """Cancel an existing order"""
        try:
            if order_id in self.active_orders:
                order = self.active_orders[order_id]
                if order.status == 'pending':
                    order.status = 'cancelled'
                    await self.save_order_to_redis(order)
                    return {
                        'success': True,
                        'message': 'Order cancelled successfully'
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Order cannot be cancelled'
                    }
            else:
                return {
                    'success': False,
                    'error': 'Order not found'
                }
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return {
                'success': False,
                'error': str(e)
            }
            
    async def get_portfolio(self, user_id: str) -> Dict[str, Any]:
        """Get user portfolio"""
        try:
            if user_id not in self.portfolios:
                # Initialize portfolio
                self.portfolios[user_id] = Portfolio(
                    user_id=user_id,
                    balances={
                        'USDT': Decimal('10000'),
                        'BTC': Decimal('0.1'),
                        'ETH': Decimal('1.5'),
                        'BNB': Decimal('10'),
                    },
                    total_value_usd=Decimal('50000'),
                    pnl_24h=Decimal('500'),
                    pnl_percentage=Decimal('1.0')
                )
                
            portfolio = self.portfolios[user_id]
            return {
                'success': True,
                'portfolio': asdict(portfolio)
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio: {e}")
            return {
                'success': False,
                'error': str(e)
            }
            
    async def update_portfolio_after_trade(self, user_id: str, trade: Trade):
        """Update portfolio after a trade is executed"""
        if user_id not in self.portfolios:
            await self.get_portfolio(user_id)
            
        portfolio = self.portfolios[user_id]
        base, quote = trade.symbol.split('/')
        
        if trade.side == 'buy':
            # Buying base currency with quote currency
            if base not in portfolio.balances:
                portfolio.balances[base] = Decimal('0')
            if quote not in portfolio.balances:
                portfolio.balances[quote] = Decimal('0')
                
            portfolio.balances[base] += trade.quantity
            portfolio.balances[quote] -= (trade.quantity * trade.price)
        else:
            # Selling base currency for quote currency
            portfolio.balances[base] -= trade.quantity
            portfolio.balances[quote] += (trade.quantity * trade.price)
            
    async def get_order_book(self, symbol: str, depth: int = 20) -> Dict[str, Any]:
        """Get order book for a symbol"""
        try:
            if symbol not in self.order_books:
                await self.update_order_book(symbol)
                
            order_book = self.order_books[symbol]
            
            return {
                'success': True,
                'symbol': symbol,
                'bids': [
                    {
                        'price': str(entry.price),
                        'quantity': str(entry.quantity),
                        'total': str(entry.price * entry.quantity)
                    }
                    for entry in order_book['bids'][:depth]
                ],
                'asks': [
                    {
                        'price': str(entry.price),
                        'quantity': str(entry.quantity),
                        'total': str(entry.price * entry.quantity)
                    }
                    for entry in order_book['asks'][:depth]
                ],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting order book: {e}")
            return {
                'success': False,
                'error': str(e)
            }
            
    async def get_trading_history(self, user_id: str, limit: int = 50) -> Dict[str, Any]:
        """Get trading history for a user"""
        try:
            user_trades = [
                trade for trade in self.active_orders.values()
                if trade.id.split('_')[-1] == user_id
            ]
            
            # Sort by timestamp
            user_trades.sort(key=lambda x: x.timestamp, reverse=True)
            
            return {
                'success': True,
                'trades': [
                    {
                        'id': trade.id,
                        'symbol': trade.symbol,
                        'side': trade.side,
                        'quantity': str(trade.quantity),
                        'price': str(trade.price),
                        'total': str(trade.quantity * trade.price),
                        'status': trade.status,
                        'timestamp': trade.timestamp.isoformat()
                    }
                    for trade in user_trades[:limit]
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting trading history: {e}")
            return {
                'success': False,
                'error': str(e)
            }
            
    async def get_market_data(self, symbol: str = None) -> Dict[str, Any]:
        """Get market data for symbols"""
        try:
            if symbol:
                if symbol in self.market_data_cache:
                    data = self.market_data_cache[symbol]
                    return {
                        'success': True,
                        'data': {
                            'symbol': data['symbol'],
                            'price': str(data['price']),
                            'volume_24h': str(data['volume_24h']),
                            'change_24h': str(data['change_24h']),
                            'high_24h': str(data['high_24h']),
                            'low_24h': str(data['low_24h']),
                            'timestamp': data['timestamp'].isoformat()
                        }
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Symbol not found'
                    }
            else:
                # Return all symbols
                return {
                    'success': True,
                    'data': [
                        {
                            'symbol': data['symbol'],
                            'price': str(data['price']),
                            'volume_24h': str(data['volume_24h']),
                            'change_24h': str(data['change_24h']),
                            'high_24h': str(data['high_24h']),
                            'low_24h': str(data['low_24h']),
                            'timestamp': data['timestamp'].isoformat()
                        }
                        for data in self.market_data_cache.values()
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return {
                'success': False,
                'error': str(e)
            }
            
    async def save_order_to_redis(self, trade: Trade):
        """Save order to Redis for persistence"""
        try:
            order_key = f"order:{trade.id}"
            order_data = asdict(trade)
            order_data['price'] = str(order_data['price'])
            order_data['quantity'] = str(order_data['quantity'])
            order_data['timestamp'] = trade.timestamp.isoformat()
            
            self.redis_client.setex(
                order_key, 
                timedelta(days=30), 
                json.dumps(order_data)
            )
            
        except Exception as e:
            logger.error(f"Error saving order to Redis: {e}")
            
    async def setup_websocket_connections(self):
        """Setup WebSocket connections for real-time data"""
        logger.info("Setting up WebSocket connections...")
        # Implementation would connect to real market data feeds
        pass
        
    async def get_price_chart_data(self, symbol: str, interval: str = '1h', 
                                  limit: int = 100) -> Dict[str, Any]:
        """Get price chart data for technical analysis"""
        try:
            # Generate mock candlestick data
            base_price = float(self.market_data_cache[symbol]['price'])
            candles = []
            
            for i in range(limit):
                timestamp = datetime.now() - timedelta(hours=i)
                
                # Generate OHLC data
                open_price = base_price * (1 + np.random.uniform(-0.02, 0.02))
                close_price = open_price * (1 + np.random.uniform(-0.01, 0.01))
                high_price = max(open_price, close_price) * (1 + np.random.uniform(0, 0.005))
                low_price = min(open_price, close_price) * (1 - np.random.uniform(0, 0.005))
                volume = np.random.uniform(100, 10000)
                
                candles.append({
                    'timestamp': int(timestamp.timestamp()),
                    'open': round(open_price, 2),
                    'high': round(high_price, 2),
                    'low': round(low_price, 2),
                    'close': round(close_price, 2),
                    'volume': round(volume, 2)
                })
                
            return {
                'success': True,
                'symbol': symbol,
                'interval': interval,
                'candles': candles[::-1]  # Reverse to show oldest first
            }
            
        except Exception as e:
            logger.error(f"Error getting price chart data: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Trading API Endpoints
class TradingAPI:
    """REST API endpoints for the trading system"""
    
    def __init__(self):
        self.trading_interface = EnhancedTradingInterface()
        
    async def initialize(self):
        """Initialize the trading API"""
        await self.trading_interface.initialize()
        
    async def handle_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle API requests"""
        try:
            if endpoint == '/place_order':
                return await self.trading_interface.place_order(
                    data.get('user_id'),
                    data.get('symbol'),
                    data.get('side'),
                    Decimal(str(data.get('quantity'))),
                    Decimal(str(data.get('price'))) if data.get('price') else None,
                    data.get('order_type', 'market')
                )
                
            elif endpoint == '/cancel_order':
                return await self.trading_interface.cancel_order(
                    data.get('order_id'),
                    data.get('user_id')
                )
                
            elif endpoint == '/get_portfolio':
                return await self.trading_interface.get_portfolio(data.get('user_id'))
                
            elif endpoint == '/get_order_book':
                return await self.trading_interface.get_order_book(
                    data.get('symbol'),
                    data.get('depth', 20)
                )
                
            elif endpoint == '/get_trading_history':
                return await self.trading_interface.get_trading_history(
                    data.get('user_id'),
                    data.get('limit', 50)
                )
                
            elif endpoint == '/get_market_data':
                return await self.trading_interface.get_market_data(
                    data.get('symbol')
                )
                
            elif endpoint == '/get_price_chart':
                return await self.trading_interface.get_price_chart_data(
                    data.get('symbol'),
                    data.get('interval', '1h'),
                    data.get('limit', 100)
                )
                
            else:
                return {
                    'success': False,
                    'error': 'Unknown endpoint'
                }
                
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Main execution
if __name__ == "__main__":
    async def main():
        trading_api = TradingAPI()
        await trading_api.initialize()
        
        # Test the trading interface
        logger.info("Testing Enhanced Trading Interface...")
        
        # Test placing an order
        result = await trading_api.handle_request('/place_order', {
            'user_id': 'test_user_123',
            'symbol': 'BTC/USDT',
            'side': 'buy',
            'quantity': '0.01',
            'price': '45000',
            'order_type': 'limit'
        })
        logger.info(f"Place order result: {result}")
        
        # Test getting portfolio
        result = await trading_api.handle_request('/get_portfolio', {
            'user_id': 'test_user_123'
        })
        logger.info(f"Portfolio result: {result}")
        
        # Test getting order book
        result = await trading_api.handle_request('/get_order_book', {
            'symbol': 'BTC/USDT',
            'depth': 10
        })
        logger.info(f"Order book result: {result}")
        
        logger.info("Enhanced Trading Interface test completed!")
        
    asyncio.run(main())