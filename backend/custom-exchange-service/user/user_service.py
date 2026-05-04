#!/usr/bin/env python3
"""
TigerEx Custom Exchange Service - User Interface
Supports CEX (Centralized Exchange), DEX (Decentralized Exchange), and Hybrid
"""
import os
import json
import hashlib
import logging
import uuid
import time
import threading
import requests
from typing import Dict, List
from datetime import datetime, timedelta
from collections import defaultdict
from flask import Flask, jsonify, request
from flask_cors import CORS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Trading pairs
PAIRS = {
    "TIG/ETH": {"base": "TIG", "quote": "ETH", "min_order": 0.001, "maker_fee": 0.001, "taker_fee": 0.002},
    "TIG/USDC": {"base": "TIG", "quote": "USDC", "min_order": 0.001, "maker_fee": 0.001, "taker_fee": 0.002},
    "TIG/USDT": {"base": "TIG", "quote": "USDT", "min_order": 0.001, "maker_fee": 0.001, "taker_fee": 0.002},
    "ETH/USDC": {"base": "ETH", "quote": "USDC", "min_order": 0.001, "maker_fee": 0.001, "taker_fee": 0.002},
    "ETH/USDT": {"base": "ETH", "quote": "USDT", "min_order": 0.001, "maker_fee": 0.001, "taker_fee": 0.002},
    "USDC/USDT": {"base": "USDC", "quote": "USDT", "min_order": 1, "maker_fee": 0.0001, "taker_fee": 0.0002},
}


