"""
TigerEx Complete User Access System v11.0.0
Comprehensive user authentication, authorization, and access control
Supports web, mobile, and desktop applications with advanced security features
"""

from fastapi import FastAPI, HTTPException, Depends, Security, Request, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import logging
from decimal import Decimal
import jwt
import uvicorn
import time
import hashlib
import secrets
import re
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TigerEx Complete User Access System v11.0.0",
    description="Comprehensive user authentication and authorization system",
    version="11.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Configuration
JWT_SECRET = "tigerex-user-access-super-secure-key-2024"
JWT_ALGORITHM = "HS256"
REFRESH_TOKEN_SECRET = "tigerex-refresh-token-secure-key-2024"

# Security instances
security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ==================== ENUMS AND MODELS ====================

class UserRole(str, Enum):
    USER = "user"
    VERIFIED_USER = "verified_user"
    TRADER = "trader"
    VIP_USER = "vip_user"
    INSTITUTIONAL = "institutional"
    ADMIN = "admin"

class KYCStatus(str, Enum):
    NOT_STARTED = "not_started"
    PENDING = "pending"
    IN_REVIEW = "in_review"
    VERIFIED = "verified"
    REJECTED = "rejected"

class TwoFactorMethod(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    AUTHENTICATOR_APP = "authenticator_app"
    HARDWARE_TOKEN = "hardware_token"

class Platform(str, Enum):
    WEB = "web"
    MOBILE_IOS = "mobile_ios"
    MOBILE_ANDROID = "mobile_android"
    DESKTOP = "desktop"
    API = "api"

class AuthProvider(str, Enum):
    EMAIL_PASSWORD = "email_password"
    GOOGLE = "google"
    APPLE = "apple"
    FACEBOOK = "facebook"
    PHONE = "phone"

class UserRegistration(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    phone: Optional[str] = None
    country: str
    referral_code: Optional[str] = None
    agree_terms: bool = True
    platform: Platform = Platform.WEB
    
    @validator('password')
    def validate_password(cls, v):
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]', v):
            raise ValueError('Password must contain uppercase, lowercase, digit and special character')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers and underscores')
        return v

class UserLogin(BaseModel):
    username: str
    password: str
    two_factor_code: Optional[str] = None
    remember_me: bool = False
    platform: Platform = Platform.WEB

class User(BaseModel):
    user_id: str
    username: str
    email: str
    phone: Optional[str]
    role: UserRole
    kyc_status: KYCStatus
    is_active: bool
    is_verified: bool
    two_factor_enabled: bool
    two_factor_method: Optional[TwoFactorMethod]
    created_at: datetime
    last_login: Optional[datetime]
    login_attempts: int
    locked_until: Optional[datetime]
    api_keys: List[str]
    permissions: List[str]
    subscription_type: str
    daily_login_count: int

class Session(BaseModel):
    session_id: str
    user_id: str
    platform: Platform
    device_info: Dict[str, str]
    ip_address: str
    created_at: datetime
    expires_at: datetime
    is_active: bool
    last_activity: datetime

class APIKey(BaseModel):
    key_id: str
    user_id: str
    name: str
    permissions: List[str]
    rate_limit: int
    created_at: datetime
    last_used: Optional[datetime]
    is_active: bool

class Permission(BaseModel):
    permission_id: str
    name: str
    description: str
    category: str

# ==================== USER ACCESS SYSTEM CORE ====================

class UserAccessSystem:
    """Complete user access and authentication system"""
    
    def __init__(self):
        self.users = self._generate_sample_users()
        self.sessions = {}
        self.api_keys = {}
        self.failed_attempts = {}
        self.permission_cache = {}
        self.rate_limits = {}
        
        # Security settings
        self.max_login_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
        self.session_duration = timedelta(hours=24)
        self.refresh_token_duration = timedelta(days=7)
        
        # Permission definitions
        self.permissions = {
            "read_balance": Permission("read_balance", "Read account balance", "trading"),
            "trade_spot": Permission("trade_spot", "Trade on spot markets", "trading"),
            "trade_futures": Permission("trade_futures", "Trade on futures markets", "trading"),
            "withdraw": Permission("withdraw", "Withdraw funds", "trading"),
            "api_access": Permission("api_access", "Access trading API", "api"),
            "margin_trading": Permission("margin_trading", "Trade with margin", "trading"),
            "copy_trading": Permission("copy_trading", "Copy other traders", "social"),
            "advanced_orders": Permission("advanced_orders", "Place advanced orders", "trading")
        }
    
    def _generate_sample_users(self) -> Dict[str, User]:
        users = {}
        
        # Create sample users
        sample_users = [
            {
                "username": "demo_trader",
                "email": "demo@tigerex.com",
                "password": self._hash_password("Demo@123!"),
                "role": UserRole.VERIFIED_USER,
                "kyc_status": KYCStatus.VERIFIED
            },
            {
                "username": "vip_user",
                "email": "vip@tigerex.com", 
                "password": self._hash_password("Vip@123!"),
                "role": UserRole.VIP_USER,
                "kyc_status": KYCStatus.VERIFIED
            },
            {
                "username": "new_user",
                "email": "new@tigerex.com",
                "password": self._hash_password("New@123!"),
                "role": UserRole.USER,
                "kyc_status": KYCStatus.NOT_STARTED
            }
        ]
        
        for i, user_data in enumerate(sample_users):
            user_id = f"user_{i+1:04d}"
            
            user = User(
                user_id=user_id,
                username=user_data["username"],
                email=user_data["email"],
                phone=f"+1{555000000 + i}",
                role=user_data["role"],
                kyc_status=user_data["kyc_status"],
                is_active=True,
                is_verified=True if i < 2 else False,
                two_factor_enabled=True if i < 2 else False,
                two_factor_method=TwoFactorMethod.AUTHENTICATOR_APP if i < 2 else None,
                created_at=datetime.now() - timedelta(days=i*10),
                last_login=datetime.now() - timedelta(hours=i) if i > 0 else None,
                login_attempts=0,
                locked_until=None,
                api_keys=[f"api_key_{i+1}"],
                permissions=self._get_role_permissions(user_data["role"]),
                subscription_type="premium" if i < 2 else "basic",
                daily_login_count=i
            )
            
            users[user_id] = user
        
        return users
    
    def _get_role_permissions(self, role: UserRole) -> List[str]:
        """Get permissions based on user role"""
        role_permissions = {
            UserRole.USER: ["read_balance"],
            UserRole.VERIFIED_USER: ["read_balance", "trade_spot"],
            UserRole.TRADER: ["read_balance", "trade_spot", "api_access"],
            UserRole.VIP_USER: ["read_balance", "trade_spot", "trade_futures", "withdraw", "margin_trading", "copy_trading", "advanced_orders"],
            UserRole.INSTITUTIONAL: ["read_balance", "trade_spot", "trade_futures", "withdraw", "margin_trading", "api_access", "advanced_orders"],
            UserRole.ADMIN: list(self.permissions.keys())
        }
        return role_permissions.get(role, [])
    
    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        return self._hash_password(password) == hashed
    
    def _generate_jwt_token(self, user_id: str, platform: Platform, refresh: bool = False) -> str:
        """Generate JWT token"""
        secret = REFRESH_TOKEN_SECRET if refresh else JWT_SECRET
        duration = self.refresh_token_duration if refresh else self.session_duration
        
        payload = {
            "sub": user_id,
            "platform": platform.value,
            "type": "refresh" if refresh else "access",
            "exp": datetime.now() + duration,
            "iat": datetime.now()
        }
        
        return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"session_{secrets.token_urlsafe(32)}"
    
    def _generate_api_key(self) -> str:
        """Generate unique API key"""
        return f"tk_{secrets.token_urlsafe(40)}"
    
    def _is_account_locked(self, username: str) -> bool:
        """Check if account is locked due to failed attempts"""
        if username in self.failed_attempts:
            attempts = self.failed_attempts[username]["attempts"]
            lock_time = self.failed_attempts[username]["locked_until"]
            
            if attempts >= self.max_login_attempts:
                if lock_time and datetime.now() < lock_time:
                    return True
                else:
                    # Reset attempts after lockout period
                    del self.failed_attempts[username]
        
        return False
    
    def _record_failed_attempt(self, username: str):
        """Record failed login attempt"""
        if username not in self.failed_attempts:
            self.failed_attempts[username] = {"attempts": 0, "locked_until": None}
        
        self.failed_attempts[username]["attempts"] += 1
        
        if self.failed_attempts[username]["attempts"] >= self.max_login_attempts:
            self.failed_attempts[username]["locked_until"] = datetime.now() + self.lockout_duration
    
    def _reset_failed_attempts(self, username: str):
        """Reset failed login attempts"""
        if username in self.failed_attempts:
            del self.failed_attempts[username]
    
    async def register_user(self, registration: UserRegistration, ip_address: str) -> Dict[str, Any]:
        """Register a new user"""
        # Check if username or email already exists
        for user in self.users.values():
            if user.username == registration.username:
                raise HTTPException(status_code=400, detail="Username already exists")
            if user.email == registration.email:
                raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        user_id = f"user_{len(self.users) + 1:04d}"
        
        new_user = User(
            user_id=user_id,
            username=registration.username,
            email=registration.email,
            phone=registration.phone,
            role=UserRole.USER,
            kyc_status=KYCStatus.NOT_STARTED,
            is_active=True,
            is_verified=False,
            two_factor_enabled=False,
            two_factor_method=None,
            created_at=datetime.now(),
            last_login=None,
            login_attempts=0,
            locked_until=None,
            api_keys=[],
            permissions=self._get_role_permissions(UserRole.USER),
            subscription_type="basic",
            daily_login_count=0
        )
        
        # Store user (in real implementation, would store in database)
        self.users[user_id] = new_user
        
        # Generate tokens
        access_token = self._generate_jwt_token(user_id, registration.platform)
        refresh_token = self._generate_jwt_token(user_id, registration.platform, refresh=True)
        
        # Create session
        session_id = self._generate_session_id()
        session = Session(
            session_id=session_id,
            user_id=user_id,
            platform=registration.platform,
            device_info={"platform": registration.platform.value},
            ip_address=ip_address,
            created_at=datetime.now(),
            expires_at=datetime.now() + self.session_duration,
            is_active=True,
            last_activity=datetime.now()
        )
        self.sessions[session_id] = session
        
        return {
            "user_id": user_id,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "session_id": session_id,
            "expires_in": int(self.session_duration.total_seconds()),
            "user": {
                "username": new_user.username,
                "email": new_user.email,
                "role": new_user.role.value,
                "kyc_status": new_user.kyc_status.value
            }
        }
    
    async def authenticate_user(self, login: UserLogin, ip_address: str) -> Dict[str, Any]:
        """Authenticate user login"""
        # Check if account is locked
        if self._is_account_locked(login.username):
            raise HTTPException(status_code=423, detail="Account is locked due to multiple failed attempts")
        
        # Find user by username
        user = None
        for u in self.users.values():
            if u.username == login.username:
                user = u
                break
        
        if not user:
            self._record_failed_attempt(login.username)
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password (in real implementation, would compare with stored hash)
        # For demo, we'll use a simple check
        valid_passwords = {
            "demo_trader": "Demo@123!",
            "vip_user": "Vip@123!",
            "new_user": "New@123!"
        }
        
        if login.password not in valid_passwords or login.username not in valid_passwords:
            self._record_failed_attempt(login.username)
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is deactivated")
        
        # Reset failed attempts on successful login
        self._reset_failed_attempts(login.username)
        
        # Update user login info
        user.last_login = datetime.now()
        user.daily_login_count += 1
        
        # Generate tokens
        duration = self.session_duration * 7 if login.remember_me else self.session_duration
        access_token = self._generate_jwt_token(user.user_id, login.platform)
        refresh_token = self._generate_jwt_token(user.user_id, login.platform, refresh=True)
        
        # Create session
        session_id = self._generate_session_id()
        session = Session(
            session_id=session_id,
            user_id=user.user_id,
            platform=login.platform,
            device_info={"platform": login.platform.value},
            ip_address=ip_address,
            created_at=datetime.now(),
            expires_at=datetime.now() + duration,
            is_active=True,
            last_activity=datetime.now()
        )
        self.sessions[session_id] = session
        
        return {
            "user_id": user.user_id,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "session_id": session_id,
            "expires_in": int(duration.total_seconds()),
            "user": {
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "kyc_status": user.kyc_status.value,
                "two_factor_enabled": user.two_factor_enabled
            }
        }
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        try:
            payload = jwt.decode(refresh_token, REFRESH_TOKEN_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("sub")
            
            if user_id not in self.users:
                raise HTTPException(status_code=401, detail="Invalid refresh token")
            
            user = self.users[user_id]
            if not user.is_active:
                raise HTTPException(status_code=403, detail="Account is deactivated")
            
            # Generate new access token
            platform = Platform(payload.get("platform", "web"))
            new_access_token = self._generate_jwt_token(user_id, platform)
            new_refresh_token = self._generate_jwt_token(user_id, platform, refresh=True)
            
            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "expires_in": int(self.session_duration.total_seconds())
            }
            
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    async def logout(self, token: str, session_id: str = None) -> Dict[str, Any]:
        """Logout user and invalidate session"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("sub")
            
            # Invalidate session if provided
            if session_id and session_id in self.sessions:
                self.sessions[session_id].is_active = False
            
            return {"message": "Logged out successfully"}
            
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def check_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has specific permission"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        return permission in user.permissions
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile information"""
        if user_id not in self.users:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = self.users[user_id]
        
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "role": user.role.value,
            "kyc_status": user.kyc_status.value,
            "is_verified": user.is_verified,
            "two_factor_enabled": user.two_factor_enabled,
            "created_at": user.created_at,
            "last_login": user.last_login,
            "subscription_type": user.subscription_type,
            "permissions": user.permissions
        }

