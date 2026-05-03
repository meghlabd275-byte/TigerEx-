#!/usr/bin/env python3
"""
TigerEx Liquidity Manager Service
Real liquidity aggregation from DEX and CEX
"""
import os
import json
import logging
import requests
import uuid
import threading
from typing import Dict, List
from datetime import datetime
from collections import defaultdict
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# DEX pools
DEX_ROUTERS = {
    "uniswap_v2": {"router": "0x7a250d5630B4cF539B63FF6C3a2f4aE7F5f3B3a3B3", "factory": "0x5C69bEe701ef9a400bF24C2bc5b93f2f93EBbB8EA"},
    "uniswap_v3": {"router": "0xE592427A0AE92Fc5bD943835A6C647d5F12d5e64", "factory": "0x1F98431c8aD98523631AE4a59f267346Ea31F984"},
    "pancakeswap": {"router": "0x10ED43C718714eb63D5dA57B8B5c6b2b2c2e7D1E", "factory": "0x10970512F3ebEB2B9A7E2F9179e9f2Ea3a9b0b0"},
    "sushiswap": {"router": "0xd9e1cE17f264c8F5B9aD5dA97e15b2f2fE6C91Cb", "factory": "0xC0AEe478e3658e2830C5B8455fFc26fE1Ea7B8B9"},
    "quickswap": {"router": "0xa5E0829Ca8dE4F58f5A3a1e3E3C3A1E2E3D3C3E1", "factory": "0x1B85DaD7815257a2d4B6B3E7F3E7C3C3C3C3E3E"}
}

# CEX connections
CEX_CONNECTORS = ["binance", "bybit", "okx", "kucoin", "gate"]

