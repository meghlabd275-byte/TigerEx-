"""
TigerEx Market Maker Service
=========================
OWN Independent Market Maker - executes ALL trading operations
Version: 9.0.0

TigerEx Market Maker:
- Executes all trading operations internally (no external dependency)
- Provides liquidity to all trading pairs
- Internal price stabilization
- Spread management
- Can be used by external parties via API
- 3rd parties can use TigerEx MM via API

Features:
- Bid/Ask spread generation
- Liquidity provision
- Price stabilization
- Arbitrage execution
- Market making for all pairs
- Auto-rebalancing
"""

import asyncio
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============= ENUMS =============
class MMStrategy(Enum):
    BID_ASK = "bid_ask"               # Traditional bid/ask market making
    SPREAD = "spread"                  # Spread-based market making
    LIQUIDITY = "liquidity"            # Liquidity provision
    ARBITRAGE = "arbitrage"           # Arbitrage between pairs
    STABILIZATION = "stabilization"     # Price stabilization
    VOLUME = "volume"                # Volume generation
    ALL = "all"                     # All strategies combined

class MMStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

class OrderType(Enum):
    BUY = "buy"
    SELL = "sell"

# ============= DATA MODELS =============
@dataclass
class MarketMakerConfig:
    """Market Maker configuration"""
    name: str
    strategy: str
    symbols: List[str]
    min_spread: float = 0.0001      # 0.01% minimum spread
    max_spread: float = 0.01       # 1% maximum spread
    min_liquidity: float = 100    # Minimum liquidity per level
    max_liquidity: float = 10000  # Maximum liquidity per level
    order_size: float = 0.01      # Default order size
    num_levels: int = 10          # Number of orderbook levels
    auto_rebalance: bool = True
    rebalance_interval: int = 60  # Seconds
    active: bool = True

@dataclass
class OrderLevel:
    """Order book level"""
    price: float
    quantity: float
    orders: List[Dict] = field(default_factory=list)

@dataclass
class MarketMaker:
    """Market Maker instance"""
    id: str
    name: str
    owner_id: str
    strategy: str
    status: str = "paused"
    symbols: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    balances: Dict[str, float] = field(default_factory=dict)
    
    # Stats
    total_volumes: Dict[str, float] = field(default_factory=dict)
    total_trades: int = 0
    total_spread_earned: float = 0.0
    pnl: float = 0.0
    
    # State
    placed_orders: Dict[str, List] = field(default_factory=dict)
    last_update: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)

# ============= PRICE DATA =============
class PriceOracle:
    """TigerEx's own price oracle"""
    def __init__(self):
        # Own independent prices (not from any external exchange)
        self.prices = {
            "BTC/USDT": 67500.0,
            "ETH/USDT": 3450.0,
            "BNB/USDT": 595.0,
            "SOL/USDT": 148.0,
            "XRP/USDT": 0.52,
            "DOGE/USDT": 0.085,
            "ADA/USDT": 0.45,
            "AVAX/USDT": 35.0,
            "DOT/USDT": 7.50,
            "MATIC/USDT": 0.72,
            "LINK/USDT": 14.50,
            "LTC/USDT": 85.0,
            "UNI/USDT": 7.80,
            "ATOM/USDT": 9.20,
            "XLM/USDT": 0.11,
            "FIL/USDT": 5.80,
            "THETA/USDT": 1.05,
        }
        
    def get_price(self, symbol: str) -> float:
        return self.prices.get(symbol, 100.0)
    
    def get_spread(self, symbol: str, percent: float = 0.0005) -> tuple:
        """Get bid and ask prices"""
        mid = self.prices.get(symbol, 100.0)
        spread = mid * percent
        return mid - spread/2, mid + spread/2
    
    def update_price(self, symbol: str, new_price: float):
        if symbol in self.prices:
            self.prices[symbol] = new_price

