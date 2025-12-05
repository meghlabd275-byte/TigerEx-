#!/usr/bin/env python3
"""
Tiger Admin Service - Comprehensive Admin Control System
Consolidates functionality from 30+ admin services
Features complete control over all TigerEx services
"""

from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import os
import json
import uuid
from decimal import Decimal
from functools import wraps
from enum import Enum

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

class UserRole(Enum):
    SUPER_ADMIN = "super_admin"
    EXCHANGE_ADMIN = "exchange_admin"
    SUPPORT_ADMIN = "support_admin"
    COMPLIANCE_ADMIN = "compliance_admin"
    TRADING_ADMIN = "trading_admin"
    FINANCIAL_ADMIN = "financial_admin"
    SYSTEM_ADMIN = "system_admin"

class Permission(Enum):
    USER_MANAGEMENT = "user_management"
    TRADING_CONTROL = "trading_control"
    FINANCIAL_OPERATIONS = "financial_operations"
    SYSTEM_CONFIGURATION = "system_configuration"
    COMPLIANCE_MANAGEMENT = "compliance_management"
    SUPPORT_OPERATIONS = "support_operations"
    EXCHANGE_INTEGRATION = "exchange_integration"
    ANALYTICS_ACCESS = "analytics_access"
    EMERGENCY_CONTROLS = "emergency_controls"

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.SUPPORT_ADMIN)
    is_active = db.Column(db.Boolean, default=True)
    permissions = db.Column(db.JSON, default=list)
    kyc_status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

class AdminAction(db.Model):
    __tablename__ = 'admin_actions'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action_type = db.Column(db.String(100), nullable=False)
    action_details = db.Column(db.JSON, nullable=False)
    target_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    target_service = db.Column(db.String(100))
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    status = db.Column(db.String(20), default='completed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SystemConfig(db.Model):
    __tablename__ = 'system_configs'
    id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(100), unique=True, nullable=False)
    config_value = db.Column(db.JSON, nullable=False)
    config_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    is_sensitive = db.Column(db.Boolean, default=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ExchangeIntegration(db.Model):
    __tablename__ = 'exchange_integrations'
    id = db.Column(db.Integer, primary_key=True)
    exchange_name = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    api_credentials = db.Column(db.JSON)  # Encrypted
    supported_features = db.Column(db.JSON, default=list)
    rate_limits = db.Column(db.JSON)
    webhook_urls = db.Column(db.JSON)
    last_sync = db.Column(db.DateTime)
    sync_status = db.Column(db.String(20), default='active')
    error_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TradingControl(db.Model):
    __tablename__ = 'trading_controls'
    id = db.Column(db.Integer, primary_key=True)
    control_type = db.Column(db.String(50), nullable=False)  # 'pause', 'limit', 'emergency_stop'
    scope = db.Column(db.String(50), nullable=False)  # 'global', 'symbol', 'user'
    target = db.Column(db.String(100))  # symbol, user_id, etc.
    parameters = db.Column(db.JSON, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

class AlertRule(db.Model):
    __tablename__ = 'alert_rules'
    id = db.Column(db.Integer, primary_key=True)
    rule_name = db.Column(db.String(100), nullable=False)
    rule_type = db.Column(db.String(50), nullable=False)  # 'volume', 'price', 'system', 'security'
    conditions = db.Column(db.JSON, nullable=False)
    actions = db.Column(db.JSON, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    severity = db.Column(db.String(20), default='medium')
    notification_channels = db.Column(db.JSON, default=list)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ComplianceReport(db.Model):
    __tablename__ = 'compliance_reports'
    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(50), nullable=False)
    report_data = db.Column(db.JSON, nullable=False)
    generated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    date_range_start = db.Column(db.DateTime, nullable=False)
    date_range_end = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='generated')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Role-based permission decorators
def require_role(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or not user.is_active:
                return jsonify({'error': 'Invalid user'}), 403
            if user.role not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            g.current_user = user
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or not user.is_active:
                return jsonify({'error': 'Invalid user'}), 403
            if permission.value not in user.permissions and user.role != UserRole.SUPER_ADMIN:
                return jsonify({'error': 'Permission denied'}), 403
            g.current_user = user
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_admin_action(action_type, details, target_user_id=None, target_service=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            
            # Execute the function
            result = f(*args, **kwargs)
            
            # Log the action
            action = AdminAction(
                admin_id=user_id,
                action_type=action_type,
                action_details=details,
                target_user_id=target_user_id,
                target_service=target_service,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )
            db.session.add(action)
            db.session.commit()
            
            return result
        return decorated_function
    return decorator

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Tiger Admin Service',
        'version': '2.0.0',
        'consolidated_services': 30
    })

# User Management
@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
@require_permission(Permission.USER_MANAGEMENT)
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    status = request.args.get('status')
    role = request.args.get('role')
    
    query = User.query
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    
    if role:
        query = query.filter_by(role=UserRole(role))
    
    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'users': [{
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'role': user.role.value,
            'permissions': user.permissions,
            'is_active': user.is_active,
            'kyc_status': user.kyc_status,
            'created_at': user.created_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None
        } for user in users.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': users.total,
            'pages': users.pages
        }
    })

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@require_permission(Permission.USER_MANAGEMENT)
@log_admin_action('user_update', 'Updated user information', target_user_id=lambda: int(request.view_args['user_id']))
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'role' in data:
        user.role = UserRole(data['role'])
    if 'permissions' in data:
        user.permissions = data['permissions']
    if 'is_active' in data:
        user.is_active = data['is_active']
    if 'kyc_status' in data:
        user.kyc_status = data['kyc_status']
    
    db.session.commit()
    
    return jsonify({
        'message': 'User updated successfully',
        'user_id': user_id,
        'role': user.role.value,
        'is_active': user.is_active
    })

