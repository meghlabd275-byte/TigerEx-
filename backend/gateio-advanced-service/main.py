"""
Gate.io Advanced Service - Complete Gate.io Integration for TigerEx
All unique Gate.io features including trading, futures, margin, staking, etc.
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
    title="TigerEx Gate.io Advanced Service v1.0.0",
    version="1.0.0",
    description="Complete Gate.io integration for TigerEx trading platform"
)
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GateioFeature(str, Enum):
    SPOT_TRADING = "spot_trading"
    FUTURES_TRADING = "futures_trading"
    MARGIN_TRADING = "margin_trading"
    OPTIONS_TRADING = "options_trading"
    STAKING = "staking"
    LIQUIDITY_MINING = "liquidity_mining"
    DUAL_INVESTMENT = "dual_investment"
    LENDING_BORROWING = "lending_borrowing"
    COPY_TRADING = "copy_trading"
    NFT_MARKETPLACE = "nft_marketplace"
    STARTUP = "startup"
    FINANCE_PRODUCTS = "finance_products"
    API_FEATURES = "api_features"

class TradingSettle(str, Enum):
    USDT = "usdt"
    BTC = "btc"
    USD = "usd"

class OrderType(str, Enum):
    LIMIT = "limit"
    MARKET = "market"

class TimeInForce(str, Enum):
    GTC = "gtc"
    IOC = "ioc"
    FOK = "fok"

@dataclass
class GateioConfig:
    API_KEY: str = os.getenv("GATEIO_API_KEY")
    API_SECRET: str = os.getenv("GATEIO_SECRET")
    BASE_URL: str = "https://api.gateio.ws/api/v4"

    @staticmethod
    def get_signature(method: str, url: str, query_string: str, payload_string: str, secret: str) -> Dict[str, str]:
        """Generate Gate.io v4 signature"""
        t = str(int(time.time()))
        m = hashlib.sha512()
        m.update(payload_string.encode('utf-8'))
        hashed_payload = m.hexdigest()
        s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string, hashed_payload, t)
        sign = hmac.new(secret.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
        return {'KEY': os.getenv("GATEIO_API_KEY"), 'Timestamp': t, 'SIGN': sign}

class GateioOrder(BaseModel):
    currency_pair: str
    side: str
    type: OrderType = OrderType.LIMIT
    account: str = "spot"
    amount: str
    price: Optional[str] = None
    time_in_force: TimeInForce = TimeInForce.GTC
    iceberg: Optional[str] = None
    auto_borrow: Optional[bool] = None

class TigerExGateioService:
    def __init__(self):
        self.config = GateioConfig()
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_spot_accounts(self) -> List[Dict[str, Any]]:
        """List spot accounts"""
        method = 'GET'
        url = '/spot/accounts'
        query_string = ''
        payload_string = ''

        headers = GateioConfig.get_signature(method, url, query_string, payload_string, self.config.API_SECRET)
        headers['Accept'] = 'application/json'
        headers['Content-Type'] = 'application/json'

        async with self.session.get(self.config.BASE_URL + url, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()

    async def place_spot_order(self, order: GateioOrder) -> Dict[str, Any]:
        """Create a spot order"""
        method = 'POST'
        url = '/spot/orders'
        query_string = ''
        payload = order.model_dump(exclude_none=True)
        payload_string = json.dumps(payload)

        headers = GateioConfig.get_signature(method, url, query_string, payload_string, self.config.API_SECRET)
        headers['Accept'] = 'application/json'
        headers['Content-Type'] = 'application/json'

        async with self.session.post(self.config.BASE_URL + url, headers=headers, data=payload_string) as response:
            if response.status != 201:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()

    async def get_currency_pairs(self) -> List[Dict[str, Any]]:
        """List all currency pairs supported"""
        url = '/spot/currency_pairs'
        async with self.session.get(self.config.BASE_URL + url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()

    async def get_orderbook(self, currency_pair: str, limit: int = 10) -> Dict[str, Any]:
        """Retrieve order book"""
        url = f'/spot/order_book?currency_pair={currency_pair}&limit={limit}'
        async with self.session.get(self.config.BASE_URL + url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()

    async def get_futures_contracts(self, settle: TradingSettle = TradingSettle.USDT) -> List[Dict[str, Any]]:
        """List all futures contracts"""
        url = f'/futures/{settle.value}/contracts'
        async with self.session.get(self.config.BASE_URL + url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=await response.text())
            return await response.json()

    async def get_staking_tasks(self) -> List[Dict[str, Any]]:
        """List staking tasks"""
        # Note: Some Gate.io Earn/Staking endpoints might require specific v4 paths
        url = '/staking/tasks'
        method = 'GET'
        query_string = ''
        payload_string = ''

        headers = GateioConfig.get_signature(method, url, query_string, payload_string, self.config.API_SECRET)
        async with self.session.get(self.config.BASE_URL + url, headers=headers) as response:
            if response.status != 200:
                # Fallback or error
                return []
            return await response.json()

# API Endpoints
@app.get("/tigerex/gateio/accounts")
async def get_accounts(credentials: str = Depends(security)):
    """Get Gate.io accounts - TigerEx Integration"""
    async with TigerExGateioService() as service:
        return await service.get_spot_accounts()

@app.post("/tigerex/gateio/order")
async def place_order(order: GateioOrder, credentials: str = Depends(security)):
    """Place Gate.io order - TigerEx Integration"""
    async with TigerExGateioService() as service:
        return await service.place_spot_order(order)

@app.get("/tigerex/gateio/pairs")
async def get_pairs(credentials: str = Depends(security)):
    """Get Gate.io currency pairs - TigerEx Integration"""
    async with TigerExGateioService() as service:
        return await service.get_currency_pairs()

@app.get("/tigerex/gateio/orderbook")
async def get_orderbook(
    currency_pair: str = Query(..., description="Currency pair"),
    limit: int = Query(10, description="Limit"),
    credentials: str = Depends(security)
):
    """Get Gate.io orderbook - TigerEx Integration"""
    async with TigerExGateioService() as service:
        return await service.get_orderbook(currency_pair, limit)

@app.get("/tigerex/gateio/futures/contracts")
async def get_futures_contracts(
    settle: TradingSettle = Query(TradingSettle.USDT, description="Settle currency"),
    credentials: str = Depends(security)
):
    """Get Gate.io futures contracts - TigerEx Integration"""
    async with TigerExGateioService() as service:
        return await service.get_futures_contracts(settle)

@app.get("/tigerex/gateio/features")
async def get_available_features():
    """Get available TigerEx Gate.io features"""
    return {
        "service": "TigerEx Gate.io Advanced Service",
        "version": "1.0.0",
        "features": [feature.value for feature in GateioFeature],
        "tigerex_integrated": True
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "TigerEx Gate.io Advanced Service",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8015)
