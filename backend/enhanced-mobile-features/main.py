"""
Enhanced Mobile Features Service
TigerEx v11.0.0 - Advanced Mobile Trading Platform Backend
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import asyncio
import uvicorn
import httpx
from datetime import datetime, timedelta
import json
import logging
import hashlib
import uuid
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal
from collections import defaultdict
import aiofiles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Enhanced Mobile Features Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Enums
class DeviceType(str, Enum):
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"

class NotificationType(str, Enum):
    PRICE_ALERT = "price_alert"
    ORDER_FILLED = "order_filled"
    PORTFOLIO_UPDATE = "portfolio_update"
    MARKET_NEWS = "market_news"
    SYSTEM_UPDATE = "system_update"
    SECURITY_ALERT = "security_alert"
    TRADE_CONFIRMATION = "trade_confirmation"
    MARGIN_CALL = "margin_call"

class BiometricType(str, Enum):
    FACE_ID = "face_id"
    TOUCH_ID = "touch_id"
    FINGERPRINT = "fingerprint"
    VOICE_RECOGNITION = "voice_recognition"

class TradingMode(str, Enum):
    SIMPLE = "simple"
    ADVANCED = "advanced"
    PRO = "pro"

# Data Models
@dataclass
class MobileDevice:
    device_id: str
    user_id: str
    device_type: DeviceType
    device_token: str
    app_version: str
    os_version: str
    is_active: bool
    registered_at: datetime
    last_active: datetime
    biometric_enabled: bool
    biometric_type: Optional[BiometricType]
    push_notifications_enabled: bool

class MobileNotificationRequest(BaseModel):
    user_id: str
    notification_type: NotificationType
    title: str
    message: str
    data: Optional[Dict[str, Any]] = {}
    priority: str = Field(default="normal", regex="^(low|normal|high|critical)$")
    devices: Optional[List[str]] = None  # Specific device IDs

class MobileSettings(BaseModel):
    user_id: str
    trading_mode: TradingMode = TradingMode.SIMPLE
    biometric_enabled: bool = False
    biometric_type: Optional[BiometricType] = None
    push_notifications_enabled: bool = True
    price_alerts_enabled: bool = True
    trade_confirmations_enabled: bool = True
    market_news_enabled: bool = True
    dark_mode: bool = False
    haptic_feedback: bool = True
    sound_effects: bool = True
    auto_refresh_interval: int = Field(default=30, ge=5, le=300)
    chart_type: str = Field(default="candlestick", regex="^(line|bar|candlestick|heikin_ashi)$")
    default_timeframe: str = Field(default="1D", regex="^(1M|5M|15M|1H|4H|1D|1W|1M)$")
    quick_trade_amounts: List[float] = [100, 500, 1000, 5000]
    watchlist_refresh_rate: int = Field(default=10, ge=5, le=60)

class MobileTradeRequest(BaseModel):
    user_id: str
    symbol: str
    side: str = Field(..., regex="^(buy|sell)$")
    order_type: str = Field(default="market", regex="^(market|limit|stop)$")
    quantity: Decimal = Field(..., gt=0)
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = Field(default="IOC", regex="^(IOC|GTC|FOK|DAY)$")
    use_biometric: bool = False
    quick_trade: bool = False
    quick_amount: Optional[float] = None

class MobileWatchlistItem(BaseModel):
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: float
    added_at: datetime
    alerts_enabled: bool
    price_alert_high: Optional[float] = None
    price_alert_low: Optional[float] = None

class MobilePortfolioRequest(BaseModel):
    user_id: str
    include_realized_pnl: bool = True
    include_unrealized_pnl: bool = True
    include_cost_basis: bool = True
    include_allocations: bool = True
    include_performance: bool = True
    timeframe: str = Field(default="1D", regex="^(1D|1W|1M|3M|6M|1Y)$")

# Service Classes
class MobileDeviceService:
    """Manage mobile devices and authentication"""
    
    def __init__(self):
        self.devices = {}
        self.device_sessions = {}
        self.biometric_tokens = {}
    
    async def register_device(self, device_data: Dict[str, Any]) -> MobileDevice:
        """Register new mobile device"""
        try:
            device_id = str(uuid.uuid4())
            
            device = MobileDevice(
                device_id=device_id,
                user_id=device_data['user_id'],
                device_type=DeviceType(device_data['device_type']),
                device_token=device_data['device_token'],
                app_version=device_data['app_version'],
                os_version=device_data['os_version'],
                is_active=True,
                registered_at=datetime.utcnow(),
                last_active=datetime.utcnow(),
                biometric_enabled=device_data.get('biometric_enabled', False),
                biometric_type=BiometricType(device_data['biometric_type']) if device_data.get('biometric_type') else None,
                push_notifications_enabled=device_data.get('push_notifications_enabled', True)
            )
            
            self.devices[device_id] = device
            
            logger.info(f"Registered mobile device: {device_id} for user: {device.user_id}")
            return device
            
        except Exception as e:
            logger.error(f"Error registering device: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def update_device_activity(self, device_id: str) -> bool:
        """Update device last active timestamp"""
        if device_id not in self.devices:
            return False
        
        self.devices[device_id].last_active = datetime.utcnow()
        return True
    
    async def enable_biometric(self, device_id: str, biometric_type: BiometricType, 
                             biometric_token: str) -> bool:
        """Enable biometric authentication for device"""
        if device_id not in self.devices:
            raise HTTPException(status_code=404, detail="Device not found")
        
        device = self.devices[device_id]
        device.biometric_enabled = True
        device.biometric_type = biometric_type
        
        # Store biometric token (mock - would be properly encrypted)
        self.biometric_tokens[device_id] = biometric_token
        
        logger.info(f"Enabled biometric for device: {device_id}")
        return True
    
    async def verify_biometric(self, device_id: str, biometric_token: str) -> bool:
        """Verify biometric authentication"""
        if device_id not in self.biometric_tokens:
            return False
        
        stored_token = self.biometric_tokens[device_id]
        # Mock biometric verification
        return stored_token == biometric_token
    
    async def get_user_devices(self, user_id: str) -> List[MobileDevice]:
        """Get all devices for user"""
        return [device for device in self.devices.values() if device.user_id == user_id]
    
    async def revoke_device(self, device_id: str) -> bool:
        """Revoke device access"""
        if device_id not in self.devices:
            raise HTTPException(status_code=404, detail="Device not found")
        
        self.devices[device_id].is_active = False
        
        # Remove biometric tokens
        if device_id in self.biometric_tokens:
            del self.biometric_tokens[device_id]
        
        logger.info(f"Revoked device access: {device_id}")
        return True

class MobileNotificationService:
    """Handle mobile push notifications"""
    
    def __init__(self):
        self.notification_queue = asyncio.Queue()
        self.notification_history = {}
        self.user_preferences = {}
        self.apns_tokens = {}  # iOS tokens
        self.fcm_tokens = {}   # Android tokens
    
    async def send_notification(self, request: MobileNotificationRequest) -> Dict[str, Any]:
        """Send push notification to mobile devices"""
        try:
            notification_id = str(uuid.uuid4())
            
            # Get user devices
            user_devices = [d for d in device_service.devices.values() 
                          if d.user_id == request.user_id and d.is_active and d.push_notifications_enabled]
            
            if request.devices:
                # Filter by specific devices
                user_devices = [d for d in user_devices if d.device_id in request.devices]
            
            if not user_devices:
                return {"notification_id": notification_id, "status": "no_active_devices"}
            
            # Check user notification preferences
            user_prefs = self.user_preferences.get(request.user_id, {})
            if not self._is_notification_enabled(request.notification_type, user_prefs):
                return {"notification_id": notification_id, "status": "disabled_by_user"}
            
            # Prepare notification payload
            payload = self._prepare_notification_payload(request, notification_id)
            
            # Send to each device
            sent_count = 0
            failed_count = 0
            
            for device in user_devices:
                try:
                    success = await self._send_to_device(device, payload)
                    if success:
                        sent_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.error(f"Failed to send to device {device.device_id}: {str(e)}")
                    failed_count += 1
            
            # Store notification record
            notification_record = {
                'notification_id': notification_id,
                'user_id': request.user_id,
                'type': request.notification_type,
                'title': request.title,
                'message': request.message,
                'sent_at': datetime.utcnow(),
                'devices_sent': sent_count,
                'devices_failed': failed_count,
                'priority': request.priority
            }
            
            self.notification_history[notification_id] = notification_record
            
            return {
                "notification_id": notification_id,
                "status": "sent",
                "devices_sent": sent_count,
                "devices_failed": failed_count
            }
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def send_price_alert(self, user_id: str, symbol: str, current_price: float, 
                             alert_type: str, target_price: float) -> bool:
        """Send price alert notification"""
        try:
            title = f"Price Alert: {symbol}"
            
            if alert_type == "above":
                message = f"{symbol} has risen above ${target_price:.2f}. Current price: ${current_price:.2f}"
            else:
                message = f"{symbol} has fallen below ${target_price:.2f}. Current price: ${current_price:.2f}"
            
            request = MobileNotificationRequest(
                user_id=user_id,
                notification_type=NotificationType.PRICE_ALERT,
                title=title,
                message=message,
                data={
                    "symbol": symbol,
                    "current_price": current_price,
                    "target_price": target_price,
                    "alert_type": alert_type,
                    "deep_link": f"tigerex://trade/{symbol}"
                },
                priority="high"
            )
            
            await self.send_notification(request)
            return True
            
        except Exception as e:
            logger.error(f"Error sending price alert: {str(e)}")
            return False
    
    async def send_trade_confirmation(self, user_id: str, trade_data: Dict[str, Any]) -> bool:
        """Send trade confirmation notification"""
        try:
            title = f"Trade {trade_data['side'].title()}: {trade_data['symbol']}"
            message = f"{trade_data['quantity']} {trade_data['symbol']} @ ${trade_data['price']}"
            
            request = MobileNotificationRequest(
                user_id=user_id,
                notification_type=NotificationType.TRADE_CONFIRMATION,
                title=title,
                message=message,
                data={
                    "trade_id": trade_data['trade_id'],
                    "symbol": trade_data['symbol'],
                    "side": trade_data['side'],
                    "quantity": str(trade_data['quantity']),
                    "price": trade_data['price'],
                    "deep_link": f"tigerex://portfolio"
                },
                priority="high"
            )
            
            await self.send_notification(request)
            return True
            
        except Exception as e:
            logger.error(f"Error sending trade confirmation: {str(e)}")
            return False
    
    def _is_notification_enabled(self, notification_type: NotificationType, 
                                user_prefs: Dict[str, bool]) -> bool:
        """Check if notification type is enabled by user"""
        preference_map = {
            NotificationType.PRICE_ALERT: 'price_alerts_enabled',
            NotificationType.TRADE_CONFIRMATION: 'trade_confirmations_enabled',
            NotificationType.MARKET_NEWS: 'market_news_enabled'
        }
        
        pref_key = preference_map.get(notification_type)
        return user_prefs.get(pref_key, True) if pref_key else True
    
    def _prepare_notification_payload(self, request: MobileNotificationRequest, 
                                    notification_id: str) -> Dict[str, Any]:
        """Prepare notification payload for different platforms"""
        return {
            "notification_id": notification_id,
            "title": request.title,
            "body": request.message,
            "data": request.data,
            "priority": request.priority,
            "sound": "default" if request.priority in ["high", "critical"] else None,
            "badge": 1,
            "click_action": "FLUTTER_NOTIFICATION_CLICK"
        }
    
    async def _send_to_device(self, device: MobileDevice, payload: Dict[str, Any]) -> bool:
        """Send notification to specific device"""
        # Mock implementation - would integrate with APNS for iOS and FCM for Android
        if device.device_type == DeviceType.IOS:
            # Mock APNS sending
            await asyncio.sleep(0.1)
            return True
        elif device.device_type == DeviceType.ANDROID:
            # Mock FCM sending
            await asyncio.sleep(0.1)
            return True
        else:
            # Web notification (WebSocket or Service Worker)
            await asyncio.sleep(0.1)
            return True

class MobileSettingsService:
    """Manage mobile app settings and preferences"""
    
    def __init__(self):
        self.user_settings = {}
        self.default_settings = {
            'trading_mode': 'simple',
            'biometric_enabled': False,
            'push_notifications_enabled': True,
            'price_alerts_enabled': True,
            'trade_confirmations_enabled': True,
            'market_news_enabled': True,
            'dark_mode': False,
            'haptic_feedback': True,
            'sound_effects': True,
            'auto_refresh_interval': 30,
            'chart_type': 'candlestick',
            'default_timeframe': '1D',
            'quick_trade_amounts': [100, 500, 1000, 5000],
            'watchlist_refresh_rate': 10
        }
    
    async def get_settings(self, user_id: str) -> MobileSettings:
        """Get user's mobile settings"""
        if user_id not in self.user_settings:
            # Return default settings
            settings_data = self.default_settings.copy()
            settings_data['user_id'] = user_id
            return MobileSettings(**settings_data)
        
        return MobileSettings(**self.user_settings[user_id])
    
    async def update_settings(self, user_id: str, settings_update: Dict[str, Any]) -> MobileSettings:
        """Update user's mobile settings"""
        current_settings = await self.get_settings(user_id)
        
        # Update only provided fields
        for key, value in settings_update.items():
            if hasattr(current_settings, key):
                setattr(current_settings, key, value)
        
        # Save updated settings
        self.user_settings[user_id] = current_settings.dict()
        
        # Update notification service preferences
        notification_service.user_preferences[user_id] = {
            'price_alerts_enabled': current_settings.price_alerts_enabled,
            'trade_confirmations_enabled': current_settings.trade_confirmations_enabled,
            'market_news_enabled': current_settings.market_news_enabled
        }
        
        logger.info(f"Updated mobile settings for user: {user_id}")
        return current_settings
    
    async def reset_settings(self, user_id: str) -> MobileSettings:
        """Reset user settings to defaults"""
        settings_data = self.default_settings.copy()
        settings_data['user_id'] = user_id
        
        self.user_settings[user_id] = settings_data
        
        return MobileSettings(**settings_data)

