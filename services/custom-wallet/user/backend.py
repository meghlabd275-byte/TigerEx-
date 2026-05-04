#!/usr/bin/env python3
"""Custom Wallet - User Backend with Social Login + Bind Email/Phone"""
from flask import Flask, jsonify, request
import uuid, time

app = Flask(__name__)

# Storage
users = {}
sessions = {}
wallets = {}
balances = {}
verification_codes = {}

CHAINS = {
    "ethereum": {"name": "Ethereum", "symbol": "ETH", "type": "evm", "flag": "🔷"},
    "bsc": {"name": "BNB Chain", "symbol": "BNB", "type": "evm", "flag": "🟡"},
    "polygon": {"name": "Polygon", "symbol": "MATIC", "type": "evm", "flag": "🟣"},
    "avalanche": {"name": "Avalanche", "symbol": "AVAX", "type": "evm", "flag": "🔺"},
    "solana": {"name": "Solana", "symbol": "SOL", "type": "non-evm", "flag": "⚡"},
    "cardano": {"name": "Cardano", "symbol": "ADA", "type": "non-evm", "flag": "🟢"},
    "near": {"name": "NEAR", "symbol": "NEAR", "type": "non-evm", "flag": "🟡"},
    "aptos": {"name": "Aptos", "symbol": "APT", "type": "non-evm", "flag": "🔵"},
}

@app.route('/api/user/health')
def health(): return jsonify({"status": "ok"})