# Exchange Management
@app.route('/api/admin/exchanges', methods=['GET'])
@jwt_required()
@require_permission(Permission.EXCHANGE_INTEGRATION)
def get_exchanges():
    exchanges = ExchangeIntegration.query.all()
    
    return jsonify({
        'exchanges': [{
            'id': ex.id,
            'exchange_name': ex.exchange_name,
            'is_active': ex.is_active,
            'supported_features': ex.supported_features,
            'sync_status': ex.sync_status,
            'error_count': ex.error_count,
            'last_sync': ex.last_sync.isoformat() if ex.last_sync else None,
            'created_at': ex.created_at.isoformat()
        } for ex in exchanges]
    })

@app.route('/api/admin/exchanges/<int:exchange_id>/toggle', methods=['POST'])
@jwt_required()
@require_permission(Permission.EXCHANGE_INTEGRATION)
@log_admin_action('exchange_toggle', 'Toggled exchange status')
def toggle_exchange(exchange_id):
    exchange = ExchangeIntegration.query.get_or_404(exchange_id)
    exchange.is_active = not exchange.is_active
    db.session.commit()
    
    return jsonify({
        'message': f'Exchange {exchange.exchange_name} {"enabled" if exchange.is_active else "disabled"}',
        'is_active': exchange.is_active
    })

# Trading Controls
@app.route('/api/admin/trading-controls', methods=['POST'])
@jwt_required()
@require_permission(Permission.TRADING_CONTROL)
@log_admin_action('trading_control', 'Applied trading control')
def create_trading_control():
    data = request.get_json()
    
    control = TradingControl(
        control_type=data['control_type'],
        scope=data['scope'],
        target=data.get('target'),
        parameters=data['parameters'],
        created_by=g.current_user.id,
        expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
    )
    
    db.session.add(control)
    db.session.commit()
    
    return jsonify({
        'message': 'Trading control created successfully',
        'control_id': control.id,
        'control_type': control.control_type
    }), 201

@app.route('/api/admin/trading-controls', methods=['GET'])
@jwt_required()
@require_permission(Permission.TRADING_CONTROL)
def get_trading_controls():
    controls = TradingControl.query.filter_by(is_active=True).all()
    
    return jsonify({
        'trading_controls': [{
            'id': control.id,
            'control_type': control.control_type,
            'scope': control.scope,
            'target': control.target,
            'parameters': control.parameters,
            'expires_at': control.expires_at.isoformat() if control.expires_at else None,
            'created_at': control.created_at.isoformat()
        } for control in controls]
    })

