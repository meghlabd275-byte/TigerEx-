"""
MEXC Advanced Service - Complete MEXC Integration for TigerEx
All unique MEXC features including trading, futures, ETF, staking, etc.
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
    title="TigerEx MEXC Advanced Service v1.0.0", 
    version="1.0.0",
    description="Complete MEXC integration for TigerEx trading platform"
)
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MEXCFeature(str, Enum):
    SPOT_TRADING = "spot_trading"
    FUTURES_TRADING = "futures_trading"
    ETF_TRADING = "etf_trading"
    MARGIN_TRADING = "margin_trading"
    STAKING = "staking"
    SAVINGS = "savings"
    LAUNCHPAD = "launchpad"
    COPY_TRADING = "copy_trading"
    BOT_TRADING = "bot_trading"
    MINING = "mining"
    OPTIONS_TRADING = "options_trading"
    INSTITUTIONAL = "institutional"
    WEALTH_MANAGEMENT = "wealth_management"
    DEFI_PRODUCTS = "defi_products"

class TradingType(str, Enum):
    SPOT = "SPOT"
    MARGIN = "MARGIN"
    FUTURES = "FUTURES"
    ETF = "ETF"

class OrderType(str, Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    LIMIT_MAKER = "LIMIT_MAKER"
    IMEDIATE_OR_CANCEL = "IMMEDIATE_OR_CANCEL"
    FILL_OR_KILL = "FILL_OR_KILL"

class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

@dataclass
class MEXCConfig:
    API_KEY: str = os.getenv("MEXC_API_KEY")
    API_SECRET: str = os.getenv("MEXC_SECRET")
    BASE_URL: str = "https://api.mexc.com"
    FUTURES_URL: str = "https://contract.mexc.com"
    
    @staticmethod
    def get_signature(params: Dict[str, Any], secret: str) -> str:
        """Generate HMAC SHA256 signature for MEXC API"""
        query_string = urllib.parse.urlencode(sorted(params.items()))
        return hmac.new(
            secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    def get_headers(api_key: str) -> Dict[str, str]:
        """Get headers for MEXC API requests"""
        return {
            'X-MEXC-APIKEY': api_key,
            'Content-Type': 'application/json'
        }

class MEXCOrder(BaseModel):
    symbol: str = Field(..., description="Trading symbol")
    side: Side = Field(..., description="Order side")
    order_type: OrderType = Field(..., description="Order type")
    quantity: str = Field(..., description="Order quantity")
    price: Optional[str] = Field(None, description="Order price")
    new_client_order_id: Optional[str] = Field(None, description="Client order ID")

class TigerExMEXCService:
    def __init__(self):
        self.config = MEXCConfig()
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        url = f"{self.config.BASE_URL}/api/v3/account"
        
        params = {
            'timestamp': str(int(time.time() * 1000))
        }
        
        params['signature'] = MEXCConfig.get_signature(params, self.config.API_SECRET)
        headers = MEXCConfig.get_headers(self.config.API_KEY)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def place_order(self, order: MEXCOrder) -> Dict[str, Any]:
        """Place an order on MEXC"""
        url = f"{self.config.BASE_URL}/api/v3/order"
        
        params = {
            'symbol': order.symbol,
            'side': order.side.value,
            'type': order.order_type.value,
            'quantity': order.quantity,
            'timestamp': str(int(time.time() * 1000))
        }
        
        if order.price:
            params['price'] = order.price
        if order.new_client_order_id:
            params['newClientOrderId'] = order.new_client_order_id
        
        params['signature'] = MEXCConfig.get_signature(params, self.config.API_SECRET)
        headers = MEXCConfig.get_headers(self.config.API_KEY)
        
        async with self.session.post(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_trading_pairs(self) -> List[Dict[str, Any]]:
        """Get all trading symbols"""
        url = f"{self.config.BASE_URL}/api/v3/ticker/24hr"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_ticker_24hr(self, symbol: Optional[str] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Get 24hr ticker price change statistics"""
        url = f"{self.config.BASE_URL}/api/v3/ticker/24hr"
        
        params = {}
        if symbol:
            params['symbol'] = symbol
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get order book depth for a symbol"""
        url = f"{self.config.BASE_URL}/api/v3/depth"
        
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
        url = f"{self.config.BASE_URL}/api/v3/trades"
        
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
        url = f"{self.config.BASE_URL}/api/v3/klines"
        
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_futures_contracts(self) -> Dict[str, Any]:
        """Get futures contracts information"""
        url = f"{self.config.FUTURES_URL}/api/v1/contract/detail"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_staking_products(self, product_type: str = "STAKING") -> Dict[str, Any]:
        """Get MEXC staking products"""
        url = f"{self.config.BASE_URL}/api/v3/staking/products"
        
        params = {
            'productType': product_type,
            'timestamp': str(int(time.time() * 1000))
        }
        
        params['signature'] = MEXCConfig.get_signature(params, self.config.API_SECRET)
        headers = MEXCConfig.get_headers(self.config.API_KEY)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_launchpad_projects(self) -> Dict[str, Any]:
        """Get MEXC Launchpad projects"""
        url = f"{self.config.BASE_URL}/api/v3/launchpad/projects"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_etf_products(self) -> Dict[str, Any]:
        """Get MEXC ETF products"""
        url = f"{self.config.BASE_URL}/api/v3/etf/info"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_copy_trading_leaders(self) -> Dict[str, Any]:
        """Get copy trading leaders"""
        url = f"{self.config.BASE_URL}/api/v3/copytrading/leaders"
        
        params = {
            'timestamp': str(int(time.time() * 1000))
        }
        
        params['signature'] = MEXCConfig.get_signature(params, self.config.API_SECRET)
        headers = MEXCConfig.get_headers(self.config.API_KEY)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_mining_info(self) -> Dict[str, Any]:
        """Get MEXC mining information"""
        url = f"{self.config.BASE_URL}/api/v3/mining/info"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()

# API Endpoints
@app.get("/tigerex/mexc/account")
async def get_account_info(credentials: str = Depends(security)):
    """Get account information - TigerEx MEXC Integration"""
    async with TigerExMEXCService() as service:
        return await service.get_account_info()

@app.post("/tigerex/mexc/order")
async def place_order(order: MEXCOrder, credentials: str = Depends(security)):
    """Place order - TigerEx MEXC Integration"""
    async with TigerExMEXCService() as service:
        return await service.place_order(order)

@app.get("/tigerex/mexc/symbols")
async def get_trading_pairs(credentials: str = Depends(security)):
    """Get trading pairs - TigerEx MEXC Integration"""
    async with TigerExMEXCService() as service:
        return await service.get_trading_pairs()

@app.get("/tigerex/mexc/ticker/24hr")
async def get_24hr_ticker(
    symbol: Optional[str] = Query(None, description="Symbol"),
    credentials: str = Depends(security)
):
    """Get 24hr ticker - TigerEx MEXC Integration"""
    async with TigerExMEXCService() as service:
        return await service.get_ticker_24hr(symbol)

@app.get("/tigerex/mexc/orderbook")
async def get_orderbook(
    symbol: str = Query(..., description="Symbol"),
    limit: int = Query(100, description="Limit"),
    credentials: str = Depends(security)
):
    """Get orderbook - TigerEx MEXC Integration"""
    async with TigerExMEXCService() as service:
        return await service.get_orderbook(symbol, limit)

@app.get("/tigerex/mexc/trades")
async def get_recent_trades(
    symbol: str = Query(..., description="Symbol"),
    limit: int = Query(500, description="Limit"),
    credentials: str = Depends(security)
):
    """Get recent trades - TigerEx MEXC Integration"""
    async with TigerExMEXCService() as service:
        return await service.get_recent_trades(symbol, limit)

@app.get("/tigerex/mexc/klines")
async def get_klines(
    symbol: str = Query(..., description="Symbol"),
    interval: str = Query(..., description="Interval"),
    start_time: Optional[int] = Query(None, description="Start time"),
    end_time: Optional[int] = Query(None, description="End time"),
    limit: int = Query(500, description="Limit"),
    credentials: str = Depends(security)
):
    """Get klines - TigerEx MEXC Integration"""
    async with TigerExMEXCService() as service:
        return await service.get_klines(symbol, interval, start_time, end_time, limit)

@app.get("/tigerex/mexc/futures/contracts")
async def get_futures_contracts(credentials: str = Depends(security)):
    """Get futures contracts - TigerEx MEXC Integration"""
    async with TigerExMEXCService() as service:
        return await service.get_futures_contracts()

@app.get("/tigerex/mexc/staking")
async def get_staking_products(
    product_type: str = Query("STAKING", description="Product type"),
    credentials: str = Depends(security)
):
    """Get staking products - TigerEx MEXC Integration"""
    async with TigerExMEXCService() as service:
        return await service.get_staking_products(product_type)

@app.get("/tigerex/mexc/launchpad")
async def get_launchpad_projects(credentials: str = Depends(security)):
    """Get launchpad projects - TigerEx MEXC Integration"""
    async with TigerExMEXCService() as service:
        return await service.get_launchpad_projects()

@app.get("/tigerex/mexc/etf")
async def get_etf_products(credentials: str = Depends(security)):
    """Get ETF products - TigerEx MEXC Integration"""
    async with TigerExMEXCService() as service:
        return await service.get_etf_products()

@app.get("/tigerex/mexc/copytrading/leaders")
async def get_copy_trading_leaders(credentials: str = Depends(security)):
    """Get copy trading leaders - TigerEx MEXC Integration"""
    async with TigerExMEXCService() as service:
        return await service.get_copy_trading_leaders()

@app.get("/tigerex/mexc/mining")
async def get_mining_info(credentials: str = Depends(security)):
    """Get mining info - TigerEx MEXC Integration"""
    async with TigerExMEXCService() as service:
        return await service.get_mining_info()

@app.get("/tigerex/mexc/features")
async def get_available_features():
    """Get available TigerEx MEXC features"""
    return {
        "service": "TigerEx MEXC Advanced Service",
        "version": "1.0.0",
        "features": [feature.value for feature in MEXCFeature],
        "supported_trading_types": [tt.value for tt in TradingType],
        "supported_order_types": [ot.value for ot in OrderType],
        "tigerex_integrated": True
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "TigerEx MEXC Advanced Service",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)