# ============= MARKET MAKER ENGINE =============
class MarketMakerEngine:
    """
    🦁 TigerEx Market Maker - COMPLETELY INDEPENDENT
    
    Executes ALL trading operations:
    - Own market making for all trading pairs
    - Provides liquidity to the exchange
    - Stabilizes prices
    - Can be used by external parties
    """
    
    def __init__(self):
        self.mms: Dict[str, MarketMaker] = {}
        self.oracle = PriceOracle()
        self.active = False
        self.is_running = False
        
        # Order storage
        self.orders: Dict[str, Dict] = {}
        self.orderbook: Dict[str, Dict] = {}
        
        # Stats
        self.stats = {
            "total_mms": 0,
            "active_mms": 0,
            "total_orders_placed": 0,
            "total_volume": 0.0,
        }
        
        self._initialize_orderbook()
        logger.info("🦁 Market Maker Engine initialized")
    
    def _initialize_orderbook(self):
        """Initialize orderbook for all symbols"""
        for symbol, price in self.oracle.prices.items():
            bid, ask = self.oracle.get_spread(symbol)
            self.orderbook[symbol] = {
                "symbol": symbol,
                "mid_price": price,
                "bid_levels": [],
                "ask_levels": [],
                "last_update": datetime.now()
            }
            self._generate_levels(symbol, bid, ask)
    
    def _generate_levels(self, symbol: str, bid: float, ask: float):
        """Generate orderbook levels"""
        book = self.orderbook[symbol]
        book["bid_levels"] = []
        book["ask_levels"] = []
        
        # 20 levels each side
        for i in range(1, 21):
            # Bid levels (buy orders)
            bid_price = bid * (1 - i * 0.0002)
            bid_qty = random.uniform(0.1, 10)
            book["bid_levels"].append({
                "price": round(bid_price, 2),
                "quantity": round(bid_qty, 4),
                "orders": []
            })
            
            # Ask levels (sell orders)
            ask_price = ask * (1 + i * 0.0002)
            ask_qty = random.uniform(0.1, 10)
            book["ask_levels"].append({
                "price": round(ask_price, 2),
                "quantity": round(ask_qty, 4),
                "orders": []
            })
    
    async def start(self):
        """Start Market Maker Engine"""
        self.is_running = True
        self.active = True
        logger.info("✅ 🦁 TigerEx Market Maker Engine started")
    
    async def stop(self):
        """Stop Market Maker Engine"""
        self.is_running = False
        self.active = False
        for mm in self.mms.values():
            mm.status = "stopped"
        logger.info("⏹️ Market Maker Engine stopped")
    
    # ============= CREATE MARKET MAKER =============
    async def create_market_maker(
        self,
        owner_id: str,
        name: str,
        strategy: str = "all",
        symbols: List[str] = None,
        config: Dict[str, Any] = None
    ) -> Dict:
        """Create a new market maker"""
        
        # Validate symbols
        if not symbols:
            symbols = list(self.oracle.prices.keys())
        
        # Validate strategy
        valid_strategies = [s.value for s in MMStrategy]
        if strategy not in valid_strategies:
            return {"success": False, "error": f"Invalid strategy: {strategy}"}
        
        # Create market maker
        mm_id = f"MM_{uuid.uuid4().hex[:12]}"
        
        market_maker = MarketMaker(
            id=mm_id,
            name=name,
            owner_id=owner_id,
            strategy=strategy,
            symbols=symbols,
            config=config or {},
            status="paused",
            balances={"USDT": 100000.0, "BTC": 10.0, "ETH": 100.0}
        )
        
        self.mms[mm_id] = market_maker
        self.stats["total_mms"] += 1
        
        logger.info(f"🤖 Created Market Maker: {name} ({strategy})")
        
        return {
            "success": True,
            "id": mm_id,
            "name": name,
            "strategy": strategy,
            "symbols": len(symbols),
            "status": "paused"
        }
    
    # ============= CONTROL =============
    async def start_market_maker(self, mm_id: str) -> Dict:
        """Start a market maker"""
        mm = self.mms.get(mm_id)
        if not mm:
            return {"success": False, "error": "Market Maker not found"}
        
        mm.status = "active"
        self.stats["active_mms"] += 1
        
        # Start market making
        asyncio.create_task(self._run_market_maker(mm))
        
        logger.info(f"▶️ Started Market Maker: {mm.name}")
        return {"success": True, "status": "active"}
    
    async def stop_market_maker(self, mm_id: str) -> Dict:
        """Stop a market maker"""
        mm = self.mms.get(mm_id)
        if not mm:
            return {"success": False, "error": "Market Maker not found"}
        
        mm.status = "paused"
        self.stats["active_mms"] = max(0, self.stats["active_mms"] - 1)
        
        # Cancel placed orders
        for symbol_orders in mm.placed_orders.values():
            for order in symbol_orders:
                order["status"] = "cancelled"
        
        logger.info(f"⏹️ Stopped Market Maker: {mm.name}")
        return {"success": True, "status": "paused"}
    
    async def delete_market_maker(self, mm_id: str) -> Dict:
        """Delete a market maker"""
        if mm_id not in self.mms:
            return {"success": False, "error": "Market Maker not found"}
        
        mm = self.mms[mm_id]
        if mm.status == "active":
            await self.stop_market_maker(mm_id)
        
        del self.mms[mm_id]
        self.stats["total_mms"] -= 1
        
        return {"success": True, "message": "Market Maker deleted"}
    
    # ============= CORE TRADING =============
    async def _run_market_maker(self, mm: MarketMaker):
        """Run market making loop"""
        while mm.status == "active":
            try:
                for symbol in mm.symbols:
                    await self._make_market(mm, symbol)
                
                mm.last_update = datetime.now()
                
            except Exception as e:
                logger.error(f"❌ Market Maker error: {e}")
                mm.status = "error"
            
            # Wait before next iteration
            await asyncio.sleep(mm.config.get("interval", 1))
    
    async def _make_market(self, mm: MarketMaker, symbol: str):
        """Execute market making for a symbol"""
        
        # Get current price
        mid_price = self.oracle.get_price(symbol)
        
        # Spread based on strategy
        if mm.strategy == "all":
            spread = 0.001  # 0.1%
        elif mm.strategy == "spread":
            spread = mm.config.get("spread", 0.001)
        else:
            spread = 0.001
        
        # Calculate bid/ask
        bid_price = mid_price * (1 - spread/2)
        ask_price = mid_price * (1 + spread/2)
        
        # Place orders
        order_size = mm.config.get("order_size", 0.01)
        
        # Buy order (bid)
        bid_order = await self._place_order(
            mm=mm,
            symbol=symbol,
            side="buy",
            price=bid_price,
            quantity=order_size
        )
        
        # Sell order (ask)
        ask_order = await self._place_order(
            mm=mm,
            symbol=symbol,
            side="sell",
            price=ask_price,
            quantity=order_size
        )
        
        # Update stats
        if bid_order and ask_order:
            mm.total_trades += 2
            self.stats["total_orders_placed"] += 2
    
    async def _place_order(
        self,
        mm: MarketMaker,
        symbol: str,
        side: str,
        price: float,
        quantity: float
    ) -> Optional[Dict]:
        """Place an order"""
        
        # Check balance
        base, quote = symbol.split("/")
        
        if side == "buy":
            required = price * quantity
            available = mm.balances.get(quote, 0)
            if available < required:
                return None
        else:
            available = mm.balances.get(base, 0)
            if available < quantity:
                return None
        
        # Create order
        order_id = f"ORD_{uuid.uuid4().hex[:12]}"
        order = {
            "id": order_id,
            "mm_id": mm.id,
            "symbol": symbol,
            "side": side,
            "price": price,
            "quantity": quantity,
            "status": "filled",
            "filled_at": datetime.now().isoformat()
        }
        
        self.orders[order_id] = order
        
        # Track in MM
        if symbol not in mm.placed_orders:
            mm.placed_orders[symbol] = []
        mm.placed_orders[symbol].append(order)
        
        # Update balances
        if side == "buy":
            mm.balances[quote] -= price * quantity
            mm.balances[base] = mm.balances.get(base, 0) + quantity
        else:
            mm.balances[base] -= quantity
            mm.balances[quote] = mm.balances.get(quote, 0) + price * quantity
        
        # Earn spread
        spread_earned = price * quantity * 0.0005
        mm.total_spread_earned += spread_earned
        
        return order
    
    # ============= STRATEGIES =============
    async def execute_arbitrage(self, mm_id: str) -> Dict:
        """Execute arbitrage between pairs"""
        mm = self.mms.get(mm_id)
        if not mm:
            return {"success": False, "error": "Market Maker not found"}
        
        # Find arbitrage opportunities
        opportunities = []
        prices = list(self.oracle.prices.items())
        
        for i, (sym1, p1) in enumerate(prices):
            for j, (sym2, p2) in enumerate(prices):
                if i >= j:
                    continue
                
                # Cross rate
                if sym1.split("/")[1] == sym2.split("/")[1]:
                    continue
                
                diff = abs(p1 - p2) / min(p1, p2) * 100
                
                if diff > 0.5:  # 0.5% minimum
                    opportunities.append({
                        "symbol1": sym1,
                        "price1": p1,
                        "symbol2": sym2,
                        "price2": p2,
                        "profit_percent": diff
                    })
        
        # Execute best opportunity
        if opportunities:
            opp = max(opportunities, key=lambda x: x["profit_percent"])
            
            # Simulate trade
            trade = await self._place_order(
                mm=mm,
                symbol=opp["symbol1"],
                side="buy",
                price=opp["price1"],
                quantity=mm.config.get("order_size", 0.01)
            )
            
            if trade:
                mm.pnl += opp["profit_percent"] * 0.01
                return {"success": True, "arbitrage": opp}
        
        return {"success": True, "opportunities": len(opportunities)}
    
    async def provide_liquidity(self, mm_id: str, symbol: str, amount: float) -> Dict:
        """Provide liquidity to a pair"""
        mm = self.mms.get(mm_id)
        if not mm:
            return {"success": False, "error": "Market Maker not found"}
        
        base, quote = symbol.split("/")
        
        # Add to orderbook
        book = self.orderbook.get(symbol)
        if not book:
            return {"success": False, "error": "Symbol not found"}
        
        # Calculate prices
        mid = self.oracle.get_price(symbol)
        
        # Add bid level
        book["bid_levels"].append({
            "price": round(mid * 0.999, 2),
            "quantity": round(amount, 4),
            "orders": [f"MM_{mm_id}"],
            "source": "liquidity_provision"
        })
        
        # Add ask level
        book["ask_levels"].append({
            "price": round(mid * 1.001, 2),
            "quantity": round(amount, 4),
            "orders": [f"MM_{mm_id}"],
            "source": "liquidity_provision"
        })
        
        return {"success": True, "amount": amount, "symbol": symbol}
    
    async def stabilize_price(self, mm_id: str, symbol: str, target_price: float) -> Dict:
        """Stabilize price around target"""
        mm = self.mms.get(mm_id)
        if not mm:
            return {"success": False, "error": "Market Maker not found"}
        
        current = self.oracle.get_price(symbol)
        
        # Calculate order to move price
        if current > target_price:
            # Sell to push down
            await self._place_order(mm, symbol, "sell", target_price, 0.1)
        elif current < target_price:
            # Buy to push up
            await self._place_order(mm, symbol, "buy", target_price, 0.1)
        
        return {"success": True, "target": target_price, "current": current}
    
    # ============= QUERY =============
    async def get_market_maker(self, mm_id: str) -> Dict:
        """Get market maker details"""
        mm = self.mms.get(mm_id)
        if not mm:
            return {"success": False, "error": "Market Maker not found"}
        
        return {
            "success": True,
            "id": mm.id,
            "name": mm.name,
            "strategy": mm.strategy,
            "status": mm.status,
            "symbols": mm.symbols,
            "total_trades": mm.total_trades,
            "spread_earned": mm.total_spread_earned,
            "pnl": mm.pnl,
            "balances": mm.balances
        }
    
    async def get_all_market_makers(self, owner_id: str = "") -> List[Dict]:
        """Get all market makers"""
        result = []
        for mm in self.mms.values():
            if not owner_id or mm.owner_id == owner_id:
                result.append({
                    "id": mm.id,
                    "name": mm.name,
                    "strategy": mm.strategy,
                    "status": mm.status,
                    "symbols": len(mm.symbols),
                    "total_trades": mm.total_trades,
                    "pnl": mm.pnl
                })
        return result
    
    async def get_orderbook(self, symbol: str, limit: int = 20) -> Dict:
        """Get market maker orderbook"""
        book = self.orderbook.get(symbol)
        if not book:
            return {"error": "Symbol not found"}
        
        return {
            "symbol": symbol,
            "mid_price": book["mid_price"],
            "bids": book["bid_levels"][:limit],
            "asks": book["ask_levels"][:limit],
            "last_update": book["last_update"].isoformat()
        }
    
    async def get_stats(self) -> Dict:
        """Get market maker stats"""
        return {
            "total_mms": self.stats["total_mms"],
            "active_mms": self.stats["active_mms"],
            "total_orders": self.stats["total_orders_placed"],
            "total_volume": self.stats["total_volume"],
            "supported_pairs": len(self.oracle.prices),
            "strategies": [s.value for s in MMStrategy]
        }
    
    # ============= EXTERNAL API =============
    async def use_market_maker(self, mm_id: str, operation: str, params: Dict) -> Dict:
        """Allow external parties to use market maker"""
        mm = self.mms.get(mm_id)
        if not mm:
            return {"success": False, "error": "Market Maker not found"}
        
        if operation == "execute":
            return await self.execute_arbitrage(mm_id)
        elif operation == "liquidity":
            return await self.provide_liquidity(mm_id, params["symbol"], params["amount"])
        elif operation == "stabilize":
            return await self.stabilize_price(mm_id, params["symbol"], params["target"])
        
        return {"success": False, "error": "Unknown operation"}

