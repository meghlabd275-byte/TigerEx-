"""
TigerEx Comprehensive Admin Service
Central admin service for managing tokens, trading pairs, blockchains, and liquidity
Port: 8160
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
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
from contextlib import asynccontextmanager
from web3 import Web3
import ccxt.async_support as ccxt

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
VIRTUAL_LIQUIDITY_SERVICE_URL = os.getenv("VIRTUAL_LIQUIDITY_SERVICE_URL", "http://localhost:8150")
TOKEN_LISTING_SERVICE_URL = os.getenv("TOKEN_LISTING_SERVICE_URL", "http://localhost:8000")
TRADING_PAIR_SERVICE_URL = os.getenv("TRADING_PAIR_SERVICE_URL", "http://localhost:8000")

# Global connections
db_pool = None
redis_client = None
http_client = None

# Security
security = HTTPBearer()

# Enums
class BlockchainType(str, Enum):
    EVM = "evm"
    NON_EVM = "non_evm"
    CUSTOM = "custom"

class NetworkType(str, Enum):
    MAINNET = "mainnet"
    TESTNET = "testnet"
    DEVNET = "devnet"

class TokenStandard(str, Enum):
    ERC20 = "ERC20"
    BEP20 = "BEP20"
    TRC20 = "TRC20"
    SPL = "SPL"
    NATIVE = "NATIVE"

class TradingType(str, Enum):
    SPOT = "spot"
    FUTURES = "futures"
    OPTIONS = "options"
    MARGIN = "margin"
    ETF = "etf"

# Pydantic Models

# Token Listing Models
class TokenListingRequest(BaseModel):
    token_symbol: str = Field(..., min_length=1, max_length=10)
    token_name: str = Field(..., min_length=1, max_length=100)
    token_standard: TokenStandard
    blockchain_id: str
    contract_address: Optional[str] = None
    decimals: int = Field(..., ge=0, le=18)
    total_supply: Optional[Decimal] = Field(None, gt=0)
    description: Optional[str] = None
    website: Optional[str] = None
    whitepaper_url: Optional[str] = None
    logo_url: Optional[str] = None
    is_iou: bool = False
    auto_create_liquidity_pool: bool = True
    initial_liquidity_usdt: Optional[Decimal] = Field(None, gt=0)

class TokenUpdateRequest(BaseModel):
    status: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None

# Trading Pair Models
class TradingPairCreateRequest(BaseModel):
    base_asset: str = Field(..., min_length=1, max_length=10)
    quote_asset: str = Field(..., min_length=1, max_length=10)
    trading_type: TradingType
    min_order_size: Decimal = Field(..., gt=0)
    max_order_size: Optional[Decimal] = Field(None, gt=0)
    min_price: Decimal = Field(..., gt=0)
    max_price: Optional[Decimal] = Field(None, gt=0)
    price_precision: int = Field(..., ge=0, le=8)
    quantity_precision: int = Field(..., ge=0, le=8)
    maker_fee: Decimal = Field(default=Decimal("0.001"), ge=0, le=1)
    taker_fee: Decimal = Field(default=Decimal("0.001"), ge=0, le=1)
    auto_provide_liquidity: bool = True
    virtual_liquidity_percentage: Decimal = Field(default=Decimal("0.7"), ge=0, le=1)

# Blockchain Integration Models
class BlockchainIntegrationRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    symbol: str = Field(..., min_length=1, max_length=10)
    blockchain_type: BlockchainType
    network_type: NetworkType
    chain_id: Optional[int] = None
    rpc_url: str
    ws_url: Optional[str] = None
    explorer_url: Optional[str] = None
    consensus_mechanism: str
    block_time: int = Field(..., gt=0)
    native_currency: str
    description: Optional[str] = None

class NonEVMBlockchainRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    symbol: str = Field(..., min_length=1, max_length=10)
    blockchain_type: str  # pi_network, ton, cosmos, polkadot, etc.
    api_endpoint: str
    websocket_endpoint: Optional[str] = None
    explorer_url: Optional[str] = None
    native_currency: str
    supports_smart_contracts: bool = False
    custom_integration_config: Optional[Dict[str, Any]] = None
    description: Optional[str] = None

# Liquidity Management Models
class LiquidityPoolCreateRequest(BaseModel):
    base_asset: str
    quote_asset: str
    initial_base_amount: Decimal = Field(..., gt=0)
    initial_quote_amount: Decimal = Field(..., gt=0)
    virtual_base_percentage: Decimal = Field(default=Decimal("0.7"), ge=0, le=1)
    virtual_quote_percentage: Decimal = Field(default=Decimal("0.7"), ge=0, le=1)
    fee_rate: Decimal = Field(default=Decimal("0.003"), ge=0, le=1)
    is_public: bool = True

class VirtualReserveAdjustment(BaseModel):
    asset_symbol: str
    adjustment_amount: Decimal
    adjustment_type: str  # add, remove
    reason: str

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global db_pool, redis_client, http_client
    
    logger.info("Starting Comprehensive Admin Service...")
    
    # Initialize database pool
    db_pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=10,
        max_size=50,
        command_timeout=60
    )
    logger.info("Database pool created")
    
    # Initialize Redis
    redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
    logger.info("Redis client connected")
    
    # Initialize HTTP client
    http_client = httpx.AsyncClient(timeout=30.0)
    logger.info("HTTP client initialized")
    
    logger.info("Comprehensive Admin Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Comprehensive Admin Service...")
    
    if db_pool:
        await db_pool.close()
    if redis_client:
        await redis_client.close()
    if http_client:
        await http_client.aclose()
    
    logger.info("Comprehensive Admin Service shut down")

# Initialize FastAPI app
app = FastAPI(
    title="TigerEx Comprehensive Admin Service",
    description="Central admin service for managing all exchange features",
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

# Helper functions
async def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify admin authentication token"""
    # TODO: Implement proper JWT verification
    token = credentials.credentials
    # For now, accept any token (implement proper auth in production)
    return {"admin_id": "admin_001", "permissions": ["*"]}

