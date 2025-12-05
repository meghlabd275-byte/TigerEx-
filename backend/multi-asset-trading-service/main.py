"""
TigerEx Multi-Asset Trading Service
Integration for Gold, FOREX, Commodities, and traditional financial assets
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

app = FastAPI(title="TigerEx Multi-Asset Trading Service", version="1.0.0")
security = HTTPBearer()

class AssetType(str, Enum):
    FOREX = "forex"
    COMMODITY = "commodity"
    METAL = "metal"
    INDEX = "index"
    STOCK = "stock"
    CRYPTO = "crypto"

class TradingSession(str, Enum):
    ASIAN = "asian"
    EUROPEAN = "european"
    AMERICAN = "american"
    TWENTY_FOUR_SEVEN = "24/7"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"

class PositionSide(str, Enum):
    LONG = "long"
    SHORT = "short"

@dataclass
class MarketData:
    symbol: str
    asset_type: AssetType
    current_price: float
    bid: float
    ask: float
    spread: float
    volume_24h: float
    change_24h: float
    high_24h: float
    low_24h: float
    trading_session: TradingSession
    leverage_max: int

class MultiAssetInstrument(BaseModel):
    symbol: str = Field(..., description="Trading symbol")
    name: str = Field(..., description="Full instrument name")
    asset_type: AssetType = Field(..., description="Asset category")
    trading_session: TradingSession = Field(..., description="Trading session availability")
    leverage_max: int = Field(default=500, description="Maximum leverage")
    minimum_lot_size: float = Field(default=0.01, description="Minimum lot size")
    tick_size: float = Field(default=0.00001, description="Minimum price increment")
    margin_requirement: float = Field(default=0.002, description="Margin requirement")
    overnight_fee: float = Field(default=-0.0005, description="Overnight swap fee")
    commission_rate: float = Field(default=0.00002, description="Commission rate")

class MultiAssetOrder(BaseModel):
    id: str
    user_id: str
    instrument: MultiAssetInstrument
    order_type: OrderType
    position_side: PositionSide
    lot_size: float
    entry_price: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    trailing_distance: Optional[float]
    leverage: int
    status: str
    created_at: datetime
    updated_at: datetime

class Position(BaseModel):
    id: str
    user_id: str
    instrument: MultiAssetInstrument
    position_side: PositionSide
    lot_size: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    margin_used: float
    swap_fees: float
    commission_paid: float
    open_time: datetime
    last_update: datetime

class MarketAnalysisRequest(BaseModel):
    symbol: str = Field(..., description="Symbol to analyze")
    timeframe: str = Field(default="1h", description="Timeframe for analysis")
    analysis_types: List[str] = Field(default=["technical", "fundamental", "sentiment"], description="Analysis types")

# In-memory storage (replace with database in production)
market_data_cache: Dict[str, MarketData] = {}
instruments: Dict[str, MultiAssetInstrument] = {}
active_orders: Dict[str, MultiAssetOrder] = {}
open_positions: Dict[str, Position] = {}

class MultiAssetMarketDataFeed:
    """Real-time market data for multiple asset classes"""
    
    def __init__(self):
        self.initialize_instruments()
        self.initialize_market_data()
    
    def initialize_instruments(self):
        """Initialize available trading instruments"""
        
        # FOREX pairs
        instruments["EUR/USD"] = MultiAssetInstrument(
            symbol="EUR/USD",
            name="Euro/US Dollar",
            asset_type=AssetType.FOREX,
            trading_session=TradingSession.TWENTY_FOUR_SEVEN,
            leverage_max=500,
            minimum_lot_size=0.01,
            tick_size=0.00001,
            margin_requirement=0.002,
            overnight_fee=0.0003,
            commission_rate=0.0000
        )
        
        instruments["GBP/USD"] = MultiAssetInstrument(
            symbol="GBP/USD",
            name="British Pound/US Dollar",
            asset_type=AssetType.FOREX,
            trading_session=TradingSession.TWENTY_FOUR_SEVEN,
            leverage_max=500,
            minimum_lot_size=0.01,
            tick_size=0.00001,
            margin_requirement=0.005,
            overnight_fee=0.0002,
            commission_rate=0.0000
        )
        
        instruments["USD/JPY"] = MultiAssetInstrument(
            symbol="USD/JPY",
            name="US Dollar/Japanese Yen",
            asset_type=AssetType.FOREX,
            trading_session=TradingSession.TWENTY_FOUR_SEVEN,
            leverage_max=500,
            minimum_lot_size=0.01,
            tick_size=0.001,
            margin_requirement=0.004,
            overnight_fee=-0.0001,
            commission_rate=0.0000
        )
        
        # Metals
        instruments["XAU/USD"] = MultiAssetInstrument(
            symbol="XAU/USD",
            name="Gold/US Dollar",
            asset_type=AssetType.METAL,
            trading_session=TradingSession.TWENTY_FOUR_SEVEN,
            leverage_max=400,
            minimum_lot_size=0.01,
            tick_size=0.01,
            margin_requirement=0.01,
            overnight_fee=-0.002,
            commission_rate=0.0000
        )
        
        instruments["XAG/USD"] = MultiAssetInstrument(
            symbol="XAG/USD",
            name="Silver/US Dollar",
            asset_type=AssetType.METAL,
            trading_session=TradingSession.TWENTY_FOUR_SEVEN,
            leverage_max=300,
            minimum_lot_size=0.01,
            tick_size=0.001,
            margin_requirement=0.02,
            overnight_fee=-0.0015,
            commission_rate=0.0000
        )
        
        # Commodities
        instruments["OIL/USD"] = MultiAssetInstrument(
            symbol="OIL/USD",
            name="Crude Oil/US Dollar",
            asset_type=AssetType.COMMODITY,
            trading_session=TradingSession.AMERICAN,
            leverage_max=200,
            minimum_lot_size=0.1,
            tick_size=0.01,
            margin_requirement=0.1,
            overnight_fee=-0.003,
            commission_rate=0.0001
        )
        
        instruments["NATGAS/USD"] = MultiAssetInstrument(
            symbol="NATGAS/USD",
            name="Natural Gas/US Dollar",
            asset_type=AssetType.COMMODITY,
            trading_session=TradingSession.AMERICAN,
            leverage_max=150,
            minimum_lot_size=0.1,
            tick_size=0.001,
            margin_requirement=0.15,
            overnight_fee=-0.0025,
            commission_rate=0.00015
        )
        
        # Indices
        instruments["SPX500"] = MultiAssetInstrument(
            symbol="SPX500",
            name="S&P 500 Index",
            asset_type=AssetType.INDEX,
            trading_session=TradingSession.AMERICAN,
            leverage_max=100,
            minimum_lot_size=0.1,
            tick_size=0.25,
            margin_requirement=0.05,
            overnight_fee=-0.001,
            commission_rate=0.0002
        )
        
        instruments["NAS100"] = MultiAssetInstrument(
            symbol="NAS100",
            name="NASDAQ 100 Index",
            asset_type=AssetType.INDEX,
            trading_session=TradingSession.AMERICAN,
            leverage_max=100,
            minimum_lot_size=0.1,
            tick_size=0.25,
            margin_requirement=0.05,
            overnight_fee=-0.001,
            commission_rate=0.0002
        )
        
        # Stocks (CFDs)
        instruments["AAPL"] = MultiAssetInstrument(
            symbol="AAPL",
            name="Apple Inc. Stock",
            asset_type=AssetType.STOCK,
            trading_session=TradingSession.AMERICAN,
            leverage_max=20,
            minimum_lot_size=1.0,
            tick_size=0.01,
            margin_requirement=0.2,
            overnight_fee=-0.0008,
            commission_rate=0.0005
        )
        
        instruments["TSLA"] = MultiAssetInstrument(
            symbol="TSLA",
            name="Tesla Inc. Stock",
            asset_type=AssetType.STOCK,
            trading_session=TradingSession.AMERICAN,
            leverage_max=20,
            minimum_lot_size=1.0,
            tick_size=0.01,
            margin_requirement=0.25,
            overnight_fee=-0.001,
            commission_rate=0.0005
        )
    
    def initialize_market_data(self):
        """Initialize current market data"""
        base_prices = {
            "EUR/USD": 1.0850,
            "GBP/USD": 1.2750,
            "USD/JPY": 149.50,
            "XAU/USD": 2030.50,
            "XAG/USD": 24.35,
            "OIL/USD": 78.25,
            "NATGAS/USD": 2.85,
            "SPX500": 4525.50,
            "NAS100": 17850.25,
            "AAPL": 185.75,
            "TSLA": 245.50
        }
        
        for symbol, base_price in base_prices.items():
            if symbol in instruments:
                instrument = instruments[symbol]
                
                # Generate realistic market data
                price_change = np.random.normal(0, 0.002) * base_price
                current_price = base_price + price_change
                
                # Calculate bid/ask spread based on asset type
                spread_pct = 0.0001 if instrument.asset_type == AssetType.FOREX else 0.0002
                spread = current_price * spread_pct
                
                market_data = MarketData(
                    symbol=symbol,
                    asset_type=instrument.asset_type,
                    current_price=current_price,
                    bid=current_price - spread/2,
                    ask=current_price + spread/2,
                    spread=spread,
                    volume_24h=np.random.uniform(1000000, 10000000),
                    change_24h=(price_change / base_price) * 100,
                    high_24h=current_price * np.random.uniform(1.01, 1.03),
                    low_24h=current_price * np.random.uniform(0.97, 0.99),
                    trading_session=instrument.trading_session,
                    leverage_max=instrument.leverage_max
                )
                
                market_data_cache[symbol] = market_data
    
    async def get_market_data(self, symbol: str) -> Optional[MarketData]:
        """Get current market data for a symbol"""
        if symbol in market_data_cache:
            # Simulate real-time price updates
            data = market_data_cache[symbol]
            price_change = np.random.normal(0, 0.0001) * data.current_price
            data.current_price += price_change
            data.bid = data.current_price - data.spread/2
            data.ask = data.current_price + data.spread/2
            return data
        return None
    
    async def get_instruments_by_type(self, asset_type: AssetType) -> List[MultiAssetInstrument]:
        """Get all instruments of a specific type"""
        return [inst for inst in instruments.values() if inst.asset_type == asset_type]

class MultiAssetTradingEngine:
    """Advanced trading engine for multiple asset classes"""
    
    def __init__(self):
        self.market_data = MultiAssetMarketDataFeed()
    
    async def calculate_margin_requirement(self, instrument: MultiAssetInstrument, lot_size: float, leverage: int) -> float:
        """Calculate margin requirement for a position"""
        market_data = await self.market_data.get_market_data(instrument.symbol)
        if not market_data:
            return 0.0
        
        position_value = market_data.current_price * lot_size
        margin = position_value * instrument.margin_requirement
        return margin
    
    async def calculate_pnl(self, position: Position) -> Dict[str, float]:
        """Calculate P&L for a position"""
        market_data = await self.market_data.get_market_data(position.instrument.symbol)
        if not market_data:
            return {"unrealized_pnl": 0.0, "percentage": 0.0}
        
        if position.position_side == PositionSide.LONG:
            price_diff = market_data.current_price - position.entry_price
            pnl_per_lot = price_diff
        else:  # SHORT
            price_diff = position.entry_price - market_data.current_price
            pnl_per_lot = price_diff
        
        unrealized_pnl = pnl_per_lot * position.lot_size
        percentage = (unrealized_pnl / (position.entry_price * position.lot_size)) * 100 if position.lot_size > 0 else 0
        
        return {
            "unrealized_pnl": unrealized_pnl,
            "percentage": percentage
        }
    
    async def execute_order(self, order: MultiAssetOrder) -> Position:
        """Execute an order and create a position"""
        market_data = await self.market_data.get_market_data(order.instrument.symbol)
        if not market_data:
            raise HTTPException(status_code=400, detail="Market data not available")
        
        # Determine entry price
        if order.order_type == OrderType.MARKET:
            if order.position_side == PositionSide.LONG:
                entry_price = market_data.ask
            else:
                entry_price = market_data.bid
        else:
            entry_price = order.entry_price
        
        # Calculate margin
        margin = await self.calculate_margin_requirement(order.instrument, order.lot_size, order.leverage)
        
        # Create position
        position = Position(
            id=f"pos_{datetime.now().timestamp()}_{len(open_positions)}",
            user_id=order.user_id,
            instrument=order.instrument,
            position_side=order.position_side,
            lot_size=order.lot_size,
            entry_price=entry_price,
            current_price=entry_price,
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            margin_used=margin,
            swap_fees=0.0,
            commission_paid=order.lot_size * order.instrument.commission_rate * entry_price,
            open_time=datetime.now(),
            last_update=datetime.now()
        )
        
        open_positions[position.id] = position
        return position
    
    async def close_position(self, position_id: str, user_id: str) -> Dict[str, Any]:
        """Close a position"""
        if position_id not in open_positions:
            raise HTTPException(status_code=404, detail="Position not found")
        
        position = open_positions[position_id]
        if position.user_id != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        market_data = await self.market_data.get_market_data(position.instrument.symbol)
        if not market_data:
            raise HTTPException(status_code=400, detail="Market data not available")
        
        # Determine exit price
        if position.position_side == PositionSide.LONG:
            exit_price = market_data.bid
        else:
            exit_price = market_data.ask
        
        # Calculate final P&L
        if position.position_side == PositionSide.LONG:
            price_diff = exit_price - position.entry_price
        else:
            price_diff = position.entry_price - exit_price
        
        final_pnl = price_diff * position.lot_size
        commission = position.lot_size * position.instrument.commission_rate * exit_price
        
        # Update position
        position.current_price = exit_price
        position.realized_pnl = final_pnl - commission
        position.unrealized_pnl = 0.0
        position.last_update = datetime.now()
        
        # Calculate holding period for swap fees
        holding_days = (datetime.now() - position.open_time).days
        swap_fees = position.lot_size * position.instrument.overnight_fee * position.entry_price * holding_days
        
        result = {
            "position_id": position_id,
            "entry_price": position.entry_price,
            "exit_price": exit_price,
            "lot_size": position.lot_size,
            "gross_pnl": final_pnl,
            "commission": commission,
            "swap_fees": swap_fees,
            "net_pnl": final_pnl - commission + swap_fees,
            "holding_days": holding_days,
            "return_percentage": ((final_pnl - commission + swap_fees) / (position.entry_price * position.lot_size)) * 100
        }
        
        # Remove from open positions
        del open_positions[position_id]
        
        return result

class MarketAnalyzer:
    """Advanced market analysis for multiple asset classes"""
    
    async def analyze_market(self, request: MarketAnalysisRequest) -> Dict[str, Any]:
        """Perform comprehensive market analysis"""
        
        if request.symbol not in instruments:
            raise HTTPException(status_code=404, detail="Instrument not found")
        
        instrument = instruments[request.symbol]
        market_data = await MultiAssetMarketDataFeed().get_market_data(request.symbol)
        
        if not market_data:
            raise HTTPException(status_code=400, detail="Market data not available")
        
        analysis = {
            "symbol": request.symbol,
            "current_price": market_data.current_price,
            "change_24h": market_data.change_24h,
            "volume_24h": market_data.volume_24h,
            "analysis": {}
        }
        
        # Technical Analysis
        if "technical" in request.analysis_types:
            analysis["analysis"]["technical"] = await self.perform_technical_analysis(request.symbol, request.timeframe)
        
        # Fundamental Analysis
        if "fundamental" in request.analysis_types:
            analysis["analysis"]["fundamental"] = await self.perform_fundamental_analysis(request.symbol)
        
        # Sentiment Analysis
        if "sentiment" in request.analysis_types:
            analysis["analysis"]["sentiment"] = await self.perform_sentiment_analysis(request.symbol)
        
        return analysis
    
    async def perform_technical_analysis(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Perform technical analysis"""
        # Simulated technical indicators (replace with real calculations)
        market_data = market_data_cache.get(symbol)
        
        if not market_data:
            return {}
        
        return {
            "trend": "bullish" if market_data.change_24h > 0 else "bearish",
            "rsi": np.random.uniform(30, 70),
            "macd": {
                "macd_line": np.random.uniform(-0.001, 0.001),
                "signal_line": np.random.uniform(-0.001, 0.001),
                "histogram": np.random.uniform(-0.0005, 0.0005)
            },
            "moving_averages": {
                "sma_20": market_data.current_price * np.random.uniform(0.98, 1.02),
                "sma_50": market_data.current_price * np.random.uniform(0.96, 1.04),
                "ema_12": market_data.current_price * np.random.uniform(0.99, 1.01),
                "ema_26": market_data.current_price * np.random.uniform(0.98, 1.02)
            },
            "bollinger_bands": {
                "upper": market_data.current_price * np.random.uniform(1.02, 1.05),
                "middle": market_data.current_price,
                "lower": market_data.current_price * np.random.uniform(0.95, 0.98)
            },
            "support_resistance": {
                "support": market_data.current_price * np.random.uniform(0.95, 0.98),
                "resistance": market_data.current_price * np.random.uniform(1.02, 1.05)
            },
            "signal": "buy" if np.random.random() > 0.5 else "sell",
            "confidence": np.random.uniform(0.6, 0.9)
        }
    
    async def perform_fundamental_analysis(self, symbol: str) -> Dict[str, Any]:
        """Perform fundamental analysis"""
        instrument = instruments[symbol]
        
        if instrument.asset_type == AssetType.FOREX:
            return await self.forex_fundamental_analysis(symbol)
        elif instrument.asset_type == AssetType.COMMODITY:
            return await self.commodity_fundamental_analysis(symbol)
        elif instrument.asset_type == AssetType.INDEX:
            return await self.index_fundamental_analysis(symbol)
        elif instrument.asset_type == AssetType.STOCK:
            return await self.stock_fundamental_analysis(symbol)
        else:
            return {"analysis": "Fundamental analysis not available for this asset type"}
    
    async def forex_fundamental_analysis(self, symbol: str) -> Dict[str, Any]:
        """Forex fundamental analysis"""
        return {
            "interest_rate_differential": np.random.uniform(-0.05, 0.05),
            "inflation_outlook": "moderate",
            "gdp_growth": "positive",
            "employment_data": "strong",
            "central_bank_stance": "hawkish" if np.random.random() > 0.5 else "dovish",
            "economic_calendar": {
                "high_impact_events": np.random.randint(1, 4),
                "medium_impact_events": np.random.randint(2, 6),
                "next_cpi_release": "in 3 days"
            },
            "correlation_matrix": {
                "with_gold": np.random.uniform(-0.3, 0.3),
                "with_oil": np.random.uniform(-0.2, 0.2),
                "with_sp500": np.random.uniform(-0.4, 0.4)
            }
        }
    
    async def commodity_fundamental_analysis(self, symbol: str) -> Dict[str, Any]:
        """Commodity fundamental analysis"""
        return {
            "supply_demand_balance": "tight" if np.random.random() > 0.5 else "balanced",
            "inventory_levels": "low" if np.random.random() > 0.5 else "normal",
            "production_trends": "increasing" if np.random.random() > 0.5 else "decreasing",
            "consumption_trends": "strong" if np.random.random() > 0.5 else "moderate",
            "geopolitical_factors": "stable" if np.random.random() > 0.5 else "tense",
            "weather_impact": "minimal" if np.random.random() > 0.5 else "significant",
            "storage_costs": np.random.uniform(0.001, 0.01)
        }
    
    async def index_fundamental_analysis(self, symbol: str) -> Dict[str, Any]:
        """Index fundamental analysis"""
        return {
            "earnings_growth": np.random.uniform(0.05, 0.15),
            "price_to_earnings": np.random.uniform(15, 30),
            "dividend_yield": np.random.uniform(0.01, 0.04),
            "market_sentiment": "bullish" if np.random.random() > 0.5 else "bearish",
            "sector_performance": {
                "technology": np.random.uniform(-0.05, 0.08),
                "healthcare": np.random.uniform(-0.03, 0.06),
                "finance": np.random.uniform(-0.04, 0.07)
            },
            "economic_outlook": "positive" if np.random.random() > 0.5 else "cautious"
        }
    
    async def stock_fundamental_analysis(self, symbol: str) -> Dict[str, Any]:
        """Stock fundamental analysis"""
        return {
            "revenue_growth": np.random.uniform(0.05, 0.25),
            "earnings_per_share": np.random.uniform(1.0, 10.0),
            "price_to_earnings": np.random.uniform(10, 40),
            "price_to_book": np.random.uniform(1.0, 8.0),
            "debt_to_equity": np.random.uniform(0.2, 1.5),
            "return_on_equity": np.random.uniform(0.05, 0.25),
            "analyst_ratings": {
                "buy": np.random.randint(5, 15),
                "hold": np.random.randint(3, 10),
                "sell": np.random.randint(0, 5)
            },
            "growth_prospects": "strong" if np.random.random() > 0.5 else "moderate"
        }
    
    async def perform_sentiment_analysis(self, symbol: str) -> Dict[str, Any]:
        """Perform sentiment analysis"""
        return {
            "overall_sentiment": np.random.uniform(-1, 1),
            "news_sentiment": np.random.uniform(-1, 1),
            "social_media_sentiment": np.random.uniform(-1, 1),
            "institutional_sentiment": np.random.uniform(-1, 1),
            "retail_sentiment": np.random.uniform(-1, 1),
            "sentiment_trend": "improving" if np.random.random() > 0.5 else "declining",
            "fear_greed_index": np.random.randint(20, 80),
            "volatility_expectation": "increasing" if np.random.random() > 0.5 else "decreasing"
        }

