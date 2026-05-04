#!/usr/bin/env python3
"""
TigerEx User Backend - Full Operational
"""
from flask import Flask, jsonify, request
import uuid, time, hashlib

app = Flask(__name__)

# Storage
users = {}
sessions = {}
wallets = {}
transactions = {}
balances = {}
kyc_requests = {}
verification_codes = {}
orders = {}

# Chains
CHAINS = {
    "ethereum": {"name": "Ethereum", "symbol": "ETH", "type": "evm"},
    "bsc": {"name": "BNB Chain", "symbol": "BNB", "type": "evm"},
    "polygon": {"name": "Polygon", "symbol": "MATIC", "type": "evm"},
    "solana": {"name": "Solana", "symbol": "SOL", "type": "non-evm"},
    "cardano": {"name": "Cardano", "symbol": "ADA", "type": "non-evm"},
    "near": {"name": "NEAR", "symbol": "NEAR", "type": "non-evm"},
}

@app.route('/api/user/health')
def health(): return jsonify({"status": "ok", "service": "tigerex", "role": "user"})

# Register
@app.route('/api/user/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email', '')
    phone = data.get('phone', '')
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    
    # Check if exists
    for u in users:
        if users[u]['email'] == email:
            return jsonify({"error": "User exists"}), 400
    
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    users[email] = {
        "user_id": user_id,
        "email": email,
        "phone": phone,
        "password": hashlib.sha256(password.encode()).hexdigest(),
        "status": "active",
        "kyc_status": "none",
        "2fa_enabled": False,
        "created_at": time.time()
    }
    balances[user_id] = {"USDT": 10000}  # Demo balance
    
    return jsonify({"status": "registered", "user_id": user_id})

