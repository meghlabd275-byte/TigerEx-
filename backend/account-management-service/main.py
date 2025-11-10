#!/usr/bin/env python3
"""
Account Management Service
Comprehensive account management including VIP upgrades, profile management, and account info
"""

from flask import Flask, request, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import os
import uuid
from authlib.integrations.flask_client import OAuth
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/tigerex')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)
oauth = OAuth(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models
class UserAccount(db.Model):
    __tablename__ = 'user_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    binance_id = db.Column(db.String(20), unique=True)
    
    # Account Status
    account_type = db.Column(db.String(20), default='Regular')
    verification_status = db.Column(db.String(20), default='Unverified')
    account_status = db.Column(db.String(20), default='Active')
    is_admin = db.Column(db.Boolean, default=False)
    
    # Profile Information
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    date_of_birth = db.Column(db.Date)
    nationality = db.Column(db.String(50))
    phone_number = db.Column(db.String(20))
    
    # VIP Information
    vip_level = db.Column(db.Integer, default=0)
    vip_progress = db.Column(db.Float, default=0.0)
    trading_volume_30d = db.Column(db.Float, default=0.0)
    bnb_balance = db.Column(db.Float, default=0.0)
    
    # Social Connections
    twitter_connected = db.Column(db.Boolean, default=False)
    telegram_connected = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Admin check decorator
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()
            account = UserAccount.query.filter_by(user_id=user_id).first()
            if not account or not account.is_admin:
                return jsonify({'success': False, 'error': 'Admin access required'}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

# Social Login Routes
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
)

@app.route('/login/google')
def login_google():
    redirect_uri = url_for('authorized_google', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/authorized')
def authorized_google():
    token = google.authorize_access_token()
    user_info = google.get('userinfo').json()
    
    user = UserAccount.query.filter_by(email=user_info['email']).first()
    if not user:
        user = UserAccount(
            user_id=str(uuid.uuid4()),
            username=user_info['name'],
            email=user_info['email'],
            binance_id=str(uuid.uuid4())[:8].upper()
        )
        db.session.add(user)
        db.session.commit()
    
    access_token = create_access_token(identity=user.user_id)
    return jsonify(access_token=access_token)

@app.route('/api/admin/accounts', methods=['GET'])
@jwt_required()
@admin_required()
def get_all_user_accounts():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        accounts = UserAccount.query.paginate(page, per_page, False)
        
        return jsonify({
            'success': True,
            'accounts': [
                {
                    'user_id': account.user_id,
                    'username': account.username,
                    'email': account.email,
                    'binance_id': account.binance_id,
                    'account_type': account.account_type,
                    'verification_status': account.verification_status,
                    'account_status': account.account_status,
                    'is_admin': account.is_admin,
                    'created_at': account.created_at.isoformat()
                }
                for account in accounts.items
            ],
            'pagination': {
                'page': accounts.page,
                'per_page': accounts.per_page,
                'total': accounts.total,
                'total_pages': accounts.pages
            }
        })
    except Exception as e:
        logger.error(f"Error getting all accounts: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/account/resume', methods=['POST'])
@jwt_required()
@admin_required()
def resume_account():
    try:
        data = request.get_json()
        user_to_resume_id = data.get('user_id')
        
        if not user_to_resume_id:
            return jsonify({'success': False, 'error': 'User ID is required'}), 400
            
        account = UserAccount.query.filter_by(user_id=user_to_resume_id).first()
        if not account:
            return jsonify({'success': False, 'error': 'Account not found'}), 404
            
        if account.account_status != 'Suspended':
            return jsonify({'success': False, 'error': 'Account is not suspended'}), 400
            
        account.account_status = 'Active'
        account.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Account resumed successfully'})
    except Exception as e:
        logger.error(f"Error resuming account: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/account/email/<email>', methods=['GET'])
@jwt_required()
@admin_required()
def get_user_account_by_email(email):
    try:
        account = UserAccount.query.filter_by(email=email).first()
        
        if not account:
            return jsonify({'success': False, 'error': 'Account not found'}), 404
        
        return jsonify({
            'success': True,
            'account': {
                'user_id': account.user_id,
                'username': account.username,
                'email': account.email,
                'binance_id': account.binance_id,
                'account_type': account.account_type,
                'verification_status': account.verification_status,
                'account_status': account.account_status,
                'is_admin': account.is_admin,
                'created_at': account.created_at.isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Error getting account info: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/account/<user_id>', methods=['GET'])
@jwt_required()
@admin_required()
def get_user_account_by_id(user_id):
    try:
        account = UserAccount.query.filter_by(user_id=user_id).first()
        
        if not account:
            return jsonify({'success': False, 'error': 'Account not found'}), 404
        
        return jsonify({
            'success': True,
            'account': {
                'user_id': account.user_id,
                'username': account.username,
                'email': account.email,
                'binance_id': account.binance_id,
                'account_type': account.account_type,
                'verification_status': account.verification_status,
                'account_status': account.account_status,
                'is_admin': account.is_admin,
                'created_at': account.created_at.isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Error getting account info: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/account/<user_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_user_account(user_id):
    try:
        account = UserAccount.query.filter_by(user_id=user_id).first()
        
        if not account:
            return jsonify({'success': False, 'error': 'Account not found'}), 404
            
        db.session.delete(account)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Account deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting account: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/account/profile', methods=['GET'])
   @jwt_required()
   def get_account_profile():
       try:
           user_id = get_jwt_identity()
           account = UserAccount.query.filter_by(user_id=user_id).first()
           
           if not account:
               return jsonify({'success': False, 'error': 'Account not found'}), 404
           
           return jsonify({
               'success': True,
               'profile': {
                   'user_id': account.user_id,
                   'username': account.username,
                   'email': account.email,
                   'binance_id': account.binance_id,
                   'account_type': account.account_type,
                   'verification_status': account.verification_status,
                   'account_status': account.account_status,
                   'is_admin': account.is_admin,
                   'first_name': account.first_name,
                   'last_name': account.last_name,
                   'date_of_birth': account.date_of_birth.isoformat() if account.date_of_birth else None,
                   'nationality': account.nationality,
                   'phone_number': account.phone_number,
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
           logger.error(f"Error getting account profile: {str(e)}")
           return jsonify({'success': False, 'error': str(e)}), 500

   @app.route('/api/account/profile', methods=['PUT'])
   @jwt_required()
   def update_account_profile():
       try:
           user_id = get_jwt_identity()
           account = UserAccount.query.filter_by(user_id=user_id).first()
           
           if not account:
               return jsonify({'success': False, 'error': 'Account not found'}), 404
           
           data = request.get_json()
           
           # Update profile fields
           if 'first_name' in data:
               account.first_name = data['first_name']
           if 'last_name' in data:
               account.last_name = data['last_name']
           if 'date_of_birth' in data:
               account.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
           if 'nationality' in data:
               account.nationality = data['nationality']
           if 'phone_number' in data:
               account.phone_number = data['phone_number']
           
           account.updated_at = datetime.utcnow()
           db.session.commit()
           
           return jsonify({'success': True, 'message': 'Profile updated successfully'})
       except Exception as e:
           logger.error(f"Error updating account profile: {str(e)}")
           return jsonify({'success': False, 'error': str(e)}), 500

   @app.route('/api/account/vip/upgrade', methods=['POST'])
   @jwt_required()
   def upgrade_vip():
       try:
           user_id = get_jwt_identity()
           account = UserAccount.query.filter_by(user_id=user_id).first()
           
           if not account:
               return jsonify({'success': False, 'error': 'Account not found'}), 404
           
           data = request.get_json()
           target_vip_level = data.get('vip_level', account.vip_level + 1)
           
           # Check VIP upgrade requirements
           vip_requirements = {
               1: {'trading_volume': 1000, 'bnb_balance': 0.1},
               2: {'trading_volume': 5000, 'bnb_balance': 0.5},
               3: {'trading_volume': 10000, 'bnb_balance': 1.0},
               4: {'trading_volume': 50000, 'bnb_balance': 5.0},
               5: {'trading_volume': 100000, 'bnb_balance': 10.0}
           }
           
           if target_vip_level not in vip_requirements:
               return jsonify({'success': False, 'error': 'Invalid VIP level'}), 400
           
           requirements = vip_requirements[target_vip_level]
           
           if (account.trading_volume_30d < requirements['trading_volume'] or 
               account.bnb_balance < requirements['bnb_balance']):
               return jsonify({
                   'success': False, 
                   'error': 'Requirements not met',
                   'requirements': requirements,
                   'current': {
                       'trading_volume': account.trading_volume_30d,
                       'bnb_balance': account.bnb_balance
                   }
               }), 400
           
           account.vip_level = target_vip_level
           account.account_type = f'VIP {target_vip_level}'
           account.updated_at = datetime.utcnow()
           db.session.commit()
           
           return jsonify({
               'success': True, 
               'message': f'Successfully upgraded to VIP {target_vip_level}',
               'vip_level': account.vip_level,
               'account_type': account.account_type
           })
       except Exception as e:
           logger.error(f"Error upgrading VIP: {str(e)}")
           return jsonify({'success': False, 'error': str(e)}), 500

   @app.route('/api/admin/account/<user_id>/suspend', methods=['POST'])
   @jwt_required()
   @admin_required()
   def suspend_account(user_id):
       try:
           data = request.get_json()
           reason = data.get('reason', 'Administrative action')
           
           account = UserAccount.query.filter_by(user_id=user_id).first()
           if not account:
               return jsonify({'success': False, 'error': 'Account not found'}), 404
           
           account.account_status = 'Suspended'
           account.updated_at = datetime.utcnow()
           db.session.commit()
           
           return jsonify({'success': True, 'message': f'Account suspended. Reason: {reason}'})
       except Exception as e:
           logger.error(f"Error suspending account: {str(e)}")
           return jsonify({'success': False, 'error': str(e)}), 500

   @app.route('/api/account/verify', methods=['POST'])
   @jwt_required()
   def verify_account():
       try:
           user_id = get_jwt_identity()
           account = UserAccount.query.filter_by(user_id=user_id).first()
           
           if not account:
               return jsonify({'success': False, 'error': 'Account not found'}), 404
           
           data = request.get_json()
           
           # Implement verification logic
           verification_data = {
               'id_document': data.get('id_document'),
               'proof_of_address': data.get('proof_of_address'),
               'selfie': data.get('selfie')
           }
           
           # Simulate verification process
           account.verification_status = 'Pending'
           account.updated_at = datetime.utcnow()
           db.session.commit()
           
           return jsonify({'success': True, 'message': 'Verification submitted for review'})
       except Exception as e:
           logger.error(f"Error verifying account: {str(e)}")
           return jsonify({'success': False, 'error': str(e)}), 500

   @app.route('/api/admin/accounts/search', methods=['POST'])
   @jwt_required()
   @admin_required()
   def search_accounts():
       try:
           data = request.get_json()
           search_term = data.get('search_term', '')
           search_type = data.get('search_type', 'all')
           
           query = UserAccount.query
           
           if search_type == 'username':
               query = query.filter(UserAccount.username.ilike(f'%{search_term}%'))
           elif search_type == 'email':
               query = query.filter(UserAccount.email.ilike(f'%{search_term}%'))
           elif search_type == 'binance_id':
               query = query.filter(UserAccount.binance_id.ilike(f'%{search_term}%'))
           else:  # all
               query = query.filter(
                   db.or_(
                       UserAccount.username.ilike(f'%{search_term}%'),
                       UserAccount.email.ilike(f'%{search_term}%'),
                       UserAccount.binance_id.ilike(f'%{search_term}%')
                   )
               )
           
           accounts = query.all()
           
           return jsonify({
               'success': True,
               'accounts': [
                   {
                       'user_id': account.user_id,
                       'username': account.username,
                       'email': account.email,
                       'binance_id': account.binance_id,
                       'account_type': account.account_type,
                       'verification_status': account.verification_status,
                       'account_status': account.account_status,
                       'is_admin': account.is_admin,
                       'created_at': account.created_at.isoformat()
                   }
                   for account in accounts
               ]
           })
       except Exception as e:
           logger.error(f"Error searching accounts: {str(e)}")
           return jsonify({'success': False, 'error': str(e)}), 500

   if __name__ == '__main__':
       with app.app_context():
           db.create_all()
           logger.info("Account Management Service started successfully")
       app.run(host='0.0.0.0', port=5001, debug=True)
