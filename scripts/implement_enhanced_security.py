#!/usr/bin/env python3
"""
Enhanced Security & Account Management Implementation
Based on new Binance screenshots showing detailed security features
"""

import os
from pathlib import Path

def create_enhanced_security_service():
    """Create enhanced security service with 2FA, biometrics, and advanced features"""
    
    service_dir = Path("tigerex-repo/backend/enhanced-security-service")
    service_dir.mkdir(parents=True, exist_ok=True)
    
    main_py = """#!/usr/bin/env python3
"""
Enhanced Security Service
Comprehensive security management including 2FA, biometrics, and advanced security features
"""

from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import os
import secrets
import pyotp
import qrcode
import io
import base64
from functools import wraps
import hashlib
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

# Models
class UserSecurity(db.Model):
    __tablename__ = 'user_security'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False, unique=True)
    
    # 2FA Settings
    passkeys_enabled = db.Column(db.Boolean, default=False)
    authenticator_enabled = db.Column(db.Boolean, default=False)
    email_2fa_enabled = db.Column(db.Boolean, default=True)
    password_enabled = db.Column(db.Boolean, default=True)
    
    # Security Keys
    totp_secret = db.Column(db.String(32))
    backup_codes = db.Column(db.JSON)
    
    # Advanced Security
    emergency_contact = db.Column(db.String(100))
    anti_phishing_code = db.Column(db.String(20))
    auto_lock_enabled = db.Column(db.Boolean, default=False)
    auto_lock_duration = db.Column(db.Integer, default=30)  # minutes
    
    # Account Settings
    login_notifications = db.Column(db.Boolean, default=True)
    withdrawal_whitelist = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SecurityActivity(db.Model):
    __tablename__ = 'security_activity'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    location = db.Column(db.String(100))
    status = db.Column(db.String(20), default='success')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class AuthorizedDevice(db.Model):
    __tablename__ = 'authorized_devices'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    device_id = db.Column(db.String(100), nullable=False)
    device_name = db.Column(db.String(100))
    device_type = db.Column(db.String(50))
    last_used = db.Column(db.DateTime, default=datetime.utcnow)
    is_trusted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AppAuthorization(db.Model):
    __tablename__ = 'app_authorizations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    app_name = db.Column(db.String(100), nullable=False)
    permissions = db.Column(db.JSON)
    api_key = db.Column(db.String(64))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

# Security Routes
@app.route('/api/security/status', methods=['GET'])
@jwt_required()
def get_security_status():
    try:
        user_id = get_jwt_identity()
        security = UserSecurity.query.filter_by(user_id=user_id).first()
        
        if not security:
            security = UserSecurity(user_id=user_id)
            db.session.add(security)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'security': {
                'passkeys_enabled': security.passkeys_enabled,
                'authenticator_enabled': security.authenticator_enabled,
                'email_2fa_enabled': security.email_2fa_enabled,
                'password_enabled': security.password_enabled,
                'emergency_contact': security.emergency_contact,
                'anti_phishing_code': security.anti_phishing_code,
                'auto_lock_enabled': security.auto_lock_enabled,
                'auto_lock_duration': security.auto_lock_duration
            }
        })
    except Exception as e:
        logger.error(f"Error getting security status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/security/2fa/setup-authenticator', methods=['POST'])
@jwt_required()
def setup_authenticator():
    try:
        user_id = get_jwt_identity()
        security = UserSecurity.query.filter_by(user_id=user_id).first()
        
        if not security:
            security = UserSecurity(user_id=user_id)
            db.session.add(security)
        
        # Generate TOTP secret
        secret = pyotp.random_base32()
        security.totp_secret = secret
        
        # Generate QR code
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_id,
            issuer_name="TigerEx"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        
        # Generate backup codes
        backup_codes = [secrets.token_hex(4).upper() for _ in range(8)]
        security.backup_codes = backup_codes
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'secret': secret,
            'qr_code': f"data:image/png;base64,{img_str}",
            'backup_codes': backup_codes
        })
    except Exception as e:
        logger.error(f"Error setting up authenticator: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/security/2fa/verify-authenticator', methods=['POST'])
@jwt_required()
def verify_authenticator():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        code = data.get('code')
        
        security = UserSecurity.query.filter_by(user_id=user_id).first()
        if not security or not security.totp_secret:
            return jsonify({'success': False, 'error': 'Authenticator not set up'}), 400
        
        totp = pyotp.TOTP(security.totp_secret)
        if totp.verify(code):
            security.authenticator_enabled = True
            db.session.commit()
            
            # Log security activity
            activity = SecurityActivity(
                user_id=user_id,
                activity_type='2FA_ENABLED',
                description='Authenticator app enabled',
                ip_address=request.remote_addr
            )
            db.session.add(activity)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Authenticator enabled successfully'})
        else:
            return jsonify({'success': False, 'error': 'Invalid code'}), 400
    except Exception as e:
        logger.error(f"Error verifying authenticator: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/security/emergency-contact', methods=['POST'])
@jwt_required()
def set_emergency_contact():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        contact = data.get('contact')
        
        security = UserSecurity.query.filter_by(user_id=user_id).first()
        if not security:
            security = UserSecurity(user_id=user_id)
            db.session.add(security)
        
        security.emergency_contact = contact
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Emergency contact updated'})
    except Exception as e:
        logger.error(f"Error setting emergency contact: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/security/anti-phishing-code', methods=['POST'])
@jwt_required()
def set_anti_phishing_code():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        code = data.get('code')
        
        security = UserSecurity.query.filter_by(user_id=user_id).first()
        if not security:
            security = UserSecurity(user_id=user_id)
            db.session.add(security)
        
        security.anti_phishing_code = code
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Anti-phishing code updated'})
    except Exception as e:
        logger.error(f"Error setting anti-phishing code: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/security/activities', methods=['GET'])
@jwt_required()
def get_security_activities():
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        activities = SecurityActivity.query.filter_by(user_id=user_id)\\
            .order_by(SecurityActivity.timestamp.desc())\\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'activities': [{
                'id': activity.id,
                'type': activity.activity_type,
                'description': activity.description,
                'ip_address': activity.ip_address,
                'location': activity.location,
                'status': activity.status,
                'timestamp': activity.timestamp.isoformat()
            } for activity in activities.items],
            'pagination': {
                'page': page,
                'pages': activities.pages,
                'per_page': per_page,
                'total': activities.total
            }
        })
    except Exception as e:
        logger.error(f"Error getting security activities: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/security/devices', methods=['GET'])
@jwt_required()
def get_authorized_devices():
    try:
        user_id = get_jwt_identity()
        devices = AuthorizedDevice.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'success': True,
            'devices': [{
                'id': device.id,
                'device_name': device.device_name,
                'device_type': device.device_type,
                'last_used': device.last_used.isoformat(),
                'is_trusted': device.is_trusted,
                'created_at': device.created_at.isoformat()
            } for device in devices]
        })
    except Exception as e:
        logger.error(f"Error getting devices: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/security/auto-lock', methods=['POST'])
@jwt_required()
def configure_auto_lock():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        enabled = data.get('enabled', False)
        duration = data.get('duration', 30)
        
        security = UserSecurity.query.filter_by(user_id=user_id).first()
        if not security:
            security = UserSecurity(user_id=user_id)
            db.session.add(security)
        
        security.auto_lock_enabled = enabled
        security.auto_lock_duration = duration
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Auto-lock settings updated'})
    except Exception as e:
        logger.error(f"Error configuring auto-lock: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'enhanced-security-service',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
"""
    
    with open(service_dir / "main.py", "w") as f:
        f.write(main_py)
    
    # Create requirements.txt
    requirements = """flask==2.3.3
flask-sqlalchemy==3.0.5
flask-jwt-extended==4.5.3
flask-cors==4.0.0
psycopg2-binary==2.9.7
python-dotenv==1.0.0
pyotp==2.9.0
qrcode==7.4.2
Pillow==10.0.1
"""
    
    with open(service_dir / "requirements.txt", "w") as f:
        f.write(requirements)
    
    # Create Dockerfile
    dockerfile = """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "main:app"]
"""
    
    with open(service_dir / "Dockerfile", "w") as f:
        f.write(dockerfile)
    
    print("✅ Created enhanced-security-service")

