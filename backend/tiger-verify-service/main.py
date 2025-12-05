#!/usr/bin/env python3

"""
Tiger Verify Service
Category: identity_verification
Description: Complete identity verification and KYC system for TigerEx platform
Features: Multi-level verification, document upload, facial recognition, admin controls
"""

from flask import Flask, request, jsonify, g, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import os
import uuid
import json
import hashlib
import shutil
from werkzeug.utils import secure_filename
from functools import wraps
import base64
from io import BytesIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/tigerex')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'tiger-verify-secret-key')
app.config['UPLOAD_FOLDER'] = 'uploads/verifications'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Role-based access control
def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.role != 'admin':
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.role != 'super_admin':
            return jsonify({'success': False, 'error': 'Super admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Models
class User(db.Model):
    __tablename__ = 'tiger_verify_users'
    
    id = db.Column(db.String(50), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default='user')  # user, admin, super_admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VerificationRecord(db.Model):
    __tablename__ = 'tiger_verification_records'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(50), db.ForeignKey('tiger_verify_users.id'), nullable=False)
    verification_type = db.Column(db.String(50), nullable=False)  # basic, advanced, institutional
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, needs_review
    personal_info = db.Column(db.JSON)
    document_info = db.Column(db.JSON)
    biometric_data = db.Column(db.JSON)
    admin_notes = db.Column(db.Text)
    reviewed_by = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='verifications')

