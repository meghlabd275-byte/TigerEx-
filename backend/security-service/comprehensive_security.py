"""
TigerEx Comprehensive Security Service
Complete security implementation for all platforms
"""

from fastapi import FastAPI, HTTPException, Depends, Request, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import jwt
import hashlib
import secrets
import re
from passlib.context import CryptContext
import pyotp
import qrcode
from io import BytesIO
import base64

app = FastAPI(title="TigerEx Security Service", version="1.0.0")

# Security configuration
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Add security middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MODELS ====================

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    
class TwoFactorSetup(BaseModel):
    secret: str
    qr_code: str
    backup_codes: List[str]
    
class TwoFactorVerify(BaseModel):
    code: str
    
class PasswordReset(BaseModel):
    email: EmailStr
    
class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    
class APIKeyCreate(BaseModel):
    name: str
    permissions: List[str]
    ip_whitelist: Optional[List[str]] = None
    
class SecurityLog(BaseModel):
    user_id: str
    action: str
    ip_address: str
    user_agent: str
    timestamp: datetime
    status: str
    details: Optional[Dict] = None

# In-memory storage (use database in production)
users_db: Dict[str, Dict] = {}
sessions_db: Dict[str, Dict] = {}
security_logs_db: List[Dict] = []
api_keys_db: Dict[str, Dict] = {}
rate_limit_db: Dict[str, List] = {}

# ==================== PASSWORD SECURITY ====================

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r"[!@#$%^&*(),.?&quot;:{}|<>]", password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"

# ==================== JWT TOKEN MANAGEMENT ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ==================== TWO-FACTOR AUTHENTICATION ====================

def generate_2fa_secret() -> str:
    """Generate 2FA secret"""
    return pyotp.random_base32()

def generate_2fa_qr_code(email: str, secret: str) -> str:
    """Generate 2FA QR code"""
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(email, issuer_name="TigerEx")
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

def verify_2fa_code(secret: str, code: str) -> bool:
    """Verify 2FA code"""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)

def generate_backup_codes(count: int = 10) -> List[str]:
    """Generate backup codes for 2FA"""
    return [secrets.token_hex(4).upper() for _ in range(count)]

# ==================== RATE LIMITING ====================

def check_rate_limit(identifier: str, max_requests: int = 100, window_seconds: int = 60) -> bool:
    """Check if request is within rate limit"""
    now = datetime.now()
    
    if identifier not in rate_limit_db:
        rate_limit_db[identifier] = []
    
    # Remove old requests outside the window
    rate_limit_db[identifier] = [
        req_time for req_time in rate_limit_db[identifier]
        if (now - req_time).total_seconds() < window_seconds
    ]
    
    # Check if limit exceeded
    if len(rate_limit_db[identifier]) >= max_requests:
        return False
    
    # Add current request
    rate_limit_db[identifier].append(now)
    return True

# ==================== IP WHITELISTING ====================

def check_ip_whitelist(ip_address: str, whitelist: List[str]) -> bool:
    """Check if IP is in whitelist"""
    if not whitelist:
        return True
    return ip_address in whitelist

# ==================== SECURITY LOGGING ====================

def log_security_event(
    user_id: str,
    action: str,
    ip_address: str,
    user_agent: str,
    status: str,
    details: Optional[Dict] = None
):
    """Log security event"""
    log_entry = {
        "log_id": secrets.token_hex(16),
        "user_id": user_id,
        "action": action,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "timestamp": datetime.now(),
        "status": status,
        "details": details or {}
    }
    security_logs_db.append(log_entry)

# ==================== API ENDPOINTS ====================

