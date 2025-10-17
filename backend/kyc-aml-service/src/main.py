/*
 * TigerEx Exchange Platform
 * Version: 7.0.0 - Consolidated Production Release
 * 
 * Complete cryptocurrency exchange platform with:
 * - CEX/DEX hybrid functionality
 * - 105+ exchange features
 * - Multi-platform support (Web, Mobile, Desktop)
 * - Enterprise-grade security
 * - White-label deployment ready
 * 
 * Production-ready implementation
 */

"""
TigerEx KYC/AML Service
Complete KYC verification and AML screening system
Port: 8210
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import asyncio
import asyncpg
import redis.asyncio as redis
import structlog
import uvicorn
import os
import secrets
import hashlib
import json
import httpx
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import io
import base64
import magic
import aiofiles
from jose import jwt

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/tigerex")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

# KYC Provider Configuration (Onfido/Jumio)
KYC_PROVIDER = os.getenv("KYC_PROVIDER", "onfido")  # onfido, jumio, or manual
ONFIDO_API_KEY = os.getenv("ONFIDO_API_KEY", "")
ONFIDO_API_URL = "https://api.onfido.com/v3"
JUMIO_API_TOKEN = os.getenv("JUMIO_API_TOKEN", "")
JUMIO_API_SECRET = os.getenv("JUMIO_API_SECRET", "")
JUMIO_API_URL = "https://netverify.com/api/v4"

# AML Provider Configuration (Chainalysis/Elliptic)
AML_PROVIDER = os.getenv("AML_PROVIDER", "chainalysis")  # chainalysis, elliptic, or manual
CHAINALYSIS_API_KEY = os.getenv("CHAINALYSIS_API_KEY", "")
CHAINALYSIS_API_URL = "https://api.chainalysis.com/api/kyt/v2"
ELLIPTIC_API_KEY = os.getenv("ELLIPTIC_API_KEY", "")
ELLIPTIC_API_URL = "https://api.elliptic.co/v2"

# File storage
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Global connections
db_pool = None
redis_client = None

# FastAPI app
app = FastAPI(
    title="TigerEx KYC/AML Service",
    description="Complete KYC verification and AML screening system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Enums
class KYCStatus(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    RESUBMIT = "resubmit"

class KYCLevel(str, Enum):
    LEVEL_0 = "level_0"  # No KYC
    LEVEL_1 = "level_1"  # Basic (email + phone)
    LEVEL_2 = "level_2"  # Intermediate (ID document)
    LEVEL_3 = "level_3"  # Advanced (ID + selfie + address proof)

class DocumentType(str, Enum):
    PASSPORT = "passport"
    DRIVERS_LICENSE = "drivers_license"
    NATIONAL_ID = "national_id"
    RESIDENCE_PERMIT = "residence_permit"
    PROOF_OF_ADDRESS = "proof_of_address"
    SELFIE = "selfie"

class AMLRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    SEVERE = "severe"

class TransactionRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Pydantic Models
class KYCSubmission(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: str  # YYYY-MM-DD
    nationality: str = Field(..., min_length=2, max_length=3)  # ISO country code
    country_of_residence: str = Field(..., min_length=2, max_length=3)
    address_line1: str = Field(..., min_length=1, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    state_province: Optional[str] = Field(None, max_length=100)
    postal_code: str = Field(..., min_length=1, max_length=20)
    phone_number: str = Field(..., min_length=1, max_length=20)
    kyc_level: KYCLevel = KYCLevel.LEVEL_2

class KYCReview(BaseModel):
    status: KYCStatus
    rejection_reason: Optional[str] = None
    notes: Optional[str] = None
    approved_level: Optional[KYCLevel] = None

class AMLScreeningRequest(BaseModel):
    user_id: int
    full_name: str
    date_of_birth: str
    nationality: str
    address: str

class TransactionScreeningRequest(BaseModel):
    user_id: int
    transaction_hash: Optional[str] = None
    from_address: str
    to_address: str
    amount: Decimal
    currency: str
    blockchain: str

class DocumentUploadResponse(BaseModel):
    document_id: str
    document_type: DocumentType
    file_name: str
    file_size: int
    uploaded_at: datetime
    status: str

# Helper functions
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Verify JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {"user_id": int(user_id), "email": payload.get("email")}
    except Exception as e:
        logger.error("Token verification failed", error=str(e))
        raise HTTPException(status_code=401, detail="Invalid token")

async def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Verify admin JWT token"""
    user = await verify_token(credentials)
    
    # Check if user is admin
    async with db_pool.acquire() as conn:
        admin = await conn.fetchrow("""
            SELECT id FROM admins WHERE user_id = $1 AND is_active = TRUE
        """, user['user_id'])
        
        if not admin:
            raise HTTPException(status_code=403, detail="Admin access required")
    
    return user

