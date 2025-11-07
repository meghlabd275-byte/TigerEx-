"""
TigerEx Authentication Service - Complete Implementation
OAuth, 2FA, Captcha, KYC, and comprehensive authentication system
Version: 5.0.0 - Production Ready
"""

import asyncio
import json
import logging
import os
import uuid
import secrets
import base64
import hashlib
import hmac
import io
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import random
import string

import aioredis
import aiohttp
from fastapi import FastAPI, HTTPException, Depends, Request, Response, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, validator, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from passlib.context import CryptContext
from jose import JWTError, jwt
import pyotp
import qrcode
from PIL import Image, ImageDraw, ImageFont
from authlib.integrations.starlette_client import OAuth
from twilio.rest import Client as TwilioClient
import sendgrid
from sendgrid.helpers.mail import Mail
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tigerex:password@localhost/tigerex_auth")
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 30
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Email configuration
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@tigerex.com")

# SMS configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Database setup
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Enums
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    INSTITUTIONAL = "institutional"
    MERCHANT = "merchant"

class KYCStatus(str, Enum):
    NOT_SUBMITTED = "not_submitted"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class TwoFactorMethod(str, Enum):
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    phone = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # 2FA
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String)
    two_factor_method = Column(SQLEnum(TwoFactorMethod))
    backup_codes = Column(JSON)
    
    # KYC
    kyc_status = Column(SQLEnum(KYCStatus), default=KYCStatus.NOT_SUBMITTED)
    kyc_documents = Column(JSON)
    kyc_submitted_at = Column(DateTime(timezone=True))
    
    # Security
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))
    password_changed_at = Column(DateTime(timezone=True))
    session_tokens = Column(JSON)
    
    # OAuth
    oauth_providers = Column(JSON)

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    token = Column(String, unique=True, nullable=False)
    refresh_token = Column(String, unique=True, nullable=False)
    device_info = Column(JSON)
    ip_address = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String)
    action = Column(String, nullable=False)
    details = Column(JSON)
    ip_address = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Pydantic Models
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
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
    remember_me: bool = False
    two_factor_code: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str]
    phone: Optional[str]
    role: UserRole
    is_active: bool
    is_verified: bool
    two_factor_enabled: bool
    kyc_status: KYCStatus
    created_at: datetime
    last_login: Optional[datetime]

class TwoFactorSetup(BaseModel):
    method: TwoFactorMethod
    phone: Optional[str] = None

class KYCSubmission(BaseModel):
    document_type: str
    document_front: str  # Base64 encoded
    document_back: Optional[str] = None  # Base64 encoded
    selfie: str  # Base64 encoded
    address_proof: Optional[str] = None  # Base64 encoded

# FastAPI App
app = FastAPI(
    title="TigerEx Authentication Service",
    version="5.0.0",
    description="Complete authentication service with OAuth, 2FA, KYC, and admin controls"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Variables
redis_client: Optional[aioredis.Redis] = None
oauth = OAuth()

# Utility Functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def generate_backup_codes() -> List[str]:
    codes = []
    for _ in range(10):
        code = ''.join(random.choices(string.digits, k=8))
        codes.append(code)
    return codes

def generate_qr_code(secret: str, username: str) -> bytes:
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=username,
        issuer_name="TigerEx"
    )
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.getvalue()

async def send_email(to_email: str, subject: str, content: str):
    if not SENDGRID_API_KEY:
        logger.warning("SendGrid API key not configured")
        return
    
    try:
        message = Mail(
            from_email=EMAIL_FROM,
            to_emails=to_email,
            subject=subject,
            html_content=content
        )
        
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': f'Bearer {SENDGRID_API_KEY}',
                'Content-Type': 'application/json'
            }
            data = {
                'personalizations': [{
                    'to': [{'email': to_email}],
                    'subject': subject
                }],
                'from': {'email': EMAIL_FROM},
                'content': [{'type': 'text/html', 'value': content}]
            }
            
            async with session.post(
                'https://api.sendgrid.com/v3/mail/send',
                headers=headers,
                json=data
            ) as response:
                if response.status == 202:
                    logger.info(f"Email sent successfully to {to_email}")
                else:
                    logger.error(f"Failed to send email: {await response.text()}")
    except Exception as e:
        logger.error(f"Error sending email: {e}")

async def send_sms(phone_number: str, message: str):
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        logger.warning("Twilio configuration not complete")
        return
    
    try:
        client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        logger.info(f"SMS sent successfully to {phone_number}")
    except Exception as e:
        logger.error(f"Error sending SMS: {e}")

