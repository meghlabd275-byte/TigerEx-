"""
Comprehensive Security System for TigerEx Platform
Advanced security implementation with multi-layer protection
"""

import asyncio
import hashlib
import hmac
import secrets
import time
import jwt
import bcrypt
import ssl
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import redis
import aiohttp
from aiohttp import web, ClientSession
from ratelimit import limits, sleep_and_retry
import ipaddress
import geoip2.database
from prometheus_client import Counter, Histogram, Gauge
import sentry_sdk

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize monitoring
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_SESSIONS = Gauge('active_sessions_total', 'Number of active sessions')
SECURITY_EVENTS = Counter('security_events_total', 'Security events', ['event_type'])

# Sentry for error tracking
sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/project-id",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

@dataclass
class SecurityEvent:
    event_type: str
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    timestamp: datetime
    details: Dict[str, Any]
    severity: str  # low, medium, high, critical

class SecurityConfig:
    # Rate limiting
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_PERIOD = 60  # seconds
    
    # Session management
    SESSION_TIMEOUT = 3600  # 1 hour
    MAX_CONCURRENT_SESSIONS = 5
    
    # Password security
    MIN_PASSWORD_LENGTH = 12
    PASSWORD_HISTORY_SIZE = 5
    MAX_LOGIN_ATTEMPTS = 5
    ACCOUNT_LOCKOUT_DURATION = 900  # 15 minutes
    
    # JWT settings
    JWT_SECRET_KEY = secrets.token_urlsafe(64)
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION = timedelta(hours=1)
    
    # Encryption
    ENCRYPTION_KEY = Fernet.generate_key()
    
    # IP security
    ALLOWED_IP_RANGES = [
        ipaddress.ip_network('192.168.1.0/24'),
        ipaddress.ip_network('10.0.0.0/8'),
    ]
    
    # 2FA settings
    TOTP_ISSUER = 'TigerEx'
    BACKUP_CODES_COUNT = 10

class AdvancedEncryption:
    """Advanced encryption and decryption utilities"""
    
    def __init__(self, key: bytes):
        self.cipher_suite = Fernet(key)
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple:
        """Hash password with bcrypt"""
        if salt is None:
            salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8'), salt.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure token"""
        return secrets.token_urlsafe(length)

class RateLimiter:
    """Advanced rate limiting with Redis backend"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    @sleep_and_retry
    @limits(calls=SecurityConfig.RATE_LIMIT_REQUESTS, period=SecurityConfig.RATE_LIMIT_PERIOD)
    async def check_rate_limit(self, key: str, limit: int = SecurityConfig.RATE_LIMIT_REQUESTS, period: int = SecurityConfig.RATE_LIMIT_PERIOD) -> bool:
        """Check if request is within rate limits"""
        current_time = int(time.time())
        window_start = current_time - period
        
        # Clean old entries
        self.redis.zremrangebyscore(f"rate_limit:{key}", 0, window_start)
        
        # Check current count
        current_count = self.redis.zcard(f"rate_limit:{key}")
        
        if current_count >= limit:
            return False
        
        # Add current request
        self.redis.zadd(f"rate_limit:{key}", {str(current_time): current_time})
        self.redis.expire(f"rate_limit:{key}", period)
        
        return True

class IPSecurityManager:
    """IP-based security and geo-location filtering"""
    
    def __init__(self):
        try:
            self.geoip_reader = geoip2.database.Reader('GeoLite2-City.mmdb')
        except:
            self.geoip_reader = None
            logger.warning("GeoIP database not found")
    
    def is_ip_allowed(self, ip_address: str) -> bool:
        """Check if IP is allowed based on configured ranges"""
        try:
            ip = ipaddress.ip_address(ip_address)
            for allowed_range in SecurityConfig.ALLOWED_IP_RANGES:
                if ip in allowed_range:
                    return True
            return False
        except ValueError:
            return False
    
    def get_geo_location(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Get geo-location information for IP"""
        if not self.geoip_reader:
            return None
        
        try:
            response = self.geoip_reader.city(ip_address)
            return {
                'country': response.country.name,
                'city': response.city.name,
                'latitude': response.location.latitude,
                'longitude': response.location.longitude,
                'timezone': response.location.time_zone
            }
        except:
            return None

