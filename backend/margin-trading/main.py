"""
Margin Trading Service
Handles leveraged spot trading with isolated and cross margin
Port: 8053
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum
import uvicorn
from decimal import Decimal

app = FastAPI(
    title="Margin Trading Service",
    description="Leveraged spot trading with margin accounts",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class MarginType(str, Enum):
    ISOLATED = "isolated"
    CROSS = "cross"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"

class LoanStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    REPAID = "repaid"
    LIQUIDATED = "liquidated"

# Models
class MarginPair(BaseModel):
    symbol: str
    base_asset: str
    quote_asset: str
    max_leverage: int = 10
    maintenance_margin_rate: Decimal
    initial_margin_rate: Decimal
    interest_rate_base: Decimal  # Daily interest rate
    interest_rate_quote: Decimal
    is_borrowable_base: bool = True
    is_borrowable_quote: bool = True

class MarginAccount(BaseModel):
    user_id: str
    account_type: MarginType
    symbol: Optional[str] = None  # For isolated margin
    total_asset: Decimal = Decimal("0")
    total_liability: Decimal = Decimal("0")
    total_net_asset: Decimal = Decimal("0")
    margin_level: Decimal = Decimal("0")
    assets: Dict[str, Decimal] = {}
    liabilities: Dict[str, Decimal] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MarginOrder(BaseModel):
    order_id: str
    user_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Optional[Decimal] = None
    margin_type: MarginType
    status: str = "pending"
    filled_quantity: Decimal = Decimal("0")
    average_price: Optional[Decimal] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Loan(BaseModel):
    loan_id: str
    user_id: str
    asset: str
    principal: Decimal
    interest: Decimal = Decimal("0")
    total_debt: Decimal
    interest_rate: Decimal
    margin_type: MarginType
    symbol: Optional[str] = None  # For isolated margin
    status: LoanStatus = LoanStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BorrowRequest(BaseModel):
    asset: str
    amount: Decimal
    margin_type: MarginType
    symbol: Optional[str] = None

class RepayRequest(BaseModel):
    loan_id: str
    amount: Decimal

class TransferRequest(BaseModel):
    asset: str
    amount: Decimal
    from_account: str  # "spot" or "margin"
    to_account: str
    margin_type: Optional[MarginType] = None
    symbol: Optional[str] = None

# In-memory storage
margin_pairs_db: Dict[str, MarginPair] = {}
margin_accounts_db: Dict[str, List[MarginAccount]] = {}
margin_orders_db: Dict[str, List[MarginOrder]] = {}
loans_db: Dict[str, List[Loan]] = {}

# Initialize sample margin pairs
def initialize_margin_pairs():
    """Initialize sample margin trading pairs"""
    sample_pairs = [
        {
            "symbol": "BTCUSDT",
            "base_asset": "BTC",
            "quote_asset": "USDT",
            "max_leverage": 10,
            "maintenance_margin_rate": Decimal("0.10"),
            "initial_margin_rate": Decimal("0.15"),
            "interest_rate_base": Decimal("0.0002"),  # 0.02% daily
            "interest_rate_quote": Decimal("0.0001")   # 0.01% daily
        },
        {
            "symbol": "ETHUSDT",
            "base_asset": "ETH",
            "quote_asset": "USDT",
            "max_leverage": 10,
            "maintenance_margin_rate": Decimal("0.10"),
            "initial_margin_rate": Decimal("0.15"),
            "interest_rate_base": Decimal("0.0002"),
            "interest_rate_quote": Decimal("0.0001")
        },
        {
            "symbol": "BNBUSDT",
            "base_asset": "BNB",
            "quote_asset": "USDT",
            "max_leverage": 5,
            "maintenance_margin_rate": Decimal("0.15"),
            "initial_margin_rate": Decimal("0.20"),
            "interest_rate_base": Decimal("0.0003"),
            "interest_rate_quote": Decimal("0.0001")
        }
    ]
    
    for pair_data in sample_pairs:
        pair = MarginPair(**pair_data)
        margin_pairs_db[pair.symbol] = pair

initialize_margin_pairs()

# Helper functions
def calculate_margin_level(account: MarginAccount, prices: Dict[str, Decimal]) -> Decimal:
    """Calculate margin level (total asset / total liability)"""
    if account.total_liability == 0:
        return Decimal("999999")  # Infinite margin level
    
    return (account.total_asset / account.total_liability) * 100

def calculate_max_borrowable(
    account: MarginAccount,
    asset: str,
    pair: MarginPair,
    current_price: Decimal
) -> Decimal:
    """Calculate maximum borrowable amount"""
    net_asset_value = account.total_net_asset
    max_liability = net_asset_value / pair.initial_margin_rate
    current_liability = account.total_liability
    
    available_to_borrow = max_liability - current_liability
    
    if asset == pair.base_asset:
        max_amount = available_to_borrow / current_price
    else:
        max_amount = available_to_borrow
    
    return max_amount

def check_liquidation_risk(account: MarginAccount, pair: MarginPair) -> bool:
    """Check if account is at risk of liquidation"""
    if account.margin_level < (pair.maintenance_margin_rate * 100):
        return True
    return False

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "margin-trading",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/pairs", response_model=List[MarginPair])
async def get_margin_pairs():
    """Get all available margin trading pairs"""
    return list(margin_pairs_db.values())

@app.get("/pairs/{symbol}", response_model=MarginPair)
async def get_margin_pair(symbol: str):
    """Get specific margin trading pair details"""
    if symbol not in margin_pairs_db:
        raise HTTPException(status_code=404, detail="Margin pair not found")
    
    return margin_pairs_db[symbol]

@app.post("/accounts")
async def create_margin_account(
    user_id: str,
    margin_type: MarginType,
    symbol: Optional[str] = None
):
    """Create a new margin account"""
    if margin_type == MarginType.ISOLATED and not symbol:
        raise HTTPException(
            status_code=400,
            detail="Symbol required for isolated margin account"
        )
    
    if symbol and symbol not in margin_pairs_db:
        raise HTTPException(status_code=404, detail="Margin pair not found")
    
    # Check if account already exists
    if user_id in margin_accounts_db:
        for account in margin_accounts_db[user_id]:
            if account.account_type == margin_type and account.symbol == symbol:
                raise HTTPException(
                    status_code=400,
                    detail="Margin account already exists"
                )
    
    # Create new account
    account = MarginAccount(
        user_id=user_id,
        account_type=margin_type,
        symbol=symbol
    )
    
    if user_id not in margin_accounts_db:
        margin_accounts_db[user_id] = []
    
    margin_accounts_db[user_id].append(account)
    
    return {
        "message": "Margin account created successfully",
        "account_type": margin_type,
        "symbol": symbol
    }

@app.get("/accounts/{user_id}", response_model=List[MarginAccount])
async def get_margin_accounts(user_id: str):
    """Get user's margin accounts"""
    if user_id not in margin_accounts_db:
        return []
    
    return margin_accounts_db[user_id]

