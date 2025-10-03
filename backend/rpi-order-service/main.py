"""
TigerEx RPI (Retail Price Improvement) Order Service
Implements price improvement mechanism for retail traders
Based on Bybit RPI system (2025-04-01)
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum
import uuid
import random

app = FastAPI(title="TigerEx RPI Order Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(str, Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"

class TimeInForce(str, Enum):
    GTC = "GTC"  # Good Till Cancel
    IOC = "IOC"  # Immediate or Cancel
    FOK = "FOK"  # Fill or Kill
    RPI = "RPI"  # Retail Price Improvement

class OrderStatus(str, Enum):
    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

# Models
class RPIOrderRequest(BaseModel):
    symbol: str = Field(..., description="Trading pair symbol")
    side: OrderSide = Field(..., description="Buy or Sell")
    order_type: OrderType = Field(..., description="Order type")
    quantity: float = Field(..., gt=0, description="Order quantity")
    price: Optional[float] = Field(default=None, description="Limit price (required for LIMIT orders)")
    time_in_force: TimeInForce = Field(default=TimeInForce.RPI, description="Time in force")
    max_price_improvement: Optional[float] = Field(default=0.001, description="Max price improvement (0.1%)")

class RPIExecution(BaseModel):
    execution_id: str
    order_id: str
    price: float
    quantity: float
    is_rpi_trade: bool
    price_improvement: float
    price_improvement_percentage: float
    timestamp: datetime

class RPIOrder(BaseModel):
    order_id: str
    user_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float]
    time_in_force: TimeInForce
    status: OrderStatus
    filled_quantity: float
    average_price: Optional[float]
    executions: List[RPIExecution]
    total_price_improvement: float
    created_at: datetime
    updated_at: datetime

# In-memory storage
order_storage: Dict[str, RPIOrder] = {}
execution_storage: Dict[str, RPIExecution] = {}

def calculate_rpi_price(order: RPIOrderRequest, market_price: float) -> tuple:
    """
    Calculate RPI execution price
    Returns: (execution_price, price_improvement, is_rpi_trade)
    """
    if order.time_in_force != TimeInForce.RPI:
        return market_price, 0.0, False
    
    # Simulate price improvement opportunity (70% chance)
    has_improvement = random.random() < 0.7
    
    if not has_improvement:
        return market_price, 0.0, False
    
    # Calculate improved price
    max_improvement = order.max_price_improvement or 0.001
    improvement_factor = random.uniform(0.0001, max_improvement)
    
    if order.side == OrderSide.BUY:
        # For buy orders, improve by reducing price
        improved_price = market_price * (1 - improvement_factor)
        price_improvement = market_price - improved_price
    else:
        # For sell orders, improve by increasing price
        improved_price = market_price * (1 + improvement_factor)
        price_improvement = improved_price - market_price
    
    return improved_price, price_improvement, True

@app.get("/")
async def root():
    return {
        "service": "TigerEx RPI Order Service",
        "version": "1.0.0",
        "status": "operational"
    }

@app.post("/api/v1/rpi/order", response_model=RPIOrder)
async def create_rpi_order(request: RPIOrderRequest, user_id: str = "user_001"):
    """
    Create a new RPI order
    """
    # Validate
    if request.order_type == OrderType.LIMIT and request.price is None:
        raise HTTPException(status_code=400, detail="Price is required for LIMIT orders")
    
    order_id = f"rpi_{uuid.uuid4().hex[:16]}"
    created_at = datetime.utcnow()
    
    # Create order
    order = RPIOrder(
        order_id=order_id,
        user_id=user_id,
        symbol=request.symbol,
        side=request.side,
        order_type=request.order_type,
        quantity=request.quantity,
        price=request.price,
        time_in_force=request.time_in_force,
        status=OrderStatus.NEW,
        filled_quantity=0.0,
        average_price=None,
        executions=[],
        total_price_improvement=0.0,
        created_at=created_at,
        updated_at=created_at
    )
    
    order_storage[order_id] = order
    
    # Simulate immediate execution for market orders
    if request.order_type == OrderType.MARKET:
        market_price = 50000.0  # Simulated market price
        execution_price, price_improvement, is_rpi = calculate_rpi_price(request, market_price)
        
        execution = RPIExecution(
            execution_id=f"exec_{uuid.uuid4().hex[:16]}",
            order_id=order_id,
            price=execution_price,
            quantity=request.quantity,
            is_rpi_trade=is_rpi,
            price_improvement=price_improvement,
            price_improvement_percentage=(price_improvement / market_price * 100) if price_improvement > 0 else 0,
            timestamp=datetime.utcnow()
        )
        
        execution_storage[execution.execution_id] = execution
        order.executions.append(execution)
        order.filled_quantity = request.quantity
        order.average_price = execution_price
        order.total_price_improvement = price_improvement
        order.status = OrderStatus.FILLED
        order.updated_at = datetime.utcnow()
    
    return order

@app.get("/api/v1/rpi/order/{order_id}", response_model=RPIOrder)
async def get_rpi_order(order_id: str):
    """
    Get RPI order details
    """
    order = order_storage.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order

@app.get("/api/v1/rpi/orders")
async def get_rpi_orders(user_id: str = "user_001", limit: int = 50):
    """
    Get user's RPI orders
    """
    user_orders = [order for order in order_storage.values() if order.user_id == user_id]
    user_orders.sort(key=lambda x: x.created_at, reverse=True)
    
    return {
        "total": len(user_orders),
        "orders": user_orders[:limit]
    }

@app.delete("/api/v1/rpi/order/{order_id}")
async def cancel_rpi_order(order_id: str):
    """
    Cancel an RPI order
    """
    order = order_storage.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail="Cannot cancel filled or already cancelled order")
    
    order.status = OrderStatus.CANCELLED
    order.updated_at = datetime.utcnow()
    
    return {
        "status": "success",
        "order_id": order_id,
        "message": "Order cancelled successfully"
    }

@app.get("/api/v1/rpi/statistics")
async def get_rpi_statistics(user_id: Optional[str] = None):
    """
    Get RPI statistics
    """
    orders = list(order_storage.values())
    if user_id:
        orders = [o for o in orders if o.user_id == user_id]
    
    total_orders = len(orders)
    rpi_orders = [o for o in orders if o.time_in_force == TimeInForce.RPI]
    rpi_executions = [e for o in rpi_orders for e in o.executions if e.is_rpi_trade]
    
    total_improvement = sum(e.price_improvement for e in rpi_executions)
    avg_improvement = (total_improvement / len(rpi_executions)) if rpi_executions else 0
    
    return {
        "total_orders": total_orders,
        "rpi_orders": len(rpi_orders),
        "rpi_executions": len(rpi_executions),
        "rpi_success_rate": (len(rpi_executions) / len(rpi_orders) * 100) if rpi_orders else 0,
        "total_price_improvement": total_improvement,
        "average_price_improvement": avg_improvement,
        "estimated_savings_usd": total_improvement
    }

@app.get("/api/v1/rpi/orderbook/{symbol}")
async def get_rpi_orderbook(symbol: str):
    """
    Get orderbook with RPI quotes
    """
    # Simulated orderbook with RPI indicators
    base_price = 50000.0
    
    bids = []
    asks = []
    
    for i in range(10):
        bid_price = base_price - (i * 10)
        ask_price = base_price + (i * 10)
        
        bids.append({
            "price": bid_price,
            "quantity": random.uniform(0.1, 2.0),
            "rpi_available": random.random() < 0.3
        })
        
        asks.append({
            "price": ask_price,
            "quantity": random.uniform(0.1, 2.0),
            "rpi_available": random.random() < 0.3
        })
    
    return {
        "symbol": symbol,
        "timestamp": datetime.utcnow(),
        "bids": bids,
        "asks": asks,
        "rpi_enabled": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)