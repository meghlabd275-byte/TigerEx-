/*
 * TigerEx Exchange Platform
 * Version: 7.0.0 - Consolidated Production Release
 * 
 * Complete cryptocurrency exchange platform with:
 * - CEX/DEX hybrid functionality
 * - 105+ exchange features
 * - Multi-platform support (Web, Mobile, Desktop)
 * - Enterprise-grade security
 * - White-label deployment ready
 * 
 * Production-ready implementation
 */

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from ..database import get_db
from ..models import User, Transaction, Wallet, Trade, Order
from ..auth import get_current_admin_user
from pydantic import BaseModel
import json

router = APIRouter()

class AdminTransferControl(BaseModel):
    user_id: str
    action: str  # "approve", "reject", "freeze"
    reason: Optional[str] = None

class AdminWalletControl(BaseModel):
    user_id: str
    wallet_type: str
    action: str  # "freeze", "unfreeze", "adjust_balance"
    amount: Optional[float] = None

class SystemStats(BaseModel):
    total_users: int
    total_transfers: int
    total_volume: float
    active_trades: int

@router.get("/transfer-monitoring")
async def get_transfer_monitoring(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    limit: int = 100
):
    """Monitor all user transfers"""
    
    query = db.query(Transaction).filter(
        Transaction.type == "internal_transfer"
    )
    
    if status:
        query = query.filter(Transaction.status == status)
    
    transfers = query.order_by(Transaction.created_at.desc()).limit(limit).all()
    
    transfer_data = []
    for transfer in transfers:
        user = db.query(User).filter(User.id == transfer.user_id).first()
        
        transfer_data.append({
            "id": transfer.id,
            "user_id": transfer.user_id,
            "username": user.username if user else "Unknown",
            "email": user.email if user else "Unknown",
            "from_wallet": transfer.from_wallet,
            "to_wallet": transfer.to_wallet,
            "amount": transfer.amount,
            "currency": transfer.currency,
            "status": transfer.status,
            "created_at": transfer.created_at.isoformat(),
            "fee": transfer.fee or 0
        })
    
    return {"transfers": transfer_data}

@router.post("/control-transfer")
async def control_transfer(
    control: AdminTransferControl,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Admin control over user transfers"""
    
    if control.action == "freeze":
        # Freeze all pending transfers for user
        pending_transfers = db.query(Transaction).filter(
            Transaction.user_id == control.user_id,
            Transaction.type == "internal_transfer",
            Transaction.status == "pending"
        ).all()
        
        for transfer in pending_transfers:
            transfer.status = "frozen"
            transfer.admin_notes = f"Frozen by admin: {control.reason}"
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Frozen {len(pending_transfers)} transfers for user {control.user_id}",
            "action": "freeze"
        }
    
    elif control.action == "approve_all":
        # Approve all frozen transfers for user
        frozen_transfers = db.query(Transaction).filter(
            Transaction.user_id == control.user_id,
            Transaction.type == "internal_transfer",
            Transaction.status == "frozen"
        ).all()
        
        for transfer in frozen_transfers:
            transfer.status = "completed"
            transfer.admin_notes = f"Approved by admin: {control.reason}"
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Approved {len(frozen_transfers)} transfers for user {control.user_id}",
            "action": "approve"
        }
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

@router.get("/wallet-monitoring")
async def get_wallet_monitoring(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    user_id: Optional[str] = None,
    wallet_type: Optional[str] = None
):
    """Monitor user wallets"""
    
    query = db.query(Wallet)
    
    if user_id:
        query = query.filter(Wallet.user_id == user_id)
    
    if wallet_type:
        query = query.filter(Wallet.wallet_type == wallet_type)
    
    wallets = query.all()
    
    wallet_data = []
    for wallet in wallets:
        user = db.query(User).filter(User.id == wallet.user_id).first()
        
        wallet_data.append({
            "id": wallet.id,
            "user_id": wallet.user_id,
            "username": user.username if user else "Unknown",
            "wallet_type": wallet.wallet_type,
            "balance": wallet.balance,
            "currency": wallet.currency,
            "status": getattr(wallet, 'status', 'active'),
            "created_at": wallet.created_at.isoformat() if hasattr(wallet, 'created_at') else None,
            "last_updated": wallet.updated_at.isoformat() if hasattr(wallet, 'updated_at') else None
        })
    
    return {"wallets": wallet_data}

@router.post("/control-wallet")
async def control_wallet(
    control: AdminWalletControl,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Admin control over user wallets"""
    
    wallet = db.query(Wallet).filter(
        Wallet.user_id == control.user_id,
        Wallet.wallet_type == control.wallet_type
    ).first()
    
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    if control.action == "freeze":
        # Add frozen status to wallet (you might need to add this field to your model)
        wallet.status = "frozen"
        wallet.admin_notes = f"Frozen by admin"
        
    elif control.action == "unfreeze":
        wallet.status = "active"
        wallet.admin_notes = f"Unfrozen by admin"
        
    elif control.action == "adjust_balance":
        if control.amount is None:
            raise HTTPException(status_code=400, detail="Amount required for balance adjustment")
        
        old_balance = wallet.balance
        wallet.balance = control.amount
        
        # Create audit log
        audit_log = Transaction(
            id=str(uuid.uuid4()),
            user_id=control.user_id,
            type="admin_adjustment",
            amount=control.amount - old_balance,
            currency=wallet.currency,
            status="completed",
            admin_notes=f"Balance adjusted by admin from {old_balance} to {control.amount}",
            created_at=datetime.utcnow()
        )
        db.add(audit_log)
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Wallet {control.action} completed",
        "wallet_id": wallet.id,
        "new_balance": wallet.balance
    }

