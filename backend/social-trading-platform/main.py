#!/usr/bin/env python3
"""
Social Trading Platform Service
Complete social trading with influencer partnerships, copy trading, and social features
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
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
import json
from collections import defaultdict

# FastAPI app
app = FastAPI(
    title="TigerEx Social Trading Platform",
    description="Complete social trading platform with influencer partnerships and copy trading",
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
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/tigerex_social")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_connections[user_id] = websocket

    def disconnect(self, websocket: WebSocket, user_id: str):
        self.active_connections.remove(websocket)
        if user_id in self.user_connections:
            del self.user_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.user_connections:
            await self.user_connections[user_id].send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Database Models
class SocialTrader(Base):
    __tablename__ = "social_traders"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    display_name = Column(String, nullable=False)
    bio = Column(Text)
    avatar_url = Column(String)
    is_verified = Column(Boolean, default=False)
    is_influencer = Column(Boolean, default=False)
    is_professional = Column(Boolean, default=False)
    tier = Column(String, default="bronze")  # bronze, silver, gold, platinum, diamond
    
    # Trading stats
    total_pnl = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    avg_holding_time = Column(Float, default=0.0)  # in hours
    max_drawdown = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    
    # Social stats
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    copiers_count = Column(Integer, default=0)
    posts_count = Column(Integer, default=0)
    likes_received = Column(Integer, default=0)
    
    # Copy trading settings
    is_copyable = Column(Boolean, default=False)
    copy_fee_percentage = Column(Float, default=0.0)
    min_copy_amount = Column(Float, default=100.0)
    max_copiers = Column(Integer, default=1000)
    
    # Influencer settings
    partnership_tier = Column(String)  # bronze, silver, gold, platinum
    commission_rate = Column(Float, default=0.0)
    referral_code = Column(String, unique=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SocialPost(Base):
    __tablename__ = "social_posts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    trader_id = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    post_type = Column(String, default="text")  # text, image, video, trade_idea, analysis
    media_urls = Column(JSON)
    
    # Trade-related data
    symbol = Column(String)
    entry_price = Column(Float)
    target_price = Column(Float)
    stop_loss = Column(Float)
    trade_direction = Column(String)  # long, short
    confidence_level = Column(Integer)  # 1-10
    
    # Engagement
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    
    # Visibility
    is_public = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SocialFollow(Base):
    __tablename__ = "social_follows"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    follower_id = Column(String, nullable=False)
    following_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class CopyTrade(Base):
    __tablename__ = "copy_trades"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    copier_id = Column(String, nullable=False)
    trader_id = Column(String, nullable=False)
    
    # Copy settings
    copy_amount = Column(Float, nullable=False)
    copy_percentage = Column(Float, default=100.0)  # Percentage of trader's position to copy
    max_risk_per_trade = Column(Float, default=5.0)  # Max % of portfolio per trade
    
    # Status
    is_active = Column(Boolean, default=True)
    auto_copy = Column(Boolean, default=True)
    
    # Stats
    total_copied_trades = Column(Integer, default=0)
    total_pnl = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CopyTradeExecution(Base):
    __tablename__ = "copy_trade_executions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    copy_trade_id = Column(String, nullable=False)
    original_trade_id = Column(String, nullable=False)
    copied_trade_id = Column(String, nullable=False)
    
    # Trade details
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)  # buy, sell
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float)
    
    # Performance
    pnl = Column(Float, default=0.0)
    pnl_percentage = Column(Float, default=0.0)
    
    # Status
    status = Column(String, default="open")  # open, closed, cancelled
    
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime)

class SocialComment(Base):
    __tablename__ = "social_comments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = Column(String, nullable=False)
    commenter_id = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    parent_comment_id = Column(String)  # For replies
    
    likes_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SocialLike(Base):
    __tablename__ = "social_likes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    target_id = Column(String, nullable=False)  # post_id or comment_id
    target_type = Column(String, nullable=False)  # post, comment
    created_at = Column(DateTime, default=datetime.utcnow)

class TradingSignal(Base):
    __tablename__ = "trading_signals"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    trader_id = Column(String, nullable=False)
    
    # Signal details
    symbol = Column(String, nullable=False)
    signal_type = Column(String, nullable=False)  # buy, sell, hold
    entry_price = Column(Float, nullable=False)
    target_prices = Column(JSON)  # Multiple targets
    stop_loss = Column(Float)
    confidence = Column(Integer, default=5)  # 1-10
    
    # Analysis
    analysis = Column(Text)
    timeframe = Column(String)  # 1m, 5m, 15m, 1h, 4h, 1d
    
    # Performance tracking
    hit_rate = Column(Float, default=0.0)
    avg_return = Column(Float, default=0.0)
    
    # Visibility
    is_premium = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

class InfluencerPartnership(Base):
    __tablename__ = "influencer_partnerships"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    trader_id = Column(String, nullable=False)
    
    # Partnership details
    tier = Column(String, nullable=False)  # bronze, silver, gold, platinum
    commission_rate = Column(Float, nullable=False)
    min_followers = Column(Integer, default=0)
    
    # Performance requirements
    min_win_rate = Column(Float, default=0.0)
    min_monthly_volume = Column(Float, default=0.0)
    
    # Benefits
    benefits = Column(JSON)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

class SocialLeaderboard(Base):
    __tablename__ = "social_leaderboards"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    trader_id = Column(String, nullable=False)
    
    # Leaderboard categories
    category = Column(String, nullable=False)  # pnl, win_rate, followers, copiers
    period = Column(String, nullable=False)  # daily, weekly, monthly, all_time
    
    # Metrics
    value = Column(Float, nullable=False)
    rank = Column(Integer, nullable=False)
    
    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class SocialTraderCreate(BaseModel):
    user_id: str
    username: str
    display_name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class SocialTraderUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_copyable: Optional[bool] = None
    copy_fee_percentage: Optional[float] = None
    min_copy_amount: Optional[float] = None
    max_copiers: Optional[int] = None

class SocialPostCreate(BaseModel):
    content: str
    post_type: str = "text"
    media_urls: Optional[List[str]] = None
    symbol: Optional[str] = None
    entry_price: Optional[float] = None
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    trade_direction: Optional[str] = None
    confidence_level: Optional[int] = None
    is_premium: bool = False

class CopyTradeCreate(BaseModel):
    trader_id: str
    copy_amount: float
    copy_percentage: float = 100.0
    max_risk_per_trade: float = 5.0
    auto_copy: bool = True

class SocialCommentCreate(BaseModel):
    post_id: str
    content: str
    parent_comment_id: Optional[str] = None

class TradingSignalCreate(BaseModel):
    symbol: str
    signal_type: str
    entry_price: float
    target_prices: List[float]
    stop_loss: Optional[float] = None
    confidence: int = 5
    analysis: Optional[str] = None
    timeframe: str = "1h"
    is_premium: bool = False
    expires_at: Optional[datetime] = None

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

def calculate_trader_stats(trader_id: str, db: Session) -> Dict[str, float]:
    """Calculate comprehensive trader statistics"""
    # This would integrate with the trading engine to get actual trade data
    # For now, returning mock data
    return {
        "total_pnl": 15420.50,
        "win_rate": 68.5,
        "total_trades": 156,
        "winning_trades": 107,
        "avg_holding_time": 24.5,
        "max_drawdown": -8.2,
        "sharpe_ratio": 1.85
    }

def update_leaderboards(db: Session):
    """Update all leaderboards"""
    categories = ["pnl", "win_rate", "followers", "copiers"]
    periods = ["daily", "weekly", "monthly", "all_time"]
    
    for category in categories:
        for period in periods:
            # Clear existing leaderboard
            db.query(SocialLeaderboard).filter(
                SocialLeaderboard.category == category,
                SocialLeaderboard.period == period
            ).delete()
            
            # Calculate new rankings
            if category == "pnl":
                traders = db.query(SocialTrader).order_by(SocialTrader.total_pnl.desc()).limit(100).all()
                for rank, trader in enumerate(traders, 1):
                    leaderboard_entry = SocialLeaderboard(
                        trader_id=trader.id,
                        category=category,
                        period=period,
                        value=trader.total_pnl,
                        rank=rank
                    )
                    db.add(leaderboard_entry)
            
            elif category == "win_rate":
                traders = db.query(SocialTrader).filter(
                    SocialTrader.total_trades > 10
                ).order_by(SocialTrader.win_rate.desc()).limit(100).all()
                for rank, trader in enumerate(traders, 1):
                    leaderboard_entry = SocialLeaderboard(
                        trader_id=trader.id,
                        category=category,
                        period=period,
                        value=trader.win_rate,
                        rank=rank
                    )
                    db.add(leaderboard_entry)
            
            elif category == "followers":
                traders = db.query(SocialTrader).order_by(SocialTrader.followers_count.desc()).limit(100).all()
                for rank, trader in enumerate(traders, 1):
                    leaderboard_entry = SocialLeaderboard(
                        trader_id=trader.id,
                        category=category,
                        period=period,
                        value=trader.followers_count,
                        rank=rank
                    )
                    db.add(leaderboard_entry)
            
            elif category == "copiers":
                traders = db.query(SocialTrader).order_by(SocialTrader.copiers_count.desc()).limit(100).all()
                for rank, trader in enumerate(traders, 1):
                    leaderboard_entry = SocialLeaderboard(
                        trader_id=trader.id,
                        category=category,
                        period=period,
                        value=trader.copiers_count,
                        rank=rank
                    )
                    db.add(leaderboard_entry)
    
    db.commit()

# API Routes

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "social-trading-platform"}

# WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle real-time messages
            await manager.broadcast(f"User {user_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

# Trader endpoints
@app.post("/traders")
async def create_trader(trader: SocialTraderCreate, db: Session = Depends(get_db)):
    """Create social trader profile"""
    # Check if trader already exists
    existing = db.query(SocialTrader).filter(SocialTrader.user_id == trader.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Trader profile already exists")
    
    db_trader = SocialTrader(**trader.dict())
    db.add(db_trader)
    db.commit()
    db.refresh(db_trader)
    return db_trader

@app.get("/traders/{trader_id}")
async def get_trader(trader_id: str, db: Session = Depends(get_db)):
    """Get trader profile"""
    trader = db.query(SocialTrader).filter(SocialTrader.id == trader_id).first()
    if not trader:
        raise HTTPException(status_code=404, detail="Trader not found")
    
    # Update stats
    stats = calculate_trader_stats(trader_id, db)
    for key, value in stats.items():
        setattr(trader, key, value)
    db.commit()
    
    return trader

@app.put("/traders/{trader_id}")
async def update_trader(
    trader_id: str,
    trader_update: SocialTraderUpdate,
    db: Session = Depends(get_db)
):
    """Update trader profile"""
    trader = db.query(SocialTrader).filter(SocialTrader.id == trader_id).first()
    if not trader:
        raise HTTPException(status_code=404, detail="Trader not found")
    
    for key, value in trader_update.dict(exclude_unset=True).items():
        setattr(trader, key, value)
    
    db.commit()
    db.refresh(trader)
    return trader

@app.get("/traders")
async def get_traders(
    sort_by: str = "followers",
    verified_only: bool = False,
    influencers_only: bool = False,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get traders with filters"""
    query = db.query(SocialTrader)
    
    if verified_only:
        query = query.filter(SocialTrader.is_verified == True)
    if influencers_only:
        query = query.filter(SocialTrader.is_influencer == True)
    
    # Sorting
    if sort_by == "followers":
        query = query.order_by(SocialTrader.followers_count.desc())
    elif sort_by == "pnl":
        query = query.order_by(SocialTrader.total_pnl.desc())
    elif sort_by == "win_rate":
        query = query.order_by(SocialTrader.win_rate.desc())
    elif sort_by == "copiers":
        query = query.order_by(SocialTrader.copiers_count.desc())
    else:
        query = query.order_by(SocialTrader.created_at.desc())
    
    traders = query.offset(skip).limit(limit).all()
    return traders

