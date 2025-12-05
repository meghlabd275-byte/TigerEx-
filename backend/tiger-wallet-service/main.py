#!/usr/bin/env python3
"""
Tiger Wallet Service
Category: wallet
Description: Comprehensive cryptocurrency wallet service with multi-chain support
"""

from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import os
import uuid
import json
import hashlib
import hmac
from decimal import Decimal
from functools import wraps
from web3 import Web3
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/tigerex')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    kyc_status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Wallet(db.Model):
    __tablename__ = 'wallets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    wallet_id = db.Column(db.String(100), unique=True, nullable=False)
    wallet_name = db.Column(db.String(100), nullable=False)
    wallet_type = db.Column(db.String(50), default='hot')  # 'hot', 'cold', 'hardware', 'paper'
    blockchains = db.Column(db.JSON, default=list)  # List of supported blockchains
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    backup_phrase = db.Column(db.Text)  # Encrypted backup phrase
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed_at = db.Column(db.DateTime, default=datetime.utcnow)

class WalletAddress(db.Model):
    __tablename__ = 'wallet_addresses'
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    blockchain = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    private_key = db.Column(db.Text)  # Encrypted private key
    public_key = db.Column(db.String(200))
    derivation_path = db.Column(db.String(100))  # For HD wallets
    index = db.Column(db.Integer)  # Address index for HD wallets
    is_active = db.Column(db.Boolean, default=True)
    balance = db.Column(db.Numeric(20, 8), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    from_address = db.Column(db.String(200), nullable=False)
    to_address = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Numeric(20, 8), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    blockchain = db.Column(db.String(50), nullable=False)
    transaction_hash = db.Column(db.String(200))
    block_number = db.Column(db.Integer)
    block_hash = db.Column(db.String(200))
    gas_price = db.Column(db.Numeric(20, 8))
    gas_used = db.Column(db.Integer)
    gas_limit = db.Column(db.Integer)
    nonce = db.Column(db.Integer)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'confirmed', 'failed'
    confirmations = db.Column(db.Integer, default=0)
    fee = db.Column(db.Numeric(20, 8), default=0)
    metadata = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime)

class Token(db.Model):
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    blockchain = db.Column(db.String(50), nullable=False)
    contract_address = db.Column(db.String(200))
    decimals = db.Column(db.Integer, default=18)
    is_native = db.Column(db.Boolean, default=False)
    logo_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DeFiProtocol(db.Model):
    __tablename__ = 'defi_protocols'
    id = db.Column(db.Integer, primary_key=True)
    protocol_name = db.Column(db.String(100), nullable=False)
    blockchain = db.Column(db.String(50), nullable=False)
    contract_address = db.Column(db.String(200), nullable=False)
    protocol_type = db.Column(db.String(50), nullable=False)  # 'lending', 'dex', 'yield', 'bridge'
    logo_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class NFTCollection(db.Model):
    __tablename__ = 'nft_collections'
    id = db.Column(db.Integer, primary_key=True)
    collection_name = db.Column(db.String(200), nullable=False)
    blockchain = db.Column(db.String(50), nullable=False)
    contract_address = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(500))
    floor_price = db.Column(db.Numeric(20, 8))
    total_supply = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class NFT(db.Model):
    __tablename__ = 'nfts'
    id = db.Column(db.Integer, primary_key=True)
    nft_id = db.Column(db.String(100), unique=True, nullable=False)
    collection_id = db.Column(db.Integer, db.ForeignKey('nft_collections.id'), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    token_id = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(200))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    attributes = db.Column(db.JSON)
    acquired_at = db.Column(db.DateTime, default=datetime.utcnow)
    acquired_price = db.Column(db.Numeric(20, 8))

