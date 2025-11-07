"""
TigerEx Enhanced Admin Panel System
Complete admin control with comprehensive user management, CRUD operations, and full platform control
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid
import hashlib
import jwt
import asyncio
import json
import csv
import io
import base64
from passlib.context import CryptContext
import redis
import asyncpg
from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Text, Integer, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.postgresql import UUID
import pandas as pd
import numpy as np

# Initialize FastAPI
app = FastAPI(
    title="TigerEx Enhanced Admin System",
    version="4.0.0",
    description="Complete admin control panel with comprehensive user management and full platform control"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "tigerex-admin-enhanced-secret-key-2025"
ALGORITHM = "HS256"

# Database Configuration
DATABASE_URL = "postgresql://tigerex:tigerex123@localhost:5432/tigerex"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis Configuration
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# ==================== MODELS ====================

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    SUPPORT = "support"
    COMPLIANCE = "compliance"
    RISK_MANAGER = "risk_manager"
    TRADER = "trader"
    USER = "user"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    RESTRICTED = "restricted"
    BANNED = "banned"

class KYCStatus(str, Enum):
    NOT_SUBMITTED = "not_submitted"
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"

class TradingStatus(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    RESTRICTED = "restricted"
    MARGIN_CALL = "margin_call"
    LIQUIDATION = "liquidation"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    role = Column(String(50), default=UserRole.USER)
    status = Column(String(50), default=UserStatus.UNVERIFIED)
    kyc_status = Column(String(50), default=KYCStatus.NOT_SUBMITTED)
    trading_status = Column(String(50), default=TradingStatus.DISABLED)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_2fa_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    login_count = Column(Integer, default=0)
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime)
    
    # Profile data
    profile_data = Column(JSON)
    preferences = Column(JSON)
    security_settings = Column(JSON)
    
    # Trading data
    trading_preferences = Column(JSON)
    risk_profile = Column(JSON)
    trading_limits = Column(JSON)

class TradingAccount(Base):
    __tablename__ = "trading_accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    account_type = Column(String(50))  # spot, margin, futures
    currency = Column(String(10))
    balance = Column(Float, default=0.0)
    frozen_balance = Column(Float, default=0.0)
    total_pnl = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class KYCDocument(Base):
    __tablename__ = "kyc_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    document_type = Column(String(50))  # passport, id_card, driver_license, proof_of_address
    document_number = Column(String(100))
    document_url = Column(Text)
    status = Column(String(50), default=KYCStatus.PENDING)
    review_notes = Column(Text)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TradingOrder(Base):
    __tablename__ = "trading_orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    symbol = Column(String(20))
    order_type = Column(String(20))  # market, limit, stop_loss, take_profit
    side = Column(String(10))  # buy, sell
    quantity = Column(Float)
    price = Column(Float)
    filled_quantity = Column(Float, default=0.0)
    status = Column(String(20))  # pending, filled, cancelled, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(100))
    resource = Column(String(100))
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# ==================== PYDANTIC MODELS ====================

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role: UserRole = UserRole.USER
    
    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    kyc_status: Optional[KYCStatus] = None
    trading_status: Optional[TradingStatus] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_2fa_enabled: Optional[bool] = None
    profile_data: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    security_settings: Optional[Dict[str, Any]] = None
    trading_preferences: Optional[Dict[str, Any]] = None
    risk_profile: Optional[Dict[str, Any]] = None
    trading_limits: Optional[Dict[str, Any]] = None

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    role: UserRole
    status: UserStatus
    kyc_status: KYCStatus
    trading_status: TradingStatus
    is_active: bool
    is_verified: bool
    is_2fa_enabled: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    login_count: int
    failed_login_attempts: int
    account_locked_until: Optional[datetime]
    profile_data: Optional[Dict[str, Any]]
    preferences: Optional[Dict[str, Any]]
    security_settings: Optional[Dict[str, Any]]
    trading_preferences: Optional[Dict[str, Any]]
    risk_profile: Optional[Dict[str, Any]]
    trading_limits: Optional[Dict[str, Any]]

class LoginRequest(BaseModel):
    username: str
    password: str
    remember_me: bool = False

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('passwords do not match')
        return v

class KYCReviewRequest(BaseModel):
    status: KYCStatus
    review_notes: Optional[str] = None

class BulkActionRequest(BaseModel):
    user_ids: List[str]
    action: str  # activate, deactivate, suspend, delete, etc.
    parameters: Optional[Dict[str, Any]] = None

class SystemConfigRequest(BaseModel):
    config_key: str
    config_value: Any
    description: Optional[str] = None

class AnalyticsRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    metrics: List[str]
    filters: Optional[Dict[str, Any]] = None

# ==================== UTILITIES ====================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def require_role(required_role: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role and current_user.role != UserRole.SUPER_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

def log_audit_event(user_id: str, action: str, resource: str, details: Dict[str, Any], ip_address: str, user_agent: str):
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db = SessionLocal()
    try:
        db.add(audit_log)
        db.commit()
    finally:
        db.close()

# ==================== ADMIN ENDPOINTS ====================

@app.post("/admin/auth/login", response_model=LoginResponse)
async def admin_login(request: LoginRequest, db: Session = Depends(get_db)):
    """Admin login endpoint"""
    user = db.query(User).filter(User.username == request.username).first()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MODERATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Update login info
    user.last_login = datetime.utcnow()
    user.login_count += 1
    user.failed_login_attempts = 0
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(hours=24 if request.remember_me else 8)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    # Log audit event
    log_audit_event(
        user_id=str(user.id),
        action="login",
        resource="admin_panel",
        details={"remember_me": request.remember_me},
        ip_address="0.0.0.0",  # Get from request
        user_agent="admin_panel"
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
        user=UserResponse.from_orm(user)
    )

@app.get("/admin/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None,
    kyc_status: Optional[KYCStatus] = None,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Get all users with filtering and pagination"""
    query = db.query(User)
    
    if search:
        query = query.filter(
            (User.email.ilike(f"%{search}%")) |
            (User.username.ilike(f"%{search}%")) |
            (User.first_name.ilike(f"%{search}%")) |
            (User.last_name.ilike(f"%{search}%"))
        )
    
    if role:
        query = query.filter(User.role == role)
    
    if status:
        query = query.filter(User.status == status)
    
    if kyc_status:
        query = query.filter(User.kyc_status == kyc_status)
    
    users = query.offset(skip).limit(limit).all()
    
    # Log audit event
    log_audit_event(
        user_id=str(current_user.id),
        action="view_users",
        resource="admin_panel",
        details={"filters": {"search": search, "role": role, "status": status, "kyc_status": kyc_status}},
        ip_address="0.0.0.0",
        user_agent="admin_panel"
    )
    
    return [UserResponse.from_orm(user) for user in users]

