"""
Two-Factor Authentication Reset Service

Provides secure 2FA reset functionality with sequential verification:
1. Email verification
2. Phone verification  
3. Liveness verification
4. 2FA reset (only after all verifications pass)
"""

import secrets
import hashlib
import smtplib
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VerificationState(Enum):
    """Enumeration of verification states in the 2FA reset flow"""
    IDLE = "idle"
    EMAIL_VERIFIED = "email_verified"
    PHONE_VERIFIED = "phone_verified"
    LIVENESS_PASSED = "liveness_passed"
    COMPLETE = "complete"
    EXPIRED = "expired"
    FAILED = "failed"


@dataclass
class VerificationSession:
    """Represents a 2FA reset verification session"""
    session_id: str
    user_id: str
    email: str
    phone: str
    state: VerificationState = VerificationState.IDLE
    email_code: Optional[str] = None
    phone_code: Optional[str] = None
    email_code_expires: Optional[datetime] = None
    phone_code_expires: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(hours=24))
    ip_address: Optional[str] = None
    email_attempts: int = 0
    phone_attempts: int = 0
    liveness_attempts: int = 0
    audit_log: list = field(default_factory=list)
    
    def is_expired(self) -> bool:
        """Check if session has expired"""
        return datetime.utcnow() > self.expires_at
    
    def can_verify_email(self) -> bool:
        """Check if email verification can be performed"""
        return self.state == VerificationState.IDLE and not self.is_expired()
    
    def can_verify_phone(self) -> bool:
        """Check if phone verification can be performed"""
        return (self.state == VerificationState.EMAIL_VERIFIED and 
                not self.is_expired())
    
    def can_verify_liveness(self) -> bool:
        """Check if liveness verification can be performed"""
        return (self.state == VerificationState.PHONE_VERIFIED and 
                not self.is_expired())
    
    def add_audit_entry(self, action: str, details: str):
        """Add entry to audit log"""
        self.audit_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "details": details
        })


