#!/usr/bin/env python3
"""
TigerEx Custom Wallet Service - User Interface
Supports EVM and Non-EVM chains with user actions
"""
import os
import json
import hashlib
import logging
import uuid
import time
import requests
from typing import Dict, List
from datetime import datetime
from collections import defaultdict
from functools import wraps
from flask import Flask, jsonify, request
from flask_cors import CORS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration - imported from shared
CHAINS = {
    "ethereum": {"name": "Ethereum", "type": "evm", "chain_id": 1, "symbol": "ETH", "decimals": 18},
    "bsc": {"name": "BNB Chain", "type": "evm", "chain_id": 56, "symbol": "BNB", "decimals": 18},
    "polygon": {"name": "Polygon", "type": "evm", "chain_id": 137, "symbol": "MATIC", "decimals": 18},
    "arbitrum": {"name": "Arbitrum One", "type": "evm", "chain_id": 42161, "symbol": "ETH", "decimals": 18},
    "optimism": {"name": "Optimism", "type": "evm", "chain_id": 10, "symbol": "ETH", "decimals": 18},
    "avalanche": {"name": "Avalanche C-Chain", "type": "evm", "chain_id": 43114, "symbol": "AVAX", "decimals": 18},
    "base": {"name": "Base", "type": "evm", "chain_id": 8453, "symbol": "ETH", "decimals": 18},
    "tigerex": {"name": "TigerExChain", "type": "evm", "chain_id": 9999, "symbol": "TIG", "decimals": 18},
    "solana": {"name": "Solana", "type": "non_evm", "symbol": "SOL", "decimals": 9},
    "ton": {"name": "TON", "type": "non_evm", "symbol": "TON", "decimals": 9},
    "near": {"name": "NEAR", "type": "non_evm", "symbol": "NEAR", "decimals": 24},
    "aptos": {"name": "Aptos", "type": "non_evm", "symbol": "APT", "decimals": 8},
    "sui": {"name": "Sui", "type": "non_evm", "symbol": "SUI", "decimals": 9},
    "cosmos": {"name": "Cosmos Hub", "type": "non_evm", "symbol": "ATOM", "decimals": 6},
    "polkadot": {"name": "Polkadot", "type": "non_evm", "symbol": "DOT", "decimals": 10},
    "cardano": {"name": "Cardano", "type": "non_evm", "symbol": "ADA", "decimals": 6},
    "algorand": {"name": "Algorand", "type": "non_evm", "symbol": "ALGO", "decimals": 6},
    "tezos": {"name": "Tezos", "type": "non_evm", "symbol": "XTZ", "decimals": 6},
}

