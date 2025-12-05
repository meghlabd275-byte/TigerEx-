#!/usr/bin/env python3
"""
Tiger Staking Service
Category: staking
Description: Comprehensive staking platform for cryptocurrency investments
"""

from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import os
import uuid
import json
from decimal import Decimal
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

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    kyc_status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class StakingPool(db.Model):
    __tablename__ = 'staking_pools'
    id = db.Column(db.Integer, primary_key=True)
    pool_name = db.Column(db.String(100), nullable=False)
    cryptocurrency = db.Column(db.String(20), nullable=False)
    staking_type = db.Column(db.String(20), nullable=False)  # 'flexible', 'locked', 'defi', 'liquid'
    apy = db.Column(db.Numeric(10, 4), nullable=False)  # Annual Percentage Yield
    minimum_stake = db.Column(db.Numeric(20, 8), nullable=False)
    maximum_stake = db.Column(db.Numeric(20, 8))
    lock_period_days = db.Column(db.Integer)  # For locked staking
    total_staked = db.Column(db.Numeric(20, 8), default=0)
    maximum_capacity = db.Column(db.Numeric(20, 8))
    is_active = db.Column(db.Boolean, default=True)
    description = db.Column(db.Text)
    risks = db.Column(db.JSON)
    rewards_schedule = db.Column(db.JSON)  # Daily, weekly, monthly rewards
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserStake(db.Model):
    __tablename__ = 'user_stakes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    pool_id = db.Column(db.Integer, db.ForeignKey('staking_pools.id'), nullable=False)
    stake_id = db.Column(db.String(100), unique=True, nullable=False)
    amount = db.Column(db.Numeric(20, 8), nullable=False)
    cryptocurrency = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='active')  # 'active', 'completed', 'withdrawn', 'early_withdrawal'
    apy = db.Column(db.Numeric(10, 4), nullable=False)
    rewards_earned = db.Column(db.Numeric(20, 8), default=0)
    last_reward_calculation = db.Column(db.DateTime, default=datetime.utcnow)
    staked_at = db.Column(db.DateTime, default=datetime.utcnow)
    unlock_date = db.Column(db.DateTime)  # For locked staking
    completed_at = db.Column(db.DateTime)
    auto_compound = db.Column(db.Boolean, default=False)
    compound_frequency = db.Column(db.String(20), default='daily')  # 'daily', 'weekly', 'monthly'

class StakingReward(db.Model):
    __tablename__ = 'staking_rewards'
    id = db.Column(db.Integer, primary_key=True)
    user_stake_id = db.Column(db.Integer, db.ForeignKey('user_stakes.id'), nullable=False)
    reward_amount = db.Column(db.Numeric(20, 8), nullable=False)
    reward_type = db.Column(db.String(20), default='staking')  # 'staking', 'bonus', 'referral'
    apy_rate = db.Column(db.Numeric(10, 4))
    calculation_date = db.Column(db.DateTime, default=datetime.utcnow)
    transaction_hash = db.Column(db.String(100))  # For on-chain rewards
    is_compounded = db.Column(db.Boolean, default=False)

class StakingTransaction(db.Model):
    __tablename__ = 'staking_transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_stake_id = db.Column(db.Integer, db.ForeignKey('user_stakes.id'))
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'stake', 'unstake', 'reward', 'penalty'
    amount = db.Column(db.Numeric(20, 8), nullable=False)
    cryptocurrency = db.Column(db.String(20), nullable=False)
    fee = db.Column(db.Numeric(20, 8), default=0)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'completed', 'failed'
    transaction_hash = db.Column(db.String(100))
    metadata = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

