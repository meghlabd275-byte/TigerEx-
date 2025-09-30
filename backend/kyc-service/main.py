#!/usr/bin/env python3
"""
TigerEx KYC Service
Advanced KYC/AML compliance service with AI-powered document verification
"""

import os
import uuid
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

import cv2
import numpy as np
import face_recognition
import pytesseract
from PIL import Image
import requests
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import asyncpg
import redis.asyncio as redis
import boto3
from botocore.exceptions import ClientError
import tensorflow as tf
from transformers import pipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models and Enums
class KYCStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRED = "required"

class DocumentType(str, Enum):
    PASSPORT = "passport"
    DRIVERS_LICENSE = "drivers_license"
    NATIONAL_ID = "national_id"
    UTILITY_BILL = "utility_bill"
    BANK_STATEMENT = "bank_statement"
    SELFIE = "selfie"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class KYCDocument:
    id: str
    user_id: str
    document_type: DocumentType
    document_number: Optional[str]
    document_url: str
    status: KYCStatus
    verified_by: Optional[str]
    verified_at: Optional[datetime]
    rejection_reason: Optional[str]
    expiry_date: Optional[datetime]
    confidence_score: float
    ai_analysis: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class KYCRequest(BaseModel):
    document_type: DocumentType
    document_number: Optional[str] = None
    expiry_date: Optional[str] = None

class KYCVerificationResult(BaseModel):
    document_id: str
    status: KYCStatus
    confidence_score: float
    ai_analysis: Dict[str, Any]
    verification_details: Dict[str, Any]

class UserKYCProfile(BaseModel):
    user_id: str
    kyc_level: int
    overall_status: KYCStatus
    risk_level: RiskLevel
    documents: List[Dict[str, Any]]
    verification_history: List[Dict[str, Any]]
    compliance_flags: List[str]
    last_updated: datetime