class VerificationDocument(db.Model):
    __tablename__ = 'tiger_verification_documents'
    
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    verification_id = db.Column(db.String(50), db.ForeignKey('tiger_verification_records.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # passport, id_card, driver_license, proof_of_address
    file_path = db.Column(db.String(255), nullable=False)
    file_hash = db.Column(db.String(64), nullable=False)
    extraction_data = db.Column(db.JSON)  # OCR extracted data
    status = db.Column(db.String(20), default='uploaded')  # uploaded, verified, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    verification = db.relationship('VerificationRecord', backref='documents')

# User Routes
@app.route('/api/tiger-verify/status', methods=['GET'])
@jwt_required()
def get_verification_status():
    try:
        user_id = get_jwt_identity()
        verifications = VerificationRecord.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'success': True,
            'service': 'tiger-verify-service',
            'verifications': [{
                'id': v.id,
                'type': v.verification_type,
                'status': v.status,
                'created_at': v.created_at.isoformat(),
                'updated_at': v.updated_at.isoformat()
            } for v in verifications],
            'current_level': max([v.verification_type for v in verifications], default='none')
        })
    except Exception as e:
        logger.error(f"Error getting verification status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tiger-verify/submit', methods=['POST'])
@jwt_required()
def submit_verification():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        verification_type = data.get('verification_type', 'basic')
        personal_info = data.get('personal_info', {})
        
        # Check if user already has a pending verification
        existing = VerificationRecord.query.filter_by(
            user_id=user_id, 
            verification_type=verification_type,
            status='pending'
        ).first()
        
        if existing:
            return jsonify({
                'success': False, 
                'error': 'You already have a pending verification of this type'
            }), 400
        
        verification = VerificationRecord(
            user_id=user_id,
            verification_type=verification_type,
            personal_info=personal_info,
            status='pending'
        )
        
        db.session.add(verification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Verification submitted successfully',
            'verification_id': verification.id
        })
    except Exception as e:
        logger.error(f"Error submitting verification: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tiger-verify/upload-document', methods=['POST'])
@jwt_required()
def upload_document():
    try:
        user_id = get_jwt_identity()
        verification_id = request.form.get('verification_id')
        document_type = request.form.get('document_type')
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Verify ownership
        verification = VerificationRecord.query.filter_by(
            id=verification_id, 
            user_id=user_id
        ).first()
        
        if not verification:
            return jsonify({'success': False, 'error': 'Verification not found'}), 404
        
        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(
            app.config['UPLOAD_FOLDER'], 
            f"{verification_id}_{document_type}_{filename}"
        )
        file.save(file_path)
        
        # Calculate file hash
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        # Create document record
        document = VerificationDocument(
            verification_id=verification_id,
            document_type=document_type,
            file_path=file_path,
            file_hash=file_hash
        )
        
        db.session.add(document)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Document uploaded successfully',
            'document_id': document.id
        })
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Admin Routes
@app.route('/api/tiger-verify/admin/pending-verifications', methods=['GET'])
@admin_required
def get_pending_verifications():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        verifications = VerificationRecord.query.filter_by(status='pending')\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'verifications': [{
                'id': v.id,
                'user_id': v.user_id,
                'verification_type': v.verification_type,
                'personal_info': v.personal_info,
                'created_at': v.created_at.isoformat(),
                'documents': [{
                    'id': d.id,
                    'document_type': d.document_type,
                    'status': d.status
                } for d in v.documents]
            } for v in verifications.items],
            'total': verifications.total,
            'pages': verifications.pages,
            'current_page': page
        })
    except Exception as e:
        logger.error(f"Error getting pending verifications: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tiger-verify/admin/approve/<verification_id>', methods=['POST'])
@admin_required
def approve_verification(verification_id):
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        notes = data.get('notes', '')
        
        verification = VerificationRecord.query.get(verification_id)
        if not verification:
            return jsonify({'success': False, 'error': 'Verification not found'}), 404
        
        verification.status = 'approved'
        verification.admin_notes = notes
        verification.reviewed_by = current_user_id
        verification.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Verification approved successfully'
        })
    except Exception as e:
        logger.error(f"Error approving verification: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tiger-verify/admin/reject/<verification_id>', methods=['POST'])
@admin_required
def reject_verification(verification_id):
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        reason = data.get('reason', '')
        
        verification = VerificationRecord.query.get(verification_id)
        if not verification:
            return jsonify({'success': False, 'error': 'Verification not found'}), 404
        
        verification.status = 'rejected'
        verification.admin_notes = reason
        verification.reviewed_by = current_user_id
        verification.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Verification rejected successfully'
        })
    except Exception as e:
        logger.error(f"Error rejecting verification: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tiger-verify/admin/stats', methods=['GET'])
@admin_required
def admin_stats():
    try:
        total_verifications = VerificationRecord.query.count()
        pending_verifications = VerificationRecord.query.filter_by(status='pending').count()
        approved_verifications = VerificationRecord.query.filter_by(status='approved').count()
        rejected_verifications = VerificationRecord.query.filter_by(status='rejected').count()
        
        # Stats by verification type
        basic_count = VerificationRecord.query.filter_by(verification_type='basic').count()
        advanced_count = VerificationRecord.query.filter_by(verification_type='advanced').count()
        institutional_count = VerificationRecord.query.filter_by(verification_type='institutional').count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_verifications': total_verifications,
                'pending_verifications': pending_verifications,
                'approved_verifications': approved_verifications,
                'rejected_verifications': rejected_verifications,
                'approval_rate': (approved_verifications / total_verifications * 100) if total_verifications > 0 else 0,
                'by_type': {
                    'basic': basic_count,
                    'advanced': advanced_count,
                    'institutional': institutional_count
                },
                'service_name': 'tiger-verify-service',
                'category': 'identity_verification'
            }
        })
    except Exception as e:
        logger.error(f"Error getting admin stats: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tiger-verify/admin/users', methods=['GET'])
@super_admin_required
def admin_user_management():
    try:
        users = User.query.all()
        return jsonify({
            'success': True,
            'users': [{
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'created_at': user.created_at.isoformat(),
                'verification_count': len(user.verifications)
            } for user in users]
        })
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tiger-verify/admin/users/<user_id>/role', methods=['PUT'])
@super_admin_required
def update_user_role(user_id):
    try:
        data = request.get_json()
        new_role = data.get('role')
        
        if new_role not in ['user', 'admin', 'super_admin']:
            return jsonify({'success': False, 'error': 'Invalid role'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        user.role = new_role
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User role updated successfully'
        })
    except Exception as e:
        logger.error(f"Error updating user role: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'tiger-verify-service',
        'category': 'identity_verification',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5003)), debug=True)