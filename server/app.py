"""
TigerEx Backend Server - With Test Code 727752
"""
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import hashlib
import uuid
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'tigerex-secret-key-change-in-production')

# CORS
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# JWT
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

# TEST CODE FOR ALL VERIFICATIONS
TEST_CODE = "727752"
TOTP_SECRET = "JBSWY3DPEHPK3PXP"  # Base32 secret for TOTP

# In-memory database
users_db = {}
orders_db = {}
wallets_db = {}
staking_db = {}
markets_db = {
    "BTCUSDT": {"symbol": "BTCUSDT", "price": 67234.50, "change24h": 2.34},
    "ETHUSDT": {"symbol": "ETHUSDT", "price": 3456.78, "change24h": 1.56},
}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token():
    return str(uuid.uuid4())

# ==================== AUTH ROUTES ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    identifier = data.get('identifier', '')
    password = data.get('password', '')
    
    if not identifier or not password:
        return jsonify({"success": False, "message": "Missing required fields"}), 400
    
    user_id = generate_token()
    users_db[user_id] = {
        "id": user_id,
        "identifier": identifier,
        "password_hash": hash_password(password),
        "email_verified": False,
        "phone_verified": False,
        "2fa_enabled": False,
        "kyc_verified": False,
        "created_at": "2024-01-01T00:00:00Z"
    }
    
    wallets_db[user_id] = {"BTC": 0, "USDT": 1000}
    
    return jsonify({
        "success": True,
        "message": "Registration successful",
        "user": {"id": user_id, "identifier": identifier}
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    identifier = data.get('identifier', '')
    password = data.get('password', '')
    
    user = next((u for u in users_db.values() 
            if u.get('identifier') == identifier), None)
    
    if not user or user.get('password_hash') != hash_password(password):
        return jsonify({"success": False, "message": "Invalid credentials"}), 401
    
    token = create_access_token(identity=user['id'])
    
    return jsonify({
        "success": True,
        "token": token,
        "user": {
            "id": user['id'], 
            "identifier": user['identifier'],
            "email_verified": user.get('email_verified', False),
            "phone_verified": user.get('phone_verified', False),
            "2fa_enabled": user.get('2fa_enabled', False),
            "kyc_verified": user.get('kyc_verified', False)
        }
    })

@app.route('/api/auth/session', methods=['GET'])
@jwt_required()
def get_session():
    user_id = get_jwt_identity()
    user = users_db.get(user_id)
    if not user:
        return jsonify({"success": False}), 401
    return jsonify({
        "success": True,
        "user": {"id": user['id'], "identifier": user['identifier']}
    })

# ==================== EMAIL VERIFICATION ====================

@app.route('/api/auth/send-email-code', methods=['POST'])
def send_email_code():
    data = request.get_json()
    email = data.get('email', '')
    
    # In production, send real email
    # For testing, use TEST_CODE
    return jsonify({
        "success": True,
        "message": f"Code sent to {email}",
        "test_code": TEST_CODE  # 727752
    })

@app.route('/api/auth/verify-email', methods=['POST'])
def verify_email():
    data = request.get_json()
    code = data.get('code', '')
    
    if code == TEST_CODE:  # 727752
        return jsonify({
            "success": True,
            "message": "Email verified successfully",
            "test_code_used": TEST_CODE
        })
    else:
        return jsonify({"success": False, "message": "Invalid code"}), 400

# ==================== PHONE VERIFICATION ====================

@app.route('/api/auth/send-phone-code', methods=['POST'])
def send_phone_code():
    data = request.get_json()
    phone = data.get('phone', '')
    
    return jsonify({
        "success": True,
        "message": f"Code sent to {phone}",
        "test_code": TEST_CODE  # 727752
    })

@app.route('/api/auth/verify-phone', methods=['POST'])
def verify_phone():
    data = request.get_json()
    code = data.get('code', '')
    
    if code == TEST_CODE:  # 727752
        return jsonify({
            "success": True,
            "message": "Phone verified successfully",
            "test_code_used": TEST_CODE
        })
    else:
        return jsonify({"success": False, "message": "Invalid code"}), 400

# ==================== 2FA / TOTP VERIFICATION ====================

@app.route('/api/auth/enable-2fa', methods=['POST'])
@jwt_required()
def enable_2fa():
    # Return TOTP secret for Google Authenticator
    return jsonify({
        "success": True,
        "secret": TOTP_SECRET,
        "test_code": TEST_CODE,
        "message": "2FA enabled. Use test code 727752"
    })

@app.route('/api/auth/verify-2fa', methods=['POST'])
def verify_2fa():
    data = request.get_json()
    code = data.get('code', '')
    
    if code == TEST_CODE:  # 727752
        return jsonify({
            "success": True,
            "message": "2FA verified successfully",
            "test_code_used": TEST_CODE
        })
    else:
        return jsonify({"success": False, "message": "Invalid 2FA code"}), 400

# ==================== KYC VERIFICATION ====================

@app.route('/api/kyc/submit', methods=['POST'])
@jwt_required()
def submit_kyc():
    user_id = get_jwt_identity()
    user = users_db.get(user_id)
    
    if user:
        user['kyc_verified'] = True
    
    return jsonify({
        "success": True,
        "message": "KYC documents submitted",
        "reference": f"KYC-{uuid.uuid4().hex[:6].upper()}"
    })

@app.route('/api/kyc/status', methods=['GET'])
@jwt_required()
def kyc_status():
    user_id = get_jwt_identity()
    user = users_db.get(user_id, {})
    
    return jsonify({
        "success": True,
        "status": "verified" if user.get('kyc_verified') else "pending"
    })

# ==================== TRADING ====================

@app.route('/api/trading/markets', methods=['GET'])
def get_markets():
    return jsonify({"success": True, "markets": list(markets_db.values())})

@app.route('/api/wallet/balance', methods=['GET'])
@jwt_required()
def get_balance():
    user_id = get_jwt_identity()
    balance = wallets_db.get(user_id, {"BTC": 0, "USDT": 1000})
    return jsonify({"success": True, "balance": balance})

@app.route('/')
def index():
    return jsonify({
        "message": "TigerEx API Server - TEST MODE",
        "test_code": TEST_CODE,
        "totp_secret": TOTP_SECRET
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
