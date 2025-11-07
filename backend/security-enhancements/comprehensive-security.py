"""
Comprehensive Security Enhancements for TigerEx
Complete security system for all trading types and user access
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import hmac
import secrets
import jwt
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis
import asyncio
from dataclasses import dataclass
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import bcrypt
import pyotp
import qrcode
from io import BytesIO

logger = logging.getLogger(__name__)

# ============================================================================
# SECURITY ENUMS AND CONFIG
# ============================================================================

class SecurityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class UserRole(str, Enum):
    USER = "user"
    VERIFIED_USER = "verified_user"
    TRADER = "trader"
    INSTITUTIONAL = "institutional"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class Permission(str, Enum):
    # Basic permissions
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    
    # Trading permissions
    TRADE_SPOT = "trade_spot"
    TRADE_FUTURES = "trade_futures"
    TRADE_MARGIN = "trade_margin"
    TRADE_OPTIONS = "trade_options"
    TRADE_COPY = "trade_copy"
    TRADE_GRID = "trade_grid"
    
    # Admin permissions
    ADMIN_USERS = "admin_users"
    ADMIN_TRADING = "admin_trading"
    ADMIN_SYSTEM = "admin_system"
    ADMIN_SECURITY = "admin_security"
    ADMIN_AUDIT = "admin_audit"
    
    # Special permissions
    EMERGENCY_STOP = "emergency_stop"
    CIRCUIT_BREAKER = "circuit_breaker"
    WHITELIST_MANAGE = "whitelist_manage"
    API_KEY_MANAGE = "api_key_manage"

# ============================================================================
# SECURITY CONFIGURATION
# ============================================================================

@dataclass
class SecurityConfig:
    # Authentication settings
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 30
    
    # Password security
    password_min_length: int = 12
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_symbols: bool = True
    password_hash_rounds: int = 12
    
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 100
    rate_limit_burst_size: int = 200
    
    # IP security
    ip_whitelist_enabled: bool = True
    ip_blacklist_enabled: bool = True
    max_failed_attempts: int = 5
    account_lockout_minutes: int = 30
    
    # 2FA settings
    two_factor_required: bool = True
    two_factor_backup_codes: int = 10
    two_fa_issuer: str = "TigerEx"
    
    # Session security
    session_timeout_minutes: int = 30
    max_concurrent_sessions: int = 5
    
    # API security
    api_key_required: bool = True
    api_signature_required: bool = True
    api_timestamp_tolerance: int = 300
    
    # Trading security
    max_withdrawal_per_day: float = 100000.0
    max_withdrawal_per_transaction: float = 50000.0
    withdrawal_approval_threshold: float = 10000.0

# ============================================================================
# AUTHENTICATION SYSTEM
# ============================================================================

class AuthenticationService:
    def __init__(self, config: SecurityConfig, redis_client: redis.Redis):
        self.config = config
        self.redis = redis_client
        self.fernet = Fernet(self._generate_encryption_key())
        self.security = HTTPBearer()
        
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key from JWT secret"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'tigerex_security_salt',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.config.jwt_secret_key.encode()))
        return key
    
    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt(rounds=self.config.password_hash_rounds)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        errors = []
        score = 0
        
        if len(password) < self.config.password_min_length:
            errors.append(f"Password must be at least {self.config.password_min_length} characters")
        else:
            score += 1
            
        if self.config.password_require_uppercase and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        else:
            score += 1
            
        if self.config.password_require_lowercase and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        else:
            score += 1
            
        if self.config.password_require_numbers and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        else:
            score += 1
            
        if self.config.password_require_symbols and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must contain at least one special character")
        else:
            score += 1
        
        strength = "weak"
        if score >= 4:
            strength = "strong"
        elif score >= 2:
            strength = "medium"
            
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "score": score,
            "strength": strength
        }
    
    def generate_jwt_tokens(self, user_id: str, user_role: UserRole) -> Dict[str, str]:
        """Generate JWT access and refresh tokens"""
        now = datetime.utcnow()
        
        # Access token
        access_payload = {
            "user_id": user_id,
            "role": user_role.value,
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=self.config.jwt_access_token_expire_minutes),
            "jti": secrets.token_urlsafe(32)
        }
        
        # Refresh token
        refresh_payload = {
            "user_id": user_id,
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(days=self.config.jwt_refresh_token_expire_days),
            "jti": secrets.token_urlsafe(32)
        }
        
        access_token = jwt.encode(access_payload, self.config.jwt_secret_key, algorithm=self.config.jwt_algorithm)
        refresh_token = jwt.encode(refresh_payload, self.config.jwt_secret_key, algorithm=self.config.jwt_algorithm)
        
        # Store refresh token in Redis
        self.redis.setex(
            f"refresh_token:{user_id}",
            timedelta(days=self.config.jwt_refresh_token_expire_days),
            refresh_token
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.config.jwt_access_token_expire_minutes * 60
        }
    
    def verify_jwt_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.config.jwt_secret_key, algorithms=[self.config.jwt_algorithm])
            
            if payload.get("type") != token_type:
                raise jwt.InvalidTokenError("Invalid token type")
            
            # Check if refresh token is still valid (for refresh tokens)
            if token_type == "refresh":
                stored_token = self.redis.get(f"refresh_token:{payload['user_id']}")
                if not stored_token or stored_token.decode() != token:
                    raise jwt.InvalidTokenError("Refresh token revoked")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

# ============================================================================
# TWO FACTOR AUTHENTICATION
# ============================================================================

class TwoFactorAuthService:
    def __init__(self, config: SecurityConfig):
        self.config = config
        
    def generate_totp_secret(self) -> str:
        """Generate TOTP secret for 2FA"""
        return pyotp.random_base32()
    
    def generate_qr_code(self, user_email: str, secret: str) -> BytesIO:
        """Generate QR code for TOTP setup"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_email,
            issuer_name=self.config.two_fa_issuer
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        bio = BytesIO()
        img.save(bio)
        bio.seek(0)
        return bio
    
    def verify_totp(self, secret: str, token: str) -> bool:
        """Verify TOTP token"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
    
    def generate_backup_codes(self) -> List[str]:
        """Generate backup codes for 2FA"""
        return [secrets.token_urlsafe(8) for _ in range(self.config.two_factor_backup_codes)]

# ============================================================================
# RATE LIMITING SYSTEM
# ============================================================================

class RateLimitService:
    def __init__(self, redis_client: redis.Redis, config: SecurityConfig):
        self.redis = redis_client
        self.config = config
        
    async def check_rate_limit(self, identifier: str, limit: int = None, window: int = 60) -> Dict[str, Any]:
        """Check rate limit for identifier"""
        if not self.config.rate_limit_enabled:
            return {"allowed": True, "remaining": float('inf'), "reset_time": 0}
        
        limit = limit or self.config.rate_limit_requests_per_minute
        key = f"rate_limit:{identifier}"
        
        current_time = int(datetime.utcnow().timestamp())
        window_start = current_time - (current_time % window)
        
        # Clean up old entries
        self.redis.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        current_requests = self.redis.zcard(key)
        
        if current_requests >= limit:
            # Get oldest request time for reset
            oldest = self.redis.zrange(key, 0, 0, withscores=True)
            reset_time = int(oldest[0][1]) + window if oldest else current_time + window
            
            return {
                "allowed": False,
                "remaining": 0,
                "reset_time": reset_time,
                "retry_after": reset_time - current_time
            }
        
        # Add current request
        self.redis.zadd(key, {str(current_time): current_time})
        self.redis.expire(key, window)
        
        return {
            "allowed": True,
            "remaining": limit - current_requests - 1,
            "reset_time": window_start + window
        }

# ============================================================================
# IP SECURITY SYSTEM
# ============================================================================

class IPSecurityService:
    def __init__(self, redis_client: redis.Redis, config: SecurityConfig):
        self.redis = redis_client
        self.config = config
        
    async def is_ip_allowed(self, ip_address: str) -> bool:
        """Check if IP address is allowed"""
        # Check blacklist
        if self.config.ip_blacklist_enabled:
            if self.redis.sismember("ip_blacklist", ip_address):
                return False
        
        # Check whitelist
        if self.config.ip_whitelist_enabled:
            whitelist_size = self.redis.scard("ip_whitelist")
            if whitelist_size > 0 and not self.redis.sismember("ip_whitelist", ip_address):
                return False
        
        return True
    
    async def add_to_blacklist(self, ip_address: str, reason: str = ""):
        """Add IP to blacklist"""
        self.redis.sadd("ip_blacklist", ip_address)
        self.redis.hset("ip_blacklog", ip_address, f"{datetime.utcnow().isoformat()}:{reason}")
    
    async def add_to_whitelist(self, ip_address: str, added_by: str = ""):
        """Add IP to whitelist"""
        self.redis.sadd("ip_whitelist", ip_address)
        self.redis.hset("ip_whitelist_log", ip_address, f"{datetime.utcnow().isoformat()}:{added_by}")
    
    async def remove_from_blacklist(self, ip_address: str):
        """Remove IP from blacklist"""
        self.redis.srem("ip_blacklist", ip_address)
        self.redis.hdel("ip_blacklog", ip_address)
    
    async def remove_from_whitelist(self, ip_address: str):
        """Remove IP from whitelist"""
        self.redis.srem("ip_whitelist", ip_address)
        self.redis.hdel("ip_whitelist_log", ip_address)

# ============================================================================
# ACCOUNT SECURITY SYSTEM
# ============================================================================

class AccountSecurityService:
    def __init__(self, redis_client: redis.Redis, config: SecurityConfig):
        self.redis = redis_client
        self.config = config
        
    async def record_failed_login(self, identifier: str, ip_address: str):
        """Record failed login attempt"""
        key = f"failed_login:{identifier}"
        self.redis.lpush(key, f"{datetime.utcnow().isoformat()}:{ip_address}")
        self.redis.ltrim(key, 0, self.config.max_failed_attempts - 1)
        self.redis.expire(key, self.config.account_lockout_minutes * 60)
        
        # Check if account should be locked
        attempts = self.redis.llen(key)
        if attempts >= self.config.max_failed_attempts:
            await self.lock_account(identifier)
    
    async def clear_failed_logins(self, identifier: str):
        """Clear failed login attempts"""
        self.redis.delete(f"failed_login:{identifier}")
    
    async def is_account_locked(self, identifier: str) -> bool:
        """Check if account is locked"""
        return self.redis.exists(f"account_locked:{identifier}")
    
    async def lock_account(self, identifier: str, reason: str = "Too many failed attempts"):
        """Lock user account"""
        self.redis.setex(
            f"account_locked:{identifier}",
            self.config.account_lockout_minutes * 60,
            f"{datetime.utcnow().isoformat()}:{reason}"
        )
    
    async def unlock_account(self, identifier: str):
        """Unlock user account"""
        self.redis.delete(f"account_locked:{identifier}")
        await self.clear_failed_logins(identifier)

# ============================================================================
# API SECURITY SYSTEM
# ============================================================================

class APISecurityService:
    def __init__(self, config: SecurityConfig, redis_client: redis.Redis):
        self.config = config
        self.redis = redis_client
    
    def generate_api_key(self, user_id: str, permissions: List[Permission]) -> Dict[str, str]:
        """Generate API key for user"""
        api_key = f"tigerex_{secrets.token_urlsafe(32)}"
        api_secret = secrets.token_urlsafe(64)
        
        # Store API key info
        key_data = {
            "user_id": user_id,
            "permissions": [p.value for p in permissions],
            "created_at": datetime.utcnow().isoformat(),
            "last_used": None,
            "usage_count": 0
        }
        
        self.redis.hset(f"api_key:{api_key}", mapping=key_data)
        self.redis.hset(f"api_secret:{api_key}", "secret", self.hash_api_secret(api_secret))
        
        return {
            "api_key": api_key,
            "api_secret": api_secret,
            "permissions": [p.value for p in permissions]
        }
    
    def hash_api_secret(self, secret: str) -> str:
        """Hash API secret"""
        return hashlib.sha256(secret.encode()).hexdigest()
    
    def verify_api_signature(self, api_key: str, timestamp: str, signature: str, payload: str) -> bool:
        """Verify API signature"""
        api_secret = self.redis.hget(f"api_secret:{api_key}", "secret")
        if not api_secret:
            return False
        
        # Check timestamp
        try:
            request_time = int(timestamp)
            current_time = int(datetime.utcnow().timestamp())
            if abs(current_time - request_time) > self.config.api_timestamp_tolerance:
                return False
        except ValueError:
            return False
        
        # Generate expected signature
        expected_signature = hmac.new(
            api_secret.encode(),
            f"{timestamp}{payload}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    async def check_api_permissions(self, api_key: str, required_permission: Permission) -> bool:
        """Check if API key has required permission"""
        permissions = self.redis.hget(f"api_key:{api_key}", "permissions")
        if not permissions:
            return False
        
        try:
            perms = json.loads(permissions)
            return required_permission.value in perms
        except json.JSONDecodeError:
            return False

# ============================================================================
# TRADING SECURITY SYSTEM
# ============================================================================

class TradingSecurityService:
    def __init__(self, config: SecurityConfig, redis_client: redis.Redis):
        self.config = config
        self.redis = redis_client
    
    async def check_withdrawal_limit(self, user_id: str, amount: float) -> Dict[str, Any]:
        """Check withdrawal limits"""
        daily_key = f"withdrawal_daily:{user_id}:{datetime.utcnow().strftime('%Y-%m-%d')}"
        current_daily = float(self.redis.get(daily_key) or 0)
        
        # Check per-transaction limit
        if amount > self.config.max_withdrawal_per_transaction:
            return {
                "allowed": False,
                "reason": "Amount exceeds per-transaction limit",
                "limit": self.config.max_withdrawal_per_transaction
            }
        
        # Check daily limit
        if current_daily + amount > self.config.max_withdrawal_per_day:
            return {
                "allowed": False,
                "reason": "Amount exceeds daily limit",
                "current_daily": current_daily,
                "daily_limit": self.config.max_withdrawal_per_day
            }
        
        # Check if approval needed
        needs_approval = amount > self.config.withdrawal_approval_threshold
        
        return {
            "allowed": True,
            "needs_approval": needs_approval,
            "current_daily": current_daily,
            "remaining_daily": self.config.max_withdrawal_per_day - current_daily - amount
        }
    
    async def record_withdrawal(self, user_id: str, amount: float):
        """Record withdrawal for limit tracking"""
        daily_key = f"withdrawal_daily:{user_id}:{datetime.utcnow().strftime('%Y-%m-%d')}"
        self.redis.incrbyfloat(daily_key, amount)
        self.redis.expire(daily_key, 86400)  # 24 hours
    
    async def check_trading_permissions(self, user_id: str, trading_type: str, action: str) -> bool:
        """Check if user has permission for specific trading action"""
        # This would integrate with user role/permission system
        user_role = self.redis.hget(f"user:{user_id}", "role")
        if not user_role:
            return False
        
        # Define trading permissions per role
        role_permissions = {
            UserRole.USER.value: ["trade_spot"],
            UserRole.VERIFIED_USER.value: ["trade_spot", "trade_margin"],
            UserRole.TRADER.value: ["trade_spot", "trade_margin", "trade_futures"],
            UserRole.INSTITUTIONAL.value: ["trade_spot", "trade_margin", "trade_futures", "trade_options"],
            UserRole.ADMIN.value: ["trade_spot", "trade_margin", "trade_futures", "trade_options", "trade_copy", "trade_grid"],
            UserRole.SUPER_ADMIN.value: ["trade_spot", "trade_margin", "trade_futures", "trade_options", "trade_copy", "trade_grid"]
        }
        
        allowed_actions = role_permissions.get(user_role.decode(), [])
        return action in allowed_actions

# ============================================================================
# SECURITY AUDIT SYSTEM
# ============================================================================

class SecurityAuditService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def log_security_event(self, event_type: str, user_id: str, ip_address: str, details: Dict[str, Any]):
        """Log security event"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "details": details
        }
        
        # Add to security log
        self.redis.lpush("security_audit_log", json.dumps(event))
        self.redis.ltrim("security_audit_log", 0, 9999)  # Keep last 10k events
        
        # Add to user-specific log
        if user_id:
            self.redis.lpush(f"security_user_log:{user_id}", json.dumps(event))
            self.redis.ltrim(f"security_user_log:{user_id}", 0, 999)
    
    async def get_security_events(self, user_id: str = None, event_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get security events"""
        key = f"security_user_log:{user_id}" if user_id else "security_audit_log"
        
        events = self.redis.lrange(key, 0, limit - 1)
        result = []
        
        for event in events:
            try:
                data = json.loads(event)
                if event_type and data.get("event_type") != event_type:
                    continue
                result.append(data)
            except json.JSONDecodeError:
                continue
        
        return result

# ============================================================================
# MAIN SECURITY MANAGER
# ============================================================================

class ComprehensiveSecurityManager:
    def __init__(self, config: SecurityConfig, redis_client: redis.Redis):
        self.config = config
        self.redis = redis_client
        
        # Initialize services
        self.auth_service = AuthenticationService(config, redis_client)
        self.two_factor_service = TwoFactorAuthService(config)
        self.rate_limit_service = RateLimitService(redis_client, config)
        self.ip_security_service = IPSecurityService(redis_client, config)
        self.account_security_service = AccountSecurityService(redis_client, config)
        self.api_security_service = APISecurityService(config, redis_client)
        self.trading_security_service = TradingSecurityService(config, redis_client)
        self.audit_service = SecurityAuditService(redis_client)
    
    async def authenticate_user(self, username: str, password: str, ip_address: str) -> Dict[str, Any]:
        """Authenticate user with comprehensive security checks"""
        # Rate limiting check
        rate_limit_result = await self.rate_limit_service.check_rate_limit(f"auth:{username}:{ip_address}")
        if not rate_limit_result["allowed"]:
            await self.audit_service.log_security_event(
                "rate_limit_exceeded",
                username,
                ip_address,
                {"reason": "Too many authentication attempts"}
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # IP security check
        if not await self.ip_security_service.is_ip_allowed(ip_address):
            await self.audit_service.log_security_event(
                "ip_blocked",
                username,
                ip_address,
                {"reason": "IP address not allowed"}
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="IP address not allowed"
            )
        
        # Account lockout check
        if await self.account_security_service.is_account_locked(username):
            await self.audit_service.log_security_event(
                "login_blocked",
                username,
                ip_address,
                {"reason": "Account is locked"}
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is locked"
            )
        
        # Password verification (would integrate with user database)
        # user = await get_user_by_username(username)
        # if not user or not self.auth_service.verify_password(password, user.password_hash):
        #     await self.account_security_service.record_failed_login(username, ip_address)
        #     await self.audit_service.log_security_event("login_failed", username, ip_address)
        #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        # Simulate successful authentication
        user_id = username
        user_role = UserRole.USER
        
        # Clear failed login attempts
        await self.account_security_service.clear_failed_logins(username)
        
        # Generate tokens
        tokens = self.auth_service.generate_jwt_tokens(user_id, user_role)
        
        # Log successful login
        await self.audit_service.log_security_event(
            "login_success",
            user_id,
            ip_address,
            {"role": user_role.value}
        )
        
        return {
            "user_id": user_id,
            "role": user_role.value,
            **tokens
        }
    
    async def validate_trading_request(self, user_id: str, trading_type: str, action: str, amount: float = 0) -> Dict[str, Any]:
        """Validate trading request with security checks"""
        # Check trading permissions
        if not await self.trading_security_service.check_trading_permissions(user_id, trading_type, action):
            await self.audit_service.log_security_event(
                "trading_permission_denied",
                user_id,
                "",
                {"trading_type": trading_type, "action": action}
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Trading permission denied"
            )
        
        # Check withdrawal limits for withdrawal actions
        if action == "withdraw" and amount > 0:
            limit_check = await self.trading_security_service.check_withdrawal_limit(user_id, amount)
            if not limit_check["allowed"]:
                await self.audit_service.log_security_event(
                    "withdrawal_limit_exceeded",
                    user_id,
                    "",
                    {"amount": amount, "reason": limit_check["reason"]}
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=limit_check["reason"]
                )
        
        return {"allowed": True, "needs_approval": limit_check.get("needs_approval", False)}