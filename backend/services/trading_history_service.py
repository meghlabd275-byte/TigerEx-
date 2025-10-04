from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
from ..database import get_db
from ..models import User, Trade, Order, Transaction
from ..auth import get_current_user
from pydantic import BaseModel

router = APIRouter()

class TradeHistoryItem(BaseModel):
    id: str
    symbol: str
    side: str
    amount: float
    price: float
    fee: float
    timestamp: datetime
    type: str

class OrderHistoryItem(BaseModel):
    id: str
    symbol: str
    side: str
    type: str
    amount: float
    price: float
    filled: float
    status: str
    timestamp: datetime

class FundingFeeItem(BaseModel):
    asset: str
    symbol: str
    amount: float
    timestamp: datetime
    type: str

@router.get("/order-history")
async def get_order_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    asset: Optional[str] = None,
    type_filter: Optional[str] = None,
    limit: int = 50
):
    """Get user's order history"""
    
    query = db.query(Order).filter(Order.user_id == current_user.id)
    
    if asset:
        query = query.filter(Order.symbol.contains(asset))
    
    if type_filter:
        query = query.filter(Order.type == type_filter)
    
    orders = query.order_by(Order.created_at.desc()).limit(limit).all()
    
    history = []
    for order in orders:
        history.append({
            "id": order.id,
            "symbol": order.symbol,
            "side": order.side,
            "type": order.type,
            "amount": order.amount,
            "price": order.price,
            "filled": order.filled_amount or 0,
            "status": order.status,
            "timestamp": order.created_at.isoformat(),
            "fee": order.fee or 0
        })
    
    return {"orders": history}

@router.get("/position-history")
async def get_position_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    asset: Optional[str] = None,
    limit: int = 50
):
    """Get user's position history"""
    
    # Get closed positions from trades
    query = db.query(Trade).filter(
        Trade.user_id == current_user.id,
        Trade.status == "closed"
    )
    
    if asset:
        query = query.filter(Trade.symbol.contains(asset))
    
    positions = query.order_by(Trade.created_at.desc()).limit(limit).all()
    
    history = []
    for position in positions:
        pnl = (position.close_price - position.entry_price) * position.amount
        if position.side == "short":
            pnl = -pnl
            
        history.append({
            "id": position.id,
            "symbol": position.symbol,
            "side": position.side,
            "entry_price": position.entry_price,
            "close_price": position.close_price,
            "amount": position.amount,
            "pnl": round(pnl, 8),
            "fee": position.fee or 0,
            "timestamp": position.created_at.isoformat(),
            "close_time": position.updated_at.isoformat() if position.updated_at else None
        })
    
    return {"positions": history}

@router.get("/trade-history")
async def get_trade_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    asset: Optional[str] = None,
    limit: int = 50
):
    """Get user's trade history"""
    
    query = db.query(Trade).filter(Trade.user_id == current_user.id)
    
    if asset:
        query = query.filter(Trade.symbol.contains(asset))
    
    trades = query.order_by(Trade.created_at.desc()).limit(limit).all()
    
    history = []
    for trade in trades:
        history.append({
            "id": trade.id,
            "symbol": trade.symbol,
            "side": trade.side,
            "amount": trade.amount,
            "price": trade.entry_price,
            "fee": trade.fee or 0,
            "timestamp": trade.created_at.isoformat(),
            "type": "Market" if trade.type == "market" else "Limit",
            "status": trade.status
        })
    
    return {"trades": history}

@router.get("/transaction-history")
async def get_transaction_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    asset: Optional[str] = None,
    type_filter: Optional[str] = None,
    limit: int = 50
):
    """Get user's transaction history"""
    
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)
    
    if asset:
        query = query.filter(Transaction.currency == asset)
    
    if type_filter:
        query = query.filter(Transaction.type == type_filter)
    
    transactions = query.order_by(Transaction.created_at.desc()).limit(limit).all()
    
    history = []
    for tx in transactions:
        history.append({
            "id": tx.id,
            "type": tx.type.replace("_", " ").title(),
            "asset": tx.currency,
            "amount": tx.amount,
            "status": tx.status,
            "timestamp": tx.created_at.isoformat(),
            "fee": tx.fee or 0,
            "from_wallet": getattr(tx, 'from_wallet', None),
            "to_wallet": getattr(tx, 'to_wallet', None)
        })
    
    return {"transactions": history}

@router.get("/funding-fee")
async def get_funding_fee_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    asset: Optional[str] = None,
    limit: int = 50
):
    """Get user's funding fee history"""
    
    # Generate sample funding fee data based on user's futures positions
    query = db.query(Trade).filter(
        Trade.user_id == current_user.id,
        Trade.symbol.contains("USDT")  # Futures contracts
    )
    
    if asset:
        query = query.filter(Trade.symbol.contains(asset))
    
    trades = query.order_by(Trade.created_at.desc()).limit(limit).all()
    
    funding_fees = []
    for trade in trades:
        # Calculate funding fee (0.01% every 8 hours for futures)
        funding_rate = 0.0001  # 0.01%
        fee_amount = trade.amount * trade.entry_price * funding_rate
        
        # Generate funding fee entries for each 8-hour period
        current_time = trade.created_at
        end_time = trade.updated_at or datetime.utcnow()
        
        while current_time < end_time:
            funding_fees.append({
                "asset": "USDT",
                "symbol": trade.symbol,
                "amount": -fee_amount,  # Negative for fee paid
                "timestamp": current_time.isoformat(),
                "type": "Funding Fee",
                "rate": funding_rate
            })
            current_time += timedelta(hours=8)
            
            if len(funding_fees) >= limit:
                break
        
        if len(funding_fees) >= limit:
            break
    
    return {"funding_fees": funding_fees[:limit]}

@router.get("/my-trades")
async def get_my_trades_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive trading overview"""
    
    # Get recent activity counts
    today = datetime.utcnow().date()
    
    orders_today = db.query(Order).filter(
        Order.user_id == current_user.id,
        Order.created_at >= today
    ).count()
    
    trades_today = db.query(Trade).filter(
        Trade.user_id == current_user.id,
        Trade.created_at >= today
    ).count()
    
    transactions_today = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.created_at >= today
    ).count()
    
    return {
        "overview": {
            "orders_today": orders_today,
            "trades_today": trades_today,
            "transactions_today": transactions_today,
            "active_positions": db.query(Trade).filter(
                Trade.user_id == current_user.id,
                Trade.status == "open"
            ).count()
        },
        "tabs": [
            {"id": "order_history", "name": "Order History", "count": orders_today},
            {"id": "position_history", "name": "Position History", "count": 0},
            {"id": "trade_history", "name": "Trade History", "count": trades_today},
            {"id": "transaction_history", "name": "Transaction History", "count": transactions_today},
            {"id": "funding_fee", "name": "Funding Fee", "count": 0}
        ]
    }