@app.post("/admin/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Create a new user"""
    
    # Check if email already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        role=user_data.role,
        status=UserStatus.ACTIVE if user_data.role != UserRole.USER else UserStatus.UNVERIFIED,
        is_active=True,
        is_verified=user_data.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create trading account
    trading_account = TradingAccount(
        user_id=db_user.id,
        account_type="spot",
        currency="BTC"
    )
    db.add(trading_account)
    db.commit()
    
    # Log audit event
    log_audit_event(
        user_id=str(current_user.id),
        action="create_user",
        resource="admin_panel",
        details={"created_user_id": str(db_user.id), "email": db_user.email, "role": db_user.role},
        ip_address="0.0.0.0",
        user_agent="admin_panel"
    )
    
    return UserResponse.from_orm(db_user)

@app.get("/admin/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Log audit event
    log_audit_event(
        user_id=str(current_user.id),
        action="view_user",
        resource="admin_panel",
        details={"viewed_user_id": str(user.id)},
        ip_address="0.0.0.0",
        user_agent="admin_panel"
    )
    
    return UserResponse.from_orm(user)

@app.put("/admin/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Update user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check permissions for role changes
    if user_data.role and current_user.role != UserRole.SUPER_ADMIN:
        if user_data.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super admin can assign admin roles"
            )
    
    # Update user fields
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    # Log audit event
    log_audit_event(
        user_id=str(current_user.id),
        action="update_user",
        resource="admin_panel",
        details={"updated_user_id": str(user.id), "changes": update_data},
        ip_address="0.0.0.0",
        user_agent="admin_panel"
    )
    
    return UserResponse.from_orm(user)

@app.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: Session = Depends(get_db)
):
    """Delete user (soft delete)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Soft delete
    user.is_active = False
    user.status = UserStatus.BANNED
    user.updated_at = datetime.utcnow()
    db.commit()
    
    # Log audit event
    log_audit_event(
        user_id=str(current_user.id),
        action="delete_user",
        resource="admin_panel",
        details={"deleted_user_id": str(user.id)},
        ip_address="0.0.0.0",
        user_agent="admin_panel"
    )
    
    return {"message": "User deleted successfully"}

@app.post("/admin/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: str,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Reset user password"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Generate new password
    new_password = str(uuid.uuid4())[:12]
    hashed_password = get_password_hash(new_password)
    
    user.hashed_password = hashed_password
    user.updated_at = datetime.utcnow()
    user.is_2fa_enabled = False  # Disable 2FA on password reset
    db.commit()
    
    # Log audit event
    log_audit_event(
        user_id=str(current_user.id),
        action="reset_password",
        resource="admin_panel",
        details={"reset_user_id": str(user.id)},
        ip_address="0.0.0.0",
        user_agent="admin_panel"
    )
    
    return {"message": "Password reset successfully", "new_password": new_password}

@app.post("/admin/users/bulk-action")
async def bulk_user_action(
    bulk_request: BulkActionRequest,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Perform bulk actions on users"""
    updated_count = 0
    
    for user_id in bulk_request.user_ids:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            if bulk_request.action == "activate":
                user.is_active = True
                user.status = UserStatus.ACTIVE
                updated_count += 1
            elif bulk_request.action == "deactivate":
                user.is_active = False
                user.status = UserStatus.INACTIVE
                updated_count += 1
            elif bulk_request.action == "suspend":
                user.is_active = False
                user.status = UserStatus.SUSPENDED
                updated_count += 1
            elif bulk_request.action == "verify":
                user.is_verified = True
                user.kyc_status = KYCStatus.APPROVED
                updated_count += 1
            elif bulk_request.action == "enable_trading":
                user.trading_status = TradingStatus.ENABLED
                updated_count += 1
            elif bulk_request.action == "disable_trading":
                user.trading_status = TradingStatus.DISABLED
                updated_count += 1
    
    db.commit()
    
    # Log audit event
    log_audit_event(
        user_id=str(current_user.id),
        action="bulk_action",
        resource="admin_panel",
        details={
            "action": bulk_request.action,
            "user_count": updated_count,
            "total_requested": len(bulk_request.user_ids)
        },
        ip_address="0.0.0.0",
        user_agent="admin_panel"
    )
    
    return {"message": f"Bulk action completed. {updated_count} users updated."}

@app.get("/admin/analytics/users")
async def get_user_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Get user analytics"""
    
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    # Get user statistics
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    verified_users = db.query(User).filter(User.is_verified == True).count()
    kyc_approved = db.query(User).filter(User.kyc_status == KYCStatus.APPROVED).count()
    
    # Get new users by date
    new_users_by_date = db.query(User).filter(
        User.created_at >= start_date,
        User.created_at <= end_date
    ).all()
    
    # Get users by role
    users_by_role = db.query(User.role, db.func.count(User.id)).group_by(User.role).all()
    
    # Get users by status
    users_by_status = db.query(User.status, db.func.count(User.id)).group_by(User.status).all()
    
    # Log audit event
    log_audit_event(
        user_id=str(current_user.id),
        action="view_analytics",
        resource="admin_panel",
        details={"start_date": start_date, "end_date": end_date},
        ip_address="0.0.0.0",
        user_agent="admin_panel"
    )
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "verified_users": verified_users,
        "kyc_approved": kyc_approved,
        "new_users_count": len(new_users_by_date),
        "users_by_role": dict(users_by_role),
        "users_by_status": dict(users_by_status),
        "registration_trend": [
            {
                "date": user.created_at.date().isoformat(),
                "count": 1
            } for user in new_users_by_date
        ]
    }

@app.get("/admin/system/health")
async def system_health_check(
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """Get system health status"""
    
    # Check database connection
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db_status = "healthy"
    except:
        db_status = "unhealthy"
    finally:
        db.close()
    
    # Check Redis connection
    try:
        redis_client.ping()
        redis_status = "healthy"
    except:
        redis_status = "unhealthy"
    
    # Get system metrics
    import psutil
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    
    # Log audit event
    log_audit_event(
        user_id=str(current_user.id),
        action="health_check",
        resource="admin_panel",
        details={},
        ip_address="0.0.0.0",
        user_agent="admin_panel"
    )
    
    return {
        "status": "healthy" if db_status == "healthy" and redis_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": db_status,
            "redis": redis_status,
            "api": "healthy"
        },
        "metrics": {
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "disk_usage": disk_usage
        }
    }

@app.get("/admin/export/users")
async def export_users(
    format: str = "csv",
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Export users data"""
    
    users = db.query(User).all()
    
    if format.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "ID", "Email", "Username", "First Name", "Last Name", "Phone",
            "Role", "Status", "KYC Status", "Trading Status", "Is Active",
            "Is Verified", "Created At", "Last Login", "Login Count"
        ])
        
        # Write data
        for user in users:
            writer.writerow([
                str(user.id), user.email, user.username, user.first_name,
                user.last_name, user.phone, user.role, user.status,
                user.kyc_status, user.trading_status, user.is_active,
                user.is_verified, user.created_at, user.last_login,
                user.login_count
            ])
        
        output.seek(0)
        
        # Log audit event
        log_audit_event(
            user_id=str(current_user.id),
            action="export_users",
            resource="admin_panel",
            details={"format": format},
            ip_address="0.0.0.0",
            user_agent="admin_panel"
        )
        
        return JSONResponse(
            content={"data": output.getvalue()},
            headers={"Content-Disposition": "attachment; filename=users_export.csv"}
        )
    
    elif format.lower() == "json":
        users_data = [UserResponse.from_orm(user).dict() for user in users]
        
        # Log audit event
        log_audit_event(
            user_id=str(current_user.id),
            action="export_users",
            resource="admin_panel",
            details={"format": format},
            ip_address="0.0.0.0",
            user_agent="admin_panel"
        )
        
        return JSONResponse(
            content={"users": users_data},
            headers={"Content-Disposition": "attachment; filename=users_export.json"}
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported format. Use 'csv' or 'json'"
        )

