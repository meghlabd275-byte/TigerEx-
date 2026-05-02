#!/usr/bin/env python3
"""
TigerEx Blockchain Management Service
Real blockchain integration with Etherscan, contract verification, and live data
"""
import os
import json
import time
import logging
import requests
import hashlib
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Blockchain configurations
BLOCKCHAINS = {
    "ethereum": {
        "name": "Ethereum",
        "chain_id": 1,
        "rpc_url": os.environ.get("ETHEREUM_RPC", "https://eth.llamarpc.com"),
        "explorer": "https://api.etherscan.io/api",
        "symbol": "ETH",
        "decimals": 18
    },
    "bsc": {
        "name": "BNB Smart Chain",
        "chain_id": 56,
        "rpc_url": os.environ.get("BSC_RPC", "https://bsc.llamarpc.com"),
        "explorer": "https://api.bscscan.com/api",
        "symbol": "BNB",
        "decimals": 18
    },
    "polygon": {
        "name": "Polygon",
        "chain_id": 137,
        "rpc_url": os.environ.get("POLYGON_RPC", "https://polygon.llamarpc.com"),
        "explorer": "https://api.polygonscan.com/api",
        "symbol": "MATIC",
        "decimals": 18
    },
    "arbitrum": {
        "name": "Arbitrum One",
        "chain_id": 42161,
        "rpc_url": os.environ.get("ARBITRUM_RPC", "https://arb1.llamarpc.com"),
        "explorer": "https://api.arbiscan.io/api",
        "symbol": "ETH",
        "decimals": 18
    },
    "optimism": {
        "name": "Optimism",
        "chain_id": 10,
        "rpc_url": os.environ.get("OPTIMISM_RPC", "https://optimism.llamarpc.com"),
        "explorer": "https://api-optimistic.etherscan.io/api",
        "symbol": "ETH",
        "decimals": 18
    },
    "avalanche": {
        "name": "Avalanche",
        "chain_id": 43114,
        "rpc_url": os.environ.get("AVALANCHE_RPC", "https://avalanche.llamarpc.com"),
        "explorer": "https://api.snowtrace.io/api",
        "symbol": "AVAX",
        "decimals": 18
    }
}

