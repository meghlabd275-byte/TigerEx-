#!/usr/bin/env python3
from flask import Flask, jsonify, request
import uuid, time

app = Flask(__name__)

EXPLORERS = {
    "ethereum": {"name": "Ethereum", "type": "evm"},
    "bsc": {"name": "BNB Chain", "type": "evm"},
    "polygon": {"name": "Polygon", "type": "evm"},
    "avalanche": {"name": "Avalanche", "type": "evm"},
    "solana": {"name": "Solana", "type": "non-evm"},
    "cardano": {"name": "Cardano", "type": "non-evm"},
    "near": {"name": "NEAR", "type": "non-evm"},
    "aptos": {"name": "Aptos", "type": "non-evm"},
}

blocks_db, txs_db, tokens = {}, {}, {}

@app.route('/api/admin/health')
def a_health(): return jsonify({"status": "ok"})

@app.route('/api/admin/explorers', methods=['GET'])
def a_explorers(): return jsonify({"explorers": EXPLORERS})

@app.route('/api/admin/blocks', methods=['GET'])
def a_blocks(): return jsonify({"blocks": blocks_db})

@app.route('/api/admin/txs', methods=['GET'])
def a_txs(): return jsonify({"transactions": txs_db})

@app.route('/api/admin/reindex', methods=['POST'])
def a_reindex():
    data = request.get_json()
    return jsonify({"status": "reindexed", "chain": data.get('chain')})

@app.route('/api/admin/token', methods=['POST'])
def a_add_token():
    data = request.get_json()
    tokens[data['address']] = data
    return jsonify({"status": "added"})

@app.route('/api/admin/stats')
def a_stats(): return jsonify({"explorers": len(EXPLORERS), "blocks": len(blocks_db), "txs": len(txs_db), "tokens": len(tokens)})

@app.route('/api/user/health')
def u_health(): return jsonify({"status": "ok"})

@app.route('/api/user/explorers')
def u_explorers(): return jsonify({"explorers": EXPLORERS})

@app.route('/api/user/block/<chain>/<int:block>')
def u_block(chain, block): return jsonify({"chain": chain, "block": block})

@app.route('/api/user/tx/<tx_hash>')
def u_tx(tx_hash): return jsonify({"tx_hash": tx_hash, "status": "confirmed"})

@app.route('/api/user/address/<addr>')
def u_address(addr): return jsonify({"address": addr})

@app.route('/api/user/gas/<chain>')
def u_gas(chain): return jsonify({"gas": {"slow": 10, "normal": 20, "fast": 50}})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6300)