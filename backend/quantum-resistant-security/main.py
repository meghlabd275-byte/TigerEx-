#!/usr/bin/env python3
"""
Quantum-Resistant Security Service
Advanced quantum-resistant cryptography and security implementation
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
import uuid
import logging
import os
import asyncio
import aioredis
import json
from decimal import Decimal
import numpy as np
import hashlib
import hmac
import secrets
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64

# FastAPI app
app = FastAPI(
    title="TigerEx Quantum-Resistant Security",
    description="Advanced quantum-resistant cryptography and security implementation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/tigerex_quantum_security")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Quantum-resistant algorithms configuration
QUANTUM_ALGORITHMS = {
    "lattice_based": {
        "kyber": {"key_size": 1568, "security_level": 128},
        "dilithium": {"signature_size": 2420, "security_level": 128},
        "falcon": {"signature_size": 690, "security_level": 128}
    },
    "hash_based": {
        "sphincs": {"signature_size": 17088, "security_level": 128},
        "xmss": {"signature_size": 2500, "security_level": 128}
    },
    "code_based": {
        "mceliece": {"key_size": 261120, "security_level": 128},
        "bike": {"key_size": 5122, "security_level": 128}
    },
    "multivariate": {
        "rainbow": {"signature_size": 66, "security_level": 128},
        "gemss": {"signature_size": 33, "security_level": 128}
    }
}

# Database Models
class QuantumKeyPair(Base):
    __tablename__ = "quantum_key_pairs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Key identification
    key_id = Column(String, unique=True, nullable=False)
    user_id = Column(String, nullable=False)
    key_type = Column(String, nullable=False)  # encryption, signing, authentication
    
    # Algorithm details
    algorithm = Column(String, nullable=False)  # kyber, dilithium, falcon, etc.
    security_level = Column(Integer, default=128)
    
    # Key data (encrypted)
    public_key = Column(Text, nullable=False)
    private_key_encrypted = Column(Text, nullable=False)
    key_derivation_salt = Column(String, nullable=False)
    
    # Key metadata
    key_size = Column(Integer, nullable=False)
    generation_method = Column(String, default="secure_random")
    
    # Key lifecycle
    status = Column(String, default="active")  # active, revoked, expired, compromised
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    revoked_at = Column(DateTime)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime)

class QuantumSignature(Base):
    __tablename__ = "quantum_signatures"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Signature details
    key_id = Column(String, nullable=False)
    message_hash = Column(String, nullable=False)
    signature_data = Column(Text, nullable=False)
    algorithm = Column(String, nullable=False)
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verification_timestamp = Column(DateTime)
    
    # Context
    transaction_id = Column(String)
    operation_type = Column(String)  # login, trade, withdrawal, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)

class QuantumEncryption(Base):
    __tablename__ = "quantum_encryption"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Encryption details
    key_id = Column(String, nullable=False)
    encrypted_data = Column(Text, nullable=False)
    algorithm = Column(String, nullable=False)
    
    # Encryption metadata
    data_type = Column(String, nullable=False)  # wallet_key, user_data, transaction
    encryption_iv = Column(String, nullable=False)
    
    # Access control
    authorized_users = Column(JSON, default=list)
    access_level = Column(String, default="private")  # public, private, restricted
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

class SecurityAudit(Base):
    __tablename__ = "security_audits"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Audit details
    audit_type = Column(String, nullable=False)  # key_rotation, signature_verification, encryption_check
    target_id = Column(String, nullable=False)  # ID of audited object
    
    # Results
    status = Column(String, nullable=False)  # passed, failed, warning
    findings = Column(JSON)
    recommendations = Column(JSON)
    
    # Risk assessment
    risk_level = Column(String, default="low")  # low, medium, high, critical
    
    # Remediation
    remediation_required = Column(Boolean, default=False)
    remediation_deadline = Column(DateTime)
    remediation_status = Column(String, default="not_required")
    
    created_at = Column(DateTime, default=datetime.utcnow)

class QuantumThreatAssessment(Base):
    __tablename__ = "quantum_threat_assessments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Threat assessment
    threat_level = Column(String, default="low")  # low, medium, high, critical
    quantum_readiness_score = Column(Float, default=0.0)  # 0-100
    
    # Algorithm assessment
    vulnerable_algorithms = Column(JSON, default=list)
    secure_algorithms = Column(JSON, default=list)
    migration_priority = Column(JSON, default=dict)
    
    # Timeline
    estimated_quantum_threat_date = Column(DateTime)
    migration_deadline = Column(DateTime)
    
    # Recommendations
    immediate_actions = Column(JSON, default=list)
    long_term_strategy = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class KeyPairRequest(BaseModel):
    user_id: str
    key_type: str
    algorithm: str
    security_level: int = 128
    expires_in_days: Optional[int] = 365

class SignatureRequest(BaseModel):
    key_id: str
    message: str
    operation_type: str
    transaction_id: Optional[str] = None

class EncryptionRequest(BaseModel):
    key_id: str
    data: str
    data_type: str
    authorized_users: Optional[List[str]] = None
    expires_in_days: Optional[int] = None

class DecryptionRequest(BaseModel):
    encryption_id: str
    requesting_user_id: str

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions
async def get_redis():
    return await aioredis.from_url(REDIS_URL)

class QuantumCrypto:
    """Quantum-resistant cryptographic operations"""
    
    @staticmethod
    def generate_kyber_keypair() -> Dict[str, str]:
        """Generate Kyber key pair (mock implementation)"""
        # In production, use actual Kyber implementation
        private_key = secrets.token_bytes(1568)
        public_key = hashlib.sha256(private_key).digest()
        
        return {
            "private_key": base64.b64encode(private_key).decode(),
            "public_key": base64.b64encode(public_key).decode()
        }
    
    @staticmethod
    def generate_dilithium_keypair() -> Dict[str, str]:
        """Generate Dilithium key pair (mock implementation)"""
        private_key = secrets.token_bytes(2420)
        public_key = hashlib.sha256(private_key).digest()
        
        return {
            "private_key": base64.b64encode(private_key).decode(),
            "public_key": base64.b64encode(public_key).decode()
        }
    
    @staticmethod
    def generate_falcon_keypair() -> Dict[str, str]:
        """Generate Falcon key pair (mock implementation)"""
        private_key = secrets.token_bytes(690)
        public_key = hashlib.sha256(private_key).digest()
        
        return {
            "private_key": base64.b64encode(private_key).decode(),
            "public_key": base64.b64encode(public_key).decode()
        }
    
    @staticmethod
    def sign_dilithium(message: str, private_key: str) -> str:
        """Sign message with Dilithium (mock implementation)"""
        # In production, use actual Dilithium signing
        message_bytes = message.encode('utf-8')
        key_bytes = base64.b64decode(private_key)
        
        signature = hmac.new(key_bytes, message_bytes, hashlib.sha256).digest()
        return base64.b64encode(signature).decode()
    
    @staticmethod
    def verify_dilithium(message: str, signature: str, public_key: str) -> bool:
        """Verify Dilithium signature (mock implementation)"""
        try:
            # Mock verification
            return len(signature) > 0 and len(public_key) > 0
        except:
            return False
    
    @staticmethod
    def encrypt_kyber(data: str, public_key: str) -> Dict[str, str]:
        """Encrypt data with Kyber (mock implementation)"""
        # Generate symmetric key
        symmetric_key = secrets.token_bytes(32)
        
        # Encrypt data with AES
        iv = secrets.token_bytes(16)
        cipher = Cipher(algorithms.AES(symmetric_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # Pad data
        data_bytes = data.encode('utf-8')
        padding_length = 16 - (len(data_bytes) % 16)
        padded_data = data_bytes + bytes([padding_length] * padding_length)
        
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        # Mock Kyber encapsulation of symmetric key
        encapsulated_key = hashlib.sha256(symmetric_key + base64.b64decode(public_key)).digest()
        
        return {
            "encrypted_data": base64.b64encode(encrypted_data).decode(),
            "encapsulated_key": base64.b64encode(encapsulated_key).decode(),
            "iv": base64.b64encode(iv).decode()
        }
    
    @staticmethod
    def decrypt_kyber(encrypted_data: str, encapsulated_key: str, iv: str, private_key: str) -> str:
        """Decrypt data with Kyber (mock implementation)"""
        try:
            # Mock Kyber decapsulation
            key_bytes = base64.b64decode(private_key)
            symmetric_key = hashlib.sha256(key_bytes).digest()[:32]
            
            # Decrypt with AES
            cipher = Cipher(algorithms.AES(symmetric_key), modes.CBC(base64.b64decode(iv)), backend=default_backend())
            decryptor = cipher.decryptor()
            
            decrypted_padded = decryptor.update(base64.b64decode(encrypted_data)) + decryptor.finalize()
            
            # Remove padding
            padding_length = decrypted_padded[-1]
            decrypted_data = decrypted_padded[:-padding_length]
            
            return decrypted_data.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return ""

def encrypt_private_key(private_key: str, password: str) -> Dict[str, str]:
    """Encrypt private key with password"""
    salt = secrets.token_bytes(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    
    iv = secrets.token_bytes(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    # Pad private key
    key_bytes = private_key.encode('utf-8')
    padding_length = 16 - (len(key_bytes) % 16)
    padded_key = key_bytes + bytes([padding_length] * padding_length)
    
    encrypted_key = encryptor.update(padded_key) + encryptor.finalize()
    
    return {
        "encrypted_key": base64.b64encode(encrypted_key).decode(),
        "salt": base64.b64encode(salt).decode(),
        "iv": base64.b64encode(iv).decode()
    }

def decrypt_private_key(encrypted_data: Dict[str, str], password: str) -> str:
    """Decrypt private key with password"""
    try:
        salt = base64.b64decode(encrypted_data["salt"])
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        
        iv = base64.b64decode(encrypted_data["iv"])
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        decrypted_padded = decryptor.update(base64.b64decode(encrypted_data["encrypted_key"])) + decryptor.finalize()
        
        # Remove padding
        padding_length = decrypted_padded[-1]
        decrypted_key = decrypted_padded[:-padding_length]
        
        return decrypted_key.decode('utf-8')
    except Exception as e:
        logger.error(f"Private key decryption error: {e}")
        return ""

def assess_quantum_threat() -> Dict[str, Any]:
    """Assess current quantum threat level"""
    # Mock quantum threat assessment
    # In production, this would analyze current quantum computing capabilities
    
    current_year = datetime.now().year
    estimated_quantum_threat_year = 2030  # Conservative estimate
    
    years_until_threat = estimated_quantum_threat_year - current_year
    threat_probability = max(0, min(1, (10 - years_until_threat) / 10))
    
    if years_until_threat <= 2:
        threat_level = "critical"
    elif years_until_threat <= 5:
        threat_level = "high"
    elif years_until_threat <= 10:
        threat_level = "medium"
    else:
        threat_level = "low"
    
    return {
        "threat_level": threat_level,
        "threat_probability": threat_probability,
        "years_until_threat": years_until_threat,
        "estimated_threat_date": f"{estimated_quantum_threat_year}-01-01",
        "quantum_readiness_required": threat_level in ["high", "critical"]
    }

def calculate_migration_priority(algorithm: str, usage_frequency: int, data_sensitivity: str) -> int:
    """Calculate migration priority for cryptographic systems"""
    # Base priority based on algorithm vulnerability
    vulnerable_algorithms = ["rsa", "ecc", "dh", "ecdsa"]
    base_priority = 10 if algorithm.lower() in vulnerable_algorithms else 1
    
    # Adjust for usage frequency
    usage_multiplier = min(usage_frequency / 1000, 3.0)
    
    # Adjust for data sensitivity
    sensitivity_multiplier = {
        "low": 1.0,
        "medium": 1.5,
        "high": 2.0,
        "critical": 3.0
    }.get(data_sensitivity, 1.0)
    
    priority = int(base_priority * usage_multiplier * sensitivity_multiplier)
    return min(priority, 100)  # Cap at 100

# API Routes

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "quantum-resistant-security"}

@app.get("/algorithms")
async def get_supported_algorithms():
    """Get supported quantum-resistant algorithms"""
    return QUANTUM_ALGORITHMS

@app.get("/threat-assessment")
async def get_threat_assessment(db: Session = Depends(get_db)):
    """Get current quantum threat assessment"""
    threat_data = assess_quantum_threat()
    
    # Save assessment
    assessment = QuantumThreatAssessment(
        threat_level=threat_data["threat_level"],
        quantum_readiness_score=85.0,  # Mock score
        vulnerable_algorithms=["rsa-2048", "ecc-256", "dh-2048"],
        secure_algorithms=["kyber-768", "dilithium-3", "falcon-512"],
        migration_priority={
            "wallet_keys": 95,
            "api_keys": 80,
            "session_tokens": 60,
            "user_data": 70
        },
        estimated_quantum_threat_date=datetime(2030, 1, 1),
        migration_deadline=datetime(2028, 1, 1),
        immediate_actions=[
            "Implement hybrid classical-quantum cryptography",
            "Begin key rotation to quantum-resistant algorithms",
            "Update security policies and procedures"
        ],
        long_term_strategy=[
            "Complete migration to post-quantum cryptography",
            "Implement quantum key distribution",
            "Deploy quantum-safe protocols"
        ]
    )
    
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    return assessment

# Key management
@app.post("/keys/generate")
async def generate_quantum_keypair(
    request: KeyPairRequest,
    password: str,
    db: Session = Depends(get_db)
):
    """Generate quantum-resistant key pair"""
    try:
        # Generate key pair based on algorithm
        if request.algorithm == "kyber":
            keypair = QuantumCrypto.generate_kyber_keypair()
        elif request.algorithm == "dilithium":
            keypair = QuantumCrypto.generate_dilithium_keypair()
        elif request.algorithm == "falcon":
            keypair = QuantumCrypto.generate_falcon_keypair()
        else:
            raise HTTPException(status_code=400, detail="Unsupported algorithm")
        
        # Encrypt private key
        encrypted_private_key = encrypt_private_key(keypair["private_key"], password)
        
        # Generate unique key ID
        key_id = f"qr_{request.algorithm}_{uuid.uuid4().hex[:8]}"
        
        # Save key pair
        db_keypair = QuantumKeyPair(
            key_id=key_id,
            user_id=request.user_id,
            key_type=request.key_type,
            algorithm=request.algorithm,
            security_level=request.security_level,
            public_key=keypair["public_key"],
            private_key_encrypted=json.dumps(encrypted_private_key),
            key_derivation_salt=encrypted_private_key["salt"],
            key_size=QUANTUM_ALGORITHMS.get(request.algorithm.split('_')[0], {}).get(request.algorithm, {}).get("key_size", 0),
            expires_at=datetime.utcnow() + timedelta(days=request.expires_in_days) if request.expires_in_days else None
        )
        
        db.add(db_keypair)
        db.commit()
        db.refresh(db_keypair)
        
        return {
            "key_id": key_id,
            "public_key": keypair["public_key"],
            "algorithm": request.algorithm,
            "security_level": request.security_level,
            "expires_at": db_keypair.expires_at
        }
        
    except Exception as e:
        logger.error(f"Error generating key pair: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/keys/{user_id}")
async def get_user_keys(user_id: str, db: Session = Depends(get_db)):
    """Get user's quantum-resistant keys"""
    keys = db.query(QuantumKeyPair).filter(
        QuantumKeyPair.user_id == user_id,
        QuantumKeyPair.status == "active"
    ).all()
    
    # Return public information only
    return [
        {
            "key_id": key.key_id,
            "key_type": key.key_type,
            "algorithm": key.algorithm,
            "security_level": key.security_level,
            "public_key": key.public_key,
            "created_at": key.created_at,
            "expires_at": key.expires_at,
            "usage_count": key.usage_count,
            "last_used": key.last_used
        }
        for key in keys
    ]

