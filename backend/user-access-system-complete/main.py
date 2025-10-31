"""
Complete User Access System - Full User Functionality
Registration, KYC, Portfolio, Trading Interface, 2FA, Wallet Management
"""

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import asyncio
import json
import logging

app = FastAPI(title="Complete User Access System", version="1.0.0")
security = HTTPBearer()

class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"

class AccountTier(str, Enum):
    BASIC = "basic"
    VERIFIED = "verified"
    PREMIUM = "premium"
    INSTITUTIONAL = "institutional"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LIMIT = "stop_limit"
    STOP_MARKET = "stop_market"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class User(BaseModel):
    user_id: str
    username: str
    email: str
    phone: str
    password_hash: str
    account_tier: AccountTier
    verification_status: VerificationStatus
    is_active: bool
    two_factor_enabled: bool
    created_at: datetime
    last_login: Optional[datetime]
    api_key: Optional[str]
    referral_code: Optional[str]

class KYCDocument(BaseModel):
    document_id: str
    user_id: str
    document_type: str  # passport, driver_license, id_card
    document_number: str
    front_image_url: str
    back_image_url: Optional[str]
    selfie_url: str
    status: VerificationStatus
    submitted_at: datetime
    reviewed_at: Optional[datetime]
    rejection_reason: Optional[str]

class Portfolio(BaseModel):
    user_id: str
    total_value_usd: float
    total_value_btc: float
    assets: Dict[str, float]
    daily_change: float
    daily_change_percent: float
    last_updated: datetime

class Order(BaseModel):
    order_id: str
    user_id: str
    symbol: str
    order_type: OrderType
    order_side: OrderSide
    amount: float
    price: Optional[float]
    filled_amount: float
    remaining_amount: float
    average_price: float
    status: str
    created_at: datetime
    updated_at: datetime

class Wallet(BaseModel):
    wallet_id: str
    user_id: str
    currency: str
    network: str
    address: str
    balance: float
    frozen_balance: float
    created_at: datetime

class Transaction(BaseModel):
    transaction_id: str
    user_id: str
    type: str  # deposit, withdraw, trade, transfer
    currency: str
    amount: float
    fee: float
    status: str
    from_address: Optional[str]
    to_address: Optional[str]
    tx_hash: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

class TwoFactorSetup(BaseModel):
    secret_key: str
    backup_codes: List[str]
    qr_code_url: str

class UserAccessSystem:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.kyc_documents: Dict[str, KYCDocument] = {}
        self.portfolios: Dict[str, Portfolio] = {}
        self.orders: Dict[str, Order] = {}
        self.wallets: Dict[str, Wallet] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.sessions: Dict[str, str] = {}  # token -> user_id
        
    def generate_user_id(self) -> str:
        """Generate unique user ID"""
        import uuid
        return f"user_{uuid.uuid4().hex[:16]}"
    
    def generate_wallet_address(self, currency: str, network: str) -> str:
        """Generate wallet address"""
        import uuid
        import hashlib
        
        unique_string = f"{currency}_{network}_{datetime.utcnow().timestamp()}"
        hash_object = hashlib.sha256(unique_string.encode())
        
        if network == "bitcoin":
            return "1" + hash_object.hexdigest()[:32]
        elif network in ["ethereum", "bsc", "polygon", "arbitrum", "optimism"]:
            return "0x" + hash_object.hexdigest()[:40]
        else:
            return hash_object.hexdigest()[:40]
    
    def calculate_portfolio_value(self, user_id: str) -> Portfolio:
        """Calculate user portfolio value"""
        user_wallets = [w for w in self.wallets.values() if w.user_id == user_id]
        
        assets = {}
        total_value_usd = 0.0
        
        # Mock prices - in production would fetch from market data
        mock_prices = {
            "BTC": 45000.0,
            "ETH": 3000.0,
            "BNB": 300.0,
            "USDT": 1.0,
            "USDC": 1.0,
            "MATIC": 1.5
        }
        
        for wallet in user_wallets:
            balance = wallet.balance + wallet.frozen_balance
            assets[wallet.currency] = balance
            price = mock_prices.get(wallet.currency, 1.0)
            total_value_usd += balance * price
        
        total_value_btc = total_value_usd / mock_prices.get("BTC", 45000.0)
        
        portfolio = Portfolio(
            user_id=user_id,
            total_value_usd=total_value_usd,
            total_value_btc=total_value_btc,
            assets=assets,
            daily_change=0.0,  # Would calculate from historical data
            daily_change_percent=0.0,
            last_updated=datetime.utcnow()
        )
        
        return portfolio