class StakingPromotion(db.Model):
    __tablename__ = 'staking_promotions'
    id = db.Column(db.Integer, primary_key=True)
    promotion_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    promotion_type = db.Column(db.String(20), nullable=False)  # 'bonus_apy', 'cashback', 'referral'
    bonus_apy = db.Column(db.Numeric(10, 4))  # Additional APY
    cashback_percentage = db.Column(db.Numeric(5, 2))
    minimum_stake = db.Column(db.Numeric(20, 8))
    maximum_bonus = db.Column(db.Numeric(20, 8))
    applicable_cryptocurrencies = db.Column(db.JSON)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    usage_count = db.Column(db.Integer, default=0)
    max_usage = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def require_kyc(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.kyc_status != 'verified':
            return jsonify({'error': 'KYC verification required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Tiger Staking Service',
        'version': '1.0.0'
    })

@app.route('/api/staking-pools', methods=['GET'])
def get_staking_pools():
    cryptocurrency = request.args.get('cryptocurrency')
    staking_type = request.args.get('staking_type')
    
    query = StakingPool.query.filter_by(is_active=True)
    
    if cryptocurrency:
        query = query.filter_by(cryptocurrency=cryptocurrency)
    if staking_type:
        query = query.filter_by(staking_type=staking_type)
    
    pools = query.order_by(StakingPool.apy.desc()).all()
    
    return jsonify({
        'staking_pools': [{
            'id': pool.id,
            'pool_name': pool.pool_name,
            'cryptocurrency': pool.cryptocurrency,
            'staking_type': pool.staking_type,
            'apy': float(pool.apy),
            'minimum_stake': float(pool.minimum_stake),
            'maximum_stake': float(pool.maximum_stake) if pool.maximum_stake else None,
            'lock_period_days': pool.lock_period_days,
            'total_staked': float(pool.total_staked),
            'maximum_capacity': float(pool.maximum_capacity) if pool.maximum_capacity else None,
            'description': pool.description,
            'risks': pool.risks,
            'rewards_schedule': pool.rewards_schedule,
            'created_at': pool.created_at.isoformat()
        } for pool in pools]
    })

@app.route('/api/staking-pools/<int:pool_id>', methods=['GET'])
def get_staking_pool(pool_id):
    pool = StakingPool.query.filter_by(id=pool_id, is_active=True).first()
    if not pool:
        return jsonify({'error': 'Staking pool not found'}), 404
    
    # Get pool statistics
    total_users = UserStake.query.filter_by(pool_id=pool_id, status='active').count()
    total_staked = db.session.query(db.func.sum(UserStake.amount))\
        .filter_by(pool_id=pool_id, status='active')\
        .scalar() or Decimal('0')
    
    return jsonify({
        'pool': {
            'id': pool.id,
            'pool_name': pool.pool_name,
            'cryptocurrency': pool.cryptocurrency,
            'staking_type': pool.staking_type,
            'apy': float(pool.apy),
            'minimum_stake': float(pool.minimum_stake),
            'maximum_stake': float(pool.maximum_stake) if pool.maximum_stake else None,
            'lock_period_days': pool.lock_period_days,
            'total_staked': float(pool.total_staked),
            'maximum_capacity': float(pool.maximum_capacity) if pool.maximum_capacity else None,
            'description': pool.description,
            'risks': pool.risks,
            'rewards_schedule': pool.rewards_schedule,
            'created_at': pool.created_at.isoformat()
        },
        'statistics': {
            'total_users': total_users,
            'total_staked_by_users': float(total_staked),
            'utilization_percentage': float((total_staked / pool.maximum_capacity) * 100) if pool.maximum_capacity else None
        }
    })

@app.route('/api/stake', methods=['POST'])
@jwt_required()
@require_kyc
def create_stake():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['pool_id', 'amount']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    pool = StakingPool.query.filter_by(id=data['pool_id'], is_active=True).first()
    if not pool:
        return jsonify({'error': 'Staking pool not found'}), 404
    
    amount = Decimal(str(data['amount']))
    
    # Validate amount
    if amount < pool.minimum_stake:
        return jsonify({'error': f'Minimum stake amount is {pool.minimum_stake} {pool.cryptocurrency}'}), 400
    
    if pool.maximum_stake and amount > pool.maximum_stake:
        return jsonify({'error': f'Maximum stake amount is {pool.maximum_stake} {pool.cryptocurrency}'}), 400
    
    if pool.maximum_capacity:
        current_total = pool.total_staked + amount
        if current_total > pool.maximum_capacity:
            return jsonify({'error': 'Pool capacity exceeded'}), 400
    
    # Generate stake ID
    stake_id = f"TS{datetime.utcnow().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    
    # Calculate unlock date for locked staking
    unlock_date = None
    if pool.lock_period_days:
        unlock_date = datetime.utcnow() + timedelta(days=pool.lock_period_days)
    
    # Create user stake
    user_stake = UserStake(
        user_id=user_id,
        pool_id=pool.id,
        stake_id=stake_id,
        amount=amount,
        cryptocurrency=pool.cryptocurrency,
        apy=pool.apy,
        unlock_date=unlock_date,
        auto_compound=data.get('auto_compound', False),
        compound_frequency=data.get('compound_frequency', 'daily')
    )
    
    db.session.add(user_stake)
    
    # Update pool total staked
    pool.total_staked += amount
    
    # Create transaction record
    transaction_id = f"TX{datetime.utcnow().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    transaction = StakingTransaction(
        user_id=user_id,
        user_stake_id=user_stake.id,
        transaction_id=transaction_id,
        transaction_type='stake',
        amount=amount,
        cryptocurrency=pool.cryptocurrency,
        status='completed',
        completed_at=datetime.utcnow()
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    # Check for applicable promotions
    apply_staking_promotions(user_id, user_stake)
    
    return jsonify({
        'message': 'Stake created successfully',
        'stake_id': stake_id,
        'pool_name': pool.pool_name,
        'amount': float(amount),
        'cryptocurrency': pool.cryptocurrency,
        'apy': float(pool.apy),
        'unlock_date': unlock_date.isoformat() if unlock_date else None,
        'auto_compound': user_stake.auto_compound
    }), 201

def apply_staking_promotions(user_id, user_stake):
    """Apply applicable staking promotions"""
    current_time = datetime.utcnow()
    
    promotions = StakingPromotion.query.filter(
        StakingPromotion.is_active == True,
        StakingPromotion.start_date <= current_time,
        StakingPromotion.end_date >= current_time,
        StakingPromotion.applicable_cryptocurrencies.contains([user_stake.cryptocurrency])
    ).all()
    
    for promotion in promotions:
        if promotion.minimum_stake and user_stake.amount < promotion.minimum_stake:
            continue
        
        if promotion.max_usage and promotion.usage_count >= promotion.max_usage:
            continue
        
        # Apply bonus APY
        if promotion.promotion_type == 'bonus_apy' and promotion.bonus_apy:
            user_stake.apy += promotion.bonus_apy
        
        # Apply cashback
        if promotion.promotion_type == 'cashback' and promotion.cashback_percentage:
            cashback_amount = user_stake.amount * (promotion.cashback_percentage / 100)
            create_reward_transaction(user_id, user_stake.id, cashback_amount, 'bonus')
        
        promotion.usage_count += 1

@app.route('/api/my-stakes', methods=['GET'])
@jwt_required()
def get_my_stakes():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    
    query = db.session.query(UserStake, StakingPool)\
        .join(StakingPool, UserStake.pool_id == StakingPool.id)\
        .filter(UserStake.user_id == user_id)
    
    if status:
        query = query.filter(UserStake.status == status)
    
    stakes = query.order_by(UserStake.staked_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    # Calculate pending rewards for each stake
    stakes_with_rewards = []
    for user_stake, pool in stakes.items:
        pending_rewards = calculate_pending_rewards(user_stake)
        stakes_with_rewards.append({
            'stake': {
                'id': user_stake.id,
                'stake_id': user_stake.stake_id,
                'pool_name': pool.pool_name,
                'cryptocurrency': user_stake.cryptocurrency,
                'amount': float(user_stake.amount),
                'staking_type': pool.staking_type,
                'apy': float(user_stake.apy),
                'rewards_earned': float(user_stake.rewards_earned),
                'pending_rewards': float(pending_rewards),
                'status': user_stake.status,
                'auto_compound': user_stake.auto_compound,
                'compound_frequency': user_stake.compound_frequency,
                'staked_at': user_stake.staked_at.isoformat(),
                'unlock_date': user_stake.unlock_date.isoformat() if user_stake.unlock_date else None,
                'completed_at': user_stake.completed_at.isoformat() if user_stake.completed_at else None
            },
            'pool': {
                'id': pool.id,
                'lock_period_days': pool.lock_period_days,
                'minimum_stake': float(pool.minimum_stake)
            }
        })
    
    return jsonify({
        'stakes': stakes_with_rewards,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': stakes.total,
            'pages': stakes.pages
        }
    })

def calculate_pending_rewards(user_stake):
    """Calculate pending rewards for a stake"""
    if user_stake.status != 'active':
        return Decimal('0')
    
    # Time since last reward calculation
    time_diff = datetime.utcnow() - user_stake.last_reward_calculation
    days = time_diff.total_seconds() / (24 * 3600)
    
    if days <= 0:
        return Decimal('0')
    
    # Calculate daily rewards
    daily_rate = user_stake.apy / 100 / 365
    daily_reward = user_stake.amount * Decimal(str(daily_rate))
    
    # Calculate total pending rewards
    pending_rewards = daily_reward * Decimal(str(days))
    
    # Include already earned rewards
    total_pending = user_stake.rewards_earned + pending_rewards
    
    return total_pending

@app.route('/api/stakes/<int:stake_id>/unstake', methods=['POST'])
@jwt_required()
def unstake(stake_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    user_stake = UserStake.query.filter_by(id=stake_id, user_id=user_id).first()
    if not user_stake:
        return jsonify({'error': 'Stake not found'}), 404
    
    if user_stake.status != 'active':
        return jsonify({'error': 'Stake is not active'}), 400
    
    pool = StakingPool.query.get(user_stake.pool_id)
    
    # Check if unlock period has passed for locked staking
    if pool.staking_type == 'locked' and user_stake.unlock_date:
        if datetime.utcnow() < user_stake.unlock_date:
            return jsonify({
                'error': 'Stake is still locked',
                'unlock_date': user_stake.unlock_date.isoformat()
            }), 400
    
    # Calculate final rewards
    final_rewards = calculate_pending_rewards(user_stake)
    
    # Check for early withdrawal penalty
    penalty_amount = Decimal('0')
    if pool.staking_type == 'locked' and data.get('early_withdrawal', False):
        penalty_percentage = 10  # 10% penalty for early withdrawal
        penalty_amount = user_stake.amount * Decimal(str(penalty_percentage / 100))
    
    # Final amount to return
    final_amount = user_stake.amount + final_rewards - penalty_amount
    
    # Update stake status
    user_stake.status = 'withdrawn'
    user_stake.completed_at = datetime.utcnow()
    user_stake.rewards_earned = final_rewards
    
    # Update pool total staked
    pool.total_staked -= user_stake.amount
    
    # Create unstake transaction
    transaction_id = f"TX{datetime.utcnow().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    transaction = StakingTransaction(
        user_id=user_id,
        user_stake_id=user_stake.id,
        transaction_id=transaction_id,
        transaction_type='unstake',
        amount=final_amount,
        cryptocurrency=user_stake.cryptocurrency,
        fee=penalty_amount,
        status='completed',
        completed_at=datetime.utcnow(),
        metadata={
            'early_withdrawal': data.get('early_withdrawal', False),
            'penalty_amount': float(penalty_amount)
        }
    )
    
    db.session.add(transaction)
    
    # Create reward transaction
    if final_rewards > 0:
        create_reward_transaction(user_id, user_stake.id, final_rewards, 'staking')
    
    db.session.commit()
    
    return jsonify({
        'message': 'Stake unstaked successfully',
        'stake_id': user_stake.stake_id,
        'amount_returned': float(final_amount),
        'rewards_earned': float(final_rewards),
        'penalty_amount': float(penalty_amount),
        'transaction_id': transaction_id
    })

def create_reward_transaction(user_id, user_stake_id, reward_amount, reward_type):
    """Create a reward transaction"""
    user_stake = UserStake.query.get(user_stake_id)
    
    transaction_id = f"RX{datetime.utcnow().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    transaction = StakingTransaction(
        user_id=user_id,
        user_stake_id=user_stake_id,
        transaction_id=transaction_id,
        transaction_type='reward',
        amount=reward_amount,
        cryptocurrency=user_stake.cryptocurrency,
        status='completed',
        completed_at=datetime.utcnow(),
        metadata={'reward_type': reward_type}
    )
    
    db.session.add(transaction)
    
    # Create reward record
    reward = StakingReward(
        user_stake_id=user_stake_id,
        reward_amount=reward_amount,
        reward_type=reward_type,
        apy_rate=user_stake.apy
    )
    
    db.session.add(reward)

