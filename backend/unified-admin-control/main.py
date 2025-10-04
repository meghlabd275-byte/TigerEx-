#!/usr/bin/env python3
"""
Unified Admin Control Panel
Manages all TigerEx services with complete administrative control
"""

from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import os
import requests
import json
from functools import wraps

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
class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='admin')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

class ServiceStatus(db.Model):
    __tablename__ = 'service_status'
    
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='active')
    endpoint = db.Column(db.String(200))
    last_health_check = db.Column(db.DateTime)
    health_status = db.Column(db.String(20), default='unknown')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserActivity(db.Model):
    __tablename__ = 'user_activity'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    service_name = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Admin decorator
def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        admin_user = AdminUser.query.filter_by(id=current_user_id, is_active=True).first()
        if not admin_user:
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Service definitions
SERVICES = {
    "common_function": [
        "transfer-service", "binance-wallet-service", "buy-crypto-service", 
        "disable-account-service", "account-statement-service", "demo-trading",
        "launchpool", "recurring-buy-service", "deposit-fiat-service", "deposit",
        "referral", "pay", "orders", "sell-to-fiat-service", "withdraw-fiat-service", "security-service"
    ],
    "gift_campaign": [
        "word-of-day-service", "new-listing-promos-service", "spot-colosseum-service",
        "button-game-service", "carnival-quest-service", "refer-win-bnb-service",
        "bnb-ath-service", "monthly-challenge-service", "rewards-hub-service",
        "futures-masters-service", "my-gifts-service", "learn-earn-service",
        "red-packet-service", "alpha-events-service"
    ],
    "trade": [
        "convert", "spot", "alpha", "margin", "futures", "copy-trading",
        "otc", "p2p", "trading-bots", "convert-recurring-service", "index-linked-service", "options"
    ],
    "earn": [
        "earn", "sol-staking-service", "smart-arbitrage-service", "yield-arena-service",
        "super-mine-service", "discount-buy-service", "rwusd-service", "bfusd-service",
        "onchain-yields-service", "soft-staking-service", "simple-earn-service",
        "pool", "eth-staking-service", "dual-investment"
    ],
    "finance": [
        "loans-service", "sharia-earn-service", "vip-loan-service", 
        "fixed-rate-loans-service", "binance-wealth-service"
    ],
    "information": [
        "chat-service", "square-service", "binance-academy-service", "live-service",
        "research-service", "futures-chatroom-service", "deposit-withdrawal-status-service",
        "proof-of-reserves"
    ],
    "help_support": [
        "action-required-service", "binance-verify-service", "support-service",
        "customer-service-service", "self-service-service"
    ],
    "others": [
        "third-party-account-service", "affiliate", "megadrop-service", "token-unlock-service",
        "gift-card-service", "trading-insight", "api-management-service", "fan-token-service",
        "binance-nft-service", "marketplace", "babt-service", "send-cash-service", "charity-service"
    ]
}

