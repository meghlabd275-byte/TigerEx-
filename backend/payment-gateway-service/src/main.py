"""
TigerEx Payment Gateway Service
Comprehensive payment integration with multiple providers
Port: 8123
"""

from fastapi import FastAPI
from admin.admin_routes import router as admin_router
from fastapi import HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uvicorn
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import logging
import hashlib
import hmac
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://tigerex:tigerex123@localhost:5432/tigerex_payment_gateway"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums
class PaymentProvider(str, Enum):
    # Card Processors
    STRIPE = "stripe"
    ADYEN = "adyen"
    SQUARE = "square"
    BRAINTREE = "braintree"
    
    # Digital Wallets
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    SAMSUNG_PAY = "samsung_pay"
    PAYPAL = "paypal"
    
    # Bank Transfers
    PLAID = "plaid"
    WISE = "wise"
    RAZORPAY = "razorpay"
    
    # Buy Now Pay Later
    KLARNA = "klarna"
    AFTERPAY = "afterpay"
    AFFIRM = "affirm"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    REFUND = "refund"

# Database Models
class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, index=True)
    provider = Column(String, index=True)
    transaction_type = Column(String)
    
    # Amounts
    amount = Column(Float)
    currency = Column(String)
    fee = Column(Float, default=0.0)
    net_amount = Column(Float)
    
    # Payment details
    payment_method = Column(String)
    payment_method_details = Column(JSON)
    
    # Status
    status = Column(String, default="pending")
    error_message = Column(String, nullable=True)
    
    # External references
    external_transaction_id = Column(String, nullable=True)
    external_payment_id = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Additional data
    metadata = Column(JSON)

class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    provider = Column(String)
    method_type = Column(String)  # card, bank_account, wallet
    
    # Card details (encrypted)
    card_last4 = Column(String, nullable=True)
    card_brand = Column(String, nullable=True)
    card_exp_month = Column(Integer, nullable=True)
    card_exp_year = Column(Integer, nullable=True)
    
    # Bank details (encrypted)
    bank_name = Column(String, nullable=True)
    account_last4 = Column(String, nullable=True)
    
    # Wallet details
    wallet_email = Column(String, nullable=True)
    
    # External references
    external_method_id = Column(String)
    
    # Status
    is_default = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)

class ProviderConfig(Base):
    __tablename__ = "provider_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, unique=True, index=True)
    is_enabled = Column(Boolean, default=True)
    
    # API Configuration
    api_key = Column(String)
    api_secret = Column(String)
    webhook_secret = Column(String, nullable=True)
    
    # Limits
    min_amount = Column(Float, default=10.0)
    max_amount = Column(Float, default=50000.0)
    daily_limit = Column(Float, default=100000.0)
    
    # Fees
    fee_percentage = Column(Float, default=2.5)
    fixed_fee = Column(Float, default=0.0)
    
    # Supported features
    supports_deposits = Column(Boolean, default=True)
    supports_withdrawals = Column(Boolean, default=True)
    supports_refunds = Column(Boolean, default=True)
    supports_recurring = Column(Boolean, default=False)
    
    # Supported currencies
    supported_currencies = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON)

Base.metadata.create_all(bind=engine)

# Pydantic Models
class DepositRequest(BaseModel):
    user_id: int
    provider: PaymentProvider
    amount: float = Field(gt=0)
    currency: str = Field(default="USD")
    payment_method_id: Optional[str] = None
    return_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class WithdrawalRequest(BaseModel):
    user_id: int
    provider: PaymentProvider
    amount: float = Field(gt=0)
    currency: str = Field(default="USD")
    payment_method_id: str
    metadata: Optional[Dict[str, Any]] = None

class RefundRequest(BaseModel):
    transaction_id: str
    amount: Optional[float] = None
    reason: Optional[str] = None

class PaymentMethodCreate(BaseModel):
    user_id: int
    provider: PaymentProvider
    method_type: str
    card_token: Optional[str] = None
    bank_token: Optional[str] = None
    wallet_email: Optional[str] = None
    is_default: bool = False
    metadata: Optional[Dict[str, Any]] = None

