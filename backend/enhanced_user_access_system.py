"""
Enhanced User Access Management System with Full Admin Control
Supports multiple platforms: Web, Mobile, Desktop
"""

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import jwt
import bcrypt
import secrets
import asyncio
import redis
import json
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Enhanced User Access Management System", version="2.0.0")

# Security
security = HTTPBearer()
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"

# Redis for session management
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    TRADER = "trader"
    VERIFIED_USER = "verified_user"
    USER = "user"
    GUEST = "guest"

class Permission(str, Enum):
    # User Management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_SUSPEND = "user:suspend"
    
    # Trading Permissions
    TRADE_CREATE = "trade:create"
    TRADE_READ = "trade:read"
    TRADE_CANCEL = "trade:cancel"
    TRADE_MODIFY = "trade:modify"
    
    # Admin Permissions
    ADMIN_PANEL = "admin:panel"
    SYSTEM_CONFIG = "system:config"
    SYSTEM_MONITOR = "system:monitor"
    FINANCIAL_CONTROL = "financial:control"
    
    # Platform Access
    WEB_ACCESS = "platform:web"
    MOBILE_ACCESS = "platform:mobile"
    DESKTOP_ACCESS = "platform:desktop"
    API_ACCESS = "platform:api"

class PlatformType(str, Enum):
    WEB = "web"
    MOBILE = "mobile"
    DESKTOP = "desktop"
    API = "api"

@dataclass
class UserSession:
    user_id: str
    session_token: str
    platform: PlatformType
    created_at: datetime
    expires_at: datetime
    is_active: bool = True

class User(BaseModel):
    id: Optional[str] = None
    email: EmailStr
    username: str
    full_name: str
    role: UserRole
    is_active: bool = True
    is_verified: bool = False
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    permissions: List[Permission] = []
    platform_access: List[PlatformType] = []
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    platform: PlatformType
    device_info: Optional[Dict[str, Any]] = None

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: User
    expires_in: int
    session_id: str

class PermissionCheck(BaseModel):
    user_id: str
    permission: Permission
    resource_id: Optional[str] = None

# Role-Permission Mapping
ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: [
        Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE,
        Permission.USER_DELETE, Permission.USER_SUSPEND, Permission.TRADE_CREATE,
        Permission.TRADE_READ, Permission.TRADE_CANCEL, Permission.TRADE_MODIFY,
        Permission.ADMIN_PANEL, Permission.SYSTEM_CONFIG, Permission.SYSTEM_MONITOR,
        Permission.FINANCIAL_CONTROL, Permission.WEB_ACCESS, Permission.MOBILE_ACCESS,
        Permission.DESKTOP_ACCESS, Permission.API_ACCESS
    ],
    UserRole.ADMIN: [
        Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE,
        Permission.USER_SUSPEND, Permission.TRADE_READ, Permission.ADMIN_PANEL,
        Permission.SYSTEM_MONITOR, Permission.WEB_ACCESS, Permission.MOBILE_ACCESS,
        Permission.DESKTOP_ACCESS, Permission.API_ACCESS
    ],
    UserRole.MODERATOR: [
        Permission.USER_READ, Permission.USER_SUSPEND, Permission.TRADE_READ,
        Permission.WEB_ACCESS, Permission.MOBILE_ACCESS, Permission.API_ACCESS
    ],
    UserRole.TRADER: [
        Permission.TRADE_CREATE, Permission.TRADE_READ, Permission.TRADE_CANCEL,
        Permission.WEB_ACCESS, Permission.MOBILE_ACCESS, Permission.DESKTOP_ACCESS,
        Permission.API_ACCESS
    ],
    UserRole.VERIFIED_USER: [
        Permission.TRADE_CREATE, Permission.TRADE_READ,
        Permission.WEB_ACCESS, Permission.MOBILE_ACCESS, Permission.API_ACCESS
    ],
    UserRole.USER: [
        Permission.TRADE_READ, Permission.WEB_ACCESS, Permission.MOBILE_ACCESS
    ],
    UserRole.GUEST: [
        Permission.TRADE_READ, Permission.WEB_ACCESS
    ]
}

# In-memory user database (replace with actual database)
users_db = {}
sessions_db = {}

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_permissions(user_role: UserRole) -> List[Permission]:
    return ROLE_PERMISSIONS.get(user_role, [])

def check_platform_access(user: User, platform: PlatformType) -> bool:
    return platform in user.platform_access

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if session is still active
        session_key = f"session:{credentials.credentials}"
        if not redis_client.exists(session_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired"
            )
        
        user = users_db.get(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def require_permission(permission: Permission):
    def permission_checker(current_user: User = Depends(get_current_user)):
        if permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission {permission} required"
            )
        return current_user
    return permission_checker

@app.post("/auth/register", response_model=User)
async def register(user: User, background_tasks: BackgroundTasks):
    if user.email in [u.email for u in users_db.values()]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate user ID and set default permissions
    user.id = f"user_{secrets.token_hex(8)}"
    user.created_at = datetime.utcnow()
    user.permissions = get_user_permissions(user.role)
    user.platform_access = [PlatformType.WEB, PlatformType.MOBILE] if user.role != UserRole.GUEST else [PlatformType.WEB]
    
    users_db[user.id] = user
    
    # Send verification email (background task)
    background_tasks.add_task(send_verification_email, user.email)
    
    logger.info(f"New user registered: {user.email} with role {user.role}")
    return user

