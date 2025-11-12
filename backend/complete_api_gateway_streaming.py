#!/usr/bin/env python3
"""
Complete API Gateway & Real-Time Streaming Services
All microservices integration with real-time data streaming
Complete functionality for traders, Full admin control
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from decimal import Decimal
import redis
import aiohttp
import numpy as np
import pandas as pd
from enum import Enum
import websocket
import threading
import time
import uuid
import jwt
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamType(Enum):
    MARKET_DATA = "market_data"
    ORDER_BOOK = "order_book"
    TRADES = "trades"
    PORTFOLIO = "portfolio"
    POSITIONS = "positions"
    NOTIFICATIONS = "notifications"
    SYSTEM_STATUS = "system_status"
    PRICE_ALERTS = "price_alerts"
    ORDER_UPDATES = "order_updates"

class UserRole(Enum):
    TRADER = "trader"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    TECHNICAL_TEAM = "technical_team"
    MODERATOR = "moderator"

@dataclass
class StreamSubscription:
    subscription_id: str
    user_id: str
    stream_type: StreamType
    symbols: List[str]
    filters: Dict[str, Any]
    created_at: datetime
    active: bool

@dataclass
class ConnectedClient:
    client_id: str
    user_id: str
    websocket: WebSocket
    role: UserRole
    subscriptions: List[str]
    connected_at: datetime
    last_ping: datetime

class CompleteAPIGatewayStreaming:
    """Complete API Gateway with real-time streaming"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=0)
        self.connected_clients: Dict[str, ConnectedClient] = {}
        self.stream_subscriptions: Dict[str, StreamSubscription] = {}
        self.market_data_cache: Dict[str, Any] = {}
        self.order_books: Dict[str, List[Dict]] = {}
        self.recent_trades: List[Dict] = []
        self.user_portfolios: Dict[str, Dict] = {}
        self.user_positions: Dict[str, List[Dict]] = {}
        self.notifications: List[Dict] = []
        self.system_metrics: Dict[str, Any] = {}
        
    async def initialize(self):
        """Initialize the API Gateway and streaming system"""
        logger.info("Initializing Complete API Gateway & Streaming System...")
        await self.load_initial_data()
        await self.start_background_tasks()
        await self.setup_websocket_handlers()
        
    async def load_initial_data(self):
        """Load initial data for streaming"""
        
        # Market data
        symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "ADA/USDT"]
        for symbol in symbols:
            base_price = np.random.uniform(10, 50000)
            self.market_data_cache[symbol] = {
                "symbol": symbol,
                "price": str(base_price),
                "change_24h": str(np.random.uniform(-10, 10)),
                "volume_24h": str(np.random.uniform(1000000, 100000000)),
                "high_24h": str(base_price * 1.05),
                "low_24h": str(base_price * 0.95),
                "timestamp": datetime.now().isoformat(),
                "bid": str(base_price * 0.999),
                "ask": str(base_price * 1.001)
            }
            
            # Order books
            bids = []
            asks = []
            for i in range(20):
                bid_price = base_price * (1 - (i * 0.001))
                ask_price = base_price * (1 + (i * 0.001))
                bids.append({
                    "price": str(bid_price),
                    "quantity": str(np.random.uniform(0.1, 100)),
                    "total": str(bid_price * np.random.uniform(0.1, 100))
                })
                asks.append({
                    "price": str(ask_price),
                    "quantity": str(np.random.uniform(0.1, 100)),
                    "total": str(ask_price * np.random.uniform(0.1, 100))
                })
            self.order_books[symbol] = {"bids": bids, "asks": asks}
        
        # Recent trades
        for i in range(50):
            self.recent_trades.append({
                "id": f"trade_{i}",
                "symbol": np.random.choice(symbols),
                "price": str(np.random.uniform(10, 50000)),
                "quantity": str(np.random.uniform(0.001, 10)),
                "side": np.random.choice(["buy", "sell"]),
                "timestamp": (datetime.now() - timedelta(minutes=i*5)).isoformat()
            })
        
        # System metrics
        self.system_metrics = {
            "total_users": 50000,
            "active_users": 12000,
            "total_trades_24h": 250000,
            "volume_24h": str(500000000),
            "system_load": np.random.uniform(20, 80),
            "memory_usage": np.random.uniform(30, 90),
            "api_requests_per_minute": np.random.randint(5000, 50000),
            "error_rate": np.random.uniform(0, 2),
            "uptime_hours": np.random.randint(100, 1000),
            "last_updated": datetime.now().isoformat()
        }
    
    async def start_background_tasks(self):
        """Start background tasks for data updates"""
        
        # Market data updates
        asyncio.create_task(self.update_market_data_loop())
        
        # Order book updates
        asyncio.create_task(self.update_order_books_loop())
        
        # Trade updates
        asyncio.create_task(self.update_trades_loop())
        
        # System metrics updates
        asyncio.create_task(self.update_system_metrics_loop())
        
        # Cleanup disconnected clients
        asyncio.create_task(self.cleanup_clients_loop())
    
    async def setup_websocket_handlers(self):
        """Setup WebSocket connection handlers"""
        logger.info("Setting up WebSocket handlers...")
    
    async def authenticate_websocket(self, token: str) -> Dict[str, Any]:
        """Authenticate WebSocket connection"""
        
        try:
            # Decode JWT token
            payload = jwt.decode(token, "your-secret-key", algorithms=["HS256"])
            user_id = payload.get("sub")
            role = UserRole(payload.get("role", "trader"))
            
            return {
                "success": True,
                "user_id": user_id,
                "role": role,
                "permissions": self.get_user_permissions(role)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_user_permissions(self, role: UserRole) -> List[str]:
        """Get permissions based on user role"""
        
        permissions_map = {
            UserRole.TRADER: [
                "view_market_data", "place_orders", "view_portfolio",
                "view_positions", "receive_notifications"
            ],
            UserRole.ADMIN: [
                "view_market_data", "place_orders", "view_portfolio",
                "view_positions", "receive_notifications", "manage_users",
                "view_system_metrics", "control_trading"
            ],
            UserRole.SUPER_ADMIN: [
                "view_market_data", "place_orders", "view_portfolio",
                "view_positions", "receive_notifications", "manage_users",
                "view_system_metrics", "control_trading", "system_config",
                "emergency_control", "full_data_access"
            ],
            UserRole.TECHNICAL_TEAM: [
                "view_system_metrics", "system_config", "debug_access",
                "monitor_services", "view_logs"
            ],
            UserRole.MODERATOR: [
                "view_market_data", "manage_users", "view_trading_activity",
                "receive_notifications", "moderation_tools"
            ]
        }
        
        return permissions_map.get(role, [])
    
    async def handle_websocket_connection(self, websocket: WebSocket, token: str):
        """Handle new WebSocket connection"""
        
        try:
            # Authenticate connection
            auth_result = await self.authenticate_websocket(token)
            if not auth_result["success"]:
                await websocket.close(code=4001, reason="Authentication failed")
                return
            
            # Accept connection
            await websocket.accept()
            
            # Create connected client
            client_id = str(uuid.uuid4())
            connected_client = ConnectedClient(
                client_id=client_id,
                user_id=auth_result["user_id"],
                websocket=websocket,
                role=auth_result["role"],
                subscriptions=[],
                connected_at=datetime.now(),
                last_ping=datetime.now()
            )
            
            self.connected_clients[client_id] = connected_client
            
            # Send initial data
            await self.send_initial_data(connected_client)
            
            # Handle messages
            await self.handle_client_messages(connected_client)
            
        except WebSocketDisconnect:
            if client_id in self.connected_clients:
                del self.connected_clients[client_id]
        except Exception as e:
            logger.error(f"Error handling WebSocket connection: {e}")
            try:
                await websocket.close(code=4000, reason="Internal server error")
            except:
                pass
    
    async def send_initial_data(self, client: ConnectedClient):
        """Send initial data to connected client"""
        
        try:
            initial_data = {
                "type": "initial_data",
                "user_id": client.user_id,
                "role": client.role.value,
                "permissions": self.get_user_permissions(client.role),
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "market_data": list(self.market_data_cache.values()),
                    "system_metrics": self.system_metrics,
                    "available_streams": [
                        {
                            "type": stream_type.value,
                            "description": self.get_stream_description(stream_type),
                            "requires_symbols": self.stream_requires_symbols(stream_type)
                        }
                        for stream_type in StreamType
                    ]
                }
            }
            
            await client.websocket.send_text(json.dumps(initial_data))
            
        except Exception as e:
            logger.error(f"Error sending initial data: {e}")
    
    def get_stream_description(self, stream_type: StreamType) -> str:
        """Get description for stream type"""
        
        descriptions = {
            StreamType.MARKET_DATA: "Real-time market data updates",
            StreamType.ORDER_BOOK: "Live order book depth updates",
            StreamType.TRADES: "Recent trades feed",
            StreamType.PORTFOLIO: "Portfolio balance updates",
            StreamType.POSITIONS: "Position and P&L updates",
            StreamType.NOTIFICATIONS: "System and trading notifications",
            StreamType.SYSTEM_STATUS: "System health and metrics",
            StreamType.PRICE_ALERTS: "Price alert notifications",
            StreamType.ORDER_UPDATES: "Order status updates"
        }
        
        return descriptions.get(stream_type, "Unknown stream type")
    
    def stream_requires_symbols(self, stream_type: StreamType) -> bool:
        """Check if stream requires symbol selection"""
        
        return stream_type in [
            StreamType.MARKET_DATA, StreamType.ORDER_BOOK, 
            StreamType.TRADES, StreamType.PRICE_ALERTS
        ]
    
    async def handle_client_messages(self, client: ConnectedClient):
        """Handle messages from WebSocket client"""
        
        try:
            while True:
                # Receive message
                message = await client.websocket.receive_text()
                data = json.loads(message)
                
                # Update last ping
                client.last_ping = datetime.now()
                
                # Handle message based on type
                if data.get("type") == "subscribe":
                    await self.handle_subscription(client, data)
                elif data.get("type") == "unsubscribe":
                    await self.handle_unsubscription(client, data)
                elif data.get("type") == "ping":
                    await client.websocket.send_text(json.dumps({"type": "pong"}))
                elif data.get("type") == "place_order":
                    await self.handle_order_placement(client, data)
                elif data.get("type") == "get_data":
                    await self.handle_data_request(client, data)
                
        except WebSocketDisconnect:
            logger.info(f"Client {client.client_id} disconnected")
            if client.client_id in self.connected_clients:
                del self.connected_clients[client.client_id]
        except Exception as e:
            logger.error(f"Error handling client messages: {e}")
    
    async def handle_subscription(self, client: ConnectedClient, data: Dict[str, Any]):
        """Handle stream subscription"""
        
        try:
            stream_type = StreamType(data.get("stream_type"))
            symbols = data.get("symbols", [])
            filters = data.get("filters", {})
            
            # Validate subscription
            if not self.can_subscribe_to_stream(client.role, stream_type):
                await client.websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Insufficient permissions for this stream"
                }))
                return
            
            # Create subscription
            subscription_id = str(uuid.uuid4())
            subscription = StreamSubscription(
                subscription_id=subscription_id,
                user_id=client.user_id,
                stream_type=stream_type,
                symbols=symbols,
                filters=filters,
                created_at=datetime.now(),
                active=True
            )
            
            self.stream_subscriptions[subscription_id] = subscription
            client.subscriptions.append(subscription_id)
            
            # Send confirmation
            await client.websocket.send_text(json.dumps({
                "type": "subscription_confirmed",
                "subscription_id": subscription_id,
                "stream_type": stream_type.value,
                "symbols": symbols,
                "timestamp": datetime.now().isoformat()
            }))
            
            # Send initial stream data
            await self.send_stream_data(client, subscription)
            
        except Exception as e:
            await client.websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Subscription failed: {str(e)}"
            }))
    
    def can_subscribe_to_stream(self, role: UserRole, stream_type: StreamType) -> bool:
        """Check if user role can subscribe to stream"""
        
        stream_permissions = {
            UserRole.TRADER: [
                StreamType.MARKET_DATA, StreamType.ORDER_BOOK, StreamType.TRADES,
                StreamType.PORTFOLIO, StreamType.POSITIONS, StreamType.NOTIFICATIONS,
                StreamType.PRICE_ALERTS, StreamType.ORDER_UPDATES
            ],
            UserRole.ADMIN: [
                StreamType.MARKET_DATA, StreamType.ORDER_BOOK, StreamType.TRADES,
                StreamType.PORTFOLIO, StreamType.POSITIONS, StreamType.NOTIFICATIONS,
                StreamType.SYSTEM_STATUS, StreamType.PRICE_ALERTS, StreamType.ORDER_UPDATES
            ],
            UserRole.SUPER_ADMIN: list(StreamType),
            UserRole.TECHNICAL_TEAM: [
                StreamType.SYSTEM_STATUS, StreamType.NOTIFICATIONS
            ],
            UserRole.MODERATOR: [
                StreamType.TRADES, StreamType.NOTIFICATIONS, StreamType.ORDER_UPDATES
            ]
        }
        
        return stream_type in stream_permissions.get(role, [])
    
    async def handle_unsubscription(self, client: ConnectedClient, data: Dict[str, Any]):
        """Handle stream unsubscription"""
        
        try:
            subscription_id = data.get("subscription_id")
            
            if subscription_id in self.stream_subscriptions:
                del self.stream_subscriptions[subscription_id]
            
            if subscription_id in client.subscriptions:
                client.subscriptions.remove(subscription_id)
            
            await client.websocket.send_text(json.dumps({
                "type": "unsubscription_confirmed",
                "subscription_id": subscription_id,
                "timestamp": datetime.now().isoformat()
            }))
            
        except Exception as e:
            await client.websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Unsubscription failed: {str(e)}"
            }))
    
    async def handle_order_placement(self, client: ConnectedClient, data: Dict[str, Any]):
        """Handle order placement from WebSocket"""
        
        try:
            if not self.can_place_orders(client.role):
                await client.websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Insufficient permissions to place orders"
                }))
                return
            
            order_data = data.get("order_data", {})
            
            # Simulate order placement
            order_result = {
                "type": "order_result",
                "order_id": f"order_{uuid.uuid4()}",
                "status": "submitted",
                "timestamp": datetime.now().isoformat(),
                "message": "Order placed successfully"
            }
            
            await client.websocket.send_text(json.dumps(order_result))
            
        except Exception as e:
            await client.websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Order placement failed: {str(e)}"
            }))
    
    def can_place_orders(self, role: UserRole) -> bool:
        """Check if user role can place orders"""
        
        return role in [UserRole.TRADER, UserRole.ADMIN, UserRole.SUPER_ADMIN]
    
    async def handle_data_request(self, client: ConnectedClient, data: Dict[str, Any]):
        """Handle data request from WebSocket"""
        
        try:
            request_type = data.get("request_type")
            
            if request_type == "portfolio":
                portfolio_data = await self.get_user_portfolio(client.user_id)
                await client.websocket.send_text(json.dumps({
                    "type": "portfolio_data",
                    "data": portfolio_data,
                    "timestamp": datetime.now().isoformat()
                }))
            elif request_type == "positions":
                positions_data = await self.get_user_positions(client.user_id)
                await client.websocket.send_text(json.dumps({
                    "type": "positions_data",
                    "data": positions_data,
                    "timestamp": datetime.now().isoformat()
                }))
            elif request_type == "order_book":
                symbol = data.get("symbol")
                if symbol in self.order_books:
                    await client.websocket.send_text(json.dumps({
                        "type": "order_book_data",
                        "symbol": symbol,
                        "data": self.order_books[symbol],
                        "timestamp": datetime.now().isoformat()
                    }))
            
        except Exception as e:
            await client.websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Data request failed: {str(e)}"
            }))
    
    async def get_user_portfolio(self, user_id: str) -> Dict[str, Any]:
        """Get user portfolio data"""
        
        if user_id not in self.user_portfolios:
            self.user_portfolios[user_id] = {
                "total_value": str(np.random.uniform(10000, 100000)),
                "pnl_24h": str(np.random.uniform(-5000, 5000)),
                "balances": {
                    "USDT": str(np.random.uniform(1000, 50000)),
                    "BTC": str(np.random.uniform(0.001, 10)),
                    "ETH": str(np.random.uniform(0.01, 100)),
                    "BNB": str(np.random.uniform(1, 1000))
                },
                "last_updated": datetime.now().isoformat()
            }
        
        return self.user_portfolios[user_id]
    
    async def get_user_positions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user positions"""
        
        if user_id not in self.user_positions:
            self.user_positions[user_id] = [
                {
                    "symbol": "BTCUSDT-PERP",
                    "side": "long",
                    "size": str(np.random.uniform(0.01, 10)),
                    "entry_price": str(np.random.uniform(40000, 50000)),
                    "mark_price": str(np.random.uniform(40000, 50000)),
                    "pnl": str(np.random.uniform(-5000, 5000)),
                    "leverage": str(np.random.choice([1, 2, 5, 10, 20, 50])),
                    "liquidation_price": str(np.random.uniform(30000, 40000)),
                    "last_updated": datetime.now().isoformat()
                }
                for _ in range(np.random.randint(0, 5))
            ]
        
        return self.user_positions[user_id]
    
    async def send_stream_data(self, client: ConnectedClient, subscription: StreamSubscription):
        """Send initial data for a stream subscription"""
        
        try:
            if subscription.stream_type == StreamType.MARKET_DATA:
                data = {
                    "type": "market_data_update",
                    "subscription_id": subscription.subscription_id,
                    "data": [
                        self.market_data_cache[symbol]
                        for symbol in subscription.symbols
                        if symbol in self.market_data_cache
                    ],
                    "timestamp": datetime.now().isoformat()
                }
                await client.websocket.send_text(json.dumps(data))
                
            elif subscription.stream_type == StreamType.ORDER_BOOK:
                for symbol in subscription.symbols:
                    if symbol in self.order_books:
                        data = {
                            "type": "order_book_update",
                            "subscription_id": subscription.subscription_id,
                            "symbol": symbol,
                            "data": self.order_books[symbol],
                            "timestamp": datetime.now().isoformat()
                        }
                        await client.websocket.send_text(json.dumps(data))
                        
            elif subscription.stream_type == StreamType.TRADES:
                data = {
                    "type": "trades_update",
                    "subscription_id": subscription.subscription_id,
                    "data": self.recent_trades[:20],
                    "timestamp": datetime.now().isoformat()
                }
                await client.websocket.send_text(json.dumps(data))
                
        except Exception as e:
            logger.error(f"Error sending stream data: {e}")
    
    async def broadcast_to_subscribers(self, stream_type: StreamType, data: Dict[str, Any]):
        """Broadcast data to all subscribed clients"""
        
        try:
            for subscription in self.stream_subscriptions.values():
                if subscription.stream_type == stream_type and subscription.active:
                    # Find the client
                    for client in self.connected_clients.values():
                        if subscription.subscription_id in client.subscriptions:
                            message = {
                                "type": f"{stream_type.value}_update",
                                "subscription_id": subscription.subscription_id,
                                "data": data,
                                "timestamp": datetime.now().isoformat()
                            }
                            await client.websocket.send_text(json.dumps(message))
                            
        except Exception as e:
            logger.error(f"Error broadcasting to subscribers: {e}")
    
    async def update_market_data_loop(self):
        """Background loop to update market data"""
        
        while True:
            try:
                await asyncio.sleep(1)  # Update every second
                
                for symbol, data in self.market_data_cache.items():
                    # Simulate price movement
                    current_price = float(data["price"])
                    change = (np.random.random() - 0.5) * 0.002 * current_price
                    new_price = current_price + change
                    
                    data["price"] = str(new_price)
                    data["change_24h"] = str(float(data["change_24h"]) + np.random.uniform(-0.1, 0.1))
                    data["timestamp"] = datetime.now().isoformat()
                    data["bid"] = str(new_price * 0.999)
                    data["ask"] = str(new_price * 1.001)
                
                # Broadcast to subscribers
                await self.broadcast_to_subscribers(
                    StreamType.MARKET_DATA,
                    list(self.market_data_cache.values())
                )
                
            except Exception as e:
                logger.error(f"Error in market data update loop: {e}")
    
    async def update_order_books_loop(self):
        """Background loop to update order books"""
        
        while True:
            try:
                await asyncio.sleep(2)  # Update every 2 seconds
                
                for symbol, order_book in self.order_books.items():
                    base_price = float(self.market_data_cache[symbol]["price"])
                    
                    # Update bids and asks
                    new_bids = []
                    new_asks = []
                    
                    for i in range(20):
                        bid_price = base_price * (1 - (i * 0.001))
                        ask_price = base_price * (1 + (i * 0.001))
                        
                        new_bids.append({
                            "price": str(bid_price),
                            "quantity": str(np.random.uniform(0.1, 100)),
                            "total": str(bid_price * np.random.uniform(0.1, 100))
                        })
                        new_asks.append({
                            "price": str(ask_price),
                            "quantity": str(np.random.uniform(0.1, 100)),
                            "total": str(ask_price * np.random.uniform(0.1, 100))
                        })
                    
                    order_book["bids"] = new_bids
                    order_book["asks"] = new_asks
                
                # Broadcast to subscribers
                for symbol in self.order_books:
                    await self.broadcast_to_subscribers(
                        StreamType.ORDER_BOOK,
                        {"symbol": symbol, "order_book": self.order_books[symbol]}
                    )
                
            except Exception as e:
                logger.error(f"Error in order books update loop: {e}")
    
    async def update_trades_loop(self):
        """Background loop to update recent trades"""
        
        while True:
            try:
                await asyncio.sleep(3)  # Update every 3 seconds
                
                # Add new trade
                new_trade = {
                    "id": f"trade_{int(time.time())}",
                    "symbol": np.random.choice(list(self.market_data_cache.keys())),
                    "price": str(np.random.uniform(10, 50000)),
                    "quantity": str(np.random.uniform(0.001, 10)),
                    "side": np.random.choice(["buy", "sell"]),
                    "timestamp": datetime.now().isoformat()
                }
                
                self.recent_trades.insert(0, new_trade)
                self.recent_trades = self.recent_trades[:50]  # Keep last 50 trades
                
                # Broadcast to subscribers
                await self.broadcast_to_subscribers(
                    StreamType.TRADES,
                    self.recent_trades[:20]
                )
                
            except Exception as e:
                logger.error(f"Error in trades update loop: {e}")
    
    async def update_system_metrics_loop(self):
        """Background loop to update system metrics"""
        
        while True:
            try:
                await asyncio.sleep(5)  # Update every 5 seconds
                
                # Update metrics
                self.system_metrics.update({
                    "active_users": np.random.randint(10000, 15000),
                    "total_trades_24h": np.random.randint(200000, 300000),
                    "volume_24h": str(np.random.uniform(400000000, 600000000)),
                    "system_load": np.random.uniform(20, 80),
                    "memory_usage": np.random.uniform(30, 90),
                    "api_requests_per_minute": np.random.randint(5000, 50000),
                    "error_rate": np.random.uniform(0, 2),
                    "last_updated": datetime.now().isoformat()
                })
                
                # Broadcast to subscribers
                await self.broadcast_to_subscribers(
                    StreamType.SYSTEM_STATUS,
                    self.system_metrics
                )
                
            except Exception as e:
                logger.error(f"Error in system metrics update loop: {e}")
    
    async def cleanup_clients_loop(self):
        """Background loop to cleanup disconnected clients"""
        
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                current_time = datetime.now()
                disconnected_clients = []
                
                for client_id, client in self.connected_clients.items():
                    # Remove clients that haven't sent ping in 5 minutes
                    if (current_time - client.last_ping).seconds > 300:
                        disconnected_clients.append(client_id)
                
                for client_id in disconnected_clients:
                    del self.connected_clients[client_id]
                    logger.info(f"Cleaned up disconnected client: {client_id}")
                
            except Exception as e:
                logger.error(f"Error in cleanup clients loop: {e}")
    
    async def get_api_status(self) -> Dict[str, Any]:
        """Get API Gateway status"""
        
        return {
            "status": "operational",
            "connected_clients": len(self.connected_clients),
            "active_subscriptions": len(self.stream_subscriptions),
            "available_streams": len(StreamType),
            "system_metrics": self.system_metrics,
            "last_updated": datetime.now().isoformat()
        }

# FastAPI Application
app = FastAPI(
    title="TigerEx Complete API Gateway & Streaming",
    description="Complete API Gateway with real-time WebSocket streaming",
    version="v5.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize streaming system
streaming_system = CompleteAPIGatewayStreaming()

@app.on_event("startup")
async def startup_event():
    """Initialize streaming system on startup"""
    await streaming_system.initialize()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "TigerEx Complete API Gateway & Streaming System",
        "version": "v5.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/status")
async def get_status():
    """Get API Gateway status"""
    return await streaming_system.get_api_status()

@app.get("/market-data")
async def get_market_data():
    """Get current market data"""
    return {
        "success": True,
        "data": list(streaming_system.market_data_cache.values()),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/order-book/{symbol}")
async def get_order_book(symbol: str):
    """Get order book for symbol"""
    if symbol in streaming_system.order_books:
        return {
            "success": True,
            "symbol": symbol,
            "data": streaming_system.order_books[symbol],
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise HTTPException(status_code=404, detail="Order book not found")

@app.get("/recent-trades")
async def get_recent_trades(limit: int = Query(20, le=100)):
    """Get recent trades"""
    return {
        "success": True,
        "data": streaming_system.recent_trades[:limit],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/portfolio/{user_id}")
async def get_portfolio(user_id: str):
    """Get user portfolio"""
    portfolio_data = await streaming_system.get_user_portfolio(user_id)
    return {
        "success": True,
        "user_id": user_id,
        "data": portfolio_data,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/positions/{user_id}")
async def get_positions(user_id: str):
    """Get user positions"""
    positions_data = await streaming_system.get_user_positions(user_id)
    return {
        "success": True,
        "user_id": user_id,
        "data": positions_data,
        "timestamp": datetime.now().isoformat()
    }

@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """WebSocket endpoint for real-time streaming"""
    await streaming_system.handle_websocket_connection(websocket, token)

@app.get("/admin/control")
async def admin_control(
    action: str,
    service_id: Optional[str] = None,
    parameters: Optional[str] = Query(None)
):
    """Admin control endpoint"""
    
    try:
        # Parse parameters
        params = json.loads(parameters) if parameters else {}
        
        # Execute control action
        result = await streaming_system.control_microservice(
            "super_admin", service_id, action, params
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/dashboard")
async def admin_dashboard():
    """Get admin dashboard data"""
    
    try:
        dashboard_data = {
            "api_status": await streaming_system.get_api_status(),
            "connected_clients": len(streaming_system.connected_clients),
            "active_subscriptions": len(streaming_system.stream_subscriptions),
            "system_metrics": streaming_system.system_metrics,
            "recent_activity": [
                {
                    "client_id": client.client_id,
                    "user_id": client.user_id,
                    "role": client.role.value,
                    "connected_at": client.connected_at.isoformat(),
                    "subscriptions": len(client.subscriptions)
                }
                for client in list(streaming_system.connected_clients.values())[:10]
            ],
            "stream_statistics": {
                stream_type.value: len([s for s in streaming_system.stream_subscriptions.values() if s.stream_type == stream_type])
                for stream_type in StreamType
            }
        }
        
        return {
            "success": True,
            "dashboard_data": dashboard_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Main execution
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)