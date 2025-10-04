#!/usr/bin/env python3
"""
Yield Arena Service Service
Category: earn
Description: Yield farming competitions
"""

from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import os
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/tigerex')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Admin decorator
def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        # Add admin check logic here
        return f(*args, **kwargs)
    return decorated_function

# Models
class YieldarenaserviceRecord(db.Model):
    __tablename__ = 'yield_arena_service_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    data = db.Column(db.JSON)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# User Routes
@app.route('/api/yield-arena-service/status', methods=['GET'])
@jwt_required()
def get_status():
    try:
        user_id = get_jwt_identity()
        records = YieldarenaserviceRecord.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'success': True,
            'service': 'yield-arena-service',
            'status': 'active',
            'records_count': len(records),
            'data': [{
                'id': r.id,
                'data': r.data,
                'status': r.status,
                'created_at': r.created_at.isoformat(),
                'updated_at': r.updated_at.isoformat()
            } for r in records]
        })
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/yield-arena-service/create', methods=['POST'])
@jwt_required()
def create_record():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        record = YieldarenaserviceRecord(
            user_id=user_id,
            data=data
        )
        
        db.session.add(record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Record created successfully',
            'record_id': record.id
        })
    except Exception as e:
        logger.error(f"Error creating record: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/yield-arena-service/update/<int:record_id>', methods=['PUT'])
@jwt_required()
def update_record(record_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        record = YieldarenaserviceRecord.query.filter_by(
            id=record_id, user_id=user_id
        ).first()
        
        if not record:
            return jsonify({'success': False, 'error': 'Record not found'}), 404
        
        record.data = data
        record.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Record updated successfully'
        })
    except Exception as e:
        logger.error(f"Error updating record: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Admin Routes
@app.route('/api/yield-arena-service/admin/stats', methods=['GET'])
@admin_required
def admin_stats():
    try:
        total_records = YieldarenaserviceRecord.query.count()
        active_records = YieldarenaserviceRecord.query.filter_by(status='active').count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_records': total_records,
                'active_records': active_records,
                'service_name': 'yield-arena-service',
                'category': 'earn'
            }
        })
    except Exception as e:
        logger.error(f"Error getting admin stats: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'yield-arena-service',
        'category': 'earn',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
