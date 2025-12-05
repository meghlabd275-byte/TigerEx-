#!/usr/bin/env python3
"""
Tiger NFT Service - Unified NFT Platform
Consolidates functionality from 10+ NFT services
Features complete NFT marketplace, launchpad, and management
"""

from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import os
import uuid
import json
from decimal import Decimal
from functools import wraps
from enum import Enum

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/tigerex')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')

db = SQLAlchemy(app)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NFTStatus(Enum):
    DRAFT = "draft"
    MINTED = "minted"
    LISTED = "listed"
    SOLD = "sold"
    BURNED = "burned"

class ListingType(Enum):
    FIXED_PRICE = "fixed_price"
    AUCTION = "auction"
    TIMED_AUCTION = "timed_auction"
    OFFER = "offer"

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    kyc_status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class NFTCollection(db.Model):
    __tablename__ = 'nft_collections'
    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.String(100), unique=True, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(500))
    banner_url = db.Column(db.String(500))
    blockchain = db.Column(db.String(50), nullable=False)
    contract_address = db.Column(db.String(200))
    category = db.Column(db.String(100))
    tags = db.Column(db.JSON, default=list)
    supply = db.Column(db.Integer, default=0)
    minted_count = db.Column(db.Integer, default=0)
    floor_price = db.Column(db.Numeric(20, 8))
    total_volume = db.Column(db.Numeric(20, 8), default=0)
    owner_count = db.Column(db.Integer, default=0)
    is_verified = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    royalty_percentage = db.Column(db.Numeric(5, 2), default=2.5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NFT(db.Model):
    __tablename__ = 'nfts'
    id = db.Column(db.Integer, primary_key=True)
    nft_id = db.Column(db.String(100), unique=True, nullable=False)
    collection_id = db.Column(db.Integer, db.ForeignKey('nft_collections.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token_id = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500), nullable=False)
    image_thumbnail_url = db.Column(db.String(500))
    animation_url = db.Column(db.String(500))
    external_url = db.Column(db.String(500))
    attributes = db.Column(db.JSON, default=list)
    rarity = db.Column(db.String(50))  # 'common', 'rare', 'epic', 'legendary'
    ranking = db.Column(db.Integer)
    mint_number = db.Column(db.Integer)
    mint_price = db.Column(db.Numeric(20, 8))
    last_sale_price = db.Column(db.Numeric(20, 8))
    current_price = db.Column(db.Numeric(20, 8))
    status = db.Column(db.Enum(NFTStatus), default=NFTStatus.DRAFT)
    blockchain = db.Column(db.String(50), nullable=False)
    contract_address = db.Column(db.String(200))
    token_uri = db.Column(db.String(500))
    metadata = db.Column(db.JSON)
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    minted_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NFTListing(db.Model):
    __tablename__ = 'nft_listings'
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.String(100), unique=True, nullable=False)
    nft_id = db.Column(db.Integer, db.ForeignKey('nfts.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    listing_type = db.Column(db.Enum(ListingType), nullable=False)
    price = db.Column(db.Numeric(20, 8))
    starting_price = db.Column(db.Numeric(20, 8))
    reserve_price = db.Column(db.Numeric(20, 8))
    buy_now_price = db.Column(db.Numeric(20, 8))
    auction_end_time = db.Column(db.DateTime)
    highest_bid = db.Column(db.Numeric(20, 8))
    highest_bidder_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    bid_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='active')  # 'active', 'sold', 'cancelled', 'expired'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Bid(db.Model):
    __tablename__ = 'bids'
    id = db.Column(db.Integer, primary_key=True)
    bid_id = db.Column(db.String(100), unique=True, nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('nft_listings.id'), nullable=False)
    bidder_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(20, 8), nullable=False)
    status = db.Column(db.String(20), default='active')  # 'active', 'accepted', 'rejected', 'withdrawn'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class NFTLike(db.Model):
    __tablename__ = 'nft_likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nft_id = db.Column(db.Integer, db.ForeignKey('nfts.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'nft_id'),)