@app.route('/api/user/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    provider = data.get('provider', '')
    
    if not email and not provider:
        return jsonify({"error": "Email or provider required"}), 400
    
    if email not in users:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        users[email] = {"user_id": user_id, "email": email, "password": password, "phone": "", "phone_verified": False, "email_verified": False, "provider": provider, "created_at": time.time()}
    else:
        if password and users[email].get('password') != password:
            return jsonify({"error": "Invalid password"}), 401
        user_id = users[email]['user_id']
    
    if not users[email].get('email_verified') or not users[email].get('phone_verified'):
        return jsonify({"status": "verification_needed", "email_verified": users[email].get('email_verified', False), "phone_verified": users[email].get('phone_verified', False)})
    
    session_id = f"sess_{uuid.uuid4().hex}"
    sessions[session_id] = {"user_id": user_id, "email": email, "time": time.time()}
    return jsonify({"status": "logged_in", "session_id": session_id, "user_id": user_id})

@app.route('/api/user/social/<provider>', methods=['POST'])
def social_login(provider):
    data = request.get_json()
    social_id = data.get('social_id', '')
    email = f"{provider}_{social_id}@social.local"
    if email not in users:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        users[email] = {"user_id": user_id, "email": email, "phone": "", "phone_verified": False, "email_verified": True, "provider": provider, "created_at": time.time()}
    return jsonify({"status": "bind_needed", "user_id": users[email]['user_id']})

@app.route('/api/user/bind/email', methods=['POST'])
def bind_email():
    session_id = request.headers.get('session_id')
    if session_id not in sessions: return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    email = data.get('email', '')
    if not email or '@' not in email: return jsonify({"error": "Invalid email"}), 400
    user_id = sessions[session_id]['user_id']
    code = str(uuid.uuid4().int)[:6]
    verification_codes[email] = {"code": code, "user_id": user_id, "type": "email", "time": time.time()}
    return jsonify({"status": "code_sent", "code": code})

@app.route('/api/user/verify/email', methods=['POST'])
def verify_email():
    session_id = request.headers.get('session_id')
    if session_id not in sessions: return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    code = data.get('code', '')
    email = data.get('email', '')
    stored = verification_codes.get(email, {})
    if stored.get('code') == code:
        user_id = sessions[session_id]['user_id']
        for u_email, user in users.items():
            if user['user_id'] == user_id:
                user['email'] = email
                user['email_verified'] = True
        return jsonify({"status": "verified"})
    return jsonify({"error": "Invalid code"}), 400

@app.route('/api/user/bind/phone', methods=['POST'])
def bind_phone():
    session_id = request.headers.get('session_id')
    if session_id not in sessions: return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    phone = data.get('phone', '')
    country_code = data.get('country_code', '+1')
    full_phone = country_code + phone
    user_id = sessions[session_id]['user_id']
    code = str(uuid.uuid4().int)[:6]
    verification_codes[full_phone] = {"code": code, "user_id": user_id, "type": "phone", "time": time.time()}
    return jsonify({"status": "code_sent", "code": code})

@app.route('/api/user/verify/phone', methods=['POST'])
def verify_phone():
    session_id = request.headers.get('session_id')
    if session_id not in sessions: return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    code = data.get('code', '')
    phone = data.get('phone', '')
    stored = verification_codes.get(phone, {})
    if stored.get('code') == code:
        user_id = sessions[session_id]['user_id']
        for u_email, user in users.items():
            if user['user_id'] == user_id:
                user['phone'] = phone
                user['phone_verified'] = True
        return jsonify({"status": "verified"})
    return jsonify({"error": "Invalid code"}), 400

@app.route('/api/user/chains')
def get_chains(): return jsonify({"chains": CHAINS})

@app.route('/api/user/wallet', methods=['POST'])
def create_wallet():
    session_id = request.headers.get('session_id')
    if session_id not in sessions: return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    chain = data.get('chain', 'ethereum')
    wallet_id = f"wallet_{uuid.uuid4().hex[:12]}"
    wallets[wallet_id] = {"wallet_id": wallet_id, "address": f"0x{uuid.uuid4().hex[2:42]}", "chain": chain, "user_id": sessions[session_id]['user_id'], "created_at": time.time()}
    balances[wallet_id] = {}
    return jsonify({"status": "created", "wallet": wallets[wallet_id]})

@app.route('/api/user/wallets', methods=['GET'])
def get_wallets():
    session_id = request.headers.get('session_id')
    if session_id not in sessions: return jsonify({"error": "Unauthorized"}), 401
    user_id = sessions[session_id]['user_id']
    user_wallets = {k: v for k, v in wallets.items() if v.get('user_id') == user_id}
    for wid in user_wallets:
        user_wallets[wid]['balance'] = balances.get(wid, {})
    return jsonify({"wallets": user_wallets})

@app.route('/api/user/wallet/<wallet_id>/deposit', methods=['POST'])
def deposit(wallet_id):
    session_id = request.headers.get('session_id')
    if session_id not in sessions: return jsonify({"error": "Unauthorized"}), 401
    if wallet_id not in wallets: return jsonify({"error": "Wallet not found"}), 404
    data = request.get_json()
    token = data.get('token', 'native')
    amount = float(data.get('amount', 0))
    if wallet_id not in balances: balances[wallet_id] = {}
    balances[wallet_id][token] = balances[wallet_id].get(token, 0) + amount
    return jsonify({"status": "deposited", "balance": balances[wallet_id]})

@app.route('/api/user/wallet/<wallet_id>/withdraw', methods=['POST'])
def withdraw(wallet_id):
    session_id = request.headers.get('session_id')
    if session_id not in sessions: return jsonify({"error": "Unauthorized"}), 401
    if wallet_id not in wallets: return jsonify({"error": "Wallet not found"}), 404
    data = request.get_json()
    token = data.get('token', 'native')
    amount = float(data.get('amount', 0))
    if balances.get(wallet_id, {}).get(token, 0) < amount: return jsonify({"error": "Insufficient balance"}), 400
    balances[wallet_id][token] -= amount
    return jsonify({"status": "withdrawn", "balance": balances[wallet_id]})

@app.route('/api/user/verification-status', methods=['GET'])
def verification_status():
    session_id = request.headers.get('session_id')
    if session_id not in sessions: return jsonify({"error": "Unauthorized"}), 401
    user_id = sessions[session_id]['user_id']
    foruser = None
    for email, user in users.items():
        if user['user_id'] == user_id: foruser = user
    return jsonify({"email_verified": foruser.get('email_verified', False) if foruser else False, "phone_verified": foruser.get('phone_verified', False) if foruser else False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6100)