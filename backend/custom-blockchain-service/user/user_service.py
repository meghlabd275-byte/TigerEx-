#!/usr/bin/env python3
"""
TigerEx Custom Blockchain Service - User Interface
Supports EVM and Non-EVM chains for user transactions
"""
import os
import json
import hashlib
import logging
import uuid
import time
import threading
import requests
from typing import Dict, List
from datetime import datetime
from collections import defaultdict
from flask import Flask, jsonify, request
from flask_cors import CORS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Chain configurations
CHAINS = {
    "tigerex": {"name": "TigerExChain", "type": "evm", "chain_id": 9999, "symbol": "TIG", "rpc": "http://localhost:6200", "decimals": 18},
    "ethereum": {"name": "Ethereum", "type": "evm", "chain_id": 1, "symbol": "ETH"},
    "bsc": {"name": "BNB Chain", "type": "evm", "chain_id": 56, "symbol": "BNB"},
    "polygon": {"name": "Polygon", "type": "evm", "chain_id": 137, "symbol": "MATIC"},
    "arbitrum": {"name": "Arbitrum", "type": "evm", "chain_id": 42161, "symbol": "ETH"},
    "avalanche": {"name": "Avalanche", "type": "evm", "chain_id": 43114, "symbol": "AVAX"},
    "solana": {"name": "Solana", "type": "non_evm", "symbol": "SOL"},
    "ton": {"name": "TON", "type": "non_evm", "symbol": "TON"},
    "near": {"name": "NEAR", "type": "non_evm", "symbol": "NEAR"},
    "aptos": {"name": "Aptos", "type": "non_evm", "symbol": "APT"},
    "sui": {"name": "Sui", "type": "non_evm", "symbol": "SUI"},
    "cosmos": {"name": "Cosmos", "type": "non_evm", "symbol": "ATOM"},
}


