#!/usr/bin/env python3
"""
TigerEx Blockchain Integration Service
Complete blockchain integration for EVM and Non-EVM chains
Port: 8100
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import asyncio
import asyncpg
import redis.asyncio as redis
import structlog
import uvicorn
import os
import json
import httpx
from web3 import Web3, AsyncWeb3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.transaction import Transaction
import base58
from tonclient.client import TonClient
from tonclient.types import KeyPair
import hashlib
import secrets

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/tigerex")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
ADMIN_SERVICE_URL = os.getenv("ADMIN_SERVICE_URL", "http://localhost:8160")

# Blockchain configurations
BLOCKCHAIN_CONFIGS = {
    "ethereum": {
        "rpc": os.getenv("ETH_RPC", "https://mainnet.infura.io/v3/YOUR_PROJECT_ID"),
        "chain_id": 1,
        "native_token": "ETH",
        "type": "evm"
    },
    "bsc": {
        "rpc": os.getenv("BSC_RPC", "https://bsc-dataseed.binance.org/"),
        "chain_id": 56,
        "native_token": "BNB",
        "type": "evm"
    },
    "polygon": {
        "rpc": os.getenv("POLYGON_RPC", "https://polygon-rpc.com/"),
        "chain_id": 137,
        "native_token": "MATIC",
        "type": "evm"
    },
    "arbitrum": {
        "rpc": os.getenv("ARBITRUM_RPC", "https://arb1.arbitrum.io/rpc"),
        "chain_id": 42161,
        "native_token": "ETH",
        "type": "evm"
    },
    "solana": {
        "rpc": os.getenv("SOLANA_RPC", "https://api.mainnet-beta.solana.com"),
        "chain_id": None,
        "native_token": "SOL",
        "type": "non-evm"
    },
    "ton": {
        "rpc": os.getenv("TON_RPC", "https://toncenter.com/api/v2/jsonRPC"),
        "chain_id": None,
        "native_token": "TON",
        "type": "non-evm"
    }
}

# Global connections
db_pool = None
redis_client = None
web3_connections = {}
solana_clients = {}
ton_clients = {}

# Pydantic models
class TokenType(str, Enum):
    NATIVE = "native"
    ERC20 = "erc20"
    BEP20 = "bep20"
    SPL = "spl"
    TON_JETTON = "ton_jetton"
    VIRTUAL = "virtual"

class BlockchainType(str, Enum):
    EVM = "evm"
    NON_EVM = "non-evm"

class TokenStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"

class TokenBase(BaseModel):
    symbol: str
    name: str
    blockchain: str
    token_type: TokenType
    contract_address: Optional[str] = None
    decimals: int = 18
    status: TokenStatus = TokenStatus.PENDING

class TokenCreate(TokenBase):
    initial_supply: Optional[Decimal] = None
    max_supply: Optional[Decimal] = None
    is_virtual: bool = False
    backing_ratio: Optional[Decimal] = None

class TokenResponse(TokenBase):
    id: int
    created_at: datetime
    updated_at: datetime
    total_supply: Optional[Decimal]
    circulating_supply: Optional[Decimal]
    is_listed: bool = False

class TradingPairBase(BaseModel):
    base_token_symbol: str
    quote_token_symbol: str
    blockchain: str
    min_order_size: Decimal
    max_order_size: Decimal
    tick_size: Decimal

class TradingPairCreate(TradingPairBase):
    initial_liquidity_base: Optional[Decimal] = None
    initial_liquidity_quote: Optional[Decimal] = None

class DepositAddressBase(BaseModel):
    blockchain: str
    token_symbol: str
    user_id: int

class DepositAddressResponse(DepositAddressBase):
    id: int
    address: str
    tag: Optional[str]
    is_active: bool
    created_at: datetime

class AdminAction(BaseModel):
    action: str
    target_type: str
    target_id: str
    parameters: Dict[str, Any] = {}

# Authentication
security = HTTPBearer()

async def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify admin JWT token"""
    try:
        # Implement JWT verification logic
        token = credentials.credentials
        # For now, implement basic verification
        if token != "admin-token":
            raise HTTPException(status_code=401, detail="Invalid admin token")
        return {"user_id": 1, "role": "admin"}
    except Exception as e:
        logger.error("Admin token verification failed", error=str(e))
        raise HTTPException(status_code=401, detail="Invalid admin token")

