"""
Bitfinex Advanced Service - Complete Bitfinex Integration for TigerEx
All unique Bitfinex features including advanced trading, derivatives, funding, etc.
TigerEx Branded Implementation
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
import hashlib
import hmac
import base64
import json
import logging
import os
import time
import urllib.parse
from dataclasses import dataclass

app = FastAPI(
    title="TigerEx Bitfinex Advanced Service v1.0.0", 
    version="1.0.0",
    description="Complete Bitfinex integration for TigerEx trading platform"
)
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BitfinexFeature(str, Enum):
    SPOT_TRADING = "spot_trading"
    MARGIN_TRADING = "margin_trading"
    DERIVATIVES_TRADING = "derivatives_trading"
    FUNDING = "funding"
    STAKING = "staking"
    LENDING = "lending"
    OTC_DESK = "otc_desk"
    ADVANCED_ORDER_TYPES = "advanced_order_types"
    DERIVATIVES_FUTURES = "derivatives_futures"
    DERIVATICES_OPTIONS = "derivatives_options"
    PORTFOLIO_MANAGEMENT = "portfolio_management"
    MOBILE_TRADING = "mobile_trading"
    API_TRADING = "api_trading"

class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"
    TRAILING_STOP = "TRAILING_STOP"
    FILL_OR_KILL = "FOK"
    IMMEDIATE_OR_CANCEL = "IOC"
    HIDDEN = "HIDDEN"

class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass
class BitfinexConfig:
    API_KEY: str = os.getenv("BITFINEX_API_KEY")
    API_SECRET: str = os.getenv("BITFINEX_SECRET")
    BASE_URL: str = "https://api-pub.bitfinex.com/v2"
    AUTH_URL: str = "https://api.bitfinex.com/v2"
    
    @staticmethod
    def get_signature(path: str, body: str, nonce: str) -> str:
        """Generate Bitfinex API signature"""
        message = f"/api/v2{path}{nonce}{body}"
        signature = hmac.new(
            BitfinexConfig.API_SECRET.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha384
        ).hexdigest()
        return signature
    
    @staticmethod
    def get_auth_headers(path: str, body: str = "") -> Dict[str, str]:
        """Get authenticated headers for Bitfinex API"""
        nonce = str(int(time.time() * 1000))
        signature = BitfinexConfig.get_signature(path, body, nonce)
        
        return {
            'bfx-nonce': nonce,
            'bfx-apikey': BitfinexConfig.API_KEY,
            'bfx-signature': signature,
            'Content-Type': 'application/json'
        }

class BitfinexOrder(BaseModel):
    symbol: str = Field(..., description="Trading symbol")
    side: Side = Field(..., description="Order side")
    order_type: OrderType = Field(..., description="Order type")
    amount: str = Field(..., description="Order amount")
    price: Optional[str] = Field(None, description="Order price")
    use_lev: Optional[int] = Field(None, description="Leverage")
    stop_price: Optional[str] = Field(None, description="Stop price")
    trailing_stop: Optional[float] = Field(None, description="Trailing stop")
    hidden: Optional[bool] = Field(False, description="Hidden order")
    oco_order: Optional[Dict[str, Any]] = Field(None, description="OCO order")
    aff_code: Optional[str] = Field(None, description="Affiliate code")

class TigerExBitfinexService:
    def __init__(self):
        self.config = BitfinexConfig()
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        url = f"{self.config.AUTH_URL}/auth/r/wallets"
        
        headers = BitfinexConfig.get_auth_headers("/auth/r/wallets")
        
        async with self.session.post(url, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def place_order(self, order: BitfinexOrder) -> Dict[str, Any]:
        """Place an order on Bitfinex"""
        url = f"{self.config.AUTH_URL}/auth/w/order/submit"
        
        order_data = {
            "symbol": order.symbol,
            "side": order.side.value,
            "type": order.order_type.value,
            "amount": order.amount
        }
        
        if order.price:
            order_data["price"] = order.price
        if order.use_lev:
            order_data["lev"] = order.use_lev
        if order.stop_price:
            order_data["price_trailing"] = order.stop_price
        if order.trailing_stop:
            order_data["trailing_amount"] = order.trailing_stop
        if order.hidden:
            order_data["hidden"] = 1
        if order.oco_order:
            order_data.update(order.oco_order)
        
        body = json.dumps(order_data)
        headers = BitfinexConfig.get_auth_headers("/auth/w/order/submit", body)
        
        async with self.session.post(url, headers=headers, data=body) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_trading_pairs(self) -> List[Dict[str, Any]]:
        """Get all trading symbols"""
        url = f"{self.config.BASE_URL}/conf/pub:list:pair:exchange"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker information for a symbol"""
        url = f"{self.config.BASE_URL}/ticker/t{symbol}"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get order book depth for a symbol"""
        url = f"{self.config.BASE_URL}/book/t{symbol}/P{limit}"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_recent_trades(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent trades list for a symbol"""
        url = f"{self.config.BASE_URL}/trades/t{symbol}/hist"
        
        params = {"limit": limit}
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_klines(
        self, 
        symbol: str, 
        timeframe: str = "1m", 
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 100
    ) -> List[List[str]]:
        """Get historical candlestick data"""
        url = f"{self.config.BASE_URL}/candles/trade:{timeframe}:t{symbol}/hist"
        
        params = {
            "limit": limit
        }
        
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_derivatives_contracts(self) -> List[Dict[str, Any]]:
        """Get derivatives contracts information"""
        url = f"{self.config.BASE_URL}/conf/pub:list:contract:derivatives"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_funding_products(self) -> Dict[str, Any]:
        """Get Bitfinex funding products"""
        url = f"{self.config.AUTH_URL}/auth/r/info/funding"
        
        headers = BitfinexConfig.get_auth_headers("/auth/r/info/funding")
        
        async with self.session.post(url, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_staking_products(self) -> Dict[str, Any]:
        """Get Bitfinex staking products"""
        url = f"{self.config.AUTH_URL}/auth/r/staking/products"
        
        headers = BitfinexConfig.get_auth_headers("/auth/r/staking/products")
        
        async with self.session.post(url, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_lending_products(self) -> Dict[str, Any]:
        """Get Bitfinex lending products"""
        url = f"{self.config.AUTH_URL}/auth/r/funding/offer/hist"
        
        headers = BitfinexConfig.get_auth_headers("/auth/r/funding/offer/hist")
        
        async with self.session.post(url, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_portfolio_info(self) -> Dict[str, Any]:
        """Get portfolio information"""
        url = f"{self.config.AUTH_URL}/auth/r/portfolio"
        
        headers = BitfinexConfig.get_auth_headers("/auth/r/portfolio")
        
        async with self.session.post(url, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_derivatives_futures_positions(self) -> Dict[str, Any]:
        """Get derivatives futures positions"""
        url = f"{self.config.AUTH_URL}/auth/r/positions"
        
        headers = BitfinexConfig.get_auth_headers("/auth/r/positions")
        
        async with self.session.post(url, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_derivatives_options_info(self) -> Dict[str, Any]:
        """Get derivatives options information"""
        url = f"{self.config.BASE_URL}/conf/pub:list:contract:options"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()

# API Endpoints
@app.get("/tigerex/bitfinex/account")
async def get_account_info(credentials: str = Depends(security)):
    """Get account information - TigerEx Bitfinex Integration"""
    async with TigerExBitfinexService() as service:
        return await service.get_account_info()

@app.post("/tigerex/bitfinex/order")
async def place_order(order: BitfinexOrder, credentials: str = Depends(security)):
    """Place order - TigerEx Bitfinex Integration"""
    async with TigerExBitfinexService() as service:
        return await service.place_order(order)

@app.get("/tigerex/bitfinex/symbols")
async def get_trading_pairs(credentials: str = Depends(security)):
    """Get trading pairs - TigerEx Bitfinex Integration"""
    async with TigerExBitfinexService() as service:
        return await service.get_trading_pairs()

@app.get("/tigerex/bitfinex/ticker")
async def get_ticker(
    symbol: str = Query(..., description="Symbol"),
    credentials: str = Depends(security)
):
    """Get ticker - TigerEx Bitfinex Integration"""
    async with TigerExBitfinexService() as service:
        return await service.get_ticker(symbol)

@app.get("/tigerex/bitfinex/orderbook")
async def get_orderbook(
    symbol: str = Query(..., description="Symbol"),
    limit: int = Query(100, description="Limit"),
    credentials: str = Depends(security)
):
    """Get orderbook - TigerEx Bitfinex Integration"""
    async with TigerExBitfinexService() as service:
        return await service.get_orderbook(symbol, limit)

@app.get("/tigerex/bitfinex/trades")
async def get_recent_trades(
    symbol: str = Query(..., description="Symbol"),
    limit: int = Query(100, description="Limit"),
    credentials: str = Depends(security)
):
    """Get recent trades - TigerEx Bitfinex Integration"""
    async with TigerExBitfinexService() as service:
        return await service.get_recent_trades(symbol, limit)

@app.get("/tigerex/bitfinex/klines")
async def get_klines(
    symbol: str = Query(..., description="Symbol"),
    timeframe: str = Query("1m", description="Timeframe"),
    start: Optional[str] = Query(None, description="Start"),
    end: Optional[str] = Query(None, description="End"),
    limit: int = Query(100, description="Limit"),
    credentials: str = Depends(security)
):
    """Get klines - TigerEx Bitfinex Integration"""
    async with TigerExBitfinexService() as service:
        return await service.get_klines(symbol, timeframe, start, end, limit)

@app.get("/tigerex/bitfinex/derivatives/contracts")
async def get_derivatives_contracts(credentials: str = Depends(security)):
    """Get derivatives contracts - TigerEx Bitfinex Integration"""
    async with TigerExBitfinexService() as service:
        return await service.get_derivatives_contracts()

@app.get("/tigerex/bitfinex/funding")
async def get_funding_products(credentials: str = Depends(security)):
    """Get funding products - TigerEx Bitfinex Integration"""
    async with TigerExBitfinexService() as service:
        return await service.get_funding_products()

@app.get("/tigerex/bitfinex/staking")
async def get_staking_products(credentials: str = Depends(security)):
    """Get staking products - TigerEx Bitfinex Integration"""
    async with TigerExBitfinexService() as service:
        return await service.get_staking_products()

@app.get("/tigerex/bitfinex/lending")
async def get_lending_products(credentials: str = Depends(security)):
    """Get lending products - TigerEx Bitfinex Integration"""
    async with TigerExBitfinexService() as service:
        return await service.get_lending_products()

@app.get("/tigerex/bitfinex/portfolio")
async def get_portfolio_info(credentials: str = Depends(security)):
    """Get portfolio info - TigerEx Bitfinex Integration"""
    async with TigerExBitfinexService() as service:
        return await service.get_portfolio_info()

@app.get("/tigerex/bitfinex/derivatives/positions")
async def get_derivatives_futures_positions(credentials: str = Depends(security)):
    """Get derivatives positions - TigerEx Bitfinex Integration"""
    async with TigerExBitfinexService() as service:
        return await service.get_derivatives_futures_positions()

@app.get("/tigerex/bitfinex/derivatives/options")
async def get_derivatives_options_info(credentials: str = Depends(security)):
    """Get derivatives options - TigerEx Bitfinex Integration"""
    async with TigerExBitfinexService() as service:
        return await service.get_derivatives_options_info()

@app.get("/tigerex/bitfinex/features")
async def get_available_features():
    """Get available TigerEx Bitfinex features"""
    return {
        "service": "TigerEx Bitfinex Advanced Service",
        "version": "1.0.0",
        "features": [feature.value for feature in BitfinexFeature],
        "supported_order_types": [ot.value for ot in OrderType],
        "tigerex_integrated": True
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "TigerEx Bitfinex Advanced Service",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8014)