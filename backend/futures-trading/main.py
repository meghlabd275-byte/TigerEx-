"""
Futures Trading Service
Handles perpetual and delivery futures contracts with leverage trading
Port: 8052
"""

from fastapi import FastAPI
from admin.admin_routes import router as admin_router
, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from enum import Enum
import uvicorn
import asyncio
from decimal import Decimal

app = FastAPI(

# Include admin router
app.include_router(admin_router)
    title="Futures Trading Service",
    description="Advanced futures trading with perpetual and delivery contracts",
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
class ContractType(str, Enum):
    PERPETUAL = "perpetual"
    DELIVERY = "delivery"
    INVERSE = "inverse"

class PositionSide(str, Enum):
    LONG = "long"
    SHORT = "short"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_MARKET = "stop_market"
    STOP_LIMIT = "stop_limit"
    TAKE_PROFIT_MARKET = "take_profit_market"
    TAKE_PROFIT_LIMIT = "take_profit_limit"

class MarginType(str, Enum):
    ISOLATED = "isolated"
    CROSS = "cross"

class PositionMode(str, Enum):
    ONE_WAY = "one_way"
    HEDGE = "hedge"

# Models
class FuturesContract(BaseModel):
    symbol: str
    contract_type: ContractType
    base_asset: str
    quote_asset: str
    delivery_date: Optional[datetime] = None
    contract_size: Decimal
    tick_size: Decimal
    max_leverage: int = 125
    maintenance_margin_rate: Decimal
    funding_rate: Optional[Decimal] = None
    mark_price: Decimal
    index_price: Decimal
    last_price: Decimal
    volume_24h: Decimal
    open_interest: Decimal

class Position(BaseModel):
    user_id: str
    symbol: str
    position_side: PositionSide
    position_amt: Decimal
    entry_price: Decimal
    mark_price: Decimal
    liquidation_price: Decimal
    leverage: int
    margin_type: MarginType
    isolated_margin: Optional[Decimal] = None
    unrealized_pnl: Decimal
    realized_pnl: Decimal = Decimal("0")
    margin_ratio: Decimal
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class FuturesOrder(BaseModel):
    order_id: str
    user_id: str
    symbol: str
    side: PositionSide
    order_type: OrderType
    quantity: Decimal
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    leverage: int
    margin_type: MarginType
    reduce_only: bool = False
    post_only: bool = False
    time_in_force: str = "GTC"
    status: str = "pending"
    filled_quantity: Decimal = Decimal("0")
    average_price: Optional[Decimal] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class LeverageUpdate(BaseModel):
    symbol: str
    leverage: int = Field(ge=1, le=125)

class MarginTypeUpdate(BaseModel):
    symbol: str
    margin_type: MarginType

class PositionModeUpdate(BaseModel):
    position_mode: PositionMode

class FundingRate(BaseModel):
    symbol: str
    funding_rate: Decimal
    funding_time: datetime
    next_funding_time: datetime

# In-memory storage
contracts_db: Dict[str, FuturesContract] = {}
positions_db: Dict[str, List[Position]] = {}
orders_db: Dict[str, List[FuturesOrder]] = {}
user_settings: Dict[str, Dict] = {}

# Initialize sample contracts
def initialize_contracts():
    """Initialize sample futures contracts"""
    sample_contracts = [
        {
            "symbol": "BTCUSDT",
            "contract_type": ContractType.PERPETUAL,
            "base_asset": "BTC",
            "quote_asset": "USDT",
            "contract_size": Decimal("1"),
            "tick_size": Decimal("0.1"),
            "max_leverage": 125,
            "maintenance_margin_rate": Decimal("0.004"),
            "funding_rate": Decimal("0.0001"),
            "mark_price": Decimal("45000"),
            "index_price": Decimal("45000"),
            "last_price": Decimal("45000"),
            "volume_24h": Decimal("1000000"),
            "open_interest": Decimal("500000")
        },
        {
            "symbol": "ETHUSDT",
            "contract_type": ContractType.PERPETUAL,
            "base_asset": "ETH",
            "quote_asset": "USDT",
            "contract_size": Decimal("1"),
            "tick_size": Decimal("0.01"),
            "max_leverage": 100,
            "maintenance_margin_rate": Decimal("0.005"),
            "funding_rate": Decimal("0.0001"),
            "mark_price": Decimal("3000"),
            "index_price": Decimal("3000"),
            "last_price": Decimal("3000"),
            "volume_24h": Decimal("500000"),
            "open_interest": Decimal("250000")
        }
    ]
    
    for contract_data in sample_contracts:
        contract = FuturesContract(**contract_data)
        contracts_db[contract.symbol] = contract

initialize_contracts()

# Helper functions
def calculate_liquidation_price(
    entry_price: Decimal,
    leverage: int,
    position_side: PositionSide,
    maintenance_margin_rate: Decimal
) -> Decimal:
    """Calculate liquidation price for a position"""
    if position_side == PositionSide.LONG:
        liquidation_price = entry_price * (1 - (1 / leverage) + maintenance_margin_rate)
    else:
        liquidation_price = entry_price * (1 + (1 / leverage) - maintenance_margin_rate)
    
    return liquidation_price

def calculate_unrealized_pnl(
    position: Position,
    current_price: Decimal
) -> Decimal:
    """Calculate unrealized PnL for a position"""
    if position.position_side == PositionSide.LONG:
        pnl = (current_price - position.entry_price) * position.position_amt
    else:
        pnl = (position.entry_price - current_price) * position.position_amt
    
    return pnl

def calculate_margin_ratio(
    position: Position,
    current_price: Decimal
) -> Decimal:
    """Calculate margin ratio for a position"""
    position_value = position.position_amt * current_price
    unrealized_pnl = calculate_unrealized_pnl(position, current_price)
    
    if position.margin_type == MarginType.ISOLATED:
        margin = position.isolated_margin or Decimal("0")
    else:
        margin = position_value / position.leverage
    
    total_margin = margin + unrealized_pnl
    margin_ratio = (total_margin / position_value) * 100
    
    return margin_ratio

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "futures-trading",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/contracts", response_model=List[FuturesContract])
async def get_contracts(
    contract_type: Optional[ContractType] = None
):
    """Get all available futures contracts"""
    contracts = list(contracts_db.values())
    
    if contract_type:
        contracts = [c for c in contracts if c.contract_type == contract_type]
    
    return contracts

@app.get("/contracts/{symbol}", response_model=FuturesContract)
async def get_contract(symbol: str):
    """Get specific futures contract details"""
    if symbol not in contracts_db:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    return contracts_db[symbol]

@app.post("/orders")
async def create_order(order: FuturesOrder):
    """Create a new futures order"""
    # Validate contract exists
    if order.symbol not in contracts_db:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    contract = contracts_db[order.symbol]
    
    # Validate leverage
    if order.leverage > contract.max_leverage:
        raise HTTPException(
            status_code=400,
            detail=f"Leverage exceeds maximum of {contract.max_leverage}x"
        )
    
    # Store order
    if order.user_id not in orders_db:
        orders_db[order.user_id] = []
    
    orders_db[order.user_id].append(order)
    
    # Simulate order execution for market orders
    if order.order_type == OrderType.MARKET:
        order.status = "filled"
        order.filled_quantity = order.quantity
        order.average_price = contract.mark_price
        
        # Create or update position
        await update_position(order, contract)
    
    return {
        "order_id": order.order_id,
        "status": order.status,
        "message": "Order created successfully"
    }

async def update_position(order: FuturesOrder, contract: FuturesContract):
    """Update or create position based on order"""
    if order.user_id not in positions_db:
        positions_db[order.user_id] = []
    
    # Find existing position
    existing_position = None
    for pos in positions_db[order.user_id]:
        if pos.symbol == order.symbol and pos.position_side == order.side:
            existing_position = pos
            break
    
    if existing_position:
        # Update existing position
        total_amt = existing_position.position_amt + order.filled_quantity
        total_cost = (existing_position.entry_price * existing_position.position_amt +
                     order.average_price * order.filled_quantity)
        existing_position.entry_price = total_cost / total_amt
        existing_position.position_amt = total_amt
        existing_position.updated_at = datetime.utcnow()
    else:
        # Create new position
        liquidation_price = calculate_liquidation_price(
            order.average_price,
            order.leverage,
            order.side,
            contract.maintenance_margin_rate
        )
        
        position = Position(
            user_id=order.user_id,
            symbol=order.symbol,
            position_side=order.side,
            position_amt=order.filled_quantity,
            entry_price=order.average_price,
            mark_price=contract.mark_price,
            liquidation_price=liquidation_price,
            leverage=order.leverage,
            margin_type=order.margin_type,
            unrealized_pnl=Decimal("0"),
            margin_ratio=Decimal("100")
        )
        
        if order.margin_type == MarginType.ISOLATED:
            position.isolated_margin = (order.average_price * order.filled_quantity) / order.leverage
        
        positions_db[order.user_id].append(position)

@app.get("/positions/{user_id}", response_model=List[Position])
async def get_positions(user_id: str, symbol: Optional[str] = None):
    """Get user's futures positions"""
    if user_id not in positions_db:
        return []
    
    positions = positions_db[user_id]
    
    if symbol:
        positions = [p for p in positions if p.symbol == symbol]
    
    # Update unrealized PnL and margin ratio
    for position in positions:
        if position.symbol in contracts_db:
            contract = contracts_db[position.symbol]
            position.mark_price = contract.mark_price
            position.unrealized_pnl = calculate_unrealized_pnl(position, contract.mark_price)
            position.margin_ratio = calculate_margin_ratio(position, contract.mark_price)
    
    return positions

@app.post("/positions/{user_id}/close")
async def close_position(user_id: str, symbol: str, position_side: PositionSide):
    """Close a futures position"""
    if user_id not in positions_db:
        raise HTTPException(status_code=404, detail="No positions found")
    
    # Find and remove position
    position_found = False
    for i, pos in enumerate(positions_db[user_id]):
        if pos.symbol == symbol and pos.position_side == position_side:
            # Calculate final PnL
            if symbol in contracts_db:
                contract = contracts_db[symbol]
                final_pnl = calculate_unrealized_pnl(pos, contract.mark_price)
                pos.realized_pnl += final_pnl
            
            positions_db[user_id].pop(i)
            position_found = True
            break
    
    if not position_found:
        raise HTTPException(status_code=404, detail="Position not found")
    
    return {
        "message": "Position closed successfully",
        "realized_pnl": str(pos.realized_pnl)
    }

@app.post("/leverage")
async def update_leverage(user_id: str, update: LeverageUpdate):
    """Update leverage for a symbol"""
    if update.symbol not in contracts_db:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    contract = contracts_db[update.symbol]
    
    if update.leverage > contract.max_leverage:
        raise HTTPException(
            status_code=400,
            detail=f"Leverage exceeds maximum of {contract.max_leverage}x"
        )
    
    # Store user leverage setting
    if user_id not in user_settings:
        user_settings[user_id] = {}
    
    user_settings[user_id][update.symbol] = {
        "leverage": update.leverage
    }
    
    return {
        "symbol": update.symbol,
        "leverage": update.leverage,
        "message": "Leverage updated successfully"
    }

@app.post("/margin-type")
async def update_margin_type(user_id: str, update: MarginTypeUpdate):
    """Update margin type for a symbol"""
    if update.symbol not in contracts_db:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    # Store user margin type setting
    if user_id not in user_settings:
        user_settings[user_id] = {}
    
    if update.symbol not in user_settings[user_id]:
        user_settings[user_id][update.symbol] = {}
    
    user_settings[user_id][update.symbol]["margin_type"] = update.margin_type
    
    return {
        "symbol": update.symbol,
        "margin_type": update.margin_type,
        "message": "Margin type updated successfully"
    }

@app.get("/funding-rate/{symbol}", response_model=FundingRate)
async def get_funding_rate(symbol: str):
    """Get current funding rate for a perpetual contract"""
    if symbol not in contracts_db:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    contract = contracts_db[symbol]
    
    if contract.contract_type != ContractType.PERPETUAL:
        raise HTTPException(status_code=400, detail="Funding rate only available for perpetual contracts")
    
    now = datetime.utcnow()
    next_funding = now + timedelta(hours=8)
    
    return FundingRate(
        symbol=symbol,
        funding_rate=contract.funding_rate or Decimal("0"),
        funding_time=now,
        next_funding_time=next_funding
    )

@app.get("/orders/{user_id}", response_model=List[FuturesOrder])
async def get_orders(
    user_id: str,
    symbol: Optional[str] = None,
    status: Optional[str] = None
):
    """Get user's futures orders"""
    if user_id not in orders_db:
        return []
    
    orders = orders_db[user_id]
    
    if symbol:
        orders = [o for o in orders if o.symbol == symbol]
    
    if status:
        orders = [o for o in orders if o.status == status]
    
    return orders

@app.get("/market-data/{symbol}")
async def get_market_data(symbol: str):
    """Get real-time market data for a futures contract"""
    if symbol not in contracts_db:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    contract = contracts_db[symbol]
    
    return {
        "symbol": symbol,
        "mark_price": str(contract.mark_price),
        "index_price": str(contract.index_price),
        "last_price": str(contract.last_price),
        "funding_rate": str(contract.funding_rate) if contract.funding_rate else None,
        "volume_24h": str(contract.volume_24h),
        "open_interest": str(contract.open_interest),
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8052)