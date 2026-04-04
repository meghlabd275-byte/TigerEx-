"""
KuCoin Advanced Service - Complete KuCoin Integration
All unique KuCoin features including trading, futures, margin, staking, etc.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import aiohttp
import hashlib
import hmac
import base64
import json
import logging

app = FastAPI(title="KuCoin Advanced Service v1.0.0", version="1.0.0")
security = HTTPBearer()

class KuCoinFeature(str, Enum):
    SPOT_TRADING = "spot_trading"
    FUTURES_TRADING = "futures_trading"
    MARGIN_TRADING = "margin_trading"
    STAKING = "staking"
    SAVINGS = "savings"
    BOT_TRADING = "bot_trading"
    POOL_X = "pool_x"
    LENDING = "lending"
    COPY_TRADING = "copy_trading"

class KuCoinConfig:
    API_KEY = os.getenv("KUCOIN_API_KEY")
    API_SECRET = os.getenv("KUCOIN_SECRET")
    API_PASSPHRASE = os.getenv("KUCOIN_PASSPHRASE")
    BASE_URL = "https://api.kucoin.com"
    FUTURES_URL = "https://api-futures.kucoin.com"

    @staticmethod
    def get_headers(endpoint: str, method: str, body: str = "") -> Dict:
        timestamp = str(int(time.time() * 1000))
        message = timestamp + method + endpoint + body
        signature = base64.b64encode(
            hmac.new(KuCoinConfig.API_SECRET.encode(), message.encode(), hashlib.sha256).digest()
        )
        
        return {
            "KC-API-KEY": KuCoinConfig.API_KEY,
            "KC-API-SIGN": signature.decode(),
            "KC-API-TIMESTAMP": timestamp,
            "KC-API-PASSPHRASE": KuCoinConfig.API_PASSPHRASE,
            "KC-API-KEY-VERSION": "2",
            "Content-Type": "application/json"
        }

class TradingPair(BaseModel):
    symbol: str
    base_currency: str
    quote_currency: str
    price: float
    volume_24h: float
    change_24h: float

class OrderRequest(BaseModel):
    symbol: str
    side: str  # buy/sell
    type: str   # market/limit
    size: float
    price: Optional[float] = None
    time_in_force: str = "GTC"

class FuturesOrderRequest(BaseModel):
    symbol: str
    side: str
    type: str
    leverage: int
    size: float
    price: Optional[float] = None

class StakingProduct(BaseModel):
    product_id: str
    currency: str
    apy: float
    duration: int
    min_amount: float
    status: str

class LendingProduct(BaseModel):
    product_id: str
    currency: str
    daily_rate: float
    term: int
    min_amount: float

@app.get("/")
async def root():
    return {
        "service": "KuCoin Advanced Service",
        "features": [feature.value for feature in KuCoinFeature],
        "status": "operational"
    }

@app.get("/trading/pairs")
async def get_trading_pairs():
    """Get all available trading pairs"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{KuCoinConfig.BASE_URL}/api/v1/symbols") as response:
                data = await response.json()
                
                pairs = []
                for symbol_data in data["data"]:
                    pairs.append(TradingPair(
                        symbol=symbol_data["symbol"],
                        base_currency=symbol_data["baseCurrency"],
                        quote_currency=symbol_data["quoteCurrency"],
                        price=float(symbol_data.get("price", 0)),
                        volume_24h=float(symbol_data.get("quoteVolume", 0)),
                        change_24h=float(symbol_data.get("changeRate", 0)) * 100
                    ))
                
                return {"pairs": pairs}
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trading/order")
async def place_order(order: OrderRequest):
    """Place spot trading order"""
    try:
        endpoint = "/api/v1/orders"
        url = KuCoinConfig.BASE_URL + endpoint
        
        payload = {
            "clientOid": str(uuid.uuid4()),
            "side": order.side,
            "symbol": order.symbol,
            "type": order.type,
            "size": str(order.size),
            "timeInForce": order.time_in_force
        }
        
        if order.price:
            payload["price"] = str(order.price)
        
        body = json.dumps(payload)
        headers = KuCoinConfig.get_headers(endpoint, "POST", body)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=body, headers=headers) as response:
                return await response.json()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/futures/contracts")
