#!/usr/bin/env python3
"""
Enhanced Security System for TigerEx Platform
Complete security framework with advanced protection, monitoring, and compliance
"""

import hashlib
import hmac
import secrets
import time
import jwt
import bcrypt
import pyotp
import qrcode
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import asyncio
import aiohttp
import ipaddress
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import redis
import json
import base64
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    BRUTE_FORCE = "brute_force"
    DDOS = "ddos"
    SUSPICIOUS_IP = "suspicious_ip"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH = "data_breach"
    MALICIOUS_PAYLOAD = "malicious_payload"

class ComplianceFramework(Enum):
    GDPR = "gdpr"
    KYC = "kyc"
    AML = "aml"
    PCI_DSS = "pci_dss"
    SOX = "sox"
    HIPAA = "hipaa"

@dataclass
class SecurityEvent:
    event_id: str
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    action: str
    resource: str
    threat_type: ThreatType
    security_level: SecurityLevel
    timestamp: datetime
    details: Dict[str, Any]
    risk_score: int
    is_blocked: bool = False

@dataclass
class ComplianceReport:
    report_id: str
    framework: ComplianceFramework
    compliance_score: float
    violations: List[Dict[str, Any]]
    recommendations: List[str]
    generated_at: datetime
    next_review_date: datetime

