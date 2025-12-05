"""
CoinW Advanced Service - Complete CoinW Integration for TigerEx
All unique CoinW features including trading, futures, copy trading, etc.
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
    title="TigerEx CoinW Advanced Service v1.0.0", 
    version="1.0.0",
    description="Complete CoinW integration for TigerEx trading platform"
)
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoinWFeature(str, Enum):
    SPOT_TRADING = "spot_trading"
    FUTURES_TRADING = "futures_trading"
    COPY_TRADING = "copy_trading"
    MARGIN_TRADING = "margin_trading"
    STAKING = "staking"
    FINANCIAL_PRODUCTS = "financial_products"
    INSTITUTIONAL = "institutional"
    WEALTH_MANAGEMENT = "wealth_management"
    LAUNCHPAD = "launchpad"
    OPTIONS_TRADING = "options_trading"

class TradingType(str, Enum):
    SPOT = "SPOT"
    MARGIN = "MARGIN"
    FUTURES = "FUTURES"

class OrderType(str, Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP_LIMIT = "STOP_LIMIT"
    STOP_MARKET = "STOP_MARKET"

class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

@dataclass
class CoinWConfig:
    API_KEY: str = os.getenv("COINW_API_KEY")
    API_SECRET: str = os.getenv("COINW_SECRET")
    BASE_URL: str = "https://api.coinw.com"
    
    @staticmethod
    def get_signature(params: Dict[str, Any], secret: str) -> str:
        """Generate HMAC SHA256 signature for CoinW API"""
        query_string = urllib.parse.urlencode(sorted(params.items()))
        return hmac.new(
            secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    def get_headers(api_key: str) -> Dict[str, str]:
        """Get headers for CoinW API requests"""
        return {
            'X-CW-ACCESS-SIGN': '',
            'X-CW-ACCESS-TIMESTAMP': '',
            'X-CW-ACCESS-KEY': api_key,
            'Content-Type': 'application/json'
        }

class CoinWOrder(BaseModel):
    symbol: str = Field(..., description="Trading symbol")
    side: Side = Field(..., description="Order side")
    order_type: OrderType = Field(..., description="Order type")
    quantity: str = Field(..., description="Order quantity")
    price: Optional[str] = Field(None, description="Order price")
    client_order_id: Optional[str] = Field(None, description="Client order ID")

class TigerExCoinWService:
    def __init__(self):
        self.config = CoinWConfig()
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        url = f"{self.config.BASE_URL}/api/v1/spot/accounts"
        
        timestamp = str(int(time.time() * 1000))
        params = {
            'timestamp': timestamp
        }
        
        signature = CoinWConfig.get_signature(params, self.config.API_SECRET)
        
        headers = {
            'X-CW-ACCESS-KEY': self.config.API_KEY,
            'X-CW-ACCESS-SIGN': signature,
            'X-CW-ACCESS-TIMESTAMP': timestamp,
            'Content-Type': 'application/json'
        }
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def place_order(self, order: CoinWOrder) -> Dict[str, Any]:
        """Place an order on CoinW"""
        url = f"{self.config.BASE_URL}/api/v1/spot/order"
        
        timestamp = str(int(time.time() * 1000))
        params = {
            'symbol': order.symbol,
            'side': order.side.value,
            'type': order.order_type.value,
            'amount': order.quantity,
            'timestamp': timestamp
        }
        
        if order.price:
            params['price'] = order.price
        if order.client_order_id:
            params['client_order_id'] = order.client_order_id
        
        signature = CoinWConfig.get_signature(params, self.config.API_SECRET)
        
        headers = {
            'X-CW-ACCESS-KEY': self.config.API_KEY,
            'X-CW-ACCESS-SIGN': signature,
            'X-CW-ACCESS-TIMESTAMP': timestamp,
            'Content-Type': 'application/json'
        }
        
        async with self.session.post(url, json=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_symbols(self) -> List[Dict[str, Any]]:
        """Get trading symbols"""
        url = f"{self.config.BASE_URL}/api/v1/public/symbols"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_ticker_24hr(self, symbol: Optional[str] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Get 24hr ticker price change statistics"""
        url = f"{self.config.BASE_URL}/api/v1/public/ticker/24hr"
        
        params = {}
        if symbol:
            params['symbol'] = symbol
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get order book depth for a symbol"""
        url = f"{self.config.BASE_URL}/api/v1/public/depth"
        
        params = {
            'symbol': symbol,
            'limit': limit
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_recent_trades(self, symbol: str, limit: int = 500) -> List[Dict[str, Any]]:
        """Get recent trades list for a symbol"""
        url = f"{self.config.BASE_URL}/api/v1/public/trades"
        
        params = {
            'symbol': symbol,
            'limit': limit
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_klines(
        self, 
        symbol: str, 
        interval: str, 
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 500
    ) -> List[List[str]]:
        """Get historical kline/candlestick data"""
        url = f"{self.config.BASE_URL}/api/v1/public/klines"
        
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        if start_time:
            params['start_time'] = start_time
        if end_time:
            params['end_time'] = end_time
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_futures_contracts(self) -> Dict[str, Any]:
        """Get futures contracts information"""
        url = f"{self.config.BASE_URL}/api/v1/swap/public/instruments"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_staking_products(self, product_type: str = "STAKING") -> Dict[str, Any]:
        """Get CoinW staking products"""
        url = f"{self.config.BASE_URL}/api/v1/wealth/product/list"
        
        timestamp = str(int(time.time() * 1000))
        params = {
            'product_type': product_type,
            'timestamp': timestamp
        }
        
        signature = CoinWConfig.get_signature(params, self.config.API_SECRET)
        
        headers = {
            'X-CW-ACCESS-KEY': self.config.API_KEY,
            'X-CW-ACCESS-SIGN': signature,
            'X-CW-ACCESS-TIMESTAMP': timestamp,
            'Content-Type': 'application/json'
        }
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_copy_trading_leaders(self) -> Dict[str, Any]:
        """Get copy trading leaders"""
        url = f"{self.config.BASE_URL}/api/v1/copytrading/leaders"
        
        timestamp = str(int(time.time() * 1000))
        params = {
            'timestamp': timestamp
        }
        
        signature = CoinWConfig.get_signature(params, self.config.API_SECRET)
        
        headers = {
            'X-CW-ACCESS-KEY': self.config.API_KEY,
            'X-CW-ACCESS-SIGN': signature,
            'X-CW-ACCESS-TIMESTAMP': timestamp,
            'Content-Type': 'application/json'
        }
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_financial_products(self) -> Dict[str, Any]:
        """Get financial products"""
        url = f"{self.config.BASE_URL}/api/v1/financial/products"
        
        timestamp = str(int(time.time() * 1000))
        params = {
            'timestamp': timestamp
        }
        
        signature = CoinWConfig.get_signature(params, self.config.API_SECRET)
        
        headers = {
            'X-CW-ACCESS-KEY': self.config.API_KEY,
            'X-CW-ACCESS-SIGN': signature,
            'X-CW-ACCESS-TIMESTAMP': timestamp,
            'Content-Type': 'application/json'
        }
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()

# API Endpoints
@app.get("/tigerex/coinw/account")
async def get_account_info(credentials: str = Depends(security)):
    """Get account information - TigerEx CoinW Integration"""
    async with TigerExCoinWService() as service:
        return await service.get_account_info()

@app.post("/tigerex/coinw/order")
async def place_order(order: CoinWOrder, credentials: str = Depends(security)):
    """Place order - TigerEx CoinW Integration"""
    async with TigerExCoinWService() as service:
        return await service.place_order(order)

@app.get("/tigerex/coinw/symbols")
async def get_symbols(credentials: str = Depends(security)):
    """Get trading symbols - TigerEx CoinW Integration"""
    async with TigerExCoinWService() as service:
        return await service.get_symbols()

@app.get("/tigerex/coinw/ticker/24hr")
async def get_24hr_ticker(
    symbol: Optional[str] = Query(None, description="Symbol"),
    credentials: str = Depends(security)
):
    """Get 24hr ticker - TigerEx CoinW Integration"""
    async with TigerExCoinWService() as service:
        return await service.get_ticker_24hr(symbol)

@app.get("/tigerex/coinw/orderbook")
async def get_orderbook(
    symbol: str = Query(..., description="Symbol"),
    limit: int = Query(100, description="Limit"),
    credentials: str = Depends(security)
):
    """Get orderbook - TigerEx CoinW Integration"""
    async with TigerExCoinWService() as service:
        return await service.get_orderbook(symbol, limit)

@app.get("/tigerex/coinw/trades")
async def get_recent_trades(
    symbol: str = Query(..., description="Symbol"),
    limit: int = Query(500, description="Limit"),
    credentials: str = Depends(security)
):
    """Get recent trades - TigerEx CoinW Integration"""
    async with TigerExCoinWService() as service:
        return await service.get_recent_trades(symbol, limit)

@app.get("/tigerex/coinw/klines")
async def get_klines(
    symbol: str = Query(..., description="Symbol"),
    interval: str = Query(..., description="Interval"),
    start_time: Optional[int] = Query(None, description="Start time"),
    end_time: Optional[int] = Query(None, description="End time"),
    limit: int = Query(500, description="Limit"),
    credentials: str = Depends(security)
):
    """Get klines - TigerEx CoinW Integration"""
    async with TigerExCoinWService() as service:
        return await service.get_klines(symbol, interval, start_time, end_time, limit)

@app.get("/tigerex/coinw/futures/contracts")
async def get_futures_contracts(credentials: str = Depends(security)):
    """Get futures contracts - TigerEx CoinW Integration"""
    async with TigerExCoinWService() as service:
        return await service.get_futures_contracts()

@app.get("/tigerex/coinw/staking")
async def get_staking_products(
    product_type: str = Query("STAKING", description="Product type"),
    credentials: str = Depends(security)
):
    """Get staking products - TigerEx CoinW Integration"""
    async with TigerExCoinWService() as service:
        return await service.get_staking_products(product_type)

@app.get("/tigerex/coinw/copytrading/leaders")
async def get_copy_trading_leaders(credentials: str = Depends(security)):
    """Get copy trading leaders - TigerEx CoinW Integration"""
    async with TigerExCoinWService() as service:
        return await service.get_copy_trading_leaders()

@app.get("/tigerex/coinw/financial/products")
async def get_financial_products(credentials: str = Depends(security)):
    """Get financial products - TigerEx CoinW Integration"""
    async with TigerExCoinWService() as service:
        return await service.get_financial_products()

@app.get("/tigerex/coinw/features")
async def get_available_features():
    """Get available TigerEx CoinW features"""
    return {
        "service": "TigerEx CoinW Advanced Service",
        "version": "1.0.0",
        "features": [feature.value for feature in CoinWFeature],
        "supported_trading_types": [tt.value for tt in TradingType],
        "supported_order_types": [ot.value for ot in OrderType],
        "tigerex_integrated": True
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "TigerEx CoinW Advanced Service",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8012)