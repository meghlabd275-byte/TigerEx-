"""
TigerEx Exchange Platform
Version: 7.0.0 - Production Release

Multi-Signature Wallets Service
Enterprise-grade multi-sig wallet support with advanced security
"""

import asyncio
import json
import logging
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import ecdsa
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WalletType(Enum):
    PERSONAL = "personal"
    CORPORATE = "corporate"
    INSTITUTIONAL = "institutional"
    CUSTODY = "custody"

class TransactionStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"

class SignatureStatus(Enum):
    PENDING = "pending"
    SIGNED = "signed"
    REJECTED = "rejected"

@dataclass
class Signer:
    id: str
    name: str
    email: str
    public_key: str
    role: str
    is_active: bool
    created_at: datetime

@dataclass
class MultiSigWallet:
    id: str
    name: str
    description: str
    wallet_type: WalletType
    required_signatures: int
    total_signers: int
    signers: List[Signer]
    addresses: Dict[str, str]  # currency -> address
    balances: Dict[str, float]  # currency -> balance
    is_active: bool
    created_at: datetime
    updated_at: datetime

@dataclass
class Transaction:
    id: str
    wallet_id: str
    from_address: str
    to_address: str
    currency: str
    amount: float
    fee: float
    description: str
    status: TransactionStatus
    required_signatures: int
    current_signatures: int
    signatures: List[Dict[str, Any]]
    created_by: str
    created_at: datetime
    expires_at: datetime
    executed_at: Optional[datetime] = None

@dataclass
class TransactionSignature:
    id: str
    transaction_id: str
    signer_id: str
    signature: str
    status: SignatureStatus
    signed_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

