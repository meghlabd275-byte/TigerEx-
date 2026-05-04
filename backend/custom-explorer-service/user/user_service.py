#!/usr/bin/env python3
"""
TigerEx Custom Block Explorer Service - User Interface
Supports EVM and Non-EVM block explorers
"""
import os
import json
import hashlib
import logging
import uuid
import time
import requests
from typing import Dict, List
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Chain configurations
CHAINS = {
    "tigerex": {"name": "TigerEx Explorer", "type": "evm", "chain_id": 9999, "symbol": "TIG"},
    "ethereum": {"name": "Etherscan", "type": "evm", "chain_id": 1, "symbol": "ETH", "explorer": "https://etherscan.io"},
    "bsc": {"name": "BscScan", "type": "evm", "chain_id": 56, "symbol": "BNB", "explorer": "https://bscscan.com"},
    "polygon": {"name": "Polygonscan", "type": "evm", "chain_id": 137, "symbol": "MATIC", "explorer": "https://polygonscan.com"},
    "arbitrum": {"name": "Arbiscan", "type": "evm", "chain_id": 42161, "symbol": "ETH", "explorer": "https://arbiscan.io"},
    "avalanche": {"name": "Snowtrace", "type": "evm", "chain_id": 43114, "symbol": "AVAX", "explorer": "https://snowtrace.io"},
    "solana": {"name": "Solscan", "type": "non_evm", "symbol": "SOL", "explorer": "https://solscan.io"},
    "ton": {"name": "Tonscan", "type": "non_evm", "symbol": "TON", "explorer": "https://tonscan.org"},
    "near": {"name": "NEAR Explorer", "type": "non_evm", "symbol": "NEAR", "explorer": "https://explorer.near.org"},
    "aptos": {"name": "Aptos Explorer", "type": "non_evm", "symbol": "APT", "explorer": "https://explorer.aptoslabs.com"},
    "sui": {"name": "Suiscan", "type": "non_evm", "symbol": "SUI", "explorer": "https://suiscan.xyz"},
    "cosmos": {"name": "Mintscan", "type": "non_evm", "symbol": "ATOM", "explorer": "https://mintscan.io"},
}


class ExplorerUserService:
    """User-facing explorer service"""
    
    def __init__(self):
        self.blocks = {}
        self.transactions = {}
        self.addresses = {}
        self.tokens = {}
        
        # Initialize sample data
        self._init_sample_data()
        
        logger.info("Explorer User Service initialized")
    
    def _init_sample_data(self):
        """Initialize with sample data"""
        for i in range(100):
            self.blocks[i] = {
                "number": i,
                "hash": f"0x{uuid.uuid4().hex[:64]}",
                "parentHash": f"0x{uuid.uuid4().hex[:64]}",
                "timestamp": (datetime.utcnow() - timedelta(hours=100-i)).isoformat(),
                "tx_count": i * 3,
                "miner": "0x" + "1" * 40,
                "gasUsed": i * 15000,
                "gasLimit": 30000000,
            }
        
        for i in range(200):
            tx_hash = f"0x{uuid.uuid4().hex[:64]}"
            self.transactions[tx_hash] = {
                "hash": tx_hash,
                "block": i % 100,
                "from": f"0x{uuid.uuid4().hex[:40]}",
                "to": f"0x{uuid.uuid4().hex[:40]}",
                "value": float(i % 100),
                "gasPrice": 20000000000,
                "gasUsed": 21000,
                "nonce": i % 10,
                "type": "0x",
                "status": "success" if i % 10 != 0 else "pending",
                "timestamp": (datetime.utcnow() - timedelta(hours=i)).isoformat(),
            }
        
        for i in range(50):
            addr = f"0x{uuid.uuid4().hex[:40]}"
            self.addresses[addr] = {
                "address": addr,
                "balance": float(i * 10),
                "txCount": i * 5,
                "firstTx": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                "lastTx": datetime.utcnow().isoformat(),
                "isContract": False,
            }
    
    # --- User Methods ---
    
    def get_block(self, block_number: int) -> Dict:
        """Get block by number"""
        if block_number in self.blocks:
            return self.blocks[block_number]
        return {"error": "Block not found"}
    
    def get_block_by_hash(self, block_hash: str) -> Dict:
        """Get block by hash"""
        for block in self.blocks.values():
            if block.get("hash") == block_hash:
                return block
        return {"error": "Block not found"}
    
    def get_transaction(self, tx_hash: str) -> Dict:
        """Get transaction"""
        if tx_hash in self.transactions:
            return self.transactions[tx_hash]
        return {"error": "Transaction not found"}
    
    def get_address(self, address: str) -> Dict:
        """Get address details"""
        if address in self.addresses:
            return self.addresses[address]
        return {"error": "Address not found"}
    
    def get_address_txs(self, address: str, limit: int = 50) -> List[Dict]:
        """Get address transactions"""
        txs = [tx for tx in self.transactions.values() 
              if tx.get("from") == address or tx.get("to") == address]
        return sorted(txs, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]
    
    def get_token(self, address: str) -> Dict:
        """Get token"""
        if address in self.tokens:
            return self.tokens[address]
        return {"error": "Token not found"}
    
    def get_token_holders(self, address: str) -> List[Dict]:
        """Get token holders"""
        return [{"address": a, "balance": self.addresses[a].get("balance", 0)} 
                for a in list(self.addresses.keys())[:10]]
    
    def search(self, query: str) -> Dict:
        """Search"""
        # Check if block number
        try:
            num = int(query)
            if num in self.blocks:
                return {"type": "block", "data": self.blocks[num]}
        except:
            pass
        
        # Check if address
        if query.startswith("0x") and len(query) == 42:
            if query in self.addresses:
                return {"type": "address", "data": self.addresses[query]}
            if query in self.tokens:
                return {"type": "token", "data": self.tokens[query]}
        
        # Check if tx hash
        if query.startswith("0x") and len(query) == 66:
            if query in self.transactions:
                return {"type": "transaction", "data": self.transactions[query]}
        
        return {"error": "Not found"}
    
    def get_latest_blocks(self, limit: int = 10) -> List[Dict]:
        """Get latest blocks"""
        blocks = sorted(self.blocks.values(), key=lambda b: b.get("number", 0), reverse=True)
        return list(blocks)[:limit]
    
    def get_latest_transactions(self, limit: int = 10) -> List[Dict]:
        """Get latest transactions"""
        txs = sorted(self.transactions.values(), key=lambda x: x.get("timestamp", ""), reverse=True)
        return list(txs)[:limit]
    
    def get_chain_info(self, chain_id: str) -> Dict:
        """Get chain info"""
        if chain_id in CHAINS:
            return CHAINS[chain_id]
        return {"error": "Chain not found"}
    
    def get_supported_chains(self) -> List[Dict]:
        return [{"id": k, "name": v["name"], "type": v["type"], "symbol": v["symbol"]} for k, v in CHAINS.items()]
    
    def get_gas_oracle(self, chain_id: str = "tigerex") -> Dict:
        """Get gas prices"""
        return {
            "chain": chain_id,
            "slow": 10000000000,
            "average": 20000000000,
            "fast": 50000000000,
            "last_update": datetime.utcnow().isoformat()
        }


