#!/usr/bin/env python3
"""
Cross-Chain DEX Aggregator Service
Advanced cross-chain DEX aggregation with optimal routing and bridge integration
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
import uuid
import logging
import os
import asyncio
import aioredis
import json
import aiohttp
from web3 import Web3
from decimal import Decimal
import numpy as np

# FastAPI app
app = FastAPI(
    title="TigerEx Cross-Chain DEX Aggregator",
    description="Advanced cross-chain DEX aggregation with optimal routing and bridge integration",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/tigerex_dex")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supported chains and DEXs
SUPPORTED_CHAINS = {
    "ethereum": {
        "chain_id": 1,
        "rpc_url": "https://mainnet.infura.io/v3/your-key",
        "native_token": "ETH",
        "dexs": ["uniswap_v3", "uniswap_v2", "sushiswap", "curve", "balancer", "1inch"]
    },
    "bsc": {
        "chain_id": 56,
        "rpc_url": "https://bsc-dataseed.binance.org/",
        "native_token": "BNB",
        "dexs": ["pancakeswap_v3", "pancakeswap_v2", "biswap", "apeswap", "mdex"]
    },
    "polygon": {
        "chain_id": 137,
        "rpc_url": "https://polygon-rpc.com/",
        "native_token": "MATIC",
        "dexs": ["quickswap", "sushiswap", "curve", "balancer", "dodo"]
    },
    "arbitrum": {
        "chain_id": 42161,
        "rpc_url": "https://arb1.arbitrum.io/rpc",
        "native_token": "ETH",
        "dexs": ["uniswap_v3", "sushiswap", "curve", "balancer", "camelot"]
    },
    "optimism": {
        "chain_id": 10,
        "rpc_url": "https://mainnet.optimism.io",
        "native_token": "ETH",
        "dexs": ["uniswap_v3", "curve", "velodrome", "beethoven_x"]
    },
    "avalanche": {
        "chain_id": 43114,
        "rpc_url": "https://api.avax.network/ext/bc/C/rpc",
        "native_token": "AVAX",
        "dexs": ["traderjoe", "pangolin", "curve", "platypus"]
    },
    "fantom": {
        "chain_id": 250,
        "rpc_url": "https://rpc.ftm.tools/",
        "native_token": "FTM",
        "dexs": ["spookyswap", "spiritswap", "curve", "beethoven_x"]
    },
    "solana": {
        "chain_id": "solana",
        "rpc_url": "https://api.mainnet-beta.solana.com",
        "native_token": "SOL",
        "dexs": ["jupiter", "raydium", "orca", "serum"]
    }
}

# Bridge protocols
BRIDGE_PROTOCOLS = {
    "multichain": {
        "supported_chains": ["ethereum", "bsc", "polygon", "arbitrum", "optimism", "avalanche", "fantom"],
        "fee_percentage": 0.1,
        "min_amount": 10,
        "max_amount": 1000000
    },
    "hop": {
        "supported_chains": ["ethereum", "polygon", "arbitrum", "optimism"],
        "fee_percentage": 0.04,
        "min_amount": 1,
        "max_amount": 100000
    },
    "synapse": {
        "supported_chains": ["ethereum", "bsc", "polygon", "arbitrum", "optimism", "avalanche"],
        "fee_percentage": 0.05,
        "min_amount": 5,
        "max_amount": 500000
    },
    "stargate": {
        "supported_chains": ["ethereum", "bsc", "polygon", "arbitrum", "optimism", "avalanche", "fantom"],
        "fee_percentage": 0.06,
        "min_amount": 1,
        "max_amount": 1000000
    }
}

# Database Models
class DEXQuote(Base):
    __tablename__ = "dex_quotes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Trade details
    chain = Column(String, nullable=False)
    dex = Column(String, nullable=False)
    token_in = Column(String, nullable=False)
    token_out = Column(String, nullable=False)
    amount_in = Column(String, nullable=False)  # Use string for precision
    amount_out = Column(String, nullable=False)
    
    # Pricing
    price = Column(Float, nullable=False)
    price_impact = Column(Float, default=0.0)
    gas_estimate = Column(String, default="0")
    gas_price = Column(String, default="0")
    
    # Route details
    route = Column(JSON)
    pools = Column(JSON)
    
    # Metadata
    slippage_tolerance = Column(Float, default=0.5)
    deadline = Column(Integer, default=1200)  # 20 minutes
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

class CrossChainRoute(Base):
    __tablename__ = "cross_chain_routes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Source and destination
    source_chain = Column(String, nullable=False)
    destination_chain = Column(String, nullable=False)
    token_in = Column(String, nullable=False)
    token_out = Column(String, nullable=False)
    amount_in = Column(String, nullable=False)
    
    # Route steps
    steps = Column(JSON, nullable=False)  # Array of route steps
    
    # Costs and estimates
    total_gas_cost = Column(String, default="0")
    bridge_fee = Column(String, default="0")
    total_fee = Column(String, default="0")
    estimated_time = Column(Integer, default=600)  # seconds
    
    # Output
    amount_out = Column(String, nullable=False)
    minimum_received = Column(String, nullable=False)
    
    # Route quality
    efficiency_score = Column(Float, default=0.0)  # 0-100
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

class DEXTransaction(Base):
    __tablename__ = "dex_transactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_address = Column(String, nullable=False)
    
    # Transaction details
    chain = Column(String, nullable=False)
    tx_hash = Column(String, unique=True)
    status = Column(String, default="pending")  # pending, confirmed, failed
    
    # Trade details
    token_in = Column(String, nullable=False)
    token_out = Column(String, nullable=False)
    amount_in = Column(String, nullable=False)
    amount_out = Column(String)
    actual_amount_out = Column(String)
    
    # Route used
    route_id = Column(String)
    dex_used = Column(String)
    
    # Costs
    gas_used = Column(String)
    gas_price = Column(String)
    total_cost = Column(String)
    
    # Performance
    slippage = Column(Float)
    execution_time = Column(Integer)  # seconds
    
    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime)

class LiquidityPool(Base):
    __tablename__ = "liquidity_pools"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Pool identification
    chain = Column(String, nullable=False)
    dex = Column(String, nullable=False)
    pool_address = Column(String, nullable=False)
    
    # Tokens
    token0 = Column(String, nullable=False)
    token1 = Column(String, nullable=False)
    
    # Pool data
    reserve0 = Column(String, default="0")
    reserve1 = Column(String, default="0")
    total_supply = Column(String, default="0")
    
    # Metrics
    tvl_usd = Column(Float, default=0.0)
    volume_24h = Column(Float, default=0.0)
    fees_24h = Column(Float, default=0.0)
    apr = Column(Float, default=0.0)
    
    # Pool info
    fee_tier = Column(Float, default=0.3)  # 0.3%
    is_stable = Column(Boolean, default=False)
    
    last_updated = Column(DateTime, default=datetime.utcnow)

class BridgeTransaction(Base):
    __tablename__ = "bridge_transactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_address = Column(String, nullable=False)
    
    # Bridge details
    bridge_protocol = Column(String, nullable=False)
    source_chain = Column(String, nullable=False)
    destination_chain = Column(String, nullable=False)
    
    # Transaction hashes
    source_tx_hash = Column(String)
    destination_tx_hash = Column(String)
    
    # Token details
    token = Column(String, nullable=False)
    amount = Column(String, nullable=False)
    
    # Status tracking
    status = Column(String, default="initiated")  # initiated, confirmed, bridging, completed, failed
    
    # Costs and timing
    bridge_fee = Column(String, default="0")
    estimated_time = Column(Integer, default=600)
    actual_time = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class QuoteRequest(BaseModel):
    chain: str
    token_in: str
    token_out: str
    amount_in: str
    slippage_tolerance: float = 0.5
    dexs: Optional[List[str]] = None

class CrossChainQuoteRequest(BaseModel):
    source_chain: str
    destination_chain: str
    token_in: str
    token_out: str
    amount_in: str
    slippage_tolerance: float = 0.5
    max_hops: int = 3

class SwapRequest(BaseModel):
    quote_id: str
    user_address: str
    deadline: Optional[int] = 1200

class CrossChainSwapRequest(BaseModel):
    route_id: str
    user_address: str
    destination_address: Optional[str] = None

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions
async def get_redis():
    return await aioredis.from_url(REDIS_URL)

class DEXIntegration:
    """Base class for DEX integrations"""
    
    def __init__(self, chain: str, dex: str):
        self.chain = chain
        self.dex = dex
        self.w3 = Web3(Web3.HTTPProvider(SUPPORTED_CHAINS[chain]["rpc_url"]))
    
    async def get_quote(self, token_in: str, token_out: str, amount_in: str) -> Dict[str, Any]:
        """Get quote from DEX"""
        # Mock implementation - integrate with actual DEX APIs
        return {
            "amount_out": str(int(float(amount_in) * 0.95)),  # Mock 5% slippage
            "price": 0.95,
            "price_impact": 0.05,
            "gas_estimate": "150000",
            "route": [token_in, token_out],
            "pools": [f"{token_in}-{token_out}"]
        }
    
    async def execute_swap(self, quote: Dict[str, Any], user_address: str) -> str:
        """Execute swap transaction"""
        # Mock transaction hash
        return f"0x{uuid.uuid4().hex}"

class UniswapV3Integration(DEXIntegration):
    """Uniswap V3 integration"""
    
    async def get_quote(self, token_in: str, token_out: str, amount_in: str) -> Dict[str, Any]:
        # Integrate with Uniswap V3 quoter contract
        return await super().get_quote(token_in, token_out, amount_in)

class PancakeSwapIntegration(DEXIntegration):
    """PancakeSwap integration"""
    
    async def get_quote(self, token_in: str, token_out: str, amount_in: str) -> Dict[str, Any]:
        # Integrate with PancakeSwap router
        return await super().get_quote(token_in, token_out, amount_in)

class JupiterIntegration:
    """Jupiter (Solana) integration"""
    
    def __init__(self):
        self.base_url = "https://quote-api.jup.ag/v6"
    
    async def get_quote(self, token_in: str, token_out: str, amount_in: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            params = {
                "inputMint": token_in,
                "outputMint": token_out,
                "amount": amount_in,
                "slippageBps": 50  # 0.5%
            }
            
            async with session.get(f"{self.base_url}/quote", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "amount_out": data.get("outAmount", "0"),
                        "price": float(data.get("outAmount", 0)) / float(amount_in),
                        "price_impact": data.get("priceImpactPct", 0),
                        "route": data.get("routePlan", []),
                        "gas_estimate": "5000"  # SOL uses compute units
                    }
                else:
                    return await super().get_quote(token_in, token_out, amount_in)

def get_dex_integration(chain: str, dex: str):
    """Factory function to get DEX integration"""
    if chain == "solana" and dex == "jupiter":
        return JupiterIntegration()
    elif dex == "uniswap_v3":
        return UniswapV3Integration(chain, dex)
    elif dex in ["pancakeswap_v2", "pancakeswap_v3"]:
        return PancakeSwapIntegration(chain, dex)
    else:
        return DEXIntegration(chain, dex)

async def get_all_quotes(chain: str, token_in: str, token_out: str, amount_in: str, dexs: List[str] = None) -> List[Dict[str, Any]]:
    """Get quotes from all available DEXs"""
    if not dexs:
        dexs = SUPPORTED_CHAINS[chain]["dexs"]
    
    quotes = []
    tasks = []
    
    for dex in dexs:
        integration = get_dex_integration(chain, dex)
        task = integration.get_quote(token_in, token_out, amount_in)
        tasks.append((dex, task))
    
    results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
    
    for (dex, _), result in zip(tasks, results):
        if not isinstance(result, Exception):
            result["dex"] = dex
            result["chain"] = chain
            quotes.append(result)
    
    return quotes

async def find_cross_chain_routes(
    source_chain: str,
    destination_chain: str,
    token_in: str,
    token_out: str,
    amount_in: str,
    max_hops: int = 3
) -> List[Dict[str, Any]]:
    """Find optimal cross-chain routes"""
    routes = []
    
    # Direct bridge route (if tokens are the same)
    if token_in == token_out:
        for bridge_name, bridge_config in BRIDGE_PROTOCOLS.items():
            if source_chain in bridge_config["supported_chains"] and destination_chain in bridge_config["supported_chains"]:
                bridge_fee = float(amount_in) * bridge_config["fee_percentage"] / 100
                amount_out = float(amount_in) - bridge_fee
                
                route = {
                    "steps": [
                        {
                            "type": "bridge",
                            "protocol": bridge_name,
                            "from_chain": source_chain,
                            "to_chain": destination_chain,
                            "token": token_in,
                            "amount_in": amount_in,
                            "amount_out": str(amount_out),
                            "fee": str(bridge_fee)
                        }
                    ],
                    "total_amount_out": str(amount_out),
                    "total_fee": str(bridge_fee),
                    "estimated_time": 600,
                    "efficiency_score": 95.0
                }
                routes.append(route)
    
    # Swap + Bridge + Swap routes
    if len(routes) < 5:  # Generate more complex routes
        # Get quotes on source chain
        source_quotes = await get_all_quotes(source_chain, token_in, token_out, amount_in)
        
        # Get quotes on destination chain
        dest_quotes = await get_all_quotes(destination_chain, token_in, token_out, amount_in)
        
        # Create hybrid routes
        for bridge_name, bridge_config in BRIDGE_PROTOCOLS.items():
            if source_chain in bridge_config["supported_chains"] and destination_chain in bridge_config["supported_chains"]:
                # Route: Swap on source -> Bridge -> Swap on destination
                if source_quotes and dest_quotes:
                    best_source_quote = max(source_quotes, key=lambda x: float(x["amount_out"]))
                    best_dest_quote = max(dest_quotes, key=lambda x: float(x["amount_out"]))
                    
                    # Calculate bridge step
                    bridge_amount = best_source_quote["amount_out"]
                    bridge_fee = float(bridge_amount) * bridge_config["fee_percentage"] / 100
                    bridged_amount = float(bridge_amount) - bridge_fee
                    
                    # Final swap amount
                    final_amount = float(best_dest_quote["amount_out"]) * (bridged_amount / float(amount_in))
                    
                    route = {
                        "steps": [
                            {
                                "type": "swap",
                                "chain": source_chain,
                                "dex": best_source_quote["dex"],
                                "token_in": token_in,
                                "token_out": token_out,
                                "amount_in": amount_in,
                                "amount_out": best_source_quote["amount_out"]
                            },
                            {
                                "type": "bridge",
                                "protocol": bridge_name,
                                "from_chain": source_chain,
                                "to_chain": destination_chain,
                                "token": token_out,
                                "amount_in": bridge_amount,
                                "amount_out": str(bridged_amount),
                                "fee": str(bridge_fee)
                            },
                            {
                                "type": "swap",
                                "chain": destination_chain,
                                "dex": best_dest_quote["dex"],
                                "token_in": token_out,
                                "token_out": token_out,
                                "amount_in": str(bridged_amount),
                                "amount_out": str(final_amount)
                            }
                        ],
                        "total_amount_out": str(final_amount),
                        "total_fee": str(bridge_fee + float(best_source_quote.get("gas_estimate", 0)) + float(best_dest_quote.get("gas_estimate", 0))),
                        "estimated_time": 900,
                        "efficiency_score": 85.0
                    }
                    routes.append(route)
    
    # Sort routes by efficiency score
    routes.sort(key=lambda x: x["efficiency_score"], reverse=True)
    
    return routes[:5]  # Return top 5 routes

async def update_pool_data():
    """Update liquidity pool data"""
    # This would integrate with various DEX subgraphs and APIs
    logger.info("Updating pool data...")

# API Routes

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "cross-chain-dex-aggregator-enhanced"}

@app.get("/supported-chains")
async def get_supported_chains():
    """Get list of supported chains and DEXs"""
    return SUPPORTED_CHAINS

@app.get("/supported-bridges")
async def get_supported_bridges():
    """Get list of supported bridge protocols"""
    return BRIDGE_PROTOCOLS

@app.post("/quote")
async def get_quote(request: QuoteRequest, db: Session = Depends(get_db)):
    """Get best quote for a token swap"""
    try:
        if request.chain not in SUPPORTED_CHAINS:
            raise HTTPException(status_code=400, detail="Unsupported chain")
        
        # Get quotes from all DEXs
        quotes = await get_all_quotes(
            request.chain,
            request.token_in,
            request.token_out,
            request.amount_in,
            request.dexs
        )
        
        if not quotes:
            raise HTTPException(status_code=404, detail="No quotes available")
        
        # Find best quote
        best_quote = max(quotes, key=lambda x: float(x["amount_out"]))
        
        # Save quote to database
        db_quote = DEXQuote(
            chain=request.chain,
            dex=best_quote["dex"],
            token_in=request.token_in,
            token_out=request.token_out,
            amount_in=request.amount_in,
            amount_out=best_quote["amount_out"],
            price=best_quote["price"],
            price_impact=best_quote.get("price_impact", 0.0),
            gas_estimate=best_quote.get("gas_estimate", "0"),
            route=best_quote.get("route", []),
            pools=best_quote.get("pools", []),
            slippage_tolerance=request.slippage_tolerance,
            expires_at=datetime.utcnow() + timedelta(minutes=5)
        )
        
        db.add(db_quote)
        db.commit()
        db.refresh(db_quote)
        
        # Return all quotes with best quote highlighted
        return {
            "best_quote": db_quote,
            "all_quotes": quotes,
            "quote_id": db_quote.id
        }
        
    except Exception as e:
        logger.error(f"Error getting quote: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cross-chain-quote")
async def get_cross_chain_quote(request: CrossChainQuoteRequest, db: Session = Depends(get_db)):
    """Get cross-chain swap quote"""
    try:
        if request.source_chain not in SUPPORTED_CHAINS:
            raise HTTPException(status_code=400, detail="Unsupported source chain")
        if request.destination_chain not in SUPPORTED_CHAINS:
            raise HTTPException(status_code=400, detail="Unsupported destination chain")
        
        # Find cross-chain routes
        routes = await find_cross_chain_routes(
            request.source_chain,
            request.destination_chain,
            request.token_in,
            request.token_out,
            request.amount_in,
            request.max_hops
        )
        
        if not routes:
            raise HTTPException(status_code=404, detail="No cross-chain routes available")
        
        # Save best route
        best_route = routes[0]
        
        db_route = CrossChainRoute(
            source_chain=request.source_chain,
            destination_chain=request.destination_chain,
            token_in=request.token_in,
            token_out=request.token_out,
            amount_in=request.amount_in,
            steps=best_route["steps"],
            total_fee=best_route["total_fee"],
            estimated_time=best_route["estimated_time"],
            amount_out=best_route["total_amount_out"],
            minimum_received=str(float(best_route["total_amount_out"]) * (1 - request.slippage_tolerance / 100)),
            efficiency_score=best_route["efficiency_score"],
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        
        db.add(db_route)
        db.commit()
        db.refresh(db_route)
        
        return {
            "best_route": db_route,
            "all_routes": routes,
            "route_id": db_route.id
        }
        
    except Exception as e:
        logger.error(f"Error getting cross-chain quote: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/swap")
async def execute_swap(request: SwapRequest, db: Session = Depends(get_db)):
    """Execute a token swap"""
    try:
        # Get quote from database
        quote = db.query(DEXQuote).filter(DEXQuote.id == request.quote_id).first()
        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found")
        
        if quote.expires_at < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Quote expired")
        
        # Execute swap
        dex_integration = get_dex_integration(quote.chain, quote.dex)
        tx_hash = await dex_integration.execute_swap(
            {
                "token_in": quote.token_in,
                "token_out": quote.token_out,
                "amount_in": quote.amount_in,
                "amount_out": quote.amount_out,
                "route": quote.route
            },
            request.user_address
        )
        
        # Save transaction
        db_tx = DEXTransaction(
            user_address=request.user_address,
            chain=quote.chain,
            tx_hash=tx_hash,
            token_in=quote.token_in,
            token_out=quote.token_out,
            amount_in=quote.amount_in,
            amount_out=quote.amount_out,
            route_id=quote.id,
            dex_used=quote.dex,
            gas_used=quote.gas_estimate
        )
        
        db.add(db_tx)
        db.commit()
        db.refresh(db_tx)
        
        return {
            "transaction": db_tx,
            "tx_hash": tx_hash,
            "status": "pending"
        }
        
    except Exception as e:
        logger.error(f"Error executing swap: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cross-chain-swap")
async def execute_cross_chain_swap(request: CrossChainSwapRequest, db: Session = Depends(get_db)):
    """Execute a cross-chain swap"""
    try:
        # Get route from database
        route = db.query(CrossChainRoute).filter(CrossChainRoute.id == request.route_id).first()
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        if route.expires_at < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Route expired")
        
        # Execute each step of the route
        transactions = []
        
        for step in route.steps:
            if step["type"] == "swap":
                # Execute DEX swap
                dex_integration = get_dex_integration(step["chain"], step["dex"])
                tx_hash = await dex_integration.execute_swap(step, request.user_address)
                
                db_tx = DEXTransaction(
                    user_address=request.user_address,
                    chain=step["chain"],
                    tx_hash=tx_hash,
                    token_in=step["token_in"],
                    token_out=step["token_out"],
                    amount_in=step["amount_in"],
                    amount_out=step["amount_out"],
                    route_id=route.id,
                    dex_used=step["dex"]
                )
                db.add(db_tx)
                transactions.append({"type": "swap", "tx_hash": tx_hash, "chain": step["chain"]})
                
            elif step["type"] == "bridge":
                # Execute bridge transaction
                bridge_tx_hash = f"0x{uuid.uuid4().hex}"  # Mock bridge transaction
                
                db_bridge = BridgeTransaction(
                    user_address=request.user_address,
                    bridge_protocol=step["protocol"],
                    source_chain=step["from_chain"],
                    destination_chain=step["to_chain"],
                    source_tx_hash=bridge_tx_hash,
                    token=step["token"],
                    amount=step["amount_in"],
                    bridge_fee=step["fee"]
                )
                db.add(db_bridge)
                transactions.append({"type": "bridge", "tx_hash": bridge_tx_hash, "protocol": step["protocol"]})
        
        db.commit()
        
        return {
            "transactions": transactions,
            "route_id": route.id,
            "status": "initiated",
            "estimated_completion": datetime.utcnow() + timedelta(seconds=route.estimated_time)
        }
        
    except Exception as e:
        logger.error(f"Error executing cross-chain swap: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pools/{chain}")
async def get_liquidity_pools(
    chain: str,
    token0: Optional[str] = None,
    token1: Optional[str] = None,
    dex: Optional[str] = None,
    min_tvl: Optional[float] = None,
    sort_by: str = "tvl",
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get liquidity pools"""
    query = db.query(LiquidityPool).filter(LiquidityPool.chain == chain)
    
    if token0:
        query = query.filter(LiquidityPool.token0 == token0)
    if token1:
        query = query.filter(LiquidityPool.token1 == token1)
    if dex:
        query = query.filter(LiquidityPool.dex == dex)
    if min_tvl:
        query = query.filter(LiquidityPool.tvl_usd >= min_tvl)
    
    # Sorting
    if sort_by == "tvl":
        query = query.order_by(LiquidityPool.tvl_usd.desc())
    elif sort_by == "volume":
        query = query.order_by(LiquidityPool.volume_24h.desc())
    elif sort_by == "apr":
        query = query.order_by(LiquidityPool.apr.desc())
    
    pools = query.limit(limit).all()
    return pools

