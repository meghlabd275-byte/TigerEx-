"""
Multi-Tenant Architecture Service
TigerEx v11.0.0 - Enterprise Multi-Tenant Management Platform
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
import jwt
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Multi-Tenant Architecture Service", version="1.0.0")

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
JWT_SECRET = "your-secret-key-here"
JWT_ALGORITHM = "HS256"

# Enums
class TenantStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    TERMINATED = "terminated"

class TenantTier(str, Enum):
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    TENANT_ADMIN = "tenant_admin"
    USER = "user"
    VIEWER = "viewer"

# Data Models
@dataclass
class TenantConfiguration:
    tenant_id: str
    tenant_name: str
    domain: str
    database_name: str
    storage_quota_gb: int
    user_limit: int
    api_rate_limit: int
    features_enabled: List[str]
    custom_settings: Dict[str, Any]
    tier: TenantTier
    status: TenantStatus
    created_at: datetime
    updated_at: datetime

class TenantRequest(BaseModel):
    tenant_name: str = Field(..., min_length=3, max_length=100)
    domain: str = Field(..., min_length=3, max_length=100)
    tier: TenantTier = TenantTier.BASIC
    admin_email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    admin_first_name: str = Field(..., min_length=1, max_length=50)
    admin_last_name: str = Field(..., min_length=1, max_length=50)
    company_name: Optional[str] = Field(None, max_length=200)
    industry: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[Dict[str, str]] = None
    custom_settings: Optional[Dict[str, Any]] = {}

class TenantUpdateRequest(BaseModel):
    tenant_name: Optional[str] = Field(None, min_length=3, max_length=100)
    domain: Optional[str] = Field(None, min_length=3, max_length=100)
    tier: Optional[TenantTier] = None
    status: Optional[TenantStatus] = None
    storage_quota_gb: Optional[int] = Field(None, gt=0)
    user_limit: Optional[int] = Field(None, gt=0)
    api_rate_limit: Optional[int] = Field(None, gt=0)
    features_enabled: Optional[List[str]] = None
    custom_settings: Optional[Dict[str, Any]] = None

class UserRequest(BaseModel):
    tenant_id: str
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    role: UserRole = UserRole.USER
    permissions: List[str] = []
    department: Optional[str] = None
    position: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True

class DatabaseConfiguration(BaseModel):
    database_type: str = "postgresql"
    host: str
    port: int = 5432
    username: str
    password: str
    database_name: str
    connection_pool_size: int = 10
    ssl_enabled: bool = True
    backup_frequency: str = "daily"
    retention_days: int = 30

class ResourceUsage(BaseModel):
    tenant_id: str
    storage_used_gb: float
    users_count: int
    api_calls_today: int
    api_calls_month: int
    cpu_usage_percent: float
    memory_usage_percent: float
    bandwidth_used_gb: float
    last_updated: datetime

class FeatureFlag(BaseModel):
    feature_name: str
    enabled: bool
    description: str
    dependencies: List[str] = []
    configuration: Dict[str, Any] = {}

# Service Classes
class TenantManagementService:
    """Core tenant management operations"""
    
    def __init__(self):
        self.tenants = {}
        self.tenant_configs = {}
        self.domain_mapping = {}
        
    async def create_tenant(self, request: TenantRequest) -> TenantConfiguration:
        """Create a new tenant"""
        try:
            # Generate tenant ID
            tenant_id = str(uuid.uuid4())
            
            # Check if domain already exists
            if request.domain in self.domain_mapping:
                raise HTTPException(status_code=400, detail="Domain already exists")
            
            # Get tier configuration
            tier_config = self._get_tier_configuration(request.tier)
            
            # Create tenant configuration
            tenant_config = TenantConfiguration(
                tenant_id=tenant_id,
                tenant_name=request.tenant_name,
                domain=request.domain,
                database_name=f"tigerex_tenant_{tenant_id[:8]}",
                storage_quota_gb=tier_config['storage_quota_gb'],
                user_limit=tier_config['user_limit'],
                api_rate_limit=tier_config['api_rate_limit'],
                features_enabled=tier_config['features'],
                custom_settings=request.custom_settings or {},
                tier=request.tier,
                status=TenantStatus.PENDING,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Store tenant
            self.tenants[tenant_id] = tenant_config
            self.tenant_configs[tenant_id] = tenant_config
            self.domain_mapping[request.domain] = tenant_id
            
            # Initialize tenant infrastructure
            await self._initialize_tenant_infrastructure(tenant_config)
            
            # Create admin user
            await self._create_tenant_admin(tenant_id, request)
            
            logger.info(f"Created new tenant: {tenant_id} ({request.tenant_name})")
            return tenant_config
            
        except Exception as e:
            logger.error(f"Error creating tenant: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def update_tenant(self, tenant_id: str, request: TenantUpdateRequest) -> TenantConfiguration:
        """Update tenant configuration"""
        try:
            if tenant_id not in self.tenants:
                raise HTTPException(status_code=404, detail="Tenant not found")
            
            tenant_config = self.tenants[tenant_id]
            
            # Update fields
            if request.tenant_name:
                tenant_config.tenant_name = request.tenant_name
            if request.domain:
                if request.domain in self.domain_mapping and self.domain_mapping[request.domain] != tenant_id:
                    raise HTTPException(status_code=400, detail="Domain already exists")
                # Remove old domain mapping
                old_domain = tenant_config.domain
                del self.domain_mapping[old_domain]
                # Add new domain mapping
                tenant_config.domain = request.domain
                self.domain_mapping[request.domain] = tenant_id
            if request.tier:
                tenant_config.tier = request.tier
                # Update tier-based settings
                tier_config = self._get_tier_configuration(request.tier)
                tenant_config.storage_quota_gb = tier_config['storage_quota_gb']
                tenant_config.user_limit = tier_config['user_limit']
                tenant_config.api_rate_limit = tier_config['api_rate_limit']
                tenant_config.features_enabled = tier_config['features']
            if request.status:
                tenant_config.status = request.status
            if request.storage_quota_gb:
                tenant_config.storage_quota_gb = request.storage_quota_gb
            if request.user_limit:
                tenant_config.user_limit = request.user_limit
            if request.api_rate_limit:
                tenant_config.api_rate_limit = request.api_rate_limit
            if request.features_enabled:
                tenant_config.features_enabled = request.features_enabled
            if request.custom_settings:
                tenant_config.custom_settings.update(request.custom_settings)
            
            tenant_config.updated_at = datetime.utcnow()
            
            logger.info(f"Updated tenant: {tenant_id}")
            return tenant_config
            
        except Exception as e:
            logger.error(f"Error updating tenant: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_tenant(self, tenant_id: str) -> TenantConfiguration:
        """Get tenant configuration"""
        if tenant_id not in self.tenants:
            raise HTTPException(status_code=404, detail="Tenant not found")
        return self.tenants[tenant_id]
    
    async def list_tenants(self, status: Optional[TenantStatus] = None, 
                          tier: Optional[TenantTier] = None) -> List[TenantConfiguration]:
        """List tenants with optional filters"""
        tenants = list(self.tenants.values())
        
        if status:
            tenants = [t for t in tenants if t.status == status]
        if tier:
            tenants = [t for t in tenants if t.tier == tier]
        
        return tenants
    
    async def delete_tenant(self, tenant_id: str) -> bool:
        """Delete tenant and all associated data"""
        try:
            if tenant_id not in self.tenants:
                raise HTTPException(status_code=404, detail="Tenant not found")
            
            tenant_config = self.tenants[tenant_id]
            
            # Remove domain mapping
            del self.domain_mapping[tenant_config.domain]
            
            # Remove tenant
            del self.tenants[tenant_id]
            del self.tenant_configs[tenant_id]
            
            # Cleanup tenant infrastructure
            await self._cleanup_tenant_infrastructure(tenant_config)
            
            logger.info(f"Deleted tenant: {tenant_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting tenant: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _get_tier_configuration(self, tier: TenantTier) -> Dict[str, Any]:
        """Get configuration for tenant tier"""
        tier_configs = {
            TenantTier.BASIC: {
                'storage_quota_gb': 10,
                'user_limit': 5,
                'api_rate_limit': 1000,
                'features': ['basic_trading', 'portfolio_tracking', 'basic_analytics']
            },
            TenantTier.PROFESSIONAL: {
                'storage_quota_gb': 100,
                'user_limit': 50,
                'api_rate_limit': 10000,
                'features': ['advanced_trading', 'portfolio_analytics', 'ai_insights', 'api_access']
            },
            TenantTier.ENTERPRISE: {
                'storage_quota_gb': 1000,
                'user_limit': 500,
                'api_rate_limit': 100000,
                'features': ['all_features', 'custom_integrations', 'dedicated_support', 'white_label']
            },
            TenantTier.CUSTOM: {
                'storage_quota_gb': 0,  # Configured per tenant
                'user_limit': 0,  # Configured per tenant
                'api_rate_limit': 0,  # Configured per tenant
                'features': ['custom_features']
            }
        }
        return tier_configs.get(tier, tier_configs[TenantTier.BASIC])
    
    async def _initialize_tenant_infrastructure(self, tenant_config: TenantConfiguration):
        """Initialize tenant-specific infrastructure"""
        # Mock implementation - would create database, storage, etc.
        logger.info(f"Initializing infrastructure for tenant: {tenant_config.tenant_id}")
        await asyncio.sleep(0.1)  # Simulate async work
    
    async def _create_tenant_admin(self, tenant_id: str, request: TenantRequest):
        """Create tenant admin user"""
        # Mock implementation
        logger.info(f"Creating admin user for tenant: {tenant_id}")
        await asyncio.sleep(0.1)  # Simulate async work
    
    async def _cleanup_tenant_infrastructure(self, tenant_config: TenantConfiguration):
        """Clean up tenant-specific infrastructure"""
        # Mock implementation
        logger.info(f"Cleaning up infrastructure for tenant: {tenant_config.tenant_id}")
        await asyncio.sleep(0.1)  # Simulate async work

class UserManagementService:
    """User management within tenants"""
    
    def __init__(self):
        self.users = {}
        self.tenant_users = defaultdict(list)
    
    async def create_user(self, request: UserRequest) -> Dict[str, Any]:
        """Create a new user in a tenant"""
        try:
            # Check if tenant exists
            if request.tenant_id not in tenant_manager.tenants:
                raise HTTPException(status_code=404, detail="Tenant not found")
            
            # Check user limit
            tenant_config = tenant_manager.tenants[request.tenant_id]
            current_users = len(self.tenant_users[request.tenant_id])
            if current_users >= tenant_config.user_limit:
                raise HTTPException(status_code=400, detail="User limit exceeded")
            
            # Generate user ID
            user_id = str(uuid.uuid4())
            
            # Create user
            user = {
                'user_id': user_id,
                'tenant_id': request.tenant_id,
                'email': request.email,
                'first_name': request.first_name,
                'last_name': request.last_name,
                'role': request.role,
                'permissions': request.permissions,
                'department': request.department,
                'position': request.position,
                'phone': request.phone,
                'is_active': request.is_active,
                'created_at': datetime.utcnow(),
                'last_login': None
            }
            
            # Store user
            self.users[user_id] = user
            self.tenant_users[request.tenant_id].append(user_id)
            
            logger.info(f"Created user: {user_id} in tenant: {request.tenant_id}")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get user details"""
        if user_id not in self.users:
            raise HTTPException(status_code=404, detail="User not found")
        return self.users[user_id]
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user details"""
        if user_id not in self.users:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = self.users[user_id]
        user.update(update_data)
        user['updated_at'] = datetime.utcnow()
        
        return user
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        if user_id not in self.users:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = self.users[user_id]
        tenant_id = user['tenant_id']
        
        # Remove from tenant users
        self.tenant_users[tenant_id].remove(user_id)
        
        # Delete user
        del self.users[user_id]
        
        return True
    
    async def list_tenant_users(self, tenant_id: str) -> List[Dict[str, Any]]:
        """List users in a tenant"""
        user_ids = self.tenant_users.get(tenant_id, [])
        return [self.users[user_id] for user_id in user_ids]

class ResourceMonitoringService:
    """Monitor and manage tenant resource usage"""
    
    def __init__(self):
        self.usage_data = {}
    
    async def get_resource_usage(self, tenant_id: str) -> ResourceUsage:
        """Get current resource usage for tenant"""
        # Mock implementation
        usage = ResourceUsage(
            tenant_id=tenant_id,
            storage_used_gb=5.2,
            users_count=12,
            api_calls_today=850,
            api_calls_month=15000,
            cpu_usage_percent=15.5,
            memory_usage_percent=42.3,
            bandwidth_used_gb=125.8,
            last_updated=datetime.utcnow()
        )
        
        self.usage_data[tenant_id] = usage
        return usage
    
    async def get_usage_history(self, tenant_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical usage data"""
        # Mock implementation
        history = []
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=i)
            history.append({
                'date': date.strftime('%Y-%m-%d'),
                'storage_used_gb': 5.0 + (i * 0.1),
                'api_calls': 500 + (i * 50),
                'active_users': 10 + (i % 5),
                'bandwidth_gb': 100 + (i * 2)
            })
        
        return history
    
    async def check_resource_limits(self, tenant_id: str) -> Dict[str, bool]:
        """Check if tenant is approaching resource limits"""
        if tenant_id not in tenant_manager.tenants:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        tenant_config = tenant_manager.tenants[tenant_id]
        usage = await self.get_resource_usage(tenant_id)
        
        limits_status = {
            'storage_warning': usage.storage_used_gb > (tenant_config.storage_quota_gb * 0.8),
            'storage_critical': usage.storage_used_gb > (tenant_config.storage_quota_gb * 0.95),
            'users_warning': usage.users_count > (tenant_config.user_limit * 0.8),
            'users_critical': usage.users_count > (tenant_config.user_limit * 0.95),
            'api_warning': usage.api_calls_today > (tenant_config.api_rate_limit * 0.8),
            'api_critical': usage.api_calls_today > tenant_config.api_rate_limit
        }
        
        return limits_status