class MobileTradingService:
    """Mobile-specific trading functionality"""
    
    def __init__(self):
        self.quick_trade_presets = {}
        self.recent_trades = {}
        self.trade_templates = {}
    
    async def execute_mobile_trade(self, request: MobileTradeRequest) -> Dict[str, Any]:
        """Execute trade from mobile app"""
        try:
            # Verify biometric if required
            if request.use_biometric:
                # Mock biometric verification
                await asyncio.sleep(0.1)
            
            # Generate trade ID
            trade_id = str(uuid.uuid4())
            
            # Calculate quick trade amount if specified
            if request.quick_trade and request.quick_amount:
                # Calculate quantity based on amount and current price
                current_price = await self._get_current_price(request.symbol)
                calculated_quantity = Decimal(str(request.quick_amount)) / Decimal(str(current_price))
                request.quantity = calculated_quantity
            
            # Mock trade execution
            execution_result = {
                'trade_id': trade_id,
                'user_id': request.user_id,
                'symbol': request.symbol,
                'side': request.side,
                'order_type': request.order_type,
                'quantity': float(request.quantity),
                'price': request.price or await self._get_current_price(request.symbol),
                'status': 'filled',
                'executed_at': datetime.utcnow().isoformat(),
                'execution_price': request.price or await self._get_current_price(request.symbol),
                'commission': 0.001 * float(request.quantity) * (request.price or await self._get_current_price(request.symbol)),
                'route': 'mobile_app'
            }
            
            # Store in recent trades
            if request.user_id not in self.recent_trades:
                self.recent_trades[request.user_id] = []
            
            self.recent_trades[request.user_id].insert(0, execution_result)
            
            # Keep only last 50 trades
            self.recent_trades[request.user_id] = self.recent_trades[request.user_id][:50]
            
            # Send trade confirmation notification
            await notification_service.send_trade_confirmation(request.user_id, execution_result)
            
            logger.info(f"Executed mobile trade: {trade_id}")
            return execution_result
            
        except Exception as e:
            logger.error(f"Error executing mobile trade: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_recent_trades(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user's recent trades"""
        trades = self.recent_trades.get(user_id, [])
        return trades[:limit]
    
    async def save_trade_template(self, user_id: str, template_data: Dict[str, Any]) -> Dict[str, str]:
        """Save trade template for quick reuse"""
        try:
            template_id = str(uuid.uuid4())
            
            template = {
                'template_id': template_id,
                'user_id': user_id,
                'name': template_data['name'],
                'symbol': template_data['symbol'],
                'order_type': template_data.get('order_type', 'market'),
                'side': template_data['side'],
                'quantity_percent': template_data.get('quantity_percent', 100),
                'price_offset_percent': template_data.get('price_offset_percent', 0),
                'created_at': datetime.utcnow().isoformat()
            }
            
            if user_id not in self.trade_templates:
                self.trade_templates[user_id] = []
            
            self.trade_templates[user_id].append(template)
            
            return {"template_id": template_id, "status": "saved"}
            
        except Exception as e:
            logger.error(f"Error saving trade template: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_trade_templates(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's saved trade templates"""
        return self.trade_templates.get(user_id, [])
    
    async def _get_current_price(self, symbol: str) -> float:
        """Get current price for symbol (mock)"""
        # Mock price data
        prices = {
            'BTC': 45000.0,
            'ETH': 3000.0,
            'AAPL': 150.0,
            'GOOGL': 2800.0,
            'MSFT': 300.0
        }
        return prices.get(symbol, 100.0)

class MobileWatchlistService:
    """Mobile watchlist management"""
    
    def __init__(self):
        self.user_watchlists = {}
        self.price_alerts = {}
    
    async def get_watchlist(self, user_id: str) -> List[MobileWatchlistItem]:
        """Get user's watchlist"""
        watchlist = self.user_watchlists.get(user_id, [])
        
        # Update current prices (mock)
        updated_watchlist = []
        for item in watchlist:
            # Mock price update
            current_price = await self._get_market_data(item.symbol)
            updated_item = item.copy()
            updated_item.price = current_price['price']
            updated_item.change = current_price['change']
            updated_item.change_percent = current_price['change_percent']
            updated_item.volume = current_price['volume']
            updated_watchlist.append(updated_item)
        
        return updated_watchlist
    
    async def add_to_watchlist(self, user_id: str, symbol: str, 
                             alerts_enabled: bool = True) -> MobileWatchlistItem:
        """Add symbol to watchlist"""
        try:
            # Get market data
            market_data = await self._get_market_data(symbol)
            
            watchlist_item = MobileWatchlistItem(
                symbol=symbol,
                name=market_data['name'],
                price=market_data['price'],
                change=market_data['change'],
                change_percent=market_data['change_percent'],
                volume=market_data['volume'],
                market_cap=market_data['market_cap'],
                added_at=datetime.utcnow(),
                alerts_enabled=alerts_enabled
            )
            
            if user_id not in self.user_watchlists:
                self.user_watchlists[user_id] = []
            
            # Check if already in watchlist
            existing_symbols = [item.symbol for item in self.user_watchlists[user_id]]
            if symbol not in existing_symbols:
                self.user_watchlists[user_id].append(watchlist_item)
            
            logger.info(f"Added {symbol} to watchlist for user: {user_id}")
            return watchlist_item
            
        except Exception as e:
            logger.error(f"Error adding to watchlist: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def remove_from_watchlist(self, user_id: str, symbol: str) -> bool:
        """Remove symbol from watchlist"""
        if user_id not in self.user_watchlists:
            return False
        
        original_length = len(self.user_watchlists[user_id])
        self.user_watchlists[user_id] = [
            item for item in self.user_watchlists[user_id] if item.symbol != symbol
        ]
        
        removed = len(self.user_watchlists[user_id]) < original_length
        
        if removed:
            # Remove price alerts
            alert_key = f"{user_id}_{symbol}"
            if alert_key in self.price_alerts:
                del self.price_alerts[alert_key]
            
            logger.info(f"Removed {symbol} from watchlist for user: {user_id}")
        
        return removed
    
    async def set_price_alert(self, user_id: str, symbol: str, 
                            high_price: Optional[float] = None,
                            low_price: Optional[float] = None) -> bool:
        """Set price alert for watchlist item"""
        alert_key = f"{user_id}_{symbol}"
        
        self.price_alerts[alert_key] = {
            'user_id': user_id,
            'symbol': symbol,
            'high_price': high_price,
            'low_price': low_price,
            'created_at': datetime.utcnow()
        }
        
        # Update watchlist item
        if user_id in self.user_watchlists:
            for item in self.user_watchlists[user_id]:
                if item.symbol == symbol:
                    item.price_alert_high = high_price
                    item.price_alert_low = low_price
                    break
        
        logger.info(f"Set price alert for {symbol} for user: {user_id}")
        return True
    
    async def check_price_alerts(self) -> int:
        """Check and trigger price alerts"""
        alerts_triggered = 0
        
        for alert_key, alert in self.price_alerts.items():
            try:
                current_data = await self._get_market_data(alert['symbol'])
                current_price = current_data['price']
                
                # Check high price alert
                if alert['high_price'] and current_price >= alert['high_price']:
                    await notification_service.send_price_alert(
                        alert['user_id'], alert['symbol'], current_price, 
                        'above', alert['high_price']
                    )
                    alerts_triggered += 1
                
                # Check low price alert
                if alert['low_price'] and current_price <= alert['low_price']:
                    await notification_service.send_price_alert(
                        alert['user_id'], alert['symbol'], current_price,
                        'below', alert['low_price']
                    )
                    alerts_triggered += 1
                
            except Exception as e:
                logger.error(f"Error checking price alert for {alert['symbol']}: {str(e)}")
        
        return alerts_triggered
    
    async def _get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get market data for symbol (mock)"""
        # Mock market data
        base_prices = {
            'BTC': {'price': 45000, 'name': 'Bitcoin'},
            'ETH': {'price': 3000, 'name': 'Ethereum'},
            'AAPL': {'price': 150, 'name': 'Apple Inc.'},
            'GOOGL': {'price': 2800, 'name': 'Alphabet Inc.'},
            'MSFT': {'price': 300, 'name': 'Microsoft Corp.'}
        }
        
        if symbol not in base_prices:
            return {
                'symbol': symbol,
                'name': symbol,
                'price': 100.0,
                'change': 0.0,
                'change_percent': 0.0,
                'volume': 1000000,
                'market_cap': 1000000000
            }
        
        base = base_prices[symbol]
        
        # Add some random variation
        import random
        change_percent = random.uniform(-5, 5)
        change = base['price'] * change_percent / 100
        
        return {
            'symbol': symbol,
            'name': base['name'],
            'price': base['price'] + change,
            'change': change,
            'change_percent': change_percent,
            'volume': random.randint(1000000, 10000000),
            'market_cap': random.randint(1000000000, 10000000000)
        }

class MobilePortfolioService:
    """Mobile portfolio management"""
    
    def __init__(self):
        self.portfolio_data = {}
        self.performance_cache = {}
    
    async def get_portfolio_summary(self, request: MobilePortfolioRequest) -> Dict[str, Any]:
        """Get portfolio summary optimized for mobile"""
        try:
            # Mock portfolio data
            portfolio = {
                'total_value': 125000.50,
                'total_change': 2500.75,
                'total_change_percent': 2.04,
                'day_change': 500.25,
                'day_change_percent': 0.4,
                'total_return': 15000.50,
                'total_return_percent': 13.6,
                'holdings_count': 8,
                'cash_balance': 5000.00,
                'buying_power': 10000.00,
                'margin_used': 2500.00,
                'margin_available': 7500.00
            }
            
            # Add holdings if requested
            if request.include_realized_pnl:
                portfolio['holdings'] = [
                    {
                        'symbol': 'BTC',
                        'name': 'Bitcoin',
                        'quantity': 1.5,
                        'current_price': 45000.00,
                        'market_value': 67500.00,
                        'cost_basis': 60000.00,
                        'unrealized_pnl': 7500.00,
                        'unrealized_pnl_percent': 12.5,
                        'day_change': 1250.00,
                        'day_change_percent': 1.89
                    },
                    {
                        'symbol': 'ETH',
                        'name': 'Ethereum',
                        'quantity': 15.0,
                        'current_price': 3000.00,
                        'market_value': 45000.00,
                        'cost_basis': 40000.00,
                        'unrealized_pnl': 5000.00,
                        'unrealized_pnl_percent': 12.5,
                        'day_change': 750.00,
                        'day_change_percent': 1.69
                    }
                ]
            
            # Add allocations if requested
            if request.include_allocations:
                portfolio['allocations'] = {
                    'by_asset': [
                        {'asset': 'Cryptocurrency', 'value': 112500.50, 'percentage': 90.0},
                        {'asset': 'Cash', 'value': 12500.00, 'percentage': 10.0}
                    ],
                    'by_sector': [
                        {'sector': 'Digital Assets', 'value': 112500.50, 'percentage': 90.0},
                        {'sector': 'Cash Equivalents', 'value': 12500.00, 'percentage': 10.0}
                    ]
                }
            
            # Add performance data if requested
            if request.include_performance:
                portfolio['performance'] = {
                    'daily': {'value': 500.25, 'percent': 0.4},
                    'weekly': {'value': 1200.50, 'percent': 0.97},
                    'monthly': {'value': 3500.75, 'percent': 2.88},
                    'quarterly': {'value': 8500.25, 'percent': 7.31},
                    'yearly': {'value': 15000.50, 'percent': 13.6}
                }
            
            return portfolio
            
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_quick_portfolio_stats(self, user_id: str) -> Dict[str, Any]:
        """Get quick portfolio stats for mobile dashboard"""
        try:
            # Mock quick stats
            stats = {
                'total_value': 125000.50,
                'day_change': 500.25,
                'day_change_percent': 0.4,
                'top_gainer': {
                    'symbol': 'BTC',
                    'change_percent': 2.5
                },
                'top_loser': {
                    'symbol': 'ETH',
                    'change_percent': -0.8
                },
                'alerts_count': 2,
                'pending_orders': 1
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting quick portfolio stats: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

# Initialize services
device_service = MobileDeviceService()
notification_service = MobileNotificationService()
settings_service = MobileSettingsService()
trading_service = MobileTradingService()
watchlist_service = MobileWatchlistService()
portfolio_service = MobilePortfolioService()

# API Endpoints
@app.post("/api/v1/mobile/devices/register")
async def register_mobile_device(device_data: Dict[str, Any],
                               credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Register mobile device"""
    try:
        device = await device_service.register_device(device_data)
        
        return {
            "success": True,
            "data": {
                "device_id": device.device_id,
                "registered_at": device.registered_at.isoformat(),
                "biometric_enabled": device.biometric_enabled
            }
        }
        
    except Exception as e:
        logger.error(f"Error in device registration endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/mobile/devices/{device_id}/biometric")
async def enable_device_biometric(device_id: str, biometric_type: BiometricType,
                                biometric_token: str,
                                credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Enable biometric authentication for device"""
    try:
        result = await device_service.enable_biometric(device_id, biometric_type, biometric_token)
        
        return {
            "success": True,
            "data": {
                "device_id": device_id,
                "biometric_enabled": result,
                "biometric_type": biometric_type
            }
        }
        
    except Exception as e:
        logger.error(f"Error in biometric enable endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/mobile/notifications/send")
async def send_mobile_notification(request: MobileNotificationRequest,
                                 credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Send mobile notification"""
    try:
        result = await notification_service.send_notification(request)
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error in notification endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/mobile/settings")
async def get_mobile_settings(user_id: str,
                            credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get mobile settings"""
    try:
        settings = await settings_service.get_settings(user_id)
        
        return {
            "success": True,
            "data": settings.dict()
        }
        
    except Exception as e:
        logger.error(f"Error in get settings endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/mobile/settings")
async def update_mobile_settings(user_id: str, settings_update: Dict[str, Any],
                               credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update mobile settings"""
    try:
        settings = await settings_service.update_settings(user_id, settings_update)
        
        return {
            "success": True,
            "data": settings.dict()
        }
        
    except Exception as e:
        logger.error(f"Error in update settings endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/mobile/trade")
async def execute_mobile_trade(request: MobileTradeRequest,
                             credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Execute mobile trade"""
    try:
        result = await trading_service.execute_mobile_trade(request)
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error in mobile trade endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/mobile/watchlist")
async def get_mobile_watchlist(user_id: str,
                              credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get mobile watchlist"""
    try:
        watchlist = await watchlist_service.get_watchlist(user_id)
        
        return {
            "success": True,
            "data": [item.dict() for item in watchlist]
        }
        
    except Exception as e:
        logger.error(f"Error in watchlist endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/mobile/watchlist/add")
async def add_to_watchlist(user_id: str, symbol: str,
                         credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Add symbol to watchlist"""
    try:
        item = await watchlist_service.add_to_watchlist(user_id, symbol)
        
        return {
            "success": True,
            "data": item.dict()
        }
        
    except Exception as e:
        logger.error(f"Error in add to watchlist endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/mobile/portfolio/summary")
async def get_portfolio_summary(request: MobilePortfolioRequest,
                              credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get portfolio summary"""
    try:
        summary = await portfolio_service.get_portfolio_summary(request)
        
        return {
            "success": True,
            "data": summary
        }
        
    except Exception as e:
        logger.error(f"Error in portfolio summary endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/mobile/portfolio/quick-stats")
async def get_quick_portfolio_stats(user_id: str,
                                   credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get quick portfolio stats"""
    try:
        stats = await portfolio_service.get_quick_portfolio_stats(user_id)
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Error in quick stats endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/mobile/dashboard")
async def get_mobile_dashboard(user_id: str,
                              credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get mobile dashboard data"""
    try:
        # Get all dashboard components
        portfolio_stats = await portfolio_service.get_quick_portfolio_stats(user_id)
        watchlist = await watchlist_service.get_watchlist(user_id)
        recent_trades = await trading_service.get_recent_trades(user_id, limit=5)
        
        dashboard = {
            'portfolio': portfolio_stats,
            'watchlist': [item.dict() for item in watchlist[:8]],  # Top 8 items
            'recent_trades': recent_trades,
            'market_summary': {
                'market_status': 'open',
                'major_indices': [
                    {'name': 'S&P 500', 'value': 4500.25, 'change': 0.5},
                    {'name': 'NASDAQ', 'value': 14000.75, 'change': 0.8},
                    {'name': 'DOW', 'value': 35000.50, 'change': 0.3}
                ],
                'crypto_market': {
                    'total_market_cap': 1.8e12,
                    'dominance': {'BTC': 52.5, 'ETH': 18.2},
                    'fear_greed': 68
                }
            },
            'notifications': {
                'unread_count': 3,
                'price_alerts': 2,
                'trade_confirmations': 1
            }
        }
        
        return {
            "success": True,
            "data": dashboard
        }
        
    except Exception as e:
        logger.error(f"Error in mobile dashboard endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "enhanced-mobile-features"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8014)