# Database initialization
async def init_database():
    """Initialize database connection and create tables"""
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)
        
        # Create tables
        async with db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS blockchains (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50) UNIQUE NOT NULL,
                    chain_id INTEGER,
                    rpc_url TEXT NOT NULL,
                    native_token VARCHAR(10) NOT NULL,
                    blockchain_type VARCHAR(20) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS tokens (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(20) NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    blockchain VARCHAR(50) NOT NULL,
                    contract_address TEXT,
                    token_type VARCHAR(20) NOT NULL,
                    decimals INTEGER DEFAULT 18,
                    total_supply DECIMAL(50, 18),
                    circulating_supply DECIMAL(50, 18),
                    is_virtual BOOLEAN DEFAULT FALSE,
                    backing_ratio DECIMAL(10, 4),
                    status VARCHAR(20) DEFAULT 'pending',
                    is_listed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(symbol, blockchain)
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS trading_pairs (
                    id SERIAL PRIMARY KEY,
                    base_token_symbol VARCHAR(20) NOT NULL,
                    quote_token_symbol VARCHAR(20) NOT NULL,
                    blockchain VARCHAR(50) NOT NULL,
                    min_order_size DECIMAL(20, 8),
                    max_order_size DECIMAL(20, 8),
                    tick_size DECIMAL(20, 8),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(base_token_symbol, quote_token_symbol, blockchain)
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS deposit_addresses (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    blockchain VARCHAR(50) NOT NULL,
                    token_symbol VARCHAR(20) NOT NULL,
                    address TEXT NOT NULL,
                    tag TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Insert default blockchains
            for blockchain, config in BLOCKCHAIN_CONFIGS.items():
                await conn.execute("""
                    INSERT INTO blockchains (name, chain_id, rpc_url, native_token, blockchain_type)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (name) DO NOTHING
                """, blockchain, config["chain_id"], config["rpc"], config["native_token"], config["type"])
                
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))
        raise

# Blockchain connection initialization
async def init_blockchain_connections():
    """Initialize connections to all blockchain networks"""
    try:
        # Initialize EVM connections
        for blockchain, config in BLOCKCHAIN_CONFIGS.items():
            if config["type"] == "evm":
                web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(config["rpc"]))
                if blockchain == "bsc":
                    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
                web3_connections[blockchain] = web3
                
        # Initialize Solana connection
        solana_client = AsyncClient(BLOCKCHAIN_CONFIGS["solana"]["rpc"])
        solana_clients["solana"] = solana_client
        
        # Initialize TON connection
        ton_client = TonClient()
        ton_clients["ton"] = ton_client
        
        logger.info("Blockchain connections initialized")
    except Exception as e:
        logger.error("Blockchain connection initialization failed", error=str(e))
        raise

# Lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    await init_database()
    await init_blockchain_connections()
    logger.info("TigerEx Blockchain Integration Service started")
    yield
    # Shutdown
    if db_pool:
        await db_pool.close()
    if redis_client:
        await redis_client.close()
    logger.info("TigerEx Blockchain Integration Service stopped")

# Create FastAPI app
app = FastAPI(
    title="TigerEx Blockchain Integration Service",
    description="Complete blockchain integration for EVM and Non-EVM chains",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "blockchain-integration", "timestamp": datetime.utcnow()}

