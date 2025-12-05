#!/usr/bin/env python3
"""
Tiger Pay Service
Category: payment
Description: Comprehensive payment gateway solution for crypto and fiat transactions
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

class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    method_type = db.Column(db.String(50), nullable=False)  # 'crypto', 'card', 'bank'
    method_details = db.Column(db.JSON, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(20, 8), nullable=False)
    currency = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, completed, failed, cancelled
    transaction_type = db.Column(db.String(50), nullable=False)  # payment, withdrawal, deposit
    payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_methods.id'))
    merchant_id = db.Column(db.String(100))
    fee = db.Column(db.Numeric(20, 8), default=0)
    metadata = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

class Merchant(db.Model):
    __tablename__ = 'merchants'
    id = db.Column(db.Integer, primary_key=True)
    merchant_id = db.Column(db.String(100), unique=True, nullable=False)
    business_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    api_key = db.Column(db.String(200), unique=True, nullable=False)
    webhook_url = db.Column(db.String(500))
    fee_percentage = db.Column(db.Numeric(5, 2), default=2.5)
    is_active = db.Column(db.Boolean, default=True)
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
        'service': 'Tiger Pay Service',
        'version': '1.0.0'
    })

@app.route('/api/payment-methods', methods=['GET'])
@jwt_required()
def get_payment_methods():
    user_id = get_jwt_identity()
    methods = PaymentMethod.query.filter_by(user_id=user_id, is_active=True).all()
    
    return jsonify({
        'payment_methods': [{
            'id': method.id,
            'method_type': method.method_type,
            'method_details': method.method_details,
            'created_at': method.created_at.isoformat()
        } for method in methods]
    })

@app.route('/api/payment-methods', methods=['POST'])
@jwt_required()
@require_kyc
def add_payment_method():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['method_type', 'method_details']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    method = PaymentMethod(
        user_id=user_id,
        method_type=data['method_type'],
        method_details=data['method_details']
    )
    
    db.session.add(method)
    db.session.commit()
    
    return jsonify({
        'message': 'Payment method added successfully',
        'payment_method_id': method.id
    }), 201

@app.route('/api/payments', methods=['POST'])
@jwt_required()
@require_kyc
def create_payment():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['amount', 'currency', 'payment_method_id', 'merchant_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate payment method
    payment_method = PaymentMethod.query.filter_by(
        id=data['payment_method_id'], 
        user_id=user_id, 
        is_active=True
    ).first()
    
    if not payment_method:
        return jsonify({'error': 'Invalid payment method'}), 400
    
    # Generate transaction ID
    transaction_id = f"TP{datetime.utcnow().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    
    # Calculate fee
    merchant = Merchant.query.filter_by(merchant_id=data['merchant_id'], is_active=True).first()
    fee_amount = Decimal(str(data['amount'])) * Decimal(str(merchant.fee_percentage / 100)) if merchant else Decimal('0')
    
    transaction = Transaction(
        transaction_id=transaction_id,
        user_id=user_id,
        amount=Decimal(str(data['amount'])),
        currency=data['currency'],
        payment_method_id=data['payment_method_id'],
        merchant_id=data['merchant_id'],
        fee=fee_amount,
        transaction_type='payment',
        metadata=data.get('metadata', {})
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    # Process payment based on method type
    try:
        if payment_method.method_type == 'crypto':
            result = process_crypto_payment(transaction, payment_method)
        elif payment_method.method_type == 'card':
            result = process_card_payment(transaction, payment_method)
        elif payment_method.method_type == 'bank':
            result = process_bank_payment(transaction, payment_method)
        else:
            return jsonify({'error': 'Unsupported payment method'}), 400
        
        transaction.status = 'completed' if result['success'] else 'failed'
        transaction.completed_at = datetime.utcnow() if result['success'] else None
        db.session.commit()
        
        # Send webhook to merchant if applicable
        if merchant and merchant.webhook_url:
            send_merchant_webhook(merchant, transaction, result)
        
        return jsonify({
            'transaction_id': transaction_id,
            'status': transaction.status,
            'message': result.get('message', 'Payment processed')
        })
        
    except Exception as e:
        logger.error(f"Payment processing error: {str(e)}")
        transaction.status = 'failed'
        db.session.commit()
        return jsonify({'error': 'Payment processing failed'}), 500

def process_crypto_payment(transaction, payment_method):
    """Process cryptocurrency payment"""
    try:
        # Integration with blockchain networks
        # This is a placeholder for actual blockchain integration
        return {
            'success': True,
            'message': 'Crypto payment processed successfully',
            'tx_hash': f"0x{uuid.uuid4().hex}"
        }
    except Exception as e:
        logger.error(f"Crypto payment error: {str(e)}")
        return {'success': False, 'message': str(e)}

def process_card_payment(transaction, payment_method):
    """Process card payment"""
    try:
        # Integration with payment processors like Stripe
        # This is a placeholder for actual payment processor integration
        return {
            'success': True,
            'message': 'Card payment processed successfully',
            'charge_id': f"ch_{uuid.uuid4().hex}"
        }
    except Exception as e:
        logger.error(f"Card payment error: {str(e)}")
        return {'success': False, 'message': str(e)}

def process_bank_payment(transaction, payment_method):
    """Process bank transfer"""
    try:
        # Integration with banking systems
        # This is a placeholder for actual bank integration
        return {
            'success': True,
            'message': 'Bank transfer initiated',
            'reference': f"REF{uuid.uuid4().hex[:10].upper()}"
        }
    except Exception as e:
        logger.error(f"Bank payment error: {str(e)}")
        return {'success': False, 'message': str(e)}

def send_merchant_webhook(merchant, transaction, result):
    """Send webhook notification to merchant"""
    try:
        webhook_data = {
            'event': 'payment.completed',
            'transaction': {
                'id': transaction.transaction_id,
                'amount': float(transaction.amount),
                'currency': transaction.currency,
                'status': transaction.status,
                'fee': float(transaction.fee),
                'created_at': transaction.created_at.isoformat()
            }
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-TigerPay-Signature': generate_webhook_signature(webhook_data, merchant.api_key)
        }
        
        requests.post(merchant.webhook_url, json=webhook_data, headers=headers, timeout=10)
    except Exception as e:
        logger.error(f"Webhook delivery failed: {str(e)}")

def generate_webhook_signature(data, secret):
    """Generate webhook signature for security"""
    payload = str(data).encode('utf-8')
    return hmac.new(secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()

@app.route('/api/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    transactions = Transaction.query.filter_by(user_id=user_id)\
        .order_by(Transaction.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return jsonify({
        'transactions': [{
            'transaction_id': t.transaction_id,
            'amount': float(t.amount),
            'currency': t.currency,
            'status': t.status,
            'transaction_type': t.transaction_type,
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

@app.route('/api/merchant/register', methods=['POST'])
def register_merchant():
    data = request.get_json()
    
    required_fields = ['business_name', 'email', 'webhook_url']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Generate unique merchant ID and API key
    merchant_id = f"M{datetime.utcnow().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    api_key = f"tk_{uuid.uuid4().hex}"
    
    merchant = Merchant(
        merchant_id=merchant_id,
        business_name=data['business_name'],
        email=data['email'],
        api_key=api_key,
        webhook_url=data['webhook_url'],
        fee_percentage=data.get('fee_percentage', 2.5)
    )
    
    db.session.add(merchant)
    db.session.commit()
    
    return jsonify({
        'message': 'Merchant registered successfully',
        'merchant_id': merchant_id,
        'api_key': api_key
    }), 201

@app.route('/api/admin/transactions', methods=['GET'])
@jwt_required()
def admin_get_transactions():
    # Check if user is admin
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.email not in ['admin@tigerex.com']:
        return jsonify({'error': 'Admin access required'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    status = request.args.get('status')
    
    query = Transaction.query
    if status:
        query = query.filter_by(status=status)
    
    transactions = query.order_by(Transaction.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return jsonify({
        'transactions': [{
            'transaction_id': t.transaction_id,
            'user_id': t.user_id,
            'amount': float(t.amount),
            'currency': t.currency,
            'status': t.status,
            'transaction_type': t.transaction_type,
            'fee': float(t.fee),
            'merchant_id': t.merchant_id,
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5002, debug=True)