user_access = UserAccessSystem()

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> User:
    """Get current user from token"""
    token = credentials.credentials
    user_id = user_access.sessions.get(token)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    user = user_access.users.get(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    return user

@app.get("/")
async def root():
    return {
        "service": "Complete User Access System",
        "account_tiers": [tier.value for tier in AccountTier],
        "verification_statuses": [status.value for status in VerificationStatus],
        "status": "operational"
    }

@app.post("/auth/register")
async def register_user(
    username: str,
    email: str,
    phone: str,
    password: str,
    referral_code: Optional[str] = None
):
    """Register new user"""
    try:
        # Check if user already exists
        existing_user = next((u for u in user_access.users.values() if u.email == email or u.username == username), None)
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        import hashlib
        
        user_id = user_access.generate_user_id()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            phone=phone,
            password_hash=password_hash,
            account_tier=AccountTier.BASIC,
            verification_status=VerificationStatus.PENDING,
            is_active=True,
            two_factor_enabled=False,
            created_at=datetime.utcnow(),
            last_login=None,
            api_key=None,
            referral_code=referral_code
        )
        
        user_access.users[user_id] = user
        
        # Create default wallets for popular currencies
        default_currencies = [
            ("BTC", "bitcoin"),
            ("ETH", "ethereum"),
            ("USDT", "ethereum"),
            ("USDC", "ethereum")
        ]
        
        for currency, network in default_currencies:
            wallet_id = f"wallet_{user_id}_{currency}_{network}"
            address = user_access.generate_wallet_address(currency, network)
            
            wallet = Wallet(
                wallet_id=wallet_id,
                user_id=user_id,
                currency=currency,
                network=network,
                address=address,
                balance=0.0,
                frozen_balance=0.0,
                created_at=datetime.utcnow()
            )
            
            user_access.wallets[wallet_id] = wallet
        
        return {
            "user_id": user_id,
            "username": username,
            "email": email,
            "account_tier": AccountTier.BASIC.value,
            "verification_status": VerificationStatus.PENDING.value,
            "message": "User registered successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/login")
