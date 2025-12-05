#!/usr/bin/env python3
"""
Tiger Card Service
Category: financial
Description: Crypto debit card management service
"""

from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import os
import hashlib
import hmac
import uuid
from decimal import Decimal
import requests
import json

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

class Card(db.Model):
    __tablename__ = 'cards'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    card_number = db.Column(db.String(20), unique=True, nullable=False)
    card_type = db.Column(db.String(20), nullable=False)  # 'virtual', 'physical'
    card_brand = db.Column(db.String(20), default='visa')  # 'visa', 'mastercard'
    status = db.Column(db.String(20), default='pending')  # 'pending', 'active', 'blocked', 'expired'
    expiry_month = db.Column(db.Integer, nullable=False)
    expiry_year = db.Column(db.Integer, nullable=False)
    cvv = db.Column(db.String(4), nullable=False)
    currency = db.Column(db.String(10), default='USD')
    spending_limit = db.Column(db.Numeric(20, 8), default=Decimal('10000'))
    daily_limit = db.Column(db.Numeric(20, 8), default=Decimal('5000'))
    monthly_limit = db.Column(db.Numeric(20, 8), default=Decimal('50000'))
    pin = db.Column(db.String(4))
    shipping_address = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    activated_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)

class CardTransaction(db.Model):
    __tablename__ = 'card_transactions'
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    amount = db.Column(db.Numeric(20, 8), nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    merchant_name = db.Column(db.String(200))
    merchant_category = db.Column(db.String(100))
    transaction_type = db.Column(db.String(20), nullable=False)  # 'purchase', 'atm_withdrawal', 'refund'
    status = db.Column(db.String(20), default='pending')  # 'pending', 'completed', 'declined', 'refunded'
    authorization_code = db.Column(db.String(50))
    crypto_amount = db.Column(db.Numeric(20, 8))
    crypto_currency = db.Column(db.String(10))
    exchange_rate = db.Column(db.Numeric(20, 8))
    fee = db.Column(db.Numeric(20, 8), default=0)
    location = db.Column(db.JSON)  # GPS coordinates if available
    metadata = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

class CardReward(db.Model):
    __tablename__ = 'card_rewards'
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    transaction_id = db.Column(db.String(100))
    reward_type = db.Column(db.String(50), nullable=False)  # 'cashback', 'points', 'crypto'
    reward_amount = db.Column(db.Numeric(20, 8), nullable=False)
    reward_currency = db.Column(db.String(10))
    reward_percentage = db.Column(db.Numeric(5, 2))
    merchant_category = db.Column(db.String(100))
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

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Tiger Card Service',
        'version': '1.0.0'
    })

@app.route('/api/cards', methods=['GET'])
@jwt_required()
@require_kyc
def get_cards():
    user_id = get_jwt_identity()
    cards = Card.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'cards': [{
            'id': card.id,
            'card_number': f"****{card.card_number[-4:]}",
            'card_type': card.card_type,
            'card_brand': card.card_brand,
            'status': card.status,
            'expiry_month': card.expiry_month,
            'expiry_year': card.expiry_year,
            'currency': card.currency,
            'spending_limit': float(card.spending_limit),
            'daily_limit': float(card.daily_limit),
            'monthly_limit': float(card.monthly_limit),
            'created_at': card.created_at.isoformat(),
            'activated_at': card.activated_at.isoformat() if card.activated_at else None,
            'expires_at': card.expires_at.isoformat() if card.expires_at else None
        } for card in cards]
    })

@app.route('/api/cards', methods=['POST'])
@jwt_required()
@require_kyc
def create_card():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['card_type']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if data['card_type'] not in ['virtual', 'physical']:
        return jsonify({'error': 'Invalid card type'}), 400
    
    # Check user's existing cards
    existing_cards = Card.query.filter_by(user_id=user_id).count()
    if existing_cards >= 5:  # Limit to 5 cards per user
        return jsonify({'error': 'Maximum card limit reached'}), 400
    
    # Generate card details
    card_number = generate_card_number()
    expiry_month = datetime.utcnow().month
    expiry_year = (datetime.utcnow().year + 4) % 100
    cvv = f"{uuid.uuid4().int % 10000:04d}"
    pin = f"{uuid.uuid4().int % 10000:04d}"
    
    card = Card(
        user_id=user_id,
        card_number=card_number,
        card_type=data['card_type'],
        card_brand=data.get('card_brand', 'visa'),
        expiry_month=expiry_month,
        expiry_year=expiry_year,
        cvv=cvv,
        pin=pin,
        currency=data.get('currency', 'USD'),
        spending_limit=Decimal(str(data.get('spending_limit', 10000))),
        daily_limit=Decimal(str(data.get('daily_limit', 5000))),
        monthly_limit=Decimal(str(data.get('monthly_limit', 50000))),
        shipping_address=data.get('shipping_address') if data['card_type'] == 'physical' else None,
        expires_at=datetime.utcnow().replace(year=datetime.utcnow().year + 4)
    )
    
    db.session.add(card)
    db.session.commit()
    
    # If virtual card, activate immediately
    if data['card_type'] == 'virtual':
        card.status = 'active'
        card.activated_at = datetime.utcnow()
        db.session.commit()
    
    return jsonify({
        'message': 'Card created successfully',
        'card_id': card.id,
        'card_number': f"****{card.card_number[-4:]}",
        'expiry_month': expiry_month,
        'expiry_year': expiry_year,
        'cvv': cvv,
        'status': card.status
    }), 201

