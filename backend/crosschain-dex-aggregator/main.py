"""
TigerEx Exchange Platform
Version: 7.0.0 - Production Release

Cross-Chain DEX Aggregator Service
Aggregate liquidity across multiple DEXs and chains
"""

import asyncio
import json
import logging
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChainType(Enum):
    ETHEREUM = "ethereum"
    BSC = "bsc"
    POLYGON = "polygon"
    AVALANCHE = "avalanche"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    SOLANA = "solana"
    FANTOM = "fantom"

class DEXProtocol(Enum):
    UNISWAP_V2 = "uniswap_v2"
    UNISWAP_V3 = "uniswap_v3"
    SUSHISWAP = "sushiswap"
    PANCAKESWAP = "pancakeswap"
    QUICKSWAP = "quickswap"
    TRADERJOE = "traderjoe"
    SPOOKYSWAP = "spookyswap"
    CURVE = "curve"
    BALANCER = "balancer"
    ORCA = "orca"
    RAYDIUM = "raydium"

class SwapStatus(Enum):
    PENDING = "pending"
    ROUTING = "routing"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Token:
    address: str
    symbol: str
    name: str
    decimals: int
    chain: ChainType
    logo_url: str
    price_usd: float

@dataclass
class DEXInfo:
    protocol: DEXProtocol
    chain: ChainType
    name: str
    router_address: str
    factory_address: str
    fee_rate: float
    is_active: bool

@dataclass
class LiquidityPool:
    id: str
    dex: DEXProtocol
    chain: ChainType
    token_a: Token
    token_b: Token
    reserve_a: float
    reserve_b: float
    liquidity_usd: float
    fee_rate: float
    apy: float
    volume_24h: float

@dataclass
class SwapRoute:
    id: str
    input_token: Token
    output_token: Token
    input_amount: float
    output_amount: float
    price_impact: float
    gas_cost_usd: float
    route_path: List[Dict[str, Any]]
    estimated_time: int  # seconds
    confidence_score: float

@dataclass
class CrossChainSwap:
    id: str
    user_id: str
    from_chain: ChainType
    to_chain: ChainType
    input_token: Token
    output_token: Token
    input_amount: float
    expected_output: float
    actual_output: float
    route: SwapRoute
    bridge_fee: float
    total_fee: float
    status: SwapStatus
    transaction_hashes: List[str]
    created_at: datetime
    completed_at: Optional[datetime] = None

