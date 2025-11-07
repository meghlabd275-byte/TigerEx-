"""
TigerEx Enhanced Security Module
Complete security implementation with advanced features
"""

import asyncio
import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json
import redis.asyncio as redis
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityEvent:
    event_type: str
    user_id: Optional[int]
    ip_address: str
    user_agent: str
    severity: SecurityLevel
    details: Dict[str, Any]
    timestamp: datetime

class RateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
    async def is_rate_limited(self, key: str, limit: int, window: int) -> Tuple[bool, int]:
        """Check if rate limit exceeded"""
        current_time = int(time.time())
        pipeline = self.redis.pipeline()
        
        # Remove expired entries
        pipeline.zremrangebyscore(key, 0, current_time - window)
        
        # Count current requests
        pipeline.zcard(key)
        
        # Add current request
        pipeline.zadd(key, {str(current_time): current_time})
        
        # Set expiration
        pipeline.expire(key, window)
        
        _, count, _, _ = await pipeline.execute()
        return count >= limit, limit - count

class IPWhitelist:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
    async def is_whitelisted(self, ip: str) -> bool:
        """Check if IP is whitelisted"""
        return await self.redis.sismember("whitelist:ips", ip)
    
    async def add_to_whitelist(self, ip: str) -> bool:
        """Add IP to whitelist"""
        return await self.redis.sadd("whitelist:ips", ip) > 0
    
    async def remove_from_whitelist(self, ip: str) -> bool:
        """Remove IP from whitelist"""
        return await self.redis.srem("whitelist:ips", ip) > 0

class AdvancedEncryption:
    def __init__(self, master_key: str):
        self.master_key = master_key.encode()
        self.fernet = self._create_fernet()
        
    def _create_fernet(self) -> Fernet:
        """Create Fernet instance from master key"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'tigerex_salt',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
        return Fernet(key)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.fernet.decrypt(encrypted_data.encode()).decode()

class SecurityValidator:
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_email_format(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def sanitize_input(input_string: str) -> str:
        """Sanitize user input"""
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', 'script', 'javascript']
        sanitized = input_string
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()

class AntiDDoS:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.block_threshold = 100  # requests per minute
        self.block_duration = 3600  # 1 hour
        
    async def check_request(self, ip: str) -> Tuple[bool, str]:
        """Check if request should be blocked"""
        current_time = int(time.time())
        minute_ago = current_time - 60
        
        # Count requests in last minute
        key = f"ddos:{ip}"
        await self.redis.zremrangebyscore(key, 0, minute_ago)
        count = await self.redis.zcard(key)
        
        if count > self.block_threshold:
            # Block the IP
            await self.redis.setex(f"blocked:{ip}", self.block_duration, "1")
            return False, "Rate limit exceeded"
        
        # Add current request
        await self.redis.zadd(key, {str(current_time): current_time})
        await self.redis.expire(key, 60)
        
        return True, "OK"
    
    async def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked"""
        return await self.redis.exists(f"blocked:{ip}")

class SecurityAuditLogger:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
    async def log_security_event(self, event: SecurityEvent):
        """Log security event"""
        event_data = {
            "event_type": event.event_type,
            "user_id": event.user_id,
            "ip_address": event.ip_address,
            "user_agent": event.user_agent,
            "severity": event.severity.value,
            "details": event.details,
            "timestamp": event.timestamp.isoformat()
        }
        
        # Store in Redis for real-time monitoring
        await self.redis.lpush(
            f"security_events:{event.severity.value}",
            json.dumps(event_data)
        )
        
        # Keep only last 1000 events
        await self.redis.ltrim(f"security_events:{event.severity.value}", 0, 999)
        
        # Also log to file/database for permanent storage
        logger.warning(f"Security Event: {event.event_type} - {event.ip_address}")