# Initialize services
trading_engine = MultiAssetTradingEngine()
market_analyzer = MarketAnalyzer()

@app.get("/multi-asset/instruments", response_model=List[MultiAssetInstrument])
async def get_instruments(asset_type: Optional[AssetType] = None):
    """Get available trading instruments"""
    all_instruments = list(instruments.values())
    
    if asset_type:
        all_instruments = [inst for inst in all_instruments if inst.asset_type == asset_type]
    
    return all_instruments

@app.get("/multi-asset/instruments/{symbol}")
async def get_instrument_details(symbol: str):
    """Get detailed information about a specific instrument"""
    if symbol not in instruments:
        raise HTTPException(status_code=404, detail="Instrument not found")
    
    instrument = instruments[symbol]
    market_data = await trading_engine.market_data.get_market_data(symbol)
    
    return {
        "instrument": instrument.dict(),
        "market_data": market_data.dict() if market_data else None,
        "trading_hours": {
            "session": instrument.trading_session.value,
            "opens": "00:00" if instrument.trading_session == TradingSession.TWENTY_FOUR_SEVEN else "08:00",
            "closes": "23:59" if instrument.trading_session == TradingSession.TWENTY_FOUR_SEVEN else "16:00",
            "timezone": "UTC"
        }
    }

@app.get("/multi-asset/market-data/{symbol}")
async def get_market_data(symbol: str):
    """Get current market data for a symbol"""
    market_data = await trading_engine.market_data.get_market_data(symbol)
    if not market_data:
        raise HTTPException(status_code=404, detail="Market data not available")
    
    return market_data.dict()