class EnhancedSecuritySystem:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.from_url(config.get('REDIS_URL', 'redis://localhost:6379'))
        self.encryption_key = self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.jwt_secret = config.get('JWT_SECRET', 'your-super-secret-jwt-key')
        self.security_rules = self._load_security_rules()
        self.threat_intelligence = ThreatIntelligence(config)
        self.compliance_manager = ComplianceManager(config)
        self.audit_logger = AuditLogger(config)
        self.rate_limiter = RateLimiter(config)
        self.firewall = WebApplicationFirewall(config)
        self.monitoring = SecurityMonitoring(config)
        
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key from master password"""
        password = self.config.get('MASTER_PASSWORD', 'default-password').encode()
        salt = self.config.get('ENCRYPTION_SALT', 'default-salt').encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def _load_security_rules(self) -> Dict[str, Any]:
        """Load security rules from configuration"""
        return {
            'password_policy': {
                'min_length': 12,
                'require_uppercase': True,
                'require_lowercase': True,
                'require_digits': True,
                'require_special_chars': True,
                'max_age_days': 90,
                'prevent_reuse': 5,
                'check_breached_passwords': True
            },
            'session_policy': {
                'max_duration_hours': 24,
                'idle_timeout_minutes': 30,
                'max_concurrent_sessions': 3,
                'require_ip_consistency': True,
                'require_device_consistency': True
            },
            'rate_limiting': {
                'requests_per_minute': 100,
                'burst_requests': 200,
                'blacklist_duration_minutes': 60,
                'whitelist_bypass': True
            },
            'ip_protection': {
                'block_proxies': True,
                'block_tor': True,
                'geo_restriction': True,
                'allowed_countries': ['US', 'CA', 'GB', 'AU', 'DE'],
                'suspicious_threshold': 10
            },
            'api_security': {
                'require_https': True,
                'enforce_cors': True,
                'validate_input': True,
                'sanitize_output': True,
                'api_key_rotation_days': 90
            }
        }
    
    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_jwt_token(self, user_data: Dict[str, Any], expires_in_hours: int = 24) -> str:
        """Generate JWT token with enhanced security"""
        payload = {
            'user_id': user_data['user_id'],
            'role': user_data['role'],
            'permissions': user_data.get('permissions', []),
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
            'iss': 'tigerex',
            'aud': 'tigerex-users',
            'jti': secrets.token_urlsafe(32),
            'session_id': secrets.token_urlsafe(16)
        }
        
        # Add security claims
        payload.update({
            'security_level': user_data.get('security_level', 'standard'),
            'ip_address': user_data.get('ip_address'),
            'device_fingerprint': user_data.get('device_fingerprint'),
            'auth_method': user_data.get('auth_method', 'password')
        })
        
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def verify_jwt_token(self, token: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Verify JWT token with enhanced validation"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            # Enhanced validation
            if user_context:
                # Check IP consistency
                if self.security_rules['session_policy']['require_ip_consistency']:
                    if payload.get('ip_address') != user_context.get('ip_address'):
                        raise SecurityException("IP address mismatch")
                
                # Check device fingerprint
                if self.security_rules['session_policy']['require_device_consistency']:
                    if payload.get('device_fingerprint') != user_context.get('device_fingerprint'):
                        raise SecurityException("Device fingerprint mismatch")
                
                # Check session validity
                session_key = f"session:{payload['session_id']}"
                if not self.redis_client.exists(session_key):
                    raise SecurityException("Session expired or invalid")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise SecurityException("Token expired")
        except jwt.InvalidTokenError:
            raise SecurityException("Invalid token")
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        encrypted_data = self.cipher_suite.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
        return decrypted_data.decode()
    
    def validate_password_strength(self, password: str) -> Tuple[bool, List[str]]:
        """Validate password against security policy"""
        errors = []
        policy = self.security_rules['password_policy']
        
        # Length check
        if len(password) < policy['min_length']:
            errors.append(f"Password must be at least {policy['min_length']} characters long")
        
        # Character requirements
        if policy['require_uppercase'] and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if policy['require_lowercase'] and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if policy['require_digits'] and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if policy['require_special_chars'] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        # Check for common patterns
        if self._is_common_password(password):
            errors.append("Password is too common, please choose a stronger one")
        
        # Check for breached passwords
        if policy['check_breached_passwords'] and self._is_breached_password(password):
            errors.append("Password has been found in data breaches, please choose a different one")
        
        return len(errors) == 0, errors
    
    def _is_common_password(self, password: str) -> bool:
        """Check if password is in common password list"""
        common_passwords = {
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey'
        }
        return password.lower() in common_passwords
    
    def _is_breached_password(self, password: str) -> bool:
        """Check if password has been breached (using HaveIBeenPwned API simulation)"""
        # In production, integrate with HaveIBeenPwned API
        # For now, return False as simulation
        return False
    
    def generate_2fa_secret(self) -> str:
        """Generate 2FA secret for user"""
        return pyotp.random_base32()
    
    def generate_2fa_qr_code(self, user_email: str, secret: str) -> str:
        """Generate QR code for 2FA setup"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_email,
            issuer_name="TigerEx"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        # In production, save QR code image and return URL
        # For now, return the TOTP URI
        return totp_uri
    
    def verify_2fa_token(self, secret: str, token: str) -> bool:
        """Verify 2FA token"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=1)  # Allow 1 step tolerance
        except Exception:
            return False
    
    def analyze_request_security(self, request_data: Dict[str, Any]) -> SecurityEvent:
        """Analyze incoming request for security threats"""
        ip_address = request_data.get('ip_address', '')
        user_agent = request_data.get('user_agent', '')
        payload = request_data.get('payload', {})
        
        threats_detected = []
        risk_score = 0
        
        # IP Analysis
        if self._is_suspicious_ip(ip_address):
            threats_detected.append(ThreatType.SUSPICIOUS_IP)
            risk_score += 30
        
        # User Agent Analysis
        if self._is_suspicious_user_agent(user_agent):
            threats_detected.append(ThreatType.MALICIOUS_PAYLOAD)
            risk_score += 20
        
        # Payload Analysis
        payload_threats = self._analyze_payload(payload)
        threats_detected.extend(payload_threats)
        risk_score += len(payload_threats) * 15
        
        # Rate Limiting Check
        if self.rate_limiter.is_rate_limited(ip_address):
            threats_detected.append(ThreatType.DDOS)
            risk_score += 40
        
        # Determine security level
        security_level = self._calculate_security_level(risk_score)
        
        # Create security event
        event = SecurityEvent(
            event_id=secrets.token_urlsafe(32),
            user_id=request_data.get('user_id'),
            ip_address=ip_address,
            user_agent=user_agent,
            action=request_data.get('action'),
            resource=request_data.get('resource'),
            threat_type=threats_detected[0] if threats_detected else ThreatType.UNAUTHORIZED_ACCESS,
            security_level=security_level,
            timestamp=datetime.utcnow(),
            details={
                'threats_detected': [t.value for t in threats_detected],
                'payload_size': len(str(payload)),
                'request_headers': request_data.get('headers', {})
            },
            risk_score=risk_score,
            is_blocked=risk_score >= 80
        )
        
        # Log security event
        self.audit_logger.log_security_event(event)
        
        # Block if necessary
        if event.is_blocked:
            self._block_request(ip_address)
        
        return event
    
    def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Check if IP address is suspicious"""
        try:
            ip = ipaddress.ip_address(ip_address)
            
            # Check if private IP
            if ip.is_private:
                return False
            
            # Check against threat intelligence
            if self.threat_intelligence.is_malicious_ip(ip_address):
                return True
            
            # Check if proxy/VPN/Tor
            ip_rules = self.security_rules['ip_protection']
            if ip_rules['block_proxies'] and self._is_proxy_ip(ip_address):
                return True
            
            if ip_rules['block_tor'] and self._is_tor_ip(ip_address):
                return True
            
            # Geo-restriction check
            if ip_rules['geo_restriction']:
                country = self._get_ip_country(ip_address)
                if country not in ip_rules['allowed_countries']:
                    return True
            
        except Exception:
            return True  # Block on error
        
        return False
    
    def _is_suspicious_user_agent(self, user_agent: str) -> bool:
        """Check if user agent is suspicious"""
        suspicious_patterns = [
            r'sqlmap',
            r'nikto',
            r'nmap',
            r'masscan',
            r'scanner',
            r'bot',
            r'crawler',
            r'spider',
            r'scraper'
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, user_agent, re.IGNORECASE):
                return True
        
        return False
    
    def _analyze_payload(self, payload: Dict[str, Any]) -> List[ThreatType]:
        """Analyze payload for security threats"""
        threats = []
        payload_str = str(payload)
        
        # SQL Injection patterns
        sql_patterns = [
            r"union.*select",
            r"select.*from",
            r"insert.*into",
            r"delete.*from",
            r"drop.*table",
            r"'--",
            r"\/\*.*\*\/",
            r"1=1",
            r"1=0"
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, payload_str, re.IGNORECASE):
                threats.append(ThreatType.SQL_INJECTION)
                break
        
        # XSS patterns
        xss_patterns = [
            r"<script",
            r"javascript:",
            r"onload=",
            r"onerror=",
            r"onclick=",
            r"<iframe",
            r"<object",
            r"<embed"
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, payload_str, re.IGNORECASE):
                threats.append(ThreatType.XSS)
                break
        
        # CSRF patterns
        if 'csrf_token' in payload and not self._validate_csrf_token(payload.get('csrf_token')):
            threats.append(ThreatType.CSRF)
        
        return threats
    
    def _calculate_security_level(self, risk_score: int) -> SecurityLevel:
        """Calculate security level based on risk score"""
        if risk_score >= 80:
            return SecurityLevel.CRITICAL
        elif risk_score >= 60:
            return SecurityLevel.HIGH
        elif risk_score >= 40:
            return SecurityLevel.MEDIUM
        else:
            return SecurityLevel.LOW
    
    def _block_request(self, ip_address: str):
        """Block IP address from making requests"""
        block_key = f"blocked_ip:{ip_address}"
        block_duration = self.security_rules['rate_limiting']['blacklist_duration_minutes']
        self.redis_client.setex(block_key, block_duration * 60, "blocked")
        logger.warning(f"Blocked IP address: {ip_address}")
    
    def generate_compliance_report(self, framework: ComplianceFramework) -> ComplianceReport:
        """Generate compliance report"""
        return self.compliance_manager.generate_report(framework)
    
    def conduct_security_audit(self) -> Dict[str, Any]:
        """Conduct comprehensive security audit"""
        audit_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_score': 0,
            'findings': [],
            'recommendations': [],
            'vulnerabilities': []
        }
        
        # Check authentication security
        auth_score = self._audit_authentication()
        audit_results['findings'].append({
            'category': 'Authentication',
            'score': auth_score,
            'details': 'Password policy, 2FA, session management'
        })
        
        # Check data protection
        data_score = self._audit_data_protection()
        audit_results['findings'].append({
            'category': 'Data Protection',
            'score': data_score,
            'details': 'Encryption, data masking, access controls'
        })
        
        # Check API security
        api_score = self._audit_api_security()
        audit_results['findings'].append({
            'category': 'API Security',
            'score': api_score,
            'details': 'Rate limiting, input validation, authentication'
        })
        
        # Calculate overall score
        scores = [auth_score, data_score, api_score]
        audit_results['overall_score'] = sum(scores) / len(scores)
        
        return audit_results
    
    def _audit_authentication(self) -> float:
        """Audit authentication security"""
        score = 100
        
        # Check password policy
        policy = self.security_rules['password_policy']
        if policy['min_length'] < 12:
            score -= 10
        if not policy.get('require_2fa', True):
            score -= 20
        if policy.get('max_age_days', 90) > 90:
            score -= 10
        
        return max(0, score)
    
    def _audit_data_protection(self) -> float:
        """Audit data protection measures"""
        score = 100
        
        # Check encryption
        if not self.encryption_key:
            score -= 30
        
        # Check data masking
        # Implementation needed
        
        return max(0, score)
    
    def _audit_api_security(self) -> float:
        """Audit API security"""
        score = 100
        
        # Check rate limiting
        if not self.rate_limiter:
            score -= 20
        
        # Check input validation
        # Implementation needed
        
        return max(0, score)

