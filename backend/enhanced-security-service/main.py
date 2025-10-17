/*
 * TigerEx Exchange Platform
 * Version: 7.0.0 - Consolidated Production Release
 * 
 * Complete cryptocurrency exchange platform with:
 * - CEX/DEX hybrid functionality
 * - 105+ exchange features
 * - Multi-platform support (Web, Mobile, Desktop)
 * - Enterprise-grade security
 * - White-label deployment ready
 * 
 * Production-ready implementation
 */

#!/usr/bin/env python3
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
        
        activities = SecurityActivity.query.filter_by(user_id=user_id)\
            .order_by(SecurityActivity.timestamp.desc())\
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
