"""
TigerEx Trading Engine Admin Routes
Complete administrative controls for the trading engine
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Admin models
class TradingControlRequest(BaseModel):
    action: str  # pause, resume, emergency_stop
    symbol: Optional[str] = None
    reason: str

class RiskConfigRequest(BaseModel):
    max_order_size: float
    max_daily_volume: float
    max_position_size: float
    price_deviation_threshold: float
    circuit_breaker_threshold: float

class UserTradingLimits(BaseModel):
    user_id: str
    max_order_size: float
    max_daily_orders: int
    max_open_positions: int
    leverage_limit: float

# In-memory storage for admin settings (in production, use database)
admin_settings = {
    "trading_status": "active",  # active, paused, emergency_stop
    "paused_symbols": set(),
    "risk_config": {
        "max_order_size": 1000000.0,
        "max_daily_volume": 10000000.0,
        "max_position_size": 5000000.0,
        "price_deviation_threshold": 0.1,  # 10%
        "circuit_breaker_threshold": 0.2   # 20%
    },
    "user_limits": {},
    "emergency_actions": []
}

@router.get("/system/status")
async def get_system_status():
    """Get overall system status"""
    try:
        # Import trading engine from parent module
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from main import trading_engine
        
        # Get current stats
        stats = await trading_engine.get_trading_stats()
        
        return {
            "status": "operational",
            "trading_status": admin_settings["trading_status"],
            "paused_symbols": list(admin_settings["paused_symbols"]),
            "active_order_books": stats["active_order_books"],
            "total_orders": stats["total_orders"],
            "websocket_connections": stats["websocket_connections"],
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "order_matching": "active",
                "risk_management": "active",
                "liquidity_aggregation": "active",
                "market_data": "active"
            }
        }
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/system/trading-control")
async def control_trading(request: TradingControlRequest):
    """Control trading operations"""
    try:
        action = request.action.lower()
        symbol = request.symbol
        
        if action == "pause":
            if symbol:
                admin_settings["paused_symbols"].add(symbol)
            else:
                admin_settings["trading_status"] = "paused"
        
        elif action == "resume":
            if symbol:
                admin_settings["paused_symbols"].discard(symbol)
            else:
                admin_settings["trading_status"] = "active"
        
        elif action == "emergency_stop":
            admin_settings["trading_status"] = "emergency_stop"
            # Cancel all open orders
            await emergency_cancel_all_orders()
        
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        # Log emergency action
        admin_settings["emergency_actions"].append({
            "action": action,
            "symbol": symbol,
            "reason": request.reason,
            "timestamp": datetime.utcnow().isoformat(),
            "admin": "system"
        })
        
        return {
            "success": True,
            "action": action,
            "symbol": symbol,
            "trading_status": admin_settings["trading_status"],
            "paused_symbols": list(admin_settings["paused_symbols"]),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to control trading: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders/all")
async def get_all_orders(
    symbol: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """Get all orders with admin access"""
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from main import trading_engine
        
        all_orders = []
        
        for book_symbol, order_book in trading_engine.order_books.items():
            if symbol and book_symbol != symbol:
                continue
            
            for order in order_book.orders.values():
                if status and order.status.value != status:
                    continue
                
                all_orders.append({
                    "id": order.id,
                    "user_id": order.user_id,
                    "symbol": order.symbol,
                    "side": order.side.value,
                    "type": order.order_type.value,
                    "quantity": str(order.quantity),
                    "price": str(order.price) if order.price else None,
                    "filled_quantity": str(order.filled_quantity),
                    "remaining_quantity": str(order.remaining_quantity),
                    "status": order.status.value,
                    "created_at": order.created_at.isoformat(),
                    "updated_at": order.updated_at.isoformat()
                })
        
        # Sort and paginate
        all_orders.sort(key=lambda x: x['created_at'], reverse=True)
        paginated_orders = all_orders[offset:offset + limit]
        
        return {
            "orders": paginated_orders,
            "total": len(all_orders),
            "limit": limit,
            "offset": offset,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to get all orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/orders/{order_id}")
async def admin_cancel_order(order_id: str, reason: str = "Admin cancellation"):
    """Cancel any order (admin override)"""
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from main import trading_engine
        
        # Find and cancel the order
        success = await trading_engine.cancel_order(order_id, "admin")
        
        if success:
            # Log admin action
            admin_settings["emergency_actions"].append({
                "action": "order_cancelled",
                "order_id": order_id,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat(),
                "admin": "system"
            })
        
        return {"success": success, "order_id": order_id, "reason": reason}
    
    except Exception as e:
        logger.error(f"Failed to cancel order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/orders/cancel-all")
async def cancel_all_orders(symbol: Optional[str] = None, reason: str = "Mass cancellation"):
    """Cancel all orders (admin emergency function)"""
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from main import trading_engine
        
        cancelled_orders = []
        
        for book_symbol, order_book in trading_engine.order_books.items():
            if symbol and book_symbol != symbol:
                continue
            
            order_ids = list(order_book.orders.keys())
            for order_id in order_ids:
                try:
                    success = await trading_engine.cancel_order(order_id, "admin")
                    if success:
                        cancelled_orders.append(order_id)
                except:
                    continue
        
        # Log admin action
        admin_settings["emergency_actions"].append({
            "action": "mass_cancel",
            "symbol": symbol,
            "cancelled_count": len(cancelled_orders),
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
            "admin": "system"
        })
        
        return {
            "success": True,
            "cancelled_orders": len(cancelled_orders),
            "symbol": symbol,
            "order_ids": cancelled_orders[:100],  # Return first 100 order IDs
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to cancel all orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/orders")
async def get_user_orders_admin(user_id: str):
    """Get all orders for a specific user (admin view)"""
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from main import trading_engine
        
        user_orders = await trading_engine.get_user_orders(user_id)
        
        # Get additional user statistics
        total_orders = len(user_orders)
        filled_orders = [o for o in user_orders if o['status'] == 'filled']
        cancelled_orders = [o for o in user_orders if o['status'] == 'cancelled']
        
        total_volume = sum(
            float(o['filled_quantity']) * (float(o['price']) if o['price'] else 0)
            for o in filled_orders
        )
        
        return {
            "user_id": user_id,
            "orders": user_orders,
            "statistics": {
                "total_orders": total_orders,
                "filled_orders": len(filled_orders),
                "cancelled_orders": len(cancelled_orders),
                "total_volume": str(total_volume),
                "success_rate": len(filled_orders) / total_orders if total_orders > 0 else 0
            },
            "limits": admin_settings["user_limits"].get(user_id, {}),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to get user orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/{user_id}/limits")
async def set_user_limits(user_id: str, limits: UserTradingLimits):
    """Set trading limits for a specific user"""
    try:
        admin_settings["user_limits"][user_id] = {
            "max_order_size": limits.max_order_size,
            "max_daily_orders": limits.max_daily_orders,
            "max_open_positions": limits.max_open_positions,
            "leverage_limit": limits.leverage_limit,
            "updated_at": datetime.utcnow().isoformat(),
            "updated_by": "admin"
        }
        
        # Log admin action
        admin_settings["emergency_actions"].append({
            "action": "user_limits_updated",
            "user_id": user_id,
            "limits": limits.dict(),
            "timestamp": datetime.utcnow().isoformat(),
            "admin": "system"
        })
        
        return {
            "success": True,
            "user_id": user_id,
            "limits": admin_settings["user_limits"][user_id],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to set user limits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/risk/config")
async def get_risk_config():
    """Get current risk management configuration"""
    return {
        "risk_config": admin_settings["risk_config"],
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/risk/config")
async def update_risk_config(config: RiskConfigRequest):
    """Update risk management configuration"""
    try:
        admin_settings["risk_config"] = {
            "max_order_size": config.max_order_size,
            "max_daily_volume": config.max_daily_volume,
            "max_position_size": config.max_position_size,
            "price_deviation_threshold": config.price_deviation_threshold,
            "circuit_breaker_threshold": config.circuit_breaker_threshold,
            "updated_at": datetime.utcnow().isoformat(),
            "updated_by": "admin"
        }
        
        # Log admin action
        admin_settings["emergency_actions"].append({
            "action": "risk_config_updated",
            "config": config.dict(),
            "timestamp": datetime.utcnow().isoformat(),
            "admin": "system"
        })
        
        return {
            "success": True,
            "risk_config": admin_settings["risk_config"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to update risk config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audit/log")
async def get_audit_log(
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """Get admin action audit log"""
    try:
        all_actions = admin_settings["emergency_actions"]
        all_actions.sort(key=lambda x: x['timestamp'], reverse=True)
        
        paginated_actions = all_actions[offset:offset + limit]
        
        return {
            "actions": paginated_actions,
            "total": len(all_actions),
            "limit": limit,
            "offset": offset,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to get audit log: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/overview")
async def get_analytics_overview():
    """Get comprehensive analytics overview"""
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from main import trading_engine
        
        stats = await trading_engine.get_trading_stats()
        
        # Calculate additional metrics
        total_order_books = len(trading_engine.order_books)
        paused_order_books = len(admin_settings["paused_symbols"])
        active_order_books = total_order_books - paused_order_books
        
        # Get order distribution by status
        status_distribution = {}
        symbol_distribution = {}
        
        for symbol, order_book in trading_engine.order_books.items():
            symbol_orders = len(order_book.orders)
            symbol_distribution[symbol] = symbol_orders
            
            for order in order_book.orders.values():
                status = order.status.value
                status_distribution[status] = status_distribution.get(status, 0) + 1
        
        return {
            "trading_overview": {
                "total_orders": stats["total_orders"],
                "total_volume_24h": stats["total_volume_24h"],
                "active_order_books": active_order_books,
                "paused_order_books": paused_order_books,
                "websocket_connections": stats["websocket_connections"]
            },
            "order_distribution": {
                "by_status": status_distribution,
                "by_symbol": symbol_distribution
            },
            "system_health": {
                "trading_status": admin_settings["trading_status"],
                "paused_symbols": list(admin_settings["paused_symbols"]),
                "risk_config": admin_settings["risk_config"],
                "user_limits_count": len(admin_settings["user_limits"])
            },
            "recent_actions": admin_settings["emergency_actions"][-10:],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to get analytics overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def emergency_cancel_all_orders():
    """Emergency function to cancel all orders"""
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from main import trading_engine
        
        cancelled_count = 0
        for symbol, order_book in trading_engine.order_books.items():
            order_ids = list(order_book.orders.keys())
            for order_id in order_ids:
                try:
                    success = await trading_engine.cancel_order(order_id, "admin")
                    if success:
                        cancelled_count += 1
                except:
                    continue
        
        logger.info(f"Emergency cancelled {cancelled_count} orders")
        return cancelled_count
    
    except Exception as e:
        logger.error(f"Emergency cancel failed: {e}")
        return 0

@router.get("/health")
async def admin_health():
    """Admin endpoint health check"""
    return {
        "status": "healthy",
        "service": "trading-engine-admin",
        "version": "4.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "order_management",
            "trading_control",
            "risk_management",
            "user_management",
            "audit_logging",
            "analytics"
        ]
    }