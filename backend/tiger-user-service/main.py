#!/usr/bin/env python3
"""
Tiger User Service - Unified User Management & Authentication
Consolidates functionality from 15+ user services
Features complete user lifecycle management with security
"""

from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, jwt_required, get_jwt_identity,
    create_access_token, create_refresh_token
)
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import logging
import os
import uuid
import json
import re
from decimal import Decimal
from functools import wraps
from enum import Enum
import secrets

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/tigerex')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KYCStatus(Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"

class UserTier(Enum):
    BASIC = "basic"
    VERIFIED = "verified"
    ADVANCED = "advanced"
    PREMIUM = "premium"
    INSTITUTIONAL = "institutional"

class TwoFactorType(Enum):
    NONE = "none"
    SMS = "sms"
    EMAIL = "email"
    AUTHENTICATOR = "authenticator"

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile Information
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    country = db.Column(db.String(100))
    nationality = db.Column(db.String(100))
    
    # Verification & KYC
    kyc_status = db.Column(db.Enum(KYCStatus), default=KYCStatus.PENDING)
    kyc_documents = db.Column(db.JSON)
    kyc_submitted_at = db.Column(db.DateTime)
    kyc_approved_at = db.Column(db.DateTime)
    user_tier = db.Column(db.Enum(UserTier), default=UserTier.BASIC)
    
    # Security
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_type = db.Column(db.Enum(TwoFactorType), default=TwoFactorType.NONE)
    two_factor_secret = db.Column(db.String(100))
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    
    # Session & Preferences
    last_login = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(50))
    login_count = db.Column(db.Integer, default=0)
    preferences = db.Column(db.JSON, default=dict)
    
    # Trading & Financial
    trading_enabled = db.Column(db.Boolean, default=False)
    withdrawal_enabled = db.Column(db.Boolean, default=False)
    daily_withdrawal_limit = db.Column(db.Numeric(20, 8), default=Decimal('10000'))
    monthly_withdrawal_limit = db.Column(db.Numeric(20, 8), default=Decimal('100000'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    refresh_token = db.Column(db.String(255), unique=True, nullable=False)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    device_info = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)

class KYCDocument(db.Model):
    __tablename__ = 'kyc_documents'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # 'passport', 'id_card', 'driver_license', 'proof_of_address'
    document_number = db.Column(db.String(100))
    document_front_url = db.Column(db.String(500))
    document_back_url = db.Column(db.String(500))
    selfie_url = db.Column(db.String(500))
    verification_status = db.Column(db.String(20), default='pending')
    rejection_reason = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer)

class UserActivity(db.Model):
    __tablename__ = 'user_activities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    activity_details = db.Column(db.JSON)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SecurityEvent(db.Model):
    __tablename__ = 'security_events'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_type = db.Column(db.String(50), nullable=False)  # 'login_attempt', 'password_change', '2fa_enable', 'account_locked'
    event_details = db.Column(db.JSON)
    ip_address = db.Column(db.String(50))
    severity = db.Column(db.String(20), default='medium')  # 'low', 'medium', 'high', 'critical'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Validation functions
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    if len(password)