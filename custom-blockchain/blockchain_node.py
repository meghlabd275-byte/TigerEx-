#!/usr/bin/env python3
"""
TigerEx Custom Blockchain Node
Supports both EVM-compatible and custom non-EVM chains
"""
import os
import json
import hashlib
import time
import logging
import threading
import uuid
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
from decimal import Decimal

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Genesis configurations for custom chains
CHAIN_CONFIGS = {
    "tigerex-evm": {
        "name": "TigerEx EVM Chain",
        "type": "evm",
        "chain_id": 9999,
        "symbol": "TIG",
        "decimals": 18,
        "gas_limit": 30000000,
        "block_time": 2,
        "consensus": "proof_of_authority",
        "genesis": "0x0000000000000000000000000000000000000000000000000000000000000000"
    },
    "tigerex-native": {
        "name": "TigerEx Native Chain",
        "type": "native",
        "chain_id": 10000,
        "symbol": "TXN",
        "decimals": 8,
        "max_supply": 1000000000,
        "block_time": 1,
        "consensus": "proof_of_stake",
        "min_stake": 1000
    },
    "tigerex-hybrid": {
        "name": "TigerEx Hybrid Chain",
        "type": "hybrid",
        "chain_id": 10001,
        "symbol": "THY",
        "decimals": 18,
        "gas_limit": 50000000,
        "block_time": 2,
        "consensus": "proof_of_authority",
        "evm_compatible": True
    }
}

@dataclass
class Block:
    """Block structure for custom chain"""
    number: int
    hash: str
    parent_hash: str
    timestamp: int
    validator: str
    transactions: List[Dict]
    state_root: str
    receipts_root: str
    gas_used: int
    gas_limit: int
    difficulty: int
    extra_data: str
    
    def to_dict(self) -> Dict:
        return {
            "number": self.number,
            "hash": self.hash,
            "parentHash": self.parent_hash,
            "timestamp": self.timestamp,
            "validator": self.validator,
            "transactions": self.transactions,
            "stateRoot": self.state_root,
            "receiptsRoot": self.receipts_root,
            "gasUsed": self.gas_used,
            "gasLimit": self.gas_limit,
            "difficulty": self.difficulty,
            "extraData": self.extra_data
        }

@dataclass
class Transaction:
    """Transaction structure"""
    hash: str
    block_number: int
    from_address: str
    to_address: str
    value: int
    gas_price: int
    gas_limit: int
    data: str
    nonce: int
    v: int
    r: str
    s: str
    status: str
    
    def to_dict(self) -> Dict:
        return {
            "hash": self.hash,
            "blockNumber": self.block_number,
            "from": self.from_address,
            "to": self.to_address,
            "value": self.value,
            "gasPrice": self.gas_price,
            "gasLimit": self.gas_limit,
            "data": self.data,
            "nonce": self.nonce,
            "v": self.v,
            "r": self.r,
            "s": self.s,
            "status": self.status
        }

@dataclass
class Account:
    """Account state"""
    address: str
    balance: int
    nonce: int
    code_hash: str
    storage_root: str
    is_contract: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "address": self.address,
            "balance": self.balance,
            "nonce": self.nonce,
            "codeHash": self.code_hash,
            "storageRoot": self.storage_root,
            "isContract": self.is_contract
        }


