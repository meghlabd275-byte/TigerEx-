"""
TigerEx Exchange Platform
Version: 7.0.0 - Production Release

Liquidation Protection Service
Advanced liquidation protection and margin call systems
"""

import asyncio
import json
import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PositionType(Enum):
    LONG = "long"
    SHORT = "short"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ProtectionStatus(Enum):
    ACTIVE = "active"
    TRIGGERED = "triggered"
    DISABLED = "disabled"

class MarginCallStatus(Enum):
    NONE = "none"
    WARNING = "warning"
    MARGIN_CALL = "margin_call"
    LIQUIDATION = "liquidation"

@dataclass
class Position:
    id: str
    user_id: str
    symbol: str
    position_type: PositionType
    size: float
    entry_price: float
    current_price: float
    leverage: float
    margin: float
    unrealized_pnl: float
    liquidation_price: float
    margin_ratio: float
    created_at: datetime
    updated_at: datetime

@dataclass
class LiquidationProtection:
    id: str
    user_id: str
    position_id: str
    protection_type: str
    trigger_price: float
    protection_amount: float
    status: ProtectionStatus
    created_at: datetime
    triggered_at: Optional[datetime] = None

@dataclass
class MarginCall:
    id: str
    user_id: str
    position_id: str
    status: MarginCallStatus
    margin_ratio: float
    required_margin: float
    liquidation_price: float
    time_to_liquidation: timedelta
    created_at: datetime
    resolved_at: Optional[datetime] = None

@dataclass
class RiskMetrics:
    user_id: str
    total_margin: float
    used_margin: float
    free_margin: float
    margin_level: float
    risk_level: RiskLevel
    positions_count: int
    total_unrealized_pnl: float
    portfolio_value: float
    max_drawdown: float
    calculated_at: datetime

