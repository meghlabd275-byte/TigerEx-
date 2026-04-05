"""
TigerEx Comprehensive Admin Service
Central admin service for managing tokens, trading pairs, blockchains, and liquidity
Complete implementation with JWT authentication and RBAC
Port: 8160
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import asyncio
import asyncpg
import redis.asyncio as redis
import structlog
import uvicorn
import os
import json
import httpx
from contextlib import asynccontextmanager
from web3 import Web3
import ccxt.async_support as ccxt
import jwt
import bcrypt
from passlib.context import CryptContext
import secrets
from functools import wraps

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/tigerex")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "tigerex-super-secret-jwt-key-2024")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24
VIRTUAL_LIQUIDITY_SERVICE_URL = os.getenv("VIRTUAL_LIQUIDITY_SERVICE_URL", "http://localhost:8150")
TOKEN_LISTING_SERVICE_URL = os.getenv("TOKEN_LISTING_SERVICE_URL", "http://localhost:8000")
TRADING_PAIR_SERVICE_URL = os.getenv("TRADING_PAIR_SERVICE_URL", "http://localhost:8000")

# Global connections
db_pool = None
redis_client = None
http_client = None

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============================================================================
# USER ROLES AND PERMISSIONS
# ============================================================================

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    COMPLIANCE_OFFICER = "compliance_officer"
    RISK_MANAGER = "risk_manager"
    TECHNICAL_ADMIN = "technical_admin"
    SUPPORT_MANAGER = "support_manager"
    SUPPORT_AGENT = "support_agent"
    LISTING_MANAGER = "listing_manager"
    PARTNER = "partner"
    WHITE_LABEL_CLIENT = "white_label_client"
    INSTITUTIONAL_CLIENT = "institutional_client"
    MARKET_MAKER = "market_maker"
    LIQUIDITY_PROVIDER = "liquidity_provider"
    AFFILIATE = "affiliate"
    TRADER_PRO = "trader_pro"
    TRADER = "trader"
    USER = "user"

class Permission(str, Enum):
    # User Management
    VIEW_USERS = "view_users"
    CREATE_USERS = "create_users"
    EDIT_USERS = "edit_users"
    DELETE_USERS = "delete_users"
    SUSPEND_USERS = "suspend_users"
    BAN_USERS = "ban_users"
    
    # Trading Control
    VIEW_TRADING = "view_trading"
    CONTROL_TRADING = "control_trading"
    PAUSE_TRADING = "pause_trading"
    RESUME_TRADING = "resume_trading"
    HALT_ALL_TRADING = "halt_all_trading"
    MODIFY_FEES = "modify_fees"
    
    # Financial Control
    VIEW_FINANCIALS = "view_financials"
    PROCESS_WITHDRAWALS = "process_withdrawals"
    APPROVE_WITHDRAWALS = "approve_withdrawals"
    MANAGE_FUNDS = "manage_funds"
    
    # Token Management
    LIST_TOKENS = "list_tokens"
    DELIST_TOKENS = "delist_tokens"
    MANAGE_TRADING_PAIRS = "manage_trading_pairs"
    
    # System Control
    SYSTEM_CONFIG = "system_config"
    VIEW_LOGS = "view_logs"
    MANAGE_SECURITY = "manage_security"

# Role-Permission Mapping
ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: list(Permission),  # All permissions
    UserRole.ADMIN: [
        Permission.VIEW_USERS, Permission.CREATE_USERS, Permission.EDIT_USERS,
        Permission.SUSPEND_USERS, Permission.VIEW_TRADING, Permission.CONTROL_TRADING,
        Permission.PAUSE_TRADING, Permission.RESUME_TRADING, Permission.MODIFY_FEES,
        Permission.VIEW_FINANCIALS, Permission.PROCESS_WITHDRAWALS, Permission.APPROVE_WITHDRAWALS,
        Permission.LIST_TOKENS, Permission.DELIST_TOKENS, Permission.MANAGE_TRADING_PAIRS,
        Permission.SYSTEM_CONFIG, Permission.VIEW_LOGS,
    ],
    UserRole.COMPLIANCE_OFFICER: [
        Permission.VIEW_USERS, Permission.VIEW_TRADING, Permission.VIEW_FINANCIALS,
    ],
    UserRole.RISK_MANAGER: [
        Permission.VIEW_TRADING, Permission.PAUSE_TRADING, Permission.HALT_ALL_TRADING,
    ],
    UserRole.TECHNICAL_ADMIN: [
        Permission.SYSTEM_CONFIG, Permission.VIEW_LOGS, Permission.MANAGE_SECURITY,
    ],
    UserRole.LISTING_MANAGER: [
        Permission.LIST_TOKENS, Permission.DELIST_TOKENS, Permission.MANAGE_TRADING_PAIRS,
    ],
}

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class BlockchainType(str, Enum):
    EVM = "evm"
    NON_EVM = "non_evm"
    CUSTOM = "custom"

class NetworkType(str, Enum):
    MAINNET = "mainnet"
    TESTNET = "testnet"
    DEVNET = "devnet"

class TokenStandard(str, Enum):
    ERC20 = "ERC20"
    BEP20 = "BEP20"
    TRC20 = "TRC20"
    SPL = "SPL"
    NATIVE = "NATIVE"

class TradingType(str, Enum):
    SPOT = "spot"
    FUTURES = "futures"
    OPTIONS = "options"
    MARGIN = "margin"
    ETF = "etf"

# Admin User Models
class AdminUserCreate(BaseModel):
    email: str = Field(..., min_length=1, max_length=255)
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.USER
    permissions: Optional[List[Permission]] = None

class AdminUserLogin(BaseModel):
    email: str
    password: str

class AdminUserResponse(BaseModel):
    user_id: str
    email: str
    username: str
    role: UserRole
    permissions: List[str]
    is_active: bool
    created_at: datetime

# Token Listing Models
class TokenListingRequest(BaseModel):
    token_symbol: str = Field(..., min_length=1, max_length=10)
    token_name: str = Field(..., min_length=1, max_length=100)
    token_standard: TokenStandard
    blockchain_id: str
    contract_address: Optional[str] = None
    decimals: int = Field(..., ge=0, le=18)
    total_supply: Optional[Decimal] = Field(None, gt=0)
    description: Optional[str] = None
    website: Optional[str] = None
    whitepaper_url: Optional[str] = None
    logo_url: Optional[str] = None
    is_iou: bool = False
    auto_create_liquidity_pool: bool = True
    initial_liquidity_usdt: Optional[Decimal] = Field(None, gt=0)

class TokenUpdateRequest(BaseModel):
    status: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None

# Trading Pair Models
class TradingPairCreateRequest(BaseModel):
    base_asset: str = Field(..., min_length=1, max_length=10)
    quote_asset: str = Field(..., min_length=1, max_length=10)
    trading_type: TradingType
    min_order_size: Decimal = Field(..., gt=0)
    max_order_size: Optional[Decimal] = Field(None, gt=0)
    min_price: Decimal = Field(..., gt=0)
    max_price: Optional[Decimal] = Field(None, gt=0)
    price_precision: int = Field(..., ge=0, le=8)
    quantity_precision: int = Field(..., ge=0, le=8)
    maker_fee: Decimal = Field(default=Decimal("0.001"), ge=0, le=1)
    taker_fee: Decimal = Field(default=Decimal("0.001"), ge=0, le=1)
    auto_provide_liquidity: bool = True
    virtual_liquidity_percentage: Decimal = Field(default=Decimal("0.7"), ge=0, le=1)

# Blockchain Integration Models
class BlockchainIntegrationRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    symbol: str = Field(..., min_length=1, max_length=10)
    blockchain_type: BlockchainType
    network_type: NetworkType
    chain_id: Optional[int] = None
    rpc_url: str
    ws_url: Optional[str] = None
    explorer_url: Optional[str] = None
    consensus_mechanism: str
    block_time: int = Field(..., gt=0)
    native_currency: str
    description: Optional[str] = None

# User Management Models
class UserStatusUpdate(BaseModel):
    status: str  # active, suspended, banned
    reason: Optional[str] = None

class UserRoleUpdate(BaseModel):
    role: UserRole
    permissions: Optional[List[Permission]] = None

# ============================================================================
# AUTHENTICATION AND AUTHORIZATION
# ============================================================================

def create_jwt_token(user_id: str, email: str, role: UserRole, permissions: List[str]) -> str:
    """Create JWT token for authenticated user"""
    expiration = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role.value,
        "permissions": permissions,
        "exp": expiration,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str) -> Dict[str, Any]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Verify admin authentication token"""
    token = credentials.credentials
    payload = verify_jwt_token(token)
    
    # Check if user is active in Redis cache
    if redis_client:
        user_status = await redis_client.get(f"user_status:{payload['user_id']}")
        if user_status == "suspended":
            raise HTTPException(status_code=403, detail="User account is suspended")
        if user_status == "banned":
            raise HTTPException(status_code=403, detail="User account is banned")
    
    return payload

