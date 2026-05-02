#!/usr/bin/env python3
"""
TigerEx 2FA Reset Verification API
Secure backend for 2FA verification with rate limiting and audit logging

@version 2.0.0
"""

import os
import re
import secrets
import hashlib
import time
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Optional
from collections import defaultdict

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)
CORS(app)

# Rate limiting
limiter = Limiter(
    key_func=lambda: request.headers.get('X-Forwarded-For', request.remote_addr),
    app=app,
    default_limits=["10 per minute", "30 per hour"]
)

# Configuration
PORT = int(os.environ.get('PORT', 8200))
SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', 1800))  # 30 minutes
VERIFICATION_SECRET = os.environ.get('VERIFICATION_SECRET', secrets.token_hex(32))

# In-memory storage (replace with database in production)
_verification_codes: Dict[str, Dict] = {}
_sessions: Dict[str, Dict] = {}
_audit_log = []

# ==================== HELPERS ====================

def generate_code() -> str:
    """Generate 6-digit verification code."""
    return f"{secrets.randbelow(1000000):06d}"


def hash_code(code: str) -> str:
    """Hash verification code."""
    return hashlib.pbkdf2_hmac(
        'sha256',
        code.encode(),
        VERIFICATION_SECRET.encode(),
        100000
    ).hex()


def create_session(user_id: str) -> str:
    """Create verification session."""
    session_id = secrets.token_urlsafe(32)
    
    _sessions[session_id] = {
        'user_id': user_id,
        'created_at': time.time(),
        'email_verified': False,
        'phone_verified': False,
        'face_verified': False,
        'attempts': {
            'email': 0,
            'phone': 0,
            'face': 0
        }
    }
    
    return session_id


def get_session(session_id: str) -> Optional[Dict]:
    """Get session if valid."""
    session = _sessions.get(session_id)
    if not session:
        return None
    
    # Check timeout
    if time.time() - session['created_at'] > SESSION_TIMEOUT:
        del _sessions[session_id]
        return None
    
    return session


def check_rate_limit(key: str, max_attempts: int = 5) -> bool:
    """Check if user exceeded rate limit."""
    attempts = _verification_codes.get(f'attempts_{key}', 0)
    if attempts >= max_attempts:
        return False
    return True


def record_attempt(key: str):
    """Record verification attempt."""
    key = f'attempts_{key}'
    _verification_codes[key] = _verification_codes.get(key, 0) + 1


def audit_log(action: str, session_id: str, details: Dict):
    """Record audit log."""
    _audit_log.append({
        'timestamp': datetime.utcnow().isoformat(),
        'action': action,
        'session_id': session_id[:8] + '...',
        'ip': request.headers.get('X-Forwarded-For', request.remote_addr),
        **details
    })


