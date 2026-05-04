#!/usr/bin/env python3
"""Block Explorer - Full Backend"""
from flask import Flask, jsonify, request
import uuid, time

app = Flask(__name__)
blocks, transactions = {}, {}

@app.route('/api/admin/health')
def admin_health(): return jsonify({"status": "ok"})
@app.route('/api/admin/stats')
def admin_stats(): return jsonify({"blocks": len(blocks), "transactions": len(transactions)})
@app.route('/api/user/health')
def user_health(): return jsonify({"status": "ok"})
@app.route('/api/user/block/<block_num>')
def get_block(block_num): return jsonify({"block": int(block_num), "hash": f"0x{uuid.uuid4().hex}"})
@app.route('/api/user/tx/<tx_hash>')
def get_tx(tx_hash): return jsonify({"tx_hash": tx_hash, "status": "confirmed"})
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6700)