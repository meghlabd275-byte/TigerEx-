#!/usr/bin/env python3
"""
Account Management Service
Comprehensive account management including VIP upgrades, profile management, and account info
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import os
import uuid

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

# Models
class UserAccount(db.Model):
    __tablename__ = 'user_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    binance_id = db.Column(db.String(20), unique=True)
    
    # Account Status
    account_type = db.Column(db.String(20), default='Regular')  # Regular, VIP1, VIP2, etc.
    verification_status = db.Column(db.String(20), default='Unverified')  # Unverified, Verified, Enhanced
    account_status = db.Column(db.String(20), default='Active')  # Active, Suspended, Closed
    
    # Profile Information
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    date_of_birth = db.Column(db.Date)
    nationality = db.Column(db.String(50))
    phone_number = db.Column(db.String(20))
    
    # VIP Information
    vip_level = db.Column(db.Integer, default=0)
    vip_progress = db.Column(db.Float, default=0.0)  # Progress to next VIP level
    trading_volume_30d = db.Column(db.Float, default=0.0)
    bnb_balance = db.Column(db.Float, default=0.0)
    
    # Social Connections
    twitter_connected = db.Column(db.Boolean, default=False)
    telegram_connected = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VIPBenefit(db.Model):
    __tablename__ = 'vip_benefits'
    
    id = db.Column(db.Integer, primary_key=True)
    vip_level = db.Column(db.Integer, nullable=False)
    benefit_type = db.Column(db.String(50), nullable=False)
    benefit_value = db.Column(db.String(100))
    description = db.Column(db.String(200))

class AccountVerification(db.Model):
    __tablename__ = 'account_verifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    verification_type = db.Column(db.String(50), nullable=False)  # Identity, Address, Enhanced
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected
    documents = db.Column(db.JSON)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    reviewer_id = db.Column(db.String(50))
    notes = db.Column(db.Text)

# Account Routes
@app.route('/api/account/info', methods=['GET'])
@jwt_required()
def get_account_info():
    try:
        user_id = get_jwt_identity()
        account = UserAccount.query.filter_by(user_id=user_id).first()
        
        if not account:
            # Create default account
            binance_id = str(uuid.uuid4())[:8].upper()
            account = UserAccount(
                user_id=user_id,
                username=f"User-{binance_id[:4].lower()}",
                email="user@example.com",
                binance_id=binance_id
            )
            db.session.add(account)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'account': {
                'user_id': account.user_id,
                'username': account.username,
                'email': account.email,
                'binance_id': account.binance_id,
                'account_type': account.account_type,
                'verification_status': account.verification_status,
                'vip_level': account.vip_level,
                'vip_progress': account.vip_progress,
                'trading_volume_30d': account.trading_volume_30d,
                'bnb_balance': account.bnb_balance,
                'twitter_connected': account.twitter_connected,
                'telegram_connected': account.telegram_connected,
                'created_at': account.created_at.isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Error getting account info: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/account/vip/benefits', methods=['GET'])
@jwt_required()
def get_vip_benefits():
    try:
        user_id = get_jwt_identity()
        account = UserAccount.query.filter_by(user_id=user_id).first()
        current_level = account.vip_level if account else 0
        
        # Get benefits for current and next level
        current_benefits = VIPBenefit.query.filter_by(vip_level=current_level).all()
        next_benefits = VIPBenefit.query.filter_by(vip_level=current_level + 1).all()
        
        return jsonify({
            'success': True,
            'current_level': current_level,
            'current_benefits': [{
                'type': benefit.benefit_type,
                'value': benefit.benefit_value,
                'description': benefit.description
            } for benefit in current_benefits],
            'next_level_benefits': [{
                'type': benefit.benefit_type,
                'value': benefit.benefit_value,
                'description': benefit.description
            } for benefit in next_benefits],
            'progress_to_next': account.vip_progress if account else 0.0
        })
    except Exception as e:
        logger.error(f"Error getting VIP benefits: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/account/verification/status', methods=['GET'])
@jwt_required()
def get_verification_status():
    try:
        user_id = get_jwt_identity()
        verifications = AccountVerification.query.filter_by(user_id=user_id).all()
        
        verification_status = {
            'identity': 'Not Started',
            'address': 'Not Started',
            'enhanced': 'Not Started'
        }
        
        for verification in verifications:
            verification_status[verification.verification_type.lower()] = verification.status
        
        return jsonify({
            'success': True,
            'verifications': verification_status,
            'overall_status': 'Verified' if all(status == 'Approved' for status in verification_status.values()) else 'Pending'
        })
    except Exception as e:
        logger.error(f"Error getting verification status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/account/update-profile', methods=['POST'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        account = UserAccount.query.filter_by(user_id=user_id).first()
        if not account:
            return jsonify({'success': False, 'error': 'Account not found'}), 404
        
        # Update profile fields
        if 'first_name' in data:
            account.first_name = data['first_name']
        if 'last_name' in data:
            account.last_name = data['last_name']
        if 'phone_number' in data:
            account.phone_number = data['phone_number']
        if 'nationality' in data:
            account.nationality = data['nationality']
        
        account.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/account/connect-social', methods=['POST'])
@jwt_required()
def connect_social():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        platform = data.get('platform')
        
        account = UserAccount.query.filter_by(user_id=user_id).first()
        if not account:
            return jsonify({'success': False, 'error': 'Account not found'}), 404
        
        if platform == 'twitter':
            account.twitter_connected = True
        elif platform == 'telegram':
            account.telegram_connected = True
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'{platform.title()} connected successfully'})
    except Exception as e:
        logger.error(f"Error connecting social: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'account-management-service',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Initialize VIP benefits
        vip_benefits = [
            # VIP 0 (Regular)
            VIPBenefit(vip_level=0, benefit_type='Trading Fee', benefit_value='0.1%', description='Standard trading fee'),
            VIPBenefit(vip_level=0, benefit_type='Withdrawal Fee', benefit_value='Standard', description='Standard withdrawal fees'),
            
            # VIP 1
            VIPBenefit(vip_level=1, benefit_type='Trading Fee', benefit_value='0.09%', description='Reduced trading fee'),
            VIPBenefit(vip_level=1, benefit_type='Withdrawal Fee', benefit_value='10% Discount', description='10% discount on withdrawal fees'),
            VIPBenefit(vip_level=1, benefit_type='Customer Support', benefit_value='Priority', description='Priority customer support'),
        ]
        
        for benefit in vip_benefits:
            existing = VIPBenefit.query.filter_by(
                vip_level=benefit.vip_level,
                benefit_type=benefit.benefit_type
            ).first()
            if not existing:
                db.session.add(benefit)
        
        db.session.commit()
    
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
