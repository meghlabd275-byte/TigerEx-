"""
Gemini Advanced Service - Complete Gemini Integration
All unique Gemini features including regulated trading, custody, auctions, etc.
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

app = FastAPI(title="Gemini Advanced Service v1.0.0", version="1.0.0")
security = HTTPBearer()

class GeminiFeature(str, Enum):
    REGULATED_TRADING = "regulated_trading"
    CUSTODY_SERVICE = "custody_service"
    AUCTIONS = "auctions"
    INSTITUTIONAL = "institutional_services"
    WALLET_MANAGEMENT = "wallet_management"
    RECURRING_BUYS = "recurring_buys"
    INTEREST_EARNING = "interest_earning"
    STAKING = "staking"

class GeminiConfig:
    API_KEY = os.getenv("GEMINI_API_KEY")
    API_SECRET = os.getenv("GEMINI_SECRET")
    BASE_URL = "https://api.gemini.com"
    SANDBOX_URL = "https://api.sandbox.gemini.com"

    @staticmethod
    def get_signature(payload: str) -> str:
        """Generate Gemini API signature"""
        return hmac.new(
            GeminiConfig.API_SECRET.encode(),
            payload.encode(),
            hashlib.sha384
        ).hexdigest()

    @staticmethod
    def get_headers(payload: Dict) -> Dict:
        """Get authentication headers"""
        payload_json = json.dumps(payload)
        signature = GeminiConfig.get_signature(payload_json)
        
        return {
            "Content-Type": "text/plain",
            "X-GEMINI-APIKEY": GeminiConfig.API_KEY,
            "X-GEMINI-PAYLOAD": base64.b64encode(payload_json.encode()).decode(),
            "X-GEMINI-SIGNATURE": signature
        }

class TradingPair(BaseModel):
    symbol: str
    base_currency: str
    quote_currency: str
    symbol_status: str
    min_order_size: str
    price_precision: int
    quote_increment: str

class OrderRequest(BaseModel):
    symbol: str
    amount: str
    price: Optional[str] = None
    side: str  # buy/sell
    type: str  # exchange limit/market/stop_limit/stop_market
    options: Optional[List[str]] = None

class AuctionRequest(BaseModel):
    symbol: str
    amount: str
    price: str
    side: str  # buy/sell
    client_order_id: Optional[str] = None

class RecurringBuyRequest(BaseModel):
    symbol: str
    amount: str
    period: str  # daily/weekly/monthly
    next_run_timestamp: int

@app.get("/")
async def root():
    return {
        "service": "Gemini Advanced Service",
        "features": [feature.value for feature in GeminiFeature],
        "status": "operational"
    }

@app.get("/trading/symbols")
async def get_trading_symbols():
    """Get all available trading symbols"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{GeminiConfig.BASE_URL}/v1/symbols") as response:
                symbols = await response.json()
                
                pairs = []
                for symbol in symbols[:100]:  # Limit to first 100 for performance
                    try:
                        async with session.get(f"{GeminiConfig.BASE_URL}/v1/symbols/details/{symbol}") as response:
                            details = await response.json()
                            
                            pairs.append(TradingPair(
                                symbol=details["symbol"],
                                base_currency=details["base_currency"],
                                quote_currency=details["quote_currency"],
                                symbol_status=details["symbol_status"],
                                min_order_size=details["min_order_size"],
                                price_precision=details["price_precision"],
                                quote_increment=details["quote_increment"]
                            ))
                    except:
                        continue
                
                return {"symbols": pairs}
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trading/ticker/{symbol}")
async def get_ticker(symbol: str):
    """Get ticker information for a symbol"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{GeminiConfig.BASE_URL}/v1/pubticker/{symbol}") as response:
                data = await response.json()
                
                return {
                    "symbol": symbol,
                    "bid": data.get("bid"),
                    "ask": data.get("ask"),
                    "last": data.get("last"),
                    "volume": data.get("volume", {}).get("symbol"),
                    "change": data.get("change"),
                    "timestamp": datetime.fromtimestamp(data["timestamp"] / 1000) if "timestamp" in data else None
                }
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trading/orderbook/{symbol}")
async def get_orderbook(symbol: str, limit_bids: int = 50, limit_asks: int = 50):
    """Get order book for a symbol"""
    try:
        params = {
            "limit_bids": str(limit_bids),
            "limit_asks": str(limit_asks)
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{GeminiConfig.BASE_URL}/v1/book/{symbol}", params=params) as response:
                data = await response.json()
                
                return {
                    "symbol": symbol,
                    "bids": data.get("bids", []),
                    "asks": data.get("asks", []),
                    "timestamp": datetime.utcnow()
                }
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trading/order")
async def place_order(order: OrderRequest):
    """Place trading order"""
    try:
        payload = {
            "request": "/v1/order/new",
            "nonce": int(time.time() * 1000),
            "symbol": order.symbol,
            "amount": order.amount,
            "side": order.side,
            "type": order.type.replace(" ", "_")
        }
        
        if order.price:
            payload["price"] = order.price
        
        if order.options:
            payload["options"] = order.options
        
        headers = GeminiConfig.get_headers(payload)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{GeminiConfig.BASE_URL}/v1/order/new", headers=headers, data=json.dumps(payload)) as response:
                return await response.json()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auction/{symbol}")
async def get_auction_info(symbol: str):
    """Get auction information for a symbol"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{GeminiConfig.BASE_URL}/v1/auction/{symbol}") as response:
                data = await response.json()
                
                return {
                    "symbol": symbol,
                    "auction_id": data.get("auction_id"),
                    "highest_bid": data.get("highest_bid"),
                    "lowest_ask": data.get("lowest_ask"),
                    "collar": data.get("collar"),
                    "last_auction_price": data.get("last_auction_price"),
                    "last_auction_time": data.get("last_auction_time"),
                    "next_auction_time": data.get("next_auction_time")
                }
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auction/order")
async def place_auction_order(order: AuctionRequest):
    """Place auction order"""
    try:
        payload = {
            "request": "/v1/auction/place",
            "nonce": int(time.time() * 1000),
            "symbol": order.symbol,
            "amount": order.amount,
            "price": order.price,
            "side": order.side
        }
        
        if order.client_order_id:
            payload["client_order_id"] = order.client_order_id
        
        headers = GeminiConfig.get_headers(payload)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{GeminiConfig.BASE_URL}/v1/auction/place", headers=headers, data=json.dumps(payload)) as response:
                return await response.json()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/custody/balances")