@app.post("/transfer")
async def transfer_assets(user_id: str, transfer: TransferRequest):
    """Transfer assets between spot and margin accounts"""
    # Validate transfer
    if transfer.from_account == transfer.to_account:
        raise HTTPException(
            status_code=400,
            detail="Cannot transfer to the same account type"
        )
    
    if transfer.to_account == "margin" and not transfer.margin_type:
        raise HTTPException(
            status_code=400,
            detail="Margin type required for margin account transfer"
        )
    
    # Find or create margin account
    if user_id not in margin_accounts_db:
        margin_accounts_db[user_id] = []
    
    target_account = None
    for account in margin_accounts_db[user_id]:
        if (account.account_type == transfer.margin_type and 
            account.symbol == transfer.symbol):
            target_account = account
            break
    
    if not target_account and transfer.to_account == "margin":
        # Create new margin account
        target_account = MarginAccount(
            user_id=user_id,
            account_type=transfer.margin_type,
            symbol=transfer.symbol
        )
        margin_accounts_db[user_id].append(target_account)
    
    # Update account balances
    if transfer.to_account == "margin":
        if transfer.asset not in target_account.assets:
            target_account.assets[transfer.asset] = Decimal("0")
        target_account.assets[transfer.asset] += transfer.amount
        target_account.total_asset += transfer.amount
        target_account.total_net_asset = target_account.total_asset - target_account.total_liability
    
    target_account.updated_at = datetime.utcnow()
    
    return {
        "message": "Transfer successful",
        "asset": transfer.asset,
        "amount": str(transfer.amount),
        "from": transfer.from_account,
        "to": transfer.to_account
    }

@app.post("/borrow")
async def borrow_asset(user_id: str, borrow: BorrowRequest):
    """Borrow assets for margin trading"""
    # Find margin account
    if user_id not in margin_accounts_db:
        raise HTTPException(status_code=404, detail="No margin account found")
    
    target_account = None
    for account in margin_accounts_db[user_id]:
        if (account.account_type == borrow.margin_type and 
            account.symbol == borrow.symbol):
            target_account = account
            break
    
    if not target_account:
        raise HTTPException(status_code=404, detail="Margin account not found")
    
    # Get pair info for interest rate
    if borrow.symbol and borrow.symbol in margin_pairs_db:
        pair = margin_pairs_db[borrow.symbol]
        if borrow.asset == pair.base_asset:
            interest_rate = pair.interest_rate_base
        else:
            interest_rate = pair.interest_rate_quote
    else:
        interest_rate = Decimal("0.0002")  # Default rate
    
    # Create loan
    loan = Loan(
        loan_id=f"loan_{user_id}_{datetime.utcnow().timestamp()}",
        user_id=user_id,
        asset=borrow.asset,
        principal=borrow.amount,
        total_debt=borrow.amount,
        interest_rate=interest_rate,
        margin_type=borrow.margin_type,
        symbol=borrow.symbol
    )
    
    if user_id not in loans_db:
        loans_db[user_id] = []
    
    loans_db[user_id].append(loan)
    
    # Update account
    if borrow.asset not in target_account.assets:
        target_account.assets[borrow.asset] = Decimal("0")
    if borrow.asset not in target_account.liabilities:
        target_account.liabilities[borrow.asset] = Decimal("0")
    
    target_account.assets[borrow.asset] += borrow.amount
    target_account.liabilities[borrow.asset] += borrow.amount
    target_account.total_asset += borrow.amount
    target_account.total_liability += borrow.amount
    target_account.total_net_asset = target_account.total_asset - target_account.total_liability
    target_account.updated_at = datetime.utcnow()
    
    return {
        "loan_id": loan.loan_id,
        "asset": borrow.asset,
        "amount": str(borrow.amount),
        "interest_rate": str(interest_rate),
        "message": "Borrow successful"
    }

