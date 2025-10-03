import os
"""
TigerEx Enhanced Wallet Service
Complete wallet management with deposits, withdrawals, and balance tracking
"""

from fastapi import FastAPI
from admin.admin_routes import router as admin_router
, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from decimal import Decimal
import asyncpg
import structlog
from enum import Enum
import hashlib
import secrets

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

app = FastAPI(title="TigerEx Enhanced Wallet Service", version="1.0.0")

# Include admin router
app.include_router(admin_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection pool
db_pool: Optional[asyncpg.Pool] = None

# Enums
class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    TRADE = "trade"
    FEE = "fee"
    REWARD = "reward"
    REFUND = "refund"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WalletType(str, Enum):
    SPOT = "spot"
    FUTURES = "futures"
    MARGIN = "margin"
    EARN = "earn"
    FUNDING = "funding"

class WithdrawalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

# Models
class WalletBalance(BaseModel):
    wallet_id: int
    user_id: int
    currency: str
    wallet_type: str
    available_balance: Decimal
    locked_balance: Decimal
    total_balance: Decimal
    updated_at: datetime

class DepositRequest(BaseModel):
    user_id: int
    currency: str
    amount: Decimal = Field(..., gt=0)
    blockchain: str
    transaction_hash: str
    from_address: str
    to_address: str
    confirmations: int = 0

class WithdrawalRequest(BaseModel):
    user_id: int
    currency: str
    amount: Decimal = Field(..., gt=0)
    to_address: str
    blockchain: str
    wallet_type: WalletType = WalletType.SPOT
    two_fa_code: Optional[str] = None
    memo: Optional[str] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return v

class TransferRequest(BaseModel):
    user_id: int
    currency: str
    amount: Decimal = Field(..., gt=0)
    from_wallet_type: WalletType
    to_wallet_type: WalletType
    
    @validator('to_wallet_type')
    def validate_different_wallets(cls, v, values):
        if 'from_wallet_type' in values and v == values['from_wallet_type']:
            raise ValueError('Cannot transfer to the same wallet type')
        return v

class TransactionResponse(BaseModel):
    transaction_id: int
    user_id: int
    currency: str
    transaction_type: str
    amount: Decimal
    fee: Decimal
    status: str
    created_at: datetime

class WithdrawalResponse(BaseModel):
    withdrawal_id: int
    user_id: int
    currency: str
    amount: Decimal
    fee: Decimal
    to_address: str
    blockchain: str
    status: str
    transaction_hash: Optional[str]
    created_at: datetime

# Database functions
async def get_db():
    return db_pool

async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(
        host="localhost",
        port=5432,
        user="tigerex",
        password="tigerex_secure_password",
        database="tigerex_wallet",
        min_size=10,
        max_size=50
    )
    
    async with db_pool.acquire() as conn:
        # Create wallets table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS wallets (
                wallet_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                currency VARCHAR(20) NOT NULL,
                wallet_type VARCHAR(20) NOT NULL,
                available_balance DECIMAL(36, 18) DEFAULT 0,
                locked_balance DECIMAL(36, 18) DEFAULT 0,
                total_balance DECIMAL(36, 18) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, currency, wallet_type),
                INDEX idx_user_currency (user_id, currency),
                INDEX idx_wallet_type (wallet_type)
            )
        """)
        
        # Create transactions table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                wallet_id INTEGER REFERENCES wallets(wallet_id),
                currency VARCHAR(20) NOT NULL,
                transaction_type VARCHAR(20) NOT NULL,
                amount DECIMAL(36, 18) NOT NULL,
                fee DECIMAL(36, 18) DEFAULT 0,
                balance_before DECIMAL(36, 18),
                balance_after DECIMAL(36, 18),
                status VARCHAR(20) NOT NULL,
                reference_id VARCHAR(255),
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_transactions (user_id, created_at DESC),
                INDEX idx_transaction_type (transaction_type),
                INDEX idx_status (status)
            )
        """)
        
        # Create deposits table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS deposits (
                deposit_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                transaction_id INTEGER REFERENCES transactions(transaction_id),
                currency VARCHAR(20) NOT NULL,
                amount DECIMAL(36, 18) NOT NULL,
                blockchain VARCHAR(50) NOT NULL,
                transaction_hash VARCHAR(255) UNIQUE,
                from_address VARCHAR(255),
                to_address VARCHAR(255),
                confirmations INTEGER DEFAULT 0,
                required_confirmations INTEGER DEFAULT 6,
                status VARCHAR(20) NOT NULL,
                credited_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_deposits (user_id, created_at DESC),
                INDEX idx_tx_hash (transaction_hash),
                INDEX idx_status (status)
            )
        """)
        
        # Create withdrawals table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS withdrawals (
                withdrawal_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                transaction_id INTEGER REFERENCES transactions(transaction_id),
                currency VARCHAR(20) NOT NULL,
                amount DECIMAL(36, 18) NOT NULL,
                fee DECIMAL(36, 18) NOT NULL,
                to_address VARCHAR(255) NOT NULL,
                blockchain VARCHAR(50) NOT NULL,
                wallet_type VARCHAR(20) NOT NULL,
                transaction_hash VARCHAR(255),
                status VARCHAR(20) NOT NULL,
                approved_by INTEGER,
                approved_at TIMESTAMP,
                processed_at TIMESTAMP,
                completed_at TIMESTAMP,
                rejection_reason TEXT,
                memo TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_withdrawals (user_id, created_at DESC),
                INDEX idx_status (status),
                INDEX idx_tx_hash (transaction_hash)
            )
        """)
        
        # Create wallet locks table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS wallet_locks (
                lock_id SERIAL PRIMARY KEY,
                wallet_id INTEGER REFERENCES wallets(wallet_id),
                amount DECIMAL(36, 18) NOT NULL,
                lock_type VARCHAR(50) NOT NULL,
                reference_id VARCHAR(255),
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_wallet_locks (wallet_id),
                INDEX idx_reference (reference_id)
            )
        """)
        
        # Create withdrawal limits table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS withdrawal_limits (
                limit_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                currency VARCHAR(20) NOT NULL,
                daily_limit DECIMAL(36, 18),
                daily_used DECIMAL(36, 18) DEFAULT 0,
                monthly_limit DECIMAL(36, 18),
                monthly_used DECIMAL(36, 18) DEFAULT 0,
                last_reset_date DATE DEFAULT CURRENT_DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, currency)
            )
        """)
        
        logger.info("Database initialized successfully")

