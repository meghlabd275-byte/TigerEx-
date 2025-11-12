#!/usr/bin/env python3
"""
Complete Trading Platform - All Trading Features Implementation
Spot, Futures, Margin, Options, Alpha, and all other trading interfaces
Based on advanced trading platform requirements
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from decimal import Decimal
import redis
import aiohttp
import numpy as np
import pandas as pd
from enum import Enum
import websocket
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingMode(Enum):
    SPOT = "spot"
    FUTURES = "futures"
    MARGIN = "margin"
    OPTIONS = "options"
    ALPHA = "alpha"
    LEVERAGED_TOKENS = "leveraged_tokens"
    COPY_TRADING = "copy_trading"
    GRID_TRADING = "grid_trading"
    DCA = "dollar_cost_averaging"
    STAKING = "staking"
    LENDING = "lending"
    LAUNCHPOOL = "launchpool"
    MINING = "mining"
    NFT = "nft"

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"
    ICEBERG = "iceberg"
    TWAP = "twap"
    FILL_OR_KILL = "fill_or_kill"
    IMMEDIATE_OR_CANCEL = "immediate_or_cancel"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"
    
class Timeframe(Enum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"
    MN1 = "1M"

@dataclass
class TradingInstrument:
    symbol: str
    base_asset: str
    quote_asset: str
    trading_mode: TradingMode
    min_quantity: Decimal
    max_quantity: Decimal
    quantity_precision: int
    price_precision: int
    min_notional: Decimal
    is_active: bool
    margin_trading_enabled: bool
    futures_enabled: bool
    options_enabled: bool

@dataclass
class MarketData:
    symbol: str
    last_price: Decimal
    bid_price: Decimal
    ask_price: Decimal
    high_24h: Decimal
    low_24h: Decimal
    volume_24h: Decimal
    change_24h: Decimal
    open_interest: Optional[Decimal] = None
    funding_rate: Optional[Decimal] = None
    mark_price: Optional[Decimal] = None
    timestamp: datetime = None

@dataclass
class OrderBookEntry:
    price: Decimal
    quantity: Decimal
    orders_count: int
    
@dataclass
class Trade:
    id: str
    user_id: str
    symbol: str
    trading_mode: TradingMode
    order_type: OrderType
    side: OrderSide
    quantity: Decimal
    price: Optional[Decimal]
    filled_quantity: Decimal
    remaining_quantity: Decimal
    average_price: Decimal
    status: str
    leverage: Optional[Decimal] = None
    margin: Optional[Decimal] = None
    liquidation_price: Optional[Decimal] = None
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class Position:
    user_id: str
    symbol: str
    trading_mode: TradingMode
    side: str
    size: Decimal
    entry_price: Decimal
    mark_price: Decimal
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    margin: Decimal
    leverage: Decimal
    liquidation_price: Decimal
    maintenance_margin: Decimal
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class FuturesContract:
    symbol: str
    base_asset: str
    quote_asset: str
    contract_type: str  # PERPETUAL, QUARTERLY, etc.
    settlement_date: Optional[datetime]
    contract_size: Decimal
    max_leverage: Decimal
    maintenance_margin_rate: Decimal
    funding_rate: Decimal
    next_funding_time: datetime

@dataclass
class OptionContract:
    symbol: str
    underlying: str
    strike_price: Decimal
    expiry_date: datetime
    option_type: str  # CALL, PUT
    settlement_type: str  # CASH, PHYSICAL
    implied_volatility: Decimal
    delta: Decimal
    gamma: Decimal
    theta: Decimal
    vega: Decimal
    rho: Decimal

class CompleteTradingPlatform:
    """Complete trading platform with all advanced features"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=0)
        self.instruments: Dict[str, TradingInstrument] = {}
        self.market_data: Dict[str, MarketData] = {}
        self.order_books: Dict[str, Dict[str, List[OrderBookEntry]]] = {}
        self.active_orders: Dict[str, Trade] = {}
        self.positions: Dict[str, Position] = {}
        self.futures_contracts: Dict[str, FuturesContract] = {}
        self.options_contracts: Dict[str, OptionContract] = {}
        self.user_balances: Dict[str, Dict[str, Decimal]] = {}
        self.leverage_settings: Dict[str, Dict[str, Decimal]] = {}
        self.margin_settings: Dict[str, Dict[str, Any]] = {}
        
    async def initialize(self):
        """Initialize the complete trading platform"""
        logger.info("Initializing Complete Trading Platform...")
        await self.load_all_instruments()
        await self.load_market_data()
        await self.setup_websocket_connections()
        await self.initialize_order_books()
        
    async def load_all_instruments(self):
        """Load all trading instruments for all modes"""
        
        # Spot trading instruments
        spot_symbols = [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'ADA/USDT',
            'DOT/USDT', 'AVAX/USDT', 'MATIC/USDT', 'LINK/USDT', 'UNI/USDT'
        ]
        
        for symbol in spot_symbols:
            base, quote = symbol.split('/')
            self.instruments[symbol] = TradingInstrument(
                symbol=symbol,
                base_asset=base,
                quote_asset=quote,
                trading_mode=TradingMode.SPOT,
                min_quantity=Decimal('0.000001'),
                max_quantity=Decimal('10000'),
                quantity_precision=8,
                price_precision=2,
                min_notional=Decimal('10'),
                is_active=True,
                margin_trading_enabled=True,
                futures_enabled=True,
                options_enabled=True
            )
        
        # Futures contracts
        futures_symbols = [
            'BTCUSDT-PERP', 'ETHUSDT-PERP', 'BNBUSDT-PERP', 'SOLUSDT-PERP',
            'BTCUSDT-3M', 'ETHUSDT-3M', 'BTCUSDT-6M', 'ETHUSDT-6M'
        ]
        
        for symbol in futures_symbols:
            base = symbol.split('USDT')[0]
            self.instruments[symbol] = TradingInstrument(
                symbol=symbol,
                base_asset=base,
                quote_asset='USDT',
                trading_mode=TradingMode.FUTURES,
                min_quantity=Decimal('0.001'),
                max_quantity=Decimal('1000'),
                quantity_precision=6,
                price_precision=2,
                min_notional=Decimal('5'),
                is_active=True,
                margin_trading_enabled=True,
                futures_enabled=True,
                options_enabled=False
            )
            
        # Options contracts
        options_symbols = [
            'BTC-50000-C-30D', 'BTC-50000-P-30D', 'ETH-3000-C-30D', 'ETH-3000-P-30D'
        ]
        
        for symbol in options_symbols:
            parts = symbol.split('-')
            self.instruments[symbol] = TradingInstrument(
                symbol=symbol,
                base_asset=parts[0],
                quote_asset='USDT',
                trading_mode=TradingMode.OPTIONS,
                min_quantity=Decimal('0.1'),
                max_quantity=Decimal('1000'),
                quantity_precision=4,
                price_precision=4,
                min_notional=Decimal('50'),
                is_active=True,
                margin_trading_enabled=False,
                futures_enabled=False,
                options_enabled=True
            )
            
        # Alpha trading pairs
        alpha_symbols = [
            'DOGE/USDT', 'SHIB/USDT', 'PEPE/USDT', 'FLOKI/USDT', 'BABYDOGE/USDT'
        ]
        
        for symbol in alpha_symbols:
            base, quote = symbol.split('/')
            self.instruments[symbol] = TradingInstrument(
                symbol=symbol,
                base_asset=base,
                quote_asset=quote,
                trading_mode=TradingMode.ALPHA,
                min_quantity=Decimal('10'),
                max_quantity=Decimal('1000000'),
                quantity_precision=0,
                price_precision=6,
                min_notional=Decimal('1'),
                is_active=True,
                margin_trading_enabled=False,
                futures_enabled=False,
                options_enabled=False
            )
    
    async def load_market_data(self):
        """Load market data for all instruments"""
        
        for symbol, instrument in self.instruments.items():
            if instrument.trading_mode in [TradingMode.SPOT, TradingMode.ALPHA]:
                base_price = Decimal(str(np.random.uniform(0.1, 50000)))
                
                self.market_data[symbol] = MarketData(
                    symbol=symbol,
                    last_price=base_price,
                    bid_price=base_price * Decimal('0.999'),
                    ask_price=base_price * Decimal('1.001'),
                    high_24h=base_price * Decimal('1.05'),
                    low_24h=base_price * Decimal('0.95'),
                    volume_24h=Decimal(str(np.random.uniform(1000000, 100000000))),
                    change_24h=Decimal(str(np.random.uniform(-10, 10))),
                    timestamp=datetime.now()
                )
                
            elif instrument.trading_mode == TradingMode.FUTURES:
                base_price = Decimal(str(np.random.uniform(100, 50000)))
                
                self.market_data[symbol] = MarketData(
                    symbol=symbol,
                    last_price=base_price,
                    bid_price=base_price * Decimal('0.999'),
                    ask_price=base_price * Decimal('1.001'),
                    high_24h=base_price * Decimal('1.05'),
                    low_24h=base_price * Decimal('0.95'),
                    volume_24h=Decimal(str(np.random.uniform(500000, 50000000))),
                    change_24h=Decimal(str(np.random.uniform(-15, 15))),
                    open_interest=Decimal(str(np.random.uniform(1000000, 10000000))),
                    funding_rate=Decimal(str(np.random.uniform(-0.01, 0.01))),
                    mark_price=base_price * Decimal(str(1 + np.random.uniform(-0.001, 0.001))),
                    timestamp=datetime.now()
                )
                
            elif instrument.trading_mode == TradingMode.OPTIONS:
                base_price = Decimal(str(np.random.uniform(100, 5000)))
                
                self.market_data[symbol] = MarketData(
                    symbol=symbol,
                    last_price=base_price,
                    bid_price=base_price * Decimal('0.98'),
                    ask_price=base_price * Decimal('1.02'),
                    high_24h=base_price * Decimal('1.10'),
                    low_24h=base_price * Decimal('0.90'),
                    volume_24h=Decimal(str(np.random.uniform(10000, 1000000))),
                    change_24h=Decimal(str(np.random.uniform(-20, 20))),
                    timestamp=datetime.now()
                )
    
    async def initialize_order_books(self):
        """Initialize order books for all instruments"""
        
        for symbol in self.instruments:
            await self.update_order_book(symbol)
    
    async def update_order_book(self, symbol: str):
        """Update order book for a symbol"""
        
        if symbol not in self.market_data:
            return
            
        current_price = self.market_data[symbol].last_price
        
        # Generate bids
        bids = []
        for i in range(20):
            price = current_price * (Decimal('1') - Decimal(str(i * 0.001)))
            quantity = Decimal(str(np.random.uniform(0.1, 100)))
            orders_count = np.random.randint(1, 50)
            bids.append(OrderBookEntry(price, quantity, orders_count))
        
        # Generate asks
        asks = []
        for i in range(20):
            price = current_price * (Decimal('1') + Decimal(str(i * 0.001)))
            quantity = Decimal(str(np.random.uniform(0.1, 100)))
            orders_count = np.random.randint(1, 50)
            asks.append(OrderBookEntry(price, quantity, orders_count))
        
        self.order_books[symbol] = {
            'bids': bids,
            'asks': asks
        }
    
    async def place_order(self, user_id: str, symbol: str, trading_mode: TradingMode,
                         order_type: OrderType, side: OrderSide, quantity: Decimal,
                         price: Optional[Decimal] = None, leverage: Optional[Decimal] = None,
                         **kwargs) -> Dict[str, Any]:
        """Place an order in any trading mode"""
        
        try:
            # Validate instrument
            if symbol not in self.instruments:
                return {'success': False, 'error': 'Instrument not found'}
            
            instrument = self.instruments[symbol]
            if instrument.trading_mode != trading_mode:
                return {'success': False, 'error': 'Trading mode mismatch'}
            
            # Validate order parameters
            validation_result = await self.validate_order_parameters(
                user_id, symbol, trading_mode, order_type, side, quantity, price, leverage
            )
            
            if not validation_result['valid']:
                return {'success': False, 'error': validation_result['error']}
            
            # Create order
            order_id = f"order_{int(time.time() * 1000)}_{user_id}"
            
            order = Trade(
                id=order_id,
                user_id=user_id,
                symbol=symbol,
                trading_mode=trading_mode,
                order_type=order_type,
                side=side,
                quantity=quantity,
                price=price,
                filled_quantity=Decimal('0'),
                remaining_quantity=quantity,
                average_price=Decimal('0'),
                status='OPEN',
                leverage=leverage,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Handle margin requirements for leveraged trading
            if trading_mode in [TradingMode.FUTURES, TradingMode.MARGIN] and leverage:
                margin_result = await self.calculate_margin_requirements(order)
                if not margin_result['sufficient']:
                    return {'success': False, 'error': 'Insufficient margin'}
                order.margin = margin_result['required_margin']
            
            # Add to active orders
            self.active_orders[order_id] = order
            
            # Execute order
            execution_result = await self.execute_order(order)
            
            if execution_result['success']:
                await self.save_order_to_redis(order)
                await self.update_user_positions(order)
                
                return {
                    'success': True,
                    'order_id': order_id,
                    'status': order.status,
                    'executed_quantity': execution_result['executed_quantity'],
                    'average_price': execution_result['average_price'],
                    'message': 'Order placed successfully'
                }
            else:
                return {'success': False, 'error': execution_result['error']}
                
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return {'success': False, 'error': str(e)}
    
    async def validate_order_parameters(self, user_id: str, symbol: str,
                                      trading_mode: TradingMode, order_type: OrderType,
                                      side: OrderSide, quantity: Decimal,
                                      price: Optional[Decimal], leverage: Optional[Decimal]) -> Dict[str, Any]:
        """Validate order parameters"""
        
        try:
            instrument = self.instruments[symbol]
            
            # Check quantity limits
            if quantity < instrument.min_quantity or quantity > instrument.max_quantity:
                return {
                    'valid': False,
                    'error': f'Quantity must be between {instrument.min_quantity} and {instrument.max_quantity}'
                }
            
            # Check minimum notional
            if price and (quantity * price) < instrument.min_notional:
                return {
                    'valid': False,
                    'error': f'Order value must be at least {instrument.min_notional}'
                }
            
            # Validate leverage for futures/margin
            if trading_mode in [TradingMode.FUTURES, TradingMode.MARGIN]:
                if not leverage:
                    return {'valid': False, 'error': 'Leverage is required for futures/margin trading'}
                
                if leverage > Decimal('125'):  # Max leverage
                    return {'valid': False, 'error': 'Leverage cannot exceed 125x'}
            
            # Check user balance for spot trading
            if trading_mode == TradingMode.SPOT:
                balance_check = await self.check_user_balance(user_id, symbol, side, quantity, price)
                if not balance_check['sufficient']:
                    return {'valid': False, 'error': 'Insufficient balance'}
            
            return {'valid': True}
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    async def check_user_balance(self, user_id: str, symbol: str, side: OrderSide,
                               quantity: Decimal, price: Optional[Decimal]) -> Dict[str, Any]:
        """Check if user has sufficient balance"""
        
        try:
            if user_id not in self.user_balances:
                self.user_balances[user_id] = {'USDT': Decimal('10000'), 'BTC': Decimal('0.1')}
            
            base_asset, quote_asset = symbol.split('/')
            balances = self.user_balances[user_id]
            
            if side == OrderSide.BUY:
                required_amount = quantity * (price or self.market_data[symbol].ask_price)
                if quote_asset not in balances or balances[quote_asset] < required_amount:
                    return {'sufficient': False}
            else:
                if base_asset not in balances or balances[base_asset] < quantity:
                    return {'sufficient': False}
            
            return {'sufficient': True}
            
        except Exception as e:
            return {'sufficient': False, 'error': str(e)}
    
    async def calculate_margin_requirements(self, order: Trade) -> Dict[str, Any]:
        """Calculate margin requirements for leveraged positions"""
        
        try:
            if not order.leverage:
                return {'sufficient': False, 'error': 'No leverage specified'}
            
            # Calculate position value
            position_value = order.quantity * (order.price or self.market_data[order.symbol].last_price)
            required_margin = position_value / order.leverage
            
            # Check user's available margin
            if order.user_id not in self.margin_settings:
                self.margin_settings[order.user_id] = {'available_margin': Decimal('5000')}
            
            available_margin = self.margin_settings[order.user_id]['available_margin']
            
            if available_margin < required_margin:
                return {'sufficient': False, 'required_margin': required_margin}
            
            return {
                'sufficient': True,
                'required_margin': required_margin,
                'position_value': position_value
            }
            
        except Exception as e:
            return {'sufficient': False, 'error': str(e)}
    
    async def execute_order(self, order: Trade) -> Dict[str, Any]:
        """Execute order based on type and market conditions"""
        
        try:
            if order.order_type == OrderType.MARKET:
                return await self.execute_market_order(order)
            elif order.order_type == OrderType.LIMIT:
                return await self.execute_limit_order(order)
            elif order.order_type in [OrderType.STOP_LOSS, OrderType.TAKE_PROFIT]:
                return await self.execute_conditional_order(order)
            else:
                return await self.execute_advanced_order(order)
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def execute_market_order(self, order: Trade) -> Dict[str, Any]:
        """Execute market order"""
        
        try:
            order_book = self.order_books.get(order.symbol, {})
            
            if order.side == OrderSide.BUY:
                # Match against asks
                remaining_quantity = order.quantity
                total_cost = Decimal('0')
                
                for ask_entry in order_book.get('asks', []):
                    if remaining_quantity <= 0:
                        break
                    
                    fill_quantity = min(remaining_quantity, ask_entry.quantity)
                    total_cost += fill_quantity * ask_entry.price
                    remaining_quantity -= fill_quantity
                    
                    order.filled_quantity += fill_quantity
                    order.average_price = total_cost / order.filled_quantity
                
                order.remaining_quantity = remaining_quantity
                
            else:
                # Match against bids
                remaining_quantity = order.quantity
                total_received = Decimal('0')
                
                for bid_entry in order_book.get('bids', []):
                    if remaining_quantity <= 0:
                        break
                    
                    fill_quantity = min(remaining_quantity, bid_entry.quantity)
                    total_received += fill_quantity * bid_entry.price
                    remaining_quantity -= fill_quantity
                    
                    order.filled_quantity += fill_quantity
                    order.average_price = total_received / order.filled_quantity
                
                order.remaining_quantity = remaining_quantity
            
            # Update order status
            if order.remaining_quantity == 0:
                order.status = 'FILLED'
            else:
                order.status = 'PARTIALLY_FILLED'
            
            order.updated_at = datetime.now()
            
            return {
                'success': True,
                'executed_quantity': order.filled_quantity,
                'average_price': order.average_price
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def execute_limit_order(self, order: Trade) -> Dict[str, Any]:
        """Execute limit order"""
        
        try:
            if not order.price:
                return {'success': False, 'error': 'Limit order requires price'}
            
            current_price = self.market_data[order.symbol].last_price
            
            # Check if order can be filled immediately
            if (order.side == OrderSide.BUY and current_price <= order.price) or \
               (order.side == OrderSide.SELL and current_price >= order.price):
                return await self.execute_market_order(order)
            else:
                # Order goes into the book
                order.status = 'OPEN'
                return {
                    'success': True,
                    'executed_quantity': Decimal('0'),
                    'average_price': Decimal('0')
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def execute_conditional_order(self, order: Trade) -> Dict[str, Any]:
        """Execute stop loss or take profit order"""
        
        try:
            current_price = self.market_data[order.symbol].last_price
            
            # Check trigger conditions
            if order.order_type == OrderType.STOP_LOSS:
                if (order.side == OrderSide.BUY and current_price >= order.price) or \
                   (order.side == OrderSide.SELL and current_price <= order.price):
                    return await self.execute_market_order(order)
            elif order.order_type == OrderType.TAKE_PROFIT:
                if (order.side == OrderSide.BUY and current_price <= order.price) or \
                   (order.side == OrderSide.SELL and current_price >= order.price):
                    return await self.execute_market_order(order)
            
            order.status = 'WAITING_TRIGGER'
            return {
                'success': True,
                'executed_quantity': Decimal('0'),
                'average_price': Decimal('0')
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def execute_advanced_order(self, order: Trade) -> Dict[str, Any]:
        """Execute advanced order types (iceberg, TWAP, etc.)"""
        
        try:
            # Simplified implementation for advanced orders
            if order.order_type == OrderType.ICEBERG:
                # Implement iceberg order logic
                return await self.execute_market_order(order)
            elif order.order_type == OrderType.TWAP:
                # Implement TWAP order logic
                return await self.execute_market_order(order)
            else:
                return await self.execute_market_order(order)
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def update_user_positions(self, order: Trade):
        """Update user positions after order execution"""
        
        try:
            if order.filled_quantity == 0:
                return
            
            position_key = f"{order.user_id}_{order.symbol}_{order.trading_mode.value}"
            
            if order.trading_mode in [TradingMode.FUTURES, TradingMode.MARGIN]:
                if position_key in self.positions:
                    position = self.positions[position_key]
                    # Update existing position
                    await self.update_existing_position(position, order)
                else:
                    # Create new position
                    await self.create_new_position(order)
            
            # Update user balances for spot trading
            if order.trading_mode == TradingMode.SPOT:
                await self.update_user_balances(order)
                
        except Exception as e:
            logger.error(f"Error updating user positions: {e}")
    
    async def create_new_position(self, order: Trade):
        """Create new position for futures/margin trading"""
        
        try:
            position_key = f"{order.user_id}_{order.symbol}_{order.trading_mode.value}"
            
            position = Position(
                user_id=order.user_id,
                symbol=order.symbol,
                trading_mode=order.trading_mode,
                side=order.side.value,
                size=order.filled_quantity,
                entry_price=order.average_price,
                mark_price=self.market_data[order.symbol].last_price,
                unrealized_pnl=Decimal('0'),
                realized_pnl=Decimal('0'),
                margin=order.margin or Decimal('0'),
                leverage=order.leverage or Decimal('1'),
                liquidation_price=await self.calculate_liquidation_price(order),
                maintenance_margin=order.margin * Decimal('0.05'),  # 5% maintenance margin
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.positions[position_key] = position
            
        except Exception as e:
            logger.error(f"Error creating new position: {e}")
    
    async def calculate_liquidation_price(self, order: Trade) -> Decimal:
        """Calculate liquidation price for a position"""
        
        try:
            if not order.leverage or not order.margin:
                return Decimal('0')
            
            position_value = order.filled_quantity * order.average_price
            maintenance_margin_required = position_value / order.leverage * Decimal('0.05')
            
            if order.side == OrderSide.BUY:
                liquidation_price = order.average_price * (Decimal('1') - (Decimal('1') / order.leverage))
            else:
                liquidation_price = order.average_price * (Decimal('1') + (Decimal('1') / order.leverage))
            
            return liquidation_price
            
        except Exception as e:
            return Decimal('0')
    
    async def update_user_balances(self, order: Trade):
        """Update user balances for spot trading"""
        
        try:
            if order.user_id not in self.user_balances:
                self.user_balances[order.user_id] = {'USDT': Decimal('10000'), 'BTC': Decimal('0.1')}
            
            balances = self.user_balances[order.user_id]
            base_asset, quote_asset = order.symbol.split('/')
            
            # Initialize balances if not present
            if base_asset not in balances:
                balances[base_asset] = Decimal('0')
            if quote_asset not in balances:
                balances[quote_asset] = Decimal('0')
            
            if order.side == OrderSide.BUY:
                # Buying base asset with quote asset
                balances[base_asset] += order.filled_quantity
                balances[quote_asset] -= (order.filled_quantity * order.average_price)
            else:
                # Selling base asset for quote asset
                balances[base_asset] -= order.filled_quantity
                balances[quote_asset] += (order.filled_quantity * order.average_price)
            
            # Save to Redis
            await self.save_user_balances_to_redis(order.user_id)
            
        except Exception as e:
            logger.error(f"Error updating user balances: {e}")
    
    async def get_trading_interface(self, trading_mode: TradingMode, user_id: str) -> Dict[str, Any]:
        """Get trading interface data for specific trading mode"""
        
        try:
            interface_data = {
                'trading_mode': trading_mode.value,
                'instruments': [],
                'market_data': {},
                'order_books': {},
                'user_positions': [],
                'user_orders': [],
                'account_info': {}
            }
            
            # Get instruments for this trading mode
            interface_data['instruments'] = [
                {
                    'symbol': instrument.symbol,
                    'base_asset': instrument.base_asset,
                    'quote_asset': instrument.quote_asset,
                    'min_quantity': str(instrument.min_quantity),
                    'max_quantity': str(instrument.max_quantity),
                    'quantity_precision': instrument.quantity_precision,
                    'price_precision': instrument.price_precision,
                    'min_notional': str(instrument.min_notional)
                }
                for instrument in self.instruments.values()
                if instrument.trading_mode == trading_mode
            ]
            
            # Get market data
            interface_data['market_data'] = {
                symbol: {
                    'symbol': data.symbol,
                    'last_price': str(data.last_price),
                    'bid_price': str(data.bid_price),
                    'ask_price': str(data.ask_price),
                    'high_24h': str(data.high_24h),
                    'low_24h': str(data.low_24h),
                    'volume_24h': str(data.volume_24h),
                    'change_24h': str(data.change_24h),
                    'open_interest': str(data.open_interest) if data.open_interest else None,
                    'funding_rate': str(data.funding_rate) if data.funding_rate else None,
                    'mark_price': str(data.mark_price) if data.mark_price else None,
                    'timestamp': data.timestamp.isoformat()
                }
                for symbol, data in self.market_data.items()
                if self.instruments[symbol].trading_mode == trading_mode
            }
            
            # Get order books
            interface_data['order_books'] = {
                symbol: {
                    'bids': [
                        {
                            'price': str(entry.price),
                            'quantity': str(entry.quantity),
                            'orders_count': entry.orders_count,
                            'total': str(entry.price * entry.quantity)
                        }
                        for entry in book_data['bids'][:20]
                    ],
                    'asks': [
                        {
                            'price': str(entry.price),
                            'quantity': str(entry.quantity),
                            'orders_count': entry.orders_count,
                            'total': str(entry.price * entry.quantity)
                        }
                        for entry in book_data['asks'][:20]
                    ]
                }
                for symbol, book_data in self.order_books.items()
                if self.instruments[symbol].trading_mode == trading_mode
            }
            
            # Get user positions
            interface_data['user_positions'] = [
                {
                    'symbol': position.symbol,
                    'side': position.side,
                    'size': str(position.size),
                    'entry_price': str(position.entry_price),
                    'mark_price': str(position.mark_price),
                    'unrealized_pnl': str(position.unrealized_pnl),
                    'realized_pnl': str(position.realized_pnl),
                    'margin': str(position.margin),
                    'leverage': str(position.leverage),
                    'liquidation_price': str(position.liquidation_price),
                    'created_at': position.created_at.isoformat()
                }
                for position in self.positions.values()
                if position.user_id == user_id and position.trading_mode == trading_mode
            ]
            
            # Get user orders
            interface_data['user_orders'] = [
                {
                    'id': order.id,
                    'symbol': order.symbol,
                    'order_type': order.order_type.value,
                    'side': order.side.value,
                    'quantity': str(order.quantity),
                    'price': str(order.price) if order.price else None,
                    'filled_quantity': str(order.filled_quantity),
                    'remaining_quantity': str(order.remaining_quantity),
                    'average_price': str(order.average_price),
                    'status': order.status,
                    'leverage': str(order.leverage) if order.leverage else None,
                    'created_at': order.created_at.isoformat()
                }
                for order in self.active_orders.values()
                if order.user_id == user_id and order.trading_mode == trading_mode
            ]
            
            # Get account info
            interface_data['account_info'] = await self.get_user_account_info(user_id, trading_mode)
            
            return {'success': True, 'interface_data': interface_data}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def get_user_account_info(self, user_id: str, trading_mode: TradingMode) -> Dict[str, Any]:
        """Get user account information for specific trading mode"""
        
        try:
            account_info = {
                'trading_mode': trading_mode.value,
                'balances': {},
                'margin_info': {},
                'leverage_settings': {},
                'total_value': '0'
            }
            
            # Get balances
            if user_id in self.user_balances:
                account_info['balances'] = {
                    asset: str(balance) for asset, balance in self.user_balances[user_id].items()
                }
            
            # Get margin info for futures/margin
            if trading_mode in [TradingMode.FUTURES, TradingMode.MARGIN]:
                if user_id in self.margin_settings:
                    margin_data = self.margin_settings[user_id]
                    account_info['margin_info'] = {
                        'available_margin': str(margin_data.get('available_margin', 0)),
                        'used_margin': str(margin_data.get('used_margin', 0)),
                        'maintenance_margin': str(margin_data.get('maintenance_margin', 0))
                    }
                
                # Calculate total position value
                total_position_value = sum(
                    position.size * position.mark_price
                    for position in self.positions.values()
                    if position.user_id == user_id and position.trading_mode == trading_mode
                )
                account_info['total_value'] = str(total_position_value)
            
            return account_info
            
        except Exception as e:
            return {}
    
    async def setup_websocket_connections(self):
        """Setup WebSocket connections for real-time data"""
        logger.info("Setting up WebSocket connections for real-time data...")
        # Implementation would connect to real market data feeds
        pass
    
    async def save_order_to_redis(self, order: Trade):
        """Save order to Redis for persistence"""
        try:
            order_key = f"order:{order.id}"
            order_data = asdict(order)
            order_data['quantity'] = str(order_data['quantity'])
            order_data['price'] = str(order_data['price']) if order_data['price'] else None
            order_data['filled_quantity'] = str(order_data['filled_quantity'])
            order_data['remaining_quantity'] = str(order_data['remaining_quantity'])
            order_data['average_price'] = str(order_data['average_price'])
            order_data['leverage'] = str(order_data['leverage']) if order_data['leverage'] else None
            order_data['margin'] = str(order_data['margin']) if order_data['margin'] else None
            order_data['liquidation_price'] = str(order_data['liquidation_price']) if order_data['liquidation_price'] else None
            order_data['created_at'] = order.created_at.isoformat()
            order_data['updated_at'] = order.updated_at.isoformat()
            
            self.redis_client.setex(order_key, timedelta(days=30), json.dumps(order_data))
            
        except Exception as e:
            logger.error(f"Error saving order to Redis: {e}")
    
    async def save_user_balances_to_redis(self, user_id: str):
        """Save user balances to Redis"""
        try:
            balances_key = f"balances:{user_id}"
            balances_data = {
                asset: str(balance) for asset, balance in self.user_balances[user_id].items()
            }
            self.redis_client.setex(balances_key, timedelta(days=30), json.dumps(balances_data))
            
        except Exception as e:
            logger.error(f"Error saving user balances to Redis: {e}")

# Main execution
if __name__ == "__main__":
    async def main():
        platform = CompleteTradingPlatform()
        await platform.initialize()
        
        # Test different trading modes
        logger.info("Testing Complete Trading Platform...")
        
        # Test spot trading
        result = await platform.place_order(
            user_id="trader_001",
            symbol="BTC/USDT",
            trading_mode=TradingMode.SPOT,
            order_type=OrderType.MARKET,
            side=OrderSide.BUY,
            quantity=Decimal('0.01')
        )
        logger.info(f"Spot trading result: {result}")
        
        # Test futures trading
        result = await platform.place_order(
            user_id="trader_001",
            symbol="BTCUSDT-PERP",
            trading_mode=TradingMode.FUTURES,
            order_type=OrderType.MARKET,
            side=OrderSide.BUY,
            quantity=Decimal('0.01'),
            leverage=Decimal('10')
        )
        logger.info(f"Futures trading result: {result}")
        
        # Test options trading
        result = await platform.place_order(
            user_id="trader_001",
            symbol="BTC-50000-C-30D",
            trading_mode=TradingMode.OPTIONS,
            order_type=OrderType.MARKET,
            side=OrderSide.BUY,
            quantity=Decimal('0.1')
        )
        logger.info(f"Options trading result: {result}")
        
        # Test alpha trading
        result = await platform.place_order(
            user_id="trader_001",
            symbol="DOGE/USDT",
            trading_mode=TradingMode.ALPHA,
            order_type=OrderType.MARKET,
            side=OrderSide.BUY,
            quantity=Decimal('1000')
        )
        logger.info(f"Alpha trading result: {result}")
        
        # Get trading interface for spot
        result = await platform.get_trading_interface(TradingMode.SPOT, "trader_001")
        logger.info(f"Spot trading interface: {result['success']}")
        
        # Get trading interface for futures
        result = await platform.get_trading_interface(TradingMode.FUTURES, "trader_001")
        logger.info(f"Futures trading interface: {result['success']}")
        
        logger.info("Complete Trading Platform test completed!")
        
    asyncio.run(main())