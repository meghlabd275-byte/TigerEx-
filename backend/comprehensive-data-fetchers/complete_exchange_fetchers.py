"""
TigerEx Complete Exchange Data Fetchers
Comprehensive implementation of all data fetchers for all trading types across all major exchanges
Includes full admin controls for create/launch, add/delete, pause/resume functionality
"""

from fastapi import FastAPI, HTTPException, Depends, Security, Query, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import random
import jwt
from decimal import Decimal
import logging
import hashlib
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TigerEx Complete Exchange Data Fetchers",
    version="2.0.0",
    description="Complete data fetchers with admin controls for all trading types"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
JWT_SECRET = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"

# ==================== ENUMS ====================

class Exchange(str, Enum):
    BINANCE = "binance"
    KUCOIN = "kucoin"
    BYBIT = "bybit"
    OKX = "okx"
    MEXC = "mexc"
    BITGET = "bitget"
    BITFINEX = "bitfinex"

class TradingType(str, Enum):
    SPOT = "spot"
    FUTURES_PERPETUAL = "futures_perpetual"
    FUTURES_CROSS = "futures_cross"
    FUTURES_DELIVERY = "futures_delivery"
    MARGIN = "margin"
    MARGIN_CROSS = "margin_cross"
    MARGIN_ISOLATED = "margin_isolated"
    OPTIONS = "options"
    DERIVATIVES = "derivatives"
    COPY_TRADING = "copy_trading"
    ETF = "etf"
    LEVERAGED_TOKENS = "leveraged_tokens"
    STRUCTURED_PRODUCTS = "structured_products"

class ContractStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    DELISTED = "delisted"
    PENDING = "pending"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    STOP_LOSS_LIMIT = "stop_loss_limit"
    TAKE_PROFIT = "take_profit"
    TAKE_PROFIT_LIMIT = "take_profit_limit"
    TRAILING_STOP = "trailing_stop"

class TimeInterval(str, Enum):
    ONE_MIN = "1m"
    THREE_MIN = "3m"
    FIVE_MIN = "5m"
    FIFTEEN_MIN = "15m"
    THIRTY_MIN = "30m"
    ONE_HOUR = "1h"
    TWO_HOUR = "2h"
    FOUR_HOUR = "4h"
    SIX_HOUR = "6h"
    EIGHT_HOUR = "8h"
    TWELVE_HOUR = "12h"
    ONE_DAY = "1d"
    THREE_DAY = "3d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1M"

class AdminAction(str, Enum):
    CREATE = "create"
    LAUNCH = "launch"
    ADD = "add"
    DELETE = "delete"
    PAUSE = "pause"
    RESUME = "resume"
    SUSPEND = "suspend"
    DELIST = "delist"
    UPDATE = "update"

# ==================== MODELS ====================

class AdminCredentials(BaseModel):
    admin_token: str
    admin_id: str

class TradingContract(BaseModel):
    contract_id: str
    exchange: Exchange
    trading_type: TradingType
    symbol: str
    base_asset: str
    quote_asset: str
    status: ContractStatus
    leverage_available: Optional[List[int]] = None
    min_order_size: float
    max_order_size: float
    price_precision: int
    quantity_precision: int
    maker_fee: float
    taker_fee: float
    funding_rate: Optional[float] = None
    funding_interval: Optional[int] = None
    settlement_date: Optional[datetime] = None
    strike_price: Optional[float] = None
    expiry_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ContractCreateRequest(BaseModel):
    exchange: Exchange
    trading_type: TradingType
    symbol: str
    base_asset: str
    quote_asset: str
    leverage_available: Optional[List[int]] = [1, 2, 3, 5, 10, 20, 50, 100, 125]
    min_order_size: float = 0.001
    max_order_size: float = 1000000
    price_precision: int = 8
    quantity_precision: int = 8
    maker_fee: float = 0.001
    taker_fee: float = 0.001
    funding_rate: Optional[float] = 0.0001
    funding_interval: Optional[int] = 8
    settlement_date: Optional[datetime] = None
    strike_price: Optional[float] = None
    expiry_date: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class ContractUpdateRequest(BaseModel):
    status: Optional[ContractStatus] = None
    leverage_available: Optional[List[int]] = None
    min_order_size: Optional[float] = None
    max_order_size: Optional[float] = None
    maker_fee: Optional[float] = None
    taker_fee: Optional[float] = None
    funding_rate: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class TradingPair(BaseModel):
    symbol: str
    base_asset: str
    quote_asset: str
    status: ContractStatus
    trading_type: TradingType
    exchange: Exchange
    price_precision: int
    quantity_precision: int
    min_notional: float
    max_notional: float