# Admin Dashboard HTML Template
ADMIN_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TigerEx Admin Control Panel</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
</head>
<body class="bg-gray-100">
    <div x-data="adminDashboard()" class="min-h-screen">
        <!-- Header -->
        <header class="bg-blue-600 text-white p-4">
            <div class="container mx-auto flex justify-between items-center">
                <h1 class="text-2xl font-bold">🐅 TigerEx Admin Control Panel</h1>
                <div class="flex items-center space-x-4">
                    <span x-text="'Admin: ' + adminUser"></span>
                    <button @click="logout()" class="bg-red-500 px-4 py-2 rounded">Logout</button>
                </div>
            </div>
        </header>

        <!-- Navigation -->
        <nav class="bg-blue-500 text-white p-2">
            <div class="container mx-auto">
                <div class="flex space-x-4">
                    <button @click="activeTab = 'dashboard'" 
                            :class="activeTab === 'dashboard' ? 'bg-blue-700' : ''" 
                            class="px-4 py-2 rounded">Dashboard</button>
                    <button @click="activeTab = 'services'" 
                            :class="activeTab === 'services' ? 'bg-blue-700' : ''" 
                            class="px-4 py-2 rounded">Services</button>
                    <button @click="activeTab = 'users'" 
                            :class="activeTab === 'users' ? 'bg-blue-700' : ''" 
                            class="px-4 py-2 rounded">Users</button>
                    <button @click="activeTab = 'analytics'" 
                            :class="activeTab === 'analytics' ? 'bg-blue-700' : ''" 
                            class="px-4 py-2 rounded">Analytics</button>
                </div>
            </div>
        </nav>

        <!-- Main Content -->
        <main class="container mx-auto p-4">
            <!-- Dashboard Tab -->
            <div x-show="activeTab === 'dashboard'" class="space-y-6">
                <h2 class="text-3xl font-bold mb-6">System Overview</h2>
                
                <!-- Stats Cards -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div class="bg-white p-6 rounded-lg shadow">
                        <h3 class="text-lg font-semibold text-gray-600">Total Services</h3>
                        <p class="text-3xl font-bold text-blue-600" x-text="stats.totalServices"></p>
                    </div>
                    <div class="bg-white p-6 rounded-lg shadow">
                        <h3 class="text-lg font-semibold text-gray-600">Active Services</h3>
                        <p class="text-3xl font-bold text-green-600" x-text="stats.activeServices"></p>
                    </div>
                    <div class="bg-white p-6 rounded-lg shadow">
                        <h3 class="text-lg font-semibold text-gray-600">Total Users</h3>
                        <p class="text-3xl font-bold text-purple-600" x-text="stats.totalUsers"></p>
                    </div>
                    <div class="bg-white p-6 rounded-lg shadow">
                        <h3 class="text-lg font-semibold text-gray-600">Active Users</h3>
                        <p class="text-3xl font-bold text-orange-600" x-text="stats.activeUsers"></p>
                    </div>
                </div>

                <!-- Service Categories -->
                <div class="bg-white p-6 rounded-lg shadow">
                    <h3 class="text-xl font-bold mb-4">Service Categories</h3>
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <template x-for="(services, category) in serviceCategories" :key="category">
                            <div class="text-center p-4 bg-gray-50 rounded">
                                <h4 class="font-semibold capitalize" x-text="category.replace('_', ' ')"></h4>
                                <p class="text-2xl font-bold text-blue-600" x-text="services.length"></p>
                            </div>
                        </template>
                    </div>
                </div>
            </div>

            <!-- Services Tab -->
            <div x-show="activeTab === 'services'" class="space-y-6">
                <h2 class="text-3xl font-bold mb-6">Service Management</h2>
                
                <template x-for="(services, category) in serviceCategories" :key="category">
                    <div class="bg-white p-6 rounded-lg shadow">
                        <h3 class="text-xl font-bold mb-4 capitalize" x-text="category.replace('_', ' ')"></h3>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <template x-for="service in services" :key="service">
                                <div class="border p-4 rounded flex justify-between items-center">
                                    <div>
                                        <h4 class="font-semibold" x-text="service"></h4>
                                        <p class="text-sm text-gray-600">Status: Active</p>
                                    </div>
                                    <div class="flex space-x-2">
                                        <button class="bg-green-500 text-white px-3 py-1 rounded text-sm">Enable</button>
                                        <button class="bg-red-500 text-white px-3 py-1 rounded text-sm">Disable</button>
                                    </div>
                                </div>
                            </template>
                        </div>
                    </div>
                </template>
            </div>

            <!-- Users Tab -->
            <div x-show="activeTab === 'users'" class="space-y-6">
                <h2 class="text-3xl font-bold mb-6">User Management</h2>
                <div class="bg-white p-6 rounded-lg shadow">
                    <p class="text-gray-600">User management interface will be implemented here.</p>
                </div>
            </div>

            <!-- Analytics Tab -->
            <div x-show="activeTab === 'analytics'" class="space-y-6">
                <h2 class="text-3xl font-bold mb-6">Analytics & Reports</h2>
                <div class="bg-white p-6 rounded-lg shadow">
                    <p class="text-gray-600">Analytics dashboard will be implemented here.</p>
                </div>
            </div>
        </main>
    </div>

    <script>
        function adminDashboard() {
            return {
                activeTab: 'dashboard',
                adminUser: 'Admin User',
                stats: {
                    totalServices: 87,
                    activeServices: 87,
                    totalUsers: 1250,
                    activeUsers: 892
                },
                serviceCategories: {
                    common_function: ["transfer-service", "binance-wallet-service", "buy-crypto-service", "disable-account-service", "account-statement-service", "demo-trading", "launchpool", "recurring-buy-service", "deposit-fiat-service", "deposit", "referral", "pay", "orders", "sell-to-fiat-service", "withdraw-fiat-service", "security-service"],
                    gift_campaign: ["word-of-day-service", "new-listing-promos-service", "spot-colosseum-service", "button-game-service", "carnival-quest-service", "refer-win-bnb-service", "bnb-ath-service", "monthly-challenge-service", "rewards-hub-service", "futures-masters-service", "my-gifts-service", "learn-earn-service", "red-packet-service", "alpha-events-service"],
                    trade: ["convert", "spot", "alpha", "margin", "futures", "copy-trading", "otc", "p2p", "trading-bots", "convert-recurring-service", "index-linked-service", "options"],
                    earn: ["earn", "sol-staking-service", "smart-arbitrage-service", "yield-arena-service", "super-mine-service", "discount-buy-service", "rwusd-service", "bfusd-service", "onchain-yields-service", "soft-staking-service", "simple-earn-service", "pool", "eth-staking-service", "dual-investment"],
                    finance: ["loans-service", "sharia-earn-service", "vip-loan-service", "fixed-rate-loans-service", "binance-wealth-service"],
                    information: ["chat-service", "square-service", "binance-academy-service", "live-service", "research-service", "futures-chatroom-service", "deposit-withdrawal-status-service", "proof-of-reserves"],
                    help_support: ["action-required-service", "binance-verify-service", "support-service", "customer-service-service", "self-service-service"],
                    others: ["third-party-account-service", "affiliate", "megadrop-service", "token-unlock-service", "gift-card-service", "trading-insight", "api-management-service", "fan-token-service", "binance-nft-service", "marketplace", "babt-service", "send-cash-service", "charity-service"]
                },
                logout() {
                    alert('Logout functionality will be implemented');
                }
            }
        }
    </script>