class NFTActivity(db.Model):
    __tablename__ = 'nft_activities'
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.String(100), unique=True, nullable=False)
    nft_id = db.Column(db.Integer, db.ForeignKey('nfts.id'))
    collection_id = db.Column(db.Integer, db.ForeignKey('nft_collections.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # 'mint', 'list', 'sell', 'bid', 'like', 'transfer'
    details = db.Column(db.JSON)
    price = db.Column(db.Numeric(20, 8))
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    blockchain = db.Column(db.String(50))
    transaction_hash = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Launchpad(db.Model):
    __tablename__ = 'launchpads'
    id = db.Column(db.Integer, primary_key=True)
    launchpad_id = db.Column(db.String(100), unique=True, nullable=False)
    collection_id = db.Column(db.Integer, db.ForeignKey('nft_collections.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    website_url = db.Column(db.String(500))
    discord_url = db.Column(db.String(500))
    twitter_url = db.Column(db.String(500))
    phase = db.Column(db.String(50), default='upcoming')  # 'upcoming', 'whitelist', 'public', 'sold_out', 'ended'
    mint_start_time = db.Column(db.DateTime)
    mint_end_time = db.Column(db.DateTime)
    max_supply = db.Column(db.Integer)
    minted_supply = db.Column(db.Integer, default=0)
    mint_price = db.Column(db.Numeric(20, 8))
    max_mint_per_wallet = db.Column(db.Integer, default=5)
    whitelist_enabled = db.Column(db.Boolean, default=False)
    whitelist_users = db.Column(db.JSON, default=list)
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def require_kyc(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.kyc_status != 'verified':
            return jsonify({'error': 'KYC verification required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def log_nft_activity(nft_id, user_id, activity_type, details=None, price=None, collection_id=None):
    activity = NFTActivity(
        activity_id=f"ACT{datetime.utcnow().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}",
        nft_id=nft_id,
        collection_id=collection_id,
        user_id=user_id,
        activity_type=activity_type,
        details=details or {},
        price=price
    )
    db.session.add(activity)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Tiger NFT Service',
        'version': '2.0.0',
        'consolidated_services': 10
    })

# Collections
@app.route('/api/collections', methods=['GET'])
def get_collections():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category = request.args.get('category')
    blockchain = request.args.get('blockchain')
    search = request.args.get('search')
    
    query = NFTCollection.query.filter_by(is_active=True)
    
    if category:
        query = query.filter_by(category=category)
    if blockchain:
        query = query.filter_by(blockchain=blockchain)
    if search:
        query = query.filter(NFTCollection.name.ilike(f'%{search}%'))
    
    collections = query.order_by(NFTCollection.floor_price.desc().nullslast())\
        .paginate(page=page, per_page=per_page)
    
    return jsonify({
        'collections': [{
            'id': collection.id,
            'collection_id': collection.collection_id,
            'name': collection.name,
            'description': collection.description,
            'logo_url': collection.logo_url,
            'banner_url': collection.banner_url,
            'blockchain': collection.blockchain,
            'category': collection.category,
            'tags': collection.tags,
            'supply': collection.supply,
            'minted_count': collection.minted_count,
            'floor_price': float(collection.floor_price) if collection.floor_price else None,
            'total_volume': float(collection.total_volume),
            'owner_count': collection.owner_count,
            'is_verified': collection.is_verified,
            'is_featured': collection.is_featured,
            'royalty_percentage': float(collection.royalty_percentage),
            'created_at': collection.created_at.isoformat()
        } for collection in collections.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': collections.total,
            'pages': collections.pages
        }
    })

@app.route('/api/collections', methods=['POST'])
@jwt_required()
@require_kyc
def create_collection():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['name', 'blockchain']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    collection_id = f"COL{datetime.utcnow().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    
    collection = NFTCollection(
        collection_id=collection_id,
        creator_id=user_id,
        name=data['name'],
        description=data.get('description'),
        logo_url=data.get('logo_url'),
        banner_url=data.get('banner_url'),
        blockchain=data['blockchain'],
        category=data.get('category'),
        tags=data.get('tags', []),
        supply=data.get('supply'),
        royalty_percentage=Decimal(str(data.get('royalty_percentage', 2.5)))
    )
    
    db.session.add(collection)
    db.session.commit()
    
    log_nft_activity(None, user_id, 'collection_created', {
        'collection_id': collection_id,
        'collection_name': data['name']
    }, collection_id=collection.id)
    
    return jsonify({
        'message': 'Collection created successfully',
        'collection_id': collection_id,
        'collection': {
            'id': collection.id,
            'collection_id': collection.collection_id,
            'name': collection.name,
            'blockchain': collection.blockchain,
            'created_at': collection.created_at.isoformat()
        }
    }), 201

# NFTs
@app.route('/api/nfts', methods=['GET'])
def get_nfts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    collection_id = request.args.get('collection_id', type=int)
    category = request.args.get('category')
    status = request.args.get('status')
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'desc')
    
    query = db.session.query(NFT, NFTCollection)\
        .join(NFTCollection, NFT.collection_id == NFTCollection.id)\
        .filter(NFTCollection.is_active == True)
    
    if collection_id:
        query = query.filter(NFT.collection_id == collection_id)
    if status:
        query = query.filter(NFT.status == NFTStatus(status))
    
    # Sorting
    if sort_by == 'price' and order == 'asc':
        query = query.order_by(NFT.current_price.asc().nullslast())
    elif sort_by == 'price' and order == 'desc':
        query = query.order_by(NFT.current_price.desc().nullslast())
    elif sort_by == 'created_at' and order == 'desc':
        query = query.order_by(NFT.created_at.desc())
    else:
        query = query.order_by(NFT.created_at.asc())
    
    nfts = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'nfts': [{
            'id': nft.id,
            'nft_id': nft.nft_id,
            'collection': {
                'id': collection.id,
                'name': collection.name,
                'collection_id': collection.collection_id,
                'logo_url': collection.logo_url,
                'is_verified': collection.is_verified
            },
            'token_id': nft.token_id,
            'name': nft.name,
            'description': nft.description,
            'image_url': nft.image_url,
            'image_thumbnail_url': nft.image_thumbnail_url,
            'attributes': nft.attributes,
            'rarity': nft.rarity,
            'current_price': float(nft.current_price) if nft.current_price else None,
            'last_sale_price': float(nft.last_sale_price) if nft.last_sale_price else None,
            'status': nft.status.value,
            'blockchain': nft.blockchain,
            'view_count': nft.view_count,
            'like_count': nft.like_count,
            'is_featured': nft.is_featured,
            'created_at': nft.created_at.isoformat()
        } for nft, collection in nfts.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': nfts.total,
            'pages': nfts.pages
        }
    })

@app.route('/api/nfts', methods=['POST'])
@jwt_required()
@require_kyc
def mint_nft():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['collection_id', 'name', 'image_url']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Verify collection ownership
    collection = NFTCollection.query.filter_by(
        id=data['collection_id'],
        creator_id=user_id
    ).first()
    
    if not collection:
        return jsonify({'error': 'Collection not found or access denied'}), 404
    
    nft_id = f"NFT{datetime.utcnow().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    token_id = str(uuid.uuid4())
    
    nft = NFT(
        nft_id=nft_id,
        collection_id=data['collection_id'],
        owner_id=user_id,
        creator_id=user_id,
        token_id=token_id,
        name=data['name'],
        description=data.get('description'),
        image_url=data['image_url'],
        image_thumbnail_url=data.get('image_thumbnail_url'),
        animation_url=data.get('animation_url'),
        attributes=data.get('attributes', []),
        rarity=data.get('rarity', 'common'),
        mint_number=collection.minted_count + 1,
        mint_price=Decimal(str(data.get('mint_price', 0))),
        blockchain=collection.blockchain,
        contract_address=collection.contract_address,
        status=NFTStatus.MINTED,
        minted_at=datetime.utcnow()
    )
    
    db.session.add(nft)
    
    # Update collection stats
    collection.minted_count += 1
    if collection.minted_count >= collection.supply:
        collection.supply = collection.minted_count
    
    db.session.commit()
    
    log_nft_activity(nft.id, user_id, 'mint', {
        'token_id': token_id,
        'collection_name': collection.name
    }, price=nft.mint_price, collection_id=collection.id)
    
    return jsonify({
        'message': 'NFT minted successfully',
        'nft_id': nft_id,
        'token_id': token_id,
        'nft': {
            'id': nft.id,
            'nft_id': nft.nft_id,
            'token_id': nft.token_id,
            'name': nft.name,
            'image_url': nft.image_url,
            'status': nft.status.value,
            'minted_at': nft.minted_at.isoformat()
        }
    }), 201

# Listings
@app.route('/api/nfts/<int:nft_id>/list', methods=['POST'])
@jwt_required()
@require_kyc
def list_nft(nft_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    nft = NFT.query.get_or_404(nft_id)
    
    if nft.owner_id != user_id:
        return jsonify({'error': 'Not the owner of this NFT'}), 403
    
    if nft.status != NFTStatus.MINTED:
        return jsonify({'error': 'NFT cannot be listed'}), 400
    
    # Check if already listed
    existing_listing = NFTListing.query.filter_by(
        nft_id=nft_id,
        seller_id=user_id,
        status='active'
    ).first()
    
    if existing_listing:
        return jsonify({'error': 'NFT already listed'}), 400
    
    listing_id = f"LST{datetime.utcnow().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    listing_type = ListingType(data.get('listing_type', 'fixed_price'))
    
    listing = NFTListing(
        listing_id=listing_id,
        nft_id=nft_id,
        seller_id=user_id,
        listing_type=listing_type,
        price=Decimal(str(data['price'])) if listing_type == ListingType.FIXED_PRICE else None,
        starting_price=Decimal(str(data['starting_price'])) if listing_type in [ListingType.AUCTION, ListingType.TIMED_AUCTION] else None,
        reserve_price=Decimal(str(data['reserve_price'])) if data.get('reserve_price') else None,
        auction_end_time=datetime.fromisoformat(data['auction_end_time']) if data.get('auction_end_time') else None
    )
    
    db.session.add(listing)
    
    # Update NFT status
    nft.status = NFTStatus.LISTED
    nft.current_price = listing.price or listing.starting_price
    
    db.session.commit()
    
    log_nft_activity(nft_id, user_id, 'list', {
        'listing_type': listing_type.value,
        'price': float(listing.price) if listing.price else float(listing.starting_price)
    }, price=listing.price or listing.starting_price)
    
    return jsonify({
        'message': 'NFT listed successfully',
        'listing_id': listing_id,
        'listing_type': listing_type.value
    }), 201

@app.route('/api/nfts/<int:nft_id>/buy', methods=['POST'])
@jwt_required()
@require_kyc
def buy_nft(nft_id):
    user_id = get_jwt_identity()
    
    nft = NFT.query.get_or_404(nft_id)
    listing = NFTListing.query.filter_by(
        nft_id=nft_id,
        status='active'
    ).first()
    
    if not listing:
        return jsonify({'error': 'NFT not for sale'}), 400
    
    if listing.seller_id == user_id:
        return jsonify({'error': 'Cannot buy your own NFT'}), 400
    
    if listing.listing_type != ListingType.FIXED_PRICE:
        return jsonify({'error': 'This NFT is in an auction, use bid endpoint'}), 400
    
    # Process purchase
    # In production, this would handle payment and blockchain transaction
    
    # Update ownership
    previous_owner = nft.owner_id
    nft.owner_id = user_id
    nft.status = NFTStatus.SOLD
    nft.last_sale_price = listing.price
    
    # Update listing
    listing.status = 'sold'
    listing.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    # Log activities
    log_nft_activity(nft_id, user_id, 'buy', {
        'from_user_id': previous_owner,
        'price': float(listing.price)
    }, price=listing.price)
    
    log_nft_activity(nft_id, previous_owner, 'sell', {
        'to_user_id': user_id,
        'price': float(listing.price)
    }, price=listing.price)
    
    return jsonify({
        'message': 'NFT purchased successfully',
        'nft_id': nft.nft_id,
        'price': float(listing.price)
    })

@app.route('/api/nfts/<int:nft_id>/bid', methods=['POST'])
@jwt_required()
@require_kyc
def place_bid(nft_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    nft = NFT.query.get_or_404(nft_id)
    listing = NFTListing.query.filter_by(
        nft_id=nft_id,
        status='active'
    ).first()
    
    if not listing or listing.listing_type not in [ListingType.AUCTION, ListingType.TIMED_AUCTION]:
        return jsonify({'error': 'This NFT is not in auction'}), 400
    
    if listing.seller_id == user_id:
        return jsonify({'error': 'Cannot bid on your own NFT'}), 400
    
    bid_amount = Decimal(str(data['amount']))
    
    if listing.highest_bid and bid_amount <= listing.highest_bid:
        return jsonify({'error': 'Bid must be higher than current highest bid'}), 400
    
    if listing.starting_price and bid_amount < listing.starting_price:
        return jsonify({'error': f'Bid must be at least {listing.starting_price}'}, 400)
    
    bid_id = f"BID{datetime.utcnow().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    
    bid = Bid(
        bid_id=bid_id,
        listing_id=listing.id,
        bidder_id=user_id,
        amount=bid_amount
    )
    
    db.session.add(bid)
    
    # Update listing
    listing.highest_bid = bid_amount
    listing.highest_bidder_id = user_id
    listing.bid_count += 1
    listing.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    log_nft_activity(nft_id, user_id, 'bid', {
        'listing_id': listing.listing_id,
        'amount': float(bid_amount)
    }, price=bid_amount)
    
    return jsonify({
        'message': 'Bid placed successfully',
        'bid_id': bid_id,
        'amount': float(bid_amount)
    }), 201

# Launchpad
@app.route('/api/launchpad', methods=['GET'])
def get_launchpad():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    phase = request.args.get('phase')
    
    query = Launchpad.query.filter_by(is_active=True)
    
    if phase:
        query = query.filter_by(phase=phase)
    
    launchpads = query.order_by(Launchpad.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return jsonify({
        'launchpads': [{
            'id': launchpad.id,
            'launchpad_id': launchpad.launchpad_id,
            'project_name': launchpad.project_name,
            'description': launchpad.description,
            'logo_url': launchpad.collection.logo_url if launchpad.collection else None,
            'website_url': launchpad.website_url,
            'phase': launchpad.phase,
            'mint_start_time': launchpad.mint_start_time.isoformat() if launchpad.mint_start_time else None,
            'mint_end_time': launchpad.mint_end_time.isoformat() if launchpad.mint_end_time else None,
            'max_supply': launchpad.max_supply,
            'minted_supply': launchpad.minted_supply,
            'mint_price': float(launchpad.mint_price),
            'max_mint_per_wallet': launchpad.max_mint_per_wallet,
            'whitelist_enabled': launchpad.whitelist_enabled,
            'is_featured': launchpad.is_featured,
            'created_at': launchpad.created_at.isoformat()
        } for launchpad in launchpads.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': launchpads.total,
            'pages': launchpads.pages
        }
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5009, debug=True)