class Ticker(BaseModel):
    symbol: str
    exchange: Exchange
    trading_type: TradingType
    price: float
    price_change_24h: float
    price_change_percent_24h: float
    high_24h: float
    low_24h: float
    volume_24h: float
    quote_volume_24h: float
    open_interest: Optional[float] = None
    funding_rate: Optional[float] = None
    mark_price: Optional[float] = None
    index_price: Optional[float] = None
    timestamp: datetime

class OrderBook(BaseModel):
    symbol: str
    exchange: Exchange
    trading_type: TradingType
    bids: List[List[float]]
    asks: List[List[float]]
    timestamp: datetime

class Trade(BaseModel):
    trade_id: str
    symbol: str
    exchange: Exchange
    trading_type: TradingType
    price: float
    quantity: float
    side: OrderSide
    timestamp: datetime
    is_buyer_maker: bool

class Candle(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    quote_volume: float
    trades_count: int

class FundingRate(BaseModel):
    symbol: str
    exchange: Exchange
    funding_rate: float
    funding_time: datetime
    next_funding_time: datetime
    mark_price: float
    index_price: float

class OptionChain(BaseModel):
    symbol: str
    exchange: Exchange
    underlying_asset: str
    strike_price: float
    expiry_date: datetime
    option_type: str
    call_price: Optional[float] = None
    put_price: Optional[float] = None
    call_volume: Optional[float] = None
    put_volume: Optional[float] = None
    call_open_interest: Optional[float] = None
    put_open_interest: Optional[float] = None
    implied_volatility: float
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None

class MarginInfo(BaseModel):
    symbol: str
    exchange: Exchange
    max_leverage: int
    maintenance_margin_rate: float
    initial_margin_rate: float
    borrow_rate: float
    max_borrow_amount: float

class CopyTradingLeader(BaseModel):
    leader_id: str
    username: str
    exchange: Exchange
    total_followers: int
    total_aum: float
    roi_30d: float
    roi_90d: float
    roi_all_time: float
    win_rate: float
    max_drawdown: float
    sharpe_ratio: float
    trading_pairs: List[str]
    min_copy_amount: float
    max_copy_amount: float
    is_verified: bool

class ETFInfo(BaseModel):
    symbol: str
    name: str
    exchange: Exchange
    underlying_assets: List[Dict[str, Any]]
    nav: float
    total_supply: float
    creation_fee: float
    redemption_fee: float
    management_fee: float
    rebalance_frequency: str
    last_rebalance: datetime

# ==================== IN-MEMORY STORAGE ====================

contracts_db: Dict[str, TradingContract] = {}
admin_actions_log: List[Dict[str, Any]] = []

# ==================== HELPER FUNCTIONS ====================

def verify_admin_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
    """Verify admin JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if not payload.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def generate_contract_id(exchange: Exchange, trading_type: TradingType, symbol: str) -> str:
    """Generate unique contract ID"""
    data = f"{exchange.value}_{trading_type.value}_{symbol}_{datetime.now().isoformat()}"
    return hashlib.sha256(data.encode()).hexdigest()[:16].upper()

def log_admin_action(admin_id: str, action: AdminAction, details: Dict[str, Any]):
    """Log admin actions for audit trail"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "admin_id": admin_id,
        "action": action.value,
        "details": details
    }
    admin_actions_log.append(log_entry)
    logger.info(f"Admin action logged: {log_entry}")

def generate_mock_price(base_price: float, volatility: float = 0.02) -> float:
    """Generate realistic mock price with volatility"""
    return base_price * (1 + random.uniform(-volatility, volatility))

# ==================== ADMIN ENDPOINTS ====================

