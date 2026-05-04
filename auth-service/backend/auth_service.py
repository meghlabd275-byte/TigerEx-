#!/usr/bin/env python3
"""
TigerEx Authentication Service with Social Login Support
"""
import os
import json
import hashlib
import logging
import uuid
import time
import random
import string
import threading
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Country codes
COUNTRIES = {
    "+1": {"name": "United States", "flag": "🇺🇸"},
    "+1": {"name": "Canada", "flag": "🇨🇦"},
    "+44": {"name": "United Kingdom", "flag": "🇬🇧"},
    "+49": {"name": "Germany", "flag": "🇩🇪"},
    "+33": {"name": "France", "flag": "🇫🇷"},
    "+81": {"name": "Japan", "flag": "🇯🇵"},
    "+82": {"name": "South Korea", "flag": "🇰🇷"},
    "+86": {"name": "China", "flag": "🇨🇳"},
    "+91": {"name": "India", "flag": "🇮🇳"},
    "+55": {"name": "Brazil", "flag": "🇧🇷"},
    "+7": {"name": "Russia", "flag": "🇷🇺"},
    "+20": {"name": "Egypt", "flag": "🇪🇬"},
    "+966": {"name": "Saudi Arabia", "flag": "🇸🇦"},
    "+971": {"name": "UAE", "flag": "🇦🇪"},
    "+92": {"name": "Pakistan", "flag": "🇵🇰"},
    "+880": {"name": "Bangladesh", "flag": "🇧🇩"},
    "+65": {"name": "Singapore", "flag": "🇸🇬"},
    "+60": {"name": "Malaysia", "flag": "🇲🇾"},
    "+62": {"name": "Indonesia", "flag": "🇮🇩"},
    "+84": {"name": "Vietnam", "flag": "🇻🇳"},
    "+63": {"name": "Philippines", "flag": "🇵🇭"},
    "+94": {"name": "Sri Lanka", "flag": "🇱🇰"},
    "+977": {"name": "Nepal", "flag": "🇳🇵"},
    "+254": {"name": "Kenya", "flag": "🇰🇪"},
    "+27": {"name": "South Africa", "flag": "🇿🇦"},
    "+234": {"name": "Nigeria", "flag": "🇳🇬"},
    "+61": {"name": "Australia", "flag": "🇦🇺"},
    "+64": {"name": "New Zealand", "flag": "🇳🇿"},
}

# Social Login Providers
SOCIAL_PROVIDERS = ["google", "facebook", "twitter", "apple", "github", "linkedin", "discord", "telegram"]

class User:
    user_id: str
    email: str
    phone: str = ""
    password_hash: str = ""
    salt: str = ""
    username: str = ""
    created_at: datetime = None
    last_login: datetime = None
    status: str = "active"
    email_verified: bool = False
    phone_verified: bool = False
    twofa_enabled: bool = False
    twofa_secret: str = ""
    kyc_status: str = "none"
    kyc_level: int = 0
    login_expiry: datetime = None
    oauth_provider: str = ""
    oauth_id: str = ""
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.last_login is None:
            self.last_login = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "phone": self.phone,
            "username": self.username,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat(),
            "status": self.status,
            "email_verified": self.email_verified,
            "phone_verified": self.phone_verified,
            "twofa_enabled": self.twofa_enabled,
            "kyc_status": self.kyc_status,
            "kyc_level": self.kyc_level,
            "oauth_provider": self.oauth_provider,
        }

class VerificationCode:
    code_id: str
    user_id: str
    code_type: str
    code: str
    expires_at: datetime
    attempts: int = 0

class Session:
    session_id: str
    user_id: str
    created_at: datetime
    expires_at: datetime