class CustomBlockchain:
    """Custom blockchain implementation"""
    
    def __init__(self, chain_type: str = "tigerex-evm"):
        self.chain_type = chain_type
        self.config = CHAIN_CONFIGS.get(chain_type, CHAIN_CONFIGS["tigerex-evm"])
        
        # Chain state
        self.blocks = {}  # number -> Block
        self.transactions = {}  # hash -> Transaction
        self.accounts = {}  # address -> Account
        self.pending_txs = []
        self.validators = set()
        self.stakers = {}  # address -> stake amount
        
        # State
        self.current_block = 0
        self.state_root = hashlib.sha256(b"state").hexdigest()
        
        # Initialize genesis block
        self._initialize_genesis()
        
        # Start block production
        self._start_block_producer()
        
        logger.info(f"Custom blockchain initialized: {chain_type}")
    
    def _initialize_genesis(self):
        """Create genesis block"""
        genesis_hash = hashlib.sha256(b"genesis").hexdigest()
        
        genesis_block = Block(
            number=0,
            hash=genesis_hash,
            parent_hash="0x" + "0" * 64,
            timestamp=int(time.time()),
            validator="0x0000000000000000000000000000000000000000",
            transactions=[],
            state_root=self.state_root,
            receipts_root=hashlib.sha256(b"receipts").hexdigest(),
            gas_used=0,
            gas_limit=self.config.get("gas_limit", 30000000),
            difficulty=1,
            extra_data="TigerEx Genesis Block"
        )
        
        self.blocks[0] = genesis_block
        
        # Initialize validator accounts
        self.validators.add("0x" + "0" * 40)
        
        # Create system accounts
        self._create_system_accounts()
    
    def _create_system_accounts(self):
        """Create system accounts"""
        # Foundation account
        foundation = Account(
            address="0x" + "1" * 40,
            balance=1000000 * (10 ** self.config["decimals"]),
            nonce=0,
            code_hash=hashlib.sha256(b"").hexdigest(),
            storage_root="0x" + "0" * 64
        )
        self.accounts[foundation.address] = foundation
        
        # Rewards account
        rewards = Account(
            address="0x" + "2" * 40,
            balance=10000000 * (10 ** self.config["decimals"]),
            nonce=0,
            code_hash=hashlib.sha256(b"").hexdigest(),
            storage_root="0x" + "0" * 64
        )
        self.accounts[rewards.address] = rewards
    
    def _start_block_producer(self):
        """Start block production"""
        def producer():
            while True:
                time.sleep(self.config.get("block_time", 2))
                self._produce_block()
        
        thread = threading.Thread(target=producer, daemon=True)
        thread.start()
    
    def _produce_block(self):
        """Produce a new block"""
        parent = self.blocks[self.current_block]
        
        # Select transactions
        txs = self.pending_txs[:100]  # Max 100 txs per block
        total_gas = sum(tx.get("gas_limit", 21000) for tx in txs)
        
        # Create block
        block_number = self.current_block + 1
        block_hash = hashlib.sha256(
            f"{parent.hash}{block_number}{int(time.time())}".encode()
        ).hexdigest()
        
        block = Block(
            number=block_number,
            hash=block_hash,
            parent_hash=parent.hash,
            timestamp=int(time.time()),
            validator=list(self.validators)[0] if self.validators else "0x" + "0" * 40,
            transactions=txs,
            state_root=self.state_root,
            receipts_root=hashlib.sha256(json.dumps(txs).encode()).hexdigest(),
            gas_used=total_gas,
            gas_limit=self.config.get("gas_limit", 30000000),
            difficulty=1,
            extra_data=f"TigerEx Block #{block_number}"
        )
        
        self.blocks[block_number] = block
        self.current_block = block_number
        
        # Clear pending transactions
        self.pending_txs = self.pending_txs[100:]
        
        logger.debug(f"Block produced: #{block_number}")
    
    def create_account(self, private_key: str = "") -> Dict:
        """Create new account"""
        if private_key:
            addr_hash = hashlib.sha256(private_key.encode()).hexdigest()[-40:]
        else:
            addr_hash = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[-40:]
        
        address = "0x" + addr_hash
        
        account = Account(
            address=address,
            balance=0,
            nonce=0,
            code_hash=hashlib.sha256(b"").hexdigest(),
            storage_root="0x" + "0" * 64
        )
        
        self.accounts[address] = account
        
        return {
            "address": address,
            "private_key": private_key or hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest(),
            "balance": 0
        }
    
    def get_balance(self, address: str) -> int:
        """Get account balance"""
        account = self.accounts.get(address.lower())
        if account:
            return account.balance
        return 0
    
    def get_nonce(self, address: str) -> int:
        """Get account nonce"""
        account = self.accounts.get(address.lower())
        if account:
            return account.nonce
        return 0
    
    def send_transaction(self, from_addr: str, to_addr: str, value: int, 
                      gas_price: int = 20000000000, data: str = "") -> Dict:
        """Send transaction"""
        from_addr = from_addr.lower()
        to_addr = to_addr.lower()
        
        # Check balance
        sender = self.accounts.get(from_addr)
        if not sender:
            return {"error": "Sender not found"}
        
        gas_limit = 21000
        gas_cost = gas_limit * gas_price
        
        if sender.balance < value + gas_cost:
            return {"error": "Insufficient balance"}
        
        # Update balances
        sender.balance -= (value + gas_cost)
        
        receiver = self.accounts.get(to_addr)
        if not receiver:
            receiver = Account(
                address=to_addr,
                balance=0,
                nonce=0,
                code_hash=hashlib.sha256(b"").hexdigest(),
                storage_root="0x" + "0" * 64
            )
            self.accounts[to_addr] = receiver
        
        receiver.balance += value
        sender.nonce += 1
        
        # Create transaction
        tx_hash = hashlib.ssha256(
            f"{from_addr}{to_addr}{value}{sender.nonce}".encode()
        ).hexdigest()
        
        tx = Transaction(
            hash=tx_hash,
            block_number=-1,  # Pending
            from_address=from_addr,
            to_address=to_addr,
            value=value,
            gas_price=gas_price,
            gas_limit=gas_limit,
            data=data,
            nonce=sender.nonce,
            v=0,
            r="",
            s="",
            status="pending"
        )
        
        self.transactions[tx_hash] = tx
        self.pending_txs.append(tx.to_dict())
        
        return tx.to_dict()
    
    def deploy_contract(self, sender: str, code: str) -> Dict:
        """Deploy smart contract"""
        sender = sender.lower()
        
        sender_acc = self.accounts.get(sender)
        if not sender_acc:
            return {"error": "Sender not found"}
        
        gas_limit = len(code) * 200  # Estimate
        gas_cost = gas_limit * 20000000000
        
        if sender_acc.balance < gas_cost:
            return {"error": "Insufficient balance for deployment"}
        
        sender_acc.balance -= gas_cost
        sender_acc.nonce += 1
        
        # Contract address
        contract_addr = "0x" + hashlib.sha256(
            f"{sender}{sender_acc.nonce}".encode()
        ).hexdigest()[-40:]
        
        # Create account for contract
        contract = Account(
            address=contract_addr,
            balance=0,
            nonce=0,
            code_hash=hashlib.sha256(code.encode()).hexdigest(),
            storage_root="0x" + "0" * 64,
            is_contract=True
        )
        
        self.accounts[contract_addr] = contract
        
        # Create deployment transaction
        tx_hash = hashlib.sha256(
            f"{sender}{contract_addr}{len(code)}".encode()
        ).hexdigest()
        
        tx = Transaction(
            hash=tx_hash,
            block_number=-1,
            from_address=sender,
            to_address="",
            value=0,
            gas_price=20000000000,
            gas_limit=gas_limit,
            data=code,
            nonce=sender_acc.nonce,
            v=0,
            r="",
            s="",
            status="pending"
        )
        
        self.transactions[tx_hash] = tx
        self.pending_txs.append(tx.to_dict())
        
        return {
            "contract_address": contract_addr,
            "transaction_hash": tx_hash
        }
    
    def call_contract(self, contract_addr: str, data: str) -> Dict:
        """Call contract (read-only)"""
        contract = self.accounts.get(contract_addr.lower())
        
        if not contract or not contract.is_contract:
            return {"error": "Contract not found"}
        
        # Execute read-only (simplified)
        return {
            "result": "0x" + "0" * 64,
            "status": "0x1"
        }
    
    def get_block(self, number: int) -> Optional[Dict]:
        """Get block by number"""
        block = self.blocks.get(number)
        if block:
            return block.to_dict()
        return None
    
    def get_latest_block(self) -> Dict:
        """Get latest block"""
        return self.blocks[self.current_block].to_dict()
    
    def get_transaction(self, tx_hash: str) -> Optional[Dict]:
        """Get transaction by hash"""
        tx = self.transactions.get(tx_hash)
        if tx:
            return tx.to_dict()
        return None
    
    def get_logs(self, address: str, from_block: int = 0, to_block: int = -1) -> List[Dict]:
        """Get transaction logs"""
        logs = []
        end = self.current_block if to_block == -1 else to_block
        
        for i in range(from_block, end + 1):
            block = self.blocks.get(i)
            if not block:
                continue
            for tx in block.transactions:
                if address.lower() in [tx.get("from", "").lower(), tx.get("to", "").lower()]:
                    logs.append(tx)
        
        return logs
    
    def get_code(self, address: str) -> str:
        """Get contract code"""
        account = self.accounts.get(address.lower())
        if account and account.is_contract:
            return account.code_hash
        return "0x"
    
    def stake(self, address: str, amount: int) -> Dict:
        """Stake for proof-of-stake"""
        if self.config["type"] != "native" and self.config["type"] != "hybrid":
            return {"error": "Staking not supported on this chain"}
        
        account = self.accounts.get(address.lower())
        if not account:
            return {"error": "Account not found"}
        
        if account.balance < amount:
            return {"error": "Insufficient balance"}
        
        account.balance -= amount
        self.stakers[address] = self.stakers.get(address, 0) + amount
        
        return {
            "staked": amount,
            "total_staked": self.stakers[address]
        }
    
    def get_stakers(self) -> List[Dict]:
        """Get validator list"""
        return [
            {"address": addr, "stake": stake}
            for addr, stake in self.stakers.items()
        ]
    
    def get_chain_stats(self) -> Dict:
        """Get chain statistics"""
        return {
            "chain_type": self.chain_type,
            "name": self.config["name"],
            "chain_id": self.config["chain_id"],
            "symbol": self.config["symbol"],
            "decimals": self.config["decimals"],
            "current_block": self.current_block,
            "total_transactions": len(self.transactions),
            "total_accounts": len(self.accounts),
            "consensus": self.config["consensus"],
            "validators": len(self.validators)
        }