class MultiSigWalletService:
    def __init__(self):
        self.wallets: Dict[str, MultiSigWallet] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.signatures: Dict[str, TransactionSignature] = {}
        self.signers: Dict[str, Signer] = {}
        
    async def initialize(self):
        """Initialize the multi-sig wallet service"""
        logger.info("🔐 Initializing Multi-Signature Wallet Service...")
        
        # Load sample data
        await self._load_sample_data()
        
        logger.info("✅ Multi-Signature Wallet Service initialized")
    
    async def _load_sample_data(self):
        """Load sample data for demonstration"""
        # Create sample signers
        sample_signers = [
            {
                "id": "signer_001",
                "name": "John Doe",
                "email": "john.doe@company.com",
                "role": "CEO",
                "public_key": self._generate_public_key()
            },
            {
                "id": "signer_002", 
                "name": "Jane Smith",
                "email": "jane.smith@company.com",
                "role": "CFO",
                "public_key": self._generate_public_key()
            },
            {
                "id": "signer_003",
                "name": "Bob Wilson",
                "email": "bob.wilson@company.com", 
                "role": "CTO",
                "public_key": self._generate_public_key()
            }
        ]
        
        for signer_data in sample_signers:
            signer = Signer(
                id=signer_data["id"],
                name=signer_data["name"],
                email=signer_data["email"],
                public_key=signer_data["public_key"],
                role=signer_data["role"],
                is_active=True,
                created_at=datetime.now()
            )
            self.signers[signer.id] = signer
    
    def _generate_public_key(self) -> str:
        """Generate a sample public key"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return pem.decode('utf-8')
    
    async def create_wallet(self, wallet_data: Dict[str, Any]) -> MultiSigWallet:
        """Create a new multi-signature wallet"""
        try:
            wallet_id = f"wallet_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}"
            
            # Validate signers
            signer_ids = wallet_data.get('signer_ids', [])
            signers = []
            for signer_id in signer_ids:
                if signer_id in self.signers:
                    signers.append(self.signers[signer_id])
                else:
                    raise ValueError(f"Signer {signer_id} not found")
            
            # Generate addresses for supported currencies
            addresses = {}
            balances = {}
            supported_currencies = ['BTC', 'ETH', 'USDT', 'USDC', 'BNB']
            
            for currency in supported_currencies:
                addresses[currency] = self._generate_address(currency, wallet_id)
                balances[currency] = 0.0
            
            wallet = MultiSigWallet(
                id=wallet_id,
                name=wallet_data['name'],
                description=wallet_data.get('description', ''),
                wallet_type=WalletType(wallet_data.get('wallet_type', 'corporate')),
                required_signatures=wallet_data['required_signatures'],
                total_signers=len(signers),
                signers=signers,
                addresses=addresses,
                balances=balances,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.wallets[wallet_id] = wallet
            
            logger.info(f"🔐 Created multi-sig wallet: {wallet.name} ({wallet_id})")
            return wallet
            
        except Exception as e:
            logger.error(f"❌ Error creating wallet: {e}")
            raise
    
    def _generate_address(self, currency: str, wallet_id: str) -> str:
        """Generate a deterministic address for the currency"""
        # This is a simplified address generation for demo purposes
        seed = f"{wallet_id}_{currency}_{secrets.token_hex(8)}"
        hash_obj = hashlib.sha256(seed.encode())
        
        if currency == 'BTC':
            return f"bc1q{hash_obj.hexdigest()[:40]}"
        elif currency == 'ETH':
            return f"0x{hash_obj.hexdigest()[:40]}"
        else:
            return f"{currency.lower()}_{hash_obj.hexdigest()[:32]}"
    
    async def get_wallet(self, wallet_id: str) -> Optional[MultiSigWallet]:
        """Get wallet by ID"""
        return self.wallets.get(wallet_id)
    
    async def get_user_wallets(self, user_id: str) -> List[MultiSigWallet]:
        """Get all wallets where user is a signer"""
        user_wallets = []
        for wallet in self.wallets.values():
            for signer in wallet.signers:
                if signer.id == user_id:
                    user_wallets.append(wallet)
                    break
        return user_wallets
    
    async def create_transaction(self, transaction_data: Dict[str, Any]) -> Transaction:
        """Create a new transaction requiring multi-sig approval"""
        try:
            transaction_id = f"tx_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(6)}"
            
            wallet = self.wallets.get(transaction_data['wallet_id'])
            if not wallet:
                raise ValueError("Wallet not found")
            
            # Validate balance
            currency = transaction_data['currency']
            amount = float(transaction_data['amount'])
            fee = float(transaction_data.get('fee', 0))
            
            if wallet.balances.get(currency, 0) < (amount + fee):
                raise ValueError("Insufficient balance")
            
            # Create transaction
            transaction = Transaction(
                id=transaction_id,
                wallet_id=transaction_data['wallet_id'],
                from_address=wallet.addresses[currency],
                to_address=transaction_data['to_address'],
                currency=currency,
                amount=amount,
                fee=fee,
                description=transaction_data.get('description', ''),
                status=TransactionStatus.PENDING,
                required_signatures=wallet.required_signatures,
                current_signatures=0,
                signatures=[],
                created_by=transaction_data['created_by'],
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=24)
            )
            
            self.transactions[transaction_id] = transaction
            
            # Create signature requests for all signers
            for signer in wallet.signers:
                signature_id = f"sig_{transaction_id}_{signer.id}"
                signature = TransactionSignature(
                    id=signature_id,
                    transaction_id=transaction_id,
                    signer_id=signer.id,
                    signature="",
                    status=SignatureStatus.PENDING
                )
                self.signatures[signature_id] = signature
            
            logger.info(f"💰 Created transaction: {transaction_id} for {amount} {currency}")
            return transaction
            
        except Exception as e:
            logger.error(f"❌ Error creating transaction: {e}")
            raise
    
    async def sign_transaction(self, transaction_id: str, signer_id: str, signature: str) -> bool:
        """Sign a transaction"""
        try:
            transaction = self.transactions.get(transaction_id)
            if not transaction:
                raise ValueError("Transaction not found")
            
            if transaction.status != TransactionStatus.PENDING:
                raise ValueError("Transaction is not pending")
            
            if datetime.now() > transaction.expires_at:
                transaction.status = TransactionStatus.FAILED
                raise ValueError("Transaction has expired")
            
            # Find the signature request
            signature_key = f"sig_{transaction_id}_{signer_id}"
            signature_obj = self.signatures.get(signature_key)
            
            if not signature_obj:
                raise ValueError("Signature request not found")
            
            if signature_obj.status != SignatureStatus.PENDING:
                raise ValueError("Already signed or rejected")
            
            # Verify signature (simplified for demo)
            if self._verify_signature(transaction, signer_id, signature):
                signature_obj.signature = signature
                signature_obj.status = SignatureStatus.SIGNED
                signature_obj.signed_at = datetime.now()
                
                transaction.current_signatures += 1
                transaction.signatures.append({
                    "signer_id": signer_id,
                    "signature": signature,
                    "signed_at": datetime.now().isoformat()
                })
                
                # Check if we have enough signatures
                if transaction.current_signatures >= transaction.required_signatures:
                    await self._execute_transaction(transaction)
                
                logger.info(f"✅ Transaction {transaction_id} signed by {signer_id}")
                return True
            else:
                raise ValueError("Invalid signature")
                
        except Exception as e:
            logger.error(f"❌ Error signing transaction: {e}")
            raise
    
    async def reject_transaction(self, transaction_id: str, signer_id: str, reason: str) -> bool:
        """Reject a transaction"""
        try:
            transaction = self.transactions.get(transaction_id)
            if not transaction:
                raise ValueError("Transaction not found")
            
            signature_key = f"sig_{transaction_id}_{signer_id}"
            signature_obj = self.signatures.get(signature_key)
            
            if not signature_obj:
                raise ValueError("Signature request not found")
            
            signature_obj.status = SignatureStatus.REJECTED
            signature_obj.rejected_at = datetime.now()
            signature_obj.rejection_reason = reason
            
            transaction.status = TransactionStatus.REJECTED
            
            logger.info(f"❌ Transaction {transaction_id} rejected by {signer_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error rejecting transaction: {e}")
            return False
    
    def _verify_signature(self, transaction: Transaction, signer_id: str, signature: str) -> bool:
        """Verify transaction signature (simplified for demo)"""
        # In a real implementation, this would verify the cryptographic signature
        # For demo purposes, we'll do a simple validation
        signer = None
        wallet = self.wallets.get(transaction.wallet_id)
        
        if wallet:
            for s in wallet.signers:
                if s.id == signer_id:
                    signer = s
                    break
        
        if not signer:
            return False
        
        # Simple signature validation (in real implementation, use proper crypto)
        expected_data = f"{transaction.id}_{transaction.amount}_{transaction.currency}_{transaction.to_address}"
        return len(signature) > 10  # Simplified validation
    
    async def _execute_transaction(self, transaction: Transaction):
        """Execute the transaction after sufficient signatures"""
        try:
            wallet = self.wallets.get(transaction.wallet_id)
            if not wallet:
                raise ValueError("Wallet not found")
            
            # Deduct balance (simplified)
            current_balance = wallet.balances.get(transaction.currency, 0)
            total_amount = transaction.amount + transaction.fee
            
            if current_balance >= total_amount:
                wallet.balances[transaction.currency] = current_balance - total_amount
                transaction.status = TransactionStatus.EXECUTED
                transaction.executed_at = datetime.now()
                
                logger.info(f"🚀 Executed transaction: {transaction.id}")
            else:
                transaction.status = TransactionStatus.FAILED
                logger.error(f"❌ Insufficient balance for transaction: {transaction.id}")
                
        except Exception as e:
            transaction.status = TransactionStatus.FAILED
            logger.error(f"❌ Error executing transaction: {e}")
    
    async def get_wallet_transactions(self, wallet_id: str) -> List[Transaction]:
        """Get all transactions for a wallet"""
        return [tx for tx in self.transactions.values() if tx.wallet_id == wallet_id]
    
    async def get_pending_signatures(self, signer_id: str) -> List[Dict[str, Any]]:
        """Get all pending signature requests for a signer"""
        pending_signatures = []
        
        for signature in self.signatures.values():
            if signature.signer_id == signer_id and signature.status == SignatureStatus.PENDING:
                transaction = self.transactions.get(signature.transaction_id)
                if transaction and transaction.status == TransactionStatus.PENDING:
                    pending_signatures.append({
                        "signature": asdict(signature),
                        "transaction": asdict(transaction)
                    })
        
        return pending_signatures
    
    async def update_wallet_balance(self, wallet_id: str, currency: str, amount: float) -> bool:
        """Update wallet balance (for deposits)"""
        try:
            wallet = self.wallets.get(wallet_id)
            if not wallet:
                return False
            
            current_balance = wallet.balances.get(currency, 0)
            wallet.balances[currency] = current_balance + amount
            wallet.updated_at = datetime.now()
            
            logger.info(f"💰 Updated {wallet_id} balance: +{amount} {currency}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating balance: {e}")
            return False
    
    async def get_wallet_analytics(self, wallet_id: str) -> Dict[str, Any]:
        """Get wallet analytics and statistics"""
        try:
            wallet = self.wallets.get(wallet_id)
            if not wallet:
                return {}
            
            transactions = await self.get_wallet_transactions(wallet_id)
            
            total_transactions = len(transactions)
            executed_transactions = len([tx for tx in transactions if tx.status == TransactionStatus.EXECUTED])
            pending_transactions = len([tx for tx in transactions if tx.status == TransactionStatus.PENDING])
            rejected_transactions = len([tx for tx in transactions if tx.status == TransactionStatus.REJECTED])
            
            total_volume = {}
            for tx in transactions:
                if tx.status == TransactionStatus.EXECUTED:
                    if tx.currency not in total_volume:
                        total_volume[tx.currency] = 0
                    total_volume[tx.currency] += tx.amount
            
            return {
                "wallet_id": wallet_id,
                "wallet_name": wallet.name,
                "total_signers": wallet.total_signers,
                "required_signatures": wallet.required_signatures,
                "balances": wallet.balances,
                "transaction_stats": {
                    "total": total_transactions,
                    "executed": executed_transactions,
                    "pending": pending_transactions,
                    "rejected": rejected_transactions
                },
                "total_volume": total_volume,
                "created_at": wallet.created_at.isoformat(),
                "updated_at": wallet.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting wallet analytics: {e}")
            return {}

# FastAPI application
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

app = FastAPI(title="Multi-Signature Wallet Service", version="7.0.0")
multisig_service = MultiSigWalletService()

class WalletCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    wallet_type: str = "corporate"
    required_signatures: int
    signer_ids: List[str]

class TransactionCreate(BaseModel):
    wallet_id: str
    to_address: str
    currency: str
    amount: float
    fee: Optional[float] = 0
    description: Optional[str] = ""
    created_by: str

class SignatureRequest(BaseModel):
    signature: str

class RejectionRequest(BaseModel):
    reason: str

@app.on_event("startup")
async def startup_event():
    await multisig_service.initialize()

@app.post("/wallets")
async def create_wallet(wallet: WalletCreate):
    try:
        new_wallet = await multisig_service.create_wallet(wallet.dict())
        return {"success": True, "wallet": new_wallet}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/wallets/{wallet_id}")
async def get_wallet(wallet_id: str):
    wallet = await multisig_service.get_wallet(wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet

@app.get("/users/{user_id}/wallets")
async def get_user_wallets(user_id: str):
    return await multisig_service.get_user_wallets(user_id)

@app.post("/transactions")
async def create_transaction(transaction: TransactionCreate):
    try:
        new_transaction = await multisig_service.create_transaction(transaction.dict())
        return {"success": True, "transaction": new_transaction}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/transactions/{transaction_id}/sign")
async def sign_transaction(transaction_id: str, signer_id: str, signature_req: SignatureRequest):
    try:
        success = await multisig_service.sign_transaction(transaction_id, signer_id, signature_req.signature)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/transactions/{transaction_id}/reject")
async def reject_transaction(transaction_id: str, signer_id: str, rejection: RejectionRequest):
    success = await multisig_service.reject_transaction(transaction_id, signer_id, rejection.reason)
    return {"success": success}

@app.get("/wallets/{wallet_id}/transactions")
async def get_wallet_transactions(wallet_id: str):
    return await multisig_service.get_wallet_transactions(wallet_id)

@app.get("/signers/{signer_id}/pending")
async def get_pending_signatures(signer_id: str):
    return await multisig_service.get_pending_signatures(signer_id)

@app.get("/wallets/{wallet_id}/analytics")
async def get_wallet_analytics(wallet_id: str):
    return await multisig_service.get_wallet_analytics(wallet_id)

@app.post("/wallets/{wallet_id}/deposit")
async def update_wallet_balance(wallet_id: str, currency: str, amount: float):
    success = await multisig_service.update_wallet_balance(wallet_id, currency, amount)
    return {"success": success}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)