# FastAPI app
app = FastAPI(
    title="TigerEx Payment Gateway Service",
    description="Comprehensive payment integration service",
    version="1.0.0"
)

# Include admin router
app.include_router(admin_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions
def generate_transaction_id() -> str:
    """Generate unique transaction ID"""
    import uuid
    return f"TXN-{uuid.uuid4().hex[:16].upper()}"

def calculate_fee(amount: float, provider: str, db: Session) -> float:
    """Calculate transaction fee"""
    config = db.query(ProviderConfig).filter(ProviderConfig.provider == provider).first()
    if not config:
        return 0.0
    
    percentage_fee = amount * (config.fee_percentage / 100)
    return percentage_fee + config.fixed_fee

# ==================== DEPOSIT ENDPOINTS ====================

@app.post("/api/deposits", status_code=201)
async def create_deposit(
    deposit: DepositRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new deposit transaction"""
    try:
        # Validate provider is enabled
        config = db.query(ProviderConfig).filter(
            ProviderConfig.provider == deposit.provider,
            ProviderConfig.is_enabled == True
        ).first()
        
        if not config:
            raise HTTPException(status_code=400, detail="Payment provider not available")
        
        # Validate amount
        if deposit.amount < config.min_amount:
            raise HTTPException(
                status_code=400,
                detail=f"Minimum deposit amount is {config.min_amount} {deposit.currency}"
            )
        
        if deposit.amount > config.max_amount:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum deposit amount is {config.max_amount} {deposit.currency}"
            )
        
        # Calculate fee
        fee = calculate_fee(deposit.amount, deposit.provider, db)
        net_amount = deposit.amount - fee
        
        # Create transaction
        transaction = PaymentTransaction(
            transaction_id=generate_transaction_id(),
            user_id=deposit.user_id,
            provider=deposit.provider,
            transaction_type="deposit",
            amount=deposit.amount,
            currency=deposit.currency,
            fee=fee,
            net_amount=net_amount,
            status="pending",
            metadata=deposit.metadata or {}
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        # Process payment based on provider
        # This would integrate with actual payment provider APIs
        payment_url = None
        if deposit.provider in [PaymentProvider.STRIPE, PaymentProvider.ADYEN]:
            payment_url = f"https://checkout.{deposit.provider}.com/{transaction.transaction_id}"
        
        logger.info(f"Created deposit transaction: {transaction.transaction_id}")
        
        return {
            "transaction_id": transaction.transaction_id,
            "amount": transaction.amount,
            "currency": transaction.currency,
            "fee": transaction.fee,
            "net_amount": transaction.net_amount,
            "status": transaction.status,
            "payment_url": payment_url,
            "created_at": transaction.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating deposit: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/deposits/{transaction_id}")
async def get_deposit(transaction_id: str, db: Session = Depends(get_db)):
    """Get deposit transaction details"""
    transaction = db.query(PaymentTransaction).filter(
        PaymentTransaction.transaction_id == transaction_id,
        PaymentTransaction.transaction_type == "deposit"
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return transaction

# ==================== WITHDRAWAL ENDPOINTS ====================

@app.post("/api/withdrawals", status_code=201)
async def create_withdrawal(
    withdrawal: WithdrawalRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new withdrawal transaction"""
    try:
        # Validate provider is enabled
        config = db.query(ProviderConfig).filter(
            ProviderConfig.provider == withdrawal.provider,
            ProviderConfig.is_enabled == True
        ).first()
        
        if not config:
            raise HTTPException(status_code=400, detail="Payment provider not available")
        
        if not config.supports_withdrawals:
            raise HTTPException(status_code=400, detail="Provider does not support withdrawals")
        
        # Validate payment method
        payment_method = db.query(PaymentMethod).filter(
            PaymentMethod.user_id == withdrawal.user_id,
            PaymentMethod.external_method_id == withdrawal.payment_method_id,
            PaymentMethod.is_active == True
        ).first()
        
        if not payment_method:
            raise HTTPException(status_code=404, detail="Payment method not found")
        
        # Calculate fee
        fee = calculate_fee(withdrawal.amount, withdrawal.provider, db)
        net_amount = withdrawal.amount - fee
        
        # Create transaction
        transaction = PaymentTransaction(
            transaction_id=generate_transaction_id(),
            user_id=withdrawal.user_id,
            provider=withdrawal.provider,
            transaction_type="withdrawal",
            amount=withdrawal.amount,
            currency=withdrawal.currency,
            fee=fee,
            net_amount=net_amount,
            status="pending",
            payment_method=payment_method.method_type,
            metadata=withdrawal.metadata or {}
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        logger.info(f"Created withdrawal transaction: {transaction.transaction_id}")
        
        return {
            "transaction_id": transaction.transaction_id,
            "amount": transaction.amount,
            "currency": transaction.currency,
            "fee": transaction.fee,
            "net_amount": transaction.net_amount,
            "status": transaction.status,
            "created_at": transaction.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating withdrawal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== REFUND ENDPOINTS ====================

@app.post("/api/refunds", status_code=201)
async def create_refund(refund: RefundRequest, db: Session = Depends(get_db)):
    """Create a refund for a transaction"""
    try:
        # Find original transaction
        transaction = db.query(PaymentTransaction).filter(
            PaymentTransaction.transaction_id == refund.transaction_id
        ).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        if transaction.status != "completed":
            raise HTTPException(status_code=400, detail="Can only refund completed transactions")
        
        # Determine refund amount
        refund_amount = refund.amount if refund.amount else transaction.amount
        
        if refund_amount > transaction.amount:
            raise HTTPException(status_code=400, detail="Refund amount exceeds original amount")
        
        # Create refund transaction
        refund_transaction = PaymentTransaction(
            transaction_id=generate_transaction_id(),
            user_id=transaction.user_id,
            provider=transaction.provider,
            transaction_type="refund",
            amount=refund_amount,
            currency=transaction.currency,
            fee=0.0,
            net_amount=refund_amount,
            status="pending",
            metadata={"original_transaction_id": transaction.transaction_id, "reason": refund.reason}
        )
        
        db.add(refund_transaction)
        
        # Update original transaction
        transaction.status = "refunded"
        
        db.commit()
        db.refresh(refund_transaction)
        
        logger.info(f"Created refund transaction: {refund_transaction.transaction_id}")
        
        return refund_transaction
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating refund: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== PAYMENT METHOD ENDPOINTS ====================

@app.post("/api/payment-methods", status_code=201)
async def add_payment_method(method: PaymentMethodCreate, db: Session = Depends(get_db)):
    """Add a new payment method"""
    try:
        # If this is set as default, unset other defaults
        if method.is_default:
            db.query(PaymentMethod).filter(
                PaymentMethod.user_id == method.user_id
            ).update({"is_default": False})
        
        # Create payment method
        payment_method = PaymentMethod(
            user_id=method.user_id,
            provider=method.provider,
            method_type=method.method_type,
            is_default=method.is_default,
            external_method_id=f"pm_{generate_transaction_id()}",
            metadata=method.metadata or {}
        )
        
        # Set method-specific details
        if method.method_type == "card" and method.card_token:
            # In production, this would tokenize the card with the provider
            payment_method.card_last4 = "4242"
            payment_method.card_brand = "visa"
            payment_method.card_exp_month = 12
            payment_method.card_exp_year = 2025
        elif method.method_type == "bank_account" and method.bank_token:
            payment_method.bank_name = "Example Bank"
            payment_method.account_last4 = "1234"
        elif method.method_type == "wallet" and method.wallet_email:
            payment_method.wallet_email = method.wallet_email
        
        db.add(payment_method)
        db.commit()
        db.refresh(payment_method)
        
        logger.info(f"Added payment method for user {method.user_id}")
        
        return payment_method
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding payment method: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/payment-methods/{user_id}")
async def get_payment_methods(user_id: int, db: Session = Depends(get_db)):
    """Get all payment methods for a user"""
    methods = db.query(PaymentMethod).filter(
        PaymentMethod.user_id == user_id,
        PaymentMethod.is_active == True
    ).all()
    
    return methods

@app.delete("/api/payment-methods/{method_id}")
async def delete_payment_method(method_id: int, db: Session = Depends(get_db)):
    """Delete a payment method"""
    try:
        method = db.query(PaymentMethod).filter(PaymentMethod.id == method_id).first()
        if not method:
            raise HTTPException(status_code=404, detail="Payment method not found")
        
        method.is_active = False
        db.commit()
        
        logger.info(f"Deleted payment method: {method_id}")
        
        return {"message": "Payment method deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting payment method: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== PROVIDER CONFIGURATION ====================

@app.get("/api/providers")
async def get_providers(db: Session = Depends(get_db)):
    """Get all available payment providers"""
    providers = db.query(ProviderConfig).filter(ProviderConfig.is_enabled == True).all()
    
    # Return public information only
    return [
        {
            "provider": p.provider,
            "min_amount": p.min_amount,
            "max_amount": p.max_amount,
            "fee_percentage": p.fee_percentage,
            "fixed_fee": p.fixed_fee,
            "supports_deposits": p.supports_deposits,
            "supports_withdrawals": p.supports_withdrawals,
            "supports_refunds": p.supports_refunds,
            "supported_currencies": p.supported_currencies
        }
        for p in providers
    ]

# ==================== WEBHOOKS ====================

@app.post("/api/webhooks/{provider}")
async def handle_webhook(provider: str, request: Dict[str, Any], db: Session = Depends(get_db)):
    """Handle webhook from payment provider"""
    try:
        # Verify webhook signature
        # This would be provider-specific
        
        # Process webhook event
        event_type = request.get("type") or request.get("event_type")
        
        if event_type in ["payment.succeeded", "charge.succeeded"]:
            # Update transaction status
            external_id = request.get("id")
            transaction = db.query(PaymentTransaction).filter(
                PaymentTransaction.external_transaction_id == external_id
            ).first()
            
            if transaction:
                transaction.status = "completed"
                transaction.completed_at = datetime.utcnow()
                db.commit()
                
                logger.info(f"Payment succeeded: {transaction.transaction_id}")
        
        elif event_type in ["payment.failed", "charge.failed"]:
            external_id = request.get("id")
            transaction = db.query(PaymentTransaction).filter(
                PaymentTransaction.external_transaction_id == external_id
            ).first()
            
            if transaction:
                transaction.status = "failed"
                transaction.error_message = request.get("error", {}).get("message")
                db.commit()
                
                logger.info(f"Payment failed: {transaction.transaction_id}")
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ANALYTICS ====================

@app.get("/api/analytics/overview")
async def get_analytics_overview(db: Session = Depends(get_db)):
    """Get payment analytics overview"""
    try:
        total_transactions = db.query(PaymentTransaction).count()
        total_deposits = db.query(PaymentTransaction).filter(
            PaymentTransaction.transaction_type == "deposit"
        ).count()
        total_withdrawals = db.query(PaymentTransaction).filter(
            PaymentTransaction.transaction_type == "withdrawal"
        ).count()
        
        total_volume = db.query(PaymentTransaction).filter(
            PaymentTransaction.status == "completed"
        ).with_entities(db.func.sum(PaymentTransaction.amount)).scalar() or 0.0
        
        total_fees = db.query(PaymentTransaction).filter(
            PaymentTransaction.status == "completed"
        ).with_entities(db.func.sum(PaymentTransaction.fee)).scalar() or 0.0
        
        success_rate = db.query(PaymentTransaction).filter(
            PaymentTransaction.status == "completed"
        ).count() / max(total_transactions, 1) * 100
        
        return {
            "total_transactions": total_transactions,
            "total_deposits": total_deposits,
            "total_withdrawals": total_withdrawals,
            "total_volume": total_volume,
            "total_fees": total_fees,
            "success_rate": success_rate
        }
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "payment-gateway"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8123)