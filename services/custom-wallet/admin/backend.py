#!/usr/bin/env python3
"""
Custom Wallet Service - EVM + Non-EVM Support
Admin + User Backends
"""
from flask import Flask, jsonify, request
import uuid
import time
import hashlib
import threading

app = Flask(__name__)

# Supported Chains
CHAINS = {
    # EVM Chains
    "ethereum": {"name": "Ethereum", "symbol": "ETH", "type": "evm", " decimals": 18},
    "bsc": {"name": "BNB Smart Chain", "symbol": "BNB", "type": "evm", "decimals": 18},
    "polygon": {"name": "Polygon", "symbol": "MATIC", "type": "evm", "decimals": 18},
    "avalanche": {"name": "Avalanche", "symbol": "AVAX", "type": "evm", "decimals": 18},
    "fantom": {"name": "Fantom", "symbol": "FTM", "type": "evm", "decimals": 18},
    "arbitrum": {"name": "Arbitrum", "symbol": "ETH", "type": "evm", "decimals": 18},
    "optimism": {"name": "Optimism", "symbol": "ETH", "type": "evm", "decimals": 18},
    "solana": {"name": "Solana", "symbol": "SOL", "type": "non-evm", "decimals": 9},
    "cardano": {"name": "Cardano", "symbol": "ADA", "type": "non-evm", "decimals": 6},
    "polkadot": {"name": "Polkadot", "symbol": "DOT", "type": "non-evm", "decimals": 10},
    "near": {"name": "NEAR", "symbol": "NEAR", "type": "non-evm", "decimals": 24},
    "aptos": {"name": "Aptos", "symbol": "APT", "type": "non-evm", "decimals": 8},
    "sui": {"name": "Sui", "symbol": "SUI", "type": "non-evm", "decimals": 9},
    "ton": {"name": "Toncoin", "symbol": "TON", "type": "non-evm", "decimals": 9},
    "tron": {"name": "Tron", "symbol": "TRX", "type": "non-evm", "decimals": 6},
    "xrp": {"name": "XRP", "symbol": "XRP", "type": "non-evm", "decimals": 6},
}

# Storage
wallets = {}
transactions = {}
balances = {}
admins = {"admin": {"password": "admin123", "role": "admin"}}
users = {}
user_sessions = {}

# Admin Backend
@app.route('/api/admin/health')
def admin_health():
    return jsonify({"status": "ok", "service": "custom-wallet", "role": "admin"})

@app.route('/api/admin/wallets', methods=['GET'])
def admin_get_wallets():
    return jsonify({"wallets": wallets, "count": len(wallets)})

@app.route('/api/admin/wallet/<wallet_id>', methods=['GET'])
def admin_get_wallet(wallet_id):
    wallet = wallets.get(wallet_id)
    if not wallet:
        return jsonify({"error": "Wallet not found"}), 404
    return jsonify(wallet)

@app.route('/api/admin/wallet', methods=['POST'])
def admin_create_wallet():
    data = request.get_json()
    wallet_id = f"wallet_{uuid.uuid4().hex[:12]}"
    chain = data.get('chain', 'ethereum')
    
    wallet = {
        "wallet_id": wallet_id,
        "address": f"0x{uuid.uuid4().hex[2:42]}",
        "chain": chain,
        "type": data.get('type', 'custodial'),  # custodial, non-custodial
        "user_id": data.get('user_id', ''),
        "created_at": time.time(),
        "status": "active",
        "balance": {},
        "frozen": False
    }
    
    wallets[wallet_id] = wallet
    balances[wallet_id] = {}
    
    return jsonify({"status": "created", "wallet": wallet})

@app.route('/api/admin/wallet/<wallet_id>/freeze', methods=['POST'])
def admin_freeze_wallet(wallet_id):
    if wallet_id in wallets:
        wallets[wallet_id]['frozen'] = True
        return jsonify({"status": "frozen", "wallet_id": wallet_id})
    return jsonify({"error": "Wallet not found"}), 404