@app.post("/keys/{key_id}/rotate")
async def rotate_key(
    key_id: str,
    new_password: str,
    db: Session = Depends(get_db)
):
    """Rotate quantum-resistant key"""
    # Get existing key
    old_key = db.query(QuantumKeyPair).filter(QuantumKeyPair.key_id == key_id).first()
    if not old_key:
        raise HTTPException(status_code=404, detail="Key not found")
    
    # Generate new key pair
    if old_key.algorithm == "kyber":
        new_keypair = QuantumCrypto.generate_kyber_keypair()
    elif old_key.algorithm == "dilithium":
        new_keypair = QuantumCrypto.generate_dilithium_keypair()
    elif old_key.algorithm == "falcon":
        new_keypair = QuantumCrypto.generate_falcon_keypair()
    else:
        raise HTTPException(status_code=400, detail="Unsupported algorithm")
    
    # Encrypt new private key
    encrypted_private_key = encrypt_private_key(new_keypair["private_key"], new_password)
    
    # Create new key record
    new_key_id = f"qr_{old_key.algorithm}_{uuid.uuid4().hex[:8]}"
    
    new_key = QuantumKeyPair(
        key_id=new_key_id,
        user_id=old_key.user_id,
        key_type=old_key.key_type,
        algorithm=old_key.algorithm,
        security_level=old_key.security_level,
        public_key=new_keypair["public_key"],
        private_key_encrypted=json.dumps(encrypted_private_key),
        key_derivation_salt=encrypted_private_key["salt"],
        key_size=old_key.key_size,
        expires_at=datetime.utcnow() + timedelta(days=365)
    )
    
    db.add(new_key)
    
    # Revoke old key
    old_key.status = "revoked"
    old_key.revoked_at = datetime.utcnow()
    
    db.commit()
    db.refresh(new_key)
    
    return {
        "old_key_id": key_id,
        "new_key_id": new_key_id,
        "rotated_at": datetime.utcnow(),
        "message": "Key rotated successfully"
    }

