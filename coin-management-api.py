#!/usr/bin/env python3
"""
TigerEx Trading Pair & Coin Management API
Restful API for managing coins, tokens, trading pairs, and blockchain addresses
"""
import os
import json
import secrets
import hashlib
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, g
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tigerex-secret-key-change-in-production')
app.config['DATABASE_PATH'] = '/workspace/project/TigerEx-/coin-data/data.json'

# Load or initialize data
def load_data():
    if os.path.exists(app.config['DATABASE_PATH']):
        with open(app.config['DATABASE_PATH'], 'r') as f:
            return json.load(f)
    return {
        'users': [],
        'coins': [],
        'networks': [],
        'trading_pairs': [],
        'transactions': []
    }

def save_data(data):
    os.makedirs(os.path.dirname(app.config['DATABASE_PATH']), exist_ok=True)
    with open(app.config['DATABASE_PATH'], 'w') as f:
        json.dump(data, f, indent=2)

@app.before_request
def before_request():
    g.data = load_data()

@app.after_request
def after_request(response):
    save_data(g.data)
    return response

# ============================================
# AUTHENTICATION
# ============================================

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check token (simplified for demo)
        user = next((u for u in g.data['users'] if u.get('token') == token), None)
        if not user:
            return jsonify({'error': 'Invalid token'}), 401
        
        g.user = user
        return f(*args, **kwargs)
    return decorated

