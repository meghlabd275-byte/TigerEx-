#!/usr/bin/env python3
"""
TigerEx Complete Security Audit System
Comprehensive security monitoring, vulnerability scanning, and protection
Category: Security & Compliance
Version: 4.0.0
"""

import asyncio
import hashlib
import hmac
import secrets
import time
import json
import logging
import re
import ssl
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import aioredis
import aiohttp
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import sqlparse
import bandit
from bandit.core import manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VulnerabilityType(Enum):
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    AUTHENTICATION_BYPASS = "auth_bypass"
    AUTHORIZATION_BYPASS = "authz_bypass"
    DATA_EXPOSURE = "data_exposure"
    DENIAL_OF_SERVICE = "dos"
    INSECURE_CRYPTO = "insecure_crypto"
    INSECURE_CONFIG = "insecure_config"
    MISSING_HEADERS = "missing_headers"
    WEAK_PASSWORDS = "weak_passwords"
    SESSION_HIJACKING = "session_hijacking"
    PRIVILEGE_ESCALATION = "privilege_escalation"

class SeverityLevel(Enum):
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1
    INFO = 0

@dataclass
class Vulnerability:
    type: VulnerabilityType
    severity: SeverityLevel
    description: str
    location: str
    evidence: str
    recommendation: str
    timestamp: datetime
    cvss_score: float = 0.0