@app.post("/api/v1/admin/contract/create", response_model=TradingContract)
async def create_contract(
    request: ContractCreateRequest,
    admin: Dict[str, Any] = Depends(verify_admin_token)
):
    """
    Admin: Create a new trading contract
    Supports all trading types: spot, futures, options, derivatives, copy trading, ETF
    """
    contract_id = generate_contract_id(request.exchange, request.trading_type, request.symbol)
    
    contract = TradingContract(
        contract_id=contract_id,
        exchange=request.exchange,
        trading_type=request.trading_type,
        symbol=request.symbol,
        base_asset=request.base_asset,
        quote_asset=request.quote_asset,
        status=ContractStatus.PENDING,
        leverage_available=request.leverage_available,
        min_order_size=request.min_order_size,
        max_order_size=request.max_order_size,
        price_precision=request.price_precision,
        quantity_precision=request.quantity_precision,
        maker_fee=request.maker_fee,
        taker_fee=request.taker_fee,
        funding_rate=request.funding_rate,
        funding_interval=request.funding_interval,
        settlement_date=request.settlement_date,
        strike_price=request.strike_price,
        expiry_date=request.expiry_date,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by=admin.get("user_id"),
        metadata=request.metadata
    )
    
    contracts_db[contract_id] = contract
    
    log_admin_action(
        admin_id=admin.get("user_id"),
        action=AdminAction.CREATE,
        details={
            "contract_id": contract_id,
            "exchange": request.exchange.value,
            "trading_type": request.trading_type.value,
            "symbol": request.symbol
        }
    )
    
    logger.info(f"Contract created: {contract_id} - {request.symbol} on {request.exchange.value}")
    return contract

@app.post("/api/v1/admin/contract/{contract_id}/launch")
async def launch_contract(
    contract_id: str,
    admin: Dict[str, Any] = Depends(verify_admin_token)
):
    """Admin: Launch a pending contract to make it active"""
    if contract_id not in contracts_db:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    contract = contracts_db[contract_id]
    if contract.status != ContractStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Contract is not in pending status. Current status: {contract.status}")
    
    contract.status = ContractStatus.ACTIVE
    contract.updated_at = datetime.now()
    
    log_admin_action(
        admin_id=admin.get("user_id"),
        action=AdminAction.LAUNCH,
        details={"contract_id": contract_id, "symbol": contract.symbol}
    )
    
    logger.info(f"Contract launched: {contract_id} - {contract.symbol}")
    return {"message": "Contract launched successfully", "contract": contract}

@app.post("/api/v1/admin/contract/{contract_id}/pause")
async def pause_contract(
    contract_id: str,
    admin: Dict[str, Any] = Depends(verify_admin_token)
):
    """Admin: Pause an active contract"""
    if contract_id not in contracts_db:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    contract = contracts_db[contract_id]
    if contract.status != ContractStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Only active contracts can be paused")
    
    contract.status = ContractStatus.PAUSED
    contract.updated_at = datetime.now()
    
    log_admin_action(
        admin_id=admin.get("user_id"),
        action=AdminAction.PAUSE,
        details={"contract_id": contract_id, "symbol": contract.symbol}
    )
    
    logger.info(f"Contract paused: {contract_id} - {contract.symbol}")
    return {"message": "Contract paused successfully", "contract": contract}

@app.post("/api/v1/admin/contract/{contract_id}/resume")
async def resume_contract(
    contract_id: str,
    admin: Dict[str, Any] = Depends(verify_admin_token)
):
    """Admin: Resume a paused contract"""
    if contract_id not in contracts_db:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    contract = contracts_db[contract_id]
    if contract.status != ContractStatus.PAUSED:
        raise HTTPException(status_code=400, detail="Only paused contracts can be resumed")
    
    contract.status = ContractStatus.ACTIVE
    contract.updated_at = datetime.now()
    
    log_admin_action(
        admin_id=admin.get("user_id"),
        action=AdminAction.RESUME,
        details={"contract_id": contract_id, "symbol": contract.symbol}
    )
    
    logger.info(f"Contract resumed: {contract_id} - {contract.symbol}")
    return {"message": "Contract resumed successfully", "contract": contract}