@app.post("/repay")
async def repay_loan(user_id: str, repay: RepayRequest):
    """Repay borrowed assets"""
    if user_id not in loans_db:
        raise HTTPException(status_code=404, detail="No loans found")
    
    # Find loan
    loan = None
    for l in loans_db[user_id]:
        if l.loan_id == repay.loan_id:
            loan = l
            break
    
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    if loan.status != LoanStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Loan is not active")
    
    # Calculate current debt with interest
    days_elapsed = (datetime.utcnow() - loan.created_at).days
    interest = loan.principal * loan.interest_rate * days_elapsed
    total_debt = loan.principal + interest
    
    if repay.amount > total_debt:
        repay.amount = total_debt
    
    # Update loan
    loan.total_debt -= repay.amount
    loan.interest = interest
    loan.updated_at = datetime.utcnow()
    
    if loan.total_debt <= 0:
        loan.status = LoanStatus.REPAID
    
    # Update margin account
    if user_id in margin_accounts_db:
        for account in margin_accounts_db[user_id]:
            if (account.account_type == loan.margin_type and 
                account.symbol == loan.symbol):
                if loan.asset in account.liabilities:
                    account.liabilities[loan.asset] -= repay.amount
                    account.total_liability -= repay.amount
                    account.total_net_asset = account.total_asset - account.total_liability
                    account.updated_at = datetime.utcnow()
                break
    
    return {
        "loan_id": loan.loan_id,
        "repaid_amount": str(repay.amount),
        "remaining_debt": str(loan.total_debt),
        "status": loan.status,
        "message": "Repayment successful"
    }

@app.get("/loans/{user_id}", response_model=List[Loan])
async def get_loans(user_id: str, status: Optional[LoanStatus] = None):
    """Get user's loans"""
    if user_id not in loans_db:
        return []
    
    loans = loans_db[user_id]
    
    if status:
        loans = [l for l in loans if l.status == status]
    
    # Update interest for active loans
    for loan in loans:
        if loan.status == LoanStatus.ACTIVE:
            days_elapsed = (datetime.utcnow() - loan.created_at).days
            loan.interest = loan.principal * loan.interest_rate * days_elapsed
            loan.total_debt = loan.principal + loan.interest
    
    return loans

@app.post("/orders")
async def create_margin_order(order: MarginOrder):
    """Create a margin trading order"""
    if order.symbol not in margin_pairs_db:
        raise HTTPException(status_code=404, detail="Margin pair not found")
    
    # Store order
    if order.user_id not in margin_orders_db:
        margin_orders_db[order.user_id] = []
    
    margin_orders_db[order.user_id].append(order)
    
    # Simulate order execution for market orders
    if order.order_type == OrderType.MARKET:
        order.status = "filled"
        order.filled_quantity = order.quantity
        # Use mock price
        order.average_price = Decimal("45000") if "BTC" in order.symbol else Decimal("3000")
    
    return {
        "order_id": order.order_id,
        "status": order.status,
        "message": "Order created successfully"
    }

@app.get("/orders/{user_id}", response_model=List[MarginOrder])
async def get_margin_orders(
    user_id: str,
    symbol: Optional[str] = None,
    status: Optional[str] = None
):
    """Get user's margin orders"""
    if user_id not in margin_orders_db:
        return []
    
    orders = margin_orders_db[user_id]
    
    if symbol:
        orders = [o for o in orders if o.symbol == symbol]
    
    if status:
        orders = [o for o in orders if o.status == status]
    
    return orders

@app.get("/interest-rate/{symbol}")
async def get_interest_rates(symbol: str):
    """Get current interest rates for a margin pair"""
    if symbol not in margin_pairs_db:
        raise HTTPException(status_code=404, detail="Margin pair not found")
    
    pair = margin_pairs_db[symbol]
    
    return {
        "symbol": symbol,
        "base_asset": pair.base_asset,
        "quote_asset": pair.quote_asset,
        "interest_rate_base": str(pair.interest_rate_base),
        "interest_rate_quote": str(pair.interest_rate_quote),
        "daily_rate": True
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8053)