# Wallet operations
async def get_or_create_wallet(
    user_id: int,
    currency: str,
    wallet_type: WalletType,
    db: asyncpg.Pool
) -> int:
    """Get or create wallet for user"""
    wallet = await db.fetchrow("""
        SELECT wallet_id FROM wallets
        WHERE user_id = $1 AND currency = $2 AND wallet_type = $3
    """, user_id, currency, wallet_type.value)
    
    if wallet:
        return wallet['wallet_id']
    
    # Create new wallet
    result = await db.fetchrow("""
        INSERT INTO wallets (user_id, currency, wallet_type)
        VALUES ($1, $2, $3)
        RETURNING wallet_id
    """, user_id, currency, wallet_type.value)
    
    logger.info("wallet_created", user_id=user_id, currency=currency, wallet_type=wallet_type.value)
    return result['wallet_id']

async def update_wallet_balance(
    wallet_id: int,
    amount: Decimal,
    lock_amount: Decimal,
    db: asyncpg.Pool
):
    """Update wallet balance"""
    await db.execute("""
        UPDATE wallets
        SET available_balance = available_balance + $2,
            locked_balance = locked_balance + $3,
            total_balance = available_balance + locked_balance,
            updated_at = CURRENT_TIMESTAMP
        WHERE wallet_id = $1
    """, wallet_id, amount, lock_amount)

