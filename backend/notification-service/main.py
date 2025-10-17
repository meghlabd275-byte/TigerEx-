#!/usr/bin/env python3
"""
TigerEx Notification Service
Real-time notification system with multiple channels (email, SMS, push, in-app)
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum

import smtplib
import ssl
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders

import aioredis
import asyncpg
import aiohttp
import websockets
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket
from admin.admin_routes import router as admin_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import jwt
from twilio.rest import Client as TwilioClient
import firebase_admin
from firebase_admin import credentials, messaging
from jinja2 import Environment, FileSystemLoader
import boto3
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Notification Types and Channels
class NotificationType(str, Enum):
    TRADE_EXECUTED = "trade_executed"
    ORDER_FILLED = "order_filled"
    ORDER_CANCELLED = "order_cancelled"
    DEPOSIT_CONFIRMED = "deposit_confirmed"
    WITHDRAWAL_PROCESSED = "withdrawal_processed"
    KYC_APPROVED = "kyc_approved"
    KYC_REJECTED = "kyc_rejected"
    SECURITY_ALERT = "security_alert"
    PRICE_ALERT = "price_alert"
    MARGIN_CALL = "margin_call"
    LIQUIDATION_WARNING = "liquidation_warning"
    P2P_TRADE_REQUEST = "p2p_trade_request"
    P2P_PAYMENT_RECEIVED = "p2p_payment_received"
    COPY_TRADE_SIGNAL = "copy_trade_signal"
    SYSTEM_MAINTENANCE = "system_maintenance"
    PROMOTIONAL = "promotional"
    NEWS_UPDATE = "news_update"

class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"
    TELEGRAM = "telegram"
    DISCORD = "discord"

class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"

# Models
@dataclass
class NotificationTemplate:
    id: str
    name: str
    type: NotificationType
    channel: NotificationChannel
    subject_template: str
    body_template: str
    variables: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

@dataclass
class Notification:
    id: str
    user_id: str
    type: NotificationType
    channel: NotificationChannel
    priority: NotificationPriority
    title: str
    message: str
    data: Dict[str, Any]
    status: NotificationStatus
    scheduled_at: Optional[datetime]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    retry_count: int
    max_retries: int
    created_at: datetime
    updated_at: datetime

@dataclass
class UserPreferences:
    user_id: str
    email_enabled: bool
    sms_enabled: bool
    push_enabled: bool
    in_app_enabled: bool
    notification_types: Dict[NotificationType, bool]
    quiet_hours_start: Optional[str]
    quiet_hours_end: Optional[str]
    timezone: str
    language: str

# Request Models
class SendNotificationRequest(BaseModel):
    user_id: str
    type: NotificationType
    channel: NotificationChannel
    priority: NotificationPriority = NotificationPriority.MEDIUM
    title: str
    message: str
    data: Dict[str, Any] = {}
    scheduled_at: Optional[datetime] = None

class BulkNotificationRequest(BaseModel):
    user_ids: List[str]
    type: NotificationType
    channels: List[NotificationChannel]
    priority: NotificationPriority = NotificationPriority.MEDIUM
    title: str
    message: str
    data: Dict[str, Any] = {}
    scheduled_at: Optional[datetime] = None

class UpdatePreferencesRequest(BaseModel):
    email_enabled: bool = True
    sms_enabled: bool = True
    push_enabled: bool = True
    in_app_enabled: bool = True
    notification_types: Dict[str, bool] = {}
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"

class NotificationService:
    def __init__(self):
        self.app = FastAPI(title="TigerEx Notification Service", version="1.0.0")

# Include admin router
app.include_router(admin_router)

class NotificationService:
    def __init__(self):
        self.setup_middleware()
        self.setup_routes()
        
        # Database connections
        self.db_pool = None
        self.redis_client = None
        
        # External service clients
        self.smtp_client = None
        self.twilio_client = None
        self.firebase_app = None
        self.ses_client = None
        
        # Template engine
        self.template_env = Environment(loader=FileSystemLoader('templates'))
        
        # WebSocket connections
        self.websocket_connections: Dict[str, WebSocket] = {}
        
        # Background tasks
        self.notification_queue = asyncio.Queue()
        self.retry_queue = asyncio.Queue()
        
    async def startup(self):
        """Initialize service on startup"""
        await self.connect_databases()
        await self.initialize_external_services()
        await self.start_background_workers()
        logger.info("Notification Service started successfully")
    
    async def connect_databases(self):
        """Connect to PostgreSQL and Redis"""
        try:
            self.db_pool = await asyncpg.create_pool(
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', 5432)),
                user=os.getenv('DB_USER', 'tigerex'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME', 'tigerex'),
                min_size=10,
                max_size=20
            )
            
            self.redis_client = aioredis.from_url(
                f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}",
                password=os.getenv('REDIS_PASSWORD'),
                decode_responses=True
            )
            
            logger.info("Database connections established")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    async def initialize_external_services(self):
        """Initialize external notification services"""
        try:
            # Initialize Twilio for SMS
            if os.getenv('TWILIO_ACCOUNT_SID') and os.getenv('TWILIO_AUTH_TOKEN'):
                self.twilio_client = TwilioClient(
                    os.getenv('TWILIO_ACCOUNT_SID'),
                    os.getenv('TWILIO_AUTH_TOKEN')
                )
            
            # Initialize Firebase for push notifications
            if os.getenv('FIREBASE_CREDENTIALS_PATH'):
                cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS_PATH'))
                self.firebase_app = firebase_admin.initialize_app(cred)
            
            # Initialize AWS SES for email
            if os.getenv('AWS_ACCESS_KEY_ID'):
                self.ses_client = boto3.client(
                    'ses',
                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                    region_name=os.getenv('AWS_REGION', 'us-east-1')
                )
            
            logger.info("External services initialized")
        except Exception as e:
            logger.error(f"External services initialization failed: {e}")
    
    async def start_background_workers(self):
        """Start background worker tasks"""
        # Start notification processor
        asyncio.create_task(self.process_notification_queue())
        
        # Start retry processor
        asyncio.create_task(self.process_retry_queue())
        
        # Start scheduled notification checker
        asyncio.create_task(self.check_scheduled_notifications())
        
        # Start cleanup task
        asyncio.create_task(self.cleanup_old_notifications())
    
    def setup_middleware(self):
        """Setup FastAPI middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "service": "notification-service"}
        
        @self.app.post("/api/v1/notifications/send")
        async def send_notification(
            request: SendNotificationRequest,
            background_tasks: BackgroundTasks,
            user_id: str = Depends(self.get_current_user)
        ):
            return await self.send_single_notification(request, background_tasks)
        
        @self.app.post("/api/v1/notifications/bulk")
        async def send_bulk_notification(
            request: BulkNotificationRequest,
            background_tasks: BackgroundTasks,
            admin_id: str = Depends(self.get_admin_user)
        ):
            return await self.send_bulk_notifications(request, background_tasks)
        
        @self.app.get("/api/v1/notifications/user/{user_id}")
        async def get_user_notifications(
            user_id: str,
            page: int = 1,
            limit: int = 20,
            unread_only: bool = False,
            current_user: str = Depends(self.get_current_user)
        ):
            return await self.get_notifications_for_user(user_id, page, limit, unread_only)
        
        @self.app.put("/api/v1/notifications/{notification_id}/read")
        async def mark_notification_read(
            notification_id: str,
            user_id: str = Depends(self.get_current_user)
        ):
            return await self.mark_as_read(notification_id, user_id)
        
        @self.app.put("/api/v1/notifications/mark-all-read")
        async def mark_all_notifications_read(
            user_id: str = Depends(self.get_current_user)
        ):
            return await self.mark_all_as_read(user_id)
        
        @self.app.get("/api/v1/notifications/preferences/{user_id}")
        async def get_notification_preferences(
            user_id: str,
            current_user: str = Depends(self.get_current_user)
        ):
            return await self.get_user_preferences(user_id)
        
        @self.app.put("/api/v1/notifications/preferences/{user_id}")
        async def update_notification_preferences(
            user_id: str,
            request: UpdatePreferencesRequest,
            current_user: str = Depends(self.get_current_user)
        ):
            return await self.update_user_preferences(user_id, request)
        
        @self.app.websocket("/api/v1/notifications/ws/{user_id}")
        async def websocket_endpoint(websocket: WebSocket, user_id: str):
            await self.handle_websocket_connection(websocket, user_id)
        
        @self.app.get("/api/v1/notifications/templates")
        async def get_notification_templates(
            admin_id: str = Depends(self.get_admin_user)
        ):
            return await self.get_templates()
        
        @self.app.post("/api/v1/notifications/templates")
        async def create_notification_template(
            template_data: dict,
            admin_id: str = Depends(self.get_admin_user)
        ):
            return await self.create_template(template_data)
        
        @self.app.get("/api/v1/notifications/analytics")
        async def get_notification_analytics(
            admin_id: str = Depends(self.get_admin_user),
            start_date: Optional[str] = None,
            end_date: Optional[str] = None
        ):
            return await self.get_analytics(start_date, end_date)
    
    async def send_single_notification(
        self, 
        request: SendNotificationRequest, 
        background_tasks: BackgroundTasks
    ) -> Dict[str, Any]:
        """Send a single notification"""
        try:
            # Check user preferences
            preferences = await self.get_user_preferences(request.user_id)
            if not self.should_send_notification(request, preferences):
                return {
                    "notification_id": None,
                    "status": "skipped",
                    "message": "Notification skipped due to user preferences"
                }
            
            # Create notification record
            notification_id = await self.create_notification_record(request)
            
            # Add to processing queue
            await self.notification_queue.put({
                "notification_id": notification_id,
                "request": request
            })
            
            return {
                "notification_id": notification_id,
                "status": "queued",
                "message": "Notification queued for processing"
            }
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            raise HTTPException(500, f"Failed to send notification: {str(e)}")
    
    async def send_bulk_notifications(
        self, 
        request: BulkNotificationRequest, 
        background_tasks: BackgroundTasks
    ) -> Dict[str, Any]:
        """Send bulk notifications"""
        try:
            notification_ids = []
            
            for user_id in request.user_ids:
                for channel in request.channels:
                    single_request = SendNotificationRequest(
                        user_id=user_id,
                        type=request.type,
                        channel=channel,
                        priority=request.priority,
                        title=request.title,
                        message=request.message,
                        data=request.data,
                        scheduled_at=request.scheduled_at
                    )
                    
                    # Check user preferences
                    preferences = await self.get_user_preferences(user_id)
                    if not self.should_send_notification(single_request, preferences):
                        continue
                    
                    # Create notification record
                    notification_id = await self.create_notification_record(single_request)
                    notification_ids.append(notification_id)
                    
                    # Add to processing queue
                    await self.notification_queue.put({
                        "notification_id": notification_id,
                        "request": single_request
                    })
            
            return {
                "notification_ids": notification_ids,
                "total_queued": len(notification_ids),
                "message": "Bulk notifications queued for processing"
            }
            
        except Exception as e:
            logger.error(f"Failed to send bulk notifications: {e}")
            raise HTTPException(500, f"Failed to send bulk notifications: {str(e)}")
    
    async def process_notification_queue(self):
        """Background worker to process notification queue"""
        while True:
            try:
                # Get notification from queue
                item = await self.notification_queue.get()
                notification_id = item["notification_id"]
                request = item["request"]
                
                # Process based on channel
                success = False
                error_message = None
                
                try:
                    if request.channel == NotificationChannel.EMAIL:
                        success = await self.send_email_notification(notification_id, request)
                    elif request.channel == NotificationChannel.SMS:
                        success = await self.send_sms_notification(notification_id, request)
                    elif request.channel == NotificationChannel.PUSH:
                        success = await self.send_push_notification(notification_id, request)
                    elif request.channel == NotificationChannel.IN_APP:
                        success = await self.send_in_app_notification(notification_id, request)
                    elif request.channel == NotificationChannel.WEBHOOK:
                        success = await self.send_webhook_notification(notification_id, request)
                    elif request.channel == NotificationChannel.TELEGRAM:
                        success = await self.send_telegram_notification(notification_id, request)
                    elif request.channel == NotificationChannel.DISCORD:
                        success = await self.send_discord_notification(notification_id, request)
                    
                except Exception as e:
                    success = False
                    error_message = str(e)
                    logger.error(f"Notification processing error: {e}")
                
                # Update notification status
                if success:
                    await self.update_notification_status(
                        notification_id, 
                        NotificationStatus.SENT,
                        sent_at=datetime.utcnow()
                    )
                else:
                    await self.handle_notification_failure(
                        notification_id, 
                        request, 
                        error_message
                    )
                
                # Mark task as done
                self.notification_queue.task_done()
                
            except Exception as e:
                logger.error(f"Notification queue processing error: {e}")
                await asyncio.sleep(1)
    
    async def send_email_notification(
        self, 
        notification_id: str, 
        request: SendNotificationRequest
    ) -> bool:
        """Send email notification"""
        try:
            # Get user email
            user_email = await self.get_user_email(request.user_id)
            if not user_email:
                return False
            
            # Get or create email template
            template = await self.get_email_template(request.type)
            
            # Render template
            subject = self.render_template(template.subject_template, request.data)
            body = self.render_template(template.body_template, {
                **request.data,
                'title': request.title,
                'message': request.message,
                'user_id': request.user_id
            })
            
            # Send via AWS SES or SMTP
            if self.ses_client:
                response = self.ses_client.send_email(
                    Source=os.getenv('FROM_EMAIL', 'noreply@tigerex.com'),
                    Destination={'ToAddresses': [user_email]},
                    Message={
                        'Subject': {'Data': subject},
                        'Body': {'Html': {'Data': body}}
                    }
                )
                return True
            else:
                # Fallback to SMTP
                return await self.send_smtp_email(user_email, subject, body)
                
        except Exception as e:
            logger.error(f"Email notification failed: {e}")
            return False
    
    async def send_sms_notification(
        self, 
        notification_id: str, 
        request: SendNotificationRequest
    ) -> bool:
        """Send SMS notification"""
        try:
            if not self.twilio_client:
                return False
            
            # Get user phone number
            phone_number = await self.get_user_phone(request.user_id)
            if not phone_number:
                return False
            
            # Send SMS
            message = self.twilio_client.messages.create(
                body=f"{request.title}\n{request.message}",
                from_=os.getenv('TWILIO_PHONE_NUMBER'),
                to=phone_number
            )
            
            return message.sid is not None
            
        except Exception as e:
            logger.error(f"SMS notification failed: {e}")
            return False
    
    async def send_push_notification(
        self, 
        notification_id: str, 
        request: SendNotificationRequest
    ) -> bool:
        """Send push notification"""
        try:
            if not self.firebase_app:
                return False
            
            # Get user FCM tokens
            fcm_tokens = await self.get_user_fcm_tokens(request.user_id)
            if not fcm_tokens:
                return False
            
            # Create message
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=request.title,
                    body=request.message
                ),
                data=request.data,
                tokens=fcm_tokens
            )
            
            # Send push notification
            response = messaging.send_multicast(message)
            
            return response.success_count > 0
            
        except Exception as e:
            logger.error(f"Push notification failed: {e}")
            return False
    
    async def send_in_app_notification(
        self, 
        notification_id: str, 
        request: SendNotificationRequest
    ) -> bool:
        """Send in-app notification via WebSocket"""
        try:
            if request.user_id in self.websocket_connections:
                websocket = self.websocket_connections[request.user_id]
                
                notification_data = {
                    "id": notification_id,
                    "type": request.type,
                    "title": request.title,
                    "message": request.message,
                    "data": request.data,
                    "priority": request.priority,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await websocket.send_text(json.dumps(notification_data))
                return True
            
            # Store for later retrieval if user is offline
            await self.store_in_app_notification(notification_id, request)
            return True
            
        except Exception as e:
            logger.error(f"In-app notification failed: {e}")
            return False
    
    async def send_webhook_notification(
        self, 
        notification_id: str, 
        request: SendNotificationRequest
    ) -> bool:
        """Send webhook notification"""
        try:
            # Get user webhook URL
            webhook_url = await self.get_user_webhook_url(request.user_id)
            if not webhook_url:
                return False
            
            payload = {
                "notification_id": notification_id,
                "user_id": request.user_id,
                "type": request.type,
                "title": request.title,
                "message": request.message,
                "data": request.data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"Webhook notification failed: {e}")
            return False
    
    async def send_telegram_notification(
        self, 
        notification_id: str, 
        request: SendNotificationRequest
    ) -> bool:
        """Send Telegram notification"""
        try:
            # Get user Telegram chat ID
            chat_id = await self.get_user_telegram_chat_id(request.user_id)
            if not chat_id:
                return False
            
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            if not bot_token:
                return False
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": f"*{request.title}*\n{request.message}",
                "parse_mode": "Markdown"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"Telegram notification failed: {e}")
            return False
    
    async def send_discord_notification(
        self, 
        notification_id: str, 
        request: SendNotificationRequest
    ) -> bool:
        """Send Discord notification"""
        try:
            # Get user Discord webhook URL
            webhook_url = await self.get_user_discord_webhook(request.user_id)
            if not webhook_url:
                return False
            
            payload = {
                "embeds": [{
                    "title": request.title,
                    "description": request.message,
                    "color": self.get_priority_color(request.priority),
                    "timestamp": datetime.utcnow().isoformat()
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    return response.status == 204
                    
        except Exception as e:
            logger.error(f"Discord notification failed: {e}")
            return False
    
    # Helper methods (simplified implementations)
    async def create_notification_record(self, request: SendNotificationRequest) -> str:
        """Create notification record in database"""
        notification_id = f"notif_{datetime.utcnow().timestamp()}"
        # Database insertion logic here
        return notification_id
    
    async def get_user_preferences(self, user_id: str) -> UserPreferences:
        """Get user notification preferences"""
        # Mock implementation
        return UserPreferences(
            user_id=user_id,
            email_enabled=True,
            sms_enabled=True,
            push_enabled=True,
            in_app_enabled=True,
            notification_types={},
            quiet_hours_start=None,
            quiet_hours_end=None,
            timezone="UTC",
            language="en"
        )
    
    def should_send_notification(self, request: SendNotificationRequest, preferences: UserPreferences) -> bool:
        """Check if notification should be sent based on user preferences"""
        # Check channel preferences
        if request.channel == NotificationChannel.EMAIL and not preferences.email_enabled:
            return False
        if request.channel == NotificationChannel.SMS and not preferences.sms_enabled:
            return False
        if request.channel == NotificationChannel.PUSH and not preferences.push_enabled:
            return False
        if request.channel == NotificationChannel.IN_APP and not preferences.in_app_enabled:
            return False
        
        # Check notification type preferences
        if request.type in preferences.notification_types:
            return preferences.notification_types[request.type]
        
        # Check quiet hours
        if preferences.quiet_hours_start and preferences.quiet_hours_end:
            current_time = datetime.utcnow().time()
            # Simplified quiet hours check
            return True
        
        return True
    
    def render_template(self, template: str, data: Dict[str, Any]) -> str:
        """Render notification template"""
        try:
            template_obj = self.template_env.from_string(template)
            return template_obj.render(**data)
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            return template
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """Get current user from JWT token"""
        return "user_id"  # Simplified
    
    async def get_admin_user(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """Get admin user from JWT token"""
        return "admin_id"  # Simplified
    
    async def handle_websocket_connection(self, websocket: WebSocket, user_id: str):
        """Handle WebSocket connection for real-time notifications"""
        await websocket.accept()
        self.websocket_connections[user_id] = websocket
        
        try:
            while True:
                # Keep connection alive
                await websocket.receive_text()
        except Exception as e:
            logger.info(f"WebSocket connection closed for user {user_id}: {e}")
        finally:
            if user_id in self.websocket_connections:
                del self.websocket_connections[user_id]
    
    # Additional helper methods would be implemented here...
    async def get_user_email(self, user_id: str) -> Optional[str]:
        return "user@example.com"  # Simplified
    
    async def get_user_phone(self, user_id: str) -> Optional[str]:
        return "+1234567890"  # Simplified
    
    async def get_user_fcm_tokens(self, user_id: str) -> List[str]:
        return ["fcm_token_123"]  # Simplified
    
    def get_priority_color(self, priority: NotificationPriority) -> int:
        colors = {
            NotificationPriority.LOW: 0x00ff00,
            NotificationPriority.MEDIUM: 0xffff00,
            NotificationPriority.HIGH: 0xff8000,
            NotificationPriority.CRITICAL: 0xff0000
        }
        return colors.get(priority, 0x808080)

# Create service instance
notification_service = NotificationService()

# FastAPI app
app = notification_service.app

@app.on_event("startup")
async def startup_event():
    await notification_service.startup()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 3012)))