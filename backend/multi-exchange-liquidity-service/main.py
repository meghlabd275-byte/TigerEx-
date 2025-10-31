"""
Multi-Exchange Liquidity Aggregation Service
Integrates with major exchanges: Binance, OKX, Huobi, Kraken, Gemini, Coinbase, KuCoin, Bitfinex, Bybit
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import aiohttp
import asyncio
import hashlib
import hmac
import base64
import json
import logging

app = FastAPI(title="Multi-Exchange Liquidity Service", version="1.0.0")
security = HTTPBearer()

class Exchange(str, Enum):
    BINANCE = "binance"
    OKX = "okx"
    HUOBI = "huobi"
    KRAKEN = "kraken"
    GEMINI = "gemini"
    COINBASE = "coinbase"
    KUCOIN = "kucoin"
    BITFINEX = "bitfinex"
    BYBIT = "bybit"

class OrderBook(BaseModel):
    exchange: Exchange
    symbol: str
    bids: List[List[float]]
    asks: List[List[float]]
    timestamp: datetime

class LiquidityRequest(BaseModel):
    symbol: str
    side: str  # buy/sell
    amount: float
    exchanges: Optional[List[Exchange]] = None

class LiquidityResponse(BaseModel):
    best_price: float
    total_liquidity: float
    exchanges: Dict[str, Dict[str, Any]]
    routing: List[Dict[str, Any]]

class ExchangeConnector:
    def __init__(self):
        self.api_keys = {
            "binance": {"api_key": os.getenv("BINANCE_API_KEY"), "secret": os.getenv("BINANCE_SECRET")},
            "okx": {"api_key": os.getenv("OKX_API_KEY"), "secret": os.getenv("OKX_SECRET")},
            "huobi": {"api_key": os.getenv("HUOBI_API_KEY"), "secret": os.getenv("HUOBI_SECRET")},
            "kraken": {"api_key": os.getenv("KRAKEN_API_KEY"), "secret": os.getenv("KRAKEN_SECRET")},
            "gemini": {"api_key": os.getenv("GEMINI_API_KEY"), "secret": os.getenv("GEMINI_SECRET")},
            "coinbase": {"api_key": os.getenv("COINBASE_API_KEY"), "secret": os.getenv("COINBASE_SECRET")},
            "kucoin": {"api_key": os.getenv("KUCOIN_API_KEY"), "secret": os.getenv("KUCOIN_SECRET")},
            "bitfinex": {"api_key": os.getenv("BITFINEX_API_KEY"), "secret": os.getenv("BITFINEX_SECRET")},
            "bybit": {"api_key": os.getenv("BYBIT_API_KEY"), "secret": os.getenv("BYBIT_SECRET")},
        }

    async def get_binance_orderbook(self, symbol: str) -> Dict:
        """Get Binance order book"""
        url = f"https://api.binance.com/api/v3/depth"
        params = {"symbol": symbol.upper(), "limit": 100}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                return await response.json()

    async def get_okx_orderbook(self, symbol: str) -> Dict:
        """Get OKX order book"""
        url = "https://www.okx.com/api/v5/market/books"
        params = {"instId": symbol.replace("/", "-").upper(), "sz": 100}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                return {
                    "bids": [[float(bid[0]), float(bid[1])] for bid in data["data"][0]["bids"][:50]],
                    "asks": [[float(ask[0]), float(ask[1])] for ask in data["data"][0]["asks"][:50]]
                }

    async def get_huobi_orderbook(self, symbol: str) -> Dict:
        """Get Huobi order book"""
        url = "https://api.huobi.pro/market/depth"
        params = {"symbol": symbol.replace("/", "").lower(), "type": "step0"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                return await response.json()

    async def get_kraken_orderbook(self, symbol: str) -> Dict:
        """Get Kraken order book"""
        url = "https://api.kraken.com/0/public/Depth"
        params = {"pair": symbol.replace("/", ""), "count": 100}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                pair = list(data["result"].keys())[0]
                return data["result"][pair]

    async def get_gemini_orderbook(self, symbol: str) -> Dict:
        """Get Gemini order book"""
        url = f"https://api.gemini.com/v1/book/{symbol.lower()}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()

    async def get_coinbase_orderbook(self, symbol: str) -> Dict:
        """Get Coinbase order book"""
        url = f"https://api.pro.coinbase.com/products/{symbol.replace('/', '-')}/book?level=2"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()

    async def get_kucoin_orderbook(self, symbol: str) -> Dict:
        """Get KuCoin order book"""
        # First get token for public endpoints
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.kucoin.com/api/v1/bullet-public") as response:
                token_data = await response.json()
                token = token_data["data"]["token"]
        
        url = "https://api.kucoin.com/api/v1/market/orderbook/level2_100"
        params = {"symbol": symbol.replace("-", "").upper()}
        headers = {"KC-API-KEY": self.api_keys["kucoin"]["api_key"], "KC-API-PASSPHRASE": self.api_keys["kucoin"]["passphrase"]}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                return await response.json()

    async def get_bitfinex_orderbook(self, symbol: str) -> Dict:
        """Get Bitfinex order book"""
        url = f"https://api.bitfinex.com/v1/book/{symbol.replace('/', '')}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()

    async def get_bybit_orderbook(self, symbol: str) -> Dict:
        """Get Bybit order book"""
        url = "https://api.bybit.com/v2/public/orderBook/L2"
        params = {"symbol": symbol.replace("/", ""), "limit": 100}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                return await response.json()

connector = ExchangeConnector()

@app.get("/")
async def root():
    return {"service": "Multi-Exchange Liquidity Service", "status": "operational"}

@app.get("/exchanges")
async def get_supported_exchanges():
    return {"exchanges": [exchange.value for exchange in Exchange]}

@app.get("/orderbook/{exchange}/{symbol}")
async def get_orderbook(exchange: Exchange, symbol: str):
    """Get order book from specific exchange"""
    try:
        if exchange == Exchange.BINANCE:
            data = await connector.get_binance_orderbook(symbol)
        elif exchange == Exchange.OKX:
            data = await connector.get_okx_orderbook(symbol)
        elif exchange == Exchange.HUOBI:
            data = await connector.get_huobi_orderbook(symbol)
        elif exchange == Exchange.KRAKEN:
            data = await connector.get_kraken_orderbook(symbol)
        elif exchange == Exchange.GEMINI:
            data = await connector.get_gemini_orderbook(symbol)
        elif exchange == Exchange.COINBASE:
            data = await connector.get_coinbase_orderbook(symbol)
        elif exchange == Exchange.KUCOIN:
            data = await connector.get_kucoin_orderbook(symbol)
        elif exchange == Exchange.BITFINEX:
            data = await connector.get_bitfinex_orderbook(symbol)
        elif exchange == Exchange.BYBIT:
            data = await connector.get_bybit_orderbook(symbol)
        
        return {
            "exchange": exchange.value,
            "symbol": symbol,
            "data": data,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/aggregate-liquidity")
async def aggregate_liquidity(request: LiquidityRequest):
    """Aggregate liquidity from multiple exchanges"""
    try:
        exchanges = request.exchanges or list(Exchange)
        tasks = []
        
        for exchange in exchanges:
            task = get_orderbook(exchange, request.symbol)
            tasks.append(task)
        
        orderbooks = await asyncio.gather(*tasks)
        
        # Aggregate liquidity
        all_bids = []
        all_asks = []
        exchange_data = {}
        
        for i, orderbook in enumerate(orderbooks):
            exchange_name = exchanges[i].value
            exchange_data[exchange_name] = orderbook["data"]
            
            # Extract bids and asks (format may vary by exchange)
            if "bids" in orderbook["data"]:
                for bid in orderbook["data"]["bids"][:20]:
                    all_bids.append((bid[0], bid[1], exchange_name))
            
            if "asks" in orderbook["data"]:
                for ask in orderbook["data"]["asks"][:20]:
                    all_asks.append((ask[0], ask[1], exchange_name))
        
        # Sort and aggregate
        if request.side == "buy":
            all_bids.sort(key=lambda x: float(x[0]), reverse=True)
            best_price = float(all_bids[0][0]) if all_bids else 0
        else:
            all_asks.sort(key=lambda x: float(x[0]))
            best_price = float(all_asks[0][0]) if all_asks else 0
        
        # Calculate routing
        routing = []
        remaining_amount = request.amount
        
        if request.side == "buy":
            for price, amount, exchange in all_bids:
                if remaining_amount <= 0:
                    break
                order_amount = min(remaining_amount, float(amount))
                routing.append({
                    "exchange": exchange,
                    "price": price,
                    "amount": order_amount,
                    "total": price * order_amount
                })
                remaining_amount -= order_amount
        else:
            for price, amount, exchange in all_asks:
                if remaining_amount <= 0:
                    break
                order_amount = min(remaining_amount, float(amount))
                routing.append({
                    "exchange": exchange,
                    "price": price,
                    "amount": order_amount,
                    "total": price * order_amount
                })
                remaining_amount -= order_amount
        
        total_liquidity = sum(float(bid[1]) for bid in all_bids) if request.side == "buy" else sum(float(ask[1]) for ask in all_asks)
        
        return LiquidityResponse(
            best_price=best_price,
            total_liquidity=total_liquidity,
            exchanges=exchange_data,
            routing=routing
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/smart-order-route")
async def smart_order_route(request: LiquidityRequest):
    """Smart order routing with optimal execution"""
    try:
        # Get aggregated liquidity
        agg_response = await aggregate_liquidity(request)
        
        # Apply smart routing algorithms
        optimized_routing = []
        min_slippage = float('inf')
        best_routing = []
        
        # Try different routing strategies
        for i in range(1, min(5, len(agg_response.routing) + 1)):
            current_routing = agg_response.routing[:i]
            
            # Calculate average price and slippage
            total_amount = sum(r["amount"] for r in current_routing)
            if total_amount >= request.amount:
                avg_price = sum(r["total"] for r in current_routing) / total_amount
                reference_price = agg_response.best_price
                slippage = abs(avg_price - reference_price) / reference_price * 100
                
                if slippage < min_slippage:
                    min_slippage = slippage
                    best_routing = current_routing
        
        return {
            "symbol": request.symbol,
            "side": request.side,
            "amount": request.amount,
            "best_price": agg_response.best_price,
            "average_execution_price": sum(r["total"] for r in best_routing) / sum(r["amount"] for r in best_routing) if best_routing else 0,
            "estimated_slippage": min_slippage,
            "routing": best_routing,
            "total_cost": sum(r["total"] for r in best_routing)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)