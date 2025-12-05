"""
TigerEx DeFi Integration Service
High-yield DeFi products integration with multiple protocols
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass
from enum import Enum
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TigerEx DeFi Integration Service", version="1.0.0")
security = HTTPBearer()

class ProductType(str, Enum):
    FLEXIBLE_SAVINGS = "flexible_savings"
    FIXED_STAKING = "fixed_staking"
    LIQUIDITY_MINING = "liquidity_mining"
    DUAL_ASSET = "dual_asset"
    YIELD_FARMING = "yield_farming"
    DEFI_LENDING = "defi_lending"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

class ProtocolType(str, Enum):
    AAVE = "aave"
    COMPOUND = "compound"
    UNISWAP = "uniswap"
    CURVE = "curve"
    YEARN = "yearn"
    PANCAKESWAP = "pancakeswap"
    TIGEREX_LEND = "tigerex_lend"
    TIGEREX_FARM = "tigerex_farm"

class DeFiProduct(BaseModel):
    id: str
    name: str
    protocol: ProtocolType
    product_type: ProductType
    underlying_asset: str
    apy: float
    risk_level: RiskLevel
    minimum_amount: float
    maximum_amount: float
    lock_period_days: int
    description: str
    features: List[str]
    total_supply: float
    utilization_rate: float

class UserPosition(BaseModel):
    id: str
    user_id: str
    product_id: str
    amount: float
    entry_time: datetime
    current_value: float
    earned_rewards: float
    apy_at_entry: float
    status: str

class InvestmentRequest(BaseModel):
    product_id: str = Field(..., description="Product ID to invest in")
    amount: float = Field(..., gt=0, description="Investment amount")
    auto_compound: bool = Field(default=True, description="Auto-compound rewards")

class YieldOptimizationRequest(BaseModel):
    assets: List[str] = Field(..., description="List of assets to optimize")
    risk_tolerance: RiskLevel = Field(default="medium", description="Risk tolerance level")
    investment_horizon_days: int = Field(default=30, ge=1, le=365, description="Investment horizon")
    target_apy: Optional[float] = Field(None, description="Target APY")

# In-memory storage (replace with database in production)
defi_products: Dict[str, DeFiProduct] = {}
user_positions: Dict[str, UserPosition] = {}
protocol_data: Dict[str, Dict] = {}

class DeFiProtocolsManager:
    """Manage integration with various DeFi protocols"""
    
    def __init__(self):
        self.protocols = {
            ProtocolType.AAVE: self.initialize_aave_protocol(),
            ProtocolType.COMPOUND: self.initialize_compound_protocol(),
            ProtocolType.UNISWAP: self.initialize_uniswap_protocol(),
            ProtocolType.CURVE: self.initialize_curve_protocol(),
            ProtocolType.YEARN: self.initialize_yearn_protocol(),
            ProtocolType.PANCAKESWAP: self.initialize_pancakeswap_protocol(),
            ProtocolType.TIGEREX_LEND: self.initialize_tigerex_lend(),
            ProtocolType.TIGEREX_FARM: self.initialize_tigerex_farm()
        }
    
    def initialize_aave_protocol(self) -> Dict:
        """Initialize Aave protocol data"""
        return {
            "name": "Aave",
            "tvl": 12000000000,  # $12B TVL
            "risk_score": 0.3,
            "features": ["flash_loans", "variable_rates", "stable_rates"],
            "supported_assets": ["USDC", "USDT", "DAI", "WBTC", "ETH"]
        }
    
    def initialize_compound_protocol(self) -> Dict:
        """Initialize Compound protocol data"""
        return {
            "name": "Compound",
            "tvl": 8000000000,  # $8B TVL
            "risk_score": 0.25,
            "features": ["algorithmic_rates", "governance"],
            "supported_assets": ["USDC", "USDT", "DAI", "WBTC", "ETH"]
        }
    
    def initialize_uniswap_protocol(self) -> Dict:
        """Initialize Uniswap protocol data"""
        return {
            "name": "Uniswap V3",
            "tvl": 15000000000,  # $15B TVL
            "risk_score": 0.4,
            "features": ["concentrated_liquidity", "multiple_fee_tiers"],
            "supported_assets": ["ETH", "USDC", "USDT", "WBTC", "UNI"]
        }
    
    def initialize_curve_protocol(self) -> Dict:
        """Initialize Curve protocol data"""
        return {
            "name": "Curve Finance",
            "tvl": 6000000000,  # $6B TVL
            "risk_score": 0.2,
            "features": ["stablecoin_swaps", "low_slippage"],
            "supported_assets": ["USDC", "USDT", "DAI", "sUSD", "MIM"]
        }
    
    def initialize_yearn_protocol(self) -> Dict:
        """Initialize Yearn Finance protocol data"""
        return {
            "name": "Yearn Finance",
            "tvl": 2000000000,  # $2B TVL
            "risk_score": 0.35,
            "features": ["vault_strategy", "auto_compounding"],
            "supported_assets": ["USDC", "USDT", "DAI", "WBTC", "ETH"]
        }
    
    def initialize_pancakeswap_protocol(self) -> Dict:
        """Initialize PancakeSwap protocol data"""
        return {
            "name": "PancakeSwap",
            "tvl": 4000000000,  # $4B TVL
            "risk_score": 0.45,
            "features": ["yield_farming", "lottery", "ifo"],
            "supported_assets": ["BNB", "BUSD", "CAKE", "USDT", "ETH"]
        }
    
    def initialize_tigerex_lend(self) -> Dict:
        """Initialize TigerEx Lending protocol"""
        return {
            "name": "TigerEx Lend",
            "tvl": 500000000,  # $500M TVL
            "risk_score": 0.15,
            "features": ["insured_deposits", "competitive_rates"],
            "supported_assets": ["USDT", "USDC", "BTC", "ETH"]
        }
    
    def initialize_tigerex_farm(self) -> Dict:
        """Initialize TigerEx Farm protocol"""
        return {
            "name": "TigerEx Farm",
            "tvl": 300000000,  # $300M TVL
            "risk_score": 0.3,
            "features": ["auto_compound", "boosted_rewards"],
            "supported_assets": ["TIGER", "USDT", "USDC", "BNB"]
        }

class YieldOptimizer:
    """AI-powered yield optimization engine"""
    
    def __init__(self):
        self.risk_multipliers = {
            RiskLevel.LOW: 0.7,
            RiskLevel.MEDIUM: 1.0,
            RiskLevel.HIGH: 1.3,
            RiskLevel.EXTREME: 1.6
        }
    
    async def optimize_yield(self, request: YieldOptimizationRequest) -> Dict[str, Any]:
        """Optimize yield across multiple protocols"""
        
        # Get available products for requested assets
        available_products = []
        for product in defi_products.values():
            if product.underlying_asset in request.assets:
                # Filter by risk tolerance
                if self.risk_level_matches(product.risk_level, request.risk_tolerance):
                    available_products.append(product)
        
        # Sort by APY adjusted for risk
        risk_adjusted_products = []
        for product in available_products:
            risk_multiplier = self.risk_multipliers.get(request.risk_tolerance, 1.0)
            adjusted_apy = product.apy * (2.0 - self.protocols[product.protocol]["risk_score"])
            risk_adjusted_products.append((product, adjusted_apy))
        
        risk_adjusted_products.sort(key=lambda x: x[1], reverse=True)
        
        # Generate optimization strategy
        optimization_strategy = {
            "recommendations": [],
            "expected_portfolio_apy": 0,
            "risk_score": 0,
            "diversification_score": 0
        }
        
        # Select top products with diversification
        selected_protocols = set()
        total_weight = 0
        
        for i, (product, adjusted_apy) in enumerate(risk_adjusted_products[:10]):  # Top 10 products
            if product.protocol not in selected_protocols or i < 5:  # Ensure diversification
                weight = 1.0 / min(i + 1, 5)  # Decreasing weights
                
                optimization_strategy["recommendations"].append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "protocol": product.protocol.value,
                    "apy": product.apy,
                    "risk_adjusted_apy": adjusted_apy,
                    "recommended_allocation": f"{weight * 100:.1f}%",
                    "minimum_amount": product.minimum_amount,
                    "lock_period_days": product.lock_period_days
                })
                
                selected_protocols.add(product.protocol)
                total_weight += weight
        
        # Calculate portfolio metrics
        if optimization_strategy["recommendations"]:
            portfolio_apy = sum(rec["apy"] * float(rec["recommended_allocation"].rstrip('%')) / 100 
                              for rec in optimization_strategy["recommendations"])
            optimization_strategy["expected_portfolio_apy"] = portfolio_apy
            optimization_strategy["diversification_score"] = len(selected_protocols) / 8.0  # 8 protocols total
        
        return optimization_strategy
    
    def risk_level_matches(self, product_risk: RiskLevel, user_risk: RiskLevel) -> bool:
        """Check if product risk matches user risk tolerance"""
        risk_levels = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.EXTREME]
        product_index = risk_levels.index(product_risk)
        user_index = risk_levels.index(user_risk)
        return product_index <= user_index + 1  # Allow one level above

class DeFiProductsManager:
    """Manage DeFi products and user positions"""
    
    def __init__(self):
        self.protocols_manager = DeFiProtocolsManager()
        self.yield_optimizer = YieldOptimizer()
        self.initialize_products()
    
    def initialize_products(self):
        """Initialize available DeFi products"""
        
        # TigerEx Lending Products
        defi_products["tigerex_usdt_flexible"] = DeFiProduct(
            id="tigerex_usdt_flexible",
            name="TigerEx USDT Flexible Savings",
            protocol=ProtocolType.TIGEREX_LEND,
            product_type=ProductType.FLEXIBLE_SAVINGS,
            underlying_asset="USDT",
            apy=8.5,
            risk_level=RiskLevel.LOW,
            minimum_amount=10.0,
            maximum_amount=1000000.0,
            lock_period_days=0,
            description="Flexible USDT savings with instant withdrawal",
            features=["instant_withdrawal", "daily_interest", "insurance_fund"],
            total_supply=50000000.0,
            utilization_rate=0.75
        )
        
        defi_products["tigerex_btc_fixed"] = DeFiProduct(
            id="tigerex_btc_fixed",
            name="TigerEx BTC Fixed Staking (30 days)",
            protocol=ProtocolType.TIGEREX_LEND,
            product_type=ProductType.FIXED_STAKING,
            underlying_asset="BTC",
            apy=12.0,
            risk_level=RiskLevel.LOW,
            minimum_amount=0.001,
            maximum_amount=100.0,
            lock_period_days=30,
            description="Fixed-term BTC staking with guaranteed returns",
            features=["guaranteed_apy", "insurance_covered", "auto_renewal"],
            total_supply=1500.0,
            utilization_rate=0.85
        )
        
        # Aave Products
        defi_products["aave_usdc_variable"] = DeFiProduct(
            id="aave_usdc_variable",
            name="Aave USDC Variable Rate",
            protocol=ProtocolType.AAVE,
            product_type=ProductType.DEFI_LENDING,
            underlying_asset="USDC",
            apy=4.2,
            risk_level=RiskLevel.LOW,
            minimum_amount=1.0,
            maximum_amount=1000000.0,
            lock_period_days=0,
            description="Variable rate lending on Aave protocol",
            features=["variable_rate", "flash_loan_support", "governance_rights"],
            total_supply=200000000.0,
            utilization_rate=0.65
        )
        
        # Uniswap Products
        defi_products["uniswap_eth_usdc_lp"] = DeFiProduct(
            id="uniswap_eth_usdc_lp",
            name="Uniswap ETH/USDC Liquidity Pool",
            protocol=ProtocolType.UNISWAP,
            product_type=ProductType.LIQUIDITY_MINING,
            underlying_asset="ETH/USDC LP",
            apy=15.8,
            risk_level=RiskLevel.HIGH,
            minimum_amount=100.0,
            maximum_amount=500000.0,
            lock_period_days=0,
            description="Provide liquidity to ETH/USDC pool on Uniswap V3",
            features=["concentrated_liquidity", "fee_rewards", "impermanent_loss_protection"],
            total_supply=50000000.0,
            utilization_rate=0.90
        )
        
        # Dual Asset Products
        defi_products["tigerex_dual_btc_usdt"] = DeFiProduct(
            id="tigerex_dual_btc_usdt",
            name="TigerEx Dual Asset BTC/USDT",
            protocol=ProtocolType.TIGEREX_FARM,
            product_type=ProductType.DUAL_ASSET,
            underlying_asset="BTC/USDT",
            apy=85.0,
            risk_level=RiskLevel.EXTREME,
            minimum_amount=1000.0,
            maximum_amount=100000.0,
            lock_period_days=7,
            description="High-yield dual asset product with optimized returns",
            features=["ai_optimized", "auto_compounding", "high_yield"],
            total_supply=20000000.0,
            utilization_rate=0.95
        )
        
        # Yield Farming
        defi_products["pancakeswap_cake_bnb"] = DeFiProduct(
            id="pancakeswap_cake_bnb",
            name="PancakeSwap CAKE/BNB Farm",
            protocol=ProtocolType.PANCAKESWAP,
            product_type=ProductType.YIELD_FARMING,
            underlying_asset="CAKE/BNB LP",
            apy=45.0,
            risk_level=RiskLevel.HIGH,
            minimum_amount=10.0,
            maximum_amount=50000.0,
            lock_period_days=0,
            description="Stake CAKE/BNB LP tokens for high yields",
            features=["auto_compound", "boosted_rewards", "governance_tokens"],
            total_supply=30000000.0,
            utilization_rate=0.88
        )
    
    async def get_products_by_asset(self, asset: str) -> List[DeFiProduct]:
        """Get all products for a specific asset"""
        return [product for product in defi_products.values() 
                if product.underlying_asset == asset or asset in product.underlying_asset]
    
    async def invest(self, user_id: str, request: InvestmentRequest) -> UserPosition:
        """Invest in a DeFi product"""
        if request.product_id not in defi_products:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product = defi_products[request.product_id]
        
        # Validate investment amount
        if request.amount < product.minimum_amount:
            raise HTTPException(status_code=400, detail="Amount below minimum")
        if request.amount > product.maximum_amount:
            raise HTTPException(status_code=400, detail="Amount above maximum")
        
        # Create position
        position_id = f"pos_{datetime.now().timestamp()}_{len(user_positions)}"
        position = UserPosition(
            id=position_id,
            user_id=user_id,
            product_id=request.product_id,
            amount=request.amount,
            entry_time=datetime.now(),
            current_value=request.amount,
            earned_rewards=0.0,
            apy_at_entry=product.apy,
            status="active"
        )
        
        user_positions[position_id] = position
        
        # Update product total supply
        product.total_supply += request.amount
        
        return position
    
    async def get_user_positions(self, user_id: str) -> List[UserPosition]:
        """Get all positions for a user"""
        return [pos for pos in user_positions.values() if pos.user_id == user_id]
    
    async def calculate_rewards(self, position: UserPosition) -> float:
        """Calculate rewards for a position"""
        if position.product_id not in defi_products:
            return 0.0
        
        product = defi_products[position.product_id]
        days_held = (datetime.now() - position.entry_time).days
        
        # Simple interest calculation (can be enhanced with compounding)
        rewards = position.amount * (product.apy / 100) * (days_held / 365)
        return rewards
    
    async def withdraw_position(self, position_id: str, user_id: str) -> Dict[str, Any]:
        """Withdraw from a position"""
        if position_id not in user_positions:
            raise HTTPException(status_code=404, detail="Position not found")
        
        position = user_positions[position_id]
        if position.user_id != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        product = defi_products[position.product_id]
        
        # Calculate rewards
        rewards = await self.calculate_rewards(position)
        total_amount = position.amount + rewards
        
        # Update position
        position.status = "withdrawn"
        position.earned_rewards = rewards
        
        # Update product total supply
        product.total_supply -= position.amount
        
        return {
            "position_id": position_id,
            "principal_amount": position.amount,
            "rewards_amount": rewards,
            "total_amount": total_amount,
            "apy": position.apy_at_entry,
            "days_held": (datetime.now() - position.entry_time).days
        }

# Initialize managers
defi_manager = DeFiProductsManager()

@app.get("/defi/products", response_model=List[DeFiProduct])
async def get_defi_products(asset: Optional[str] = None, product_type: Optional[ProductType] = None):
    """Get available DeFi products with optional filtering"""
    products = list(defi_products.values())
    
    if asset:
        products = [p for p in products if p.underlying_asset == asset or asset in p.underlying_asset]
    
    if product_type:
        products = [p for p in products if p.product_type == product_type]
    
    return products

@app.get("/defi/products/{product_id}")
async def get_product_details(product_id: str):
    """Get detailed information about a specific product"""
    if product_id not in defi_products:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = defi_products[product_id]
    protocol_info = defi_manager.protocols_manager.protocols[product.protocol]
    
    return {
        "product": product.dict(),
        "protocol_info": protocol_info,
        "historical_performance": {
            "last_7_days_apy": product.apy * np.random.uniform(0.95, 1.05),
            "last_30_days_apy": product.apy * np.random.uniform(0.90, 1.10),
            "total_value_locked": product.total_supply,
            "utilization_rate": product.utilization_rate
        }
    }

@app.post("/defi/invest", response_model=UserPosition)
async def invest_in_product(
    request: InvestmentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Invest in a DeFi product"""
    try:
        user_id = "user_" + credentials.credentials[:8]
        position = await defi_manager.invest(user_id, request)
        logger.info(f"User {user_id} invested {request.amount} in product {request.product_id}")
        return position
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error investing in product: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/defi/positions", response_model=List[UserPosition])
async def get_user_positions(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all DeFi positions for the authenticated user"""
    try:
        user_id = "user_" + credentials.credentials[:8]
        positions = await defi_manager.get_user_positions(user_id)
        return positions
    except Exception as e:
        logger.error(f"Error getting user positions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/defi/positions/{position_id}/withdraw")
async def withdraw_from_position(
    position_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Withdraw from a DeFi position"""
    try:
        user_id = "user_" + credentials.credentials[:8]
        result = await defi_manager.withdraw_position(position_id, user_id)
        logger.info(f"User {user_id} withdrew from position {position_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error withdrawing from position: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/defi/optimize", response_model=Dict[str, Any])
async def optimize_yield(
    request: YieldOptimizationRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get AI-powered yield optimization recommendations"""
    try:
        optimization = await defi_manager.yield_optimizer.optimize_yield(request)
        return optimization
    except Exception as e:
        logger.error(f"Error optimizing yield: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/defi/protocols")
async def get_supported_protocols():
    """Get supported DeFi protocols and their information"""
    protocols_data = {}
    for protocol_type, protocol_info in defi_manager.protocols_manager.protocols.items():
        protocols_data[protocol_type.value] = protocol_info
    return protocols_data

@app.get("/defi/summary")
async def get_defi_summary(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get DeFi portfolio summary for the user"""
    try:
        user_id = "user_" + credentials.credentials[:8]
        positions = await defi_manager.get_user_positions(user_id)
        
        total_invested = sum(pos.amount for pos in positions if pos.status == "active")
        total_rewards = 0
        
        for position in positions:
            if position.status == "active":
                rewards = await defi_manager.calculate_rewards(position)
                total_rewards += rewards
        
        # Calculate portfolio distribution
        asset_distribution = {}
        for position in positions:
            if position.status == "active":
                product = defi_products[position.product_id]
                asset = product.underlying_asset
                if asset not in asset_distribution:
                    asset_distribution[asset] = 0
                asset_distribution[asset] += position.amount
        
        return {
            "total_invested": total_invested,
            "total_rewards": total_rewards,
            "current_value": total_invested + total_rewards,
            "active_positions": len([p for p in positions if p.status == "active"]),
            "asset_distribution": asset_distribution,
            "average_apy": np.mean([p.apy_at_entry for p in positions if p.status == "active"]) if positions else 0
        }
    except Exception as e:
        logger.error(f"Error getting DeFi summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "TigerEx DeFi Integration Service", "total_products": len(defi_products)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)