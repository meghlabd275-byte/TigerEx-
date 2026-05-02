#!/usr/bin/env python3
"""TigerEx Custom Exchange Backend - CEX + DEX Hybrid"""
import os, logging, uuid
from typing import Dict, defaultdict
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CONFIG = {"name": "TigerEx", "fee_maker": 0.001, "fee_taker": 0.002}

class OrderBook:
    def __init__(self, pair): self.pair = pair; self.bids, self.asks = [], []
    def add(self, o):
        (self.bids if o['side']=='buy' else self.asks).append(o)
        self.bids.sort(key=lambda x: x['price'], reverse=True)
        self.asks.sort(key=lambda x: x['price'])
        return []

class Exchange:
    def __init__(self):
        self.books, self.orders, self.balances = {}, {}, defaultdict(lambda: defaultdict(float))
        for u in ['u1','u2']: self.balances[u]['TIG']=10000; self.balances[u]['USDC']=50000
    def create(self, uid): return {"user_id": uid}
    def deposit(self, uid, a, amt): self.balances[uid][a] += amt; return {"tx": amt}
    def withdraw(self, uid, a, amt):
        if self.balances[uid][a] < amt: return {"error": "low_balance"}
        self.balances[uid][a] -= amt; return {"tx": amt}
    def place(self, uid, pair, side, price, qty):
        o = {'id': f"ORD{uuid.uuid4().hex[:8]}", 'user_id': uid, 'pair': pair, 'side': side, 'price': price, 'quantity': qty, 'remaining': qty}
        self.orders[o['id']] = o
        if pair not in self.books: self.books[pair] = OrderBook(pair)
        return {"order": o}
    def cancel(self, oid, uid): 
        o = self.orders.get(oid)
        if o and o['user_id'] == uid: o['status']='cancelled'; return {"ok": True}
        return {"error": "not_found"}
    def balance(self, uid): return dict(self.balances[uid])
    def book(self, pair): b = self.books.get(pair); return {'bids': [], 'asks': []}

from flask import Flask, jsonify, request
app = Flask(__name__)

ex = Exchange()

@app.route('/health')
def health(): return jsonify({"status": "ok"})

@app.route('/account', methods=['POST'])
def create(): return jsonify(ex.create(request.json.get('user_id','u1') if request.is_json else ex.create('u1')))

@app.route('/deposit', methods=['POST'])
def deposit(): 
    if request.is_json:
        d = request.json
        return jsonify(ex.deposit(d.get('user_id','u1'), d.get('asset','TIG'), d.get('amount',0)))
    return jsonify(ex.deposit('u1','TIG',0))

@app.route('/withdraw', methods=['POST'])
def withdraw():
    if request.is_json:
        d = request.json
        return jsonify(ex.withdraw(d.get('user_id','u1'), d.get('asset'), d.get('amount',0)))
    return jsonify({"error": "no_data"})

@app.route('/order', methods=['POST'])
def place_order():
    if request.is_json:
        d = request.json
        return jsonify(ex.place(d.get('user_id','u1'), d.get('pair','TIG/USDC'), d.get('side','buy'), d.get('price',0), d.get('quantity',0)))
    return jsonify({"error": "no_data"})

@app.route('/order/<oid>', methods=['DELETE'])
def cancel(oid): return jsonify(ex.cancel(oid, request.headers.get('X-User-Id','u1')))

@app.route('/balance/<uid>')
def balance(uid): return jsonify(ex.balance(uid))

@app.route('/book/<pair>')
def book(pair): return jsonify(ex.book(pair))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5900, threaded=True)