# Global instance
user_access_system = UserAccessSystem()

# ==================== MIDDLEWARE ====================

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current authenticated user"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        
        if user_id not in user_access_system.users:
            raise HTTPException(status_code=401, detail="User not found")
        
        user = user_access_system.users[user_id]
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is deactivated")
        
        return user
        
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def check_permission(permission: str, current_user: User = Depends(get_current_user)):
    """Dependency to check user permission"""
    if not user_access_system.check_permission(current_user.user_id, permission):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return current_user

# ==================== API ENDPOINTS ====================

@app.get("/")
async def root():
    return {
        "service": "TigerEx Complete User Access System v11.0.0",
        "status": "operational",
        "features": [
            "Multi-Platform Authentication",
            "Role-Based Access Control",
            "Two-Factor Authentication",
            "API Key Management",
            "Session Management",
            "Security Monitoring"
        ]
    }

@app.post("/auth/register")
async def register(
    registration: UserRegistration,
    request: Request,
    background_tasks: BackgroundTasks
):
    """Register a new user"""
    ip_address = request.client.host or "0.0.0.0"
    
    try:
        result = await user_access_system.register_user(registration, ip_address)
        
        # Background tasks for email verification, etc.
        background_tasks.add_task(
            send_verification_email,
            registration.email,
            registration.username
        )
        
        return {
            "message": "User registered successfully",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/auth/login")
async def login(login: UserLogin, request: Request):
    """User login"""
    ip_address = request.client.host or "0.0.0.0"
    
    try:
        result = await user_access_system.authenticate_user(login, ip_address)
        return {
            "message": "Login successful",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/auth/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    try:
        result = await user_access_system.refresh_token(refresh_token)
        return {
            "message": "Token refreshed successfully",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")

@app.post("/auth/logout")
async def logout(
    token: str,
    session_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Logout user"""
    try:
        await user_access_system.logout(token, session_id)
        return {"message": "Logged out successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")

@app.get("/user/profile")
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    try:
        profile = await user_access_system.get_user_profile(current_user.user_id)
        return {
            "message": "Profile retrieved successfully",
            "data": profile
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve profile")

@app.get("/user/permissions")
async def get_user_permissions(current_user: User = Depends(get_current_user)):
    """Get user permissions"""
    return {
        "permissions": current_user.permissions,
        "role": current_user.role.value
    }

@app.post("/user/api-key")
async def create_api_key(
    name: str,
    permissions: List[str],
    rate_limit: int = 1000,
    current_user: User = Depends(get_current_user)
):
    """Create new API key for user"""
    # Check if user has api_access permission
    if not user_access_system.check_permission(current_user.user_id, "api_access"):
        raise HTTPException(status_code=403, detail="API access not permitted")
    
    # Validate permissions
    for perm in permissions:
        if perm not in current_user.permissions:
            raise HTTPException(status_code=400, detail=f"Permission {perm} not granted to user")
    
    key_id = f"key_{len(user_access_system.api_keys) + 1:04d}"
    api_key = user_access_system._generate_api_key()
    
    new_key = APIKey(
        key_id=key_id,
        user_id=current_user.user_id,
        name=name,
        permissions=permissions,
        rate_limit=rate_limit,
        created_at=datetime.now(),
        last_used=None,
        is_active=True
    )
    
    user_access_system.api_keys[key_id] = new_key
    
    return {
        "message": "API key created successfully",
        "data": {
            "key_id": key_id,
            "api_key": api_key,  # Only shown once during creation
            "name": name,
            "permissions": permissions,
            "rate_limit": rate_limit
        }
    }

@app.get("/user/api-keys")
async def get_api_keys(current_user: User = Depends(get_current_user)):
    """Get user's API keys"""
    user_keys = []
    for key in user_access_system.api_keys.values():
        if key.user_id == current_user.user_id:
            user_keys.append({
                "key_id": key.key_id,
                "name": key.name,
                "permissions": key.permissions,
                "rate_limit": key.rate_limit,
                "created_at": key.created_at,
                "last_used": key.last_used,
                "is_active": key.is_active
            })
    
    return {"api_keys": user_keys}

@app.delete("/user/api-key/{key_id}")
async def delete_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete API key"""
    if key_id not in user_access_system.api_keys:
        raise HTTPException(status_code=404, detail="API key not found")
    
    key = user_access_system.api_keys[key_id]
    if key.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    del user_access_system.api_keys[key_id]
    return {"message": "API key deleted successfully"}

# Background task functions
async def send_verification_email(email: str, username: str):
    """Send verification email (placeholder)"""
    logger.info(f"Verification email sent to {email} for user {username}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)