@app.post("/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    # Find user by email
    user = next((u for u in users_db.values() if u.email == login_data.email), None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check platform access
    if not check_platform_access(user, login_data.platform):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Platform {login_data.platform} access denied"
        )
    
    # Create tokens
    access_token_expires = timedelta(hours=1)
    access_token = create_access_token(
        data={"sub": user.id, "platform": login_data.platform},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    # Create session
    session_id = secrets.token_hex(16)
    session = UserSession(
        user_id=user.id,
        session_token=access_token,
        platform=login_data.platform,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + access_token_expires
    )
    
    # Store session in Redis
    session_key = f"session:{access_token}"
    session_data = {
        "user_id": session.user_id,
        "platform": session.platform,
        "created_at": session.created_at.isoformat(),
        "expires_at": session.expires_at.isoformat(),
        "device_info": login_data.device_info
    }
    redis_client.setex(session_key, access_token_expires, json.dumps(session_data))
    
    # Update user last login
    user.last_login = datetime.utcnow()
    users_db[user.id] = user
    
    logger.info(f"User logged in: {user.email} on {login_data.platform}")
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user,
        expires_in=3600,
        session_id=session_id
    )

@app.post("/auth/refresh")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = users_db.get(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Create new access token
        access_token_expires = timedelta(hours=1)
        new_access_token = create_access_token(
            data={"sub": user_id},
            expires_delta=access_token_expires
        )
        
        return {"access_token": new_access_token, "expires_in": 3600}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/auth/logout")
async def logout(current_user: User = Depends(get_current_user)):
    # Invalidate current session
    # In a real implementation, you'd track and invalidate the specific session
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Successfully logged out"}

@app.get("/users/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/users", response_model=List[User])
async def get_users(current_user: User = Depends(require_permission(Permission.USER_READ))):
    return list(users_db.values())

@app.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_update: dict,
    current_user: User = Depends(require_permission(Permission.USER_UPDATE))
):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_db[user_id]
    
    # Update user fields
    for field, value in user_update.items():
        if hasattr(user, field) and field not in ['id', 'created_at']:
            setattr(user, field, value)
    
    # Update permissions if role changed
    if 'role' in user_update:
        user.permissions = get_user_permissions(user.role)
    
    users_db[user_id] = user
    logger.info(f"User updated: {user.email} by {current_user.email}")
    return user

@app.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_permission(Permission.USER_DELETE))
):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_db[user_id]
    del users_db[user_id]
    logger.info(f"User deleted: {user.email} by {current_user.email}")
    return {"message": "User deleted successfully"}

@app.post("/users/{user_id}/suspend")
async def suspend_user(
    user_id: str,
    current_user: User = Depends(require_permission(Permission.USER_SUSPEND))
):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_db[user_id]
    user.is_active = False
    users_db[user_id] = user
    
    # Invalidate all user sessions
    # This would require tracking user sessions in Redis
    
    logger.info(f"User suspended: {user.email} by {current_user.email}")
    return {"message": "User suspended successfully"}

@app.post("/check-permission")
async def check_permission_route(
    permission_check: PermissionCheck,
    current_user: User = Depends(get_current_user)
):
    if current_user.id != permission_check.user_id and Permission.USER_READ not in current_user.permissions:
        raise HTTPException(status_code=403, detail="Cannot check permissions for other users")
    
    user = users_db.get(permission_check.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    has_permission = permission_check.permission in user.permissions
    return {"has_permission": has_permission}

@app.get("/admin/dashboard/stats")
async def get_admin_dashboard_stats(
    current_user: User = Depends(require_permission(Permission.ADMIN_PANEL))
):
    total_users = len(users_db)
    active_users = len([u for u in users_db.values() if u.is_active])
    verified_users = len([u for u in users_db.values() if u.is_verified])
    
    # Get session stats from Redis
    active_sessions = len(redis_client.keys("session:*"))
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "verified_users": verified_users,
        "active_sessions": active_sessions,
        "user_roles": {
            role.value: len([u for u in users_db.values() if u.role == role])
            for role in UserRole
        }
    }

@app.get("/system/health")
async def system_health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "redis": "connected" if redis_client.ping() else "disconnected",
            "database": "connected",  # Replace with actual DB check
            "jwt_service": "operational"
        }
    }

async def send_verification_email(email: str):
    """Background task to send verification email"""
    # Implement email sending logic
    await asyncio.sleep(2)  # Simulate email sending
    logger.info(f"Verification email sent to {email}")

# Initialize with a super admin
@app.on_event("startup")
async def startup_event():
    # Create default super admin if not exists
    if not users_db:
        super_admin = User(
            email="admin@tigerex.com",
            username="superadmin",
            full_name="Super Admin",
            role=UserRole.SUPER_ADMIN,
            is_active=True,
            is_verified=True,
            platform_access=list(PlatformType)
        )
        await register(super_admin, BackgroundTasks())
        logger.info("Default super admin created")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)