@app.route('/api/admin/wallet/<wallet_id>/unfreeze', methods=['POST'])
def admin_unfreeze_wallet(wallet_id):
    if wallet_id in wallets:
        wallets[wallet_id]['frozen'] = False
        return jsonify({"status": "active", "wallet_id": wallet_id})
    return jsonify({"error": "Wallet not found"}), 404

@app.route('/api/admin/wallet/<wallet_id>/balance', methods=['POST'])
def admin_adjust_balance(wallet_id):
    data = request.get_json()
    if wallet_id not in wallets:
        return jsonify({"error": "Wallet not found"}), 404
    
    token = data.get('token', 'native')
    amount = float(data.get('amount', 0))
    
    if wallet_id not in balances:
        balances[wallet_id] = {}
    
    balances[wallet_id][token] = balances[wallet_id].get(token, 0) + amount
    wallets[wallet_id]['balance'][token] = balances[wallet_id][token]
    
    return jsonify({"status": "adjusted", "balance": balances[wallet_id]})

@app.route('/api/admin/transactions', methods=['GET'])
def admin_get_transactions():
    return jsonify({"transactions": transactions, "count": len(transactions)})

@app.route('/api/admin/chains', methods=['GET'])
def admin_get_chains():
    return jsonify({"chains": CHAINS})

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    total_wallets = len(wallets)
    active_wallets = sum(1 for w in wallets.values() if w.get('status') == 'active')
    frozen_wallets = sum(1 for w in wallets.values() if w.get('frozen'))
    total_transactions = len(transactions)
    total_balance = sum(sum(balances[w].values()) for w in balances)
    
    return jsonify({
        "total_wallets": total_wallets,
        "active_wallets": active_wallets,
        "frozen_wallets": frozen_wallets,
        "total_transactions": total_transactions,
        "total_balance": total_balance,
        "chains": len(CHAINS)
    })

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username in admins and admins[username]['password'] == password:
        session_id = f"session_{uuid.uuid4().hex}"
        user_sessions[session_id] = {"username": username, "role": "admin", "time": time.time()}
        return jsonify({"status": "logged_in", "session_id": session_id})
    
    return jsonify({"error": "Invalid credentials"}), 401

# User Backend
@app.route('/api/user/health')
def user_health():
    return jsonify({"status": "ok", "service": "custom-wallet", "role": "user"})

@app.route('/api/user/wallet', methods=['POST'])
def user_create_wallet():
    data = request.get_json()
    session_id = data.get('session_id')
    
    if session_id not in user_sessions:
        return jsonify({"error": "Unauthorized"}), 401
    
    wallet_id = f"wallet_{uuid.uuid4().hex[:12]}"
    chain = data.get('chain', 'ethereum')
    
    wallet = {
        "wallet_id": wallet_id,
        "address": f"0x{uuid.uuid4().hex[2:42]}",
        "chain": chain,
        "type": "non-custodial",
        "user_id": user_sessions[session_id].get('user_id', ''),
        "created_at": time.time(),
        "status": "active",
        "balance": {},
        "frozen": False
    }
    
    wallets[wallet_id] = wallet
    balances[wallet_id] = {}
    
    return jsonify({"status": "created", "wallet": wallet})

@app.route('/api/user/wallets', methods=['GET'])
def user_get_wallets():
    session_id = request.headers.get('session_id')
    if session_id not in user_sessions:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = user_sessions[session_id].get('user_id', '')
    user_wallets = {k: v for k, v in wallets.items() if v.get('user_id') == user_id}
    
    return jsonify({"wallets": user_wallets})

@app.route('/api/user/wallet/<wallet_id>/balance', methods=['GET'])
def user_get_balance(wallet_id):
    session_id = request.headers.get('session_id')
    if session_id not in user_sessions:
        return jsonify({"error": "Unauthorized"}), 401
    
    if wallet_id not in wallets:
        return jsonify({"error": "Wallet not found"}), 404
    
    return jsonify({"wallet_id": wallet_id, "balance": balances.get(wallet_id, {})})

