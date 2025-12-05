#!/usr/bin/env python3

"""
TigerEx Order Sharing Service
Category: social_trading
Description: Share orders with community, copy trades, social trading features
Features: Order sharing, one-click copy, community integration, privacy controls
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
import hashlib
from typing import Dict, List, Optional, Any
from decimal import Decimal
from functools import wraps
from enum import Enum

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/tigerex')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'tiger-order-sharing-secret-key')

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SharePermission(Enum):
    PUBLIC = "public"
    FOLLOWERS = "followers"
    PRIVATE = "private"
    PREMIUM = "premium"

class CopyMode(Enum):
    EXACT = "exact"  # Same quantity
    PROPORTIONAL = "proportional"  # Proportion to portfolio
    FIXED_AMOUNT = "fixed_amount"  # Fixed USD amount

class SharedOrder(db.Model):
    __tablename__ = 'tiger_shared_orders'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    original_order_id = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.String(50), nullable=False)
    
    # Order details
    symbol = db.Column(db.String(20), nullable=False)
    side = db.Column(db.String(4), nullable=False)  # 'buy' or 'sell'
    order_type = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Numeric(20, 8), nullable=False)
    price = db.Column(db.Numeric(20, 8))
    
    # Sharing settings
    permission = db.Column(db.Enum(SharePermission), default=SharePermission.PUBLIC)
    allow_copy = db.Column(db.Boolean, default=True)
    copy_modes = db.Column(db.JSON)  # Allowed copy modes
    max_copy_amount = db.Column(db.Numeric(20, 8))  # Maximum amount others can copy
    min_copy_amount = db.Column(db.Numeric(20, 8))  # Minimum amount others can copy
    
    # Content
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    tags = db.Column(db.JSON)
    chart_image = db.Column(db.String(500))  # URL to chart screenshot
    analysis = db.Column(db.Text)  # Technical analysis reasoning
    
    # Social features
    likes = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    copies = db.Column(db.Integer, default=0)
    comments_enabled = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # Optional expiration
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Performance tracking
    entry_price = db.Column(db.Numeric(20, 8))
    current_price = db.Column(db.Numeric(20, 8))
    pnl = db.Column(db.Numeric(20, 8))
    pnl_percentage = db.Column(db.Numeric(10, 4))
    is_completed = db.Column(db.Boolean, default=False)

class OrderCopy(db.Model):
    __tablename__ = 'tiger_order_copies'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    shared_order_id = db.Column(db.String(50), db.ForeignKey('tiger_shared_orders.id'), nullable=False)
    copier_user_id = db.Column(db.String(50), nullable=False)
    
    # Copy details
    copy_mode = db.Column(db.Enum(CopyMode), nullable=False)
    original_quantity = db.Column(db.Numeric(20, 8))
    copied_quantity = db.Column(db.Numeric(20, 8))
    copy_ratio = db.Column(db.Numeric(10, 6))  # For proportional copies
    
    # Execution details
    copied_order_id = db.Column(db.String(50))  # The actual order ID on exchange
    execution_price = db.Column(db.Numeric(20, 8))
    status = db.Column(db.String(20), default='pending')  # pending, executed, failed, cancelled
    
    # Performance
    entry_price = db.Column(db.Numeric(20, 8))
    exit_price = db.Column(db.Numeric(20, 8))
    pnl = db.Column(db.Numeric(20, 8))
    pnl_percentage = db.Column(db.Numeric(10, 4))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    executed_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    shared_order = db.relationship('SharedOrder', backref='copies')

class UserProfile(db.Model):
    __tablename__ = 'tiger_sharing_profiles'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    
    # Profile settings
    username = db.Column(db.String(50))
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(500))
    banner_url = db.Column(db.String(500))
    
    # Trading stats
    total_orders_shared = db.Column(db.Integer, default=0)
    total_copies_received = db.Column(db.Integer, default=0)
    win_rate = db.Column(db.Numeric(5, 2))  # Percentage
    total_pnl = db.Column(db.Numeric(20, 8))
    followers_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    
    # Social settings
    default_permission = db.Column(db.Enum(SharePermission), default=SharePermission.PUBLIC)
    allow_anonymous_copies = db.Column(db.Boolean, default=True)
    auto_approve_followers = db.Column(db.Boolean, default=True)
    
    # Badge system
    badges = db.Column(db.JSON)  # Achievement badges
    reputation_score = db.Column(db.Integer, default=0)
    
    # Subscription settings
    is_premium = db.Column(db.Boolean, default=False)
    premium_expires_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Follow(db.Model):
    __tablename__ = 'tiger_follows'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    follower_id = db.Column(db.String(50), nullable=False)
    following_id = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Composite unique constraint to prevent duplicate follows
    __table_args__ = (
        db.UniqueConstraint('follower_id', 'following_id', name='unique_follow'),
    )

class Comment(db.Model):
    __tablename__ = 'tiger_shared_order_comments'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    shared_order_id = db.Column(db.String(50), db.ForeignKey('tiger_shared_orders.id'), nullable=False)
    user_id = db.Column(db.String(50), nullable=False)
    
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.String(50), db.ForeignKey('tiger_shared_order_comments.id'))  # For replies
    
    # Engagement
    likes = db.Column(db.Integer, default=0)
    is_pinned = db.Column(db.Boolean, default=False)
    
    # Status
    is_deleted = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    shared_order = db.relationship('SharedOrder', backref='comments')
    parent = db.relationship('Comment', remote_side=[id], backref='replies')

# Helper functions
def get_or_create_profile(user_id):
    """Get or create user profile"""
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.session.add(profile)
        db.session.commit()
    return profile

def generate_share_link(shared_order_id):
    """Generate shareable link for order"""
    base_url = os.getenv('BASE_URL', 'https://tigerex.com')
    share_code = hashlib.md5(f"{shared_order_id}{datetime.utcnow().isoformat()}".encode()).hexdigest()[:8]
    return f"{base_url}/shared/{share_code}"

def check_permission(shared_order, user_id):
    """Check if user has permission to view shared order"""
    if shared_order.permission == SharePermission.PUBLIC:
        return True
    
    if shared_order.permission == SharePermission.PRIVATE:
        return shared_order.user_id == user_id
    
    if shared_order.permission == SharePermission.FOLLOWERS:
        follow = Follow.query.filter_by(
            follower_id=user_id,
            following_id=shared_order.user_id
        ).first()
        return follow is not None
    
    if shared_order.permission == SharePermission.PREMIUM:
        profile = get_or_create_profile(user_id)
        return profile.is_premium
    
    return False

# API Routes
@app.route('/api/v1/orders/share', methods=['POST'])
@jwt_required()
def share_order():
    """Share an order with the community"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['original_order_id', 'symbol', 'side', 'order_type', 'quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        shared_order = SharedOrder(
            original_order_id=data['original_order_id'],
            user_id=user_id,
            symbol=data['symbol'],
            side=data['side'],
            order_type=data['order_type'],
            quantity=data['quantity'],
            price=data.get('price'),
            permission=SharePermission(data.get('permission', 'public')),
            allow_copy=data.get('allow_copy', True),
            copy_modes=data.get('copy_modes', ['exact', 'proportional']),
            max_copy_amount=data.get('max_copy_amount'),
            min_copy_amount=data.get('min_copy_amount'),
            title=data.get('title'),
            description=data.get('description'),
            tags=data.get('tags', []),
            chart_image=data.get('chart_image'),
            analysis=data.get('analysis'),
            comments_enabled=data.get('comments_enabled', True),
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None,
            entry_price=data.get('entry_price'),
            current_price=data.get('current_price')
        )
        
        db.session.add(shared_order)
        db.session.commit()
        
        # Update user profile stats
        profile = get_or_create_profile(user_id)
        profile.total_orders_shared += 1
        db.session.commit()
        
        # Generate share link
        share_link = generate_share_link(shared_order.id)
        
        return jsonify({
            'success': True,
            'shared_order_id': shared_order.id,
            'share_link': share_link,
            'permission': shared_order.permission.value
        })
        
    except Exception as e:
        logger.error(f"Error sharing order: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/shared-orders/<shared_order_id>', methods=['GET'])
@jwt_required()
def get_shared_order(shared_order_id):
    """Get shared order details"""
    try:
        user_id = get_jwt_identity()
        shared_order = SharedOrder.query.filter_by(id=shared_order_id, is_active=True).first()
        
        if not shared_order:
            return jsonify({'success': False, 'error': 'Shared order not found'}), 404
        
        # Check permission
        if not check_permission(shared_order, user_id):
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        
        # Increment view count
        shared_order.views += 1
        db.session.commit()
        
        # Get user profile
        profile = get_or_create_profile(shared_order.user_id)
        
        # Check if current user follows this user
        is_following = Follow.query.filter_by(
            follower_id=user_id,
            following_id=shared_order.user_id
        ).first() is not None
        
        # Check if current user has copied this order
        has_copied = OrderCopy.query.filter_by(
            shared_order_id=shared_order_id,
            copier_user_id=user_id
        ).first() is not None
        
        return jsonify({
            'success': True,
            'shared_order': {
                'id': shared_order.id,
                'symbol': shared_order.symbol,
                'side': shared_order.side,
                'order_type': shared_order.order_type,
                'quantity': str(shared_order.quantity),
                'price': str(shared_order.price) if shared_order.price else None,
                'title': shared_order.title,
                'description': shared_order.description,
                'tags': shared_order.tags,
                'chart_image': shared_order.chart_image,
                'analysis': shared_order.analysis,
                'permission': shared_order.permission.value,
                'allow_copy': shared_order.allow_copy,
                'copy_modes': shared_order.copy_modes,
                'max_copy_amount': str(shared_order.max_copy_amount) if shared_order.max_copy_amount else None,
                'min_copy_amount': str(shared_order.min_copy_amount) if shared_order.min_copy_amount else None,
                'likes': shared_order.likes,
                'views': shared_order.views,
                'copies': shared_order.copies,
                'comments_enabled': shared_order.comments_enabled,
                'created_at': shared_order.created_at.isoformat(),
                'is_completed': shared_order.is_completed,
                'entry_price': str(shared_order.entry_price) if shared_order.entry_price else None,
                'current_price': str(shared_order.current_price) if shared_order.current_price else None,
                'pnl': str(shared_order.pnl) if shared_order.pnl else None,
                'pnl_percentage': str(shared_order.pnl_percentage) if shared_order.pnl_percentage else None
            },
            'author': {
                'user_id': profile.user_id,
                'username': profile.username,
                'avatar_url': profile.avatar_url,
                'total_orders_shared': profile.total_orders_shared,
                'total_copies_received': profile.total_copies_received,
                'win_rate': str(profile.win_rate) if profile.win_rate else None,
                'followers_count': profile.followers_count,
                'badges': profile.badges or [],
                'reputation_score': profile.reputation_score
            },
            'user_interaction': {
                'is_following': is_following,
                'has_copied': has_copied
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting shared order: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/shared-orders/<shared_order_id>/copy', methods=['POST'])
@jwt_required()
def copy_shared_order(shared_order_id):
    """Copy a shared order"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        shared_order = SharedOrder.query.filter_by(id=shared_order_id, is_active=True).first()
        
        if not shared_order:
            return jsonify({'success': False, 'error': 'Shared order not found'}), 404
        
        # Check if copying is allowed
        if not shared_order.allow_copy:
            return jsonify({'success': False, 'error': 'Copying not allowed for this order'}), 403
        
        # Check permission
        if not check_permission(shared_order, user_id):
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        
        # Check if already copied
        existing_copy = OrderCopy.query.filter_by(
            shared_order_id=shared_order_id,
            copier_user_id=user_id,
            status='pending'
        ).first()
        
        if existing_copy:
            return jsonify({'success': False, 'error': 'Order already copied'}), 400
        
        # Validate copy mode
        copy_mode = CopyMode(data.get('copy_mode', 'exact'))
        if copy_mode.value not in shared_order.copy_modes:
            return jsonify({'success': False, 'error': 'Copy mode not allowed'}), 400
        
        # Calculate copy quantity
        copy_quantity = Decimal('0')
        
        if copy_mode == CopyMode.EXACT:
            copy_quantity = shared_order.quantity
        
        elif copy_mode == CopyMode.PROPORTIONAL:
            copy_ratio = Decimal(str(data.get('copy_ratio', '0.1')))  # Default 10%
            copy_quantity = shared_order.quantity * copy_ratio
        
        elif copy_mode == CopyMode.FIXED_AMOUNT:
            fixed_amount = Decimal(str(data.get('fixed_amount')))
            if shared_order.price:
                copy_quantity = fixed_amount / shared_order.price
            else:
                return jsonify({'success': False, 'error': 'Cannot calculate quantity for fixed amount without price'}), 400
        
        # Check min/max copy limits
        if shared_order.min_copy_amount and copy_quantity < shared_order.min_copy_amount:
            return jsonify({'success': False, 'error': 'Copy amount below minimum'}), 400
        
        if shared_order.max_copy_amount and copy_quantity > shared_order.max_copy_amount:
            return jsonify({'success': False, 'error': 'Copy amount above maximum'}), 400
        
        # Create copy record
        order_copy = OrderCopy(
            shared_order_id=shared_order_id,
            copier_user_id=user_id,
            copy_mode=copy_mode,
            original_quantity=shared_order.quantity,
            copied_quantity=copy_quantity,
            copy_ratio=Decimal(str(data.get('copy_ratio', '0'))) if copy_mode == CopyMode.PROPORTIONAL else None
        )
        
        db.session.add(order_copy)
        db.session.commit()
        
        # Update shared order stats
        shared_order.copies += 1
        
        # Update author profile stats
        profile = get_or_create_profile(shared_order.user_id)
        profile.total_copies_received += 1
        db.session.commit()
        
        # Here you would integrate with your trading engine to place the actual order
        # For now, we'll simulate order placement
        order_copy.status = 'executed'
        order_copy.executed_at = datetime.utcnow()
        order_copy.execution_price = shared_order.price
        order_copy.entry_price = shared_order.price
        db.session.commit()
        
        return jsonify({
            'success': True,
            'copy_id': order_copy.id,
            'copied_quantity': str(copy_quantity),
            'copy_mode': copy_mode.value,
            'status': order_copy.status
        })
        
    except Exception as e:
        logger.error(f"Error copying shared order: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/shared-orders', methods=['GET'])
@jwt_required()
def list_shared_orders():
    """List shared orders with filters"""
    try:
        user_id = get_jwt_identity()
        
        # Query parameters
        symbol = request.args.get('symbol')
        side = request.args.get('side')
        permission = request.args.get('permission')
        tags = request.args.getlist('tags')
        featured = request.args.get('featured', '').lower() == 'true'
        user_filter = request.args.get('user_id')  # Filter by specific user
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        sort_by = request.args.get('sort_by', 'created_at')  # created_at, likes, copies, views
        sort_order = request.args.get('sort_order', 'desc')
        
        # Build query
        query = SharedOrder.query.filter_by(is_active=True)
        
        # Apply filters
        if symbol:
            query = query.filter_by(symbol=symbol.upper())
        
        if side:
            query = query.filter_by(side=side.lower())
        
        if permission:
            query = query.filter_by(permission=SharePermission(permission))
        
        if tags:
            query = query.filter(SharedOrder.tags.contains(tags))
        
        if featured:
            query = query.filter_by(is_featured=True)
        
        if user_filter:
            query = query.filter_by(user_id=user_filter)
        
        # Filter by permission visibility
        # Only show orders user can see
        public_orders = query.filter(SharedOrder.permission == SharePermission.PUBLIC).subquery()
        
        # Add follower orders if applicable
        follower_subquery = db.session.query(SharedOrder.id).join(
            Follow, SharedOrder.user_id == Follow.following_id
        ).filter(
            Follow.follower_id == user_id,
            SharedOrder.permission == SharePermission.FOLLOWERS
        ).subquery()
        
        # Get IDs user can access
        accessible_ids = db.session.query(public_orders.c.id).union(
            follower_subquery
        ).all()
        
        accessible_ids = [row[0] for row in accessible_ids]
        query = SharedOrder.query.filter(SharedOrder.id.in_(accessible_ids))
        
        # Apply sorting
        if sort_by == 'created_at':
            order_column = SharedOrder.created_at
        elif sort_by == 'likes':
            order_column = SharedOrder.likes
        elif sort_by == 'copies':
            order_column = SharedOrder.copies
        elif sort_by == 'views':
            order_column = SharedOrder.views
        else:
            order_column = SharedOrder.created_at
        
        if sort_order == 'asc':
            query = query.order_by(order_column.asc())
        else:
            query = query.order_by(order_column.desc())
        
        # Paginate
        orders = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Load profiles for authors
        author_ids = [order.user_id for order in orders.items]
        profiles = {p.user_id: p for p in UserProfile.query.filter(UserProfile.user_id.in_(author_ids)).all()}
        
        return jsonify({
            'success': True,
            'orders': [{
                'id': order.id,
                'symbol': order.symbol,
                'side': order.side,
                'order_type': order.order_type,
                'quantity': str(order.quantity),
                'price': str(order.price) if order.price else None,
                'title': order.title,
                'tags': order.tags,
                'likes': order.likes,
                'views': order.views,
                'copies': order.copies,
                'permission': order.permission.value,
                'created_at': order.created_at.isoformat(),
                'author': {
                    'user_id': order.user_id,
                    'username': profiles.get(order.user_id, UserProfile()).username,
                    'avatar_url': profiles.get(order.user_id, UserProfile()).avatar_url,
                    'followers_count': profiles.get(order.user_id, UserProfile()).followers_count
                }
            } for order in orders.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': orders.total,
                'pages': orders.pages
            }
        })
        
    except Exception as e:
        logger.error(f"Error listing shared orders: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/shared-orders/<shared_order_id>/like', methods=['POST'])
@jwt_required()
def like_shared_order(shared_order_id):
    """Like/unlike a shared order"""
    try:
        user_id = get_jwt_identity()
        shared_order = SharedOrder.query.filter_by(id=shared_order_id, is_active=True).first()
        
        if not shared_order:
            return jsonify({'success': False, 'error': 'Shared order not found'}), 404
        
        # Check permission
        if not check_permission(shared_order, user_id):
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        
        # This would typically use a separate likes table, but for simplicity:
        # In production, you'd want to track which users liked which orders
        # For now, we'll just increment the like count (this is not ideal)
        
        shared_order.likes += 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'likes': shared_order.likes
        })
        
    except Exception as e:
        logger.error(f"Error liking shared order: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/users/<user_id>/follow', methods=['POST'])
@jwt_required()
def follow_user(user_id):
    """Follow a user"""
    try:
        follower_id = get_jwt_identity()
        
        if follower_id == user_id:
            return jsonify({'success': False, 'error': 'Cannot follow yourself'}), 400
        
        # Check if already following
        existing_follow = Follow.query.filter_by(
            follower_id=follower_id,
            following_id=user_id
        ).first()
        
        if existing_follow:
            return jsonify({'success': False, 'error': 'Already following'}), 400
        
        # Create follow relationship
        follow = Follow(follower_id=follower_id, following_id=user_id)
        db.session.add(follow)
        
        # Update profile counts
        follower_profile = get_or_create_profile(follower_id)
        following_profile = get_or_create_profile(user_id)
        
        follower_profile.following_count += 1
        following_profile.followers_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'is_following': True,
            'followers_count': following_profile.followers_count
        })
        
    except Exception as e:
        logger.error(f"Error following user: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/users/<user_id>/unfollow', methods=['DELETE'])
@jwt_required()
def unfollow_user(user_id):
    """Unfollow a user"""
    try:
        follower_id = get_jwt_identity()
        
        follow = Follow.query.filter_by(
            follower_id=follower_id,
            following_id=user_id
        ).first()
        
        if not follow:
            return jsonify({'success': False, 'error': 'Not following'}), 400
        
        db.session.delete(follow)
        
        # Update profile counts
        follower_profile = get_or_create_profile(follower_id)
        following_profile = get_or_create_profile(user_id)
        
        follower_profile.following_count = max(0, follower_profile.following_count - 1)
        following_profile.followers_count = max(0, following_profile.followers_count - 1)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'is_following': False,
            'followers_count': following_profile.followers_count
        })
        
    except Exception as e:
        logger.error(f"Error unfollowing user: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    try:
        user_id = get_jwt_identity()
        profile = get_or_create_profile(user_id)
        
        return jsonify({
            'success': True,
            'profile': {
                'user_id': profile.user_id,
                'username': profile.username,
                'bio': profile.bio,
                'avatar_url': profile.avatar_url,
                'banner_url': profile.banner_url,
                'total_orders_shared': profile.total_orders_shared,
                'total_copies_received': profile.total_copies_received,
                'win_rate': str(profile.win_rate) if profile.win_rate else None,
                'total_pnl': str(profile.total_pnl) if profile.total_pnl else None,
                'followers_count': profile.followers_count,
                'following_count': profile.following_count,
                'default_permission': profile.default_permission.value,
                'allow_anonymous_copies': profile.allow_anonymous_copies,
                'auto_approve_followers': profile.auto_approve_followers,
                'badges': profile.badges or [],
                'reputation_score': profile.reputation_score,
                'is_premium': profile.is_premium,
                'premium_expires_at': profile.premium_expires_at.isoformat() if profile.premium_expires_at else None
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        profile = get_or_create_profile(user_id)
        
        # Update allowed fields
        updatable_fields = [
            'username', 'bio', 'avatar_url', 'banner_url',
            'default_permission', 'allow_anonymous_copies', 'auto_approve_followers'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field == 'default_permission':
                    setattr(profile, field, SharePermission(data[field]))
                else:
                    setattr(profile, field, data[field])
        
        profile.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'profile': {
                'user_id': profile.user_id,
                'username': profile.username,
                'bio': profile.bio,
                'avatar_url': profile.avatar_url,
                'banner_url': profile.banner_url,
                'default_permission': profile.default_permission.value,
                'allow_anonymous_copies': profile.allow_anonymous_copies,
                'auto_approve_followers': profile.auto_approve_followers
            }
        })
        
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(host='0.0.0.0', port=5005, debug=True)