@app.get("/admin/config")
async def get_system_config(
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN))
):
    """Get system configuration"""
    
    config = {
        "system": {
            "version": "4.0.0",
            "environment": "production",
            "timezone": "UTC",
            "maintenance_mode": False
        },
        "security": {
            "password_min_length": 8,
            "max_login_attempts": 5,
            "session_timeout": 86400,
            "2fa_required": False
        },
        "trading": {
            "min_order_size": 0.001,
            "max_order_size": 1000000,
            "max_leverage": 10,
            "trading_enabled": True
        },
        "kyc": {
            "required_for_trading": True,
            "auto_approve": False,
            "document_expiry_days": 365
        },
        "notifications": {
            "email_enabled": True,
            "sms_enabled": True,
            "push_enabled": True
        }
    }
    
    return config

@app.post("/admin/config")
async def update_system_config(
    config_request: SystemConfigRequest,
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN))
):
    """Update system configuration"""
    
    # Store in Redis for persistent configuration
    redis_client.set(f"config:{config_request.config_key}", json.dumps(config_request.config_value))
    
    # Log audit event
    log_audit_event(
        user_id=str(current_user.id),
        action="update_config",
        resource="admin_panel",
        details={
            "config_key": config_request.config_key,
            "config_value": config_request.config_value
        },
        ip_address="0.0.0.0",
        user_agent="admin_panel"
    )
    
    return {"message": "Configuration updated successfully"}

# ==================== HEALTH ENDPOINTS ====================

@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "TigerEx Enhanced Admin System",
        "version": "4.0.0",
        "status": "running"
    }

# ==================== STARTUP ====================

@app.on_event("startup")
async def startup_event():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    
    # Create default super admin if not exists
    db = SessionLocal()
    try:
        super_admin = db.query(User).filter(User.role == UserRole.SUPER_ADMIN).first()
        if not super_admin:
            hashed_password = get_password_hash("admin123")
            admin_user = User(
                email="admin@tigerex.com",
                username="superadmin",
                hashed_password=hashed_password,
                first_name="Super",
                last_name="Admin",
                role=UserRole.SUPER_ADMIN,
                status=UserStatus.ACTIVE,
                is_active=True,
                is_verified=True
            )
            db.add(admin_user)
            db.commit()
            print("Default super admin created: username=superadmin, password=admin123")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)