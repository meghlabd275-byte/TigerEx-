"""
Bitfinex Advanced Service - Complete Bitfinex Integration
All unique Bitfinex features including advanced trading, derivatives, funding, etc.
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

app = FastAPI(title="Bitfinex Advanced Service v1.0.0", version="1.0.0")
security = HTTPBearer()

class BitfinexFeature(str, Enum):
    SPOT_TRADING = "spot_trading"
    MARGIN_TRADING = "margin_trading"
    DERIVATIVES = "derivatives"
    FUNDING = "funding"
    STAKING = "staking"
    LENDING = "lending"
    OTC_DESK = "otc_desk"
    ORDER_TYPES = "advanced_order_types"

class BitfinexConfig:
    API_KEY = os.getenv("BITFINEX_API_KEY")
    API_SECRET = os.getenv("BITFINEX_SECRET")
    BASE_URL = "https://api-pub.bitfinex.com/v2"
    AUTH_URL = "https://api.bitfinex.com/v2"

    @staticmethod
    def get_signature(path: str, body: str, nonce: int) -> str:
        """Generate Bitfinex API signature"""
        message = f"/api/v2{path}{nonce}{body}"
        signature = hmac.new(
            BitfinexConfig.API_SECRET.encode(),
            message.encode(),
            hashlib.sha384
        ).hexdigest()
        return signature

    @staticmethod
    def get_auth_headers(path: str, body: str = "") -> Dict:
        """Get authentication headers"""
        nonce = int(time.time() * 1000)
        signature = BitfinexConfig.get_signature(path, body, nonce)
        
        return {
            "bfx-apikey": BitfinexConfig.API_KEY,
            "bfx-signature": signature,
            "bfx-nonce": str(nonce),
            "Content-Type": "application/json"
        }

class TradingPair(BaseModel):
    symbol: str
    base_currency: str
    quote_currency: str
    price_precision: int
    initial_margin: str
    minimum_order_size: str

class OrderRequest(BaseModel):
    symbol: str
    amount: float
    price: Optional[float] = None
    side: str  # buy/sell
    type: str  # exchange/market/limit
    flags: Optional[List[int]] = None

class FundingRequest(BaseModel):
    currency: str
    amount: float
    rate: float
    period: int
    direction: str  # lend/borrow

@app.get("/")
async def root():
    return {
        "service": "Bitfinex Advanced Service",
        "features": [feature.value for feature in BitfinexFeature],
        "status": "operational"
    }

@app.get("/trading/pairs")
async def get_trading_pairs():
    """Get all available trading pairs"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BitfinexConfig.BASE_URL}/conf/pub:list:pair:exchange") as response:
                data = await response.json()
                
                pairs = []
                symbols = data[0]  # Bitfinex returns array in first element
                
                # Get detailed info for each pair
                for symbol in symbols[:100]:  # Limit to first 100 for performance
                    try:
                        async with session.get(f"{BitfinexConfig.BASE_URL}/conf/pub:info:pair:{symbol}") as response:
                            pair_info = await response.json()
                            if pair_info[0]:  # If data exists
                                info = pair_info[0][0]
                                pairs.append(TradingPair(
                                    symbol=symbol,
                                    base_currency=info[0],
                                    quote_currency=info[1],
                                    price_precision=info[2],
                                    initial_margin=info[3],
                                    minimum_order_size=info[4]
                                ))
                    except:
                        continue
                
                return {"pairs": pairs}
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trading/ticker/{symbol}")
async def get_ticker(symbol: str):
    """Get ticker information for a symbol"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BitfinexConfig.BASE_URL}/ticker/t{symbol}") as response:
                data = await response.json()
                
                if data:
                    return {
                        "symbol": symbol,
                        "bid": data[0],
                        "bid_size": data[1],
                        "ask": data[2],
                        "ask_size": data[3],
                        "daily_change": data[4],
                        "daily_change_perc": data[5],
                        "last_price": data[6],
                        "volume": data[7],
                        "high": data[8],
                        "low": data[9]
                    }
                else:
                    return {"symbol": symbol, "status": "no_data"}
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trading/orderbook/{symbol}")
async def get_orderbook(symbol: str, precision: str = "P0", len: int = 25):
    """Get order book for a symbol"""
    try:
        params = {"len": str(len)}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BitfinexConfig.BASE_URL}/book/{symbol}/{precision}", params=params) as response:
                data = await response.json()
                
                # Bitfinex returns [PRICE, COUNT, AMOUNT] format
                bids = []
                asks = []
                
                for item in data:
                    price, count, amount = item
                    if amount > 0:  # Bids
                        bids.append([price, abs(amount)])
                    else:  # Asks
                        asks.append([price, abs(amount)])
                
                return {
                    "symbol": symbol,
                    "bids": bids,
                    "asks": asks,
                    "timestamp": datetime.utcnow()
                }
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trading/order")
async def place_order(order: OrderRequest):
    """Place trading order"""
    try:
        path = "/auth/w/order/submit"
        url = BitfinexConfig.AUTH_URL + path
        
        payload = {
            "type": order.type,
            "symbol": f"t{order.symbol}",
            "amount": str(order.amount),
            "side": order.side[0].upper()  # Buy -> B, Sell -> S
        }
        
        if order.price:
            payload["price"] = str(order.price)
        
        if order.flags:
            payload["flags"] = order.flags
        
        body = json.dumps(payload)
        headers = BitfinexConfig.get_auth_headers(path, body)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=body, headers=headers) as response:
                return await response.json()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/derivatives/symbols")
async def get_derivatives_symbols():
    """Get derivatives trading symbols"""
    try:
        async with aiohttp.ClientSession() as session:
            # Get futures symbols
            async with session.get(f"{BitfinexConfig.BASE_URL}/conf/pub:list:pair:futures") as response:
                futures_data = await response.json()
                
            # Get perpetual swap symbols
            async with session.get(f"{BitfinexConfig.BASE_URL}/conf/pub:list:pair:perp") as response:
                perp_data = await response.json()
                
            return {
                "futures": futures_data[0] if futures_data else [],
                "perpetual_swaps": perp_data[0] if perp_data else []
            }
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/funding/currencies")
async def get_funding_currencies():
    """Get available funding currencies"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BitfinexConfig.BASE_URL}/conf/pub:list:currency") as response:
                data = await response.json()
                return {"currencies": data[0] if data else []}
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/funding/ticker/{currency}")
async def get_funding_ticker(currency: str):
    """Get funding ticker for a currency"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BitfinexConfig.BASE_URL}/f/stats/{currency}") as response:
                return await response.json()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/funding/offer")
async def create_funding_offer(funding: FundingRequest):
    """Create funding offer"""
    try:
        path = "/auth/w/funding/offer/submit"
        url = BitfinexConfig.AUTH_URL + path
        
        payload = {
            "type": "f",
            "symbol": f"f{funding.currency}",
            "amount": str(funding.amount),
            "rate": str(funding.rate),
            "period": funding.period
        }
        
        body = json.dumps(payload)
        headers = BitfinexConfig.get_auth_headers(path, body)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=body, headers=headers) as response:
                return await response.json()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/margin/info/{symbol}")
async def get_margin_info(symbol: str):
    """Get margin trading information"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BitfinexConfig.BASE_URL}/conf/pub:info:pair:{symbol}") as response:
                data = await response.json()
                
                if data and data[0]:
                    info = data[0][0]
                    return {
                        "symbol": symbol,
                        "initial_margin": info[3],
                        "max_leverage": 1 / float(info[3]) if info[3] != "0" else 1,
                        "minimum_order_size": info[4],
                        "trading_fees": info[5]
                    }
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/lending/products")
async def get_lending_products():
    """Get lending products"""
    try:
        path = "/auth/r/stats/funding/earn"
        url = BitfinexConfig.AUTH_URL + path
        headers = BitfinexConfig.get_auth_headers(path)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                return await response.json()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/account/wallet")
async def get_wallet_balance():
    """Get wallet balance"""
    try:
        path = "/auth/r/wallets"
        url = BitfinexConfig.AUTH_URL + path
        headers = BitfinexConfig.get_auth_headers(path)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                return await response.json()
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market/candles/{symbol}")
async def get_candles(symbol: str, timeframe: str = "1h", limit: int = 100):
    """Get candlestick data"""
    try:
        params = {"limit": str(limit)}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BitfinexConfig.BASE_URL}/candles/trade:{timeframe}:t{symbol}", params=params) as response:
                data = await response.json()
                
                # Bitfinex returns [MTS, OPEN, CLOSE, HIGH, LOW, VOLUME]
                candles = []
                for candle in data:
                    candles.append({
                        "timestamp": candle[0],
                        "open": candle[1],
                        "close": candle[2],
                        "high": candle[3],
                        "low": candle[4],
                        "volume": candle[5]
                    })
                
                return {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "candles": candles
                }
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/order/types")
async def get_order_types():
    """Get available order types and flags"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BitfinexConfig.BASE_URL}/conf/pub:map:order:flags") as response:
                data = await response.json()
                return {"order_flags": data[0] if data else []}
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import time
    import os
    uvicorn.run(app, host="0.0.0.0", port=8002)