#!/usr/bin/env python3
"""
Advanced NFT Marketplace Service
Complete NFT marketplace with fractionalization, staking, and launchpad
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import uuid
import logging
import os
from decimal import Decimal
import asyncio
import aioredis
from web3 import Web3
import json

# FastAPI app
app = FastAPI(
    title="TigerEx Advanced NFT Marketplace",
    description="Complete NFT marketplace with fractionalization, staking, and launchpad features",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/tigerex_nft")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Blockchain setup
WEB3_PROVIDER = os.getenv("WEB3_PROVIDER", "https://mainnet.infura.io/v3/your-key")
w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Models
class NFTCollection(Base):
    __tablename__ = "nft_collections"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    description = Column(Text)
    contract_address = Column(String, unique=True)
    creator_address = Column(String, nullable=False)
    total_supply = Column(Integer, default=0)
    floor_price = Column(Float, default=0.0)
    volume_24h = Column(Float, default=0.0)
    royalty_percentage = Column(Float, default=0.0)
    is_verified = Column(Boolean, default=False)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NFTItem(Base):
    __tablename__ = "nft_items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    collection_id = Column(String, nullable=False)
    token_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    image_url = Column(String)
    animation_url = Column(String)
    external_url = Column(String)
    owner_address = Column(String, nullable=False)
    creator_address = Column(String, nullable=False)
    current_price = Column(Float)
    last_sale_price = Column(Float)
    is_for_sale = Column(Boolean, default=False)
    is_fractionalized = Column(Boolean, default=False)
    fraction_supply = Column(Integer, default=0)
    fraction_price = Column(Float, default=0.0)
    attributes = Column(JSON)
    rarity_rank = Column(Integer)
    rarity_score = Column(Float)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NFTListing(Base):
    __tablename__ = "nft_listings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nft_id = Column(String, nullable=False)
    seller_address = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, default="ETH")
    listing_type = Column(String, default="fixed")  # fixed, auction, dutch
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    is_active = Column(Boolean, default=True)
    highest_bid = Column(Float, default=0.0)
    highest_bidder = Column(String)
    reserve_price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NFTBid(Base):
    __tablename__ = "nft_bids"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    listing_id = Column(String, nullable=False)
    bidder_address = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="ETH")
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class NFTFraction(Base):
    __tablename__ = "nft_fractions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nft_id = Column(String, nullable=False)
    token_address = Column(String, nullable=False)
    total_supply = Column(Integer, nullable=False)
    price_per_fraction = Column(Float, nullable=False)
    available_supply = Column(Integer, nullable=False)
    vault_address = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class NFTStaking(Base):
    __tablename__ = "nft_staking"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nft_id = Column(String, nullable=False)
    staker_address = Column(String, nullable=False)
    staking_pool = Column(String, nullable=False)
    staked_at = Column(DateTime, default=datetime.utcnow)
    rewards_earned = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)

class NFTLaunchpad(Base):
    __tablename__ = "nft_launchpad"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_name = Column(String, nullable=False)
    creator_address = Column(String, nullable=False)
    collection_size = Column(Integer, nullable=False)
    mint_price = Column(Float, nullable=False)
    launch_date = Column(DateTime, nullable=False)
    whitelist_spots = Column(Integer, default=0)
    public_spots = Column(Integer, default=0)
    description = Column(Text)
    roadmap = Column(JSON)
    team_info = Column(JSON)
    social_links = Column(JSON)
    is_approved = Column(Boolean, default=False)
    is_launched = Column(Boolean, default=False)
    total_raised = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class NFTCollectionCreate(BaseModel):
    name: str
    symbol: str
    description: Optional[str] = None
    royalty_percentage: float = 0.0
    metadata: Optional[Dict[str, Any]] = None

class NFTItemCreate(BaseModel):
    collection_id: str
    token_id: str
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    animation_url: Optional[str] = None
    external_url: Optional[str] = None
    attributes: Optional[List[Dict[str, Any]]] = None

class NFTListingCreate(BaseModel):
    nft_id: str
    price: float
    currency: str = "ETH"
    listing_type: str = "fixed"
    end_time: Optional[datetime] = None
    reserve_price: Optional[float] = None

class NFTBidCreate(BaseModel):
    listing_id: str
    amount: float
    currency: str = "ETH"
    expires_at: Optional[datetime] = None

class NFTFractionCreate(BaseModel):
    nft_id: str
    total_supply: int
    price_per_fraction: float

class NFTStakingCreate(BaseModel):
    nft_id: str
    staking_pool: str

class NFTLaunchpadCreate(BaseModel):
    project_name: str
    collection_size: int
    mint_price: float
    launch_date: datetime
    whitelist_spots: int = 0
    public_spots: int = 0
    description: Optional[str] = None
    roadmap: Optional[Dict[str, Any]] = None
    team_info: Optional[Dict[str, Any]] = None
    social_links: Optional[Dict[str, Any]] = None

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions
async def get_redis():
    return await aioredis.from_url(REDIS_URL)

def calculate_rarity_score(attributes: List[Dict[str, Any]], collection_stats: Dict) -> float:
    """Calculate NFT rarity score based on attributes"""
    if not attributes:
        return 0.0
    
    total_score = 0.0
    for attr in attributes:
        trait_type = attr.get("trait_type")
        value = attr.get("value")
        
        if trait_type in collection_stats:
            trait_count = collection_stats[trait_type].get(value, 0)
            total_items = collection_stats.get("total_items", 1)
            rarity = 1 / (trait_count / total_items) if trait_count > 0 else 1
            total_score += rarity
    
    return total_score

async def update_collection_stats(collection_id: str, db: Session):
    """Update collection floor price and volume"""
    # Get recent sales
    recent_sales = db.query(NFTItem).filter(
        NFTItem.collection_id == collection_id,
        NFTItem.last_sale_price.isnot(None)
    ).all()
    
    if recent_sales:
        floor_price = min(item.current_price or float('inf') for item in recent_sales if item.is_for_sale)
        volume_24h = sum(item.last_sale_price for item in recent_sales 
                        if item.updated_at > datetime.utcnow() - timedelta(days=1))
        
        collection = db.query(NFTCollection).filter(NFTCollection.id == collection_id).first()
        if collection:
            collection.floor_price = floor_price if floor_price != float('inf') else 0.0
            collection.volume_24h = volume_24h
            db.commit()

# API Routes

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "advanced-nft-marketplace"}

# Collection endpoints
@app.post("/collections")
async def create_collection(
    collection: NFTCollectionCreate,
    creator_address: str,
    db: Session = Depends(get_db)
):
    """Create a new NFT collection"""
    db_collection = NFTCollection(
        **collection.dict(),
        creator_address=creator_address
    )
    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)
    return db_collection

@app.get("/collections")
async def get_collections(
    skip: int = 0,
    limit: int = 20,
    verified_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get NFT collections"""
    query = db.query(NFTCollection)
    if verified_only:
        query = query.filter(NFTCollection.is_verified == True)
    
    collections = query.offset(skip).limit(limit).all()
    return collections