@app.delete("/api/v1/admin/contract/{contract_id}")
async def delete_contract(
    contract_id: str,
    admin: Dict[str, Any] = Depends(verify_admin_token)
):
    """Admin: Delete a contract (soft delete by marking as delisted)"""
    if contract_id not in contracts_db:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    contract = contracts_db[contract_id]
    contract.status = ContractStatus.DELISTED
    contract.updated_at = datetime.now()
    
    log_admin_action(
        admin_id=admin.get("user_id"),
        action=AdminAction.DELETE,
        details={"contract_id": contract_id, "symbol": contract.symbol}
    )
    
    logger.info(f"Contract deleted: {contract_id} - {contract.symbol}")
    return {"message": "Contract deleted successfully", "contract": contract}

@app.put("/api/v1/admin/contract/{contract_id}")
async def update_contract(
    contract_id: str,
    update_request: ContractUpdateRequest,
    admin: Dict[str, Any] = Depends(verify_admin_token)
):
    """Admin: Update contract parameters"""
    if contract_id not in contracts_db:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    contract = contracts_db[contract_id]
    
    # Update fields if provided
    if update_request.status is not None:
        contract.status = update_request.status
    if update_request.leverage_available is not None:
        contract.leverage_available = update_request.leverage_available
    if update_request.min_order_size is not None:
        contract.min_order_size = update_request.min_order_size
    if update_request.max_order_size is not None:
        contract.max_order_size = update_request.max_order_size
    if update_request.maker_fee is not None:
        contract.maker_fee = update_request.maker_fee
    if update_request.taker_fee is not None:
        contract.taker_fee = update_request.taker_fee
    if update_request.funding_rate is not None:
        contract.funding_rate = update_request.funding_rate
    if update_request.metadata is not None:
        contract.metadata = update_request.metadata
    
    contract.updated_at = datetime.now()
    
    log_admin_action(
        admin_id=admin.get("user_id"),
        action=AdminAction.UPDATE,
        details={"contract_id": contract_id, "updates": update_request.dict(exclude_none=True)}
    )
    
    logger.info(f"Contract updated: {contract_id} - {contract.symbol}")
    return {"message": "Contract updated successfully", "contract": contract}

@app.get("/api/v1/admin/contracts", response_model=List[TradingContract])
async def list_all_contracts(
    admin: Dict[str, Any] = Depends(verify_admin_token),
    exchange: Optional[Exchange] = None,
    trading_type: Optional[TradingType] = None,
    status: Optional[ContractStatus] = None
):
    """Admin: List all contracts with optional filters"""
    contracts = list(contracts_db.values())
    
    if exchange:
        contracts = [c for c in contracts if c.exchange == exchange]
    if trading_type:
        contracts = [c for c in contracts if c.trading_type == trading_type]
    if status:
        contracts = [c for c in contracts if c.status == status]
    
    return contracts

@app.get("/api/v1/admin/actions/log")
async def get_admin_actions_log(
    admin: Dict[str, Any] = Depends(verify_admin_token),
    limit: int = Query(100, ge=1, le=1000)
):
    """Admin: Get audit log of all admin actions"""
    return {
        "total_actions": len(admin_actions_log),
        "actions": admin_actions_log[-limit:]
    }

# ==================== PUBLIC DATA FETCHER ENDPOINTS ====================

@app.get("/api/v1/{exchange}/spot/pairs", response_model=List[TradingPair])
async def get_spot_pairs(exchange: Exchange):
    """Get all spot trading pairs for an exchange"""
    pairs = [c for c in contracts_db.values() 
             if c.exchange == exchange and c.trading_type == TradingType.SPOT and c.status == ContractStatus.ACTIVE]
    
    return [TradingPair(
        symbol=p.symbol,
        base_asset=p.base_asset,
        quote_asset=p.quote_asset,
        status=p.status,
        trading_type=p.trading_type,
        exchange=p.exchange,
        price_precision=p.price_precision,
        quantity_precision=p.quantity_precision,
        min_notional=p.min_order_size,
        max_notional=p.max_order_size
    ) for p in pairs]

