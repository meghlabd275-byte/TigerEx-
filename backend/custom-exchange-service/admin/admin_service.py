#!/usr/bin/env python3
"""
TigerEx Custom Exchange Service - Admin Interface
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
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# EXCHANGE CONFIGURATION
# ============================================================
EXCHANGE_MODES = {
    "cex": {"name": "Centralized Exchange", "type": "orderbook", "custodial": True},
    "dex": {"name": "Decentralized Exchange", "type": "liquidity_pool", "custodial": False},
    "hybrid": {"name": "Hybrid Exchange", "type": "orderbook+liquidity_pool", "custodial": True},
}

SUPPORTED_PAIRS = [
    "TIG/ETH", "TIG/USDC", "TIG/USDT", "ETH/USDC", "ETH/USDT", "ETH/BNB",
    "USDC/USDT", "BTC/ETH", "BTC/USDC", "BTC/USDT", "SOL/ETH", "SOL/USDC"
]

BLOCKCHAINS = {
    "tigerex": {"name": "TigerExChain", "type": "evm", "chain_id": 9999},
    "ethereum": {"name": "Ethereum", "type": "evm", "chain_id": 1},
    "bsc": {"name": "BNB Chain", "type": "evm", "chain_id": 56},
    "polygon": {"name": "Polygon", "type": "evm", "chain_id": 137},
    "arbitrum": {"name": "Arbitrum", "type": "evm", "chain_id": 42161},
    "solana": {"name": "Solana", "type": "non_evm", "chain_id": 0},
}


# ============================================================
# DATA MODELS
# ============================================================
@dataclass
class Order:
    order_id: str
    user_id: str
    pair: str
    side: str  # buy/sell
    order_type: str  # limit/market
    price: float
    amount: float
    filled: float
    status: str  # open/partial/filled/cancelled
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        return {
            "order_id": self.order_id,
            "user_id": self.user_id,
            "pair": self.pair,
            "side": self.side,
            "type": self.order_type,
            "price": self.price,
            "amount": self.amount,
            "filled": self.filled,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class Trade:
    trade_id: str
    pair: str
    side: str
    price: float
    amount: float
    maker_order_id: str
    taker_order_id: str
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        return {
            "trade_id": self.trade_id,
            "pair": self.pair,
            "side": self.side,
            "price": self.price,
            "amount": self.amount,
            "maker": self.maker_order_id,
            "taker": self.taker_order_id,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class LiquidityPool:
    pool_id: str
    pair: str
    token_a: str
    token_b: str
    reserve_a: float
    reserve_b: float
    liquidity: float
    chain: str
    
    def to_dict(self) -> Dict:
        return {
            "pool_id": self.pool_id,
            "pair": self.pair,
            "token_a": self.token_a,
            "token_b": self.token_b,
            "reserve_a": self.reserve_a,
            "reserve_b": self.reserve_b,
            "liquidity": self.liquidity,
            "chain": self.chain,
        }


@dataclass
class TradingPair:
    pair: str
    base: str
    quote: str
    min_order: float
    max_order: float
    tick_size: float
    lot_size: float
    maker_fee: float
    taker_fee: float
    status: str
    
    def to_dict(self) -> Dict:
        return {
            "pair": self.pair,
            "base": self.base,
            "quote": self.quote,
            "min_order": self.min_order,
            "max_order": self.max_order,
            "tick_size": self.tick_size,
            "lot_size": self.lot_size,
            "maker_fee": self.maker_fee,
            "taker_fee": self.taker_fee,
            "status": self.status,
        }


@dataclass
class MarketStats:
    pair: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    trades: int
    
    def to_dict(self) -> Dict:
        return {
            "pair": self.pair,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "trades": self.trades,
        }


# ============================================================
# EXCHANGE ENGINE
# ============================================================
class ExchangeService:
    """Full exchange engine"""
    
    def __init__(self):
        self.orders = {}
        self.trades = {}
        self.pools = {}
        self.pairs = {}
        self.user_balances = defaultdict(lambda: defaultdict(float))
        self.order_book = defaultdict(lambda: {"bids": [], "asks": []})
        self.market_stats = {}
        self.admin_actions = []
        self.admins = set()
        
        # Initialize exchange
        self._init_exchange()
        
        # Start market maker
        self._start_market_maker()
        
        logger.info("Custom Exchange Service initialized")
    
    def _init_exchange(self):
        """Initialize with sample data"""
        # Add trading pairs
        for pair in SUPPORTED_PAIRS:
            base, quote = pair.split('/')
            self.pairs[pair] = TradingPair(
                pair=pair,
                base=base,
                quote=quote,
                min_order=0.001,
                max_order=1000000,
                tick_size=0.01,
                lot_size=0.0001,
                maker_fee=0.001,
                taker_fee=0.002,
                status="active"
            )
            
            # Generate market stats
            self.market_stats[pair] = MarketStats(
                pair=pair,
                open=100.0 + hash(pair) % 100,
                high=110.0 + hash(pair) % 100,
                low=90.0 + hash(pair) % 100,
                close=100.0 + hash(pair) % 100,
                volume=float(1000000 + hash(pair) % 1000000),
                trades=1000 + hash(pair) % 10000
            )
            
            # Initialize order book
            self.order_book[pair] = {
                "bids": [{"price": 100 - i*0.1, "amount": 10 + i} for i in range(10)],
                "asks": [{"price": 100 + i*0.1, "amount": 10 + i} for i in range(10)],
            }
        
        # Add liquidity pools (for DEX)
        for i, chain in enumerate(["tigerex", "ethereum", "bsc"]):
            pool = LiquidityPool(
                pool_id=f"POOL_{i}",
                pair=f"TOKEN{i}A/TOKEN{i}B",
                token_a=f"TOKEN{i}A",
                token_b=f"TOKEN{i}B",
                reserve_a=1000000,
                reserve_b=1000000,
                liquidity=1000000,
                chain=chain
            )
            self.pools[pool.pool_id] = pool
        
        # Generate sample orders
        for i in range(50):
            pair = SUPPORTED_PAIRS[i % len(SUPPORTED_PAIRS)]
            side = "buy" if i % 2 == 0 else "sell"
            order = Order(
                order_id=f"ORDER_{i}",
                user_id=f"user_{i % 10}",
                pair=pair,
                side=side,
                order_type="limit",
                price=100.0 + (i % 10) * 0.1,
                amount=float(10 + i),
                filled=float(i % 10),
                status="open",
                timestamp=datetime.utcnow() - timedelta(hours=i)
            )
            self.orders[order.order_id] = order
    
    def _start_market_maker(self):
        """Simulate market making"""
        def make():
            while True:
                time.sleep(5)
                self._update_prices()
        
        threading.Thread(target=make, daemon=True).start()
    
    def _update_prices(self):
        """Update market prices"""
        for pair, stats in self.market_stats.items():
            # Simulate price movement
            change = (hash(pair) % 100 - 50) / 1000
            stats.close *= (1 + change)
            stats.high = max(stats.high, stats.close)
            stats.low = min(stats.low, stats.close)
    
    # --- Admin Methods ---
    
    def add_admin(self, admin_id: str):
        self.admins.add(admin_id)
    
    def is_admin(self, user_id: str) -> bool:
        return user_id in self.admins
    
    def set_mode(self, admin_id: str, mode: str) -> Dict:
        """Admin: Set exchange mode"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        if mode not in EXCHANGE_MODES:
            return {"error": "Invalid mode"}
        
        self.admin_actions.append({
            "action": "set_mode",
            "mode": mode,
            "admin_id": admin_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {"status": "set", "mode": mode}
    
    def add_trading_pair(self, admin_id: str, pair_data: Dict) -> Dict:
        """Admin: Add trading pair"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        pair = TradingPair(
            pair=pair_data.get("pair", ""),
            base=pair_data.get("base", ""),
            quote=pair_data.get("quote", ""),
            min_order=pair_data.get("min_order", 0.001),
            max_order=pair_data.get("max_order", 1000000),
            tick_size=pair_data.get("tick_size", 0.01),
            lot_size=pair_data.get("lot_size", 0.0001),
            maker_fee=pair_data.get("maker_fee", 0.001),
            taker_fee=pair_data.get("taker_fee", 0.002),
            status=pair_data.get("status", "active")
        )
        
        self.pairs[pair.pair] = pair
        self.order_book[pair.pair] = {"bids": [], "asks": []}
        
        self.admin_actions.append({
            "action": "add_pair",
            "pair": pair.pair,
            "admin_id": admin_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {"status": "added", "pair": pair.pair}
    
    def remove_trading_pair(self, admin_id: str, pair: str) -> Dict:
        """Admin: Remove trading pair"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        if pair in self.pairs:
            self.pairs[pair].status = "suspended"
        
        self.admin_actions.append({
            "action": "remove_pair",
            "pair": pair,
            "admin_id": admin_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {"status": "removed", "pair": pair}
    
    def adjust_fees(self, admin_id: str, pair: str, maker_fee: float, taker_fee: float) -> Dict:
        """Admin: Adjust trading fees"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        if pair in self.pairs:
            self.pairs[pair].maker_fee = maker_fee
            self.pairs[pair].taker_fee = taker_fee
        
        self.admin_actions.append({
            "action": "adjust_fees",
            "pair": pair,
            "maker_fee": maker_fee,
            "taker_fee": taker_fee,
            "admin_id": admin_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {"status": "adjusted", "pair": pair, "maker": maker_fee, "taker": taker_fee}
    
    def add_liquidity_pool(self, admin_id: str, pool_data: Dict) -> Dict:
        """Admin: Add liquidity pool"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        pool = LiquidityPool(
            pool_id=pool_data.get("pool_id", f"POOL_{uuid.uuid4().hex[:8]}"),
            pair=pool_data.get("pair", ""),
            token_a=pool_data.get("token_a", ""),
            token_b=pool_data.get("token_b", ""),
            reserve_a=pool_data.get("reserve_a", 0),
            reserve_b=pool_data.get("reserve_b", 0),
            liquidity=pool_data.get("liquidity", 0),
            chain=pool_data.get("chain", "tigerex")
        )
        
        self.pools[pool.pool_id] = pool
        
        self.admin_actions.append({
            "action": "add_pool",
            "pool": pool.pool_id,
            "admin_id": admin_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {"status": "added", "pool": pool.pool_id}
    
    def cancel_order_admin(self, admin_id: str, order_id: str) -> Dict:
        """Admin: Cancel any order"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        if order_id in self.orders:
            self.orders[order_id].status = "cancelled"
        
        self.admin_actions.append({
            "action": "cancel_order",
            "order": order_id,
            "admin_id": admin_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {"status": "cancelled", "order_id": order_id}
    
    def adjust_user_balance(self, admin_id: str, user_id: str, asset: str, amount: float) -> Dict:
        """Admin: Adjust user balance"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        self.user_balances[user_id][asset] += amount
        
        self.admin_actions.append({
            "action": "adjust_balance",
            "user": user_id,
            "asset": asset,
            "amount": amount,
            "admin_id": admin_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {"status": "adjusted", "user": user_id, "balance": self.user_balances[user_id][asset]}
    
    def get_all_orders(self, admin_id: str, limit: int = 100) -> List[Dict]:
        """Admin: Get all orders"""
        if not self.is_admin(admin_id):
            return []
        
        orders = sorted(self.orders.values(), key=lambda o: o.timestamp, reverse=True)
        return [o.to_dict() for o in orders[:limit]]
    
    def get_all_trades(self, admin_id: str, limit: int = 100) -> List[Dict]:
        """Admin: Get all trades"""
        if not self.is_admin(admin_id):
            return []
        
        trades = sorted(self.trades.values(), key=lambda t: t.timestamp, reverse=True)
        return [t.to_dict() for t in trades[:limit]]
    
    def get_all_pools(self, admin_id: str) -> List[Dict]:
        """Admin: Get all pools"""
        if not self.is_admin(admin_id):
            return []
        
        return [p.to_dict() for p in self.pools.values()]
    
    def get_all_pairs(self, admin_id: str) -> List[Dict]:
        """Admin: Get all trading pairs"""
        if not self.is_admin(admin_id):
            return []
        
        return [p.to_dict() for p in self.pairs.values()]
    
    def get_admin_actions(self, admin_id: str, limit: int = 50) -> List[Dict]:
        """Admin: Get admin actions"""
        if not self.is_admin(admin_id):
            return []
        
        return sorted(self.admin_actions, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def get_exchange_stats(self, admin_id: str) -> Dict:
        """Admin: Get exchange statistics"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        return {
            "total_orders": len(self.orders),
            "active_orders": sum(1 for o in self.orders.values() if o.status == "open"),
            "total_trades": len(self.trades),
            "total_pairs": len(self.pairs),
            "active_pairs": sum(1 for p in self.pairs.values() if p.status == "active"),
            "total_pools": len(self.pools),
            "supported_chains": len(BLOCKCHAINS),
        }
    
    def get_order_book(self, admin_id: str, pair: str) -> Dict:
        """Admin: Get order book"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        return self.order_book.get(pair, {"bids": [], "asks": []})
    
    # --- User Methods ---
    
    def create_order(self, user_id: str, pair: str, side: str, order_type: str, price: float, amount: float) -> Dict:
        """User: Create order"""
        if pair not in self.pairs:
            return {"error": "Trading pair not found"}
        
        pair_obj = self.pairs[pair]
        if pair_obj.status != "active":
            return {"error": "Trading pair not active"}
        
        order_id = f"ORDER_{uuid.uuid4().hex[:12]}"
        order = Order(
            order_id=order_id,
            user_id=user_id,
            pair=pair,
            side=side,
            order_type=order_type,
            price=price,
            amount=amount,
            filled=0,
            status="open",
            timestamp=datetime.utcnow()
        )
        
        self.orders[order_id] = order
        
        # Add to order book
        if side == "buy":
            self.order_book[pair]["bids"].append({"price": price, "amount": amount})
        else:
            self.order_book[pair]["asks"].append({"price": price, "amount": amount})
        
        return {"order_id": order_id, "status": "open", "price": price, "amount": amount}
    
    def cancel_order(self, user_id: str, order_id: str) -> Dict:
        """User: Cancel order"""
        if order_id not in self.orders:
            return {"error": "Order not found"}
        
        order = self.orders[order_id]
        if order.user_id != user_id:
            return {"error": "Not your order"}
        
        order.status = "cancelled"
        
        return {"status": "cancelled", "order_id": order_id}
    
    def get_order(self, order_id: str) -> Dict:
        """Get order"""
        if order_id in self.orders:
            return self.orders[order_id].to_dict()
        return {"error": "Order not found"}
    
    def get_orders(self, user_id: str, pair: str = "") -> List[Dict]:
        """Get user orders"""
        orders = [o for o in self.orders.values() if o.user_id == user_id]
        if pair:
            orders = [o for o in orders if o.pair == pair]
        return [o.to_dict() for o in orders]
    
    def get_order_book(self, pair: str) -> Dict:
        """Get order book"""
        return self.order_book.get(pair, {"bids": [], "asks": []})
    
    def get_market_stats(self, pair: str) -> Dict:
        """Get market stats"""
        if pair in self.market_stats:
            return self.market_stats[pair].to_dict()
        return {"error": "Pair not found"}
    
    def get_all_pairs(self) -> List[Dict]:
        """Get all pairs"""
        return [p.to_dict() for p in self.pairs.values()]
    
    def get_trading_pair(self, pair: str) -> Dict:
        """Get trading pair"""
        if pair in self.pairs:
            return self.pairs[pair].to_dict()
        return {"error": "Pair not found"}
    
    def get_user_balance(self, user_id: str, asset: str = "") -> Dict:
        """Get user balance"""
        if asset:
            return {asset: self.user_balances[user_id].get(asset, 0)}
        return dict(self.user_balances[user_id])
    
    def get_pools(self, chain: str = "") -> List[Dict]:
        """Get liquidity pools"""
        pools = list(self.pools.values())
        if chain:
            pools = [p for p in pools if p.chain == chain]
        return [p.to_dict() for p in pools]
    
    def add_liquidity(self, user_id: str, pool_id: str, amount_a: float, amount_b: float) -> Dict:
        """User: Add liquidity"""
        if pool_id not in self.pools:
            return {"error": "Pool not found"}
        
        pool = self.pools[pool_id]
        pool.reserve_a += amount_a
        pool.reserve_b += amount_b
        
        return {"status": "added", "pool": pool_id, "token_a": amount_a, "token_b": amount_b}
    
    def remove_liquidity(self, user_id: str, pool_id: str, liquidity: float) -> Dict:
        """User: Remove liquidity"""
        if pool_id not in self.pools:
            return {"error": "Pool not found"}
        
        pool = self.pools[pool_id]
        
        amount_a = liquidity * (pool.reserve_a / pool.liquidity)
        amount_b = liquidity * (pool.reserve_b / pool.liquidity)
        
        pool.reserve_a -= amount_a
        pool.reserve_b -= amount_b
        pool.liquidity -= liquidity
        
        return {"status": "removed", "pool": pool_id, "token_a": amount_a, "token_b": amount_b}


# ============================================================
# FLASK APPS
# ============================================================
from flask import Flask, jsonify, request
from flask_cors import CORS

admin_app = Flask(__name__)
CORS(admin_app)

exchange_service = ExchangeService()
exchange_service.add_admin("admin001")

#
# Admin Routes
#
@admin_app.route('/exchange/admin/health')
def admin_health():
    return jsonify({"status": "ok", "service": "exchange", "role": "admin"})

@admin_app.route('/exchange/admin/mode', methods=['POST'])
def admin_set_mode():
    data = request.get_json() or {}
    return jsonify(exchange_service.set_mode(
        data.get('admin_id', ''),
        data.get('mode', 'cex')
    ))

@admin_app.route('/exchange/admin/add-pair', methods=['POST'])
def admin_add_pair():
    data = request.get_json() or {}
    return jsonify(exchange_service.add_trading_pair(
        data.get('admin_id', ''),
        data.get('pair_data', {})
    ))

@admin_app.route('/exchange/admin/remove-pair', methods=['POST'])
def admin_remove_pair():
    data = request.get_json() or {}
    return jsonify(exchange_service.remove_trading_pair(
        data.get('admin_id', ''),
        data.get('pair', '')
    ))

@admin_app.route('/exchange/admin/adjust-fees', methods=['POST'])
def admin_adjust_fees():
    data = request.get_json() or {}
    return jsonify(exchange_service.adjust_fees(
        data.get('admin_id', ''),
        data.get('pair', ''),
        data.get('maker_fee', 0),
        data.get('taker_fee', 0)
    ))

@admin_app.route('/exchange/admin/add-pool', methods=['POST'])
def admin_add_pool():
    data = request.get_json() or {}
    return jsonify(exchange_service.add_liquidity_pool(
        data.get('admin_id', ''),
        data.get('pool_data', {})
    ))

@admin_app.route('/exchange/admin/cancel-order', methods=['POST'])
def admin_cancel_order():
    data = request.get_json() or {}
    return jsonify(exchange_service.cancel_order_admin(
        data.get('admin_id', ''),
        data.get('order_id', '')
    ))

@admin_app.route('/exchange/admin/adjust-balance', methods=['POST'])
def admin_adjust_balance():
    data = request.get_json() or {}
    return jsonify(exchange_service.adjust_user_balance(
        data.get('admin_id', ''),
        data.get('user_id', ''),
        data.get('asset', ''),
        data.get('amount', 0)
    ))

@admin_app.route('/exchange/admin/all-orders')
def admin_orders():
    admin_id = request.args.get('admin_id', '')
    limit = request.args.get('limit', 100, type=int)
    return jsonify(exchange_service.get_all_orders(admin_id, limit))

@admin_app.route('/exchange/admin/all-trades')
def admin_trades():
    admin_id = request.args.get('admin_id', '')
    limit = request.args.get('limit', 100, type=int)
    return jsonify(exchange_service.get_all_trades(admin_id, limit))

@admin_app.route('/exchange/admin/all-pools')
def admin_pools():
    admin_id = request.args.get('admin_id', '')
    return jsonify(exchange_service.get_all_pools(admin_id))

@admin_app.route('/exchange/admin/all-pairs')
def admin_pairs():
    admin_id = request.args.get('admin_id', '')
    return jsonify(exchange_service.get_all_pairs(admin_id))

@admin_app.route('/exchange/admin/actions')
def admin_actions():
    admin_id = request.args.get('admin_id', '')
    return jsonify(exchange_service.get_admin_actions(admin_id))

@admin_app.route('/exchange/admin/stats')
def admin_stats():
    admin_id = request.args.get('admin_id', '')
    return jsonify(exchange_service.get_exchange_stats(admin_id))

@admin_app.route('/exchange/admin/order-book')
def admin_order_book():
    admin_id = request.args.get('admin_id', '')
    pair = request.args.get('pair', '')
    return jsonify(exchange_service.get_order_book(admin_id, pair))


def run_admin():
    port = int(os.environ.get('PORT', 6400))
    logger.info(f"Starting Admin Exchange Service on port {port}")
    admin_app.run(host='0.0.0.0', port=port, threaded=True)


if __name__ == '__main__':
    run_admin()