class SecurityAuditManager:
    """Complete security audit and vulnerability management system"""
    
    def __init__(self):
        self.redis = None
        self.encryption_key = None
        self.session_store = {}
        self.blocked_ips = set()
        self.rate_limits = {}
        self.security_rules = self._load_security_rules()
        self.vulnerability_scanner = VulnerabilityScanner()
        
    async def initialize(self):
        """Initialize security audit system"""
        self.redis = aioredis.from_url("redis://localhost:6379")
        self.encryption_key = self._generate_encryption_key()
        await self._setup_security_monitoring()
        
    def _generate_encryption_key(self) -> bytes:
        """Generate secure encryption key"""
        password = secrets.token_bytes(32)
        salt = secrets.token_bytes(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def _load_security_rules(self) -> Dict[str, Any]:
        """Load comprehensive security rules"""
        return {
            "sql_injection": {
                "patterns": [
                    r"('|(\')|('')|(%27)|(%22))",
                    r"(union|select|insert|update|delete|drop|create|alter|exec|execute)",
                    r"(--|#|/\*|\*/|;)",
                    r"(xp_|sp_|0x)",
                ],
                "detection_enabled": True,
                "auto_block": True,
            },
            "xss": {
                "patterns": [
                    r"(<script|<iframe|<object|<embed)",
                    r"(javascript:|vbscript:|onload=|onerror=)",
                    r"(alert|confirm|prompt|eval)",
                    r"(document\.|window\.|location\.)",
                ],
                "detection_enabled": True,
                "auto_block": True,
            },
            "authentication": {
                "max_attempts": 5,
                "lockout_duration": 900,  # 15 minutes
                "password_min_length": 12,
                "password_complexity": True,
                "2fa_required": True,
            },
            "rate_limiting": {
                "requests_per_minute": 60,
                "burst_limit": 100,
                "block_threshold": 200,
            },
            "session_security": {
                "timeout": 3600,  # 1 hour
                "renewal_threshold": 300,  # 5 minutes
                "max_concurrent": 3,
                "binding": "ip_user_agent",
            }
        }
    
    async def _setup_security_monitoring(self):
        """Setup continuous security monitoring"""
        await self._initialize_blocklist()
        await self._setup_rate_limiting()
        await self._start_vulnerability_scanner()
    
    async def analyze_request(self, request_data: Dict[str, Any]) -> List[Vulnerability]:
        """Analyze incoming request for security vulnerabilities"""
        vulnerabilities = []
        
        # SQL Injection Detection
        sql_vulns = await self._detect_sql_injection(request_data)
        vulnerabilities.extend(sql_vulns)
        
        # XSS Detection
        xss_vulns = await self._detect_xss(request_data)
        vulnerabilities.extend(xss_vulns)
        
        # Authentication Analysis
        auth_vulns = await self._analyze_authentication(request_data)
        vulnerabilities.extend(auth_vulns)
        
        # Rate Limiting Check
        rate_vulns = await self._check_rate_limits(request_data)
        vulnerabilities.extend(rate_vulns)
        
        # IP Reputation Check
        ip_vulns = await self._check_ip_reputation(request_data.get('ip'))
        vulnerabilities.extend(ip_vulns)
        
        # Session Security
        session_vulns = await self._validate_session(request_data)
        vulnerabilities.extend(session_vulns)
        
        # Store findings
        await self._store_vulnerabilities(vulnerabilities)
        
        return vulnerabilities
    
    async def _detect_sql_injection(self, request_data: Dict[str, Any]) -> List[Vulnerability]:
        """Detect SQL injection attempts"""
        vulnerabilities = []
        sql_rules = self.security_rules["sql_injection"]
        
        # Check all input parameters
        for key, value in request_data.items():
            if isinstance(value, str):
                for pattern in sql_rules["patterns"]:
                    if re.search(pattern, value, re.IGNORECASE):
                        vuln = Vulnerability(
                            type=VulnerabilityType.SQL_INJECTION,
                            severity=SeverityLevel.HIGH,
                            description=f"Potential SQL injection detected in parameter: {key}",
                            location=f"Request parameter: {key}",
                            evidence=value,
                            recommendation="Implement parameterized queries and input validation",
                            timestamp=datetime.utcnow(),
                            cvss_score=7.5
                        )
                        vulnerabilities.append(vuln)
                        
                        if sql_rules["auto_block"]:
                            await self._block_ip(request_data.get('ip'))
                        break
        
        return vulnerabilities
    
    async def _detect_xss(self, request_data: Dict[str, Any]) -> List[Vulnerability]:
        """Detect XSS attempts"""
        vulnerabilities = []
        xss_rules = self.security_rules["xss"]
        
        for key, value in request_data.items():
            if isinstance(value, str):
                for pattern in xss_rules["patterns"]:
                    if re.search(pattern, value, re.IGNORECASE):
                        vuln = Vulnerability(
                            type=VulnerabilityType.XSS,
                            severity=SeverityLevel.HIGH,
                            description=f"Potential XSS detected in parameter: {key}",
                            location=f"Request parameter: {key}",
                            evidence=value,
                            recommendation="Implement proper output encoding and CSP headers",
                            timestamp=datetime.utcnow(),
                            cvss_score=6.1
                        )
                        vulnerabilities.append(vuln)
                        
                        if xss_rules["auto_block"]:
                            await self._block_ip(request_data.get('ip'))
                        break
        
        return vulnerabilities
    
    async def _analyze_authentication(self, request_data: Dict[str, Any]) -> List[Vulnerability]:
        """Analyze authentication security"""
        vulnerabilities = []
        auth_rules = self.security_rules["authentication"]
        
        # Check password security
        if 'password' in request_data:
            password = request_data['password']
            if len(password) < auth_rules["password_min_length"]:
                vuln = Vulnerability(
                    type=VulnerabilityType.WEAK_PASSWORDS,
                    severity=SeverityLevel.MEDIUM,
                    description="Weak password detected",
                    location="Authentication endpoint",
                    evidence=f"Password length: {len(password)}",
                    recommendation="Enforce strong password policies",
                    timestamp=datetime.utcnow(),
                    cvss_score=4.0
                )
                vulnerabilities.append(vuln)
        
        # Check for failed login attempts
        if 'username' in request_data:
            username = request_data['username']
            failed_attempts = await self.redis.get(f"failed_login:{username}")
            if failed_attempts and int(failed_attempts) >= auth_rules["max_attempts"]:
                vuln = Vulnerability(
                    type=VulnerabilityType.AUTHENTICATION_BYPASS,
                    severity=SeverityLevel.HIGH,
                    description=f"Account lockout threshold reached for user: {username}",
                    location="Authentication system",
                    evidence=f"Failed attempts: {failed_attempts}",
                    recommendation="Implement account lockout and notification",
                    timestamp=datetime.utcnow(),
                    cvss_score=5.5
                )
                vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    async def _check_rate_limits(self, request_data: Dict[str, Any]) -> List[Vulnerability]:
        """Check rate limiting violations"""
        vulnerabilities = []
        rate_rules = self.security_rules["rate_limiting"]
        ip = request_data.get('ip')
        
        if ip:
            current_time = int(time.time())
            key = f"rate_limit:{ip}:{current_time // 60}"
            
            request_count = await self.redis.incr(key)
            await self.redis.expire(key, 60)
            
            if request_count > rate_rules["block_threshold"]:
                vuln = Vulnerability(
                    type=VulnerabilityType.DENIAL_OF_SERVICE,
                    severity=SeverityLevel.MEDIUM,
                    description=f"Rate limit threshold exceeded for IP: {ip}",
                    location="Rate limiting system",
                    evidence=f"Requests: {request_count}",
                    recommendation="Implement stricter rate limiting",
                    timestamp=datetime.utcnow(),
                    cvss_score=5.0
                )
                vulnerabilities.append(vuln)
                await self._block_ip(ip)
        
        return vulnerabilities
    
    async def _check_ip_reputation(self, ip: str) -> List[Vulnerability]:
        """Check IP reputation against threat intelligence"""
        vulnerabilities = []
        
        if ip and ip in self.blocked_ips:
            vuln = Vulnerability(
                type=VulnerabilityType.AUTHENTICATION_BYPASS,
                severity=SeverityLevel.CRITICAL,
                description=f"Blocked IP attempting access: {ip}",
                location="IP Reputation Check",
                evidence=f"IP found in blocklist",
                recommendation="Maintain IP blocklist and monitor for threats",
                timestamp=datetime.utcnow(),
                cvss_score=9.0
            )
            vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    async def _validate_session(self, request_data: Dict[str, Any]) -> List[Vulnerability]:
        """Validate session security"""
        vulnerabilities = []
        session_rules = self.security_rules["session_security"]
        
        # Check session timeout
        if 'session_id' in request_data:
            session_id = request_data['session_id']
            session_data = await self.redis.get(f"session:{session_id}")
            
            if not session_data:
                vuln = Vulnerability(
                    type=VulnerabilityType.SESSION_HIJACKING,
                    severity=SeverityLevel.MEDIUM,
                    description="Invalid or expired session",
                    location="Session validation",
                    evidence=f"Session ID: {session_id}",
                    recommendation="Implement proper session validation and renewal",
                    timestamp=datetime.utcnow(),
                    cvss_score=4.0
                )
                vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    async def _store_vulnerabilities(self, vulnerabilities: List[Vulnerability]):
        """Store detected vulnerabilities for analysis"""
        for vuln in vulnerabilities:
            key = f"vulnerability:{int(time.time())}:{secrets.token_hex(8)}"
            await self.redis.setex(key, 86400, json.dumps({
                'type': vuln.type.value,
                'severity': vuln.severity.value,
                'description': vuln.description,
                'location': vuln.location,
                'evidence': vuln.evidence,
                'recommendation': vuln.recommendation,
                'timestamp': vuln.timestamp.isoformat(),
                'cvss_score': vuln.cvss_score
            }))
    
    async def _block_ip(self, ip: str):
        """Block malicious IP"""
        self.blocked_ips.add(ip)
        await self.redis.setex(f"blocked_ip:{ip}", 3600, "blocked")
        logger.warning(f"IP {ip} has been blocked due to malicious activity")
    
    async def _initialize_blocklist(self):
        """Initialize IP blocklist"""
        blocked_ips = await self.redis.keys("blocked_ip:*")
        for key in blocked_ips:
            ip = key.decode().split(":")[1]
            self.blocked_ips.add(ip)
    
    async def _setup_rate_limiting(self):
        """Setup rate limiting configuration"""
        pass
    
    async def _start_vulnerability_scanner(self):
        """Start automated vulnerability scanning"""
        pass
    
    async def scan_codebase(self, codebase_path: str) -> List[Vulnerability]:
        """Scan codebase for security vulnerabilities"""
        return await self.vulnerability_scanner.scan_directory(codebase_path)
    
    async def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        # Get vulnerability statistics
        all_vulns = await self.redis.keys("vulnerability:*")
        
        vuln_count = len(all_vulns)
        critical_vulns = 0
        high_vulns = 0
        medium_vulns = 0
        low_vulns = 0
        
        for key in all_vulns:
            vuln_data = await self.redis.get(key)
            if vuln_data:
                vuln = json.loads(vuln_data)
                severity = vuln.get('severity', 0)
                
                if severity >= 4:
                    critical_vulns += 1
                elif severity >= 3:
                    high_vulns += 1
                elif severity >= 2:
                    medium_vulns += 1
                else:
                    low_vulns += 1
        
        return {
            "total_vulnerabilities": vuln_count,
            "critical_vulnerabilities": critical_vulns,
            "high_vulnerabilities": high_vulns,
            "medium_vulnerabilities": medium_vulns,
            "low_vulnerabilities": low_vulns,
            "blocked_ips": len(self.blocked_ips),
            "security_score": max(0, 100 - (critical_vulns * 10) - (high_vulns * 5) - (medium_vulns * 2) - low_vulns),
            "last_scan": datetime.utcnow().isoformat(),
            "recommendations": await self._generate_recommendations()
        }
    
    async def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations based on findings"""
        recommendations = []
        
        # Check for critical vulnerabilities
        critical_count = await self.redis.eval("""
            local keys = redis.call('keys', 'vulnerability:*')
            local critical = 0
            for i=1,#keys do
                local data = redis.call('get', keys[i])
                if data then
                    local vuln = cjson.decode(data)
                    if vuln.severity >= 4 then
                        critical = critical + 1
                    end
                end
            end
            return critical
        """)
        
        if critical_count > 0:
            recommendations.append("Critical vulnerabilities detected. Immediate action required.")
        
        # Check authentication security
        recommendations.append("Enable multi-factor authentication for all admin accounts.")
        recommendations.append("Implement regular security audits and penetration testing.")
        recommendations.append("Keep all dependencies and frameworks updated to latest versions.")
        recommendations.append("Implement comprehensive logging and monitoring.")
        
        return recommendations

class VulnerabilityScanner:
    """Advanced vulnerability scanner for code analysis"""
    
    async def scan_directory(self, directory: str) -> List[Vulnerability]:
        """Scan directory for vulnerabilities"""
        vulnerabilities = []
        
        # Scan Python files
        py_files = self._find_files(directory, "*.py")
        for file_path in py_files:
            vulns = await self._scan_python_file(file_path)
            vulnerabilities.extend(vulns)
        
        # Scan JavaScript files
        js_files = self._find_files(directory, "*.js")
        for file_path in js_files:
            vulns = await self._scan_javascript_file(file_path)
            vulnerabilities.extend(vulns)
        
        # Scan Solidity files
        sol_files = self._find_files(directory, "*.sol")
        for file_path in sol_files:
            vulns = await self._scan_solidity_file(file_path)
            vulnerabilities.extend(vulns)
        
        return vulnerabilities
    
    def _find_files(self, directory: str, pattern: str) -> List[str]:
        """Find files matching pattern"""
        import glob
        return glob.glob(f"{directory}/**/{pattern}", recursive=True)
    
    async def _scan_python_file(self, file_path: str) -> List[Vulnerability]:
        """Scan Python file for security issues"""
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Use Bandit for Python security analysis
            b_mgr = manager.BanditManager(bandit.config.BanditConfig(), 'file')
            b_mgr.discover_files([file_path], False)
            results = b_mgr.get_issue_list()
            
            for result in results:
                vuln = Vulnerability(
                    type=self._map_bandit_type(result.test_id),
                    severity=self._map_bandit_severity(result.severity),
                    description=result.text,
                    location=f"{file_path}:{result.lineno}",
                    evidence=result.get_code(),
                    recommendation=result.get_message(),
                    timestamp=datetime.utcnow(),
                    cvss_score=result.get_cvss_score()
                )
                vulnerabilities.append(vuln)
            
            # Custom pattern scanning
            vulnerabilities.extend(await self._scan_python_patterns(content, file_path))
            
        except Exception as e:
            logger.error(f"Error scanning Python file {file_path}: {e}")
        
        return vulnerabilities
    
    async def _scan_javascript_file(self, file_path: str) -> List[Vulnerability]:
        """Scan JavaScript file for security issues"""
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            vulnerabilities.extend(await self._scan_js_patterns(content, file_path))
            
        except Exception as e:
            logger.error(f"Error scanning JavaScript file {file_path}: {e}")
        
        return vulnerabilities
    
    async def _scan_solidity_file(self, file_path: str) -> List[Vulnerability]:
        """Scan Solidity file for security issues"""
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            vulnerabilities.extend(await self._scan_solidity_patterns(content, file_path))
            
        except Exception as e:
            logger.error(f"Error scanning Solidity file {file_path}: {e}")
        
        return vulnerabilities
    
    async def _scan_python_patterns(self, content: str, file_path: str) -> List[Vulnerability]:
        """Scan Python code for security patterns"""
        vulnerabilities = []
        
        # Check for hardcoded secrets
        if re.search(r'(password|secret|key)\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE):
            vuln = Vulnerability(
                type=VulnerabilityType.DATA_EXPOSURE,
                severity=SeverityLevel.HIGH,
                description="Hardcoded secret detected",
                location=file_path,
                evidence="Hardcoded password/secret/key found",
                recommendation="Use environment variables or secure configuration",
                timestamp=datetime.utcnow(),
                cvss_score=7.5
            )
            vulnerabilities.append(vuln)
        
        # Check for SQL injection vulnerabilities
        if re.search(r'execute\s*\(\s*["\'][^"\']*["\']\s*%', content):
            vuln = Vulnerability(
                type=VulnerabilityType.SQL_INJECTION,
                severity=SeverityLevel.HIGH,
                description="Potential SQL injection vulnerability",
                location=file_path,
                evidence="String formatting in SQL query",
                recommendation="Use parameterized queries",
                timestamp=datetime.utcnow(),
                cvss_score=8.1
            )
            vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    async def _scan_js_patterns(self, content: str, file_path: str) -> List[Vulnerability]:
        """Scan JavaScript code for security patterns"""
        vulnerabilities = []
        
        # Check for eval usage
        if re.search(r'eval\s*\(', content):
            vuln = Vulnerability(
                type=VulnerabilityType.XSS,
                severity=SeverityLevel.HIGH,
                description="Use of eval() function detected",
                location=file_path,
                evidence="eval() usage found",
                recommendation="Avoid eval() function",
                timestamp=datetime.utcnow(),
                cvss_score=6.1
            )
            vulnerabilities.append(vuln)
        
        # Check for innerHTML usage
        if re.search(r'innerHTML\s*=', content):
            vuln = Vulnerability(
                type=VulnerabilityType.XSS,
                severity=SeverityLevel.MEDIUM,
                description="Potential XSS vulnerability with innerHTML",
                location=file_path,
                evidence="innerHTML assignment found",
                recommendation="Use textContent or proper sanitization",
                timestamp=datetime.utcnow(),
                cvss_score=5.4
            )
            vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    async def _scan_solidity_patterns(self, content: str, file_path: str) -> List[Vulnerability]:
        """Scan Solidity code for security patterns"""
        vulnerabilities = []
        
        # Check for unguarded external calls
        if re.search(r'function.*external.*{', content) and 'nonReentrant' not in content:
            vuln = Vulnerability(
                type=VulnerabilityType.PRIVILEGE_ESCALATION,
                severity=SeverityLevel.HIGH,
                description="External function without reentrancy guard",
                location=file_path,
                evidence="External function without nonReentrant modifier",
                recommendation="Add reentrancy guard to external functions",
                timestamp=datetime.utcnow(),
                cvss_score=7.5
            )
            vulnerabilities.append(vuln)
        
        # Check for integer overflow/underflow
        if re.search(r'.*\s*\+.*\s*', content) and 'SafeMath' not in content:
            vuln = Vulnerability(
                type=VulnerabilityType.PRIVILEGE_ESCALATION,
                severity=SeverityLevel.MEDIUM,
                description="Potential integer overflow/underflow",
                location=file_path,
                evidence="Arithmetic operations without SafeMath",
                recommendation="Use SafeMath library for arithmetic operations",
                timestamp=datetime.utcnow(),
                cvss_score=5.9
            )
            vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _map_bandit_type(self, bandit_test_id: str) -> VulnerabilityType:
        """Map Bandit test ID to vulnerability type"""
        mapping = {
            'B101': VulnerabilityType.AUTHENTICATION_BYPASS,
            'B102': VulnerabilityType.AUTHENTICATION_BYPASS,
            'B103': VulnerabilityType.PRIVILEGE_ESCALATION,
            'B104': VulnerabilityType.DATA_EXPOSURE,
            'B105': VulnerabilityType.INSECURE_CONFIG,
            'B106': VulnerabilityType.INSECURE_CONFIG,
            'B107': VulnerabilityType.AUTHENTICATION_BYPASS,
            'B108': VulnerabilityType.INSECURE_CONFIG,
            'B110': VulnerabilityType.PRIVILEGE_ESCALATION,
            'B112': VulnerabilityType.AUTHENTICATION_BYPASS,
            'B201': VulnerabilityType.DATA_EXPOSURE,
            'B301': VulnerabilityType.DATA_EXPOSURE,
            'B302': VulnerabilityType.PRIVILEGE_ESCALATION,
            'B303': VulnerabilityType.DATA_EXPOSURE,
            'B304': VulnerabilityType.DATA_EXPOSURE,
            'B305': VulnerabilityType.AUTHENTICATION_BYPASS,
            'B306': VulnerabilityType.DATA_EXPOSURE,
            'B307': VulnerabilityType.DATA_EXPOSURE,
            'B308': VulnerabilityType.DATA_EXPOSURE,
            'B309': VulnerabilityType.DATA_EXPOSURE,
            'B310': VulnerabilityType.DATA_EXPOSURE,
            'B311': VulnerabilityType.DATA_EXPOSURE,
            'B312': VulnerabilityType.DATA_EXPOSURE,
            'B313': VulnerabilityType.DATA_EXPOSURE,
            'B314': VulnerabilityType.DATA_EXPOSURE,
            'B315': VulnerabilityType.DATA_EXPOSURE,
            'B316': VulnerabilityType.DATA_EXPOSURE,
            'B317': VulnerabilityType.DATA_EXPOSURE,
            'B318': VulnerabilityType.DATA_EXPOSURE,
            'B319': VulnerabilityType.DATA_EXPOSURE,
            'B320': VulnerabilityType.DATA_EXPOSURE,
            'B321': VulnerabilityType.DATA_EXPOSURE,
            'B322': VulnerabilityType.DATA_EXPOSURE,
            'B323': VulnerabilityType.DATA_EXPOSURE,
            'B324': VulnerabilityType.DATA_EXPOSURE,
            'B325': VulnerabilityType.DATA_EXPOSURE,
            'B401': VulnerabilityType.DATA_EXPOSURE,
            'B402': VulnerabilityType.DATA_EXPOSURE,
            'B403': VulnerabilityType.DATA_EXPOSURE,
            'B404': VulnerabilityType.DATA_EXPOSURE,
            'B405': VulnerabilityType.DATA_EXPOSURE,
            'B406': VulnerabilityType.DATA_EXPOSURE,
            'B407': VulnerabilityType.DATA_EXPOSURE,
            'B408': VulnerabilityType.DATA_EXPOSURE,
            'B409': VulnerabilityType.DATA_EXPOSURE,
            'B410': VulnerabilityType.DATA_EXPOSURE,
            'B411': VulnerabilityType.DATA_EXPOSURE,
            'B412': VulnerabilityType.DATA_EXPOSURE,
            'B413': VulnerabilityType.DATA_EXPOSURE,
            'B501': VulnerabilityType.DATA_EXPOSURE,
            'B502': VulnerabilityType.DATA_EXPOSURE,
            'B503': VulnerabilityType.DATA_EXPOSURE,
            'B504': VulnerabilityType.DATA_EXPOSURE,
            'B505': VulnerabilityType.DATA_EXPOSURE,
            'B506': VulnerabilityType.DATA_EXPOSURE,
            'B507': VulnerabilityType.DATA_EXPOSURE,
            'B601': VulnerabilityType.SQL_INJECTION,
            'B602': VulnerabilityType.DATA_EXPOSURE,
            'B603': VulnerabilityType.DATA_EXPOSURE,
            'B604': VulnerabilityType.DATA_EXPOSURE,
            'B605': VulnerabilityType.DATA_EXPOSURE,
            'B606': VulnerabilityType.DATA_EXPOSURE,
            'B607': VulnerabilityType.DATA_EXPOSURE,
            'B608': VulnerabilityType.SQL_INJECTION,
            'B609': VulnerabilityType.DATA_EXPOSURE,
            'B610': VulnerabilityType.DATA_EXPOSURE,
            'B611': VulnerabilityType.DATA_EXPOSURE,
            'B701': VulnerabilityType.PRIVILEGE_ESCALATION,
            'B702': VulnerabilityType.AUTHENTICATION_BYPASS,
            'B703': VulnerabilityType.AUTHENTICATION_BYPASS,
        }
        return mapping.get(bandit_test_id, VulnerabilityType.DATA_EXPOSURE)
    
    def _map_bandit_severity(self, bandit_severity: str) -> SeverityLevel:
        """Map Bandit severity to our severity levels"""
        mapping = {
            'HIGH': SeverityLevel.HIGH,
            'MEDIUM': SeverityLevel.MEDIUM,
            'LOW': SeverityLevel.LOW,
        }
        return mapping.get(bandit_severity, SeverityLevel.MEDIUM)

# Initialize global security audit manager
security_audit_manager = SecurityAuditManager()

async def main():
    """Main security audit function"""
    await security_audit_manager.initialize()
    
    # Example usage
    request_data = {
        'ip': '192.168.1.1',
        'username': 'test_user',
        'password': 'weak123',
        'search_query': "SELECT * FROM users WHERE id = '1' OR '1'='1"
    }
    
    vulnerabilities = await security_audit_manager.analyze_request(request_data)
    
    print(f"Detected {len(vulnerabilities)} vulnerabilities:")
    for vuln in vulnerabilities:
        print(f"- {vuln.type.value}: {vuln.description} (Severity: {vuln.severity.name})")
    
    # Generate security report
    report = await security_audit_manager.generate_security_report()
    print(f"\nSecurity Score: {report['security_score']}/100")
    print(f"Total Vulnerabilities: {report['total_vulnerabilities']}")
    
    return report

if __name__ == "__main__":
    asyncio.run(main())