# Health Check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "comprehensive-admin-service",
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# TOKEN LISTING MANAGEMENT
# ============================================================================

@app.post("/api/admin/tokens/list", status_code=201)
async def list_new_token(
    request: TokenListingRequest,
    admin: dict = Depends(verify_admin_token)
):
    """
    List a new token or coin on the exchange
    - Creates token entry in database
    - Optionally creates IOU token
    - Automatically creates liquidity pool if requested
    - Provisions virtual liquidity
    """
    try:
        async with db_pool.acquire() as conn:
            # Check if token already exists
            existing = await conn.fetchrow("""
                SELECT * FROM tokens WHERE symbol = $1
            """, request.token_symbol)
            
            if existing:
                raise HTTPException(status_code=400, detail="Token already listed")
            
            # Create token entry
            token_id = f"TOKEN_{request.token_symbol}_{int(datetime.now().timestamp())}"
            
            token = await conn.fetchrow("""
                INSERT INTO tokens (
                    token_id, symbol, name, token_standard, blockchain_id,
                    contract_address, decimals, total_supply, description,
                    website, whitepaper_url, logo_url, is_active, created_by
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                RETURNING *
            """, token_id, request.token_symbol, request.token_name,
            request.token_standard.value, request.blockchain_id,
            request.contract_address, request.decimals, request.total_supply,
            request.description, request.website, request.whitepaper_url,
            request.logo_url, True, admin['admin_id'])
            
            result = {"token": dict(token)}
            
            # Create IOU token if requested
            if request.is_iou:
                iou_response = await http_client.post(
                    f"{VIRTUAL_LIQUIDITY_SERVICE_URL}/api/iou-tokens",
                    json={
                        "token_symbol": f"{request.token_symbol}-IOU",
                        "token_name": f"{request.token_name} IOU",
                        "underlying_asset": request.token_symbol,
                        "total_supply": str(request.total_supply) if request.total_supply else "1000000",
                        "conversion_ratio": "1.0",
                        "is_convertible": False,
                        "description": f"IOU token for {request.token_name}"
                    }
                )
                result["iou_token"] = iou_response.json()
            
            # Create liquidity pool if requested
            if request.auto_create_liquidity_pool and request.initial_liquidity_usdt:
                pool_response = await http_client.post(
                    f"{VIRTUAL_LIQUIDITY_SERVICE_URL}/api/pools",
                    json={
                        "pool_name": f"{request.token_symbol}/USDT Pool",
                        "pool_type": "amm",
                        "base_asset": request.token_symbol,
                        "quote_asset": "USDT",
                        "base_reserve": "0",
                        "quote_reserve": str(request.initial_liquidity_usdt),
                        "virtual_base_liquidity": "0",
                        "virtual_quote_liquidity": str(float(request.initial_liquidity_usdt) * 0.7),
                        "fee_rate": "0.003",
                        "is_public": True
                    }
                )
                result["liquidity_pool"] = pool_response.json()
            
            logger.info(f"Listed new token: {request.token_symbol}", admin_id=admin['admin_id'])
            return result
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing token: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/tokens")
async def get_all_tokens(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    admin: dict = Depends(verify_admin_token)
):
    """Get all listed tokens"""
    try:
        async with db_pool.acquire() as conn:
            query = "SELECT * FROM tokens WHERE 1=1"
            params = []
            
            if is_active is not None:
                query += " AND is_active = $1"
                params.append(is_active)
            
            query += f" ORDER BY created_at DESC OFFSET ${len(params) + 1} LIMIT ${len(params) + 2}"
            params.extend([skip, limit])
            
            tokens = await conn.fetch(query, *params)
            total = await conn.fetchval("SELECT COUNT(*) FROM tokens")
            
            return {
                "total": total,
                "tokens": [dict(t) for t in tokens]
            }
            
    except Exception as e:
        logger.error(f"Error fetching tokens: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/admin/tokens/{token_symbol}")
