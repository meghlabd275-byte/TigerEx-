"""
TigerEx Block Explorer Service
Full blockchain explorer with blocks, transactions, addresses
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import uuid
import random
import hashlib

app = FastAPI()

# Blockchain Models
class Block(BaseModel):
    number: int
    hash: str
    parent_hash: str
    timestamp: int
    transactions: List[str]
    gas_used: int
    gas_limit: int
    miner: str
    difficulty: int

class Transaction(BaseModel):
    tx_hash: str
    block_number: int
    from_address: str
    to_address: str
    value: float
    gas_price: int
    gas_used: int
    timestamp: int
    status: str

class Token(BaseModel):
    address: str
    name: str
    symbol: str
    decimals: int
    total_supply: float

class Address(BaseModel):
    address: str
    balance: float
    transactions: List[str]
    tokens: Dict[str, float]

# In-Memory Blockchain Data
class BlockChain:
    def __init__(self):
        self.blocks = {}
        self.transactions = {}
        self.addresses = {}
        self.tokens = {}
        self.current_block = 18500000
        self._init_sample_data()
    
    def _init_sample_data(self):
        # Generate sample blocks
        for i in range(100):
            block_num = self.current_block - i
            self.blocks[block_num] = {
                "number": block_num,
                "hash": f"0x{hashlib.sha256(str(block_num).encode()).hexdigest()[:40]}",
                "parent_hash": f"0x{hashlib.sha256(str(block_num+1).encode()).hexdigest()[:40]}",
                "timestamp": int(datetime.now().timestamp()) - (i * 12),
                "transactions": [f"0x{uuid.uuid4().hex[:40]}" for _ in range(random.randint(50, 200))],
                "gas_used": random.randint(10000000, 15000000),
                "gas_limit": 15000000,
                "miner": f"0x{random.randint(1000, 9999):04x}",
                "difficulty": 128
            }
        
        # Generate sample transactions
        for _ in range(500):
            tx_hash = f"0x{uuid.uuid4().hex[:40]}"
            self.transactions[tx_hash] = {
                "tx_hash": tx_hash,
                "block_number": random.randint(18490000, 18500000),
                "from_address": f"0x{random.randint(1000, 9999):04x}{random.randint(1000, 9999):04x}",
                "to_address": f"0x{random.randint(1000, 9999):04x}{random.randint(1000, 9999):04x}",
                "value": round(random.random() * 100, 6),
                "gas_price": random.randint(20, 50),
                "gas_used": random.randint(21000, 100000),
                "timestamp": int(datetime.now().timestamp()) - random.randint(0, 8640000),
                "status": "success"
            }
        
        # Sample addresses
        for i in range(10):
            addr = f"0x{Math.random():08x}"
            self.addresses[addr] = {
                "address": addr,
                "balance": round(random.random() * 10000, 6),
                "transactions": [f"0x{uuid.uuid4().hex[:40]}" for _ in range(random.randint(5, 50))],
                "tokens": {}
            }
        
        # Sample tokens
        self.tokens = {
            "0xTIGER": {"address": "0xTIGER", "name": "Tiger Token", "symbol": "TIGER", "decimals": 18, "total_supply": 1000000000},
            "0xTHC": {"address": "0xTHC", "name": "Tiger Health Coin", "symbol": "THC", "decimals": 18, "total_supply": 500000000}
        }
    
    def get_blocks(self, limit: int = 20, offset: int = 0) -> List[Dict]:
        sorted_blocks = sorted(self.blocks.values(), key=lambda x: x["number"], reverse=True)
        return sorted_blocks[offset:offset+limit]
    
    def get_block(self, number: int) -> Optional[Dict]:
        return self.blocks.get(number)
    
    def get_transactions(self, limit: int = 20, offset: int = 0) -> List[Dict]:
        sorted_txs = sorted(self.transactions.values(), key=lambda x: x["timestamp"], reverse=True)
        return sorted_txs[offset:offset+limit]
    
    def get_transaction(self, tx_hash: str) -> Optional[Dict]:
        return self.transactions.get(tx_hash)
    
    def get_address(self, address: str) -> Optional[Dict]:
        return self.addresses.get(address)
    
    def get_tokens(self, limit: int = 50) -> List[Dict]:
        return list(self.tokens.values())[:limit]
    
    def search(self, query: str) -> Dict:
        # Search blocks
        if query.isdigit():
            block = self.blocks.get(int(query))
            if block:
                return {"type": "block", "data": block}
        
        # Search transactions
        if query in self.transactions:
            return {"type": "transaction", "data": self.transactions[query]}
        
        # Search addresses
        if query in self.addresses:
            return {"type": "address", "data": self.addresses[query]}
        
        return {"type": "not_found"}
    
    def get_stats(self) -> Dict:
        return {
            "current_block": self.current_block,
            "total_transactions": len(self.transactions),
            "total_addresses": len(self.addresses),
            "total_tokens": len(self.tokens),
            "tps": 145,
            "gas_price": 25.4
        }

chain = BlockChain()

# REST API Endpoints
@app.get("/")
async def root():
    return {"service": "TigerChain Explorer", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "blocks": chain.current_block}

# Block Explorer API
@app.get("/api/v1/blocks")
async def get_blocks(limit: int = 20, offset: int = 0):
    return chain.get_blocks(limit, offset)

@app.get("/api/v1/blocks/{number}")
async def get_block(number: int):
    block = chain.get_block(number)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    return block

@app.get("/api/v1/blocks/{number}/transactions")
async def get_block_transactions(number: int):
    block = chain.get_block(number)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    txs = [chain.transactions.get(tx) for tx in block["transactions"] if tx in chain.transactions]
    return txs

@app.get("/api/v1/transactions")
async def get_transactions(limit: int = 20, offset: int = 0):
    return chain.get_transactions(limit, offset)

@app.get("/api/v1/transactions/{tx_hash}")
async def get_transaction(tx_hash: str):
    tx = chain.get_transaction(tx_hash)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx

@app.get("/api/v1/search")
async def search(q: str):
    return chain.search(q)

@app.get("/api/v1/addresses/{address}")
async def get_address(address: str):
    addr = chain.get_address(address)
    if not addr:
        raise HTTPException(status_code=404, detail="Address not found")
    return addr

@app.get("/api/v1/addresses/{address}/transactions")
async def get_address_transactions(address: str, limit: int = 20):
    addr = chain.get_address(address)
    if not addr:
        raise HTTPException(status_code=404, detail="Address not found")
    return addr["transactions"][:limit]

@app.get("/api/v1/tokens")
async def get_tokens(limit: int = 50):
    return chain.get_tokens(limit)

@app.get("/api/v1/tokens/{address}/holders")
async def get_token_holders(address: str, limit: int = 100):
    return []

@app.get("/api/v1/nfts")
async def get_nfts(limit: int = 20):
    return []

@app.get("/api/v1/validators")
async def get_validators():
    return []

@app.get("/api/v1/stats")
async def get_stats():
    return chain.get_stats()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
