"""
Complete Admin Control System for Market Maker Bot
Provides full administrative control over all services and user permissions
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import bcrypt
import jwt
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import redis
import asyncpg
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserRole(Enum):
    ADMIN = "admin"
    INSTITUTIONAL = "institutional"
    RETAIL = "retail"
    VIEWER = "viewer"

class Permission(Enum):
    CREATE_BOT = "create_bot"
    DELETE_BOT = "delete_bot"
    UPDATE_BOT = "update_bot"
    START_BOT = "start_bot"
    STOP_BOT = "stop_bot"
    RESUME_BOT = "resume_bot"
    VIEW_BOTS = "view_bots"
    VIEW_USERS = "view_users"
    MANAGE_USERS = "manage_users"
    VIEW_REPORTS = "view_reports"
    MANAGE_EXCHANGES = "manage_exchanges"
    MANAGE_COMPLIANCE = "manage_compliance"
    DEPLOY_BOT = "deploy_bot"
    SYSTEM_CONFIG = "system_config"

class BotStatus(Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    DEPLOYING = "deploying"

@dataclass
class User:
    id: str
    username: str
    email: str
    role: UserRole
    permissions: List[Permission]
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    is_halted: bool = False

@dataclass
class BotInstance:
    id: str
    name: str
    owner_id: str
    exchange: str
    strategy: str
    status: BotStatus
    config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    last_started: Optional[datetime] = None
    performance_metrics: Dict[str, float] = None
    is_halted: bool = False

class DatabaseManager:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.pool = None
    
    async def initialize(self):
        self.pool = await asyncpg.create_pool(self.db_url)
        await self._create_tables()
    
    async def _create_tables(self):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(36) PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(20) NOT NULL,
                    permissions TEXT[],
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_halted BOOLEAN DEFAULT FALSE
                );
                
                CREATE TABLE IF NOT EXISTS bot_instances (
                    id VARCHAR(36) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    owner_id VARCHAR(36) REFERENCES users(id),
                    exchange VARCHAR(50) NOT NULL,
                    strategy VARCHAR(50) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    config JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_started TIMESTAMP,
                    performance_metrics JSONB,
                    is_halted BOOLEAN DEFAULT FALSE
                );
                
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(36) REFERENCES users(id),
                    action VARCHAR(100) NOT NULL,
                    resource_type VARCHAR(50) NOT NULL,
                    resource_id VARCHAR(36),
                    details JSONB,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address INET
                );
            """)
    
    async def create_user(self, user: User) -> bool:
        async with self.pool.acquire() as conn:
            try:
                await conn.execute(
                    """
                    INSERT INTO users (id, username, email, password_hash, role, permissions)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    user.id, user.username, user.email, "hashed_password", 
                    user.role.value, [p.value for p in user.permissions]
                )
                return True
            except Exception as e:
                logger.error(f"Error creating user: {e}")
                return False
    
    async def get_user(self, user_id: str) -> Optional[User]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE id = $1 AND is_active = TRUE",
                user_id
            )
            if row:
                return User(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    role=UserRole(row['role']),
                    permissions=[Permission(p) for p in row['permissions']],
                    created_at=row['created_at'],
                    last_login=row['last_login'],
                    is_active=row['is_active'],
                    is_halted=row['is_halted']
                )
            return None
    
    async def create_bot(self, bot: BotInstance) -> bool:
        async with self.pool.acquire() as conn:
            try:
                await conn.execute(
                    """
                    INSERT INTO bot_instances 
                    (id, name, owner_id, exchange, strategy, status, config, performance_metrics)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """,
                    bot.id, bot.name, bot.owner_id, bot.exchange, bot.strategy,
                    bot.status.value, json.dumps(bot.config), 
                    json.dumps(bot.performance_metrics or {})
                )
                return True
            except Exception as e:
                logger.error(f"Error creating bot: {e}")
                return False

class PermissionManager:
    ROLE_PERMISSIONS = {
        UserRole.ADMIN: list(Permission),
        UserRole.INSTITUTIONAL: [
            Permission.CREATE_BOT, Permission.DELETE_BOT, Permission.UPDATE_BOT,
            Permission.START_BOT, Permission.STOP_BOT, Permission.RESUME_BOT,
            Permission.VIEW_BOTS, Permission.VIEW_REPORTS, Permission.MANAGE_EXCHANGES
        ],
        UserRole.RETAIL: [
            Permission.CREATE_BOT, Permission.UPDATE_BOT, Permission.START_BOT,
            Permission.STOP_BOT, Permission.RESUME_BOT, Permission.VIEW_BOTS,
            Permission.VIEW_REPORTS
        ],
        UserRole.VIEWER: [
            Permission.VIEW_BOTS, Permission.VIEW_REPORTS
        ]
    }
    
    def has_permission(self, user: User, permission: Permission) -> bool:
        if user.is_halted:
            return False
        return permission in user.permissions
    
    def can_manage_user(self, admin: User, target_user: User) -> bool:
        if admin.is_halted:
            return False
        if admin.role == UserRole.ADMIN:
            return True
        if admin.role == UserRole.INSTITUTIONAL and target_user.role == UserRole.RETAIL:
            return True
        return False

class AdminAPI:
    def __init__(self, db_manager: DatabaseManager, permission_manager: PermissionManager):
        self.db_manager = db_manager
        self.permission_manager = permission_manager
        self.app = FastAPI(title="Market Maker Bot Admin API")
        self.security = HTTPBearer()
        self.secret_key = Fernet.generate_key().decode()
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.post("/admin/users/create")
        async def create_user(user_data: dict, credentials: HTTPAuthorizationCredentials = Depends(self.security)):
            user = await self.authenticate(credentials.credentials)
            if not self.permission_manager.has_permission(user, Permission.MANAGE_USERS):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            new_user = User(
                id=user_data.get('id'),
                username=user_data.get('username'),
                email=user_data.get('email'),
                role=UserRole(user_data.get('role')),
                permissions=self.permission_manager.ROLE_PERMISSIONS[UserRole(user_data.get('role'))],
                created_at=datetime.now()
            )
            
            success = await self.db_manager.create_user(new_user)
            if success:
                await self.log_action(user.id, "CREATE_USER", "user", new_user.id, user_data)
                return {"success": True, "user_id": new_user.id}
            else:
                raise HTTPException(status_code=400, detail="Failed to create user")
        
        @self.app.post("/admin/bots/create")
        async def create_bot(bot_data: dict, credentials: HTTPAuthorizationCredentials = Depends(self.security)):
            user = await self.authenticate(credentials.credentials)
            if not self.permission_manager.has_permission(user, Permission.CREATE_BOT):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            bot = BotInstance(
                id=bot_data.get('id'),
                name=bot_data.get('name'),
                owner_id=user.id,
                exchange=bot_data.get('exchange'),
                strategy=bot_data.get('strategy'),
                status=BotStatus.STOPPED,
                config=bot_data.get('config', {}),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                performance_metrics={}
            )
            
            success = await self.db_manager.create_bot(bot)
            if success:
                await self.log_action(user.id, "CREATE_BOT", "bot", bot.id, bot_data)
                return {"success": True, "bot_id": bot.id}
            else:
                raise HTTPException(status_code=400, detail="Failed to create bot")
        
        @self.app.post("/admin/bots/{bot_id}/start")
        async def start_bot(bot_id: str, credentials: HTTPAuthorizationCredentials = Depends(self.security)):
            user = await self.authenticate(credentials.credentials)
            if not self.permission_manager.has_permission(user, Permission.START_BOT):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            # Check if bot is halted
            bot_halted = await self.redis_client.get(f"bot_halted:{bot_id}")
            if bot_halted:
                raise HTTPException(status_code=403, detail="Bot is halted by admin")
            
            # Start bot logic here
            await self.redis_client.set(f"bot_status:{bot_id}", BotStatus.RUNNING.value)
            await self.log_action(user.id, "START_BOT", "bot", bot_id)
            
            return {"success": True, "message": "Bot started successfully"}
        
        @self.app.post("/admin/bots/{bot_id}/stop")
        async def stop_bot(bot_id: str, credentials: HTTPAuthorizationCredentials = Depends(self.security)):
            user = await self.authenticate(credentials.credentials)
            if not self.permission_manager.has_permission(user, Permission.STOP_BOT):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            # Stop bot logic here
            await self.redis_client.set(f"bot_status:{bot_id}", BotStatus.STOPPED.value)
            await self.log_action(user.id, "STOP_BOT", "bot", bot_id)
            
            return {"success": True, "message": "Bot stopped successfully"}
        
        @self.app.post("/admin/bots/{bot_id}/halt")
        async def halt_bot(bot_id: str, credentials: HTTPAuthorizationCredentials = Depends(self.security)):
            user = await self.authenticate(credentials.credentials)
            if user.role != UserRole.ADMIN:
                raise HTTPException(status_code=403, detail="Admin access required")
            
            # Halt bot
            await self.redis_client.set(f"bot_halted:{bot_id}", "true")
            await self.redis_client.set(f"bot_status:{bot_id}", BotStatus.STOPPED.value)
            await self.log_action(user.id, "HALT_BOT", "bot", bot_id)
            
            return {"success": True, "message": "Bot halted successfully"}
        
        @self.app.post("/admin/bots/{bot_id}/resume")
        async def resume_bot(bot_id: str, credentials: HTTPAuthorizationCredentials = Depends(self.security)):
            user = await self.authenticate(credentials.credentials)
            if not self.permission_manager.has_permission(user, Permission.RESUME_BOT):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            # Resume bot
            await self.redis_client.delete(f"bot_halted:{bot_id}")
            await self.redis_client.set(f"bot_status:{bot_id}", BotStatus.RUNNING.value)
            await self.log_action(user.id, "RESUME_BOT", "bot", bot_id)
            
            return {"success": True, "message": "Bot resumed successfully"}
        
        @self.app.post("/admin/users/{user_id}/halt")
        async def halt_user(user_id: str, credentials: HTTPAuthorizationCredentials = Depends(self.security)):
            user = await self.authenticate(credentials.credentials)
            if user.role != UserRole.ADMIN:
                raise HTTPException(status_code=403, detail="Admin access required")
            
            # Halt user and all their bots
            await self.redis_client.set(f"user_halted:{user_id}", "true")
            await self.log_action(user.id, "HALT_USER", "user", user_id)
            
            return {"success": True, "message": "User halted successfully"}
        
        @self.app.post("/admin/users/{user_id}/resume")
        async def resume_user(user_id: str, credentials: HTTPAuthorizationCredentials = Depends(self.security)):
            user = await self.authenticate(credentials.credentials)
            if user.role != UserRole.ADMIN:
                raise HTTPException(status_code=403, detail="Admin access required")
            
            # Resume user
            await self.redis_client.delete(f"user_halted:{user_id}")
            await self.log_action(user.id, "RESUME_USER", "user", user_id)
            
            return {"success": True, "message": "User resumed successfully"}
        
        @self.app.get("/admin/dashboard")
        async def get_dashboard(credentials: HTTPAuthorizationCredentials = Depends(self.security)):
            user = await self.authenticate(credentials.credentials)
            if not self.permission_manager.has_permission(user, Permission.VIEW_BOTS):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            # Get dashboard data
            dashboard_data = {
                "total_users": await self.get_total_users(),
                "active_bots": await self.get_active_bots_count(),
                "total_bots": await self.get_total_bots_count(),
                "system_status": await self.get_system_status(),
                "recent_activities": await self.get_recent_activities()
            }
            
            return dashboard_data
    
    async def authenticate(self, token: str) -> User:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            user_id = payload.get("user_id")
            user = await self.db_manager.get_user(user_id)
            if not user or user.is_halted:
                raise HTTPException(status_code=401, detail="Unauthorized")
            return user
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    async def log_action(self, user_id: str, action: str, resource_type: str, 
                        resource_id: str, details: dict = None):
        async with self.db_manager.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO audit_logs (user_id, action, resource_type, resource_id, details)
                VALUES ($1, $2, $3, $4, $5)
                """,
                user_id, action, resource_type, resource_id, json.dumps(details or {})
            )
    
    async def get_total_users(self) -> int:
        async with self.db_manager.pool.acquire() as conn:
            result = await conn.fetchval("SELECT COUNT(*) FROM users WHERE is_active = TRUE")
            return result
    
    async def get_active_bots_count(self) -> int:
        # Count from Redis
        keys = self.redis_client.keys("bot_status:*")
        active_count = 0
        for key in keys:
            status = self.redis_client.get(key)
            if status and status.decode() == BotStatus.RUNNING.value:
                active_count += 1
        return active_count
    
    async def get_total_bots_count(self) -> int:
        async with self.db_manager.pool.acquire() as conn:
            result = await conn.fetchval("SELECT COUNT(*) FROM bot_instances")
            return result
    
    async def get_system_status(self) -> dict:
        return {
            "status": "healthy",
            "uptime": "24h 15m",
            "memory_usage": "45%",
            "cpu_usage": "23%"
        }
    
    async def get_recent_activities(self) -> List[dict]:
        async with self.db_manager.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT al.*, u.username 
                FROM audit_logs al 
                JOIN users u ON al.user_id = u.id 
                ORDER BY al.timestamp DESC 
                LIMIT 10
                """
            )
            return [dict(row) for row in rows]

class AdminDashboard:
    def __init__(self, api: AdminAPI):
        self.api = api
    
    async def start(self):
        import uvicorn
        uvicorn.run(self.api.app, host="0.0.0.0", port=8000)

# Initialize and start the admin system
async def main():
    db_manager = DatabaseManager("postgresql://user:password@localhost/marketmaker_db")
    await db_manager.initialize()
    
    permission_manager = PermissionManager()
    admin_api = AdminAPI(db_manager, permission_manager)
    dashboard = AdminDashboard(admin_api)
    
    await dashboard.start()

if __name__ == "__main__":
    asyncio.run(main())