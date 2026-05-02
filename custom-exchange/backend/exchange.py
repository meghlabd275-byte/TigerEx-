#!/usr/bin/env python3
"""
TigerEx Custom Exchange Backend - CEX + DEX Hybrid

Order Matching Engine with Rate Limiting
@version 2.0.0
"""

import os
import re
import secrets
import time
import uuid
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from functools import wraps

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    "name": "TigerEx",
    "fee_maker": 0.001,
    "fee_taker": 0.002,
    "min_order_value": 1.0,
    "max_order_value": 1_000_000,
}

# Rate limiting
_rate_limits = defaultdict(lambda: {'count': 0, 'reset': 0})


def rate_limit(max_requests: int = 100, window: int = 60):
    """Rate limiting decorator."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            key = f.__name__
            now = time.time()
            limit = _rate_limits[key]
            
            if now > limit['reset']:
                limit['count'] = 0
                limit['reset'] = now + window
            
            if limit['count'] >= max_requests:
                return {'error': 'Rate limit exceeded'}, 429
            
            limit['count'] += 1
            return f(*args, **kwargs)
        return wrapper
    return decorator


def validate_input(value: str, pattern: str) -> bool:
    """Validate input against regex pattern."""
    return bool(re.match(pattern, str(value))

class OrderBook:
    """Order book with matching engine."""
    
    def __init__(self, pair):
        self.pair = pair
        self.bids = []  # Buy orders - sorted desc by price
        self.asks = []  # Sell orders - sorted asc by price
        self.trades = []  # Trade history
    
    def add(self, order: dict) -> List[dict]:
        """Add order and attempt to match.
        
        Returns list of executed trades.
        """
        side = order['side']
        price = order['price']
        qty = order['remaining']
        
        if side == 'buy':
            # Match with asks (sell orders) where price <= order price
            matches = [o for o in self.asks if o['price'] <= price and o['remaining'] > 0]
            matches.sort(key=lambda x: x['price'])  # Best price first
            
            trades = []
            for ask in matches:
                if qty <= 0:
                    break
                    
                trade_qty = min(qty, ask['remaining'])
                trade_price = ask['price']
                
                trades.append({
                    'id': f"TX{secrets.token_hex(6)}",
                    'maker_id': ask['user_id'],
                    'taker_id': order['user_id'],
                    'side': 'buy',
                    'price': trade_price,
                    'quantity': trade_qty,
                    'timestamp': time.time()
                })
                
                ask['remaining'] -= trade_qty
                qty -= trade_qty
            
            # Remove filled orders
            self.asks = [o for o in self.asks if o['remaining'] > 0]
            
            # Add remaining to bids
            if qty > 0:
                order['remaining'] = qty
                self.bids.append(order)
                self.bids.sort(key=lambda x: x['price'], reverse=True)
            
            return trades
        
        else:  # sell
            # Match with bids (buy orders) where price >= order price
            matches = [o for o in self.bids if o['price'] >= price and o['remaining'] > 0]
            matches.sort(key=lambda x: x['price'], reverse=True)  # Best price first
            
            trades = []
            for bid in matches:
                if qty <= 0:
                    break
                    
                trade_qty = min(qty, bid['remaining'])
                trade_price = bid['price']
                
                trades.append({
                    'id': f"TX{secrets.token_hex(6)}",
                    'maker_id': bid['user_id'],
                    'taker_id': order['user_id'],
                    'side': 'sell',
                    'price': trade_price,
                    'quantity': trade_qty,
                    'timestamp': time.time()
                })
                
                bid['remaining'] -= trade_qty
                qty -= trade_qty
            
            # Remove filled orders
            self.bids = [o for o in self.bids if o['remaining'] > 0]
            
            # Add remaining to asks
            if qty > 0:
                order['remaining'] = qty
                self.asks.append(order)
                self.asks.sort(key=lambda x: x['price'])
            
            return trades
    
    def get_depth(self, levels: int = 10) -> dict:
        """Get order book depth."""
        return {
            'bids': [
                {'price': o['price'], 'quantity': o['remaining']}
                for o in self.bids[:levels]
            ],
            'asks': [
                {'price': o['price'], 'quantity': o['remaining']}
                for o in self.asks[:levels]
            ]
        }
    
    def get_spread(self) -> Optional[float]:
        """Get best bid-ask spread."""
        if not self.bids or not self.asks:
            return None
        return self.asks[0]['price'] - self.bids[0]['price']

class Exchange:
    """TigerEx Exchange with matching engine."""
    
    def __init__(self):
        self.books = {}      # pair -> OrderBook
        self.orders = {}     # order_id -> order
        self.balances = defaultdict(lambda: defaultdict(float))
        self.trades = []    # executed trades
        
        # Initialize demo users
        for u in ['u1', 'u2']:
            self.balances[u]['TIG'] = 10000
            self.balances[u]['USDC'] = 50000
    
    def create(self, uid: str) -> dict:
        """Create new user account."""
        if uid not in self.balances:
            self.balances[uid]['TIG'] = 0
            self.balances[uid]['USDC'] = 0
        return {"user_id": uid}
    
    def deposit(self, uid: str, asset: str, amt: float) -> dict:
        """Handle deposit."""
        if amt <= 0:
            return {"error": "invalid_amount"}
        self.balances[uid][asset] += amt
        return {"tx": amt, "balance": self.balances[uid][asset]}
    
    def withdraw(self, uid: str, asset: str, amt: float, address: str = '') -> dict:
        """Handle withdrawal."""
        if amt <= 0:
            return {"error": "invalid_amount"}
        if self.balances[uid][asset] < amt:
            return {"error": "insufficient_balance"}
        self.balances[uid][asset] -= amt
        return {"tx": amt, "balance": self.balances[uid][asset]}
    
    @rate_limit(max_requests=100, window=60)
    def place(self, uid: str, pair: str, side: str, price: float, qty: float) -> dict:
        """Place order with matching."""
        # Validate inputs
        if not pair or side not in ['buy', 'sell']:
            return {"error": "invalid_parameters"}
        if price <= 0 or qty <= 0:
            return {"error": "invalid_amount"}
        
        # Check order value limits
        value = price * qty
        if value < CONFIG['min_order_value']:
            return {"error": "order_too_small"}
        if value > CONFIG['max_order_value']:
            return {"error": "order_too_large"}
        
        # Check balance
        base = pair.split('-')[0]
        if side == 'buy':
            quote = pair.split('-')[1]
            required = price * qty
            if self.balances[uid][quote] < required:
                return {"error": "insufficient_balance"}
        else:
            if self.balances[uid][base] < qty:
                return {"error": "insufficient_balance"}
        
        # Create order
        order = {
            'id': f"ORD{uuid.uuid4().hex[:8]}",
            'user_id': uid,
            'pair': pair,
            'side': side,
            'price': price,
            'quantity': qty,
            'remaining': qty,
            'status': 'pending',
            'created_at': time.time()
        }
        self.orders[order['id']] = order
        
        # Get or create order book
        if pair not in self.books:
            self.books[pair] = OrderBook(pair)
        
        # Attempt to match
        trades = self.books[pair].add(order)
        
        # Execute trades
        for trade in trades:
            self._execute_trade(trade)
            self.trades.append(trade)
        
        # Update order status
        if order['remaining'] <= 0:
            order['status'] = 'filled'
        elif order['remaining'] < qty:
            order['status'] = 'partially_filled'
        
        return {"order": order, "trades": len(trades)}
    
    def _execute_trade(self, trade: dict) -> dict:
        """Execute a trade and update balances."""
        maker = trade['maker_id']
        taker = trade['taker_id']
        price = trade['price']
        qty = trade['quantity']
        
        # Get pair from order
        order = self.orders.get(trade.get('order_id', ''), {})
        pair = order.get('pair', 'TIG-USDC')
        base = pair.split('-')[0]
        quote = pair.split('-')[1]
        
        # Calculate fees
        maker_fee = price * qty * CONFIG['fee_maker']
        taker_fee = price * qty * CONFIG['fee_taker']
        
        # Update balances
        if trade['side'] == 'buy':
            # Maker sells (gives base, gets quote)
            self.balances[maker][base] -= qty
            self.balances[maker][quote] += (price * qty) - maker_fee
            # Taker buys (gives quote, gets base)
            self.balances[taker][quote] -= (price * qty) + taker_fee
            self.balances[taker][base] += qty
        else:
            # Maker buys (gives quote, gets base)
            self.balances[maker][quote] -= (price * qty) + taker_fee
            self.balances[maker][base] += qty
            # Taker sells (gives base, gets quote)
            self.balances[taker][base] -= qty
            self.balances[taker][quote] += (price * qty) - maker_fee
        
        return trade
    
    def cancel(self, oid: str, uid: str) -> dict:
        """Cancel order."""
        order = self.orders.get(oid)
        if not order:
            return {"error": "not_found"}
        if order['user_id'] != uid:
            return {"error": "unauthorized"}
        if order['status'] != 'pending':
            return {"error": "cannot_cancel"}
        
        order['status'] = 'cancelled'
        return {"ok": True}
    
    def balance(self, uid: str) -> dict:
        """Get user balances."""
        return dict(self.balances[uid])
    
    def book(self, pair: str) -> dict:
        """Get order book."""
        if pair not in self.books:
            return {'bids': [], 'asks': []}
        return self.books[pair].get_depth()
    
    def trades_history(self, pair: str = '', limit: int = 50) -> List[dict]:
        """Get recent trades."""
        if pair:
            return [t for t in self.trades[-limit:] if t.get('pair') == pair]
        return self.trades[-limit:]


# Flask app
from flask import Flask, jsonify, request
app = Flask(__name__)

ex = Exchange()


@app.route('/health')
def health():
    """Health check."""
    return jsonify({
        "status": "ok",
        "orders": len(ex.orders),
        "trades": len(ex.trades)
    })


@app.route('/account', methods=['POST'])
def create():
    """Create account."""
    uid = request.json.get('user_id', 'u1') if request.is_json else 'u1'
    return jsonify(ex.create(uid))


@app.route('/deposit', methods=['POST'])
def deposit():
    """Handle deposit."""
    if request.is_json:
        d = request.json
        return jsonify(ex.deposit(d.get('user_id', 'u1'), d.get('asset', 'TIG'), d.get('amount', 0)))
    return jsonify(ex.deposit('u1', 'TIG', 0))


@app.route('/withdraw', methods=['POST'])
def withdraw():
    """Handle withdrawal."""
    if request.is_json:
        d = request.json
        return jsonify(ex.withdraw(d.get('user_id', 'u1'), d.get('asset'), d.get('amount', 0)))
    return jsonify({"error": "no_data"})


@app.route('/order', methods=['POST'])
def place_order():
    """Place order."""
    if request.is_json:
        d = request.json
        return jsonify(ex.place(
            d.get('user_id', 'u1'),
            d.get('pair', 'TIG-USDC'),
            d.get('side', 'buy'),
            d.get('price', 0),
            d.get('quantity', 0)
        ))
    return jsonify({"error": "no_data"})


@app.route('/order/<oid>', methods=['DELETE'])
def cancel(oid):
    """Cancel order."""
    return jsonify(ex.cancel(oid, request.headers.get('X-User-Id', 'u1')))


@app.route('/balance/<uid>')
def balance(uid):
    """Get balance."""
    return jsonify(ex.balance(uid))


@app.route('/book/<pair>')
def book(pair):
    """Get order book."""
    return jsonify(ex.book(pair))


@app.route('/trades/<pair>')
def trades(pair):
    """Get recent trades."""
    return jsonify(ex.trades_history(pair))


@app.route('/config')
def config():
    """Get exchange config."""
    return jsonify(CONFIG)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5900, threaded=True)
