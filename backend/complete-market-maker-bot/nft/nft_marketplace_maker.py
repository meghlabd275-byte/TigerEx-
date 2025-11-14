"""
NFT Marketplace Making System
Automated NFT trading, floor price tracking, and portfolio management
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
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
import requests
import time
from decimal import Decimal
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NFTMarketplace(Enum):
    OPENSEA = "opensea"
    LOOKSRARE = "looksrare"
    X2Y2 = "x2y2"
    BLUR = "blur"
    MAGICEDEN = "magiceden"
    SUDOSWAP = "sudoswap"

class Chain(Enum):
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    SOLANA = "solana"
    BSC = "bsc"
    ARBITRUM = "arbitrum"

class RarityLevel(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

@dataclass
class NFTAsset:
    token_id: str
    collection_address: str
    marketplace: NFTMarketplace
    chain: Chain
    name: str
    description: str
    image_url: str
    attributes: List[Dict[str, Any]]
    rarity_score: float
    rarity_rank: int
    floor_price: float
    current_price: Optional[float]
    last_sale_price: Optional[float]
    last_sale_date: Optional[datetime]
    owner: str
    created_date: datetime
    metadata: Dict[str, Any]

@dataclass
class NFTCollection:
    address: str
    name: str
    symbol: str
    description: str
    image_url: str
    total_supply: int
    floor_price: float
    volume_24h: float
    volume_7d: float
    market_cap: float
    holders_count: int
    average_price: float
    price_change_24h: float
    listed_count: int
    royalty_fee: float
    chain: Chain
    created_date: datetime
    verification_status: str

@dataclass
class NFTOrder:
    order_id: str
    collection_address: str
    token_id: Optional[str]
    marketplace: NFTMarketplace
    order_type: str  # 'bid' or 'ask'
 price: float
    quantity: int
    expiration_time: datetime
    maker: str
    taker: Optional[str]
    status: str  # 'active', 'filled', 'cancelled'
    created_time: datetime
    metadata: Dict[str, Any]

@dataclass
class NFTPortfolio:
    total_value: float
    total_assets: int
    collections: Dict[str, Dict[str, Any]]
    profit_loss: float
    profit_loss_percentage: float
    acquisitions: List[Dict[str, Any]]
    sales: List[Dict[str, Any]]
    last_updated: datetime

class OpenSeaIntegration:
    """OpenSea API integration for NFT marketplace making"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.opensea.io/v2"
        self.headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
    
    async def get_collection(self, collection_slug: str, chain: str = "ethereum") -> NFTCollection:
        """Get collection information"""
        url = f"{self.base_url}/collections/{collection_slug}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    collection_data = data['collection']
                    
                    return NFTCollection(
                        address=collection_data.get('contract_address', ''),
                        name=collection_data.get('name', ''),
                        symbol=collection_data.get('collection_slug', ''),
                        description=collection_data.get('description', ''),
                        image_url=collection_data.get('image_url', ''),
                        total_supply=collection_data.get('total_supply', 0),
                        floor_price=float(collection_data.get('floor_price', 0)),
                        volume_24h=float(collection_data.get('stats', {}).get('one_day_volume', 0)),
                        volume_7d=float(collection_data.get('stats', {}).get('seven_day_volume', 0)),
                        market_cap=float(collection_data.get('stats', {}).get('market_cap', 0)),
                        holders_count=collection_data.get('stats', {}).get('num_owners', 0),
                        average_price=float(collection_data.get('stats', {}).get('average_price', 0)),
                        price_change_24h=float(collection_data.get('stats', {}).get('one_day_change', 0)),
                        listed_count=collection_data.get('stats', {}).get('num_reports', 0),
                        royalty_fee=float(collection_data.get('dev_seller_fee_basis_points', 0)) / 100,
                        chain=Chain(chain),
                        created_date=datetime.now(),  # Would parse from actual data
                        verification_status=collection_data.get('safelist_request_status', '')
                    )
                else:
                    raise Exception(f"Failed to get collection: {response.status}")
    
    async def get_nft_asset(self, collection_slug: str, token_id: str, chain: str = "ethereum") -> NFTAsset:
        """Get NFT asset information"""
        url = f"{self.base_url}/collection/{collection_slug}/nfts/{token_id}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    nft_data = data['nft']
                    
                    return NFTAsset(
                        token_id=nft_data.get('identifier', ''),
                        collection_address=nft_data.get('contract', ''),
                        marketplace=NFTMarketplace.OPENSEA,
                        chain=Chain(chain),
                        name=nft_data.get('name', ''),
                        description=nft_data.get('description', ''),
                        image_url=nft_data.get('image_url', ''),
                        attributes=nft_data.get('traits', []),
                        rarity_score=0.0,  # Would calculate
                        rarity_rank=0,    # Would calculate
                        floor_price=0.0,   # Would get from collection
                        current_price=None,
                        last_sale_price=None,
                        last_sale_date=None,
                        owner=nft_data.get('owner', ''),
                        created_date=datetime.now(),  # Would parse from actual data
                        metadata=nft_data.get('metadata', {})
                    )
                else:
                    raise Exception(f"Failed to get NFT asset: {response.status}")
    
    async def get_orders(self, collection_slug: str, side: str = "ask", limit: int = 50) -> List[NFTOrder]:
        """Get orders for a collection"""
        url = f"{self.base_url}/listings/collection/{collection_slug}/all"
        
        params = {
            'limit': limit,
            'side': side
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    orders = []
                    
                    for order_data in data.get('listings', []):
                        order = NFTOrder(
                            order_id=order_data.get('order_hash', ''),
                            collection_address=order_data.get('contract', ''),
                            token_id=order_data.get('token_id', ''),
                            marketplace=NFTMarketplace.OPENSEA,
                            order_type=order_data.get('side', 'ask'),
                            price=float(order_data.get('price', {}).get('current', {}).get('value', 0)),
                            quantity=1,
                            expiration_time=datetime.fromisoformat(order_data.get('expiration_date', '').replace('Z', '+00:00')),
                            maker=order_data.get('maker', ''),
                            taker=None,
                            status=order_data.get('status', 'active'),
                            created_time=datetime.fromisoformat(order_data.get('created_date', '').replace('Z', '+00:00')),
                            metadata=order_data
                        )
                        orders.append(order)
                    
                    return orders
                else:
                    raise Exception(f"Failed to get orders: {response.status}")
    
    async def place_bid(self, collection_slug: str, token_id: str, amount: float, expiration_time: datetime) -> str:
        """Place a bid on an NFT"""
        # This would integrate with OpenSea's order protocol
        # Simplified implementation
        url = f"{self.base_url}/offers"
        
        payload = {
            "protocol": "seaport",
            "protocol_data": {
                "parameters": {
                    "offerer": self.maker_address,
                    "offer": [
                        {
                            "token": "0x0000000000000000000000000000000000000000",
                            "identifierOrCriteria": str(int(amount * 1e18)),
                            "startAmount": str(int(amount * 1e18)),
                            "endAmount": str(int(amount * 1e18))
                        }
                    ],
                    "consideration": [
                        {
                            "token": collection_slug,
                            "identifierOrCriteria": token_id,
                            "startAmount": "1",
                            "endAmount": "1"
                        }
                    ],
                    "endTime": int(expiration_time.timestamp()),
                    "zone": "0x0000000000000000000000000000000000000000",
                    "zoneHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
                    "salt": "0x0000000000000000000000000000000000000000000000000000000000000000",
                    "conduitKey": "0x0000000000000000000000000000000000000000000000000000000000000000",
                    "totalOriginalConsiderationItems": 1,
                    "counter": 0
                }
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('order_hash', '')
                else:
                    raise Exception(f"Failed to place bid: {response.status}")

class RarityCalculator:
    """Calculate NFT rarity scores and rankings"""
    
    def __init__(self):
        self.trait_weights = {
            'background': 0.1,
            'clothes': 0.2,
            'eyes': 0.15,
            'fur': 0.15,
            'mouth': 0.1,
            'hat': 0.1,
            'special': 0.2
        }
    
    def calculate_rarity_score(self, attributes: List[Dict[str, Any]], collection_stats: Dict[str, Any]) -> float:
        """Calculate rarity score for an NFT"""
        total_score = 0.0
        
        for trait in attributes:
            trait_type = trait.get('trait_type', '').lower()
            trait_value = trait.get('value', '')
            
            # Get trait rarity from collection stats
            trait_rarity = self._get_trait_rarity(trait_type, trait_value, collection_stats)
            
            # Apply weight
            weight = self.trait_weights.get(trait_type, 0.1)
            trait_score = (1.0 / trait_rarity) * weight
            total_score += trait_score
        
        return total_score
    
    def _get_trait_rarity(self, trait_type: str, trait_value: str, collection_stats: Dict[str, Any]) -> float:
        """Get rarity percentage for a specific trait"""
        # Mock implementation - would use actual collection stats
        trait_rarities = {
            ('background', 'blue'): 0.15,
            ('background', 'red'): 0.05,
            ('clothes', 'shirt'): 0.20,
            ('clothes', 'hoodie'): 0.08,
            ('eyes', 'normal'): 0.30,
            ('eyes', 'laser'): 0.02,
            ('fur', 'brown'): 0.25,
            ('fur', 'golden'): 0.01,
        }
        
        return trait_rarities.get((trait_type, trait_value), 0.1)
    
    def get_rarity_level(self, rarity_score: float) -> RarityLevel:
        """Determine rarity level based on score"""
        if rarity_score > 50:
            return RarityLevel.LEGENDARY
        elif rarity_score > 25:
            return RarityLevel.EPIC
        elif rarity_score > 15:
            return RarityLevel.RARE
        elif rarity_score > 8:
            return RarityLevel.UNCOMMON
        else:
            return RarityLevel.COMMON

class NFTMarketMaker:
    """Automated NFT market making system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.integrations = {}
        self.portfolio = NFTPortfolio(
            total_value=0.0,
            total_assets=0,
            collections={},
            profit_loss=0.0,
            profit_loss_percentage=0.0,
            acquisitions=[],
            sales=[],
            last_updated=datetime.now()
        )
        self.rarity_calculator = RarityCalculator()
        self.active_orders = []
        self.pricing_model = None
        
        # Initialize integrations
        if 'opensea_api_key' in config:
            self.integrations[NFTMarketplace.OPENSEA] = OpenSeaIntegration(config['opensea_api_key'])
    
    async def initialize(self):
        """Initialize the market maker"""
        logger.info("Initializing NFT Market Maker")
        
        # Initialize pricing model
        await self._initialize_pricing_model()
        
        # Load current portfolio
        await self._load_portfolio()
        
        logger.info("NFT Market Maker initialized")
    
    async def _initialize_pricing_model(self):
        """Initialize pricing model for NFT valuation"""
        # This would train a machine learning model on historical NFT sales
        # Simplified implementation using heuristic rules
        self.pricing_model = {
            'base_multiplier': 1.0,
            'rarity_multipliers': {
                RarityLevel.COMMON: 0.8,
                RarityLevel.UNCOMMON: 1.0,
                RarityLevel.RARE: 1.5,
                RarityLevel.EPIC: 2.5,
                RarityLevel.LEGENDARY: 5.0
            },
            'trait_premium': 0.1,
            'floor_discount': 0.05,
            'profit_margin': 0.15
        }
    
    async def _load_portfolio(self):
        """Load current NFT portfolio"""
        # This would fetch from database or blockchain
        # Mock implementation
        self.portfolio.collections = {
            'boredapeyachtclub': {
                'count': 5,
                'total_value': 500.0,
                'average_cost': 80.0,
                'current_value': 100.0
            }
        }
        
        self.portfolio.total_assets = sum(coll['count'] for coll in self.portfolio.collections.values())
        self.portfolio.total_value = sum(coll['total_value'] for coll in self.portfolio.collections.values())
    
    async def scan_opportunities(self, marketplaces: List[NFTMarketplace] = None) -> List[Dict[str, Any]]:
        """Scan for profitable NFT opportunities"""
        if marketplaces is None:
            marketplaces = [NFTMarketplace.OPENSEA]
        
        opportunities = []
        
        for marketplace in marketplaces:
            if marketplace in self.integrations:
                opps = await self._scan_marketplace_opportunities(marketplace)
                opportunities.extend(opps)
        
        # Sort by expected profit
        opportunities.sort(key=lambda x: x.get('expected_profit', 0), reverse=True)
        
        return opportunities
    
    async def _scan_marketplace_opportunities(self, marketplace: NFTMarketplace) -> List[Dict[str, Any]]:
        """Scan a specific marketplace for opportunities"""
        integration = self.integrations[marketplace]
        opportunities = []
        
        # Get popular collections
        popular_collections = await self._get_popular_collections(marketplace)
        
        for collection in popular_collections[:10]:  # Limit to top 10
            try:
                # Get collection data
                collection_data = await integration.get_collection(collection['slug'])
                
                # Analyze collection for opportunities
                collection_opps = await self._analyze_collection_opportunities(collection_data, marketplace)
                opportunities.extend(collection_opps)
                
            except Exception as e:
                logger.error(f"Error analyzing collection {collection['slug']}: {e}")
        
        return opportunities
    
    async def _get_popular_collections(self, marketplace: NFTMarketplace) -> List[Dict[str, Any]]:
        """Get popular collections from marketplace"""
        # Mock data - would fetch from marketplace API
        return [
            {'slug': 'boredapeyachtclub', 'name': 'Bored Ape Yacht Club'},
            {'slug': 'mutant-ape-yacht-club', 'name': 'Mutant Ape Yacht Club'},
            {'slug': 'azuki', 'name': 'Azuki'},
            {'slug': 'doodles-official', 'name': 'Doodles'},
            {'slug': 'clonex', 'name': 'CloneX'},
        ]
    
    async def _analyze_collection_opportunities(self, collection: NFTCollection, marketplace: NFTMarketplace) -> List[Dict[str, Any]]:
        """Analyze a collection for trading opportunities"""
        opportunities = []
        
        # Check for undervalued listings
        undervalued = await self._find_undervalued_listings(collection, marketplace)
        opportunities.extend(undervalued)
        
        # Check for floor price arbitrage
        arbitrage = await self._find_floor_arbitrage(collection, marketplace)
        opportunities.extend(arbitrage)
        
        # Check for rarity-based opportunities
        rarity_opps = await self._find_rarity_opportunities(collection, marketplace)
        opportunities.extend(rarity_opps)
        
        return opportunities
    
    async def _find_undervalued_listings(self, collection: NFTCollection, marketplace: NFTMarketplace) -> List[Dict[str, Any]]:
        """Find undervalued NFT listings"""
        undervalued = []
        
        try:
            # Get recent orders
            orders = await self.integrations[marketplace].get_orders(collection.symbol, side="ask", limit=20)
            
            for order in orders[:5]:  # Analyze top 5 listings
                # Get NFT details
                asset = await self.integrations[marketplace].get_nft_asset(collection.symbol, order.token_id)
                
                # Calculate fair value
                fair_value = await self._calculate_fair_value(asset, collection)
                
                if order.price < fair_value * 0.9:  # 10% discount
                    expected_profit = fair_value - order.price
                    profit_margin = expected_profit / order.price
                    
                    undervalued.append({
                        'type': 'undervalued_listing',
                        'asset': asset,
                        'order': order,
                        'fair_value': fair_value,
                        'expected_profit': expected_profit,
                        'profit_margin': profit_margin,
                        'marketplace': marketplace,
                        'confidence': min(0.9, profit_margin * 2)
                    })
        
        except Exception as e:
            logger.error(f"Error finding undervalued listings: {e}")
        
        return undervalued
    
    async def _find_floor_arbitrage(self, collection: NFTCollection, marketplace: NFTMarketplace) -> List[Dict[str, Any]]:
        """Find floor price arbitrage opportunities"""
        opportunities = []
        
        # Simple floor price arbitrage detection
        if collection.price_change_24h < -0.1:  # 10% drop in 24h
            # Potential opportunity if drop is temporary
            expected_recovery = abs(collection.price_change_24h) * 0.5
            expected_profit = collection.floor_price * expected_recovery
            
            opportunities.append({
                'type': 'floor_arbitrage',
                'collection': collection,
                'entry_price': collection.floor_price,
                'expected_profit': expected_profit,
                'profit_margin': expected_recovery,
                'marketplace': marketplace,
                'confidence': 0.6,
                'strategy': 'buy_floor_wait_recovery'
            })
        
        return opportunities
    
    async def _find_rarity_opportunities(self, collection: NFTCollection, marketplace: NFTMarketplace) -> List[Dict[str, Any]]:
        """Find opportunities based on NFT rarity"""
        opportunities = []
        
        # Get orders and analyze for rare traits
        try:
            orders = await self.integrations[marketplace].get_orders(collection.symbol, side="ask", limit=50)
            
            for order in orders:
                asset = await self.integrations[marketplace].get_nft_asset(collection.symbol, order.token_id)
                
                # Calculate rarity score
                rarity_score = self.rarity_calculator.calculate_rarity_score(
                    asset.attributes, {}
                )
                rarity_level = self.rarity_calculator.get_rarity_level(rarity_score)
                
                # Check if rare NFT is priced low
                rarity_multiplier = self.pricing_model['rarity_multipliers'][rarity_level]
                expected_price = collection.floor_price * rarity_multiplier
                
                if order.price < expected_price * 0.8:  # 20% discount for rarity
                    expected_profit = expected_price - order.price
                    profit_margin = expected_profit / order.price
                    
                    opportunities.append({
                        'type': 'rarity_opportunity',
                        'asset': asset,
                        'order': order,
                        'rarity_score': rarity_score,
                        'rarity_level': rarity_level,
                        'expected_price': expected_price,
                        'expected_profit': expected_profit,
                        'profit_margin': profit_margin,
                        'marketplace': marketplace,
                        'confidence': min(0.8, rarity_score / 10)
                    })
        
        except Exception as e:
            logger.error(f"Error finding rarity opportunities: {e}")
        
        return opportunities
    
    async def _calculate_fair_value(self, asset: NFTAsset, collection: NFTCollection) -> float:
        """Calculate fair value for an NFT"""
        base_value = collection.floor_price
        
        # Apply rarity multiplier
        rarity_score = self.rarity_calculator.calculate_rarity_score(asset.attributes, {})
        rarity_level = self.rarity_calculator.get_rarity_level(rarity_score)
        rarity_multiplier = self.pricing_model['rarity_multipliers'][rarity_level]
        
        # Check for special traits
        trait_premium = 0.0
        for trait in asset.attributes:
            if trait.get('trait_type') == 'special':
                trait_premium += self.pricing_model['trait_premium']
        
        fair_value = base_value * self.pricing_model['base_multiplier'] * rarity_multiplier * (1 + trait_premium)
        
        return fair_value
    
    async def execute_trading_strategy(self, max_investment: float, risk_tolerance: float) -> List[str]:
        """Execute automated trading strategy"""
        executed_trades = []
        
        # Scan for opportunities
        opportunities = await self.scan_opportunities()
        
        # Filter by risk tolerance and confidence
        filtered_opps = [
            opp for opp in opportunities 
            if opp.get('confidence', 0) > risk_tolerance and opp.get('expected_profit', 0) > 0
        ]
        
        total_invested = 0.0
        
        for opportunity in filtered_opps:
            if total_invested >= max_investment:
                break
            
            try:
                trade_id = await self._execute_opportunity(opportunity, max_investment - total_invested)
                if trade_id:
                    executed_trades.append(trade_id)
                    
                    # Update investment amount
                    if opportunity['type'] in ['undervalued_listing', 'rarity_opportunity']:
                        total_invested += opportunity['order'].price
                    
                    logger.info(f"Executed trade: {opportunity['type']}")
                    
            except Exception as e:
                logger.error(f"Failed to execute opportunity {opportunity['type']}: {e}")
        
        return executed_trades
    
    async def _execute_opportunity(self, opportunity: Dict[str, Any], budget: float) -> Optional[str]:
        """Execute a specific trading opportunity"""
        if opportunity['type'] == 'undervalued_listing':
            return await self._buy_undervalued_nft(opportunity, budget)
        elif opportunity['type'] == 'rarity_opportunity':
            return await self._buy_rare_nft(opportunity, budget)
        elif opportunity['type'] == 'floor_arbitrage':
            return await self._execute_floor_arbitrage(opportunity, budget)
        else:
            logger.warning(f"Unknown opportunity type: {opportunity['type']}")
            return None
    
    async def _buy_undervalued_nft(self, opportunity: Dict[str, Any], budget: float) -> Optional[str]:
        """Buy an undervalued NFT"""
        order = opportunity['order']
        
        if order.price > budget:
            return None
        
        try:
            # Execute purchase through marketplace
            # This would integrate with the marketplace's purchase API
            trade_id = f"buy_{order.token_id}_{int(time.time())}"
            
            # Record acquisition
            self.portfolio.acquisitions.append({
                'trade_id': trade_id,
                'token_id': order.token_id,
                'collection': opportunity['asset'].collection_address,
                'price': order.price,
                'timestamp': datetime.now(),
                'type': 'undervalued_listing'
            })
            
            return trade_id
            
        except Exception as e:
            logger.error(f"Failed to buy undervalued NFT: {e}")
            return None
    
    async def _buy_rare_nft(self, opportunity: Dict[str, Any], budget: float) -> Optional[str]:
        """Buy a rare NFT"""
        return await self._buy_undervalued_nft(opportunity, budget)
    
    async def _execute_floor_arbitrage(self, opportunity: Dict[str, Any], budget: float) -> Optional[str]:
        """Execute floor price arbitrage strategy"""
        # This would implement buying multiple floor NFTs
        collection = opportunity['collection']
        num_to_buy = min(5, int(budget / collection.floor_price))
        
        trade_id = f"floor_arbitrage_{collection.symbol}_{num_to_buy}_{int(time.time())}"
        
        # Record acquisition
        self.portfolio.acquisitions.append({
            'trade_id': trade_id,
            'collection': collection.address,
            'num_tokens': num_to_buy,
            'average_price': collection.floor_price,
            'total_cost': num_to_buy * collection.floor_price,
            'timestamp': datetime.now(),
            'type': 'floor_arbitrage'
        })
        
        return trade_id
    
    async def place_bids_automatically(self, collection_slugs: List[str], bid_percentage: float = 0.8) -> List[str]:
        """Automatically place bids on collections"""
        placed_bids = []
        
        for slug in collection_slugs:
            try:
                # Get collection data
                collection = await self.integrations[NFTMarketplace.OPENSEA].get_collection(slug)
                
                # Get current orders to avoid overbidding
                orders = await self.integrations[NFTMarketplace.OPENSEA].get_orders(slug, side="ask", limit=10)
                
                if orders:
                    # Calculate bid price as percentage of lowest ask
                    lowest_ask = min(order.price for order in orders)
                    bid_price = lowest_ask * bid_percentage
                    
                    # Place bid on random floor NFT
                    floor_order = min(orders, key=lambda x: x.price)
                    expiration_time = datetime.now() + timedelta(hours=24)
                    
                    bid_id = await self.integrations[NFTMarketplace.OPENSEA].place_bid(
                        slug, floor_order.token_id, bid_price, expiration_time
                    )
                    
                    placed_bids.append(bid_id)
                    logger.info(f"Placed bid on {slug}: {bid_price} ETH")
            
            except Exception as e:
                logger.error(f"Failed to place bids on {slug}: {e}")
        
        return placed_bids
    
    async def rebalance_portfolio(self) -> Dict[str, Any]:
        """Rebalance NFT portfolio based on performance"""
        rebalance_actions = []
        
        # Analyze current holdings
        for collection_name, collection_data in self.portfolio.collections.items():
            current_value = collection_data['current_value']
            average_cost = collection_data['average_cost']
            
            # Sell profitable positions
            if current_value > average_cost * 1.5:  # 50% profit
                rebalance_actions.append({
                    'action': 'sell',
                    'collection': collection_name,
                    'reason': 'profit_taking',
                    'percentage': 0.3  # Sell 30%
                })
            
            # Buy more of underperforming but promising collections
            elif current_value < average_cost * 0.8:  # 20% loss
                rebalance_actions.append({
                    'action': 'buy',
                    'collection': collection_name,
                    'reason': 'average_down',
                    'percentage': 0.2  # Buy 20% more
                })
        
        return {
            'actions': rebalance_actions,
            'summary': f"Generated {len(rebalance_actions)} rebalancing actions"
        }
    
    def get_portfolio_performance(self) -> Dict[str, Any]:
        """Get portfolio performance metrics"""
        total_cost = sum(
            acq['price'] * acq.get('quantity', 1) for acq in self.portfolio.acquisitions
        )
        total_value = self.portfolio.total_value
        
        profit_loss = total_value - total_cost
        profit_loss_percentage = (profit_loss / total_cost * 100) if total_cost > 0 else 0
        
        return {
            'total_cost': total_cost,
            'total_value': total_value,
            'profit_loss': profit_loss,
            'profit_loss_percentage': profit_loss_percentage,
            'total_assets': self.portfolio.total_assets,
            'total_acquisitions': len(self.portfolio.acquisitions),
            'total_sales': len(self.portfolio.sales),
            'collections': len(self.portfolio.collections),
            'best_performer': self._get_best_performer(),
            'worst_performer': self._get_worst_performer()
        }
    
    def _get_best_performer(self) -> Optional[Dict[str, Any]]:
        """Get best performing collection"""
        if not self.portfolio.collections:
            return None
        
        best_collection = None
        best_performance = -float('inf')
        
        for name, data in self.portfolio.collections.items():
            performance = (data['current_value'] - data['average_cost']) / data['average_cost']
            if performance > best_performance:
                best_performance = performance
                best_collection = {'name': name, 'performance': performance}
        
        return best_collection
    
    def _get_worst_performer(self) -> Optional[Dict[str, Any]]:
        """Get worst performing collection"""
        if not self.portfolio.collections:
            return None
        
        worst_collection = None
        worst_performance = float('inf')
        
        for name, data in self.portfolio.collections.items():
            performance = (data['current_value'] - data['average_cost']) / data['average_cost']
            if performance < worst_performance:
                worst_performance = performance
                worst_collection = {'name': name, 'performance': performance}
        
        return worst_collection

# Main execution
async def main():
    # Configuration
    config = {
        'opensea_api_key': 'your_opensea_api_key',
        'wallet_address': '0xYourAddress',
        'private_key': 'your_private_key',
        'max_investment': 10.0,  # ETH
        'risk_tolerance': 0.7,
    }
    
    # Initialize market maker
    market_maker = NFTMarketMaker(config)
    await market_maker.initialize()
    
    # Execute trading strategy
    trades = await market_maker.execute_trading_strategy(
        max_investment=5.0,  # 5 ETH
        risk_tolerance=0.6
    )
    
    logger.info(f"Executed {len(trades)} trades")
    
    # Place automatic bids
    bids = await market_maker.place_bids_automatically(
        collection_slugs=['boredapeyachtclub', 'azuki'],
        bid_percentage=0.85
    )
    
    logger.info(f"Placed {len(bids)} bids")
    
    # Get portfolio performance
    performance = market_maker.get_portfolio_performance()
    logger.info(f"Portfolio performance: {performance}")

if __name__ == "__main__":
    asyncio.run(main())