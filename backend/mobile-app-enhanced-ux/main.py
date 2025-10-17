#!/usr/bin/env python3
"""
Mobile App Enhanced UX Service
Next-generation mobile trading experience with advanced features
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
import uuid
import logging
import os
import asyncio
import aioredis
import json
from decimal import Decimal
import numpy as np

# FastAPI app
app = FastAPI(
    title="TigerEx Mobile App Enhanced UX",
    description="Next-generation mobile trading experience with advanced features",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/tigerex_mobile")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Models
class MobileUser(Base):
    __tablename__ = "mobile_users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, unique=True)
    
    # Device information
    device_id = Column(String, nullable=False)
    device_type = Column(String, nullable=False)  # ios, android
    device_model = Column(String)
    os_version = Column(String)
    app_version = Column(String, default="2.0.0")
    
    # User preferences
    theme = Column(String, default="dark")  # dark, light, auto
    language = Column(String, default="en")
    currency = Column(String, default="USD")
    
    # Notification preferences
    push_notifications = Column(Boolean, default=True)
    price_alerts = Column(Boolean, default=True)
    trade_notifications = Column(Boolean, default=True)
    news_notifications = Column(Boolean, default=False)
    
    # Biometric settings
    biometric_enabled = Column(Boolean, default=False)
    biometric_type = Column(String)  # fingerprint, face_id, voice
    
    # Trading preferences
    default_order_type = Column(String, default="market")
    quick_trade_amounts = Column(JSON, default=lambda: [10, 50, 100, 500, 1000])
    favorite_pairs = Column(JSON, default=list)
    
    # UI customization
    dashboard_layout = Column(JSON)
    widget_preferences = Column(JSON)
    chart_settings = Column(JSON)
    
    # Accessibility
    font_size = Column(String, default="medium")  # small, medium, large, xl
    high_contrast = Column(Boolean, default=False)
    voice_over = Column(Boolean, default=False)
    
    # Performance settings
    real_time_updates = Column(Boolean, default=True)
    data_saver_mode = Column(Boolean, default=False)
    offline_mode = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)

class MobileSession(Base):
    __tablename__ = "mobile_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    device_id = Column(String, nullable=False)
    
    # Session details
    session_token = Column(String, nullable=False, unique=True)
    refresh_token = Column(String, nullable=False)
    
    # Session metadata
    ip_address = Column(String)
    location = Column(JSON)
    user_agent = Column(String)
    
    # Session status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow)

class PushNotification(Base):
    __tablename__ = "push_notifications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    
    # Notification details
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    notification_type = Column(String, nullable=False)  # price_alert, trade, news, system
    
    # Targeting
    device_tokens = Column(JSON)  # List of device tokens
    
    # Content
    data = Column(JSON)  # Additional data payload
    image_url = Column(String)
    action_url = Column(String)
    
    # Delivery
    status = Column(String, default="pending")  # pending, sent, delivered, failed
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    
    # Interaction
    opened = Column(Boolean, default=False)
    clicked = Column(Boolean, default=False)
    opened_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class PriceAlert(Base):
    __tablename__ = "price_alerts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    
    # Alert details
    symbol = Column(String, nullable=False)
    alert_type = Column(String, nullable=False)  # price_above, price_below, price_change, volume
    
    # Conditions
    target_price = Column(Float)
    percentage_change = Column(Float)
    volume_threshold = Column(Float)
    
    # Status
    is_active = Column(Boolean, default=True)
    triggered = Column(Boolean, default=False)
    triggered_at = Column(DateTime)
    
    # Notification settings
    push_notification = Column(Boolean, default=True)
    email_notification = Column(Boolean, default=False)
    sms_notification = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class QuickTrade(Base):
    __tablename__ = "quick_trades"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    
    # Trade details
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)  # buy, sell
    amount = Column(Float, nullable=False)
    order_type = Column(String, default="market")
    
    # Execution
    executed_price = Column(Float)
    executed_at = Column(DateTime)
    status = Column(String, default="pending")  # pending, executed, failed, cancelled
    
    # Mobile specific
    executed_from_widget = Column(Boolean, default=False)
    one_tap_trade = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class MobileAnalytics(Base):
    __tablename__ = "mobile_analytics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    
    # Event details
    event_type = Column(String, nullable=False)  # screen_view, button_click, trade_executed, etc.
    event_name = Column(String, nullable=False)
    
    # Event data
    properties = Column(JSON)
    
    # Session context
    session_id = Column(String)
    screen_name = Column(String)
    
    # Device context
    device_type = Column(String)
    app_version = Column(String)
    
    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow)
    duration = Column(Float)  # For timed events

class OfflineData(Base):
    __tablename__ = "offline_data"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    
    # Data details
    data_type = Column(String, nullable=False)  # portfolio, watchlist, recent_trades, market_data
    data_content = Column(JSON, nullable=False)
    
    # Sync status
    is_synced = Column(Boolean, default=False)
    sync_priority = Column(Integer, default=1)  # 1=high, 2=medium, 3=low
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    synced_at = Column(DateTime)
    expires_at = Column(DateTime)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class MobileUserCreate(BaseModel):
    user_id: str
    device_id: str
    device_type: str
    device_model: Optional[str] = None
    os_version: Optional[str] = None

class MobileUserUpdate(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    currency: Optional[str] = None
    push_notifications: Optional[bool] = None
    price_alerts: Optional[bool] = None
    trade_notifications: Optional[bool] = None
    biometric_enabled: Optional[bool] = None
    biometric_type: Optional[str] = None
    default_order_type: Optional[str] = None
    quick_trade_amounts: Optional[List[float]] = None
    favorite_pairs: Optional[List[str]] = None
    dashboard_layout: Optional[Dict[str, Any]] = None
    font_size: Optional[str] = None
    high_contrast: Optional[bool] = None
    real_time_updates: Optional[bool] = None
    data_saver_mode: Optional[bool] = None

class PushNotificationCreate(BaseModel):
    user_id: str
    title: str
    body: str
    notification_type: str
    data: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None
    action_url: Optional[str] = None

class PriceAlertCreate(BaseModel):
    symbol: str
    alert_type: str
    target_price: Optional[float] = None
    percentage_change: Optional[float] = None
    volume_threshold: Optional[float] = None
    push_notification: bool = True
    email_notification: bool = False
    sms_notification: bool = False

class QuickTradeCreate(BaseModel):
    symbol: str
    side: str
    amount: float
    order_type: str = "market"
    executed_from_widget: bool = False
    one_tap_trade: bool = False

class AnalyticsEvent(BaseModel):
    event_type: str
    event_name: str
    properties: Optional[Dict[str, Any]] = None
    screen_name: Optional[str] = None
    duration: Optional[float] = None

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions
async def get_redis():
    return await aioredis.from_url(REDIS_URL)

async def send_push_notification(notification: PushNotification) -> bool:
    """Send push notification to device"""
    try:
        # Mock push notification sending
        # In production, integrate with FCM (Android) and APNs (iOS)
        
        logger.info(f"Sending push notification to user {notification.user_id}: {notification.title}")
        
        # Update notification status
        notification.status = "sent"
        notification.sent_at = datetime.utcnow()
        
        # Simulate delivery
        await asyncio.sleep(1)
        notification.status = "delivered"
        notification.delivered_at = datetime.utcnow()
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to send push notification: {e}")
        notification.status = "failed"
        return False

def check_price_alerts(symbol: str, current_price: float, db: Session):
    """Check and trigger price alerts"""
    alerts = db.query(PriceAlert).filter(
        PriceAlert.symbol == symbol,
        PriceAlert.is_active == True,
        PriceAlert.triggered == False
    ).all()
    
    for alert in alerts:
        triggered = False
        
        if alert.alert_type == "price_above" and current_price >= alert.target_price:
            triggered = True
        elif alert.alert_type == "price_below" and current_price <= alert.target_price:
            triggered = True
        elif alert.alert_type == "price_change":
            # Would need historical price to calculate percentage change
            pass
        
        if triggered:
            alert.triggered = True
            alert.triggered_at = datetime.utcnow()
            
            # Send notification
            if alert.push_notification:
                notification = PushNotification(
                    user_id=alert.user_id,
                    title=f"Price Alert: {symbol}",
                    body=f"{symbol} has reached ${current_price:.2f}",
                    notification_type="price_alert",
                    data={
                        "symbol": symbol,
                        "price": current_price,
                        "alert_id": alert.id
                    }
                )
                db.add(notification)
    
    db.commit()

def generate_dashboard_layout(user_preferences: Dict[str, Any]) -> Dict[str, Any]:
    """Generate personalized dashboard layout"""
    default_layout = {
        "sections": [
            {
                "id": "portfolio_summary",
                "type": "portfolio",
                "position": 0,
                "visible": True,
                "size": "large"
            },
            {
                "id": "watchlist",
                "type": "watchlist",
                "position": 1,
                "visible": True,
                "size": "medium"
            },
            {
                "id": "quick_trade",
                "type": "quick_trade",
                "position": 2,
                "visible": True,
                "size": "small"
            },
            {
                "id": "market_overview",
                "type": "market",
                "position": 3,
                "visible": True,
                "size": "medium"
            },
            {
                "id": "recent_trades",
                "type": "trades",
                "position": 4,
                "visible": True,
                "size": "small"
            },
            {
                "id": "news_feed",
                "type": "news",
                "position": 5,
                "visible": False,
                "size": "small"
            }
        ],
        "theme": user_preferences.get("theme", "dark"),
        "layout_type": "grid"
    }
    
    return default_layout

# API Routes

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mobile-app-enhanced-ux"}

# User management
@app.post("/users")
async def create_mobile_user(user: MobileUserCreate, db: Session = Depends(get_db)):
    """Create mobile user profile"""
    # Check if user already exists
    existing = db.query(MobileUser).filter(MobileUser.user_id == user.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Mobile user already exists")
    
    # Generate default dashboard layout
    dashboard_layout = generate_dashboard_layout({})
    
    db_user = MobileUser(
        **user.dict(),
        dashboard_layout=dashboard_layout,
        widget_preferences={
            "show_portfolio_chart": True,
            "show_price_changes": True,
            "show_volume": False,
            "compact_view": False
        },
        chart_settings={
            "default_timeframe": "1D",
            "chart_type": "candlestick",
            "indicators": ["MA", "RSI"],
            "drawing_tools": True
        }
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.get("/users/{user_id}")
async def get_mobile_user(user_id: str, db: Session = Depends(get_db)):
    """Get mobile user profile"""
    user = db.query(MobileUser).filter(MobileUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Mobile user not found")
    
    # Update last active
    user.last_active = datetime.utcnow()
    db.commit()
    
    return user

@app.put("/users/{user_id}")
async def update_mobile_user(
    user_id: str,
    user_update: MobileUserUpdate,
    db: Session = Depends(get_db)
):
    """Update mobile user preferences"""
    user = db.query(MobileUser).filter(MobileUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Mobile user not found")
    
    # Update fields
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return user

# Dashboard and layout
@app.get("/users/{user_id}/dashboard")
async def get_dashboard_data(user_id: str, db: Session = Depends(get_db)):
    """Get personalized dashboard data"""
    user = db.query(MobileUser).filter(MobileUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Mobile user not found")
    
    # Mock dashboard data
    dashboard_data = {
        "layout": user.dashboard_layout,
        "data": {
            "portfolio_summary": {
                "total_value": 12500.75,
                "daily_pnl": 245.30,
                "daily_pnl_percentage": 2.01,
                "positions": 8
            },
            "watchlist": [
                {"symbol": "BTCUSDT", "price": 43250.50, "change": 2.15},
                {"symbol": "ETHUSDT", "price": 2650.25, "change": -1.05},
                {"symbol": "ADAUSDT", "price": 0.485, "change": 3.25}
            ],
            "market_overview": {
                "total_market_cap": "2.1T",
                "btc_dominance": 52.3,
                "fear_greed_index": 65,
                "trending": ["BTC", "ETH", "SOL", "ADA"]
            },
            "recent_trades": [
                {"symbol": "BTCUSDT", "side": "buy", "amount": 0.1, "price": 43200, "time": "2 min ago"},
                {"symbol": "ETHUSDT", "side": "sell", "amount": 2.5, "price": 2655, "time": "15 min ago"}
            ]
        }
    }
    
    return dashboard_data

@app.post("/users/{user_id}/dashboard/layout")
async def update_dashboard_layout(
    user_id: str,
    layout: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Update dashboard layout"""
    user = db.query(MobileUser).filter(MobileUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Mobile user not found")
    
    user.dashboard_layout = layout
    user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Dashboard layout updated successfully"}

# Push notifications
@app.post("/notifications")
async def create_push_notification(
    notification: PushNotificationCreate,
    db: Session = Depends(get_db)
):
    """Create and send push notification"""
    # Get user's device tokens
    user = db.query(MobileUser).filter(MobileUser.user_id == notification.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.push_notifications:
        raise HTTPException(status_code=400, detail="Push notifications disabled for user")
    
    # Create notification
    db_notification = PushNotification(
        **notification.dict(),
        device_tokens=[user.device_id]  # Simplified
    )
    
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    
    # Send notification
    success = await send_push_notification(db_notification)
    db.commit()
    
    return {
        "notification": db_notification,
        "sent": success
    }

@app.get("/notifications/{user_id}")
async def get_user_notifications(
    user_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get user's notifications"""
    notifications = db.query(PushNotification).filter(
        PushNotification.user_id == user_id
    ).order_by(PushNotification.created_at.desc()).limit(limit).all()
    
    return notifications

@app.post("/notifications/{notification_id}/opened")
async def mark_notification_opened(
    notification_id: str,
    db: Session = Depends(get_db)
):
    """Mark notification as opened"""
    notification = db.query(PushNotification).filter(
        PushNotification.id == notification_id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.opened = True
    notification.opened_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Notification marked as opened"}

# Price alerts
@app.post("/alerts/{user_id}")
async def create_price_alert(
    user_id: str,
    alert: PriceAlertCreate,
    db: Session = Depends(get_db)
):
    """Create price alert"""
    db_alert = PriceAlert(
        user_id=user_id,
        **alert.dict()
    )
    
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    return db_alert

@app.get("/alerts/{user_id}")
async def get_user_alerts(user_id: str, db: Session = Depends(get_db)):
    """Get user's price alerts"""
    alerts = db.query(PriceAlert).filter(
        PriceAlert.user_id == user_id,
        PriceAlert.is_active == True
    ).all()
    
    return alerts

@app.delete("/alerts/{alert_id}")
async def delete_price_alert(alert_id: str, db: Session = Depends(get_db)):
    """Delete price alert"""
    alert = db.query(PriceAlert).filter(PriceAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_active = False
    db.commit()
    
    return {"message": "Alert deleted successfully"}

# Quick trading
@app.post("/quick-trade/{user_id}")
async def execute_quick_trade(
    user_id: str,
    trade: QuickTradeCreate,
    db: Session = Depends(get_db)
):
    """Execute quick trade"""
    # Create quick trade record
    db_trade = QuickTrade(
        user_id=user_id,
        **trade.dict()
    )
    
    # Mock execution
    db_trade.executed_price = 43250.50 if trade.symbol == "BTCUSDT" else 2650.25
    db_trade.executed_at = datetime.utcnow()
    db_trade.status = "executed"
    
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    
    # Send confirmation notification
    notification = PushNotification(
        user_id=user_id,
        title="Trade Executed",
        body=f"{trade.side.upper()} {trade.amount} {trade.symbol} at ${db_trade.executed_price}",
        notification_type="trade",
        data={
            "trade_id": db_trade.id,
            "symbol": trade.symbol,
            "side": trade.side,
            "amount": trade.amount,
            "price": db_trade.executed_price
        }
    )
    
    db.add(notification)
    db.commit()
    
    return db_trade

@app.get("/quick-trades/{user_id}")
async def get_user_quick_trades(
    user_id: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get user's quick trades"""
    trades = db.query(QuickTrade).filter(
        QuickTrade.user_id == user_id
    ).order_by(QuickTrade.created_at.desc()).limit(limit).all()
    
    return trades

# Analytics
@app.post("/analytics/{user_id}")
async def track_analytics_event(
    user_id: str,
    event: AnalyticsEvent,
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Track analytics event"""
    # Get user info
    user = db.query(MobileUser).filter(MobileUser.user_id == user_id).first()
    
    db_event = MobileAnalytics(
        user_id=user_id,
        session_id=session_id,
        device_type=user.device_type if user else "unknown",
        app_version=user.app_version if user else "unknown",
        **event.dict()
    )
    
    db.add(db_event)
    db.commit()
    
    return {"message": "Event tracked successfully"}

@app.get("/analytics/{user_id}/summary")
async def get_user_analytics_summary(
    user_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get user analytics summary"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    events = db.query(MobileAnalytics).filter(
        MobileAnalytics.user_id == user_id,
        MobileAnalytics.timestamp >= start_date
    ).all()
    
    # Analyze events
    event_counts = {}
    screen_views = {}
    
    for event in events:
        event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1
        if event.event_type == "screen_view":
            screen_views[event.screen_name] = screen_views.get(event.screen_name, 0) + 1
    
    return {
        "period_days": days,
        "total_events": len(events),
        "event_counts": event_counts,
        "most_viewed_screens": sorted(screen_views.items(), key=lambda x: x[1], reverse=True)[:5],
        "daily_active": len(set(event.timestamp.date() for event in events))
    }

# Offline support
@app.post("/offline/{user_id}/sync")
async def sync_offline_data(
    user_id: str,
    offline_data: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """Sync offline data when connection restored"""
    synced_items = []
    
    for data_item in offline_data:
        db_offline = OfflineData(
            user_id=user_id,
            data_type=data_item["type"],
            data_content=data_item["content"],
            sync_priority=data_item.get("priority", 2),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        db.add(db_offline)
        synced_items.append(db_offline.id)
    
    db.commit()
    
    return {
        "synced_items": len(synced_items),
        "item_ids": synced_items
    }

@app.get("/offline/{user_id}/data")
async def get_offline_data(user_id: str, db: Session = Depends(get_db)):
    """Get cached data for offline use"""
    # Mock offline data
    offline_data = {
        "portfolio": {
            "positions": [
                {"symbol": "BTCUSDT", "amount": 0.5, "value": 21625.25},
                {"symbol": "ETHUSDT", "amount": 10, "value": 26502.50}
            ],
            "total_value": 48127.75,
            "cached_at": datetime.utcnow().isoformat()
        },
        "watchlist": [
            {"symbol": "BTCUSDT", "price": 43250.50, "change": 2.15},
            {"symbol": "ETHUSDT", "price": 2650.25, "change": -1.05}
        ],
        "recent_trades": [
            {"symbol": "BTCUSDT", "side": "buy", "amount": 0.1, "price": 43200, "time": "2 min ago"}
        ]
    }
    
    return offline_data

# Biometric authentication
@app.post("/biometric/{user_id}/setup")
async def setup_biometric_auth(
    user_id: str,
    biometric_type: str,
    biometric_data: str,  # Encrypted biometric template
    db: Session = Depends(get_db)
):
    """Setup biometric authentication"""
    user = db.query(MobileUser).filter(MobileUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.biometric_enabled = True
    user.biometric_type = biometric_type
    user.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Biometric authentication setup successfully"}

@app.post("/biometric/{user_id}/verify")
async def verify_biometric_auth(
    user_id: str,
    biometric_data: str,
    db: Session = Depends(get_db)
):
    """Verify biometric authentication"""
    user = db.query(MobileUser).filter(MobileUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.biometric_enabled:
        raise HTTPException(status_code=400, detail="Biometric authentication not enabled")
    
    # Mock biometric verification
    verification_success = True  # In production, verify against stored template
    
    return {
        "verified": verification_success,
        "biometric_type": user.biometric_type
    }

# App performance
@app.get("/performance/{user_id}")
async def get_app_performance_metrics(user_id: str, db: Session = Depends(get_db)):
    """Get app performance metrics for user"""
    user = db.query(MobileUser).filter(MobileUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Mock performance metrics
    performance_metrics = {
        "app_launch_time": 1.2,  # seconds
        "screen_load_times": {
            "dashboard": 0.8,
            "trading": 1.1,
            "portfolio": 0.9,
            "market": 1.0
        },
        "api_response_times": {
            "portfolio": 150,  # ms
            "market_data": 80,
            "trade_execution": 200
        },
        "memory_usage": 85.5,  # MB
        "battery_impact": "low",
        "crash_rate": 0.001,  # 0.1%
        "data_usage": {
            "daily_average": 2.5,  # MB
            "real_time_updates": 1.8,
            "chart_data": 0.7
        }
    }
    
    return performance_metrics

# WebSocket for real-time updates
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    
    try:
        while True:
            # Send real-time updates
            update_data = {
                "type": "price_update",
                "data": {
                    "BTCUSDT": 43250.50 + np.random.uniform(-100, 100),
                    "ETHUSDT": 2650.25 + np.random.uniform(-50, 50)
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await websocket.send_text(json.dumps(update_data))
            await asyncio.sleep(1)  # Send updates every second
            
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks"""
    logger.info("Mobile App Enhanced UX service started")
    
    # Start background tasks
    asyncio.create_task(periodic_price_alert_check())
    asyncio.create_task(periodic_notification_cleanup())

async def periodic_price_alert_check():
    """Check price alerts periodically"""
    while True:
        try:
            db = SessionLocal()
            
            # Mock price updates
            price_updates = {
                "BTCUSDT": 43250.50 + np.random.uniform(-500, 500),
                "ETHUSDT": 2650.25 + np.random.uniform(-100, 100),
                "ADAUSDT": 0.485 + np.random.uniform(-0.02, 0.02)
            }
            
            for symbol, price in price_updates.items():
                check_price_alerts(symbol, price, db)
            
            db.close()
            await asyncio.sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            logger.error(f"Error checking price alerts: {e}")
            await asyncio.sleep(60)

async def periodic_notification_cleanup():
    """Clean up old notifications"""
    while True:
        try:
            db = SessionLocal()
            
            # Delete notifications older than 30 days
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            old_notifications = db.query(PushNotification).filter(
                PushNotification.created_at < cutoff_date
            ).delete()
            
            db.commit()
            db.close()
            
            if old_notifications > 0:
                logger.info(f"Cleaned up {old_notifications} old notifications")
            
            await asyncio.sleep(86400)  # Clean up daily
            
        except Exception as e:
            logger.error(f"Error cleaning up notifications: {e}")
            await asyncio.sleep(3600)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8087)