async def update_token(
    token_symbol: str,
    update: TokenUpdateRequest,
    admin: dict = Depends(verify_admin_token)
):
    """Update token information"""
    try:
        async with db_pool.acquire() as conn:
            updates = []
            params = []
            param_count = 0
            
            for field, value in update.dict(exclude_unset=True).items():
                if value is not None:
                    param_count += 1
                    updates.append(f"{field} = ${param_count}")
                    params.append(value)
            
            if not updates:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            param_count += 1
            params.append(token_symbol)
            
            query = f"""
                UPDATE tokens
                SET {', '.join(updates)}, updated_at = NOW()
                WHERE symbol = ${param_count}
                RETURNING *
            """
            
            result = await conn.fetchrow(query, *params)
            
            if not result:
                raise HTTPException(status_code=404, detail="Token not found")
            
            logger.info(f"Updated token: {token_symbol}", admin_id=admin['admin_id'])
            return dict(result)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating token: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/admin/tokens/{token_symbol}")
async def delist_token(
    token_symbol: str,
    admin: dict = Depends(verify_admin_token)
):
    """Delist a token (soft delete)"""
    try:
        async with db_pool.acquire() as conn:
            result = await conn.fetchrow("""
                UPDATE tokens
                SET is_active = false, updated_at = NOW()
                WHERE symbol = $1
                RETURNING *
            """, token_symbol)
            
            if not result:
                raise HTTPException(status_code=404, detail="Token not found")
            
            logger.info(f"Delisted token: {token_symbol}", admin_id=admin['admin_id'])
            return {"message": "Token delisted successfully", "token": dict(result)}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error delisting token: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TRADING PAIR MANAGEMENT
# ============================================================================

