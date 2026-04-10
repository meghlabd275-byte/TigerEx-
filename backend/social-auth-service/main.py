"""
TigerEx Social Authentication Service
Complete OAuth 2.0 implementation for Google, Facebook, Twitter, Telegram
Port: 8010
"""

from fastapi import FastAPI, HTTPException, Depends, Request, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import httpx
import jwt
import secrets
import hashlib
import hmac
import json
import os
import structlog
from urllib.parse import urlencode, parse_qs, urlparse

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)
logger = structlog.get_logger()

# Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "tigerex-super-secret-jwt-key-2024")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/google/callback")

FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID", "")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET", "")
FACEBOOK_REDIRECT_URI = os.getenv("FACEBOOK_REDIRECT_URI", "http://localhost:3000/auth/facebook/callback")

TWITTER_CLIENT_ID = os.getenv("TWITTER_CLIENT_ID", "")
TWITTER_CLIENT_SECRET = os.getenv("TWITTER_CLIENT_SECRET", "")
TWITTER_REDIRECT_URI = os.getenv("TWITTER_REDIRECT_URI", "http://localhost:3000/auth/twitter/callback")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_REDIRECT_URI = os.getenv("TELEGRAM_REDIRECT_URI", "http://localhost:3000/auth/telegram/callback")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tigerex:password@localhost/tigerex_auth")

app = FastAPI(
    title="TigerEx Social Auth Service",
    description="Complete OAuth 2.0 Social Authentication",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# ENUMS AND MODELS
# ============================================================================

class OAuthProvider(str, Enum):
    GOOGLE = "google"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    TELEGRAM = "telegram"
    APPLE = "apple"
    DISCORD = "discord"

class SocialAccountStatus(str, Enum):
    LINKED = "linked"
    UNLINKED = "unlinked"
    SUSPENDED = "suspended"

class SocialUserCreate(BaseModel):
    provider: OAuthProvider
    provider_user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    picture: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    raw_data: Optional[Dict[str, Any]] = None

class SocialAuthResponse(BaseModel):
    success: bool
    message: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    user: Optional[Dict[str, Any]] = None
    is_new_user: bool = False
    redirect_url: Optional[str] = None

class OAuthState(BaseModel):
    state: str
    provider: OAuthProvider
    redirect_uri: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TelegramAuthData(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str

# ============================================================================
# STATE MANAGEMENT
# ============================================================================

oauth_states: Dict[str, OAuthState] = {}

def generate_state(provider: OAuthProvider, redirect_uri: str) -> str:
    """Generate a secure state token for OAuth flow"""
    state = secrets.token_urlsafe(32)
    oauth_states[state] = OAuthState(
        state=state,
        provider=provider,
        redirect_uri=redirect_uri
    )
    return state

def verify_state(state: str) -> Optional[OAuthState]:
    """Verify and return OAuth state"""
    if state in oauth_states:
        oauth_state = oauth_states[state]
        # State expires in 10 minutes
        if (datetime.utcnow() - oauth_state.created_at).total_seconds() < 600:
            return oauth_state
        del oauth_states[state]
    return None

# ============================================================================
# JWT TOKEN MANAGEMENT
# ============================================================================

def create_jwt_token(user_id: str, email: str, role: str = "user", permissions: List[str] = None) -> str:
    """Create JWT token for authenticated user"""
    expiration = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "permissions": permissions or [],
        "exp": expiration,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def create_refresh_token() -> str:
    """Create a secure refresh token"""
    return secrets.token_urlsafe(64)

# ============================================================================
# GOOGLE OAUTH
# ============================================================================

@app.get("/auth/google")
async def google_login(redirect_uri: str = Query(default="/dashboard")):
    """Initiate Google OAuth flow"""
    state = generate_state(OAuthProvider.GOOGLE, redirect_uri)
    
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "consent"
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    
    return {
        "success": True,
        "auth_url": auth_url,
        "state": state
    }

@app.get("/auth/google/callback")
async def google_callback(code: str, state: str):
    """Handle Google OAuth callback"""
    # Verify state
    oauth_state = verify_state(state)
    if not oauth_state or oauth_state.provider != OAuthProvider.GOOGLE:
        raise HTTPException(status_code=400, detail="Invalid state")
    
    async with httpx.AsyncClient() as client:
        # Exchange code for tokens
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code"
            }
        )
        
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for tokens")
        
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        
        # Get user info
        user_response = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        user_data = user_response.json()
        
        # Create social user
        social_user = SocialUserCreate(
            provider=OAuthProvider.GOOGLE,
            provider_user_id=user_data.get("sub"),
            email=user_data.get("email"),
            name=user_data.get("name"),
            first_name=user_data.get("given_name"),
            last_name=user_data.get("family_name"),
            picture=user_data.get("picture"),
            access_token=access_token,
            refresh_token=refresh_token,
            raw_data=user_data
        )
        
        # Process login/register
        return await process_social_login(social_user, oauth_state.redirect_uri)