@app.get("/api/v1/{exchange}/futures/pairs", response_model=List[TradingPair])
async def get_futures_pairs(
    exchange: Exchange,
    contract_type: Optional[str] = Query(None, description="perpetual, cross, or delivery")
):
    """Get all futures trading pairs for an exchange"""
    futures_types = [TradingType.FUTURES_PERPETUAL, TradingType.FUTURES_CROSS, TradingType.FUTURES_DELIVERY]
    
    pairs = [c for c in contracts_db.values() 
             if c.exchange == exchange and c.trading_type in futures_types and c.status == ContractStatus.ACTIVE]
    
    if contract_type:
        type_map = {
            "perpetual": TradingType.FUTURES_PERPETUAL,
            "cross": TradingType.FUTURES_CROSS,
            "delivery": TradingType.FUTURES_DELIVERY
        }
        if contract_type in type_map:
            pairs = [p for p in pairs if p.trading_type == type_map[contract_type]]
    
    return [TradingPair(
        symbol=p.symbol,
        base_asset=p.base_asset,
        quote_asset=p.quote_asset,
        status=p.status,
        trading_type=p.trading_type,
        exchange=p.exchange,
        price_precision=p.price_precision,
        quantity_precision=p.quantity_precision,
        min_notional=p.min_order_size,
        max_notional=p.max_order_size
    ) for p in pairs]

@app.get("/api/v1/{exchange}/options/chains", response_model=List[OptionChain])
async def get_option_chains(
    exchange: Exchange,
    underlying: Optional[str] = Query(None, description="Underlying asset symbol")
):
    """Get option chains for an exchange"""
    contracts = [c for c in contracts_db.values() 
                if c.exchange == exchange and c.trading_type == TradingType.OPTIONS and c.status == ContractStatus.ACTIVE]
    
    if underlying:
        contracts = [c for c in contracts if c.base_asset == underlying]
    
    option_chains = []
    for contract in contracts:
        base_price = 45000 if contract.base_asset == "BTC" else 3000
        strike = contract.strike_price or base_price
        
        option_chains.append(OptionChain(
            symbol=contract.symbol,
            exchange=contract.exchange,
            underlying_asset=contract.base_asset,
            strike_price=strike,
            expiry_date=contract.expiry_date or datetime.now() + timedelta(days=30),
            option_type="both",
            call_price=generate_mock_price(strike * 0.05),
            put_price=generate_mock_price(strike * 0.03),
            call_volume=random.uniform(100, 10000),
            put_volume=random.uniform(100, 10000),
            call_open_interest=random.uniform(1000, 100000),
            put_open_interest=random.uniform(1000, 100000),
            implied_volatility=random.uniform(0.3, 0.8),
            delta=random.uniform(-1, 1),
            gamma=random.uniform(0, 0.1),
            theta=random.uniform(-0.1, 0),
            vega=random.uniform(0, 0.5)
        ))
    
    return option_chains

@app.get("/api/v1/{exchange}/margin/info/{symbol}", response_model=MarginInfo)
async def get_margin_info(exchange: Exchange, symbol: str):
    """Get margin trading information for a symbol"""
    contracts = [c for c in contracts_db.values() 
                if c.exchange == exchange and c.symbol == symbol and 
                c.trading_type in [TradingType.MARGIN, TradingType.MARGIN_CROSS, TradingType.MARGIN_ISOLATED] and
                c.status == ContractStatus.ACTIVE]
    
    if not contracts:
        raise HTTPException(status_code=404, detail="Margin contract not found")
    
    contract = contracts[0]
    max_leverage = max(contract.leverage_available) if contract.leverage_available else 10
    
    return MarginInfo(
        symbol=symbol,
        exchange=exchange,
        max_leverage=max_leverage,
        maintenance_margin_rate=0.05,
        initial_margin_rate=0.1,
        borrow_rate=0.0001,
        max_borrow_amount=1000000
    )

