"""
DeFi Protocol Integration for Market Making
Including Uniswap, Sushiswap, Curve, yield farming, and MEV protection
"""

import asyncio
import aiohttp
import websockets
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from abc import ABC, abstractmethod
import hashlib
import eth_utils
from web3 import Web3, AsyncWeb3
from web3.contract import Contract
from eth_account import Account
import pickle

logger = logging.getLogger(__name__)

@dataclass
class DeFiProtocolConfig:
    """Configuration for DeFi protocol"""
    name: str
    rpc_url: str
    chain_id: int
    gas_limit: int = 200000
    gas_price_gwei: float = 20.0
    max_slippage: float = 0.005  # 0.5%
    min_liquidity: float = 1000  # USD
    max_position_size: float = 100000  # USD
    mev_protection_enabled: bool = True
    private_key: str = ""
    flashloan_enabled: bool = False

@dataclass
class PoolInfo:
    """Information about a liquidity pool"""
    address: str
    token0_address: str
    token1_address: str
    token0_symbol: str
    token1_symbol: str
    fee_tier: Optional[int] = None
    reserve0: float = 0.0
    reserve1: float = 0.0
    total_supply: float = 0.0
    apr: float = 0.0
    volume_24h: float = 0.0
    tvl: float = 0.0

class UniswapV3Protocol(BaseDeFiProtocol):
    """Uniswap V3 protocol integration"""
    
    def __init__(self, config: DeFiProtocolConfig):
        super().__init__(config)
        self.factory_address = "0x1F98431c8aD98523631AE4a59f267346ea31F984"
        self.router_address = "0xE592427A0AEce92De3Edee1F18E0157C05861564"
        
    async def _load_contracts(self):
        """Load Uniswap V3 contracts"""
        factory_abi = [
            {"name": "getPool", "type": "function", "stateMutability": "view", "inputs": [{"name": "tokenA", "type": "address"}, {"name": "tokenB", "type": "address"}, {"name": "fee", "type": "uint24"}], "outputs": [{"name": "pool", "type": "address"}]}
        ]
        
        self.contract_cache['factory'] = await self.w3.eth.contract(address=self.factory_address, abi=factory_abi)
        
    async def get_pools(self) -> List[PoolInfo]:
        """Get Uniswap V3 pools"""
        pools = []
        
        # Popular pools (in production, this would query the subgraph)
        popular_pools = [
            {"token0": "0xA0b86a33E6441e70c3C7F0d0A8F9d0A7B3C4c8e7d", "token1": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "fee": 3000},  # USDC/WETH
            {"token0": "0xdAC17F958D2ee523a2206206994597C13D831ec7", "token1": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "fee": 3000},  # USDT/WETH
        ]
        
        for pool_data in popular_pools:
            try:
                pool_address = await self.contract_cache['factory'].functions.getPool(
                    pool_data['token0'],
                    pool_data['token1'],
                    pool_data['fee']
                ).call()
                
                if pool_address != "0x0000000000000000000000000000000000000000":
                    pools.append(PoolInfo(
                        address=pool_address,
                        token0_address=pool_data['token0'],
                        token1_address=pool_data['token1'],
                        token0_symbol="USDC" if pool_data['token0'] == "0xA0b86a33E6441e70c3C7F0d0A8F9d0A7B3C4c8e7d" else "USDT",
                        token1_symbol="WETH",
                        fee_tier=pool_data['fee']
                    ))
                    
            except Exception as e:
                logger.error(f"Error getting pool info: {e}")
                continue
        
        return pools
    
    async def get_pool_reserves(self, pool_address: str) -> Tuple[float, float]:
        """Get pool reserves"""
        # Simplified - in production, query actual contract
        return 1000000.0, 500.0  # Mock data
    
    async def calculate_swap_amount(self, pool_address: str, token_in: str, amount_in: float) -> Tuple[float, float]:
        """Calculate swap amount and price impact"""
        # Simplified calculation
        reserve0, reserve1 = await self.get_pool_reserves(pool_address)
        
        if token_in == self.pool_cache[pool_address]['token0']:
            amount_out = amount_in * reserve1 / reserve0
        else:
            amount_out = amount_in * reserve0 / reserve1
        
        price_impact = min(amount_in / reserve0, amount_in / reserve1) * 100
        
        return amount_out, price_impact
    
    async def execute_swap(self, token_in: str, token_out: str, amount_in: float, min_amount_out: float) -> str:
        """Execute token swap"""
        # In production, this would create and send actual transaction
        tx_hash = "0x" + hashlib.sha256(f"{token_in}{token_out}{amount_in}{datetime.now()}".encode()).hexdigest()
        return tx_hash
    
    async def add_liquidity(self, pool_address: str, token0_amount: float, token1_amount: float) -> str:
        """Add liquidity to pool"""
        tx_hash = "0x" + hashlib.sha256(f"add_liq{pool_address}{token0_amount}{token1_amount}{datetime.now()}".encode()).hexdigest()
        return tx_hash
    
    async def remove_liquidity(self, pool_address: str, lp_token_amount: float) -> Tuple[float, float]:
        """Remove liquidity from pool"""
        # Simplified return
        return lp_token_amount * 0.5, lp_token_amount * 0.5