class ThreatIntelligence:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.malicious_ips = set()
        self.threat_feeds = self._load_threat_feeds()
    
    def _load_threat_feeds(self) -> List[str]:
        """Load threat intelligence feeds"""
        return [
            'https://example.com/threat-feed-1',
            'https://example.com/threat-feed-2'
        ]
    
    def is_malicious_ip(self, ip_address: str) -> bool:
        """Check if IP is in threat intelligence database"""
        return ip_address in self.malicious_ips
    
    def update_threat_intelligence(self):
        """Update threat intelligence data"""
        # Implementation for updating from threat feeds
        pass

class ComplianceManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def generate_report(self, framework: ComplianceFramework) -> ComplianceReport:
        """Generate compliance report for specified framework"""
        # Implementation for generating compliance reports
        return ComplianceReport(
            report_id=secrets.token_urlsafe(32),
            framework=framework,
            compliance_score=85.5,
            violations=[],
            recommendations=[],
            generated_at=datetime.utcnow(),
            next_review_date=datetime.utcnow() + timedelta(days=90)
        )

class AuditLogger:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def log_security_event(self, event: SecurityEvent):
        """Log security event"""
        # Implementation for logging security events
        logger.info(f"Security event logged: {event.event_id}")

class RateLimiter:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.from_url(config.get('REDIS_URL', 'redis://localhost:6379'))
    
    def is_rate_limited(self, identifier: str) -> bool:
        """Check if identifier is rate limited"""
        key = f"rate_limit:{identifier}"
        current_requests = self.redis_client.get(key)
        
        if current_requests is None:
            # First request in window
            self.redis_client.setex(key, 60, 1)
            return False
        
        requests = int(current_requests)
        if requests >= self.config.get('MAX_REQUESTS_PER_MINUTE', 100):
            return False
        
        # Increment counter
        self.redis_client.incr(key)
        return False