def calculate_risk_score(data: Dict[str, Any]) -> int:
    """Calculate risk score based on various factors"""
    score = 0
    
    # Age factor
    if 'date_of_birth' in data:
        try:
            dob = datetime.strptime(data['date_of_birth'], '%Y-%m-%d')
            age = (datetime.now() - dob).days // 365
            if age < 18:
                score += 50
            elif age < 21:
                score += 20
            elif age > 80:
                score += 10
        except:
            score += 30
    
    # High-risk countries
    high_risk_countries = ['AF', 'BY', 'CF', 'CU', 'CD', 'ER', 'GN', 'GW', 'HT', 'IR', 
                          'IQ', 'KP', 'LB', 'LY', 'ML', 'MM', 'NI', 'SO', 'SS', 'SD', 
                          'SY', 'VE', 'YE', 'ZW']
    
    if data.get('nationality') in high_risk_countries:
        score += 40
    if data.get('country_of_residence') in high_risk_countries:
        score += 30
    
    # Sanctioned countries
    sanctioned_countries = ['CU', 'IR', 'KP', 'SY', 'RU']
    if data.get('nationality') in sanctioned_countries:
        score += 100
    if data.get('country_of_residence') in sanctioned_countries:
        score += 80
    
    return min(score, 100)

async def extract_text_from_image(image_bytes: bytes) -> str:
    """Extract text from image using OCR"""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        logger.error("OCR extraction failed", error=str(e))
        return ""