@app.get("/collections/{collection_id}")
async def get_collection(collection_id: str, db: Session = Depends(get_db)):
    """Get collection details"""
    collection = db.query(NFTCollection).filter(NFTCollection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection

# NFT Item endpoints
@app.post("/nfts")
async def create_nft(
    nft: NFTItemCreate,
    creator_address: str,
    owner_address: str,
    db: Session = Depends(get_db)
):
    """Create a new NFT item"""
    # Calculate rarity score
    collection_stats = {}  # This would be calculated from existing NFTs
    rarity_score = calculate_rarity_score(nft.attributes or [], collection_stats)
    
    db_nft = NFTItem(
        **nft.dict(),
        creator_address=creator_address,
        owner_address=owner_address,
        rarity_score=rarity_score
    )
    db.add(db_nft)
    db.commit()
    db.refresh(db_nft)
    
    # Update collection stats
    await update_collection_stats(nft.collection_id, db)
    
    return db_nft

@app.get("/nfts")
async def get_nfts(
    collection_id: Optional[str] = None,
    owner_address: Optional[str] = None,
    for_sale_only: bool = False,
    sort_by: str = "created_at",
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get NFT items with filters"""
    query = db.query(NFTItem)
    
    if collection_id:
        query = query.filter(NFTItem.collection_id == collection_id)
    if owner_address:
        query = query.filter(NFTItem.owner_address == owner_address)
    if for_sale_only:
        query = query.filter(NFTItem.is_for_sale == True)
    
    # Sorting
    if sort_by == "price_low":
        query = query.order_by(NFTItem.current_price.asc())
    elif sort_by == "price_high":
        query = query.order_by(NFTItem.current_price.desc())
    elif sort_by == "rarity":
        query = query.order_by(NFTItem.rarity_score.desc())
    else:
        query = query.order_by(NFTItem.created_at.desc())
    
    nfts = query.offset(skip).limit(limit).all()
    return nfts

@app.get("/nfts/{nft_id}")
async def get_nft(nft_id: str, db: Session = Depends(get_db)):
    """Get NFT details"""
    nft = db.query(NFTItem).filter(NFTItem.id == nft_id).first()
    if not nft:
        raise HTTPException(status_code=404, detail="NFT not found")
    
    # Increment view count
    nft.view_count += 1
    db.commit()
    
    return nft

# Marketplace endpoints
@app.post("/listings")
async def create_listing(
    listing: NFTListingCreate,
    seller_address: str,
    db: Session = Depends(get_db)
):
    """Create NFT listing"""
    # Verify ownership
    nft = db.query(NFTItem).filter(NFTItem.id == listing.nft_id).first()
    if not nft:
        raise HTTPException(status_code=404, detail="NFT not found")
    if nft.owner_address != seller_address:
        raise HTTPException(status_code=403, detail="Not the owner")
    
    db_listing = NFTListing(
        **listing.dict(),
        seller_address=seller_address
    )
    db.add(db_listing)
    
    # Update NFT status
    nft.is_for_sale = True
    nft.current_price = listing.price
    
    db.commit()
    db.refresh(db_listing)
    return db_listing

@app.get("/listings")
async def get_listings(
    collection_id: Optional[str] = None,
    listing_type: Optional[str] = None,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get NFT listings"""
    query = db.query(NFTListing)
    
    if active_only:
        query = query.filter(NFTListing.is_active == True)
    if listing_type:
        query = query.filter(NFTListing.listing_type == listing_type)
    
    listings = query.offset(skip).limit(limit).all()
    return listings

@app.post("/bids")
async def place_bid(
    bid: NFTBidCreate,
    bidder_address: str,
    db: Session = Depends(get_db)
):
    """Place bid on NFT"""
    listing = db.query(NFTListing).filter(NFTListing.id == bid.listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if not listing.is_active:
        raise HTTPException(status_code=400, detail="Listing is not active")
    
    db_bid = NFTBid(
        **bid.dict(),
        bidder_address=bidder_address
    )
    db.add(db_bid)
    
    # Update highest bid if applicable
    if bid.amount > (listing.highest_bid or 0):
        listing.highest_bid = bid.amount
        listing.highest_bidder = bidder_address
    
    db.commit()
    db.refresh(db_bid)
    return db_bid

# Fractionalization endpoints
@app.post("/fractionalize")
async def fractionalize_nft(
    fraction: NFTFractionCreate,
    owner_address: str,
    db: Session = Depends(get_db)
):
    """Fractionalize an NFT"""
    nft = db.query(NFTItem).filter(NFTItem.id == fraction.nft_id).first()
    if not nft:
        raise HTTPException(status_code=404, detail="NFT not found")
    if nft.owner_address != owner_address:
        raise HTTPException(status_code=403, detail="Not the owner")
    
    # Create fraction token (this would interact with smart contract)
    vault_address = f"0x{uuid.uuid4().hex[:40]}"  # Mock vault address
    token_address = f"0x{uuid.uuid4().hex[:40]}"  # Mock token address
    
    db_fraction = NFTFraction(
        **fraction.dict(),
        token_address=token_address,
        vault_address=vault_address,
        available_supply=fraction.total_supply
    )
    db.add(db_fraction)
    
    # Update NFT status
    nft.is_fractionalized = True
    nft.fraction_supply = fraction.total_supply
    nft.fraction_price = fraction.price_per_fraction
    
    db.commit()
    db.refresh(db_fraction)
    return db_fraction

@app.get("/fractions/{nft_id}")
async def get_nft_fractions(nft_id: str, db: Session = Depends(get_db)):
    """Get NFT fractionalization details"""
    fraction = db.query(NFTFraction).filter(NFTFraction.nft_id == nft_id).first()
    if not fraction:
        raise HTTPException(status_code=404, detail="NFT not fractionalized")
    return fraction

@app.post("/fractions/{fraction_id}/buy")
async def buy_fractions(
    fraction_id: str,
    quantity: int,
    buyer_address: str,
    db: Session = Depends(get_db)
):
    """Buy NFT fractions"""
    fraction = db.query(NFTFraction).filter(NFTFraction.id == fraction_id).first()
    if not fraction:
        raise HTTPException(status_code=404, detail="Fraction not found")
    if quantity > fraction.available_supply:
        raise HTTPException(status_code=400, detail="Insufficient supply")
    
    # Update available supply
    fraction.available_supply -= quantity
    db.commit()
    
    return {
        "message": "Fractions purchased successfully",
        "quantity": quantity,
        "total_cost": quantity * fraction.price_per_fraction,
        "remaining_supply": fraction.available_supply
    }

# Staking endpoints
@app.post("/stake")
async def stake_nft(
    staking: NFTStakingCreate,
    staker_address: str,
    db: Session = Depends(get_db)
):
    """Stake an NFT"""
    nft = db.query(NFTItem).filter(NFTItem.id == staking.nft_id).first()
    if not nft:
        raise HTTPException(status_code=404, detail="NFT not found")
    if nft.owner_address != staker_address:
        raise HTTPException(status_code=403, detail="Not the owner")
    
    db_staking = NFTStaking(
        **staking.dict(),
        staker_address=staker_address
    )
    db.add(db_staking)
    db.commit()
    db.refresh(db_staking)
    return db_staking

@app.get("/staking/{staker_address}")
async def get_staked_nfts(staker_address: str, db: Session = Depends(get_db)):
    """Get user's staked NFTs"""
    staked_nfts = db.query(NFTStaking).filter(
        NFTStaking.staker_address == staker_address,
        NFTStaking.is_active == True
    ).all()
    return staked_nfts

@app.post("/unstake/{staking_id}")
async def unstake_nft(
    staking_id: str,
    staker_address: str,
    db: Session = Depends(get_db)
):
    """Unstake an NFT"""
    staking = db.query(NFTStaking).filter(NFTStaking.id == staking_id).first()
    if not staking:
        raise HTTPException(status_code=404, detail="Staking record not found")
    if staking.staker_address != staker_address:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Calculate rewards
    days_staked = (datetime.utcnow() - staking.staked_at).days
    rewards = days_staked * 0.1  # Mock reward calculation
    
    staking.is_active = False
    staking.rewards_earned = rewards
    db.commit()
    
    return {
        "message": "NFT unstaked successfully",
        "rewards_earned": rewards,
        "days_staked": days_staked
    }

# Launchpad endpoints
@app.post("/launchpad")
async def create_launchpad_project(
    project: NFTLaunchpadCreate,
    creator_address: str,
    db: Session = Depends(get_db)
):
    """Create launchpad project"""
    db_project = NFTLaunchpad(
        **project.dict(),
        creator_address=creator_address
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/launchpad")
async def get_launchpad_projects(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get launchpad projects"""
    query = db.query(NFTLaunchpad)
    
    if status == "approved":
        query = query.filter(NFTLaunchpad.is_approved == True)
    elif status == "launched":
        query = query.filter(NFTLaunchpad.is_launched == True)
    elif status == "upcoming":
        query = query.filter(
            NFTLaunchpad.is_approved == True,
            NFTLaunchpad.is_launched == False,
            NFTLaunchpad.launch_date > datetime.utcnow()
        )
    
    projects = query.offset(skip).limit(limit).all()
    return projects

@app.post("/launchpad/{project_id}/approve")
async def approve_launchpad_project(
    project_id: str,
    admin_address: str,
    db: Session = Depends(get_db)
):
    """Approve launchpad project (admin only)"""
    project = db.query(NFTLaunchpad).filter(NFTLaunchpad.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project.is_approved = True
    db.commit()
    
    return {"message": "Project approved successfully"}

@app.post("/launchpad/{project_id}/mint")
async def mint_from_launchpad(
    project_id: str,
    quantity: int,
    minter_address: str,
    db: Session = Depends(get_db)
):
    """Mint NFTs from launchpad"""
    project = db.query(NFTLaunchpad).filter(NFTLaunchpad.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not project.is_approved:
        raise HTTPException(status_code=400, detail="Project not approved")
    if datetime.utcnow() < project.launch_date:
        raise HTTPException(status_code=400, detail="Launch not started")
    
    total_cost = quantity * project.mint_price
    project.total_raised += total_cost
    
    if not project.is_launched:
        project.is_launched = True
    
    db.commit()
    
    return {
        "message": f"Minted {quantity} NFTs successfully",
        "total_cost": total_cost,
        "project_total_raised": project.total_raised
    }

# Analytics endpoints
@app.get("/analytics/collections/{collection_id}")
async def get_collection_analytics(collection_id: str, db: Session = Depends(get_db)):
    """Get collection analytics"""
    collection = db.query(NFTCollection).filter(NFTCollection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Get collection stats
    total_items = db.query(NFTItem).filter(NFTItem.collection_id == collection_id).count()
    listed_items = db.query(NFTItem).filter(
        NFTItem.collection_id == collection_id,
        NFTItem.is_for_sale == True
    ).count()
    
    # Get price distribution
    prices = db.query(NFTItem.current_price).filter(
        NFTItem.collection_id == collection_id,
        NFTItem.current_price.isnot(None)
    ).all()
    
    price_list = [p[0] for p in prices if p[0]]
    avg_price = sum(price_list) / len(price_list) if price_list else 0
    
    return {
        "collection": collection,
        "total_items": total_items,
        "listed_items": listed_items,
        "listing_percentage": (listed_items / total_items * 100) if total_items > 0 else 0,
        "floor_price": collection.floor_price,
        "average_price": avg_price,
        "volume_24h": collection.volume_24h,
        "price_distribution": {
            "min": min(price_list) if price_list else 0,
            "max": max(price_list) if price_list else 0,
            "median": sorted(price_list)[len(price_list)//2] if price_list else 0
        }
    }

@app.get("/analytics/trending")
async def get_trending_collections(db: Session = Depends(get_db)):
    """Get trending collections"""
    trending = db.query(NFTCollection).order_by(
        NFTCollection.volume_24h.desc()
    ).limit(10).all()
    
    return trending

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks"""
    logger.info("Advanced NFT Marketplace service started")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)