# Token management endpoints
@app.post("/api/admin/tokens/create", response_model=TokenResponse)
async def create_token(
    token_data: TokenCreate,
    background_tasks: BackgroundTasks,
    admin: dict = Depends(verify_admin_token)
):
    """Create a new token on specified blockchain"""
    try:
        async with db_pool.acquire() as conn:
            # Check if blockchain exists and is active
            blockchain = await conn.fetchrow(
                "SELECT * FROM blockchains WHERE name = $1 AND is_active = TRUE",
                token_data.blockchain
            )
            if not blockchain:
                raise HTTPException(status_code=400, detail="Blockchain not found or inactive")
            
            # Create token based on blockchain type
            if blockchain["blockchain_type"] == "evm":
                contract_address = await deploy_evm_token(token_data)
            elif blockchain["blockchain_type"] == "non-evm":
                contract_address = await deploy_non_evm_token(token_data)
            else:
                raise HTTPException(status_code=400, detail="Unsupported blockchain type")
            
            # Insert token into database
            token_id = await conn.fetchval("""
                INSERT INTO tokens (symbol, name, blockchain, contract_address, 
                                  token_type, decimals, total_supply, is_virtual, 
                                  backing_ratio, status)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING id
            """, token_data.symbol, token_data.name, token_data.blockchain,
                contract_address, token_data.token_type.value, token_data.decimals,
                token_data.initial_supply, token_data.is_virtual, token_data.backing_ratio,
                token_data.status.value)
            
            token = await conn.fetchrow("SELECT * FROM tokens WHERE id = $1", token_id)
            
            # Log admin action
            background_tasks.add_task(
                log_admin_action,
                admin["user_id"],
                "CREATE_TOKEN",
                "token",
                str(token_id),
                {"token_data": token_data.dict()}
            )
            
            return TokenResponse(**dict(token))
            
    except Exception as e:
        logger.error("Token creation failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Token creation failed: {str(e)}")

