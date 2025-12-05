"""
OKX Advanced Service - Complete OKX Integration for TigerEx
All unique OKX features including trading, futures, DeFi, Web3, etc.
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
    title="TigerEx OKX Advanced Service v1.0.0", 
    version="1.0.0",
    description="Complete OKX integration for TigerEx trading platform"
)
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OKXFeature(str, Enum):
    SPOT_TRADING = "spot_trading"
    FUTURES_TRADING = "futures_trading"
    OPTIONS_TRADING = "options_trading"
    MARGIN_TRADING = "margin_trading"
    DEFI_HUB = "defi_hub"
    EARN_PRODUCTS = "earn_products"
    DEX_INTEGRATION = "dex_integration"
    NFT_MARKETPLACE = "nft_marketplace"
    WEB3_WALLET = "web3_wallet"
    JUMPSTART = "jumpstart"
    OKX_POOL = "okx_pool"
    STAKING_SERVICES = "staking_services"
    LIQUIDITY_MINING = "liquidity_mining"
    COPY_TRADING = "copy_trading"
    BOT_TRADING = "bot_trading"
    INSTITUTIONAL = "institutional"
    API_FEATURES = "api_features"

class InstType(str, Enum):
    SPOT = "SPOT"
    MARGIN = "MARGIN"
    SWAP = "SWAP"
    FUTURES = "FUTURES"
    OPTION = "OPTION"

class TradeMode(str, Enum):
    SPOT = "cash"
    ISOLATED_MARGIN = "isolated"
    CROSS_MARGIN = "cross"
    PORTFOLIO_MARGIN = "portfolio"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    POST_ONLY = "post_only"
    FOK = "fok"
    IOC = "ioc"
    OPTIMAL_LIMIT_IOC = "optimal_limit_ioc"

class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass
class OKXConfig:
    API_KEY: str = os.getenv("OKX_API_KEY")
    API_SECRET: str = os.getenv("OKX_SECRET")
    PASSPHRASE: str = os.getenv("OKX_PASSPHRASE")
    BASE_URL: str = "https://www.okx.com"
    DEMO_URL: str = "https://www.okx.com"
    
    @staticmethod
    def get_signature(timestamp: str, method: str, request_path: str, body: str, secret: str) -> str:
        """Generate HMAC SHA256 signature for OKX API"""
        message = timestamp + method + request_path + body
        return base64.b64encode(
            hmac.new(
                secret.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
    
    @staticmethod
    def get_headers(api_key: str, passphrase: str, signature: str, timestamp: str) -> Dict[str, str]:
        """Get headers for OKX API requests"""
        return {
            'OK-ACCESS-KEY': api_key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': passphrase,
            'Content-Type': 'application/json'
        }

class OKXOrder(BaseModel):
    instId: str = Field(..., description="Instrument ID")
    tdMode: TradeMode = Field(..., description="Trade mode")
    side: Side = Field(..., description="Order side")
    ordType: OrderType = Field(..., description="Order type")
    sz: str = Field(..., description="Order size")
    ccy: Optional[str] = Field(None, description="Margin currency")
    clOrdId: Optional[str] = Field(None, description="Client order ID")
    tag: Optional[str] = Field(None, description="Order tag")
    px: Optional[str] = Field(None, description="Order price")
    reduceOnly: Optional[bool] = Field(None, description="Reduce only")
    qtyCcy: Optional[str] = Field(None, description="Quantity currency")
    amm: Optional[str] = Field(None, description="AMM")
    attachAlgoOrds: Optional[Dict[str, Any]] = Field(None, description="Attach algo orders")
    tpTriggerPx: Optional[str] = Field(None, description="Take profit trigger price")
    tpTriggerPxType: Optional[str] = Field(None, description="Take profit trigger price type")
    tpOrdPx: Optional[str] = Field(None, description="Take profit order price")
    slTriggerPx: Optional[str] = Field(None, description="Stop loss trigger price")
    slTriggerPxType: Optional[str] = Field(None, description="Stop loss trigger price type")
    slOrdPx: Optional[str] = Field(None, description="Stop loss order price")
    triggerPx: Optional[str] = Field(None, description="Trigger price")
    triggerPxType: Optional[str] = Field(None, description="Trigger price type")
    algoClOrdId: Optional[str] = Field(None, description="Algo client order ID")
    algoSz: Optional[str] = Field(None, description="Algo size")
    tgtCcy: Optional[str] = Field(None, description="Target currency")

class TigerExOKXService:
    def __init__(self):
        self.config = OKXConfig()
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_balance(self, ccy: Optional[str] = None) -> Dict[str, Any]:
        """Get account balance"""
        url = f"{self.config.BASE_URL}/api/v5/account/balance"
        
        params = {}
        if ccy:
            params["ccy"] = ccy
        
        timestamp = str(time.time())
        method = "GET"
        request_path = "/api/v5/account/balance"
        body = json.dumps(params) if params else ""
        
        signature = OKXConfig.get_signature(timestamp, method, request_path, body, self.config.API_SECRET)
        headers = OKXConfig.get_headers(self.config.API_KEY, self.config.PASSPHRASE, signature, timestamp)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def place_order(self, order: OKXOrder) -> Dict[str, Any]:
        """Place an order on OKX"""
        url = f"{self.config.BASE_URL}/api/v5/trade/order"
        
        params = {
            "instId": order.instId,
            "tdMode": order.tdMode.value,
            "side": order.side.value,
            "ordType": order.ordType.value,
            "sz": order.sz
        }
        
        # Add optional parameters
        if order.ccy:
            params["ccy"] = order.ccy
        if order.clOrdId:
            params["clOrdId"] = order.clOrdId
        if order.tag:
            params["tag"] = order.tag
        if order.px:
            params["px"] = order.px
        if order.reduceOnly is not None:
            params["reduceOnly"] = order.reduceOnly
        if order.qtyCcy:
            params["qtyCcy"] = order.qtyCcy
        if order.tpTriggerPx:
            params["tpTriggerPx"] = order.tpTriggerPx
        if order.slTriggerPx:
            params["slTriggerPx"] = order.slTriggerPx
        if order.triggerPx:
            params["triggerPx"] = order.triggerPx
        
        timestamp = str(time.time())
        method = "POST"
        request_path = "/api/v5/trade/order"
        body = json.dumps(params)
        
        signature = OKXConfig.get_signature(timestamp, method, request_path, body, self.config.API_SECRET)
        headers = OKXConfig.get_headers(self.config.API_KEY, self.config.PASSPHRASE, signature, timestamp)
        
        async with self.session.post(url, json=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_instruments(self, inst_type: InstType, uly: Optional[str] = None, inst_id: Optional[str] = None) -> Dict[str, Any]:
        """Get instruments information"""
        url = f"{self.config.BASE_URL}/api/v5/public/instruments"
        
        params = {
            "instType": inst_type.value
        }
        
        if uly:
            params["uly"] = uly
        if inst_id:
            params["instId"] = inst_id
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_ticker(self, inst_type: InstType, inst_id: Optional[str] = None) -> Dict[str, Any]:
        """Get ticker information"""
        url = f"{self.config.BASE_URL}/api/v5/market/ticker"
        
        params = {
            "instType": inst_type.value
        }
        
        if inst_id:
            params["instId"] = inst_id
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_orderbook(self, inst_id: str, sz: int = 1) -> Dict[str, Any]:
        """Get orderbook information"""
        url = f"{self.config.BASE_URL}/api/v5/market/books"
        
        params = {
            "instId": inst_id,
            "sz": sz
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_trades(self, inst_id: str, limit: int = 100) -> Dict[str, Any]:
        """Get recent trades"""
        url = f"{self.config.BASE_URL}/api/v5/market/trades"
        
        params = {
            "instId": inst_id,
            "limit": limit
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_candlesticks(
        self, 
        inst_id: str, 
        bar: str = "1m", 
        after: Optional[str] = None,
        before: Optional[str] = None,
        limit: str = "100"
    ) -> Dict[str, Any]:
        """Get candlestick data"""
        url = f"{self.config.BASE_URL}/api/v5/market/candles"
        
        params = {
            "instId": inst_id,
            "bar": bar,
            "limit": limit
        }
        
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_pending_orders(self, inst_type: Optional[InstType] = None, inst_id: Optional[str] = None) -> Dict[str, Any]:
        """Get pending orders"""
        url = f"{self.config.BASE_URL}/api/v5/trade/orders-pending"
        
        params = {}
        if inst_type:
            params["instType"] = inst_type.value
        if inst_id:
            params["instId"] = inst_id
        
        timestamp = str(time.time())
        method = "GET"
        request_path = "/api/v5/trade/orders-pending"
        body = json.dumps(params) if params else ""
        
        signature = OKXConfig.get_signature(timestamp, method, request_path, body, self.config.API_SECRET)
        headers = OKXConfig.get_headers(self.config.API_KEY, self.config.PASSPHRASE, signature, timestamp)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_order_history(self, inst_type: Optional[InstType] = None, inst_id: Optional[str] = None) -> Dict[str, Any]:
        """Get order history"""
        url = f"{self.config.BASE_URL}/api/v5/trade/orders-history"
        
        params = {}
        if inst_type:
            params["instType"] = inst_type.value
        if inst_id:
            params["instId"] = inst_id
        
        timestamp = str(time.time())
        method = "GET"
        request_path = "/api/v5/trade/orders-history"
        body = json.dumps(params) if params else ""
        
        signature = OKXConfig.get_signature(timestamp, method, request_path, body, self.config.API_SECRET)
        headers = OKXConfig.get_headers(self.config.API_KEY, self.config.PASSPHRASE, signature, timestamp)
        
        async with self.session.get(url, params=params, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_earn_products(self, product_type: str = "SAVINGS") -> Dict[str, Any]:
        """Get earn products"""
        url = f"{self.config.BASE_URL}/api/v5/finance/savings/earn/info"
        
        timestamp = str(time.time())
        method = "GET"
        request_path = "/api/v5/finance/savings/earn/info"
        body = ""
        
        signature = OKXConfig.get_signature(timestamp, method, request_path, body, self.config.API_SECRET)
        headers = OKXConfig.get_headers(self.config.API_KEY, self.config.PASSPHRASE, signature, timestamp)
        
        async with self.session.get(url, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_staking_products(self) -> Dict[str, Any]:
        """Get staking products"""
        url = f"{self.config.BASE_URL}/api/v5/finance/staking-defi/earn/info"
        
        timestamp = str(time.time())
        method = "GET"
        request_path = "/api/v5/finance/staking-defi/earn/info"
        body = ""
        
        signature = OKXConfig.get_signature(timestamp, method, request_path, body, self.config.API_SECRET)
        headers = OKXConfig.get_headers(self.config.API_KEY, self.config.PASSPHRASE, signature, timestamp)
        
        async with self.session.get(url, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_jumpstart_projects(self) -> Dict[str, Any]:
        """Get jumpstart projects"""
        url = f"{self.config.BASE_URL}/api/v5/public/jumpstart/projects"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_nft_collections(self) -> Dict[str, Any]:
        """Get NFT collections"""
        url = f"{self.config.BASE_URL}/api/v5/market/nft/collection"
        
        params = {}
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_copy_trading_leaders(self) -> Dict[str, Any]:
        """Get copy trading leaders"""
        url = f"{self.config.BASE_URL}/api/v5/copytrading/current-leaders"
        
        timestamp = str(time.time())
        method = "GET"
        request_path = "/api/v5/copytrading/current-leaders"
        body = ""
        
        signature = OKXConfig.get_signature(timestamp, method, request_path, body, self.config.API_SECRET)
        headers = OKXConfig.get_headers(self.config.API_KEY, self.config.PASSPHRASE, signature, timestamp)
        
        async with self.session.get(url, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_dex_volumes(self) -> Dict[str, Any]:
        """Get DEX volumes"""
        url = f"{self.config.BASE_URL}/api/v5/dex/ranking/volume"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()
    
    async def get_defi_tokens(self) -> Dict[str, Any]:
        """Get DeFi tokens"""
        url = f"{self.config.BASE_URL}/api/v5/defi/token"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()

# API Endpoints
@app.get("/tigerex/okx/balance")
async def get_balance(
    ccy: Optional[str] = Query(None, description="Currency"),
    credentials: str = Depends(security)
):
    """Get account balance - TigerEx OKX Integration"""
    async with TigerExOKXService() as service:
        return await service.get_balance(ccy)

@app.post("/tigerex/okx/order")
async def place_order(order: OKXOrder, credentials: str = Depends(security)):
    """Place order - TigerEx OKX Integration"""
    async with TigerExOKXService() as service:
        return await service.place_order(order)

@app.get("/tigerex/okx/instruments")
async def get_instruments(
    inst_type: InstType = Query(..., description="Instrument type"),
    uly: Optional[str] = Query(None, description="Underlying"),
    inst_id: Optional[str] = Query(None, description="Instrument ID"),
    credentials: str = Depends(security)
):
    """Get instruments info - TigerEx OKX Integration"""
    async with TigerExOKXService() as service:
        return await service.get_instruments(inst_type, uly, inst_id)

@app.get("/tigerex/okx/ticker")
async def get_ticker(
    inst_type: InstType = Query(..., description="Instrument type"),
    inst_id: Optional[str] = Query(None, description="Instrument ID"),
    credentials: str = Depends(security)
):
    """Get ticker - TigerEx OKX Integration"""
    async with TigerExOKXService() as service:
        return await service.get_ticker(inst_type, inst_id)

@app.get("/tigerex/okx/orderbook")
async def get_orderbook(
    inst_id: str = Query(..., description="Instrument ID"),
    sz: int = Query(1, description="Size"),
    credentials: str = Depends(security)
):
    """Get orderbook - TigerEx OKX Integration"""
    async with TigerExOKXService() as service:
        return await service.get_orderbook(inst_id, sz)

@app.get("/tigerex/okx/trades")
async def get_trades(
    inst_id: str = Query(..., description="Instrument ID"),
    limit: int = Query(100, description="Limit"),
    credentials: str = Depends(security)
):
    """Get recent trades - TigerEx OKX Integration"""
    async with TigerExOKXService() as service:
        return await service.get_trades(inst_id, limit)

@app.get("/tigerex/okx/candles")
async def get_candlesticks(
    inst_id: str = Query(..., description="Instrument ID"),
    bar: str = Query("1m", description="Time bar"),
    after: Optional[str] = Query(None, description="After"),
    before: Optional[str] = Query(None, description="Before"),
    limit: str = Query("100", description="Limit"),
    credentials: str = Depends(security)
):
    """Get candlesticks - TigerEx OKX Integration"""
    async with TigerExOKXService() as service:
        return await service.get_candlesticks(inst_id, bar, after, before, limit)

@app.get("/tigerex/okx/orders/pending")
async def get_pending_orders(
    inst_type: Optional[InstType] = Query(None, description="Instrument type"),
    inst_id: Optional[str] = Query(None, description="Instrument ID"),
    credentials: str = Depends(security)
):
    """Get pending orders - TigerEx OKX Integration"""
    async with TigerExOKXService() as service:
        return await service.get_pending_orders(inst_type, inst_id)

@app.get("/tigerex/okx/orders/history")
async def get_order_history(
    inst_type: Optional[InstType] = Query(None, description="Instrument type"),
    inst_id: Optional[str] = Query(None, description="Instrument ID"),
    credentials: str = Depends(security)
):
    """Get order history - TigerEx OKX Integration"""
    async with TigerExOKXService() as service:
        return await service.get_order_history(inst_type, inst_id)

@app.get("/tigerex/okx/earn/products")
async def get_earn_products(
    product_type: str = Query("SAVINGS", description="Product type"),
    credentials: str = Depends(security)
):
    """Get earn products - TigerEx OKX Integration"""
    async with TigerExOKXService() as service:
        return await service.get_earn_products(product_type)

@app.get("/tigerex/okx/staking")
async def get_staking_products(credentials: str = Depends(security)):
    """Get staking products - TigerEx OKX Integration"""
    async with TigerExOKXService() as service:
        return await service.get_staking_products()

@app.get("/tigerex/okx/jumpstart")
async def get_jumpstart_projects(credentials: str = Depends(security)):
    """Get jumpstart projects - TigerEx OKX Integration"""
    async with TigerExOKXService() as service:
        return await service.get_jumpstart_projects()

@app.get("/tigerex/okx/nft/collections")
async def get_nft_collections(credentials: str = Depends(security)):
    """Get NFT collections - TigerEx OKX Integration"""
    async with TigerExOKXService() as service:
        return await service.get_nft_collections()

@app.get("/tigerex/okx/copytrading/leaders")
async def get_copy_trading_leaders(credentials: str = Depends(security)):
    """Get copy trading leaders - TigerEx OKX Integration"""
    async with TigerExOKXService() as service:
        return await service.get_copy_trading_leaders()

@app.get("/tigerex/okx/dex/volumes")
async def get_dex_volumes(credentials: str = Depends(security)):
    """Get DEX volumes - TigerEx OKX Integration"""
    async with TigerExOKXService() as service:
        return await service.get_dex_volumes()

@app.get("/tigerex/okx/defi/tokens")
async def get_defi_tokens(credentials: str = Depends(security)):
    """Get DeFi tokens - TigerEx OKX Integration"""
    async with TigerExOKXService() as service:
        return await service.get_defi_tokens()

@app.get("/tigerex/okx/features")
async def get_available_features():
    """Get available TigerEx OKX features"""
    return {
        "service": "TigerEx OKX Advanced Service",
        "version": "1.0.0",
        "features": [feature.value for feature in OKXFeature],
        "supported_instruments": [inst.value for inst in InstType],
        "supported_trade_modes": [mode.value for mode in TradeMode],
        "supported_order_types": [ot.value for ot in OrderType],
        "tigerex_integrated": True
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "TigerEx OKX Advanced Service",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)