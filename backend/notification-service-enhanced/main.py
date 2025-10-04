import os
"""
TigerEx Enhanced Notification Service
Multi-channel notifications: Email, SMS, Push, In-App
"""

from fastapi import FastAPI
from admin.admin_routes import router as admin_router
from fastapi import HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from decimal import Decimal
import asyncpg
import structlog
from enum import Enum
import json
import asyncio

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

app = FastAPI(title="TigerEx Enhanced Notification Service", version="1.0.0")

# Include admin router
app.include_router(admin_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection pool
db_pool: Optional[asyncpg.Pool] = None

# Enums
class NotificationType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"

class NotificationCategory(str, Enum):
    SECURITY = "security"
    TRADING = "trading"
    ACCOUNT = "account"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    KYC = "kyc"
    PROMOTION = "promotion"
    SYSTEM = "system"

class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"

# Models
class NotificationRequest(BaseModel):
    user_id: int
    notification_type: NotificationType
    category: NotificationCategory
    priority: NotificationPriority = NotificationPriority.MEDIUM
    title: str
    message: str
    data: Optional[Dict] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class Notification(BaseModel):
    notification_id: int
    user_id: int
    notification_type: str
    category: str
    priority: str
    title: str
    message: str
    status: str
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    created_at: datetime

class NotificationPreferences(BaseModel):
    user_id: int
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = True
    in_app_enabled: bool = True
    security_alerts: bool = True
    trading_alerts: bool = True
    deposit_alerts: bool = True
    withdrawal_alerts: bool = True
    kyc_alerts: bool = True
    promotion_alerts: bool = False

class NotificationTemplate(BaseModel):
    template_id: int
    name: str
    category: str
    subject: str
    body: str
    variables: List[str]

# Database functions
async def get_db():
    return db_pool

async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(
        host="localhost",
        port=5432,
        user="tigerex",
        password="tigerex_secure_password",
        database="tigerex_notifications",
        min_size=10,
        max_size=50
    )
    
    async with db_pool.acquire() as conn:
        # Create notifications table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                notification_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                notification_type VARCHAR(20) NOT NULL,
                category VARCHAR(50) NOT NULL,
                priority VARCHAR(20) NOT NULL,
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                data JSONB,
                status VARCHAR(20) DEFAULT 'pending',
                sent_at TIMESTAMP,
                delivered_at TIMESTAMP,
                read_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_notifications (user_id, created_at DESC),
                INDEX idx_status (status),
                INDEX idx_category (category)
            )
        """)
        
        # Create notification preferences table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS notification_preferences (
                preference_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL UNIQUE,
                email_enabled BOOLEAN DEFAULT TRUE,
                sms_enabled BOOLEAN DEFAULT FALSE,
                push_enabled BOOLEAN DEFAULT TRUE,
                in_app_enabled BOOLEAN DEFAULT TRUE,
                security_alerts BOOLEAN DEFAULT TRUE,
                trading_alerts BOOLEAN DEFAULT TRUE,
                deposit_alerts BOOLEAN DEFAULT TRUE,
                withdrawal_alerts BOOLEAN DEFAULT TRUE,
                kyc_alerts BOOLEAN DEFAULT TRUE,
                promotion_alerts BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_prefs (user_id)
            )
        """)
        
        # Create notification templates table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS notification_templates (
                template_id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                category VARCHAR(50) NOT NULL,
                subject VARCHAR(255) NOT NULL,
                body TEXT NOT NULL,
                variables JSONB,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_template_name (name),
                INDEX idx_category (category)
            )
        """)
        
        # Create notification logs table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS notification_logs (
                log_id SERIAL PRIMARY KEY,
                notification_id INTEGER REFERENCES notifications(notification_id),
                event VARCHAR(50) NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_notification_logs (notification_id, created_at DESC)
            )
        """)
        
        # Create email queue table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS email_queue (
                queue_id SERIAL PRIMARY KEY,
                notification_id INTEGER REFERENCES notifications(notification_id),
                to_email VARCHAR(255) NOT NULL,
                subject VARCHAR(255) NOT NULL,
                body TEXT NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                attempts INTEGER DEFAULT 0,
                last_attempt TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_email_status (status, created_at)
            )
        """)
        
        # Insert default templates
        await conn.execute("""
            INSERT INTO notification_templates (name, category, subject, body, variables)
            VALUES 
                ('login_alert', 'security', 'New Login Detected', 
                 'A new login was detected on your account from {ip_address} at {login_time}. If this wasn''t you, please secure your account immediately.',
                 '["ip_address", "login_time"]'),
                ('withdrawal_request', 'withdrawal', 'Withdrawal Request Submitted',
                 'Your withdrawal request for {amount} {currency} has been submitted and is being processed. Transaction ID: {transaction_id}',
                 '["amount", "currency", "transaction_id"]'),
                ('deposit_confirmed', 'deposit', 'Deposit Confirmed',
                 'Your deposit of {amount} {currency} has been confirmed and credited to your account. Transaction ID: {transaction_id}',
                 '["amount", "currency", "transaction_id"]'),
                ('kyc_approved', 'kyc', 'KYC Verification Approved',
                 'Congratulations! Your KYC verification has been approved. You now have access to Level {kyc_level} features.',
                 '["kyc_level"]'),
                ('order_filled', 'trading', 'Order Filled',
                 'Your {side} order for {quantity} {pair} at {price} has been filled. Order ID: {order_id}',
                 '["side", "quantity", "pair", "price", "order_id"]')
            ON CONFLICT (name) DO NOTHING
        """)
        
        logger.info("Database initialized successfully")

# Notification sending functions
async def send_email_notification(notification_id: int, email: str, subject: str, body: str, db: asyncpg.Pool):
    """Send email notification"""
    try:
        # Add to email queue
        await db.execute("""
            INSERT INTO email_queue (notification_id, to_email, subject, body)
            VALUES ($1, $2, $3, $4)
        """, notification_id, email, subject, body)
        
        # In production, integrate with email service (SendGrid, AWS SES, etc.)
        # For now, just log
        logger.info("email_queued", notification_id=notification_id, email=email)
        
        # Update notification status
        await db.execute("""
            UPDATE notifications
            SET status = 'sent', sent_at = CURRENT_TIMESTAMP
            WHERE notification_id = $1
        """, notification_id)
        
        # Log event
        await db.execute("""
            INSERT INTO notification_logs (notification_id, event, details)
            VALUES ($1, 'email_sent', $2)
        """, notification_id, f"Email sent to {email}")
        
    except Exception as e:
        logger.error("send_email_failed", error=str(e))
        await db.execute("""
            UPDATE notifications SET status = 'failed' WHERE notification_id = $1
        """, notification_id)

async def send_sms_notification(notification_id: int, phone: str, message: str, db: asyncpg.Pool):
    """Send SMS notification"""
    try:
        # In production, integrate with SMS service (Twilio, AWS SNS, etc.)
        logger.info("sms_sent", notification_id=notification_id, phone=phone)
        
        await db.execute("""
            UPDATE notifications
            SET status = 'sent', sent_at = CURRENT_TIMESTAMP
            WHERE notification_id = $1
        """, notification_id)
        
        await db.execute("""
            INSERT INTO notification_logs (notification_id, event, details)
            VALUES ($1, 'sms_sent', $2)
        """, notification_id, f"SMS sent to {phone}")
        
    except Exception as e:
        logger.error("send_sms_failed", error=str(e))

async def send_push_notification(notification_id: int, user_id: int, title: str, message: str, db: asyncpg.Pool):
    """Send push notification"""
    try:
        # In production, integrate with push service (Firebase, OneSignal, etc.)
        logger.info("push_sent", notification_id=notification_id, user_id=user_id)
        
        await db.execute("""
            UPDATE notifications
            SET status = 'sent', sent_at = CURRENT_TIMESTAMP
            WHERE notification_id = $1
        """, notification_id)
        
        await db.execute("""
            INSERT INTO notification_logs (notification_id, event, details)
            VALUES ($1, 'push_sent', $2)
        """, notification_id, f"Push notification sent to user {user_id}")
        
    except Exception as e:
        logger.error("send_push_failed", error=str(e))

# API Endpoints
@app.post("/api/v1/notifications/send", response_model=Notification)
async def send_notification(
    request: NotificationRequest,
    background_tasks: BackgroundTasks,
    db: asyncpg.Pool = Depends(get_db)
):
    """Send a notification"""
    try:
        # Check user preferences
        prefs = await db.fetchrow("""
            SELECT * FROM notification_preferences WHERE user_id = $1
        """, request.user_id)
        
        # Check if notification type is enabled
        if prefs:
            type_enabled = {
                NotificationType.EMAIL: prefs['email_enabled'],
                NotificationType.SMS: prefs['sms_enabled'],
                NotificationType.PUSH: prefs['push_enabled'],
                NotificationType.IN_APP: prefs['in_app_enabled']
            }
            
            if not type_enabled.get(request.notification_type, True):
                raise HTTPException(status_code=400, detail="Notification type disabled by user")
        
        # Create notification
        notification = await db.fetchrow("""
            INSERT INTO notifications (
                user_id, notification_type, category, priority,
                title, message, data
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
        """, request.user_id, request.notification_type.value, request.category.value,
            request.priority.value, request.title, request.message, json.dumps(request.data or {}))
        
        # Send notification in background
        if request.notification_type == NotificationType.EMAIL and request.email:
            background_tasks.add_task(
                send_email_notification,
                notification['notification_id'],
                request.email,
                request.title,
                request.message,
                db
            )
        elif request.notification_type == NotificationType.SMS and request.phone:
            background_tasks.add_task(
                send_sms_notification,
                notification['notification_id'],
                request.phone,
                request.message,
                db
            )
        elif request.notification_type == NotificationType.PUSH:
            background_tasks.add_task(
                send_push_notification,
                notification['notification_id'],
                request.user_id,
                request.title,
                request.message,
                db
            )
        
        logger.info("notification_created",
                   notification_id=notification['notification_id'],
                   user_id=request.user_id,
                   type=request.notification_type.value)
        
        return Notification(
            notification_id=notification['notification_id'],
            user_id=notification['user_id'],
            notification_type=notification['notification_type'],
            category=notification['category'],
            priority=notification['priority'],
            title=notification['title'],
            message=notification['message'],
            status=notification['status'],
            sent_at=notification['sent_at'],
            delivered_at=notification['delivered_at'],
            read_at=notification['read_at'],
            created_at=notification['created_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("send_notification_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/notifications/user/{user_id}", response_model=List[Notification])
async def get_user_notifications(
    user_id: int,
    category: Optional[NotificationCategory] = None,
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get user notifications"""
    try:
        query = "SELECT * FROM notifications WHERE user_id = $1"
        params = [user_id]
        
        if category:
            query += " AND category = $2"
            params.append(category.value)
        
        if unread_only:
            query += f" AND read_at IS NULL"
        
        query += f" ORDER BY created_at DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
        params.extend([limit, offset])
        
        notifications = await db.fetch(query, *params)
        
        return [
            Notification(
                notification_id=n['notification_id'],
                user_id=n['user_id'],
                notification_type=n['notification_type'],
                category=n['category'],
                priority=n['priority'],
                title=n['title'],
                message=n['message'],
                status=n['status'],
                sent_at=n['sent_at'],
                delivered_at=n['delivered_at'],
                read_at=n['read_at'],
                created_at=n['created_at']
            )
            for n in notifications
        ]
        
    except Exception as e:
        logger.error("get_user_notifications_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    user_id: int,
    db: asyncpg.Pool = Depends(get_db)
):
    """Mark notification as read"""
    try:
        result = await db.execute("""
            UPDATE notifications
            SET read_at = CURRENT_TIMESTAMP, status = 'read'
            WHERE notification_id = $1 AND user_id = $2
        """, notification_id, user_id)
        
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Notification not found")
        
        logger.info("notification_read", notification_id=notification_id, user_id=user_id)
        return {"message": "Notification marked as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("mark_notification_read_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/notifications/user/{user_id}/read-all")
async def mark_all_read(
    user_id: int,
    db: asyncpg.Pool = Depends(get_db)
):
    """Mark all notifications as read"""
    try:
        await db.execute("""
            UPDATE notifications
            SET read_at = CURRENT_TIMESTAMP, status = 'read'
            WHERE user_id = $1 AND read_at IS NULL
        """, user_id)
        
        logger.info("all_notifications_read", user_id=user_id)
        return {"message": "All notifications marked as read"}
        
    except Exception as e:
        logger.error("mark_all_read_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/notifications/preferences/{user_id}", response_model=NotificationPreferences)
async def get_notification_preferences(
    user_id: int,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get user notification preferences"""
    try:
        prefs = await db.fetchrow("""
            SELECT * FROM notification_preferences WHERE user_id = $1
        """, user_id)
        
        if not prefs:
            # Create default preferences
            prefs = await db.fetchrow("""
                INSERT INTO notification_preferences (user_id)
                VALUES ($1)
                RETURNING *
            """, user_id)
        
        return NotificationPreferences(
            user_id=prefs['user_id'],
            email_enabled=prefs['email_enabled'],
            sms_enabled=prefs['sms_enabled'],
            push_enabled=prefs['push_enabled'],
            in_app_enabled=prefs['in_app_enabled'],
            security_alerts=prefs['security_alerts'],
            trading_alerts=prefs['trading_alerts'],
            deposit_alerts=prefs['deposit_alerts'],
            withdrawal_alerts=prefs['withdrawal_alerts'],
            kyc_alerts=prefs['kyc_alerts'],
            promotion_alerts=prefs['promotion_alerts']
        )
        
    except Exception as e:
        logger.error("get_preferences_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/notifications/preferences/{user_id}")
async def update_notification_preferences(
    user_id: int,
    preferences: NotificationPreferences,
    db: asyncpg.Pool = Depends(get_db)
):
    """Update user notification preferences"""
    try:
        await db.execute("""
            INSERT INTO notification_preferences (
                user_id, email_enabled, sms_enabled, push_enabled, in_app_enabled,
                security_alerts, trading_alerts, deposit_alerts, withdrawal_alerts,
                kyc_alerts, promotion_alerts
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            ON CONFLICT (user_id)
            DO UPDATE SET
                email_enabled = $2,
                sms_enabled = $3,
                push_enabled = $4,
                in_app_enabled = $5,
                security_alerts = $6,
                trading_alerts = $7,
                deposit_alerts = $8,
                withdrawal_alerts = $9,
                kyc_alerts = $10,
                promotion_alerts = $11,
                updated_at = CURRENT_TIMESTAMP
        """, user_id, preferences.email_enabled, preferences.sms_enabled,
            preferences.push_enabled, preferences.in_app_enabled,
            preferences.security_alerts, preferences.trading_alerts,
            preferences.deposit_alerts, preferences.withdrawal_alerts,
            preferences.kyc_alerts, preferences.promotion_alerts)
        
        logger.info("preferences_updated", user_id=user_id)
        return {"message": "Preferences updated successfully"}
        
    except Exception as e:
        logger.error("update_preferences_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/notifications/stats/{user_id}")
async def get_notification_stats(
    user_id: int,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get notification statistics for user"""
    try:
        stats = await db.fetchrow("""
            SELECT
                COUNT(*) as total_notifications,
                COUNT(CASE WHEN read_at IS NULL THEN 1 END) as unread_count,
                COUNT(CASE WHEN status = 'sent' THEN 1 END) as sent_count,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_count,
                COUNT(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' THEN 1 END) as last_24h
            FROM notifications
            WHERE user_id = $1
        """, user_id)
        
        return dict(stats)
        
    except Exception as e:
        logger.error("get_notification_stats_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "notification-service-enhanced",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.on_event("startup")
async def startup():
    """Initialize service on startup"""
    await init_db()
    logger.info("Enhanced Notification Service started")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    if db_pool:
        await db_pool.close()
    logger.info("Enhanced Notification Service stopped")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8300)