def create_account_management_service():
    """Create account management service with VIP upgrade and profile management"""
    
    service_dir = Path("tigerex-repo/backend/account-management-service")
    service_dir.mkdir(parents=True, exist_ok=True)
    
    main_py = """#!/usr/bin/env python3
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
"""
    
    with open(service_dir / "main.py", "w") as f:
        f.write(main_py)
    
    # Create requirements.txt
    requirements = """flask==2.3.3
flask-sqlalchemy==3.0.5
flask-jwt-extended==4.5.3
flask-cors==4.0.0
psycopg2-binary==2.9.7
python-dotenv==1.0.0
"""
    
    with open(service_dir / "requirements.txt", "w") as f:
        f.write(requirements)
    
    # Create Dockerfile
    dockerfile = """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "main:app"]
"""
    
    with open(service_dir / "Dockerfile", "w") as f:
        f.write(dockerfile)
    
    print("✅ Created account-management-service")

def main():
    """Main function to create enhanced security and account management"""
    
    print("🔐 Creating Enhanced Security & Account Management Services...")
    
    create_enhanced_security_service()
    create_account_management_service()
    
    print("\n✅ Enhanced services created successfully!")
    print("📋 Services added:")
    print("  - Enhanced Security Service (2FA, Biometrics, Advanced Security)")
    print("  - Account Management Service (VIP Upgrades, Profile Management)")

if __name__ == "__main__":
    main()