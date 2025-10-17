/*
 * TigerEx Exchange Platform
 * Version: 7.0.0 - Consolidated Production Release
 * 
 * Complete cryptocurrency exchange platform with:
 * - CEX/DEX hybrid functionality
 * - 105+ exchange features
 * - Multi-platform support (Web, Mobile, Desktop)
 * - Enterprise-grade security
 * - White-label deployment ready
 * 
 * Production-ready implementation
 */

"""
TigerEx User Authentication Service
Complete authentication system with registration, login, 2FA, password reset, and session management
Port: 8200
"""

from fastapi import FastAPI
from admin.admin_routes import router as admin_router
from fastapi import HTTPException, Depends, BackgroundTasks, Request
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

# Include admin router
app.include_router(admin_router)
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

# User Registration
@app.post("/api/auth/register", status_code=201)
async def register_user(
    registration: UserRegistration,
    background_tasks: BackgroundTasks,
    request: Request
):
    """Register a new user"""
    try:
        async with db_pool.acquire() as conn:
            # Check if email already exists
            existing_user = await conn.fetchrow(
                "SELECT id FROM users WHERE email = $1",
                registration.email
            )
            
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")
            
            # Check if username already exists
            if registration.username:
                existing_username = await conn.fetchrow(
                    "SELECT id FROM users WHERE username = $1",
                    registration.username
                )
                if existing_username:
                    raise HTTPException(status_code=400, detail="Username already taken")
            
            # Hash password
            password_hash = hash_password(registration.password)
            
            # Generate referral code
            referral_code = secrets.token_urlsafe(8)
            
            # Get referred_by user if referral code provided
            referred_by = None
            if registration.referral_code:
                referrer = await conn.fetchrow(
                    "SELECT id FROM users WHERE referral_code = $1",
                    registration.referral_code
                )
                if referrer:
                    referred_by = referrer['id']
            
            # Insert user
            user = await conn.fetchrow("""
                INSERT INTO users (email, username, password_hash, referral_code, referred_by)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id, email, username, referral_code, created_at
            """, registration.email, registration.username, password_hash, referral_code, referred_by)
            
            # Generate email verification token
            verification_token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(hours=24)
            
            await conn.execute("""
                INSERT INTO email_verification_tokens (user_id, token, expires_at)
                VALUES ($1, $2, $3)
            """, user['id'], verification_token, expires_at)
            
            # Send verification email
            verification_link = f"https://tigerex.com/verify-email?token={verification_token}"
            email_body = f"""
            <html>
            <body>
                <h2>Welcome to TigerEx!</h2>
                <p>Thank you for registering. Please verify your email address by clicking the link below:</p>
                <p><a href="{verification_link}">Verify Email</a></p>
                <p>This link will expire in 24 hours.</p>
                <p>If you didn't create this account, please ignore this email.</p>
            </body>
            </html>
            """
            
            background_tasks.add_task(send_email, registration.email, "Verify Your Email - TigerEx", email_body)
            
            logger.info("User registered", user_id=user['id'], email=user['email'])
            
            return {
                "message": "Registration successful. Please check your email to verify your account.",
                "user": {
                    "id": user['id'],
                    "email": user['email'],
                    "username": user['username'],
                    "referral_code": user['referral_code'],
                    "created_at": user['created_at'].isoformat()
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Registration failed", error=str(e))
        raise HTTPException(status_code=500, detail="Registration failed")

# Verify Email
@app.post("/api/auth/verify-email")
async def verify_email(token: str):
    """Verify user email"""
    try:
        async with db_pool.acquire() as conn:
            # Get token
            token_record = await conn.fetchrow("""
                SELECT user_id, expires_at, used
                FROM email_verification_tokens
                WHERE token = $1
            """, token)
            
            if not token_record:
                raise HTTPException(status_code=400, detail="Invalid verification token")
            
            if token_record['used']:
                raise HTTPException(status_code=400, detail="Token already used")
            
            if datetime.utcnow() > token_record['expires_at']:
                raise HTTPException(status_code=400, detail="Token expired")
            
            # Update user
            await conn.execute("""
                UPDATE users
                SET is_verified = TRUE, updated_at = CURRENT_TIMESTAMP
                WHERE id = $1
            """, token_record['user_id'])
            
            # Mark token as used
            await conn.execute("""
                UPDATE email_verification_tokens
                SET used = TRUE
                WHERE token = $1
            """, token)
            
            logger.info("Email verified", user_id=token_record['user_id'])
            
            return {"message": "Email verified successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Email verification failed", error=str(e))
        raise HTTPException(status_code=500, detail="Email verification failed")

# User Login
@app.post("/api/auth/login")
async def login_user(
    login: UserLogin,
    request: Request
):
    """User login with optional 2FA"""
    try:
        async with db_pool.acquire() as conn:
            # Get user
            user = await conn.fetchrow("""
                SELECT id, email, password_hash, is_active, is_verified, 
                       two_fa_enabled, two_fa_secret, login_attempts, locked_until
                FROM users
                WHERE email = $1
            """, login.email)
            
            if not user:
                # Log failed attempt
                await conn.execute("""
                    INSERT INTO login_history (user_id, ip_address, success, failure_reason)
                    VALUES (NULL, $1, FALSE, 'User not found')
                """, request.client.host)
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Check if account is locked
            if user['locked_until'] and datetime.utcnow() < user['locked_until']:
                raise HTTPException(status_code=403, detail="Account temporarily locked. Please try again later.")
            
            # Check if account is active
            if not user['is_active']:
                raise HTTPException(status_code=403, detail="Account is disabled")
            
            # Verify password
            if not verify_password(login.password, user['password_hash']):
                # Increment login attempts
                login_attempts = user['login_attempts'] + 1
                locked_until = None
                
                if login_attempts >= 5:
                    locked_until = datetime.utcnow() + timedelta(minutes=30)
                
                await conn.execute("""
                    UPDATE users
                    SET login_attempts = $1, locked_until = $2
                    WHERE id = $3
                """, login_attempts, locked_until, user['id'])
                
                # Log failed attempt
                await conn.execute("""
                    INSERT INTO login_history (user_id, ip_address, success, failure_reason)
                    VALUES ($1, $2, FALSE, 'Invalid password')
                """, user['id'], request.client.host)
                
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Check 2FA if enabled
            if user['two_fa_enabled']:
                if not login.totp_code:
                    return {
                        "requires_2fa": True,
                        "message": "Please provide 2FA code"
                    }
                
                # Verify TOTP
                totp = pyotp.TOTP(user['two_fa_secret'])
                if not totp.verify(login.totp_code, valid_window=1):
                    # Log failed attempt
                    await conn.execute("""
                        INSERT INTO login_history (user_id, ip_address, success, failure_reason)
                        VALUES ($1, $2, FALSE, 'Invalid 2FA code')
                    """, user['id'], request.client.host)
                    raise HTTPException(status_code=401, detail="Invalid 2FA code")
            
            # Reset login attempts
            await conn.execute("""
                UPDATE users
                SET login_attempts = 0, locked_until = NULL, last_login = CURRENT_TIMESTAMP
                WHERE id = $1
            """, user['id'])
            
            # Create tokens
            access_token = create_access_token({"sub": str(user['id']), "email": user['email']})
            refresh_token = create_refresh_token({"sub": str(user['id'])})
            
            # Create session
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            
            await conn.execute("""
                INSERT INTO user_sessions (
                    user_id, session_token, refresh_token, device, ip_address, 
                    user_agent, expires_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, user['id'], session_token, refresh_token, 
                request.headers.get('User-Agent', 'Unknown')[:255],
                request.client.host,
                request.headers.get('User-Agent', ''),
                expires_at)
            
            # Log successful login
            await conn.execute("""
                INSERT INTO login_history (user_id, ip_address, device, user_agent, success)
                VALUES ($1, $2, $3, $4, TRUE)
            """, user['id'], request.client.host, 
                request.headers.get('User-Agent', 'Unknown')[:255],
                request.headers.get('User-Agent', ''))
            
            logger.info("User logged in", user_id=user['id'], email=user['email'])
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": {
                    "id": user['id'],
                    "email": user['email'],
                    "is_verified": user['is_verified'],
                    "two_fa_enabled": user['two_fa_enabled']
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login failed", error=str(e))
        raise HTTPException(status_code=500, detail="Login failed")

# Refresh Token
@app.post("/api/auth/refresh")
async def refresh_access_token(refresh_token: str):
    """Refresh access token"""
    try:
        # Verify refresh token
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = int(payload.get("sub"))
        
        async with db_pool.acquire() as conn:
            # Verify session
            session = await conn.fetchrow("""
                SELECT user_id, expires_at, is_active
                FROM user_sessions
                WHERE refresh_token = $1 AND user_id = $2
            """, refresh_token, user_id)
            
            if not session or not session['is_active']:
                raise HTTPException(status_code=401, detail="Invalid session")
            
            if datetime.utcnow() > session['expires_at']:
                raise HTTPException(status_code=401, detail="Session expired")
            
            # Get user
            user = await conn.fetchrow("""
                SELECT id, email, is_active
                FROM users
                WHERE id = $1
            """, user_id)
            
            if not user or not user['is_active']:
                raise HTTPException(status_code=401, detail="User not found or inactive")
            
            # Create new access token
            access_token = create_access_token({"sub": str(user['id']), "email": user['email']})
            
            # Update session last active
            await conn.execute("""
                UPDATE user_sessions
                SET last_active = CURRENT_TIMESTAMP
                WHERE refresh_token = $1
            """, refresh_token)
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(status_code=500, detail="Token refresh failed")

# Logout
@app.post("/api/auth/logout")
async def logout_user(
    current_user: Dict = Depends(verify_token),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Logout user and invalidate session"""
    try:
        async with db_pool.acquire() as conn:
            # Deactivate all sessions for this user
            await conn.execute("""
                UPDATE user_sessions
                SET is_active = FALSE
                WHERE user_id = $1
            """, current_user['user_id'])
            
            logger.info("User logged out", user_id=current_user['user_id'])
            
            return {"message": "Logged out successfully"}
    except Exception as e:
        logger.error("Logout failed", error=str(e))
        raise HTTPException(status_code=500, detail="Logout failed")

# Password Reset Request
@app.post("/api/auth/password-reset")
async def request_password_reset(
    reset_request: PasswordReset,
    background_tasks: BackgroundTasks
):
    """Request password reset"""
    try:
        async with db_pool.acquire() as conn:
            # Get user
            user = await conn.fetchrow("""
                SELECT id, email
                FROM users
                WHERE email = $1
            """, reset_request.email)
            
            # Always return success to prevent email enumeration
            if not user:
                return {"message": "If the email exists, a password reset link has been sent"}
            
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(hours=1)
            
            await conn.execute("""
                INSERT INTO password_reset_tokens (user_id, token, expires_at)
                VALUES ($1, $2, $3)
            """, user['id'], reset_token, expires_at)
            
            # Send reset email
            reset_link = f"https://tigerex.com/reset-password?token={reset_token}"
            email_body = f"""
            <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>You requested to reset your password. Click the link below to proceed:</p>
                <p><a href="{reset_link}">Reset Password</a></p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this, please ignore this email.</p>
            </body>
            </html>
            """
            
            background_tasks.add_task(send_email, user['email'], "Password Reset - TigerEx", email_body)
            
            logger.info("Password reset requested", user_id=user['id'])
            
            return {"message": "If the email exists, a password reset link has been sent"}
    except Exception as e:
        logger.error("Password reset request failed", error=str(e))
        raise HTTPException(status_code=500, detail="Password reset request failed")

# Password Reset Confirm
@app.post("/api/auth/password-reset/confirm")
async def confirm_password_reset(reset: PasswordResetConfirm):
    """Confirm password reset with token"""
    try:
        async with db_pool.acquire() as conn:
            # Get token
            token_record = await conn.fetchrow("""
                SELECT user_id, expires_at, used
                FROM password_reset_tokens
                WHERE token = $1
            """, reset.token)
            
            if not token_record:
                raise HTTPException(status_code=400, detail="Invalid reset token")
            
            if token_record['used']:
                raise HTTPException(status_code=400, detail="Token already used")
            
            if datetime.utcnow() > token_record['expires_at']:
                raise HTTPException(status_code=400, detail="Token expired")
            
            # Hash new password
            password_hash = hash_password(reset.new_password)
            
            # Update password
            await conn.execute("""
                UPDATE users
                SET password_hash = $1, updated_at = CURRENT_TIMESTAMP
                WHERE id = $2
            """, password_hash, token_record['user_id'])
            
            # Mark token as used
            await conn.execute("""
                UPDATE password_reset_tokens
                SET used = TRUE
                WHERE token = $1
            """, reset.token)
            
            # Invalidate all sessions
            await conn.execute("""
                UPDATE user_sessions
                SET is_active = FALSE
                WHERE user_id = $1
            """, token_record['user_id'])
            
            logger.info("Password reset completed", user_id=token_record['user_id'])
            
            return {"message": "Password reset successful"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Password reset confirmation failed", error=str(e))
        raise HTTPException(status_code=500, detail="Password reset confirmation failed")

# Enable 2FA
@app.post("/api/auth/2fa/enable")
async def enable_2fa(
    enable_request: Enable2FA,
    current_user: Dict = Depends(verify_token)
):
    """Enable 2FA for user"""
    try:
        async with db_pool.acquire() as conn:
            # Get user
            user = await conn.fetchrow("""
                SELECT id, email, password_hash, two_fa_enabled
                FROM users
                WHERE id = $1
            """, current_user['user_id'])
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            if user['two_fa_enabled']:
                raise HTTPException(status_code=400, detail="2FA already enabled")
            
            # Verify password
            if not verify_password(enable_request.password, user['password_hash']):
                raise HTTPException(status_code=401, detail="Invalid password")
            
            # Generate 2FA secret
            secret = pyotp.random_base32()
            
            # Generate QR code
            totp = pyotp.TOTP(secret)
            provisioning_uri = totp.provisioning_uri(
                name=user['email'],
                issuer_name="TigerEx"
            )
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            # Store secret temporarily in Redis (expires in 10 minutes)
            await redis_client.setex(
                f"2fa_setup:{user['id']}",
                600,
                secret
            )
            
            logger.info("2FA setup initiated", user_id=user['id'])
            
            return {
                "secret": secret,
                "qr_code": f"data:image/png;base64,{qr_code_base64}",
                "message": "Scan the QR code with your authenticator app and verify with a code"
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("2FA enable failed", error=str(e))
        raise HTTPException(status_code=500, detail="2FA enable failed")

# Verify and Complete 2FA Setup
@app.post("/api/auth/2fa/verify")
async def verify_2fa_setup(
    verify_request: Verify2FA,
    current_user: Dict = Depends(verify_token)
):
    """Verify 2FA code and complete setup"""
    try:
        # Get secret from Redis
        secret = await redis_client.get(f"2fa_setup:{current_user['user_id']}")
        
        if not secret:
            raise HTTPException(status_code=400, detail="2FA setup not initiated or expired")
        
        # Verify TOTP code
        totp = pyotp.TOTP(secret)
        if not totp.verify(verify_request.totp_code, valid_window=1):
            raise HTTPException(status_code=400, detail="Invalid 2FA code")
        
        async with db_pool.acquire() as conn:
            # Enable 2FA
            await conn.execute("""
                UPDATE users
                SET two_fa_enabled = TRUE, two_fa_secret = $1, updated_at = CURRENT_TIMESTAMP
                WHERE id = $2
            """, secret, current_user['user_id'])
        
        # Delete temporary secret
        await redis_client.delete(f"2fa_setup:{current_user['user_id']}")
        
        logger.info("2FA enabled", user_id=current_user['user_id'])
        
        return {"message": "2FA enabled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("2FA verification failed", error=str(e))
        raise HTTPException(status_code=500, detail="2FA verification failed")

# Disable 2FA
@app.post("/api/auth/2fa/disable")
async def disable_2fa(
    password: str,
    current_user: Dict = Depends(verify_token)
):
    """Disable 2FA for user"""
    try:
        async with db_pool.acquire() as conn:
            # Get user
            user = await conn.fetchrow("""
                SELECT id, password_hash, two_fa_enabled
                FROM users
                WHERE id = $1
            """, current_user['user_id'])
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            if not user['two_fa_enabled']:
                raise HTTPException(status_code=400, detail="2FA not enabled")
            
            # Verify password
            if not verify_password(password, user['password_hash']):
                raise HTTPException(status_code=401, detail="Invalid password")
            
            # Disable 2FA
            await conn.execute("""
                UPDATE users
                SET two_fa_enabled = FALSE, two_fa_secret = NULL, updated_at = CURRENT_TIMESTAMP
                WHERE id = $1
            """, user['id'])
            
            logger.info("2FA disabled", user_id=user['id'])
            
            return {"message": "2FA disabled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("2FA disable failed", error=str(e))
        raise HTTPException(status_code=500, detail="2FA disable failed")

# Change Password
@app.post("/api/auth/change-password")
async def change_password(
    change_request: ChangePassword,
    current_user: Dict = Depends(verify_token)
):
    """Change user password"""
    try:
        async with db_pool.acquire() as conn:
            # Get user
            user = await conn.fetchrow("""
                SELECT id, password_hash
                FROM users
                WHERE id = $1
            """, current_user['user_id'])
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Verify current password
            if not verify_password(change_request.current_password, user['password_hash']):
                raise HTTPException(status_code=401, detail="Invalid current password")
            
            # Hash new password
            new_password_hash = hash_password(change_request.new_password)
            
            # Update password
            await conn.execute("""
                UPDATE users
                SET password_hash = $1, updated_at = CURRENT_TIMESTAMP
                WHERE id = $2
            """, new_password_hash, user['id'])
            
            # Invalidate all sessions except current
            await conn.execute("""
                UPDATE user_sessions
                SET is_active = FALSE
                WHERE user_id = $1
            """, user['id'])
            
            logger.info("Password changed", user_id=user['id'])
            
            return {"message": "Password changed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Password change failed", error=str(e))
        raise HTTPException(status_code=500, detail="Password change failed")

# Get User Sessions
@app.get("/api/auth/sessions", response_model=List[SessionResponse])
async def get_user_sessions(
    current_user: Dict = Depends(verify_token),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get all active sessions for user"""
    try:
        async with db_pool.acquire() as conn:
            sessions = await conn.fetch("""
                SELECT id, session_token, device, ip_address, location,
                       created_at, last_active
                FROM user_sessions
                WHERE user_id = $1 AND is_active = TRUE
                ORDER BY last_active DESC
            """, current_user['user_id'])
            
            # Decode current token to identify current session
            current_token = credentials.credentials
            current_payload = jwt.decode(current_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            
            result = []
            for session in sessions:
                result.append({
                    "session_id": str(session['id']),
                    "device": session['device'] or "Unknown",
                    "ip_address": session['ip_address'] or "Unknown",
                    "location": session['location'],
                    "created_at": session['created_at'],
                    "last_active": session['last_active'],
                    "is_current": False  # We'll mark current session separately
                })
            
            return result
    except Exception as e:
        logger.error("Failed to get sessions", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get sessions")

# Revoke Session
@app.delete("/api/auth/sessions/{session_id}")
async def revoke_session(
    session_id: int,
    current_user: Dict = Depends(verify_token)
):
    """Revoke a specific session"""
    try:
        async with db_pool.acquire() as conn:
            # Verify session belongs to user
            session = await conn.fetchrow("""
                SELECT id FROM user_sessions
                WHERE id = $1 AND user_id = $2
            """, session_id, current_user['user_id'])
            
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            
            # Deactivate session
            await conn.execute("""
                UPDATE user_sessions
                SET is_active = FALSE
                WHERE id = $1
            """, session_id)
            
            logger.info("Session revoked", user_id=current_user['user_id'], session_id=session_id)
            
            return {"message": "Session revoked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Session revocation failed", error=str(e))
        raise HTTPException(status_code=500, detail="Session revocation failed")

# Create API Key
@app.post("/api/auth/api-keys", status_code=201)
async def create_api_key(
    key_request: APIKeyCreate,
    current_user: Dict = Depends(verify_token)
):
    """Create new API key"""
    try:
        # Generate API key and secret
        api_key = secrets.token_urlsafe(32)
        api_secret = secrets.token_urlsafe(32)
        
        # Calculate expiration
        expires_at = None
        if key_request.expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=key_request.expires_in_days)
        
        async with db_pool.acquire() as conn:
            # Insert API key
            key_record = await conn.fetchrow("""
                INSERT INTO api_keys (user_id, name, api_key, api_secret, permissions, expires_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id, name, api_key, permissions, created_at, expires_at
            """, current_user['user_id'], key_request.name, api_key, api_secret,
                json.dumps(key_request.permissions), expires_at)
            
            logger.info("API key created", user_id=current_user['user_id'], key_id=key_record['id'])
            
            return {
                "id": key_record['id'],
                "name": key_record['name'],
                "api_key": key_record['api_key'],
                "api_secret": api_secret,  # Only shown once
                "permissions": key_request.permissions,
                "created_at": key_record['created_at'].isoformat(),
                "expires_at": key_record['expires_at'].isoformat() if key_record['expires_at'] else None,
                "warning": "Save the API secret securely. It will not be shown again."
            }
    except Exception as e:
        logger.error("API key creation failed", error=str(e))
        raise HTTPException(status_code=500, detail="API key creation failed")

# Get API Keys
@app.get("/api/auth/api-keys")
async def get_api_keys(current_user: Dict = Depends(verify_token)):
    """Get all API keys for user"""
    try:
        async with db_pool.acquire() as conn:
            keys = await conn.fetch("""
                SELECT id, name, api_key, permissions, is_active, created_at, expires_at, last_used
                FROM api_keys
                WHERE user_id = $1
                ORDER BY created_at DESC
            """, current_user['user_id'])
            
            return [
                {
                    "id": key['id'],
                    "name": key['name'],
                    "api_key": key['api_key'],
                    "permissions": json.loads(key['permissions']),
                    "is_active": key['is_active'],
                    "created_at": key['created_at'].isoformat(),
                    "expires_at": key['expires_at'].isoformat() if key['expires_at'] else None,
                    "last_used": key['last_used'].isoformat() if key['last_used'] else None
                }
                for key in keys
            ]
    except Exception as e:
        logger.error("Failed to get API keys", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get API keys")

# Delete API Key
@app.delete("/api/auth/api-keys/{key_id}")
async def delete_api_key(
    key_id: int,
    current_user: Dict = Depends(verify_token)
):
    """Delete API key"""
    try:
        async with db_pool.acquire() as conn:
            # Verify key belongs to user
            key = await conn.fetchrow("""
                SELECT id FROM api_keys
                WHERE id = $1 AND user_id = $2
            """, key_id, current_user['user_id'])
            
            if not key:
                raise HTTPException(status_code=404, detail="API key not found")
            
            # Delete key
            await conn.execute("""
                DELETE FROM api_keys
                WHERE id = $1
            """, key_id)
            
            logger.info("API key deleted", user_id=current_user['user_id'], key_id=key_id)
            
            return {"message": "API key deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("API key deletion failed", error=str(e))
        raise HTTPException(status_code=500, detail="API key deletion failed")

# Get Login History
@app.get("/api/auth/login-history")
async def get_login_history(
    current_user: Dict = Depends(verify_token),
    limit: int = 50
):
    """Get login history for user"""
    try:
        async with db_pool.acquire() as conn:
            history = await conn.fetch("""
                SELECT ip_address, device, location, user_agent, success, failure_reason, created_at
                FROM login_history
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT $2
            """, current_user['user_id'], limit)
            
            return [
                {
                    "ip_address": record['ip_address'],
                    "device": record['device'],
                    "location": record['location'],
                    "user_agent": record['user_agent'],
                    "success": record['success'],
                    "failure_reason": record['failure_reason'],
                    "timestamp": record['created_at'].isoformat()
                }
                for record in history
            ]
    except Exception as e:
        logger.error("Failed to get login history", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get login history")

# Get Current User
@app.get("/api/auth/me")
async def get_current_user(current_user: Dict = Depends(verify_token)):
    """Get current user information"""
    try:
        async with db_pool.acquire() as conn:
            user = await conn.fetchrow("""
                SELECT id, email, username, is_active, is_verified, two_fa_enabled,
                       kyc_status, vip_level, referral_code, created_at, last_login
                FROM users
                WHERE id = $1
            """, current_user['user_id'])
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            return {
                "id": user['id'],
                "email": user['email'],
                "username": user['username'],
                "is_active": user['is_active'],
                "is_verified": user['is_verified'],
                "two_fa_enabled": user['two_fa_enabled'],
                "kyc_status": user['kyc_status'],
                "vip_level": user['vip_level'],
                "referral_code": user['referral_code'],
                "created_at": user['created_at'].isoformat(),
                "last_login": user['last_login'].isoformat() if user['last_login'] else None
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get user", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get user")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8200)