def generate_card_number():
    """Generate a valid card number using Luhn algorithm"""
    while True:
        # Generate 16-digit number starting with 4 (Visa)
        prefix = '4'
        middle = f"{uuid.uuid4().int % 10**14:014d}"
        number = prefix + middle
        
        # Apply Luhn algorithm
        if luhn_check(number):
            return number

def luhn_check(card_number):
    """Check if card number passes Luhn algorithm"""
    digits = [int(d) for d in card_number]
    checksum = 0
    
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    
    return checksum % 10 == 0

@app.route('/api/cards/<int:card_id>/activate', methods=['POST'])
@jwt_required()
def activate_card(card_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    card = Card.query.filter_by(id=card_id, user_id=user_id).first()
    if not card:
        return jsonify({'error': 'Card not found'}), 404
    
    if card.status != 'pending':
        return jsonify({'error': 'Card is not pending activation'}), 400
    
    # For physical cards, require CVV and shipping address verification
    if card.card_type == 'physical':
        required_fields = ['cvv', 'shipping_address']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if data['cvv'] != card.cvv:
            return jsonify({'error': 'Invalid CVV'}), 400
    
    card.status = 'active'
    card.activated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Card activated successfully',
        'card_id': card.id,
        'status': card.status
    })

@app.route('/api/cards/<int:card_id>/freeze', methods=['POST'])
@jwt_required()
def freeze_card(card_id):
    user_id = get_jwt_identity()
    
    card = Card.query.filter_by(id=card_id, user_id=user_id).first()
    if not card:
        return jsonify({'error': 'Card not found'}), 404
    
    if card.status != 'active':
        return jsonify({'error': 'Card is not active'}), 400
    
    card.status = 'blocked'
    db.session.commit()
    
    return jsonify({
        'message': 'Card frozen successfully',
        'card_id': card.id,
        'status': card.status
    })

@app.route('/api/cards/<int:card_id>/unfreeze', methods=['POST'])
@jwt_required()
def unfreeze_card(card_id):
    user_id = get_jwt_identity()
    
    card = Card.query.filter_by(id=card_id, user_id=user_id).first()
    if not card:
        return jsonify({'error': 'Card not found'}), 404
    
    if card.status != 'blocked':
        return jsonify({'error': 'Card is not blocked'}), 400
    
    card.status = 'active'
    db.session.commit()
    
    return jsonify({
        'message': 'Card unfrozen successfully',
        'card_id': card.id,
        'status': card.status
    })