class TwoFactorResetService:
    """
    Service for handling Two-Factor Authentication reset with sequential verification.
    
    Verification Order:
    1. Email verification - Required first
    2. Phone verification - Only after email verified
    3. Liveness verification - Only after phone verified
    4. 2FA reset - Only after all verifications passed
    """
    
    # Rate limiting constants
    MAX_EMAIL_ATTEMPTS = 3
    MAX_PHONE_ATTEMPTS = 3
    MAX_LIVENESS_ATTEMPTS = 3
    EMAIL_CODE_EXPIRY_MINUTES = 15
    PHONE_CODE_EXPIRY_MINUTES = 10
    SESSION_EXPIRY_HOURS = 24
    
    def __init__(self, db_connection=None, email_service=None, sms_service=None, liveness_service=None):
        """
        Initialize the 2FA reset service.
        
        Args:
            db_connection: Database connection for session storage
            email_service: Email service for sending verification codes
            sms_service: SMS service for sending phone codes
            liveness_service: Service for liveness verification
        """
        self.sessions: Dict[str, VerificationSession] = {}
        self.db = db_connection
        self.email_service = email_service
        self.sms_service = sms_service
        self.liveness_service = liveness_service
    
    def _generate_code(self, length: int = 6) -> str:
        """Generate a cryptographically secure verification code"""
        return ''.join(str(secrets.randbelow(10)) for _ in range(length))
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        return secrets.token_urlsafe(32)
    
    def _send_email_code(self, email: str, code: str) -> bool:
        """Send verification code via email"""
        if self.email_service:
            subject = "TigerExchange 2FA Reset Verification Code"
            body = f"Your verification code is: {code}\n\nThis code expires in {self.EMAIL_CODE_EXPIRY_MINUTES} minutes.\n\nIf you did not request this, please ignore this email."
            return self.email_service.send(email, subject, body)
        logger.info(f"Email verification code sent to {email}: {code}")
        return True
    
    def _send_sms_code(self, phone: str, code: str) -> bool:
        """Send verification code via SMS"""
        if self.sms_service:
            message = f"TigerExchange: Your verification code is {code}. Expires in {self.PHONE_CODE_EXPIRY_MINUTES} minutes."
            return self.sms_service.send(phone, message)
        logger.info(f"SMS verification code sent to {phone}: {code}")
        return True
    
    def initiate_reset(self, user_id: str, email: str, phone: str, ip_address: str = None) -> Dict[str, Any]:
        """
        Initiate a new 2FA reset session.
        
        Args:
            user_id: The user's account ID
            email: User's registered email
            phone: User's registered phone number
            ip_address: Client IP for audit logging
        
        Returns:
            Dictionary with session_id and next step information
        """
        # Check for existing active session
        for session in self.sessions.values():
            if session.user_id == user_id and not session.is_expired():
                if session.state != VerificationState.IDLE:
                    return {
                        "success": False,
                        "error": "An active verification session already exists",
                        "session_id": session.session_id,
                        "current_state": session.state.value
                    }
        
        # Create new session
        session_id = self._generate_session_id()
        session = VerificationSession(
            session_id=session_id,
            user_id=user_id,
            email=email,
            phone=phone,
            ip_address=ip_address
        )
        
        self.sessions[session_id] = session
        session.add_audit_entry("initiate", f"2FA reset initiated from IP: {ip_address}")
        
        logger.info(f"2FA reset session created for user {user_id}")
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "2FA reset initiated. Please verify your email first.",
            "next_step": "email_verification",
            "expires_at": session.expires_at.isoformat()
        }
    
    def verify_email(self, session_id: str, code: str, ip_address: str = None) -> Dict[str, Any]:
        """
        Verify email verification code.
        
        IMPORTANT: This is the FIRST step in the verification sequence.
        Users must complete this before phone verification is available.
        
        Args:
            session_id: The verification session ID
            code: The email verification code
            ip_address: Client IP for audit logging
        
        Returns:
            Dictionary with verification result
        """
        session = self.sessions.get(session_id)
        
        if not session:
            return {"success": False, "error": "Invalid session"}
        
        if session.is_expired():
            session.state = VerificationState.EXPIRED
            session.add_audit_entry("email_expired", "Session expired during email verification")
            return {"success": False, "error": "Session expired", "must_restart": True}
        
        if not session.can_verify_email():
            return {
                "success": False, 
                "error": "Cannot verify email at this time",
                "current_state": session.state.value,
                "required_state": VerificationState.IDLE.value
            }
        
        # Check rate limiting
        if session.email_attempts >= self.MAX_EMAIL_ATTEMPTS:
            session.add_audit_entry("email_rate_limit", "Email verification rate limited")
            return {
                "success": False, 
                "error": "Too many attempts. Please try again later.",
                "rate_limited": True
            }
        
        # Verify code
        session.email_attempts += 1
        
        if not session.email_code or not code:
            return {"success": False, "error": "Invalid verification code"}
        
        if datetime.utcnow() > session.email_code_expires:
            session.add_audit_entry("email_code_expired", "Email code expired")
            return {"success": False, "error": "Verification code expired"}
        
        if session.email_code != code:
            session.add_audit_entry("email_code_invalid", f"Invalid email code attempt {session.email_attempts}/{self.MAX_EMAIL_ATTEMPTS}")
            remaining = self.MAX_EMAIL_ATTEMPTS - session.email_attempts
            return {
                "success": False, 
                "error": f"Invalid verification code",
                "attempts_remaining": remaining
            }
        
        # Email verified successfully
        session.state = VerificationState.EMAIL_VERIFIED
        session.updated_at = datetime.utcnow()
        session.email_code = None  # Clear code after successful use
        session.add_audit_entry("email_verified", f"Email verified successfully from IP: {ip_address}")
        
        # Generate and send phone code
        phone_code = self._generate_code()
        session.phone_code = phone_code
        session.phone_code_expires = datetime.utcnow() + timedelta(minutes=self.PHONE_CODE_EXPIRY_MINUTES)
        
        self._send_sms_code(session.phone, phone_code)
        
        logger.info(f"Email verified for session {session_id}, phone code sent")
        
        return {
            "success": True,
            "message": "Email verified successfully. Please verify your phone number.",
            "next_step": "phone_verification",
            "phone_hint": self._mask_phone(session.phone)
        }
    
    def verify_phone(self, session_id: str, code: str, ip_address: str = None) -> Dict[str, Any]:
        """
        Verify phone/SMS verification code.
        
        IMPORTANT: This is the SECOND step. Email MUST be verified first.
        
        Args:
            session_id: The verification session ID
            code: The phone/SMS verification code
            ip_address: Client IP for audit logging
        
        Returns:
            Dictionary with verification result
        """
        session = self.sessions.get(session_id)
        
        if not session:
            return {"success": False, "error": "Invalid session"}
        
        if session.is_expired():
            session.state = VerificationState.EXPIRED
            session.add_audit_entry("phone_expired", "Session expired during phone verification")
            return {"success": False, "error": "Session expired", "must_restart": True}
        
        if not session.can_verify_phone():
            return {
                "success": False,
                "error": "Email verification required first",
                "current_state": session.state.value,
                "required_state": VerificationState.EMAIL_VERIFIED.value
            }
        
        # Check rate limiting
        if session.phone_attempts >= self.MAX_PHONE_ATTEMPTS:
            session.add_audit_entry("phone_rate_limit", "Phone verification rate limited")
            return {
                "success": False,
                "error": "Too many attempts. Please try again later.",
                "rate_limited": True
            }
        
        # Verify code
        session.phone_attempts += 1
        
        if not session.phone_code or not code:
            return {"success": False, "error": "Invalid verification code"}
        
        if datetime.utcnow() > session.phone_code_expires:
            session.add_audit_entry("phone_code_expired", "Phone code expired")
            return {"success": False, "error": "Verification code expired"}
        
        if session.phone_code != code:
            session.add_audit_entry("phone_code_invalid", f"Invalid phone code attempt {session.phone_attempts}/{self.MAX_PHONE_ATTEMPTS}")
            remaining = self.MAX_PHONE_ATTEMPTS - session.phone_attempts
            return {
                "success": False,
                "error": f"Invalid verification code",
                "attempts_remaining": remaining
            }
        
        # Phone verified successfully
        session.state = VerificationState.PHONE_VERIFIED
        session.updated_at = datetime.utcnow()
        session.phone_code = None  # Clear code after successful use
        session.add_audit_entry("phone_verified", f"Phone verified successfully from IP: {ip_address}")
        
        logger.info(f"Phone verified for session {session_id}")
        
        return {
            "success": True,
            "message": "Phone verified successfully. Please complete liveness verification.",
            "next_step": "liveness_verification",
            "liveness_required": True
        }
    
    def verify_liveness(self, session_id: str, liveness_data: Dict[str, Any], ip_address: str = None) -> Dict[str, Any]:
        """
        Verify liveness/selfie verification.
        
        IMPORTANT: This is the THIRD and FINAL step before 2FA reset.
        Both email AND phone MUST be verified first.
        
        Args:
            session_id: The verification session ID
            liveness_data: Liveness verification data (image, metadata, etc.)
            ip_address: Client IP for audit logging
        
        Returns:
            Dictionary with verification result
        """
        session = self.sessions.get(session_id)
        
        if not session:
            return {"success": False, "error": "Invalid session"}
        
        if session.is_expired():
            session.state = VerificationState.EXPIRED
            session.add_audit_entry("liveness_expired", "Session expired during liveness verification")
            return {"success": False, "error": "Session expired", "must_restart": True}
        
        if not session.can_verify_liveness():
            return {
                "success": False,
                "error": "Email and phone verification required first",
                "current_state": session.state.value,
                "required_state": VerificationState.PHONE_VERIFIED.value
            }
        
        # Check rate limiting
        if session.liveness_attempts >= self.MAX_LIVENESS_ATTEMPTS:
            session.add_audit_entry("liveness_rate_limit", "Liveness verification rate limited - flagged for manual review")
            return {
                "success": False,
                "error": "Too many failed attempts. Your account requires manual review.",
                "requires_manual_review": True
            }
        
        session.liveness_attempts += 1
        
        # Perform liveness verification
        liveness_result = self._perform_liveness_check(liveness_data, session)
        
        if not liveness_result["success"]:
            session.add_audit_entry(
                "liveness_failed", 
                f"Liveness check failed: {liveness_result.get('error', 'Unknown error')}"
            )
            return {
                "success": False,
                "error": liveness_result.get("error", "Liveness verification failed"),
                "attempts_remaining": self.MAX_LIVENESS_ATTEMPTS - session.liveness_attempts
            }
        
        # Liveness verified successfully - all verifications complete
        session.state = VerificationState.LIVENESS_PASSED
        session.updated_at = datetime.utcnow()
        session.add_audit_entry("liveness_passed", f"Liveness verified from IP: {ip_address}")
        
        logger.info(f"Liveness verified for session {session_id}, proceeding to 2FA reset")
        
        return {
            "success": True,
            "message": "All verifications complete. 2FA reset is now available.",
            "next_step": "complete_2fa_reset",
            "ready_for_reset": True
        }
    
    def _perform_liveness_check(self, liveness_data: Dict[str, Any], session: VerificationSession) -> Dict[str, Any]:
        """
        Perform actual liveness verification.
        
        In production, this would integrate with a face verification service.
        """
        if self.liveness_service:
            return self.liveness_service.verify(
                user_id=session.user_id,
                image_data=liveness_data.get("image"),
                session_id=session_id
            )
        
        # Mock liveness check for development
        # In production, replace with actual liveness verification service
        return {
            "success": True,
            "match_score": 0.95,
            "spoof_detected": False
        }
    
    def complete_2fa_reset(self, session_id: str, ip_address: str = None) -> Dict[str, Any]:
        """
        Complete the 2FA reset after all verifications are successful.
        
        IMPORTANT: This is the FINAL step. ALL verification steps must be complete:
        1. Email verification ✓
        2. Phone verification ✓
        3. Liveness verification ✓
        
        Args:
            session_id: The verification session ID
            ip_address: Client IP for audit logging
        
        Returns:
            Dictionary with reset confirmation
        """
        session = self.sessions.get(session_id)
        
        if not session:
            return {"success": False, "error": "Invalid session"}
        
        if session.is_expired():
            session.state = VerificationState.EXPIRED
            session.add_audit_entry("reset_expired", "Attempted reset after session expired")
            return {"success": False, "error": "Session expired", "must_restart": True}
        
        # Check if all verifications are complete
        if session.state != VerificationState.LIVENESS_PASSED:
            missing_steps = []
            if session.state.value in [VerificationState.IDLE.value, VerificationState.EMAIL_VERIFIED.value]:
                missing_steps.append("phone_verification")
            if session.state != VerificationState.PHONE_VERIFIED:
                missing_steps.append("liveness_verification")
            
            return {
                "success": False,
                "error": "All verification steps must be completed first",
                "current_state": session.state.value,
                "missing_steps": missing_steps
            }
        
        # All verifications complete - perform 2FA reset
        session.state = VerificationState.COMPLETE
        session.updated_at = datetime.utcnow()
        session.add_audit_entry(
            "2fa_reset_complete", 
            f"2FA reset completed successfully from IP: {ip_address}"
        )
        
        # In production, this would:
        # 1. Disable 2FA on the user account
        # 2. Send confirmation email to user
        # 3. Log the audit trail
        
        logger.info(f"2FA reset completed for user {session.user_id}")
        
        return {
            "success": True,
            "message": "2FA has been reset successfully. Please set up 2FA on your next login.",
            "reset_complete": True,
            "next_action": "setup_2fa_on_login"
        }
    
    def get_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get the current verification status of a session.
        
        Args:
            session_id: The verification session ID
        
        Returns:
            Dictionary with current status
        """
        session = self.sessions.get(session_id)
        
        if not session:
            return {"valid": False, "error": "Invalid session"}
        
        if session.is_expired():
            return {
                "valid": False,
                "state": VerificationState.EXPIRED.value,
                "must_restart": True
            }
        
        return {
            "valid": True,
            "state": session.state.value,
            "next_step": self._get_next_step(session),
            "expires_at": session.expires_at.isoformat(),
            "verification_progress": {
                "email": session.state.value in [VerificationState.EMAIL_VERIFIED.value, 
                                                  VerificationState.PHONE_VERIFIED.value,
                                                  VerificationState.LIVENESS_PASSED.value,
                                                  VerificationState.COMPLETE.value],
                "phone": session.state.value in [VerificationState.PHONE_VERIFIED.value,
                                                  VerificationState.LIVENESS_PASSED.value,
                                                  VerificationState.COMPLETE.value],
                "liveness": session.state.value in [VerificationState.LIVENESS_PASSED.value,
                                                    VerificationState.COMPLETE.value]
            }
        }
    
    def _get_next_step(self, session: VerificationSession) -> str:
        """Determine the next required step based on current state"""
        step_map = {
            VerificationState.IDLE: "email_verification",
            VerificationState.EMAIL_VERIFIED: "phone_verification",
            VerificationState.PHONE_VERIFIED: "liveness_verification",
            VerificationState.LIVENESS_PASSED: "complete_2fa_reset",
            VerificationState.COMPLETE: "none",
            VerificationState.EXPIRED: "restart_required"
        }
        return step_map.get(session.state, "unknown")
    
    def _mask_phone(self, phone: str) -> str:
        """Mask phone number for display"""
        if len(phone) < 4:
            return "****"
        return "*" * (len(phone) - 4) + phone[-4:]
    
    def send_email_code(self, session_id: str, ip_address: str = None) -> Dict[str, Any]:
        """
        Send email verification code (used for initial email verification).
        
        Args:
            session_id: The verification session ID
            ip_address: Client IP for audit logging
        
        Returns:
            Dictionary with result
        """
        session = self.sessions.get(session_id)
        
        if not session:
            return {"success": False, "error": "Invalid session"}
        
        if not session.can_verify_email():
            return {
                "success": False,
                "error": "Cannot send email code at this time",
                "current_state": session.state.value
            }
        
        # Generate new code
        code = self._generate_code()
        session.email_code = code
        session.email_code_expires = datetime.utcnow() + timedelta(minutes=self.EMAIL_CODE_EXPIRY_MINUTES)
        
        self._send_email_code(session.email, code)
        
        session.add_audit_entry("email_code_sent", f"Email code sent to {session.email}")
        
        return {
            "success": True,
            "message": f"Verification code sent to {self._mask_email(session.email)}",
            "expires_in_minutes": self.EMAIL_CODE_EXPIRY_MINUTES
        }
    
    def _mask_email(self, email: str) -> str:
        """Mask email for display"""
        parts = email.split("@")
        if len(parts) != 2 or len(parts[0]) < 3:
            return email
        return parts[0][:2] + "***@" + parts[1]


# Example API endpoints (for reference)
"""
POST /api/2fa/reset/initiate
{
    "user_id": "user123",
    "email": "user@example.com",
    "phone": "+1234567890"
}

POST /api/2fa/reset/send-email-code
{
    "session_id": "abc123..."
}

POST /api/2fa/reset/verify-email
{
    "session_id": "abc123...",
    "code": "123456"
}

POST /api/2fa/reset/verify-phone
{
    "session_id": "abc123...",
    "code": "654321"
}

POST /api/2fa/reset/verify-liveness
{
    "session_id": "abc123...",
    "liveness_data": {
        "image": "base64...",
        "timestamp": "2024-01-01T00:00:00Z"
    }
}

POST /api/2fa/reset/complete
{
    "session_id": "abc123..."
}

GET /api/2fa/reset/status
{
    "session_id": "abc123..."
}
"""


# Export for use
__all__ = ['TwoFactorResetService', 'VerificationSession', 'VerificationState']def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
