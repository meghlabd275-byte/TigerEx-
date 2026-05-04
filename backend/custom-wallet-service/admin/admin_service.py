#!/usr/bin/env python3
"""
TigerEx Custom Wallet Service - Separated Admin & User Backends
Supports EVM and Non-EVM chains with separate interfaces
"""
import os
import json
import hashlib
import logging
import uuid
import time
import threading
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, field
from functools import wraps

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# CONFIGURATION - SUPPORTED CHAINS (EVM + NON-EVM)
# ============================================================
CHAINS = {
    # EVM Chains
    "ethereum": {"name": "Ethereum", "type": "evm", "chain_id": 1, "symbol": "ETH", "rpc": "https://eth.llamarpc.com", "explorer": "https://etherscan.io", "decimals": 18},
    "bsc": {"name": "BNB Chain", "type": "evm", "chain_id": 56, "symbol": "BNB", "rpc": "https://bsc.llamarpc.com", "explorer": "https://bscscan.com", "decimals": 18},
    "polygon": {"name": "Polygon", "type": "evm", "chain_id": 137, "symbol": "MATIC", "rpc": "https://polygon.llamarpc.com", "explorer": "https://polygonscan.com", "decimals": 18},
    "arbitrum": {"name": "Arbitrum One", "type": "evm", "chain_id": 42161, "symbol": "ETH", "rpc": "https://arb1.llamarpc.com", "explorer": "https://arbiscan.io", "decimals": 18},
    "optimism": {"name": "Optimism", "type": "evm", "chain_id": 10, "symbol": "ETH", "rpc": "https://mainnet.optimism.io", "explorer": "https://optimistic.etherscan.io", "decimals": 18},
    "avalanche": {"name": "Avalanche C-Chain", "type": "evm", "chain_id": 43114, "symbol": "AVAX", "rpc": "https://avalanche.llamarpc.com", "explorer": "https://snowtrace.io", "decimals": 18},
    "base": {"name": "Base", "type": "evm", "chain_id": 8453, "symbol": "ETH", "rpc": "https://mainnet.base.org", "explorer": "https://basescan.org", "decimals": 18},
    "tigerex": {"name": "TigerExChain", "type": "evm", "chain_id": 9999, "symbol": "TIG", "rpc": "http://localhost:5800", "explorer": "", "decimals": 18},
    
    # Non-EVM Chains
    "solana": {"name": "Solana", "type": "non_evm", "symbol": "SOL", "rpc": "https://api.mainnet-beta.solana.com", "explorer": "https://solscan.io", "decimals": 9},
    "ton": {"name": "TON", "type": "non_evm", "symbol": "TON", "rpc": "https://toncenter.com/api/v2", "explorer": "https://tonscan.org", "decimals": 9},
    "near": {"name": "NEAR", "type": "non_evm", "symbol": "NEAR", "rpc": "https://rpc.mainnet.near.org", "explorer": "https://explorer.near.org", "decimals": 24},
    "aptos": {"name": "Aptos", "type": "non_evm", "symbol": "APT", "rpc": "https://fullnode.mainnet.aptoslabs.com", "explorer": "https://explorer.aptoslabs.com", "decimals": 8},
    "sui": {"name": "Sui", "type": "non_evm", "symbol": "SUI", "rpc": "https://fullnode.mainnet.sui.io", "explorer": "https://suiscan.xyz", "decimals": 9},
    "cosmos": {"name": "Cosmos Hub", "type": "non_evm", "symbol": "ATOM", "rpc": "https://rpc.cosmos.network", "explorer": "https://mintscan.io", "decimals": 6},
    "polkadot": {"name": "Polkadot", "type": "non_evm", "symbol": "DOT", "rpc": "https://rpc.polkadot.io", "explorer": "https://polkadot.subscan.io", "decimals": 10},
    "cardano": {"name": "Cardano", "type": "non_evm", "symbol": "ADA", "rpc": "https://cardano-mainnet.blockfrost.io", "explorer": "https://cardanoscan.io", "decimals": 6},
    "algorand": {"name": "Algorand", "type": "non_evm", "symbol": "ALGO", "rpc": "https://mainnet-api.algorand.network", "explorer": "https://algoexplorer.io", "decimals": 6},
    "tezos": {"name": "Tezos", "type": "non_evm", "symbol": "XTZ", "rpc": "https://mainnet.api.tez.ie", "explorer": "https://tzstats.com", "decimals": 6},
}

