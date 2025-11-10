#!/usr/bin/env python3
"""
Multi-Tenant Service for TigerEx v11.0.0
Complete multi-tenant architecture with tenant isolation and management
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import os
import uuid
import hashlib
import json
from sqlalchemy import event
from sqlalchemy.schema import CreateTable

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
class Tenant(db.Model):
    __tablename__ = 'tenants'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(64), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    subdomain = db.Column(db.String(50), nullable=False, unique=True)
    
    # Tenant configuration
    domain = db.Column(db.String(100))
    logo_url = db.Column(db.String(255))
    primary_color = db.Column(db.String(7), default='#3B82F6')
    secondary_color = db.Column(db.String(7), default='#10B981')
    
    # Business info
    company_name = db.Column(db.String(200))
    industry = db.Column(db.String(50))
    size = db.Column(db.String(20))  # small, medium, large, enterprise
    
    # Tenant settings
    max_users = db.Column(db.Integer, default=100)
    max_api_calls = db.Column(db.Integer, default=10000)
    features_enabled = db.Column(db.JSON)
    
    # Billing
    plan_type = db.Column(db.String(20), default='basic')  # basic, pro, enterprise
    billing_cycle = db.Column(db.String(10), default='monthly')
    trial_expires = db.Column(db.DateTime)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_suspended = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TenantUser(db.Model):
    __tablename__ = 'tenant_users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    tenant_id = db.Column(db.String(64), db.ForeignKey('tenants.tenant_id'), nullable=False)
    
    # User info
    email = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    
    # Role and permissions
    role = db.Column(db.String(20), default='user')  # owner, admin, manager, user
    permissions = db.Column(db.JSON)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Login info
    last_login = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    tenant = db.relationship('Tenant', backref=db.backref('users', lazy=True))

class TenantConfiguration(db.Model):
    __tablename__ = 'tenant_configurations'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(64), db.ForeignKey('tenants.tenant_id'), nullable=False)
    
    # Trading settings
    trading_enabled = db.Column(db.Boolean, default=True)
    allowed_pairs = db.Column(db.JSON)
    max_trade_size = db.Column(db.Numeric(20, 8), default=10000)
    leverage_limit = db.Column(db.Integer, default=10)
    
    # Security settings
    two_factor_required = db.Column(db.Boolean, default=False)
    ip_whitelist = db.Column(db.JSON)
    api_key_required = db.Column(db.Boolean, default=False)
    
    # Notification settings
    email_notifications = db.Column(db.Boolean, default=True)
    sms_notifications = db.Column(db.Boolean, default=False)
    push_notifications = db.Column(db.Boolean, default=True)
    
    # API settings
    api_rate_limit = db.Column(db.Integer, default=1000)  # requests per hour
    webhook_enabled = db.Column(db.Boolean, default=False)
    webhook_url = db.Column(db.String(255))
    
    # Compliance settings
    kyc_required = db.Column(db.Boolean, default=True)
    aml_monitoring = db.Column(db.Boolean, default=True)
    compliance_level = db.Column(db.String(20), default='standard')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    tenant = db.relationship('Tenant', backref=db.backref('configuration', uselist=False))

class TenantUsage(db.Model):
    __tablename__ = 'tenant_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(64), db.ForeignKey('tenants.tenant_id'), nullable=False)
    
    # Usage metrics
    date = db.Column(db.Date, nullable=False)
    active_users = db.Column(db.Integer, default=0)
    api_calls = db.Column(db.Integer, default=0)
    trades_executed = db.Column(db.Integer, default=0)
    data_storage_mb = db.Column(db.Float, default=0)
    bandwidth_gb = db.Column(db.Float, default=0)
    
    # Financial metrics
    trade_volume = db.Column(db.Numeric(20, 8), default=0)
    revenue_generated = db.Column(db.Numeric(20, 8), default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    tenant = db.relationship('Tenant', backref=db.backref('usage', lazy=True))

class TenantAPIKey(db.Model):
    __tablename__ = 'tenant_api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    key_id = db.Column(db.String(64), nullable=False, unique=True)
    tenant_id = db.Column(db.String(64), db.ForeignKey('tenants.tenant_id'), nullable=False)
    
    # Key details
    name = db.Column(db.String(100), nullable=False)
    key_hash = db.Column(db.String(255), nullable=False)
    permissions = db.Column(db.JSON)
    
    # Usage tracking
    last_used = db.Column(db.DateTime)
    usage_count = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    tenant = db.relationship('Tenant', backref=db.backref('api_keys', lazy=True))

class MultiTenantManager:
    def __init__(self):
        self.default_features = [
            'spot_trading',
            'basic_analytics',
            'user_management',
            'api_access'
        ]
    
    def create_tenant(self, tenant_data):
        """Create a new tenant with default configuration"""
        try:
            tenant = Tenant(
                tenant_id=str(uuid.uuid4()),
                name=tenant_data.get('name'),
                subdomain=tenant_data.get('subdomain'),
                domain=tenant_data.get('domain'),
                company_name=tenant_data.get('company_name'),
                industry=tenant_data.get('industry'),
                size=tenant_data.get('size', 'small'),
                plan_type=tenant_data.get('plan_type', 'basic'),
                features_enabled=self.get_features_for_plan(tenant_data.get('plan_type', 'basic')),
                trial_expires=datetime.utcnow() + timedelta(days=14)
            )
            
            db.session.add(tenant)
            db.session.flush()
            
            # Create default configuration
            config = TenantConfiguration(
                tenant_id=tenant.tenant_id,
                trading_enabled=True,
                allowed_pairs=['BTC/USDT', 'ETH/USDT'],
                two_factor_required=tenant_data.get('plan_type') == 'enterprise',
                kyc_required=True,
                aml_monitoring=True
            )
            
            db.session.add(config)
            db.session.commit()
            
            return tenant
        except Exception as e:
            db.session.rollback()
            raise e
    
    def get_features_for_plan(self, plan_type):
        """Get features based on plan type"""
        feature_mapping = {
            'basic': [
                'spot_trading',
                'basic_analytics',
                'user_management',
                'api_access'
            ],
            'pro': [
                'spot_trading',
                'futures_trading',
                'advanced_analytics',
                'user_management',
                'api_access',
                'white_label',
                'custom_branding'
            ],
            'enterprise': [
                'spot_trading',
                'futures_trading',
                'options_trading',
                'advanced_analytics',
                'ai_insights',
                'user_management',
                'api_access',
                'white_label',
                'custom_branding',
                'dedicated_support',
                'custom_integrations',
                'advanced_compliance'
            ]
        }
        return feature_mapping.get(plan_type, self.default_features)
    
    def add_user_to_tenant(self, tenant_id, user_data):
        """Add a user to a tenant"""
        try:
            # Check tenant limits
            tenant = Tenant.query.filter_by(tenant_id=tenant_id).first()
            if not tenant:
                raise Exception("Tenant not found")
            
            current_users = TenantUser.query.filter_by(tenant_id=tenant_id, is_active=True).count()
            if current_users >= tenant.max_users:
                raise Exception("Tenant user limit exceeded")
            
            user = TenantUser(
                user_id=user_data.get('user_id'),
                tenant_id=tenant_id,
                email=user_data.get('email'),
                username=user_data.get('username'),
                first_name=user_data.get('first_name'),
                last_name=user_data.get('last_name'),
                role=user_data.get('role', 'user'),
                permissions=user_data.get('permissions', [])
            )
            
            db.session.add(user)
            db.session.commit()
            
            return user
        except Exception as e:
            db.session.rollback()
            raise e
    
    def generate_api_key(self, tenant_id, key_data):
        """Generate API key for tenant"""
        try:
            # Check tenant limits
            current_keys = TenantAPIKey.query.filter_by(tenant_id=tenant_id, is_active=True).count()
            tenant = Tenant.query.filter_by(tenant_id=tenant_id).first()
            
            if current_keys >= 10:  # Max 10 API keys per tenant
                raise Exception("API key limit exceeded")
            
            # Generate actual API key
            api_key = f"tk_{uuid.uuid4().hex}_{uuid.uuid4().hex}"
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            api_key_obj = TenantAPIKey(
                key_id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                name=key_data.get('name'),
                key_hash=key_hash,
                permissions=key_data.get('permissions', ['read']),
                expires_at=datetime.utcnow() + timedelta(days=365)
            )
            
            db.session.add(api_key_obj)
            db.session.commit()
            
            return {
                'api_key': api_key,
                'key_id': api_key_obj.key_id
            }
        except Exception as e:
            db.session.rollback()
            raise e
    
    def track_usage(self, tenant_id, usage_data):
        """Track tenant usage"""
        try:
            today = datetime.utcnow().date()
            
            # Get or create usage record for today
            usage = TenantUsage.query.filter_by(tenant_id=tenant_id, date=today).first()
            
            if not usage:
                usage = TenantUsage(
                    tenant_id=tenant_id,
                    date=today
                )
                db.session.add(usage)
            
            # Update usage metrics
            if 'api_calls' in usage_data:
                usage.api_calls += usage_data['api_calls']
            if 'trades_executed' in usage_data:
                usage.trades_executed += usage_data['trades_executed']
            if 'trade_volume' in usage_data:
                usage.trade_volume += usage_data['trade_volume']
            if 'active_users' in usage_data:
                usage.active_users = usage_data['active_users']
            
            usage.created_at = datetime.utcnow()
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def check_permissions(self, user_id, tenant_id, required_permission):
        """Check if user has required permission in tenant"""
        user = TenantUser.query.filter_by(user_id=user_id, tenant_id=tenant_id, is_active=True).first()
        
        if not user:
            return False
        
        # Owner has all permissions
        if user.role == 'owner':
            return True
        
        # Check specific permission
        permissions = user.permissions or []
        return required_permission in permissions
    
    def validate_tenant_limits(self, tenant_id, limit_type):
        """Validate if tenant is within limits"""
        tenant = Tenant.query.filter_by(tenant_id=tenant_id, is_active=True, is_suspended=False).first()
        
        if not tenant:
            return False, "Tenant not found or suspended"
        
        today = datetime.utcnow().date()
        usage = TenantUsage.query.filter_by(tenant_id=tenant_id, date=today).first()
        
        if not usage:
            return True, "No usage data available"
        
        if limit_type == 'api_calls' and usage.api_calls >= tenant.max_api_calls:
            return False, "API call limit exceeded"
        
        if limit_type == 'users':
            current_users = TenantUser.query.filter_by(tenant_id=tenant_id, is_active=True).count()
            if current_users >= tenant.max_users:
                return False, "User limit exceeded"
        
        return True, "Within limits"

# Initialize tenant manager
tenant_manager = MultiTenantManager()

# API Routes
@app.route('/api/tenant/create', methods=['POST'])
@jwt_required()
def create_tenant():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'subdomain', 'company_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        # Check if subdomain is available
        existing_tenant = Tenant.query.filter_by(subdomain=data['subdomain']).first()
        if existing_tenant:
            return jsonify({'success': False, 'error': 'Subdomain already taken'}), 400
        
        # Create tenant
        tenant = tenant_manager.create_tenant(data)
        
        # Add creating user as owner
        user_data = {
            'user_id': user_id,
            'email': data.get('email'),
            'username': data.get('username'),
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'role': 'owner'
        }
        
        tenant_manager.add_user_to_tenant(tenant.tenant_id, user_data)
        
        return jsonify({
            'success': True,
            'tenant': {
                'tenant_id': tenant.tenant_id,
                'name': tenant.name,
                'subdomain': tenant.subdomain,
                'domain': tenant.domain,
                'plan_type': tenant.plan_type,
                'trial_expires': tenant.trial_expires.isoformat() if tenant.trial_expires else None
            }
        })
    except Exception as e:
        logger.error(f"Error creating tenant: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tenants', methods=['GET'])
@jwt_required()
def get_user_tenants():
    try:
        user_id = get_jwt_identity()
        
        tenant_users = TenantUser.query.filter_by(user_id=user_id, is_active=True).all()
        tenants = []
        
        for tu in tenant_users:
            tenant = Tenant.query.filter_by(tenant_id=tu.tenant_id, is_active=True).first()
            if tenant:
                tenants.append({
                    'tenant_id': tenant.tenant_id,
                    'name': tenant.name,
                    'subdomain': tenant.subdomain,
                    'domain': tenant.domain,
                    'company_name': tenant.company_name,
                    'role': tu.role,
                    'created_at': tenant.created_at.isoformat()
                })
        
        return jsonify({
            'success': True,
            'tenants': tenants
        })
    except Exception as e:
        logger.error(f"Error getting user tenants: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tenant/<tenant_id>/users', methods=['GET'])
@jwt_required()
def get_tenant_users(tenant_id):
    try:
        user_id = get_jwt_identity()
        
        # Check permissions
        if not tenant_manager.check_permissions(user_id, tenant_id, 'user_management'):
            return jsonify({'success': False, 'error': 'Insufficient permissions'}), 403
        
        users = TenantUser.query.filter_by(tenant_id=tenant_id).all()
        
        return jsonify({
            'success': True,
            'users': [
                {
                    'user_id': user.user_id,
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'is_active': user.is_active,
                    'created_at': user.created_at.isoformat()
                }
                for user in users
            ]
        })
    except Exception as e:
        logger.error(f"Error getting tenant users: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tenant/<tenant_id>/configuration', methods=['GET'])
@jwt_required()
def get_tenant_configuration(tenant_id):
    try:
        user_id = get_jwt_identity()
        
        # Check if user belongs to tenant
        user = TenantUser.query.filter_by(user_id=user_id, tenant_id=tenant_id, is_active=True).first()
        if not user:
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        
        tenant = Tenant.query.filter_by(tenant_id=tenant_id).first()
        config = TenantConfiguration.query.filter_by(tenant_id=tenant_id).first()
        
        return jsonify({
            'success': True,
            'tenant': {
                'tenant_id': tenant.tenant_id,
                'name': tenant.name,
                'subdomain': tenant.subdomain,
                'domain': tenant.domain,
                'company_name': tenant.company_name,
                'logo_url': tenant.logo_url,
                'primary_color': tenant.primary_color,
                'secondary_color': tenant.secondary_color,
                'plan_type': tenant.plan_type,
                'features_enabled': tenant.features_enabled,
                'is_active': tenant.is_active
            },
            'configuration': {
                'trading_enabled': config.trading_enabled,
                'allowed_pairs': config.allowed_pairs,
                'max_trade_size': float(config.max_trade_size),
                'leverage_limit': config.leverage_limit,
                'two_factor_required': config.two_factor_required,
                'api_rate_limit': config.api_rate_limit,
                'kyc_required': config.kyc_required,
                'aml_monitoring': config.aml_monitoring
            }
        })
    except Exception as e:
        logger.error(f"Error getting tenant configuration: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tenant/<tenant_id>/api-keys', methods=['POST'])
@jwt_required()
def generate_api_key(tenant_id):
    try:
        user_id = get_jwt_identity()
        
        # Check permissions
        if not tenant_manager.check_permissions(user_id, tenant_id, 'api_management'):
            return jsonify({'success': False, 'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        
        api_key_data = tenant_manager.generate_api_key(tenant_id, {
            'name': data.get('name'),
            'permissions': data.get('permissions', ['read'])
        })
        
        return jsonify({
            'success': True,
            'api_key': api_key_data
        })
    except Exception as e:
        logger.error(f"Error generating API key: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tenant/<tenant_id>/usage', methods=['GET'])
@jwt_required()
def get_tenant_usage(tenant_id):
    try:
        user_id = get_jwt_identity()
        
        # Check permissions
        if not tenant_manager.check_permissions(user_id, tenant_id, 'analytics'):
            return jsonify({'success': False, 'error': 'Insufficient permissions'}), 403
        
        days = request.args.get('days', 30, type=int)
        
        usage_records = TenantUsage.query.filter_by(tenant_id=tenant_id).order_by(
            TenantUsage.date.desc()).limit(days).all()
        
        return jsonify({
            'success': True,
            'usage': [
                {
                    'date': usage.date.isoformat(),
                    'active_users': usage.active_users,
                    'api_calls': usage.api_calls,
                    'trades_executed': usage.trades_executed,
                    'trade_volume': float(usage.trade_volume),
                    'data_storage_mb': usage.data_storage_mb,
                    'bandwidth_gb': usage.bandwidth_gb
                }
                for usage in usage_records
            ]
        })
    except Exception as e:
        logger.error(f"Error getting tenant usage: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tenant/validate/<tenant_id>', methods=['POST'])
def validate_tenant_access(tenant_id):
    """Middleware endpoint to validate tenant access"""
    try:
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'success': False, 'error': 'API key required'}), 401
        
        # Find API key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        api_key_obj = TenantAPIKey.query.filter_by(key_hash=key_hash, is_active=True).first()
        
        if not api_key_obj:
            return jsonify({'success': False, 'error': 'Invalid API key'}), 401
        
        # Check if key is expired
        if api_key_obj.expires_at and api_key_obj.expires_at < datetime.utcnow():
            return jsonify({'success': False, 'error': 'API key expired'}), 401
        
        # Check tenant limits
        valid, message = tenant_manager.validate_tenant_limits(tenant_id, 'api_calls')
        if not valid:
            return jsonify({'success': False, 'error': message}), 429
        
        # Update usage
        tenant_manager.track_usage(tenant_id, {'api_calls': 1})
        api_key_obj.usage_count += 1
        api_key_obj.last_used = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'tenant_id': tenant_id,
            'permissions': api_key_obj.permissions
        })
    except Exception as e:
        logger.error(f"Error validating tenant access: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        logger.info("Multi-Tenant Service started successfully")
    app.run(host='0.0.0.0', port=5006, debug=True)