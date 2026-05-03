#!/usr/bin/env python3
"""
TigerEx Price Synchronization System
Real-time price feed from multiple exchanges
TigerEx prices will match other exchanges in real-time
"""
import os
import asyncio
import hashlib
import json
import logging
import time
import threading
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict

import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== CONFIGURATION ====================

EXCHANGE_CONFIGS = {
    "binance": {
        "name": "Binance",
        "url": "https://api.binance.com",
        "enabled": True
    },
    "coinbase": {
        "name": "Coinbase",
        "url": "https://api.coinbase.com",
        "enabled": True
    },
    "kraken": {
        "name": "Kraken",
        "url": "https://api.kraken.com",
        "enabled": True
    },
    "kucoin": {
        "name": "KuCoin",
        "url": "https://api.kucoin.com",
        "enabled": True
    },
    "bybit": {
        "name": "Bybit",
        "url": "https://api.bybit.com",
        "enabled": True
    },
    "okx": {
        "name": "OKX",
        "url": "https://www.okx.com/api",
        "enabled": True
    }
}

SYMBOL_MAPPING = {
    "BTCUSDT": [("binance", "btcusdt"), ("coinbase", "BTC-USD"), ("kraken", "XBT/USD"), ("kucoin", "BTC-USDT"), ("bybit", "BTCUSDT"), ("okx", "BTC-USDT")],
    "ETHUSDT": [("binance", "ethusdt"), ("coinbase", "ETH-USD"), ("kraken", "ETH/USD"), ("kucoin", "ETH-USDT"), ("bybit", "ETHUSDT"), ("okx", "ETH-USDT")],
    "BNBUSDT": [("binance", "bnbusdt"), ("kucoin", "BNB-USDT"), ("okx", "BNB-USDT")],
    "SOLUSDT": [("binance", "solusdt"), ("coinbase", "SOL-USD"), ("kucoin", "SOL-USDT"), ("okx", "SOL-USDT")],
    "ADAUSDT": [("binance", "adausdt"), ("coinbase", "ADA-USD"), ("kraken", "ADA/USD"), ("kucoin", "ADA-USDT"), ("okx", "ADA-USDT")],
    "XRPUSDT": [("binance", "xrpusdt"), ("coinbase", "XRP-USD"), ("kraken", "XRP/USD"), ("kucoin", "XRP-USDT"), ("okx", "XRP-USDT")],
    "DOGEUSDT": [("binance", "dogeusdt"), ("coinbase", "DOGE-USD"), ("kraken", "DOGE/USD"), ("kucoin", "DOGE-USDT"), ("okx", "DOGE-USDT")],
    "DOTUSDT": [("binance", "dotusdt"), ("coinbase", "DOT-USD"), ("kucoin", "DOT-USDT"), ("okx", "DOT-USDT")],
    "MATICUSDT": [("binance", "maticusdt"), ("coinbase", "MATIC-USD"), ("kucoin", "MATIC-USDT"), ("okx", "MATIC-USDT")],
    "LTCUSDT": [("binance", "ltcusdt"), ("coinbase", "LTC-USD"), ("kraken", "LTC/USD"), ("kucoin", "LTC-USDT"), ("okx", "LTC-USDT")],
}


# ==================== PRICE DATA MODELS ====================

@dataclass
class PriceTick:
    symbol: str
    exchange: str
    price: float
    bid: float
    ask: float
    volume_24h: float
    timestamp: datetime
    latency_ms: float
    
    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "exchange": self.exchange,
            "price": self.price,
            "bid": self.bid,
            "ask": self.ask,
            "volume_24h": self.volume_24h,
            "timestamp": self.timestamp.isoformat(),
            "latency_ms": self.latency_ms
        }


@dataclass  
class AggregatedPrice:
    symbol: str
    price: float
    bid: float
    ask: float
    spread: float
    volume_24h: float
    change_24h: float
    last_updated: datetime
    exchange_prices: Dict[str, dict]
    sources: List[str]
    
    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "price": self.price,
            "bid": self.bid,
            "ask": self.ask,
            "spread": self.spread,
            "volume_24h": self.volume_24h,
            "change_24h": self.change_24h,
            "last_updated": self.last_updated.isoformat(),
            "exchange_prices": self.exchange_prices,
            "sources": self.sources
        }


# ==================== EXCHANGE CONNECTORS ====================

class ExchangeConnector:
    def __init__(self, config: dict):
        self.config = config
        self.name = config.get("name", "unknown")
        self.url = config.get("url", "")
        self.enabled = config.get("enabled", True)
        self.latency_ms = 0
        
    def fetch_ticker(self, symbol: str) -> Optional[PriceTick]:
        return None
    
    def _make_request(self, endpoint: str, params: dict = None) -> dict:
        start = time.time()
        try:
            response = requests.get(f"{self.url}{endpoint}", params=params or {}, timeout=5)
            self.latency_ms = (time.time() - start) * 1000
            return response.json() if response.status_code == 200 else {}
        except Exception as e:
            logger.warning(f"{self.name} error: {e}")
            return {}