class LiquidationProtectionService:
    def __init__(self):
        self.positions: Dict[str, Position] = {}
        self.protections: Dict[str, LiquidationProtection] = {}
        self.margin_calls: Dict[str, MarginCall] = {}
        self.risk_metrics: Dict[str, RiskMetrics] = {}
        self.market_prices: Dict[str, float] = {}
        self.running = False
        
    async def initialize(self):
        """Initialize the liquidation protection service"""
        logger.info("🛡️ Initializing Liquidation Protection Service...")
        
        # Load sample market data
        await self._load_market_data()
        
        # Load sample positions
        await self._load_sample_positions()
        
        # Start monitoring task
        asyncio.create_task(self._monitor_positions())
        
        self.running = True
        logger.info("✅ Liquidation Protection Service initialized")
    
    async def _load_market_data(self):
        """Load sample market data"""
        self.market_prices = {
            "BTCUSDT": 43250.50,
            "ETHUSDT": 2680.75,
            "BNBUSDT": 315.20,
            "ADAUSDT": 0.485,
            "SOLUSDT": 98.45,
            "DOTUSDT": 7.25,
            "LINKUSDT": 14.85,
            "AVAXUSDT": 36.90,
            "MATICUSDT": 0.825,
            "UNIUSDT": 6.45
        }
    
    async def _load_sample_positions(self):
        """Load sample positions for demonstration"""
        sample_positions = [
            {
                "user_id": "user_001",
                "symbol": "BTCUSDT",
                "position_type": "long",
                "size": 0.5,
                "entry_price": 42000.0,
                "leverage": 10.0,
                "margin": 2100.0
            },
            {
                "user_id": "user_002",
                "symbol": "ETHUSDT",
                "position_type": "short",
                "size": 2.0,
                "entry_price": 2700.0,
                "leverage": 5.0,
                "margin": 1080.0
            }
        ]
        
        for pos_data in sample_positions:
            await self.create_position(pos_data)
    
    async def create_position(self, position_data: Dict[str, Any]) -> Position:
        """Create a new position"""
        try:
            position_id = f"pos_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            symbol = position_data["symbol"]
            current_price = self.market_prices.get(symbol, position_data["entry_price"])
            
            position = Position(
                id=position_id,
                user_id=position_data["user_id"],
                symbol=symbol,
                position_type=PositionType(position_data["position_type"]),
                size=float(position_data["size"]),
                entry_price=float(position_data["entry_price"]),
                current_price=current_price,
                leverage=float(position_data["leverage"]),
                margin=float(position_data["margin"]),
                unrealized_pnl=0.0,
                liquidation_price=0.0,
                margin_ratio=0.0,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Calculate derived values
            await self._update_position_metrics(position)
            
            self.positions[position_id] = position
            
            logger.info(f"📊 Created position: {position_id} for {position.symbol}")
            return position
            
        except Exception as e:
            logger.error(f"❌ Error creating position: {e}")
            raise
    
    async def _update_position_metrics(self, position: Position):
        """Update position metrics"""
        try:
            # Update current price
            position.current_price = self.market_prices.get(position.symbol, position.current_price)
            
            # Calculate unrealized PnL
            if position.position_type == PositionType.LONG:
                position.unrealized_pnl = (position.current_price - position.entry_price) * position.size
            else:
                position.unrealized_pnl = (position.entry_price - position.current_price) * position.size
            
            # Calculate liquidation price
            position.liquidation_price = self._calculate_liquidation_price(position)
            
            # Calculate margin ratio
            position.margin_ratio = self._calculate_margin_ratio(position)
            
            position.updated_at = datetime.now()
            
        except Exception as e:
            logger.error(f"❌ Error updating position metrics: {e}")
    
    def _calculate_liquidation_price(self, position: Position) -> float:
        """Calculate liquidation price for a position"""
        try:
            # Simplified liquidation price calculation
            # Real implementation would consider fees, funding rates, etc.
            
            maintenance_margin_rate = 0.05  # 5% maintenance margin
            
            if position.position_type == PositionType.LONG:
                # Long liquidation price
                liquidation_price = position.entry_price * (1 - (1 / position.leverage) + maintenance_margin_rate)
            else:
                # Short liquidation price
                liquidation_price = position.entry_price * (1 + (1 / position.leverage) - maintenance_margin_rate)
            
            return max(0, liquidation_price)
            
        except Exception as e:
            logger.error(f"❌ Error calculating liquidation price: {e}")
            return 0.0
    
    def _calculate_margin_ratio(self, position: Position) -> float:
        """Calculate margin ratio"""
        try:
            equity = position.margin + position.unrealized_pnl
            used_margin = abs(position.size * position.current_price) / position.leverage
            
            if used_margin > 0:
                return (equity / used_margin) * 100
            return 0.0
            
        except Exception as e:
            logger.error(f"❌ Error calculating margin ratio: {e}")
            return 0.0
    
    async def create_liquidation_protection(self, protection_data: Dict[str, Any]) -> LiquidationProtection:
        """Create liquidation protection for a position"""
        try:
            protection_id = f"prot_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            position = self.positions.get(protection_data["position_id"])
            if not position:
                raise ValueError("Position not found")
            
            protection = LiquidationProtection(
                id=protection_id,
                user_id=protection_data["user_id"],
                position_id=protection_data["position_id"],
                protection_type=protection_data["protection_type"],
                trigger_price=float(protection_data["trigger_price"]),
                protection_amount=float(protection_data["protection_amount"]),
                status=ProtectionStatus.ACTIVE,
                created_at=datetime.now()
            )
            
            self.protections[protection_id] = protection
            
            logger.info(f"🛡️ Created liquidation protection: {protection_id}")
            return protection
            
        except Exception as e:
            logger.error(f"❌ Error creating protection: {e}")
            raise
    
    async def _monitor_positions(self):
        """Monitor positions for liquidation risk"""
        while self.running:
            try:
                for position in self.positions.values():
                    await self._update_position_metrics(position)
                    await self._check_margin_requirements(position)
                    await self._check_liquidation_protection(position)
                
                await self._update_risk_metrics()
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"❌ Error in position monitoring: {e}")
                await asyncio.sleep(5)
    
    async def _check_margin_requirements(self, position: Position):
        """Check margin requirements and issue margin calls"""
        try:
            margin_ratio = position.margin_ratio
            
            # Determine margin call status
            if margin_ratio <= 110:  # Critical - liquidation imminent
                status = MarginCallStatus.LIQUIDATION
            elif margin_ratio <= 120:  # Margin call
                status = MarginCallStatus.MARGIN_CALL
            elif margin_ratio <= 150:  # Warning
                status = MarginCallStatus.WARNING
            else:
                status = MarginCallStatus.NONE
            
            # Create or update margin call
            if status != MarginCallStatus.NONE:
                await self._create_or_update_margin_call(position, status)
            
        except Exception as e:
            logger.error(f"❌ Error checking margin requirements: {e}")
    
    async def _create_or_update_margin_call(self, position: Position, status: MarginCallStatus):
        """Create or update margin call"""
        try:
            # Find existing margin call
            existing_call = None
            for call in self.margin_calls.values():
                if call.position_id == position.id and call.resolved_at is None:
                    existing_call = call
                    break
            
            if existing_call:
                existing_call.status = status
                existing_call.margin_ratio = position.margin_ratio
                existing_call.liquidation_price = position.liquidation_price
            else:
                call_id = f"call_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
                
                # Calculate time to liquidation
                time_to_liquidation = self._calculate_time_to_liquidation(position)
                
                margin_call = MarginCall(
                    id=call_id,
                    user_id=position.user_id,
                    position_id=position.id,
                    status=status,
                    margin_ratio=position.margin_ratio,
                    required_margin=abs(position.size * position.current_price) / position.leverage,
                    liquidation_price=position.liquidation_price,
                    time_to_liquidation=time_to_liquidation,
                    created_at=datetime.now()
                )
                
                self.margin_calls[call_id] = margin_call
                
                logger.warning(f"⚠️ Margin call created: {call_id} for position {position.id}")
            
        except Exception as e:
            logger.error(f"❌ Error creating margin call: {e}")
    
    def _calculate_time_to_liquidation(self, position: Position) -> timedelta:
        """Calculate estimated time to liquidation"""
        try:
            # Simplified calculation based on current price movement
            # Real implementation would consider volatility, funding rates, etc.
            
            price_distance = abs(position.current_price - position.liquidation_price)
            current_price = position.current_price
            
            if current_price > 0:
                price_distance_pct = price_distance / current_price
                
                # Assume 1% price movement per hour (simplified)
                hours_to_liquidation = price_distance_pct / 0.01
                
                return timedelta(hours=max(0.1, hours_to_liquidation))
            
            return timedelta(hours=1)
            
        except Exception as e:
            logger.error(f"❌ Error calculating time to liquidation: {e}")
            return timedelta(hours=1)
    
    async def _check_liquidation_protection(self, position: Position):
        """Check and trigger liquidation protection"""
        try:
            for protection in self.protections.values():
                if (protection.position_id == position.id and 
                    protection.status == ProtectionStatus.ACTIVE):
                    
                    should_trigger = False
                    
                    if protection.protection_type == "stop_loss":
                        if position.position_type == PositionType.LONG:
                            should_trigger = position.current_price <= protection.trigger_price
                        else:
                            should_trigger = position.current_price >= protection.trigger_price
                    
                    elif protection.protection_type == "margin_protection":
                        should_trigger = position.margin_ratio <= protection.trigger_price
                    
                    if should_trigger:
                        await self._trigger_protection(protection, position)
            
        except Exception as e:
            logger.error(f"❌ Error checking liquidation protection: {e}")
    
    async def _trigger_protection(self, protection: LiquidationProtection, position: Position):
        """Trigger liquidation protection"""
        try:
            protection.status = ProtectionStatus.TRIGGERED
            protection.triggered_at = datetime.now()
            
            # Execute protection action (simplified)
            if protection.protection_type == "stop_loss":
                # Close position at market price
                await self._close_position(position, "Protection triggered")
            
            elif protection.protection_type == "margin_protection":
                # Add margin to position
                position.margin += protection.protection_amount
                await self._update_position_metrics(position)
            
            logger.info(f"🛡️ Protection triggered: {protection.id} for position {position.id}")
            
        except Exception as e:
            logger.error(f"❌ Error triggering protection: {e}")
    
    async def _close_position(self, position: Position, reason: str):
        """Close a position"""
        try:
            # Calculate final PnL
            final_pnl = position.unrealized_pnl
            
            # Remove position
            if position.id in self.positions:
                del self.positions[position.id]
            
            # Resolve any margin calls
            for call in self.margin_calls.values():
                if call.position_id == position.id and call.resolved_at is None:
                    call.resolved_at = datetime.now()
            
            logger.info(f"🔒 Position closed: {position.id}, PnL: {final_pnl:.2f}, Reason: {reason}")
            
        except Exception as e:
            logger.error(f"❌ Error closing position: {e}")
    
    async def _update_risk_metrics(self):
        """Update risk metrics for all users"""
        try:
            user_positions = {}
            
            # Group positions by user
            for position in self.positions.values():
                if position.user_id not in user_positions:
                    user_positions[position.user_id] = []
                user_positions[position.user_id].append(position)
            
            # Calculate risk metrics for each user
            for user_id, positions in user_positions.items():
                await self._calculate_user_risk_metrics(user_id, positions)
            
        except Exception as e:
            logger.error(f"❌ Error updating risk metrics: {e}")
    
    async def _calculate_user_risk_metrics(self, user_id: str, positions: List[Position]):
        """Calculate risk metrics for a user"""
        try:
            total_margin = sum(pos.margin for pos in positions)
            total_unrealized_pnl = sum(pos.unrealized_pnl for pos in positions)
            portfolio_value = total_margin + total_unrealized_pnl
            
            used_margin = sum(abs(pos.size * pos.current_price) / pos.leverage for pos in positions)
            free_margin = total_margin - used_margin
            
            margin_level = (portfolio_value / used_margin * 100) if used_margin > 0 else 0
            
            # Determine risk level
            if margin_level <= 120:
                risk_level = RiskLevel.CRITICAL
            elif margin_level <= 150:
                risk_level = RiskLevel.HIGH
            elif margin_level <= 200:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
            
            # Calculate max drawdown (simplified)
            max_drawdown = min(pos.unrealized_pnl for pos in positions) if positions else 0
            
            risk_metrics = RiskMetrics(
                user_id=user_id,
                total_margin=total_margin,
                used_margin=used_margin,
                free_margin=free_margin,
                margin_level=margin_level,
                risk_level=risk_level,
                positions_count=len(positions),
                total_unrealized_pnl=total_unrealized_pnl,
                portfolio_value=portfolio_value,
                max_drawdown=max_drawdown,
                calculated_at=datetime.now()
            )
            
            self.risk_metrics[user_id] = risk_metrics
            
        except Exception as e:
            logger.error(f"❌ Error calculating user risk metrics: {e}")
    
    async def get_user_positions(self, user_id: str) -> List[Position]:
        """Get all positions for a user"""
        return [pos for pos in self.positions.values() if pos.user_id == user_id]
    
    async def get_user_margin_calls(self, user_id: str) -> List[MarginCall]:
        """Get active margin calls for a user"""
        return [call for call in self.margin_calls.values() 
                if call.user_id == user_id and call.resolved_at is None]
    
    async def get_user_protections(self, user_id: str) -> List[LiquidationProtection]:
        """Get liquidation protections for a user"""
        return [prot for prot in self.protections.values() if prot.user_id == user_id]
    
    async def get_user_risk_metrics(self, user_id: str) -> Optional[RiskMetrics]:
        """Get risk metrics for a user"""
        return self.risk_metrics.get(user_id)
    
    async def add_margin(self, position_id: str, amount: float) -> bool:
        """Add margin to a position"""
        try:
            position = self.positions.get(position_id)
            if not position:
                return False
            
            position.margin += amount
            await self._update_position_metrics(position)
            
            logger.info(f"💰 Added {amount} margin to position {position_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding margin: {e}")
            return False
    
    async def update_market_price(self, symbol: str, price: float):
        """Update market price for a symbol"""
        self.market_prices[symbol] = price
        
        # Update all positions for this symbol
        for position in self.positions.values():
            if position.symbol == symbol:
                await self._update_position_metrics(position)