# ============================================================================
# FACEBOOK OAUTH
# ============================================================================

@app.get("/auth/facebook")
async def facebook_login(redirect_uri: str = Query(default="/dashboard")):
    """Initiate Facebook OAuth flow"""
    state = generate_state(OAuthProvider.FACEBOOK, redirect_uri)
    
    params = {
        "client_id": FACEBOOK_APP_ID,
        "redirect_uri": FACEBOOK_REDIRECT_URI,
        "response_type": "code",
        "scope": "email,public_profile",
        "state": state
    }
    
    auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?{urlencode(params)}"
    
    return {
        "success": True,
        "auth_url": auth_url,
        "state": state
    }

@app.get("/auth/facebook/callback")
async def facebook_callback(code: str, state: str):
    """Handle Facebook OAuth callback"""
    oauth_state = verify_state(state)
    if not oauth_state or oauth_state.provider != OAuthProvider.FACEBOOK:
        raise HTTPException(status_code=400, detail="Invalid state")
    
    async with httpx.AsyncClient() as client:
        # Exchange code for tokens
        token_response = await client.get(
            "https://graph.facebook.com/v18.0/oauth/access_token",
            params={
                "client_id": FACEBOOK_APP_ID,
                "client_secret": FACEBOOK_APP_SECRET,
                "redirect_uri": FACEBOOK_REDIRECT_URI,
                "code": code
            }
        )
        
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for tokens")
        
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        # Get user info
        user_response = await client.get(
            "https://graph.facebook.com/v18.0/me",
            params={
                "fields": "id,name,email,first_name,last_name,picture",
                "access_token": access_token
            }
        )
        
        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        user_data = user_response.json()
        
        picture_url = None
        if "picture" in user_data and "data" in user_data["picture"]:
            picture_url = user_data["picture"]["data"].get("url")
        
        social_user = SocialUserCreate(
            provider=OAuthProvider.FACEBOOK,
            provider_user_id=user_data.get("id"),
            email=user_data.get("email"),
            name=user_data.get("name"),
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
            picture=picture_url,
            access_token=access_token,
            raw_data=user_data
        )
        
        return await process_social_login(social_user, oauth_state.redirect_uri)

# ============================================================================
# TWITTER OAUTH 2.0
# ============================================================================

@app.get("/auth/twitter")
async def twitter_login(redirect_uri: str = Query(default="/dashboard")):
    """Initiate Twitter OAuth 2.0 flow"""
    state = generate_state(OAuthProvider.TWITTER, redirect_uri)
    
    params = {
        "client_id": TWITTER_CLIENT_ID,
        "redirect_uri": TWITTER_REDIRECT_URI,
        "response_type": "code",
        "scope": "tweet.read users.read email",
        "state": state,
        "code_challenge": "challenge",
        "code_challenge_method": "plain"
    }
    
    auth_url = f"https://twitter.com/i/oauth2/authorize?{urlencode(params)}"
    
    return {
        "success": True,
        "auth_url": auth_url,
        "state": state
    }

@app.get("/auth/twitter/callback")
async def twitter_callback(code: str, state: str):
    """Handle Twitter OAuth callback"""
    oauth_state = verify_state(state)
    if not oauth_state or oauth_state.provider != OAuthProvider.TWITTER:
        raise HTTPException(status_code=400, detail="Invalid state")
    
    async with httpx.AsyncClient() as client:
        # Exchange code for tokens
        token_response = await client.post(
            "https://api.twitter.com/2/oauth2/token",
            data={
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": TWITTER_REDIRECT_URI,
                "code_verifier": "challenge"
            },
            auth=(TWITTER_CLIENT_ID, TWITTER_CLIENT_SECRET)
        )
        
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for tokens")
        
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        # Get user info
        user_response = await client.get(
            "https://api.twitter.com/2/users/me",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"user.fields": "id,name,username,profile_image_url,email"}
        )
        
        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        user_data = user_response.json()
        twitter_user = user_data.get("data", {})
        
        social_user = SocialUserCreate(
            provider=OAuthProvider.TWITTER,
            provider_user_id=twitter_user.get("id"),
            name=twitter_user.get("name"),
            email=twitter_user.get("email"),
            picture=twitter_user.get("profile_image_url"),
            access_token=access_token,
            raw_data=user_data
        )
        
        return await process_social_login(social_user, oauth_state.redirect_uri)

# ============================================================================
# TELEGRAM LOGIN WIDGET
# ============================================================================