class SessionManager:
    """Secure session management with Redis"""
    
    def __init__(self, redis_client: redis.Redis, encryption: AdvancedEncryption):
        self.redis = redis_client
        self.encryption = encryption
    
    async def create_session(self, user_id: str, ip_address: str, user_agent: str) -> str:
        """Create new secure session"""
        session_id = self.encryption.generate_secure_token()
        session_data = {
            'user_id': user_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'created_at': datetime.utcnow().isoformat(),
            'last_activity': datetime.utcnow().isoformat(),
            'is_active': True
        }
        
        # Encrypt session data
        encrypted_data = self.encryption.encrypt_data(str(session_data))
        
        # Store in Redis
        await self.redis.setex(
            f"session:{session_id}",
            SecurityConfig.SESSION_TIMEOUT,
            encrypted_data
        )
        
        # Track user sessions
        user_sessions = await self.redis.lrange(f"user_sessions:{user_id}", 0, -1)
        if len(user_sessions) >= SecurityConfig.MAX_CONCURRENT_SESSIONS:
            # Remove oldest session
            old_session = await self.redis.lpop(f"user_sessions:{user_id}")
            if old_session:
                await self.redis.delete(f"session:{old_session.decode()}")
        
        await self.redis.rpush(f"user_sessions:{user_id}", session_id)
        await self.redis.expire(f"user_sessions:{user_id}", SecurityConfig.SESSION_TIMEOUT)
        
        ACTIVE_SESSIONS.inc()
        return session_id
    
    async def validate_session(self, session_id: str, ip_address: str, user_agent: str) -> Optional[Dict[str, Any]]:
        """Validate session and return user data"""
        encrypted_data = await self.redis.get(f"session:{session_id}")
        if not encrypted_data:
            return None
        
        try:
            session_data = eval(self.encryption.decrypt_data(encrypted_data.decode()))
            
            # Check IP binding
            if session_data['ip_address'] != ip_address:
                SECURITY_EVENTS.labels(event_type='session_ip_mismatch').inc()
                return None
            
            # Check user agent binding
            if session_data['user_agent'] != user_agent:
                SECURITY_EVENTS.labels(event_type='session_ua_mismatch').inc()
                return None
            
            # Update last activity
            session_data['last_activity'] = datetime.utcnow().isoformat()
            encrypted_updated = self.encryption.encrypt_data(str(session_data))
            await self.redis.setex(
                f"session:{session_id}",
                SecurityConfig.SESSION_TIMEOUT,
                encrypted_updated
            )
            
            return session_data
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return None
    
    async def destroy_session(self, session_id: str, user_id: str):
        """Destroy session"""
        await self.redis.delete(f"session:{session_id}")
        await self.redis.lrem(f"user_sessions:{user_id}", 0, session_id)
        ACTIVE_SESSIONS.dec()

class TwoFactorAuth:
    """Two-Factor Authentication implementation"""
    
    def __init__(self, encryption: AdvancedEncryption):
        self.encryption = encryption
    
    def generate_totp_secret(self) -> str:
        """Generate TOTP secret key"""
        return self.encryption.generate_secure_token(20)
    
    def generate_backup_codes(self) -> List[str]:
        """Generate backup codes for 2FA"""
        return [self.encryption.generate_secure_token(8) for _ in range(SecurityConfig.BACKUP_CODES_COUNT)]
    
    def verify_totp(self, secret: str, token: str) -> bool:
        """Verify TOTP token (simplified implementation)"""
        # In production, use pyotp library
        import pyotp
        totp = pyotp.TOTP(secret)
        return totp.verify(token)

