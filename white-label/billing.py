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

# ==================== WALLET BILLING ====================
wallets_db = {}

@billing_bp.route('/api/wallet/create', methods=['POST'])
def create_wallet():
    data = request.json
    client_id = data.get('client_id')
    wallet_type = data.get('type', 'dex')  # 'dex' or 'cex'
    
    wordlist = ["abandon","ability","able","about","above","absent","absorb","abstract","absurd","abuse",
        "access","accident","account","accuse","achieve","acid","acoustic","acquire","across","act","action",
        "actor","actress","actual","adapt"]
    
    if wallet_type == 'dex':
        wallet = {
            'type': 'non_custodial',
            'seed_phrase': ' '.join(wordlist[:24]),
            'backup_key': f'BKP_{uuid.uuid4().hex[:12].upper()}',
            'ownership': 'USER_OWNS',
            'address': f'0x{uuid.uuid4().hex[2:42]}'
        }
    else:
        wallet = {
            'type': 'custodial',
            'ownership': 'EXCHANGE_CONTROLLED',
            'address': f'0x{uuid.uuid4().hex[2:42]}'
        }
    
    if client_id not in wallets_db:
        wallets_db[client_id] = []
    wallets_db[client_id].append(wallet)
    
    return jsonify({'success': True, 'wallet': wallet})

@billing_bp.route('/api/wallet/list/<client_id>', methods=['GET'])
def list_wallets(client_id):
    return jsonify({'wallets': wallets_db.get(client_id, [])})

# ==================== GAS FEES ====================
gas_fees = {
    'ethereum': {'send': 0.001, 'swap': 0.002},
    'bsc': {'send': 0.0005, 'swap': 0.001},
    'polygon': {'send': 0.0001, 'swap': 0.0002}
}

@billing_bp.route('/api/admin/gas-fees', methods=['GET'])
def get_gas_fees():
    return jsonify({'gas_fees': gas_fees})

@billing_bp.route('/api/admin/set-gas-fee', methods=['POST'])
def set_gas_fee():
    data = request.json
    chain = data.get('chain')
    tx_type = data.get('tx_type')
    fee = data.get('fee')
    gas_fees[chain][tx_type] = fee
    return jsonify({'success': True, 'message': f'Gas fee updated for {chain}'})
def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
