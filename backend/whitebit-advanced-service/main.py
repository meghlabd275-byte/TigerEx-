"""
WhiteBit Advanced Service - Complete WhiteBit Integration for TigerEx
All unique WhiteBit features including trading, futures, copy trading, etc.
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
    title="TigerEx WhiteBit Advanced Service v1.0.0", 
    version="1.0.0",
    description="Complete WhiteBit integration for TigerEx trading platform"
)
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhiteBitFeature(str, Enum):
    SPOT_TRADING = "spot_trading"
    FUTURES_TRADING = "futures_trading"
    MARGIN_TRADING = "margin_trading"
    COPY_TRADING = "copy_trading"
    STAKING = "staking"
    IEO = "ieo"
    LOYALTY_PROGRAM = "loyalty_program"
    API_TRADING = "api_trading"
    INSTITUTIONAL = "institutional"
    WHITEBIT_LOCK = "whitebit_lock"
    WHITEBIT_EARN = "whitebit_earn"
    AFFILIATE_PROGRAM = "affiliate_program"

class MarketType(str, Enum):
    SPOT = "SPOT"
    FUTURES = "FUTURES"
    MARGIN = "MARGIN"

class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LIMIT = "STOP_LIMIT"
    STOP_MARKET = "STOP_MARKET"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass
class WhiteBitConfig:
    API_KEY: str = os.getenv("WHITEBIT_API_KEY")
    API_SECRET: str = os.getenv("WHITEBIT_SECRET")
    BASE_URL: str = "https://whitebit.com"
    
    @staticmethod
    def get_signature(request: str, secret: str) -> str:
        """Generate HMAC SHA512 signature for WhiteBit API"""
        return hmac.new(
            secret.encode('utf-8'),
            request.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
    
    @staticmethod
    def get_headers(api_key: str, signature: str) -> Dict[str, str]:
        """Get headers for WhiteBit API requests"""
        return {
            'X-TXC-APIKEY': api_key,
            'X-TXC-PAYLOAD': signature,
            'Content-Type': 'application/json'
        }

class WhiteBitOrder(BaseModel):
    market: str = Field(..., description="Trading market")
    side: OrderSide = Field(..., description="Order side")
    order_type: OrderType = Field(..., description="Order type")
    amount: str = Field(..., description="Order amount")
    price: Optional[str] = Field(None, description="Order price")
    client_order_id: Optional[str] = Field(None, description="Client order ID")

class TigerExWhiteBitService:
    def __init__(self):
        self.config = WhiteBitConfig()
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_account_balance(self) -> Dict[str, Any]:
        """Get account balance"""
        url = f"{self.config.BASE_URL}/api/v4/main/account/balance"
        
        request_data = {
            'request': '/api/v4/main/account/balance',
            'nonce': str(int(time.time()))
        }
        
        request_str = json.dumps(request_data)
        signature = WhiteBitConfig.get_signature(request_str, self.config.API_SECRET)
        
        headers = WhiteBitConfig.get_headers(self.config.API_KEY, signature)
        headers['X-TXC-PAYLOAD'] = request_str
        
        async with self.session.post(url, headers=headers, data=request_str) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def place_order(self, order: WhiteBitOrder) -> Dict[str, Any]:
        """Place an order on WhiteBit"""
        url = f"{self.config.BASE_URL}/api/v4/main/order/new"
        
        request_data = {
            'request': '/api/v4/main/order/new',
            'nonce': str(int(time.time())),
            'market': order.market,
            'side': order.side.value,
            'type': order.order_type.value,
            'amount': order.amount
        }
        
        if order.price:
            request_data['price'] = order.price
        if order.client_order_id:
            request_data['client_order_id'] = order.client_order_id
        
        request_str = json.dumps(request_data)
        signature = WhiteBitConfig.get_signature(request_str, self.config.API_SECRET)
        
        headers = WhiteBitConfig.get_headers(self.config.API_KEY, signature)
        headers['X-TXC-PAYLOAD'] = request_str
        
        async with self.session.post(url, headers=headers, data=request_str) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_markets(self) -> Dict[str, Any]:
        """Get all available markets"""
        url = f"{self.config.BASE_URL}/api/v4/main/market"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_ticker(self, market: Optional[str] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Get ticker information"""
        url = f"{self.config.BASE_URL}/api/v4/main/ticker"
        
        params = {}
        if market:
            params['market'] = market
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_orderbook(self, market: str, limit: int = 100, order_type: str = "both") -> Dict[str, Any]:
        """Get order book depth for a market"""
        url = f"{self.config.BASE_URL}/api/v4/main/orderbook"
        
        params = {
            'market': market,
            'limit': limit,
            'type': order_type
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_recent_trades(self, market: str, limit: int = 100, order_type: str = "both") -> List[Dict[str, Any]]:
        """Get recent trades list for a market"""
        url = f"{self.config.BASE_URL}/api/v4/main/trades"
        
        params = {
            'market': market,
            'limit': limit,
            'type': order_type
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_klines(
        self, 
        market: str, 
        interval: str, 
        limit: int = 100
    ) -> List[List[Any]]:
        """Get historical kline/candlestick data"""
        url = f"{self.config.BASE_URL}/api/v4/main/kline"
        
        params = {
            'market': market,
            'interval': interval,
            'limit': limit
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_futures_contracts(self) -> Dict[str, Any]:
        """Get futures contracts information"""
        url = f"{self.config.BASE_URL}/api/v4/futures/market"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_staking_products(self) -> Dict[str, Any]:
        """Get WhiteBit staking products"""
        url = f"{self.config.BASE_URL}/api/v4/main/staking/products"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_ieo_projects(self) -> Dict[str, Any]:
        """Get WhiteBit IEO projects"""
        url = f"{self.config.BASE_URL}/api/v4/main/ieo/projects"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_copy_trading_leaders(self) -> Dict[str, Any]:
        """Get copy trading leaders"""
        url = f"{self.config.BASE_URL}/api/v4/main/copytrading/leaders"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_whitebit_lock_products(self) -> Dict[str, Any]:
        """Get WhiteBit Lock products"""
        url = f"{self.config.BASE_URL}/api/v4/main/lock/products"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_whitebit_earn_products(self) -> Dict[str, Any]:
        """Get WhiteBit Earn products"""
        url = f"{self.config.BASE_URL}/api/v4/main/earn/products"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()

# API Endpoints
@app.get("/tigerex/whitebit/balance")
async def get_account_balance(credentials: str = Depends(security)):
    """Get account balance - TigerEx WhiteBit Integration"""
    async with TigerExWhiteBitService() as service:
        return await service.get_account_balance()

@app.post("/tigerex/whitebit/order")
async def place_order(order: WhiteBitOrder, credentials: str = Depends(security)):
    """Place order - TigerEx WhiteBit Integration"""
    async with TigerExWhiteBitService() as service:
        return await service.place_order(order)

@app.get("/tigerex/whitebit/markets")
async def get_markets(credentials: str = Depends(security)):
    """Get markets - TigerEx WhiteBit Integration"""
    async with TigerExWhiteBitService() as service:
        return await service.get_markets()

@app.get("/tigerex/whitebit/ticker")
async def get_ticker(
    market: Optional[str] = Query(None, description="Market"),
    credentials: str = Depends(security)
):
    """Get ticker - TigerEx WhiteBit Integration"""
    async with TigerExWhiteBitService() as service:
        return await service.get_ticker(market)

@app.get("/tigerex/whitebit/orderbook")
async def get_orderbook(
    market: str = Query(..., description="Market"),
    limit: int = Query(100, description="Limit"),
    order_type: str = Query("both", description="Order type"),
    credentials: str = Depends(security)
):
    """Get orderbook - TigerEx WhiteBit Integration"""
    async with TigerExWhiteBitService() as service:
        return await service.get_orderbook(market, limit, order_type)

@app.get("/tigerex/whitebit/trades")
async def get_recent_trades(
    market: str = Query(..., description="Market"),
    limit: int = Query(100, description="Limit"),
    order_type: str = Query("both", description="Order type"),
    credentials: str = Depends(security)
):
    """Get recent trades - TigerEx WhiteBit Integration"""
    async with TigerExWhiteBitService() as service:
        return await service.get_recent_trades(market, limit, order_type)

@app.get("/tigerex/whitebit/klines")
async def get_klines(
    market: str = Query(..., description="Market"),
    interval: str = Query(..., description="Interval"),
    limit: int = Query(100, description="Limit"),
    credentials: str = Depends(security)
):
    """Get klines - TigerEx WhiteBit Integration"""
    async with TigerExWhiteBitService() as service:
        return await service.get_klines(market, interval, limit)

@app.get("/tigerex/whitebit/futures/contracts")
async def get_futures_contracts(credentials: str = Depends(security)):
    """Get futures contracts - TigerEx WhiteBit Integration"""
    async with TigerExWhiteBitService() as service:
        return await service.get_futures_contracts()

@app.get("/tigerex/whitebit/staking")
async def get_staking_products(credentials: str = Depends(security)):
    """Get staking products - TigerEx WhiteBit Integration"""
    async with TigerExWhiteBitService() as service:
        return await service.get_staking_products()

@app.get("/tigerex/whitebit/ieo")
async def get_ieo_projects(credentials: str = Depends(security)):
    """Get IEO projects - TigerEx WhiteBit Integration"""
    async with TigerExWhiteBitService() as service:
        return await service.get_ieo_projects()

@app.get("/tigerex/whitebit/copytrading/leaders")
async def get_copy_trading_leaders(credentials: str = Depends(security)):
    """Get copy trading leaders - TigerEx WhiteBit Integration"""
    async with TigerExWhiteBitService() as service:
        return await service.get_copy_trading_leaders()

@app.get("/tigerex/whitebit/lock")
async def get_whitebit_lock_products(credentials: str = Depends(security)):
    """Get WhiteBit Lock products - TigerEx WhiteBit Integration"""
    async with TigerExWhiteBitService() as service:
        return await service.get_whitebit_lock_products()

@app.get("/tigerex/whitebit/earn")
async def get_whitebit_earn_products(credentials: str = Depends(security)):
    """Get WhiteBit Earn products - TigerEx WhiteBit Integration"""
    async with TigerExWhiteBitService() as service:
        return await service.get_whitebit_earn_products()

@app.get("/tigerex/whitebit/features")
async def get_available_features():
    """Get available TigerEx WhiteBit features"""
    return {
        "service": "TigerEx WhiteBit Advanced Service",
        "version": "1.0.0",
        "features": [feature.value for feature in WhiteBitFeature],
        "supported_market_types": [mt.value for mt in MarketType],
        "supported_order_types": [ot.value for ot in OrderType],
        "tigerex_integrated": True
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "TigerEx WhiteBit Advanced Service",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8013)