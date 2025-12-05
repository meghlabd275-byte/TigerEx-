"""
HTX Advanced Service - Complete HTX Integration for TigerEx
All unique HTX features including trading, staking, earn products, etc.
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
    title="TigerEx HTX Advanced Service v1.0.0", 
    version="1.0.0",
    description="Complete HTX integration for TigerEx trading platform"
)
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HTXFeature(str, Enum):
    SPOT_TRADING = "spot_trading"
    FUTURES_TRADING = "futures_trading"
    MARGIN_TRADING = "margin_trading"
    COPY_TRADING = "copy_trading"
    STAKING_SERVICES = "staking_services"
    EARN_PRODUCTS = "earn_products"
    HTX_EARN_PRIME = "htx_earn_prime"
    LIQUIDITY_MINING = "liquidity_mining"
    NFT_MARKETPLACE = "nft_marketplace"
    INSTITUTIONAL = "institutional"
    API_FEATURES = "api_features"
    ADVANCED_ORDER_TYPES = "advanced_order_types"

class AccountType(str, Enum):
    SPOT = "1"
    MARGIN = "2"
    FUTURES = "3"
    POINT = "4"
    SUPER_MARGIN = "5"
    CURRENCY = "6"

class OrderType(str, Enum):
    BUY_MARKET = "buy-market"
    SELL_MARKET = "sell-market"
    BUY_LIMIT = "buy-limit"
    SELL_LIMIT = "sell-limit"
    BUY_IOC = "buy-ioc"
    SELL_IOC = "sell-ioc"
    BUY_LIMIT_MAKER = "buy-limit-maker"
    SELL_LIMIT_MAKER = "sell-limit-maker"
    BUY_FOK = "buy-fok"
    SELL_FOK = "sell-fok"

class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass
class HTXConfig:
    ACCESS_KEY: str = os.getenv("HTX_ACCESS_KEY")
    SECRET_KEY: str = os.getenv("HTX_SECRET_KEY")
    BASE_URL: str = "https://api.huobi.pro"
    FUTURES_URL: str = "https://api.hbdm.com"
    COIN_M_URL: str = "https://api.hbdm.com"
    
    @staticmethod
    def get_signature(method: str, host: str, path: str, params: Dict[str, Any], secret_key: str) -> str:
        """Generate HMAC SHA256 signature for HTX API"""
        if method == "GET":
            query_string = urllib.parse.urlencode(sorted(params.items()))
            signature_str = method + "\n" + host + "\n" + path + "\n" + query_string
        else:
            signature_str = method + "\n" + host + "\n" + path + "\n"
        
        return hmac.new(
            secret_key.encode('utf-8'),
            signature_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    def get_headers(access_key: str, signature: str) -> Dict[str, str]:
        """Get headers for HTX API requests"""
        return {
            'Content-Type': 'application/json',
            'X-HB-API-KEY': access_key,
            'Authorization': f"HMAC-SHA256 Credential={access_key},Signature={signature}"
        }

class HTXOrder(BaseModel):
    symbol: str = Field(..., description="Trading symbol")
    account_type: AccountType = Field(..., description="Account type")
    order_type: OrderType = Field(..., description="Order type")
    amount: Optional[str] = Field(None, description="Order amount")
    price: Optional[str] = Field(None, description="Order price")
    source: Optional[str] = Field("api", description="Order source")
    client_order_id: Optional[str] = Field(None, description="Client order ID")

class TigerExHTXService:
    def __init__(self):
        self.config = HTXConfig()
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_accounts(self) -> Dict[str, Any]:
        """Get account information"""
        url = f"{self.config.BASE_URL}/v1/account/accounts"
        
        timestamp = str(int(time.time()))
        params = {}
        
        signature = HTXConfig.get_signature("GET", "api.huobi.pro", "/v1/account/accounts", params, self.config.SECRET_KEY)
        headers = HTXConfig.get_headers(self.config.ACCESS_KEY, signature)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_balance(self, account_id: str) -> Dict[str, Any]:
        """Get account balance"""
        url = f"{self.config.BASE_URL}/v1/account/accounts/{account_id}/balance"
        
        timestamp = str(int(time.time()))
        params = {}
        
        signature = HTXConfig.get_signature("GET", "api.huobi.pro", f"/v1/account/accounts/{account_id}/balance", params, self.config.SECRET_KEY)
        headers = HTXConfig.get_headers(self.config.ACCESS_KEY, signature)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def place_order(self, order: HTXOrder) -> Dict[str, Any]:
        """Place an order on HTX"""
        url = f"{self.config.BASE_URL}/v1/order/orders/place"
        
        timestamp = str(int(time.time()))
        params = {
            "symbol": order.symbol,
            "account-id": order.account_type.value,
            "type": order.order_type.value,
            "source": order.source
        }
        
        if order.amount:
            params["amount"] = order.amount
        if order.price:
            params["price"] = order.price
        if order.client_order_id:
            params["client-order-id"] = order.client_order_id
        
        signature = HTXConfig.get_signature("POST", "api.huobi.pro", "/v1/order/orders/place", params, self.config.SECRET_KEY)
        headers = HTXConfig.get_headers(self.config.ACCESS_KEY, signature)
        
        async with self.session.post(url, json=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_symbols(self) -> Dict[str, Any]:
        """Get trading symbols"""
        url = f"{self.config.BASE_URL}/v1/common/symbols"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_ticker(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get ticker information"""
        url = f"{self.config.BASE_URL}/market/detail/merged"
        
        params = {}
        if symbol:
            params["symbol"] = symbol
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_depth(self, symbol: str, depth_type: str = "step0") -> Dict[str, Any]:
        """Get orderbook depth"""
        url = f"{self.config.BASE_URL}/market/depth"
        
        params = {
            "symbol": symbol,
            "type": depth_type
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_trades(self, symbol: str, size: int = 100) -> Dict[str, Any]:
        """Get recent trades"""
        url = f"{self.config.BASE_URL}/market/history/trade"
        
        params = {
            "symbol": symbol,
            "size": size
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_klines(
        self, 
        symbol: str, 
        period: str = "1min", 
        size: int = 150,
        from_: Optional[int] = None,
        to: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get kline/candlestick data"""
        url = f"{self.config.BASE_URL}/market/history/kline"
        
        params = {
            "symbol": symbol,
            "period": period,
            "size": size
        }
        
        if from_:
            params["from"] = from_
        if to:
            params["to"] = to
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_open_orders(self, account_id: str, symbol: Optional[str] = None, side: Optional[Side] = None) -> Dict[str, Any]:
        """Get open orders"""
        url = f"{self.config.BASE_URL}/v1/order/orders"
        
        timestamp = str(int(time.time()))
        params = {
            "states": "submitted,partial-filled"
        }
        
        if symbol:
            params["symbol"] = symbol
        if side:
            params["side"] = side.value
        
        signature = HTXConfig.get_signature("GET", "api.huobi.pro", "/v1/order/orders", params, self.config.SECRET_KEY)
        headers = HTXConfig.get_headers(self.config.ACCESS_KEY, signature)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_order_history(self, account_id: str, symbol: Optional[str] = None, states: str = "filled") -> Dict[str, Any]:
        """Get order history"""
        url = f"{self.config.BASE_URL}/v1/order/orders"
        
        timestamp = str(int(time.time()))
        params = {
            "states": states
        }
        
        if symbol:
            params["symbol"] = symbol
        
        signature = HTXConfig.get_signature("GET", "api.huobi.pro", "/v1/order/orders", params, self.config.SECRET_KEY)
        headers = HTXConfig.get_headers(self.config.ACCESS_KEY, signature)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_staking_products(self, product_type: str = "STAKING") -> Dict[str, Any]:
        """Get staking products"""
        url = f"{self.config.BASE_URL}/v2/staking-product/quota"
        
        timestamp = str(int(time.time()))
        params = {
            "productType": product_type
        }
        
        signature = HTXConfig.get_signature("GET", "api.huobi.pro", "/v2/staking-product/quota", params, self.config.SECRET_KEY)
        headers = HTXConfig.get_headers(self.config.ACCESS_KEY, signature)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_earn_products(self, product_type: str = "SAVINGS") -> Dict[str, Any]:
        """Get earn products"""
        url = f"{self.config.BASE_URL}/v1/earn/products"
        
        timestamp = str(int(time.time()))
        params = {
            "productType": product_type
        }
        
        signature = HTXConfig.get_signature("GET", "api.huobi.pro", "/v1/earn/products", params, self.config.SECRET_KEY)
        headers = HTXConfig.get_headers(self.config.ACCESS_KEY, signature)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_nft_collections(self) -> Dict[str, Any]:
        """Get NFT collections"""
        url = f"{self.config.BASE_URL}/nft/conf/collection/list"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_copy_trading_leaders(self) -> Dict[str, Any]:
        """Get copy trading leaders"""
        url = f"{self.config.BASE_URL}/copy-trading/v1/leader/list"
        
        timestamp = str(int(time.time()))
        params = {}
        
        signature = HTXConfig.get_signature("GET", "api.huobi.pro", "/copy-trading/v1/leader/list", params, self.config.SECRET_KEY)
        headers = HTXConfig.get_headers(self.config.ACCESS_KEY, signature)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_futures_contracts(self) -> Dict[str, Any]:
        """Get futures contracts"""
        url = f"{self.config.FUTURES_URL}/api/v1/contract_contract_info"
        
        params = {}
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_futures_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get futures ticker"""
        url = f"{self.config.FUTURES_URL}/market/detail/merged"
        
        params = {
            "symbol": symbol
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()

# API Endpoints
@app.get("/tigerex/htx/accounts")
async def get_accounts(credentials: str = Depends(security)):
    """Get accounts - TigerEx HTX Integration"""
    async with TigerExHTXService() as service:
        return await service.get_accounts()

@app.get("/tigerex/htx/balance")
async def get_balance(
    account_id: str = Query(..., description="Account ID"),
    credentials: str = Depends(security)
):
    """Get account balance - TigerEx HTX Integration"""
    async with TigerExHTXService() as service:
        return await service.get_balance(account_id)

@app.post("/tigerex/htx/order")
async def place_order(order: HTXOrder, credentials: str = Depends(security)):
    """Place order - TigerEx HTX Integration"""
    async with TigerExHTXService() as service:
        return await service.place_order(order)

@app.get("/tigerex/htx/symbols")
async def get_symbols(credentials: str = Depends(security)):
    """Get trading symbols - TigerEx HTX Integration"""
    async with TigerExHTXService() as service:
        return await service.get_symbols()

@app.get("/tigerex/htx/ticker")
async def get_ticker(
    symbol: Optional[str] = Query(None, description="Symbol"),
    credentials: str = Depends(security)
):
    """Get ticker - TigerEx HTX Integration"""
    async with TigerExHTXService() as service:
        return await service.get_ticker(symbol)

@app.get("/tigerex/htx/orderbook")
async def get_depth(
    symbol: str = Query(..., description="Symbol"),
    depth_type: str = Query("step0", description="Depth type"),
    credentials: str = Depends(security)
):
    """Get orderbook - TigerEx HTX Integration"""
    async with TigerExHTXService() as service:
        return await service.get_depth(symbol, depth_type)

@app.get("/tigerex/htx/trades")
async def get_trades(
    symbol: str = Query(..., description="Symbol"),
    size: int = Query(100, description="Size"),
    credentials: str = Depends(security)
):
    """Get recent trades - TigerEx HTX Integration"""
    async with TigerExHTXService() as service:
        return await service.get_trades(symbol, size)

@app.get("/tigerex/htx/klines")
async def get_klines(
    symbol: str = Query(..., description="Symbol"),
    period: str = Query("1min", description="Period"),
    size: int = Query(150, description="Size"),
    from_: Optional[int] = Query(None, description="From"),
    to: Optional[int] = Query(None, description="To"),
    credentials: str = Depends(security)
):
    """Get klines - TigerEx HTX Integration"""
    async with TigerExHTXService() as service:
        return await service.get_klines(symbol, period, size, from_, to)

@app.get("/tigerex/htx/orders/open")
async def get_open_orders(
    account_id: str = Query(..., description="Account ID"),
    symbol: Optional[str] = Query(None, description="Symbol"),
    side: Optional[Side] = Query(None, description="Side"),
    credentials: str = Depends(security)
):
    """Get open orders - TigerEx HTX Integration"""
    async with TigerExHTXService() as service:
        return await service.get_open_orders(account_id, symbol, side)

@app.get("/tigerex/htx/orders/history")
async def get_order_history(
    account_id: str = Query(..., description="Account ID"),
    symbol: Optional[str] = Query(None, description="Symbol"),
    states: str = Query("filled", description="States"),
    credentials: str = Depends(security)
):
    """Get order history - TigerEx HTX Integration"""
    async with TigerExHTXService() as service:
        return await service.get_order_history(account_id, symbol, states)

@app.get("/tigerex/htx/staking")
async def get_staking_products(
    product_type: str = Query("STAKING", description="Product type"),
    credentials: str = Depends(security)
):
    """Get staking products - TigerEx HTX Integration"""
    async with TigerExHTXService() as service:
        return await service.get_staking_products(product_type)

@app.get("/tigerex/htx/earn/products")
async def get_earn_products(
    product_type: str = Query("SAVINGS", description="Product type"),
    credentials: str = Depends(security)
):
    """Get earn products - TigerEx HTX Integration"""
    async with TigerExHTXService() as service:
        return await service.get_earn_products(product_type)

@app.get("/tigerex/htx/nft/collections")
async def get_nft_collections(credentials: str = Depends(security)):
    """Get NFT collections - TigerEx HTX Integration"""
    async with TigerExHTXService() as service:
        return await service.get_nft_collections()

@app.get("/tigerex/htx/copytrading/leaders")
async def get_copy_trading_leaders(credentials: str = Depends(security)):
    """Get copy trading leaders - TigerEx HTX Integration"""
    async with TigerExHTXService() as service:
        return await service.get_copy_trading_leaders()

@app.get("/tigerex/htx/futures/contracts")
async def get_futures_contracts(credentials: str = Depends(security)):
    """Get futures contracts - TigerEx HTX Integration"""
    async with TigerExHTXService() as service:
        return await service.get_futures_contracts()

@app.get("/tigerex/htx/futures/ticker")
async def get_futures_ticker(
    symbol: str = Query(..., description="Symbol"),
    credentials: str = Depends(security)
):
    """Get futures ticker - TigerEx HTX Integration"""
    async with TigerExHTXService() as service:
        return await service.get_futures_ticker(symbol)

@app.get("/tigerex/htx/features")
async def get_available_features():
    """Get available TigerEx HTX features"""
    return {
        "service": "TigerEx HTX Advanced Service",
        "version": "1.0.0",
        "features": [feature.value for feature in HTXFeature],
        "supported_account_types": [at.value for at in AccountType],
        "supported_order_types": [ot.value for ot in OrderType],
        "tigerex_integrated": True
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "TigerEx HTX Advanced Service",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)