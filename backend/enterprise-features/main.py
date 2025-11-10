"""
Enterprise Features Service
TigerEx v11.0.0 - Enterprise-Grade Trading Platform Features
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Enterprise Features Service", version="1.0.0")

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
class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ENTERPRISE_ADMIN = "enterprise_admin"
    TRADING_ADMIN = "trading_admin"
    COMPLIANCE_OFFICER = "compliance_officer"
    RISK_MANAGER = "risk_manager"
    OPERATIONS_MANAGER = "operations_manager"
    TRADER = "trader"
    VIEWER = "viewer"

class PermissionLevel(str, Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"

class AccountType(str, Enum):
    CORPORATE = "corporate"
    HEDGE_FUND = "hedge_fund"
    PROP_TRADING = "prop_trading"
    FAMILY_OFFICE = "family_office"
    ASSET_MANAGER = "asset_manager"
    BANK = "bank"
    INSURANCE = "insurance"

class ReportingType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"

class IntegrationType(str, Enum):
    ERP = "erp"
    CRM = "crm"
    RISK_MANAGEMENT = "risk_management"
    COMPLIANCE = "compliance"
    ACCOUNTING = "accounting"
    MARKET_DATA = "market_data"
    EXECUTION = "execution"

# Data Models
class EnterpriseAccount(BaseModel):
    account_id: str
    account_name: str
    account_type: AccountType
    parent_account_id: Optional[str] = None
    child_account_ids: List[str] = []
    legal_entity: str
    registration_number: str
    tax_id: str
    contact_info: Dict[str, str]
    compliance_level: str
    created_at: datetime
    status: str
    settings: Dict[str, Any] = {}

class UserPermission(BaseModel):
    user_id: str
    account_id: str
    role: UserRole
    permissions: List[str]
    granted_at: datetime
    granted_by: str
    expires_at: Optional[datetime] = None

class RiskLimit(BaseModel):
    limit_id: str
    account_id: str
    limit_type: str
    limit_value: float
    current_utilization: float
    warning_threshold: float
    is_active: bool
    created_at: datetime
    updated_at: datetime

class CustomReport(BaseModel):
    report_id: str
    account_id: str
    report_name: str
    report_type: ReportingType
    template: str
    parameters: Dict[str, Any]
    schedule: Dict[str, str]
    recipients: List[str]
    is_active: bool
    created_at: datetime
    last_generated: Optional[datetime] = None

class SystemIntegration(BaseModel):
    integration_id: str
    account_id: str
    integration_type: IntegrationType
    provider: str
    configuration: Dict[str, Any]
    status: str
    last_sync: Optional[datetime] = None
    error_count: int = 0
    created_at: datetime

class WorkflowDefinition(BaseModel):
    workflow_id: str
    account_id: str
    workflow_name: str
    description: str
    steps: List[Dict[str, Any]]
    triggers: List[Dict[str, Any]]
    approvers: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

# Service Classes
class EnterpriseAccountService:
    """Manage enterprise accounts and hierarchy"""
    
    def __init__(self):
        self.accounts = {}
        self.account_hierarchy = {}
        self.compliance_frameworks = {}
    
    async def create_account(self, account_data: Dict[str, Any]) -> EnterpriseAccount:
        """Create new enterprise account"""
        try:
            account_id = str(uuid.uuid4())
            
            # Validate parent account if specified
            parent_id = account_data.get("parent_account_id")
            if parent_id and parent_id not in self.accounts:
                raise HTTPException(status_code=400, detail="Parent account not found")
            
            account = EnterpriseAccount(
                account_id=account_id,
                account_name=account_data["account_name"],
                account_type=AccountType(account_data["account_type"]),
                parent_account_id=parent_id,
                legal_entity=account_data["legal_entity"],
                registration_number=account_data["registration_number"],
                tax_id=account_data["tax_id"],
                contact_info=account_data.get("contact_info", {}),
                compliance_level=account_data.get("compliance_level", "standard"),
                created_at=datetime.utcnow(),
                status="active",
                settings=account_data.get("settings", {})
            )
            
            self.accounts[account_id] = account
            
            # Update hierarchy
            if parent_id:
                self.accounts[parent_id].child_account_ids.append(account_id)
                self.account_hierarchy[account_id] = parent_id
            
            # Initialize compliance setup
            await self._initialize_compliance(account_id, account.account_type)
            
            logger.info(f"Created enterprise account: {account_id}")
            return account
            
        except Exception as e:
            logger.error(f"Error creating account: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_account_hierarchy(self, account_id: str) -> Dict[str, Any]:
        """Get complete account hierarchy"""
        try:
            if account_id not in self.accounts:
                raise HTTPException(status_code=404, detail="Account not found")
            
            hierarchy = self._build_hierarchy_tree(account_id)
            
            return {
                "root_account": self.accounts[account_id].dict(),
                "hierarchy_tree": hierarchy,
                "total_accounts": len(self._get_all_child_accounts(account_id)) + 1,
                "depth": self._calculate_hierarchy_depth(account_id)
            }
            
        except Exception as e:
            logger.error(f"Error getting account hierarchy: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _build_hierarchy_tree(self, account_id: str) -> Dict[str, Any]:
        """Build hierarchy tree recursively"""
        account = self.accounts[account_id]
        tree = {
            "account_id": account_id,
            "account_name": account.account_name,
            "account_type": account.account_type,
            "children": []
        }
        
        for child_id in account.child_account_ids:
            if child_id in self.accounts:
                tree["children"].append(self._build_hierarchy_tree(child_id))
        
        return tree
    
    def _get_all_child_accounts(self, account_id: str) -> List[str]:
        """Get all child account IDs recursively"""
        children = []
        account = self.accounts.get(account_id)
        
        if account:
            for child_id in account.child_account_ids:
                children.append(child_id)
                children.extend(self._get_all_child_accounts(child_id))
        
        return children
    
    def _calculate_hierarchy_depth(self, account_id: str) -> int:
        """Calculate maximum depth of hierarchy"""
        account = self.accounts.get(account_id)
        if not account or not account.child_account_ids:
            return 1
        
        max_child_depth = 0
        for child_id in account.child_account_ids:
            child_depth = self._calculate_hierarchy_depth(child_id)
            max_child_depth = max(max_child_depth, child_depth)
        
        return max_child_depth + 1
    
    async def _initialize_compliance(self, account_id: str, account_type: AccountType):
        """Initialize compliance framework for account"""
        compliance_config = {
            AccountType.HEDGE_FUND: {
                "reporting_requirements": ["form_13f", "form_adv"],
                "audit_frequency": "quarterly",
                "risk_assessment": "monthly"
            },
            AccountType.BANK: {
                "reporting_requirements": ["call_reports", "sar"],
                "audit_frequency": "monthly",
                "risk_assessment": "weekly"
            },
            AccountType.ASSET_MANAGER: {
                "reporting_requirements": ["gips_compliance", "form_adv"],
                "audit_frequency": "semi_annual",
                "risk_assessment": "monthly"
            }
        }
        
        self.compliance_frameworks[account_id] = compliance_config.get(
            account_type, {
                "reporting_requirements": ["basic_trading_reports"],
                "audit_frequency": "annual",
                "risk_assessment": "quarterly"
            }
        )

class PermissionManagementService:
    """Manage user permissions and roles"""
    
    def __init__(self):
        self.user_permissions = {}
        self.role_permissions = self._initialize_role_permissions()
    
    def _initialize_role_permissions(self) -> Dict[UserRole, List[str]]:
        """Initialize role-based permissions"""
        return {
            UserRole.SUPER_ADMIN: [
                "account.admin", "user.admin", "trading.admin", 
                "compliance.admin", "risk.admin", "system.admin"
            ],
            UserRole.ENTERPRISE_ADMIN: [
                "account.manage", "user.manage", "trading.manage",
                "compliance.view", "risk.view", "reporting.admin"
            ],
            UserRole.TRADING_ADMIN: [
                "trading.execute", "trading.approve", "position.manage",
                "order.manage", "risk.view"
            ],
            UserRole.COMPLIANCE_OFFICER: [
                "compliance.monitor", "compliance.report", "user.suspend",
                "trading.view", "audit.view"
            ],
            UserRole.RISK_MANAGER: [
                "risk.monitor", "risk.approve", "position.view",
                "trading.view", "limits.manage"
            ],
            UserRole.OPERATIONS_MANAGER: [
                "operations.manage", "system.monitor", "support.admin",
                "reporting.view"
            ],
            UserRole.TRADER: [
                "trading.execute", "position.view", "order.create",
                "market_data.view"
            ],
            UserRole.VIEWER: [
                "dashboard.view", "reporting.view", "market_data.view"
            ]
        }
    
    async def assign_permission(self, user_id: str, account_id: str, role: UserRole, 
                              granted_by: str, expires_at: Optional[datetime] = None) -> UserPermission:
        """Assign permission to user"""
        try:
            permission = UserPermission(
                user_id=user_id,
                account_id=account_id,
                role=role,
                permissions=self.role_permissions[role],
                granted_at=datetime.utcnow(),
                granted_by=granted_by,
                expires_at=expires_at
            )
            
            permission_key = f"{user_id}_{account_id}"
            self.user_permissions[permission_key] = permission
            
            logger.info(f"Assigned permission {role} to user {user_id} for account {account_id}")
            return permission
            
        except Exception as e:
            logger.error(f"Error assigning permission: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

class RiskManagementService:
    """Enterprise risk management"""
    
    def __init__(self):
        self.risk_limits = {}
    
    async def set_risk_limit(self, account_id: str, limit_type: str, limit_value: float, 
                           warning_threshold: float) -> RiskLimit:
        """Set risk limit for account"""
        try:
            limit_id = str(uuid.uuid4())
            
            risk_limit = RiskLimit(
                limit_id=limit_id,
                account_id=account_id,
                limit_type=limit_type,
                limit_value=limit_value,
                current_utilization=0.0,
                warning_threshold=warning_threshold,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.risk_limits[limit_id] = risk_limit
            
            logger.info(f"Set risk limit {limit_type} for account {account_id}: {limit_value}")
            return risk_limit
            
        except Exception as e:
            logger.error(f"Error setting risk limit: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

class ReportingService:
    """Enterprise reporting service"""
    
    def __init__(self):
        self.reports = {}
    
    async def create_custom_report(self, report_data: Dict[str, Any]) -> CustomReport:
        """Create custom report"""
        try:
            report_id = str(uuid.uuid4())
            
            report = CustomReport(
                report_id=report_id,
                account_id=report_data["account_id"],
                report_name=report_data["report_name"],
                report_type=ReportingType(report_data["report_type"]),
                template=report_data["template"],
                parameters=report_data.get("parameters", {}),
                schedule=report_data.get("schedule", {}),
                recipients=report_data.get("recipients", []),
                is_active=report_data.get("is_active", True),
                created_at=datetime.utcnow()
            )
            
            self.reports[report_id] = report
            
            logger.info(f"Created custom report: {report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error creating custom report: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

# Initialize services
enterprise_service = EnterpriseAccountService()
permission_service = PermissionManagementService()
risk_service = RiskManagementService()
reporting_service = ReportingService()

# API Endpoints
@app.post("/api/v1/enterprise/accounts")
async def create_enterprise_account(account_data: Dict[str, Any],
                                  credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create enterprise account"""
    try:
        account = await enterprise_service.create_account(account_data)
        
        return {
            "success": True,
            "data": {
                "account_id": account.account_id,
                "account_name": account.account_name,
                "account_type": account.account_type,
                "created_at": account.created_at.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error in create account endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/enterprise/accounts/{account_id}/hierarchy")
async def get_account_hierarchy(account_id: str,
                              credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get account hierarchy"""
    try:
        hierarchy = await enterprise_service.get_account_hierarchy(account_id)
        
        return {
            "success": True,
            "data": hierarchy
        }
        
    except Exception as e:
        logger.error(f"Error in hierarchy endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/enterprise/permissions/assign")
async def assign_permission(user_id: str, account_id: str, role: UserRole,
                          granted_by: str,
                          credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Assign user permission"""
    try:
        permission = await permission_service.assign_permission(user_id, account_id, role, granted_by)
        
        return {
            "success": True,
            "data": {
                "user_id": user_id,
                "account_id": account_id,
                "role": role,
                "granted_at": permission.granted_at.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error in assign permission endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/enterprise/risk/limits")
async def set_risk_limit(account_id: str, limit_type: str, limit_value: float,
                        warning_threshold: float,
                        credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Set risk limit"""
    try:
        risk_limit = await risk_service.set_risk_limit(account_id, limit_type, limit_value, warning_threshold)
        
        return {
            "success": True,
            "data": {
                "limit_id": risk_limit.limit_id,
                "limit_type": limit_type,
                "limit_value": limit_value,
                "created_at": risk_limit.created_at.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error in set risk limit endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/enterprise/reports/create")
async def create_custom_report(report_data: Dict[str, Any],
                             credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Create custom report"""
    try:
        report = await reporting_service.create_custom_report(report_data)
        
        return {
            "success": True,
            "data": {
                "report_id": report.report_id,
                "report_name": report.report_name,
                "report_type": report.report_type,
                "created_at": report.created_at.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error in create report endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/enterprise/dashboard/summary")
async def get_enterprise_dashboard(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get enterprise dashboard summary"""
    try:
        summary = {
            "total_accounts": len(enterprise_service.accounts),
            "active_users": len(permission_service.user_permissions),
            "risk_limits": len(risk_service.risk_limits),
            "custom_reports": len(reporting_service.reports),
            "system_health": "operational",
            "recent_activities": [
                {
                    "type": "account_created",
                    "timestamp": datetime.utcnow().isoformat(),
                    "details": "New corporate account created"
                },
                {
                    "type": "permission_granted",
                    "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                    "details": "Trading permissions granted to user"
                }
            ]
        }
        
        return {
            "success": True,
            "data": summary
        }
        
    except Exception as e:
        logger.error(f"Error in dashboard endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "enterprise-features"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8016)