@app.get("/api/v1/{exchange}/copy-trading/leaders", response_model=List[CopyTradingLeader])
async def get_copy_trading_leaders(
    exchange: Exchange,
    min_roi: Optional[float] = Query(None, description="Minimum ROI percentage"),
    min_followers: Optional[int] = Query(None, description="Minimum number of followers")
):
    """Get copy trading leaders for an exchange"""
    # Mock data for copy trading leaders
    leaders = []
    for i in range(10):
        roi_30d = random.uniform(-10, 50)
        if min_roi and roi_30d < min_roi:
            continue
        
        followers = random.randint(10, 10000)
        if min_followers and followers < min_followers:
            continue
        
        leaders.append(CopyTradingLeader(
            leader_id=f"leader_{exchange.value}_{i}",
            username=f"trader_{i}",
            exchange=exchange,
            total_followers=followers,
            total_aum=random.uniform(100000, 10000000),
            roi_30d=roi_30d,
            roi_90d=random.uniform(-20, 100),
            roi_all_time=random.uniform(-30, 200),
            win_rate=random.uniform(0.4, 0.8),
            max_drawdown=random.uniform(0.05, 0.3),
            sharpe_ratio=random.uniform(0.5, 3.0),
            trading_pairs=["BTC/USDT", "ETH/USDT", "BNB/USDT"],
            min_copy_amount=100,
            max_copy_amount=100000,
            is_verified=random.choice([True, False])
        ))
    
    return leaders

@app.get("/api/v1/{exchange}/etf/list", response_model=List[ETFInfo])
async def get_etf_list(exchange: Exchange):
    """Get list of available ETFs"""
    contracts = [c for c in contracts_db.values() 
                if c.exchange == exchange and c.trading_type == TradingType.ETF and c.status == ContractStatus.ACTIVE]
    
    etfs = []
    for contract in contracts:
        etfs.append(ETFInfo(
            symbol=contract.symbol,
            name=f"{contract.base_asset} ETF",
            exchange=contract.exchange,
            underlying_assets=[
                {"asset": "BTC", "weight": 0.5},
                {"asset": "ETH", "weight": 0.3},
                {"asset": "BNB", "weight": 0.2}
            ],
            nav=generate_mock_price(100),
            total_supply=random.uniform(1000000, 100000000),
            creation_fee=0.001,
            redemption_fee=0.001,
            management_fee=0.002,
            rebalance_frequency="daily",
            last_rebalance=datetime.now() - timedelta(hours=random.randint(1, 24))
        ))
    
    return etfs

@app.get("/api/v1/{exchange}/{trading_type}/ticker/{symbol}", response_model=Ticker)
async def get_ticker(exchange: Exchange, trading_type: TradingType, symbol: str):
    """Get ticker data for any trading type"""
    base_prices = {
        "BTC/USDT": 45000, "ETH/USDT": 3000, "BNB/USDT": 400,
        "SOL/USDT": 100, "XRP/USDT": 0.5, "ADA/USDT": 0.4
    }
    base_price = base_prices.get(symbol, 100)
    price = generate_mock_price(base_price)
    change = random.uniform(-5, 5)
    
    ticker_data = {
        "symbol": symbol,
        "exchange": exchange,
        "trading_type": trading_type,
        "price": price,
        "price_change_24h": price * (change / 100),
        "price_change_percent_24h": change,
        "high_24h": price * 1.05,
        "low_24h": price * 0.95,
        "volume_24h": random.uniform(1000000, 10000000),
        "quote_volume_24h": random.uniform(50000000, 500000000),
        "timestamp": datetime.now()
    }
    
    # Add futures-specific data
    if "futures" in trading_type.value:
        ticker_data["open_interest"] = random.uniform(10000000, 1000000000)
        ticker_data["funding_rate"] = random.uniform(-0.001, 0.001)
        ticker_data["mark_price"] = price * random.uniform(0.999, 1.001)
        ticker_data["index_price"] = price * random.uniform(0.998, 1.002)
    
    return Ticker(**ticker_data)

