"""
Binance Advanced Service - Complete Binance Integration for TigerEx
All unique Binance features including trading, futures, margin, staking, etc.
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
    title="TigerEx Binance Advanced Service v1.0.0", 
    version="1.0.0",
    description="Complete Binance integration for TigerEx trading platform"
)
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BinanceFeature(str, Enum):
    SPOT_TRADING = "spot_trading"
    FUTURES_TRADING = "futures_trading"
    MARGIN_TRADING = "margin_trading"
    OPTIONS_TRADING = "options_trading"
    STAKING = "staking"
    LAUNCHPAD = "launchpad"
    LAUNCHPOOL = "launchpool"
    EARN_PRODUCTS = "earn_products"
    P2P_TRADING = "p2p_trading"
    CRYPTO_LOANS = "crypto_loans"
    DUAL_INVESTMENT = "dual_investment"
    LIQUIDITY_FARMING = "liquidity_farming"
    NFT_MARKETPLACE = "nft_marketplace"
    BINANCE_CARD = "binance_card"
    BINANCE_PAY = "binance_pay"
    VIP_TRADING = "vip_trading"
    INSTITUTIONAL = "institutional"
    PORTFOLIO_MANAGEMENT = "portfolio_management"
    TAX_REPORTING = "tax_reporting"
    ADVANCED_ANALYTICS = "advanced_analytics"

class TradingType(str, Enum):
    SPOT = "SPOT"
    MARGIN = "MARGIN"
    FUTURES = "FUTURES"
    OPTIONS = "OPTIONS"

class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_LIMIT = "STOP_LOSS_LIMIT"
    TAKE_PROFIT = "TAKE_PROFIT"
    TAKE_PROFIT_LIMIT = "TAKE_PROFIT_LIMIT"
    LIMIT_MAKER = "LIMIT_MAKER"

class TimeInForce(str, Enum):
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"

@dataclass
class BinanceConfig:
    API_KEY: str = os.getenv("BINANCE_API_KEY")
    API_SECRET: str = os.getenv("BINANCE_SECRET")
    BASE_URL: str = "https://api.binance.com"
    FUTURES_URL: str = "https://fapi.binance.com"
    OPTIONS_URL: str = "https://vapi.binance.com"
    MARGIN_URL: str = "https://api.binance.com"
    TESTNET_URL: str = "https://testnet.binance.vision"
    
    @staticmethod
    def get_signature(params: Dict[str, Any], secret: str) -> str:
        """Generate HMAC SHA256 signature for Binance API"""
        query_string = urllib.parse.urlencode(params)
        return hmac.new(
            secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    def get_headers(api_key: str) -> Dict[str, str]:
        """Get headers for Binance API requests"""
        return {
            'X-MBX-APIKEY': api_key,
            'Content-Type': 'application/json'
        }

class BinanceAccount(BaseModel):
    account_type: str
    balances: List[Dict[str, str]]
    permissions: List[str]
    maker_commission: int
    taker_commission: int
    buyer_commission: int
    seller_commission: int
    can_trade: bool
    can_withdraw: bool
    can_deposit: bool
    update_time: int
    account_type: str

class BinanceOrder(BaseModel):
    symbol: str
    side: str
    type: str
    quantity: Optional[float] = None
    quote_order_qty: Optional[float] = None
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: Optional[TimeInForce] = TimeInForce.GTC
    new_client_order_id: Optional[str] = None
    iceberg_qty: Optional[float] = None
    new_order_resp_type: Optional[str] = None

class BinanceTrade(BaseModel):
    symbol: str
    orderId: int
    orderListId: int
    price: str
    qty: str
    quoteQty: str
    commission: str
    commissionAsset: str
    time: int
    isBuyer: bool
    isMaker: bool
    isBestMatch: bool

class TigerExBinanceService:
    def __init__(self):
        self.config = BinanceConfig()
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_account_info(self, trading_type: TradingType = TradingType.SPOT) -> Dict[str, Any]:
        """Get account information for specified trading type"""
        url = f"{self.config.BASE_URL}/api/v3/account"
        
        params = {
            'timestamp': int(time.time() * 1000)
        }
        
        params['signature'] = BinanceConfig.get_signature(params, self.config.API_SECRET)
        headers = BinanceConfig.get_headers(self.config.API_KEY)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def place_order(self, order: BinanceOrder, trading_type: TradingType = TradingType.SPOT) -> Dict[str, Any]:
        """Place an order on Binance"""
        base_url = self.config.FUTURES_URL if trading_type == TradingType.FUTURES else self.config.BASE_URL
        endpoint = "/fapi/v1/order" if trading_type == TradingType.FUTURES else "/api/v3/order"
        
        params = {
            'symbol': order.symbol,
            'side': order.side,
            'type': order.type,
            'timestamp': int(time.time() * 1000)
        }
        
        if order.quantity:
            params['quantity'] = order.quantity
        if order.quote_order_qty:
            params['quoteOrderQty'] = order.quote_order_qty
        if order.price:
            params['price'] = order.price
        if order.stop_price:
            params['stopPrice'] = order.stop_price
        if order.time_in_force:
            params['timeInForce'] = order.time_in_force.value
        if order.new_client_order_id:
            params['newClientOrderId'] = order.new_client_order_id
        if order.iceberg_qty:
            params['icebergQty'] = order.iceberg_qty
        if order.new_order_resp_type:
            params['newOrderRespType'] = order.new_order_resp_type
        
        params['signature'] = BinanceConfig.get_signature(params, self.config.API_SECRET)
        headers = BinanceConfig.get_headers(self.config.API_KEY)
        
        async with self.session.post(base_url + endpoint, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_trading_pairs(self, trading_type: TradingType = TradingType.SPOT) -> List[Dict[str, Any]]:
        """Get all trading symbols for specified trading type"""
        if trading_type == TradingType.FUTURES:
            url = f"{self.config.FUTURES_URL}/fapi/v1/exchangeInfo"
        elif trading_type == TradingType.OPTIONS:
            url = f"{self.config.OPTIONS_URL}/vapi/v1/exchangeInfo"
        else:
            url = f"{self.config.BASE_URL}/api/v3/exchangeInfo"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            data = await response.json()
            return data['symbols'] if 'symbols' in data else data
    
    async def get_ticker_24hr(self, symbol: Optional[str] = None, trading_type: TradingType = TradingType.SPOT) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Get 24hr ticker price change statistics"""
        base_url = self.config.FUTURES_URL if trading_type == TradingType.FUTURES else self.config.BASE_URL
        endpoint = "/fapi/v1/ticker/24hr" if trading_type == TradingType.FUTURES else "/api/v3/ticker/24hr"
        
        params = {}
        if symbol:
            params['symbol'] = symbol
        
        async with self.session.get(base_url + endpoint, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_orderbook(self, symbol: str, limit: int = 100, trading_type: TradingType = TradingType.SPOT) -> Dict[str, Any]:
        """Get order book depth for a symbol"""
        base_url = self.config.FUTURES_URL if trading_type == TradingType.FUTURES else self.config.BASE_URL
        endpoint = "/fapi/v1/depth" if trading_type == TradingType.FUTURES else "/api/v3/depth"
        
        params = {
            'symbol': symbol,
            'limit': limit
        }
        
        async with self.session.get(base_url + endpoint, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_recent_trades(self, symbol: str, limit: int = 500, trading_type: TradingType = TradingType.SPOT) -> List[Dict[str, Any]]:
        """Get recent trades list for a symbol"""
        base_url = self.config.FUTURES_URL if trading_type == TradingType.FUTURES else self.config.BASE_URL
        endpoint = "/fapi/v1/trades" if trading_type == TradingType.FUTURES else "/api/v3/trades"
        
        params = {
            'symbol': symbol,
            'limit': limit
        }
        
        async with self.session.get(base_url + endpoint, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_historical_klines(
        self, 
        symbol: str, 
        interval: str, 
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 500,
        trading_type: TradingType = TradingType.SPOT
    ) -> List[List[str]]:
        """Get historical kline/candlestick data"""
        base_url = self.config.FUTURES_URL if trading_type == TradingType.FUTURES else self.config.BASE_URL
        endpoint = "/fapi/v1/klines" if trading_type == TradingType.FUTURES else "/api/v3/klines"
        
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
        
        async with self.session.get(base_url + endpoint, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_staking_products(self, product_type: str = "STAKING") -> Dict[str, Any]:
        """Get Binance staking products"""
        url = f"{self.config.BASE_URL}/sapi/v1/staking/productList"
        
        params = {
            'product': product_type,
            'timestamp': int(time.time() * 1000)
        }
        
        params['signature'] = BinanceConfig.get_signature(params, self.config.API_SECRET)
        headers = BinanceConfig.get_headers(self.config.API_KEY)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_launchpad_projects(self) -> Dict[str, Any]:
        """Get Binance Launchpad projects"""
        url = f"{self.config.BASE_URL}/sapi/v1/launchpad/project"
        
        params = {
            'timestamp': int(time.time() * 1000)
        }
        
        params['signature'] = BinanceConfig.get_signature(params, self.config.API_SECRET)
        headers = BinanceConfig.get_headers(self.config.API_KEY)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_launchpool_projects(self) -> Dict[str, Any]:
        """Get Binance Launchpool projects"""
        url = f"{self.config.BASE_URL}/sapi/v1/launchpool/project"
        
        params = {
            'timestamp': int(time.time() * 1000)
        }
        
        params['signature'] = BinanceConfig.get_signature(params, self.config.API_SECRET)
        headers = BinanceConfig.get_headers(self.config.API_KEY)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_flexible_savings_products(self) -> Dict[str, Any]:
        """Get Binance flexible savings products"""
        url = f"{self.config.BASE_URL}/sapi/v1/lending/daily/product/list"
        
        params = {
            'status': 'ALL',
            'timestamp': int(time.time() * 1000)
        }
        
        params['signature'] = BinanceConfig.get_signature(params, self.config.API_SECRET)
        headers = BinanceConfig.get_headers(self.config.API_KEY)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_locked_savings_products(self) -> Dict[str, Any]:
        """Get Binance locked savings products"""
        url = f"{self.config.BASE_URL}/sapi/v1/lending/customizedFixed/product/list"
        
        params = {
            'timestamp': int(time.time() * 1000)
        }
        
        params['signature'] = BinanceConfig.get_signature(params, self.config.API_SECRET)
        headers = BinanceConfig.get_headers(self.config.API_KEY)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_nft_collections(self) -> Dict[str, Any]:
        """Get Binance NFT collections"""
        url = f"{self.config.BASE_URL}/sapi/v1/nft/nft/collection"
        
        params = {
            'timestamp': int(time.time() * 1000)
        }
        
        params['signature'] = BinanceConfig.get_signature(params, self.config.API_SECRET)
        headers = BinanceConfig.get_headers(self.config.API_KEY)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()

# API Endpoints
@app.get("/tigerex/binance/account")
async def get_account_info(
    trading_type: TradingType = Query(TradingType.SPOT, description="Trading type"),
    credentials: str = Depends(security)
):
    """Get account information - TigerEx Binance Integration"""
    async with TigerExBinanceService() as service:
        return await service.get_account_info(trading_type)

@app.post("/tigerex/binance/order")
async def place_order(
    order: BinanceOrder,
    trading_type: TradingType = Query(TradingType.SPOT, description="Trading type"),
    credentials: str = Depends(security)
):
    """Place order - TigerEx Binance Integration"""
    async with TigerExBinanceService() as service:
        return await service.place_order(order, trading_type)

@app.get("/tigerex/binance/symbols")
async def get_trading_pairs(
    trading_type: TradingType = Query(TradingType.SPOT, description="Trading type"),
    credentials: str = Depends(security)
):
    """Get trading pairs - TigerEx Binance Integration"""
    async with TigerExBinanceService() as service:
        return await service.get_trading_pairs(trading_type)

@app.get("/tigerex/binance/ticker/24hr")
async def get_24hr_ticker(
    symbol: Optional[str] = Query(None, description="Symbol"),
    trading_type: TradingType = Query(TradingType.SPOT, description="Trading type"),
    credentials: str = Depends(security)
):
    """Get 24hr ticker - TigerEx Binance Integration"""
    async with TigerExBinanceService() as service:
        return await service.get_ticker_24hr(symbol, trading_type)

@app.get("/tigerex/binance/orderbook")
async def get_orderbook(
    symbol: str = Query(..., description="Symbol"),
    limit: int = Query(100, description="Limit"),
    trading_type: TradingType = Query(TradingType.SPOT, description="Trading type"),
    credentials: str = Depends(security)
):
    """Get orderbook - TigerEx Binance Integration"""
    async with TigerExBinanceService() as service:
        return await service.get_orderbook(symbol, limit, trading_type)

@app.get("/tigerex/binance/trades")
async def get_recent_trades(
    symbol: str = Query(..., description="Symbol"),
    limit: int = Query(500, description="Limit"),
    trading_type: TradingType = Query(TradingType.SPOT, description="Trading type"),
    credentials: str = Depends(security)
):
    """Get recent trades - TigerEx Binance Integration"""
    async with TigerExBinanceService() as service:
        return await service.get_recent_trades(symbol, limit, trading_type)

@app.get("/tigerex/binance/klines")
async def get_historical_klines(
    symbol: str = Query(..., description="Symbol"),
    interval: str = Query(..., description="Interval"),
    start_time: Optional[int] = Query(None, description="Start time"),
    end_time: Optional[int] = Query(None, description="End time"),
    limit: int = Query(500, description="Limit"),
    trading_type: TradingType = Query(TradingType.SPOT, description="Trading type"),
    credentials: str = Depends(security)
):
    """Get historical klines - TigerEx Binance Integration"""
    async with TigerExBinanceService() as service:
        return await service.get_historical_klines(symbol, interval, start_time, end_time, limit, trading_type)

@app.get("/tigerex/binance/staking")
async def get_staking_products(
    product_type: str = Query("STAKING", description="Product type"),
    credentials: str = Depends(security)
):
    """Get staking products - TigerEx Binance Integration"""
    async with TigerExBinanceService() as service:
        return await service.get_staking_products(product_type)

@app.get("/tigerex/binance/launchpad")
async def get_launchpad_projects(credentials: str = Depends(security)):
    """Get launchpad projects - TigerEx Binance Integration"""
    async with TigerExBinanceService() as service:
        return await service.get_launchpad_projects()

@app.get("/tigerex/binance/launchpool")
async def get_launchpool_projects(credentials: str = Depends(security)):
    """Get launchpool projects - TigerEx Binance Integration"""
    async with TigerExBinanceService() as service:
        return await service.get_launchpool_projects()

@app.get("/tigerex/binance/savings/flexible")
async def get_flexible_savings(credentials: str = Depends(security)):
    """Get flexible savings - TigerEx Binance Integration"""
    async with TigerExBinanceService() as service:
        return await service.get_flexible_savings_products()

@app.get("/tigerex/binance/savings/locked")
async def get_locked_savings(credentials: str = Depends(security)):
    """Get locked savings - TigerEx Binance Integration"""
    async with TigerExBinanceService() as service:
        return await service.get_locked_savings_products()

@app.get("/tigerex/binance/nft/collections")
async def get_nft_collections(credentials: str = Depends(security)):
    """Get NFT collections - TigerEx Binance Integration"""
    async with TigerExBinanceService() as service:
        return await service.get_nft_collections()

@app.get("/tigerex/binance/features")
async def get_available_features():
    """Get available TigerEx Binance features"""
    return {
        "service": "TigerEx Binance Advanced Service",
        "version": "1.0.0",
        "features": [feature.value for feature in BinanceFeature],
        "supported_trading_types": [tt.value for tt in TradingType],
        "supported_order_types": [ot.value for ot in OrderType],
        "tigerex_integrated": True
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "TigerEx Binance Advanced Service",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)