class AuthService:
    def __init__(self):
        self.users = {}
        self.email_index = {}
        self.phone_index = {}
        self.oauth_index = {}  # provider+oauth_id -> user_id
        self.sessions = {}
        self.verification_codes = {}
        self.twofa_secrets = {}
        self.pending_bindings = {}  # user_id -> {email, phone, provider}
        
        logger.info("Auth Service initialized")
    
    def _generate_salt(self) -> str:
        return hashlib.sha256(str(time.time()).encode()).hexdigest()[:32]
    
    def _hash_password(self, password: str, salt: str) -> str:
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    def _verify_password(self, password: str, salt: str, password_hash: str) -> bool:
        return self._hash_password(password, salt) == password_hash
    
    # === REGISTRATION ===
    
    def register(self, email: str, phone: str, password: str, username: str = "") -> Dict:
        if email in self.email_index:
            return {"error": "Email already registered", "redirect": "login"}
        
        if phone and phone in self.phone_index:
            return {"error": "Phone already registered", "redirect": "login"}
        
        user_id = f"user_{uuid.uuid4().hex[:16]}"
        salt = self._generate_salt()
        password_hash = self._hash_password(password, salt)
        
        user = User(
            user_id=user_id,
            email=email,
            phone=phone,
            password_hash=password_hash,
            salt=salt,
            username=username or email.split("@")[0],
            created_at=datetime.utcnow(),
            last_login=datetime.utcnow(),
            status="pending",
            email_verified=False,
            phone_verified=False
        )
        
        self.users[user_id] = user
        self.email_index[email] = user_id
        if phone:
            self.phone_index[phone] = user_id
        
        # Send verification codes
        self._send_email_verification(user_id, email)
        if phone:
            self._send_phone_verification(user_id, phone)
        
        return {
            "status": "registered",
            "user_id": user_id,
            "message": "Registration successful. Please verify email and phone.",
            "next_steps": ["verify_email", "verify_phone"]
        }
    
    # === SOCIAL LOGIN ===
    
    def social_login(self, provider: str, oauth_token: str, user_info: Dict) -> Dict:
        """Handle social media login/register"""
        if provider not in SOCIAL_PROVIDERS:
            return {"error": "Invalid provider"}
        
        oauth_id = f"{provider}:{oauth_token}"
        
        # Check if user exists via OAuth
        if oauth_id in self.oauth_index:
            user_id = self.oauth_index[oauth_id]
            user = self.users.get(user_id)
            if user:
                session = self._create_session(user_id)
                return {
                    "status": "logged_in",
                    "session_id": session.session_id,
                    "user_id": user_id,
                    "redirect": "dashboard",
                    "requires_binding": False
                }
        
        # Check if email already registered
        email = user_info.get("email", "")
        if email and email in self.email_index:
            # Link OAuth to existing account
            user_id = self.email_index[email]
            user = self.users[user_id]
            user.oauth_provider = provider
            user.oauth_id = oauth_id
            self.oauth_index[oauth_id] = user_id
            
            session = self._create_session(user_id)
            return {
                "status": "logged_in",
                "session_id": session.session_id,
                "user_id": user_id,
                "redirect": "dashboard",
                "message": "Social account linked to existing account"
            }
        
        # Create new user from social login
        user_id = f"user_{uuid.uuid4().hex[:16]}"
        
        user = User(
            user_id=user_id,
            email=email or f"{provider}_{oauth_token[:16]}@social.tigerex.com",
            phone="",
            username=user_info.get("name", user_info.get("username", f"user_{uuid.uuid4().hex[:8]}")),
            created_at=datetime.utcnow(),
            last_login=datetime.utcnow(),
            status="pending",
            email_verified=user_info.get("email_verified", False),
            phone_verified=False,
            oauth_provider=provider,
            oauth_id=oauth_id
        )
        
        self.users[user_id] = user
        self.email_index[user.email] = user_id
        self.oauth_index[oauth_id] = user_id
        
        # Check if email verified by OAuth provider
        if not user.email_verified:
            self._send_email_verification(user_id, user.email)
        
        session = self._create_session(user_id)
        
        # If no email, need to bind
        if not email:
            return {
                "status": "logged_in",
                "session_id": session.session_id,
                "user_id": user_id,
                "redirect": "bind_email",
                "requires_binding": True,
                "bind_type": "email",
                "message": "Please bind your email"
            }
        
        return {
            "status": "logged_in",
            "session_id": session.session_id,
            "user_id": user_id,
            "redirect": "dashboard",
            "requires_binding": False
        }
    
    # === BIND EMAIL/PHONE AFTER SOCIAL LOGIN ===
    
    def bind_email(self, user_id: str, email: str) -> Dict:
        """Bind email to social account"""
        user = self.users.get(user_id)
        if not user:
            return {"error": "User not found"}
        
        if email in self.email_index:
            return {"error": "Email already in use", "redirect": "login"}
        
        # Send verification code
        code = self._send_email_verification(user_id, email)
        
        self.pending_bindings[user_id] = {
            "type": "email",
            "value": email,
            "code": code
        }
        
        return {
            "status": "pending_verification",
            "bind_type": "email",
            "message": "Verification code sent to email"
        }
    
    def bind_phone(self, user_id: str, phone: str) -> Dict:
        """Bind phone to social account"""
        user = self.users.get(user_id)
        if not user:
            return {"error": "User not found"}
        
        if phone in self.phone_index:
            return {"error": "Phone already in use", "redirect": "login"}
        
        # Send verification code
        code = self._send_phone_verification(user_id, phone)
        
        self.pending_bindings[user_id] = {
            "type": "phone",
            "value": phone,
            "code": code
        }
        
        return {
            "status": "pending_verification",
            "bind_type": "phone",
            "message": "Verification code sent to phone"
        }
    
    def confirm_binding(self, user_id: str, code: str) -> Dict:
        """Confirm email/phone binding"""
        pending = self.pending_bindings.get(user_id)
        if not pending:
            return {"error": "No pending binding"}
        
        if pending.get("code") != code:
            return {"error": "Invalid code"}
        
        user = self.users.get(user_id)
        if not user:
            return {"error": "User not found"}
        
        if pending["type"] == "email":
            user.email = pending["value"]
            user.email_verified = True
            self.email_index[pending["value"]] = user_id
        elif pending["type"] == "phone":
            user.phone = pending["value"]
            user.phone_verified = True
            self.phone_index[pending["value"]] = user_id
        
        del self.pending_bindings[user_id]
        
        return {
            "status": "bound",
            "bind_type": pending["type"],
            "message": f"{pending['type'].capitalize()} bound successfully"
        }
    
    # === LOGIN ===
    
    def login(self, identifier: str, password: str, stay_logged_in: bool = False) -> Dict:
        user = self._find_user(identifier)
        if not user:
            return {"error": "Invalid credentials"}
        
        if not user.password_hash:
            return {"error": "Please use social login or reset password"}
        
        if not self._verify_password(password, user.salt, user.password_hash):
            return {"error": "Invalid credentials"}
        
        if user.twofa_enabled:
            self._send_2fa_code(user.user_id)
            return {
                "require_2fa": True,
                "user_id": user.user_id,
                "message": "Enter 2FA code"
            }
        
        session = self._create_session(user.user_id, stay_logged_in)
        return {
            "status": "logged_in",
            "session_id": session.session_id,
            "user_id": user.user_id,
            "redirect": "dashboard"
        }
    
    def verify_2fa(self, user_id: str, code: str, stay_logged_in: bool = False) -> Dict:
        user = self.users.get(user_id)
        if not user:
            return {"error": "User not found"}
        
        secret = self.twofa_secrets.get(user_id)
        if not self._verify_2fa_code(code, secret):
            return {"error": "Invalid 2FA code"}
        
        session = self._create_session(user_id, stay_logged_in)
        return {
            "status": "logged_in",
            "session_id": session.session_id,
            "user_id": user_id,
            "redirect": "dashboard"
        }
    
    def logout(self, session_id: str) -> Dict:
        if session_id in self.sessions:
            del self.sessions[session_id]
        return {"status": "logged_out"}
    
    def verify_session(self, session_id: str) -> Dict:
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if datetime.utcnow() < session.expires_at:
                return {"valid": True, "user_id": session.user_id}
        return {"valid": False}
    
    # === HELPERS ===
    
    def _create_session(self, user_id: str, stay_logged_in: bool = False) -> Session:
        session_id = f"sess_{uuid.uuid4().hex[:32]}"
        days = 30 if stay_logged_in else 1
        session = Session(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=days)
        )
        self.sessions[session_id] = session
        return session
    
    def _find_user(self, identifier: str):
        if identifier in self.email_index:
            return self.users.get(self.email_index[identifier])
        if identifier in self.phone_index:
            return self.users.get(self.phone_index[identifier])
        return None
    
    def _send_email_verification(self, user_id: str, email: str) -> str:
        code = str(random.randint(100000, 999999))
        self.verification_codes[f"email_{user_id}"] = VerificationCode(
            code_id=f"email_{user_id}",
            user_id=user_id,
            code_type="email",
            code=code,
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        logger.info(f"Email verification for {email}: {code}")
        return code
    
    def _send_phone_verification(self, user_id: str, phone: str) -> str:
        code = str(random.randint(100000, 999999))
        self.verification_codes[f"phone_{user_id}"] = VerificationCode(
            code_id=f"phone_{user_id}",
            user_id=user_id,
            code_type="phone",
            code=code,
            expires_at=datetime.utcnow() + timedelta(minutes=5)
        )
        logger.info(f"Phone verification for {phone}: {code}")
        return code
    
    def _send_2fa_code(self, user_id: str) -> str:
        code = str(random.randint(100000, 999999))
        self.verification_codes[f"2fa_{user_id}"] = VerificationCode(
            code_id=f"2fa_{user_id}",
            user_id=user_id,
            code_type="2fa",
            code=code,
            expires_at=datetime.utcnow() + timedelta(minutes=1)
        )
        logger.info(f"2FA code for user {user_id}: {code}")
        return code
    
    def _verify_2fa_code(self, code: str, secret: str) -> bool:
        return len(code) == 6 and code.isdigit()
    
    def verify_code(self, user_id: str, code_type: str, code: str) -> Dict:
        key = f"{code_type}_{user_id}"
        veri = self.verification_codes.get(key)
        
        if not veri or datetime.utcnow() > veri.expires_at:
            return {"error": "Code expired"}
        
        if veri.code != code:
            return {"error": "Invalid code"}
        
        user = self.users.get(user_id)
        if not user:
            return {"error": "User not found"}
        
        if code_type == "email":
            user.email_verified = True
        elif code_type == "phone":
            user.phone_verified = True
        
        del self.verification_codes[key]
        
        return {"status": "verified", "type": code_type}
    
    def get_user(self, user_id: str) -> Dict:
        user = self.users.get(user_id)
        if user:
            return user.to_dict()
        return {"error": "User not found"}
    
    def get_countries(self) -> Dict:
        return COUNTRIES
    
    def get_providers(self) -> List[Dict]:
        return [
            {"id": "google", "name": "Google", "icon": "fab fa-google"},
            {"id": "facebook", "name": "Facebook", "icon": "fab fa-facebook"},
            {"id": "twitter", "name": "Twitter/X", "icon": "fab fa-twitter"},
            {"id": "apple", "name": "Apple", "icon": "fab fa-apple"},
            {"id": "github", "name": "GitHub", "icon": "fab fa-github"},
            {"id": "linkedin", "name": "LinkedIn", "icon": "fab fa-linkedin"},
            {"id": "discord", "name": "Discord", "icon": "fab fa-discord"},
            {"id": "telegram", "name": "Telegram", "icon": "fab fa-telegram"},
        ]


# Flask API
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
auth_service = AuthService()

@app.route('/auth/health')
def health():
    return jsonify({"status": "ok", "service": "auth"})

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    return jsonify(auth_service.register(
        data.get('email', ''),
        data.get('phone', ''),
        data.get('password', ''),
        data.get('username', '')
    ))

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    return jsonify(auth_service.login(
        data.get('identifier', ''),
        data.get('password', ''),
        data.get('stay_logged_in', False)
    ))

@app.route('/auth/social-login', methods=['POST'])
def social_login():
    data = request.get_json() or {}
    return jsonify(auth_service.social_login(
        data.get('provider', ''),
        data.get('oauth_token', ''),
        data.get('user_info', {})
    ))

@app.route('/auth/bind-email', methods=['POST'])
def bind_email():
    data = request.get_json() or {}
    return jsonify(auth_service.bind_email(
        data.get('user_id', ''),
        data.get('email', '')
    ))

@app.route('/auth/bind-phone', methods=['POST'])
def bind_phone():
    data = request.get_json() or {}
    return jsonify(auth_service.bind_phone(
        data.get('user_id', ''),
        data.get('phone', '')
    ))

@app.route('/auth/confirm-binding', methods=['POST'])
def confirm_binding():
    data = request.get_json() or {}
    return jsonify(auth_service.confirm_binding(
        data.get('user_id', ''),
        data.get('code', '')
    ))

@app.route('/auth/verify-2fa', methods=['POST'])
def verify_2fa():
    data = request.get_json() or {}
    return jsonify(auth_service.verify_2fa(
        data.get('user_id', ''),
        data.get('code', ''),
        data.get('stay_logged_in', False)
    ))

@app.route('/auth/verify-code', methods=['POST'])
def verify_code():
    data = request.get_json() or {}
    return jsonify(auth_service.verify_code(
        data.get('user_id', ''),
        data.get('type', ''),
        data.get('code', '')
    ))

@app.route('/auth/logout', methods=['POST'])
def logout():
    data = request.get_json() or {}
    return jsonify(auth_service.logout(data.get('session_id', '')))

@app.route('/auth/verify-session', methods=['POST'])
def verify_session():
    data = request.get_json() or {}
    return jsonify(auth_service.verify_session(data.get('session_id', '')))

@app.route('/auth/user/<user_id>')
def get_user(user_id):
    return jsonify(auth_service.get_user(user_id))

@app.route('/auth/countries')
def countries():
    return jsonify(auth_service.get_countries())

@app.route('/auth/providers')
def providers():
    return jsonify(auth_service.get_providers())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6600))
    logger.info(f"Starting Auth Service on port {port}")
    app.run(host='0.0.0.0', port=port, threaded=True)