class WalletActivity(db.Model):
    __tablename__ = 'wallet_activities'
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # 'send', 'receive', 'swap', 'stake', 'unstake', 'nft_buy', 'nft_sell'
    description = db.Column(db.Text)
    amount = db.Column(db.Numeric(20, 8))
    symbol = db.Column(db.String(20))
    blockchain = db.Column(db.String(50))
    transaction_hash = db.Column(db.String(200))
    metadata = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def require_kyc(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.kyc_status != 'verified':
            return jsonify({'error': 'KYC verification required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def encrypt_private_key(private_key, user_password):
    """Encrypt private key with user password"""
    # This is a simplified encryption - in production, use proper encryption
    return hmac.new(user_password.encode(), private_key.encode(), hashlib.sha256).hexdigest()

def decrypt_private_key(encrypted_key, user_password):
    """Decrypt private key with user password"""
    # This is a simplified decryption - in production, use proper decryption
    return encrypted_key  # Placeholder

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Tiger Wallet Service',
        'version': '1.0.0'
    })

@app.route('/api/wallets', methods=['GET'])
@jwt_required()
def get_wallets():
    user_id = get_jwt_identity()
    wallets = Wallet.query.filter_by(user_id=user_id, is_active=True).all()
    
    return jsonify({
        'wallets': [{
            'id': wallet.id,
            'wallet_id': wallet.wallet_id,
            'wallet_name': wallet.wallet_name,
            'wallet_type': wallet.wallet_type,
            'blockchains': wallet.blockchains,
            'is_verified': wallet.is_verified,
            'created_at': wallet.created_at.isoformat(),
            'last_accessed_at': wallet.last_accessed_at.isoformat()
        } for wallet in wallets]
    })

@app.route('/api/wallets', methods=['POST'])
@jwt_required()
@require_kyc
def create_wallet():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['wallet_name', 'wallet_type', 'blockchains']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if data['wallet_type'] not in ['hot', 'cold', 'hardware']:
        return jsonify({'error': 'Invalid wallet type'}), 400
    
    # Generate unique wallet ID
    wallet_id = f"TW{datetime.utcnow().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    
    # Generate backup phrase for hot wallets
    backup_phrase = None
    if data['wallet_type'] == 'hot':
        backup_phrase = generate_backup_phrase()
    
    wallet = Wallet(
        user_id=user_id,
        wallet_id=wallet_id,
        wallet_name=data['wallet_name'],
        wallet_type=data['wallet_type'],
        blockchains=data['blockchains'],
        backup_phrase=backup_phrase
    )
    
    db.session.add(wallet)
    db.session.commit()
    
    # Generate addresses for each blockchain
    for blockchain in data['blockchains']:
        create_wallet_address(wallet.id, blockchain)
    
    return jsonify({
        'message': 'Wallet created successfully',
        'wallet_id': wallet_id,
        'backup_phrase': backup_phrase
    }), 201

def generate_backup_phrase():
    """Generate 12-word backup phrase"""
    words = [
        'abandon', 'ability', 'able', 'about', 'above', 'absent', 'absorb', 'abstract',
        'absurd', 'abuse', 'access', 'accident', 'account', 'accuse', 'achieve', 'acid',
        'acoustic', 'acquire', 'across', 'act', 'action', 'actor', 'actress', 'actual'
    ]
    
    import random
    phrase = ' '.join(random.choices(words, k=12))
    return phrase

def create_wallet_address(wallet_id, blockchain):
    """Create wallet address for specific blockchain"""
    address_data = generate_address_for_blockchain(blockchain)
    
    address = WalletAddress(
        wallet_id=wallet_id,
        blockchain=blockchain,
        address=address_data['address'],
        private_key=address_data['private_key'],
        public_key=address_data['public_key'],
        derivation_path=address_data.get('derivation_path'),
        index=address_data.get('index', 0)
    )
    
    db.session.add(address)

def generate_address_for_blockchain(blockchain):
    """Generate address for specific blockchain"""
    # This is a simplified address generation
    # In production, use proper blockchain libraries
    
    if blockchain == 'ethereum':
        private_key = f"0x{uuid.uuid4().hex}"
        account = Web3().eth.account.from_key(private_key)
        return {
            'address': account.address,
            'private_key': private_key,
            'public_key': account.key.hex(),
            'derivation_path': "m/44'/60'/0'/0/0",
            'index': 0
        }
    elif blockchain == 'bitcoin':
        # Simplified Bitcoin address generation
        private_key = uuid.uuid4().hex
        address = f"bc1{uuid.uuid4().hex[:32]}"
        return {
            'address': address,
            'private_key': private_key,
            'public_key': None,
            'derivation_path': "m/44'/0'/0'/0/0",
            'index': 0
        }
    else:
        # Generic address generation for other blockchains
        private_key = uuid.uuid4().hex
        address = f"{blockchain[:3].lower()}1{uuid.uuid4().hex[:32]}"
        return {
            'address': address,
            'private_key': private_key,
            'public_key': None,
            'derivation_path': None,
            'index': 0
        }

@app.route('/api/wallets/<int:wallet_id>/addresses', methods=['GET'])
@jwt_required()
def get_wallet_addresses(wallet_id):
    user_id = get_jwt_identity()
    
    wallet = Wallet.query.filter_by(id=wallet_id, user_id=user_id).first()
    if not wallet:
        return jsonify({'error': 'Wallet not found'}), 404
    
    addresses = WalletAddress.query.filter_by(wallet_id=wallet_id, is_active=True).all()
    
    # Update last accessed time
    wallet.last_accessed_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'addresses': [{
            'id': addr.id,
            'blockchain': addr.blockchain,
            'address': addr.address,
            'balance': float(addr.balance),
            'created_at': addr.created_at.isoformat()
        } for addr in addresses]
    })