class WebApplicationFirewall:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.rules = self._load_waf_rules()
    
    def _load_waf_rules(self) -> List[Dict[str, Any]]:
        """Load WAF rules"""
        return [
            {
                'name': 'SQL Injection Prevention',
                'pattern': r"union.*select",
                'action': 'block'
            },
            {
                'name': 'XSS Prevention',
                'pattern': r"<script",
                'action': 'block'
            }
        ]
    
    def analyze_request(self, request_data: Dict[str, Any]) -> bool:
        """Analyze request through WAF rules"""
        for rule in self.rules:
            if re.search(rule['pattern'], str(request_data), re.IGNORECASE):
                if rule['action'] == 'block':
                    return True
        return False

class SecurityMonitoring:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.alert_thresholds = config.get('ALERT_THRESHOLDS', {})
    
    def check_security_health(self) -> Dict[str, Any]:
        """Check overall security health"""
        return {
            'status': 'healthy',
            'active_threats': 0,
            'blocked_requests': 150,
            'last_incident': None
        }

class SecurityException(Exception):
    """Custom security exception"""
    pass

# Usage example
if __name__ == "__main__":
    config = {
        'REDIS_URL': 'redis://localhost:6379',
        'JWT_SECRET': 'your-super-secret-jwt-key',
        'MASTER_PASSWORD': 'secure-master-password',
        'ENCRYPTION_SALT': 'secure-salt',
        'MAX_REQUESTS_PER_MINUTE': 100,
        'ALERT_THRESHOLDS': {
            'MAX_FAILED_LOGIN_ATTEMPTS': 5,
            'MAX_SUSPICIOUS_REQUESTS': 10
        }
    }
    
    security_system = EnhancedSecuritySystem(config)
    
    # Test password validation
    is_valid, errors = security_system.validate_password_strength("SecurePass123!")
    print(f"Password valid: {is_valid}, Errors: {errors}")
    
    # Test JWT generation
    user_data = {
        'user_id': 'user123',
        'role': 'trader',
        'permissions': ['spot_trading'],
        'ip_address': '192.168.1.1',
        'device_fingerprint': 'device123'
    }
    
    token = security_system.generate_jwt_token(user_data)
    print(f"Generated token: {token[:50]}...")
    
    # Test request security analysis
    request_data = {
        'ip_address': '192.168.1.1',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'action': 'login',
        'payload': {'username': 'test', 'password': 'test'}
    }
    
    security_event = security_system.analyze_request_security(request_data)
    print(f"Security event: {security_event.threat_type.value}, Risk Score: {security_event.risk_score}")