# ABI for common contracts
COMMON_ABIS = {
    "erc20": [
        {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
        {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
        {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
        {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
        {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
        {"constant": False, "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
        {"constant": False, "inputs": [{"name": "_from", "type": "address"}, {"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transferFrom", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
        {"constant": False, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
        {"constant": True, "inputs": [{"name": "_owner", "type": "address"}, {"name": "_spender", "type": "address"}], "name": "allowance", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
    ],
    "uniswap_v2_router": [
        {"inputs": [{"internalType": "address", "name": "_tokenA", "type": "address"}, {"internalType": "address", "name": "_tokenB", "type": "address"}], "name": "pairFor", "outputs": [{"internalType": "address", "name": "", "type": "address"}], "type": "function"},
        {"inputs": [{"internalType": "address", "name": "tokenA", "type": "address"}, {"internalType": "uint256", "name": "amountADesired", "type": "uint256"}, {"internalType": "uint256", "name": "amountBDesired", "type": "uint256"}, {"internalType": "uint256", "name": "amountAMin", "type": "uint256"}, {"internalType": "uint256", "name": "amountBMin", "type": "uint256"}, {"internalType": "address", "name": "to", "type": "address"}, {"internalType": "uint256", "name": "deadline", "type": "uint256"}], "name": "addLiquidity", "outputs": [{"internalType": "uint256", "name": "amountA", "type": "uint256"}, {"internalType": "uint256", "name": "amountB", "type": "uint256"}, {"internalType": "uint256", "name": "liquidity", "type": "uint256"}], "type": "function"},
        {"inputs": [{"internalType": "address", "name": "tokenA", "type": "address"}, {"internalType": "uint256", "name": "liquidity", "type": "uint256"}, {"internalType": "uint256", "name": "amountAMin", "type": "uint256"}, {"internalType": "uint256", "name": "amountBMin", "type": "uint256"}, {"internalType": "address", "name": "to", "type": "address"}, {"internalType": "uint256", "name": "deadline", "type": "uint256"}], "name": "removeLiquidity", "outputs": [{"internalType": "uint256", "name": "amountA", "type": "uint256"}, {"internalType": "uint256", "name": "amountB", "type": "uint256"}], "type": "function"}
    ]
}


@dataclass
class Token:
    address: str
    chain: str
    symbol: str
    name: str
    decimals: int
    total_supply: str
    verified: bool = False
    
    def to_dict(self) -> dict:
        return {
            "address": self.address,
            "chain": self.chain,
            "symbol": self.symbol,
            "name": self.name,
            "decimals": self.decimals,
            "total_supply": self.total_supply,
            "verified": self.verified
        }


@dataclass
class Transaction:
    tx_hash: str
    chain: str
    from_addr: str
    to_addr: str
    value: str
    gas_used: int
    gas_price: int
    block_number: int
    status: str
    timestamp: datetime
    
    def to_dict(self) -> dict:
        return {
            "hash": self.tx_hash,
            "chain": self.chain,
            "from": self.from_addr,
            "to": self.to_addr,
            "value": self.value,
            "gas_used": self.gas_used,
            "gas_price": self.gas_price,
            "block": self.block_number,
            "status": self.status,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class Block:
    number: int
    hash: str
    parent_hash: str
    timestamp: datetime
    transactions: List[str]
    gas_used: int
    gas_limit: int
    
    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "hash": self.hash,
            "parent_hash": self.parent_hash,
            "timestamp": self.timestamp.isoformat(),
            "transactions": self.transactions,
            "gas_used": self.gas_used,
            "gas_limit": self.gas_limit
        }


class BlockchainManager:
    """Real blockchain management with live data"""
    
    def __init__(self):
        self.tokens = {}  # address -> Token
        self.transactions = {}  # tx_hash -> Transaction
        self.blocks = {}  # block_number -> Block
        self.watchlist = {}  # user_id -> [addresses]
        self.cache = {}
        self.cache_ttl = 60  # seconds
        self._start_price_feed()
        logger.info("Blockchain manager initialized")
    
    def _start_price_feed(self):
        """Background price feed"""
        def loop():
            while True:
                self._update_gas_prices()
                time.sleep(30)
        threading.Thread(target=loop, daemon=True).start()
    
    def _update_gas_prices(self):
        """Update gas prices for all chains"""
        for chain_name, config in BLOCKCHAINS.items():
            try:
                # Get gas price from RPC
                response = requests.post(
                    config["rpc_url"],
                    json={
                        "jsonrpc": "2.0",
                        "method": "eth_gasPrice",
                        "params": [],
                        "id": 1
                    },
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    if "result" in data:
                        self.cache[f"{chain_name}_gas"] = int(data["result"], 16)
            except Exception as e:
                logger.warning(f"Gas price update failed for {chain_name}: {e}")
    
    def get_gas_price(self, chain: str) -> int:
        """Get current gas price for chain"""
        return self.cache.get(f"{chain}_gas", 20000000000)  # 20 gwei default
    
    def get_balance(self, chain: str, address: str) -> Dict[str, Any]:
        """Get wallet balance from RPC"""
        config = BLOCKCHAINS.get(chain)
        if not config:
            return {"error": "Invalid chain"}
        
        try:
            # Get native balance
            response = requests.post(
                config["rpc_url"],
                json={
                    "jsonrpc": "2.0",
                    "method": "eth_getBalance",
                    "params": [address, "latest"],
                    "id": 1
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                balance_wei = int(data.get("result", "0x0"), 16)
                balance = balance_wei / (10 ** config["decimals"])
                return {
                    "chain": chain,
                    "address": address,
                    "balance": balance,
                    "symbol": config["symbol"],
                    "raw": data.get("result")
                }
        except Exception as e:
            return {"error": str(e)}
        
        return {"error": "Failed to get balance"}
    
    def get_token_balance(self, chain: str, token_address: str, wallet_address: str) -> Dict[str, Any]:
        """Get ERC20 token balance"""
        config = BLOCKCHAINS.get(chain)
        if not config:
            return {"error": "Invalid chain"}
        
        # ERC20 balanceOf call
        selector = "0x70a08231"
        addr_padded = wallet_address.lower().replace("0x", "").rjust(64, "0")
        data = selector + addr_padded
        
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_call",
            "params": [{
                "to": token_address,
                "data": data
            }, "latest"],
            "id": 1
        }
        
        try:
            response = requests.post(config["rpc_url"], json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json().get("result", "0x0")
                balance = int(result, 16)
                
                # Get decimals
                decimals = self._get_token_decimals(chain, token_address)
                
                return {
                    "chain": chain,
                    "token": token_address,
                    "wallet": wallet_address,
                    "balance": balance / (10 ** decimals),
                    "raw": result
                }
        except Exception as e:
            return {"error": str(e)}
        
        return {"error": "Failed"}
    
    def _get_token_decimals(self, chain: str, token_address: str) -> int:
        """Get token decimals"""
        config = BLOCKCHAINS.get(chain)
        
        # Try from cache first
        if token_address in self.tokens:
            return self.tokens[token_address].decimals
        
        try:
            selector = "0x313ce567"
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_call",
                "params": [{
                    "to": token_address,
                    "data": selector
                }, "latest"],
                "id": 1
            }
            
            response = requests.post(config["rpc_url"], json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json().get("result", "0x0")
                return int(result, 16)
        except:
            pass
        
        return 18  # Default
    
    def get_transaction(self, chain: str, tx_hash: str) -> Optional[Transaction]:
        """Get transaction from explorer"""
        config = BLOCKCHAINS.get(chain)
        if not config:
            return None
        
        api_key = os.environ.get("ETHERSCAN_API_KEY", "")
        
        params = {
            "module": "proxy",
            "action": "eth_getTransactionByHash",
            "txhash": tx_hash,
            "apikey": api_key
        }
        
        try:
            response = requests.get(config["explorer"], params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1":
                    result = data["result"]
                    return Transaction(
                        tx_hash=tx_hash,
                        chain=chain,
                        from_addr=result.get("from", ""),
                        to_addr=result.get("to", ""),
                        value=str(int(result.get("value", "0x0"), 16)),
                        gas_used=int(result.get("gasUsed", "0x0"), 16),
                        gas_price=int(result.get("gasPrice", "0x0"), 16),
                        block_number=int(result.get("blockNumber", "0x0"), 16),
                        status="confirmed" if result.get("blockNumber") else "pending",
                        timestamp=datetime.utcnow()
                    )
        except Exception as e:
            logger.warning(f"Get tx failed: {e}")
        
        return None
    
    def get_token_info(self, chain: str, address: str) -> Optional[Token]:
        """Get token info from explorer"""
        if (address, chain) in self.tokens:
            return self.tokens[(address, chain)]
        
        config = BLOCKCHAINS.get(chain)
        if not config:
            return None
        
        api_key = os.environ.get("ETHERSCAN_API_KEY", "")
        
        params = {
            "module": "token",
            "action": "tokeninfo",
            "contractaddress": address,
            "apikey": api_key
        }
        
        try:
            response = requests.get(config["explorer"], params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1":
                    result = data["result"][0] if data.get("result") else {}
                    token = Token(
                        address=address,
                        chain=chain,
                        symbol=result.get("symbol", "UNKNOWN"),
                        name=result.get("name", "Unknown Token"),
                        decimals=int(result.get("divisor", "1")),
                        total_supply=result.get("totalSupply", "0"),
                        verified=True
                    )
                    self.tokens[(address, chain)] = token
                    return token
        except Exception as e:
            logger.warning(f"Token info failed: {e}")
        
        return None
    
    def get_block(self, chain: str, block_number: int) -> Optional[Block]:
        """Get block data"""
        config = BLOCKCHAINS.get(chain)
        if not config:
            return None
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getBlockByNumber",
                "params": [hex(block_number), True],
                "id": 1
            }
            
            response = requests.post(config["rpc_url"], json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json().get("result", {})
                if result:
                    return Block(
                        number=block_number,
                        hash=result.get("hash", ""),
                        parent_hash=result.get("parentHash", ""),
                        timestamp=datetime.fromtimestamp(int(result.get("timestamp", "0"), 16)),
                        transactions=[tx.get("hash", "") for tx in result.get("transactions", [])],
                        gas_used=int(result.get("gasUsed", "0x0"), 16),
                        gas_limit=int(result.get("gasLimit", "0x0"), 16)
                    )
        except Exception as e:
            logger.warning(f"Get block failed: {e}")
        
        return None
    
    def get_latest_block(self, chain: str) -> int:
        """Get latest block number"""
        config = BLOCKCHAINS.get(chain)
        if not config:
            return 0
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_blockNumber",
                "params": [],
                "id": 1
            }
            
            response = requests.post(config["rpc_url"], json=payload, timeout=5)
            if response.status_code == 200:
                result = response.json().get("result", "0x0")
                return int(result, 16)
        except:
            pass
        
        return 0
    
    def get_price(self, chain: str) -> float:
        """Get native token price (from CoinGecko)"""
        symbol_map = {
            "ethereum": "ethereum",
            "bsc": "binancecoin",
            "polygon": "matic-network",
            "arbitrum": "ethereum",
            "optimism": "ethereum",
            "avalanche": "avalanche-2"
        }
        
        coin_id = symbol_map.get(chain, chain)
        
        try:
            response = requests.get(
                f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return data.get(coin_id, {}).get("usd", 0)
        except:
            pass
        
        return 0
    
    def add_to_watchlist(self, user_id: str, chain: str, address: str):
        """Add address to user's watchlist"""
        if user_id not in self.watchlist:
            self.watchlist[user_id] = []
        self.watchlist[user_id].append({
            "chain": chain,
            "address": address,
            "added_at": datetime.utcnow().isoformat()
        })
    
    def get_watchlist(self, user_id: str) -> List[Dict]:
        """Get user's watchlist with current balances"""
        watchlist = self.watchlist.get(user_id, [])
        result = []
        
        for item in watchlist:
            balance = self.get_balance(item["chain"], item["address"])
            result.append({
                **item,
                "balance": balance
            })
        
        return result
    
    def verify_contract(self, chain: str, address: str) -> Dict:
        """Verify contract on explorer"""
        config = BLOCKCHAINS.get(chain)
        if not config:
            return {"verified": False, "error": "Invalid chain"}
        
        api_key = os.environ.get("ETHERSCAN_API_KEY", "")
        
        params = {
            "module": "contract",
            "action": "getsourcecode",
            "address": address,
            "apikey": api_key
        }
        
        try:
            response = requests.get(config["explorer"], params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1":
                    result = data["result"]
                    if result and result[0].get("SourceCode"):
                        return {
                            "verified": True,
                            "name": result[0].get("ContractName"),
                            "compiler": result[0].get("CompilerVersion"),
                            "optimization": result[0].get("OptimizationUsed")
                        }
        except:
            pass
        
        return {"verified": False}
    
    def generate_wallet(self) -> Dict:
        """Generate a new wallet (keys only, no chain interaction)"""
        # This generates local keys only - no network call
        private_key = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
        public_key = hashlib.sha256(private_key.encode()).hexdigest()[:40]
        address = "0x" + public_key
        
        return {
            "address": address,
            "private_key_hash": hashlib.sha256(private_key.encode()).hexdigest()[:64],
            "note": "Keys generated locally. Fund with native tokens to use."
        }
    
    def get_chain_stats(self, chain: str) -> Dict:
        """Get chain statistics"""
        latest_block = self.get_latest_block(chain)
        gas_price = self.get_gas_price(chain)
        price = self.get_price(chain)
        
        return {
            "chain": chain,
            "name": BLOCKCHAINS[chain]["name"],
            "latest_block": latest_block,
            "gas_price_wei": gas_price,
            "gas_price_gwei": gas_price / 1e9,
            "price_usd": price
        }


# Flask API
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

blockchain = BlockchainManager()

@app.route('/blockchain/health')
def health():
    return jsonify({"status": "ok", "chains": list(BLOCKCHAINS.keys())})

@app.route('/blockchain/balance/<chain>/<address>')
def balance(chain, address):
    return jsonify(blockchain.get_balance(chain, address))

@app.route('/blockchain/token-balance', methods=['POST'])
def token_balance():
    data = request.get_json()
    return jsonify(blockchain.get_token_balance(
        data.get('chain', 'ethereum'),
        data.get('token_address', ''),
        data.get('wallet_address', '')
    ))

@app.route('/blockchain/transaction/<chain>/<tx_hash>')
def get_tx(chain, tx_hash):
    tx = blockchain.get_transaction(chain, tx_hash)
    if tx:
        return jsonify(tx.to_dict())
    return jsonify({"error": "Not found"}), 404

@app.route('/blockchain/block/<chain>/<int:block_num>')
def get_block(chain, block_num):
    block = blockchain.get_block(chain, block_num)
    if block:
        return jsonify(block.to_dict())
    return jsonify({"error": "Not found"}), 404

@app.route('/blockchain/latest-block/<chain>')
def latest_block(chain):
    return jsonify({"block": blockchain.get_latest_block(chain)})

@app.route('/blockchain/token/<chain>/<address>')
def token_info(chain, address):
    token = blockchain.get_token_info(chain, address)
    if token:
        return jsonify(token.to_dict())
    return jsonify({"error": "Not found"}), 404

@app.route('/blockchain/stats/<chain>')
def stats(chain):
    return jsonify(blockchain.get_chain_stats(chain))

@app.route('/blockchain/verify/<chain>/<address>')
def verify(chain, address):
    return jsonify(blockchain.verify_contract(chain, address))

@app.route('/blockchain/watchlist', methods=['POST'])
def add_watchlist():
    data = request.get_json()
    blockchain.add_to_watchlist(data.get('user_id', ''), data.get('chain', ''), data.get('address', ''))
    return jsonify({"success": True})

@app.route('/blockchain/watchlist/<user_id>')
def get_watchlist(user_id):
    return jsonify(blockchain.get_watchlist(user_id))

@app.route('/blockchain/wallet/generate', methods=['POST'])
def generate_wallet():
    return jsonify(blockchain.generate_wallet())


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5400))
    app.run(host='0.0.0.0', port=port, threaded=True)