# Signing operations
@app.post("/sign")
async def create_quantum_signature(
    request: SignatureRequest,
    password: str,
    db: Session = Depends(get_db)
):
    """Create quantum-resistant signature"""
    try:
        # Get key
        key = db.query(QuantumKeyPair).filter(QuantumKeyPair.key_id == request.key_id).first()
        if not key:
            raise HTTPException(status_code=404, detail="Key not found")
        
        if key.status != "active":
            raise HTTPException(status_code=400, detail="Key not active")
        
        # Decrypt private key
        encrypted_key_data = json.loads(key.private_key_encrypted)
        private_key = decrypt_private_key(encrypted_key_data, password)
        
        if not private_key:
            raise HTTPException(status_code=400, detail="Invalid password")
        
        # Create signature
        message_hash = hashlib.sha256(request.message.encode()).hexdigest()
        
        if key.algorithm == "dilithium":
            signature_data = QuantumCrypto.sign_dilithium(request.message, private_key)
        else:
            # Default to HMAC for other algorithms (mock)
            signature_data = hmac.new(
                base64.b64decode(private_key),
                request.message.encode(),
                hashlib.sha256
            ).hexdigest()
        
        # Save signature
        db_signature = QuantumSignature(
            key_id=request.key_id,
            message_hash=message_hash,
            signature_data=signature_data,
            algorithm=key.algorithm,
            transaction_id=request.transaction_id,
            operation_type=request.operation_type
        )
        
        db.add(db_signature)
        
        # Update key usage
        key.usage_count += 1
        key.last_used = datetime.utcnow()
        
        db.commit()
        db.refresh(db_signature)
        
        return {
            "signature_id": db_signature.id,
            "signature": signature_data,
            "algorithm": key.algorithm,
            "message_hash": message_hash
        }
        
    except Exception as e:
        logger.error(f"Error creating signature: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify")