# Emergency Controls
@app.route('/api/admin/emergency/stop-all-trading', methods=['POST'])
@jwt_required()
@require_role(UserRole.SUPER_ADMIN, UserRole.TRADING_ADMIN)
@log_admin_action('emergency_stop', 'Emergency stop - all trading paused')
def emergency_stop_all_trading():
    # Create emergency control
    control = TradingControl(
        control_type='emergency_stop',
        scope='global',
        parameters={'reason': 'Emergency admin action', 'all_services': True},
        created_by=g.current_user.id
    )
    
    db.session.add(control)
    
    # Disable all exchange integrations
    ExchangeIntegration.query.update({'is_active': False})
    
    db.session.commit()
    
    return jsonify({
        'message': 'EMERGENCY STOP ACTIVATED - All trading has been paused',
        'control_id': control.id,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/admin/emergency/restore-trading', methods=['POST'])
@jwt_required()
@require_role(UserRole.SUPER_ADMIN, UserRole.TRADING_ADMIN)
@log_admin_action('emergency_restore', 'Emergency restore - trading resumed')
def emergency_restore_trading():
    # Remove emergency controls
    TradingControl.query.filter_by(control_type='emergency_stop', is_active=True).update({'is_active': False})
    
    # Re-enable all exchange integrations
    ExchangeIntegration.query.update({'is_active': True})
    
    db.session.commit()
    
    return jsonify({
        'message': 'EMERGENCY RESTORE COMPLETED - All trading has been resumed',
        'timestamp': datetime.utcnow().isoformat()
    })

# System Configuration
@app.route('/api/admin/config', methods=['GET'])
@jwt_required()
@require_permission(Permission.SYSTEM_CONFIGURATION)
def get_system_config():
    configs = SystemConfig.query.all()
    
    # Hide sensitive values
    safe_configs = []
    for config in configs:
        config_data = {
            'id': config.id,
            'config_key': config.config_key,
            'config_type': config.config_type,
            'description': config.description,
            'updated_at': config.updated_at.isoformat()
        }
        
        if not config.is_sensitive:
            config_data['config_value'] = config.config_value
        else:
            config_data['config_value'] = '[HIDDEN]'
        
        safe_configs.append(config_data)
    
    return jsonify({'configs': safe_configs})

@app.route('/api/admin/config/<int:config_id>', methods=['PUT'])
@jwt_required()
@require_permission(Permission.SYSTEM_CONFIGURATION)
@log_admin_action('config_update', 'Updated system configuration')
def update_system_config(config_id):
    config = SystemConfig.query.get_or_404(config_id)
    data = request.get_json()
    
    if 'config_value' in data:
        config.config_value = data['config_value']
    config.updated_by = g.current_user.id
    config.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Configuration updated successfully',
        'config_key': config.config_key
    })

# Analytics & Monitoring
@app.route('/api/admin/analytics/dashboard', methods=['GET'])
@jwt_required()
@require_permission(Permission.ANALYTICS_ACCESS)
def get_analytics_dashboard():
    # This would typically connect to your analytics service
    # For now, returning mock data
    return jsonify({
        'dashboard_data': {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'total_exchanges': ExchangeIntegration.query.count(),
            'active_exchanges': ExchangeIntegration.query.filter_by(is_active=True).count(),
            'active_trading_controls': TradingControl.query.filter_by(is_active=True).count(),
            'recent_admin_actions': AdminAction.query.filter(
                AdminAction.created_at >= datetime.utcnow() - timedelta(hours=24)
            ).count()
        }
    })