class BinanceConnector(ExchangeConnector):
    def fetch_ticker(self, symbol: str) -> Optional[PriceTick]:
        try:
            data = self._make_request("/api/v3/ticker/24hr", {"symbol": symbol.upper()})
            if data:
                return PriceTick(
                    symbol=symbol, exchange="binance",
                    price=float(data.get("lastPrice", 0)),
                    bid=float(data.get("bidPrice", 0)),
                    ask=float(data.get("askPrice", 0)),
                    volume_24h=float(data.get("volume", 0)),
                    timestamp=datetime.utcnow(),
                    latency_ms=self.latency_ms
                )
        except Exception as e:
            logger.warning(f"Binance error: {e}")
        return None


class CoinbaseConnector(ExchangeConnector):
    def fetch_ticker(self, symbol: str) -> Optional[PriceTick]:
        try:
            pair = {"BTCUSDT": "BTC-USD", "ETHUSDT": "ETH-USD"}.get(symbol, symbol.replace("USDT", "-USD"))
            data = self._make_request(f"/v2/bicker/{pair}", {"state": "MATCHED"})
            if data and "data" in data:
                d = data["data"]
                return PriceTick(
                    symbol=symbol, exchange="coinbase",
                    price=float(d.get("price", 0)),
                    bid=float(d.get("bid", 0)),
                    ask=float(d.get("ask", 0)),
                    volume_24h=float(d.get("volume", 0)),
                    timestamp=datetime.utcnow(),
                    latency_ms=self.latency_ms
                )
        except Exception as e:
            logger.warning(f"Coinbase error: {e}")
        return None


class KrakenConnector(ExchangeConnector):
    def fetch_ticker(self, symbol: str) -> Optional[PriceTick]:
        try:
            pair = "XBT/USD" if "BTC" in symbol else symbol.replace("USDT", "/USD")
            data = self._make_request("/0/public/Ticker", {"pair": pair})
            if data and "result" in data:
                result = list(data["result"].values())[0]
                return PriceTick(
                    symbol=symbol, exchange="kraken",
                    price=float(result.get("c", [0])[0]),
                    bid=float(result.get("b", [0])[0]),
                    ask=float(result.get("a", [0])[0]),
                    volume_24h=float(result.get("v", [0])[0]),
                    timestamp=datetime.utcnow(),
                    latency_ms=self.latency_ms
                )
        except Exception as e:
            logger.warning(f"Kraken error: {e}")
        return None


class KuCoinConnector(ExchangeConnector):
    def fetch_ticker(self, symbol: str) -> Optional[PriceTick]:
        try:
            data = self._make_request(f"/api/v1/market/orderbook/level1?symbol={symbol}")
            if data and "data" in data:
                d = data["data"]
                return PriceTick(
                    symbol=symbol, exchange="kucoin",
                    price=float(d.get("price", 0)),
                    bid=float(d.get("bestBid", 0)),
                    ask=float(d.get("bestAsk", 0)),
                    volume_24h=float(d.get("size", 0)),
                    timestamp=datetime.utcnow(),
                    latency_ms=self.latency_ms
                )
        except Exception as e:
            logger.warning(f"KuCoin error: {e}")
        return None


class BybitConnector(ExchangeConnector):
    def fetch_ticker(self, symbol: str) -> Optional[PriceTick]:
        try:
            data = self._make_request("/v5/market/ticker", {"symbol": symbol, "category": "spot"})
            if data and "result" in data and "list" in data["result"]:
                d = data["result"]["list"][0]
                return PriceTick(
                    symbol=symbol, exchange="bybit",
                    price=float(d.get("lastPrice", 0)),
                    bid=float(d.get("bid1Price", 0)),
                    ask=float(d.get("ask1Price", 0)),
                    volume_24h=float(d.get("volume24h", 0)),
                    timestamp=datetime.utcnow(),
                    latency_ms=self.latency_ms
                )
        except Exception as e:
            logger.warning(f"Bybit error: {e}")
        return None


class OKXConnector(ExchangeConnector):
    def fetch_ticker(self, symbol: str) -> Optional[PriceTick]:
        try:
            data = self._make_request(f"/v5/market/ticker?instId={symbol}&usd=true")
            if data and "data" in data:
                d = data["data"][0]
                return PriceTick(
                    symbol=symbol, exchange="okx",
                    price=float(d.get("last", 0)),
                    bid=float(d.get("bidPx", 0)),
                    ask=float(d.get("askPx", 0)),
                    volume_24h=float(d.get("vol24h", 0)),
                    timestamp=datetime.utcnow(),
                    latency_ms=self.latency_ms
                )
        except Exception as e:
            logger.warning(f"OKX error: {e}")
        return None


# ==================== PRICE AGGREGATOR ====================