@app.route('/api/user/wallet/<wallet_id>/send', methods=['POST'])
def user_send_transaction(wallet_id):
    session_id = request.headers.get('session_id')
    if session_id not in user_sessions:
        return jsonify({"error": "Unauthorized"}), 401
    
    if wallet_id not in wallets:
        return jsonify({"error": "Wallet not found"}), 404
    
    if wallets[wallet_id].get('frozen'):
        return jsonify({"error": "Wallet is frozen"}), 403
    
    data = request.get_json()
    to_address = data.get('to')
    token = data.get('token', 'native')
    amount = float(data.get('amount', 0))
    
    if balances.get(wallet_id, {}).get(token, 0) < amount:
        return jsonify({"error": "Insufficient balance"}), 400
    
    tx_id = f"tx_{uuid.uuid4().hex[:16]}"
    tx = {
        "tx_id": tx_id,
        "wallet_id": wallet_id,
        "to": to_address,
        "token": token,
        "amount": amount,
        "status": "pending",
        "timestamp": time.time(),
        "type": "send"
    }
    
    transactions[tx_id] = tx
    balances[wallet_id][token] -= amount
    
    return jsonify({"status": "pending", "tx_id": tx_id})

@app.route('/api/user/wallet/<wallet_id>/deposit', methods=['POST'])
def user_deposit(wallet_id):
    session_id = request.headers.get('session_id')
    if session_id not in user_sessions:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    tx_id = f"tx_{uuid.uuid4().hex[:16]}"
    tx = {
        "tx_id": tx_id,
        "wallet_id": wallet_id,
        "token": data.get('token', 'native'),
        "amount": float(data.get('amount', 0)),
        "status": "confirmed",
        "timestamp": time.time(),
        "type": "deposit"
    }
    
    transactions[tx_id] = tx
    if wallet_id not in balances:
        balances[wallet_id] = {}
    token = data.get('token', 'native')
    balances[wallet_id][token] = balances[wallet_id].get(token, 0) + float(data.get('amount', 0))
    wallets[wallet_id]['balance'] = balances[wallet_id]
    
    return jsonify({"status": "confirmed", "tx": tx})

@app.route('/api/user/wallet/<wallet_id>/withdraw', methods=['POST'])
def user_withdraw(wallet_id):
    session_id = request.headers.get('session_id')
    if session_id not in user_sessions:
        return jsonify({"error": "Unauthorized"}), 401
    
    if wallet_id not in wallets:
        return jsonify({"error": "Wallet not found"}), 404
    
    data = request.get_json()
    token = data.get('token', 'native')
    amount = float(data.get('amount', 0))
    
    if balances.get(wallet_id, {}).get(token, 0) < amount:
        return jsonify({"error": "Insufficient balance"}), 400
    
    tx_id = f"tx_{uuid.uuid4().hex[:16]}"
    tx = {
        "tx_id": tx_id,
        "wallet_id": wallet_id,
        "token": token,
        "amount": amount,
        "status": "pending",
        "timestamp": time.time(),
        "type": "withdraw"
    }
    
    transactions[tx_id] = tx
    balances[wallet_id][token] -= amount
    wallets[wallet_id]['balance'] = balances[wallet_id]
    
    return jsonify({"status": "pending", "tx_id": tx_id})

@app.route('/api/user/chains', methods=['GET'])
def user_get_chains():
    return jsonify({"chains": CHAINS})

@app.route('/api/user/login', methods=['POST'])
def user_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    # Create user if not exists
    if email not in users:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        users[email] = {
            "user_id": user_id,
            "email": email,
            "password": password,
            "created_at": time.time()
        }
    else:
        if users[email]['password'] != password:
            return jsonify({"error": "Invalid credentials"}), 401
        user_id = users[email]['user_id']
    
    session_id = f"session_{uuid.uuid4().hex}"
    user_sessions[session_id] = {"user_id": user_id, "email": email, "time": time.time()}
    
    return jsonify({"status": "logged_in", "session_id": session_id, "user_id": user_id})

@app.route('/api/user/transactions', methods=['GET'])
def user_get_transactions():
    session_id = request.headers.get('session_id')
    if session_id not in user_sessions:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = user_sessions[session_id]['user_id']
    user_txs = {k: v for k, v in transactions.items() if v.get('wallet_id', '').startswith('wallet_')}
    
    return jsonify({"transactions": user_txs})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 6100))
    app.run(host='0.0.0.0', port=port, threaded=True)