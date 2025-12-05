"""
Bybit Advanced Service - Complete Bybit Integration for TigerEx
All unique Bybit features including trading, derivatives, copy trading, etc.
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
    title="TigerEx Bybit Advanced Service v1.0.0", 
    version="1.0.0",
    description="Complete Bybit integration for TigerEx trading platform"
)
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BybitFeature(str, Enum):
    SPOT_TRADING = "spot_trading"
    DERIVATIVES_TRADING = "derivatives_trading"
    OPTIONS_TRADING = "options_trading"
    COPY_TRADING = "copy_trading"
    BOT_TRADING = "bot_trading"
    BYBIT_EARN = "bybit_earn"
    LEARN_AND_EARN = "learn_and_earn"
    LAUNCHPAD = "launchpad"
    BYBIT_CARD = "bybit_card"
    INSTITUTIONAL = "institutional"
    VIP_PROGRAM = "vip_program"
    LIQUIDITY_MINING = "liquidity_mining"
    STAKING_PRODUCTS = "staking_products"
    DEFI_MINING = "defi_mining"
    INSURANCE_FUND = "insurance_fund"
    API_FEATURES = "api_features"

class TradingCategory(str, Enum):
    SPOT = "spot"
    LINEAR = "linear"
    INVERSE = "inverse"
    OPTION = "option"

class OrderType(str, Enum):
    MARKET = "Market"
    LIMIT = "Limit"
    STOP_LIMIT = "StopLimit"
    STOP_MARKET = "StopMarket"
    TRAILING_STOP = "TrailingStop"
    iceberg = "Iceberg"
    LIMIT_MAKER = "LimitMaker"
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"

class Side(str, Enum):
    BUY = "Buy"
    SELL = "Sell"

@dataclass
class BybitConfig:
    API_KEY: str = os.getenv("BYBIT_API_KEY")
    API_SECRET: str = os.getenv("BYBIT_SECRET")
    BASE_URL: str = "https://api.bybit.com"
    TESTNET_URL: str = "https://api-testnet.bybit.com"
    
    @staticmethod
    def get_signature(params: Dict[str, Any], secret: str, recv_window: int = 5000) -> str:
        """Generate HMAC SHA256 signature for Bybit API"""
        timestamp = str(int(time.time() * 1000))
        param_str = timestamp + str(recv_window) + json.dumps(params)
        return hmac.new(
            secret.encode('utf-8'),
            param_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    def get_headers(api_key: str, signature: str, timestamp: str, recv_window: int = 5000) -> Dict[str, str]:
        """Get headers for Bybit API requests"""
        return {
            'X-BAPI-API-KEY': api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': str(recv_window),
            'Content-Type': 'application/json'
        }

class BybitOrder(BaseModel):
    category: TradingCategory
    symbol: str
    side: Side
    orderType: OrderType
    qty: str
    price: Optional[str] = None
    triggerPrice: Optional[str] = None
    triggerDirection: Optional[str] = None
    orderLinkId: Optional[str] = None
    takeProfit: Optional[str] = None
    stopLoss: Optional[str] = None
    tpslMode: Optional[str] = None
    tpTriggerPrice: Optional[str] = None
    slTriggerPrice: Optional[str] = None
    tpLimitPrice: Optional[str] = None
    slLimitPrice: Optional[str] = None
    triggerBy: Optional[str] = None
    orderFilter: Optional[str] = None
    limitMakerPriceType: Optional[str] = None
    timeInForce: Optional[str] = None
    positionIdx: Optional[int] = None
    reduceOnly: Optional[bool] = None
    closeOnTrigger: Optional[bool] = None
    smpType: Optional[str] = None
    mmp: Optional[str] = None
    tpOrderType: Optional[str] = None
    slOrderType: Optional[str] = None
    tpSize: Optional[str] = None
    slSize: Optional[str] = None
    tpPrice: Optional[str] = None
    slPrice: Optional[str] = None

class BybitWalletBalance(BaseModel):
    totalEquity: str
    accountIMRate: str
    totalMarginBalance: str
    totalInitialMargin: str
    accountType: str
    accountMMRate: str
    totalPerpUPL: str
    accountLTV: str
    totalAvailableBalance: str

class TigerExBybitService:
    def __init__(self):
        self.config = BybitConfig()
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_wallet_balance(self, account_type: str = "UNIFIED") -> Dict[str, Any]:
        """Get wallet balance information"""
        url = f"{self.config.BASE_URL}/v5/account/wallet-balance"
        
        params = {
            "accountType": account_type
        }
        
        timestamp = str(int(time.time() * 1000))
        recv_window = 5000
        signature = BybitConfig.get_signature(params, self.config.API_SECRET, recv_window)
        headers = BybitConfig.get_headers(self.config.API_KEY, signature, timestamp, recv_window)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def place_order(self, order: BybitOrder) -> Dict[str, Any]:
        """Place an order on Bybit"""
        url = f"{self.config.BASE_URL}/v5/order/create"
        
        params = {
            "category": order.category.value,
            "symbol": order.symbol,
            "side": order.side.value,
            "orderType": order.orderType.value,
            "qty": order.qty
        }
        
        # Add optional parameters
        if order.price:
            params["price"] = order.price
        if order.triggerPrice:
            params["triggerPrice"] = order.triggerPrice
        if order.orderLinkId:
            params["orderLinkId"] = order.orderLinkId
        if order.takeProfit:
            params["takeProfit"] = order.takeProfit
        if order.stopLoss:
            params["stopLoss"] = order.stopLoss
        if order.timeInForce:
            params["timeInForce"] = order.timeInForce
        if order.reduceOnly is not None:
            params["reduceOnly"] = order.reduceOnly
        if order.closeOnTrigger is not None:
            params["closeOnTrigger"] = order.closeOnTrigger
        
        timestamp = str(int(time.time() * 1000))
        recv_window = 5000
        signature = BybitConfig.get_signature(params, self.config.API_SECRET, recv_window)
        headers = BybitConfig.get_headers(self.config.API_KEY, signature, timestamp, recv_window)
        
        async with self.session.post(url, json=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_instruments_info(self, category: TradingCategory, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get instruments information for specified category"""
        url = f"{self.config.BASE_URL}/v5/market/instruments-info"
        
        params = {
            "category": category.value
        }
        
        if symbol:
            params["symbol"] = symbol
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_tickers(self, category: TradingCategory, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get tickers information"""
        url = f"{self.config.BASE_URL}/v5/market/tickers"
        
        params = {
            "category": category.value
        }
        
        if symbol:
            params["symbol"] = symbol
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_orderbook(self, category: TradingCategory, symbol: str, limit: int = 25) -> Dict[str, Any]:
        """Get orderbook information"""
        url = f"{self.config.BASE_URL}/v5/market/orderbook"
        
        params = {
            "category": category.value,
            "symbol": symbol,
            "limit": limit
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_recent_trades(self, category: TradingCategory, symbol: str, limit: int = 60) -> Dict[str, Any]:
        """Get recent trades"""
        url = f"{self.config.BASE_URL}/v5/market/recent-trade"
        
        params = {
            "category": category.value,
            "symbol": symbol,
            "limit": limit
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_kline_data(
        self, 
        category: TradingCategory, 
        symbol: str, 
        interval: str, 
        start: Optional[int] = None,
        end: Optional[int] = None,
        limit: int = 200
    ) -> Dict[str, Any]:
        """Get kline/candlestick data"""
        url = f"{self.config.BASE_URL}/v5/market/kline"
        
        params = {
            "category": category.value,
            "symbol": symbol,
            "interval": interval,
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
    
    async def get_open_orders(self, category: TradingCategory, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get open orders"""
        url = f"{self.config.BASE_URL}/v5/order/realtime"
        
        params = {
            "category": category.value
        }
        
        if symbol:
            params["symbol"] = symbol
        
        timestamp = str(int(time.time() * 1000))
        recv_window = 5000
        signature = BybitConfig.get_signature(params, self.config.API_SECRET, recv_window)
        headers = BybitConfig.get_headers(self.config.API_KEY, signature, timestamp, recv_window)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_order_history(self, category: TradingCategory, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get order history"""
        url = f"{self.config.BASE_URL}/v5/order/history"
        
        params = {
            "category": category.value
        }
        
        if symbol:
            params["symbol"] = symbol
        
        timestamp = str(int(time.time() * 1000))
        recv_window = 5000
        signature = BybitConfig.get_signature(params, self.config.API_SECRET, recv_window)
        headers = BybitConfig.get_headers(self.config.API_KEY, signature, timestamp, recv_window)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_copy_trading_leaders(self) -> Dict[str, Any]:
        """Get copy trading leaders"""
        url = f"{self.config.BASE_URL}/v5/copytrading/leader/list"
        
        timestamp = str(int(time.time() * 1000))
        recv_window = 5000
        params = {}
        signature = BybitConfig.get_signature(params, self.config.API_SECRET, recv_window)
        headers = BybitConfig.get_headers(self.config.API_KEY, signature, timestamp, recv_window)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_bot_trading_list(self) -> Dict[str, Any]:
        """Get bot trading list"""
        url = f"{self.config.BASE_URL}/v5/bot/order/list"
        
        params = {}
        
        timestamp = str(int(time.time() * 1000))
        recv_window = 5000
        signature = BybitConfig.get_signature(params, self.config.API_SECRET, recv_window)
        headers = BybitConfig.get_headers(self.config.API_KEY, signature, timestamp, recv_window)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_bybit_earn_products(self, product_type: str = "savings") -> Dict[str, Any]:
        """Get Bybit Earn products"""
        url = f"{self.config.BASE_URL}/v5/earn/loan/product/list"
        
        params = {
            "productType": product_type
        }
        
        timestamp = str(int(time.time() * 1000))
        recv_window = 5000
        signature = BybitConfig.get_signature(params, self.config.API_SECRET, recv_window)
        headers = BybitConfig.get_headers(self.config.API_KEY, signature, timestamp, recv_window)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_launchpad_projects(self) -> Dict[str, Any]:
        """Get launchpad projects"""
        url = f"{self.config.BASE_URL}/v5/market/launchpool/info"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_vip_info(self) -> Dict[str, Any]:
        """Get VIP information"""
        url = f"{self.config.BASE_URL}/v5/user/vip-info"
        
        params = {}
        
        timestamp = str(int(time.time() * 1000))
        recv_window = 5000
        signature = BybitConfig.get_signature(params, self.config.API_SECRET, recv_window)
        headers = BybitConfig.get_headers(self.config.API_KEY, signature, timestamp, recv_window)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_insurance_fund(self) -> Dict[str, Any]:
        """Get insurance fund data"""
        url = f"{self.config.BASE_URL}/v5/market/insurance-fund"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()

# API Endpoints
@app.get("/tigerex/bybit/wallet/balance")
async def get_wallet_balance(
    account_type: str = Query("UNIFIED", description="Account type"),
    credentials: str = Depends(security)
):
    """Get wallet balance - TigerEx Bybit Integration"""
    async with TigerExBybitService() as service:
        return await service.get_wallet_balance(account_type)

@app.post("/tigerex/bybit/order")
async def place_order(order: BybitOrder, credentials: str = Depends(security)):
    """Place order - TigerEx Bybit Integration"""
    async with TigerExBybitService() as service:
        return await service.place_order(order)

@app.get("/tigerex/bybit/instruments")
async def get_instruments_info(
    category: TradingCategory = Query(..., description="Trading category"),
    symbol: Optional[str] = Query(None, description="Symbol"),
    credentials: str = Depends(security)
):
    """Get instruments info - TigerEx Bybit Integration"""
    async with TigerExBybitService() as service:
        return await service.get_instruments_info(category, symbol)

@app.get("/tigerex/bybit/tickers")
async def get_tickers(
    category: TradingCategory = Query(..., description="Trading category"),
    symbol: Optional[str] = Query(None, description="Symbol"),
    credentials: str = Depends(security)
):
    """Get tickers - TigerEx Bybit Integration"""
    async with TigerExBybitService() as service:
        return await service.get_tickers(category, symbol)

@app.get("/tigerex/bybit/orderbook")
async def get_orderbook(
    category: TradingCategory = Query(..., description="Trading category"),
    symbol: str = Query(..., description="Symbol"),
    limit: int = Query(25, description="Limit"),
    credentials: str = Depends(security)
):
    """Get orderbook - TigerEx Bybit Integration"""
    async with TigerExBybitService() as service:
        return await service.get_orderbook(category, symbol, limit)

@app.get("/tigerex/bybit/trades")
async def get_recent_trades(
    category: TradingCategory = Query(..., description="Trading category"),
    symbol: str = Query(..., description="Symbol"),
    limit: int = Query(60, description="Limit"),
    credentials: str = Depends(security)
):
    """Get recent trades - TigerEx Bybit Integration"""
    async with TigerExBybitService() as service:
        return await service.get_recent_trades(category, symbol, limit)

@app.get("/tigerex/bybit/klines")
async def get_kline_data(
    category: TradingCategory = Query(..., description="Trading category"),
    symbol: str = Query(..., description="Symbol"),
    interval: str = Query(..., description="Interval"),
    start: Optional[int] = Query(None, description="Start time"),
    end: Optional[int] = Query(None, description="End time"),
    limit: int = Query(200, description="Limit"),
    credentials: str = Depends(security)
):
    """Get kline data - TigerEx Bybit Integration"""
    async with TigerExBybitService() as service:
        return await service.get_kline_data(category, symbol, interval, start, end, limit)

@app.get("/tigerex/bybit/orders/open")
async def get_open_orders(
    category: TradingCategory = Query(..., description="Trading category"),
    symbol: Optional[str] = Query(None, description="Symbol"),
    credentials: str = Depends(security)
):
    """Get open orders - TigerEx Bybit Integration"""
    async with TigerExBybitService() as service:
        return await service.get_open_orders(category, symbol)

@app.get("/tigerex/bybit/orders/history")
async def get_order_history(
    category: TradingCategory = Query(..., description="Trading category"),
    symbol: Optional[str] = Query(None, description="Symbol"),
    credentials: str = Depends(security)
):
    """Get order history - TigerEx Bybit Integration"""
    async with TigerExBybitService() as service:
        return await service.get_order_history(category, symbol)

@app.get("/tigerex/bybit/copytrading/leaders")
async def get_copy_trading_leaders(credentials: str = Depends(security)):
    """Get copy trading leaders - TigerEx Bybit Integration"""
    async with TigerExBybitService() as service:
        return await service.get_copy_trading_leaders()

@app.get("/tigerex/bybit/bots")
async def get_bot_trading_list(credentials: str = Depends(security)):
    """Get bot trading list - TigerEx Bybit Integration"""
    async with TigerExBybitService() as service:
        return await service.get_bot_trading_list()

@app.get("/tigerex/bybit/earn/products")
async def get_bybit_earn_products(
    product_type: str = Query("savings", description="Product type"),
    credentials: str = Depends(security)
):
    """Get earn products - TigerEx Bybit Integration"""
    async with TigerExBybitService() as service:
        return await service.get_bybit_earn_products(product_type)

@app.get("/tigerex/bybit/launchpad")
async def get_launchpad_projects(credentials: str = Depends(security)):
    """Get launchpad projects - TigerEx Bybit Integration"""
    async with TigerExBybitService() as service:
        return await service.get_launchpad_projects()

@app.get("/tigerex/bybit/vip/info")
async def get_vip_info(credentials: str = Depends(security)):
    """Get VIP information - TigerEx Bybit Integration"""
    async with TigerExBybitService() as service:
        return await service.get_vip_info()

@app.get("/tigerex/bybit/insurance/fund")
async def get_insurance_fund(credentials: str = Depends(security)):
    """Get insurance fund - TigerEx Bybit Integration"""
    async with TigerExBybitService() as service:
        return await service.get_insurance_fund()

@app.get("/tigerex/bybit/features")
async def get_available_features():
    """Get available TigerEx Bybit features"""
    return {
        "service": "TigerEx Bybit Advanced Service",
        "version": "1.0.0",
        "features": [feature.value for feature in BybitFeature],
        "supported_categories": [cat.value for cat in TradingCategory],
        "supported_order_types": [ot.value for ot in OrderType],
        "tigerex_integrated": True
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "TigerEx Bybit Advanced Service",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)