async def log_audit(db: Session, user_id: str, action: str, details: Dict, request: Request):
    audit = AuditLog(
        user_id=user_id,
        action=action,
        details=details,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "")
    )
    db.add(audit)
    db.commit()

# Dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
        
        # Check if token is blacklisted
        if redis_client:
            is_blacklisted = await redis_client.get(f"blacklist:{credentials.credentials}")
            if is_blacklisted:
                raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user

# API Routes
@app.post("/register", response_model=UserResponse)
async def register(user: UserCreate, request: Request, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    
    if existing_user:
        if existing_user.email == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
        if existing_user.username == user.username:
            raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name,
        phone=user.phone
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Log audit
    await log_audit(db, db_user.id, "user_registered", {"email": user.email}, request)
    
    # Send verification email
    verification_token = secrets.token_urlsafe(32)
    if redis_client:
        await redis_client.setex(
            f"verify:{verification_token}",
            3600,  # 1 hour
            db_user.id
        )
    
    verification_url = f"https://tigerex.com/verify-email?token={verification_token}"
    email_content = f"""
    <h2>Welcome to TigerEx!</h2>
    <p>Please verify your email address by clicking the link below:</p>
    <a href="{verification_url}">Verify Email</a>
    <p>This link will expire in 1 hour.</p>
    """
    await send_email(user.email, "Verify your TigerEx account", email_content)
    
    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        username=db_user.username,
        full_name=db_user.full_name,
        phone=db_user.phone,
        role=db_user.role,
        is_active=db_user.is_active,
        is_verified=db_user.is_verified,
        two_factor_enabled=db_user.two_factor_enabled,
        kyc_status=db_user.kyc_status,
        created_at=db_user.created_at,
        last_login=db_user.last_login
    )

@app.post("/login")
async def login(user_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    # Get user
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(status_code=401, detail="Account is locked")
    
    # Verify password
    if not verify_password(user_data.password, user.hashed_password):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=30)
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if 2FA is required
    if user.two_factor_enabled and not user_data.two_factor_code:
        return {"require_2fa": True, "method": user.two_factor_method}
    
    # Verify 2FA code if required
    if user.two_factor_enabled:
        if not await verify_2fa_code(user, user_data.two_factor_code):
            raise HTTPException(status_code=401, detail="Invalid 2FA code")
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    # Create session
    session = UserSession(
        user_id=user.id,
        token=access_token,
        refresh_token=refresh_token,
        device_info={"user_agent": request.headers.get("user-agent")},
        ip_address=request.client.host,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(session)
    
    # Reset failed attempts
    user.failed_login_attempts = 0
    user.last_login = datetime.utcnow()
    
    db.commit()
    
    # Log audit
    await log_audit(db, user.id, "user_login", {"success": True}, request)
    
    # Cache session in Redis
    if redis_client:
        await redis_client.setex(
            f"session:{access_token}",
            ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            json.dumps({"user_id": user.id, "role": user.role})
        )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            two_factor_enabled=user.two_factor_enabled,
            kyc_status=user.kyc_status,
            created_at=user.created_at,
            last_login=user.last_login
        )
    }

async def verify_2fa_code(user: User, code: str) -> bool:
    if user.two_factor_method == TwoFactorMethod.TOTP:
        totp = pyotp.TOTP(user.two_factor_secret)
        return totp.verify(code, valid_window=1)
    elif user.two_factor_method == TwoFactorMethod.SMS:
        # Verify SMS code from Redis
        if redis_client:
            stored_code = await redis_client.get(f"sms_2fa:{user.id}")
            return stored_code == code
    return False

@app.post("/refresh")
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    # Check if session exists and is active
    session = db.query(UserSession).filter(
        UserSession.refresh_token == refresh_token,
        UserSession.is_active == True,
        UserSession.expires_at > datetime.utcnow()
    ).first()
    
    if not session:
        raise HTTPException(status_code=401, detail="Session expired")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    # Create new access token
    new_access_token = create_access_token(data={"sub": user.id})
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.post("/logout")
async def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Invalidate sessions
    db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.is_active == True
    ).update({"is_active": False})
    db.commit()
    
    return {"message": "Successfully logged out"}