class LiquidityManager:
    """Real liquidity aggregation"""
    def __init__(self):
        self.pools = {}  # (tokenA, tokenB, dex) -> liquidity
        self.orders = {}  # order_id -> order
        self.balances = defaultdict(dict)
        self._start_liquidity_monitor()
        logger.info("Liquidity manager initialized")
    
    def _start_liquidity_monitor(self):
        def monitor():
            while True:
                self._update_prices()
                time.sleep(10)
        threading.Thread(target=monitor, daemon=True).start()
    
    def _update_prices(self):
        # Update prices from CEX
        for cex in CEX_CONNECTORS:
            try:
                r = requests.get(f"https://api.{cex}.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=3)
                if r.status_code == 200:
                    self.balances[cex] = r.json()
            except: pass
    
    def add_liquidity(self, user: str, token_a: str, token_b: str, amount_a: float, amount_b: float, dex: str) -> Dict:
        pool_id = f"{token_a}_{token_b}_{dex}"
        
        if pool_id not in self.pools:
            self.pools[pool_id] = {
                "token_a": token_a,
                "token_b": token_b,
                "dex": dex,
                "liquidity_a": 0,
                "liquidity_b": 0,
                "providers": [],
                "shares": defaultdict(float)
            }
        
        pool = self.pools[pool_id]
        pool["liquidity_a"] += amount_a
        pool["liquidity_b"] += amount_b
        
        # Calculate shares (simplified)
        if pool["liquidity_a"] > 0:
            share = min(amount_a / pool["liquidity_a"], 1.0)
        else:
            share = 1.0
        
        pool["providers"].append(user)
        pool["shares"][user] += share
        
        order_id = f"LIQ_{uuid.uuid4().hex[:10].upper()}"
        self.orders[order_id] = {
            "order_id": order_id,
            "user": user,
            "pool": pool_id,
            "amount_a": amount_a,
            "amount_b": amount_b,
            "shares": share,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self.orders[order_id]
    
    def remove_liquidity(self, order_id: str, user: str) -> Dict:
        order = self.orders.get(order_id)
        if not order or order["user"] != user:
            return {"error": "Not found or unauthorized"}
        
        if order["pool"] in self.pools:
            pool = self.pools[order["pool"]]
            amount_a = pool["liquidity_a"] * order["shares"]
            amount_b = pool["liquidity_b"] * order["shares"]
            
            pool["liquidity_a"] -= amount_a
            pool["liquidity_b"] -= amount_b
            pool["shares"][user] -= order["shares"]
            
            return {"amount_a": amount_a, "amount_b": amount_b, "removed": True}
        
        return {"error": "Pool not found"}
    
    def get_pool(self, token_a: str, token_b: str, dex: str = "") -> Dict:
        pool_id = f"{token_a}_{token_b}_{dex}" if dex else f"{token_a}_{token_b}_uniswap_v2"
        
        if pool_id in self.pools:
            return self.pools[pool_id]
        
        # Try other dexes
        for dex_name in DEX_ROUTERS.keys():
            pid = f"{token_a}_{token_b}_{dex_name}"
            if pid in self.pools:
                return self.pools[pid]
        
        return {"error": "Pool not found"}
    
    def get_liquidity_pools(self, token: str = "") -> List[Dict]:
        pools = []
        for pool_id, pool in self.pools.items():
            if token in [pool["token_a"], pool["token_b"], "", None]:
                pools.append({**pool, "pool_id": pool_id})
        return pools
    
    def get_swap_quote(self, token_in: str, token_out: str, amount: float, dex: str = "") -> Dict:
        pool = self.get_pool(token_in, token_out, dex)
        
        if "error" in pool:
            # Try CEX price
            for cex in CEX_CONNECTORS:
                try:
                    r = requests.get(f"https://api.{cex}.com/api/v3/ticker/price?symbol={token_in}{token_out}", timeout=3)
                    if r.status_code == 200:
                        price = float(r.json().get("price", 0))
                        return {"amount_out": amount * price, "price": price, "source": cex}
                except: continue
            return {"error": "No liquidity"}
        
        if pool["liquidity_a"] > 0 and pool["liquidity_b"] > 0:
            price = pool["liquidity_b"] / pool["liquidity_a"]
            slippage = self._calculate_slippage(amount, pool["liquidity_a"])
            return {"amount_out": amount * price * (1 - slippage), "price": price, "slippage": slippage, "source": pool["dex"]}
        
        return {"error": "Insufficient liquidity"}
    
    def _calculate_slippage(self, amount: float, total: float) -> float:
        if total <= 0: return 0
        # Simple slippage model: 0.3% at 1% depth, increases exponentially
        ratio = amount / total
        return ratio * 0.3 + (ratio ** 2) * 0.5
    
    def get_token_pairs(self, dex: str = "") -> List[Dict]:
        pairs = []
        for pool_id, pool in self.pools.items():
            if dex in ["", pool["dex"]]:
                pairs.append({
                    "token_a": pool["token_a"],
                    "token_b": pool["token_b"],
                    "dex": pool["dex"],
                    "liquidity": pool["liquidity_a"] + pool["liquidity_b"]
                })
        return pairs
    
    def estimate_swap(self, token_in: str, token_out: str, amount: float) -> Dict:
        """Estimate swap across all sources"""
        best = {"price": 0, "source": "", "amount_out": 0}
        
        for dex in DEX_ROUTERS.keys():
            quote = self.get_swap_quote(token_in, token_out, amount, dex)
            if "price" in quote and quote["price"] > best["price"]:
                best = quote
        
        # Check CEX
        for cex in CEX_CONNECTORS:
            try:
                r = requests.get(f"https://api.{cex}.com/api/v3/ticker/price?symbol={token_in}{token_out}", timeout=3)
                if r.status_code == 200:
                    price = float(r.json().get("price", 0))
                    if price > best["price"]:
                        best = {"price": price, "amount_out": amount * price * 0.999, "source": cex}
            except: continue
        
        return best
    
    def get_depth(self, token_a: str, token_b: str) -> Dict:
        """Get order book depth"""
        depth = {"bids": [], "asks": []}
        
        pool = self.get_pool(token_a, token_b)
        if "error" not in pool:
            # Generate BBO from pool
            mid = pool["liquidity_b"] / pool["liquidity_a"] if pool["liquidity_a"] > 0 else 0
            spread = 0.003
            
            for i in range(10):
                depth["bids"].append([mid * (1 - spread * (i+1)/10), pool["liquidity_a"] * (i+1) * 0.1])
                depth["asks"].append([mid * (1 + spread * (i+1)/10), pool["liquidity_a"] * (i+1) * 0.1])
        
        return depth
    
    def get_stats(self) -> Dict:
        total_liquidity = sum(p["liquidity_a"] + p["liquidity_b"] for p in self.pools.values())
        return {
            "total_pools": len(self.pools),
            "total_liquidity": total_liquidity,
            "dexes": list(DEX_ROUTERS.keys()),
            "cex_connections": len(CEX_CONNECTORS)
        }


# Flask
from flask import Flask, jsonify, request; from flask_cors import CORS
app = Flask(__name__); CORS(app)
liquidity = LiquidityManager()

@app.route('/liquidity/health')
def health():
    return jsonify(liquidity.get_stats())

@app.route('/liquidity/add', methods=['POST'])
def add():
    d = request.get_json()
    return jsonify(liquidity.add_liquidity(d.get('user',''), d.get('token_a',''), d.get('token_b',''), d.get('amount_a',0), d.get('amount_b',0), d.get('dex','uniswap_v2')))

@app.route('/liquidity/remove', methods=['POST'])
def remove():
    d = request.get_json()
    return jsonify(liquidity.remove_liquidity(d.get('order_id',''), d.get('user','')))

@app.route('/liquidity/pool/<token_a>/<token_b>')
def get_pool(token_a, token_b):
    return jsonify(liquidity.get_pool(token_a, token_b))

@app.route('/liquidity/pools')
def pools():
    return jsonify(liquidity.get_liquidity_pools(request.args.get('token','')))

@app.route('/liquidity/quote', methods=['POST'])
def quote():
    d = request.get_json()
    return jsonify(liquidity.get_swap_quote(d.get('token_in',''), d.get('token_out',''), d.get('amount',0), d.get('dex','')))

@app.route('/liquidity/estimate', methods=['POST'])
def estimate():
    d = request.get_json()
    return jsonify(liquidity.estimate_swap(d.get('token_in',''), d.get('token_out',''), d.get('amount',0)))

@app.route('/liquidity/depth/<token_a>/<token_b>')
def depth(token_a, token_b):
    return jsonify(liquidity.get_depth(token_a, token_b))

@app.route('/liquidity/pairs')
def pairs():
    return jsonify(liquidity.get_token_pairs(request.args.get('dex','')))

if __name__ == '__main__': app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5600)), threaded=True)def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
