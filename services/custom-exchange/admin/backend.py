#!/usr/bin/env python3
"""
Custom Exchange - Full Backend (Admin + User)
CEX + DEX Support
"""
from flask import Flask, jsonify, request
import uuid, time

app = Flask(__name__)

# Storage
users, sessions, orders, trades, balances = {}, {}, {}, {}, {}
admins = {"admin": {"password": "admin123"}}

TRADING_PAIRS = {
    "ETH/USDT": {"base": "ETH", "quote": "USDT"},
    "BTC/USDT": {"base": "BTC", "quote": "USDT"},
    "ETH/BTC": {"base": "ETH", "quote": "BTC"},
    "SOL/USDT": {"base": "SOL", "quote": "USDT"},
}

# ADMIN
@app.route('/api/admin/health')
def admin_health(): return jsonify({"status": "ok"})

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    if data.get('username') in admins and admins[data['username']]['password'] == data.get('password'):
        return jsonify({"status": "logged_in"})
    return jsonify({"error": "Invalid"}), 401

@app.route('/api/admin/stats')
def admin_stats(): return jsonify({"users": len(users), "orders": len(orders), "pairs": len(TRADING_PAIRS)})

@app.route('/api/admin/users', methods=['GET'])
def admin_users(): return jsonify({"users": users})

@app.route('/api/admin/orders', methods=['GET'])
def admin_orders(): return jsonify({"orders": orders})

# USER
@app.route('/api/user/health')
def user_health(): return jsonify({"status": "ok"})

@app.route('/api/user/pairs')
def user_pairs(): return jsonify({"pairs": TRADING_PAIRS})

@app.route('/api/user/register', methods=['POST'])
def user_register():
    data = request.get_json()
    email = data.get('email', '')
    if email in users: return jsonify({"error": "User exists"}), 400
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    users[email] = {"user_id": user_id, "email": email}
    balances[user_id] = {"USDT": 10000}
    return jsonify({"status": "registered"})

@app.route('/api/user/login', methods=['POST'])
def user_login():
    data = request.get_json()
    email = data.get('email', '')
    if email not in users: return jsonify({"error": "Not found"}), 404
    session_id = f"sess_{uuid.uuid4().hex}"
    sessions[session_id] = {"user_id": users[email]['user_id'], "email": email}
    return jsonify({"status": "logged_in", "session_id": session_id})

@app.route('/api/user/balance', methods=['GET'])
def user_balance():
    session_id = request.headers.get('session_id')
    if session_id not in sessions: return jsonify({"error": "Unauthorized"}), 401
    user_id = sessions[session_id]['user_id']
    return jsonify({"balance": balances.get(user_id, {})})

@app.route('/api/user/order', methods=['POST'])
def place_order():
    session_id = request.headers.get('session_id')
    if session_id not in sessions: return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    order_id = f"ord_{uuid.uuid4().hex[:12]}"
    orders[order_id] = {"order_id": order_id, "user_id": sessions[session_id]['user_id'], "pair": data.get('pair'), "type": data.get('type'), "side": data.get('side'), "price": data.get('price'), "amount": data.get('amount'), "status": "open"}
    return jsonify({"status": "placed"})

@app.route('/api/user/orders', methods=['GET'])
def user_orders():
    session_id = request.headers.get('session_id')
    if session_id not in sessions: return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"orders": orders})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6400)