@app.post("/api/admin/trading-pairs", status_code=201)
async def create_trading_pair(
    request: TradingPairCreateRequest,
    admin: dict = Depends(verify_admin_token)
):
    """
    Create a new trading pair
    - Supports all trading types (Spot, Futures, Options, Margin, ETF)
    - Automatically provisions virtual liquidity if requested
    """
    try:
        async with db_pool.acquire() as conn:
            symbol = f"{request.base_asset}{request.quote_asset}"
            
            # Check if pair already exists
            existing = await conn.fetchrow("""
                SELECT * FROM trading_pairs WHERE symbol = $1
            """, symbol)
            
            if existing:
                raise HTTPException(status_code=400, detail="Trading pair already exists")
            
            # Create trading pair
            pair = await conn.fetchrow("""
                INSERT INTO trading_pairs (
                    symbol, base_asset, quote_asset, status,
                    min_quantity, max_quantity, step_size,
                    min_price, max_price, tick_size,
                    maker_fee, taker_fee,
                    is_spot_enabled, is_margin_enabled, is_futures_enabled, is_options_enabled,
                    is_active
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
                RETURNING *
            """, symbol, request.base_asset, request.quote_asset, 'TRADING',
            request.min_order_size, request.max_order_size, Decimal("0.00000001"),
            request.min_price, request.max_price, Decimal("0.00000001"),
            request.maker_fee, request.taker_fee,
            request.trading_type == TradingType.SPOT,
            request.trading_type == TradingType.MARGIN,
            request.trading_type == TradingType.FUTURES,
            request.trading_type == TradingType.OPTIONS,
            True)
            
            result = {"trading_pair": dict(pair)}
            
            # Provide virtual liquidity if requested
            if request.auto_provide_liquidity:
                # Create liquidity pool
                pool_response = await http_client.post(
                    f"{VIRTUAL_LIQUIDITY_SERVICE_URL}/api/pools",
                    json={
                        "pool_name": f"{symbol} Liquidity Pool",
                        "pool_type": "amm",
                        "base_asset": request.base_asset,
                        "quote_asset": request.quote_asset,
                        "base_reserve": "0",
                        "quote_reserve": "0",
                        "virtual_base_liquidity": "0",
                        "virtual_quote_liquidity": "0",
                        "fee_rate": str(request.maker_fee),
                        "is_public": True
                    }
                )
                result["liquidity_pool"] = pool_response.json()
            
            logger.info(f"Created trading pair: {symbol}", admin_id=admin['admin_id'])
            return result
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating trading pair: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/trading-pairs")
async def get_trading_pairs(
    trading_type: Optional[TradingType] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    admin: dict = Depends(verify_admin_token)
):
    """Get all trading pairs"""
    try:
        async with db_pool.acquire() as conn:
            query = "SELECT * FROM trading_pairs WHERE 1=1"
            params = []
            
            if is_active is not None:
                query += " AND is_active = $1"
                params.append(is_active)
            
            if trading_type:
                if trading_type == TradingType.SPOT:
                    query += " AND is_spot_enabled = true"
                elif trading_type == TradingType.MARGIN:
                    query += " AND is_margin_enabled = true"
                elif trading_type == TradingType.FUTURES:
                    query += " AND is_futures_enabled = true"
                elif trading_type == TradingType.OPTIONS:
                    query += " AND is_options_enabled = true"
            
            query += f" ORDER BY created_at DESC OFFSET ${len(params) + 1} LIMIT ${len(params) + 2}"
            params.extend([skip, limit])
            
            pairs = await conn.fetch(query, *params)
            total = await conn.fetchval("SELECT COUNT(*) FROM trading_pairs")
            
            return {
                "total": total,
                "trading_pairs": [dict(p) for p in pairs]
            }
            
    except Exception as e:
        logger.error(f"Error fetching trading pairs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# BLOCKCHAIN INTEGRATION
# ============================================================================

@app.post("/api/admin/blockchains/evm", status_code=201)
async def integrate_evm_blockchain(
    request: BlockchainIntegrationRequest,
    admin: dict = Depends(verify_admin_token)
):
    """
    Integrate a new EVM-compatible blockchain
    - Validates RPC connectivity
    - Stores blockchain configuration
    - Sets up monitoring
    """
    try:
        # Validate RPC connection
        try:
            w3 = Web3(Web3.HTTPProvider(request.rpc_url))
            if not w3.is_connected():
                raise HTTPException(status_code=400, detail="Cannot connect to RPC endpoint")
            
            # Get chain ID from network
            network_chain_id = w3.eth.chain_id
            if request.chain_id and network_chain_id != request.chain_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Chain ID mismatch: expected {request.chain_id}, got {network_chain_id}"
                )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"RPC validation failed: {str(e)}")
        
        async with db_pool.acquire() as conn:
            blockchain_id = f"{request.symbol}_MAINNET" if request.network_type == NetworkType.MAINNET else f"{request.symbol}_TESTNET"
            
            # Check if blockchain already exists
            existing = await conn.fetchrow("""
                SELECT * FROM custom_blockchains WHERE blockchain_id = $1
            """, blockchain_id)
            
            if existing:
                raise HTTPException(status_code=400, detail="Blockchain already integrated")
            
            # Create blockchain entry
            blockchain = await conn.fetchrow("""
                INSERT INTO custom_blockchains (
                    blockchain_id, name, symbol, description,
                    chain_id, network_type, consensus_mechanism,
                    block_time, rpc_url, ws_url, explorer_url,
                    deployment_status, created_by
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                RETURNING *
            """, blockchain_id, request.name, request.symbol, request.description,
            network_chain_id, request.network_type.value, request.consensus_mechanism,
            request.block_time, request.rpc_url, request.ws_url, request.explorer_url,
            'deployed', admin['admin_id'])
            
            logger.info(f"Integrated EVM blockchain: {blockchain_id}", admin_id=admin['admin_id'])
            return dict(blockchain)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error integrating EVM blockchain: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/blockchains/non-evm", status_code=201)
