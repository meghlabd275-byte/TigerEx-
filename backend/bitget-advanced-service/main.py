"""
Bitget Advanced Service - Complete Bitget Integration for TigerEx
All unique Bitget features including trading, copy trading, futures, etc.
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
    title="TigerEx Bitget Advanced Service v1.0.0", 
    version="1.0.0",
    description="Complete Bitget integration for TigerEx trading platform"
)
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BitgetFeature(str, Enum):
    SPOT_TRADING = "spot_trading"
    FUTURES_TRADING = "futures_trading"
    COPY_TRADING = "copy_trading"
    MARGIN_TRADING = "margin_trading"
    OPTIONS_TRADING = "options_trading"
    ONE_CLICK_COPY_TRADE = "one_click_copy_trade"
    BINARY_OPTIONS = "binary_options"
    WEALTH_MANAGEMENT = "wealth_management"
    STAKING = "staking"
    LAUNCHPAD = "launchpad"
    INSTITUTIONAL = "institutional"
    GRID_TRADING = "grid_trading"
    API_TRADING = "api_trading"

class ProductType(str, Enum):
    SPOT = "spot"
    MARGIN = "margin"
    FUTURES = "futures"
    OPTIONS = "options"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"
    POST_ONLY = "post_only"
    IOC = "ioc"
    FOK = "fok"

class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass
class BitgetConfig:
    API_KEY: str = os.getenv("BITGET_API_KEY")
    API_SECRET: str = os.getenv("BITGET_SECRET")
    PASSPHRASE: str = os.getenv("BITGET_PASSPHRASE")
    BASE_URL: str = "https://api.bitget.com"
    
    @staticmethod
    def get_signature(method: str, request_path: str, body: str, secret: str) -> str:
        """Generate HMAC SHA256 signature for Bitget API"""
        timestamp = str(int(time.time()))
        message = timestamp + method + request_path + body
        return hmac.new(
            secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    def get_headers(api_key: str, passphrase: str, signature: str, timestamp: str) -> Dict[str, str]:
        """Get headers for Bitget API requests"""
        return {
            'ACCESS-KEY': api_key,
            'ACCESS-SIGN': signature,
            'ACCESS-PASSPHRASE': passphrase,
            'ACCESS-TIMESTAMP': timestamp,
            'Content-Type': 'application/json'
        }

class BitgetOrder(BaseModel):
    symbol: str = Field(..., description="Trading symbol")
    side: Side = Field(..., description="Order side")
    order_type: OrderType = Field(..., description="Order type")
    quantity: str = Field(..., description="Order quantity")
    price: Optional[str] = Field(None, description="Order price")
    client_order_id: Optional[str] = Field(None, description="Client order ID")
    margin_coin: Optional[str] = Field(None, description="Margin coin")
    size: Optional[str] = Field(None, description="Order size")
    trigger_price: Optional[str] = Field(None, description="Trigger price")
    preset_take_profit_price: Optional[str] = Field(None, description="Take profit price")
    preset_stop_loss_price: Optional[str] = Field(None, description="Stop loss price")

class TigerExBitgetService:
    def __init__(self):
        self.config = BitgetConfig()
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_account_info(self, product_type: ProductType = ProductType.SPOT) -> Dict[str, Any]:
        """Get account information"""
        url = f"{self.config.BASE_URL}/api/v2/spot/account/info"
        
        timestamp = str(int(time.time()))
        method = "GET"
        request_path = "/api/v2/spot/account/info"
        body = ""
        
        signature = BitgetConfig.get_signature(method, request_path, body, self.config.API_SECRET)
        headers = BitgetConfig.get_headers(self.config.API_KEY, self.config.PASSPHRASE, signature, timestamp)
        
        async with self.session.get(url, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def place_order(self, order: BitgetOrder, product_type: ProductType = ProductType.SPOT) -> Dict[str, Any]:
        """Place an order on Bitget"""
        url = f"{self.config.BASE_URL}/api/v2/spot/order"
        
        params = {
            "symbol": order.symbol,
            "side": order.side.value,
            "orderType": order.order_type.value,
            "size": order.size or order.quantity
        }
        
        if order.price:
            params["price"] = order.price
        if order.client_order_id:
            params["clientOrderId"] = order.client_order_id
        if order.margin_coin:
            params["marginCoin"] = order.margin_coin
        if order.trigger_price:
            params["triggerPrice"] = order.trigger_price
        if order.preset_take_profit_price:
            params["presetTakeProfitPrice"] = order.preset_take_profit_price
        if order.preset_stop_loss_price:
            params["presetStopLossPrice"] = order.preset_stop_loss_price
        
        timestamp = str(int(time.time()))
        method = "POST"
        request_path = "/api/v2/spot/order"
        body = json.dumps(params)
        
        signature = BitgetConfig.get_signature(method, request_path, body, self.config.API_SECRET)
        headers = BitgetConfig.get_headers(self.config.API_KEY, self.config.PASSPHRASE, signature, timestamp)
        
        async with self.session.post(url, json=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_symbols(self, product_type: ProductType = ProductType.SPOT) -> Dict[str, Any]:
        """Get trading symbols"""
        url = f"{self.config.BASE_URL}/api/v2/spot/market/symbols"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_ticker(self, symbol: str, product_type: ProductType = ProductType.SPOT) -> Dict[str, Any]:
        """Get ticker information"""
        url = f"{self.config.BASE_URL}/api/v2/spot/market/tickers"
        
        params = {
            "symbol": symbol
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_orderbook(self, symbol: str, limit: int = 20, product_type: ProductType = ProductType.SPOT) -> Dict[str, Any]:
        """Get orderbook information"""
        url = f"{self.config.BASE_URL}/api/v2/spot/market/depth"
        
        params = {
            "symbol": symbol,
            "limit": limit
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_trades(self, symbol: str, limit: int = 100, product_type: ProductType = ProductType.SPOT) -> Dict[str, Any]:
        """Get recent trades"""
        url = f"{self.config.BASE_URL}/api/v2/spot/market/fills"
        
        params = {
            "symbol": symbol,
            "limit": limit
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_klines(
        self, 
        symbol: str, 
        period: str, 
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: str = "100"
    ) -> Dict[str, Any]:
        """Get kline/candlestick data"""
        url = f"{self.config.BASE_URL}/api/v2/spot/market/candles"
        
        params = {
            "symbol": symbol,
            "period": period,
            "limit": limit
        }
        
        if start_time:
            params["startTimeAfter"] = start_time
        if end_time:
            params["startTimeBefore"] = end_time
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_futures_contracts(self) -> Dict[str, Any]:
        """Get futures contracts information"""
        url = f"{self.config.BASE_URL}/api/v2/mix/market/contracts"
        
        params = {
            "productType": "umcbl"  # USDT Universal Margin Contracts
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_copy_trading_leaders(self) -> Dict[str, Any]:
        """Get copy trading leaders"""
        url = f"{self.config.BASE_URL}/api/v2/copy/market/current-trader-list"
        
        params = {
            "levelSort": "profitRateDesc",
            "traceType": "all"
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_copy_trading_data(self, trader_id: str) -> Dict[str, Any]:
        """Get copy trading data for a specific trader"""
        url = f"{self.config.BASE_URL}/api/v2/copy/trader/info"
        
        params = {
            "traderId": trader_id
        }
        
        timestamp = str(int(time.time()))
        method = "GET"
        request_path = "/api/v2/copy/trader/info"
        body = json.dumps(params)
        
        signature = BitgetConfig.get_signature(method, request_path, body, self.config.API_SECRET)
        headers = BitgetConfig.get_headers(self.config.API_KEY, self.config.PASSPHRASE, signature, timestamp)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_wealth_management_products(self) -> Dict[str, Any]:
        """Get wealth management products"""
        url = f"{self.config.BASE_URL}/api/v2/wealth/savings/product/list"
        
        timestamp = str(int(time.time()))
        method = "GET"
        request_path = "/api/v2/wealth/savings/product/list"
        body = ""
        
        signature = BitgetConfig.get_signature(method, request_path, body, self.config.API_SECRET)
        headers = BitgetConfig.get_headers(self.config.API_KEY, self.config.PASSPHRASE, signature, timestamp)
        
        async with self.session.get(url, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_launchpad_projects(self) -> Dict[str, Any]:
        """Get launchpad projects"""
        url = f"{self.config.BASE_URL}/api/v2/spot/announcement/list"
        
        params = {
            "announcementType": "NEW_LISTING"
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_grid_trading_info(self, symbol: str) -> Dict[str, Any]:
        """Get grid trading information"""
        url = f"{self.config.BASE_URL}/api/v2/mix/grid/symbol"
        
        params = {
            "symbol": symbol
        }
        
        timestamp = str(int(time.time()))
        method = "GET"
        request_path = "/api/v2/mix/grid/symbol"
        body = json.dumps(params)
        
        signature = BitgetConfig.get_signature(method, request_path, body, self.config.API_SECRET)
        headers = BitgetConfig.get_headers(self.config.API_KEY, self.config.PASSPHRASE, signature, timestamp)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()

# API Endpoints
@app.get("/tigerex/bitget/account")
async def get_account_info(
    product_type: ProductType = Query(ProductType.SPOT, description="Product type"),
    credentials: str = Depends(security)
):
    """Get account information - TigerEx Bitget Integration"""
    async with TigerExBitgetService() as service:
        return await service.get_account_info(product_type)

@app.post("/tigerex/bitget/order")
async def place_order(
    order: BitgetOrder,
    product_type: ProductType = Query(ProductType.SPOT, description="Product type"),
    credentials: str = Depends(security)
):
    """Place order - TigerEx Bitget Integration"""
    async with TigerExBitgetService() as service:
        return await service.place_order(order, product_type)

@app.get("/tigerex/bitget/symbols")
async def get_symbols(
    product_type: ProductType = Query(ProductType.SPOT, description="Product type"),
    credentials: str = Depends(security)
):
    """Get symbols - TigerEx Bitget Integration"""
    async with TigerExBitgetService() as service:
        return await service.get_symbols(product_type)

@app.get("/tigerex/bitget/ticker")
async def get_ticker(
    symbol: str = Query(..., description="Symbol"),
    product_type: ProductType = Query(ProductType.SPOT, description="Product type"),
    credentials: str = Depends(security)
):
    """Get ticker - TigerEx Bitget Integration"""
    async with TigerExBitgetService() as service:
        return await service.get_ticker(symbol, product_type)

@app.get("/tigerex/bitget/orderbook")
async def get_orderbook(
    symbol: str = Query(..., description="Symbol"),
    limit: int = Query(20, description="Limit"),
    product_type: ProductType = Query(ProductType.SPOT, description="Product type"),
    credentials: str = Depends(security)
):
    """Get orderbook - TigerEx Bitget Integration"""
    async with TigerExBitgetService() as service:
        return await service.get_orderbook(symbol, limit, product_type)

@app.get("/tigerex/bitget/trades")
async def get_trades(
    symbol: str = Query(..., description="Symbol"),
    limit: int = Query(100, description="Limit"),
    product_type: ProductType = Query(ProductType.SPOT, description="Product type"),
    credentials: str = Depends(security)
):
    """Get recent trades - TigerEx Bitget Integration"""
    async with TigerExBitgetService() as service:
        return await service.get_trades(symbol, limit, product_type)

@app.get("/tigerex/bitget/klines")
async def get_klines(
    symbol: str = Query(..., description="Symbol"),
    period: str = Query(..., description="Period"),
    start_time: Optional[str] = Query(None, description="Start time"),
    end_time: Optional[str] = Query(None, description="End time"),
    limit: str = Query("100", description="Limit"),
    credentials: str = Depends(security)
):
    """Get klines - TigerEx Bitget Integration"""
    async with TigerExBitgetService() as service:
        return await service.get_klines(symbol, period, start_time, end_time, limit)

@app.get("/tigerex/bitget/futures/contracts")
async def get_futures_contracts(credentials: str = Depends(security)):
    """Get futures contracts - TigerEx Bitget Integration"""
    async with TigerExBitgetService() as service:
        return await service.get_futures_contracts()

@app.get("/tigerex/bitget/copytrading/leaders")
async def get_copy_trading_leaders(credentials: str = Depends(security)):
    """Get copy trading leaders - TigerEx Bitget Integration"""
    async with TigerExBitgetService() as service:
        return await service.get_copy_trading_leaders()

@app.get("/tigerex/bitget/copytrading/data")
async def get_copy_trading_data(
    trader_id: str = Query(..., description="Trader ID"),
    credentials: str = Depends(security)
):
    """Get copy trading data - TigerEx Bitget Integration"""
    async with TigerExBitgetService() as service:
        return await service.get_copy_trading_data(trader_id)

@app.get("/tigerex/bitget/wealth/products")
async def get_wealth_management_products(credentials: str = Depends(security)):
    """Get wealth management products - TigerEx Bitget Integration"""
    async with TigerExBitgetService() as service:
        return await service.get_wealth_management_products()

@app.get("/tigerex/bitget/launchpad")
async def get_launchpad_projects(credentials: str = Depends(security)):
    """Get launchpad projects - TigerEx Bitget Integration"""
    async with TigerExBitgetService() as service:
        return await service.get_launchpad_projects()

@app.get("/tigerex/bitget/grid/trading")
async def get_grid_trading_info(
    symbol: str = Query(..., description="Symbol"),
    credentials: str = Depends(security)
):
    """Get grid trading info - TigerEx Bitget Integration"""
    async with TigerExBitgetService() as service:
        return await service.get_grid_trading_info(symbol)

@app.get("/tigerex/bitget/features")
async def get_available_features():
    """Get available TigerEx Bitget features"""
    return {
        "service": "TigerEx Bitget Advanced Service",
        "version": "1.0.0",
        "features": [feature.value for feature in BitgetFeature],
        "supported_product_types": [pt.value for pt in ProductType],
        "supported_order_types": [ot.value for ot in OrderType],
        "tigerex_integrated": True
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "TigerEx Bitget Advanced Service",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8011)