@app.route('/api/cards/<int:card_id>/transactions', methods=['GET'])
@jwt_required()
def get_card_transactions(card_id):
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    card = Card.query.filter_by(id=card_id, user_id=user_id).first()
    if not card:
        return jsonify({'error': 'Card not found'}), 404
    
    transactions = CardTransaction.query.filter_by(card_id=card_id)\
        .order_by(CardTransaction.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return jsonify({
        'transactions': [{
            'id': t.id,
            'transaction_id': t.transaction_id,
            'amount': float(t.amount),
            'currency': t.currency,
            'merchant_name': t.merchant_name,
            'merchant_category': t.merchant_category,
            'transaction_type': t.transaction_type,
            'status': t.status,
            'crypto_amount': float(t.crypto_amount) if t.crypto_amount else None,
            'crypto_currency': t.crypto_currency,
            'exchange_rate': float(t.exchange_rate) if t.exchange_rate else None,
            'fee': float(t.fee),
            'created_at': t.created_at.isoformat(),
            'completed_at': t.completed_at.isoformat() if t.completed_at else None
        } for t in transactions.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': transactions.total,
            'pages': transactions.pages
        }
    })

@app.route('/api/cards/<int:card_id>/set-limits', methods=['POST'])
@jwt_required()
def set_card_limits(card_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    card = Card.query.filter_by(id=card_id, user_id=user_id).first()
    if not card:
        return jsonify({'error': 'Card not found'}), 404
    
    # Update limits if provided
    if 'spending_limit' in data:
        card.spending_limit = Decimal(str(data['spending_limit']))
    if 'daily_limit' in data:
        card.daily_limit = Decimal(str(data['daily_limit']))
    if 'monthly_limit' in data:
        card.monthly_limit = Decimal(str(data['monthly_limit']))
    
    db.session.commit()
    
    return jsonify({
        'message': 'Card limits updated successfully',
        'card_id': card.id,
        'spending_limit': float(card.spending_limit),
        'daily_limit': float(card.daily_limit),
        'monthly_limit': float(card.monthly_limit)
    })

@app.route('/api/process-transaction', methods=['POST'])
def process_transaction():
    """External endpoint for processing card transactions"""
    data = request.get_json()
    
    required_fields = ['card_number', 'amount', 'currency', 'merchant_name']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Find card by last 4 digits
    card_last4 = data['card_number'][-4:]
    card = Card.query.filter(Card.card_number.like(f'%{card_last4}')).first()
    
    if not card:
        return jsonify({'error': 'Card not found'}), 404
    
    if card.status != 'active':
        return jsonify({'error': 'Card is not active'}), 400
    
    # Check limits
    if not check_card_limits(card, Decimal(str(data['amount']))):
        return jsonify({'error': 'Transaction exceeds card limits'}), 400
    
    # Generate transaction ID
    transaction_id = f"TC{datetime.utcnow().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    
    # Calculate crypto conversion if needed
    crypto_amount = None
    crypto_currency = None
    exchange_rate = None
    
    if data.get('convert_to_crypto'):
        result = convert_to_crypto(Decimal(str(data['amount'])), data['currency'], data['convert_to_crypto'])
        if result:
            crypto_amount = result['amount']
            crypto_currency = result['currency']
            exchange_rate = result['rate']
    
    # Calculate transaction fee
    fee = calculate_transaction_fee(Decimal(str(data['amount'])), data.get('merchant_category'))
    
    transaction = CardTransaction(
        card_id=card.id,
        transaction_id=transaction_id,
        amount=Decimal(str(data['amount'])),
        currency=data['currency'],
        merchant_name=data['merchant_name'],
        merchant_category=data.get('merchant_category'),
        transaction_type=data.get('transaction_type', 'purchase'),
        crypto_amount=crypto_amount,
        crypto_currency=crypto_currency,
        exchange_rate=exchange_rate,
        fee=fee,
        location=data.get('location'),
        metadata=data.get('metadata', {})
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    # Process the transaction
    transaction.status = 'completed'
    transaction.completed_at = datetime.utcnow()
    transaction.authorization_code = f"AUTH{uuid.uuid4().hex[:8].upper()}"
    db.session.commit()
    
    # Calculate and add rewards
    add_card_rewards(card, transaction)
    
    return jsonify({
        'transaction_id': transaction_id,
        'status': 'completed',
        'authorization_code': transaction.authorization_code,
        'amount': float(transaction.amount),
        'crypto_amount': float(crypto_amount) if crypto_amount else None
    })

def check_card_limits(card, amount):
    """Check if transaction amount exceeds card limits"""
    # Check daily limit
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    daily_spent = db.session.query(db.func.sum(CardTransaction.amount))\
        .filter_by(card_id=card.id, status='completed')\
        .filter(CardTransaction.created_at >= today_start)\
        .scalar() or Decimal('0')
    
    if daily_spent + amount > card.daily_limit:
        return False
    
    # Check monthly limit
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_spent = db.session.query(db.func.sum(CardTransaction.amount))\
        .filter_by(card_id=card.id, status='completed')\
        .filter(CardTransaction.created_at >= month_start)\
        .scalar() or Decimal('0')
    
    if monthly_spent + amount > card.monthly_limit:
        return False
    
    return True

def convert_to_crypto(amount, from_currency, to_crypto):
    """Convert fiat amount to cryptocurrency"""
    try:
        # This is a placeholder for actual exchange rate API
        # Integration with exchange APIs needed
        exchange_rates = {
            'USD-BTC': 0.000025,
            'USD-ETH': 0.00035,
            'EUR-BTC': 0.000027,
            'EUR-ETH': 0.00038
        }
        
        rate_key = f"{from_currency}-{to_crypto}"
        if rate_key not in exchange_rates:
            return None
        
        rate = Decimal(str(exchange_rates[rate_key]))
        crypto_amount = amount * rate
        
        return {
            'amount': crypto_amount,
            'currency': to_crypto,
            'rate': rate
        }
    except Exception as e:
        logger.error(f"Currency conversion error: {str(e)}")
        return None

def calculate_transaction_fee(amount, merchant_category):
    """Calculate transaction fee based on merchant category"""
    fee_rates = {
        'restaurant': 0.025,
        'retail': 0.020,
        'online': 0.030,
        'atm': 0.035,
        'international': 0.040
    }
    
    fee_rate = fee_rates.get(merchant_category, 0.025)
    return amount * Decimal(str(fee_rate))

def add_card_rewards(card, transaction):
    """Add rewards based on transaction"""
    reward_rates = {
        'restaurant': 0.03,
        'retail': 0.02,
        'travel': 0.05,
        'online': 0.025,
        'default': 0.01
    }
    
    reward_rate = reward_rates.get(transaction.merchant_category, reward_rates['default'])
    reward_amount = transaction.amount * Decimal(str(reward_rate))
    
    reward = CardReward(
        card_id=card.id,
        transaction_id=transaction.transaction_id,
        reward_type='cashback',
        reward_amount=reward_amount,
        reward_currency=transaction.currency,
        reward_percentage=reward_rate * 100,
        merchant_category=transaction.merchant_category
    )
    
    db.session.add(reward)
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5003, debug=True)