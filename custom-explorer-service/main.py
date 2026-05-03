#!/usr/bin/env python3
"""
TigerEx Custom Blockchain Explorer Backend
Blockchain data indexing and query API

@version 2.0.0
"""

import os
import time
import hashlib
import secrets
import logging
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
PORT = int(os.environ.get('PORT', 5901))
CHAIN_ID = int(os.environ.get('CHAIN_ID', 5777))

# Flask app
app = Flask(__name__)
CORS(app)
limiter = Limiter(key_func=lambda: request.remote_addr, app=app)

# ==================== BLOCKCHAIN DATA ====================

class Blockchain:
    """In-memory blockchain data."""
    
    def __init__(self):
        self.name = "TigerChain"
        self.symbol = "TIG"
        self.consensus = "Proof of Authority"
        
        self.blocks = {}
        self.transactions = {}
        self.accounts = defaultdict(lambda: {
            'balance': 0,
            'nonce': 0,
            'code': '',
            'storage': {}
        })
        
        self.current_block = 0
        self.total_transactions = 0
        
        # Generate demo data
        self._generate_demo_data()
    
    def _generate_demo_data(self):
        """Generate demo blocks and transactions."""
        # Create accounts
        for i in range(10):
            addr = f"0x{secrets.token_hex(20).zfill(42)}"
            self.accounts[addr] = {
                'balance': secrets.randbelow(1_000_000),
                'nonce': secrets.randbelow(1000),
                'code': '',
                'storage': {}
            }
        
        # Create blocks
        base_hash = secrets.token_hex(32)
        validators = list(self.accounts.keys())[:3]
        
        for num in range(100):
            parent_hash = base_hash
            base_hash = hashlib.sha256(f"{num}{base_hash}".encode()).hexdigest()
            
            block = {
                'number': num,
                'hash': f"0x{base_hash}",
                'parent_hash': f"0x{parent_hash}",
                'validator': validators[num % 3],
                'timestamp': int(datetime.now().timestamp()) - (100 - num) * 15,
                'transactions': [],
                'gas_used': secrets.randbelow(1_000_000),
                'gas_limit': 8_000_000,
                'size': secrets.randbelow(100),
                'difficulty': 1,
                'extra_data': f"Block {num}"
            }
            
            # Add some transactions
            num_txs = secrets.randbelow(50)
            for i in range(num_txs):
                tx_hash = secrets.token_hex(32)
                from_addr = validators[i % 3]
                to_addr = list(self.accounts.keys())[secrets.randbelow(len(self.accounts))]
                
                tx = {
                    'hash': f"0x{tx_hash}",
                    'block_number': num,
                    'from': from_addr,
                    'to': to_addr,
                    'value': secrets.randbelow(1000),
                    'gas': 21000,
                    'gas_price': secrets.randbelow(100_000_000),
                    'nonce': secrets.randbelow(10),
                    'status': 1,
                    'timestamp': block['timestamp']
                }
                
                block['transactions'].append(tx['hash'])
                self.transactions[tx['hash']] = tx
            
            self.blocks[num] = block
        
        self.current_block = 99
        self.total_transactions = len(self.transactions)
    
    def get_stats(self) -> Dict:
        """Get chain stats."""
        return {
            'name': self.name,
            'chain_id': CHAIN_ID,
            'symbol': self.symbol,
            'consensus': self.consensus,
            'current_block': self.current_block,
            'total_transactions': self.total_transactions,
            'total_accounts': len(self.accounts),
            'gas_price': 20_000_000_000
        }
    
    def get_block(self, number: int) -> Optional[Dict]:
        """Get block by number."""
        if number < 0:
            number = self.current_block + number  # Support negative indices
        return self.blocks.get(number)
    
    def get_transaction(self, tx_hash: str) -> Optional[Dict]:
        """Get transaction by hash."""
        return self.transactions.get(tx_hash)
    
    def get_account(self, address: str) -> Optional[Dict]:
        """Get account by address."""
        return self.accounts.get(address)
    
    def get_latest_blocks(self, limit: int = 10) -> List[Dict]:
        """Get latest blocks."""
        blocks = []
        for num in range(self.current_block, self.current_block - limit, -1):
            if num >= 0:
                blocks.append(self.blocks[num])
        return blocks
    
    def get_latest_transactions(self, limit: int = 20) -> List[Dict]:
        """Get latest transactions."""
        return list(self.transactions.values())[-limit:]
    
    def search(self, query: str) -> Dict:
        """Search blocks, transactions, or accounts."""
        result = {'type': 'unknown', 'data': None}
        
        # Try as transaction hash
        if query.startswith('0x') and len(query) == 66:
            tx = self.transactions.get(query)
            if tx:
                return {'type': 'transaction', 'data': tx}
        
        # Try as address
        if query.startswith('0x') and len(query) == 42:
            acc = self.accounts.get(query)
            if acc:
                return {'type': 'account', 'data': {**acc, 'address': query}}
        
        # Try as block number
        try:
            number = int(query)
            block = self.blocks.get(number)
            if block:
                return {'type': 'block', 'data': block}
        except ValueError:
            pass
        
        return result