async def get_futures_contracts():
    """Get all futures contracts"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{KuCoinConfig.FUTURES_URL}/api/v1/contracts/active") as response:
                data = await response.json()
                return {"contracts": data["data"]}
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/futures/order")
async def place_futures_order(order: FuturesOrderRequest):
    """Place futures order"""
    try:
        endpoint = "/api/v1/orders"
        url = KuCoinConfig.FUTURES_URL + endpoint
        
        payload = {
            "clientOid": str(uuid.uuid4()),
            "side": order.side,
            "symbol": order.symbol,
            "type": order.type,
            "leverage": str(order.leverage),
            "size": str(order.size)
        }
        
        if order.price:
            payload["price"] = str(order.price)
        
        body = json.dumps(payload)
        headers = KuCoinConfig.get_headers(endpoint, "POST", body)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=body, headers=headers) as response:
                return await response.json()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/margin/market")
async def get_margin_market():
    """Get margin trading market data"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{KuCoinConfig.BASE_URL}/api/v1/margin/market") as response:
                data = await response.json()
                return {"margin_pairs": data["data"]}
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/staking/products")
async def get_staking_products():
    """Get staking products"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{KuCoinConfig.BASE_URL}/api/v1/staking/products") as response:
                data = await response.json()
                
                products = []
                for item in data["data"]:
                    products.append(StakingProduct(
                        product_id=item["productId"],
                        currency=item["currency"],
                        apy=float(item["annualizedRate"]),
                        duration=int(item["duration"]),
                        min_amount=float(item["minAmount"]),
                        status=item["status"]
                    ))
                
                return {"products": products}
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/staking/subscribe")
async def subscribe_staking(product_id: str, amount: float):
    """Subscribe to staking product"""
    try:
        endpoint = "/api/v1/staking/subscribe"
        url = KuCoinConfig.BASE_URL + endpoint
        
        payload = {
            "productId": product_id,
            "amount": str(amount)
        }
        
        body = json.dumps(payload)
        headers = KuCoinConfig.get_headers(endpoint, "POST", body)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=body, headers=headers) as response:
                return await response.json()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/lending/products")
async def get_lending_products():
    """Get lending products"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{KuCoinConfig.BASE_URL}/api/v1/lending/products") as response:
                data = await response.json()
                
                products = []
                for item in data["data"]:
                    products.append(LendingProduct(
                        product_id=item["productId"],
                        currency=item["currency"],
                        daily_rate=float(item["dailyInterestRate"]),
                        term=int(item["term"]),
                        min_amount=float(item["minAmount"])
                    ))
                
                return {"products": products}
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bot-trading/strategies")
async def get_trading_bots():
    """Get available trading bot strategies"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{KuCoinConfig.BASE_URL}/api/v1/bots/strategies") as response:
                return await response.json()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pool-x/products")
async def get_pool_x_products():
    """Get Pool-X products"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{KuCoinConfig.BASE_URL}/api/v1/pool-x/products") as response:
                return await response.json()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/account/info")
async def get_account_info():
    """Get account information"""
    try:
        endpoint = "/api/v1/accounts"
        url = KuCoinConfig.BASE_URL + endpoint
        headers = KuCoinConfig.get_headers(endpoint, "GET")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                return await response.json()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market/ticker/{symbol}")
async def get_ticker(symbol: str):
    """Get ticker information for a symbol"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{KuCoinConfig.BASE_URL}/api/v1/market/orderbook/level1?symbol={symbol}") as response:
                return await response.json()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market/klines/{symbol}")
async def get_klines(symbol: str, interval: str = "1hour", start_at: Optional[int] = None, end_at: Optional[int] = None):
    """Get kline/candlestick data"""
    try:
        params = {"symbol": symbol, "type": interval}
        if start_at:
            params["startAt"] = start_at
        if end_at:
            params["endAt"] = end_at
            
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{KuCoinConfig.BASE_URL}/api/v1/market/candles", params=params) as response:
                return await response.json()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import time
    import uuid
    import os
    uvicorn.run(app, host="0.0.0.0", port=8001)