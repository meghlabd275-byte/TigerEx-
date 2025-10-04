from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
from ..database import get_db
from ..models import User, Wallet, Transaction
from ..auth import get_current_user
from pydantic import BaseModel

router = APIRouter()

class WalletType(BaseModel):
    id: str
    name: str
    balance: float
    currency: str
    icon: str
    description: str

class TransferRequest(BaseModel):
    from_wallet: str
    to_wallet: str
    coin: str
    amount: float

class TransferResponse(BaseModel):
    success: bool
    transaction_id: str
    message: str

# Wallet types configuration
WALLET_TYPES = {
    "funding": {
        "name": "Funding",
        "description": "Main funding wallet",
        "icon": "💰"
    },
    "usd_m_futures": {
        "name": "USD-M Futures",
        "description": "USD-margined futures trading",
        "icon": "📈"
    },
    "coin_m_futures": {
        "name": "COIN-M Futures", 
        "description": "Coin-margined futures trading",
        "icon": "🪙"
    },
    "cross_margin": {
        "name": "Cross Margin",
        "description": "Cross margin trading",
        "icon": "⚡"
    },
    "spot_wallet": {
        "name": "Spot Wallet",
        "description": "Spot trading wallet",
        "icon": "💎"
    },
    "earn_flexible": {
        "name": "Earn-Flexible Assets",
        "description": "Flexible earning products",
        "icon": "🌱"
    },
    "options": {
        "name": "Options",
        "description": "Options trading wallet",
        "icon": "📊"
    }
}

@router.get("/wallet-types")
async def get_wallet_types(current_user: User = Depends(get_current_user)):
    """Get all available wallet types"""
    return {
        "wallet_types": [
            {
                "id": wallet_id,
                "name": wallet_info["name"],
                "description": wallet_info["description"],
                "icon": wallet_info["icon"]
            }
            for wallet_id, wallet_info in WALLET_TYPES.items()
        ]
    }

@router.get("/wallets")
async def get_user_wallets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's wallets with balances"""
    wallets = []
    
    for wallet_id, wallet_info in WALLET_TYPES.items():
        # Get or create wallet for user
        wallet = db.query(Wallet).filter(
            Wallet.user_id == current_user.id,
            Wallet.wallet_type == wallet_id
        ).first()
        
        if not wallet:
            # Create wallet if doesn't exist
            wallet = Wallet(
                user_id=current_user.id,
                wallet_type=wallet_id,
                balance=0.0,
                currency="USDT"
            )
            db.add(wallet)
            db.commit()
            db.refresh(wallet)
        
        wallets.append({
            "id": wallet_id,
            "name": wallet_info["name"],
            "balance": wallet.balance,
            "currency": wallet.currency,
            "icon": wallet_info["icon"],
            "description": wallet_info["description"]
        })
    
    return {"wallets": wallets}

@router.post("/transfer", response_model=TransferResponse)
async def transfer_funds(
    transfer_request: TransferRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Transfer funds between wallets"""
    
    # Validate wallet types
    if transfer_request.from_wallet not in WALLET_TYPES:
        raise HTTPException(status_code=400, detail="Invalid source wallet")
    
    if transfer_request.to_wallet not in WALLET_TYPES:
        raise HTTPException(status_code=400, detail="Invalid destination wallet")
    
    if transfer_request.from_wallet == transfer_request.to_wallet:
        raise HTTPException(status_code=400, detail="Cannot transfer to same wallet")
    
    # Get source wallet
    from_wallet = db.query(Wallet).filter(
        Wallet.user_id == current_user.id,
        Wallet.wallet_type == transfer_request.from_wallet
    ).first()
    
    if not from_wallet:
        raise HTTPException(status_code=404, detail="Source wallet not found")
    
    # Check sufficient balance
    if from_wallet.balance < transfer_request.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Get or create destination wallet
    to_wallet = db.query(Wallet).filter(
        Wallet.user_id == current_user.id,
        Wallet.wallet_type == transfer_request.to_wallet
    ).first()
    
    if not to_wallet:
        to_wallet = Wallet(
            user_id=current_user.id,
            wallet_type=transfer_request.to_wallet,
            balance=0.0,
            currency=transfer_request.coin
        )
        db.add(to_wallet)
    
    # Perform transfer
    from_wallet.balance -= transfer_request.amount
    to_wallet.balance += transfer_request.amount
    
    # Create transaction record
    transaction_id = str(uuid.uuid4())
    transaction = Transaction(
        id=transaction_id,
        user_id=current_user.id,
        type="internal_transfer",
        amount=transfer_request.amount,
        currency=transfer_request.coin,
        status="completed",
        from_wallet=transfer_request.from_wallet,
        to_wallet=transfer_request.to_wallet,
        created_at=datetime.utcnow()
    )
    
    db.add(transaction)
    db.commit()
    
    return TransferResponse(
        success=True,
        transaction_id=transaction_id,
        message=f"Successfully transferred {transfer_request.amount} {transfer_request.coin} from {WALLET_TYPES[transfer_request.from_wallet]['name']} to {WALLET_TYPES[transfer_request.to_wallet]['name']}"
    )

@router.get("/transfer-history")
async def get_transfer_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """Get user's transfer history"""
    
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "internal_transfer"
    ).order_by(Transaction.created_at.desc()).limit(limit).all()
    
    history = []
    for tx in transactions:
        from_wallet_name = WALLET_TYPES.get(tx.from_wallet, {}).get("name", tx.from_wallet)
        to_wallet_name = WALLET_TYPES.get(tx.to_wallet, {}).get("name", tx.to_wallet)
        
        history.append({
            "id": tx.id,
            "amount": tx.amount,
            "currency": tx.currency,
            "from_wallet": from_wallet_name,
            "to_wallet": to_wallet_name,
            "status": tx.status,
            "created_at": tx.created_at.isoformat(),
            "type": "Internal Transfer"
        })
    
    return {"transfers": history}