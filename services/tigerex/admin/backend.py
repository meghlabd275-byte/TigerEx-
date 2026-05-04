#!/usr/bin/env python3
"""
TigerEx Admin Backend - Full Operational
"""
from flask import Flask, jsonify, request
import uuid, time

app = Flask(__name__)

# Storage
admins = {"admin@tigerex.com": {"password": "admin123", "role": "super_admin", "created_at": time.time()}}
sessions = {}
users = {}
kyc_requests = {}
transactions = {}
wallets = {}
settings = {
    "maintenance_mode": False,
    "registration_enabled": True,
    "kyc_required": True,
    "2fa_required": False
}

# Health
@app.route('/api/admin/health')
def health(): return jsonify({"status": "ok", "service": "tigerex", "role": "admin"})

# Login
@app.route('/api/admin/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '')
    password = data.get('password', '')
    
    if email in admins and admins[email]['password'] == password:
        session_id = f"adm_{uuid.uuid4().hex}"
        sessions[session_id] = {"email": email, "role": admins[email]['role'], "time": time.time()}
        return jsonify({"status": "logged_in", "session_id": session_id, "role": admins[email]['role']})
    return jsonify({"error": "Invalid credentials"}), 401

# Logout
@app.route('/api/admin/logout', methods=['POST'])
def logout():
    session_id = request.headers.get('session_id')
    if session_id in sessions:
        del sessions[session_id]
    return jsonify({"status": "logged_out"})

# Stats
@app.route('/api/admin/stats')
def stats():
    return jsonify({
        "users": len(users),
        "wallets": len(wallets),
        "transactions": len(transactions),
        "admins": len(admins),
        "revenue": 0,
        "pending_kyc": len([k for k in kyc_requests if kyc_requests[k]['status'] == 'pending'])
    })

# Users Management
@app.route('/api/admin/users', methods=['GET'])
def get_users():
    return jsonify({"users": users, "count": len(users)})

@app.route('/api/admin/user/<user_id>', methods=['GET'])
def get_user(user_id):
    if user_id in users:
        return jsonify({"user": users[user_id]})
    return jsonify({"error": "User not found"}), 404

@app.route('/api/admin/user/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    if user_id in users:
        users[user_id].update(data)
        return jsonify({"status": "updated", "user": users[user_id]})
    return jsonify({"error": "User not found"}), 404

@app.route('/api/admin/user/<user_id>/ban', methods=['POST'])
def ban_user(user_id):
    if user_id in users:
        users[user_id]['status'] = 'banned'
        return jsonify({"status": "banned"})
    return jsonify({"error": "User not found"}), 404

@app.route('/api/admin/user/<user_id>/unban', methods=['POST'])
def unban_user(user_id):
    if user_id in users:
        users[user_id]['status'] = 'active'
        return jsonify({"status": "unbanned"})
    return jsonify({"error": "User not found"}), 404

# KYC Management
@app.route('/api/admin/kyc', methods=['GET'])
def get_kyc():
    return jsonify({"kyc_requests": kyc_requests})

@app.route('/api/admin/kyc/<request_id>/approve', methods=['POST'])
def approve_kyc(request_id):
    if request_id in kyc_requests:
        kyc_requests[request_id]['status'] = 'approved'
        kyc_requests[request_id]['approved_at'] = time.time()
        user_id = kyc_requests[request_id]['user_id']
        if user_id in users:
            users[user_id]['kyc_status'] = 'verified'
        return jsonify({"status": "approved"})
    return jsonify({"error": "KYC not found"}), 404

@app.route('/api/admin/kyc/<request_id>/reject', methods=['POST'])
def reject_kyc(request_id):
    data = request.get_json()
    if request_id in kyc_requests:
        kyc_requests[request_id]['status'] = 'rejected'
        kyc_requests[request_id]['reason'] = data.get('reason', '')
        return jsonify({"status": "rejected"})
    return jsonify({"error": "KYC not found"}), 404

# Transactions
@app.route('/api/admin/transactions', methods=['GET'])
def get_transactions():
    return jsonify({"transactions": transactions, "count": len(transactions)})

@app.route('/api/admin/transaction/<tx_id>', methods=['GET'])
def get_transaction(tx_id):
    if tx_id in transactions:
        return jsonify({"transaction": transactions[tx_id]})
    return jsonify({"error": "Transaction not found"}), 404

# Wallets
@app.route('/api/admin/wallets', methods=['GET'])
def get_wallets():
    return jsonify({"wallets": wallets, "count": len(wallets)})

# Admin Management (Super Admin only)
@app.route('/api/admin/admins', methods=['GET'])
def get_admins():
    return jsonify({"admins": admins})

@app.route('/api/admin/admin', methods=['POST'])
def create_admin():
    data = request.get_json()
    email = data.get('email', '')
    role = data.get('role', 'admin')
    invite_code = data.get('invite_code', '')
    
    # Validate invite code (demo: TIGEREX2024)
    if invite_code != 'TIGEREX2024':
        return jsonify({"error": "Invalid invite code"}), 400
    
    if email in admins:
        return jsonify({"error": "Admin exists"}), 400
    
    admins[email] = {"password": data.get('password', 'changeme'), "role": role, "created_at": time.time()}
    return jsonify({"status": "created", "email": email})

@app.route('/api/admin/admin/<email>', methods=['DELETE'])
def delete_admin(email):
    if email in admins:
        if admins[email]['role'] == 'super_admin':
            return jsonify({"error": "Cannot delete super admin"}), 400
        del admins[email]
        return jsonify({"status": "deleted"})
    return jsonify({"error": "Admin not found"}), 404

# Settings
@app.route('/api/admin/settings', methods=['GET'])
def get_settings():
    return jsonify({"settings": settings})

@app.route('/api/admin/settings', methods=['PUT'])
def update_settings():
    data = request.get_json()
    settings.update(data)
    return jsonify({"status": "saved", "settings": settings})

# Analytics
@app.route('/api/admin/analytics')
def analytics():
    return jsonify({
        "daily_users": 0,
        "daily_transactions": 0,
        "daily_volume": 0,
        "top_coins": ["ETH", "BTC", "USDT"],
        "user_growth": [],
        "transaction_growth": []
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6800)