@app.get("/transactions/{user_address}")
async def get_user_transactions(
    user_address: str,
    chain: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get user's transaction history"""
    query = db.query(DEXTransaction).filter(DEXTransaction.user_address == user_address)
    
    if chain:
        query = query.filter(DEXTransaction.chain == chain)
    if status:
        query = query.filter(DEXTransaction.status == status)
    
    transactions = query.order_by(DEXTransaction.created_at.desc()).limit(limit).all()
    return transactions

@app.get("/bridge-transactions/{user_address}")
async def get_user_bridge_transactions(
    user_address: str,
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get user's bridge transaction history"""
    query = db.query(BridgeTransaction).filter(BridgeTransaction.user_address == user_address)
    
    if status:
        query = query.filter(BridgeTransaction.status == status)
    
    transactions = query.order_by(BridgeTransaction.created_at.desc()).limit(limit).all()
    return transactions

@app.get("/analytics/volume")
async def get_volume_analytics(
    chain: Optional[str] = None,
    dex: Optional[str] = None,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get volume analytics"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(DEXTransaction).filter(
        DEXTransaction.created_at >= start_date,
        DEXTransaction.status == "confirmed"
    )
    
    if chain:
        query = query.filter(DEXTransaction.chain == chain)
    if dex:
        query = query.filter(DEXTransaction.dex_used == dex)
    
    transactions = query.all()
    
    # Calculate metrics
    total_volume = sum(float(tx.amount_in) for tx in transactions if tx.amount_in)
    total_transactions = len(transactions)
    unique_users = len(set(tx.user_address for tx in transactions))
    
    # Volume by chain
    volume_by_chain = {}
    for tx in transactions:
        if tx.chain not in volume_by_chain:
            volume_by_chain[tx.chain] = 0
        volume_by_chain[tx.chain] += float(tx.amount_in) if tx.amount_in else 0
    
    return {
        "total_volume": total_volume,
        "total_transactions": total_transactions,
        "unique_users": unique_users,
        "volume_by_chain": volume_by_chain,
        "period_days": days
    }

@app.get("/analytics/pools")
async def get_pool_analytics(
    chain: Optional[str] = None,
    dex: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get pool analytics"""
    query = db.query(LiquidityPool)
    
    if chain:
        query = query.filter(LiquidityPool.chain == chain)
    if dex:
        query = query.filter(LiquidityPool.dex == dex)
    
    pools = query.all()
    
    # Calculate metrics
    total_tvl = sum(pool.tvl_usd for pool in pools)
    total_volume_24h = sum(pool.volume_24h for pool in pools)
    avg_apr = np.mean([pool.apr for pool in pools if pool.apr > 0]) if pools else 0
    
    # Top pools by TVL
    top_pools_by_tvl = sorted(pools, key=lambda x: x.tvl_usd, reverse=True)[:10]
    
    return {
        "total_tvl": total_tvl,
        "total_volume_24h": total_volume_24h,
        "average_apr": avg_apr,
        "total_pools": len(pools),
        "top_pools": top_pools_by_tvl
    }

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks"""
    logger.info("Cross-Chain DEX Aggregator Enhanced service started")
    
    # Start background tasks
    asyncio.create_task(periodic_pool_updates())
    asyncio.create_task(transaction_status_monitor())

async def periodic_pool_updates():
    """Update pool data periodically"""
    while True:
        try:
            await update_pool_data()
            await asyncio.sleep(300)  # Update every 5 minutes
        except Exception as e:
            logger.error(f"Error updating pool data: {e}")
            await asyncio.sleep(60)

async def transaction_status_monitor():
    """Monitor transaction status"""
    while True:
        try:
            db = SessionLocal()
            
            # Check pending transactions
            pending_txs = db.query(DEXTransaction).filter(
                DEXTransaction.status == "pending"
            ).all()
            
            for tx in pending_txs:
                # Mock status check - integrate with actual blockchain APIs
                if np.random.random() > 0.8:  # 20% chance to confirm
                    tx.status = "confirmed"
                    tx.confirmed_at = datetime.utcnow()
            
            db.commit()
            db.close()
            
            await asyncio.sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            logger.error(f"Error monitoring transactions: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8083)