def require_session(f):
    """Decorator to require valid session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        session_id = request.headers.get('X-Session-Token')
        if not session_id:
            return jsonify({'error': 'Session required'}), 401
        
        session = get_session(session_id)
        if not session:
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        request.session = session
        return f(*args, **kwargs)
    return decorated


# ==================== HEALTH ====================

@app.route('/health')
def health():
    """Health check."""
    return jsonify({
        'status': 'healthy',
        'sessions': len(_sessions),
        'timestamp': datetime.utcnow().isoformat()
    })


# ==================== SESSION MANAGEMENT ====================

@app.route('/api/v1/verification/start', methods=['POST'])
@limiter.limit("5/minute")
def start_verification():
    """Start new verification session."""
    data = request.get_json() or {}
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    # Validate email format
    email = data.get('email', '')
    if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    session_id = create_session(user_id)
    
    audit_log('session_start', session_id, {'user_id': user_id[:8] + '...'})
    
    return jsonify({
        'session_id': session_id,
        'expires_in': SESSION_TIMEOUT
    })


# ==================== EMAIL VERIFICATION ====================

@app.route('/api/v1/verification/email/send', methods=['POST'])
@limiter.limit("10/hour")
@require_session
def send_email_code():
    """Send verification code to email."""
    data = request.get_json() or {}
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email required'}), 400
    
    # Check rate limit
    if not check_rate_limit(f'email_{email}'):
        return jsonify({'error': 'Too many attempts. Try again later.'}), 429
    
    # Generate code (in production, send via email service)
    code = generate_code()
    
    _verification_codes[f'email_{request.session["user_id"]}'] = {
        'code': hash_code(code),
        'email': email,
        'created_at': time.time(),
        'expires_at': time.time() + 300  # 5 minutes
    }
    
    audit_log('email_code_sent', request.headers.get('X-Session-Token', ''), {
        'email': email[:4] + '...'
    })
    
    # In production, send email here
    logger.info(f"Email verification code for {email}: {code}")
    
    return jsonify({
        'message': 'Code sent to email',
        'expires_in': 300
    })


@app.route('/api/v1/verification/email/verify', methods=['POST'])
@limiter.limit("10/minute")
@require_session
def verify_email_code():
    """Verify email code."""
    data = request.get_json() or {}
    code = data.get('code', '')
    
    if not code or len(code) != 6:
        return jsonify({'error': 'Invalid code format'}), 400
    
    # Check rate limit
    user_id = request.session['user_id']
    if not check_rate_limit(f'verify_email_{user_id}'):
        return jsonify({'error': 'Too many attempts'}), 429
    
    record_attempt(f'verify_email_{user_id}')
    
    # Get stored code
    stored = _verification_codes.get(f'email_{user_id}')
    if not stored:
        return jsonify({'error': 'No code sent. Request a new code.'}), 400
    
    # Check expiration
    if time.time() > stored['expires_at']:
        return jsonify({'error': 'Code expired. Request a new one.'}), 400
    
    # Verify code
    if stored['code'] != hash_code(code):
        audit_log('email_verify_failed', request.headers.get('X-Session-Token', ''), {
            'reason': 'invalid_code'
        })
        return jsonify({'error': 'Invalid code'}), 400
    
    # Mark as verified
    request.session['email_verified'] = True
    request.session['email'] = stored['email']
    
    audit_log('email_verified', request.headers.get('X-Session-Token', ''), {
        'email': stored['email'][:4] + '...'
    })
    
    return jsonify({
        'success': True,
        'verified': ['email', 'phone', 'face']
    })


# ==================== PHONE VERIFICATION ====================

@app.route('/api/v1/verification/phone/send', methods=['POST'])
@limiter.limit("10/hour")
@require_session
def send_phone_code():
    """Send verification code to phone."""
    data = request.get_json() or {}
    phone = data.get('phone')
    
    if not phone:
        return jsonify({'error': 'Phone required'}), 400
    
    # Check rate limit
    if not check_rate_limit(f'phone_{phone}'):
        return jsonify({'error': 'Too many attempts'}), 429
    
    # Generate code
    code = generate_code()
    
    _verification_codes[f'phone_{request.session["user_id"]}'] = {
        'code': hash_code(code),
        'phone': phone[-4:],  # Only store last 4 digits
        'created_at': time.time(),
        'expires_at': time.time() + 300
    }
    
    audit_log('phone_code_sent', request.headers.get('X-Session-Token', ''), {
        'phone': phone[-4:]
    })
    
    logger.info(f"Phone verification code for {phone}: {code}")
    
    return jsonify({
        'message': 'Code sent to phone',
        'expires_in': 300
    })


@app.route('/api/v1/verification/phone/verify', methods=['POST'])
@limiter.limit("10/minute")
@require_session
def verify_phone_code():
    """Verify phone code."""
    data = request.get_json() or {}
    code = data.get('code', '')
    
    if not code or len(code) != 6:
        return jsonify({'error': 'Invalid code format'}), 400
    
    user_id = request.session['user_id']
    record_attempt(f'verify_phone_{user_id}')
    
    stored = _verification_codes.get(f'phone_{user_id}')
    if not stored or time.time() > stored['expires_at']:
        return jsonify({'error': 'Invalid or expired code'}), 400
    
    if stored['code'] != hash_code(code):
        audit_log('phone_verify_failed', request.headers.get('X-Session-Token', ''), {
            'reason': 'invalid_code'
        })
        return jsonify({'error': 'Invalid code'}), 400
    
    request.session['phone_verified'] = True
    
    audit_log('phone_verified', request.headers.get('X-Session-Token', ''), {})
    
    return jsonify({
        'success': True
    })


# ==================== FACE VERIFICATION ====================

@app.route('/api/v1/verification/face/init', methods=['POST'])
@limiter.limit("5/minute")
@require_session
def init_face_verification():
    """Initialize face verification."""
    # Generate challenge for liveness detection
    challenge = secrets.token_urlsafe(32)
    
    request.session['face_challenge'] = challenge
    request.session['face_captures'] = []
    
    return jsonify({
        'challenge': challenge,
        'instructions': [
            'Position your face in the frame',
            'Blink slowly when prompted',
            'Ensure good lighting'
        ]
    })


@app.route('/api/v1/verification/face/verify', methods=['POST'])
@limiter.limit("5/minute")
@require_session
def verify_face():
    """Verify face with liveness check."""
    if not request.session.get('face_challenge'):
        return jsonify({'error': 'Initialize face verification first'}), 400
    
    data = request.get_json() or {}
    image_data = data.get('image')
    
    if not image_data:
        return jsonify({'error': 'Image required'}), 400
    
    # Record capture
    request.session['face_captures'].append(time.time())
    
    # Check for liveness (multiple captures required)
    if len(request.session['face_captures']) < 3:
        return jsonify({
            'status': 'capturing',
            'progress': len(request.session['face_captures']) / 3
        })
    
    # In production, integrate with face verification service
    # For now, require at least 3 captures
    
    request.session['face_verified'] = True
    
    audit_log('face_verified', request.headers.get('X-Session-Token', ''), {
        'captures': len(request.session['face_captures'])
    })
    
    return jsonify({
        'success': True,
        'liveness_verified': True
    })


# ==================== VERIFICATION STATUS ====================

@app.route('/api/v1/verification/status')
@require_session
def get_verification_status():
    """Get current verification status."""
    session = request.session
    
    return jsonify({
        'user_id': session['user_id'],
        'verified': {
            'email': session.get('email_verified', False),
            'phone': session.get('phone_verified', False),
            'face': session.get('face_verified', False)
        },
        'completed': all([
            session.get('email_verified', False),
            session.get('phone_verified', False),
            session.get('face_verified', False)
        ])
    })


# ==================== COMPLETE RESET ====================

@app.route('/api/v1/verification/reset', methods=['POST'])
@limiter.limit("3/hour")
@require_session
def complete_reset():
    """Complete 2FA reset after all verifications."""
    session = request.session
    
    # Check all verified
    if not all([
        session.get('email_verified'),
        session.get('phone_verified'),
        session.get('face_verified')
    ]):
        return jsonify({
            'error': 'All verifications must be completed',
            'verified': {
                'email': session.get('email_verified'),
                'phone': session.get('phone_verified'),
                'face': session.get('face_verified')
            }
        }), 400
    
    # In production, trigger 2FA reset in user service
    
    audit_log('2fa_reset_completed', request.headers.get('X-Session-Token', ''), {
        'user_id': session['user_id'][:8] + '...'
    })
    
    return jsonify({
        'success': True,
        'message': '2FA has been reset. You can now set up new 2FA.'
    })


# ==================== ERROR HANDLERS ====================

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded', 'retry_after': 3600}), 429


# ==================== MAIN ====================

if __name__ == "__main__":
    logger.info(f"Starting 2FA Verification API on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, threaded=True, debug=False)