async def login_user(email: str, password: str, two_factor_code: Optional[str] = None):
    """User login"""
    try:
        import hashlib
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        user = next((u for u in user_access.users.values() if u.email == email and u.password_hash == password_hash), None)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if user.two_factor_enabled and not two_factor_code:
            raise HTTPException(status_code=400, detail="2FA code required")
        
        # Generate session token
        import uuid
        token = str(uuid.uuid4())
        user_access.sessions[token] = user.user_id
        
        user.last_login = datetime.utcnow()
        
        return {
            "token": token,
            "user_id": user.user_id,
            "username": user.username,
            "account_tier": user.account_tier.value,
            "verification_status": user.verification_status.value,
            "two_factor_enabled": user.two_factor_enabled
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/logout")
async def logout_user(current_user: User = Depends(get_current_user)):
    """User logout"""
    try:
        # Remove session token
        tokens_to_remove = [token for token, user_id in user_access.sessions.items() if user_id == current_user.user_id]
        for token in tokens_to_remove:
            del user_access.sessions[token]
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/kyc/submit")
async def submit_kyc(
    document_type: str,
    document_number: str,
    front_image_url: str,
    back_image_url: Optional[str],
    selfie_url: str,
    current_user: User = Depends(get_current_user)
):
    """Submit KYC documents"""
    try:
        if current_user.verification_status != VerificationStatus.PENDING:
            raise HTTPException(status_code=400, detail="KYC already submitted or verified")
        
        document_id = f"kyc_{current_user.user_id}_{int(datetime.utcnow().timestamp())}"
        
        kyc_doc = KYCDocument(
            document_id=document_id,
            user_id=current_user.user_id,
            document_type=document_type,
            document_number=document_number,
            front_image_url=front_image_url,
            back_image_url=back_image_url,
            selfie_url=selfie_url,
            status=VerificationStatus.PENDING,
            submitted_at=datetime.utcnow(),
            reviewed_at=None,
            rejection_reason=None
        )
        
        user_access.kyc_documents[document_id] = kyc_doc
        
        return {
            "document_id": document_id,
            "status": VerificationStatus.PENDING.value,
            "message": "KYC documents submitted successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kyc/status")
async def get_kyc_status(current_user: User = Depends(get_current_user)):
    """Get KYC status"""
    user_kyc = [doc for doc in user_access.kyc_documents.values() if doc.user_id == current_user.user_id]
    
    if not user_kyc:
        return {"status": "not_submitted", "documents": []}
    
    latest_kyc = max(user_kyc, key=lambda x: x.submitted_at)
    
    return {
        "status": latest_kyc.status.value,
        "document_type": latest_kyc.document_type,
        "submitted_at": latest_kyc.submitted_at,
        "rejection_reason": latest_kyc.rejection_reason
    }

@app.get("/portfolio")
async def get_portfolio(current_user: User = Depends(get_current_user)):
    """Get user portfolio"""
    portfolio = user_access.calculate_portfolio_value(current_user.user_id)
    return {"portfolio": portfolio}

@app.get("/wallets")
async def get_wallets(current_user: User = Depends(get_current_user)):
    """Get user wallets"""
    user_wallets = [w for w in user_access.wallets.values() if w.user_id == current_user.user_id]
    return {"wallets": user_wallets}

@app.post("/orders")
async def place_order(
    symbol: str,
    order_type: OrderType,
    order_side: OrderSide,
    amount: float,
    price: Optional[float] = None,
    current_user: User = Depends(get_current_user)
):
    """Place trading order"""
    try:
        if current_user.account_tier == AccountTier.BASIC:
            raise HTTPException(status_code=403, detail="KYC verification required for trading")
        
        order_id = f"order_{current_user.user_id}_{int(datetime.utcnow().timestamp())}"
        
        order = Order(
            order_id=order_id,
            user_id=current_user.user_id,
            symbol=symbol,
            order_type=order_type,
            order_side=order_side,
            amount=amount,
            price=price,
            filled_amount=0.0,
            remaining_amount=amount,
            average_price=0.0,
            status="pending",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        user_access.orders[order_id] = order
        
        return {
            "order_id": order_id,
            "symbol": symbol,
            "order_type": order_type.value,
            "order_side": order_side.value,
            "amount": amount,
            "price": price,
            "status": "pending",
            "message": "Order placed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders")
async def get_orders(
    status: Optional[str] = None,
    symbol: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get user orders"""
    user_orders = [o for o in user_access.orders.values() if o.user_id == current_user.user_id]
    
    if status:
        user_orders = [o for o in user_orders if o.status == status]
    
    if symbol:
        user_orders = [o for o in user_orders if o.symbol == symbol]
    
    # Sort by creation time and limit
    user_orders.sort(key=lambda x: x.created_at, reverse=True)
    user_orders = user_orders[:limit]
    
    return {"orders": user_orders}

@app.get("/transactions")
async def get_transactions(
    type: Optional[str] = None,
    currency: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get user transactions"""
    user_transactions = [t for t in user_access.transactions.values() if t.user_id == current_user.user_id]
    
    if type:
        user_transactions = [t for t in user_transactions if t.type == type]
    
    if currency:
        user_transactions = [t for t in user_transactions if t.currency == currency]
    
    # Sort by creation time and limit
    user_transactions.sort(key=lambda x: x.created_at, reverse=True)
    user_transactions = user_transactions[:limit]
    
    return {"transactions": user_transactions}

@app.post("/2fa/setup")
async def setup_2fa(current_user: User = Depends(get_current_user)):
    """Setup 2FA for user"""
    try:
        if current_user.two_factor_enabled:
            raise HTTPException(status_code=400, detail="2FA already enabled")
        
        import pyotp
        import qrcode
        import io
        import base64
        
        # Generate secret
        secret = pyotp.random_base32()
        
        # Generate QR code
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            current_user.email,
            issuer_name="TigerEx"
        )
        
        # Generate backup codes
        backup_codes = [f"{i:06d}" for i in range(100000, 100010)]
        
        # In production, would generate actual QR code
        qr_code_url = "data:image/png;base64,mock_qr_code_data"
        
        return {
            "secret_key": secret,
            "backup_codes": backup_codes,
            "qr_code_url": qr_code_url,
            "message": "2FA setup initiated"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/2fa/verify")
async def verify_2fa(secret: str, code: str, current_user: User = Depends(get_current_user)):
    """Verify and enable 2FA"""
    try:
        import pyotp
        
        totp = pyotp.TOTP(secret)
        
        if not totp.verify(code):
            raise HTTPException(status_code=400, detail("Invalid verification code"))
        
        # Update user
        user = user_access.users.get(current_user.user_id)
        user.two_factor_enabled = True
        
        return {
            "message": "2FA enabled successfully",
            "two_factor_enabled": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get user profile"""
    # Remove sensitive data
    user_data = current_user.dict()
    user_data.pop("password_hash", None)
    
    return {"profile": user_data}

@app.put("/profile")
async def update_profile(
    username: Optional[str] = None,
    phone: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Update user profile"""
    try:
        if username and username != current_user.username:
            # Check if username already exists
            existing = next((u for u in user_access.users.values() if u.username == username and u.user_id != current_user.user_id), None)
            if existing:
                raise HTTPException(status_code=400, detail="Username already exists")
            current_user.username = username
        
        if phone:
            current_user.phone = phone
        
        return {"message": "Profile updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trading/pairs")
async def get_trading_pairs():
    """Get available trading pairs"""
    # Mock trading pairs - in production would fetch from trading engine
    pairs = [
        {"symbol": "BTC/USDT", "base": "BTC", "quote": "USDT", "price": 45000.0},
        {"symbol": "ETH/USDT", "base": "ETH", "quote": "USDT", "price": 3000.0},
        {"symbol": "BNB/USDT", "base": "BNB", "quote": "USDT", "price": 300.0},
        {"symbol": "ETH/BTC", "base": "ETH", "quote": "BTC", "price": 0.067},
    ]
    
    return {"trading_pairs": pairs}

@app.get("/market/ticker/{symbol}")
async def get_ticker(symbol: str):
    """Get ticker for specific symbol"""
    # Mock ticker data
    ticker_data = {
        "symbol": symbol,
        "price": 45000.0 if "BTC" in symbol else 3000.0,
        "change_24h": 2.5,
        "volume_24h": 1000000.0,
        "high_24h": 46000.0,
        "low_24h": 44000.0
    }
    
    return {"ticker": ticker_data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)