async def verify_quantum_signature(
    signature_id: str,
    message: str,
    db: Session = Depends(get_db)
):
    """Verify quantum-resistant signature"""
    try:
        # Get signature
        signature = db.query(QuantumSignature).filter(QuantumSignature.id == signature_id).first()
        if not signature:
            raise HTTPException(status_code=404, detail="Signature not found")
        
        # Get public key
        key = db.query(QuantumKeyPair).filter(QuantumKeyPair.key_id == signature.key_id).first()
        if not key:
            raise HTTPException(status_code=404, detail="Key not found")
        
        # Verify message hash
        message_hash = hashlib.sha256(message.encode()).hexdigest()
        if message_hash != signature.message_hash:
            return {"verified": False, "reason": "Message hash mismatch"}
        
        # Verify signature
        if key.algorithm == "dilithium":
            verified = QuantumCrypto.verify_dilithium(message, signature.signature_data, key.public_key)
        else:
            # Mock verification for other algorithms
            verified = len(signature.signature_data) > 0
        
        # Update verification status
        signature.is_verified = verified
        signature.verification_timestamp = datetime.utcnow()
        db.commit()
        
        return {
            "verified": verified,
            "algorithm": key.algorithm,
            "signature_id": signature_id,
            "verification_timestamp": signature.verification_timestamp
        }
        
    except Exception as e:
        logger.error(f"Error verifying signature: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Encryption operations
@app.post("/encrypt")
async def encrypt_data(
    request: EncryptionRequest,
    db: Session = Depends(get_db)
):
    """Encrypt data with quantum-resistant algorithm"""
    try:
        # Get key
        key = db.query(QuantumKeyPair).filter(QuantumKeyPair.key_id == request.key_id).first()
        if not key:
            raise HTTPException(status_code=404, detail="Key not found")
        
        if key.key_type != "encryption":
            raise HTTPException(status_code=400, detail="Key not suitable for encryption")
        
        # Encrypt data
        if key.algorithm == "kyber":
            encryption_result = QuantumCrypto.encrypt_kyber(request.data, key.public_key)
        else:
            # Fallback to AES encryption
            symmetric_key = secrets.token_bytes(32)
            iv = secrets.token_bytes(16)
            
            cipher = Cipher(algorithms.AES(symmetric_key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            
            data_bytes = request.data.encode('utf-8')
            padding_length = 16 - (len(data_bytes) % 16)
            padded_data = data_bytes + bytes([padding_length] * padding_length)
            
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            
            encryption_result = {
                "encrypted_data": base64.b64encode(encrypted_data).decode(),
                "iv": base64.b64encode(iv).decode()
            }
        
        # Save encryption record
        db_encryption = QuantumEncryption(
            key_id=request.key_id,
            encrypted_data=json.dumps(encryption_result),
            algorithm=key.algorithm,
            data_type=request.data_type,
            encryption_iv=encryption_result.get("iv", ""),
            authorized_users=request.authorized_users or [key.user_id],
            expires_at=datetime.utcnow() + timedelta(days=request.expires_in_days) if request.expires_in_days else None
        )
        
        db.add(db_encryption)
        
        # Update key usage
        key.usage_count += 1
        key.last_used = datetime.utcnow()
        
        db.commit()
        db.refresh(db_encryption)
        
        return {
            "encryption_id": db_encryption.id,
            "algorithm": key.algorithm,
            "encrypted_at": db_encryption.created_at
        }
        
    except Exception as e:
        logger.error(f"Error encrypting data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/decrypt")
async def decrypt_data(
    request: DecryptionRequest,
    password: str,
    db: Session = Depends(get_db)
):
    """Decrypt data with quantum-resistant algorithm"""
    try:
        # Get encryption record
        encryption = db.query(QuantumEncryption).filter(
            QuantumEncryption.id == request.encryption_id
        ).first()
        
        if not encryption:
            raise HTTPException(status_code=404, detail="Encryption record not found")
        
        # Check authorization
        if request.requesting_user_id not in encryption.authorized_users:
            raise HTTPException(status_code=403, detail="Not authorized to decrypt")
        
        # Check expiration
        if encryption.expires_at and datetime.utcnow() > encryption.expires_at:
            raise HTTPException(status_code=400, detail="Encrypted data expired")
        
        # Get key
        key = db.query(QuantumKeyPair).filter(QuantumKeyPair.key_id == encryption.key_id).first()
        if not key:
            raise HTTPException(status_code=404, detail="Key not found")
        
        # Decrypt private key
        encrypted_key_data = json.loads(key.private_key_encrypted)
        private_key = decrypt_private_key(encrypted_key_data, password)
        
        if not private_key:
            raise HTTPException(status_code=400, detail="Invalid password")
        
        # Decrypt data
        encryption_data = json.loads(encryption.encrypted_data)
        
        if key.algorithm == "kyber":
            decrypted_data = QuantumCrypto.decrypt_kyber(
                encryption_data["encrypted_data"],
                encryption_data["encapsulated_key"],
                encryption_data["iv"],
                private_key
            )
        else:
            # Fallback decryption
            decrypted_data = "Mock decrypted data"
        
        return {
            "decrypted_data": decrypted_data,
            "algorithm": key.algorithm,
            "decrypted_at": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error decrypting data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Security auditing
@app.post("/audit/keys")
async def audit_quantum_keys(db: Session = Depends(get_db)):
    """Audit quantum-resistant keys"""
    try:
        # Get all active keys
        keys = db.query(QuantumKeyPair).filter(QuantumKeyPair.status == "active").all()
        
        audit_results = []
        
        for key in keys:
            findings = []
            recommendations = []
            risk_level = "low"
            
            # Check key age
            key_age_days = (datetime.utcnow() - key.created_at).days
            if key_age_days > 365:
                findings.append("Key is older than 1 year")
                recommendations.append("Consider key rotation")
                risk_level = "medium"
            
            # Check usage frequency
            if key.usage_count > 10000:
                findings.append("High usage count detected")
                recommendations.append("Monitor for potential compromise")
            
            # Check algorithm strength
            if key.security_level < 128:
                findings.append("Security level below recommended minimum")
                recommendations.append("Upgrade to higher security level")
                risk_level = "high"
            
            # Check expiration
            if key.expires_at and key.expires_at < datetime.utcnow() + timedelta(days=30):
                findings.append("Key expires within 30 days")
                recommendations.append("Schedule key renewal")
                risk_level = "medium"
            
            # Create audit record
            audit = SecurityAudit(
                audit_type="key_rotation",
                target_id=key.key_id,
                status="passed" if not findings else "warning",
                findings=findings,
                recommendations=recommendations,
                risk_level=risk_level,
                remediation_required=len(findings) > 0,
                remediation_deadline=datetime.utcnow() + timedelta(days=30) if findings else None
            )
            
            db.add(audit)
            audit_results.append(audit)
        
        db.commit()
        
        return {
            "total_keys_audited": len(keys),
            "audit_results": audit_results,
            "high_risk_keys": len([a for a in audit_results if a.risk_level == "high"]),
            "recommendations_count": sum(len(a.recommendations) for a in audit_results)
        }
        
    except Exception as e:
        logger.error(f"Error auditing keys: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audit/reports")
async def get_audit_reports(
    audit_type: Optional[str] = None,
    risk_level: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get security audit reports"""
    query = db.query(SecurityAudit)
    
    if audit_type:
        query = query.filter(SecurityAudit.audit_type == audit_type)
    if risk_level:
        query = query.filter(SecurityAudit.risk_level == risk_level)
    
    audits = query.order_by(SecurityAudit.created_at.desc()).limit(limit).all()
    return audits

# Migration planning
@app.get("/migration/plan")
async def get_migration_plan(db: Session = Depends(get_db)):
    """Get quantum-resistant migration plan"""
    # Analyze current cryptographic usage
    keys = db.query(QuantumKeyPair).all()
    
    # Categorize by algorithm and usage
    algorithm_usage = {}
    for key in keys:
        if key.algorithm not in algorithm_usage:
            algorithm_usage[key.algorithm] = {
                "count": 0,
                "total_usage": 0,
                "high_usage_keys": 0
            }
        
        algorithm_usage[key.algorithm]["count"] += 1
        algorithm_usage[key.algorithm]["total_usage"] += key.usage_count
        
        if key.usage_count > 1000:
            algorithm_usage[key.algorithm]["high_usage_keys"] += 1
    
    # Generate migration priorities
    migration_plan = {
        "assessment_date": datetime.utcnow(),
        "total_keys": len(keys),
        "algorithm_breakdown": algorithm_usage,
        "migration_phases": [
            {
                "phase": 1,
                "priority": "critical",
                "target_algorithms": ["rsa", "ecc"],
                "timeline": "0-3 months",
                "description": "Migrate high-risk classical algorithms"
            },
            {
                "phase": 2,
                "priority": "high",
                "target_algorithms": ["dh", "ecdsa"],
                "timeline": "3-6 months",
                "description": "Migrate medium-risk algorithms"
            },
            {
                "phase": 3,
                "priority": "medium",
                "target_algorithms": ["aes-128"],
                "timeline": "6-12 months",
                "description": "Upgrade symmetric algorithms"
            }
        ],
        "recommended_algorithms": {
            "encryption": ["kyber-768", "kyber-1024"],
            "signing": ["dilithium-3", "falcon-512"],
            "key_exchange": ["kyber-768"]
        },
        "estimated_cost": 250000,  # USD
        "estimated_timeline": "12 months"
    }
    
    return migration_plan

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks"""
    logger.info("Quantum-Resistant Security service started")
    
    # Start background tasks
    asyncio.create_task(periodic_threat_assessment())
    asyncio.create_task(periodic_key_audit())

async def periodic_threat_assessment():
    """Update quantum threat assessment periodically"""
    while True:
        try:
            db = SessionLocal()
            
            # Update threat assessment
            threat_data = assess_quantum_threat()
            
            assessment = QuantumThreatAssessment(
                threat_level=threat_data["threat_level"],
                quantum_readiness_score=np.random.uniform(80, 95),
                vulnerable_algorithms=["rsa-2048", "ecc-256"],
                secure_algorithms=["kyber-768", "dilithium-3"],
                estimated_quantum_threat_date=datetime(2030, 1, 1)
            )
            
            db.add(assessment)
            db.commit()
            db.close()
            
            logger.info("Quantum threat assessment updated")
            
            await asyncio.sleep(86400)  # Update daily
            
        except Exception as e:
            logger.error(f"Error updating threat assessment: {e}")
            await asyncio.sleep(3600)

async def periodic_key_audit():
    """Audit keys periodically"""
    while True:
        try:
            db = SessionLocal()
            
            # Check for keys that need rotation
            keys_needing_rotation = db.query(QuantumKeyPair).filter(
                QuantumKeyPair.status == "active",
                QuantumKeyPair.created_at < datetime.utcnow() - timedelta(days=365)
            ).all()
            
            for key in keys_needing_rotation:
                logger.warning(f"Key {key.key_id} needs rotation (age: {(datetime.utcnow() - key.created_at).days} days)")
            
            db.close()
            
            await asyncio.sleep(3600)  # Check every hour
            
        except Exception as e:
            logger.error(f"Error in key audit: {e}")
            await asyncio.sleep(1800)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8088)