@app.route('/api/stakes/<int:stake_id>/rewards', methods=['GET'])
@jwt_required()
def get_stake_rewards(stake_id):
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    user_stake = UserStake.query.filter_by(id=stake_id, user_id=user_id).first()
    if not user_stake:
        return jsonify({'error': 'Stake not found'}), 404
    
    rewards = StakingReward.query.filter_by(user_stake_id=stake_id)\
        .order_by(StakingReward.calculation_date.desc())\
        .paginate(page=page, per_page=per_page)
    
    return jsonify({
        'rewards': [{
            'id': reward.id,
            'reward_amount': float(reward.reward_amount),
            'reward_type': reward.reward_type,
            'apy_rate': float(reward.apy_rate) if reward.apy_rate else None,
            'calculation_date': reward.calculation_date.isoformat(),
            'transaction_hash': reward.transaction_hash,
            'is_compounded': reward.is_compounded
        } for reward in rewards.items],
        'total_rewards_earned': float(user_stake.rewards_earned),
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': rewards.total,
            'pages': rewards.pages
        }
    })

@app.route('/api/promotions', methods=['GET'])
def get_promotions():
    current_time = datetime.utcnow()
    
    promotions = StakingPromotion.query.filter(
        StakingPromotion.is_active == True,
        StakingPromotion.start_date <= current_time,
        StakingPromotion.end_date >= current_time
    ).order_by(StakingPromotion.created_at.desc()).all()
    
    return jsonify({
        'promotions': [{
            'id': promotion.id,
            'promotion_name': promotion.promotion_name,
            'description': promotion.description,
            'promotion_type': promotion.promotion_type,
            'bonus_apy': float(promotion.bonus_apy) if promotion.bonus_apy else None,
            'cashback_percentage': float(promotion.cashback_percentage) if promotion.cashback_percentage else None,
            'minimum_stake': float(promotion.minimum_stake) if promotion.minimum_stake else None,
            'maximum_bonus': float(promotion.maximum_bonus) if promotion.maximum_bonus else None,
            'applicable_cryptocurrencies': promotion.applicable_cryptocurrencies,
            'start_date': promotion.start_date.isoformat(),
            'end_date': promotion.end_date.isoformat(),
            'usage_count': promotion.usage_count,
            'max_usage': promotion.max_usage
        } for promotion in promotions]
    })

@app.route('/api/admin/pools', methods=['POST'])
@jwt_required()
def create_staking_pool():
    # Check admin permissions
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.email not in ['admin@tigerex.com']:
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    required_fields = ['pool_name', 'cryptocurrency', 'staking_type', 'apy', 'minimum_stake']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    pool = StakingPool(
        pool_name=data['pool_name'],
        cryptocurrency=data['cryptocurrency'],
        staking_type=data['staking_type'],
        apy=Decimal(str(data['apy'])),
        minimum_stake=Decimal(str(data['minimum_stake'])),
        maximum_stake=Decimal(str(data['maximum_stake'])) if data.get('maximum_stake') else None,
        lock_period_days=data.get('lock_period_days'),
        maximum_capacity=Decimal(str(data['maximum_capacity'])) if data.get('maximum_capacity') else None,
        description=data.get('description'),
        risks=data.get('risks', []),
        rewards_schedule=data.get('rewards_schedule', {'frequency': 'daily'}),
        is_active=data.get('is_active', True)
    )
    
    db.session.add(pool)
    db.session.commit()
    
    return jsonify({
        'message': 'Staking pool created successfully',
        'pool_id': pool.id
    }), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5005, debug=True)