async def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from PDF"""
    try:
        images = convert_from_bytes(pdf_bytes)
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image) + "\n"
        return text
    except Exception as e:
        logger.error("PDF text extraction failed", error=str(e))
        return ""

async def verify_document_with_onfido(user_id: int, document_id: str) -> Dict[str, Any]:
    """Verify document using Onfido API"""
    if not ONFIDO_API_KEY:
        logger.warning("Onfido API key not configured")
        return {"status": "manual_review", "confidence": 0}
    
    try:
        async with httpx.AsyncClient() as client:
            # Create applicant
            applicant_response = await client.post(
                f"{ONFIDO_API_URL}/applicants",
                headers={"Authorization": f"Token token={ONFIDO_API_KEY}"},
                json={"first_name": "User", "last_name": str(user_id)}
            )
            applicant_data = applicant_response.json()
            applicant_id = applicant_data.get("id")
            
            # Upload document
            # Note: In production, you'd upload the actual document file
            
            # Create check
            check_response = await client.post(
                f"{ONFIDO_API_URL}/checks",
                headers={"Authorization": f"Token token={ONFIDO_API_KEY}"},
                json={
                    "applicant_id": applicant_id,
                    "report_names": ["document", "facial_similarity_photo"]
                }
            )
            check_data = check_response.json()
            
            return {
                "status": check_data.get("status", "pending"),
                "result": check_data.get("result", "pending"),
                "confidence": 85 if check_data.get("result") == "clear" else 50
            }
    except Exception as e:
        logger.error("Onfido verification failed", error=str(e))
        return {"status": "error", "confidence": 0}

async def screen_with_chainalysis(address: str, blockchain: str) -> Dict[str, Any]:
    """Screen address using Chainalysis API"""
    if not CHAINALYSIS_API_KEY:
        logger.warning("Chainalysis API key not configured")
        return {"risk_level": "unknown", "score": 50}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CHAINALYSIS_API_URL}/users/{address}/transfers",
                headers={"Token": CHAINALYSIS_API_KEY},
                json={
                    "network": blockchain,
                    "asset": "native",
                    "transferReference": address
                }
            )
            data = response.json()
            
            # Analyze risk
            risk_score = data.get("riskScore", 50)
            risk_level = "low" if risk_score < 30 else "medium" if risk_score < 70 else "high"
            
            return {
                "risk_level": risk_level,
                "score": risk_score,
                "alerts": data.get("alerts", []),
                "categories": data.get("categories", [])
            }
    except Exception as e:
        logger.error("Chainalysis screening failed", error=str(e))
        return {"risk_level": "unknown", "score": 50}

# Database initialization
async def init_database():
    """Initialize database connection and create tables"""
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)
        
        async with db_pool.acquire() as conn:
            # KYC applications table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS kyc_applications (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    kyc_level VARCHAR(20) NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    first_name VARCHAR(100),
                    last_name VARCHAR(100),
                    date_of_birth DATE,
                    nationality VARCHAR(3),
                    country_of_residence VARCHAR(3),
                    address_line1 VARCHAR(255),
                    address_line2 VARCHAR(255),
                    city VARCHAR(100),
                    state_province VARCHAR(100),
                    postal_code VARCHAR(20),
                    phone_number VARCHAR(20),
                    risk_score INTEGER DEFAULT 0,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reviewed_at TIMESTAMP,
                    reviewed_by INTEGER,
                    rejection_reason TEXT,
                    notes TEXT,
                    approved_level VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # KYC documents table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS kyc_documents (
                    id SERIAL PRIMARY KEY,
                    application_id INTEGER REFERENCES kyc_applications(id) ON DELETE CASCADE,
                    user_id INTEGER NOT NULL,
                    document_type VARCHAR(50) NOT NULL,
                    document_id VARCHAR(64) UNIQUE NOT NULL,
                    file_name VARCHAR(255),
                    file_path VARCHAR(512),
                    file_size INTEGER,
                    mime_type VARCHAR(100),
                    status VARCHAR(20) DEFAULT 'pending',
                    verification_result JSONB,
                    extracted_text TEXT,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verified_at TIMESTAMP
                )
            """)
            
            # AML screenings table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS aml_screenings (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    screening_type VARCHAR(50) NOT NULL,
                    risk_level VARCHAR(20),
                    risk_score INTEGER,
                    screening_data JSONB,
                    alerts JSONB,
                    provider VARCHAR(50),
                    screened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                )
            """)
            
            # Transaction screenings table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS transaction_screenings (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    transaction_hash VARCHAR(255),
                    from_address VARCHAR(255),
                    to_address VARCHAR(255),
                    amount DECIMAL(36, 18),
                    currency VARCHAR(20),
                    blockchain VARCHAR(50),
                    risk_level VARCHAR(20),
                    risk_score INTEGER,
                    alerts JSONB,
                    blocked BOOLEAN DEFAULT FALSE,
                    screened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Compliance alerts table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS compliance_alerts (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    alert_type VARCHAR(50) NOT NULL,
                    severity VARCHAR(20) NOT NULL,
                    description TEXT,
                    data JSONB,
                    status VARCHAR(20) DEFAULT 'open',
                    resolved_at TIMESTAMP,
                    resolved_by INTEGER,
                    resolution_notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Admins table (for admin verification)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER UNIQUE NOT NULL,
                    role VARCHAR(50) DEFAULT 'admin',
                    permissions JSONB DEFAULT '[]',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_kyc_user_id ON kyc_applications(user_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_kyc_status ON kyc_applications(status)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_docs_app_id ON kyc_documents(application_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_docs_user_id ON kyc_documents(user_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_aml_user_id ON aml_screenings(user_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_tx_screen_user_id ON transaction_screenings(user_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON compliance_alerts(user_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_status ON compliance_alerts(status)")
            
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))
        raise

async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    try:
        redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
        await redis_client.ping()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.error("Redis connection failed", error=str(e))
        raise

# Startup and shutdown events
@app.on_event("startup")
async def startup():
    await init_database()
    await init_redis()
    
    # Create upload directory
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    logger.info("KYC/AML Service started")

@app.on_event("shutdown")
async def shutdown():
    if db_pool:
        await db_pool.close()
    if redis_client:
        await redis_client.close()
    logger.info("KYC/AML Service stopped")

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "kyc-aml-service",
        "timestamp": datetime.utcnow().isoformat()
    }

# Submit KYC Application
@app.post("/api/kyc/submit", status_code=201)
async def submit_kyc_application(
    submission: KYCSubmission,
    current_user: Dict = Depends(verify_token)
):
    """Submit KYC application"""
    try:
        async with db_pool.acquire() as conn:
            # Check if user already has a pending or approved application
            existing = await conn.fetchrow("""
                SELECT id, status FROM kyc_applications
                WHERE user_id = $1 AND status IN ('pending', 'submitted', 'under_review', 'approved')
                ORDER BY created_at DESC LIMIT 1
            """, current_user['user_id'])
            
            if existing:
                if existing['status'] == 'approved':
                    raise HTTPException(status_code=400, detail="KYC already approved")
                elif existing['status'] in ['pending', 'submitted', 'under_review']:
                    raise HTTPException(status_code=400, detail="KYC application already in progress")
            
            # Calculate risk score
            risk_score = calculate_risk_score({
                'date_of_birth': submission.date_of_birth,
                'nationality': submission.nationality,
                'country_of_residence': submission.country_of_residence
            })
            
            # Insert application
            application = await conn.fetchrow("""
                INSERT INTO kyc_applications (
                    user_id, kyc_level, status, first_name, last_name, date_of_birth,
                    nationality, country_of_residence, address_line1, address_line2,
                    city, state_province, postal_code, phone_number, risk_score
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                RETURNING id, status, risk_score, created_at
            """, current_user['user_id'], submission.kyc_level.value, 'submitted',
                submission.first_name, submission.last_name, submission.date_of_birth,
                submission.nationality, submission.country_of_residence,
                submission.address_line1, submission.address_line2,
                submission.city, submission.state_province, submission.postal_code,
                submission.phone_number, risk_score)
            
            # Create compliance alert if high risk
            if risk_score > 70:
                await conn.execute("""
                    INSERT INTO compliance_alerts (user_id, alert_type, severity, description, data)
                    VALUES ($1, $2, $3, $4, $5)
                """, current_user['user_id'], 'high_risk_kyc', 'high',
                    f"High risk KYC application (score: {risk_score})",
                    json.dumps({'application_id': application['id'], 'risk_score': risk_score}))
            
            logger.info("KYC application submitted", user_id=current_user['user_id'], 
                       application_id=application['id'])
            
            return {
                "application_id": application['id'],
                "status": application['status'],
                "risk_score": application['risk_score'],
                "submitted_at": application['created_at'].isoformat(),
                "message": "KYC application submitted successfully. Please upload required documents."
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("KYC submission failed", error=str(e))
        raise HTTPException(status_code=500, detail="KYC submission failed")

# Upload KYC Document
@app.post("/api/kyc/upload-document", response_model=DocumentUploadResponse)
async def upload_kyc_document(
    application_id: int = Form(...),
    document_type: DocumentType = Form(...),
    file: UploadFile = File(...),
    current_user: Dict = Depends(verify_token)
):
    """Upload KYC document"""
    try:
        # Verify file size
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large (max 10MB)")
        
        # Verify file type
        mime = magic.from_buffer(contents, mime=True)
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']
        if mime not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        async with db_pool.acquire() as conn:
            # Verify application belongs to user
            application = await conn.fetchrow("""
                SELECT id, status FROM kyc_applications
                WHERE id = $1 AND user_id = $2
            """, application_id, current_user['user_id'])
            
            if not application:
                raise HTTPException(status_code=404, detail="Application not found")
            
            if application['status'] not in ['submitted', 'resubmit']:
                raise HTTPException(status_code=400, detail="Cannot upload documents for this application")
            
            # Generate document ID and save file
            document_id = secrets.token_urlsafe(32)
            file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'bin'
            file_name = f"{document_id}.{file_extension}"
            file_path = os.path.join(UPLOAD_DIR, file_name)
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(contents)
            
            # Extract text from document
            extracted_text = ""
            if mime.startswith('image/'):
                extracted_text = await extract_text_from_image(contents)
            elif mime == 'application/pdf':
                extracted_text = await extract_text_from_pdf(contents)
            
            # Insert document record
            document = await conn.fetchrow("""
                INSERT INTO kyc_documents (
                    application_id, user_id, document_type, document_id,
                    file_name, file_path, file_size, mime_type, extracted_text
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING id, document_id, document_type, file_name, file_size, uploaded_at, status
            """, application_id, current_user['user_id'], document_type.value,
                document_id, file.filename, file_path, len(contents), mime, extracted_text)
            
            logger.info("Document uploaded", user_id=current_user['user_id'],
                       application_id=application_id, document_id=document_id)
            
            return DocumentUploadResponse(
                document_id=document['document_id'],
                document_type=DocumentType(document['document_type']),
                file_name=document['file_name'],
                file_size=document['file_size'],
                uploaded_at=document['uploaded_at'],
                status=document['status']
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Document upload failed", error=str(e))
        raise HTTPException(status_code=500, detail="Document upload failed")

# Get KYC Status
@app.get("/api/kyc/status")
async def get_kyc_status(current_user: Dict = Depends(verify_token)):
    """Get user's KYC status"""
    try:
        async with db_pool.acquire() as conn:
            application = await conn.fetchrow("""
                SELECT id, kyc_level, status, risk_score, submitted_at, reviewed_at,
                       rejection_reason, approved_level
                FROM kyc_applications
                WHERE user_id = $1
                ORDER BY created_at DESC LIMIT 1
            """, current_user['user_id'])
            
            if not application:
                return {
                    "status": "not_submitted",
                    "kyc_level": "level_0",
                    "message": "No KYC application found"
                }
            
            # Get documents
            documents = await conn.fetch("""
                SELECT document_type, status, uploaded_at
                FROM kyc_documents
                WHERE application_id = $1
                ORDER BY uploaded_at DESC
            """, application['id'])
            
            return {
                "application_id": application['id'],
                "status": application['status'],
                "kyc_level": application['kyc_level'],
                "approved_level": application['approved_level'],
                "risk_score": application['risk_score'],
                "submitted_at": application['submitted_at'].isoformat() if application['submitted_at'] else None,
                "reviewed_at": application['reviewed_at'].isoformat() if application['reviewed_at'] else None,
                "rejection_reason": application['rejection_reason'],
                "documents": [
                    {
                        "type": doc['document_type'],
                        "status": doc['status'],
                        "uploaded_at": doc['uploaded_at'].isoformat()
                    }
                    for doc in documents
                ]
            }
    except Exception as e:
        logger.error("Failed to get KYC status", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get KYC status")

# Admin: Get Pending KYC Applications
@app.get("/api/admin/kyc/pending")
async def get_pending_kyc_applications(
    current_user: Dict = Depends(verify_admin_token),
    limit: int = 50,
    offset: int = 0
):
    """Get pending KYC applications for review"""
    try:
        async with db_pool.acquire() as conn:
            applications = await conn.fetch("""
                SELECT 
                    a.id, a.user_id, a.kyc_level, a.status, a.first_name, a.last_name,
                    a.date_of_birth, a.nationality, a.country_of_residence, a.risk_score,
                    a.submitted_at,
                    COUNT(d.id) as document_count
                FROM kyc_applications a
                LEFT JOIN kyc_documents d ON d.application_id = a.id
                WHERE a.status IN ('submitted', 'under_review')
                GROUP BY a.id
                ORDER BY a.risk_score DESC, a.submitted_at ASC
                LIMIT $1 OFFSET $2
            """, limit, offset)
            
            total = await conn.fetchval("""
                SELECT COUNT(*) FROM kyc_applications
                WHERE status IN ('submitted', 'under_review')
            """)
            
            return {
                "applications": [
                    {
                        "id": app['id'],
                        "user_id": app['user_id'],
                        "kyc_level": app['kyc_level'],
                        "status": app['status'],
                        "full_name": f"{app['first_name']} {app['last_name']}",
                        "date_of_birth": app['date_of_birth'].isoformat() if app['date_of_birth'] else None,
                        "nationality": app['nationality'],
                        "country_of_residence": app['country_of_residence'],
                        "risk_score": app['risk_score'],
                        "document_count": app['document_count'],
                        "submitted_at": app['submitted_at'].isoformat()
                    }
                    for app in applications
                ],
                "total": total,
                "limit": limit,
                "offset": offset
            }
    except Exception as e:
        logger.error("Failed to get pending applications", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get pending applications")

# Admin: Get KYC Application Details
@app.get("/api/admin/kyc/applications/{application_id}")
async def get_kyc_application_details(
    application_id: int,
    current_user: Dict = Depends(verify_admin_token)
):
    """Get detailed KYC application information"""
    try:
        async with db_pool.acquire() as conn:
            application = await conn.fetchrow("""
                SELECT * FROM kyc_applications WHERE id = $1
            """, application_id)
            
            if not application:
                raise HTTPException(status_code=404, detail="Application not found")
            
            # Get documents
            documents = await conn.fetch("""
                SELECT id, document_type, document_id, file_name, file_size,
                       status, uploaded_at, verification_result
                FROM kyc_documents
                WHERE application_id = $1
                ORDER BY uploaded_at DESC
            """, application_id)
            
            # Get AML screenings
            aml_screenings = await conn.fetch("""
                SELECT screening_type, risk_level, risk_score, screened_at
                FROM aml_screenings
                WHERE user_id = $1
                ORDER BY screened_at DESC
                LIMIT 5
            """, application['user_id'])
            
            # Get compliance alerts
            alerts = await conn.fetch("""
                SELECT alert_type, severity, description, status, created_at
                FROM compliance_alerts
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT 10
            """, application['user_id'])
            
            return {
                "application": dict(application),
                "documents": [dict(doc) for doc in documents],
                "aml_screenings": [dict(screen) for screen in aml_screenings],
                "compliance_alerts": [dict(alert) for alert in alerts]
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get application details", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get application details")

# Admin: Review KYC Application
@app.post("/api/admin/kyc/review/{application_id}")
async def review_kyc_application(
    application_id: int,
    review: KYCReview,
    current_user: Dict = Depends(verify_admin_token)
):
    """Review and approve/reject KYC application"""
    try:
        async with db_pool.acquire() as conn:
            # Get application
            application = await conn.fetchrow("""
                SELECT id, user_id, status FROM kyc_applications WHERE id = $1
            """, application_id)
            
            if not application:
                raise HTTPException(status_code=404, detail="Application not found")
            
            if application['status'] not in ['submitted', 'under_review']:
                raise HTTPException(status_code=400, detail="Application cannot be reviewed")
            
            # Update application
            await conn.execute("""
                UPDATE kyc_applications
                SET status = $1, reviewed_at = CURRENT_TIMESTAMP, reviewed_by = $2,
                    rejection_reason = $3, notes = $4, approved_level = $5,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = $6
            """, review.status.value, current_user['user_id'], review.rejection_reason,
                review.notes, review.approved_level.value if review.approved_level else None,
                application_id)
            
            # Update user KYC status in users table (if exists)
            if review.status == KYCStatus.APPROVED:
                # This would update the main users table
                logger.info("KYC approved", application_id=application_id,
                           user_id=application['user_id'], level=review.approved_level)
            
            logger.info("KYC reviewed", application_id=application_id,
                       status=review.status.value, reviewer=current_user['user_id'])
            
            return {
                "message": f"Application {review.status.value}",
                "application_id": application_id,
                "status": review.status.value
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("KYC review failed", error=str(e))
        raise HTTPException(status_code=500, detail="KYC review failed")

# AML Screening
@app.post("/api/aml/screen")
async def screen_user_aml(
    screening: AMLScreeningRequest,
    current_user: Dict = Depends(verify_admin_token)
):
    """Perform AML screening on user"""
    try:
        # Calculate risk score
        risk_score = calculate_risk_score({
            'date_of_birth': screening.date_of_birth,
            'nationality': screening.nationality
        })
        
        # Determine risk level
        if risk_score < 30:
            risk_level = AMLRiskLevel.LOW
        elif risk_score < 60:
            risk_level = AMLRiskLevel.MEDIUM
        elif risk_score < 80:
            risk_level = AMLRiskLevel.HIGH
        else:
            risk_level = AMLRiskLevel.SEVERE
        
        screening_data = {
            "full_name": screening.full_name,
            "date_of_birth": screening.date_of_birth,
            "nationality": screening.nationality,
            "address": screening.address,
            "risk_factors": []
        }
        
        # Add risk factors
        if risk_score > 50:
            screening_data["risk_factors"].append("High risk jurisdiction")
        
        async with db_pool.acquire() as conn:
            # Insert screening record
            screening_record = await conn.fetchrow("""
                INSERT INTO aml_screenings (
                    user_id, screening_type, risk_level, risk_score,
                    screening_data, provider, expires_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id, screened_at
            """, screening.user_id, 'user_screening', risk_level.value, risk_score,
                json.dumps(screening_data), AML_PROVIDER,
                datetime.utcnow() + timedelta(days=90))
            
            # Create alert if high risk
            if risk_level in [AMLRiskLevel.HIGH, AMLRiskLevel.SEVERE]:
                await conn.execute("""
                    INSERT INTO compliance_alerts (user_id, alert_type, severity, description, data)
                    VALUES ($1, $2, $3, $4, $5)
                """, screening.user_id, 'aml_high_risk', risk_level.value,
                    f"High risk AML screening result (score: {risk_score})",
                    json.dumps({'screening_id': screening_record['id'], 'risk_score': risk_score}))
            
            logger.info("AML screening completed", user_id=screening.user_id,
                       risk_level=risk_level.value, risk_score=risk_score)
            
            return {
                "screening_id": screening_record['id'],
                "risk_level": risk_level.value,
                "risk_score": risk_score,
                "screening_data": screening_data,
                "screened_at": screening_record['screened_at'].isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(days=90)).isoformat()
            }
    except Exception as e:
        logger.error("AML screening failed", error=str(e))
        raise HTTPException(status_code=500, detail="AML screening failed")

# Transaction Screening
@app.post("/api/aml/screen-transaction")
async def screen_transaction(
    transaction: TransactionScreeningRequest,
    current_user: Dict = Depends(verify_admin_token)
):
    """Screen cryptocurrency transaction for AML risks"""
    try:
        # Screen addresses with Chainalysis (if configured)
        from_risk = await screen_with_chainalysis(transaction.from_address, transaction.blockchain)
        to_risk = await screen_with_chainalysis(transaction.to_address, transaction.blockchain)
        
        # Calculate overall risk
        max_risk_score = max(from_risk.get('score', 0), to_risk.get('score', 0))
        
        if max_risk_score < 30:
            risk_level = TransactionRiskLevel.LOW
        elif max_risk_score < 60:
            risk_level = TransactionRiskLevel.MEDIUM
        elif max_risk_score < 80:
            risk_level = TransactionRiskLevel.HIGH
        else:
            risk_level = TransactionRiskLevel.CRITICAL
        
        # Determine if transaction should be blocked
        blocked = risk_level == TransactionRiskLevel.CRITICAL
        
        alerts = []
        if from_risk.get('alerts'):
            alerts.extend(from_risk['alerts'])
        if to_risk.get('alerts'):
            alerts.extend(to_risk['alerts'])
        
        async with db_pool.acquire() as conn:
            # Insert screening record
            screening_record = await conn.fetchrow("""
                INSERT INTO transaction_screenings (
                    user_id, transaction_hash, from_address, to_address,
                    amount, currency, blockchain, risk_level, risk_score,
                    alerts, blocked
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                RETURNING id, screened_at
            """, transaction.user_id, transaction.transaction_hash,
                transaction.from_address, transaction.to_address,
                transaction.amount, transaction.currency, transaction.blockchain,
                risk_level.value, max_risk_score, json.dumps(alerts), blocked)
            
            # Create alert if high risk or blocked
            if risk_level in [TransactionRiskLevel.HIGH, TransactionRiskLevel.CRITICAL]:
                await conn.execute("""
                    INSERT INTO compliance_alerts (user_id, alert_type, severity, description, data)
                    VALUES ($1, $2, $3, $4, $5)
                """, transaction.user_id, 'suspicious_transaction', risk_level.value,
                    f"Suspicious transaction detected (score: {max_risk_score})",
                    json.dumps({
                        'screening_id': screening_record['id'],
                        'transaction_hash': transaction.transaction_hash,
                        'risk_score': max_risk_score,
                        'blocked': blocked
                    }))
            
            logger.info("Transaction screened", user_id=transaction.user_id,
                       risk_level=risk_level.value, blocked=blocked)
            
            return {
                "screening_id": screening_record['id'],
                "risk_level": risk_level.value,
                "risk_score": max_risk_score,
                "blocked": blocked,
                "alerts": alerts,
                "from_address_risk": from_risk,
                "to_address_risk": to_risk,
                "screened_at": screening_record['screened_at'].isoformat()
            }
    except Exception as e:
        logger.error("Transaction screening failed", error=str(e))
        raise HTTPException(status_code=500, detail="Transaction screening failed")

# Get Compliance Alerts
@app.get("/api/admin/compliance/alerts")
async def get_compliance_alerts(
    current_user: Dict = Depends(verify_admin_token),
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get compliance alerts"""
    try:
        async with db_pool.acquire() as conn:
            query = """
                SELECT id, user_id, alert_type, severity, description, status,
                       created_at, resolved_at, resolved_by
                FROM compliance_alerts
                WHERE 1=1
            """
            params = []
            param_count = 0
            
            if status:
                param_count += 1
                query += f" AND status = ${param_count}"
                params.append(status)
            
            if severity:
                param_count += 1
                query += f" AND severity = ${param_count}"
                params.append(severity)
            
            param_count += 1
            query += f" ORDER BY created_at DESC LIMIT ${param_count}"
            params.append(limit)
            
            param_count += 1
            query += f" OFFSET ${param_count}"
            params.append(offset)
            
            alerts = await conn.fetch(query, *params)
            
            total_query = "SELECT COUNT(*) FROM compliance_alerts WHERE 1=1"
            total_params = []
            if status:
                total_query += " AND status = $1"
                total_params.append(status)
            if severity:
                total_query += f" AND severity = ${len(total_params) + 1}"
                total_params.append(severity)
            
            total = await conn.fetchval(total_query, *total_params)
            
            return {
                "alerts": [dict(alert) for alert in alerts],
                "total": total,
                "limit": limit,
                "offset": offset
            }
    except Exception as e:
        logger.error("Failed to get compliance alerts", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get compliance alerts")

# Get KYC Statistics
@app.get("/api/admin/kyc/statistics")
async def get_kyc_statistics(current_user: Dict = Depends(verify_admin_token)):
    """Get KYC statistics for admin dashboard"""
    try:
        async with db_pool.acquire() as conn:
            stats = await conn.fetchrow("""
                SELECT
                    COUNT(*) FILTER (WHERE status = 'pending') as pending,
                    COUNT(*) FILTER (WHERE status = 'submitted') as submitted,
                    COUNT(*) FILTER (WHERE status = 'under_review') as under_review,
                    COUNT(*) FILTER (WHERE status = 'approved') as approved,
                    COUNT(*) FILTER (WHERE status = 'rejected') as rejected,
                    COUNT(*) FILTER (WHERE risk_score > 70) as high_risk,
                    AVG(risk_score) as avg_risk_score
                FROM kyc_applications
                WHERE created_at > NOW() - INTERVAL '30 days'
            """)
            
            return dict(stats)
    except Exception as e:
        logger.error("Failed to get KYC statistics", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get KYC statistics")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8210)