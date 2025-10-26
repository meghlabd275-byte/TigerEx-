"""
TigerEx Own Liquidity System
Complete implementation of internal liquidity providing system
"""

import asyncio
import json
import logging
import math
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
from decimal import Decimal, getcontext

# Set precision for decimal calculations
getcontext().prec = 28

class LiquidityPoolType(Enum):
    AUTOMATED_MARKET_MAKER = "amm"
    ORDER_BOOK = "orderbook"
    HYBRID = "hybrid"

class FeeTier(Enum):
    TIER_1 = (0.001, 0)      # 0.1% fee, 0% rebate
    TIER_2 = (0.0008, 0.0001)  # 0.08% fee, 0.01% rebate
    TIER_3 = (0.0005, 0.0002)  # 0.05% fee, 0.02% rebate
    TIER_4 = (0.0003, 0.0003)  # 0.03% fee, 0.03% rebate

@dataclass
class Token:
    symbol: str
    name: str
    decimals: int
    total_supply: float
    address: str = ""

@dataclass
class LiquidityPosition:
    id: str
    user_id: str
    token_a: str
    token_b: str
    amount_a: float
    amount_b: float
    pool_share: float
    created_at: datetime
    updated_at: datetime

@dataclass
class LiquidityPool:
    id: str
    token_a: Token
    token_b: Token
    reserve_a: float = 0.0
    reserve_b: float = 0.0
    total_supply: float = 0.0
    fee_rate: float = 0.003  # 0.3% default
    pool_type: LiquidityPoolType = LiquidityPoolType.AUTOMATED_MARKET_MAKER
    positions: Dict[str, LiquidityPosition] = field(default_factory=dict)
    volume_24h: float = 0.0
    apr: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_price(self, token_in: str) -> float:
        """Get price of token in terms of the other token"""
        if self.reserve_a == 0 or self.reserve_b == 0:
            return 0.0
        
        if token_in == self.token_a.symbol:
            return self.reserve_b / self.reserve_a
        else:
            return self.reserve_a / self.reserve_b
    
    def calculate_output_amount(self, amount_in: float, token_in: str) -> float:
        """Calculate output amount using constant product formula"""
        if self.pool_type != LiquidityPoolType.AUTOMATED_MARKET_MAKER:
            return 0.0
        
        if token_in == self.token_a.symbol:
            if self.reserve_a == 0:
                return 0.0
            k = self.reserve_a * self.reserve_b
            new_reserve_a = self.reserve_a + amount_in
            new_reserve_b = k / new_reserve_a
            amount_out = self.reserve_b - new_reserve_b
            return max(0, amount_out * (1 - self.fee_rate))
        else:
            if self.reserve_b == 0:
                return 0.0
            k = self.reserve_a * self.reserve_b
            new_reserve_b = self.reserve_b + amount_in
            new_reserve_a = k / new_reserve_b
            amount_out = self.reserve_a - new_reserve_a
            return max(0, amount_out * (1 - self.fee_rate))

@dataclass
class OrderBookEntry:
    price: float
    amount: float
    order_id: str
    user_id: str
    timestamp: datetime

@dataclass
class Order:
    id: str
    user_id: str
    symbol: str
    side: str  # "buy" or "sell"
    order_type: str  # "market", "limit", "stop"
    amount: float
    price: Optional[float]
    filled: float = 0.0
    status: str = "open"  # "open", "filled", "cancelled"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

class LiquidityManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pools: Dict[str, LiquidityPool] = {}
        self.tokens: Dict[str, Token] = {}
        self.order_books: Dict[str, Dict[str, List[OrderBookEntry]]] = {}
        self.orders: Dict[str, Order] = {}
        self.user_balances: Dict[str, Dict[str, float]] = {}
        self.fee_tiers: Dict[str, FeeTier] = {}
        self.trading_volumes: Dict[str, float] = {}
        self.pool_metrics: Dict[str, Dict[str, Any]] = {}
        
    def add_token(self, token: Token):
        """Add a new token to the system"""
        self.tokens[token.symbol] = token
        self.logger.info(f"Added token: {token.symbol}")
    
    def create_pool(self, token_a: str, token_b: str, pool_type: LiquidityPoolType = LiquidityPoolType.AUTOMATED_MARKET_MAKER, fee_rate: float = 0.003) -> str:
        """Create a new liquidity pool"""
        if token_a not in self.tokens or token_b not in self.tokens:
            raise ValueError("One or both tokens not found")
        
        pool_id = f"{token_a}_{token_b}"
        if pool_id in self.pools:
            raise ValueError(f"Pool {pool_id} already exists")
        
        pool = LiquidityPool(
            id=pool_id,
            token_a=self.tokens[token_a],
            token_b=self.tokens[token_b],
            pool_type=pool_type,
            fee_rate=fee_rate
        )
        
        self.pools[pool_id] = pool
        self.order_books[pool_id] = {"bids": [], "asks": []}
        self.pool_metrics[pool_id] = {
            "volume_24h": 0.0,
            "fee_24h": 0.0,
            "transactions_24h": 0,
            "liquidity_utilization": 0.0,
            "last_updated": datetime.now()
        }
        
        self.logger.info(f"Created pool: {pool_id}")
        return pool_id
    
    def add_liquidity(self, user_id: str, pool_id: str, amount_a: float, amount_b: float) -> str:
        """Add liquidity to a pool"""
        if pool_id not in self.pools:
            raise ValueError(f"Pool {pool_id} not found")
        
        pool = self.pools[pool_id]
        
        # Check user balances
        self._check_balance(user_id, pool.token_a.symbol, amount_a)
        self._check_balance(user_id, pool.token_b.symbol, amount_b)
        
        # Calculate liquidity tokens to mint
        if pool.total_supply == 0:
            # First liquidity provider - sets the price
            liquidity_tokens = math.sqrt(amount_a * amount_b) - 0.001
        else:
            # Proportional to existing reserves
            liquidity_a = (amount_a / pool.reserve_a) * pool.total_supply
            liquidity_b = (amount_b / pool.reserve_b) * pool.total_supply
            liquidity_tokens = min(liquidity_a, liquidity_b)
        
        # Create liquidity position
        position_id = str(uuid.uuid4())
        position = LiquidityPosition(
            id=position_id,
            user_id=user_id,
            token_a=pool.token_a.symbol,
            token_b=pool.token_b.symbol,
            amount_a=amount_a,
            amount_b=amount_b,
            pool_share=liquidity_tokens / (pool.total_supply + liquidity_tokens) * 100,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Update pool reserves
        pool.reserve_a += amount_a
        pool.reserve_b += amount_b
        pool.total_supply += liquidity_tokens
        pool.positions[position_id] = position
        
        # Update user balances
        self._debit_balance(user_id, pool.token_a.symbol, amount_a)
        self._debit_balance(user_id, pool.token_b.symbol, amount_b)
        self._credit_balance(user_id, f"LP_{pool_id}", liquidity_tokens)
        
        # Calculate new APR
        self._calculate_pool_apr(pool_id)
        
        self.logger.info(f"Added liquidity to pool {pool_id}: {amount_a} {pool.token_a.symbol}, {amount_b} {pool.token_b.symbol}")
        return position_id
    
    def remove_liquidity(self, user_id: str, position_id: str, percentage: float = 1.0) -> Dict[str, float]:
        """Remove liquidity from a pool"""
        if position_id not in self._get_user_positions(user_id):
            raise ValueError("Position not found or not owned by user")
        
        position = None
        for pool in self.pools.values():
            if position_id in pool.positions:
                position = pool.positions[position_id]
                break
        
        if not position:
            raise ValueError("Position not found")
        
        pool = self.pools[position.pool_share]
        
        # Calculate amounts to return
        amount_a_to_return = position.amount_a * percentage
        amount_b_to_return = position.amount_b * percentage
        liquidity_tokens_to_burn = (position.pool_share / 100) * pool.total_supply * percentage
        
        # Update pool
        pool.reserve_a -= amount_a_to_return
        pool.reserve_b -= amount_b_to_return
        pool.total_supply -= liquidity_tokens_to_burn
        
        # Update position or remove if fully withdrawn
        if percentage >= 1.0:
            del pool.positions[position_id]
        else:
            position.amount_a -= amount_a_to_return
            position.amount_b -= amount_b_to_return
            position.pool_share *= (1 - percentage)
            position.updated_at = datetime.now()
        
        # Update user balances
        self._credit_balance(user_id, pool.token_a.symbol, amount_a_to_return)
        self._credit_balance(user_id, pool.token_b.symbol, amount_b_to_return)
        self._debit_balance(user_id, f"LP_{pool.id}", liquidity_tokens_to_burn)
        
        self.logger.info(f"Removed liquidity from pool {pool.id}: {amount_a_to_return} {pool.token_a.symbol}, {amount_b_to_return} {pool.token_b.symbol}")
        
        return {
            "amount_a": amount_a_to_return,
            "amount_b": amount_b_to_return,
            "liquidity_tokens": liquidity_tokens_to_burn
        }
    
    def swap(self, user_id: str, token_in: str, token_out: str, amount_in: float, min_amount_out: float = 0.0) -> Dict[str, Any]:
        """Execute a swap between tokens"""
        pool_id = f"{token_in}_{token_out}"
        reverse_pool_id = f"{token_out}_{token_in}"
        
        # Find the correct pool
        pool = None
        if pool_id in self.pools:
            pool = self.pools[pool_id]
        elif reverse_pool_id in self.pools:
            pool = self.pools[reverse_pool_id]
            token_in, token_out = token_out, token_in  # Swap the tokens
        else:
            raise ValueError("No pool found for this token pair")
        
        # Check user balance
        self._check_balance(user_id, token_in, amount_in)
        
        # Calculate output amount
        amount_out = pool.calculate_output_amount(amount_in, token_in)
        
        if amount_out < min_amount_out:
            raise ValueError(f"Insufficient output amount. Expected minimum: {min_amount_out}, Got: {amount_out}")
        
        # Calculate fees
        fee_amount = amount_in * pool.fee_rate
        
        # Execute swap
        if token_in == pool.token_a.symbol:
            pool.reserve_a += amount_in
            pool.reserve_b -= amount_out
        else:
            pool.reserve_b += amount_in
            pool.reserve_a -= amount_out
        
        # Update user balances
        self._debit_balance(user_id, token_in, amount_in)
        self._credit_balance(user_id, token_out, amount_out)
        
        # Distribute fees to liquidity providers
        self._distribute_fees(pool.id, fee_amount, token_in)
        
        # Update metrics
        self._update_trading_metrics(pool.id, amount_in, fee_amount)
        self._update_user_volume(user_id, amount_in)
        self._calculate_pool_apr(pool.id)
        
        # Calculate slippage
        expected_price = pool.get_price(token_in)
        actual_price = amount_out / (amount_in - fee_amount)
        slippage = abs((expected_price - actual_price) / expected_price) * 100
        
        self.logger.info(f"Executed swap: {user_id} swapped {amount_in} {token_in} for {amount_out} {token_out}")
        
        return {
            "amount_in": amount_in,
            "amount_out": amount_out,
            "fee_amount": fee_amount,
            "price": actual_price,
            "slippage": slippage,
            "pool_id": pool.id
        }
    
    def place_limit_order(self, user_id: str, symbol: str, side: str, amount: float, price: float) -> str:
        """Place a limit order in the order book"""
        self._check_balance(user_id, symbol.split("_")[0] if side == "sell" else symbol.split("_")[1], amount)
        
        order_id = str(uuid.uuid4())
        order = Order(
            id=order_id,
            user_id=user_id,
            symbol=symbol,
            side=side,
            order_type="limit",
            amount=amount,
            price=price
        )
        
        self.orders[order_id] = order
        
        # Add to order book
        if symbol not in self.order_books:
            self.order_books[symbol] = {"bids": [], "asks": []}
        
        entry = OrderBookEntry(
            price=price,
            amount=amount,
            order_id=order_id,
            user_id=user_id,
            timestamp=datetime.now()
        )
        
        if side == "buy":
            self.order_books[symbol]["bids"].append(entry)
            self.order_books[symbol]["bids"].sort(key=lambda x: x.price, reverse=True)  # Highest price first
        else:
            self.order_books[symbol]["asks"].append(entry)
            self.order_books[symbol]["asks"].sort(key=lambda x: x.price)  # Lowest price first
        
        # Try to match orders
        self._match_orders(symbol)
        
        self.logger.info(f"Placed limit order: {order_id}")
        return order_id
    
    def _match_orders(self, symbol: str):
        """Match orders in the order book"""
        if symbol not in self.order_books:
            return
        
        bids = self.order_books[symbol]["bids"]
        asks = self.order_books[symbol]["asks"]
        
        while bids and asks:
            best_bid = bids[0]
            best_ask = asks[0]
            
            if best_bid.price >= best_ask.price:
                # Match the orders
                trade_amount = min(best_bid.amount, best_ask.amount)
                trade_price = (best_bid.price + best_ask.price) / 2
                
                # Update order book
                best_bid.amount -= trade_amount
                best_ask.amount -= trade_amount
                
                # Update orders
                bid_order = self.orders[best_bid.order_id]
                ask_order = self.orders[best_ask.order_id]
                
                bid_order.filled += trade_amount
                ask_order.filled += trade_amount
                
                bid_order.updated_at = datetime.now()
                ask_order.updated_at = datetime.now()
                
                # Handle user balances
                # This would involve actual token transfers in a real system
                
                # Remove filled orders
                if best_bid.amount <= 0:
                    bids.pop(0)
                    bid_order.status = "filled"
                if best_ask.amount <= 0:
                    asks.pop(0)
                    ask_order.status = "filled"
            else:
                break  # No more matches possible
    
    def _calculate_pool_apr(self, pool_id: str):
        """Calculate APR for a liquidity pool"""
        pool = self.pools[pool_id]
        metrics = self.pool_metrics.get(pool_id, {})
        
        if pool.total_supply > 0:
            daily_fees = metrics.get("fee_24h", 0.0)
            annual_fees = daily_fees * 365
            pool.apr = (annual_fees / pool.total_supply) * 100
        else:
            pool.apr = 0.0
    
    def _distribute_fees(self, pool_id: str, fee_amount: float, fee_token: str):
        """Distribute trading fees to liquidity providers"""
        pool = self.pools[pool_id]
        
        if pool.total_supply == 0:
            return
        
        # Distribute fees proportionally to liquidity providers
        for position in pool.positions.values():
            fee_share = (position.pool_share / 100) * fee_amount
            self._credit_balance(position.user_id, fee_token, fee_share)
    
    def _update_trading_metrics(self, pool_id: str, volume: float, fee_amount: float):
        """Update trading metrics for a pool"""
        metrics = self.pool_metrics[pool_id]
        metrics["volume_24h"] += volume
        metrics["fee_24h"] += fee_amount
        metrics["transactions_24h"] += 1
        metrics["last_updated"] = datetime.now()
        
        # Calculate liquidity utilization
        pool = self.pools[pool_id]
        if pool.reserve_a > 0 and pool.reserve_b > 0:
            metrics["liquidity_utilization"] = (metrics["volume_24h"] / ((pool.reserve_a + pool.reserve_b) / 2)) * 100
    
    def _update_user_volume(self, user_id: str, volume: float):
        """Update user trading volume for fee tier calculation"""
        if user_id not in self.trading_volumes:
            self.trading_volumes[user_id] = 0.0
        self.trading_volumes[user_id] += volume
        
        # Update fee tier based on volume
        if self.trading_volumes[user_id] >= 1000000:  # $1M+
            self.fee_tiers[user_id] = FeeTier.TIER_4
        elif self.trading_volumes[user_id] >= 100000:  # $100K+
            self.fee_tiers[user_id] = FeeTier.TIER_3
        elif self.trading_volumes[user_id] >= 10000:  # $10K+
            self.fee_tiers[user_id] = FeeTier.TIER_2
        else:
            self.fee_tiers[user_id] = FeeTier.TIER_1
    
    def _get_user_positions(self, user_id: str) -> List[str]:
        """Get all liquidity positions for a user"""
        positions = []
        for pool in self.pools.values():
            for position_id, position in pool.positions.items():
                if position.user_id == user_id:
                    positions.append(position_id)
        return positions
    
    def _check_balance(self, user_id: str, token: str, amount: float):
        """Check if user has sufficient balance"""
        if user_id not in self.user_balances:
            self.user_balances[user_id] = {}
        
        if token not in self.user_balances[user_id]:
            self.user_balances[user_id][token] = 0.0
        
        if self.user_balances[user_id][token] < amount:
            raise ValueError(f"Insufficient balance: {self.user_balances[user_id][token]} {token}, required: {amount}")
    
    def _debit_balance(self, user_id: str, token: str, amount: float):
        """Debit amount from user balance"""
        if user_id not in self.user_balances:
            self.user_balances[user_id] = {}
        
        self.user_balances[user_id][token] = self.user_balances[user_id].get(token, 0.0) - amount
    
    def _credit_balance(self, user_id: str, token: str, amount: float):
        """Credit amount to user balance"""
        if user_id not in self.user_balances:
            self.user_balances[user_id] = {}
        
        self.user_balances[user_id][token] = self.user_balances[user_id].get(token, 0.0) + amount
    
    def get_pool_info(self, pool_id: str) -> Dict[str, Any]:
        """Get detailed information about a liquidity pool"""
        if pool_id not in self.pools:
            raise ValueError(f"Pool {pool_id} not found")
        
        pool = self.pools[pool_id]
        metrics = self.pool_metrics.get(pool_id, {})
        
        return {
            "id": pool.id,
            "token_a": pool.token_a.symbol,
            "token_b": pool.token_b.symbol,
            "reserve_a": pool.reserve_a,
            "reserve_b": pool.reserve_b,
            "total_supply": pool.total_supply,
            "fee_rate": pool.fee_rate,
            "pool_type": pool.pool_type.value,
            "price_a_to_b": pool.get_price(pool.token_a.symbol),
            "price_b_to_a": pool.get_price(pool.token_b.symbol),
            "volume_24h": metrics.get("volume_24h", 0.0),
            "fee_24h": metrics.get("fee_24h", 0.0),
            "transactions_24h": metrics.get("transactions_24h", 0),
            "liquidity_utilization": metrics.get("liquidity_utilization", 0.0),
            "apr": pool.apr,
            "num_positions": len(pool.positions),
            "created_at": pool.created_at.isoformat()
        }
    
    def get_user_liquidity_positions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all liquidity positions for a user"""
        positions = []
        for pool in self.pools.values():
            for position in pool.positions.values():
                if position.user_id == user_id:
                    position_info = {
                        "id": position.id,
                        "pool_id": pool.id,
                        "token_a": position.token_a,
                        "token_b": position.token_b,
                        "amount_a": position.amount_a,
                        "amount_b": position.amount_b,
                        "pool_share": position.pool_share,
                        "created_at": position.created_at.isoformat(),
                        "updated_at": position.updated_at.isoformat(),
                        "pool_value_usd": self._calculate_position_value(position, pool)
                    }
                    positions.append(position_info)
        return positions
    
    def _calculate_position_value(self, position: LiquidityPosition, pool: LiquidityPool) -> float:
        """Calculate the USD value of a liquidity position"""
        # This would need price oracle integration in a real system
        # For now, return a simple calculation
        return position.amount_a + position.amount_b
    
    def get_order_book(self, symbol: str, depth: int = 20) -> Dict[str, List[Tuple[float, float]]]:
        """Get the order book for a symbol"""
        if symbol not in self.order_books:
            return {"bids": [], "asks": []}
        
        book = self.order_books[symbol]
        
        bids = [(entry.price, entry.amount) for entry in book["bids"][:depth]]
        asks = [(entry.price, entry.amount) for entry in book["asks"][:depth]]
        
        return {"bids": bids, "asks": asks}
    
    def rebalance_pools(self):
        """Rebalance liquidity pools based on market conditions"""
        for pool_id, pool in self.pools.items():
            if pool.pool_type == LiquidityPoolType.HYBRID:
                # Implement rebalancing logic for hybrid pools
                self._rebalance_hybrid_pool(pool)
    
    def _rebalance_hybrid_pool(self, pool: LiquidityPool):
        """Rebalance a hybrid pool between AMM and order book"""
        # This is a simplified rebalancing algorithm
        # In practice, this would be more sophisticated
        
        # Check if order book has sufficient depth
        order_book_depth = 0
        if pool.id in self.order_books:
            book = self.order_books[pool.id]
            order_book_depth = sum(amount for _, amount in book["bids"][:5]) + sum(amount for _, amount in book["asks"][:5])
        
        # If order book depth is low, shift more liquidity to AMM
        amm_ratio = 0.7  # 70% in AMM by default
        if order_book_depth < (pool.reserve_a + pool.reserve_b) * 0.1:  # Less than 10% of total liquidity
            amm_ratio = 0.9  # Shift more to AMM
        
        # This would require complex rebalancing logic in practice
        self.logger.info(f"Rebalancing pool {pool.id} with AMM ratio: {amm_ratio}")

# Initialize the liquidity management system
liquidity_manager = LiquidityManager()

# FastAPI endpoints
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="TigerEx Liquidity Management API", version="1.0.0")
security = HTTPBearer()

class TokenModel(BaseModel):
    symbol: str
    name: str
    decimals: int
    total_supply: float
    address: str = ""

class PoolRequest(BaseModel):
    token_a: str
    token_b: str
    pool_type: str = "amm"
    fee_rate: float = 0.003

class LiquidityRequest(BaseModel):
    pool_id: str
    amount_a: float
    amount_b: float

class SwapRequest(BaseModel):
    token_in: str
    token_out: str
    amount_in: float
    min_amount_out: float = 0.0

class LimitOrderRequest(BaseModel):
    symbol: str
    side: str
    amount: float
    price: float

@app.post("/api/v1/liquidity/tokens")
async def add_token(token: TokenModel, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Add a new token to the system"""
    try:
        new_token = Token(
            symbol=token.symbol,
            name=token.name,
            decimals=token.decimals,
            total_supply=token.total_supply,
            address=token.address
        )
        liquidity_manager.add_token(new_token)
        return {"message": f"Token {token.symbol} added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/liquidity/pools")
async def create_pool(request: PoolRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create a new liquidity pool"""
    try:
        pool_type = LiquidityPoolType(request.pool_type)
        pool_id = liquidity_manager.create_pool(
            request.token_a,
            request.token_b,
            pool_type,
            request.fee_rate
        )
        return {"pool_id": pool_id, "message": "Pool created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/liquidity/add")
async def add_liquidity(user_id: str, request: LiquidityRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Add liquidity to a pool"""
    try:
        position_id = liquidity_manager.add_liquidity(
            user_id,
            request.pool_id,
            request.amount_a,
            request.amount_b
        )
        return {"position_id": position_id, "message": "Liquidity added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/liquidity/remove")
async def remove_liquidity(user_id: str, position_id: str, percentage: float = 1.0, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Remove liquidity from a pool"""
    try:
        result = liquidity_manager.remove_liquidity(user_id, position_id, percentage)
        return {"result": result, "message": "Liquidity removed successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/liquidity/swap")
async def swap_tokens(user_id: str, request: SwapRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Execute a token swap"""
    try:
        result = liquidity_manager.swap(
            user_id,
            request.token_in,
            request.token_out,
            request.amount_in,
            request.min_amount_out
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/liquidity/orders/limit")
async def place_limit_order(user_id: str, request: LimitOrderRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Place a limit order"""
    try:
        order_id = liquidity_manager.place_limit_order(
            user_id,
            request.symbol,
            request.side,
            request.amount,
            request.price
        )
        return {"order_id": order_id, "message": "Limit order placed successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/liquidity/pools/{pool_id}")
async def get_pool_info(pool_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get detailed information about a pool"""
    try:
        info = liquidity_manager.get_pool_info(pool_id)
        return info
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/v1/liquidity/positions/{user_id}")
async def get_user_positions(user_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all liquidity positions for a user"""
    try:
        positions = liquidity_manager.get_user_liquidity_positions(user_id)
        return {"positions": positions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/liquidity/orderbook/{symbol}")
async def get_order_book(symbol: str, depth: int = Query(20, ge=1, le=100), credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get the order book for a symbol"""
    try:
        book = liquidity_manager.get_order_book(symbol, depth)
        return book
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/liquidity/pools")
async def list_pools(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """List all available pools"""
    pools = []
    for pool_id, pool in liquidity_manager.pools.items():
        pools.append({
            "id": pool_id,
            "token_a": pool.token_a.symbol,
            "token_b": pool.token_b.symbol,
            "pool_type": pool.pool_type.value,
            "reserve_a": pool.reserve_a,
            "reserve_b": pool.reserve_b,
            "apr": pool.apr,
            "fee_rate": pool.fee_rate
        })
    return {"pools": pools}

@app.post("/api/v1/liquidity/rebalance")
async def rebalance_pools(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Rebalance all liquidity pools"""
    try:
        liquidity_manager.rebalance_pools()
        return {"message": "Pools rebalanced successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=8002)