class CrossChainDEXAggregator:
    def __init__(self):
        self.dexes: Dict[str, DEXInfo] = {}
        self.tokens: Dict[str, Token] = {}
        self.pools: Dict[str, LiquidityPool] = {}
        self.swaps: Dict[str, CrossChainSwap] = {}
        self.price_cache: Dict[str, Dict[str, float]] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def initialize(self):
        """Initialize the cross-chain DEX aggregator"""
        logger.info("🌉 Initializing Cross-Chain DEX Aggregator...")
        
        # Initialize HTTP session
        self.session = aiohttp.ClientSession()
        
        # Load DEX configurations
        await self._load_dex_configs()
        
        # Load token configurations
        await self._load_token_configs()
        
        # Load liquidity pools
        await self._load_liquidity_pools()
        
        # Start price monitoring
        asyncio.create_task(self._monitor_prices())
        
        logger.info("✅ Cross-Chain DEX Aggregator initialized")
    
    async def _load_dex_configs(self):
        """Load DEX configurations"""
        dex_configs = [
            {
                "protocol": DEXProtocol.UNISWAP_V2,
                "chain": ChainType.ETHEREUM,
                "name": "Uniswap V2",
                "router_address": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
                "factory_address": "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
                "fee_rate": 0.003
            },
            {
                "protocol": DEXProtocol.UNISWAP_V3,
                "chain": ChainType.ETHEREUM,
                "name": "Uniswap V3",
                "router_address": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
                "factory_address": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
                "fee_rate": 0.003
            },
            {
                "protocol": DEXProtocol.PANCAKESWAP,
                "chain": ChainType.BSC,
                "name": "PancakeSwap",
                "router_address": "0x10ED43C718714eb63d5aA57B78B54704E256024E",
                "factory_address": "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73",
                "fee_rate": 0.0025
            },
            {
                "protocol": DEXProtocol.QUICKSWAP,
                "chain": ChainType.POLYGON,
                "name": "QuickSwap",
                "router_address": "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff",
                "factory_address": "0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32",
                "fee_rate": 0.003
            },
            {
                "protocol": DEXProtocol.TRADERJOE,
                "chain": ChainType.AVALANCHE,
                "name": "Trader Joe",
                "router_address": "0x60aE616a2155Ee3d9A68541Ba4544862310933d4",
                "factory_address": "0x9Ad6C38BE94206cA50bb0d90783181662f0Cfa10",
                "fee_rate": 0.003
            }
        ]
        
        for config in dex_configs:
            dex_id = f"{config['protocol'].value}_{config['chain'].value}"
            self.dexes[dex_id] = DEXInfo(
                protocol=config["protocol"],
                chain=config["chain"],
                name=config["name"],
                router_address=config["router_address"],
                factory_address=config["factory_address"],
                fee_rate=config["fee_rate"],
                is_active=True
            )
    
    async def _load_token_configs(self):
        """Load token configurations"""
        token_configs = [
            # Ethereum tokens
            {
                "address": "0xA0b86a33E6441b8435b662303c0f098C8c8c3b4e",
                "symbol": "ETH",
                "name": "Ethereum",
                "decimals": 18,
                "chain": ChainType.ETHEREUM,
                "price_usd": 2680.75
            },
            {
                "address": "0xA0b86a33E6441b8435b662303c0f098C8c8c3b4e",
                "symbol": "USDT",
                "name": "Tether USD",
                "decimals": 6,
                "chain": ChainType.ETHEREUM,
                "price_usd": 1.0
            },
            # BSC tokens
            {
                "address": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
                "symbol": "BNB",
                "name": "BNB",
                "decimals": 18,
                "chain": ChainType.BSC,
                "price_usd": 315.20
            },
            {
                "address": "0x55d398326f99059fF775485246999027B3197955",
                "symbol": "USDT",
                "name": "Tether USD",
                "decimals": 18,
                "chain": ChainType.BSC,
                "price_usd": 1.0
            },
            # Polygon tokens
            {
                "address": "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",
                "symbol": "MATIC",
                "name": "Polygon",
                "decimals": 18,
                "chain": ChainType.POLYGON,
                "price_usd": 0.825
            },
            {
                "address": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
                "symbol": "USDT",
                "name": "Tether USD",
                "decimals": 6,
                "chain": ChainType.POLYGON,
                "price_usd": 1.0
            }
        ]
        
        for config in token_configs:
            token_id = f"{config['symbol']}_{config['chain'].value}"
            self.tokens[token_id] = Token(
                address=config["address"],
                symbol=config["symbol"],
                name=config["name"],
                decimals=config["decimals"],
                chain=config["chain"],
                logo_url=f"https://assets.coingecko.com/coins/images/{config['symbol'].lower()}.png",
                price_usd=config["price_usd"]
            )
    
    async def _load_liquidity_pools(self):
        """Load liquidity pool data"""
        # Sample liquidity pools
        pool_configs = [
            {
                "dex": DEXProtocol.UNISWAP_V2,
                "chain": ChainType.ETHEREUM,
                "token_a_symbol": "ETH",
                "token_b_symbol": "USDT",
                "reserve_a": 1000.0,
                "reserve_b": 2680750.0,
                "volume_24h": 50000000.0,
                "apy": 12.5
            },
            {
                "dex": DEXProtocol.PANCAKESWAP,
                "chain": ChainType.BSC,
                "token_a_symbol": "BNB",
                "token_b_symbol": "USDT",
                "reserve_a": 5000.0,
                "reserve_b": 1576000.0,
                "volume_24h": 25000000.0,
                "apy": 15.2
            },
            {
                "dex": DEXProtocol.QUICKSWAP,
                "chain": ChainType.POLYGON,
                "token_a_symbol": "MATIC",
                "token_b_symbol": "USDT",
                "reserve_a": 100000.0,
                "reserve_b": 82500.0,
                "volume_24h": 5000000.0,
                "apy": 18.7
            }
        ]
        
        for config in pool_configs:
            pool_id = f"{config['dex'].value}_{config['chain'].value}_{config['token_a_symbol']}_{config['token_b_symbol']}"
            
            token_a_id = f"{config['token_a_symbol']}_{config['chain'].value}"
            token_b_id = f"{config['token_b_symbol']}_{config['chain'].value}"
            
            token_a = self.tokens.get(token_a_id)
            token_b = self.tokens.get(token_b_id)
            
            if token_a and token_b:
                dex_info = next((dex for dex in self.dexes.values() 
                               if dex.protocol == config['dex'] and dex.chain == config['chain']), None)
                
                if dex_info:
                    liquidity_usd = (config['reserve_a'] * token_a.price_usd + 
                                   config['reserve_b'] * token_b.price_usd)
                    
                    self.pools[pool_id] = LiquidityPool(
                        id=pool_id,
                        dex=config['dex'],
                        chain=config['chain'],
                        token_a=token_a,
                        token_b=token_b,
                        reserve_a=config['reserve_a'],
                        reserve_b=config['reserve_b'],
                        liquidity_usd=liquidity_usd,
                        fee_rate=dex_info.fee_rate,
                        apy=config['apy'],
                        volume_24h=config['volume_24h']
                    )
    
    async def _monitor_prices(self):
        """Monitor token prices"""
        while True:
            try:
                await self._update_token_prices()
                await asyncio.sleep(30)  # Update every 30 seconds
            except Exception as e:
                logger.error(f"❌ Error monitoring prices: {e}")
                await asyncio.sleep(60)
    
    async def _update_token_prices(self):
        """Update token prices from external APIs"""
        try:
            # Simulate price updates (in real implementation, fetch from APIs)
            import random
            
            for token in self.tokens.values():
                # Add small random price movement
                price_change = random.uniform(-0.02, 0.02)  # ±2%
                token.price_usd *= (1 + price_change)
                
                # Update price cache
                cache_key = f"{token.symbol}_{token.chain.value}"
                if token.chain.value not in self.price_cache:
                    self.price_cache[token.chain.value] = {}
                self.price_cache[token.chain.value][token.symbol] = token.price_usd
            
        except Exception as e:
            logger.error(f"❌ Error updating prices: {e}")
    
    async def find_best_route(self, 
                            input_token_symbol: str, 
                            output_token_symbol: str,
                            input_amount: float,
                            from_chain: Optional[ChainType] = None,
                            to_chain: Optional[ChainType] = None) -> List[SwapRoute]:
        """Find the best swap routes across chains and DEXs"""
        try:
            routes = []
            
            # Find all possible routes
            for pool in self.pools.values():
                # Check if this pool can be part of the route
                if self._can_use_pool_for_route(pool, input_token_symbol, output_token_symbol, from_chain, to_chain):
                    route = await self._calculate_route(pool, input_token_symbol, output_token_symbol, input_amount)
                    if route:
                        routes.append(route)
            
            # Sort routes by output amount (best first)
            routes.sort(key=lambda r: r.output_amount, reverse=True)
            
            return routes[:5]  # Return top 5 routes
            
        except Exception as e:
            logger.error(f"❌ Error finding routes: {e}")
            return []
    
    def _can_use_pool_for_route(self, pool: LiquidityPool, 
                               input_symbol: str, output_symbol: str,
                               from_chain: Optional[ChainType], to_chain: Optional[ChainType]) -> bool:
        """Check if a pool can be used for the route"""
        # Check if pool contains the required tokens
        pool_symbols = {pool.token_a.symbol, pool.token_b.symbol}
        
        if input_symbol in pool_symbols or output_symbol in pool_symbols:
            # Check chain constraints
            if from_chain and pool.chain != from_chain:
                return False
            if to_chain and pool.chain != to_chain:
                return False
            return True
        
        return False
    
    async def _calculate_route(self, pool: LiquidityPool, 
                             input_symbol: str, output_symbol: str, 
                             input_amount: float) -> Optional[SwapRoute]:
        """Calculate swap route through a pool"""
        try:
            # Determine input and output tokens
            if pool.token_a.symbol == input_symbol:
                input_token = pool.token_a
                output_token = pool.token_b
                input_reserve = pool.reserve_a
                output_reserve = pool.reserve_b
            elif pool.token_b.symbol == input_symbol:
                input_token = pool.token_b
                output_token = pool.token_a
                input_reserve = pool.reserve_b
                output_reserve = pool.reserve_a
            else:
                return None
            
            # Calculate output amount using constant product formula
            # x * y = k, where x and y are reserves
            fee_multiplier = 1 - pool.fee_rate
            input_amount_with_fee = input_amount * fee_multiplier
            
            output_amount = (output_reserve * input_amount_with_fee) / (input_reserve + input_amount_with_fee)
            
            # Calculate price impact
            price_impact = (input_amount / input_reserve) * 100
            
            # Estimate gas cost (simplified)
            gas_cost_usd = self._estimate_gas_cost(pool.chain)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(pool, input_amount, price_impact)
            
            route_id = f"route_{uuid.uuid4().hex[:8]}"
            
            return SwapRoute(
                id=route_id,
                input_token=input_token,
                output_token=output_token,
                input_amount=input_amount,
                output_amount=output_amount,
                price_impact=price_impact,
                gas_cost_usd=gas_cost_usd,
                route_path=[{
                    "dex": pool.dex.value,
                    "chain": pool.chain.value,
                    "pool_id": pool.id,
                    "fee_rate": pool.fee_rate
                }],
                estimated_time=30,  # 30 seconds
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"❌ Error calculating route: {e}")
            return None
    
    def _estimate_gas_cost(self, chain: ChainType) -> float:
        """Estimate gas cost for a chain"""
        gas_costs = {
            ChainType.ETHEREUM: 25.0,
            ChainType.BSC: 0.5,
            ChainType.POLYGON: 0.1,
            ChainType.AVALANCHE: 0.2,
            ChainType.ARBITRUM: 2.0,
            ChainType.OPTIMISM: 1.5
        }
        return gas_costs.get(chain, 5.0)
    
    def _calculate_confidence_score(self, pool: LiquidityPool, input_amount: float, price_impact: float) -> float:
        """Calculate confidence score for a route"""
        try:
            # Base score
            score = 100.0
            
            # Reduce score based on price impact
            score -= min(price_impact * 2, 30)
            
            # Reduce score based on liquidity
            if pool.liquidity_usd < 100000:  # Low liquidity
                score -= 20
            elif pool.liquidity_usd < 1000000:  # Medium liquidity
                score -= 10
            
            # Reduce score based on volume
            if pool.volume_24h < 1000000:  # Low volume
                score -= 15
            elif pool.volume_24h < 10000000:  # Medium volume
                score -= 5
            
            return max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"❌ Error calculating confidence score: {e}")
            return 50.0
    
    async def execute_swap(self, user_id: str, route: SwapRoute) -> CrossChainSwap:
        """Execute a cross-chain swap"""
        try:
            swap_id = f"swap_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Determine if this is a cross-chain swap
            from_chain = route.input_token.chain
            to_chain = route.output_token.chain
            is_cross_chain = from_chain != to_chain
            
            # Calculate fees
            bridge_fee = 0.0
            if is_cross_chain:
                bridge_fee = route.output_amount * 0.001  # 0.1% bridge fee
            
            total_fee = route.gas_cost_usd + bridge_fee
            
            swap = CrossChainSwap(
                id=swap_id,
                user_id=user_id,
                from_chain=from_chain,
                to_chain=to_chain,
                input_token=route.input_token,
                output_token=route.output_token,
                input_amount=route.input_amount,
                expected_output=route.output_amount,
                actual_output=0.0,
                route=route,
                bridge_fee=bridge_fee,
                total_fee=total_fee,
                status=SwapStatus.PENDING,
                transaction_hashes=[],
                created_at=datetime.now()
            )
            
            self.swaps[swap_id] = swap
            
            # Start swap execution
            asyncio.create_task(self._execute_swap_async(swap))
            
            logger.info(f"🔄 Started swap execution: {swap_id}")
            return swap
            
        except Exception as e:
            logger.error(f"❌ Error executing swap: {e}")
            raise
    
    async def _execute_swap_async(self, swap: CrossChainSwap):
        """Execute swap asynchronously"""
        try:
            swap.status = SwapStatus.ROUTING
            
            # Simulate swap execution
            await asyncio.sleep(2)  # Routing time
            
            swap.status = SwapStatus.EXECUTING
            
            # Generate mock transaction hash
            tx_hash = f"0x{uuid.uuid4().hex}"
            swap.transaction_hashes.append(tx_hash)
            
            # Simulate execution time
            await asyncio.sleep(5)
            
            # Calculate actual output (with some slippage)
            slippage = 0.005  # 0.5% slippage
            swap.actual_output = swap.expected_output * (1 - slippage)
            
            swap.status = SwapStatus.COMPLETED
            swap.completed_at = datetime.now()
            
            logger.info(f"✅ Swap completed: {swap.id}")
            
        except Exception as e:
            swap.status = SwapStatus.FAILED
            logger.error(f"❌ Swap failed: {swap.id}, Error: {e}")
    
    async def get_swap_status(self, swap_id: str) -> Optional[CrossChainSwap]:
        """Get swap status"""
        return self.swaps.get(swap_id)
    
    async def get_user_swaps(self, user_id: str) -> List[CrossChainSwap]:
        """Get all swaps for a user"""
        return [swap for swap in self.swaps.values() if swap.user_id == user_id]
    
    async def get_supported_tokens(self, chain: Optional[ChainType] = None) -> List[Token]:
        """Get supported tokens"""
        if chain:
            return [token for token in self.tokens.values() if token.chain == chain]
        return list(self.tokens.values())
    
    async def get_liquidity_pools(self, chain: Optional[ChainType] = None) -> List[LiquidityPool]:
        """Get liquidity pools"""
        if chain:
            return [pool for pool in self.pools.values() if pool.chain == chain]
        return list(self.pools.values())
    
    async def get_dex_analytics(self) -> Dict[str, Any]:
        """Get DEX analytics"""
        try:
            total_liquidity = sum(pool.liquidity_usd for pool in self.pools.values())
            total_volume_24h = sum(pool.volume_24h for pool in self.pools.values())
            total_swaps = len(self.swaps)
            successful_swaps = len([s for s in self.swaps.values() if s.status == SwapStatus.COMPLETED])
            
            chain_stats = {}
            for pool in self.pools.values():
                chain = pool.chain.value
                if chain not in chain_stats:
                    chain_stats[chain] = {
                        "liquidity_usd": 0,
                        "volume_24h": 0,
                        "pools_count": 0
                    }
                chain_stats[chain]["liquidity_usd"] += pool.liquidity_usd
                chain_stats[chain]["volume_24h"] += pool.volume_24h
                chain_stats[chain]["pools_count"] += 1
            
            return {
                "total_liquidity_usd": total_liquidity,
                "total_volume_24h": total_volume_24h,
                "total_swaps": total_swaps,
                "successful_swaps": successful_swaps,
                "success_rate": (successful_swaps / total_swaps * 100) if total_swaps > 0 else 0,
                "supported_chains": len(set(pool.chain for pool in self.pools.values())),
                "supported_dexes": len(set(pool.dex for pool in self.pools.values())),
                "chain_stats": chain_stats,
                "updated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting analytics: {e}")
            return {}