class ExchangeUserService:
    """User-facing exchange service"""
    
    def __init__(self):
        self.orders = {}
        self.trades = {}
        self.pools = {}
        self.user_balances = defaultdict(lambda: defaultdict(float))
        self.order_book = defaultdict(lambda: {"bids": [], "asks": []})
        self.market_stats = {}
        
        # Initialize
        self._init_data()
        
        logger.info("Exchange User Service initialized")
    
    def _init_data(self):
        """Initialize sample data"""
        for pair, data in PAIRS.items():
            self.market_stats[pair] = {
                "pair": pair,
                "open": 100.0 + hash(pair) % 100,
                "high": 110.0 + hash(pair) % 100,
                "low": 90.0 + hash(pair) % 100,
                "close": 100.0 + hash(pair) % 100,
                "volume": float(1000000 + hash(pair) % 1000000),
                "trades": 1000 + hash(pair) % 10000,
            }
            
            self.order_book[pair] = {
                "bids": [{"price": 100 - i*0.1, "amount": 10 + i} for i in range(10)],
                "asks": [{"price": 100 + i*0.1, "amount": 10 + i} for i in range(10)],
            }
        
        # Liquidity pools
        for i in range(5):
            self.pools[f"POOL_{i}"] = {
                "pool_id": f"POOL_{i}",
                "pair": f"TOKEN{i}A/TOKEN{i}B",
                "token_a": f"TOKEN{i}A",
                "token_b": f"TOKEN{i}B",
                "reserve_a": 1000000,
                "reserve_b": 1000000,
                "liquidity": 1000000,
            }
    
    # --- User Methods ---
    
    def create_order(self, user_id: str, pair: str, side: str, order_type: str, price: float, amount: float) -> Dict:
        """Create order"""
        if pair not in PAIRS:
            return {"error": "Trading pair not found"}
        
        order_id = f"ORDER_{uuid.uuid4().hex[:12]}"
        
        self.orders[order_id] = {
            "order_id": order_id,
            "user_id": user_id,
            "pair": pair,
            "side": side,
            "type": order_type,
            "price": price,
            "amount": amount,
            "filled": 0,
            "status": "open",
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Add to order book
        if side == "buy":
            self.order_book[pair]["bids"].append({"price": price, "amount": amount})
        else:
            self.order_book[pair]["asks"].append({"price": price, "amount": amount})
        
        return {"order_id": order_id, "status": "open", "price": price, "amount": amount}
    
    def cancel_order(self, user_id: str, order_id: str) -> Dict:
        """Cancel order"""
        if order_id not in self.orders:
            return {"error": "Order not found"}
        
        order = self.orders[order_id]
        if order["user_id"] != user_id:
            return {"error": "Not your order"}
        
        order["status"] = "cancelled"
        
        return {"status": "cancelled", "order_id": order_id}
    
    def get_order(self, order_id: str) -> Dict:
        """Get order"""
        if order_id in self.orders:
            return self.orders[order_id]
        return {"error": "Order not found"}
    
    def get_orders(self, user_id: str, pair: str = "") -> List[Dict]:
        """Get user orders"""
        orders = [o for o in self.orders.values() if o["user_id"] == user_id]
        if pair:
            orders = [o for o in orders if o["pair"] == pair]
        return orders
    
    def get_order_book(self, pair: str) -> Dict:
        """Get order book"""
        if pair in self.order_book:
            bids = sorted(self.order_book[pair]["bids"], key=lambda x: x["price"], reverse=True)[:20]
            asks = sorted(self.order_book[pair]["asks"], key=lambda x: x["price"])[:20]
            return {"bids": bids, "asks": asks}
        return {"bids": [], "asks": []}
    
    def get_market_stats(self, pair: str = "") -> Dict:
        """Get market stats"""
        if pair:
            return self.market_stats.get(pair, {"error": "Pair not found"})
        
        return list(self.market_stats.values())
    
    def get_pairs(self) -> List[Dict]:
        """Get trading pairs"""
        return [{"pair": k, **v} for k, v in PAIRS.items()]
    
    def get_user_balance(self, user_id: str) -> Dict:
        """Get user balance"""
        return dict(self.user_balances[user_id])
    
    def deposit(self, user_id: str, asset: str, amount: float) -> Dict:
        """Deposit funds"""
        self.user_balances[user_id][asset] += amount
        
        return {"status": "deposited", "asset": asset, "amount": amount}
    
    def withdraw(self, user_id: str, asset: str, amount: float) -> Dict:
        """Withdraw funds"""
        if self.user_balances[user_id][asset] < amount:
            return {"error": "Insufficient balance"}
        
        self.user_balances[user_id][asset] -= amount
        
        return {"status": "withdrawn", "asset": asset, "amount": amount}
    
    def get_pools(self, chain: str = "") -> List[Dict]:
        """Get liquidity pools"""
        pools = list(self.pools.values())
        return pools
    
    def add_liquidity(self, user_id: str, pool_id: str, amount_a: float, amount_b: float) -> Dict:
        """Add liquidity"""
        if pool_id not in self.pools:
            return {"error": "Pool not found"}
        
        pool = self.pools[pool_id]
        pool["reserve_a"] += amount_a
        pool["reserve_b"] += amount_b
        
        return {"status": "added", "pool": pool_id}
    
    def remove_liquidity(self, user_id: str, pool_id: str, liquidity: float) -> Dict:
        """Remove liquidity"""
        if pool_id not in self.pools:
            return {"error": "Pool not found"}
        
        pool = self.pools[pool_id]
        
        amount_a = liquidity * (pool["reserve_a"] / pool["liquidity"])
        amount_b = liquidity * (pool["reserve_b"] / pool["liquidity"])
        
        pool["reserve_a"] -= amount_a
        pool["reserve_b"] -= amount_b
        pool["liquidity"] -= liquidity
        
        return {"status": "removed", "pool": pool_id}
    
    def swap(self, user_id: str, from_token: str, to_token: str, amount: float) -> Dict:
        """Token swap"""
        # Find pool
        pool_id = None
        for pid, pool in self.pools.items():
            if pool["token_a"] == from_token and pool["token_b"] == to_token:
                pool_id = pid
                break
        
        if not pool_id:
            return {"error": "Pool not found"}
        
        pool = self.pools[pool_id]
        rate = pool["reserve_b"] / pool["reserve_a"]
        output = amount * rate
        
        pool["reserve_a"] += amount
        pool["reserve_b"] -= output
        
        self.user_balances[user_id][from_token] -= amount
        self.user_balances[user_id][to_token] += output
        
        return {"status": "swapped", "input": amount, "output": output}
    
    def get_recent_trades(self, pair: str, limit: int = 20) -> List[Dict]:
        """Get recent trades"""
        txs = [t for t in self.trades.values() if t.get("pair") == pair]
        return sorted(txs, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]


# Create Flask app
app = Flask(__name__)
CORS(app)

exchange_user_service = ExchangeUserService()


@app.route('/exchange/user/health')
def health():
    return jsonify({"status": "ok", "service": "exchange", "role": "user"})


@app.route('/exchange/user/create-order', methods=['POST'])
def user_create_order():
    data = request.get_json() or {}
    return jsonify(exchange_user_service.create_order(
        data.get('user_id', str(uuid.uuid4())),
        data.get('pair', ''),
        data.get('side', 'buy'),
        data.get('type', 'limit'),
        data.get('price', 0),
        data.get('amount', 0)
    ))


@app.route('/exchange/user/cancel-order', methods=['POST'])
def user_cancel_order():
    data = request.get_json() or {}
    return jsonify(exchange_user_service.cancel_order(
        data.get('user_id', ''),
        data.get('order_id', '')
    ))


@app.route('/exchange/user/order/<order_id>')
def user_order(order_id):
    return jsonify(exchange_user_service.get_order(order_id))


@app.route('/exchange/user/orders/<user_id>')
def user_orders(user_id):
    pair = request.args.get('pair', '')
    return jsonify(exchange_user_service.get_orders(user_id, pair))


@app.route('/exchange/user/order-book/<pair>')
def user_order_book(pair):
    return jsonify(exchange_user_service.get_order_book(pair))


@app.route('/exchange/user/market-stats')
def user_market_stats():
    pair = request.args.get('pair', '')
    return jsonify(exchange_user_service.get_market_stats(pair))


@app.route('/exchange/user/pairs')
def user_pairs():
    return jsonify(exchange_user_service.get_pairs())


@app.route('/exchange/user/balance/<user_id>')
def user_balance(user_id):
    return jsonify(exchange_user_service.get_user_balance(user_id))


@app.route('/exchange/user/deposit', methods=['POST'])
def user_deposit():
    data = request.get_json() or {}
    return jsonify(exchange_user_service.deposit(
        data.get('user_id', ''),
        data.get('asset', ''),
        data.get('amount', 0)
    ))


@app.route('/exchange/user/withdraw', methods=['POST'])
def user_withdraw():
    data = request.get_json() or {}
    return jsonify(exchange_user_service.withdraw(
        data.get('user_id', ''),
        data.get('asset', ''),
        data.get('amount', 0)
    ))


@app.route('/exchange/user/pools')
def user_pools():
    chain = request.args.get('chain', '')
    return jsonify(exchange_user_service.get_pools(chain))


@app.route('/exchange/user/add-liquidity', methods=['POST'])
def user_add_liquidity():
    data = request.get_json() or {}
    return jsonify(exchange_user_service.add_liquidity(
        data.get('user_id', ''),
        data.get('pool_id', ''),
        data.get('amount_a', 0),
        data.get('amount_b', 0)
    ))


@app.route('/exchange/user/remove-liquidity', methods=['POST'])
def user_remove_liquidity():
    data = request.get_json() or {}
    return jsonify(exchange_user_service.remove_liquidity(
        data.get('user_id', ''),
        data.get('pool_id', ''),
        data.get('liquidity', 0)
    ))


@app.route('/exchange/user/swap', methods=['POST'])
def user_swap():
    data = request.get_json() or {}
    return jsonify(exchange_user_service.swap(
        data.get('user_id', ''),
        data.get('from_token', ''),
        data.get('to_token', ''),
        data.get('amount', 0)
    ))


@app.route('/exchange/user/trades/<pair>')
def user_trades(pair):
    limit = request.args.get('limit', 20, type=int)
    return jsonify(exchange_user_service.get_recent_trades(pair, limit))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6401))
    logger.info(f"Starting User Exchange Service on port {port}")
    app.run(host='0.0.0.0', port=port, threaded=True)