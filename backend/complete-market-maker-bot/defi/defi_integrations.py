"""
DeFi Protocol Integration for Market Maker Bot
Complete integration with major DeFi protocols and yield farming
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import pandas as pd
from web3 import Web3, AsyncWeb3
from web3.middleware import geth_poa_middleware
from eth_account import Account
import eth_utils
from decimal import Decimal
import requests
import time
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeFiProtocol(Enum):
    UNISWAP_V3 = "uniswap_v3"
    SUSHISWAP = "sushiswap"
    CURVE = "curve"
    AAVE = "aave"
    COMPOUND = "compound"
    YEARN = "yearn"
    BALANCER = "balancer"
    PANCAKESWAP = "pancakeswap"
    QUICKSWAP = "quickswap"

class Chain(Enum):
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BSC = "bsc"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    AVALANCHE = "avalanche"
    FANTOM = "fantom"

@dataclass
class DeFiPosition:
    protocol: DeFiProtocol
    chain: Chain
    token0: str
    token1: Optional[str]
    amount0: Decimal
    amount1: Optional[Decimal]
    lp_tokens: Decimal
    pool_address: str
    yield_apy: float
    impermanent_loss: float
    timestamp: datetime

@dataclass
class YieldOpportunity:
    protocol: DeFiProtocol
    chain: Chain
    pool_address: str
    token0: str
    token1: Optional[str]
    apy: float
    tvl: Decimal
    volume_24h: Decimal
    fee_rate: float
    risk_score: float
    gas_estimate: float
    timestamp: datetime

@dataclass
class LendingPosition:
    protocol: DeFiProtocol
    chain: Chain
    token: str
    supplied_amount: Decimal
    borrowed_amount: Decimal
    supply_apy: float
    borrow_apy: float
    collateral_factor: float
    health_factor: float
    timestamp: datetime

class UniswapV3Integration:
    """Uniswap V3 integration for concentrated liquidity"""
    
    def __init__(self, web3: Web3, config: Dict[str, Any]):
        self.web3 = web3
        self.config = config
        self.pool_contract = None
        self.nft_manager_contract = None
        
        # Uniswap V3 contract addresses
        self.addresses = {
            'mainnet': {
                'factory': '0x1F98431c8aD98523631AE4a59f267346ea31F984',
                'router': '0xE592427A0AEce92De3Edee1F18E0157C05861564',
                'nft_manager': '0xC36442b4a4522E871399CD717aBDD847Ab11FE88',
            },
            'polygon': {
                'factory': '0x1F98431c8aD98523631AE4a59f267346ea31F984',
                'router': '0xE592427A0AEce92De3Edee1F18E0157C05861564',
                'nft_manager': '0xC36442b4a4522E871399CD717aBDD847Ab11FE88',
            }
        }
        
        # ABI definitions (simplified)
        self.pool_abi = [
            {"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"int24","name":"tickLower","type":"int24"},{"internalType":"int24","name":"tickUpper","type":"int24"},{"internalType":"uint128","name":"amount","type":"uint128"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"mint","outputs":[{"internalType":"uint256","name":"amount0","type":"uint256"},{"internalType":"uint256","name":"amount1","type":"uint256"}],"stateMutability":"payable","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"uint128","name":"liquidity","type":"uint128"},{"internalType":"uint256","name":"amount0Min","type":"uint256"},{"internalType":"uint256","name":"amount1Min","type":"uint256"},{"internalType":"address","name":"recipient","type":"address"}],"name":"collect","outputs":[{"internalType":"uint256","name":"amount0","type":"uint256"},{"internalType":"uint256","name":"amount1","type":"uint256"}],"stateMutability":"payable","type":"function"},
        ]
        
        self.nft_manager_abi = [
            {"inputs":[{"internalType":"address","name":"token0","type":"address"},{"internalType":"address","name":"token1","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"},{"internalType":"int24","name":"tickLower","type":"int24"},{"internalType":"int24","name":"tickUpper","type":"int24"},{"internalType":"uint256","name":"amount0Desired","type":"uint256"},{"internalType":"uint256","name":"amount1Desired","type":"uint256"},{"internalType":"uint256","name":"amount0Min","type":"uint256"},{"internalType":"uint256","name":"amount1Min","type":"uint256"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"mint","outputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"uint128","name":"liquidity","type":"uint128"},{"internalType":"uint256","name":"amount0","type":"uint256"},{"internalType":"uint256","name":"amount1","type":"uint256"}],"stateMutability":"payable","type":"function"},
        ]
    
    async def create_position(
        self,
        token0: str,
        token1: str,
        fee: int,
        tick_lower: int,
        tick_upper: int,
        amount0: Decimal,
        amount1: Decimal,
        recipient: str
    ) -> str:
        """Create a new liquidity position"""
        try:
            # Get NFT Manager contract
            nft_manager = self.web3.eth.contract(
                address=self.addresses['mainnet']['nft_manager'],
                abi=self.nft_manager_abi
            )
            
            # Build transaction
            transaction = nft_manager.functions.mint(
                token0,
                token1,
                fee,
                tick_lower,
                tick_upper,
                int(amount0 * 10**18),
                int(amount1 * 10**18),
                0,  # amount0Min
                0,  # amount1Min
                recipient,
                int(time.time() + 3600)  # deadline
            ).build_transaction({
                'from': self.config['address'],
                'gas': 500000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.config['address']),
            })
            
            # Sign transaction
            signed_txn = self.web3.eth.account.sign_transaction(
                transaction, 
                self.config['private_key']
            )
            
            # Send transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                # Get token ID from logs
                for log in receipt.logs:
                    if log.address == self.addresses['mainnet']['nft_manager']:
                        token_id = int(log.topics[1].hex(), 16)
                        logger.info(f"Created Uniswap V3 position with token ID: {token_id}")
                        return str(token_id)
            
            raise Exception("Transaction failed")
            
        except Exception as e:
            logger.error(f"Error creating Uniswap V3 position: {e}")
            raise
    
    async def collect_fees(self, token_id: str, recipient: str) -> Tuple[Decimal, Decimal]:
        """Collect fees from a position"""
        try:
            nft_manager = self.web3.eth.contract(
                address=self.addresses['mainnet']['nft_manager'],
                abi=self.nft_manager_abi
            )
            
            # Build collect transaction
            transaction = nft_manager.functions.collect(
                int(token_id),
                2**128 - 1,  # Max amount0
                2**128 - 1,  # Max amount1
                recipient
            ).build_transaction({
                'from': self.config['address'],
                'gas': 200000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.config['address']),
            })
            
            # Sign and send transaction
            signed_txn = self.web3.eth.account.sign_transaction(
                transaction, 
                self.config['private_key']
            )
            
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                # Parse amounts from logs
                # This would need more detailed log parsing
                logger.info(f"Collected fees for position {token_id}")
                return Decimal('0'), Decimal('0')  # Placeholder
            
            raise Exception("Collect fees transaction failed")
            
        except Exception as e:
            logger.error(f"Error collecting fees: {e}")
            raise
    
    async def get_position_info(self, token_id: str) -> Dict[str, Any]:
        """Get information about a position"""
        # This would query the NFT contract for position details
        # Simplified implementation
        return {
            'token_id': token_id,
            'liquidity': 0,
            'tick_lower': 0,
            'tick_upper': 0,
            'fee_growth_inside0_last_x128': 0,
            'fee_growth_inside1_last_x128': 0,
        }

class AaveIntegration:
    """Aave protocol integration for lending and borrowing"""
    
    def __init__(self, web3: Web3, config: Dict[str, Any]):
        self.web3 = web3
        self.config = config
        
        # Aave contract addresses
        self.addresses = {
            'mainnet': {
                'lending_pool': '0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9',
                'a_token': '0xA50ba011c48153De246E5192C8f9258A2ba79Ca9',  # Example aDAI
            }
        }
        
        # Aave ABI
        self.lending_pool_abi = [
            {"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"address","name":"onBehalfOf","type":"address"},{"internalType":"uint16","name":"referralCode","type":"uint16"}],"name":"deposit","outputs":[],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"interestRateMode","type":"uint256"},{"internalType":"uint16","name":"referralCode","type":"uint16"},{"internalType":"address","name":"onBehalfOf","type":"address"}],"name":"borrow","outputs":[],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"address","name":"onBehalfOf","type":"address"}],"name":"withdraw","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"address","name":"asset","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"address","name":"onBehalfOf","type":"address"}],"name":"repay","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
        ]
    
    async def deposit(self, token_address: str, amount: Decimal, on_behalf_of: str) -> str:
        """Deposit tokens to Aave"""
        try:
            lending_pool = self.web3.eth.contract(
                address=self.addresses['mainnet']['lending_pool'],
                abi=self.lending_pool_abi
            )
            
            # Build deposit transaction
            transaction = lending_pool.functions.deposit(
                token_address,
                int(amount * 10**18),
                on_behalf_of,
                0  # referral code
            ).build_transaction({
                'from': self.config['address'],
                'gas': 200000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.config['address']),
            })
            
            # Sign and send transaction
            signed_txn = self.web3.eth.account.sign_transaction(
                transaction, 
                self.config['private_key']
            )
            
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"Deposited {amount} tokens to Aave")
                return tx_hash.hex()
            
            raise Exception("Deposit transaction failed")
            
        except Exception as e:
            logger.error(f"Error depositing to Aave: {e}")
            raise
    
    async def borrow(
        self, 
        token_address: str, 
        amount: Decimal, 
        interest_rate_mode: int,
        on_behalf_of: str
    ) -> str:
        """Borrow tokens from Aave"""
        try:
            lending_pool = self.web3.eth.contract(
                address=self.addresses['mainnet']['lending_pool'],
                abi=self.lending_pool_abi
            )
            
            # Build borrow transaction
            transaction = lending_pool.functions.borrow(
                token_address,
                int(amount * 10**18),
                interest_rate_mode,
                0,  # referral code
                on_behalf_of
            ).build_transaction({
                'from': self.config['address'],
                'gas': 200000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.config['address']),
            })
            
            # Sign and send transaction
            signed_txn = self.web3.eth.account.sign_transaction(
                transaction, 
                self.config['private_key']
            )
            
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"Borrowed {amount} tokens from Aave")
                return tx_hash.hex()
            
            raise Exception("Borrow transaction failed")
            
        except Exception as e:
            logger.error(f"Error borrowing from Aave: {e}")
            raise
    
    async def get_user_data(self, user_address: str) -> Dict[str, Any]:
        """Get user's lending and borrowing data"""
        try:
            lending_pool = self.web3.eth.contract(
                address=self.addresses['mainnet']['lending_pool'],
                abi=self.lending_pool_abi
            )
            
            # Get user account data
            user_data = lending_pool.functions.getUserAccountData(user_address).call()
            
            return {
                'total_collateral_eth': user_data[0],
                'total_debt_eth': user_data[1],
                'available_borrows_eth': user_data[2],
                'current_liquidation_threshold': user_data[3],
                'ltv': user_data[4],
                'health_factor': user_data[5],
            }
            
        except Exception as e:
            logger.error(f"Error getting user data from Aave: {e}")
            raise