class KYCService:
    def __init__(self):
        self.app = FastAPI(title="TigerEx KYC Service", version="1.0.0")
        self.setup_middleware()
        self.setup_routes()
        
        # Database connections
        self.db_pool = None
        self.redis_client = None
        
        # AI Models
        self.document_classifier = None
        self.face_recognition_model = None
        self.ocr_engine = None
        self.fraud_detection_model = None
        
        # AWS S3 for document storage
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        
        # External verification services
        self.jumio_api_key = os.getenv('JUMIO_API_KEY')
        self.onfido_api_key = os.getenv('ONFIDO_API_KEY')
        
    async def startup(self):
        """Initialize service on startup"""
        await self.connect_databases()
        await self.load_ai_models()
        logger.info("KYC Service started successfully")
    
    async def connect_databases(self):
        """Connect to PostgreSQL and Redis"""
        try:
            self.db_pool = await asyncpg.create_pool(
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', 5432)),
                user=os.getenv('DB_USER', 'tigerex'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME', 'tigerex'),
                min_size=10,
                max_size=20
            )
            
            self.redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                password=os.getenv('REDIS_PASSWORD'),
                decode_responses=True
            )
            
            logger.info("Database connections established")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    async def load_ai_models(self):
        """Load AI models for document verification"""
        try:
            # Document classification model
            self.document_classifier = pipeline(
                "image-classification",
                model="microsoft/dit-base-finetuned-rvlcdip"
            )
            
            # OCR setup
            pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
            
            # Fraud detection model (simplified)
            self.fraud_detection_model = tf.keras.models.load_model(
                'models/fraud_detection_model.h5'
            ) if os.path.exists('models/fraud_detection_model.h5') else None
            
            logger.info("AI models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load AI models: {e}")
    
    def setup_middleware(self):
        """Setup FastAPI middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "service": "kyc-service"}
        
        @self.app.post("/api/v1/kyc/upload-document")
        async def upload_document(
            background_tasks: BackgroundTasks,
            document_type: DocumentType,
            file: UploadFile = File(...),
            user_id: str = Depends(self.get_current_user)
        ):
            return await self.handle_document_upload(
                user_id, document_type, file, background_tasks
            )
        
        @self.app.get("/api/v1/kyc/profile/{user_id}")
        async def get_kyc_profile(
            user_id: str,
            current_user: str = Depends(self.get_current_user)
        ):
            return await self.get_user_kyc_profile(user_id)
        
        @self.app.post("/api/v1/kyc/verify/{document_id}")
        async def verify_document(
            document_id: str,
            admin_id: str = Depends(self.get_admin_user)
        ):
            return await self.manual_document_verification(document_id, admin_id)
        
        @self.app.post("/api/v1/kyc/reject/{document_id}")
        async def reject_document(
            document_id: str,
            reason: str,
            admin_id: str = Depends(self.get_admin_user)
        ):
            return await self.reject_document_verification(document_id, reason, admin_id)
        
        @self.app.get("/api/v1/kyc/pending-verifications")
        async def get_pending_verifications(
            admin_id: str = Depends(self.get_admin_user),
            page: int = 1,
            limit: int = 20
        ):
            return await self.get_pending_documents(page, limit)
        
        @self.app.post("/api/v1/kyc/bulk-verify")
        async def bulk_verify_documents(
            document_ids: List[str],
            admin_id: str = Depends(self.get_admin_user)
        ):
            return await self.bulk_document_verification(document_ids, admin_id)
        
        @self.app.get("/api/v1/kyc/analytics")
        async def get_kyc_analytics(
            admin_id: str = Depends(self.get_admin_user),
            start_date: Optional[str] = None,
            end_date: Optional[str] = None
        ):
            return await self.get_verification_analytics(start_date, end_date)
        
        @self.app.post("/api/v1/kyc/aml-check")
        async def perform_aml_check(
            user_id: str,
            admin_id: str = Depends(self.get_admin_user)
        ):
            return await self.perform_aml_screening(user_id)
    
    async def handle_document_upload(
        self, 
        user_id: str, 
        document_type: DocumentType, 
        file: UploadFile,
        background_tasks: BackgroundTasks
    ) -> Dict[str, Any]:
        """Handle document upload and initiate verification"""
        try:
            # Validate file
            if not file.content_type.startswith('image/'):
                raise HTTPException(400, "Only image files are allowed")
            
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                raise HTTPException(400, "File size too large")
            
            # Generate document ID
            document_id = str(uuid.uuid4())
            
            # Read file content
            file_content = await file.read()
            
            # Upload to S3
            s3_key = f"kyc-documents/{user_id}/{document_id}/{file.filename}"
            self.s3_client.put_object(
                Bucket=os.getenv('S3_BUCKET_NAME'),
                Key=s3_key,
                Body=file_content,
                ContentType=file.content_type
            )
            
            document_url = f"https://{os.getenv('S3_BUCKET_NAME')}.s3.amazonaws.com/{s3_key}"
            
            # Save document record
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO kyc_documents 
                    (id, user_id, document_type, document_url, status, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, document_id, user_id, document_type.value, document_url, 
                KYCStatus.PENDING.value, datetime.utcnow(), datetime.utcnow())
            
            # Start AI verification in background
            background_tasks.add_task(
                self.ai_document_verification, 
                document_id, 
                file_content, 
                document_type
            )
            
            return {
                "document_id": document_id,
                "status": "uploaded",
                "message": "Document uploaded successfully and verification started"
            }
            
        except Exception as e:
            logger.error(f"Document upload failed: {e}")
            raise HTTPException(500, f"Upload failed: {str(e)}")
    
    async def ai_document_verification(
        self, 
        document_id: str, 
        file_content: bytes, 
        document_type: DocumentType
    ):
        """AI-powered document verification"""
        try:
            # Convert bytes to image
            image = Image.open(io.BytesIO(file_content))
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            verification_results = {
                "document_quality": await self.check_document_quality(cv_image),
                "text_extraction": await self.extract_document_text(cv_image),
                "face_detection": await self.detect_faces(cv_image) if document_type == DocumentType.SELFIE else None,
                "fraud_indicators": await self.detect_fraud_indicators(cv_image),
                "document_classification": await self.classify_document(image),
            }
            
            # Calculate confidence score
            confidence_score = self.calculate_confidence_score(verification_results)
            
            # Determine auto-approval
            auto_approve = (
                confidence_score > 0.85 and 
                len(verification_results["fraud_indicators"]) == 0 and
                verification_results["document_quality"]["score"] > 0.8
            )
            
            status = KYCStatus.APPROVED if auto_approve else KYCStatus.PENDING
            
            # Update database
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE kyc_documents 
                    SET status = $1, confidence_score = $2, ai_analysis = $3, updated_at = $4
                    WHERE id = $5
                """, status.value, confidence_score, json.dumps(verification_results), 
                datetime.utcnow(), document_id)
            
            # Send notification
            await self.send_verification_notification(document_id, status, confidence_score)
            
            logger.info(f"AI verification completed for document {document_id}")
            
        except Exception as e:
            logger.error(f"AI verification failed for document {document_id}: {e}")
            
            # Mark as requiring manual review
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE kyc_documents 
                    SET status = $1, ai_analysis = $2, updated_at = $3
                    WHERE id = $4
                """, KYCStatus.PENDING.value, json.dumps({"error": str(e)}), 
                datetime.utcnow(), document_id)
    
    async def check_document_quality(self, image: np.ndarray) -> Dict[str, Any]:
        """Check document image quality"""
        # Blur detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Brightness check
        brightness = np.mean(gray)
        
        # Resolution check
        height, width = gray.shape
        resolution_score = min(height, width) / 1000  # Normalize to 0-1
        
        return {
            "blur_score": float(blur_score),
            "brightness": float(brightness),
            "resolution_score": float(resolution_score),
            "score": min(1.0, (blur_score / 1000 + brightness / 255 + resolution_score) / 3)
        }
    
    async def extract_document_text(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract text from document using OCR"""
        try:
            # Preprocess image for better OCR
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Extract text
            text = pytesseract.image_to_string(denoised)
            
            # Extract structured data
            data = pytesseract.image_to_data(denoised, output_type=pytesseract.Output.DICT)
            
            return {
                "raw_text": text,
                "confidence": np.mean([int(conf) for conf in data['conf'] if int(conf) > 0]),
                "word_count": len([word for word in data['text'] if word.strip()]),
                "structured_data": self.parse_document_fields(text)
            }
        except Exception as e:
            return {"error": str(e), "raw_text": "", "confidence": 0}
    
    async def detect_faces(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect and analyze faces in selfie documents"""
        try:
            # Convert BGR to RGB for face_recognition
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Find faces
            face_locations = face_recognition.face_locations(rgb_image)
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            
            return {
                "face_count": len(face_locations),
                "face_locations": face_locations,
                "face_quality": self.assess_face_quality(rgb_image, face_locations),
                "liveness_score": self.check_liveness(rgb_image, face_locations)
            }
        except Exception as e:
            return {"error": str(e), "face_count": 0}
    
    async def detect_fraud_indicators(self, image: np.ndarray) -> List[str]:
        """Detect potential fraud indicators"""
        indicators = []
        
        try:
            # Check for digital manipulation
            if self.detect_digital_manipulation(image):
                indicators.append("digital_manipulation")
            
            # Check for photocopied documents
            if self.detect_photocopy(image):
                indicators.append("photocopy_detected")
            
            # Check for screen capture
            if self.detect_screen_capture(image):
                indicators.append("screen_capture")
            
            # Check for template matching (fake documents)
            if self.detect_template_fraud(image):
                indicators.append("template_fraud")
                
        except Exception as e:
            logger.error(f"Fraud detection error: {e}")
            indicators.append("fraud_detection_error")
        
        return indicators
    
    async def classify_document(self, image: Image.Image) -> Dict[str, Any]:
        """Classify document type using AI"""
        try:
            if self.document_classifier:
                results = self.document_classifier(image)
                return {
                    "predicted_type": results[0]["label"],
                    "confidence": results[0]["score"],
                    "all_predictions": results
                }
        except Exception as e:
            logger.error(f"Document classification error: {e}")
        
        return {"predicted_type": "unknown", "confidence": 0.0}
    
    def calculate_confidence_score(self, verification_results: Dict[str, Any]) -> float:
        """Calculate overall confidence score"""
        scores = []
        
        # Document quality score
        if "document_quality" in verification_results:
            scores.append(verification_results["document_quality"]["score"])
        
        # OCR confidence
        if "text_extraction" in verification_results:
            scores.append(verification_results["text_extraction"]["confidence"] / 100)
        
        # Classification confidence
        if "document_classification" in verification_results:
            scores.append(verification_results["document_classification"]["confidence"])
        
        # Fraud penalty
        fraud_penalty = len(verification_results.get("fraud_indicators", [])) * 0.2
        
        base_score = np.mean(scores) if scores else 0.5
        return max(0.0, min(1.0, base_score - fraud_penalty))
    
    async def get_user_kyc_profile(self, user_id: str) -> UserKYCProfile:
        """Get comprehensive KYC profile for user"""
        async with self.db_pool.acquire() as conn:
            # Get user KYC status
            user_row = await conn.fetchrow("""
                SELECT kyc_status, kyc_level FROM users WHERE id = $1
            """, user_id)
            
            if not user_row:
                raise HTTPException(404, "User not found")
            
            # Get documents
            documents = await conn.fetch("""
                SELECT * FROM kyc_documents WHERE user_id = $1 ORDER BY created_at DESC
            """, user_id)
            
            # Calculate risk level
            risk_level = await self.calculate_risk_level(user_id)
            
            return UserKYCProfile(
                user_id=user_id,
                kyc_level=user_row["kyc_level"],
                overall_status=KYCStatus(user_row["kyc_status"]),
                risk_level=risk_level,
                documents=[dict(doc) for doc in documents],
                verification_history=await self.get_verification_history(user_id),
                compliance_flags=await self.get_compliance_flags(user_id),
                last_updated=datetime.utcnow()
            )
    
    async def perform_aml_screening(self, user_id: str) -> Dict[str, Any]:
        """Perform AML screening against watchlists"""
        try:
            # Get user information
            async with self.db_pool.acquire() as conn:
                user = await conn.fetchrow("""
                    SELECT first_name, last_name, email, country_code, date_of_birth
                    FROM users WHERE id = $1
                """, user_id)
            
            if not user:
                raise HTTPException(404, "User not found")
            
            # Screen against sanctions lists
            screening_results = {
                "ofac_screening": await self.screen_ofac(user),
                "eu_sanctions": await self.screen_eu_sanctions(user),
                "un_sanctions": await self.screen_un_sanctions(user),
                "pep_screening": await self.screen_pep(user),
                "adverse_media": await self.screen_adverse_media(user)
            }
            
            # Calculate overall risk score
            risk_score = self.calculate_aml_risk_score(screening_results)
            
            # Update user risk profile
            await self.update_user_risk_profile(user_id, risk_score, screening_results)
            
            return {
                "user_id": user_id,
                "risk_score": risk_score,
                "screening_results": screening_results,
                "recommendations": self.get_aml_recommendations(risk_score),
                "screened_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AML screening failed for user {user_id}: {e}")
            raise HTTPException(500, f"AML screening failed: {str(e)}")
    
    # Helper methods (simplified implementations)
    def parse_document_fields(self, text: str) -> Dict[str, str]:
        """Parse structured fields from document text"""
        # Implement document-specific parsing logic
        return {"parsed_fields": "implementation_needed"}
    
    def assess_face_quality(self, image: np.ndarray, face_locations: List) -> float:
        """Assess quality of detected faces"""
        return 0.8  # Simplified
    
    def check_liveness(self, image: np.ndarray, face_locations: List) -> float:
        """Check if face is from a live person"""
        return 0.9  # Simplified
    
    def detect_digital_manipulation(self, image: np.ndarray) -> bool:
        """Detect digital manipulation in image"""
        return False  # Simplified
    
    def detect_photocopy(self, image: np.ndarray) -> bool:
        """Detect if document is a photocopy"""
        return False  # Simplified
    
    def detect_screen_capture(self, image: np.ndarray) -> bool:
        """Detect if image is a screen capture"""
        return False  # Simplified
    
    def detect_template_fraud(self, image: np.ndarray) -> bool:
        """Detect template-based fraud"""
        return False  # Simplified
    
    async def calculate_risk_level(self, user_id: str) -> RiskLevel:
        """Calculate user risk level"""
        return RiskLevel.LOW  # Simplified
    
    async def get_verification_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get verification history for user"""
        return []  # Simplified
    
    async def get_compliance_flags(self, user_id: str) -> List[str]:
        """Get compliance flags for user"""
        return []  # Simplified
    
    async def screen_ofac(self, user: dict) -> Dict[str, Any]:
        """Screen against OFAC sanctions list"""
        return {"matches": [], "risk_score": 0.0}
    
    async def screen_eu_sanctions(self, user: dict) -> Dict[str, Any]:
        """Screen against EU sanctions list"""
        return {"matches": [], "risk_score": 0.0}
    
    async def screen_un_sanctions(self, user: dict) -> Dict[str, Any]:
        """Screen against UN sanctions list"""
        return {"matches": [], "risk_score": 0.0}
    
    async def screen_pep(self, user: dict) -> Dict[str, Any]:
        """Screen for Politically Exposed Persons"""
        return {"matches": [], "risk_score": 0.0}
    
    async def screen_adverse_media(self, user: dict) -> Dict[str, Any]:
        """Screen for adverse media mentions"""
        return {"matches": [], "risk_score": 0.0}
    
    def calculate_aml_risk_score(self, screening_results: Dict[str, Any]) -> float:
        """Calculate overall AML risk score"""
        return 0.1  # Simplified
    
    async def update_user_risk_profile(self, user_id: str, risk_score: float, results: Dict[str, Any]):
        """Update user's risk profile"""
        pass  # Simplified
    
    def get_aml_recommendations(self, risk_score: float) -> List[str]:
        """Get AML compliance recommendations"""
        return ["regular_monitoring"]  # Simplified
    
    async def send_verification_notification(self, document_id: str, status: KYCStatus, confidence: float):
        """Send verification notification"""
        pass  # Simplified
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """Get current user from JWT token"""
        return "user_id"  # Simplified
    
    async def get_admin_user(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """Get admin user from JWT token"""
        return "admin_id"  # Simplified
    
    async def manual_document_verification(self, document_id: str, admin_id: str):
        """Manual document verification by admin"""
        pass  # Implementation needed
    
    async def reject_document_verification(self, document_id: str, reason: str, admin_id: str):
        """Reject document verification"""
        pass  # Implementation needed
    
    async def get_pending_documents(self, page: int, limit: int):
        """Get pending documents for review"""
        pass  # Implementation needed
    
    async def bulk_document_verification(self, document_ids: List[str], admin_id: str):
        """Bulk verify documents"""
        pass  # Implementation needed
    
    async def get_verification_analytics(self, start_date: str, end_date: str):
        """Get verification analytics"""
        pass  # Implementation needed

# Create service instance
kyc_service = KYCService()

# FastAPI app
app = kyc_service.app

@app.on_event("startup")
async def startup_event():
    await kyc_service.startup()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 3004)))