@app.post("/api/v1/auth/register", response_model=Dict)
async def register(user: UserCreate, request: Request):
    """Register new user"""
    # Validate password strength
    is_strong, message = validate_password_strength(user.password)
    if not is_strong:
        raise HTTPException(status_code=400, detail=message)
    
    # Check if user exists
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_id = secrets.token_hex(16)
    hashed_password = hash_password(user.password)
    
    users_db[user.email] = {
        "user_id": user_id,
        "email": user.email,
        "username": user.username,
        "password": hashed_password,
        "is_active": True,
        "is_verified": False,
        "2fa_enabled": False,
        "2fa_secret": None,
        "created_at": datetime.now(),
        "last_login": None
    }
    
    # Log event
    log_security_event(
        user_id=user_id,
        action="register",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    
    return {
        "success": True,
        "user_id": user_id,
        "message": "User registered successfully"
    }

@app.post("/api/v1/auth/login", response_model=Token)
async def login(credentials: UserLogin, request: Request):
    """User login"""
    # Check rate limit
    if not check_rate_limit(f"login_{credentials.email}", max_requests=5, window_seconds=300):
        raise HTTPException(status_code=429, detail="Too many login attempts")
    
    # Verify credentials
    user = users_db.get(credentials.email)
    if not user or not verify_password(credentials.password, user["password"]):
        log_security_event(
            user_id=user["user_id"] if user else "unknown",
            action="login",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            status="failed",
            details={"reason": "invalid_credentials"}
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if 2FA is enabled
    if user["2fa_enabled"]:
        # Return temporary token for 2FA verification
        temp_token = create_access_token(
            data={"sub": user["user_id"], "email": user["email"], "requires_2fa": True},
            expires_delta=timedelta(minutes=5)
        )
        return Token(
            access_token=temp_token,
            refresh_token="",
            token_type="bearer",
            expires_in=300
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user["user_id"], "email": user["email"]})
    refresh_token = create_refresh_token(data={"sub": user["user_id"]})
    
    # Update last login
    user["last_login"] = datetime.now()
    
    # Log event
    log_security_event(
        user_id=user["user_id"],
        action="login",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status="success"
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@app.post("/api/v1/auth/2fa/setup", response_model=TwoFactorSetup)
async def setup_2fa(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Setup 2FA for user"""
    payload = verify_token(credentials.credentials)
    user_id = payload.get("sub")
    
    user = next((u for u in users_db.values() if u["user_id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate 2FA secret
    secret = generate_2fa_secret()
    qr_code = generate_2fa_qr_code(user["email"], secret)
    backup_codes = generate_backup_codes()
    
    # Store secret (not enabled yet)
    user["2fa_secret_pending"] = secret
    user["backup_codes"] = [hash_password(code) for code in backup_codes]
    
    return TwoFactorSetup(
        secret=secret,
        qr_code=qr_code,
        backup_codes=backup_codes
    )

@app.post("/api/v1/auth/2fa/verify")
async def verify_2fa(
    verification: TwoFactorVerify,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Verify 2FA code"""
    payload = verify_token(credentials.credentials)
    user_id = payload.get("sub")
    
    user = next((u for u in users_db.values() if u["user_id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if setting up or logging in
    if "2fa_secret_pending" in user:
        secret = user["2fa_secret_pending"]
        if verify_2fa_code(secret, verification.code):
            user["2fa_enabled"] = True
            user["2fa_secret"] = secret
            del user["2fa_secret_pending"]
            return {"success": True, "message": "2FA enabled successfully"}
    elif user["2fa_enabled"]:
        if verify_2fa_code(user["2fa_secret"], verification.code):
            # Create full access tokens
            access_token = create_access_token(data={"sub": user_id, "email": user["email"]})
            refresh_token = create_refresh_token(data={"sub": user_id})
            
            return Token(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
    
    raise HTTPException(status_code=401, detail="Invalid 2FA code")

@app.post("/api/v1/auth/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    payload = verify_token(refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    
    user_id = payload.get("sub")
    user = next((u for u in users_db.values() if u["user_id"] == user_id), None)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create new access token
    access_token = create_access_token(data={"sub": user_id, "email": user["email"]})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@app.post("/api/v1/auth/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """User logout"""
    payload = verify_token(credentials.credentials)
    user_id = payload.get("sub")
    
    # Invalidate session (implement session management in production)
    log_security_event(
        user_id=user_id,
        action="logout",
        ip_address="",
        user_agent="",
        status="success"
    )
    
    return {"success": True, "message": "Logged out successfully"}

@app.get("/api/v1/security/logs")
async def get_security_logs(
    limit: int = 100,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get security logs"""
    payload = verify_token(credentials.credentials)
    user_id = payload.get("sub")
    
    # Filter logs for user
    user_logs = [log for log in security_logs_db if log["user_id"] == user_id]
    user_logs.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {"logs": user_logs[:limit]}

@app.get("/api/v1/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)