async def check_withdrawal_limits(
    user_id: int,
    currency: str,
    amount: Decimal,
    db: asyncpg.Pool
) -> tuple[bool, str]:
    """Check if withdrawal is within limits"""
    limits = await db.fetchrow("""
        SELECT * FROM withdrawal_limits
        WHERE user_id = $1 AND currency = $2
    """, user_id, currency)
    
    if not limits:
        # No limits set, allow withdrawal
        return True, ""
    
    # Check if we need to reset daily/monthly counters
    today = datetime.utcnow().date()
    if limits['last_reset_date'] < today:
        await db.execute("""
            UPDATE withdrawal_limits
            SET daily_used = 0, last_reset_date = $2
            WHERE user_id = $1 AND currency = $3
        """, user_id, today, currency)
        limits = dict(limits)
        limits['daily_used'] = Decimal(0)
    
    # Check daily limit
    if limits['daily_limit'] and (limits['daily_used'] + amount) > limits['daily_limit']:
        return False, f"Daily withdrawal limit exceeded. Limit: {limits['daily_limit']}, Used: {limits['daily_used']}"
    
    # Check monthly limit
    if limits['monthly_limit'] and (limits['monthly_used'] + amount) > limits['monthly_limit']:
        return False, f"Monthly withdrawal limit exceeded. Limit: {limits['monthly_limit']}, Used: {limits['monthly_used']}"
    
    return True, ""

