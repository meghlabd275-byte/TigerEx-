#!/usr/bin/env python3
"""TigerEx - Full Backend"""
from flask import Flask, jsonify, request
import uuid, time

app = Flask(__name__)
users, sessions, wallets, balances, trades, orders = {}, {}, {}, {}, {}, {}

@app.route('/api/admin/health')
def admin_health(): return jsonify({"status": "ok", "service": "tigerex"})
@app.route('/api/admin/stats')
def admin_stats(): return jsonify({"users": len(users), "wallets": len(wallets), "trades": len(trades)})
@app.route('/api/admin/users', methods=['GET'])
def admin_users(): return jsonify({"users": users})

@app.route('/api/user/health')
def user_health(): return jsonify({"status": "ok", "service": "tigerex"})
@app.route('/api/user/register', methods=['POST'])
def user_register():
    data = request.get_json()
    email = data.get('email', '')
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    users[email] = {"user_id": user_id, "email": email}
    return jsonify({"status": "registered", "user_id": user_id})

@app.route('/api/user/login', methods=['POST'])
def user_login():
    data = request.get_json()
    email = data.get('email', '')
    if email not in users: return jsonify({"error": "Not found"}), 404
    session_id = f"sess_{uuid.uuid4().hex}"
    sessions[session_id] = {"user_id": users[email]['user_id'], "email": email}
    return jsonify({"status": "logged_in", "session_id": session_id})

@app.route('/api/user/wallet', methods=['POST'])
def create_wallet():
    session_id = request.headers.get('session_id')
    if session_id not in sessions: return jsonify({"error": "Unauthorized"}), 401
    wallet_id = f"wallet_{uuid.uuid4().hex[:12]}"
    wallets[wallet_id] = {"wallet_id": wallet_id, "address": f"0x{uuid.uuid4().hex[2:42]}"}
    balances[wallet_id] = {}
    return jsonify({"status": "created", "wallet_id": wallet_id})

@app.route('/api/user/wallets', methods=['GET'])
def get_wallets(): return jsonify({"wallets": wallets})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6800)