async def get_custody_balances():
    """Get custody account balances"""
    try:
        payload = {
            "request": "/v1/custody/account/balances",
            "nonce": int(time.time() * 1000)
        }
        
        headers = GeminiConfig.get_headers(payload)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{GeminiConfig.BASE_URL}/v1/custody/account/balances", headers=headers, data=json.dumps(payload)) as response:
                return await response.json()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/custody/withdraw")
async def custody_withdrawal(currency: str, amount: str, address: str):
    """Initiate custody withdrawal"""
    try:
        payload = {
            "request": "/v1/custody/withdraw/withdrawalRequest",
            "nonce": int(time.time() * 1000),
            "currency": currency,
            "amount": amount,
            "address": address
        }
        
        headers = GeminiConfig.get_headers(payload)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{GeminiConfig.BASE_URL}/v1/custody/withdraw/withdrawalRequest", headers=headers, data=json.dumps(payload)) as response:
                return await response.json()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recurring-buys")
async def get_recurring_buys():
    """Get recurring buy orders"""
    try:
        payload = {
            "request": "/v1/recurringbuys",
            "nonce": int(time.time() * 1000)
        }
        
        headers = GeminiConfig.get_headers(payload)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{GeminiConfig.BASE_URL}/v1/recurringbuys", headers=headers, data=json.dumps(payload)) as response:
                return await response.json()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recurring-buys")
async def create_recurring_buy(recurring: RecurringBuyRequest):
    """Create recurring buy order"""
    try:
        payload = {
            "request": "/v1/recurringbuys/new",
            "nonce": int(time.time() * 1000),
            "symbol": recurring.symbol,
            "amount": recurring.amount,
            "period": recurring.period,
            "next_run_timestamp": recurring.next_run_timestamp
        }
        
        headers = GeminiConfig.get_headers(payload)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{GeminiConfig.BASE_URL}/v1/recurringbuys/new", headers=headers, data=json.dumps(payload)) as response:
                return await response.json()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/interest/earn/balance")
async def get_interest_earn_balance():
    """Get interest earning balance"""
    try:
        payload = {
            "request": "/v1/interest/balance",
            "nonce": int(time.time() * 1000)
        }
        
        headers = GeminiConfig.get_headers(payload)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{GeminiConfig.BASE_URL}/v1/interest/balance", headers=headers, data=json.dumps(payload)) as response:
                return await response.json()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/account/balances")
async def get_account_balances():
    """Get account balances"""
    try:
        payload = {
            "request": "/v1/balances",
            "nonce": int(time.time() * 1000)
        }
        
        headers = GeminiConfig.get_headers(payload)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{GeminiConfig.BASE_URL}/v1/balances", headers=headers, data=json.dumps(payload)) as response:
                return await response.json()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/account/volume")
async def get_trading_volume():
    """Get account trading volume"""
    try:
        payload = {
            "request": "/v1/mytrades",
            "nonce": int(time.time() * 1000)
        }
        
        headers = GeminiConfig.get_headers(payload)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{GeminiConfig.BASE_URL}/v1/mytrades", headers=headers, data=json.dumps(payload)) as response:
                return await response.json()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market/trades/{symbol}")
async def get_recent_trades(symbol: str, limit: int = 500):
    """Get recent trades for a symbol"""
    try:
        params = {"limit": str(limit)} if limit != 500 else {}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{GeminiConfig.BASE_URL}/v1/trades/{symbol}", params=params) as response:
                data = await response.json()
                
                trades = []
                for trade in data:
                    trades.append({
                        "timestamp": trade["timestamp"],
                        "price": trade["price"],
                        "amount": trade["amount"],
                        "exchange": trade["exchange"],
                        "type": trade["type"]
                    })
                
                return {
                    "symbol": symbol,
                    "trades": trades
                }
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market/candles/{symbol}")
async def get_candles(symbol: str, time_frame: str = "1day"):
    """Get candlestick data"""
    try:
        params = {"time_frame": time_frame}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{GeminiConfig.BASE_URL}/v2/candles/{symbol}", params=params) as response:
                data = await response.json()
                
                # Gemini returns [timestamp, open, high, low, close, volume]
                candles = []
                for candle in data:
                    candles.append({
                        "timestamp": candle[0],
                        "open": candle[1],
                        "high": candle[2],
                        "low": candle[3],
                        "close": candle[4],
                        "volume": candle[5]
                    })
                
                return {
                    "symbol": symbol,
                    "time_frame": time_frame,
                    "candles": candles
                }
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import time
    import os
    uvicorn.run(app, host="0.0.0.0", port=8003)