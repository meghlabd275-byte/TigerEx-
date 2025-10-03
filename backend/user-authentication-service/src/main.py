"""
TigerEx User Authentication Service
Complete authentication system with registration, login, 2FA, password reset, and session management
Port: 8200
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal
import asyncio
import asyncpg
import redis.asyncio as redis
import structlog
import uvicorn
import os
import secrets
import hashlib
import pyotp
import qrcode
import io
import base64
from jose import JWTError, jwt
from passlib.context import CryptContext
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

# Import admin routes
from admin.admin_routes import router as admin_router

# Configure structured logging
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
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/tigerex")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Email configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@tigerex.com")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Global connections
db_pool = None
redis_client = None

# FastAPI app
app = FastAPI(
    title="TigerEx User Authentication Service",
    description="Complete authentication system with 2FA, session management, and security features",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include admin router
app.include_router(admin_router)

security = HTTPBearer()

# Pydantic Models
class UserRegistration(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    referral_code: Optional[str] = None
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    totp_code: Optional[str] = None

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class Enable2FA(BaseModel):
    password: str

class Verify2FA(BaseModel):
    totp_code: str

class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class APIKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    permissions: List[str] = []
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)

class SessionResponse(BaseModel):
    session_id: str
    device: str
    ip_address: str
    location: Optional[str]
    created_at: datetime
    last_active: datetime
    is_current: bool

# Helper functions
def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Verify JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {"user_id": int(user_id), "email": payload.get("email")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def send_email(to_email: str, subject: str, body: str):
    """Send email"""
    try:
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        if SMTP_USER and SMTP_PASSWORD:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            logger.info("Email sent", to=to_email, subject=subject)
        else:
            logger.warning("Email not configured, skipping send", to=to_email)
    except Exception as e:
        logger.error("Failed to send email", error=str(e), to=to_email)

# Database initialization
async def init_database():
    """Initialize database connection and create tables"""
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)
        
        async with db_pool.acquire() as conn:
            # Users table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    username VARCHAR(50) UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_verified BOOLEAN DEFAULT FALSE,
                    two_fa_enabled BOOLEAN DEFAULT FALSE,
                    two_fa_secret VARCHAR(32),
                    kyc_status VARCHAR(20) DEFAULT 'pending',
                    vip_level INTEGER DEFAULT 0,
                    referral_code VARCHAR(20) UNIQUE,
                    referred_by INTEGER REFERENCES users(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    login_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP
                )
            """)
            
            # Sessions table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    session_token VARCHAR(255) UNIQUE NOT NULL,
                    refresh_token VARCHAR(255) UNIQUE NOT NULL,
                    device VARCHAR(255),
                    ip_address VARCHAR(45),
                    location VARCHAR(255),
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # API Keys table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    name VARCHAR(100) NOT NULL,
                    api_key VARCHAR(64) UNIQUE NOT NULL,
                    api_secret VARCHAR(64) NOT NULL,
                    permissions JSONB DEFAULT '[]',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    last_used TIMESTAMP
                )
            """)
            
            # Password reset tokens table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    token VARCHAR(64) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Email verification tokens table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS email_verification_tokens (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    token VARCHAR(64) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Login history table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS login_history (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    ip_address VARCHAR(45),
                    device VARCHAR(255),
                    location VARCHAR(255),
                    user_agent TEXT,
                    success BOOLEAN,
                    failure_reason VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_api_keys_key ON api_keys(api_key)")
            
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))
        raise

async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    try:
        redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
        await redis_client.ping()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.error("Redis connection failed", error=str(e))
        raise

# Startup and shutdown events
@app.on_event("startup")
async def startup():
    await init_database()
    await init_redis()
    logger.info("User Authentication Service started")

@app.on_event("shutdown")
async def shutdown():
    if db_pool:
        await db_pool.close()
    if redis_client:
        await redis_client.close()
    logger.info("User Authentication Service stopped")

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "user-authentication-service",
        "timestamp": datetime.utcnow().isoformat()
    }

# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8200)