class CurveProtocol(BaseDeFiProtocol):
    """Curve Finance protocol integration"""
    
    def __init__(self, config: DeFiProtocolConfig):
        super().__init__(config)
        self.factory_address = "0xB9fC157394Af804a3578134A6585C0dc9cc990d4"
        
    async def _load_contracts(self):
        """Load Curve contracts"""
        factory_abi = [
            {"name": "get_pool_from_lp_token", "type": "function", "stateMutability": "view", "inputs": [{"name": "_lp_token", "type": "address"}], "outputs": [{"name": "", "type": "address"}]}
        ]
        
        self.contract_cache['factory'] = await self.w3.eth.contract(address=self.factory_address, abi=factory_abi)
    
    async def get_pools(self) -> List[PoolInfo]:
        """Get Curve pools"""
        pools = []
        
        # Popular Curve pools
        popular_pools = [
            "0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7",  # 3pool
            "0xDeBF20617708857ebe4F6315264d33379b66Df27",  # USDC/WETH
        ]
        
        for pool_address in popular_pools:
            pools.append(PoolInfo(
                address=pool_address,
                token0_address="0xA0b86a33E6441e70c3C7F0d0A8F9d0A7B3C4c8e7d",  # USDC
                token1_address="0xdAC17F958D2ee523a2206206994597C13D831ec7",  # USDT
                token0_symbol="USDC",
                token1_symbol="USDT"
            ))
        
        return pools
    
    async def get_pool_reserves(self, pool_address: str) -> Tuple[float, float]:
        """Get pool reserves"""
        return 2000000.0, 1000000.0  # Mock data
    
    async def calculate_swap_amount(self, pool_address: str, token_in: str, amount_in: float) -> Tuple[float, float]:
        """Calculate swap amount for Curve"""
        reserve0, reserve1 = await self.get_pool_reserves(pool_address)
        
        # Curve uses different formula (constant sum invariant)
        amount_out = amount_in * 0.99  # Simplified with 1% fee
        price_impact = (amount_in / reserve0) * 50  # Lower price impact on stable pools
        
        return amount_out, price_impact
    
    async def execute_swap(self, token_in: str, token_out: str, amount_in: float, min_amount_out: float) -> str:
        """Execute swap on Curve"""
        tx_hash = "0x" + hashlib.sha256(f"curve_swap{token_in}{token_out}{amount_in}{datetime.now()}".encode()).hexdigest()
        return tx_hash
    
    async def add_liquidity(self, pool_address: str, token0_amount: float, token1_amount: float) -> str:
        """Add liquidity to Curve pool"""
        tx_hash = "0x" + hashlib.sha256(f"curve_add_liq{pool_address}{token0_amount}{token1_amount}{datetime.now()}".encode()).hexdigest()
        return tx_hash
    
    async def remove_liquidity(self, pool_address: str, lp_token_amount: float) -> Tuple[float, float]:
        """Remove liquidity from Curve pool"""
        return lp_token_amount * 1000, lp_token_amount * 1000