# Initialize blockchain
bc = Blockchain()


# ==================== HEALTH ====================

@app.route('/health')
def health():
    """Health check."""
    return jsonify({
        'status': 'ok',
        'chain': bc.name,
        'block': bc.current_block
    })


# ==================== STATS ====================

@app.route('/blockchain/stats')
@limiter.limit("60/minute")
def stats():
    """Get chain statistics."""
    return jsonify(bc.get_stats())


# ==================== BLOCKS ====================

@app.route('/blockchain/latest_block')
@limiter.limit("60/minute")
def latest_block():
    """Get latest block."""
    block = bc.get_block(-1)
    if block:
        return jsonify(block)
    return jsonify({'error': 'No blocks'}), 404


@app.route('/blockchain/block/<int:number>')
@limiter.limit("60/minute")
def block(number):
    """Get block by number."""
    block = bc.get_block(number)
    if block:
        return jsonify(block)
    return jsonify({'error': 'Block not found'}), 404


# ==================== TRANSACTIONS ====================

@app.route('/blockchain/tx/<tx_hash>')
@limiter.limit("60/minute")
def transaction(tx_hash):
    """Get transaction by hash."""
    tx = bc.get_transaction(f"0x{tx_hash}" if not tx_hash.startswith('0x') else tx_hash)
    if tx:
        return jsonify(tx)
    return jsonify({'error': 'Transaction not found'}), 404


# ==================== ACCOUNTS ====================

@app.route('/blockchain/account/<address>')
@limiter.limit("60/minute")
def account(address):
    """Get account by address."""
    if not address.startswith('0x'):
        address = f"0x{address}"
    
    acc = bc.get_account(address)
    if acc:
        return jsonify({**acc, 'address': address})
    return jsonify({'error': 'Account not found'}), 404


@app.route('/blockchain/balance/<address>')
@limiter.limit("60/minute")
def balance(address):
    """Get account balance."""
    if not address.startswith('0x'):
        address = f"0x{address}"
    
    acc = bc.get_account(address)
    if acc:
        return jsonify({'address': address, 'balance': acc['balance']})
    return jsonify({'balance': 0})


# ==================== SEARCH ====================

@app.route('/blockchain/search')
@limiter.limit("30/minute")
def search():
    """Search blockchain."""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Query required'}), 400
    
    result = bc.search(query)
    if result['data']:
        return jsonify(result)
    return jsonify({'error': 'Not found'}), 404


# ==================== ERROR HANDLERS ====================

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded'}), 429


# ==================== MAIN ====================

if __name__ == '__main__':
    logger.info(f"Starting Explorer API on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, threaded=True, debug=False)# TigerEx Wallet API
class WalletService:
    @staticmethod
    def create(auth_token):
        wordlist = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
        return {'address': '0x' + os.urandom(20).hex(), 'seed': ' '.join(wordlist.split()[:24]), 'ownership': 'USER_OWNS'}
def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