@app.post("/multi-asset/orders", response_model=MultiAssetOrder)
async def create_order(
    symbol: str,
    order_type: OrderType,
    position_side: PositionSide,
    lot_size: float,
    leverage: int = 1,
    entry_price: Optional[float] = None,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
    trailing_distance: Optional[float] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a trading order"""
    try:
        user_id = "user_" + credentials.credentials[:8]
        
        if symbol not in instruments:
            raise HTTPException(status_code=404, detail="Instrument not found")
        
        instrument = instruments[symbol]
        
        # Validate order parameters
        if lot_size < instrument.minimum_lot_size:
            raise HTTPException(status_code=400, detail="Lot size below minimum")
        
        if leverage > instrument.leverage_max:
            raise HTTPException(status_code=400, detail="Leverage exceeds maximum")
        
        order = MultiAssetOrder(
            id=f"order_{datetime.now().timestamp()}_{len(active_orders)}",
            user_id=user_id,
            instrument=instrument,
            order_type=order_type,
            position_side=position_side,
            lot_size=lot_size,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            trailing_distance=trailing_distance,
            leverage=leverage,
            status="pending",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Execute market orders immediately
        if order_type == OrderType.MARKET:
            position = await trading_engine.execute_order(order)
            order.status = "executed"
        
        active_orders[order.id] = order
        
        logger.info(f"Created order {order.id} for user {user_id}")
        return order
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/multi-asset/positions", response_model=List[Position])
async def get_open_positions(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get all open positions for the authenticated user"""
    try:
        user_id = "user_" + credentials.credentials[:8]
        user_positions = [pos for pos in open_positions.values() if pos.user_id == user_id]
        
        # Update P&L for all positions
        for position in user_positions:
            pnl_data = await trading_engine.calculate_pnl(position)
            position.unrealized_pnl = pnl_data["unrealized_pnl"]
            position.current_price = (await trading_engine.market_data.get_market_data(position.instrument.symbol)).current_price
            position.last_update = datetime.now()
        
        return user_positions
    except Exception as e:
        logger.error(f"Error getting positions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/multi-asset/positions/{position_id}/close")
async def close_position(
    position_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Close an open position"""
    try:
        user_id = "user_" + credentials.credentials[:8]
        result = await trading_engine.close_position(position_id, user_id)
        logger.info(f"User {user_id} closed position {position_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error closing position: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/multi-asset/analysis")
async def analyze_market(
    request: MarketAnalysisRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Perform comprehensive market analysis"""
    try:
        analysis = await market_analyzer.analyze_market(request)
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing market: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/multi-asset/summary")
async def get_trading_summary(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get trading summary for the user"""
    try:
        user_id = "user_" + credentials.credentials[:8]
        user_positions = [pos for pos in open_positions.values() if pos.user_id == user_id]
        
        total_pnl = sum(pos.unrealized_pnl for pos in user_positions)
        total_margin = sum(pos.margin_used for pos in user_positions)
        total_invested = sum(pos.entry_price * pos.lot_size for pos in user_positions)
        
        # Group by asset type
        asset_distribution = {}
        for position in user_positions:
            asset_type = position.instrument.asset_type.value
            if asset_type not in asset_distribution:
                asset_distribution[asset_type] = {"count": 0, "pnl": 0, "investment": 0}
            asset_distribution[asset_type]["count"] += 1
            asset_distribution[asset_type]["pnl"] += position.unrealized_pnl
            asset_distribution[asset_type]["investment"] += position.entry_price * position.lot_size
        
        return {
            "total_positions": len(user_positions),
            "total_pnl": total_pnl,
            "total_margin_used": total_margin,
            "total_invested": total_invested,
            "return_percentage": (total_pnl / total_invested * 100) if total_invested > 0 else 0,
            "asset_distribution": asset_distribution,
            "top_performers": sorted([(p.id, p.unrealized_pnl) for p in user_positions], key=lambda x: x[1], reverse=True)[:5],
            "worst_performers": sorted([(p.id, p.unrealized_pnl) for p in user_positions], key=lambda x: x[1])[:5]
        }
    except Exception as e:
        logger.error(f"Error getting trading summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "TigerEx Multi-Asset Trading Service", "instruments": len(instruments)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)