#!/usr/bin/env python3
"""Custom Blockchain Service - EVM + Non-EVM"""
from flask import Flask, jsonify, request
import uuid, time, random, hashlib

app = Flask(__name__)

CHAINS = {
    "ethereum": {"name": "Ethereum", "symbol": "ETH", "type": "evm"},
    "bsc": {"name": "BNB Chain", "symbol": "BNB", "type": "evm"},
    "polygon": {"name": "Polygon", "symbol": "MATIC", "type": "evm"},
    "avalanche": {"name": "Avalanche", "symbol": "AVAX", "type": "evm"},
    "solana": {"name": "Solana", "symbol": "SOL", "type": "non-evm"},
    "cardano": {"name": "Cardano", "symbol": "ADA", "type": "non-evm"},
    "near": {"name": "NEAR", "symbol": "NEAR", "type": "non-evm"},
    "aptos": {"name": "Aptos", "symbol": "APT", "type": "non-evm"},
    "sui": {"name": "Sui", "symbol": "SUI", "type": "non-evm"},
    "polkadot": {"name": "Polkadot", "symbol": "DOT", "type": "non-evm"},
}

blocks = {}
transactions = {}
validators = {}
accounts = {}
gas_prices = {}

# Admin
@app.route('/api/admin/health')
def admin_health(): return jsonify({"status": "ok", "service": "custom-blockchain", "role": "admin"})

@app.route('/api/admin/chains', methods=['GET'])
def admin_chains(): return jsonify({"chains": CHAINS})

@app.route('/api/admin/chain', methods=['POST'])
def create_chain():
    data = request.get_json()
    chain_id = data.get('chain_id')
    CHAINS[chain_id] = {"name": data.get('name'), "symbol": data.get('symbol'), "type": data.get('type', 'evm')}
    return jsonify({"status": "created", "chain": chain_id})

@app.route('/api/admin/blocks', methods=['GET'])
def get_blocks(): return jsonify({"blocks": blocks, "count": len(blocks)})

@app.route('/api/admin/block/<chain_id>', methods=['GET'])
def get_chain_blocks(chain_id):
    chain_blocks = {k: v for k, v in blocks.items() if v.get('chain') == chain_id}
    return jsonify({"blocks": chain_blocks})

@app.route('/api/admin/validator', methods=['POST'])
def add_validator():
    data = request.get_json()
    vid = f"validator_{uuid.uuid4().hex[:8]}"
    validators[vid] = {"validator_id": vid, "address": data.get('address'), "stake": data.get('stake', 1000), "status": "active", "added_at": time.time()}
    return jsonify({"status": "created", "validator": validators[vid]})

@app.route('/api/admin/gas', methods=['POST'])
def set_gas():
    data = request.get_json()
    chain = data.get('chain')
    gas = data.get('gas_price')
    gas_prices[chain] = gas
    return jsonify({"status": "set", "chain": chain, "gas_price": gas})

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    return jsonify({"total_blocks": len(blocks), "total_txs": len(transactions), "validators": len(validators), "accounts": len(accounts), "chains": len(CHAINS)})

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    return jsonify({"status": "logged_in", "session_id": f"s_{uuid.uuid4().hex}"})

# User
@app.route('/api/user/health')
def user_health(): return jsonify({"status": "ok", "service": "custom-blockchain", "role": "user"})

@app.route('/api/user/account', methods=['POST'])
def create_account():
    data = request.get_json()
    aid = f"acc_{uuid.uuid4().hex[:12]}"
    accounts[aid] = {"account_id": aid, "address": f"0x{uuid.uuid4().hex[2:42]}", "chain": data.get('chain', 'ethereum'), "created_at": time.time(), "nonce": 0}
    return jsonify({"status": "created", "account": accounts[aid]})

@app.route('/api/user/account/<account_id>', methods=['GET'])
def get_account(account_id):
    return jsonify(accounts.get(account_id, {"error": "Not found"}))

@app.route('/api/user/accounts', methods=['GET'])
def get_accounts(): return jsonify({"accounts": accounts})

@app.route('/api/user/send', methods=['POST'])
def send_tx():
    data = request.get_json()
    tx_id = f"tx_{uuid.uuid4().hex[:16]}"
    tx = {"tx_id": tx_id, "from": data.get('from'), "to": data.get('to'), "value": data.get('value'), "data": data.get('data', ''), "chain": data.get('chain'), "status": "pending", "timestamp": time.time()}
    transactions[tx_id] = tx
    return jsonify({"status": "pending", "tx": tx})

@app.route('/api/user/tx/<tx_id>', methods=['GET'])
def get_tx(tx_id): return jsonify(transactions.get(tx_id, {"error": "Not found"}))

@app.route('/api/user/gas/<chain>', methods=['GET'])
def get_gas(chain): return jsonify({"gas_price": gas_prices.get(chain, random.randint(10, 100))})

@app.route('/api/user/chains', methods=['GET'])
def user_chains(): return jsonify({"chains": CHAINS})

@app.route('/api/user/block/<chain_id>/latest', methods=['GET'])
def latest_block(chain_id):
    chain_blocks = {k: v for k, v in blocks.items() if v.get('chain') == chain_id}
    if chain_blocks: return jsonify({"block": list(chain_blocks.values())[-1]})
    return jsonify({"block": None})

@app.route('/api/user/login', methods=['POST'])
def user_login():
    data = request.get_json()
    return jsonify({"status": "logged_in", "session_id": f"s_{uuid.uuid4().hex}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6200)