# Follow system
@app.post("/follow/{trader_id}")
async def follow_trader(
    trader_id: str,
    follower_id: str,
    db: Session = Depends(get_db)
):
    """Follow a trader"""
    # Check if already following
    existing = db.query(SocialFollow).filter(
        SocialFollow.follower_id == follower_id,
        SocialFollow.following_id == trader_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already following this trader")
    
    # Create follow relationship
    follow = SocialFollow(follower_id=follower_id, following_id=trader_id)
    db.add(follow)
    
    # Update counts
    trader = db.query(SocialTrader).filter(SocialTrader.id == trader_id).first()
    follower = db.query(SocialTrader).filter(SocialTrader.id == follower_id).first()
    
    if trader:
        trader.followers_count += 1
    if follower:
        follower.following_count += 1
    
    db.commit()
    
    # Send real-time notification
    await manager.send_personal_message(
        json.dumps({
            "type": "new_follower",
            "follower_id": follower_id,
            "message": f"You have a new follower!"
        }),
        trader_id
    )
    
    return {"message": "Successfully followed trader"}

@app.delete("/unfollow/{trader_id}")
async def unfollow_trader(
    trader_id: str,
    follower_id: str,
    db: Session = Depends(get_db)
):
    """Unfollow a trader"""
    follow = db.query(SocialFollow).filter(
        SocialFollow.follower_id == follower_id,
        SocialFollow.following_id == trader_id
    ).first()
    
    if not follow:
        raise HTTPException(status_code=404, detail="Not following this trader")
    
    db.delete(follow)
    
    # Update counts
    trader = db.query(SocialTrader).filter(SocialTrader.id == trader_id).first()
    follower = db.query(SocialTrader).filter(SocialTrader.id == follower_id).first()
    
    if trader:
        trader.followers_count = max(0, trader.followers_count - 1)
    if follower:
        follower.following_count = max(0, follower.following_count - 1)
    
    db.commit()
    return {"message": "Successfully unfollowed trader"}

@app.get("/traders/{trader_id}/followers")
async def get_followers(
    trader_id: str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get trader's followers"""
    followers = db.query(SocialFollow).filter(
        SocialFollow.following_id == trader_id
    ).offset(skip).limit(limit).all()
    
    return followers

@app.get("/traders/{trader_id}/following")
async def get_following(
    trader_id: str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get who trader is following"""
    following = db.query(SocialFollow).filter(
        SocialFollow.follower_id == trader_id
    ).offset(skip).limit(limit).all()
    
    return following

# Posts and social feed
@app.post("/posts")
async def create_post(
    post: SocialPostCreate,
    trader_id: str,
    db: Session = Depends(get_db)
):
    """Create social post"""
    db_post = SocialPost(**post.dict(), trader_id=trader_id)
    db.add(db_post)
    
    # Update trader's post count
    trader = db.query(SocialTrader).filter(SocialTrader.id == trader_id).first()
    if trader:
        trader.posts_count += 1
    
    db.commit()
    db.refresh(db_post)
    
    # Broadcast to followers
    followers = db.query(SocialFollow).filter(SocialFollow.following_id == trader_id).all()
    for follow in followers:
        await manager.send_personal_message(
            json.dumps({
                "type": "new_post",
                "post_id": db_post.id,
                "trader_id": trader_id,
                "content": post.content[:100] + "..." if len(post.content) > 100 else post.content
            }),
            follow.follower_id
        )
    
    return db_post

@app.get("/posts")
async def get_posts(
    trader_id: Optional[str] = None,
    following_only: bool = False,
    user_id: Optional[str] = None,
    post_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get social posts feed"""
    query = db.query(SocialPost)
    
    if trader_id:
        query = query.filter(SocialPost.trader_id == trader_id)
    
    if following_only and user_id:
        # Get posts from followed traders
        following_ids = db.query(SocialFollow.following_id).filter(
            SocialFollow.follower_id == user_id
        ).subquery()
        query = query.filter(SocialPost.trader_id.in_(following_ids))
    
    if post_type:
        query = query.filter(SocialPost.post_type == post_type)
    
    query = query.filter(SocialPost.is_public == True)
    posts = query.order_by(SocialPost.created_at.desc()).offset(skip).limit(limit).all()
    
    return posts

@app.get("/posts/{post_id}")
async def get_post(post_id: str, db: Session = Depends(get_db)):
    """Get specific post"""
    post = db.query(SocialPost).filter(SocialPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Increment view count
    post.views_count += 1
    db.commit()
    
    return post

# Comments
@app.post("/comments")
async def create_comment(
    comment: SocialCommentCreate,
    commenter_id: str,
    db: Session = Depends(get_db)
):
    """Create comment on post"""
    db_comment = SocialComment(**comment.dict(), commenter_id=commenter_id)
    db.add(db_comment)
    
    # Update post comment count
    post = db.query(SocialPost).filter(SocialPost.id == comment.post_id).first()
    if post:
        post.comments_count += 1
    
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.get("/posts/{post_id}/comments")
async def get_comments(
    post_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get post comments"""
    comments = db.query(SocialComment).filter(
        SocialComment.post_id == post_id
    ).order_by(SocialComment.created_at.asc()).offset(skip).limit(limit).all()
    
    return comments

# Likes
@app.post("/like")
async def like_content(
    target_id: str,
    target_type: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Like post or comment"""
    # Check if already liked
    existing = db.query(SocialLike).filter(
        SocialLike.user_id == user_id,
        SocialLike.target_id == target_id,
        SocialLike.target_type == target_type
    ).first()
    
    if existing:
        # Unlike
        db.delete(existing)
        increment = -1
    else:
        # Like
        like = SocialLike(
            user_id=user_id,
            target_id=target_id,
            target_type=target_type
        )
        db.add(like)
        increment = 1
    
    # Update like count
    if target_type == "post":
        target = db.query(SocialPost).filter(SocialPost.id == target_id).first()
    else:
        target = db.query(SocialComment).filter(SocialComment.id == target_id).first()
    
    if target:
        target.likes_count = max(0, target.likes_count + increment)
    
    db.commit()
    return {"message": "Like updated successfully", "liked": increment > 0}

# Copy trading
@app.post("/copy-trade")
async def start_copy_trading(
    copy_trade: CopyTradeCreate,
    copier_id: str,
    db: Session = Depends(get_db)
):
    """Start copying a trader"""
    # Check if already copying
    existing = db.query(CopyTrade).filter(
        CopyTrade.copier_id == copier_id,
        CopyTrade.trader_id == copy_trade.trader_id,
        CopyTrade.is_active == True
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already copying this trader")
    
    # Check trader's copy settings
    trader = db.query(SocialTrader).filter(SocialTrader.id == copy_trade.trader_id).first()
    if not trader or not trader.is_copyable:
        raise HTTPException(status_code=400, detail="Trader is not available for copying")
    
    if copy_trade.copy_amount < trader.min_copy_amount:
        raise HTTPException(status_code=400, detail="Copy amount below minimum")
    
    if trader.copiers_count >= trader.max_copiers:
        raise HTTPException(status_code=400, detail="Trader has reached maximum copiers")
    
    db_copy_trade = CopyTrade(**copy_trade.dict(), copier_id=copier_id)
    db.add(db_copy_trade)
    
    # Update trader's copier count
    trader.copiers_count += 1
    
    db.commit()
    db.refresh(db_copy_trade)
    
    # Notify trader
    await manager.send_personal_message(
        json.dumps({
            "type": "new_copier",
            "copier_id": copier_id,
            "copy_amount": copy_trade.copy_amount
        }),
        copy_trade.trader_id
    )
    
    return db_copy_trade

@app.get("/copy-trades/{copier_id}")
async def get_copy_trades(copier_id: str, db: Session = Depends(get_db)):
    """Get user's copy trades"""
    copy_trades = db.query(CopyTrade).filter(
        CopyTrade.copier_id == copier_id,
        CopyTrade.is_active == True
    ).all()
    
    return copy_trades

@app.delete("/copy-trade/{copy_trade_id}")
async def stop_copy_trading(
    copy_trade_id: str,
    copier_id: str,
    db: Session = Depends(get_db)
):
    """Stop copying a trader"""
    copy_trade = db.query(CopyTrade).filter(
        CopyTrade.id == copy_trade_id,
        CopyTrade.copier_id == copier_id
    ).first()
    
    if not copy_trade:
        raise HTTPException(status_code=404, detail="Copy trade not found")
    
    copy_trade.is_active = False
    
    # Update trader's copier count
    trader = db.query(SocialTrader).filter(SocialTrader.id == copy_trade.trader_id).first()
    if trader:
        trader.copiers_count = max(0, trader.copiers_count - 1)
    
    db.commit()
    return {"message": "Copy trading stopped successfully"}

# Trading signals
@app.post("/signals")
async def create_signal(
    signal: TradingSignalCreate,
    trader_id: str,
    db: Session = Depends(get_db)
):
    """Create trading signal"""
    db_signal = TradingSignal(**signal.dict(), trader_id=trader_id)
    db.add(db_signal)
    db.commit()
    db.refresh(db_signal)
    
    # Broadcast to followers
    followers = db.query(SocialFollow).filter(SocialFollow.following_id == trader_id).all()
    for follow in followers:
        await manager.send_personal_message(
            json.dumps({
                "type": "new_signal",
                "signal_id": db_signal.id,
                "symbol": signal.symbol,
                "signal_type": signal.signal_type,
                "entry_price": signal.entry_price
            }),
            follow.follower_id
        )
    
    return db_signal

@app.get("/signals")
async def get_signals(
    trader_id: Optional[str] = None,
    symbol: Optional[str] = None,
    active_only: bool = True,
    premium_only: bool = False,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get trading signals"""
    query = db.query(TradingSignal)
    
    if trader_id:
        query = query.filter(TradingSignal.trader_id == trader_id)
    if symbol:
        query = query.filter(TradingSignal.symbol == symbol)
    if active_only:
        query = query.filter(TradingSignal.is_active == True)
    if premium_only:
        query = query.filter(TradingSignal.is_premium == True)
    
    signals = query.order_by(TradingSignal.created_at.desc()).offset(skip).limit(limit).all()
    return signals

# Leaderboards
@app.get("/leaderboard/{category}")
async def get_leaderboard(
    category: str,
    period: str = "all_time",
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get leaderboard"""
    leaderboard = db.query(SocialLeaderboard).filter(
        SocialLeaderboard.category == category,
        SocialLeaderboard.period == period
    ).order_by(SocialLeaderboard.rank.asc()).limit(limit).all()
    
    return leaderboard

@app.post("/leaderboard/update")
async def update_leaderboard(db: Session = Depends(get_db)):
    """Update leaderboards (admin only)"""
    update_leaderboards(db)
    return {"message": "Leaderboards updated successfully"}

# Influencer partnerships
@app.post("/influencer/apply")
async def apply_for_partnership(
    trader_id: str,
    tier: str,
    db: Session = Depends(get_db)
):
    """Apply for influencer partnership"""
    trader = db.query(SocialTrader).filter(SocialTrader.id == trader_id).first()
    if not trader:
        raise HTTPException(status_code=404, detail="Trader not found")
    
    # Check eligibility
    tier_requirements = {
        "bronze": {"followers": 1000, "win_rate": 60.0},
        "silver": {"followers": 5000, "win_rate": 65.0},
        "gold": {"followers": 10000, "win_rate": 70.0},
        "platinum": {"followers": 50000, "win_rate": 75.0}
    }
    
    requirements = tier_requirements.get(tier, {})
    if trader.followers_count < requirements.get("followers", 0):
        raise HTTPException(status_code=400, detail="Insufficient followers")
    if trader.win_rate < requirements.get("win_rate", 0):
        raise HTTPException(status_code=400, detail="Insufficient win rate")
    
    # Create partnership application
    partnership = InfluencerPartnership(
        trader_id=trader_id,
        tier=tier,
        commission_rate=0.1 if tier == "bronze" else 0.15 if tier == "silver" else 0.2 if tier == "gold" else 0.25,
        min_followers=requirements.get("followers", 0),
        min_win_rate=requirements.get("win_rate", 0),
        benefits={
            "commission_rate": 0.1 if tier == "bronze" else 0.15 if tier == "silver" else 0.2 if tier == "gold" else 0.25,
            "priority_support": True,
            "marketing_support": tier in ["gold", "platinum"],
            "custom_referral_code": True
        },
        expires_at=datetime.utcnow() + timedelta(days=365)
    )
    
    db.add(partnership)
    
    # Update trader status
    trader.is_influencer = True
    trader.partnership_tier = tier
    trader.commission_rate = partnership.commission_rate
    trader.referral_code = f"TGR{trader.username.upper()}"
    
    db.commit()
    db.refresh(partnership)
    
    return partnership

# Analytics
@app.get("/analytics/trader/{trader_id}")
async def get_trader_analytics(trader_id: str, db: Session = Depends(get_db)):
    """Get comprehensive trader analytics"""
    trader = db.query(SocialTrader).filter(SocialTrader.id == trader_id).first()
    if not trader:
        raise HTTPException(status_code=404, detail="Trader not found")
    
    # Get engagement metrics
    posts = db.query(SocialPost).filter(SocialPost.trader_id == trader_id).all()
    total_likes = sum(post.likes_count for post in posts)
    total_views = sum(post.views_count for post in posts)
    total_comments = sum(post.comments_count for post in posts)
    
    # Get copy trading metrics
    copy_trades = db.query(CopyTrade).filter(
        CopyTrade.trader_id == trader_id,
        CopyTrade.is_active == True
    ).all()
    
    total_aum = sum(ct.copy_amount for ct in copy_trades)
    
    return {
        "trader": trader,
        "engagement": {
            "total_likes": total_likes,
            "total_views": total_views,
            "total_comments": total_comments,
            "avg_likes_per_post": total_likes / len(posts) if posts else 0,
            "engagement_rate": (total_likes + total_comments) / total_views if total_views > 0 else 0
        },
        "copy_trading": {
            "total_copiers": len(copy_trades),
            "total_aum": total_aum,
            "avg_copy_amount": total_aum / len(copy_trades) if copy_trades else 0
        },
        "performance": {
            "total_pnl": trader.total_pnl,
            "win_rate": trader.win_rate,
            "sharpe_ratio": trader.sharpe_ratio,
            "max_drawdown": trader.max_drawdown
        }
    }

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks"""
    logger.info("Social Trading Platform service started")
    
    # Schedule leaderboard updates
    asyncio.create_task(periodic_leaderboard_update())

async def periodic_leaderboard_update():
    """Update leaderboards periodically"""
    while True:
        try:
            db = SessionLocal()
            update_leaderboards(db)
            db.close()
            logger.info("Leaderboards updated")
        except Exception as e:
            logger.error(f"Error updating leaderboards: {e}")
        
        # Update every hour
        await asyncio.sleep(3600)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)