class SecurityAuditor:
    """Security event auditing and monitoring"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def log_security_event(self, event: SecurityEvent):
        """Log security event for auditing"""
        event_data = {
            'event_type': event.event_type,
            'user_id': event.user_id,
            'ip_address': event.ip_address,
            'user_agent': event.user_agent,
            'timestamp': event.timestamp.isoformat(),
            'details': event.details,
            'severity': event.severity
        }
        
        # Store in Redis
        await self.redis.lpush(
            'security_events',
            str(event_data)
        )
        await self.redis.expire('security_events', 86400 * 30)  # 30 days
        
        # Log to file
        logger.warning(f"Security Event: {event.event_type} - {event.details}")
        
        # Update metrics
        SECURITY_EVENTS.labels(event_type=event.event_type).inc()
        
        # Check for critical events
        if event.severity == 'critical':
            await self.trigger_security_alert(event)
    
    async def trigger_security_alert(self, event: SecurityEvent):
        """Trigger immediate security alert"""
        # Send to monitoring system
        alert_data = {
            'alert_type': 'security_critical',
            'event': event.__dict__,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # In production, integrate with alerting systems
        logger.critical(f"CRITICAL SECURITY ALERT: {event.event_type}")
        
        # Send to Sentry
        sentry_sdk.capture_message(
            f"Critical Security Event: {event.event_type}",
            level="error"
        )

class ComprehensiveSecuritySystem:
    """Main security system orchestrator"""
    
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=1)
        self.encryption = AdvancedEncryption(SecurityConfig.ENCRYPTION_KEY)
        self.rate_limiter = RateLimiter(self.redis_client)
        self.ip_security = IPSecurityManager()
        self.session_manager = SessionManager(self.redis_client, self.encryption)
        self.two_factor_auth = TwoFactorAuth(self.encryption)
        self.auditor = SecurityAuditor(self.redis_client)
        
        # Track failed login attempts
        self.failed_attempts: Dict[str, List[datetime]] = {}
    
    async def authenticate_user(self, email: str, password: str, ip_address: str, user_agent: str, totp_token: Optional[str] = None) -> Dict[str, Any]:
        """Comprehensive user authentication"""
        
        # Rate limiting check
        rate_limit_key = f"auth:{email}"
        if not await self.rate_limiter.check_rate_limit(rate_limit_key):
            await self.auditor.log_security_event(SecurityEvent(
                event_type='rate_limit_exceeded',
                user_id=email,
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=datetime.utcnow(),
                details={'endpoint': 'authentication'},
                severity='medium'
            ))
            return {'success': False, 'error': 'Rate limit exceeded'}
        
        # IP security check
        if not self.ip_security.is_ip_allowed(ip_address):
            await self.auditor.log_security_event(SecurityEvent(
                event_type='unauthorized_ip',
                user_id=email,
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=datetime.utcnow(),
                details={'geo_location': self.ip_security.get_geo_location(ip_address)},
                severity='high'
            ))
            return {'success': False, 'error': 'Unauthorized IP address'}
        
        # Check account lockout
        if email in self.failed_attempts:
            recent_attempts = [
                attempt for attempt in self.failed_attempts[email]
                if datetime.utcnow() - attempt < timedelta(seconds=SecurityConfig.ACCOUNT_LOCKOUT_DURATION)
            ]
            if len(recent_attempts) >= SecurityConfig.MAX_LOGIN_ATTEMPTS:
                await self.auditor.log_security_event(SecurityEvent(
                    event_type='account_locked',
                    user_id=email,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    timestamp=datetime.utcnow(),
                    details={'failed_attempts': len(recent_attempts)},
                    severity='high'
                ))
                return {'success': False, 'error': 'Account temporarily locked'}
        
        # Validate credentials (mock implementation)
        # In production, verify against database
        user_data = await self.get_user_data(email)
        if not user_data or not self.encryption.verify_password(password, user_data['password_hash']):
            # Record failed attempt
            if email not in self.failed_attempts:
                self.failed_attempts[email] = []
            self.failed_attempts[email].append(datetime.utcnow())
            
            await self.auditor.log_security_event(SecurityEvent(
                event_type='failed_login',
                user_id=email,
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=datetime.utcnow(),
                details={'remaining_attempts': SecurityConfig.MAX_LOGIN_ATTEMPTS - len(self.failed_attempts[email])},
                severity='medium'
            ))
            
            return {'success': False, 'error': 'Invalid credentials'}
        
        # Check 2FA if enabled
        if user_data.get('2fa_enabled'):
            if not totp_token or not self.two_factor_auth.verify_totp(user_data['totp_secret'], totp_token):
                await self.auditor.log_security_event(SecurityEvent(
                    event_type='failed_2fa',
                    user_id=email,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    timestamp=datetime.utcnow(),
                    details={},
                    severity='medium'
                ))
                return {'success': False, 'error': 'Invalid 2FA token'}
        
        # Clear failed attempts on successful login
        if email in self.failed_attempts:
            del self.failed_attempts[email]
        
        # Create session
        session_id = await self.session_manager.create_session(user_data['id'], ip_address, user_agent)
        
        # Generate JWT token
        jwt_payload = {
            'user_id': user_data['id'],
            'email': email,
            'role': user_data['role'],
            'session_id': session_id,
            'exp': datetime.utcnow() + SecurityConfig.JWT_EXPIRATION
        }
        
        access_token = jwt.encode(jwt_payload, SecurityConfig.JWT_SECRET_KEY, algorithm=SecurityConfig.JWT_ALGORITHM)
        
        await self.auditor.log_security_event(SecurityEvent(
            event_type='successful_login',
            user_id=email,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow(),
            details={'session_id': session_id},
            severity='low'
        ))
        
        return {
            'success': True,
            'access_token': access_token,
            'session_id': session_id,
            'user': user_data
        }
    
    async def authorize_request(self, request: web.Request) -> Optional[Dict[str, Any]]:
        """Authorize incoming request"""
        
        # Extract token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header[7:]
        
        # Verify JWT
        try:
            payload = jwt.decode(token, SecurityConfig.JWT_SECRET_KEY, algorithms=[SecurityConfig.JWT_ALGORITHM])
        except jwt.PyJWTError:
            return None
        
        # Validate session
        ip_address = request.remote
        user_agent = request.headers.get('User-Agent', '')
        session_data = await self.session_manager.validate_session(
            payload['session_id'],
            ip_address,
            user_agent
        )
        
        if not session_data:
            return None
        
        return payload
    
    async def get_user_data(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user data from database (mock implementation)"""
        # In production, query actual database
        if email == 'admin@tigerex.com':
            return {
                'id': 'user_1',
                'email': 'admin@tigerex.com',
                'password_hash': self.encryption.hash_password('secure_password')[0],
                'role': 'admin',
                '2fa_enabled': False,
                'totp_secret': None
            }
        return None
    
    @web.middleware
    async def security_middleware(self, request: web.Request, handler):
        """Security middleware for all requests"""
        start_time = time.time()
        
        # Log request
        REQUEST_COUNT.labels(method=request.method, endpoint=request.path).inc()
        
        # Rate limiting
        client_ip = request.remote
        rate_limit_key = f"global:{client_ip}"
        if not await self.rate_limiter.check_rate_limit(rate_limit_key):
            await self.auditor.log_security_event(SecurityEvent(
                event_type='rate_limit_exceeded',
                user_id=None,
                ip_address=client_ip,
                user_agent=request.headers.get('User-Agent', ''),
                timestamp=datetime.utcnow(),
                details={'endpoint': request.path},
                severity='medium'
            ))
            return web.json_response({'error': 'Rate limit exceeded'}, status=429)
        
        # IP security
        if not self.ip_security.is_ip_allowed(client_ip):
            await self.auditor.log_security_event(SecurityEvent(
                event_type='unauthorized_ip',
                user_id=None,
                ip_address=client_ip,
                user_agent=request.headers.get('User-Agent', ''),
                timestamp=datetime.utcnow(),
                details={'endpoint': request.path},
                severity='high'
            ))
            return web.json_response({'error': 'Unauthorized IP'}, status=403)
        
        # Process request
        try:
            response = await handler(request)
        except Exception as e:
            await self.auditor.log_security_event(SecurityEvent(
                event_type='request_error',
                user_id=None,
                ip_address=client_ip,
                user_agent=request.headers.get('User-Agent', ''),
                timestamp=datetime.utcnow(),
                details={'error': str(e), 'endpoint': request.path},
                severity='medium'
            ))
            raise
        
        # Log response time
        duration = time.time() - start_time
        REQUEST_DURATION.observe(duration)
        
        return response