@app.route('/api/wallets/<int:wallet_id>/balance', methods=['GET'])
@jwt_required()
def get_wallet_balance(wallet_id):
    user_id = get_jwt_identity()
    
    wallet = Wallet.query.filter_by(id=wallet_id, user_id=user_id).first()
    if not wallet:
        return jsonify({'error': 'Wallet not found'}), 404
    
    addresses = WalletAddress.query.filter_by(wallet_id=wallet_id, is_active=True).all()
    
    balances = {}
    total_value_usd = Decimal('0')
    
    for addr in addresses:
        # Update balance from blockchain (simplified)
        current_balance = get_blockchain_balance(addr.blockchain, addr.address)
        addr.balance = current_balance
        
        # Group by blockchain
        if addr.blockchain not in balances:
            balances[addr.blockchain] = {}
        
        balances[addr.blockchain][addr.blockchain.upper()] = float(current_balance)
        
        # Get token balances for this address
        token_balances = get_token_balances(addr.blockchain, addr.address)
        balances[addr.blockchain].update(token_balances)
    
    db.session.commit()
    
    return jsonify({
        'wallet_id': wallet.wallet_id,
        'balances': balances,
        'total_value_usd': float(total_value_usd)
    })

def get_blockchain_balance(blockchain, address):
    """Get balance from blockchain (simplified)"""
    # In production, this would call actual blockchain APIs
    return Decimal('1.5')  # Placeholder

def get_token_balances(blockchain, address):
    """Get token balances for address (simplified)"""
    # In production, this would call actual blockchain APIs
    return {
        'USDT': 1000.0,
        'USDC': 500.0,
        'ETH': 2.5
    }

@app.route('/api/transactions/send', methods=['POST'])
@jwt_required()
@require_kyc
def send_transaction():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['wallet_id', 'from_address', 'to_address', 'amount', 'symbol', 'blockchain']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate wallet ownership
    wallet = Wallet.query.filter_by(id=data['wallet_id'], user_id=user_id).first()
    if not wallet:
        return jsonify({'error': 'Wallet not found'}), 404
    
    # Validate address ownership
    from_address = WalletAddress.query.filter_by(
        wallet_id=data['wallet_id'],
        address=data['from_address'],
        blockchain=data['blockchain'],
        is_active=True
    ).first()
    
    if not from_address:
        return jsonify({'error': 'Invalid from address'}), 400
    
    amount = Decimal(str(data['amount']))
    
    # Check balance
    if from_address.balance < amount:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    # Generate transaction ID
    transaction_id = f"TX{datetime.utcnow().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    
    # Create transaction record
    transaction = Transaction(
        transaction_id=transaction_id,
        wallet_id=data['wallet_id'],
        from_address=data['from_address'],
        to_address=data['to_address'],
        amount=amount,
        symbol=data['symbol'],
        blockchain=data['blockchain'],
        fee=Decimal(str(data.get('fee', 0))),
        metadata=data.get('metadata', {})
    )
    
    db.session.add(transaction)
    
    # Update balance (pending)
    from_address.balance -= amount
    
    # Create activity record
    activity = WalletActivity(
        wallet_id=data['wallet_id'],
        activity_type='send',
        description=f"Sent {amount} {data['symbol']} to {data['to_address'][:10]}...",
        amount=amount,
        symbol=data['symbol'],
        blockchain=data['blockchain']
    )
    
    db.session.add(activity)
    db.session.commit()
    
    # Process transaction on blockchain (simplified)
    try:
        result = process_blockchain_transaction(transaction, from_address)
        transaction.transaction_hash = result.get('tx_hash')
        transaction.status = 'pending'
        db.session.commit()
        
        return jsonify({
            'message': 'Transaction sent successfully',
            'transaction_id': transaction_id,
            'transaction_hash': result.get('tx_hash'),
            'status': 'pending'
        })
        
    except Exception as e:
        transaction.status = 'failed'
        db.session.commit()
        return jsonify({'error': f'Transaction failed: {str(e)}'}), 500

