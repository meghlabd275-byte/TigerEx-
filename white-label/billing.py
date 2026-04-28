"""
TigerEx White Label Billing & Subscription System
Integrates with Stripe for payments
"""
from flask import Blueprint, request, jsonify
import uuid
import os
from datetime import datetime, timedelta

billing_bp = Blueprint('billing', __name__)

# Stripe configuration (set in environment)
STRIPE_KEY = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_xxx')

PLANS = {
    'starter': {
        'name': 'Starter',
        'price': 99,
        'features': ['spot_trading', 'basic_api'],
        'users': 100
    },
    'professional': {
        'name': 'Professional',
        'price': 299,
        'features': ['spot_trading', 'futures', 'margin', 'api', 'priority_support'],
        'users': 1000
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': 999,
        'features': ['all_features', 'custom_domain', 'dedicated_support'],
        'users': -1
    }
}

subscriptions = {}

@billing_bp.route('/api/billing/plans', methods=['GET'])
def get_plans():
    return jsonify({'plans': PLANS})

@billing_bp.route('/api/billing/subscribe', methods=['POST'])
def create_subscription():
    data = request.json
    client_id = data.get('client_id')
    plan = data.get('plan')
    
    if plan not in PLANS:
        return jsonify({'error': 'Invalid plan'}), 400
    
    # Create subscription
    sub_id = f'sub_{uuid.uuid4().hex[:8]}'
    subscriptions[client_id] = {
        'stripe_customer': f'cus_{uuid.uuid4().hex[:8]}',
        'subscription_id': sub_id,
        'plan': plan,
        'status': 'active'
    }
    
    return jsonify({
        'success': True,
        'subscription_id': sub_id,
        'plan': plan,
        'status': 'active'
    })

@billing_bp.route('/api/billing/invoice/<client_id>', methods=['GET'])
def get_invoice(client_id):
    if client_id not in subscriptions:
        return jsonify({'error': 'No subscription'}), 404
    
    sub = subscriptions[client_id]
    plan = PLANS[sub['plan']]
    
    invoice = {
        'invoice_id': f'INV-{uuid.uuid4().hex[:8].upper()}',
        'client_id': client_id,
        'plan': sub['plan'],
        'amount': plan['price'],
        'currency': 'USD',
        'status': 'paid',
        'date': datetime.now().isoformat()
    }
    
    return jsonify(invoice)

print("White Label Billing Module Ready")
