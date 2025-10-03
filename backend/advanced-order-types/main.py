"""
Advanced Order Types Service
Implements Iceberg, TWAP, OCO, and other advanced order types
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from enum import Enum
import asyncio

app = FastAPI(title="Advanced Order Types", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class OrderType(str, Enum):
    ICEBERG = "iceberg"
    TWAP = "twap"
    OCO = "oco"
    POST_ONLY = "post_only"
    FOK = "fill_or_kill"
    IOC = "immediate_or_cancel"

class OrderStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

# Models
class IcebergOrder(BaseModel):
    trading_pair: str
    side: str  # buy/sell
    total_quantity: float
    visible_quantity: float
    price: float
    user_id: str

class TWAPOrder(BaseModel):
    trading_pair: str
    side: str
    total_quantity: float
    duration_minutes: int
    num_slices: int
    price_limit: Optional[float] = None
    user_id: str

class OCOOrder(BaseModel):
    trading_pair: str
    side: str
    quantity: float
    stop_price: float
    stop_limit_price: float
    limit_price: float
    user_id: str

class PostOnlyOrder(BaseModel):
    trading_pair: str
    side: str
    quantity: float
    price: float
    user_id: str

class FOKOrder(BaseModel):
    trading_pair: str
    side: str
    quantity: float
    price: float
    user_id: str

# ==================== ICEBERG ORDERS ====================

@app.post("/api/v1/orders/iceberg")
async def create_iceberg_order(order: IcebergOrder):
    """
    Create an Iceberg order
    Only shows a small portion of the total order size
    """
    
    if order.visible_quantity >= order.total_quantity:
        raise HTTPException(
            status_code=400,
            detail="Visible quantity must be less than total quantity"
        )
    
    order_id = f"iceberg_{datetime.utcnow().timestamp()}"
    
    # Calculate number of slices
    num_slices = int(order.total_quantity / order.visible_quantity)
    remaining = order.total_quantity % order.visible_quantity
    
    return {
        "success": True,
        "order_id": order_id,
        "order_type": "iceberg",
        "trading_pair": order.trading_pair,
        "side": order.side,
        "total_quantity": order.total_quantity,
        "visible_quantity": order.visible_quantity,
        "price": order.price,
        "num_slices": num_slices,
        "remaining_quantity": remaining,
        "status": OrderStatus.ACTIVE,
        "created_at": datetime.utcnow().isoformat(),
        "estimated_completion": (datetime.utcnow() + timedelta(hours=1)).isoformat()
    }

@app.get("/api/v1/orders/iceberg/{order_id}")
async def get_iceberg_order(order_id: str):
    """Get Iceberg order details"""
    
    return {
        "success": True,
        "order_id": order_id,
        "order_type": "iceberg",
        "trading_pair": "BTC/USDT",
        "side": "buy",
        "total_quantity": 10.0,
        "visible_quantity": 1.0,
        "filled_quantity": 3.5,
        "remaining_quantity": 6.5,
        "price": 50000,
        "avg_fill_price": 49950,
        "status": OrderStatus.PARTIALLY_FILLED,
        "slices_completed": 3,
        "total_slices": 10,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }

# ==================== TWAP ORDERS ====================

@app.post("/api/v1/orders/twap")
async def create_twap_order(order: TWAPOrder):
    """
    Create a TWAP (Time-Weighted Average Price) order
    Splits order into equal slices over time
    """
    
    if order.num_slices < 2:
        raise HTTPException(
            status_code=400,
            detail="Number of slices must be at least 2"
        )
    
    order_id = f"twap_{datetime.utcnow().timestamp()}"
    
    # Calculate slice details
    slice_quantity = order.total_quantity / order.num_slices
    interval_minutes = order.duration_minutes / order.num_slices
    
    slices = []
    for i in range(order.num_slices):
        execution_time = datetime.utcnow() + timedelta(minutes=interval_minutes * i)
        slices.append({
            "slice_number": i + 1,
            "quantity": slice_quantity,
            "scheduled_time": execution_time.isoformat(),
            "status": "pending"
        })
    
    return {
        "success": True,
        "order_id": order_id,
        "order_type": "twap",
        "trading_pair": order.trading_pair,
        "side": order.side,
        "total_quantity": order.total_quantity,
        "duration_minutes": order.duration_minutes,
        "num_slices": order.num_slices,
        "slice_quantity": slice_quantity,
        "interval_minutes": interval_minutes,
        "price_limit": order.price_limit,
        "slices": slices,
        "status": OrderStatus.ACTIVE,
        "created_at": datetime.utcnow().isoformat(),
        "estimated_completion": (
            datetime.utcnow() + timedelta(minutes=order.duration_minutes)
        ).isoformat()
    }

@app.get("/api/v1/orders/twap/{order_id}")
async def get_twap_order(order_id: str):
    """Get TWAP order details"""
    
    return {
        "success": True,
        "order_id": order_id,
        "order_type": "twap",
        "trading_pair": "ETH/USDT",
        "side": "buy",
        "total_quantity": 100.0,
        "filled_quantity": 45.0,
        "remaining_quantity": 55.0,
        "num_slices": 10,
        "completed_slices": 4,
        "avg_fill_price": 2995,
        "status": OrderStatus.PARTIALLY_FILLED,
        "progress_percentage": 45.0,
        "created_at": datetime.utcnow().isoformat(),
        "estimated_completion": (datetime.utcnow() + timedelta(hours=1)).isoformat()
    }

# ==================== OCO ORDERS ====================

@app.post("/api/v1/orders/oco")
async def create_oco_order(order: OCOOrder):
    """
    Create an OCO (One-Cancels-Other) order
    Two orders where execution of one cancels the other
    """
    
    order_id = f"oco_{datetime.utcnow().timestamp()}"
    
    # Create stop-limit order
    stop_order = {
        "order_id": f"{order_id}_stop",
        "type": "stop_limit",
        "stop_price": order.stop_price,
        "limit_price": order.stop_limit_price,
        "quantity": order.quantity,
        "status": "pending"
    }
    
    # Create limit order
    limit_order = {
        "order_id": f"{order_id}_limit",
        "type": "limit",
        "price": order.limit_price,
        "quantity": order.quantity,
        "status": "active"
    }
    
    return {
        "success": True,
        "order_id": order_id,
        "order_type": "oco",
        "trading_pair": order.trading_pair,
        "side": order.side,
        "quantity": order.quantity,
        "stop_order": stop_order,
        "limit_order": limit_order,
        "status": OrderStatus.ACTIVE,
        "created_at": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/orders/oco/{order_id}")
async def get_oco_order(order_id: str):
    """Get OCO order details"""
    
    return {
        "success": True,
        "order_id": order_id,
        "order_type": "oco",
        "trading_pair": "BTC/USDT",
        "side": "sell",
        "quantity": 1.0,
        "stop_order": {
            "order_id": f"{order_id}_stop",
            "type": "stop_limit",
            "stop_price": 48000,
            "limit_price": 47900,
            "status": "pending"
        },
        "limit_order": {
            "order_id": f"{order_id}_limit",
            "type": "limit",
            "price": 52000,
            "status": "active"
        },
        "status": OrderStatus.ACTIVE,
        "created_at": datetime.utcnow().isoformat()
    }

# ==================== POST-ONLY ORDERS ====================

@app.post("/api/v1/orders/post-only")
async def create_post_only_order(order: PostOnlyOrder):
    """
    Create a Post-Only order
    Only adds liquidity, never takes liquidity
    """
    
    order_id = f"post_{datetime.utcnow().timestamp()}"
    
    # Check if order would match immediately
    current_price = 50000  # Mock current price
    would_match = (
        (order.side == "buy" and order.price >= current_price) or
        (order.side == "sell" and order.price <= current_price)
    )
    
    if would_match:
        return {
            "success": False,
            "error": "Order would match immediately and is rejected (post-only)",
            "current_price": current_price,
            "order_price": order.price
        }
    
    return {
        "success": True,
        "order_id": order_id,
        "order_type": "post_only",
        "trading_pair": order.trading_pair,
        "side": order.side,
        "quantity": order.quantity,
        "price": order.price,
        "status": OrderStatus.ACTIVE,
        "maker_fee": 0.0,  # No maker fee
        "created_at": datetime.utcnow().isoformat()
    }

# ==================== FILL-OR-KILL ORDERS ====================

@app.post("/api/v1/orders/fok")
async def create_fok_order(order: FOKOrder):
    """
    Create a Fill-or-Kill order
    Must be filled completely immediately or cancelled
    """
    
    order_id = f"fok_{datetime.utcnow().timestamp()}"
    
    # Check if full quantity is available
    available_liquidity = 5.0  # Mock available liquidity
    can_fill = order.quantity <= available_liquidity
    
    if not can_fill:
        return {
            "success": False,
            "order_id": order_id,
            "order_type": "fill_or_kill",
            "status": OrderStatus.CANCELLED,
            "reason": "Insufficient liquidity to fill entire order",
            "requested_quantity": order.quantity,
            "available_liquidity": available_liquidity,
            "created_at": datetime.utcnow().isoformat()
        }
    
    return {
        "success": True,
        "order_id": order_id,
        "order_type": "fill_or_kill",
        "trading_pair": order.trading_pair,
        "side": order.side,
        "quantity": order.quantity,
        "price": order.price,
        "filled_quantity": order.quantity,
        "avg_fill_price": order.price,
        "status": OrderStatus.FILLED,
        "execution_time_ms": 15,
        "created_at": datetime.utcnow().isoformat(),
        "filled_at": datetime.utcnow().isoformat()
    }

# ==================== ORDER MANAGEMENT ====================

@app.get("/api/v1/orders/advanced")
async def list_advanced_orders(
    user_id: str,
    order_type: Optional[OrderType] = None,
    status: Optional[OrderStatus] = None
):
    """List all advanced orders for a user"""
    
    orders = [
        {
            "order_id": f"iceberg_{i}",
            "order_type": "iceberg",
            "trading_pair": "BTC/USDT",
            "side": "buy",
            "total_quantity": 10.0,
            "filled_quantity": 3.5,
            "status": "partially_filled",
            "created_at": datetime.utcnow().isoformat()
        }
        for i in range(1, 6)
    ] + [
        {
            "order_id": f"twap_{i}",
            "order_type": "twap",
            "trading_pair": "ETH/USDT",
            "side": "buy",
            "total_quantity": 100.0,
            "filled_quantity": 45.0,
            "status": "partially_filled",
            "created_at": datetime.utcnow().isoformat()
        }
        for i in range(1, 4)
    ]
    
    if order_type:
        orders = [o for o in orders if o["order_type"] == order_type]
    if status:
        orders = [o for o in orders if o["status"] == status]
    
    return {
        "success": True,
        "orders": orders,
        "total": len(orders)
    }

@app.delete("/api/v1/orders/{order_id}")
async def cancel_order(order_id: str):
    """Cancel an advanced order"""
    
    return {
        "success": True,
        "order_id": order_id,
        "status": OrderStatus.CANCELLED,
        "cancelled_at": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/orders/{order_id}/history")
async def get_order_history(order_id: str):
    """Get execution history for an order"""
    
    return {
        "success": True,
        "order_id": order_id,
        "history": [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "event": "created",
                "details": "Order created"
            },
            {
                "timestamp": datetime.utcnow().isoformat(),
                "event": "partial_fill",
                "quantity": 1.0,
                "price": 49950,
                "details": "Slice 1 filled"
            },
            {
                "timestamp": datetime.utcnow().isoformat(),
                "event": "partial_fill",
                "quantity": 1.0,
                "price": 49975,
                "details": "Slice 2 filled"
            }
        ]
    }

# ==================== ADMIN ENDPOINTS ====================

@app.get("/api/v1/admin/orders/advanced/stats")
async def get_advanced_order_stats():
    """Get statistics for advanced orders"""
    
    return {
        "success": True,
        "stats": {
            "total_orders": 1500,
            "by_type": {
                "iceberg": 600,
                "twap": 400,
                "oco": 300,
                "post_only": 150,
                "fok": 50
            },
            "by_status": {
                "active": 500,
                "partially_filled": 300,
                "filled": 600,
                "cancelled": 100
            },
            "total_volume_24h": 50000000,
            "avg_execution_time": {
                "iceberg": 3600,  # seconds
                "twap": 7200,
                "oco": 1800,
                "post_only": 300,
                "fok": 1
            }
        }
    }

@app.post("/api/v1/admin/orders/{order_id}/force-cancel")
async def admin_force_cancel(order_id: str, reason: str):
    """Admin force cancel an order"""
    
    return {
        "success": True,
        "order_id": order_id,
        "status": OrderStatus.CANCELLED,
        "reason": reason,
        "cancelled_by": "admin",
        "cancelled_at": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "advanced-order-types", "version": "3.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)