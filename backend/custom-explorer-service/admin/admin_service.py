#!/usr/bin/env python3
"""
TigerEx Custom Block Explorer Service - Admin Interface
Supports EVM and Non-EVM block explorers
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
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# EXPLORER CONFIGURATION - SUPPORTED CHAINS
# ============================================================
EXPLORERS = {
    "tigerex": {
        "name": "TigerEx Explorer",
        "type": "evm",
        "chain_id": 9999,
        "symbol": "TIG",
        "rpc": "http://localhost:6200",
        "api_url": "http://localhost:6300",
    },
    "ethereum": {"name": "Etherscan", "type": "evm", "chain_id": 1, "symbol": "ETH", "explorer": "https://etherscan.io"},
    "bsc": {"name": "BscScan", "type": "evm", "chain_id": 56, "symbol": "BNB", "explorer": "https://bscscan.com"},
    "polygon": {"name": "Polygonscan", "type": "evm", "chain_id": 137, "symbol": "MATIC", "explorer": "https://polygonscan.com"},
    "arbitrum": {"name": "Arbiscan", "type": "evm", "chain_id": 42161, "symbol": "ETH", "explorer": "https://arbiscan.io"},
    "avalanche": {"name": "Snowtrace", "type": "evm", "chain_id": 43114, "symbol": "AVAX", "explorer": "https://snowtrace.io"},
    "optimism": {"name": "Optimistic Etherscan", "type": "evm", "chain_id": 10, "symbol": "ETH", "explorer": "https://optimistic.etherscan.io"},
    "base": {"name": "Basescan", "type": "evm", "chain_id": 8453, "symbol": "ETH", "explorer": "https://basescan.org"},
    "solana": {"name": "Solscan", "type": "non_evm", "symbol": "SOL", "explorer": "https://solscan.io"},
    "ton": {"name": "Tonscan", "type": "non_evm", "symbol": "TON", "explorer": "https://tonscan.org"},
    "near": {"name": "NEAR Explorer", "type": "non_evm", "symbol": "NEAR", "explorer": "https://explorer.near.org"},
    "aptos": {"name": "Aptos Explorer", "type": "non_evm", "symbol": "APT", "explorer": "https://explorer.aptoslabs.com"},
    "sui": {"name": "Suiscan", "type": "non_evm", "symbol": "SUI", "explorer": "https://suiscan.xyz"},
    "cosmos": {"name": "Mintscan", "type": "non_evm", "symbol": "ATOM", "explorer": "https://mintscan.io"},
    "polkadot": {"name": "Subscan", "type": "non_evm", "symbol": "DOT", "explorer": "https://polkadot.subscan.io"},
    "cardano": {"name": "Cardanoscan", "type": "non_evm", "symbol": "ADA", "explorer": "https://cardanoscan.io"},
}


# ============================================================
# DATA MODELS
# ============================================================
@dataclass
class Block:
    block_number: int
    block_hash: str
    parent_hash: str
    timestamp: datetime
    tx_count: int
    miner: str
    gas_used: int
    gas_limit: int
    difficulty: int
    size: int
    
    def to_dict(self) -> Dict:
        return {
            "number": self.block_number,
            "hash": self.block_hash,
            "parentHash": self.parent_hash,
            "timestamp": self.timestamp.isoformat(),
            "transactions": self.tx_count,
            "miner": self.miner,
            "gasUsed": self.gas_used,
            "gasLimit": self.gas_limit,
            "difficulty": self.difficulty,
            "size": self.size,
        }


@dataclass
class Transaction:
    tx_hash: str
    block_number: int
    from_addr: str
    to_addr: str
    value: float
    gas_price: int
    gas_used: int
    nonce: int
    tx_type: str
    status: str
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        return {
            "hash": self.tx_hash,
            "block": self.block_number,
            "from": self.from_addr,
            "to": self.to_addr,
            "value": self.value,
            "gasPrice": self.gas_price,
            "gasUsed": self.gas_used,
            "nonce": self.nonce,
            "type": self.tx_type,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class Address:
    address: str
    balance: float
    tx_count: int
    first_tx: datetime
    last_tx: datetime
    is_contract: bool
    contract_code: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "address": self.address,
            "balance": self.balance,
            "txCount": self.tx_count,
            "firstTx": self.first_tx.isoformat(),
            "lastTx": self.last_tx.isoformat(),
            "isContract": self.is_contract,
        }


@dataclass
class Token:
    address: str
    symbol: str
    name: str
    decimals: int
    total_supply: float
    holders: int
    transfers: int
    
    def to_dict(self) -> Dict:
        return {
            "address": self.address,
            "symbol": self.symbol,
            "name": self.name,
            "decimals": self.decimals,
            "totalSupply": self.total_supply,
            "holders": self.holders,
            "transfers": self.transfers,
        }


@dataclass
class Contract:
    address: str
    creator: str
    bytecode: str
    salt: str
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        return {
            "address": self.address,
            "creator": self.creator,
            "bytecode": self.bytecode[:100] + "...",
            "timestamp": self.timestamp.isoformat(),
        }


# ============================================================
# EXPLORER ENGINE
# ============================================================
class ExplorerService:
    """Block explorer engine"""
    
    def __init__(self):
        self.blocks = {}
        self.transactions = {}
        self.addresses = {}
        self.tokens = {}
        self.contracts = {}
        self.internal_txs = {}
        self.token_transfers = {}
        self.admin_actions = []
        self.admins = set()
        
        # Initialize index
        self._init_index()
        
        logger.info("Custom Block Explorer Service initialized")
    
    def _init_index(self):
        """Initialize with some data"""
        for i in range(100):
            block = Block(
                block_number=i,
                block_hash=f"0x{uuid.uuid4().hex[:64]}",
                parent_hash=f"0x{uuid.uuid4().hex[:64]}" if i > 0 else "0x" + "0" * 64,
                timestamp=datetime.utcnow() - timedelta(hours=100-i),
                tx_count=i * 3,
                miner="0x" + "1" * 40,
                gas_used=i * 15000,
                gas_limit=30000000,
                difficulty=1,
                size=1000 + i * 100
            )
            self.blocks[i] = block
        
        # Create some addresses
        for i in range(50):
            addr = f"0x{uuid.uuid4().hex[:40]}"
            self.addresses[addr] = Address(
                address=addr,
                balance=float(i * 10),
                tx_count=i * 5,
                first_tx=datetime.utcnow() - timedelta(days=30),
                last_tx=datetime.utcnow() - timedelta(hours=i),
                is_contract=False
            )
        
        # Create some transactions
        for i in range(200):
            from_addr = f"0x{uuid.uuid4().hex[:40]}"
            to_addr = f"0x{uuid.uuid4().hex[:40]}"
            tx = Transaction(
                tx_hash=f"0x{uuid.uuid4().hex[:64]}",
                block_number=i % 100,
                from_addr=from_addr,
                to_addr=to_addr,
                value=float(i % 100),
                gas_price=20000000000,
                gas_used=21000,
                nonce=i % 10,
                tx_type="0x",
                status="success" if i % 10 != 0 else "pending",
                timestamp=datetime.utcnow() - timedelta(hours=i)
            )
            self.transactions[tx.tx_hash] = tx
    
    # --- Admin Methods ---
    
    def add_admin(self, admin_id: str):
        self.admins.add(admin_id)
    
    def is_admin(self, user_id: str) -> bool:
        return user_id in self.admins
    
    def reindex_chain(self, admin_id: str, chain_id: str) -> Dict:
        """Admin: Reindex chain"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        self.admin_actions.append({
            "action": "reindex",
            "chain": chain_id,
            "admin_id": admin_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {"status": "indexed", "chain": chain_id}
    
    def update_block_data(self, admin_id: str, block_data: Dict) -> Dict:
        """Admin: Update block data"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        block = Block(
            block_number=block_data.get("number", 0),
            block_hash=block_data.get("hash", ""),
            parent_hash=block_data.get("parentHash", ""),
            timestamp=datetime.utcnow(),
            tx_count=block_data.get("tx_count", 0),
            miner=block_data.get("miner", ""),
            gas_used=block_data.get("gas_used", 0),
            gas_limit=block_data.get("gas_limit", 30000000),
            difficulty=block_data.get("difficulty", 1),
            size=block_data.get("size", 0)
        )
        
        self.blocks[block.block_number] = block
        
        self.admin_actions.append({
            "action": "update_block",
            "block": block.block_number,
            "admin_id": admin_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {"status": "updated", "block": block.block_number}
    
    def update_tx_status(self, admin_id: str, tx_hash: str, status: str) -> Dict:
        """Admin: Update transaction status"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        if tx_hash in self.transactions:
            self.transactions[tx_hash].status = status
        
        self.admin_actions.append({
            "action": "update_tx_status",
            "tx": tx_hash,
            "status": status,
            "admin_id": admin_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {"status": "updated", "tx": tx_hash, "status": status}
    
    def add_token(self, admin_id: str, token_data: Dict) -> Dict:
        """Admin: Add token"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        token = Token(
            address=token_data.get("address", ""),
            symbol=token_data.get("symbol", ""),
            name=token_data.get("name", ""),
            decimals=token_data.get("decimals", 18),
            total_supply=token_data.get("total_supply", 0),
            holders=token_data.get("holders", 0),
            transfers=token_data.get("transfers", 0)
        )
        
        self.tokens[token.address] = token
        
        self.admin_actions.append({
            "action": "add_token",
            "token": token.symbol,
            "admin_id": admin_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {"status": "added", "token": token.symbol}
    
    def remove_token(self, admin_id: str, address: str) -> Dict:
        """Admin: Remove token"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        if address in self.tokens:
            del self.tokens[address]
        
        self.admin_actions.append({
            "action": "remove_token",
            "address": address,
            "admin_id": admin_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {"status": "removed", "address": address}
    
    def get_all_blocks(self, admin_id: str, limit: int = 50) -> List[Dict]:
        """Admin: Get all blocks"""
        if not self.is_admin(admin_id):
            return []
        
        blocks = sorted(self.blocks.values(), key=lambda b: b.block_number, reverse=True)
        return [b.to_dict() for b in blocks[:limit]]
    
    def get_all_transactions(self, admin_id: str, limit: int = 100) -> List[Dict]:
        """Admin: Get all transactions"""
        if not self.is_admin(admin_id):
            return []
        
        txs = sorted(self.transactions.values(), key=lambda t: t.timestamp, reverse=True)
        return [t.to_dict() for t in txs[:limit]]
    
    def get_all_addresses(self, admin_id: str, limit: int = 50) -> List[Dict]:
        """Admin: Get all addresses"""
        if not self.is_admin(admin_id):
            return []
        
        return [a.to_dict() for a in list(self.addresses.values())[:limit]]
    
    def get_all_tokens(self, admin_id: str) -> List[Dict]:
        """Admin: Get all tokens"""
        if not self.is_admin(admin_id):
            return []
        
        return [t.to_dict() for t in self.tokens.values()]
    
    def get_admin_actions(self, admin_id: str, limit: int = 50) -> List[Dict]:
        """Admin: Get admin actions"""
        if not self.is_admin(admin_id):
            return []
        
        return sorted(self.admin_actions, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def get_search_stats(self, admin_id: str) -> Dict:
        """Admin: Get search statistics"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        return {
            "total_blocks": len(self.blocks),
            "total_transactions": len(self.transactions),
            "total_addresses": len(self.addresses),
            "total_tokens": len(self.tokens),
            "total_contracts": len(self.contracts),
            "pending_txs": sum(1 for t in self.transactions.values() if t.status == "pending"),
        }
    
    def get_explorer_stats(self, admin_id: str) -> Dict:
        """Admin: Get explorer statistics"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        return {
            "supported_chains": len(EXPLORERS),
            "blocks_indexed": len(self.blocks),
            "transactions_indexed": len(self.transactions),
            "addresses_indexed": len(self.addresses),
            "tokens_tracked": len(self.tokens),
        }
    
    # --- User Methods ---
    
    def get_block(self, block_number: int) -> Dict:
        """User: Get block"""
        if block_number in self.blocks:
            return self.blocks[block_number].to_dict()
        return {"error": "Block not found"}
    
    def get_block_by_hash(self, block_hash: str) -> Dict:
        """User: Get block by hash"""
        for block in self.blocks.values():
            if block.block_hash == block_hash:
                return block.to_dict()
        return {"error": "Block not found"}
    
    def get_transaction(self, tx_hash: str) -> Dict:
        """User: Get transaction"""
        if tx_hash in self.transactions:
            return self.transactions[tx_hash].to_dict()
        return {"error": "Transaction not found"}
    
    def get_address(self, address: str) -> Dict:
        """User: Get address details"""
        if address in self.addresses:
            return self.addresses[address].to_dict()
        return {"error": "Address not found"}
    
    def get_address_txs(self, address: str, limit: int = 50) -> List[Dict]:
        """User: Get address transactions"""
        txs = [t.to_dict() for t in self.transactions.values() 
              if t.from_addr == address or t.to_addr == address]
        return sorted(txs, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def get_token(self, address: str) -> Dict:
        """User: Get token"""
        if address in self.tokens:
            return self.tokens[address].to_dict()
        return {"error": "Token not found"}
    
    def get_token_holders(self, address: str) -> List[Dict]:
        """User: Get token holders"""
        # Simplified - return from addresses
        return [{"address": a, "balance": self.addresses[a].balance} 
                for a in list(self.addresses.keys())[:10]]
    
    def get_token_transfers(self, address: str, limit: int = 50) -> List[Dict]:
        """User: Get token transfers"""
        return list(self.token_transfers.values())[:limit]
    
    def search(self, query: str) -> Dict:
        """User: Search"""
        # Check if block number
        try:
            num = int(query)
            if num in self.blocks:
                return {"type": "block", "data": self.blocks[num].to_dict()}
        except:
            pass
        
        # Check if address
        if query.startswith("0x") and len(query) == 42:
            if query in self.addresses:
                return {"type": "address", "data": self.addresses[query].to_dict()}
            if query in self.tokens:
                return {"type": "token", "data": self.tokens[query].to_dict()}
        
        # Check if tx hash
        if query.startswith("0x") and len(query) == 66:
            if query in self.transactions:
                return {"type": "transaction", "data": self.transactions[query].to_dict()}
        
        return {"error": "Not found"}
    
    def get_latest_blocks(self, limit: int = 10) -> List[Dict]:
        """User: Get latest blocks"""
        blocks = sorted(self.blocks.values(), key=lambda b: b.block_number, reverse=True)
        return [b.to_dict() for b in blocks[:limit]]
    
    def get_latest_transactions(self, limit: int = 10) -> List[Dict]:
        """User: Get latest transactions"""
        txs = sorted(self.transactions.values(), key=lambda t: t.timestamp, reverse=True)
        return [t.to_dict() for t in txs[:limit]]
    
    def get_chain_info(self, chain_id: str) -> Dict:
        """User: Get chain info"""
        if chain_id in EXPLORERS:
            return EXPLORERS[chain_id]
        return {"error": "Chain not found"}
    
    def get_supported_chains(self) -> List[Dict]:
        return [{"id": k, "name": v["name"], "type": v["type"], "symbol": v["symbol"]} for k, v in EXPLORERS.items()]
    
    def get_gas_oracle(self, chain_id: str = "tigerex") -> Dict:
        """User: Get gas prices"""
        return {
            "chain": chain_id,
            "slow": 10000000000,
            "average": 20000000000,
            "fast": 50000000000,
            "last_update": datetime.utcnow().isoformat()
        }


# ============================================================
# FLASK APPS
# ============================================================
from flask import Flask, jsonify, request
from flask_cors import CORS

admin_app = Flask(__name__)
CORS(admin_app)

explorer_service = ExplorerService()
explorer_service.add_admin("admin001")

#
# Admin Routes
#
@admin_app.route('/explorer/admin/health')
def admin_health():
    return jsonify({"status": "ok", "service": "explorer", "role": "admin"})

@admin_app.route('/explorer/admin/reindex', methods=['POST'])
def admin_reindex():
    data = request.get_json() or {}
    return jsonify(explorer_service.reindex_chain(
        data.get('admin_id', ''),
        data.get('chain', 'tigerex')
    ))

@admin_app.route('/explorer/admin/update-block', methods=['POST'])
def admin_update_block():
    data = request.get_json() or {}
    return jsonify(explorer_service.update_block_data(
        data.get('admin_id', ''),
        data.get('block_data', {})
    ))

@admin_app.route('/explorer/admin/update-tx', methods=['POST'])
def admin_update_tx():
    data = request.get_json() or {}
    return jsonify(explorer_service.update_tx_status(
        data.get('admin_id', ''),
        data.get('tx_hash', ''),
        data.get('status', '')
    ))

@admin_app.route('/explorer/admin/add-token', methods=['POST'])
def admin_add_token():
    data = request.get_json() or {}
    return jsonify(explorer_service.add_token(
        data.get('admin_id', ''),
        data.get('token_data', {})
    ))

@admin_app.route('/explorer/admin/remove-token', methods=['POST'])
def admin_remove_token():
    data = request.get_json() or {}
    return jsonify(explorer_service.remove_token(
        data.get('admin_id', ''),
        data.get('address', '')
    ))

@admin_app.route('/explorer/admin/all-blocks')
def admin_blocks():
    admin_id = request.args.get('admin_id', '')
    limit = request.args.get('limit', 50, type=int)
    return jsonify(explorer_service.get_all_blocks(admin_id, limit))

@admin_app.route('/explorer/admin/all-transactions')
def admin_txs():
    admin_id = request.args.get('admin_id', '')
    limit = request.args.get('limit', 100, type=int)
    return jsonify(explorer_service.get_all_transactions(admin_id, limit))

@admin_app.route('/explorer/admin/all-addresses')
def admin_addresses():
    admin_id = request.args.get('admin_id', '')
    limit = request.args.get('limit', 50, type=int)
    return jsonify(explorer_service.get_all_addresses(admin_id, limit))

@admin_app.route('/explorer/admin/all-tokens')
def admin_tokens():
    admin_id = request.args.get('admin_id', '')
    return jsonify(explorer_service.get_all_tokens(admin_id))

@admin_app.route('/explorer/admin/actions')
def admin_actions():
    admin_id = request.args.get('admin_id', '')
    return jsonify(explorer_service.get_admin_actions(admin_id))

@admin_app.route('/explorer/admin/search-stats')
def admin_search_stats():
    admin_id = request.args.get('admin_id', '')
    return jsonify(explorer_service.get_search_stats(admin_id))

@admin_app.route('/explorer/admin/stats')
def admin_stats():
    admin_id = request.args.get('admin_id', '')
    return jsonify(explorer_service.get_explorer_stats(admin_id))

@admin_app.route('/explorer/admin/chains')
def admin_chains():
    return jsonify(explorer_service.get_supported_chains())


def run_admin():
    port = int(os.environ.get('PORT', 6300))
    logger.info(f"Starting Admin Block Explorer Service on port {port}")
    admin_app.run(host='0.0.0.0', port=port, threaded=True)


if __name__ == '__main__':
    run_admin()