# FastAPI application
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(title="Cross-Chain DEX Aggregator", version="7.0.0")
aggregator = CrossChainDEXAggregator()

class SwapRequest(BaseModel):
    user_id: str
    input_token: str
    output_token: str
    input_amount: float
    from_chain: Optional[str] = None
    to_chain: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    await aggregator.initialize()

@app.get("/routes")
async def find_routes(
    input_token: str,
    output_token: str,
    input_amount: float,
    from_chain: Optional[str] = None,
    to_chain: Optional[str] = None
):
    from_chain_enum = ChainType(from_chain) if from_chain else None
    to_chain_enum = ChainType(to_chain) if to_chain else None
    
    routes = await aggregator.find_best_route(
        input_token, output_token, input_amount, from_chain_enum, to_chain_enum
    )
    return {"routes": routes}

@app.post("/swaps")
async def execute_swap(swap_request: SwapRequest):
    try:
        # First find the best route
        from_chain_enum = ChainType(swap_request.from_chain) if swap_request.from_chain else None
        to_chain_enum = ChainType(swap_request.to_chain) if swap_request.to_chain else None
        
        routes = await aggregator.find_best_route(
            swap_request.input_token,
            swap_request.output_token,
            swap_request.input_amount,
            from_chain_enum,
            to_chain_enum
        )
        
        if not routes:
            raise HTTPException(status_code=400, detail="No routes found")
        
        # Execute with best route
        swap = await aggregator.execute_swap(swap_request.user_id, routes[0])
        return {"success": True, "swap": swap}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/swaps/{swap_id}")
async def get_swap_status(swap_id: str):
    swap = await aggregator.get_swap_status(swap_id)
    if not swap:
        raise HTTPException(status_code=404, detail="Swap not found")
    return swap

@app.get("/users/{user_id}/swaps")
async def get_user_swaps(user_id: str):
    return await aggregator.get_user_swaps(user_id)

@app.get("/tokens")
async def get_supported_tokens(chain: Optional[str] = None):
    chain_enum = ChainType(chain) if chain else None
    return await aggregator.get_supported_tokens(chain_enum)

@app.get("/pools")
async def get_liquidity_pools(chain: Optional[str] = None):
    chain_enum = ChainType(chain) if chain else None
    return await aggregator.get_liquidity_pools(chain_enum)

@app.get("/analytics")
async def get_analytics():
    return await aggregator.get_dex_analytics()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)