class PriceAggregator:
    """Aggregates prices from multiple exchanges in real-time"""
    
    def __init__(self):
        self.connectors: Dict[str, ExchangeConnector] = {}
        self.prices: Dict[str, Dict[str, PriceTick]] = defaultdict(dict)
        self.aggregated_prices: Dict[str, AggregatedPrice] = {}
        self.last_update = {}
        self.running = False
        self._init_connectors()
        self._start_sync()
    
    def _init_connectors(self):
        self.connectors["binance"] = BinanceConnector(EXCHANGE_CONFIGS["binance"])
        self.connectors["coinbase"] = CoinbaseConnector(EXCHANGE_CONFIGS["coinbase"])
        self.connectors["kraken"] = KrakenConnector(EXCHANGE_CONFIGS["kraken"])
        self.connectors["kucoin"] = KuCoinConnector(EXCHANGE_CONFIGS["kucoin"])
        self.connectors["bybit"] = BybitConnector(EXCHANGE_CONFIGS["bybit"])
        self.connectors["okx"] = OKXConnector(EXCHANGE_CONFIGS["okx"])
        logger.info(f"Initialized {len(self.connectors)} exchange connectors")
    
    def _start_sync(self):
        def sync_loop():
            while True:
                try:
                    self.sync_all_prices()
                except Exception as e:
                    logger.error(f"Sync error: {e}")
                time.sleep(1)
        
        thread = threading.Thread(target=sync_loop, daemon=True)
        thread.start()
        self.running = True
    
    def sync_all_prices(self):
        for symbol in SYMBOL_MAPPING.keys():
            self.sync_symbol(symbol)
    
    def sync_symbol(self, symbol: str):
        exchange_prices = {}
        for exchange_name in ["binance", "coinbase", "kraken", "kucoin", "bybit", "okx"]:
            connector = self.connectors.get(exchange_name)
            if connector and connector.enabled:
                tick = connector.fetch_ticker(symbol)
                if tick:
                    exchange_prices[exchange_name] = tick
                    self.prices[symbol][exchange_name] = tick
        
        if exchange_prices:
            self.aggregated_prices[symbol] = self._aggregate(symbol, exchange_prices)
            self.last_update[symbol] = datetime.utcnow()
    
    def _aggregate(self, symbol: str, prices: Dict[str, PriceTick]) -> AggregatedPrice:
        price_values = [p.price for p in prices.values()]
        if not price_values:
            return AggregatedPrice(symbol, 0, 0, 0, 0, 0, 0, datetime.utcnow(), {}, [])
        
        volumes = [p.volume_24h for p in prices.values()]
        total_volume = sum(volumes) or 1
        
        weighted_price = sum(p.price * p.volume_24h for p in prices.values()) / total_volume
        weighted_bid = sum(p.bid * p.volume_24h for p in prices.values()) / total_volume
        weighted_ask = sum(p.ask * p.volume_24h for p in prices.values()) / total_volume
        
        return AggregatedPrice(
            symbol=symbol,
            price=round(weighted_price, 8),
            bid=round(weighted_bid, 8),
            ask=round(weighted_ask, 8),
            spread=round(weighted_ask - weighted_bid, 8),
            volume_24h=sum(volumes),
            change_24h=0,
            last_updated=datetime.utcnow(),
            exchange_prices={k: v.to_dict() for k, v in prices.items()},
            sources=list(prices.keys())
        )
    
    def get_price(self, symbol: str) -> Optional[AggregatedPrice]:
        return self.aggregated_prices.get(symbol)
    
    def get_all_prices(self) -> Dict[str, dict]:
        return {symbol: price.to_dict() for symbol, price in self.aggregated_prices.items()}
    
    def is_healthy(self) -> bool:
        return self.running and len(self.aggregated_prices) > 0


# ==================== GLOBAL ====================

_price_aggregator = None

def get_price_aggregator() -> PriceAggregator:
    global _price_aggregator
    if _price_aggregator is None:
        _price_aggregator = PriceAggregator()
    return _price_aggregator


# ==================== FLASK ====================

app = Flask(__name__)
CORS(app)

@app.route('/price/health', methods=['GET'])
def price_health():
    agg = get_price_aggregator()
    return jsonify({
        "status": "ok" if agg.is_healthy() else "error",
        "connected_exchanges": len(agg.connectors),
        "symbols_tracked": len(agg.aggregated_prices)
    })

@app.route('/price/<symbol>', methods=['GET'])
def get_symbol_price(symbol):
    agg = get_price_aggregator()
    price = agg.get_price(symbol.upper())
    if price:
        return jsonify({"success": True, "price": price.to_dict()})
    return jsonify({"success": False}), 404

@app.route('/price', methods=['GET'])
def get_all_prices():
    agg = get_price_aggregator()
    return jsonify({"success": True, "prices": agg.get_all_prices()})

@app.route('/price/sync', methods=['POST'])
def sync_prices():
    agg = get_price_aggregator()
    agg.sync_all_prices()
    return jsonify({"success": True})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5200))
    agg = get_price_aggregator()
    agg.sync_all_prices()
    logger.info(f"Price sync started on port {port}")
    app.run(host='0.0.0.0', port=port, threaded=True)def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