def require_role(role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if g.user.get('role') not in ['admin', role]:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

# ============================================
# AUTH ROUTES
# ============================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Find user
    user = next((u for u in g.data['users'] if u.get('username') == username), None)
    if not user:
        # Auto-register for demo
        user = {
            'id': len(g.data['users']) + 1,
            'username': username,
            'password': hashlib.sha256(password.encode()).hexdigest(),
            'role': 'admin',
            'status': 'active',
            'created_at': datetime.now().isoformat()
        }
        g.data['users'].append(user)
    
    # Generate token
    token = secrets.token_urlsafe(32)
    user['token'] = token
    
    return jsonify({
        'token': token,
        'user': {k: v for k, v in user.items() if k != 'password' and k != 'token'}
    })

@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    g.user.pop('token', None)
    return jsonify({'message': 'Logged out successfully'})

# ============================================
# COIN ROUTES
# ============================================

@app.route('/api/coins', methods=['GET'])
def get_coins():
    """Get all coins/tokens"""
    return jsonify(g.data['coins'])

@app.route('/api/coins/<int:coin_id>', methods=['GET'])
def get_coin(coin_id):
    """Get single coin"""
    coin = next((c for c in g.data['coins'] if c.get('id') == coin_id), None)
    if not coin:
        return jsonify({'error': 'Coin not found'}), 404
    return jsonify(coin)

@app.route('/api/coins', methods=['POST'])
@require_auth
@require_role('admin')
def create_coin():
    """Create new coin/token"""
    data = request.json
    
    coin = {
        'id': len(g.data['coins']) + 1,
        'name': data.get('name'),
        'symbol': data.get('symbol', '').upper(),
        'type': data.get('type', 'coin'),
        'logo_url': data.get('logo_url', ''),
        'status': data.get('status', 'pending'),
        'decimals': data.get('decimals', 18),
        'contract_address': data.get('contract_address', ''),
        'website_url': data.get('website_url', ''),
        'whitepaper_url': data.get('whitepaper_url', ''),
        'description': data.get('description', ''),
        'socials': data.get('socials', {}),
        'networks': [],
        'is_listed': False,
        'created_by': g.user.get('id'),
        'created_at': datetime.now().isoformat()
    }
    
    g.data['coins'].append(coin)
    return jsonify(coin), 201

@app.route('/api/coins/<int:coin_id>', methods=['PUT'])
@require_auth
@require_role('admin')
def update_coin(coin_id):
    """Update coin"""
    coin = next((c for c in g.data['coins'] if c.get('id') == coin_id), None)
    if not coin:
        return jsonify({'error': 'Coin not found'}), 404
    
    data = request.json
    for key in ['name', 'symbol', 'type', 'status', 'logo_url', 'website_url', 'description', 'socials']:
        if key in data:
            coin[key] = data[key]
    
    coin['updated_at'] = datetime.now().isoformat()
    return jsonify(coin)

@app.route('/api/coins/<int:coin_id>', methods=['DELETE'])
@require_auth
@require_role('admin')
def delete_coin(coin_id):
    """Delete coin"""
    g.data['coins'] = [c for c in g.data['coins'] if c.get('id') != coin_id]
    return jsonify({'message': 'Coin deleted'})

# ============================================
# NETWORK ADDRESS ROUTES
# ============================================

@app.route('/api/coins/<int:coin_id>/addresses', methods=['GET'])
@require_auth
def get_coin_addresses(coin_id):
    """Get deposit/withdrawal addresses for a coin"""
    coin = next((c for c in g.data['coins'] if c.get('id') == coin_id), None)
    if not coin:
        return jsonify({'error': 'Coin not found'}), 404
    
    return jsonify(coin.get('networks', []))

@app.route('/api/coins/<int:coin_id>/addresses/deposit', methods=['POST'])
@require_auth
@require_role('admin')
def generate_deposit_address(coin_id):
    """Generate deposit address for a network"""
    data = request.json
    network = data.get('network')
    address_type = data.get('type', 'deposit')
    
    if not network:
        return jsonify({'error': 'Network is required'}), 400
    
    coin = next((c for c in g.data['coins'] if c.get('id') == coin_id), None)
    if not coin:
        return jsonify({'error': 'Coin not found'}), 404
    
    # Generate address based on network type
    address = generate_crypto_address(network)
    
    # Update or add address
    networks = coin.get('networks', [])
    existing = next((n for n in networks if n.get('network') == network), None)
    
    if existing:
        existing[f'{address_type}_address'] = address
    else:
        networks.append({
            'network': network,
            'deposit_address': address if address_type == 'deposit' else '',
            'withdraw_address': address if address_type == 'withdraw' else '',
            'deposit_enabled': True,
            'withdraw_enabled': True
        })
        coin['networks'] = networks
    
    return jsonify({'network': network, f'{address_type}_address': address})

@app.route('/api/coins/<int:coin_id>/addresses/withdraw', methods=['POST'])
@require_auth
@require_role('admin')
def generate_withdraw_address(coin_id):
    """Generate withdrawal address for a network"""
    data = request.json
    network = data.get('network')
    
    if not network:
        return jsonify({'error': 'Network is required'}), 400
    
    # Same as deposit, just different type
    address = generate_crypto_address(network)
    
    coin = next((c for c in g.data['coins'] if c.get('id') == coin_id), None)
    if not coin:
        return jsonify({'error': 'Coin not found'}), 404
    
    networks = coin.get('networks', [])
    existing = next((n for n in networks if n.get('network') == network), None)
    
    if existing:
        existing['withdraw_address'] = address
    else:
        networks.append({
            'network': network,
            'deposit_address': '',
            'withdraw_address': address,
            'deposit_enabled': True,
            'withdraw_enabled': True
        })
        coin['networks'] = networks
    
    return jsonify({'network': network, 'withdraw_address': address})

# ============================================
# NETWORK ROUTES
# ============================================

@app.route('/api/networks', methods=['GET'])
def get_networks():
    """Get all blockchain networks"""
    return jsonify(g.data.get('networks', []))

@app.route('/api/networks', methods=['POST'])
@require_auth
@require_role('admin')
def create_network():
    """Create new blockchain network"""
    data = request.json
    
    network = {
        'id': len(g.data.get('networks', [])) + 1,
        'name': data.get('name'),
        'symbol': data.get('symbol', '').upper(),
        'chain_id': data.get('chain_id'),
        'type': data.get('type'),
        'rpc_url': data.get('rpc_url', ''),
        'explorer_url': data.get('explorer_url', ''),
        'color': data.get('color', '#F0B90B'),
        'status': data.get('status', 'active'),
        'created_at': datetime.now().isoformat()
    }
    
    if 'networks' not in g.data:
        g.data['networks'] = []
    g.data['networks'].append(network)
    
    return jsonify(network), 201

# ============================================
# TRADING PAIR ROUTES
# ============================================

@app.route('/api/pairs', methods=['GET'])
def get_trading_pairs():
    """Get all trading pairs"""
    return jsonify(g.data['trading_pairs'])

@app.route('/api/pairs/<pair_symbol>', methods=['GET'])
def get_trading_pair(pair_symbol):
    """Get single trading pair"""
    pair = next((p for p in g.data['trading_pairs'] if p.get('pair_symbol') == pair_symbol), None)
    if not pair:
        return jsonify({'error': 'Trading pair not found'}), 404
    return jsonify(pair)

@app.route('/api/pairs', methods=['POST'])
@require_auth
@require_role('manager')
def create_trading_pair():
    """Create new trading pair"""
    data = request.json
    
    base_coin = data.get('base_coin')
    quote_coin = data.get('quote_coin')
    
    if not base_coin or not quote_coin:
        return jsonify({'error': 'Base and quote coins are required'}), 400
    
    pair_symbol = f"{base_coin}/{quote_coin}"
    
    pair = {
        'id': len(g.data['trading_pairs']) + 1,
        'base_coin': base_coin,
        'quote_coin': quote_coin,
        'pair_symbol': pair_symbol,
        'status': data.get('status', 'pending'),
        'maker_fee': data.get('maker_fee', 0.001),
        'taker_fee': data.get('taker_fee', 0.001),
        'min_trade_amount': data.get('min_trade_amount', 0.0001),
        'price_precision': data.get('price_precision', 8),
        'quantity_precision': data.get('quantity_precision', 8),
        'is_active': False,
        'created_by': g.user.get('id'),
        'created_at': datetime.now().isoformat()
    }
    
    g.data['trading_pairs'].append(pair)
    return jsonify(pair), 201

@app.route('/api/pairs/<pair_symbol>', methods=['PUT'])
@require_auth
@require_role('manager')
def update_trading_pair(pair_symbol):
    """Update trading pair"""
    pair = next((p for p in g.data['trading_pairs'] if p.get('pair_symbol') == pair_symbol), None)
    if not pair:
        return jsonify({'error': 'Trading pair not found'}), 404
    
    data = request.json
    for key in ['status', 'maker_fee', 'taker_fee', 'min_trade_amount', 'is_active']:
        if key in data:
            pair[key] = data[key]
    
    pair['updated_at'] = datetime.now().isoformat()
    return jsonify(pair)

# ============================================
# WALLET/ADDRESS GENERATION
# ============================================

def generate_crypto_address(network_type):
    """Generate cryptocurrency address based on network type"""
    import random
    import string
    
    chars = string.ascii_letters + string.digits
    
    if network_type in ['bitcoin', 'BTC', 'btc']:
        # Bitcoin Legacy/P2PKH
        return 'bc1q' + ''.join(random.choices(chars, k=38))
    elif network_type in ['ethereum', 'ETH', 'bsc', 'BSC', 'polygon', 'MATIC', 'arbitrum', 'OP', 'avalanche']:
        # EVM compatible (ERC20/BEP20)
        return '0x' + ''.join(random.choices(chars, k=40))
    elif network_type in ['solana', 'SOL']:
        # Solana (Base58)
        return ''.join(random.choices(chars, k=44))
    elif network_type in ['tron', 'TRX']:
        # Tron (Base58)
        return 'T' + ''.join(random.choices(chars, k=33))
    else:
        # Generic
        return ''.join(random.choices(chars, k=42))

# ============================================
# TRANSACTION ROUTES
# ============================================

@app.route('/api/transactions', methods=['GET'])
@require_auth
def get_transactions():
    """Get user transactions"""
    user_id = g.user.get('id')
    transactions = [t for t in g.data.get('transactions', []) if t.get('user_id') == user_id]
    return jsonify(transactions)

@app.route('/api/transactions', methods=['POST'])
@require_auth
def create_transaction():
    """Create new transaction (deposit/withdrawal request)"""
    data = request.json
    
    tx = {
        'id': len(g.data.get('transactions', [])) + 1,
        'user_id': g.user.get('id'),
        'coin_id': data.get('coin_id'),
        'network': data.get('network'),
        'type': data.get('type'),
        'amount': data.get('amount'),
        'to_address': data.get('to_address', ''),
        'status': 'pending',
        'created_at': datetime.now().isoformat()
    }
    
    if 'transactions' not in g.data:
        g.data['transactions'] = []
    g.data['transactions'].append(tx)
    
    return jsonify(tx), 201

# ============================================
# UTILITY ROUTES
# ============================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get global statistics"""
    return jsonify({
        'total_coins': len(g.data['coins']),
        'total_networks': len(g.data.get('networks', [])),
        'total_pairs': len(g.data['trading_pairs']),
        'total_transactions': len(g.data.get('transactions', []))
    })

# Initialize with sample data
def init_sample_data():
    data = load_data()
    
    if not data.get('networks'):
        data['networks'] = [
            {'id': 1, 'name': 'Bitcoin', 'symbol': 'BTC', 'chain_id': '1', 'type': 'main', 'color': '#F7931A', 'status': 'active'},
            {'id': 2, 'name': 'Ethereum', 'symbol': 'ETH', 'chain_id': '1', 'type': 'erc20', 'color': '#627EEA', 'status': 'active'},
            {'id': 3, 'name': 'BNB Smart Chain', 'symbol': 'BSC', 'chain_id': '56', 'type': 'bep20', 'color': '#F0B90B', 'status': 'active'},
            {'id': 4, 'name': 'Solana', 'symbol': 'SOL', 'chain_id': 'main', 'type': 'spl', 'color': '#00D4A1', 'status': 'active'},
            {'id': 5, 'name': 'Polygon', 'symbol': 'MATIC', 'chain_id': '137', 'type': 'erc20', 'color': '#8247E5', 'status': 'active'},
            {'id': 6, 'name': 'Avalanche', 'symbol': 'AVAX', 'chain_id': '43114', 'type': 'c-chain', 'color': '#E84142', 'status': 'active'},
            {'id': 7, 'name': 'Arbitrum', 'symbol': 'ARB', 'chain_id': '42161', 'type': 'erc20', 'color': '#28A0F0', 'status': 'active'},
            {'id': 8, 'name': 'Optimism', 'symbol': 'OP', 'chain_id': '10', 'type': 'erc20', 'color': '#FF0420', 'status': 'active'},
            {'id': 9, 'name': 'Tron', 'symbol': 'TRX', 'chain_id': 'main', 'type': 'trc20', 'color': '#FF0013', 'status': 'active'}
        ]
    
    if not data.get('coins'):
        data['coins'] = [
            {
                'id': 1, 'name': 'Bitcoin', 'symbol': 'BTC', 'type': 'coin', 'status': 'active', 'is_listed': True,
                'networks': [{'network': 'bitcoin', 'deposit_address': 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh', 'deposit_enabled': True, 'withdraw_enabled': True}],
                'description': 'Decentralized digital currency'
            },
            {
                'id': 2, 'name': 'Ethereum', 'symbol': 'ETH', 'type': 'token', 'status': 'active', 'is_listed': True,
                'networks': [{'network': 'ethereum', 'deposit_address': '0x742d35Cc6634C0532925a3b5448C0f6d3f7d3d3d3', 'deposit_enabled': True, 'withdraw_enabled': True}],
                'description': 'Smart contract platform'
            },
            {
                'id': 3, 'name': 'BNB', 'symbol': 'BNB', 'type': 'token', 'status': 'active', 'is_listed': True,
                'networks': [{'network': 'bsc', 'deposit_address': '0x742d35Cc6634C0532925a3b5448C0f6d3f7d3d3d3', 'deposit_enabled': True, 'withdraw_enabled': True}],
                'description': 'BNB Chain native token'
            },
            {
                'id': 4, 'name': 'Solana', 'symbol': 'SOL', 'type': 'coin', 'status': 'active', 'is_listed': True,
                'networks': [{'network': 'solana', 'deposit_address': '7xKXtg2CW87d97TXJSDbDToRdfGjnz6rBf6uccrF7F6P', 'deposit_enabled': True, 'withdraw_enabled': True}],
                'description': 'High-performance blockchain'
            },
            {
                'id': 5, 'name': 'Tether USD', 'symbol': 'USDT', 'type': 'token', 'status': 'active', 'is_listed': True,
                'networks': [
                    {'network': 'ethereum', 'deposit_address': '0x742d35Cc6634C0532925a3b5448C0f6d3f7d3d3d3', 'deposit_enabled': True, 'withdraw_enabled': True},
                    {'network': 'bsc', 'deposit_address': '0x742d35Cc6634C0532925a3b5448C0f6d3f7d3d3d3', 'deposit_enabled': True, 'withdraw_enabled': True},
                    {'network': 'tron', 'deposit_address': 'TXkCwm3BiWqY5GgF1khiV4F2Y8a6x6J3r9', 'deposit_enabled': True, 'withdraw_enabled': True}
                ],
                'description': 'USD-pegged stablecoin'
            }
        ]
    
    if not data.get('trading_pairs'):
        data['trading_pairs'] = [
            {'id': 1, 'base_coin': 'BTC', 'quote_coin': 'USDT', 'pair_symbol': 'BTC/USDT', 'status': 'active', 'is_active': True, 'maker_fee': 0.001, 'taker_fee': 0.001},
            {'id': 2, 'base_coin': 'ETH', 'quote_coin': 'USDT', 'pair_symbol': 'ETH/USDT', 'status': 'active', 'is_active': True, 'maker_fee': 0.001, 'taker_fee': 0.001},
            {'id': 3, 'base_coin': 'BNB', 'quote_coin': 'USDT', 'pair_symbol': 'BNB/USDT', 'status': 'active', 'is_active': True, 'maker_fee': 0.001, 'taker_fee': 0.001},
            {'id': 4, 'base_coin': 'SOL', 'quote_coin': 'USDT', 'pair_symbol': 'SOL/USDT', 'status': 'active', 'is_active': True, 'maker_fee': 0.001, 'taker_fee': 0.001},
            {'id': 5, 'base_coin': 'USDT', 'quote_coin': 'USDT', 'pair_symbol': 'USDT/USDT', 'status': 'active', 'is_active': True, 'maker_fee': 0, 'taker_fee': 0}
        ]
    
    if not data.get('users'):
        data['users'] = [
            {'id': 1, 'username': 'admin', 'email': 'admin@tigerex.com', 'password': hashlib.sha256('admin123'.encode()).hexdigest(), 'role': 'admin', 'status': 'active'},
            {'id': 2, 'username': 'manager', 'email': 'manager@tigerex.com', 'password': hashlib.sha256('manager123'.encode()).hexdigest(), 'role': 'manager', 'status': 'active'},
            {'id': 3, 'username': 'trader', 'email': 'trader@tigerex.com', 'password': hashlib.sha256('trader123'.encode()).hexdigest(), 'role': 'trader', 'status': 'active'}
        ]
    
    save_data(data)

# Initialize sample data on startup
init_sample_data()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
