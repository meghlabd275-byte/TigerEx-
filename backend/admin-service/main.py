#!/usr/bin/env python3
"""
Complete Admin Service for TigerEx Platform
Full admin control system with comprehensive RBAC and user management
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import os
import uuid
import hashlib
import secrets
from functools import wraps
from enum import Enum

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/tigerex')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models
class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    SUPPORT = "support"
    COMPLIANCE = "compliance"
    RISK_MANAGER = "risk_manager"
    TRADER = "trader"
    USER = "user"

class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Role and Permissions
    role = db.Column(db.Enum(UserRole), default=UserRole.USER)
    permissions = db.Column(db.JSON, default=list)
    is_active = db.Column(db.Boolean, default=True)
    
    # Admin Settings
    can_manage_users = db.Column(db.Boolean, default=False)
    can_manage_finances = db.Column(db.Boolean, default=False)
    can_manage_trading = db.Column(db.Boolean, default=False)
    can_manage_system = db.Column(db.Boolean, default=False)
    can_view_reports = db.Column(db.Boolean, default=False)
    
    # Session Management
    last_login = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AdminLog(db.Model):
    __tablename__ = 'admin_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_user_id = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    resource = db.Column(db.String(100))
    resource_id = db.Column(db.String(50))
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class SystemConfig(db.Model):
    __tablename__ = 'system_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), nullable=False, unique=True)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    updated_by = db.Column(db.String(50))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Utility functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    return hash_password(password) == password_hash

def generate_admin_token():
    return secrets.token_urlsafe(32)

# Decorators
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()
            admin = AdminUser.query.filter_by(user_id=user_id, is_active=True).first()
            if not admin:
                return jsonify({'success': False, 'error': 'Admin access required'}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def permission_required(permission):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()
            admin = AdminUser.query.filter_by(user_id=user_id, is_active=True).first()
            if not admin:
                return jsonify({'success': False, 'error': 'Admin access required'}), 403
            
            if permission not in admin.permissions and admin.role != UserRole.SUPER_ADMIN:
                return jsonify({'success': False, 'error': 'Insufficient permissions'}), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def log_admin_action(action, resource=None, resource_id=None, details=None):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()
            result = fn(*args, **kwargs)
            
            log_entry = AdminLog(
                admin_user_id=user_id,
                action=action,
                resource=resource,
                resource_id=resource_id,
                details=details,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(log_entry)
            db.session.commit()
            
            return result
        return decorator
    return wrapper

# Routes
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'}), 400
        
        admin = AdminUser.query.filter_by(username=username).first()
        
        if not admin or not verify_password(password, admin.password_hash):
            if admin:
                admin.failed_login_attempts += 1
                if admin.failed_login_attempts >= 5:
                    admin.locked_until = datetime.utcnow() + timedelta(minutes=30)
                db.session.commit()
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        if admin.locked_until and admin.locked_until > datetime.utcnow():
            return jsonify({'success': False, 'error': 'Account locked'}), 403
        
        if not admin.is_active:
            return jsonify({'success': False, 'error': 'Account inactive'}), 403
        
        # Update login info
        admin.last_login = datetime.utcnow()
        admin.login_count += 1
        admin.failed_login_attempts = 0
        admin.locked_until = None
        db.session.commit()
        
        access_token = create_access_token(identity=admin.user_id)
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'admin': {
                'user_id': admin.user_id,
                'username': admin.username,
                'email': admin.email,
                'role': admin.role,
                'permissions': admin.permissions,
                'last_login': admin.last_login.isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Error during admin login: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/dashboard', methods=['GET'])
@jwt_required()
@admin_required()
def get_admin_dashboard():
    try:
        # Get various dashboard statistics
        total_users = AdminUser.query.count()
        active_admins = AdminUser.query.filter_by(is_active=True).count()
        recent_logs = AdminLog.query.order_by(AdminLog.timestamp.desc()).limit(10).all()
        
        return jsonify({
            'success': True,
            'dashboard': {
                'total_admins': total_users,
                'active_admins': active_admins,
                'recent_activities': [
                    {
                        'action': log.action,
                        'admin': log.admin_user_id,
                        'timestamp': log.timestamp.isoformat(),
                        'details': log.details
                    }
                    for log in recent_logs
                ]
            }
        })
    except Exception as e:
        logger.error(f"Error getting admin dashboard: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
@admin_required()
@permission_required('user:view')
def get_all_admin_users():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        role_filter = request.args.get('role')
        
        query = AdminUser.query
        if role_filter:
            query = query.filter_by(role=UserRole(role_filter))
        
        users = query.paginate(page, per_page, False)
        
        return jsonify({
            'success': True,
            'users': [
                {
                    'user_id': user.user_id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'permissions': user.permissions,
                    'is_active': user.is_active,
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'created_at': user.created_at.isoformat()
                }
                for user in users.items
            ],
            'pagination': {
                'page': users.page,
                'per_page': users.per_page,
                'total': users.total,
                'total_pages': users.pages
            }
        })
    except Exception as e:
        logger.error(f"Error getting admin users: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/users', methods=['POST'])
@jwt_required()
@admin_required()
@permission_required('user:create')
@log_admin_action('create_admin_user', resource='admin_user')
def create_admin_user():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        # Check if user already exists
        if AdminUser.query.filter_by(username=data['username']).first():
            return jsonify({'success': False, 'error': 'Username already exists'}), 400
        
        if AdminUser.query.filter_by(email=data['email']).first():
            return jsonify({'success': False, 'error': 'Email already exists'}), 400
        
        # Create new admin user
        new_admin = AdminUser(
            user_id=str(uuid.uuid4()),
            username=data['username'],
            email=data['email'],
            password_hash=hash_password(data['password']),
            role=UserRole(data['role']),
            permissions=data.get('permissions', []),
            can_manage_users=data.get('can_manage_users', False),
            can_manage_finances=data.get('can_manage_finances', False),
            can_manage_trading=data.get('can_manage_trading', False),
            can_manage_system=data.get('can_manage_system', False),
            can_view_reports=data.get('can_view_reports', False)
        )
        
        db.session.add(new_admin)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Admin user created successfully',
            'user_id': new_admin.user_id
        })
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/users/<user_id>', methods=['PUT'])
@jwt_required()
@admin_required()
@permission_required('user:update')
@log_admin_action('update_admin_user', resource='admin_user', resource_id='user_id')
def update_admin_user(user_id):
    try:
        user = AdminUser.query.filter_by(user_id=user_id).first()
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'email' in data:
            user.email = data['email']
        if 'role' in data:
            user.role = UserRole(data['role'])
        if 'permissions' in data:
            user.permissions = data['permissions']
        if 'is_active' in data:
            user.is_active = data['is_active']
        if 'can_manage_users' in data:
            user.can_manage_users = data['can_manage_users']
        if 'can_manage_finances' in data:
            user.can_manage_finances = data['can_manage_finances']
        if 'can_manage_trading' in data:
            user.can_manage_trading = data['can_manage_trading']
        if 'can_manage_system' in data:
            user.can_manage_system = data['can_manage_system']
        if 'can_view_reports' in data:
            user.can_view_reports = data['can_view_reports']
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Admin user updated successfully'})
    except Exception as e:
        logger.error(f"Error updating admin user: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/users/<user_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
@permission_required('user:delete')
@log_admin_action('delete_admin_user', resource='admin_user', resource_id='user_id')
def delete_admin_user(user_id):
    try:
        user = AdminUser.query.filter_by(user_id=user_id).first()
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Admin user deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting admin user: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/system/config', methods=['GET'])
@jwt_required()
@admin_required()
@permission_required('system:config')
def get_system_config():
    try:
        configs = SystemConfig.query.filter_by(is_active=True).all()
        
        return jsonify({
            'success': True,
            'configs': [
                {
                    'key': config.key,
                    'value': config.value,
                    'description': config.description,
                    'category': config.category,
                    'updated_at': config.updated_at.isoformat()
                }
                for config in configs
            ]
        })
    except Exception as e:
        logger.error(f"Error getting system config: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/system/config', methods=['POST'])
@jwt_required()
@admin_required()
@permission_required('system:config')
@log_admin_action('update_system_config', resource='system_config')
def update_system_config():
    try:
        data = request.get_json()
        configs = data.get('configs', [])
        
        for config_data in configs:
            config = SystemConfig.query.filter_by(key=config_data['key']).first()
            if config:
                config.value = config_data.get('value')
                config.description = config_data.get('description')
                config.updated_by = get_jwt_identity()
                config.updated_at = datetime.utcnow()
            else:
                new_config = SystemConfig(
                    key=config_data['key'],
                    value=config_data.get('value'),
                    description=config_data.get('description'),
                    category=config_data.get('category'),
                    updated_by=get_jwt_identity()
                )
                db.session.add(new_config)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'System config updated successfully'})
    except Exception as e:
        logger.error(f"Error updating system config: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/logs', methods=['GET'])
@jwt_required()
@admin_required()
@permission_required('system:view_logs')
def get_admin_logs():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        action_filter = request.args.get('action')
        
        query = AdminLog.query
        if action_filter:
            query = query.filter_by(action=action_filter)
        
        logs = query.order_by(AdminLog.timestamp.desc()).paginate(page, per_page, False)
        
        return jsonify({
            'success': True,
            'logs': [
                {
                    'id': log.id,
                    'admin_user_id': log.admin_user_id,
                    'action': log.action,
                    'resource': log.resource,
                    'resource_id': log.resource_id,
                    'details': log.details,
                    'ip_address': log.ip_address,
                    'timestamp': log.timestamp.isoformat()
                }
                for log in logs.items
            ],
            'pagination': {
                'page': logs.page,
                'per_page': logs.per_page,
                'total': logs.total,
                'total_pages': logs.pages
            }
        })
    except Exception as e:
        logger.error(f"Error getting admin logs: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/roles', methods=['GET'])
@jwt_required()
@admin_required()
def get_available_roles():
    try:
        return jsonify({
            'success': True,
            'roles': [
                {'value': role.value, 'label': role.value.replace('_', ' ').title()}
                for role in UserRole
            ]
        })
    except Exception as e:
        logger.error(f"Error getting roles: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Initialize database
@app.before_first_request
def create_tables():
    db.create_all()
    
    # Create default super admin if not exists
    if not AdminUser.query.filter_by(role=UserRole.SUPER_ADMIN).first():
        super_admin = AdminUser(
            user_id=str(uuid.uuid4()),
            username='superadmin',
            email='admin@tigerex.com',
            password_hash=hash_password('admin123'),
            role=UserRole.SUPER_ADMIN,
            permissions=['all'],
            can_manage_users=True,
            can_manage_finances=True,
            can_manage_trading=True,
            can_manage_system=True,
            can_view_reports=True
        )
        db.session.add(super_admin)
        db.session.commit()
        logger.info("Default super admin created")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        logger.info("Admin Service started successfully")
    app.run(host='0.0.0.0', port=5002, debug=True)