@app.route('/api/admin/alerts/rules', methods=['GET'])
@jwt_required()
@require_permission(Permission.ANALYTICS_ACCESS)
def get_alert_rules():
    rules = AlertRule.query.filter_by(is_active=True).all()
    
    return jsonify({
        'alert_rules': [{
            'id': rule.id,
            'rule_name': rule.rule_name,
            'rule_type': rule.rule_type,
            'conditions': rule.conditions,
            'actions': rule.actions,
            'severity': rule.severity,
            'created_at': rule.created_at.isoformat()
        } for rule in rules]
    })

@app.route('/api/admin/alerts/rules', methods=['POST'])
@jwt_required()
@require_permission(Permission.SYSTEM_CONFIGURATION)
@log_admin_action('alert_rule_create', 'Created alert rule')
def create_alert_rule():
    data = request.get_json()
    
    rule = AlertRule(
        rule_name=data['rule_name'],
        rule_type=data['rule_type'],
        conditions=data['conditions'],
        actions=data['actions'],
        severity=data.get('severity', 'medium'),
        notification_channels=data.get('notification_channels', []),
        created_by=g.current_user.id
    )
    
    db.session.add(rule)
    db.session.commit()
    
    return jsonify({
        'message': 'Alert rule created successfully',
        'rule_id': rule.id
    }), 201

# Compliance Management
@app.route('/api/admin/compliance/reports', methods=['POST'])
@jwt_required()
@require_permission(Permission.COMPLIANCE_MANAGEMENT)
@log_admin_action('compliance_report', 'Generated compliance report')
def generate_compliance_report():
    data = request.get_json()
    
    report = ComplianceReport(
        report_type=data['report_type'],
        report_data=data['report_data'],
        generated_by=g.current_user.id,
        date_range_start=datetime.fromisoformat(data['date_range_start']),
        date_range_end=datetime.fromisoformat(data['date_range_end'])
    )
    
    db.session.add(report)
    db.session.commit()
    
    return jsonify({
        'message': 'Compliance report generated successfully',
        'report_id': report.id
    }), 201

@app.route('/api/admin/compliance/reports', methods=['GET'])
@jwt_required()
@require_permission(Permission.COMPLIANCE_MANAGEMENT)
def get_compliance_reports():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    report_type = request.args.get('report_type')
    
    query = ComplianceReport.query
    if report_type:
        query = query.filter_by(report_type=report_type)
    
    reports = query.order_by(ComplianceReport.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return jsonify({
        'reports': [{
            'id': report.id,
            'report_type': report.report_type,
            'date_range_start': report.date_range_start.isoformat(),
            'date_range_end': report.date_range_end.isoformat(),
            'status': report.status,
            'created_at': report.created_at.isoformat()
        } for report in reports.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': reports.total,
            'pages': reports.pages
        }
    })

# Service Health Monitoring
@app.route('/api/admin/services/health', methods=['GET'])
@jwt_required()
@require_permission(Permission.SYSTEM_CONFIGURATION)
def get_services_health():
    # This would typically check all microservices
    services = [
        {'name': 'tiger-pay-service', 'status': 'healthy', 'port': 5002},
        {'name': 'tiger-card-service', 'status': 'healthy', 'port': 5003},
        {'name': 'tiger-academy-service', 'status': 'healthy', 'port': 5004},
        {'name': 'tiger-staking-service', 'status': 'healthy', 'port': 5005},
        {'name': 'tiger-trading-service', 'status': 'healthy', 'port': 5006},
        {'name': 'tiger-wallet-service', 'status': 'healthy', 'port': 5007},
        {'name': 'tiger-user-service', 'status': 'healthy', 'port': 5001}
    ]
    
    return jsonify({
        'services': services,
        'total_services': len(services),
        'healthy_services': sum(1 for s in services if s['status'] == 'healthy'),
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create default super admin if not exists
        if not User.query.filter_by(email='admin@tigerex.com').first():
            super_admin = User(
                email='admin@tigerex.com',
                username='superadmin',
                role=UserRole.SUPER_ADMIN,
                permissions=[p.value for p in Permission],
                is_active=True
            )
            db.session.add(super_admin)
            db.session.commit()
            logger.info("Super admin user created")
    
    app.run(host='0.0.0.0', port=5008, debug=True)