async def integrate_non_evm_blockchain(
    request: NonEVMBlockchainRequest,
    admin: dict = Depends(verify_admin_token)
):
    """
    Integrate a non-EVM blockchain (Pi Network, TON, Cosmos, Polkadot, etc.)
    - Stores custom integration configuration
    - Sets up custom adapters
    """
    try:
        async with db_pool.acquire() as conn:
            blockchain_id = f"{request.symbol}_MAINNET"
            
            # Check if blockchain already exists
            existing = await conn.fetchrow("""
                SELECT * FROM custom_blockchains WHERE blockchain_id = $1
            """, blockchain_id)
            
            if existing:
                raise HTTPException(status_code=400, detail="Blockchain already integrated")
            
            # Create blockchain entry with custom config
            blockchain = await conn.fetchrow("""
                INSERT INTO custom_blockchains (
                    blockchain_id, name, symbol, description,
                    chain_id, network_type, consensus_mechanism,
                    block_time, rpc_url, ws_url, explorer_url,
                    deployment_status, deployment_config, created_by
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                RETURNING *
            """, blockchain_id, request.name, request.symbol, request.description,
            0, 'mainnet', 'Custom', 5,
            request.api_endpoint, request.websocket_endpoint, request.explorer_url,
            'deployed', json.dumps({
                "blockchain_type": request.blockchain_type,
                "supports_smart_contracts": request.supports_smart_contracts,
                "custom_config": request.custom_integration_config or {}
            }), admin['admin_id'])
            
            logger.info(f"Integrated non-EVM blockchain: {blockchain_id}", admin_id=admin['admin_id'])
            return dict(blockchain)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error integrating non-EVM blockchain: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/blockchains")