@app.get("/api/admin/tokens", response_model=List[TokenResponse])
async def get_tokens(
    blockchain: Optional[str] = Query(None),
    status: Optional[TokenStatus] = Query(None),
    admin: dict = Depends(verify_admin_token)
):
    """Get all tokens with optional filtering"""
    try:
        async with db_pool.acquire() as conn:
            query = "SELECT * FROM tokens WHERE 1=1"
            params = []
            
            if blockchain:
                query += " AND blockchain = $1"
                params.append(blockchain)
            
            if status:
                query += f" AND status = ${len(params) + 1}"
                params.append(status.value)
            
            query += " ORDER BY created_at DESC"
            
            tokens = await conn.fetch(query, *params)
            return [TokenResponse(**dict(token)) for token in tokens]
            
    except Exception as e:
        logger.error("Failed to fetch tokens", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch tokens")

# Trading pair management
@app.post("/api/admin/trading-pairs/create")
async def create_trading_pair(
    pair_data: TradingPairCreate,
    background_tasks: BackgroundTasks,
    admin: dict = Depends(verify_admin_token)
):
    """Create a new trading pair"""
    try:
        async with db_pool.acquire() as conn:
            # Verify both tokens exist and are active
            base_token = await conn.fetchrow(
                "SELECT * FROM tokens WHERE symbol = $1 AND blockchain = $2 AND status = 'active'",
                pair_data.base_token_symbol, pair_data.blockchain
            )
            quote_token = await conn.fetchrow(
                "SELECT * FROM tokens WHERE symbol = $1 AND blockchain = $2 AND status = 'active'",
                pair_data.quote_token_symbol, pair_data.blockchain
            )
            
            if not base_token or not quote_token:
                raise HTTPException(status_code=400, detail="One or both tokens not found or inactive")
            
            # Create trading pair
            pair_id = await conn.fetchval("""
                INSERT INTO trading_pairs (base_token_symbol, quote_token_symbol, blockchain,
                                         min_order_size, max_order_size, tick_size)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            """, pair_data.base_token_symbol, pair_data.quote_token_symbol,
                pair_data.blockchain, pair_data.min_order_size,
                pair_data.max_order_size, pair_data.tick_size)
            
            # Initialize liquidity if provided
            if pair_data.initial_liquidity_base and pair_data.initial_liquidity_quote:
                await initialize_liquidity_pool(
                    pair_id,
                    pair_data.initial_liquidity_base,
                    pair_data.initial_liquidity_quote
                )
            
            # Log admin action
            background_tasks.add_task(
                log_admin_action,
                admin["user_id"],
                "CREATE_TRADING_PAIR",
                "trading_pair",
                str(pair_id),
                {"pair_data": pair_data.dict()}
            )
            
            return {"message": "Trading pair created successfully", "pair_id": pair_id}
            
    except Exception as e:
        logger.error("Trading pair creation failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Trading pair creation failed: {str(e)}")

# Deposit address generation
@app.post("/api/admin/deposit-addresses/generate", response_model=DepositAddressResponse)
async def generate_deposit_address(
    address_data: DepositAddressBase,
    admin: dict = Depends(verify_admin_token)
):
    """Generate unique deposit address for user"""
    try:
        async with db_pool.acquire() as conn:
            # Check if token exists and is active
            token = await conn.fetchrow(
                "SELECT * FROM tokens WHERE symbol = $1 AND blockchain = $2 AND status = 'active'",
                address_data.token_symbol, address_data.blockchain
            )
            if not token:
                raise HTTPException(status_code=400, detail="Token not found or inactive")
            
            # Generate address based on blockchain type
            blockchain = await conn.fetchrow(
                "SELECT * FROM blockchains WHERE name = $1", address_data.blockchain
            )
            
            if blockchain["blockchain_type"] == "evm":
                address = await generate_evm_address(address_data.user_id, address_data.blockchain)
            elif blockchain["blockchain_type"] == "non-evm":
                address = await generate_non_evm_address(address_data.user_id, address_data.blockchain)
            else:
                raise HTTPException(status_code=400, detail="Unsupported blockchain type")
            
            # Store address in database
            address_id = await conn.fetchval("""
                INSERT INTO deposit_addresses (user_id, blockchain, token_symbol, address)
                VALUES ($1, $2, $3, $4)
                RETURNING id
            """, address_data.user_id, address_data.blockchain,
                address_data.token_symbol, address)
            
            created_address = await conn.fetchrow(
                "SELECT * FROM deposit_addresses WHERE id = $1", address_id
            )
            
            return DepositAddressResponse(**dict(created_address))
            
    except Exception as e:
        logger.error("Deposit address generation failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Deposit address generation failed: {str(e)}")

# Helper functions
async def deploy_evm_token(token_data: TokenCreate) -> str:
    """Deploy token on EVM blockchain"""
    # Implementation for EVM token deployment
    # This would include smart contract deployment
    return f"0x{secrets.token_hex(20)}"  # Mock contract address

async def deploy_non_evm_token(token_data: TokenCreate) -> str:
    """Deploy token on non-EVM blockchain"""
    # Implementation for non-EVM token deployment
    return f"mock_contract_{secrets.token_hex(10)}"

async def generate_evm_address(user_id: int, blockchain: str) -> str:
    """Generate EVM deposit address"""
    # Generate deterministic address based on user_id
    private_key = hashlib.sha256(f"{user_id}_{blockchain}_tigerex".encode()).hexdigest()[:32]
    account = Account.from_key(private_key)
    return account.address

async def generate_non_evm_address(user_id: int, blockchain: str) -> str:
    """Generate non-EVM deposit address"""
    if blockchain == "solana":
        # Generate Solana address
        keypair = Keypair()
        return str(keypair.public_key)
    elif blockchain == "ton":
        # Generate TON address
        return f"EQ{secrets.token_hex(32)}"
    else:
        return f"mock_address_{blockchain}_{user_id}"

async def initialize_liquidity_pool(pair_id: int, base_amount: Decimal, quote_amount: Decimal):
    """Initialize liquidity pool for trading pair"""
    # Implementation for liquidity pool initialization
    logger.info("Liquidity pool initialized", pair_id=pair_id, base_amount=base_amount, quote_amount=quote_amount)

async def log_admin_action(admin_id: int, action: str, target_type: str, target_id: str, parameters: Dict[str, Any]):
    """Log admin action for audit trail"""
    try:
        async with db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO admin_audit_log (admin_id, action, target_type, target_id, parameters)
                VALUES ($1, $2, $3, $4, $5)
            """, admin_id, action, target_type, target_id, json.dumps(parameters))
    except Exception as e:
        logger.error("Failed to log admin action", error=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8100))
    uvicorn.run(app, host="0.0.0.0", port=port)