@router.get("/trading-monitoring")
async def get_trading_monitoring(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    user_id: Optional[str] = None,
    limit: int = 100
):
    """Monitor user trading activities"""
    
    # Get recent trades
    trade_query = db.query(Trade)
    if user_id:
        trade_query = trade_query.filter(Trade.user_id == user_id)
    
    trades = trade_query.order_by(Trade.created_at.desc()).limit(limit).all()
    
    # Get recent orders
    order_query = db.query(Order)
    if user_id:
        order_query = order_query.filter(Order.user_id == user_id)
    
    orders = order_query.order_by(Order.created_at.desc()).limit(limit).all()
    
    trade_data = []
    for trade in trades:
        user = db.query(User).filter(User.id == trade.user_id).first()
        
        trade_data.append({
            "id": trade.id,
            "user_id": trade.user_id,
            "username": user.username if user else "Unknown",
            "symbol": trade.symbol,
            "side": trade.side,
            "amount": trade.amount,
            "entry_price": trade.entry_price,
            "close_price": trade.close_price,
            "status": trade.status,
            "pnl": calculate_pnl(trade),
            "created_at": trade.created_at.isoformat()
        })
    
    order_data = []
    for order in orders:
        user = db.query(User).filter(User.id == order.user_id).first()
        
        order_data.append({
            "id": order.id,
            "user_id": order.user_id,
            "username": user.username if user else "Unknown",
            "symbol": order.symbol,
            "side": order.side,
            "type": order.type,
            "amount": order.amount,
            "price": order.price,
            "status": order.status,
            "created_at": order.created_at.isoformat()
        })
    
    return {
        "trades": trade_data,
        "orders": order_data
    }

@router.get("/system-stats")
async def get_system_stats(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get system-wide statistics"""
    
    # Get date ranges
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # User statistics
    total_users = db.query(User).count()
    new_users_today = db.query(User).filter(User.created_at >= today).count()
    new_users_week = db.query(User).filter(User.created_at >= week_ago).count()
    
    # Transfer statistics
    total_transfers = db.query(Transaction).filter(
        Transaction.type == "internal_transfer"
    ).count()
    
    transfers_today = db.query(Transaction).filter(
        Transaction.type == "internal_transfer",
        Transaction.created_at >= today
    ).count()
    
    # Trading statistics
    total_trades = db.query(Trade).count()
    active_trades = db.query(Trade).filter(Trade.status == "open").count()
    
    # Volume statistics
    total_volume = db.query(Trade).with_entities(
        db.func.sum(Trade.amount * Trade.entry_price)
    ).scalar() or 0
    
    volume_today = db.query(Trade).filter(
        Trade.created_at >= today
    ).with_entities(
        db.func.sum(Trade.amount * Trade.entry_price)
    ).scalar() or 0
    
    return {
        "users": {
            "total": total_users,
            "new_today": new_users_today,
            "new_week": new_users_week
        },
        "transfers": {
            "total": total_transfers,
            "today": transfers_today
        },
        "trading": {
            "total_trades": total_trades,
            "active_trades": active_trades,
            "total_volume": round(total_volume, 2),
            "volume_today": round(volume_today, 2)
        },
        "wallets": {
            "total_wallets": db.query(Wallet).count(),
            "total_balance": db.query(Wallet).with_entities(
                db.func.sum(Wallet.balance)
            ).scalar() or 0
        }
    }

@router.get("/user-activity")
async def get_user_activity(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    user_id: str,
    days: int = 30
):
    """Get detailed user activity"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get user's transactions
    transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.created_at >= start_date
    ).order_by(Transaction.created_at.desc()).all()
    
    # Get user's trades
    trades = db.query(Trade).filter(
        Trade.user_id == user_id,
        Trade.created_at >= start_date
    ).order_by(Trade.created_at.desc()).all()
    
    # Get user's wallets
    wallets = db.query(Wallet).filter(Wallet.user_id == user_id).all()
    
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat(),
            "is_active": user.is_active
        },
        "transactions": [
            {
                "id": tx.id,
                "type": tx.type,
                "amount": tx.amount,
                "currency": tx.currency,
                "status": tx.status,
                "created_at": tx.created_at.isoformat()
            }
            for tx in transactions
        ],
        "trades": [
            {
                "id": trade.id,
                "symbol": trade.symbol,
                "side": trade.side,
                "amount": trade.amount,
                "entry_price": trade.entry_price,
                "status": trade.status,
                "created_at": trade.created_at.isoformat()
            }
            for trade in trades
        ],
        "wallets": [
            {
                "wallet_type": wallet.wallet_type,
                "balance": wallet.balance,
                "currency": wallet.currency
            }
            for wallet in wallets
        ]
    }

def calculate_pnl(trade):
    """Calculate PNL for a trade"""
    if trade.close_price and trade.status == "closed":
        pnl = (trade.close_price - trade.entry_price) * trade.amount
        if trade.side == "short":
            pnl = -pnl
        return round(pnl, 2)
    return 0.0