</body>
</html>
"""

# Routes
@app.route('/')
def admin_dashboard():
    """Serve the admin dashboard"""
    return render_template_string(ADMIN_DASHBOARD_HTML)

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Admin login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # For demo purposes, accept admin/admin
        if username == 'admin' and password == 'admin':
            access_token = create_access_token(identity=1)
            return jsonify({
                'success': True,
                'access_token': access_token,
                'user': {'id': 1, 'username': 'admin', 'role': 'admin'}
            })
        
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def get_admin_stats():
    """Get system statistics"""
    try:
        total_services = sum(len(services) for services in SERVICES.values())
        active_services = ServiceStatus.query.filter_by(status='active').count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_services': total_services,
                'active_services': active_services if active_services > 0 else total_services,
                'total_users': 1250,  # Mock data
                'active_users': 892,  # Mock data
                'service_categories': SERVICES
            }
        })
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/services', methods=['GET'])
@admin_required
def get_all_services():
    """Get all services with their status"""
    try:
        services_data = {}
        
        for category, services in SERVICES.items():
            services_data[category] = []
            for service in services:
                service_status = ServiceStatus.query.filter_by(service_name=service).first()
                services_data[category].append({
                    'name': service,
                    'status': service_status.status if service_status else 'active',
                    'health': service_status.health_status if service_status else 'healthy',
                    'last_check': service_status.last_health_check.isoformat() if service_status and service_status.last_health_check else None
                })
        
        return jsonify({
            'success': True,
            'services': services_data
        })
    except Exception as e:
        logger.error(f"Error getting services: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/service/<service_name>/toggle', methods=['POST'])
@admin_required
def toggle_service(service_name):
    """Enable/disable a service"""
    try:
        data = request.get_json()
        new_status = data.get('status', 'active')
        
        service_status = ServiceStatus.query.filter_by(service_name=service_name).first()
        if not service_status:
            service_status = ServiceStatus(
                service_name=service_name,
                category='unknown',
                status=new_status
            )
            db.session.add(service_status)
        else:
            service_status.status = new_status
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Service {service_name} {new_status}',
            'service': service_name,
            'status': new_status
        })
    except Exception as e:
        logger.error(f"Error toggling service: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users"""
    try:
        # Mock user data for now
        users = [
            {'id': 1, 'username': 'user1', 'email': 'user1@example.com', 'status': 'active'},
            {'id': 2, 'username': 'user2', 'email': 'user2@example.com', 'status': 'active'},
        ]
        
        return jsonify({
            'success': True,
            'users': users
        })
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'unified-admin-control',
        'timestamp': datetime.utcnow().isoformat(),
        'total_services': sum(len(services) for services in SERVICES.values())
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Initialize service status records
        for category, services in SERVICES.items():
            for service in services:
                existing = ServiceStatus.query.filter_by(service_name=service).first()
                if not existing:
                    service_status = ServiceStatus(
                        service_name=service,
                        category=category,
                        status='active',
                        health_status='healthy'
                    )
                    db.session.add(service_status)
        
        db.session.commit()
    
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)), debug=True)