class BlockchainUserService:
    """User-facing blockchain service"""
    
    def __init__(self):
        self.accounts = {}
        self.transactions = {}
        self.pending_txs = []
        self.blocks = {}
        self.prices = {}
        
        # Initialize
        self._init_block0()
        self._update_prices()
        
        logger.info("Blockchain User Service initialized")
    
    def _init_block0(self):
        self.blocks[0] = {
            "number": 0,
            "hash": "0x" + "0" * 64,
            "timestamp": datetime.utcnow().isoformat(),
            "txs": []
        }
    
    def _update_prices(self):
        try:
            ids = "ethereum,solana,ton,near,aptos"
            r = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd", timeout=10)
            if r.status_code == 200:
                self.prices = r.json()
        except Exception as e:
            logger.warning(f"Price update error: {e}")
    
    # --- User Methods ---
    
    def create_account(self, user_id: str) -> Dict:
        """Create new account"""
        address = "0x" + hashlib.sha256(f"{user_id}{time.time()}".encode()).hexdigest()[-40:]
        
        self.accounts[address] = {
            "address": address,
            "balance": 0,
            "nonce": 0,
            "code": ""
        }
        
        return {"address": address, "balance": 0, "nonce": 0}
    
    def get_balance(self, address: str) -> Dict:
        """Get account balance"""
        if address in self.accounts:
            acc = self.accounts[address]
            return {"address": address, "balance": acc["balance"], "nonce": acc["nonce"]}
        return {"address": address, "balance": 0, "nonce": 0}
    
    def send_transaction(self, from_addr: str, to_addr: str, value: float, gas_price: int = 20000000000) -> Dict:
        """Send transaction"""
        if from_addr not in self.accounts:
            return {"error": "Sender account not found"}
        
        sender = self.accounts[from_addr]
        
        if sender["balance"] < value:
            return {"error": "Insufficient balance"}
        
        sender["balance"] -= value
        sender["nonce"] += 1
        
        if to_addr not in self.accounts:
            self.accounts[to_addr] = {"address": to_addr, "balance": 0, "nonce": 0}
        self.accounts[to_addr]["balance"] += value
        
        tx_hash = f"0x{uuid.uuid4().hex[:64]}"
        tx = {
            "hash": tx_hash,
            "from": from_addr,
            "to": to_addr,
            "value": value,
            "gasPrice": gas_price,
            "nonce": sender["nonce"],
            "status": "pending",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.transactions[tx_hash] = tx
        self.pending_txs.append(tx_hash)
        
        return {"tx_hash": tx_hash, "status": "pending"}
    
    def get_transaction(self, tx_hash: str) -> Dict:
        """Get transaction"""
        if tx_hash in self.transactions:
            return self.transactions[tx_hash]
        
        # Check pending
        for tx in self.pending_txs:
            if isinstance(tx, dict) and tx.get("hash") == tx_hash:
                return tx
        
        return {"error": "Transaction not found"}
    
    def get_block(self, block_number: int) -> Dict:
        """Get block"""
        if block_number in self.blocks:
            return self.blocks[block_number]
        return {"error": "Block not found"}
    
    def get_latest_block(self) -> Dict:
        """Get latest block"""
        if self.blocks:
            latest = max(self.blocks.keys())
            return self.blocks[latest]
        return {"error": "No blocks"}
    
    def get_chain_config(self, chain_id: str) -> Dict:
        """Get chain configuration"""
        if chain_id in CHAINS:
            return CHAINS[chain_id]
        return {"error": "Chain not found"}
    
    def get_supported_chains(self) -> List[Dict]:
        """Get supported chains"""
        return [{"id": k, "name": v["name"], "type": v["type"], "symbol": v["symbol"]} for k, v in CHAINS.items()]
    
    def deploy_contract(self, from_addr: str, bytecode: str) -> Dict:
        """Deploy contract"""
        if from_addr not in self.accounts:
            return {"error": "Account not found"}
        
        contract_addr = "0x" + hashlib.sha256(f"{bytecode}{time.time()}".encode()).hexdigest()[-40:]
        
        self.accounts[contract_addr] = {
            "address": contract_addr,
            "balance": 0,
            "nonce": 0,
            "code": bytecode
        }
        
        tx_hash = f"0x{uuid.uuid4().hex[:64]}"
        
        return {"tx_hash": tx_hash, "contract_address": contract_addr, "status": "deployed"}
    
    def call_contract(self, from_addr: str, contract_addr: str, method: str, params: List) -> Dict:
        """Call contract"""
        if from_addr not in self.accounts:
            return {"error": "Account not found"}
        
        if contract_addr not in self.accounts:
            return {"error": "Contract not found"}
        
        return {"result": f"Called {method}", "status": "success"}
    
    def get_code(self, address: str) -> Dict:
        """Get contract code"""
        if address in self.accounts and self.accounts[address].get("code"):
            return {"address": address, "code": self.accounts[address]["code"]}
        return {"address": address, "code": ""}
    
    def estimate_gas(self, from_addr: str, to_addr: str, value: float) -> Dict:
        """Estimate gas"""
        return {"gasEstimate": 21000, "gasPrice": 20000000000}


# Create Flask app
app = Flask(__name__)
CORS(app)

blockchain_user_service = BlockchainUserService()


@app.route('/blockchain/user/health')
def health():
    return jsonify({"status": "ok", "service": "blockchain", "role": "user"})


@app.route('/blockchain/user/create-account', methods=['POST'])
def create_account():
    data = request.get_json() or {}
    return jsonify(blockchain_user_service.create_account(
        data.get('user_id', str(uuid.uuid4()))
    ))


@app.route('/blockchain/user/balance/<address>')
def user_balance(address):
    return jsonify(blockchain_user_service.get_balance(address))


@app.route('/blockchain/user/send', methods=['POST'])
def user_send():
    data = request.get_json() or {}
    return jsonify(blockchain_user_service.send_transaction(
        data.get('from', ''),
        data.get('to', ''),
        data.get('value', 0),
        data.get('gas_price', 20000000000)
    ))


@app.route('/blockchain/user/transaction/<tx_hash>')
def user_tx(tx_hash):
    return jsonify(blockchain_user_service.get_transaction(tx_hash))


@app.route('/blockchain/user/block/<int:block_number>')
def user_block(block_number):
    return jsonify(blockchain_user_service.get_block(block_number))


@app.route('/blockchain/user/latest-block')
def user_latest():
    return jsonify(blockchain_user_service.get_latest_block())


@app.route('/blockchain/user/chain/<chain_id>')
def user_chain(chain_id):
    return jsonify(blockchain_user_service.get_chain_config(chain_id))


@app.route('/blockchain/user/chains')
def user_chains():
    return jsonify(blockchain_user_service.get_supported_chains())


@app.route('/blockchain/user/deploy', methods=['POST'])
def user_deploy():
    data = request.get_json() or {}
    return jsonify(blockchain_user_service.deploy_contract(
        data.get('from', ''),
        data.get('bytecode', '')
    ))


@app.route('/blockchain/user/call', methods=['POST'])
def user_call():
    data = request.get_json() or {}
    return jsonify(blockchain_user_service.call_contract(
        data.get('from', ''),
        data.get('contract', ''),
        data.get('method', ''),
        data.get('params', [])
    ))


@app.route('/blockchain/user/code/<address>')
def user_code(address):
    return jsonify(blockchain_user_service.get_code(address))


@app.route('/blockchain/user/estimate-gas', methods=['POST'])
def user_estimate():
    data = request.get_json() or {}
    return jsonify(blockchain_user_service.estimate_gas(
        data.get('from', ''),
        data.get('to', ''),
        data.get('value', 0)
    ))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6201))
    logger.info(f"Starting User Blockchain Service on port {port}")
    app.run(host='0.0.0.0', port=port, threaded=True)