# Flask API
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize chain
chain = CustomBlockchain("tigerex-hybrid")

@app.route('/blockchain/health')
def health():
    return jsonify(chain.get_chain_stats())

@app.route('/blockchain/create_account', methods=['POST'])
def create_account():
    data = request.get_json() or {}
    private_key = data.get('private_key', '')
    return jsonify(chain.create_account(private_key))

@app.route('/blockchain/account/<address>')
def get_account(address):
    account = chain.accounts.get(address.lower())
    if account:
        return jsonify(account.to_dict())
    return jsonify({"error": "Not found"}), 404

@app.route('/blockchain/balance/<address>')
def get_balance(address):
    return jsonify({
        "balance": chain.get_balance(address.lower()),
        "decimals": chain.config["decimals"]
    })

@app.route('/blockchain/nonce/<address>')
def get_nonce(address):
    return jsonify({"nonce": chain.get_nonce(address.lower())})

@app.route('/blockchain/send', methods=['POST'])
def send_tx():
    data = request.get_json()
    return jsonify(chain.send_transaction(
        data.get('from', '').lower(),
        data.get('to', '').lower(),
        data.get('value', 0),
        data.get('gas_price', 20000000000),
        data.get('data', '')
    ))

@app.route('/blockchain/deploy', methods=['POST'])
def deploy():
    data = request.get_json()
    return jsonify(chain.deploy_contract(
        data.get('sender', '').lower(),
        data.get('code', '')
    ))