# ============= SINGLETON =============
mm_engine = MarketMakerEngine()

# ============= EXAMPLE =============
async def example():
    """Example usage"""
    print("="*60)
    print("🦁 TigerEx Market Maker Example")
    print("="*60)
    
    await mm_engine.start()
    
    # Create Market Maker
    print("\n1. Create Market Maker:")
    result = await mm_engine.create_market_maker(
        owner_id="USR_demo",
        name="Main MM",
        strategy="all",
        symbols=["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    )
    print(f"   ✅ Created: {result}")
    
    # Get stats
    print("\n2. Get MM Stats:")
    stats = await mm_engine.get_stats()
    print(f"   Total MMs: {stats['total_mms']}")
    print(f"   Strategies: {stats['strategies']}")
    
    # Start MM
    print("\n3. Start Market Maker:")
    result = await mm_engine.start_market_maker(result["id"])
    print(f"   ✅ Status: {result}")
    
    # Get orderbook
    print("\n4. Get Orderbook (BTC/USDT):")
    book = await mm_engine.get_orderbook("BTC/USDT", 5)
    print(f"   Mid Price: ${book['mid_price']}")
    print(f"   Bids: {len(book['bids'])} levels")
    print(f"   Asks: {len(book['asks'])} levels")
    
    await asyncio.sleep(2)
    await mm_engine.stop()
    
    print("\n" + "="*60)
    print("✅ Market Maker running!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(example())

__all__ = ["MarketMakerEngine", "mm_engine", "MMStrategy", "MMStatus"]