class SecurityService:
    """Multi-tenant security management"""
    
    def __init__(self):
        self.api_keys = {}
        self.session_tokens = {}
    
    async def generate_api_key(self, tenant_id: str, user_id: str) -> str:
        """Generate API key for tenant user"""
        api_key = str(uuid.uuid4())
        self.api_keys[api_key] = {
            'tenant_id': tenant_id,
            'user_id': user_id,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(days=365)
        }
        return api_key
    
    async def revoke_api_key(self, api_key: str) -> bool:
        """Revoke API key"""
        if api_key in self.api_keys:
            del self.api_keys[api_key]
            return True
        return False
    
    async def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key and return associated info"""
        if api_key not in self.api_keys:
            return None
        
        key_info = self.api_keys[api_key]
        if key_info['expires_at'] < datetime.utcnow():
            del self.api_keys[api_key]
            return None
        
        return key_info
    
    async def create_session_token(self, user_id: str, tenant_id: str) -> str:
        """Create JWT session token"""
        payload = {
            'user_id': user_id,
            'tenant_id': tenant_id,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        self.session_tokens[token] = {
            'user_id': user_id,
            'tenant_id': tenant_id,
            'created_at': datetime.utcnow()
        }
        
        return token
    
    async def validate_session_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT session token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            if token in self.session_tokens:
                del self.session_tokens[token]
            return None
        except jwt.InvalidTokenError:
            return None

# Initialize services
tenant_manager = TenantManagementService()
user_manager = UserManagementService()
resource_monitor = ResourceMonitoringService()
security_service = SecurityService()

# API Endpoints
@app.post("/api/v1/tenants")
async def create_tenant(request: TenantRequest,
                       credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create a new tenant"""
    try:
        # Validate super admin permissions (mock)
        tenant_config = await tenant_manager.create_tenant(request)
        
        return {
            "success": True,
            "data": {
                "tenant_id": tenant_config.tenant_id,
                "tenant_name": tenant_config.tenant_name,
                "domain": tenant_config.domain,
                "tier": tenant_config.tier,
                "status": tenant_config.status,
                "created_at": tenant_config.created_at.isoformat(),
                "setup_url": f"https://{tenant_config.domain}.tigerex.com/setup"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in create tenant endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/tenants/{tenant_id}")
async def get_tenant(tenant_id: str,
                    credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get tenant details"""
    try:
        tenant_config = await tenant_manager.get_tenant(tenant_id)
        
        return {
            "success": True,
            "data": {
                "tenant_id": tenant_config.tenant_id,
                "tenant_name": tenant_config.tenant_name,
                "domain": tenant_config.domain,
                "tier": tenant_config.tier,
                "status": tenant_config.status,
                "storage_quota_gb": tenant_config.storage_quota_gb,
                "user_limit": tenant_config.user_limit,
                "api_rate_limit": tenant_config.api_rate_limit,
                "features_enabled": tenant_config.features_enabled,
                "created_at": tenant_config.created_at.isoformat(),
                "updated_at": tenant_config.updated_at.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error in get tenant endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/tenants/{tenant_id}")
async def update_tenant(tenant_id: str, request: TenantUpdateRequest,
                       credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update tenant configuration"""
    try:
        tenant_config = await tenant_manager.update_tenant(tenant_id, request)
        
        return {
            "success": True,
            "data": {
                "tenant_id": tenant_config.tenant_id,
                "tenant_name": tenant_config.tenant_name,
                "domain": tenant_config.domain,
                "tier": tenant_config.tier,
                "status": tenant_config.status,
                "updated_at": tenant_config.updated_at.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error in update tenant endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/tenants")
async def list_tenants(status: Optional[TenantStatus] = None,
                      tier: Optional[TenantTier] = None,
                      credentials: HTTPAuthorizationCredentials = Depends(security)):
    """List tenants"""
    try:
        tenants = await tenant_manager.list_tenants(status, tier)
        
        return {
            "success": True,
            "data": [
                {
                    "tenant_id": t.tenant_id,
                    "tenant_name": t.tenant_name,
                    "domain": t.domain,
                    "tier": t.tier,
                    "status": t.status,
                    "created_at": t.created_at.isoformat()
                }
                for t in tenants
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in list tenants endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/tenants/{tenant_id}")
async def delete_tenant(tenant_id: str,
                       credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Delete tenant"""
    try:
        result = await tenant_manager.delete_tenant(tenant_id)
        
        return {
            "success": True,
            "message": "Tenant deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error in delete tenant endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/tenants/{tenant_id}/users")
async def create_tenant_user(tenant_id: str, request: UserRequest,
                            credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create user in tenant"""
    try:
        request.tenant_id = tenant_id
        user = await user_manager.create_user(request)
        
        return {
            "success": True,
            "data": {
                "user_id": user['user_id'],
                "email": user['email'],
                "first_name": user['first_name'],
                "last_name": user['last_name'],
                "role": user['role'],
                "created_at": user['created_at'].isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error in create user endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/tenants/{tenant_id}/users")
async def list_tenant_users(tenant_id: str,
                           credentials: HTTPAuthorizationCredentials = Depends(security)):
    """List users in tenant"""
    try:
        users = await user_manager.list_tenant_users(tenant_id)
        
        return {
            "success": True,
            "data": [
                {
                    "user_id": u['user_id'],
                    "email": u['email'],
                    "first_name": u['first_name'],
                    "last_name": u['last_name'],
                    "role": u['role'],
                    "is_active": u['is_active'],
                    "created_at": u['created_at'].isoformat()
                }
                for u in users
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in list users endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/tenants/{tenant_id}/usage")
async def get_tenant_usage(tenant_id: str,
                          credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get tenant resource usage"""
    try:
        usage = await resource_monitor.get_resource_usage(tenant_id)
        limits_status = await resource_monitor.check_resource_limits(tenant_id)
        
        return {
            "success": True,
            "data": {
                "tenant_id": usage.tenant_id,
                "storage_used_gb": usage.storage_used_gb,
                "users_count": usage.users_count,
                "api_calls_today": usage.api_calls_today,
                "api_calls_month": usage.api_calls_month,
                "cpu_usage_percent": usage.cpu_usage_percent,
                "memory_usage_percent": usage.memory_usage_percent,
                "bandwidth_used_gb": usage.bandwidth_used_gb,
                "last_updated": usage.last_updated.isoformat(),
                "limits_status": limits_status
            }
        }
        
    except Exception as e:
        logger.error(f"Error in tenant usage endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/tenants/{tenant_id}/api-keys")
async def generate_api_key(tenant_id: str,
                          credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Generate API key for tenant"""
    try:
        # Mock user ID extraction from token
        user_id = "mock_user_id"
        api_key = await security_service.generate_api_key(tenant_id, user_id)
        
        return {
            "success": True,
            "data": {
                "api_key": api_key,
                "tenant_id": tenant_id,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(days=365)).isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error in generate API key endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "multi-tenant-architecture"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8010)