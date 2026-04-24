"""
TigerEx Backend Server
Flask REST API Server
"""
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import hashlib
import uuid
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'tigerex-secret-key-change-in-production')

# CORS
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# JWT
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

# In-memory database (replace with real DB in production)
users_db = {}
tokens_db = {}
orders_db = {}
wallets_db = {}
staking_db = {}
markets_db = {
    "BTCUSDT": {"symbol": "BTCUSDT", "price": 67234.50, "change24h": 2.34, "volume24h": 1250000000},
    "ETHUSDT": {"symbol": "ETHUSDT", "price": 3456.78, "change24h": 1.56, "volume24h": 890000000},
    "BNBUSDT": {"symbol": "BNBUSDT", "price": 567.89, "change24h": -0.45, "volume24h": 234000000},
    "SOLUSDT": {"symbol": "SOLUSDT", "price": 145.67, "change24h": 5.67, "volume24h": 456000000},
    "XRPUSDT": {"symbol": "XRPUSDT", "price": 0.5678, "change24h": 2.34, "volume24h": 678000000}
}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token():
    return str(uuid.uuid4())

# ==================== AUTH ROUTES ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    identifier = data.get('identifier', '')
    password = data.get('password', '')
    referral = data.get('referral', '')
    
    if not identifier or not password:
        return jsonify({"success": False, "message": "Missing required fields"}), 400
    
    user_id = generate_token()
    users_db[user_id] = {
        "id": user_id,
        "identifier": identifier,
        "password_hash": hash_password(password),
        "email": identifier if '@' in identifier else None,
        "phone": identifier if '@' not in identifier else None,
        "referral": referral,
        "created_at": "2024-01-01T00:00:00Z"
    }
    
    wallets_db[user_id] = {"BTC": 0, "USDT": 1000}
    staking_db[user_id] = []
    
    return jsonify({
        "success": True,
        "message": "Registration successful",
        "user": {"id": user_id, "identifier": identifier}
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    identifier = data.get('identifier', '')
    password = data.get('password', '')
    
    user = next((u for u in users_db.values() 
            if u.get('identifier') == identifier), None)
    
    if not user or user.get('password_hash') != hash_password(password):
        return jsonify({"success": False, "message": "Invalid credentials"}), 401
    
    token = create_access_token(identity=user['id'])
    tokens_db[token] = user['id']
    
    return jsonify({
        "success": True,
        "token": token,
        "user": {"id": user['id'], "identifier": user['identifier']}
    })

@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if token in tokens_db:
        del tokens_db[token]
    return jsonify({"success": True})

@app.route('/api/auth/session', methods=['GET'])
@jwt_required()
def get_session():
    user_id = get_jwt_identity()
    user = users_db.get(user_id)
    if not user:
        return jsonify({"success": False}), 401
    return jsonify({
        "success": True,
        "user": {"id": user['id'], "identifier": user['identifier']}
    })

# ==================== USER ROUTES ====================

@app.route('/api/user/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = users_db.get(user_id, {})
    wallet = wallets_db.get(user_id, {})
    staking = staking_db.get(user_id, [])
    return jsonify({
        "success": True,
        "profile": user,
        "wallet": wallet,
        "staking": staking
    })

# ==================== TRADING ROUTES ====================

@app.route('/api/trading/markets', methods=['GET'])
def get_markets():
    return jsonify({"success": True, "markets": list(markets_db.values())})

@app.route('/api/trading/orderbook/<symbol>', methods=['GET'])
def get_orderbook(symbol):
    market = markets_db.get(symbol.upper())
    if not market:
        return jsonify({"success": False, "message": "Market not found"}), 404
    return jsonify({
        "success": True,
        "symbol": symbol.upper(),
        "bids": [[market['price'] * 0.999, 10], [market['price'] * 0.998, 20]],
        "asks": [[market['price'] * 1.001, 15], [market['price'] * 1.002, 25]]
    })

@app.route('/api/trading/order', methods=['POST'])
@jwt_required()
def create_order():
    user_id = get_jwt_identity()
    data = request.get_json()
    order = {
        "id": generate_token(),
        "user_id": user_id,
        "symbol": data.get('symbol', ''),
        "side": data.get('side', ''),
        "type": data.get('type', 'limit'),
        "price": data.get('price', 0),
        "amount": data.get('amount', 0),
        "status": "pending",
        "created_at": "2024-01-01T00:00:00Z"
    }
    orders_db[order['id']] = order
    return jsonify({"success": True, "order": order})

@app.route('/api/trading/orders', methods=['GET'])
@jwt_required()
def get_orders():
    user_id = get_jwt_identity()
    user_orders = [o for o in orders_db.values() if o.get('user_id') == user_id]
    return jsonify({"success": True, "orders": user_orders})

# ==================== WALLET ROUTES ====================

@app.route('/api/wallet/balance', methods=['GET'])
@jwt_required()
def get_balance():
    user_id = get_jwt_identity()
    balance = wallets_db.get(user_id, {"BTC": 0, "USDT": 1000})
    return jsonify({"success": True, "balance": balance})

@app.route('/api/wallet/addresses', methods=['GET'])
@jwt_required()
def get_addresses():
    user_id = get_jwt_identity()
    addresses = {
        "BTC": f"bc1q{user_id[:40]}",
        "ETH": f"0x{user_id[:40]}",
        "TRX": f"T{user_id[:33]}"
    }
    return jsonify({"success": True, "addresses": addresses})

@app.route('/api/wallet/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    user_id = get_jwt_identity()
    transactions = [
        {"id": "tx1", "type": "deposit", "amount": 1000, "currency": "USDT", "status": "completed", "date": "2024-01-01"},
        {"id": "tx2", "type": "withdrawal", "amount": 50, "currency": "USDT", "status": "completed", "date": "2024-01-02"}
    ]
    return jsonify({"success": True, "transactions": transactions})

# ==================== EARN ROUTES ====================

@app.route('/api/earn/products', methods=['GET'])
def get_earn_products():
    products = [
        {"id": "staking-btc", "name": "BTC Staking", "apy": 4.5, "min_amount": 0.001, "lock_period": 30},
        {"id": "staking-eth", "name": "ETH Staking", "apy": 3.2, "min_amount": 0.01, "lock_period": 15},
        {"id": "savings-usdt", "name": "USDT Savings", "apy": 2.5, "min_amount": 10, "lock_period": 7}
    ]
    return jsonify({"success": True, "products": products})

@app.route('/api/earn/staking', methods=['GET'])
@jwt_required()
def get_staking():
    user_id = get_jwt_identity()
    staking = staking_db.get(user_id, [])
    return jsonify({"success": True, "staking": staking})

# ==================== ROOT ====================

@app.route('/')
def index():
    return jsonify({"message": "TigerEx API Server", "version": "1.0.0"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
