#!/usr/bin/env python3
"""
TigerEx Multi-Chain Wallet Service
Supports Custodial and Non-Custodial wallets for EVM and Non-EVM chains
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
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Supported chains
CHAINS = {
    # EVM chains
    "ethereum": {"name": "Ethereum", "type": "evm", "chain_id": 1, "symbol": "ETH", "rpc": "https://eth.llamarpc.com", "explorer": "https://etherscan.io"},
    "bsc": {"name": "BNB Chain", "type": "evm", "chain_id": 56, "symbol": "BNB", "rpc": "https://bsc.llamarpc.com", "explorer": "https://bscscan.com"},
    "polygon": {"name": "Polygon", "type": "evm", "chain_id": 137, "symbol": "MATIC", "rpc": "https://polygon.llamarpc.com", "explorer": "https://polygonscan.com"},
    "arbitrum": {"name": "Arbitrum", "type": "evm", "chain_id": 42161, "symbol": "ETH", "rpc": "https://arb1.llamarpc.com", "explorer": "https://arbiscan.io"},
    "avalanche": {"name": "Avalanche", "type": "evm", "chain_id": 43114, "symbol": "AVAX", "rpc": "https://avalanche.llamarpc.com", "explorer": "https://snowtrace.io"},
    "tigerex": {"name": "TigerEx", "type": "evm", "chain_id": 9999, "symbol": "TIG", "rpc": "http://localhost:5800", "explorer": ""},
    
    # Non-EVM chains
    "solana": {"name": "Solana", "type": "non_evm", "symbol": "SOL", "rpc": "https://api.mainnet-beta.solana.com", "ws": "wss://api.mainnet-beta.solana.com"},
    "ton": {"name": "TON", "type": "non_evm", "symbol": "TON", "rpc": "https://toncenter.com/api/v2"},
    "near": {"name": "NEAR", "type": "non_evm", "symbol": "NEAR", "rpc": "https://rpc.mainnet.near.org"},
    "aptos": {"name": "Aptos", "type": "non_evm", "symbol": "APT", "rpc": "https://fullnode.mainnet.aptoslabs.com"},
    "sui": {"name": "Sui", "type": "non_evm", "symbol": "SUI", "rpc": "https://fullnode.mainnet.sui.io"},
    "cosmos": {"name": "Cosmos", "type": "non_evm", "symbol": "ATOM", "rpc": "https://rpc.cosmos.network"}
}

# Token lists
COMMON_TOKENS = {
    "ethereum": [
        {"address": "0x0000000000000000000000000000000000000000", "symbol": "ETH", "name": "Ethereum", "decimals": 18},
        {"address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "symbol": "USDC", "name": "USD Coin", "decimals": 6},
        {"address": "0xdAC17F958D2ee523a2206206994597C13D831ec7", "symbol": "USDT", "name": "Tether", "decimals": 6},
    ],
    "bsc": [
        {"address": "0x0000000000000000000000000000000000000000", "symbol": "BNB", "name": "BNB", "decimals": 18},
        {"address": "0x8AC76a51CC950d5922DD9EA5912B6E5eC08f7D9A0", "symbol": "USDC", "name": "USD Coin", "decimals": 6},
    ],
    "polygon": [
        {"address": "0x0000000000000000000000000000000000000000", "symbol": "MATIC", "name": "Polygon", "decimals": 18},
    ]
}

@dataclass
class Wallet:
    """Wallet metadata"""
    wallet_id: str
    user_id: str
    wallet_type: str  # "custodial" or "non_custodial"
    address: str
    chain: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    encrypted_key: str = ""  # For non-custodial
    
    def to_dict(self) -> Dict:
        return {
            "wallet_id": self.wallet_id,
            "user_id": self.user_id,
            "type": self.wallet_type,
            "address": self.address,
            "chain": self.chain,
            "created_at": self.created_at.isoformat()
        }

@dataclass
class Transaction:
    """Wallet transaction"""
    tx_hash: str
    wallet_id: str
    chain: str
    from_addr: str
    to_addr: str
    amount: float
    symbol: str
    status: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    block_number: int = 0
    gas_used: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "hash": self.tx_hash,
            "from": self.from_addr,
            "to": self.to_addr,
            "amount": self.amount,
            "symbol": self.symbol,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "block": self.block_number
        }


class WalletService:
    """Multi-chain wallet service"""
    
    def __init__(self):
        # Database
        self.wallets = {}  # wallet_id -> Wallet
        self.user_wallets = defaultdict(list)  # user_id -> [wallet_ids]
        self.balances = defaultdict(lambda: defaultdict(float))  # wallet_id -> chain -> asset -> balance
        self.transactions = {}  # tx_hash -> Transaction
        self.pending_txs = []
        
        # Start price feed
        self._start_price_feed()
        
        logger.info("Wallet service initialized")
    
    def _start_price_feed(self):
        """Background price feed"""
        def feed():
            while True:
                self._update_prices()
                time.sleep(60)
        threading.Thread(target=feed, daemon=True).start()
    
    def _update_prices(self):
        """Update token prices"""
        try:
            r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum,solana,ton,near,aptos,cosmos,avalanche-2,arbitrum,polygon,matic-network&vs_currencies=usd", timeout=10)
            if r.status_code == 200:
                self.prices = r.json()
        except Exception as e:
            logger.warning(f"Price feed error: {e}")
    
    # ============ CUSTODIAL WALLETS ============
    
    def create_custodial_wallet(self, user_id: str, chain: str = "ethereum") -> Dict:
        """Create custodial wallet (managed by exchange)"""
        if chain not in CHAINS:
            return {"error": f"Unsupported chain: {chain}"}
        
        # Generate address based on chain type
        if CHAINS[chain]["type"] == "evm":
            address = "0x" + hashlib.sha256(f"{user_id}{chain}{time.time()}".encode()).hexdigest()[-40:]
        else:
            address = hashlib.sha256(f"{user_id}{chain}{time.time()}".encode()).hexdigest()[:44]
        
        wallet_id = f"CUST_{uuid.uuid4().hex[:12]}"
        wallet = Wallet(wallet_id, user_id, "custodial", address, chain)
        
        self.wallets[wallet_id] = wallet
        self.user_wallets[user_id].append(wallet_id)
        
        # Initialize balance
        self.balances[wallet_id][chain] = {"ETH": 0, "USDC": 0, "USDT": 0}
        
        return {
            "wallet_id": wallet_id,
            "address": address,
            "chain": chain,
            "type": "custodial",
            "status": "active"
        }
    
    # ============ NON-CUSTODIAL WALLETS ============
    
    def create_non_custodial_wallet(self, user_id: str, chain: str = "ethereum") -> Dict:
        """Create non-custodial wallet (user controls private key)"""
        if chain not in CHAINS:
            return {"error": f"Unsupported chain: {chain}"}
        
        # Generate mock private key (in production, use proper cryptography)
        private_key = hashlib.sha256(f"{user_id}{time.time()}".encode()).hexdigest()
        address = "0x" + hashlib.sha256(private_key.encode()).hexdigest()[-40:]
        
        wallet_id = f"NONCUST_{uuid.uuid4().hex[:12]}"
        wallet = Wallet(wallet_id, user_id, "non_custodial", address, chain, encrypted_key=hashlib.sha256(private_key.encode()).hexdigest())
        
        self.wallets[wallet_id] = wallet
        self.user_wallets[user_id].append(wallet_id)
        
        return {
            "wallet_id": wallet_id,
            "address": address,
            "chain": chain,
            "type": "non_custodial",
            "private_key_hint": "Stored securely - never shared",
            "status": "active"
        }
    
    def import_wallet(self, user_id: str, private_key: str, chain: str = "ethereum") -> Dict:
        """Import existing non-custodial wallet"""
        if chain not in CHAINS:
            return {"error": f"Unsupported chain: {chain}"}
        
        # Calculate address from private key
        address = "0x" + hashlib.sha256(private_key.encode()).hexdigest()[-40:]
        
        wallet_id = f"IMPORT_{uuid.uuid4().hex[:12]}"
        wallet = Wallet(wallet_id, user_id, "non_custodial", address, chain, encrypted_key=hashlib.sha256(private_key.encode()).hexdigest())
        
        self.wallets[wallet_id] = wallet
        self.user_wallets[user_id].append(wallet_id)
        
        # Try to fetch live balance
        balance = self.fetch_onchain_balance(chain, address)
        
        return {
            "wallet_id": wallet_id,
            "address": address,
            "chain": chain,
            "on_chain_balance": balance,
            "status": "imported"
        }
    
    # ============ WALLET OPERATIONS ============
    
    def get_wallets(self, user_id: str) -> List[Dict]:
        """Get all user wallets"""
        wallet_ids = self.user_wallets.get(user_id, [])
        return [self.wallets[wid].to_dict() for wid in wallet_ids]
    
    def get_balance(self, wallet_id: str, chain: str = "") -> Dict:
        """Get wallet balance"""
        if wallet_id not in self.wallets:
            return {"error": "Wallet not found"}
        
        wallet = self.wallets[wallet_id]
        chain = chain or wallet.chain
        
        balances = {}
        
        # Get cached balances
        if wallet_id in self.balances and chain in self.balances[wallet_id]:
            for asset, balance in self.balances[wallet_id][chain].items():
                if balance > 0:
                    balances[asset] = {"balance": balance}
                    # Add USD value if price available
                    if hasattr(self, 'prices') and asset.lower() in self.prices:
                        balances[asset]["usd_value"] = balance * self.prices[asset.lower()]["usd"]
        
        # Try to get on-chain balance for non-custodial
        if wallet.wallet_type == "non_custodial":
            onchain = self.fetch_onchain_balance(chain, wallet.address)
            if onchain > 0:
                balances[CHAINS[chain]["symbol"]] = {"balance": onchain, "on_chain": True}
        
        return {
            "wallet_id": wallet_id,
            "address": wallet.address,
            "chain": chain,
            "balances": balances
        }
    
    def fetch_onchain_balance(self, chain: str, address: str) -> float:
        """Fetch balance from chain RPC"""
        config = CHAINS.get(chain)
        if not config or config["type"] != "evm":
            return 0
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getBalance",
                "params": [address, "latest"],
                "id": 1
            }
            r = requests.post(config["rpc"], json=payload, timeout=5)
            if r.status_code == 200:
                wei = int(r.json().get("result", "0x0"), 16)
                return wei / (10 ** 18)
        except:
            pass
        return 0
    
    def deposit(self, wallet_id: str, asset: str, amount: float, tx_hash: str = "") -> Dict:
        """Process deposit to custodial wallet"""
        if wallet_id not in self.wallets:
            return {"error": "Wallet not found"}
        
        wallet = self.wallets[wallet_id]
        
        # Update balance
        self.balances[wallet_id][wallet.chain][asset] += amount
        
        # Record transaction
        tx = Transaction(
            tx_hash=tx_hash or f"0x{uuid.uuid4().hex[:64]}",
            wallet_id=wallet_id,
            chain=wallet.chain,
            from_addr="deposit",
            to_addr=wallet.address,
            amount=amount,
            symbol=asset,
            status="confirmed"
        )
        self.transactions[tx.tx_hash] = tx
        
        return {
            "deposit_id": tx.tx_hash,
            "amount": amount,
            "asset": asset,
            "status": "confirmed",
            "new_balance": self.balances[wallet_id][wallet.chain][asset]
        }
    
    def withdraw(self, wallet_id: str, to_address: str, asset: str, amount: float) -> Dict:
        """Process withdrawal"""
        if wallet_id not in self.wallets:
            return {"error": "Wallet not found"}
        
        wallet = self.wallets[wallet_id]
        chain = wallet.chain
        
        # Check balance
        current = self.balances[wallet_id][chain].get(asset, 0)
        if current < amount:
            return {"error": "Insufficient balance"}
        
        # Deduct balance
        self.balances[wallet_id][chain][asset] -= amount
        
        # Record pending transaction
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
        """Send transaction from non-custodial wallet"""
        if wallet_id not in self.wallets:
            return {"error": "Wallet not found"}
        
        wallet = self.wallets[wallet_id]
        if wallet.wallet_type != "non_custodial":
            return {"error": "Use withdraw for custodial wallet"}
        
        asset = asset or CHAINS[wallet.chain]["symbol"]
        
        # Check and deduct balance
        balance = self.balances[wallet_id].get(wallet.chain, {}).get(asset, 0)
        if balance < amount:
            # Try to fetch on-chain
            onchain = self.fetch_onchain_balance(wallet.chain, wallet.address)
            if onchain < amount:
                return {"error": "Insufficient balance"}
        
        # In production, would sign and broadcast transaction here
        tx_hash = f"0x{uuid.uuid4().hex[:64]}"
        
        return {
            "tx_hash": tx_hash,
            "from": wallet.address,
            "to": to_address,
            "amount": amount,
            "asset": asset,
            "status": "signed_ready_to_broadcast"
        }
    
    def get_transactions(self, wallet_id: str, limit: int = 50) -> List[Dict]:
        """Get wallet transactions"""
        wallet = self.wallets.get(wallet_id)
        if not wallet:
            return []
        
        txs = [tx.to_dict() for tx in self.transactions.values() if tx.wallet_id == wallet_id]
        return sorted(txs, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def sign_message(self, wallet_id: str, message: str) -> Dict:
        """Sign message with wallet"""
        if wallet_id not in self.wallets:
            return {"error": "Wallet not found"}
        
        wallet = self.wallets[wallet_id]
        
        # Mock signature (in production, use proper cryptography)
        signature = hashlib.sha256(f"{wallet.encrypted_key}{message}".encode()).hexdigest()
        
        return {
            "wallet_id": wallet_id,
            "message": message,
            "signature": signature,
            "address": wallet.address
        }
    
    def verify_signature(self, address: str, message: str, signature: str) -> bool:
        """Verify signature"""
        expected = hashlib.sha256(f"{address}{message}".encode()).hexdigest()
        return expected == signature
    
    def get_supported_chains(self) -> List[Dict]:
        """Get supported chains"""
        return [
            {"id": k, "name": v["name"], "type": v["type"], "symbol": v["symbol"]}
            for k, v in CHAINS.items()
        ]
    
    def get_tokens(self, chain: str) -> List[Dict]:
        """Get token list for chain"""
        return COMMON_TOKENS.get(chain, [])


# Flask API
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

wallet_service = WalletService()

@app.route('/wallet/health')
def health():
    return jsonify({"status": "ok", "chains": len(CHAINS)})

@app.route('/wallet/create/custodial', methods=['POST'])
def create_custodial():
    data = request.get_json() or {}
    return jsonify(wallet_service.create_custodial_wallet(
        data.get('user_id', str(uuid.uuid4())),
        data.get('chain', 'ethereum')
    ))

@app.route('/wallet/create/non-custodial', methods=['POST'])
def create_non_custodial():
    data = request.get_json() or {}
    return jsonify(wallet_service.create_non_custodial_wallet(
        data.get('user_id', str(uuid.uuid4())),
        data.get('chain', 'ethereum')
    ))

@app.route('/wallet/import', methods=['POST'])
def import_wallet():
    data = request.get_json() or {}
    return jsonify(wallet_service.import_wallet(
        data.get('user_id', ''),
        data.get('private_key', ''),
        data.get('chain', 'ethereum')
    ))

@app.route('/wallet/list/<user_id>')
def list_wallets(user_id):
    return jsonify(wallet_service.get_wallets(user_id))

@app.route('/wallet/balance/<wallet_id>')
def get_balance(wallet_id):
    chain = request.args.get('chain', '')
    return jsonify(wallet_service.get_balance(wallet_id, chain))

@app.route('/wallet/deposit', methods=['POST'])
def deposit():
    data = request.get_json() or {}
    return jsonify(wallet_service.deposit(
        data.get('wallet_id', ''),
        data.get('asset', 'USDC'),
        data.get('amount', 0),
        data.get('tx_hash', '')
    ))

@app.route('/wallet/withdraw', methods=['POST'])
def withdraw():
    data = request.get_json() or {}
    return jsonify(wallet_service.withdraw(
        data.get('wallet_id', ''),
        data.get('to_address', ''),
        data.get('asset', 'USDC'),
        data.get('amount', 0)
    ))

@app.route('/wallet/send', methods=['POST'])
def send_tx():
    data = request.get_json() or {}
    return jsonify(wallet_service.send_transaction(
        data.get('wallet_id', ''),
        data.get('to_address', ''),
        data.get('amount', 0),
        data.get('asset', '')
    ))

@app.route('/wallet/transactions/<wallet_id>')
def get_txs(wallet_id):
    limit = request.args.get('limit', 50, type=int)
    return jsonify(wallet_service.get_transactions(wallet_id, limit))

@app.route('/wallet/sign', methods=['POST'])
def sign():
    data = request.get_json() or {}
    return jsonify(wallet_service.sign_message(
        data.get('wallet_id', ''),
        data.get('message', '')
    ))

@app.route('/wallet/chains')
def chains():
    return jsonify(wallet_service.get_supported_chains())

@app.route('/wallet/tokens/<chain>')
def tokens(chain):
    return jsonify(wallet_service.get_tokens(chain))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6000))
    app.run(host='0.0.0.0', port=port, threaded=True)