class CurveIntegration:
    """Curve Finance integration for stablecoin trading"""
    
    def __init__(self, web3: Web3, config: Dict[str, Any]):
        self.web3 = web3
        self.config = config
        
        # Curve pool addresses
        self.pools = {
            '3pool': '0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7',
            'steth': '0xDC24316b9AE028F1497c275EB9192a3Ea0f67022',
        }
        
        # Curve ABI
        self.pool_abi = [
            {"inputs":[{"internalType":"uint256","name":"i","type":"uint256"},{"internalType":"uint256","name":"j","type":"uint256"},{"internalType":"uint256","name":"dx","type":"uint256"},{"internalType":"uint256","name":"min_dy","type":"uint256"}],"name":"exchange","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"},{"internalType":"uint256","name":"min_mint_amount","type":"uint256"}],"name":"add_liquidity","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
            {"inputs":[{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"uint256[]","name":"min_amounts","type":"uint256[]"}],"name":"remove_liquidity","outputs":[{"internalType":"uint256[]","name":"","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},
        ]
    
    async def add_liquidity(
        self, 
        pool_name: str, 
        amounts: List[Decimal], 
        min_mint_amount: Decimal
    ) -> str:
        """Add liquidity to Curve pool"""
        try:
            pool_address = self.pools.get(pool_name)
            if not pool_address:
                raise ValueError(f"Pool {pool_name} not found")
            
            pool_contract = self.web3.eth.contract(
                address=pool_address,
                abi=self.pool_abi
            )
            
            # Convert amounts to wei
            amounts_wei = [int(amount * 10**18) for amount in amounts]
            
            # Build transaction
            transaction = pool_contract.functions.add_liquidity(
                amounts_wei,
                int(min_mint_amount * 10**18)
            ).build_transaction({
                'from': self.config['address'],
                'gas': 500000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.config['address']),
            })
            
            # Sign and send transaction
            signed_txn = self.web3.eth.account.sign_transaction(
                transaction, 
                self.config['private_key']
            )
            
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"Added liquidity to Curve {pool_name} pool")
                return tx_hash.hex()
            
            raise Exception("Add liquidity transaction failed")
            
        except Exception as e:
            logger.error(f"Error adding liquidity to Curve: {e}")
            raise