# Token lists by chain
TOKENS = {
    "ethereum": [
        {"address": "0x0000000000000000000000000000000000000000", "symbol": "ETH", "name": "Ethereum", "decimals": 18},
        {"address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "symbol": "USDC", "name": "USD Coin", "decimals": 6},
        {"address": "0xdAC17F958D2ee523a2206206994597C13D831ec7", "symbol": "USDT", "name": "Tether USD", "decimals": 6},
        {"address": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C805", "symbol": "WBTC", "name": "Wrapped Bitcoin", "decimals": 8},
    ],
    "bsc": [
        {"address": "0x0000000000000000000000000000000000000000", "symbol": "BNB", "name": "BNB", "decimals": 18},
        {"address": "0x8AC76a51CC950d5922DD9EA5912B6E5eC08f7D9A0", "symbol": "USDC", "name": "USD Coin", "decimals": 6},
        {"address": "0x55d398326f99059fF7754852467Fb06d8F7D86d1", "symbol": "USDT", "name": "Tether USD", "decimals": 6},
    ],
    "polygon": [
        {"address": "0x0000000000000000000000000000000000000000", "symbol": "MATIC", "name": "Polygon", "decimals": 18},
        {"address": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa841bB", "symbol": "USDC", "name": "USD Coin", "decimals": 6},
    ],
}

# ============================================================
# DATA MODELS
# ============================================================
@dataclass
class Wallet:
    wallet_id: str
    user_id: str
    wallet_type: str  # "custodial" or "non_custodial" or " imported"
    address: str
    chain: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    encrypted_key: str = ""
    status: str = "active"
    is_admin: bool = False  # Admin controlled
    
    def to_dict(self) -> Dict:
        return {
            "wallet_id": self.wallet_id,
            "user_id": self.user_id,
            "type": self.wallet_type,
            "address": self.address,
            "chain": self.chain,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
        }

@dataclass
class Transaction:
    tx_hash: str
    wallet_id: str
    chain: str
    from_addr: str
    to_addr: str
    amount: float
    symbol: str
    status: str  # pending, confirmed, failed
    timestamp: datetime = field(default_factory=datetime.utcnow)
    block_number: int = 0
    gas_used: int = 0
    gas_price: int = 0
    tx_type: str = "transfer"  # transfer, swap, contract_call
    nonce: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "hash": self.tx_hash,
            "from": self.from_addr,
            "to": self.to_addr,
            "amount": self.amount,
            "symbol": self.symbol,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "block": self.block_number,
            "gas_used": self.gas_used,
            "type": self.tx_type,
        }

@dataclass
class AdminAction:
    action_id: str
    admin_id: str
    action_type: str
    target: str
    details: Dict
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: str = "completed"
    
    def to_dict(self) -> Dict:
        return {
            "action_id": self.action_id,
            "admin_id": self.admin_id,
            "action_type": self.action_type,
            "target": self.target,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
        }

# ============================================================
# WALLET SERVICE
# ============================================================
class WalletService:
    """Core wallet service"""
    
    def __init__(self):
        # Storage
        self.wallets = {}
        self.user_wallets = defaultdict(list)
        self.balances = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        self.transactions = {}
        self.pending_txs = []
        self.admin_actions = []
        self.admin_users = set()
        
        # Price cache
        self.prices = {}
        self._start_price_feed()
        
        logger.info("Custom Wallet Service initialized")
    
    def _start_price_feed(self):
        def feed():
            while True:
                self._update_prices()
                time.sleep(30)
        threading.Thread(target=feed, daemon=True).start()
    
    def _update_prices(self):
        try:
            ids = "ethereum,solana,ton,near,aptos,cosmos,polkadot,cardano,algorand,tezos"
            r = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd", timeout=10)
            if r.status_code == 200:
                self.prices = r.json()
        except Exception as e:
            logger.warning(f"Price update error: {e}")
    
    # --- Admin Methods ---
    
    def add_admin(self, admin_id: str):
        self.admin_users.add(admin_id)
        action = AdminAction(
            action_id=f"ADMIN_{uuid.uuid4().hex[:8]}",
            admin_id=admin_id,
            action_type="add_admin",
            target=admin_id,
            details={}
        )
        self.admin_actions.append(action)
    
    def is_admin(self, user_id: str) -> bool:
        return user_id in self.admin_users
    
    def create_admin_wallet(self, user_id: str, chain: str) -> Dict:
        """Create wallet with admin privileges"""
        if chain not in CHAINS:
            return {"error": f"Unsupported chain: {chain}"}
        
        chain_type = CHAINS[chain]["type"]
        if chain_type == "evm":
            address = "0x" + hashlib.sha256(f"{user_id}{chain}{time.time()}".encode()).hexdigest()[-40:]
        else:
            address = hashlib.sha256(f"{user_id}{chain}{time.time()}".encode()).hexdigest()[:44]
        
        wallet_id = f"ADMIN_{uuid.uuid4().hex[:12]}"
        wallet = Wallet(wallet_id, user_id, "custodial", address, chain, is_admin=True)
        
        self.wallets[wallet_id] = wallet
        self.user_wallets[user_id].append(wallet_id)
        self.balances[wallet_id][chain] = {"ETH": 0, "USDC": 0, "USDT": 0, "TIG": 10000}  # Admin gets test tokens
        
        # Log admin action
        action = AdminAction(
            action_id=f"ACTION_{uuid.uuid4().hex[:8]}",
            admin_id=user_id,
            action_type="create_wallet",
            target=wallet_id,
            details={"chain": chain}
        )
        self.admin_actions.append(action)
        
        return {
            "wallet_id": wallet_id,
            "address": address,
            "chain": chain,
            "type": "custodial",
            "status": "active",
            "is_admin": True
        }
    
    def freeze_wallet(self, admin_id: str, wallet_id: str, reason: str) -> Dict:
        """Admin: Freeze wallet"""
        if wallet_id not in self.wallets:
            return {"error": "Wallet not found"}
        
        # Verify admin
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        self.wallets[wallet_id].status = "frozen"
        
        action = AdminAction(
            action_id=f"ACTION_{uuid.uuid4().hex[:8]}",
            admin_id=admin_id,
            action_type="freeze_wallet",
            target=wallet_id,
            details={"reason": reason}
        )
        self.admin_actions.append(action)
        
        return {"status": "frozen", "wallet_id": wallet_id}
    
    def unfreeze_wallet(self, admin_id: str, wallet_id: str) -> Dict:
        """Admin: Unfreeze wallet"""
        if wallet_id not in self.wallets:
            return {"error": "Wallet not found"}
        
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        self.wallets[wallet_id].status = "active"
        
        action = AdminAction(
            action_id=f"ACTION_{uuid.uuid4().hex[:8]}",
            admin_id=admin_id,
            action_type="unfreeze_wallet",
            target=wallet_id,
            details={}
        )
        self.admin_actions.append(action)
        
        return {"status": "active", "wallet_id": wallet_id}
    
    def adjust_balance(self, admin_id: str, wallet_id: str, asset: str, amount: float, operation: str) -> Dict:
        """Admin: Adjust wallet balance"""
        if wallet_id not in self.wallets:
            return {"error": "Wallet not found"}
        
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        wallet = self.wallets[wallet_id]
        chain = wallet.chain
        
        if operation == "add":
            self.balances[wallet_id][chain][asset] += amount
        elif operation == "subtract":
            self.balances[wallet_id][chain][asset] -= amount
        else:
            return {"error": "Invalid operation"}
        
        action = AdminAction(
            action_id=f"ACTION_{uuid.uuid4().hex[:8]}",
            admin_id=admin_id,
            action_type="adjust_balance",
            target=wallet_id,
            details={"asset": asset, "amount": amount, "operation": operation}
        )
        self.admin_actions.append(action)
        
        return {"status": "adjusted", "new_balance": self.balances[wallet_id][chain][asset]}
    
    def get_all_wallets(self, admin_id: str) -> List[Dict]:
        """Admin: Get all wallets"""
        if not self.is_admin(admin_id):
            return []
        return [w.to_dict() for w in self.wallets.values()]
    
    def get_all_transactions(self, admin_id: str, limit: int = 100) -> List[Dict]:
        """Admin: Get all transactions"""
        if not self.is_admin(admin_id):
            return []
        txs = sorted([t.to_dict() for t in self.transactions.values()], key=lambda x: x["timestamp"], reverse=True)
        return txs[:limit]
    
    def get_admin_actions(self, admin_id: str, limit: int = 50) -> List[Dict]:
        """Admin: Get admin actions"""
        if not self.is_admin(admin_id):
            return []
        return sorted([a.to_dict() for a in self.admin_actions], key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def get_system_stats(self, admin_id: str) -> Dict:
        """Admin: Get system statistics"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        total_wallets = len(self.wallets)
        active_wallets = sum(1 for w in self.wallets.values() if w.status == "active")
        frozen_wallets = sum(1 for w in self.wallets.values() if w.status == "frozen")
        total_txs = len(self.transactions)
        pending_txs = sum(1 for t in self.transactions.values() if t.status == "pending")
        
        return {
            "total_wallets": total_wallets,
            "active_wallets": active_wallets,
            "frozen_wallets": frozen_wallets,
            "total_transactions": total_txs,
            "pending_transactions": pending_txs,
            "supported_chains": len(CHAINS),
            "evm_chains": sum(1 for c in CHAINS.values() if c["type"] == "evm"),
            "non_evm_chains": sum(1 for c in CHAINS.values() if c["type"] == "non_evm"),
        }
    
    # --- User Methods ---
    
    def create_custodial_wallet(self, user_id: str, chain: str) -> Dict:
        """User: Create custodial wallet"""
        if chain not in CHAINS:
            return {"error": f"Unsupported chain: {chain}"}
        
        chain_type = CHAINS[chain]["type"]
        if chain_type == "evm":
            address = "0x" + hashlib.sha256(f"{user_id}{chain}{time.time()}".encode()).hexdigest()[-40:]
        else:
            address = hashlib.sha256(f"{user_id}{chain}{time.time()}".encode()).hexdigest()[:44]
        
        wallet_id = f"CUST_{uuid.uuid4().hex[:12]}"
        wallet = Wallet(wallet_id, user_id, "custodial", address, chain)
        
        self.wallets[wallet_id] = wallet
        self.user_wallets[user_id].append(wallet_id)
        self.balances[wallet_id][chain] = {"ETH": 0, "USDC": 0, "USDT": 0}
        
        return {
            "wallet_id": wallet_id,
            "address": address,
            "chain": chain,
            "type": "custodial",
            "status": "active"
        }
    
    def create_non_custodial_wallet(self, user_id: str, chain: str) -> Dict:
        """User: Create non-custodial wallet"""
        if chain not in CHAINS:
            return {"error": f"Unsupported chain: {chain}"}
        
        private_key = hashlib.sha256(f"{user_id}{time.time()}".encode()).hexdigest()
        
        chain_type = CHAINS[chain]["type"]
        if chain_type == "evm":
            address = "0x" + hashlib.sha256(private_key.encode()).hexdigest()[-40:]
        else:
            address = hashlib.sha256(private_key.encode()).hexdigest()[:44]
        
        wallet_id = f"NONCUST_{uuid.uuid4().hex[:12]}"
        wallet = Wallet(wallet_id, user_id, "non_custodial", address, chain, encrypted_key=hashlib.sha256(private_key.encode()).hexdigest())
        
        self.wallets[wallet_id] = wallet
        self.user_wallets[user_id].append(wallet_id)
        
        return {
            "wallet_id": wallet_id,
            "address": address,
            "chain": chain,
            "type": "non_custodial",
            "status": "active",
            "note": "Private key generated locally - store securely"
        }
    
    def import_wallet(self, user_id: str, private_key: str, chain: str) -> Dict:
        """User: Import wallet"""
        if chain not in CHAINS:
            return {"error": f"Unsupported chain: {chain}"}
        
        # Derive address from key (simplified for demo)
        key_hash = hashlib.sha256(private_key.encode()).hexdigest()
        
        chain_type = CHAINS[chain]["type"]
        if chain_type == "evm":
            address = "0x" + key_hash[-40:]
        else:
            address = key_hash[:44]
        
        wallet_id = f"IMP_{uuid.uuid4().hex[:12]}"
        wallet = Wallet(wallet_id, user_id, "imported", address, chain, encrypted_key=key_hash)
        
        self.wallets[wallet_id] = wallet
        self.user_wallets[user_id].append(wallet_id)
        
        return {
            "wallet_id": wallet_id,
            "address": address,
            "chain": chain,
            "type": "imported",
            "status": "active"
        }
    
    def get_user_wallets(self, user_id: str) -> List[Dict]:
        """User: Get their wallets"""
        wallet_ids = self.user_wallets.get(user_id, [])
        return [self.wallets[wid].to_dict() for wid in wallet_ids if wid in self.wallets]
    
    def get_balance(self, wallet_id: str, chain: str = "") -> Dict:
        """User: Get wallet balance"""
        if wallet_id not in self.wallets:
            return {"error": "Wallet not found"}
        
        wallet = self.wallets[wallet_id]
        chain = chain or wallet.chain
        
        balances = {}
        for asset, amount in self.balances[wallet_id][chain].items():
            if amount > 0:
                price = self.prices.get(asset.lower(), {}).get("usd", 0)
                balances[asset] = {
                    "amount": amount,
                    "usd_value": amount * price
                }
        
        return {
            "wallet_id": wallet_id,
            "chain": chain,
            "balances": balances
        }
    
    def deposit(self, wallet_id: str, asset: str, amount: float, tx_hash: str = "") -> Dict:
        """User: Deposit funds"""
        if wallet_id not in self.wallets:
            return {"error": "Wallet not found"}
        
        wallet = self.wallets[wallet_id]
        if wallet.status != "active":
            return {"error": "Wallet is not active"}
        
        chain = wallet.chain
        self.balances[wallet_id][chain][asset] += amount
        
        # Record transaction
        if tx_hash:
            tx = Transaction(
                tx_hash=tx_hash,
                wallet_id=wallet_id,
                chain=chain,
                from_addr="deposit",
                to_addr=wallet.address,
                amount=amount,
                symbol=asset,
                status="confirmed"
            )
            self.transactions[tx_hash] = tx
        
        return {
            "status": "deposited",
            "amount": amount,
            "asset": asset
        }
    
    def withdraw(self, wallet_id: str, to_address: str, asset: str, amount: float) -> Dict:
        """User: Withdraw funds"""
        if wallet_id not in self.wallets:
            return {"error": "Wallet not found"}
        
        wallet = self.wallets[wallet_id]
        if wallet.status != "active":
            return {"error": "Wallet is not active"}
        
        chain = wallet.chain
        current = self.balances[wallet_id][chain].get(asset, 0)
        
        if current < amount:
            return {"error": "Insufficient balance"}
        
        self.balances[wallet_id][chain][asset] -= amount
        
        tx_hash = f"0x{uuid.uuid4().hex[:64]}"
        tx = Transaction(
            tx_hash=tx_hash,
            wallet_id=wallet_id,
            chain=chain,
            from_addr=wallet.address,
            to_addr=to_address,
            amount=amount,
            symbol=asset,
            status="pending"
        )
        self.transactions[tx_hash] = tx
        self.pending_txs.append(tx_hash)
        
        return {
            "withdrawal_id": tx_hash,
            "to": to_address,
            "amount": amount,
            "asset": asset,
            "status": "pending"
        }
    
    def send_transaction(self, wallet_id: str, to_address: str, amount: float, asset: str = "") -> Dict:
        """User: Send transaction"""
        if wallet_id not in self.wallets:
            return {"error": "Wallet not found"}
        
        wallet = self.wallets[wallet_id]
        if wallet.status != "active":
            return {"error": "Wallet is not active"}
        
        if wallet.wallet_type != "non_custodial":
            return {"error": "Use withdraw for custodial wallet"}
        
        asset = asset or CHAINS[wallet.chain]["symbol"]
        
        balance = self.balances[wallet_id].get(wallet.chain, {}).get(asset, 0)
        if balance < amount:
            return {"error": "Insufficient balance"}
        
        self.balances[wallet_id][wallet.chain][asset] -= amount
        
        tx_hash = f"0x{uuid.uuid4().hex[:64]}"
        
        return {
            "tx_hash": tx_hash,
            "from": wallet.address,
            "to": to_address,
            "amount": amount,
            "asset": asset,
            "status": "signed"
        }
    
    def get_user_transactions(self, wallet_id: str, limit: int = 50) -> List[Dict]:
        """User: Get transaction history"""
        if wallet_id not in self.wallets:
            return []
        
        txs = [t.to_dict() for t in self.transactions.values() if t.wallet_id == wallet_id]
        return sorted(txs, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def sign_message(self, wallet_id: str, message: str) -> Dict:
        """User: Sign message"""
        if wallet_id not in self.wallets:
            return {"error": "Wallet not found"}
        
        wallet = self.wallets[wallet_id]
        if wallet.status != "active":
            return {"error": "Wallet is not active"}
        
        signature = hashlib.sha256(f"{wallet.encrypted_key}{message}".encode()).hexdigest()
        
        return {
            "wallet_id": wallet_id,
            "message": message,
            "signature": signature,
            "address": wallet.address
        }
    
    def get_supported_chains(self) -> List[Dict]:
        return [{"id": k, "name": v["name"], "type": v["type"], "symbol": v["symbol"]} for k, v in CHAINS.items()]
    
    def get_chain_info(self, chain: str) -> Dict:
        if chain not in CHAINS:
            return {"error": "Chain not found"}
        return CHAINS[chain]
    
    def get_tokens(self, chain: str) -> List[Dict]:
        return TOKENS.get(chain, [])


# ============================================================
# FLASK ADMIN API
# ============================================================
from flask import Flask, jsonify, request
from flask_cors import CORS

admin_app = Flask(__name__)
CORS(admin_app)

wallet_service = WalletService()

# Default admin
wallet_service.add_admin("admin001")

@admin_app.route('/wallet/admin/health')
def admin_health():
    return jsonify({"status": "ok", "service": "wallet", "role": "admin", "chains": len(CHAINS)})

@admin_app.route('/wallet/admin/create-wallet', methods=['POST'])
def admin_create_wallet():
    data = request.get_json() or {}
    return jsonify(wallet_service.create_admin_wallet(
        data.get('user_id', str(uuid.uuid4())),
        data.get('chain', 'ethereum')
    ))

@admin_app.route('/wallet/admin/freeze', methods=['POST'])
def admin_freeze():
    data = request.get_json() or {}
    return jsonify(wallet_service.freeze_wallet(
        data.get('admin_id', ''),
        data.get('wallet_id', ''),
        data.get('reason', '')
    ))

@admin_app.route('/wallet/admin/unfreeze', methods=['POST'])
def admin_unfreeze():
    data = request.get_json() or {}
    return jsonify(wallet_service.unfreeze_wallet(
        data.get('admin_id', ''),
        data.get('wallet_id', '')
    ))

@admin_app.route('/wallet/admin/adjust-balance', methods=['POST'])
def admin_adjust():
    data = request.get_json() or {}
    return jsonify(wallet_service.adjust_balance(
        data.get('admin_id', ''),
        data.get('wallet_id', ''),
        data.get('asset', 'USDC'),
        data.get('amount', 0),
        data.get('operation', 'add')
    ))

@admin_app.route('/wallet/admin/all-wallets')
def admin_all_wallets():
    admin_id = request.args.get('admin_id', '')
    return jsonify(wallet_service.get_all_wallets(admin_id))

@admin_app.route('/wallet/admin/all-transactions')
def admin_all_txs():
    admin_id = request.args.get('admin_id', '')
    limit = request.args.get('limit', 100, type=int)
    return jsonify(wallet_service.get_all_transactions(admin_id, limit))

@admin_app.route('/wallet/admin/actions')
def admin_actions():
    admin_id = request.args.get('admin_id', '')
    return jsonify(wallet_service.get_admin_actions(admin_id))

@admin_app.route('/wallet/admin/stats')
def admin_stats():
    admin_id = request.args.get('admin_id', '')
    return jsonify(wallet_service.get_system_stats(admin_id))

@admin_app.route('/wallet/admin/chains')
def admin_chains():
    return jsonify(wallet_service.get_supported_chains())


# ============================================================
# FLASK USER API
# ============================================================
user_app = Flask(__name__)
CORS(user_app)

@user_app.route('/wallet/user/health')
def user_health():
    return jsonify({"status": "ok", "service": "wallet", "role": "user"})

@user_app.route('/wallet/user/create-custodial', methods=['POST'])
def user_create_custodial():
    data = request.get_json() or {}
    return jsonify(wallet_service.create_custodial_wallet(
        data.get('user_id', str(uuid.uuid4())),
        data.get('chain', 'ethereum')
    ))

@user_app.route('/wallet/user/create-non-custodial', methods=['POST'])
def user_create_non_custodial():
    data = request.get_json() or {}
    return jsonify(wallet_service.create_non_custodial_wallet(
        data.get('user_id', str(uuid.uuid4())),
        data.get('chain', 'ethereum')
    ))

@user_app.route('/wallet/user/import', methods=['POST'])
def user_import():
    data = request.get_json() or {}
    return jsonify(wallet_service.import_wallet(
        data.get('user_id', str(uuid.uuid4())),
        data.get('private_key', ''),
        data.get('chain', 'ethereum')
    ))

@user_app.route('/wallet/user/wallets/<user_id>')
def user_wallets(user_id):
    return jsonify(wallet_service.get_user_wallets(user_id))

@user_app.route('/wallet/user/balance/<wallet_id>')
def user_balance(wallet_id):
    chain = request.args.get('chain', '')
    return jsonify(wallet_service.get_balance(wallet_id, chain))

@user_app.route('/wallet/user/deposit', methods=['POST'])
def user_deposit():
    data = request.get_json() or {}
    return jsonify(wallet_service.deposit(
        data.get('wallet_id', ''),
        data.get('asset', 'USDC'),
        data.get('amount', 0),
        data.get('tx_hash', '')
    ))

@user_app.route('/wallet/user/withdraw', methods=['POST'])
def user_withdraw():
    data = request.get_json() or {}
    return jsonify(wallet_service.withdraw(
        data.get('wallet_id', ''),
        data.get('to_address', ''),
        data.get('asset', 'USDC'),
        data.get('amount', 0)
    ))

@user_app.route('/wallet/user/send', methods=['POST'])
def user_send():
    data = request.get_json() or {}
    return jsonify(wallet_service.send_transaction(
        data.get('wallet_id', ''),
        data.get('to_address', ''),
        data.get('amount', 0),
        data.get('asset', '')
    ))

@user_app.route('/wallet/user/transactions/<wallet_id>')
def user_txs(wallet_id):
    limit = request.args.get('limit', 50, type=int)
    return jsonify(wallet_service.get_user_transactions(wallet_id, limit))

@user_app.route('/wallet/user/sign', methods=['POST'])
def user_sign():
    data = request.get_json() or {}
    return jsonify(wallet_service.sign_message(
        data.get('wallet_id', ''),
        data.get('message', '')
    ))

@user_app.route('/wallet/user/chains')
def user_chains():
    return jsonify(wallet_service.get_supported_chains())

@user_app.route('/wallet/user/chain/<chain>')
def user_chain_info(chain):
    return jsonify(wallet_service.get_chain_info(chain))

@user_app.route('/wallet/user/tokens/<chain>')
def user_tokens(chain):
    return jsonify(wallet_service.get_tokens(chain))


def run_admin():
    port = int(os.environ.get('PORT', 6100))
    logger.info(f"Starting Admin Wallet Service on port {port}")
    admin_app.run(host='0.0.0.0', port=port, threaded=True)

def run_user():
    port = int(os.environ.get('PORT', 6101))
    logger.info(f"Starting User Wallet Service on port {port}")
    user_app.run(host='0.0.0.0', port=port, threaded=True)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'admin':
        run_admin()
    elif len(sys.argv) > 1 and sys.argv[1] == 'user':
        run_user()
    else:
        # Run both
        import threading
        threading.Thread(target=run_admin, daemon=True).start()
        run_user()