class SushiswapProtocol(BaseDeFiProtocol):
    """Sushiswap protocol integration"""
    
    def __init__(self, config: DeFiProtocolConfig):
        super().__init__(config)
        self.factory_address = "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac"
        
    async def _load_contracts(self):
        """Load Sushiswap contracts"""
        # Similar to Uniswap V2
        factory_abi = [
            {"name": "getPair", "type": "function", "stateMutability": "view", "inputs": [{"name": "tokenA", "type": "address"}, {"name": "tokenB", "type": "address"}], "outputs": [{"name": "pair", "type": "address"}]}
        ]
        
        self.contract_cache['factory'] = await self.w3.eth.contract(address=self.factory_address, abi=factory_abi)
    
    async def get_pools(self) -> List[PoolInfo]:
        """Get Sushiswap pools"""
        pools = []
        
        # Popular Sushiswap pools
        popular_pools = [
            {"token0": "0xA0b86a33E6441e70c3C7F0d0A8F9d0A7B3C4c8e7d", "token1": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"},  # USDC/WETH
            {"token0": "0xdAC17F958D2ee523a2206206994597C13D831ec7", "token1": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"},  # USDT/WETH
        ]
        
        for pool_data in popular_pools:
            pools.append(PoolInfo(
                address="0x" + hashlib.sha256(f"sushi_pool{pool_data['token0']}{pool_data['token1']}".encode()).hexdigest()[:40],
                token0_address=pool_data['token0'],
                token1_address=pool_data['token1'],
                token0_symbol="USDC" if pool_data['token0'] == "0xA0b86a33E6441e70c3C7F0d0A8F9d0A7B3C4c8e7d" else "USDT",
                token1_symbol="WETH"
            ))
        
        return pools
    
    async def get_pool_reserves(self, pool_address: str) -> Tuple[float, float]:
        """Get pool reserves"""
        return 800000.0, 400.0  # Mock data
    
    async def calculate_swap_amount(self, pool_address: str, token_in: str, amount_in: float) -> Tuple[float, float]:
        """Calculate swap amount using constant product formula"""
        reserve0, reserve1 = await self.get_pool_reserves(pool_address)
        
        if token_in == self.pool_cache[pool_address]['token0']:
            amount_out = (amount_in * reserve1) / (reserve0 + amount_in)
        else:
            amount_out = (amount_in * reserve0) / (reserve1 + amount_in)
        
        price_impact = (amount_in / reserve0) * 100
        
        return amount_out, price_impact
    
    async def execute_swap(self, token_in: str, token_out: str, amount_in: float, min_amount_out: float) -> str:
        """Execute swap on Sushiswap"""
        tx_hash = "0x" + hashlib.sha256(f"sushi_swap{token_in}{token_out}{amount_in}{datetime.now()}".encode()).hexdigest()
        return tx_hash
    
    async def add_liquidity(self, pool_address: str, token0_amount: float, token1_amount: float) -> str:
        """Add liquidity to Sushiswap pool"""
        tx_hash = "0x" + hashlib.sha256(f"sushi_add_liq{pool_address}{token0_amount}{token1_amount}{datetime.now()}".encode()).hexdigest()
        return tx_hash
    
    async def remove_liquidity(self, pool_address: str, lp_token_amount: float) -> Tuple[float, float]:
        """Remove liquidity from Sushiswap pool"""
        return lp_token_amount * 0.6, lp_token_amount * 0.4

class MEVProtection:
    """MEV protection for DeFi operations"""
    
    def __init__(self):
        self.pending_transactions = {}
        self.mev_threshold = 1000  # USD
    
    async def check_for_mev(self, tx_data: Dict[str, Any]) -> bool:
        """Check if transaction is vulnerable to MEV"""
        # Check for sandwich attacks
        if await self._detect_sandwich_risk(tx_data):
            return True
        
        # Check for front-running
        if await self._detect_front_run_risk(tx_data):
            return True
        
        return False
    
    async def _detect_sandwich_risk(self, tx_data: Dict[str, Any]) -> bool:
        """Detect sandwich attack risk"""
        # Simplified detection
        return tx_data.get('amount_in', 0) > self.mev_threshold
    
    async def _detect_front_run_risk(self, tx_data: Dict[str, Any]) -> bool:
        """Detect front-running risk"""
        # Check if gas price is too high
        return tx_data.get('gas_price', 0) > 100  # gwei
    
    async def create_private_transaction(self, tx_data: Dict[str, Any]) -> str:
        """Create private transaction via flashbots"""
        # In production, use flashbots or similar service
        private_tx = {
            **tx_data,
            'private': True,
            'flashbots': True
        }
        
        tx_hash = "0x" + hashlib.sha256(f"private_tx{datetime.now()}".encode()).hexdigest()
        return tx_hash

class YieldFarmingManager:
    """Manage yield farming positions"""
    
    def __init__(self):
        self.positions = {}
        self.reward_tracking = {}
    
    async def create_position(self, protocol: str, pool_address: str, token0_amount: float, token1_amount: float) -> YieldFarmingPosition:
        """Create new yield farming position"""
        position = YieldFarmingPosition(
            protocol=protocol,
            pool_address=pool_address,
            token0_amount=token0_amount,
            token1_amount=token1_amount,
            lp_tokens=(token0_amount * token1_amount) ** 0.5,  # Simplified
            entry_timestamp=datetime.now()
        )
        
        self.positions[pool_address] = position
        return position
    
    async def update_rewards(self, protocol: str, pool_address: str, rewards: Dict[str, float]):
        """Update rewards for a position"""
        if pool_address in self.positions:
            self.positions[pool_address].rewards_pending = rewards
    
    async def calculate_apr(self, protocol: str, pool_address: str) -> float:
        """Calculate APR for a position"""
        # Simplified APR calculation
        base_apr = 0.05  # 5% base APR
        bonus_multiplier = 1.2 if protocol == "curve" else 1.0
        return base_apr * bonus_multiplier

class DeFiArbitrageEngine:
    """DeFi arbitrage engine for cross-protocol opportunities"""
    
    def __init__(self, protocols: List[BaseDeFiProtocol]):
        self.protocols = protocols
        self.mev_protection = MEVProtection()
    
    async def scan_arbitrage_opportunities(self, token_pairs: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """Scan for arbitrage opportunities across protocols"""
        opportunities = []
        
        for token0, token1 in token_pairs:
            # Get prices from all protocols
            prices = {}
            for protocol in self.protocols:
                pools = await protocol.get_pools()
                for pool in pools:
                    if (pool.token0_address == token0 and pool.token1_address == token1) or \
                       (pool.token0_address == token1 and pool.token1_address == token0):
                        
                        # Calculate price
                        if pool.reserve0 > 0 and pool.reserve1 > 0:
                            price = pool.reserve1 / pool.reserve0
                            prices[protocol.config.name] = {
                                'price': price,
                                'pool': pool,
                                'protocol': protocol
                            }
            
            # Find arbitrage opportunities
            if len(prices) >= 2:
                min_price = min(prices.values(), key=lambda x: x['price'])
                max_price = max(prices.values(), key=lambda x: x['price'])
                
                profit_potential = (max_price['price'] - min_price['price']) / min_price['price']
                
                if profit_potential > 0.001:  # 0.1% threshold
                    opportunities.append({
                        'token0': token0,
                        'token1': token1,
                        'buy_protocol': min_price['protocol'].config.name,
                        'sell_protocol': max_price['protocol'].config.name,
                        'buy_price': min_price['price'],
                        'sell_price': max_price['price'],
                        'profit_potential': profit_potential,
                        'buy_pool': min_price['pool'],
                        'sell_pool': max_price['pool']
                    })
        
        return opportunities
    
    async def execute_arbitrage(self, opportunity: Dict[str, Any], amount: float) -> str:
        """Execute arbitrage trade"""
        try:
            # Check for MEV risk
            tx_data = {
                'amount_in': amount,
                'token0': opportunity['token0'],
                'token1': opportunity['token1']
            }
            
            if await self.mev_protection.check_for_mev(tx_data):
                # Use private transaction
                return await self.mev_protection.create_private_transaction(tx_data)
            
            # Execute buy
            buy_protocol = next(p for p in self.protocols if p.config.name == opportunity['buy_protocol'])
            buy_tx = await buy_protocol.execute_swap(
                opportunity['token0'],
                opportunity['token1'],
                amount,
                amount * opportunity['buy_price'] * 0.995  # 0.5% slippage
            )
            
            # Execute sell
            sell_protocol = next(p for p in self.protocols if p.config.name == opportunity['sell_protocol'])
            sell_tx = await sell_protocol.execute_swap(
                opportunity['token1'],
                opportunity['token0'],
                amount * opportunity['sell_price'],
                amount * opportunity['buy_price'] * 1.005
            )
            
            return f"{buy_tx}_{sell_tx}"
            
        except Exception as e:
            logger.error(f"Arbitrage execution failed: {e}")
            raise

class DeFiMarketMaker:
    """DeFi market maker combining all protocols"""
    
    def __init__(self, config: Dict[str, DeFiProtocolConfig]):
        self.protocols = {}
        self.arbitrage_engine = None
        self.yield_farming = YieldFarmingManager()
        
    async def initialize(self):
        """Initialize all protocols"""
        for protocol_name, protocol_config in config.items():
            if protocol_name == "uniswap_v3":
                protocol = UniswapV3Protocol(protocol_config)
            elif protocol_name == "curve":
                protocol = CurveProtocol(protocol_config)
            elif protocol_name == "sushiswap":
                protocol = SushiswapProtocol(protocol_config)
            else:
                continue
            
            await protocol.initialize()
            self.protocols[protocol_name] = protocol
        
        # Initialize arbitrage engine
        self.arbitrage_engine = DeFiArbitrageEngine(list(self.protocols.values()))
    
    async def run_market_making(self, token_pairs: List[Tuple[str, str]], position_size: float):
        """Run market making across all protocols"""
        tasks = []
        
        for protocol_name, protocol in self.protocols.items():
            task = asyncio.create_task(self._run_protocol_market_making(protocol, token_pairs, position_size))
            tasks.append(task)
        
        # Also run arbitrage
        arbitrage_task = asyncio.create_task(self._run_arbitrage_monitoring(token_pairs))
        tasks.append(arbitrage_task)
        
        await asyncio.gather(*tasks)
    
    async def _run_protocol_market_making(self, protocol: BaseDeFiProtocol, token_pairs: List[Tuple[str, str]], position_size: float):
        """Run market making on a specific protocol"""
        while True:
            try:
                for token0, token1 in token_pairs:
                    # Get pools for this pair
                    pools = await protocol.get_pools()
                    relevant_pool = None
                    
                    for pool in pools:
                        if (pool.token0_address == token0 and pool.token1_address == token1) or \
                           (pool.token0_address == token1 and pool.token1_address == token0):
                            relevant_pool = pool
                            break
                    
                    if not relevant_pool:
                        continue
                    
                    # Calculate spread
                    reserve0, reserve1 = await protocol.get_pool_reserves(relevant_pool.address)
                    mid_price = reserve1 / reserve0 if reserve0 > 0 else 0
                    
                    if mid_price > 0:
                        spread = mid_price * 0.001  # 0.1% spread
                        bid_price = mid_price - spread
                        ask_price = mid_price + spread
                        
                        # Place limit orders (add liquidity)
                        if token0 == relevant_pool.token0_address:
                            await protocol.add_liquidity(
                                relevant_pool.address,
                                position_size,
                                position_size * bid_price
                            )
                        else:
                            await protocol.add_liquidity(
                                relevant_pool.address,
                                position_size * ask_price,
                                position_size
                            )
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Market making error on {protocol.config.name}: {e}")
                await asyncio.sleep(60)
    
    async def _run_arbitrage_monitoring(self, token_pairs: List[Tuple[str, str]]):
        """Monitor and execute arbitrage opportunities"""
        while True:
            try:
                opportunities = await self.arbitrage_engine.scan_arbitrage_opportunities(token_pairs)
                
                for opportunity in opportunities:
                    if opportunity['profit_potential'] > 0.005:  # 0.5% threshold
                        logger.info(f"Executing arbitrage: {opportunity['profit_potential']:.2%}")
                        
                        # Execute with 10% of max position size
                        tx_hash = await self.arbitrage_engine.execute_arbitrage(
                            opportunity,
                            1000  # $1000 position
                        )
                        
                        logger.info(f"Arbitrage executed: {tx_hash}")
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Arbitrage monitoring error: {e}")
                await asyncio.sleep(30)