@app.route('/blockchain/call', methods=['POST'])
def call():
    data = request.get_json()
    return jsonify(chain.call_contract(
        data.get('contract', '').lower(),
        data.get('data', '')
    ))

@app.route('/blockchain/block/<int:block_num>')
def get_block(block_num):
    block = chain.get_block(block_num)
    if block:
        return jsonify(block)
    return jsonify({"error": "Not found"}), 404

@app.route('/blockchain/latest_block')
def latest_block():
    return jsonify(chain.get_latest_block())

@app.route('/blockchain/tx/<tx_hash>')
def get_tx(tx_hash):
    tx = chain.get_transaction(tx_hash)
    if tx:
        return jsonify(tx)
    return jsonify({"error": "Not found"}), 404

@app.route('/blockchain/logs')
def get_logs():
    address = request.args.get('address', '')
    from_block = int(request.args.get('from_block', 0))
    to_block = int(request.args.get('to_block', -1))
    return jsonify(chain.get_logs(address, from_block, to_block))

@app.route('/blockchain/code/<address>')
def get_code(address):
    return jsonify({"code": chain.get_code(address.lower())})

@app.route('/blockchain/stake', methods=['POST'])
def stake():
    data = request.get_json()
    return jsonify(chain.stake(
        data.get('address', '').lower(),
        data.get('amount', 0)
    ))

@app.route('/blockchain/validators')
def validators():
    return jsonify(chain.get_stakers())

@app.route('/blockchain/stats')
def stats():
    return jsonify(chain.get_chain_stats())


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5800))
    app.run(host='0.0.0.0', port=port, threaded=True)