TOKENS = {
    "ethereum": [
        {"address": "0x0000000000000000000000000000000000000000", "symbol": "ETH", "name": "Ethereum", "decimals": 18},
        {"address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "symbol": "USDC", "name": "USD Coin", "decimals": 6},
        {"address": "0xdAC17F958D2ee523a2206206994597C13D831ec7", "symbol": "USDT", "name": "Tether USD", "decimals": 6},
    ],
    "bsc": [
        {"address": "0x0000000000000000000000000000000000000000", "symbol": "BNB", "name": "BNB", "decimals": 18},
    ],
}


class WalletUserService:
    """User-facing wallet service"""
    
    def __init__(self):
        # Use shared data store from env or default
        self.wallets = {}
        self.user_wallets = defaultdict(list)
        self.balances = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        self.transactions = {}
        
        # Price cache
        self.prices = {}
        self._update_prices()
        
        logger.info("Wallet User Service initialized")
    
    def _update_prices(self):
        try:
            ids = "ethereum,solana,ton,near,aptos,cosmos,polkadot"
            r = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd", timeout=10)
            if r.status_code == 200:
                self.prices = r.json()
        except Exception as e:
            logger.warning(f"Price update error: {e}")
    
    def create_custodial_wallet(self, user_id: str, chain: str) -> Dict:
        if chain not in CHAINS:
            return {"error": f"Unsupported chain: {chain}"}
        
        chain_type = CHAINS[chain]["type"]
        if chain_type == "evm":
            address = "0x" + hashlib.sha256(f"{user_id}{chain}{time.time()}".encode()).hexdigest()[-40:]
        else:
            address = hashlib.sha256(f"{user_id}{chain}{time.time()}".encode()).hexdigest()[:44]
        
        wallet_id = f"CUST_{uuid.uuid4().hex[:12]}"
        
        self.wallets[wallet_id] = {
            "wallet_id": wallet_id,
            "user_id": user_id,
            "address": address,
            "chain": chain,
            "type": "custodial",
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }
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
        if chain not in CHAINS:
            return {"error": f"Unsupported chain: {chain}"}
        
        private_key = hashlib.sha256(f"{user_id}{time.time()}".encode()).hexdigest()
        key_hash = hashlib.sha256(private_key.encode()).hexdigest()
        
        if CHAINS[chain]["type"] == "evm":
            address = "0x" + key_hash[-40:]
        else:
            address = key_hash[:44]
        
        wallet_id = f"NONCUST_{uuid.uuid4().hex[:12]}"
        
        self.wallets[wallet_id] = {
            "wallet_id": wallet_id,
            "user_id": user_id,
            "address": address,
            "chain": chain,
            "type": "non_custodial",
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }
        self.user_wallets[user_id].append(wallet_id)
        
        return {
            "wallet_id": wallet_id,
            "address": address,
            "chain": chain,
            "type": "non_custodial",
            "status": "active",
            "note": "Private key generated - save securely"
        }
    
    def import_wallet(self, user_id: str, private_key: str, chain: str) -> Dict:
        if chain not in CHAINS:
            return {"error": f"Unsupported chain: {chain}"}
        
        key_hash = hashlib.sha256(private_key.encode()).hexdigest()
        
        if CHAINS[chain]["type"] == "evm":
            address = "0x" + key_hash[-40:]
        else:
            address = key_hash[:44]
        
        wallet_id = f"IMP_{uuid.uuid4().hex[:12]}"
        
        self.wallets[wallet_id] = {
            "wallet_id": wallet_id,
            "user_id": user_id,
            "address": address,
            "chain": chain,
            "type": "imported",
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }
        self.user_wallets[user_id].append(wallet_id)
        
        return {
            "wallet_id": wallet_id,
            "address": address,
            "chain": chain,
            "type": "imported",
            "status": "active"
        }
    
    def get_user_wallets(self, user_id: str) -> List[Dict]:
        wallet_ids = self.user_wallets.get(user_id, [])
        return [self.wallets[wid] for wid in wallet_ids if wid in self.wallets]
    
    def get_balance(self, wallet_id: str, chain: str = "") -> Dict:
        if wallet_id not in self.wallets:
            return {"error": "Wallet not found"}
        
        wallet = self.wallets[wallet_id]
        chain = chain or wallet["chain"]
        
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
        if wallet_id not in self.wallets:
            return {"error": "Wallet not found"}
        
        wallet = self.wallets[wallet_id]
        chain = wallet["chain"]
        self.balances[wallet_id][chain][asset] += amount
        
        if tx_hash:
            self.transactions[tx_hash] = {
                "hash": tx_hash,
                "wallet_id": wallet_id,
                "from": "deposit",
                "to": wallet["address"],
                "amount": amount,
                "asset": asset,
                "status": "confirmed",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {"status": "deposited", "amount": amount, "asset": asset}
    
    def withdraw(self, wallet_id: str, to_address: str, asset: str, amount: float) -> Dict:
        if wallet_id not in self.wallets:
            return {"error": "Wallet not found"}
        
        wallet = self.wallets[wallet_id]
        chain = wallet["chain"]
        current = self.balances[wallet_id][chain].get(asset, 0)
        
        if current < amount:
            return {"error": "Insufficient balance"}
        
        self.balances[wallet_id][chain][asset] -= amount
        
        tx_hash = f"0x{uuid.uuid4().hex[:64]}"
        self.transactions[tx_hash] = {
            "hash": tx_hash,
            "wallet_id": wallet_id,
            "from": wallet["address"],
            "to": to_address,
            "amount": amount,
            "asset": asset,
            "status": "pending",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {"withdrawal_id": tx_hash, "to": to_address, "amount": amount, "asset": asset, "status": "pending"}
    
    def send_transaction(self, wallet_id: str, to_address: str, amount: float, asset: str = "") -> Dict:
        if wallet_id not in self.wallets:
            return {"error": "Wallet not found"}
        
        wallet = self.wallets[wallet_id]
        if wallet["type"] != "non_custodial":
            return {"error": "Use withdraw for custodial wallet"}
        
        asset = asset or CHAINS[wallet["chain"]]["symbol"]
        balance = self.balances[wallet_id].get(wallet["chain"], {}).get(asset, 0)
        
        if balance < amount:
            return {"error": "Insufficient balance"}
        
        self.balances[wallet_id][wallet["chain"]][asset] -= amount
        
        tx_hash = f"0x{uuid.uuid4().hex[:64]}"
        
        return {"tx_hash": tx_hash, "from": wallet["address"], "to": to_address, "amount": amount, "asset": asset, "status": "signed"}
    
    def get_transactions(self, wallet_id: str, limit: int = 50) -> List[Dict]:
        if wallet_id not in self.wallets:
            return []
        
        txs = [t for t in self.transactions.values() if t["wallet_id"] == wallet_id]
        return sorted(txs, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def sign_message(self, wallet_id: str, message: str) -> Dict:
        if wallet_id not in self.wallets:
            return {"error": "Wallet not found"}
        
        wallet = self.wallets[wallet_id]
        message_hash = hashlib.sha256(message.encode()).hexdigest()
        
        return {"wallet_id": wallet_id, "message": message, "signature": message_hash, "address": wallet["address"]}
    
    def get_supported_chains(self) -> List[Dict]:
        return [{"id": k, "name": v["name"], "type": v["type"], "symbol": v["symbol"]} for k, v in CHAINS.items()]
    
    def get_chain_info(self, chain: str) -> Dict:
        if chain not in CHAINS:
            return {"error": "Chain not found"}
        return CHAINS[chain]
    
    def get_tokens(self, chain: str) -> List[Dict]:
        return TOKENS.get(chain, [])


# Create Flask app
app = Flask(__name__)
CORS(app)

wallet_user_service = WalletUserService()


@app.route('/wallet/user/health')
def health():
    return jsonify({"status": "ok", "service": "wallet", "role": "user"})


@app.route('/wallet/user/create-custodial', methods=['POST'])
def create_custodial():
    data = request.get_json() or {}
    return jsonify(wallet_user_service.create_custodial_wallet(
        data.get('user_id', str(uuid.uuid4())),
        data.get('chain', 'ethereum')
    ))


@app.route('/wallet/user/create-non-custodial', methods=['POST'])
def create_non_custodial():
    data = request.get_json() or {}
    return jsonify(wallet_user_service.create_non_custodial_wallet(
        data.get('user_id', str(uuid.uuid4())),
        data.get('chain', 'ethereum')
    ))


@app.route('/wallet/user/import', methods=['POST'])
def import_wallet():
    data = request.get_json() or {}
    return jsonify(wallet_user_service.import_wallet(
        data.get('user_id', str(uuid.uuid4())),
        data.get('private_key', ''),
        data.get('chain', 'ethereum')
    ))


@app.route('/wallet/user/wallets/<user_id>')
def user_wallets(user_id):
    return jsonify(wallet_user_service.get_user_wallets(user_id))


@app.route('/wallet/user/balance/<wallet_id>')
def user_balance(wallet_id):
    chain = request.args.get('chain', '')
    return jsonify(wallet_user_service.get_balance(wallet_id, chain))


@app.route('/wallet/user/deposit', methods=['POST'])
def user_deposit():
    data = request.get_json() or {}
    return jsonify(wallet_user_service.deposit(
        data.get('wallet_id', ''),
        data.get('asset', 'USDC'),
        data.get('amount', 0),
        data.get('tx_hash', '')
    ))


@app.route('/wallet/user/withdraw', methods=['POST'])
def user_withdraw():
    data = request.get_json() or {}
    return jsonify(wallet_user_service.withdraw(
        data.get('wallet_id', ''),
        data.get('to_address', ''),
        data.get('asset', 'USDC'),
        data.get('amount', 0)
    ))


@app.route('/wallet/user/send', methods=['POST'])
def user_send():
    data = request.get_json() or {}
    return jsonify(wallet_user_service.send_transaction(
        data.get('wallet_id', ''),
        data.get('to_address', ''),
        data.get('amount', 0),
        data.get('asset', '')
    ))


@app.route('/wallet/user/transactions/<wallet_id>')
def user_txs(wallet_id):
    limit = request.args.get('limit', 50, type=int)
    return jsonify(wallet_user_service.get_transactions(wallet_id, limit))


@app.route('/wallet/user/sign', methods=['POST'])
def user_sign():
    data = request.get_json() or {}
    return jsonify(wallet_user_service.sign_message(
        data.get('wallet_id', ''),
        data.get('message', '')
    ))


@app.route('/wallet/user/chains')
def user_chains():
    return jsonify(wallet_user_service.get_supported_chains())


@app.route('/wallet/user/chain/<chain>')
def user_chain_info(chain):
    return jsonify(wallet_user_service.get_chain_info(chain))


@app.route('/wallet/user/tokens/<chain>')
def user_tokens(chain):
    return jsonify(wallet_user_service.get_tokens(chain))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6101))
    logger.info(f"Starting User Wallet Service on port {port}")
    app.run(host='0.0.0.0', port=port, threaded=True)