# Create Flask app
app = Flask(__name__)
CORS(app)

explorer_user_service = ExplorerUserService()


@app.route('/explorer/user/health')
def health():
    return jsonify({"status": "ok", "service": "explorer", "role": "user"})


@app.route('/explorer/user/block/<int:block_number>')
def user_block(block_number):
    return jsonify(explorer_user_service.get_block(block_number))


@app.route('/explorer/user/block-by-hash/<block_hash>')
def user_block_hash(block_hash):
    return jsonify(explorer_user_service.get_block_by_hash(block_hash))


@app.route('/explorer/user/transaction/<tx_hash>')
def user_tx(tx_hash):
    return jsonify(explorer_user_service.get_transaction(tx_hash))


@app.route('/explorer/user/address/<address>')
def user_address(address):
    return jsonify(explorer_user_service.get_address(address))


@app.route('/explorer/user/address-txs/<address>')
def user_address_txs(address):
    limit = request.args.get('limit', 50, type=int)
    return jsonify(explorer_user_service.get_address_txs(address, limit))


@app.route('/explorer/user/token/<address>')
def user_token(address):
    return jsonify(explorer_user_service.get_token(address))


@app.route('/explorer/user/token-holders/<address>')
def user_token_holders(address):
    return jsonify(explorer_user_service.get_token_holders(address))


@app.route('/explorer/user/search')
def user_search():
    query = request.args.get('q', '')
    return jsonify(explorer_user_service.search(query))


@app.route('/explorer/user/latest-blocks')
def user_latest_blocks():
    limit = request.args.get('limit', 10, type=int)
    return jsonify(explorer_user_service.get_latest_blocks(limit))


@app.route('/explorer/user/latest-transactions')
def user_latest_txs():
    limit = request.args.get('limit', 10, type=int)
    return jsonify(explorer_user_service.get_latest_transactions(limit))


@app.route('/explorer/user/chain/<chain_id>')
def user_chain(chain_id):
    return jsonify(explorer_user_service.get_chain_info(chain_id))


@app.route('/explorer/user/chains')
def user_chains():
    return jsonify(explorer_user_service.get_supported_chains())


@app.route('/explorer/user/gas')
def user_gas():
    chain_id = request.args.get('chain', 'tigerex')
    return jsonify(explorer_user_service.get_gas_oracle(chain_id))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6301))
    logger.info(f"Starting User Block Explorer Service on port {port}")
    app.run(host='0.0.0.0', port=port, threaded=True)