def require_permission(permission: Permission):
    """Decorator to check if user has required permission"""
    async def dependency(payload: Dict = Depends(verify_admin_token)):
        user_permissions = payload.get("permissions", [])
        user_role = payload.get("role", "user")
        
        # Super admin has all permissions
        if user_role == UserRole.SUPER_ADMIN.value:
            return payload
        
        # Check if user has the required permission
        if permission.value not in user_permissions:
            # Check role-based permissions
            role = UserRole(user_role)
            role_perms = [p.value for p in ROLE_PERMISSIONS.get(role, [])]
            if permission.value not in role_perms:
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: {permission.value} required"
                )
        
        return payload
    
    return dependency

# ============================================================================
# LIFESPAN CONTEXT MANAGER
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global db_pool, redis_client, http_client

    logger.info("Starting Comprehensive Admin Service...")

    # Initialize database pool
    try:
        db_pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=10,
            max_size=50,
            command_timeout=60
        )
        logger.info("Database pool created")
        
        # Create tables if not exist
        async with db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS admin_users (
                    user_id VARCHAR(50) PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL DEFAULT 'user',
                    permissions JSONB DEFAULT '[]',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    last_login TIMESTAMP
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS tokens (
                    token_id VARCHAR(50) PRIMARY KEY,
                    symbol VARCHAR(20) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    token_standard VARCHAR(20),
                    blockchain_id VARCHAR(50),
                    contract_address VARCHAR(255),
                    decimals INTEGER DEFAULT 18,
                    total_supply DECIMAL(38, 8),
                    description TEXT,
                    website VARCHAR(255),
                    whitepaper_url VARCHAR(255),
                    logo_url VARCHAR(255),
                    is_active BOOLEAN DEFAULT TRUE,
                    is_iou BOOLEAN DEFAULT FALSE,
                    created_by VARCHAR(50),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS trading_pairs (
                    pair_id VARCHAR(50) PRIMARY KEY,
                    symbol VARCHAR(20) UNIQUE NOT NULL,
                    base_asset VARCHAR(20) NOT NULL,
                    quote_asset VARCHAR(20) NOT NULL,
                    trading_type VARCHAR(20) DEFAULT 'spot',
                    min_order_size DECIMAL(38, 8),
                    max_order_size DECIMAL(38, 8),
                    min_price DECIMAL(38, 8),
                    max_price DECIMAL(38, 8),
                    price_precision INTEGER DEFAULT 8,
                    quantity_precision INTEGER DEFAULT 8,
                    maker_fee DECIMAL(10, 6) DEFAULT 0.001,
                    taker_fee DECIMAL(10, 6) DEFAULT 0.001,
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id VARCHAR(50) PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255),
                    role VARCHAR(50) DEFAULT 'user',
                    permissions JSONB DEFAULT '[]',
                    status VARCHAR(20) DEFAULT 'active',
                    kyc_level INTEGER DEFAULT 0,
                    is_verified BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create default super admin if not exists
            existing_admin = await conn.fetchval(
                "SELECT user_id FROM admin_users WHERE role = $1",
                UserRole.SUPER_ADMIN.value
            )
            
            if not existing_admin:
                import uuid
                admin_id = f"ADMIN_{uuid.uuid4().hex[:8].upper()}"
                password_hash = pwd_context.hash("Admin@2024!TigerEx")
                
                await conn.execute("""
                    INSERT INTO admin_users (user_id, email, username, password_hash, role, permissions, is_active)
                    VALUES ($1, $2, $3, $4, $5, $6, TRUE)
                """, admin_id, "admin@tigerex.com", "superadmin", password_hash,
                    UserRole.SUPER_ADMIN.value, json.dumps([p.value for p in Permission]))
                
                logger.info(f"Created default super admin: {admin_id}")
            
            logger.info("Database tables initialized")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

    # Initialize Redis
    try:
        redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
        logger.info("Redis client connected")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")

    # Initialize HTTP client
    http_client = httpx.AsyncClient(timeout=30.0)
    logger.info("HTTP client initialized")

    logger.info("Comprehensive Admin Service started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Comprehensive Admin Service...")

    if db_pool:
        await db_pool.close()
    if redis_client:
        await redis_client.close()
    if http_client:
        await http_client.aclose()

    logger.info("Comprehensive Admin Service shut down")

# Initialize FastAPI app
app = FastAPI(
    title="TigerEx Comprehensive Admin Service",
    description="Central admin service for managing all exchange features",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/api/admin/auth/register", response_model=AdminUserResponse)
async def register_admin(
    user_data: AdminUserCreate,
    current_user: Dict = Depends(require_permission(Permission.CREATE_USERS))
):
    """Register a new admin user"""
    try:
        async with db_pool.acquire() as conn:
            # Check if email exists
            existing = await conn.fetchval(
                "SELECT user_id FROM admin_users WHERE email = $1",
                user_data.email
            )
            if existing:
                raise HTTPException(status_code=400, detail="Email already registered")
            
            # Check if username exists
            existing = await conn.fetchval(
                "SELECT user_id FROM admin_users WHERE username = $1",
                user_data.username
            )
            if existing:
                raise HTTPException(status_code=400, detail="Username already taken")
            
            # Create user
            import uuid
            user_id = f"ADMIN_{uuid.uuid4().hex[:8].upper()}"
            password_hash = pwd_context.hash(user_data.password)
            
            permissions = [p.value for p in user_data.permissions] if user_data.permissions else []
            permissions.extend([p.value for p in ROLE_PERMISSIONS.get(user_data.role, [])])
            permissions = list(set(permissions))
            
            await conn.execute("""
                INSERT INTO admin_users (user_id, email, username, password_hash, role, permissions, is_active)
                VALUES ($1, $2, $3, $4, $5, $6, TRUE)
            """, user_id, user_data.email, user_data.username, password_hash,
                user_data.role.value, json.dumps(permissions))
            
            logger.info(f"Created admin user: {user_id}", admin_id=current_user['user_id'])
            
            return AdminUserResponse(
                user_id=user_id,
                email=user_data.email,
                username=user_data.username,
                role=user_data.role,
                permissions=permissions,
                is_active=True,
                created_at=datetime.utcnow()
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/auth/login")
async def login_admin(credentials: AdminUserLogin):
    """Login admin user and return JWT token"""
    try:
        async with db_pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT * FROM admin_users WHERE email = $1",
                credentials.email
            )
            
            if not user:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            if not user['is_active']:
                raise HTTPException(status_code=403, detail="Account is deactivated")
            
            if not pwd_context.verify(credentials.password, user['password_hash']):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Update last login
            await conn.execute(
                "UPDATE admin_users SET last_login = NOW() WHERE user_id = $1",
                user['user_id']
            )
            
            # Generate token
            permissions = json.loads(user['permissions']) if isinstance(user['permissions'], str) else user['permissions']
            token = create_jwt_token(
                user['user_id'],
                user['email'],
                UserRole(user['role']),
                permissions
            )
            
            logger.info(f"Admin login: {user['user_id']}")
            
            return {
                "success": True,
                "token": token,
                "token_type": "Bearer",
                "expires_in": JWT_EXPIRATION_HOURS * 3600,
                "user": {
                    "user_id": user['user_id'],
                    "email": user['email'],
                    "username": user['username'],
                    "role": user['role'],
                    "permissions": permissions,
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/auth/me")
async def get_current_user(current_user: Dict = Depends(verify_admin_token)):
    """Get current authenticated user info"""
    return {"user": current_user}

# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/admin/users")
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    role: Optional[str] = None,
    current_user: Dict = Depends(require_permission(Permission.VIEW_USERS))
):
    """Get all users with filtering"""
    try:
        async with db_pool.acquire() as conn:
            query = "SELECT user_id, email, username, role, status, kyc_level, is_verified, created_at FROM users WHERE 1=1"
            params = []
            param_count = 0
            
            if status:
                param_count += 1
                query += f" AND status = ${param_count}"
                params.append(status)
            
            if role:
                param_count += 1
                query += f" AND role = ${param_count}"
                params.append(role)
            
            param_count += 1
            query += f" ORDER BY created_at DESC OFFSET ${param_count}"
            params.append(skip)
            
            param_count += 1
            query += f" LIMIT ${param_count}"
            params.append(limit)
            
            users = await conn.fetch(query, *params)
            total = await conn.fetchval("SELECT COUNT(*) FROM users")
            
            return {
                "total": total,
                "users": [dict(u) for u in users]
            }
            
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/admin/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    update: UserStatusUpdate,
    current_user: Dict = Depends(require_permission(Permission.SUSPEND_USERS))
):
    """Update user status (suspend, ban, activate)"""
    try:
        async with db_pool.acquire() as conn:
            result = await conn.fetchrow("""
                UPDATE users
                SET status = $1, updated_at = NOW()
                WHERE user_id = $2
                RETURNING *
            """, update.status, user_id)
            
            if not result:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Update Redis cache
            if redis_client:
                await redis_client.set(f"user_status:{user_id}", update.status)
            
            logger.info(f"Updated user status: {user_id} -> {update.status}", admin_id=current_user['user_id'])
            
            return {"success": True, "user": dict(result)}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/admin/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    update: UserRoleUpdate,
    current_user: Dict = Depends(require_permission(Permission.EDIT_USERS))
):
    """Update user role and permissions"""
    try:
        async with db_pool.acquire() as conn:
            permissions = [p.value for p in update.permissions] if update.permissions else []
            permissions.extend([p.value for p in ROLE_PERMISSIONS.get(update.role, [])])
            permissions = list(set(permissions))
            
            result = await conn.fetchrow("""
                UPDATE users
                SET role = $1, permissions = $2, updated_at = NOW()
                WHERE user_id = $3
                RETURNING *
            """, update.role.value, json.dumps(permissions), user_id)
            
            if not result:
                raise HTTPException(status_code=404, detail="User not found")
            
            logger.info(f"Updated user role: {user_id} -> {update.role.value}", admin_id=current_user['user_id'])
            
            return {"success": True, "user": dict(result)}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user role: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: Dict = Depends(require_permission(Permission.DELETE_USERS))
):
    """Delete a user"""
    try:
        async with db_pool.acquire() as conn:
            result = await conn.fetchrow(
                "DELETE FROM users WHERE user_id = $1 RETURNING user_id",
                user_id
            )
            
            if not result:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Remove from Redis cache
            if redis_client:
                await redis_client.delete(f"user_status:{user_id}")
            
            logger.info(f"Deleted user: {user_id}", admin_id=current_user['user_id'])
            
            return {"success": True, "message": "User deleted"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TOKEN LISTING MANAGEMENT
# ============================================================================

@app.post("/api/admin/tokens/list", status_code=201)
async def list_new_token(
    request: TokenListingRequest,
    admin: dict = Depends(require_permission(Permission.LIST_TOKENS))
):
    """List a new token or coin on the exchange"""
    try:
        async with db_pool.acquire() as conn:
            # Check if token already exists
            existing = await conn.fetchrow(
                "SELECT * FROM tokens WHERE symbol = $1",
                request.token_symbol
            )

            if existing:
                raise HTTPException(status_code=400, detail="Token already listed")

            # Create token entry
            import uuid
            token_id = f"TOKEN_{request.token_symbol}_{uuid.uuid4().hex[:8].upper()}"

            token = await conn.fetchrow("""
                INSERT INTO tokens (
                    token_id, symbol, name, token_standard, blockchain_id,
                    contract_address, decimals, total_supply, description,
                    website, whitepaper_url, logo_url, is_active, is_iou, created_by
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                RETURNING *
            """, token_id, request.token_symbol, request.token_name,
                request.token_standard.value, request.blockchain_id,
                request.contract_address, request.decimals, request.total_supply,
                request.description, request.website, request.whitepaper_url,
                request.logo_url, True, request.is_iou, admin['user_id'])

            result = {"token": dict(token)}

            # Create liquidity pool if requested
            if request.auto_create_liquidity_pool and request.initial_liquidity_usdt:
                try:
                    pool_response = await http_client.post(
                        f"{VIRTUAL_LIQUIDITY_SERVICE_URL}/api/pools",
                        json={
                            "pool_name": f"{request.token_symbol}/USDT Pool",
                            "pool_type": "amm",
                            "base_asset": request.token_symbol,
                            "quote_asset": "USDT",
                            "base_reserve": "0",
                            "quote_reserve": str(request.initial_liquidity_usdt),
                            "virtual_base_liquidity": "0",
                            "virtual_quote_liquidity": str(float(request.initial_liquidity_usdt) * 0.7),
                            "fee_rate": "0.003",
                            "is_public": True
                        }
                    )
                    result["liquidity_pool"] = pool_response.json()
                except Exception as e:
                    logger.warning(f"Failed to create liquidity pool: {e}")

            logger.info(f"Listed new token: {request.token_symbol}", admin_id=admin['user_id'])
            return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing token: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/tokens")
async def get_all_tokens(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    admin: dict = Depends(require_permission(Permission.VIEW_TRADING))
):
    """Get all listed tokens"""
    try:
        async with db_pool.acquire() as conn:
            query = "SELECT * FROM tokens WHERE 1=1"
            params = []

            if is_active is not None:
                query += " AND is_active = $1"
                params.append(is_active)

            query += f" ORDER BY created_at DESC OFFSET ${len(params) + 1} LIMIT ${len(params) + 2}"
            params.extend([skip, limit])

            tokens = await conn.fetch(query, *params)
            total = await conn.fetchval("SELECT COUNT(*) FROM tokens")

            return {
                "total": total,
                "tokens": [dict(t) for t in tokens]
            }

    except Exception as e:
        logger.error(f"Error fetching tokens: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/admin/tokens/{token_symbol}")
async def update_token(
    token_symbol: str,
    update: TokenUpdateRequest,
    admin: dict = Depends(require_permission(Permission.LIST_TOKENS))
):
    """Update token information"""
    try:
        async with db_pool.acquire() as conn:
            updates = []
            params = []
            param_count = 0

            for field, value in update.dict(exclude_unset=True).items():
                if value is not None:
                    param_count += 1
                    updates.append(f"{field} = ${param_count}")
                    params.append(value)

            if not updates:
                raise HTTPException(status_code=400, detail="No fields to update")

            param_count += 1
            params.append(token_symbol)

            query = f"""
                UPDATE tokens
                SET {', '.join(updates)}, updated_at = NOW()
                WHERE symbol = ${param_count}
                RETURNING *
            """

            result = await conn.fetchrow(query, *params)

            if not result:
                raise HTTPException(status_code=404, detail="Token not found")

            logger.info(f"Updated token: {token_symbol}", admin_id=admin['user_id'])
            return dict(result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating token: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/admin/tokens/{token_symbol}")
async def delist_token(
    token_symbol: str,
    admin: dict = Depends(require_permission(Permission.DELIST_TOKENS))
):
    """Delist a token"""
    try:
        async with db_pool.acquire() as conn:
            result = await conn.fetchrow("""
                UPDATE tokens
                SET is_active = FALSE, updated_at = NOW()
                WHERE symbol = $1
                RETURNING *
            """, token_symbol)

            if not result:
                raise HTTPException(status_code=404, detail="Token not found")

            logger.info(f"Delisted token: {token_symbol}", admin_id=admin['user_id'])
            return {"success": True, "message": f"Token {token_symbol} delisted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error delisting token: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TRADING PAIR MANAGEMENT
# ============================================================================

@app.post("/api/admin/trading-pairs", status_code=201)
async def create_trading_pair(
    request: TradingPairCreateRequest,
    admin: dict = Depends(require_permission(Permission.MANAGE_TRADING_PAIRS))
):
    """Create a new trading pair"""
    try:
        async with db_pool.acquire() as conn:
            import uuid
            pair_id = f"PAIR_{uuid.uuid4().hex[:8].upper()}"
            symbol = f"{request.base_asset}{request.quote_asset}"
            
            result = await conn.fetchrow("""
                INSERT INTO trading_pairs (
                    pair_id, symbol, base_asset, quote_asset, trading_type,
                    min_order_size, max_order_size, min_price, max_price,
                    price_precision, quantity_precision, maker_fee, taker_fee, status
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, 'active')
                RETURNING *
            """, pair_id, symbol, request.base_asset, request.quote_asset,
                request.trading_type.value, request.min_order_size, request.max_order_size,
                request.min_price, request.max_price, request.price_precision,
                request.quantity_precision, request.maker_fee, request.taker_fee)

            logger.info(f"Created trading pair: {symbol}", admin_id=admin['user_id'])
            return dict(result)

    except Exception as e:
        logger.error(f"Error creating trading pair: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/trading-pairs")
async def get_all_trading_pairs(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    admin: dict = Depends(require_permission(Permission.VIEW_TRADING))
):
    """Get all trading pairs"""
    try:
        async with db_pool.acquire() as conn:
            query = "SELECT * FROM trading_pairs WHERE 1=1"
            params = []

            if status:
                query += " AND status = $1"
                params.append(status)

            query += f" ORDER BY created_at DESC OFFSET ${len(params) + 1} LIMIT ${len(params) + 2}"
            params.extend([skip, limit])

            pairs = await conn.fetch(query, *params)
            total = await conn.fetchval("SELECT COUNT(*) FROM trading_pairs")

            return {
                "total": total,
                "pairs": [dict(p) for p in pairs]
            }

    except Exception as e:
        logger.error(f"Error fetching trading pairs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/admin/trading-pairs/{symbol}")
async def update_trading_pair(
    symbol: str,
    maker_fee: Optional[Decimal] = None,
    taker_fee: Optional[Decimal] = None,
    status: Optional[str] = None,
    admin: dict = Depends(require_permission(Permission.MANAGE_TRADING_PAIRS))
):
    """Update trading pair"""
    try:
        async with db_pool.acquire() as conn:
            updates = []
            params = []
            param_count = 0

            if maker_fee is not None:
                param_count += 1
                updates.append(f"maker_fee = ${param_count}")
                params.append(maker_fee)

            if taker_fee is not None:
                param_count += 1
                updates.append(f"taker_fee = ${param_count}")
                params.append(taker_fee)

            if status is not None:
                param_count += 1
                updates.append(f"status = ${param_count}")
                params.append(status)

            if not updates:
                raise HTTPException(status_code=400, detail="No fields to update")

            param_count += 1
            params.append(symbol)

            query = f"""
                UPDATE trading_pairs
                SET {', '.join(updates)}, updated_at = NOW()
                WHERE symbol = ${param_count}
                RETURNING *
            """

            result = await conn.fetchrow(query, *params)

            if not result:
                raise HTTPException(status_code=404, detail="Trading pair not found")

            logger.info(f"Updated trading pair: {symbol}", admin_id=admin['user_id'])
            return dict(result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating trading pair: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TRADING CONTROL
# ============================================================================

@app.post("/api/admin/trading/pause")
async def pause_trading(
    symbol: Optional[str] = None,
    reason: str = "Manual pause by admin",
    admin: dict = Depends(require_permission(Permission.PAUSE_TRADING))
):
    """Pause trading for specific symbol or all trading"""
    try:
        async with db_pool.acquire() as conn:
            if symbol:
                result = await conn.fetchrow("""
                    UPDATE trading_pairs SET status = 'paused', updated_at = NOW()
                    WHERE symbol = $1 RETURNING *
                """, symbol)
            else:
                result = await conn.execute("""
                    UPDATE trading_pairs SET status = 'paused', updated_at = NOW()
                """)

            # Set Redis flag
            if redis_client:
                key = f"trading:halted:{symbol}" if symbol else "trading:halted:all"
                await redis_client.set(key, "true")
                await redis_client.set(f"{key}:reason", reason)
                await redis_client.set(f"{key}:by", admin['user_id'])

            logger.info(f"Trading paused: {symbol or 'all'} - {reason}", admin_id=admin['user_id'])
            return {"success": True, "message": f"Trading paused for {symbol or 'all symbols'}"}

    except Exception as e:
        logger.error(f"Error pausing trading: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/trading/resume")
async def resume_trading(
    symbol: Optional[str] = None,
    admin: dict = Depends(require_permission(Permission.RESUME_TRADING))
):
    """Resume trading for specific symbol or all trading"""
    try:
        async with db_pool.acquire() as conn:
            if symbol:
                result = await conn.fetchrow("""
                    UPDATE trading_pairs SET status = 'active', updated_at = NOW()
                    WHERE symbol = $1 RETURNING *
                """, symbol)
            else:
                result = await conn.execute("""
                    UPDATE trading_pairs SET status = 'active', updated_at = NOW()
                """)

            # Clear Redis flag
            if redis_client:
                key = f"trading:halted:{symbol}" if symbol else "trading:halted:all"
                await redis_client.delete(key)
                await redis_client.delete(f"{key}:reason")
                await redis_client.delete(f"{key}:by")

            logger.info(f"Trading resumed: {symbol or 'all'}", admin_id=admin['user_id'])
            return {"success": True, "message": f"Trading resumed for {symbol or 'all symbols'}"}

    except Exception as e:
        logger.error(f"Error resuming trading: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SYSTEM HEALTH AND MONITORING
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "comprehensive-admin-service",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/admin/system/status")
async def system_status(
    admin: dict = Depends(require_permission(Permission.SYSTEM_CONFIG))
):
    """Get system status"""
    try:
        status = {
            "database": "connected" if db_pool else "disconnected",
            "redis": "connected" if redis_client else "disconnected",
            "services": {}
        }
        
        # Check Redis
        if redis_client:
            try:
                await redis_client.ping()
                status["redis"] = "healthy"
            except:
                status["redis"] = "unhealthy"
        
        # Check database
        if db_pool:
            try:
                async with db_pool.acquire() as conn:
                    await conn.fetchval("SELECT 1")
                status["database"] = "healthy"
            except:
                status["database"] = "unhealthy"
        
        return status
        
    except Exception as e:
        logger.error(f"Error checking system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8160,
        reload=True,
        log_level="info"
    )