class DeFiManager:
    """Main DeFi protocol manager"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.web3_connections = {}
        self.protocol_integrations = {}
        self.positions = []
        self.opportunities = []
        
    async def initialize(self):
        """Initialize all Web3 connections and protocol integrations"""
        # Initialize Web3 connections for each chain
        chain_rpcs = {
            'ethereum': 'https://mainnet.infura.io/v3/' + self.config.get('infura_key', ''),
            'polygon': 'https://polygon-mainnet.infura.io/v3/' + self.config.get('infura_key', ''),
            'bsc': 'https://bsc-dataseed.binance.org/',
            'arbitrum': 'https://arb1.arbitrum.io/rpc',
        }
        
        for chain, rpc_url in chain_rpcs.items():
            web3 = Web3(Web3.HTTPProvider(rpc_url))
            if chain == 'polygon':
                web3.middleware_onion.inject(geth_poa_middleware, layer=0)
            
            self.web3_connections[chain] = web3
        
        # Initialize protocol integrations
        self.protocol_integrations[DeFiProtocol.UNISWAP_V3] = UniswapV3Integration(
            self.web3_connections['ethereum'], self.config
        )
        
        self.protocol_integrations[DeFiProtocol.AAVE] = AaveIntegration(
            self.web3_connections['ethereum'], self.config
        )
        
        self.protocol_integrations[DeFiProtocol.CURVE] = CurveIntegration(
            self.web3_connections['ethereum'], self.config
        )
        
        logger.info("DeFi Manager initialized")
    
    async def scan_yield_opportunities(self) -> List[YieldOpportunity]:
        """Scan for yield opportunities across protocols"""
        opportunities = []
        
        # Scan Uniswap V3 pools
        uniswap_opportunities = await self._scan_uniswap_opportunities()
        opportunities.extend(uniswap_opportunities)
        
        # Scan Aave lending rates
        aave_opportunities = await self._scan_aave_opportunities()
        opportunities.extend(aave_opportunities)
        
        # Scan Curve pools
        curve_opportunities = await self._scan_curve_opportunities()
        opportunities.extend(curve_opportunities)
        
        # Sort by APY
        opportunities.sort(key=lambda x: x.apy, reverse=True)
        
        self.opportunities = opportunities
        return opportunities
    
    async def _scan_uniswap_opportunities(self) -> List[YieldOpportunity]:
        """Scan Uniswap V3 for yield opportunities"""
        opportunities = []
        
        # Mock data - in practice, fetch from Uniswap subgraph
        pools_data = [
            {
                'address': '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640',
                'token0': 'USDC',
                'token1': 'WETH',
                'fee': 500,
                'apy': 0.12,
                'tvl': Decimal('50000000'),
                'volume_24h': Decimal('10000000'),
            },
            {
                'address': '0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8',
                'token0': 'USDC',
                'token1': 'USDT',
                'fee': 100,
                'apy': 0.08,
                'tvl': Decimal('200000000'),
                'volume_24h': Decimal('50000000'),
            }
        ]
        
        for pool_data in pools_data:
            opportunity = YieldOpportunity(
                protocol=DeFiProtocol.UNISWAP_V3,
                chain=Chain.ETHEREUM,
                pool_address=pool_data['address'],
                token0=pool_data['token0'],
                token1=pool_data['token1'],
                apy=pool_data['apy'],
                tvl=pool_data['tvl'],
                volume_24h=pool_data['volume_24h'],
                fee_rate=pool_data['fee'] / 1000000,
                risk_score=self._calculate_risk_score(pool_data),
                gas_estimate=0.01,  # ETH
                timestamp=datetime.now()
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    async def _scan_aave_opportunities(self) -> List[YieldOpportunity]:
        """Scan Aave for lending opportunities"""
        opportunities = []
        
        # Mock data - in practice, fetch from Aave API
        assets_data = [
            {
                'symbol': 'USDC',
                'address': '0xA0b86a33E6441b8e8C7C7b0b8e8e8e8e8e8e8e8e',
                'supply_apy': 0.04,
                'stable_borrow_apy': 0.06,
                'variable_borrow_apy': 0.08,
                'liquidity': Decimal('100000000'),
            },
            {
                'symbol': 'WETH',
                'address': '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1',
                'supply_apy': 0.02,
                'stable_borrow_apy': 0.04,
                'variable_borrow_apy': 0.05,
                'liquidity': Decimal('50000000'),
            }
        ]
        
        for asset in assets_data:
            opportunity = YieldOpportunity(
                protocol=DeFiProtocol.AAVE,
                chain=Chain.ETHEREUM,
                pool_address=asset['address'],
                token0=asset['symbol'],
                token1=None,
                apy=asset['supply_apy'],
                tvl=asset['liquidity'],
                volume_24h=Decimal('0'),
                fee_rate=0,
                risk_score=self._calculate_risk_score(asset),
                gas_estimate=0.005,
                timestamp=datetime.now()
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    async def _scan_curve_opportunities(self) -> List[YieldOpportunity]:
        """Scan Curve for stablecoin opportunities"""
        opportunities = []
        
        # Mock data
        pools_data = [
            {
                'name': '3pool',
                'address': '0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7',
                'apy': 0.06,
                'tvl': Decimal('300000000'),
                'volume_24h': Decimal('20000000'),
                'coins': ['USDC', 'USDT', 'DAI'],
            }
        ]
        
        for pool_data in pools_data:
            opportunity = YieldOpportunity(
                protocol=DeFiProtocol.CURVE,
                chain=Chain.ETHEREUM,
                pool_address=pool_data['address'],
                token0='.'.join(pool_data['coins']),
                token1=None,
                apy=pool_data['apy'],
                tvl=pool_data['tvl'],
                volume_24h=pool_data['volume_24h'],
                fee_rate=0.0004,
                risk_score=self._calculate_risk_score(pool_data),
                gas_estimate=0.008,
                timestamp=datetime.now()
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    def _calculate_risk_score(self, pool_data: Dict[str, Any]) -> float:
        """Calculate risk score for a pool"""
        # Simple risk calculation based on TVL and volatility
        tvl = float(pool_data.get('tvl', 0))
        
        if tvl > 100000000:  # > $100M
            base_risk = 0.2
        elif tvl > 10000000:  # > $10M
            base_risk = 0.4
        else:
            base_risk = 0.6
        
        # Adjust for asset type
        if 'stable' in str(pool_data).lower():
            base_risk *= 0.5
        
        return min(base_risk, 1.0)
    
    async def execute_yield_strategy(self, amount: Decimal, risk_tolerance: float) -> List[DeFiPosition]:
        """Execute automated yield farming strategy"""
        positions = []
        
        # Get opportunities
        opportunities = await self.scan_yield_opportunities()
        
        # Filter based on risk tolerance
        filtered_opportunities = [
            opp for opp in opportunities 
            if opp.risk_score <= risk_tolerance
        ]
        
        # Allocate capital
        allocation_amount = amount / len(filtered_opportunities)
        
        for opportunity in filtered_opportunities[:3]:  # Limit to top 3
            try:
                position = await self._create_position(opportunity, allocation_amount)
                positions.append(position)
                logger.info(f"Created position in {opportunity.protocol.value}")
            except Exception as e:
                logger.error(f"Failed to create position: {e}")
        
        self.positions.extend(positions)
        return positions
    
    async def _create_position(self, opportunity: YieldOpportunity, amount: Decimal) -> DeFiPosition:
        """Create a position based on opportunity"""
        if opportunity.protocol == DeFiProtocol.UNISWAP_V3:
            # Create Uniswap V3 position
            integration = self.protocol_integrations[DeFiProtocol.UNISWAP_V3]
            
            # Simplified - would need proper tick calculation
            token_id = await integration.create_position(
                opportunity.token0,
                opportunity.token1 or 'WETH',
                3000,  # 0.3% fee
                -60720,  # tick lower (simplified)
                60720,   # tick upper (simplified)
                amount / 2,
                amount / 2,
                self.config['address']
            )
            
            return DeFiPosition(
                protocol=opportunity.protocol,
                chain=opportunity.chain,
                token0=opportunity.token0,
                token1=opportunity.token1,
                amount0=amount / 2,
                amount1=amount / 2,
                lp_tokens=Decimal('0'),
                pool_address=opportunity.pool_address,
                yield_apy=opportunity.apy,
                impermanent_loss=0.0,
                timestamp=datetime.now()
            )
        
        elif opportunity.protocol == DeFiProtocol.AAVE:
            # Supply to Aave
            integration = self.protocol_integrations[DeFiProtocol.AAVE]
            
            # Mock token address
            token_address = '0xA0b86a33E6441b8e8C7C7b0b8e8e8e8e8e8e8e8e'
            
            tx_hash = await integration.deposit(
                token_address,
                amount,
                self.config['address']
            )
            
            return DeFiPosition(
                protocol=opportunity.protocol,
                chain=opportunity.chain,
                token0=opportunity.token0,
                token1=None,
                amount0=amount,
                amount1=None,
                lp_tokens=Decimal('0'),
                pool_address=opportunity.pool_address,
                yield_apy=opportunity.apy,
                impermanent_loss=0.0,
                timestamp=datetime.now()
            )
        
        else:
            raise ValueError(f"Protocol {opportunity.protocol} not implemented")
    
    async def rebalance_positions(self) -> List[str]:
        """Rebalance positions based on current opportunities"""
        changes = []
        
        # Get current positions and opportunities
        current_positions = self.positions
        opportunities = await self.scan_yield_opportunities()
        
        # Check for underperforming positions
        for position in current_positions:
            current_opp = next(
                (opp for opp in opportunities 
                 if opp.protocol == position.protocol and opp.pool_address == position.pool_address),
                None
            )
            
            if current_opp and current_opp.apy < position.yield_apy * 0.8:
                # Position is underperforming significantly
                changes.append(f"Consider exiting position in {position.protocol.value}")
        
        return changes
    
    async def calculate_impermanent_loss(self, position: DeFiPosition) -> float:
        """Calculate impermanent loss for a position"""
        if position.token1 is None:
            return 0.0  # No impermanent loss for single-sided positions
        
        # Get current prices
        price_ratio = self._get_price_ratio(position.token0, position.token1)
        initial_ratio = position.amount0 / position.amount1
        
        if price_ratio == 0:
            return 0.0
        
        # Calculate impermanent loss
        price_change = price_ratio / initial_ratio
        impermanent_loss = 2 * math.sqrt(price_change) / (1 + price_change) - 1
        
        return impermanent_loss
    
    def _get_price_ratio(self, token0: str, token1: str) -> float:
        """Get price ratio between two tokens"""
        # Mock implementation
        prices = {
            'USDC': 1.0,
            'USDT': 1.0,
            'DAI': 1.0,
            'WETH': 2000.0,
            'WBTC': 50000.0,
        }
        
        price0 = prices.get(token0, 1.0)
        price1 = positions.get(token1, 1.0)
        
        return price0 / price1 if price1 != 0 else 0.0
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get summary of all DeFi positions"""
        if not self.positions:
            return {
                'total_positions': 0,
                'total_value': Decimal('0'),
                'average_apy': 0.0,
                'positions_by_protocol': {},
            }
        
        total_value = sum(pos.amount0 + (pos.amount1 or 0) for pos in self.positions)
        weighted_apy = sum(pos.yield_apy * float(pos.amount0 + (pos.amount1 or 0)) for pos in self.positions)
        average_apy = weighted_apy / float(total_value) if total_value > 0 else 0.0
        
        positions_by_protocol = {}
        for position in self.positions:
            protocol = position.protocol.value
            if protocol not in positions_by_protocol:
                positions_by_protocol[protocol] = 0
            positions_by_protocol[protocol] += 1
        
        return {
            'total_positions': len(self.positions),
            'total_value': total_value,
            'average_apy': average_apy,
            'positions_by_protocol': positions_by_protocol,
        }

# Main execution
async def main():
    # Configuration
    config = {
        'address': '0xYourAddress',
        'private_key': 'your_private_key',
        'infura_key': 'your_infura_key',
    }
    
    # Initialize DeFi manager
    defi_manager = DeFiManager(config)
    await defi_manager.initialize()
    
    # Scan for opportunities
    opportunities = await defi_manager.scan_yield_opportunities()
    logger.info(f"Found {len(opportunities)} yield opportunities")
    
    # Execute yield strategy
    positions = await defi_manager.execute_yield_strategy(
        Decimal('10000'),  # $10,000
        0.5  # Medium risk tolerance
    )
    logger.info(f"Created {len(positions)} positions")
    
    # Get portfolio summary
    summary = defi_manager.get_portfolio_summary()
    logger.info(f"Portfolio summary: {summary}")

if __name__ == "__main__":
    asyncio.run(main())