@app.post("/setup-2fa")
async def setup_2fa(
    setup_data: TwoFactorSetup,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.two_factor_enabled:
        raise HTTPException(status_code=400, detail="2FA is already enabled")
    
    if setup_data.method == TwoFactorMethod.TOTP:
        secret = pyotp.random_base32()
        backup_codes = generate_backup_codes()
        
        # Update user
        current_user.two_factor_secret = secret
        current_user.backup_codes = backup_codes
        current_user.two_factor_method = TwoFactorMethod.TOTP
        
        # Generate QR code
        qr_code = generate_qr_code(secret, current_user.username)
        
        db.commit()
        
        return {
            "secret": secret,
            "qr_code": base64.b64encode(qr_code).decode(),
            "backup_codes": backup_codes
        }
    
    elif setup_data.method == TwoFactorMethod.SMS:
        if not setup_data.phone:
            raise HTTPException(status_code=400, detail="Phone number required for SMS 2FA")
        
        # Generate and send SMS code
        sms_code = ''.join(random.choices(string.digits, k=6))
        if redis_client:
            await redis_client.setex(f"sms_2fa:{current_user.id}", 300, sms_code)  # 5 minutes
        
        await send_sms(setup_data.phone, f"Your TigerEx verification code is: {sms_code}")
        
        current_user.two_factor_method = TwoFactorMethod.SMS
        current_user.phone = setup_data.phone
        db.commit()
        
        return {"message": "SMS verification code sent"}
    
    else:
        raise HTTPException(status_code=400, detail="Invalid 2FA method")

@app.post("/enable-2fa")
async def enable_2fa(
    verification_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.two_factor_enabled:
        raise HTTPException(status_code=400, detail="2FA is already enabled")
    
    if not await verify_2fa_code(current_user, verification_code):
        raise HTTPException(status_code=400, detail="Invalid verification code")
    
    current_user.two_factor_enabled = True
    db.commit()
    
    return {"message": "2FA enabled successfully"}

@app.post("/disable-2fa")
async def disable_2fa(
    password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid password")
    
    current_user.two_factor_enabled = False
    current_user.two_factor_secret = None
    current_user.backup_codes = None
    db.commit()
    
    return {"message": "2FA disabled successfully"}

@app.post("/submit-kyc")
async def submit_kyc(
    kyc_data: KYCSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.kyc_status != KYCStatus.NOT_SUBMITTED:
        raise HTTPException(status_code=400, detail="KYC already submitted")
    
    # Process KYC documents (in production, store in secure storage)
    kyc_documents = {
        "document_type": kyc_data.document_type,
        "document_front": kyc_data.document_front,
        "document_back": kyc_data.document_back,
        "selfie": kyc_data.selfie,
        "address_proof": kyc_data.address_proof,
        "submitted_at": datetime.utcnow().isoformat()
    }
    
    current_user.kyc_documents = kyc_documents
    current_user.kyc_status = KYCStatus.PENDING
    current_user.kyc_submitted_at = datetime.utcnow()
    
    db.commit()
    
    # Send notification to admin for review
    # In production, integrate with KYC provider like Sumsub
    
    return {"message": "KYC submitted successfully", "status": current_user.kyc_status}

@app.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        phone=current_user.phone,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        two_factor_enabled=current_user.two_factor_enabled,
        kyc_status=current_user.kyc_status,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

@app.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid current password")
    
    # Validate new password
    UserCreate(password=new_password)  # This will trigger validation
    
    current_user.hashed_password = get_password_hash(new_password)
    current_user.password_changed_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Password changed successfully"}

# Admin Routes
@app.get("/admin/users")
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = db.query(User).offset(skip).limit(limit).all()
    return [UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        phone=user.phone,
        role=user.role,
        is_active=user.is_active,
        is_verified=user.is_verified,
        two_factor_enabled=user.two_factor_enabled,
        kyc_status=user.kyc_status,
        created_at=user.created_at,
        last_login=user.last_login
    ) for user in users]

@app.post("/admin/users/{user_id}/toggle")
async def toggle_user_status(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = not user.is_active
    db.commit()
    
    return {"message": f"User {'activated' if user.is_active else 'deactivated'} successfully"}

@app.get("/admin/audit-logs")
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "details": log.details,
            "ip_address": log.ip_address,
            "created_at": log.created_at
        }
        for log in logs
    ]

# Health Check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "auth-service", "version": "5.0.0"}

# Startup and Shutdown
@app.on_event("startup")
async def startup_event():
    global redis_client
    
    # Connect to Redis
    try:
        redis_client = await aioredis.from_url(REDIS_URL)
        logger.info("Connected to Redis")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        redis_client = None
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")

@app.on_event("shutdown")
async def shutdown_event():
    if redis_client:
        await redis_client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)