# Login
@app.route('/api/user/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '')
    password = data.get('password', '')
    
    if email not in users:
        return jsonify({"error": "User not found"}), 404
    
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    if users[email]['password'] != pw_hash:
        return jsonify({"error": "Invalid password"}), 401
    
    if users[email].get('2fa_enabled'):
        return jsonify({"status": "2fa_required"})
    
    session_id = f"sess_{uuid.uuid4().hex}"
    sessions[session_id] = {"user_id": users[email]['user_id'], "email": email, "time": time.time()}
    return jsonify({"status": "logged_in", "session_id": session_id})

# Verify 2FA
@app.route('/api/user/verify-2fa', methods=['POST'])
def verify_2fa():
    data = request.get_json()
    email = data.get('email', '')
    code = data.get('code', '')
    
    # Demo: accept any 6-digit code
    if len(code) == 6:
        session_id = f"sess_{uuid.uuid4().hex}"
        sessions[session_id] = {"user_id": users[email]['user_id'], "email": email, "time": time.time()}
        return jsonify({"status": "logged_in", "session_id": session_id})
    return jsonify({"error": "Invalid code"}), 400

# Logout
@app.route('/api/user/logout', methods=['POST'])
def logout():
    session_id = request.headers.get('session_id')
    if session_id in sessions:
        del sessions[session_id]
    return jsonify({"status": "logged_out"})

# Get User
def get_user_from_session():
    session_id = request.headers.get('session_id')
    if session_id not in sessions:
        return None, jsonify({"error": "Unauthorized"}), 401
    email = sessions[session_id]['email']
    return users[email], None

# Chains
@app.route('/api/user/chains')
def chains(): return jsonify({"chains": CHAINS})

# Wallet Management
@app.route('/api/user/wallet', methods=['POST'])
def create_wallet():
    user, err = get_user_from_session()
    if err: return err
    
    data = request.get_json()
    chain = data.get('chain', 'ethereum')
    wallet_id = f"wallet_{uuid.uuid4().hex[:12]}"
    address = f"0x{uuid.uuid4().hex[2:42]}"
    
    wallets[wallet_id] = {
        "wallet_id": wallet_id,
        "address": address,
        "chain": chain,
        "user_id": user['user_id'],
        "created_at": time.time()
    }
    balances[wallet_id] = {}
    return jsonify({"status": "created", "wallet": wallets[wallet_id]})

@app.route('/api/user/wallets', methods=['GET'])
def get_wallets():
    user, err = get_user_from_session()
    if err: return err
    
    user_wallets = {w: v for w, v in wallets.items() if v.get('user_id') == user['user_id']}
    for w in user_wallets:
        user_wallets[w]['balance'] = balances.get(w, {})
    return jsonify({"wallets": user_wallets})

@app.route('/api/user/wallet/<wallet_id>', methods=['DELETE'])
def delete_wallet(wallet_id):
    user, err = get_user_from_session()
    if err: return err
    
    if wallet_id in wallets and wallets[wallet_id]['user_id'] == user['user_id']:
        del wallets[wallet_id]
        return jsonify({"status": "deleted"})
    return jsonify({"error": "Wallet not found"}), 404

# Deposit
@app.route('/api/user/wallet/<wallet_id>/deposit', methods=['POST'])
def deposit(wallet_id):
    user, err = get_user_from_session()
    if err: return err
    
    if wallet_id not in wallets or wallets[wallet_id]['user_id'] != user['user_id']:
        return jsonify({"error": "Wallet not found"}), 404
    
    data = request.get_json()
    token = data.get('token', 'native')
    amount = float(data.get('amount', 0))
    
    if wallet_id not in balances:
        balances[wallet_id] = {}
    balances[wallet_id][token] = balances[wallet_id].get(token, 0) + amount
    
    tx_id = f"tx_{uuid.uuid4().hex[:12]}"
    transactions[tx_id] = {
        "tx_id": tx_id,
        "wallet_id": wallet_id,
        "type": "deposit",
        "token": token,
        "amount": amount,
        "status": "completed",
        "timestamp": time.time()
    }
    return jsonify({"status": "deposited", "balance": balances[wallet_id]})

# Withdraw
@app.route('/api/user/wallet/<wallet_id>/withdraw', methods=['POST'])
def withdraw(wallet_id):
    user, err = get_user_from_session()
    if err: return err
    
    if wallet_id not in wallets or wallets[wallet_id]['user_id'] != user['user_id']:
        return jsonify({"error": "Wallet not found"}), 404
    
    data = request.get_json()
    token = data.get('token', 'native')
    amount = float(data.get('amount', 0))
    
    if balances.get(wallet_id, {}).get(token, 0) < amount:
        return jsonify({"error": "Insufficient balance"}), 400
    
    balances[wallet_id][token] -= amount
    
    tx_id = f"tx_{uuid.uuid4().hex[:12]}"
    transactions[tx_id] = {
        "tx_id": tx_id,
        "wallet_id": wallet_id,
        "type": "withdraw",
        "token": token,
        "amount": amount,
        "status": "pending",
        "timestamp": time.time()
    }
    return jsonify({"status": "withdrawn", "balance": balances[wallet_id]})

# Transactions
@app.route('/api/user/transactions', methods=['GET'])
def get_transactions():
    user, err = get_user_from_session()
    if err: return err
    
    user_txs = {t: v for t, v in transactions.items() if wallets.get(v.get('wallet_id', ''), {}).get('user_id') == user['user_id']}
    return jsonify({"transactions": user_txs})

# KYC
@app.route('/api/user/kyc', methods=['POST'])
def submit_kyc():
    user, err = get_user_from_session()
    if err: return err
    
    data = request.get_json()
    kyc_id = f"kyc_{uuid.uuid4().hex[:12]}"
    kyc_requests[kyc_id] = {
        "kyc_id": kyc_id,
        "user_id": user['user_id'],
        "first_name": data.get('first_name', ''),
        "last_name": data.get('last_name', ''),
        "dob": data.get('dob', ''),
        "address": data.get('address', ''),
        "status": "pending",
        "created_at": time.time()
    }
    user['kyc_status'] = 'pending'
    return jsonify({"status": "submitted", "kyc_id": kyc_id})

@app.route('/api/user/kyc/status')
def kyc_status():
    user, err = get_user_from_session()
    if err: return err
    
    for k, v in kyc_requests.items():
        if v.get('user_id') == user['user_id']:
            return jsonify({"status": v['status'], "kyc_id": k})
    return jsonify({"status": user.get('kyc_status', 'none')})

# Verification Codes
@app.route('/api/user/send-code', methods=['POST'])
def send_code():
    data = request.get_json()
    target = data.get('email') or data.get('phone', '')
    type = data.get('type', 'email')
    
    code = str(uuid.uuid4().int)[:6]
    verification_codes[target] = {"code": code, "type": type, "time": time.time()}
    return jsonify({"status": "sent", "code": code})  # Demo

@app.route('/api/user/verify-code', methods=['POST'])
def verify_code():
    data = request.get_json()
    target = data.get('email') or data.get('phone', '')
    code = data.get('code', '')
    
    stored = verification_codes.get(target, {})
    if stored.get('code') == code:
        return jsonify({"status": "verified"})
    return jsonify({"error": "Invalid code"}), 400

# Enable 2FA
@app.route('/api/user/2fa/enable', methods=['POST'])
def enable_2fa():
    user, err = get_user_from_session()
    if err: return err
    
    user['2fa_enabled'] = True
    return jsonify({"status": "enabled"})

@app.route('/api/user/2fa/disable', methods=['POST'])
def disable_2fa():
    user, err = get_user_from_session()
    if err: return err
    
    user['2fa_enabled'] = False
    return jsonify({"status": "disabled"})

# Profile
@app.route('/api/user/profile')
def profile():
    user, err = get_user_from_session()
    if err: return err
    
    return jsonify({
        "user_id": user['user_id'],
        "email": user['email'],
        "phone": user.get('phone', ''),
        "kyc_status": user.get('kyc_status', 'none'),
        "2fa_enabled": user.get('2fa_enabled', False)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6801)