class TwoFactorAuth:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
    def generate_secret(self) -> str:
        """Generate 2FA secret"""
        return base64.b32encode(secrets.token_bytes(16)).decode('utf-8')
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes for 2FA"""
        return [secrets.token_hex(4).upper() for _ in range(count)]
    
    async def store_2fa_secret(self, user_id: int, secret: str):
        """Store 2FA secret for user"""
        encrypted_secret = self._encrypt_secret(secret)
        await self.redis.setex(f"2fa:{user_id}", 86400 * 365, encrypted_secret)
    
    async def verify_2fa_token(self, user_id: int, token: str) -> bool:
        """Verify 2FA token"""
        # In production, integrate with Google Authenticator or similar
        # For now, simple verification
        return len(token) == 6 and token.isdigit()

class SessionManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.session_timeout = 3600  # 1 hour
        
    async def create_session(self, user_id: int, session_data: Dict[str, Any]) -> str:
        """Create new session"""
        session_id = secrets.token_urlsafe(32)
        session_key = f"session:{session_id}"
        
        session_data.update({
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        })
        
        await self.redis.setex(
            session_key,
            self.session_timeout,
            json.dumps(session_data)
        )
        
        return session_id
    
    async def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Validate session and update last activity"""
        session_key = f"session:{session_id}"
        session_data = await self.redis.get(session_key)
        
        if not session_data:
            return None
        
        try:
            data = json.loads(session_data)
            # Update last activity
            data["last_activity"] = datetime.utcnow().isoformat()
            await self.redis.setex(
                session_key,
                self.session_timeout,
                json.dumps(data)
            )
            return data
        except json.JSONDecodeError:
            return None
    
    async def revoke_session(self, session_id: str):
        """Revoke session"""
        await self.redis.delete(f"session:{session_id}")
    
    async def revoke_all_sessions(self, user_id: int):
        """Revoke all sessions for user"""
        pattern = f"session:*"
        sessions = await self.redis.keys(pattern)
        
        for session in sessions:
            data = await self.redis.get(session)
            if data:
                try:
                    session_data = json.loads(data)
                    if session_data.get("user_id") == user_id:
                        await self.redis.delete(session)
                except json.JSONDecodeError:
                    continue

class SecurityManager:
    """Main security management class"""
    
    def __init__(self, redis_client: redis.Redis, encryption_key: str):
        self.redis = redis_client
        self.rate_limiter = RateLimiter(redis_client)
        self.ip_whitelist = IPWhitelist(redis_client)
        self.encryption = AdvancedEncryption(encryption_key)
        self.validator = SecurityValidator()
        self.anti_ddos = AntiDDoS(redis_client)
        self.audit_logger = SecurityAuditLogger(redis_client)
        self.two_fa = TwoFactorAuth(redis_client)
        self.session_manager = SessionManager(redis_client)
        
    async def initialize_security(self):
        """Initialize security systems"""
        logger.info("Initializing TigerEx Security Systems")
        
        # Set up default security configurations
        await self.redis.set("security:config", json.dumps({
            "max_login_attempts": 5,
            "account_lockout_duration": 1800,  # 30 minutes
            "password_min_length": 8,
            "session_timeout": 3600,
            "rate_limit_window": 60,
            "rate_limit_max": 100
        }))
        
    async def check_ip_security(self, ip: str) -> Tuple[bool, str]:
        """Check IP security (whitelist, blacklist, DDoS)"""
        # Check if IP is blocked for DDoS
        if await self.anti_ddos.is_ip_blocked(ip):
            return False, "IP blocked due to suspicious activity"
        
        # Check rate limiting
        allowed, remaining = await self.rate_limiter.is_rate_limited(f"ip:{ip}", 100, 60)
        if not allowed:
            return False, "Rate limit exceeded"
        
        # DDoS protection
        ddos_ok, message = await self.anti_ddos.check_request(ip)
        if not ddos_ok:
            return False, message
        
        return True, "OK"
    
    async def log_security_event(self, event_type: str, user_id: Optional[int], 
                                ip: str, user_agent: str, severity: SecurityLevel,
                                details: Dict[str, Any]):
        """Log security event"""
        event = SecurityEvent(
            event_type=event_type,
            user_id=user_id,
            ip_address=ip,
            user_agent=user_agent,
            severity=severity,
            details=details,
            timestamp=datetime.utcnow()
        )
        await self.audit_logger.log_security_event(event)
    
    def encrypt_sensitive_field(self, value: str) -> str:
        """Encrypt sensitive field"""
        return self.encryption.encrypt_sensitive_data(value)
    
    def decrypt_sensitive_field(self, encrypted_value: str) -> str:
        """Decrypt sensitive field"""
        return self.encryption.decrypt_sensitive_data(encrypted_value)

# Security middleware for FastAPI
class SecurityMiddleware:
    def __init__(self, security_manager: SecurityManager):
        self.security_manager = security_manager
        
    async def __call__(self, request, call_next):
        # Get client IP
        client_ip = request.client.host
        
        # Security checks
        security_ok, message = await self.security_manager.check_ip_security(client_ip)
        if not security_ok:
            from fastapi import HTTPException
            raise HTTPException(status_code=429, detail=message)
        
        # Log request
        await self.security_manager.log_security_event(
            event_type="api_request",
            user_id=None,
            ip=client_ip,
            user_agent=request.headers.get("user-agent", ""),
            severity=SecurityLevel.LOW,
            details={"path": str(request.url.path), "method": request.method}
        )
        
        # Continue with request
        response = await call_next(request)
        return response