# API Endpoints
@app.post("/api/v1/wallet/deposit", response_model=TransactionResponse)
async def process_deposit(
    request: DepositRequest,
    background_tasks: BackgroundTasks,
    db: asyncpg.Pool = Depends(get_db)
):
    """Process a deposit transaction"""
    try:
        # Check if deposit already exists
        existing = await db.fetchrow("""
            SELECT deposit_id FROM deposits
            WHERE transaction_hash = $1
        """, request.transaction_hash)
        
        if existing:
            raise HTTPException(status_code=400, detail="Deposit already processed")
        
        # Get or create wallet
        wallet_id = await get_or_create_wallet(
            request.user_id,
            request.currency,
            WalletType.SPOT,
            db
        )
        
        # Get current balance
        wallet = await db.fetchrow("""
            SELECT available_balance FROM wallets WHERE wallet_id = $1
        """, wallet_id)
        
        balance_before = wallet['available_balance']
        
        # Create transaction record
        transaction = await db.fetchrow("""
            INSERT INTO transactions (
                user_id, wallet_id, currency, transaction_type,
                amount, balance_before, balance_after, status
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING transaction_id, created_at
        """, request.user_id, wallet_id, request.currency, TransactionType.DEPOSIT.value,
            request.amount, balance_before, balance_before + request.amount, 
            TransactionStatus.PENDING.value)
        
        # Create deposit record
        await db.execute("""
            INSERT INTO deposits (
                user_id, transaction_id, currency, amount, blockchain,
                transaction_hash, from_address, to_address, confirmations, status
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """, request.user_id, transaction['transaction_id'], request.currency,
            request.amount, request.blockchain, request.transaction_hash,
            request.from_address, request.to_address, request.confirmations,
            TransactionStatus.PENDING.value)
        
        # If confirmations are sufficient, credit immediately
        if request.confirmations >= 6:  # Required confirmations
            await update_wallet_balance(wallet_id, request.amount, Decimal(0), db)
            
            await db.execute("""
                UPDATE transactions SET status = $2, updated_at = CURRENT_TIMESTAMP
                WHERE transaction_id = $1
            """, transaction['transaction_id'], TransactionStatus.COMPLETED.value)
            
            await db.execute("""
                UPDATE deposits SET status = $2, credited_at = CURRENT_TIMESTAMP
                WHERE transaction_id = $1
            """, transaction['transaction_id'], TransactionStatus.COMPLETED.value)
            
            logger.info("deposit_completed", 
                       user_id=request.user_id,
                       currency=request.currency,
                       amount=str(request.amount))
        
        return TransactionResponse(
            transaction_id=transaction['transaction_id'],
            user_id=request.user_id,
            currency=request.currency,
            transaction_type=TransactionType.DEPOSIT.value,
            amount=request.amount,
            fee=Decimal(0),
            status=TransactionStatus.COMPLETED.value if request.confirmations >= 6 else TransactionStatus.PENDING.value,
            created_at=transaction['created_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("deposit_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Deposit processing failed: {str(e)}")

@app.post("/api/v1/wallet/withdraw", response_model=WithdrawalResponse)
async def request_withdrawal(
    request: WithdrawalRequest,
    db: asyncpg.Pool = Depends(get_db)
):
    """Request a withdrawal"""
    try:
        # Get wallet
        wallet = await db.fetchrow("""
            SELECT wallet_id, available_balance FROM wallets
            WHERE user_id = $1 AND currency = $2 AND wallet_type = $3
        """, request.user_id, request.currency, request.wallet_type.value)
        
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        # Calculate fee (0.1% for now)
        fee = request.amount * Decimal("0.001")
        total_amount = request.amount + fee
        
        # Check balance
        if wallet['available_balance'] < total_amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        # Check withdrawal limits
        within_limits, limit_message = await check_withdrawal_limits(
            request.user_id, request.currency, request.amount, db
        )
        
        if not within_limits:
            raise HTTPException(status_code=400, detail=limit_message)
        
        # Lock funds
        await update_wallet_balance(
            wallet['wallet_id'],
            -total_amount,
            total_amount,
            db
        )
        
        # Create transaction record
        transaction = await db.fetchrow("""
            INSERT INTO transactions (
                user_id, wallet_id, currency, transaction_type,
                amount, fee, status
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING transaction_id, created_at
        """, request.user_id, wallet['wallet_id'], request.currency,
            TransactionType.WITHDRAWAL.value, request.amount, fee,
            TransactionStatus.PENDING.value)
        
        # Create withdrawal record
        withdrawal = await db.fetchrow("""
            INSERT INTO withdrawals (
                user_id, transaction_id, currency, amount, fee,
                to_address, blockchain, wallet_type, status, memo
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            RETURNING withdrawal_id, created_at
        """, request.user_id, transaction['transaction_id'], request.currency,
            request.amount, fee, request.to_address, request.blockchain,
            request.wallet_type.value, WithdrawalStatus.PENDING.value, request.memo)
        
        # Update withdrawal limits
        await db.execute("""
            INSERT INTO withdrawal_limits (user_id, currency, daily_used, monthly_used)
            VALUES ($1, $2, $3, $3)
            ON CONFLICT (user_id, currency)
            DO UPDATE SET
                daily_used = withdrawal_limits.daily_used + $3,
                monthly_used = withdrawal_limits.monthly_used + $3,
                updated_at = CURRENT_TIMESTAMP
        """, request.user_id, request.currency, request.amount)
        
        logger.info("withdrawal_requested",
                   user_id=request.user_id,
                   currency=request.currency,
                   amount=str(request.amount))
        
        return WithdrawalResponse(
            withdrawal_id=withdrawal['withdrawal_id'],
            user_id=request.user_id,
            currency=request.currency,
            amount=request.amount,
            fee=fee,
            to_address=request.to_address,
            blockchain=request.blockchain,
            status=WithdrawalStatus.PENDING.value,
            transaction_hash=None,
            created_at=withdrawal['created_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("withdrawal_request_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Withdrawal request failed: {str(e)}")

@app.post("/api/v1/wallet/transfer", response_model=TransactionResponse)
async def transfer_between_wallets(
    request: TransferRequest,
    db: asyncpg.Pool = Depends(get_db)
):
    """Transfer funds between wallet types"""
    try:
        # Get source wallet
        from_wallet = await db.fetchrow("""
            SELECT wallet_id, available_balance FROM wallets
            WHERE user_id = $1 AND currency = $2 AND wallet_type = $3
        """, request.user_id, request.currency, request.from_wallet_type.value)
        
        if not from_wallet:
            raise HTTPException(status_code=404, detail="Source wallet not found")
        
        if from_wallet['available_balance'] < request.amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        # Get or create destination wallet
        to_wallet_id = await get_or_create_wallet(
            request.user_id,
            request.currency,
            request.to_wallet_type,
            db
        )
        
        # Perform transfer
        async with db.transaction():
            # Deduct from source
            await update_wallet_balance(
                from_wallet['wallet_id'],
                -request.amount,
                Decimal(0),
                db
            )
            
            # Add to destination
            await update_wallet_balance(
                to_wallet_id,
                request.amount,
                Decimal(0),
                db
            )
            
            # Create transaction record
            transaction = await db.fetchrow("""
                INSERT INTO transactions (
                    user_id, wallet_id, currency, transaction_type,
                    amount, status, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING transaction_id, created_at
            """, request.user_id, from_wallet['wallet_id'], request.currency,
                TransactionType.TRANSFER.value, request.amount,
                TransactionStatus.COMPLETED.value,
                {
                    "from_wallet_type": request.from_wallet_type.value,
                    "to_wallet_type": request.to_wallet_type.value
                })
        
        logger.info("transfer_completed",
                   user_id=request.user_id,
                   currency=request.currency,
                   amount=str(request.amount),
                   from_wallet=request.from_wallet_type.value,
                   to_wallet=request.to_wallet_type.value)
        
        return TransactionResponse(
            transaction_id=transaction['transaction_id'],
            user_id=request.user_id,
            currency=request.currency,
            transaction_type=TransactionType.TRANSFER.value,
            amount=request.amount,
            fee=Decimal(0),
            status=TransactionStatus.COMPLETED.value,
            created_at=transaction['created_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("transfer_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Transfer failed: {str(e)}")

@app.get("/api/v1/wallet/balance/{user_id}", response_model=List[WalletBalance])
async def get_user_balances(
    user_id: int,
    currency: Optional[str] = None,
    wallet_type: Optional[WalletType] = None,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get user wallet balances"""
    try:
        query = "SELECT * FROM wallets WHERE user_id = $1"
        params = [user_id]
        
        if currency:
            query += " AND currency = $2"
            params.append(currency)
        
        if wallet_type:
            query += f" AND wallet_type = ${len(params) + 1}"
            params.append(wallet_type.value)
        
        query += " ORDER BY currency, wallet_type"
        
        wallets = await db.fetch(query, *params)
        
        return [
            WalletBalance(
                wallet_id=w['wallet_id'],
                user_id=w['user_id'],
                currency=w['currency'],
                wallet_type=w['wallet_type'],
                available_balance=w['available_balance'],
                locked_balance=w['locked_balance'],
                total_balance=w['total_balance'],
                updated_at=w['updated_at']
            )
            for w in wallets
        ]
        
    except Exception as e:
        logger.error("get_balances_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/wallet/transactions/{user_id}", response_model=List[TransactionResponse])
async def get_user_transactions(
    user_id: int,
    transaction_type: Optional[TransactionType] = None,
    currency: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get user transaction history"""
    try:
        query = "SELECT * FROM transactions WHERE user_id = $1"
        params = [user_id]
        
        if transaction_type:
            query += " AND transaction_type = $2"
            params.append(transaction_type.value)
        
        if currency:
            query += f" AND currency = ${len(params) + 1}"
            params.append(currency)
        
        query += f" ORDER BY created_at DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
        params.extend([limit, offset])
        
        transactions = await db.fetch(query, *params)
        
        return [
            TransactionResponse(
                transaction_id=t['transaction_id'],
                user_id=t['user_id'],
                currency=t['currency'],
                transaction_type=t['transaction_type'],
                amount=t['amount'],
                fee=t['fee'],
                status=t['status'],
                created_at=t['created_at']
            )
            for t in transactions
        ]
        
    except Exception as e:
        logger.error("get_transactions_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/wallet/withdrawals/{user_id}", response_model=List[WithdrawalResponse])
async def get_user_withdrawals(
    user_id: int,
    status: Optional[WithdrawalStatus] = None,
    limit: int = 50,
    offset: int = 0,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get user withdrawal history"""
    try:
        query = "SELECT * FROM withdrawals WHERE user_id = $1"
        params = [user_id]
        
        if status:
            query += " AND status = $2"
            params.append(status.value)
        
        query += f" ORDER BY created_at DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
        params.extend([limit, offset])
        
        withdrawals = await db.fetch(query, *params)
        
        return [
            WithdrawalResponse(
                withdrawal_id=w['withdrawal_id'],
                user_id=w['user_id'],
                currency=w['currency'],
                amount=w['amount'],
                fee=w['fee'],
                to_address=w['to_address'],
                blockchain=w['blockchain'],
                status=w['status'],
                transaction_hash=w['transaction_hash'],
                created_at=w['created_at']
            )
            for w in withdrawals
        ]
        
    except Exception as e:
        logger.error("get_withdrawals_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "enhanced-wallet-service",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.on_event("startup")
async def startup():
    """Initialize service on startup"""
    await init_db()
    logger.info("Enhanced Wallet Service started")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    if db_pool:
        await db_pool.close()
    logger.info("Enhanced Wallet Service stopped")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8230)