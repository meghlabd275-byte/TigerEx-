"""
TigerEx Exchange Platform
Version: 7.0.0 - Production Release

Social Trading Network Service
Social features for traders to share strategies and performance
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostType(Enum):
    TRADE_IDEA = "trade_idea"
    ANALYSIS = "analysis"
    PORTFOLIO_UPDATE = "portfolio_update"
    MARKET_OUTLOOK = "market_outlook"
    EDUCATIONAL = "educational"

class PrivacyLevel(Enum):
    PUBLIC = "public"
    FOLLOWERS_ONLY = "followers_only"
    PRIVATE = "private"

@dataclass
class TraderProfile:
    user_id: str
    username: str
    display_name: str
    bio: str
    avatar_url: str
    verified: bool
    followers_count: int
    following_count: int
    posts_count: int
    performance_stats: Dict[str, float]
    badges: List[str]
    joined_at: datetime

@dataclass
class SocialPost:
    id: str
    author_id: str
    content: str
    post_type: PostType
    attachments: List[Dict[str, Any]]
    likes_count: int
    comments_count: int
    shares_count: int
    privacy: PrivacyLevel
    tags: List[str]
    mentioned_users: List[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class Comment:
    id: str
    post_id: str
    author_id: str
    content: str
    likes_count: int
    parent_comment_id: Optional[str]
    created_at: datetime

@dataclass
class FollowRelationship:
    follower_id: str
    following_id: str
    created_at: datetime

class SocialTradingService:
    def __init__(self):
        self.profiles: Dict[str, TraderProfile] = {}
        self.posts: Dict[str, SocialPost] = {}
        self.comments: Dict[str, Comment] = {}
        self.follows: Dict[str, FollowRelationship] = {}
        self.likes: Dict[str, set] = {}  # post_id -> set of user_ids
        self.trending_tags: Dict[str, int] = {}
        
    async def initialize(self):
        """Initialize the social trading service"""
        logger.info("🌐 Initializing Social Trading Network Service...")
        
        # Load sample data
        await self._load_sample_data()
        
        logger.info("✅ Social Trading Network Service initialized")
    
    async def _load_sample_data(self):
        """Load sample data for demonstration"""
        # Create sample trader profiles
        sample_traders = [
            {
                "user_id": "trader_001",
                "username": "cryptowhale",
                "display_name": "Crypto Whale",
                "bio": "Professional trader with 10+ years experience. Specializing in BTC and ETH.",
                "avatar_url": "https://example.com/avatars/cryptowhale.jpg",
                "verified": True,
                "performance_stats": {
                    "win_rate": 68.5,
                    "total_return": 245.6,
                    "sharpe_ratio": 1.85,
                    "max_drawdown": -12.3,
                    "followers_gain": 1850
                },
                "badges": ["Top Trader", "Verified", "Mentor"]
            },
            {
                "user_id": "trader_002",
                "username": "defi_master",
                "display_name": "DeFi Master",
                "bio": "DeFi enthusiast and yield farming expert. Sharing alpha 24/7.",
                "avatar_url": "https://example.com/avatars/defi_master.jpg",
                "verified": True,
                "performance_stats": {
                    "win_rate": 72.1,
                    "total_return": 189.3,
                    "sharpe_ratio": 2.12,
                    "max_drawdown": -8.7,
                    "followers_gain": 1230
                },
                "badges": ["DeFi Expert", "Verified", "Yield Farmer"]
            }
        ]
        
        for trader_data in sample_traders:
            profile = TraderProfile(
                user_id=trader_data["user_id"],
                username=trader_data["username"],
                display_name=trader_data["display_name"],
                bio=trader_data["bio"],
                avatar_url=trader_data["avatar_url"],
                verified=trader_data["verified"],
                followers_count=0,
                following_count=0,
                posts_count=0,
                performance_stats=trader_data["performance_stats"],
                badges=trader_data["badges"],
                joined_at=datetime.now() - timedelta(days=365)
            )
            self.profiles[profile.user_id] = profile
    
    async def create_profile(self, user_data: Dict[str, Any]) -> TraderProfile:
        """Create a new trader profile"""
        try:
            profile = TraderProfile(
                user_id=user_data["user_id"],
                username=user_data["username"],
                display_name=user_data.get("display_name", user_data["username"]),
                bio=user_data.get("bio", ""),
                avatar_url=user_data.get("avatar_url", ""),
                verified=user_data.get("verified", False),
                followers_count=0,
                following_count=0,
                posts_count=0,
                performance_stats=user_data.get("performance_stats", {}),
                badges=user_data.get("badges", []),
                joined_at=datetime.now()
            )
            
            self.profiles[profile.user_id] = profile
            logger.info(f"👤 Created profile for {profile.username}")
            return profile
            
        except Exception as e:
            logger.error(f"❌ Error creating profile: {e}")
            raise
    
    async def get_profile(self, user_id: str) -> Optional[TraderProfile]:
        """Get trader profile by user ID"""
        return self.profiles.get(user_id)
    
    async def update_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update trader profile"""
        try:
            profile = self.profiles.get(user_id)
            if not profile:
                return False
            
            for key, value in updates.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            
            logger.info(f"✏️ Updated profile for {profile.username}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating profile: {e}")
            return False
    
    async def create_post(self, post_data: Dict[str, Any]) -> SocialPost:
        """Create a new social post"""
        try:
            post_id = str(uuid.uuid4())
            
            post = SocialPost(
                id=post_id,
                author_id=post_data["author_id"],
                content=post_data["content"],
                post_type=PostType(post_data.get("post_type", "trade_idea")),
                attachments=post_data.get("attachments", []),
                likes_count=0,
                comments_count=0,
                shares_count=0,
                privacy=PrivacyLevel(post_data.get("privacy", "public")),
                tags=post_data.get("tags", []),
                mentioned_users=post_data.get("mentioned_users", []),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.posts[post_id] = post
            self.likes[post_id] = set()
            
            # Update trending tags
            for tag in post.tags:
                self.trending_tags[tag] = self.trending_tags.get(tag, 0) + 1
            
            # Update author's post count
            if post.author_id in self.profiles:
                self.profiles[post.author_id].posts_count += 1
            
            logger.info(f"📝 Created post {post_id} by {post.author_id}")
            return post
            
        except Exception as e:
            logger.error(f"❌ Error creating post: {e}")
            raise
    
    async def get_post(self, post_id: str) -> Optional[SocialPost]:
        """Get post by ID"""
        return self.posts.get(post_id)
    
    async def get_feed(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get user's social feed"""
        try:
            # Get users that current user follows
            following_ids = set()
            for follow in self.follows.values():
                if follow.follower_id == user_id:
                    following_ids.add(follow.following_id)
            
            # Add own posts
            following_ids.add(user_id)
            
            # Get posts from followed users
            feed_posts = []
            for post in self.posts.values():
                if post.author_id in following_ids and post.privacy == PrivacyLevel.PUBLIC:
                    feed_posts.append(post)
            
            # Sort by creation time (newest first)
            feed_posts.sort(key=lambda x: x.created_at, reverse=True)
            
            # Paginate
            paginated_posts = feed_posts[offset:offset + limit]
            
            # Convert to dict format
            feed_data = []
            for post in paginated_posts:
                author = self.profiles.get(post.author_id)
                post_dict = asdict(post)
                post_dict["author"] = asdict(author) if author else None
                post_dict["is_liked"] = user_id in self.likes.get(post.id, set())
                feed_data.append(post_dict)
            
            return feed_data
            
        except Exception as e:
            logger.error(f"❌ Error getting feed: {e}")
            return []
    
    async def like_post(self, post_id: str, user_id: str) -> bool:
        """Like a post"""
        try:
            if post_id not in self.posts:
                return False
            
            if post_id not in self.likes:
                self.likes[post_id] = set()
            
            if user_id not in self.likes[post_id]:
                self.likes[post_id].add(user_id)
                self.posts[post_id].likes_count += 1
                logger.info(f"👍 User {user_id} liked post {post_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error liking post: {e}")
            return False
    
    async def unlike_post(self, post_id: str, user_id: str) -> bool:
        """Unlike a post"""
        try:
            if post_id not in self.posts or post_id not in self.likes:
                return False
            
            if user_id in self.likes[post_id]:
                self.likes[post_id].remove(user_id)
                self.posts[post_id].likes_count -= 1
                logger.info(f"👎 User {user_id} unliked post {post_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error unliking post: {e}")
            return False
    
    async def create_comment(self, comment_data: Dict[str, Any]) -> Comment:
        """Create a comment on a post"""
        try:
            comment_id = str(uuid.uuid4())
            
            comment = Comment(
                id=comment_id,
                post_id=comment_data["post_id"],
                author_id=comment_data["author_id"],
                content=comment_data["content"],
                likes_count=0,
                parent_comment_id=comment_data.get("parent_comment_id"),
                created_at=datetime.now()
            )
            
            self.comments[comment_id] = comment
            
            # Update post's comment count
            if comment.post_id in self.posts:
                self.posts[comment.post_id].comments_count += 1
            
            logger.info(f"💬 Created comment {comment_id} on post {comment.post_id}")
            return comment
            
        except Exception as e:
            logger.error(f"❌ Error creating comment: {e}")
            raise
    
    async def get_comments(self, post_id: str) -> List[Dict[str, Any]]:
        """Get comments for a post"""
        try:
            post_comments = []
            for comment in self.comments.values():
                if comment.post_id == post_id and not comment.parent_comment_id:
                    author = self.profiles.get(comment.author_id)
                    comment_dict = asdict(comment)
                    comment_dict["author"] = asdict(author) if author else None
                    comment_dict["replies"] = await self._get_comment_replies(comment.id)
                    post_comments.append(comment_dict)
            
            # Sort by creation time
            post_comments.sort(key=lambda x: x["created_at"])
            return post_comments
            
        except Exception as e:
            logger.error(f"❌ Error getting comments: {e}")
            return []
    
    async def _get_comment_replies(self, parent_comment_id: str) -> List[Dict[str, Any]]:
        """Get replies to a comment"""
        replies = []
        for comment in self.comments.values():
            if comment.parent_comment_id == parent_comment_id:
                author = self.profiles.get(comment.author_id)
                comment_dict = asdict(comment)
                comment_dict["author"] = asdict(author) if author else None
                replies.append(comment_dict)
        
        replies.sort(key=lambda x: x["created_at"])
        return replies
    
    async def follow_user(self, follower_id: str, following_id: str) -> bool:
        """Follow a user"""
        try:
            # Check if already following
            follow_key = f"{follower_id}_{following_id}"
            if follow_key in self.follows:
                return False
            
            # Create follow relationship
            follow = FollowRelationship(
                follower_id=follower_id,
                following_id=following_id,
                created_at=datetime.now()
            )
            
            self.follows[follow_key] = follow
            
            # Update follower counts
            if follower_id in self.profiles:
                self.profiles[follower_id].following_count += 1
            
            if following_id in self.profiles:
                self.profiles[following_id].followers_count += 1
            
            logger.info(f"👥 User {follower_id} followed {following_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error following user: {e}")
            return False
    
    async def unfollow_user(self, follower_id: str, following_id: str) -> bool:
        """Unfollow a user"""
        try:
            follow_key = f"{follower_id}_{following_id}"
            
            if follow_key not in self.follows:
                return False
            
            del self.follows[follow_key]
            
            # Update follower counts
            if follower_id in self.profiles:
                self.profiles[follower_id].following_count -= 1
            
            if following_id in self.profiles:
                self.profiles[following_id].followers_count -= 1
            
            logger.info(f"🚫 User {follower_id} unfollowed {following_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error unfollowing user: {e}")
            return False
    
    async def get_followers(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's followers"""
        followers = []
        for follow in self.follows.values():
            if follow.following_id == user_id:
                follower_profile = self.profiles.get(follow.follower_id)
                if follower_profile:
                    followers.append(asdict(follower_profile))
        
        return followers
    
    async def get_following(self, user_id: str) -> List[Dict[str, Any]]:
        """Get users that user follows"""
        following = []
        for follow in self.follows.values():
            if follow.follower_id == user_id:
                following_profile = self.profiles.get(follow.following_id)
                if following_profile:
                    following.append(asdict(following_profile))
        
        return following
    
    async def search_traders(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for traders"""
        try:
            results = []
            query_lower = query.lower()
            
            for profile in self.profiles.values():
                if (query_lower in profile.username.lower() or 
                    query_lower in profile.display_name.lower() or
                    query_lower in profile.bio.lower()):
                    results.append(asdict(profile))
            
            # Sort by followers count (most popular first)
            results.sort(key=lambda x: x["followers_count"], reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"❌ Error searching traders: {e}")
            return []
    
    async def get_trending_posts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get trending posts"""
        try:
            # Sort posts by engagement (likes + comments + shares)
            trending_posts = []
            for post in self.posts.values():
                if post.privacy == PrivacyLevel.PUBLIC:
                    engagement = post.likes_count + post.comments_count + post.shares_count
                    trending_posts.append((post, engagement))
            
            # Sort by engagement (highest first)
            trending_posts.sort(key=lambda x: x[1], reverse=True)
            
            # Convert to dict format
            trending_data = []
            for post, _ in trending_posts[:limit]:
                author = self.profiles.get(post.author_id)
                post_dict = asdict(post)
                post_dict["author"] = asdict(author) if author else None
                trending_data.append(post_dict)
            
            return trending_data
            
        except Exception as e:
            logger.error(f"❌ Error getting trending posts: {e}")
            return []
    
    async def get_trending_tags(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending tags"""
        try:
            sorted_tags = sorted(self.trending_tags.items(), key=lambda x: x[1], reverse=True)
            return [{"tag": tag, "count": count} for tag, count in sorted_tags[:limit]]
            
        except Exception as e:
            logger.error(f"❌ Error getting trending tags: {e}")
            return []

# FastAPI application
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(title="Social Trading Network Service", version="7.0.0")
social_service = SocialTradingService()

class ProfileCreate(BaseModel):
    user_id: str
    username: str
    display_name: Optional[str] = None
    bio: Optional[str] = ""
    avatar_url: Optional[str] = ""
    verified: bool = False
    performance_stats: Optional[Dict[str, float]] = {}
    badges: Optional[List[str]] = []

class PostCreate(BaseModel):
    author_id: str
    content: str
    post_type: str = "trade_idea"
    attachments: Optional[List[Dict[str, Any]]] = []
    privacy: str = "public"
    tags: Optional[List[str]] = []
    mentioned_users: Optional[List[str]] = []

class CommentCreate(BaseModel):
    post_id: str
    author_id: str
    content: str
    parent_comment_id: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    await social_service.initialize()

@app.post("/profiles")
async def create_profile(profile: ProfileCreate):
    try:
        new_profile = await social_service.create_profile(profile.dict())
        return {"success": True, "profile": new_profile}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/profiles/{user_id}")
async def get_profile(user_id: str):
    profile = await social_service.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@app.put("/profiles/{user_id}")
async def update_profile(user_id: str, updates: dict):
    success = await social_service.update_profile(user_id, updates)
    return {"success": success}

@app.post("/posts")
async def create_post(post: PostCreate):
    try:
        new_post = await social_service.create_post(post.dict())
        return {"success": True, "post": new_post}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/posts/{post_id}")
async def get_post(post_id: str):
    post = await social_service.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.get("/feed/{user_id}")
async def get_feed(user_id: str, limit: int = Query(20), offset: int = Query(0)):
    return await social_service.get_feed(user_id, limit, offset)

@app.post("/posts/{post_id}/like")
async def like_post(post_id: str, user_id: str):
    success = await social_service.like_post(post_id, user_id)
    return {"success": success}

@app.delete("/posts/{post_id}/like")
async def unlike_post(post_id: str, user_id: str):
    success = await social_service.unlike_post(post_id, user_id)
    return {"success": success}

@app.post("/comments")
async def create_comment(comment: CommentCreate):
    try:
        new_comment = await social_service.create_comment(comment.dict())
        return {"success": True, "comment": new_comment}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/posts/{post_id}/comments")
async def get_comments(post_id: str):
    return await social_service.get_comments(post_id)

@app.post("/follow")
async def follow_user(follower_id: str, following_id: str):
    success = await social_service.follow_user(follower_id, following_id)
    return {"success": success}

@app.delete("/follow")
async def unfollow_user(follower_id: str, following_id: str):
    success = await social_service.unfollow_user(follower_id, following_id)
    return {"success": success}

@app.get("/profiles/{user_id}/followers")
async def get_followers(user_id: str):
    return await social_service.get_followers(user_id)

@app.get("/profiles/{user_id}/following")
async def get_following(user_id: str):
    return await social_service.get_following(user_id)

@app.get("/search/traders")
async def search_traders(q: str = Query(...), limit: int = Query(20)):
    return await social_service.search_traders(q, limit)

@app.get("/trending/posts")
async def get_trending_posts(limit: int = Query(20)):
    return await social_service.get_trending_posts(limit)

@app.get("/trending/tags")
async def get_trending_tags(limit: int = Query(10)):
    return await social_service.get_trending_tags(limit)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)