# Initialize security system
security_system = ComprehensiveSecuritySystem()

# Example web application setup
async def create_security_app():
    """Create secure web application"""
    app = web.Application(middlewares=[security_system.security_middleware])
    
    # Authentication endpoint
    app.router.add_post('/auth/login', handle_login)
    app.router.add_post('/auth/logout', handle_logout)
    app.router.add_get('/auth/me', handle_get_user)
    
    # Protected endpoints
    app.router.add_get('/api/portfolio', handle_protected_endpoint)
    app.router.add_post('/api/trade', handle_protected_endpoint)
    
    return app

async def handle_login(request: web.Request):
    """Handle login request"""
    data = await request.json()
    
    result = await security_system.authenticate_user(
        data.get('email'),
        data.get('password'),
        request.remote,
        request.headers.get('User-Agent', ''),
        data.get('totp_token')
    )
    
    return web.json_response(result)

async def handle_logout(request: web.Request):
    """Handle logout request"""
    user_data = await security_system.authorize_request(request)
    if not user_data:
        return web.json_response({'error': 'Unauthorized'}, status=401)
    
    await security_system.session_manager.destroy_session(
        user_data['session_id'],
        user_data['user_id']
    )
    
    return web.json_response({'message': 'Logged out successfully'})

async def handle_get_user(request: web.Request):
    """Handle get user info request"""
    user_data = await security_system.authorize_request(request)
    if not user_data:
        return web.json_response({'error': 'Unauthorized'}, status=401)
    
    return web.json_response({'user': user_data})

async def handle_protected_endpoint(request: web.Request):
    """Example protected endpoint"""
    user_data = await security_system.authorize_request(request)
    if not user_data:
        return web.json_response({'error': 'Unauthorized'}, status=401)
    
    return web.json_response({'message': 'Access granted', 'user': user_data})

if __name__ == '__main__':
    # Start secure application
    app = asyncio.run(create_security_app())
    web.run_app(app, host='0.0.0.0', port=8080, ssl_context=None)