async def get_blockchains(
    network_type: Optional[NetworkType] = None,
    skip: int = 0,
    limit: int = 100,
    admin: dict = Depends(verify_admin_token)
):
    """Get all integrated blockchains"""
    try:
        async with db_pool.acquire() as conn:
            query = "SELECT * FROM custom_blockchains WHERE 1=1"
            params = []
            
            if network_type:
                query += " AND network_type = $1"
                params.append(network_type.value)
            
            query += f" ORDER BY created_at DESC OFFSET ${len(params) + 1} LIMIT ${len(params) + 2}"
            params.extend([skip, limit])
            
            blockchains = await conn.fetch(query, *params)
            total = await conn.fetchval("SELECT COUNT(*) FROM custom_blockchains")
            
            return {
                "total": total,
                "blockchains": [dict(b) for b in blockchains]
            }
            
    except Exception as e:
        logger.error(f"Error fetching blockchains: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# LIQUIDITY POOL MANAGEMENT
# ============================================================================

@app.post("/api/admin/liquidity-pools", status_code=201)
async def create_liquidity_pool(
    request: LiquidityPoolCreateRequest,
    admin: dict = Depends(verify_admin_token)
):
    """
    Create a new liquidity pool for a token
    - Provisions virtual liquidity from reserves
    - Sets up AMM parameters
    """
    try:
        # Calculate virtual liquidity amounts
        virtual_base = float(request.initial_base_amount) * float(request.virtual_base_percentage)
        virtual_quote = float(request.initial_quote_amount) * float(request.virtual_quote_percentage)
        
        # Create pool via virtual liquidity service
        pool_response = await http_client.post(
            f"{VIRTUAL_LIQUIDITY_SERVICE_URL}/api/pools",
            json={
                "pool_name": f"{request.base_asset}/{request.quote_asset} Pool",
                "pool_type": "amm",
                "base_asset": request.base_asset,
                "quote_asset": request.quote_asset,
                "base_reserve": str(request.initial_base_amount),
                "quote_reserve": str(request.initial_quote_amount),
                "virtual_base_liquidity": str(virtual_base),
                "virtual_quote_liquidity": str(virtual_quote),
                "fee_rate": str(request.fee_rate),
                "is_public": request.is_public
            }
        )
        
        pool = pool_response.json()
        
        # Allocate virtual liquidity from reserves
        if virtual_quote > 0:
            # Allocate USDT/USDC from virtual reserves
            await http_client.post(
                f"{VIRTUAL_LIQUIDITY_SERVICE_URL}/api/allocations",
                json={
                    "reserve_id": 1,  # USDT reserve
                    "pool_id": pool['id'],
                    "allocated_amount": str(virtual_quote),
                    "asset_symbol": request.quote_asset
                }
            )
        
        logger.info(f"Created liquidity pool: {request.base_asset}/{request.quote_asset}", 
                   admin_id=admin['admin_id'])
        return pool
        
    except Exception as e:
        logger.error(f"Error creating liquidity pool: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/liquidity-pools")
async def get_liquidity_pools(
    admin: dict = Depends(verify_admin_token)
):
    """Get all liquidity pools"""
    try:
        response = await http_client.get(f"{VIRTUAL_LIQUIDITY_SERVICE_URL}/api/pools")
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching liquidity pools: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# VIRTUAL RESERVE MANAGEMENT
# ============================================================================

@app.get("/api/admin/virtual-reserves")
async def get_virtual_reserves(
    admin: dict = Depends(verify_admin_token)
):
    """Get all virtual asset reserves"""
    try:
        response = await http_client.get(f"{VIRTUAL_LIQUIDITY_SERVICE_URL}/api/reserves")
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching virtual reserves: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/virtual-reserves/adjust")
async def adjust_virtual_reserve(
    adjustment: VirtualReserveAdjustment,
    admin: dict = Depends(verify_admin_token)
):
    """Adjust virtual reserve amounts"""
    try:
        # Get reserve by asset symbol
        reserves_response = await http_client.get(
            f"{VIRTUAL_LIQUIDITY_SERVICE_URL}/api/reserves",
            params={"asset_symbol": adjustment.asset_symbol}
        )
        reserves = reserves_response.json()
        
        if not reserves['reserves']:
            raise HTTPException(status_code=404, detail="Reserve not found")
        
        reserve = reserves['reserves'][0]
        
        # Perform rebalancing
        rebalance_response = await http_client.post(
            f"{VIRTUAL_LIQUIDITY_SERVICE_URL}/api/reserves/{reserve['reserve_id']}/rebalance",
            json={
                "reserve_id": reserve['id'],
                "rebalance_type": "manual",
                "amount_to_add": str(adjustment.adjustment_amount) if adjustment.adjustment_type == "add" else None,
                "amount_to_remove": str(adjustment.adjustment_amount) if adjustment.adjustment_type == "remove" else None,
                "trigger_reason": adjustment.reason,
                "notes": f"Manual adjustment by admin {admin['admin_id']}"
            }
        )
        
        logger.info(f"Adjusted virtual reserve: {adjustment.asset_symbol}", 
                   admin_id=admin['admin_id'],
                   adjustment_type=adjustment.adjustment_type,
                   amount=float(adjustment.adjustment_amount))
        
        return rebalance_response.json()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adjusting virtual reserve: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# IOU TOKEN MANAGEMENT
# ============================================================================

@app.get("/api/admin/iou-tokens")
async def get_iou_tokens(
    admin: dict = Depends(verify_admin_token)
):
    """Get all IOU tokens"""
    try:
        response = await http_client.get(f"{VIRTUAL_LIQUIDITY_SERVICE_URL}/api/iou-tokens")
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching IOU tokens: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/admin/iou-tokens/{iou_id}/enable-conversion")
async def enable_iou_conversion(
    iou_id: str,
    conversion_start: datetime,
    conversion_end: datetime,
    admin: dict = Depends(verify_admin_token)
):
    """Enable conversion for an IOU token"""
    try:
        async with db_pool.acquire() as conn:
            result = await conn.fetchrow("""
                UPDATE iou_tokens
                SET is_convertible = true,
                    conversion_start_date = $1,
                    conversion_end_date = $2,
                    status = 'converting',
                    updated_at = NOW()
                WHERE iou_id = $3
                RETURNING *
            """, conversion_start, conversion_end, iou_id)
            
            if not result:
                raise HTTPException(status_code=404, detail="IOU token not found")
            
            logger.info(f"Enabled conversion for IOU token: {iou_id}", admin_id=admin['admin_id'])
            return dict(result)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enabling IOU conversion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ANALYTICS & MONITORING
# ============================================================================

@app.get("/api/admin/analytics/overview")
async def get_admin_analytics_overview(
    admin: dict = Depends(verify_admin_token)
):
    """Get comprehensive analytics overview"""
    try:
        async with db_pool.acquire() as conn:
            # Token metrics
            token_metrics = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_tokens,
                    COUNT(*) FILTER (WHERE is_active = true) as active_tokens
                FROM tokens
            """)
            
            # Trading pair metrics
            pair_metrics = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_pairs,
                    COUNT(*) FILTER (WHERE is_active = true) as active_pairs,
                    COUNT(*) FILTER (WHERE is_spot_enabled = true) as spot_pairs,
                    COUNT(*) FILTER (WHERE is_futures_enabled = true) as futures_pairs,
                    COUNT(*) FILTER (WHERE is_margin_enabled = true) as margin_pairs
                FROM trading_pairs
            """)
            
            # Blockchain metrics
            blockchain_metrics = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_blockchains,
                    COUNT(*) FILTER (WHERE deployment_status = 'deployed') as deployed_blockchains
                FROM custom_blockchains
            """)
        
        # Get virtual liquidity metrics
        liquidity_response = await http_client.get(
            f"{VIRTUAL_LIQUIDITY_SERVICE_URL}/api/analytics/overview"
        )
        liquidity_metrics = liquidity_response.json()
        
        return {
            "tokens": dict(token_metrics),
            "trading_pairs": dict(pair_metrics),
            "blockchains": dict(blockchain_metrics),
            "liquidity": liquidity_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/activity-log")
async def get_admin_activity_log(
    skip: int = 0,
    limit: int = 100,
    admin: dict = Depends(verify_admin_token)
):
    """Get admin activity log"""
    try:
        async with db_pool.acquire() as conn:
            activities = await conn.fetch("""
                SELECT * FROM admin_activity_log
                ORDER BY created_at DESC
                OFFSET $1 LIMIT $2
            """, skip, limit)
            
            total = await conn.fetchval("SELECT COUNT(*) FROM admin_activity_log")
            
            return {
                "total": total,
                "activities": [dict(a) for a in activities]
            }
            
    except Exception as e:
        logger.error(f"Error fetching activity log: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8160)