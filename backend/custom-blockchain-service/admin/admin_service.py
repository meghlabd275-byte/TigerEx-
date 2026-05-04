#!/usr/bin/env python3
"""
TigerEx Custom Blockchain Service - Admin Interface
Supports EVM and Non-EVM chains with full node and mining capabilities
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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# BLOCKCHAIN NETWORK CONFIGURATION
# ============================================================
SUPPORTED_CHAINS = {
    "tigerex": {
        "name": "TigerExChain",
        "type": "evm",
        "chain_id": 9999,
        "symbol": "TIG",
        "rpc": "http://localhost:6200",
        "explorer": "http://localhost:6300",
        "decimals": 18,
        "block_time": 2,
        "max_gas": 30000000,
    },
    "ethereum": {"name": "Ethereum", "type": "evm", "chain_id": 1, "symbol": "ETH", "rpc": "https://eth.llamarpc.com", "decimals": 18},
    "bsc": {"name": "BNB Chain", "type": "evm", "chain_id": 56, "symbol": "BNB", "rpc": "https://bsc.llamarpc.com", "decimals": 18},
    "polygon": {"name": "Polygon", "type": "evm", "chain_id": 137, "symbol": "MATIC", "rpc": "https://polygon.llamarpc.com", "decimals": 18},
    "arbitrum": {"name": "Arbitrum", "type": "evm", "chain_id": 42161, "symbol": "ETH", "rpc": "https://arb1.llamarpc.com", "decimals": 18},
    "avalanche": {"name": "Avalanche", "type": "evm", "chain_id": 43114, "symbol": "AVAX", "rpc": "https://avalanche.llamarpc.com", "decimals": 18},
    "solana": {"name": "Solana", "type": "non_evm", "symbol": "SOL", "rpc": "https://api.mainnet-beta.solana.com"},
    "ton": {"name": "TON", "type": "non_evm", "symbol": "TON", "rpc": "https://toncenter.com/api/v2"},
    "near": {"name": "NEAR", "type": "non_evm", "symbol": "NEAR", "rpc": "https://rpc.mainnet.near.org"},
    "aptos": {"name": "Aptos", "type": "non_evm", "symbol": "APT", "rpc": "https://fullnode.mainnet.aptoslabs.com"},
    "sui": {"name": "Sui", "type": "non_evm", "symbol": "SUI", "rpc": "https://fullnode.mainnet.sui.io"},
    "cosmos": {"name": "Cosmos", "type": "non_evm", "symbol": "ATOM", "rpc": "https://rpc.cosmos.network"},
}

# ============================================================
# DATA MODELS
# ============================================================
@dataclass
class Block:
    block_number: int
    block_hash: str
    parent_hash: str
    transactions: List[str]
    timestamp: datetime
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
            "transactions": self.transactions,
            "timestamp": self.timestamp.isoformat(),
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
    gas_limit: int
    nonce: int
    data: str
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        return {
            "hash": self.tx_hash,
            "blockNumber": self.block_number,
            "from": self.from_addr,
            "to": self.to_addr,
            "value": self.value,
            "gasPrice": self.gas_price,
            "gasLimit": self.gas_limit,
            "nonce": self.nonce,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
        }

@dataclass
class Account:
    address: str
    balance: float
    nonce: int
    code: str = ""
    storage: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "address": self.address,
            "balance": self.balance,
            "nonce": self.nonce,
            "code": self.code,
            "storage": self.storage,
        }

@dataclass
class Validator:
    address: str
    stake: float
    delegators: int
    uptime: float
    blocks_forged: int
    slash_count: int
    
    def to_dict(self) -> Dict:
        return {
            "address": self.address,
            "stake": self.stake,
            "delegators": self.delegators,
            "uptime": self.uptime,
            "blocksForged": self.blocks_forged,
            "slashes": self.slash_count,
        }

@dataclass
class ChainStats:
    chain_id: str
    block_height: int
    total_tx: int
    total_accounts: int
    validators: int
    tps: float
    gas_price: int
    last_update: datetime
    
    def to_dict(self) -> Dict:
        return {
            "chain": self.chain_id,
            "height": self.block_height,
            "totalTransactions": self.total_tx,
            "totalAccounts": self.total_accounts,
            "validators": self.validators,
            "tps": self.tps,
            "gasPrice": self.gas_price,
            "lastUpdate": self.last_update.isoformat(),
        }

# ============================================================
# BLOCKCHAIN ENGINE
# ============================================================
class BlockchainService:
    """Full blockchain engine"""
    
    def __init__(self):
        self.genesis_block = None
        self.blocks = {}
        self.transactions = {}
        self.accounts = {}
        self.pending_txs = []
        self.validators = {}
        self.chain_stats = {}
        self.admin_actions = []
        self.admins = set()
        
        # Initialize TigerEx chain
        self._init_tigerex_chain()
        
        # Start block production
        self._start_block_production()
        
        logger.info("Custom Blockchain Service initialized")
    
    def _init_tigerex_chain(self):
        """Initialize TigerEx native chain"""
        chain_id = "tigerex"
        
        # Genesis block
        genesis = Block(
            block_number=0,
            block_hash="0x" + "0" * 64,
            parent_hash="0x" + "0" * 64,
            transactions=[],
            timestamp=datetime.utcnow(),
            miner="0x0000000000000000000000000000000000000000",
            gas_used=0,
            gas_limit=30000000,
            difficulty=1,
            size=0
        )
        self.blocks[0] = genesis
        
        # Create validator (founder)
        founder = "0x" + "1" * 40
        self.accounts[founder] = Account(founder, 1000000, 0)
        
        self.validators[founder] = Validator(
            address=founder,
            stake=1000000,
            delegators=0,
            uptime=100.0,
            blocks_forged=0,
            slash_count=0
        )
        
        self.chain_stats[chain_id] = ChainStats(
            chain_id=chain_id,
            block_height=0,
            total_tx=0,
            total_accounts=1,
            validators=1,
            tps=0,
            gas_price=20000000000,
            last_update=datetime.utcnow()
        )
    
    def _start_block_production(self):
        def produce():
            while True:
                time.sleep(2)  # Block time
                self._produce_block()
        
        threading.Thread(target=produce, daemon=True).start()
    
    def _produce_block(self):
        """Produce new block"""
        chain_id = "tigerex"
        last_block = self.blocks[max(self.blocks.keys())]
        new_number = last_block.block_number + 1
        
        # Select transactions
        txs = self.pending_txs[:100]
        self.pending_txs = self.pending_txs[100:]
        
        tx_hashes = [tx["hash"] for tx in txs]
        
        # Create new block
        block = Block(
            block_number=new_number,
            block_hash=hashlib.sha256(f"{new_number}{time.time()}".encode()).hexdigest(),
            parent_hash=last_block.block_hash,
            transactions=tx_hashes,
            timestamp=datetime.utcnow(),
            miner=founder if hasattr(self, 'founder') else "0x0",
            gas_used=len(txs) * 21000,
            gas_limit=30000000,
            difficulty=1,
            size=len(json.dumps(txs))
        )
        
        self.blocks[new_number] = block
        
        # Update stats
        if chain_id in self.chain_stats:
            stats = self.chain_stats[chain_id]
            stats.block_height = new_number
            stats.total_tx += len(txs)
            stats.last_update = datetime.utcnow()
        
        logger.debug(f"Block {new_number} produced with {len(txs)} transactions")
    
    # --- Admin Methods ---
    
    def add_admin(self, admin_id: str):
        self.admins.add(admin_id)
    
    def is_admin(self, user_id: str) -> bool:
        return user_id in self.admins
    
    def create_chain(self, admin_id: str, chain_id: str, chain_type: str, config: Dict) -> Dict:
        """Admin: Create new chain"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        if chain_id in SUPPORTED_CHAINS:
            return {"error": "Chain already exists"}
        
        SUPPORTED_CHAINS[chain_id] = {
            "name": config.get("name", chain_id),
            "type": chain_type,
            "chain_id": config.get("chain_id", 0),
            "symbol": config.get("symbol", "UNKNOWN"),
            "rpc": config.get("rpc", ""),
            "decimals": config.get("decimals", 18),
        }
        
        self.admin_actions.append({
            "action": "create_chain",
            "chain_id": chain_id,
            "admin_id": admin_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {"status": "created", "chain_id": chain_id}
    
    def add_validator(self, admin_id: str, address: str, stake: float) -> Dict:
        """Admin: Add validator"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        self.validators[address] = Validator(
            address=address,
            stake=stake,
            delegators=0,
            uptime=100.0,
            blocks_forged=0,
            slash_count=0
        )
        
        self.admin_actions.append({
            "action": "add_validator",
            "address": address,
            "stake": stake,
            "admin_id": admin_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {"status": "added", "validator": address}
    
    def remove_validator(self, admin_id: str, address: str) -> Dict:
        """Admin: Remove validator"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        if address in self.validators:
            del self.validators[address]
        
        self.admin_actions.append({
            "action": "remove_validator",
            "address": address,
            "admin_id": admin_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {"status": "removed", "validator": address}
    
    def adjust_gas_price(self, admin_id: str, gas_price: int) -> Dict:
        """Admin: Adjust gas price"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        chain_id = "tigerex"
        if chain_id in self.chain_stats:
            self.chain_stats[chain_id].gas_price = gas_price
        
        self.admin_actions.append({
            "action": "adjust_gas_price",
            "gas_price": gas_price,
            "admin_id": admin_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {"status": "adjusted", "gas_price": gas_price}
    
    def fund_account(self, admin_id: str, address: str, amount: float) -> Dict:
        """Admin: Fund account"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        if address not in self.accounts:
            self.accounts[address] = Account(address, amount, 0)
        else:
            self.accounts[address].balance += amount
        
        self.admin_actions.append({
            "action": "fund_account",
            "address": address,
            "amount": amount,
            "admin_id": admin_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {"status": "funded", "address": address, "balance": self.accounts[address].balance}
    
    def get_all_blocks(self, admin_id: str, limit: int = 100) -> List[Dict]:
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
    
    def get_all_accounts(self, admin_id: str) -> List[Dict]:
        """Admin: Get all accounts"""
        if not self.is_admin(admin_id):
            return []
        
        return [acc.to_dict() for acc in self.accounts.values()]
    
    def get_validators(self, admin_id: str) -> List[Dict]:
        """Admin: Get validators"""
        if not self.is_admin(admin_id):
            return []
        
        return [v.to_dict() for v in self.validators.values()]
    
    def get_admin_actions(self, admin_id: str, limit: int = 50) -> List[Dict]:
        """Admin: Get admin actions"""
        if not self.is_admin(admin_id):
            return []
        
        return sorted(self.admin_actions, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def get_chain_stats(self, admin_id: str, chain_id: str = "tigerex") -> Dict:
        """Admin: Get chain statistics"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        if chain_id in self.chain_stats:
            return self.chain_stats[chain_id].to_dict()
        return {"error": "Chain not found"}
    
    def get_pending_txs(self, admin_id: str) -> List[Dict]:
        """Admin: Get pending transactions"""
        if not self.is_admin(admin_id):
            return []
        
        return self.pending_txs
    
    def get_system_status(self, admin_id: str) -> Dict:
        """Admin: Get system status"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        chain_id = "tigerex"
        stats = self.chain_stats.get(chain_id)
        
        return {
            "status": "running",
            "chain": chain_id,
            "block_height": stats.block_height if stats else 0,
            "total_transactions": stats.total_tx if stats else 0,
            "total_accounts": len(self.accounts),
            "validators": len(self.validators),
            "pending_txs": len(self.pending_txs),
            "supported_chains": len(SUPPORTED_CHAINS),
        }
    
    # --- User Methods ---
    
    def create_account(self, user_id: str) -> Dict:
        """User: Create account"""
        address = "0x" + hashlib.sha256(f"{user_id}{time.time()}".encode()).hexdigest()[-40:]
        
        self.accounts[address] = Account(address, 0, 0)
        
        return {"address": address, "balance": 0, "nonce": 0}
    
    def get_balance(self, address: str) -> Dict:
        """User: Get account balance"""
        if address in self.accounts:
            acc = self.accounts[address]
            return {"address": address, "balance": acc.balance, "nonce": acc.nonce}
        return {"address": address, "balance": 0, "nonce": 0}
    
    def send_transaction(self, from_addr: str, to_addr: str, value: float, gas_price: int = 0) -> Dict:
        """User: Send transaction"""
        if from_addr not in self.accounts:
            return {"error": "Sender account not found"}
        
        sender = self.accounts[from_addr]
        
        if sender.balance < value:
            return {"error": "Insufficient balance"}
        
        gas_price = gas_price or self.chain_stats.get("tigerex", ChainStats("",0,0,0,0,0,0,datetime.utcnow())).gas_price
        
        sender.balance -= value
        sender.nonce += 1
        
        if to_addr not in self.accounts:
            self.accounts[to_addr] = Account(to_addr, 0, 0)
        self.accounts[to_addr].balance += value
        
        tx_hash = f"0x{uuid.uuid4().hex[:64]}"
        tx = Transaction(
            tx_hash=tx_hash,
            block_number=-1,
            from_addr=from_addr,
            to_addr=to_addr,
            value=value,
            gas_price=gas_price,
            gas_limit=21000,
            nonce=sender.nonce,
            data="",
            timestamp=datetime.utcnow()
        )
        
        self.transactions[tx_hash] = tx
        self.pending_txs.append(tx.to_dict())
        
        return {"tx_hash": tx_hash, "status": "pending"}
    
    def get_transaction(self, tx_hash: str) -> Dict:
        """User: Get transaction"""
        if tx_hash in self.transactions:
            return self.transactions[tx_hash].to_dict()
        
        for tx in self.pending_txs:
            if tx["hash"] == tx_hash:
                return tx
        
        return {"error": "Transaction not found"}
    
    def get_block(self, block_number: int) -> Dict:
        """User: Get block"""
        if block_number in self.blocks:
            return self.blocks[block_number].to_dict()
        return {"error": "Block not found"}
    
    def get_latest_block(self) -> Dict:
        """User: Get latest block"""
        latest = max(self.blocks.keys())
        return self.blocks[latest].to_dict()
    
    def get_chain_config(self, chain_id: str) -> Dict:
        """User: Get chain configuration"""
        if chain_id in SUPPORTED_CHAINS:
            return SUPPORTED_CHAINS[chain_id]
        return {"error": "Chain not found"}
    
    def get_supported_chains(self) -> List[Dict]:
        return [{"id": k, "name": v["name"], "type": v["type"], "symbol": v["symbol"]} for k, v in SUPPORTED_CHAINS.items()]
    
    def deploy_contract(self, from_addr: str, bytecode: str) -> Dict:
        """User: Deploy contract"""
        if from_addr not in self.accounts:
            return {"error": "Account not found"}
        
        sender = self.accounts[from_addr]
        
        contract_addr = "0x" + hashlib.sha256(f"{bytecode}{time.time()}".encode()).hexdigest()[-40:]
        
        self.accounts[contract_addr] = Account(contract_addr, 0, 0, code=bytecode)
        
        tx_hash = f"0x{uuid.uuid4().hex[:64]}"
        
        return {"tx_hash": tx_hash, "contract_address": contract_addr, "status": "deployed"}
    
    def call_contract(self, from_addr: str, contract_addr: str, method: str, params: List) -> Dict:
        """User: Call contract"""
        if from_addr not in self.accounts:
            return {"error": "Account not found"}
        
        if contract_addr not in self.accounts:
            return {"error": "Contract not found"}
        
        contract = self.accounts[contract_addr]
        
        return {"result": f"Called {method} on {contract_addr}", "status": "success"}


# ============================================================
# FLASK APPS
# ============================================================
from flask import Flask, jsonify, request
from flask_cors import CORS

admin_app = Flask(__name__)
CORS(admin_app)

blockchain_service = BlockchainService()
blockchain_service.add_admin("admin001")

#
# Admin Routes
#
@admin_app.route('/blockchain/admin/health')
def admin_health():
    return jsonify({"status": "ok", "service": "blockchain", "role": "admin"})

@admin_app.route('/blockchain/admin/create-chain', methods=['POST'])
def admin_create_chain():
    data = request.get_json() or {}
    return jsonify(blockchain_service.create_chain(
        data.get('admin_id', ''),
        data.get('chain_id', ''),
        data.get('type', 'evm'),
        data.get('config', {})
    ))

@admin_app.route('/blockchain/admin/add-validator', methods=['POST'])
def admin_add_validator():
    data = request.get_json() or {}
    return jsonify(blockchain_service.add_validator(
        data.get('admin_id', ''),
        data.get('address', ''),
        data.get('stake', 0)
    ))

@admin_app.route('/blockchain/admin/remove-validator', methods=['POST'])
def admin_remove_validator():
    data = request.get_json() or {}
    return jsonify(blockchain_service.remove_validator(
        data.get('admin_id', ''),
        data.get('address', '')
    ))

@admin_app.route('/blockchain/admin/adjust-gas', methods=['POST'])
def admin_adjust_gas():
    data = request.get_json() or {}
    return jsonify(blockchain_service.adjust_gas_price(
        data.get('admin_id', ''),
        data.get('gas_price', 0)
    ))

@admin_app.route('/blockchain/admin/fund-account', methods=['POST'])
def admin_fund_account():
    data = request.get_json() or {}
    return jsonify(blockchain_service.fund_account(
        data.get('admin_id', ''),
        data.get('address', ''),
        data.get('amount', 0)
    ))

@admin_app.route('/blockchain/admin/all-blocks')
def admin_blocks():
    admin_id = request.args.get('admin_id', '')
    limit = request.args.get('limit', 100, type=int)
    return jsonify(blockchain_service.get_all_blocks(admin_id, limit))

@admin_app.route('/blockchain/admin/all-transactions')
def admin_txs():
    admin_id = request.args.get('admin_id', '')
    limit = request.args.get('limit', 100, type=int)
    return jsonify(blockchain_service.get_all_transactions(admin_id, limit))

@admin_app.route('/blockchain/admin/all-accounts')
def admin_accounts():
    admin_id = request.args.get('admin_id', '')
    return jsonify(blockchain_service.get_all_accounts(admin_id))

@admin_app.route('/blockchain/admin/validators')
def admin_validators():
    admin_id = request.args.get('admin_id', '')
    return jsonify(blockchain_service.get_validators(admin_id))

@admin_app.route('/blockchain/admin/actions')
def admin_actions():
    admin_id = request.args.get('admin_id', '')
    return jsonify(blockchain_service.get_admin_actions(admin_id))

@admin_app.route('/blockchain/admin/stats')
def admin_stats():
    admin_id = request.args.get('admin_id', '')
    chain_id = request.args.get('chain', 'tigerex')
    return jsonify(blockchain_service.get_chain_stats(admin_id, chain_id))

@admin_app.route('/blockchain/admin/pending')
def admin_pending():
    admin_id = request.args.get('admin_id', '')
    return jsonify(blockchain_service.get_pending_txs(admin_id))

@admin_app.route('/blockchain/admin/status')
def admin_status():
    admin_id = request.args.get('admin_id', '')
    return jsonify(blockchain_service.get_system_status(admin_id))

@admin_app.route('/blockchain/admin/chains')
def admin_chains():
    return jsonify(blockchain_service.get_supported_chains())


def run_admin():
    port = int(os.environ.get('PORT', 6200))
    logger.info(f"Starting Admin Blockchain Service on port {port}")
    admin_app.run(host='0.0.0.0', port=port, threaded=True)


if __name__ == '__main__':
    run_admin()