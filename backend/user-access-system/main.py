"""
TigerEx User Access System
Complete implementation with user registration, KYC, trading interface, and portfolio management
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import hashlib
import secrets
import re
from decimal import Decimal

class UserStatus(Enum):
    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    CLOSED = "closed"

class KYCStatus(Enum):
    NOT_SUBMITTED = "not_submitted"
    PENDING_REVIEW = "pending_review"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    DOCUMENTS_REQUIRED = "documents_required"

class VerificationLevel(Enum):
    LEVEL_0 = 0  # Unverified
    LEVEL_1 = 1  # Basic info
    LEVEL_2 = 2  # ID verified
    LEVEL_3 = 3  # Address verified
    LEVEL_4 = 4  # Enhanced due diligence

class OrderStatus(Enum):
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    STOP_LIMIT = "stop_limit"
    TAKE_PROFIT = "take_profit"

@dataclass
class User:
    id: str
    username: str
    email: str
    password_hash: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    country: Optional[str]
    status: UserStatus = UserStatus.PENDING_VERIFICATION
    kyc_status: KYCStatus = KYCStatus.NOT_SUBMITTED
    verification_level: VerificationLevel = VerificationLevel.LEVEL_0
    is_email_verified: bool = False
    is_phone_verified: bool = False
    two_factor_enabled: bool = False
    two_factor_secret: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    login_count: int = 0
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    referral_code: Optional[str] = None
    referred_by: Optional[str] = None
    api_keys: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)

@dataclass
class KYCDocument:
    id: str
    user_id: str
    document_type: str  # "passport", "id_card", "driving_license", "proof_of_address", etc.
    document_number: Optional[str]
    front_image_url: Optional[str]
    back_image_url: Optional[str]
    selfie_image_url: Optional[str]
    expiry_date: Optional[datetime]
    issued_date: Optional[datetime]
    issuing_country: Optional[str]
    status: str = "pending"
    submitted_at: datetime = field(default_factory=datetime.now)
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    rejection_reason: Optional[str] = None

@dataclass
class UserWallet:
    id: str
    user_id: str
    cryptocurrency: str
    address: str
    balance: float = 0.0
    frozen_balance: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

@dataclass
class Order:
    id: str
    user_id: str
    symbol: str
    side: str  # "buy" or "sell"
    order_type: OrderType
    amount: float
    price: Optional[float]  # None for market orders
    filled_amount: float = 0.0
    average_price: float = 0.0
    status: OrderStatus = OrderStatus.OPEN
    fee: float = 0.0
    fee_rate: float = 0.001
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    stop_price: Optional[float] = None
    trailing_percentage: Optional[float] = None

@dataclass
class Trade:
    id: str
    order_id: str
    user_id: str
    symbol: str
    side: str
    amount: float
    price: float
    fee: float
    fee_rate: float
    created_at: datetime = field(default_factory=datetime.now)
    maker_order_id: Optional[str] = None
    taker_order_id: Optional[str] = None

@dataclass
class Portfolio:
    user_id: str
    total_value_usd: float = 0.0
    total_value_btc: float = 0.0
    total_value_eth: float = 0.0
    24h_change_usd: float = 0.0
    24h_change_percentage: float = 0.0
    assets: Dict[str, Dict[str, float]] = field(default_factory=dict)  # symbol -> {amount, value_usd, percentage}
    last_updated: datetime = field(default_factory=datetime.now)

class UserAccessSystem:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.users: Dict[str, User] = {}
        self.kyc_documents: Dict[str, KYCDocument] = {}
        self.user_wallets: Dict[str, UserWallet] = {}
        self.orders: Dict[str, Order] = {}
        self.trades: List[Trade] = []
        self.portfolios: Dict[str, Portfolio] = {}
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
        self.password_reset_tokens: Dict[str, Dict[str, Any]] = {}
        self.email_verification_tokens: Dict[str, str] = {}
        self.referral_codes: Dict[str, str] = {}
        
        # Trading pairs (would be loaded from trading system)
        self.trading_pairs: Dict[str, Dict[str, Any]] = {
            "BTC-USDT": {"base": "BTC", "quote": "USDT", "min_amount": 0.0001, "price_precision": 2},
            "ETH-USDT": {"base": "ETH", "quote": "USDT", "min_amount": 0.001, "price_precision": 2},
            "BNB-USDT": {"base": "BNB", "quote": "USDT", "min_amount": 0.01, "price_precision": 4},
        }

    def _hash_password(self, password: str) -> str:
        """Hash a password"""
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${password_hash.hex()}"

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        try:
            salt, hash_value = password_hash.split('$')
            computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return computed_hash.hex() == hash_value
        except:
            return False

    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def _validate_password(self, password: str) -> Tuple[bool, str]:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is valid"

    def _generate_referral_code(self) -> str:
        """Generate a unique referral code"""
        while True:
            code = ''.join(secrets.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(8))
            if code not in self.referral_codes.values():
                return code

    def register_user(self, username: str, email: str, password: str, first_name: Optional[str] = None, last_name: Optional[str] = None, referral_code: Optional[str] = None) -> Dict[str, Any]:
        """Register a new user"""
        # Validate input
        if not self._validate_email(email):
            raise ValueError("Invalid email format")
        
        valid, message = self._validate_password(password)
        if not valid:
            raise ValueError(message)
        
        # Check if username or email already exists
        for user in self.users.values():
            if user.username == username:
                raise ValueError("Username already exists")
            if user.email == email:
                raise ValueError("Email already registered")
        
        # Verify referral code if provided
        referred_by = None
        if referral_code:
            for user_id, user_referral_code in self.referral_codes.items():
                if user_referral_code == referral_code:
                    referred_by = user_id
                    break
            else:
                raise ValueError("Invalid referral code")
        
        # Create new user
        user_id = str(uuid.uuid4())
        password_hash = self._hash_password(password)
        user_referral_code = self._generate_referral_code()
        
        new_user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            referral_code=user_referral_code,
            referred_by=referred_by,
            status=UserStatus.PENDING_VERIFICATION,
            preferences={
                "language": "en",
                "timezone": "UTC",
                "theme": "light",
                "notifications": {
                    "email": True,
                    "push": True,
                    "trading": True,
                    "security": True
                }
            }
        )
        
        self.users[user_id] = new_user
        self.referral_codes[user_id] = user_referral_code
        
        # Generate email verification token
        verification_token = secrets.token_urlsafe(32)
        self.email_verification_tokens[user_id] = verification_token
        
        self.logger.info(f"User registered: {username} ({email})")
        
        return {
            "user_id": user_id,
            "username": username,
            "email": email,
            "message": "Registration successful. Please verify your email.",
            "email_verification_token": verification_token
        }

    def authenticate_user(self, username: str, password: str, ip_address: str, user_agent: str) -> Optional[str]:
        """Authenticate user and create session"""
        # Find user by username or email
        user = None
        for u in self.users.values():
            if u.username == username or u.email == username:
                user = u
                break
        
        if not user:
            return None
        
        # Check if account is locked
        if user.locked_until and datetime.now() < user.locked_until:
            return None
        
        # Verify password
        if not self._verify_password(password, user.password_hash):
            user.failed_login_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.now() + timedelta(minutes=30)
            
            return None
        
        # Check account status
        if user.status != UserStatus.ACTIVE:
            return None
        
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.now()
        user.login_count += 1
        
        # Create session
        session_id = secrets.token_urlsafe(32)
        self.user_sessions[session_id] = {
            "user_id": user.id,
            "created_at": datetime.now(),
            "ip_address": ip_address,
            "user_agent": user_agent,
            "last_activity": datetime.now()
        }
        
        return session_id

    def verify_email(self, token: str) -> bool:
        """Verify user email"""
        for user_id, verification_token in self.email_verification_tokens.items():
            if verification_token == token:
                if user_id in self.users:
                    self.users[user_id].is_email_verified = True
                    del self.email_verification_tokens[user_id]
                    
                    # Update user status if email is verified
                    if self.users[user_id].status == UserStatus.PENDING_VERIFICATION:
                        self.users[user_id].status = UserStatus.ACTIVE
                    
                    return True
        return False

    def submit_kyc_documents(self, user_id: str, document_type: str, document_data: Dict[str, Any]) -> str:
        """Submit KYC documents for verification"""
        if user_id not in self.users:
            raise ValueError("User not found")
        
        user = self.users[user_id]
        
        # Check if KYC is already approved
        if user.kyc_status == KYCStatus.APPROVED:
            raise ValueError("KYC already approved")
        
        # Create KYC document
        document_id = str(uuid.uuid4())
        kyc_document = KYCDocument(
            id=document_id,
            user_id=user_id,
            document_type=document_type,
            document_number=document_data.get("document_number"),
            front_image_url=document_data.get("front_image_url"),
            back_image_url=document_data.get("back_image_url"),
            selfie_image_url=document_data.get("selfie_image_url"),
            expiry_date=datetime.fromisoformat(document_data["expiry_date"]) if document_data.get("expiry_date") else None,
            issued_date=datetime.fromisoformat(document_data["issued_date"]) if document_data.get("issued_date") else None,
            issuing_country=document_data.get("issuing_country"),
            status="pending"
        )
        
        self.kyc_documents[document_id] = kyc_document
        
        # Update user KYC status
        user.kyc_status = KYCStatus.PENDING_REVIEW
        
        self.logger.info(f"KYC document submitted for user {user.username}")
        
        return document_id

    def create_user_wallet(self, user_id: str, cryptocurrency: str) -> str:
        """Create a wallet for a user"""
        if user_id not in self.users:
            raise ValueError("User not found")
        
        wallet_id = str(uuid.uuid4())
        address = f"{cryptocurrency.lower()}_{secrets.token_urlsafe(32)}"
        
        wallet = UserWallet(
            id=wallet_id,
            user_id=user_id,
            cryptocurrency=cryptocurrency,
            address=address
        )
        
        self.user_wallets[wallet_id] = wallet
        
        self.logger.info(f"Created wallet for user {user_id}: {cryptocurrency}")
        
        return wallet_id

    def get_user_wallets(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all wallets for a user"""
        wallets = []
        for wallet in self.user_wallets.values():
            if wallet.user_id == user_id:
                wallets.append({
                    "id": wallet.id,
                    "cryptocurrency": wallet.cryptocurrency,
                    "address": wallet.address,
                    "balance": wallet.balance,
                    "frozen_balance": wallet.frozen_balance,
                    "available_balance": wallet.balance - wallet.frozen_balance,
                    "created_at": wallet.created_at.isoformat(),
                    "is_active": wallet.is_active
                })
        
        return wallets

    def place_order(self, user_id: str, symbol: str, side: str, order_type: str, amount: float, price: Optional[float] = None, **kwargs) -> str:
        """Place a trading order"""
        if user_id not in self.users:
            raise ValueError("User not found")
        
        if symbol not in self.trading_pairs:
            raise ValueError("Trading pair not supported")
        
        user = self.users[user_id]
        
        # Check if user can trade
        if user.status != UserStatus.ACTIVE:
            raise ValueError("Account not active for trading")
        
        if user.kyc_status not in [KYCStatus.APPROVED, KYCStatus.NOT_SUBMITTED]:
            raise ValueError("KYC verification required for trading")
        
        # Validate order
        if side not in ["buy", "sell"]:
            raise ValueError("Invalid side")
        
        order_type_enum = OrderType(order_type)
        
        if order_type_enum == OrderType.LIMIT and price is None:
            raise ValueError("Price required for limit orders")
        
        # Create order
        order_id = str(uuid.uuid4())
        order = Order(
            id=order_id,
            user_id=user_id,
            symbol=symbol,
            side=side,
            order_type=order_type_enum,
            amount=amount,
            price=price,
            fee_rate=0.001,  # Default fee rate
            expires_at=kwargs.get("expires_at"),
            stop_price=kwargs.get("stop_price"),
            trailing_percentage=kwargs.get("trailing_percentage")
        )
        
        self.orders[order_id] = order
        
        self.logger.info(f"Order placed: {user.username} {side} {amount} {symbol} at {price}")
        
        # Simulate order execution (in real system, this would interact with trading engine)
        self._simulate_order_execution(order)
        
        return order_id

    def _simulate_order_execution(self, order: Order):
        """Simulate order execution for demonstration"""
        # Simulate immediate execution for market orders
        if order.order_type == OrderType.MARKET:
            # Mock execution price
            if order.price is None:
                order.price = 50000 if "BTC" in order.symbol else 3000 if "ETH" in order.symbol else 100
            
            order.filled_amount = order.amount
            order.average_price = order.price
            order.fee = order.amount * order.price * order.fee_rate
            order.status = OrderStatus.FILLED
            order.updated_at = datetime.now()
            
            # Create trade record
            trade = Trade(
                id=str(uuid.uuid4()),
                order_id=order.id,
                user_id=order.user_id,
                symbol=order.symbol,
                side=order.side,
                amount=order.amount,
                price=order.price,
                fee=order.fee,
                fee_rate=order.fee_rate
            )
            
            self.trades.append(trade)

    def get_user_orders(self, user_id: str, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user orders"""
        orders = []
        
        for order in self.orders.values():
            if order.user_id == user_id:
                if status is None or order.status.value == status:
                    order_data = {
                        "id": order.id,
                        "symbol": order.symbol,
                        "side": order.side,
                        "type": order.order_type.value,
                        "amount": order.amount,
                        "filled_amount": order.filled_amount,
                        "price": order.price,
                        "average_price": order.average_price,
                        "status": order.status.value,
                        "fee": order.fee,
                        "created_at": order.created_at.isoformat(),
                        "updated_at": order.updated_at.isoformat()
                    }
                    orders.append(order_data)
        
        # Sort by created_at (newest first)
        orders.sort(key=lambda x: x["created_at"], reverse=True)
        
        return orders[:limit]

    def get_user_trades(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get user trades"""
        trades = []
        
        for trade in self.trades:
            if trade.user_id == user_id:
                trade_data = {
                    "id": trade.id,
                    "order_id": trade.order_id,
                    "symbol": trade.symbol,
                    "side": trade.side,
                    "amount": trade.amount,
                    "price": trade.price,
                    "fee": trade.fee,
                    "created_at": trade.created_at.isoformat()
                }
                trades.append(trade_data)
        
        # Sort by created_at (newest first)
        trades.sort(key=lambda x: x["created_at"], reverse=True)
        
        return trades[:limit]

    def calculate_portfolio(self, user_id: str) -> Portfolio:
        """Calculate user portfolio"""
        if user_id not in self.users:
            raise ValueError("User not found")
        
        # Get user wallets
        wallets = [w for w in self.user_wallets.values() if w.user_id == user_id]
        
        # Calculate portfolio values
        assets = {}
        total_value_usd = 0.0
        
        for wallet in wallets:
            if wallet.balance > 0:
                # Mock prices (in real system, would get from price oracle)
                price = {
                    "BTC": 50000,
                    "ETH": 3000,
                    "USDT": 1,
                    "BNB": 300
                }.get(wallet.cryptocurrency, 1)
                
                value_usd = wallet.balance * price
                total_value_usd += value_usd
                
                assets[wallet.cryptocurrency] = {
                    "amount": wallet.balance,
                    "value_usd": value_usd,
                    "percentage": 0  # Will be calculated below
                }
        
        # Calculate percentages
        for symbol in assets:
            if total_value_usd > 0:
                assets[symbol]["percentage"] = (assets[symbol]["value_usd"] / total_value_usd) * 100
        
        # Create portfolio
        portfolio = Portfolio(
            user_id=user_id,
            total_value_usd=total_value_usd,
            total_value_btc=total_value_usd / 50000,  # Mock BTC price
            total_value_eth=total_value_usd / 3000,   # Mock ETH price
            assets=assets,
            last_updated=datetime.now()
        )
        
        self.portfolios[user_id] = portfolio
        
        return portfolio

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile"""
        if user_id not in self.users:
            raise ValueError("User not found")
        
        user = self.users[user_id]
        
        # Get portfolio
        portfolio = self.calculate_portfolio(user_id)
        
        # Get trading stats
        user_trades = [t for t in self.trades if t.user_id == user_id]
        total_trades = len(user_trades)
        total_volume = sum(t.amount * t.price for t in user_trades)
        total_fees = sum(t.fee for t in user_trades)
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "status": user.status.value,
            "kyc_status": user.kyc_status.value,
            "verification_level": user.verification_level.value,
            "is_email_verified": user.is_email_verified,
            "is_phone_verified": user.is_phone_verified,
            "two_factor_enabled": user.two_factor_enabled,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "login_count": user.login_count,
            "referral_code": user.referral_code,
            "portfolio": {
                "total_value_usd": portfolio.total_value_usd,
                "total_value_btc": portfolio.total_value_btc,
                "total_value_eth": portfolio.total_value_eth,
                "assets": portfolio.assets,
                "last_updated": portfolio.last_updated.isoformat()
            },
            "trading_stats": {
                "total_trades": total_trades,
                "total_volume": total_volume,
                "total_fees": total_fees
            }
        }

    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        if user_id not in self.users:
            return False
        
        self.users[user_id].preferences.update(preferences)
        return True

    def get_user_by_session(self, session_id: str) -> Optional[User]:
        """Get user by session ID"""
        if session_id not in self.user_sessions:
            return None
        
        session = self.user_sessions[session_id]
        user_id = session["user_id"]
        
        # Check session expiration (24 hours)
        if datetime.now() - session["created_at"] > timedelta(hours=24):
            del self.user_sessions[session_id]
            return None
        
        # Update last activity
        session["last_activity"] = datetime.now()
        
        return self.users.get(user_id)

# Initialize the user access system
user_system = UserAccessSystem()

# FastAPI endpoints
from fastapi import FastAPI, HTTPException, Depends, Request, Header, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

app = FastAPI(title="TigerEx User Access System API", version="1.0.0")
security = HTTPBearer()

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    referral_code: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class KYCDocumentRequest(BaseModel):
    document_type: str
    document_number: Optional[str] = None
    front_image_url: Optional[str] = None
    back_image_url: Optional[str] = None
    selfie_image_url: Optional[str] = None
    expiry_date: Optional[str] = None
    issued_date: Optional[str] = None
    issuing_country: Optional[str] = None

class OrderRequest(BaseModel):
    symbol: str
    side: str
    order_type: str
    amount: float
    price: Optional[float] = None
    expires_at: Optional[datetime] = None
    stop_price: Optional[float] = None
    trailing_percentage: Optional[float] = None

class PreferencesRequest(BaseModel):
    preferences: Dict[str, Any]

def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current user from session"""
    session_id = credentials.credentials
    user = user_system.get_user_by_session(session_id)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    return user

@app.post("/api/v1/auth/register")
async def register(request: Request, user_data: RegisterRequest):
    """User registration"""
    try:
        result = user_system.register_user(
            user_data.username,
            user_data.email,
            user_data.password,
            user_data.first_name,
            user_data.last_name,
            user_data.referral_code
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/auth/login")
async def login(request: Request, login_data: LoginRequest):
    """User login"""
    try:
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        session_id = user_system.authenticate_user(
            login_data.username,
            login_data.password,
            ip_address,
            user_agent
        )
        
        if not session_id:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        return {"session_id": session_id, "message": "Login successful"}
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/api/v1/auth/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """User logout"""
    # In a real implementation, you would invalidate the session
    return {"message": "Logout successful"}

@app.post("/api/v1/auth/verify-email")
async def verify_email(token: str):
    """Verify email address"""
    success = user_system.verify_email(token)
    
    if success:
        return {"message": "Email verified successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid verification token")

@app.post("/api/v1/kyc/submit")
async def submit_kyc_documents(
    request_data: KYCDocumentRequest,
    current_user: User = Depends(get_current_user)
):
    """Submit KYC documents"""
    try:
        document_data = request_data.dict(exclude_none=True)
        document_id = user_system.submit_kyc_documents(
            current_user.id,
            request_data.document_type,
            document_data
        )
        
        return {"document_id": document_id, "message": "KYC documents submitted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/wallets")
async def get_user_wallets(current_user: User = Depends(get_current_user)):
    """Get user wallets"""
    wallets = user_system.get_user_wallets(current_user.id)
    return {"wallets": wallets}

@app.post("/api/v1/wallets/{cryptocurrency}")
async def create_wallet(
    cryptocurrency: str,
    current_user: User = Depends(get_current_user)
):
    """Create new wallet"""
    try:
        wallet_id = user_system.create_user_wallet(current_user.id, cryptocurrency.upper())
        return {"wallet_id": wallet_id, "message": "Wallet created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/orders")
async def place_order(
    order_data: OrderRequest,
    current_user: User = Depends(get_current_user)
):
    """Place trading order"""
    try:
        order_id = user_system.place_order(
            current_user.id,
            order_data.symbol.upper(),
            order_data.side.lower(),
            order_data.order_type.lower(),
            order_data.amount,
            order_data.price,
            expires_at=order_data.expires_at,
            stop_price=order_data.stop_price,
            trailing_percentage=order_data.trailing_percentage
        )
        
        return {"order_id": order_id, "message": "Order placed successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/orders")
async def get_user_orders(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user)
):
    """Get user orders"""
    orders = user_system.get_user_orders(current_user.id, status, limit)
    return {"orders": orders}

@app.get("/api/v1/trades")
async def get_user_trades(
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user)
):
    """Get user trades"""
    trades = user_system.get_user_trades(current_user.id, limit)
    return {"trades": trades}

@app.get("/api/v1/portfolio")
async def get_portfolio(current_user: User = Depends(get_current_user)):
    """Get user portfolio"""
    portfolio = user_system.calculate_portfolio(current_user.id)
    
    return {
        "total_value_usd": portfolio.total_value_usd,
        "total_value_btc": portfolio.total_value_btc,
        "total_value_eth": portfolio.total_value_eth,
        "assets": portfolio.assets,
        "last_updated": portfolio.last_updated.isoformat()
    }

@app.get("/api/v1/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get user profile"""
    profile = user_system.get_user_profile(current_user.id)
    return profile

@app.put("/api/v1/profile/preferences")
async def update_preferences(
    request_data: PreferencesRequest,
    current_user: User = Depends(get_current_user)
):
    """Update user preferences"""
    success = user_system.update_user_preferences(current_user.id, request_data.preferences)
    
    if success:
        return {"message": "Preferences updated successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to update preferences")

@app.get("/api/v1/trading-pairs")
async def get_trading_pairs(current_user: User = Depends(get_current_user)):
    """Get available trading pairs"""
    return {"trading_pairs": user_system.trading_pairs}

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=8006)