def process_blockchain_transaction(transaction, from_address):
    """Process transaction on blockchain (simplified)"""
    # In production, this would use actual blockchain libraries
    return {
        'tx_hash': f"0x{uuid.uuid4().hex}",
        'block_number': 12345
    }

@app.route('/api/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    user_id = get_jwt_identity()
    wallet_id = request.args.get('wallet_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = db.session.query(Transaction, Wallet)\
        .join(Wallet, Transaction.wallet_id == Wallet.id)\
        .filter(Wallet.user_id == user_id)
    
    if wallet_id:
        query = query.filter(Transaction.wallet_id == wallet_id)
    
    transactions = query.order_by(Transaction.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return jsonify({
        'transactions': [{
            'transaction_id': tx.transaction_id,
            'from_address': tx.from_address,
            'to_address': tx.to_address,
            'amount': float(tx.amount),
            'symbol': tx.symbol,
            'blockchain': tx.blockchain,
            'status': tx.status,
            'transaction_hash': tx.transaction_hash,
            'confirmations': tx.confirmations,
            'fee': float(tx.fee),
            'created_at': tx.created_at.isoformat(),
            'confirmed_at': tx.confirmed_at.isoformat() if tx.confirmed_at else None
        } for tx, wallet in transactions.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': transactions.total,
            'pages': transactions.pages
        }
    })

@app.route('/api/nfts', methods=['GET'])
@jwt_required()
def get_nfts():
    user_id = get_jwt_identity()
    wallet_id = request.args.get('wallet_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = db.session.query(NFT, Wallet, NFTCollection)\
        .join(Wallet, NFT.wallet_id == Wallet.id)\
        .join(NFTCollection, NFT.collection_id == NFTCollection.id)\
        .filter(Wallet.user_id == user_id)
    
    if wallet_id:
        query = query.filter(NFT.wallet_id == wallet_id)
    
    nfts = query.order_by(NFT.acquired_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return jsonify({
        'nfts': [{
            'nft_id': nft.nft_id,
            'collection': {
                'name': collection.collection_name,
                'contract_address': collection.contract_address,
                'floor_price': float(collection.floor_price) if collection.floor_price else None
            },
            'token_id': nft.token_id,
            'name': nft.name,
            'description': nft.description,
            'image_url': nft.image_url,
            'attributes': nft.attributes,
            'acquired_at': nft.acquired_at.isoformat(),
            'acquired_price': float(nft.acquired_price) if nft.acquired_price else None
        } for nft, wallet, collection in nfts.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': nfts.total,
            'pages': nfts.pages
        }
    })

@app.route('/api/defi/protocols', methods=['GET'])
def get_defi_protocols():
    blockchain = request.args.get('blockchain')
    protocol_type = request.args.get('type')
    
    query = DeFiProtocol.query.filter_by(is_active=True)
    
    if blockchain:
        query = query.filter_by(blockchain=blockchain)
    if protocol_type:
        query = query.filter_by(protocol_type=protocol_type)
    
    protocols = query.order_by(DeFiProtocol.protocol_name).all()
    
    return jsonify({
        'protocols': [{
            'id': protocol.id,
            'protocol_name': protocol.protocol_name,
            'blockchain': protocol.blockchain,
            'contract_address': protocol.contract_address,
            'protocol_type': protocol.protocol_type,
            'logo_url': protocol.logo_url
        } for protocol in protocols]
    })

@app.route('/api/admin/tokens', methods=['POST'])
@jwt_required()
def add_token():
    # Check admin permissions
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.email not in ['admin@tigerex.com']:
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    required_fields = ['symbol', 'name', 'blockchain']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    token = Token(
        symbol=data['symbol'],
        name=data['name'],
        blockchain=data['blockchain'],
        contract_address=data.get('contract_address'),
        decimals=data.get('decimals', 18),
        is_native=data.get('is_native', False),
        logo_url=data.get('logo_url')
    )
    
    db.session.add(token)
    db.session.commit()
    
    return jsonify({
        'message': 'Token added successfully',
        'token_id': token.id
    }), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5007, debug=True)