# FastAPI application
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Liquidation Protection Service", version="7.0.0")
protection_service = LiquidationProtectionService()

class PositionCreate(BaseModel):
    user_id: str
    symbol: str
    position_type: str
    size: float
    entry_price: float
    leverage: float
    margin: float

class ProtectionCreate(BaseModel):
    user_id: str
    position_id: str
    protection_type: str
    trigger_price: float
    protection_amount: float

@app.on_event("startup")
async def startup_event():
    await protection_service.initialize()

@app.post("/positions")
async def create_position(position: PositionCreate):
    try:
        new_position = await protection_service.create_position(position.dict())
        return {"success": True, "position": new_position}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/{user_id}/positions")
async def get_user_positions(user_id: str):
    return await protection_service.get_user_positions(user_id)

@app.get("/users/{user_id}/margin-calls")
async def get_user_margin_calls(user_id: str):
    return await protection_service.get_user_margin_calls(user_id)

@app.get("/users/{user_id}/protections")
async def get_user_protections(user_id: str):
    return await protection_service.get_user_protections(user_id)

@app.get("/users/{user_id}/risk-metrics")
async def get_user_risk_metrics(user_id: str):
    metrics = await protection_service.get_user_risk_metrics(user_id)
    if not metrics:
        raise HTTPException(status_code=404, detail="Risk metrics not found")
    return metrics

@app.post("/protections")
async def create_protection(protection: ProtectionCreate):
    try:
        new_protection = await protection_service.create_liquidation_protection(protection.dict())
        return {"success": True, "protection": new_protection}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/positions/{position_id}/add-margin")
async def add_margin(position_id: str, amount: float):
    success = await protection_service.add_margin(position_id, amount)
    return {"success": success}

@app.post("/market-prices/{symbol}")
async def update_market_price(symbol: str, price: float):
    await protection_service.update_market_price(symbol, price)
    return {"success": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)