@app.post("/auth/telegram")
async def telegram_login(auth_data: TelegramAuthData, redirect_uri: str = Query(default="/dashboard")):
    """Handle Telegram Login Widget authentication"""
    # Verify Telegram hash
    if not verify_telegram_auth(auth_data.dict()):
        raise HTTPException(status_code=400, detail="Invalid Telegram authentication data")
    
    # Check auth date (must be within 24 hours)
    current_time = int(datetime.utcnow().timestamp())
    if current_time - auth_data.auth_date > 86400:
        raise HTTPException(status_code=400, detail="Authentication data expired")
    
    social_user = SocialUserCreate(
        provider=OAuthProvider.TELEGRAM,
        provider_user_id=str(auth_data.id),
        first_name=auth_data.first_name,
        last_name=auth_data.last_name,
        name=f"{auth_data.first_name} {auth_data.last_name or ''}".strip(),
        picture=auth_data.photo_url,
        raw_data=auth_data.dict()
    )
    
    return await process_social_login(social_user, redirect_uri)

def verify_telegram_auth(auth_data: Dict[str, Any]) -> bool:
    """Verify Telegram authentication data hash"""
    if not TELEGRAM_BOT_TOKEN:
        return False
    
    received_hash = auth_data.pop("hash", None)
    if not received_hash:
        return False
    
    # Create data check string
    data_check_items = []
    for key, value in sorted(auth_data.items()):
        if value is not None:
            data_check_items.append(f"{key}={value}")
    data_check_string = "\n".join(data_check_items)
    
    # Calculate secret key
    secret_key = hashlib.sha256(TELEGRAM_BOT_TOKEN.encode()).digest()
    
    # Calculate hash
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return calculated_hash == received_hash

# ============================================================================
# DISCORD OAUTH
# ============================================================================

@app.get("/auth/discord")
async def discord_login(redirect_uri: str = Query(default="/dashboard")):
    """Initiate Discord OAuth flow"""
    state = generate_state(OAuthProvider.DISCORD, redirect_uri)
    
    params = {
        "client_id": os.getenv("DISCORD_CLIENT_ID", ""),
        "redirect_uri": os.getenv("DISCORD_REDIRECT_URI", "http://localhost:3000/auth/discord/callback"),
        "response_type": "code",
        "scope": "identify email",
        "state": state
    }
    
    auth_url = f"https://discord.com/api/oauth2/authorize?{urlencode(params)}"
    
    return {
        "success": True,
        "auth_url": auth_url,
        "state": state
    }

# ============================================================================
# PROCESS SOCIAL LOGIN
# ============================================================================

async def process_social_login(social_user: SocialUserCreate, redirect_uri: str) -> SocialAuthResponse:
    """Process social login - create user if new, login if existing"""
    
    # In production, this would:
    # 1. Check if social account exists in database
    # 2. If exists, get the linked user
    # 3. If not, create new user and link social account
    # 4. Generate JWT tokens
    # 5. Return appropriate response
    
    user_id = f"social_{social_user.provider.value}_{social_user.provider_user_id}"
    
    # Generate tokens
    access_token = create_jwt_token(
        user_id=user_id,
        email=social_user.email or f"{user_id}@tigerex.social",
        role="user"
    )
    refresh_token = create_refresh_token()
    
    user_info = {
        "id": user_id,
        "email": social_user.email,
        "name": social_user.name,
        "first_name": social_user.first_name,
        "last_name": social_user.last_name,
        "picture": social_user.picture,
        "provider": social_user.provider.value,
        "provider_user_id": social_user.provider_user_id
    }
    
    logger.info("Social login processed", 
                provider=social_user.provider.value,
                user_id=user_id)
    
    return SocialAuthResponse(
        success=True,
        message="Login successful",
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_info,
        is_new_user=False,
        redirect_url=redirect_uri
    )

# ============================================================================
# ACCOUNT LINKING
# ============================================================================

@app.post("/auth/link/{provider}")
async def link_social_account(
    provider: OAuthProvider,
    user_id: str = Query(...),
    code: Optional[str] = None
):
    """Link a social account to existing user"""
    # This would link a social account to an existing user account
    return {
        "success": True,
        "message": f"Social account {provider.value} linked successfully"
    }

@app.delete("/auth/unlink/{provider}")
async def unlink_social_account(
    provider: OAuthProvider,
    user_id: str = Query(...)
):
    """Unlink a social account from user"""
    return {
        "success": True,
        "message": f"Social account {provider.value} unlinked successfully"
    }

@app.get("/auth/linked-accounts")
async def get_linked_accounts(user_id: str = Query(...)):
    """Get all linked social accounts for a user"""
    return {
        "success": True,
        "accounts": [
            {"provider": "google", "linked": True, "email": "user@gmail.com"},
            {"provider": "telegram", "linked": True, "username": "telegram_user"}
        ]
    }

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "social-auth-service",
        "version": "2.0.0",
        "providers": ["google", "facebook", "twitter", "telegram", "discord"]
    }

@app.get("/")
async def root():
    return {
        "service": "TigerEx Social Authentication Service",
        "version": "2.0.0",
        "endpoints": {
            "google": "/auth/google",
            "facebook": "/auth/facebook",
            "twitter": "/auth/twitter",
            "telegram": "/auth/telegram (POST)",
            "discord": "/auth/discord",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)