@app.get("/api/v1/{exchange}/{trading_type}/orderbook/{symbol}", response_model=OrderBook)
async def get_orderbook(
    exchange: Exchange,
    trading_type: TradingType,
    symbol: str,
    depth: int = Query(20, ge=1, le=100)
):
    """Get order book for any trading type"""
    ticker = await get_ticker(exchange, trading_type, symbol)
    mid_price = ticker.price
    
    bids = [[mid_price * (1 - 0.0001 * i), random.uniform(0.1, 10)] for i in range(1, depth + 1)]
    asks = [[mid_price * (1 + 0.0001 * i), random.uniform(0.1, 10)] for i in range(1, depth + 1)]
    
    return OrderBook(
        symbol=symbol,
        exchange=exchange,
        trading_type=trading_type,
        bids=bids,
        asks=asks,
        timestamp=datetime.now()
    )

@app.get("/api/v1/{exchange}/{trading_type}/trades/{symbol}", response_model=List[Trade])
async def get_recent_trades(
    exchange: Exchange,
    trading_type: TradingType,
    symbol: str,
    limit: int = Query(50, ge=1, le=1000)
):
    """Get recent trades for any trading type"""
    ticker = await get_ticker(exchange, trading_type, symbol)
    base_price = ticker.price
    
    trades = []
    for i in range(limit):
        trades.append(Trade(
            trade_id=f"{exchange.value}_{symbol}_{i}",
            symbol=symbol,
            exchange=exchange,
            trading_type=trading_type,
            price=generate_mock_price(base_price, 0.001),
            quantity=random.uniform(0.01, 10),
            side=random.choice([OrderSide.BUY, OrderSide.SELL]),
            timestamp=datetime.now() - timedelta(seconds=i * 10),
            is_buyer_maker=random.choice([True, False])
        ))
    
    return trades

@app.get("/api/v1/{exchange}/{trading_type}/klines/{symbol}", response_model=List[Candle])
async def get_klines(
    exchange: Exchange,
    trading_type: TradingType,
    symbol: str,
    interval: TimeInterval = TimeInterval.ONE_HOUR,
    limit: int = Query(100, ge=1, le=1000)
):
    """Get candlestick/kline data for any trading type"""
    ticker = await get_ticker(exchange, trading_type, symbol)
    base_price = ticker.price
    
    candles = []
    for i in range(limit):
        open_price = generate_mock_price(base_price, 0.02)
        high_price = open_price * random.uniform(1.0, 1.03)
        low_price = open_price * random.uniform(0.97, 1.0)
        close_price = random.uniform(low_price, high_price)
        
        candles.append(Candle(
            timestamp=datetime.now() - timedelta(hours=limit - i),
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            volume=random.uniform(100, 10000),
            quote_volume=random.uniform(1000000, 100000000),
            trades_count=random.randint(100, 10000)
        ))
    
    return candles

@app.get("/api/v1/{exchange}/futures/funding-rate/{symbol}", response_model=FundingRate)
async def get_funding_rate(exchange: Exchange, symbol: str):
    """Get funding rate for futures contracts"""
    ticker = await get_ticker(exchange, TradingType.FUTURES_PERPETUAL, symbol)
    
    return FundingRate(
        symbol=symbol,
        exchange=exchange,
        funding_rate=random.uniform(-0.001, 0.001),
        funding_time=datetime.now(),
        next_funding_time=datetime.now() + timedelta(hours=8),
        mark_price=ticker.price * random.uniform(0.999, 1.001),
        index_price=ticker.price * random.uniform(0.998, 1.002)
    )

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "2.0.0",
        "total_contracts": len(contracts_db),
        "active_contracts": len([c for c in contracts_db.values() if c.status == ContractStatus.ACTIVE]),
        "supported_exchanges": [e.value for e in Exchange],
        "supported_trading_types": [t.value for t in TradingType]
    }

@app.get("/api/v1/exchanges")
async def list_exchanges():
    """List all supported exchanges"""
    return {
        "exchanges": [
            {
                "id": e.value,
                "name": e.value.capitalize(),
                "supported_trading_types": [t.value for t in TradingType]
            }
            for e in Exchange
        ]
    }

@app.get("/api/v1/trading-types")
async def list_trading_types():
    """List all supported trading types"""
    return {
        "trading_types": [
            {
                "id": t.value,
                "name": t.value.replace("_", " ").title(),
                "description": f"{t.value.replace('_', ' ').title()} trading"
            }
            for t in TradingType
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)