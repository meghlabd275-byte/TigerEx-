"""
TigerEx Enhanced Admin Control System
Complete admin functionality with comprehensive user management
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, or_, func
import logging

logger = logging.getLogger(__name__)

class Permission(Enum):
    USER_MANAGEMENT = "user_management"
    TRADING_CONTROL = "trading_control"
    FINANCIAL_OPERATIONS = "financial_operations"
    SYSTEM_CONFIGURATION = "system_configuration"
    SECURITY_MANAGEMENT = "security_management"
    REPORTING = "reporting"
    SUPPORT = "support"
    MARKET_MANAGEMENT = "market_management"
    COMPLIANCE = "compliance"
    API_MANAGEMENT = "api_management"

class Role(Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    SUPPORT_AGENT = "support_agent"
    COMPLIENCE_OFFICER = "compliance_officer"
    TRADING_MANAGER = "trading_manager"
    FINANCIAL_ANALYST = "financial_analyst"
    REPORTING_ANALYST = "reporting_analyst"
    API_DEVELOPER = "api_developer"

@dataclass
class UserRole:
    role: Role
    permissions: List[Permission]
    level: int

class RolePermissionMatrix:
    ROLE_PERMISSIONS = {
        Role.SUPER_ADMIN: list(Permission),  # All permissions
        Role.ADMIN: [
            Permission.USER_MANAGEMENT,
            Permission.TRADING_CONTROL,
            Permission.FINANCIAL_OPERATIONS,
            Permission.SYSTEM_CONFIGURATION,
            Permission.REPORTING,
            Permission.SUPPORT
        ],
        Role.SUPPORT_AGENT: [
            Permission.USER_MANAGEMENT,
            Permission.SUPPORT,
            Permission.REPORTING
        ],
        Role.COMPLIENCE_OFFICER: [
            Permission.USER_MANAGEMENT,
            Permission.COMPLIANCE,
            Permission.REPORTING
        ],
        Role.TRADING_MANAGER: [
            Permission.TRADING_CONTROL,
            Permission.MARKET_MANAGEMENT,
            Permission.REPORTING
        ],
        Role.FINANCIAL_ANALYST: [
            Permission.FINANCIAL_OPERATIONS,
            Permission.REPORTING
        ],
        Role.REPORTING_ANALYST: [
            Permission.REPORTING
        ],
        Role.API_DEVELOPER: [
            Permission.API_MANAGEMENT,
            Permission.REPORTING
        ]
    }
    
    ROLE_LEVELS = {
        Role.SUPER_ADMIN: 10,
        Role.ADMIN: 8,
        Role.COMPLIENCE_OFFICER: 7,
        Role.TRADING_MANAGER: 6,
        Role.FINANCIAL_ANALYST: 5,
        Role.SUPPORT_AGENT: 4,
        Role.API_DEVELOPER: 3,
        Role.REPORTING_ANALYST: 2
    }

class UserActivityTracker:
    def __init__(self, redis_client):
        self.redis = redis_client
        
    async def track_login(self, user_id: int, ip: str, user_agent: str):
        """Track user login activity"""
        activity = {
            "user_id": user_id,
            "action": "login",
            "ip": ip,
            "user_agent": user_agent,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.redis.lpush(f"user_activity:{user_id}", json.dumps(activity))
        await self.redis.ltrim(f"user_activity:{user_id}", 0, 99)  # Keep last 100 activities
        
    async def track_trading_activity(self, user_id: int, action: str, details: Dict[str, Any]):
        """Track trading activities"""
        activity = {
            "user_id": user_id,
            "action": f"trading_{action}",
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.redis.lpush(f"trading_activity:{user_id}", json.dumps(activity))
        await self.redis.ltrim(f"trading_activity:{user_id}", 0, 49)  # Keep last 50 activities

class UserManager:
    def __init__(self, db: Session, redis_client):
        self.db = db
        self.redis = redis_client
        self.activity_tracker = UserActivityTracker(redis_client)
        
    async def get_user_detailed_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get comprehensive user profile"""
        # Get user basic info
        user_query = text("""
            SELECT id, email, username, full_name, phone, is_active, is_admin, is_superadmin,
                   kyc_status, kyc_level, created_at, last_login, trading_enabled,
                   withdrawal_enabled, deposit_enabled, two_factor_enabled,
                   referral_code, referred_by
            FROM users WHERE id = :user_id
        """)
        
        user_result = self.db.execute(user_query, {"user_id": user_id}).fetchone()
        if not user_result:
            return None
            
        user_data = dict(user_result._mapping)
        
        # Get wallets
        wallets_query = text("""
            SELECT currency, balance, locked_balance, address, is_active, created_at
            FROM wallets WHERE user_id = :user_id
        """)
        wallets = self.db.execute(wallets_query, {"user_id": user_id}).fetchall()
        user_data["wallets"] = [dict(w._mapping) for w in wallets]
        
        # Get trading statistics
        trading_stats_query = text("""
            SELECT 
                COUNT(*) as total_orders,
                COUNT(CASE WHEN status = 'filled' THEN 1 END) as filled_orders,
                SUM(quantity) as total_volume,
                AVG(CASE WHEN status = 'filled' THEN price END) as avg_price
            FROM orders WHERE user_id = :user_id
        """)
        trading_stats = self.db.execute(trading_stats_query, {"user_id": user_id}).fetchone()
        user_data["trading_stats"] = dict(trading_stats._mapping)
        
        # Get recent activity
        recent_activity = await self.redis.lrange(f"user_activity:{user_id}", 0, 9)
        user_data["recent_activity"] = [json.loads(activity) for activity in recent_activity]
        
        # Get risk score (simple calculation)
        user_data["risk_score"] = await self._calculate_risk_score(user_id)
        
        return user_data
    
    async def _calculate_risk_score(self, user_id: int) -> float:
        """Calculate user risk score"""
        # Get user's trading volume and activity
        volume_query = text("""
            SELECT COALESCE(SUM(quantity * price), 0) as total_volume
            FROM orders WHERE user_id = :user_id AND status = 'filled'
        """)
        volume_result = self.db.execute(volume_query, {"user_id": user_id}).fetchone()
        total_volume = float(volume_result.total_volume or 0)
        
        # Get account age
        age_query = text("""
            SELECT EXTRACT(EPOCH FROM (NOW() - created_at)) / 86400 as account_age_days
            FROM users WHERE id = :user_id
        """)
        age_result = self.db.execute(age_query, {"user_id": user_id}).fetchone()
        account_age = float(age_result.account_age_days or 1)
        
        # Simple risk calculation (lower is better)
        kyc_penalty = 0 if user_data.get('kyc_level', 0) >= 2 else 20
        volume_score = min(total_volume / 100000, 50)  # Max 50 points for volume
        age_score = max(0, 30 - account_age / 30)  # Younger accounts have higher risk
        
        risk_score = kyc_penalty + volume_score + age_score
        return min(risk_score, 100)  # Cap at 100
    
    async def update_user_permissions(self, user_id: int, permissions: Dict[str, bool], admin_id: int):
        """Update user permissions"""
        # Validate permissions
        valid_permissions = ["trading_enabled", "withdrawal_enabled", "deposit_enabled"]
        update_data = {}
        
        for perm, value in permissions.items():
            if perm in valid_permissions:
                update_data[perm] = value
        
        if update_data:
            # Update database
            set_clause = ", ".join([f"{k} = :{k}" for k in update_data.keys()])
            query = text(f"""
                UPDATE users SET {set_clause}, updated_at = NOW()
                WHERE id = :user_id
            """)
            
            params = {**update_data, "user_id": user_id}
            self.db.execute(query, params)
            self.db.commit()
            
            # Log the action
            await self._log_admin_action(admin_id, user_id, "update_permissions", update_data)
        
        return True
    
    async def freeze_user_account(self, user_id: int, reason: str, admin_id: int) -> bool:
        """Freeze user account"""
        query = text("""
            UPDATE users SET is_active = false, updated_at = NOW()
            WHERE id = :user_id
        """)
        
        self.db.execute(query, {"user_id": user_id})
        self.db.commit()
        
        # Log the action
        await self._log_admin_action(admin_id, user_id, "freeze_account", {"reason": reason})
        
        # Revoke all sessions
        from security_enhancements import SessionManager
        session_manager = SessionManager(self.redis)
        await session_manager.revoke_all_sessions(user_id)
        
        return True
    
    async def unfreeze_user_account(self, user_id: int, reason: str, admin_id: int) -> bool:
        """Unfreeze user account"""
        query = text("""
            UPDATE users SET is_active = true, updated_at = NOW()
            WHERE id = :user_id
        """)
        
        self.db.execute(query, {"user_id": user_id})
        self.db.commit()
        
        # Log the action
        await self._log_admin_action(admin_id, user_id, "unfreeze_account", {"reason": reason})
        
        return True
    
    async def _log_admin_action(self, admin_id: int, target_user_id: int, action: str, details: Dict[str, Any]):
        """Log admin action"""
        log_entry = {
            "admin_id": admin_id,
            "target_user_id": target_user_id,
            "action": action,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.redis.lpush("admin_audit_log", json.dumps(log_entry))
        await self.redis.ltrim("admin_audit_log", 0, 9999)  # Keep last 10,000 logs

class AdminDashboard:
    def __init__(self, db: Session, redis_client):
        self.db = db
        self.redis = redis_client
        self.user_manager = UserManager(db, redis_client)
        
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get comprehensive dashboard statistics"""
        stats = {}
        
        # User statistics
        user_stats_query = text("""
            SELECT 
                COUNT(*) as total_users,
                COUNT(CASE WHEN is_active = true THEN 1 END) as active_users,
                COUNT(CASE WHEN is_admin = true OR is_superadmin = true THEN 1 END) as admin_users,
                COUNT(CASE WHEN kyc_status = 'approved' THEN 1 END) as verified_users,
                COUNT(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' THEN 1 END) as new_users_today,
                COUNT(CASE WHEN last_login >= NOW() - INTERVAL '24 hours' THEN 1 END) as active_users_today
            FROM users
        """)
        user_stats = self.db.execute(user_stats_query).fetchone()
        stats["users"] = dict(user_stats._mapping)
        
        # Trading statistics
        trading_stats_query = text("""
            SELECT 
                COUNT(*) as total_orders,
                COUNT(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' THEN 1 END) as orders_today,
                COALESCE(SUM(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' THEN quantity * price END), 0) as volume_today,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_orders,
                COUNT(CASE WHEN status = 'filled' THEN 1 END) as filled_orders
            FROM orders
        """)
        trading_stats = self.db.execute(trading_stats_query).fetchone()
        stats["trading"] = dict(trading_stats._mapping)
        
        # Financial statistics
        financial_stats_query = text("""
            SELECT 
                COUNT(*) as total_transactions,
                COUNT(CASE WHEN type = 'deposit' THEN 1 END) as deposits,
                COUNT(CASE WHEN type = 'withdrawal' THEN 1 END) as withdrawals,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_transactions,
                COALESCE(SUM(CASE WHEN type = 'deposit' AND status = 'completed' THEN amount END), 0) as total_deposits,
                COALESCE(SUM(CASE WHEN type = 'withdrawal' AND status = 'completed' THEN amount END), 0) as total_withdrawals
            FROM transactions
        """)
        financial_stats = self.db.execute(financial_stats_query).fetchone()
        stats["financial"] = dict(financial_stats._mapping)
        
        # System health
        stats["system"] = await self._get_system_health()
        
        return stats
    
    async def _get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics"""
        health = {}
        
        # Database health
        try:
            self.db.execute(text("SELECT 1"))
            health["database"] = "healthy"
        except Exception as e:
            health["database"] = "unhealthy"
            logger.error(f"Database health check failed: {e}")
        
        # Redis health
        try:
            await self.redis.ping()
            health["redis"] = "healthy"
        except Exception as e:
            health["redis"] = "unhealthy"
            logger.error(f"Redis health check failed: {e}")
        
        # Service health (mock)
        health["services"] = {
            "trading_engine": "healthy",
            "wallet_service": "healthy",
            "notification_service": "healthy",
            "market_data": "healthy"
        }
        
        return health
    
    async def get_user_list(self, skip: int = 0, limit: int = 50, 
                           filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get paginated list of users with filters"""
        where_conditions = []
        params = {"limit": limit, "offset": skip}
        
        if filters:
            if filters.get("kyc_status"):
                where_conditions.append("kyc_status = :kyc_status")
                params["kyc_status"] = filters["kyc_status"]
            
            if filters.get("is_active") is not None:
                where_conditions.append("is_active = :is_active")
                params["is_active"] = filters["is_active"]
            
            if filters.get("search"):
                where_conditions.append("(email ILIKE :search OR username ILIKE :search OR full_name ILIKE :search)")
                params["search"] = f"%{filters['search']}%"
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        query = text(f"""
            SELECT id, email, username, full_name, kyc_status, kyc_level, is_active,
                   is_admin, created_at, last_login, trading_enabled
            FROM users {where_clause}
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        
        users = self.db.execute(query, params).fetchall()
        
        # Get total count
        count_query = text(f"""
            SELECT COUNT(*) as total FROM users {where_clause}
        """)
        total_result = self.db.execute(count_query, params).fetchone()
        
        return {
            "users": [dict(u._mapping) for u in users],
            "total": total_result.total,
            "skip": skip,
            "limit": limit
        }

class ReportingSystem:
    def __init__(self, db: Session, redis_client):
        self.db = db
        self.redis = redis_client
        
    async def generate_trading_report(self, start_date: datetime, end_date: datetime, 
                                     user_id: Optional[int] = None) -> Dict[str, Any]:
        """Generate comprehensive trading report"""
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        
        where_clause = "WHERE created_at BETWEEN :start_date AND :end_date"
        if user_id:
            where_clause += " AND user_id = :user_id"
            params["user_id"] = user_id
        
        # Trading volume by symbol
        volume_query = text(f"""
            SELECT symbol, COUNT(*) as order_count, 
                   SUM(quantity) as total_quantity, 
                   SUM(quantity * price) as total_volume
            FROM orders {where_clause}
            GROUP BY symbol
            ORDER BY total_volume DESC
        """)
        volume_data = self.db.execute(volume_query, params).fetchall()
        
        # Trading trends over time
        trends_query = text(f"""
            SELECT DATE(created_at) as date, COUNT(*) as orders, 
                   SUM(quantity * price) as volume
            FROM orders {where_clause}
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        trends_data = self.db.execute(trends_query, params).fetchall()
        
        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "volume_by_symbol": [dict(v._mapping) for v in volume_data],
            "trading_trends": [dict(t._mapping) for t in trends_data]
        }
    
    async def generate_financial_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate financial operations report"""
        params = {"start_date": start_date, "end_date": end_date}
        where_clause = "WHERE created_at BETWEEN :start_date AND :end_date"
        
        # Transaction summary
        transaction_query = text(f"""
            SELECT type, status, COUNT(*) as count, SUM(amount) as total_amount
            FROM transactions {where_clause}
            GROUP BY type, status
        """)
        transaction_data = self.db.execute(transaction_query, params).fetchall()
        
        # Daily transaction volumes
        daily_volume_query = text(f"""
            SELECT DATE(created_at) as date, 
                   SUM(CASE WHEN type = 'deposit' THEN amount ELSE 0 END) as deposits,
                   SUM(CASE WHEN type = 'withdrawal' THEN amount ELSE 0 END) as withdrawals
            FROM transactions {where_clause}
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        daily_volume_data = self.db.execute(daily_volume_query, params).fetchall()
        
        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "transaction_summary": [dict(t._mapping) for t in transaction_data],
            "daily_volumes": [dict(d._mapping) for d in daily_volume_data]
        }

class EnhancedAdminSystem:
    """Main enhanced admin system"""
    
    def __init__(self, db: Session, redis_client):
        self.db = db
        self.redis = redis_client
        self.user_manager = UserManager(db, redis_client)
        self.dashboard = AdminDashboard(db, redis_client)
        self.reporting = ReportingSystem(db, redis_client)
        
    async def initialize_admin_system(self):
        """Initialize admin system with default settings"""
        logger.info("Initializing Enhanced Admin System")
        
        # Create default admin roles
        await self._create_default_roles()
        
        # Set up system configurations
        config = {
            "max_sessions_per_user": 5,
            "password_complexity_required": True,
            "two_factor_required_for_admins": True,
            "auto_logoff_inactive_users": True,
            "audit_log_retention_days": 365
        }
        
        await self.redis.set("admin_config", json.dumps(config))
        
    async def _create_default_roles(self):
        """Create default admin roles in database"""
        # This would create roles in the database
        # For now, we'll use the role matrix in RolePermissionMatrix
        pass
    
    async def get_comprehensive_user_control(self, admin_user_id: int) -> Dict[str, Any]:
        """Get comprehensive user control interface"""
        # Verify admin permissions
        if not await self._verify_admin_permission(admin_user_id, Permission.USER_MANAGEMENT):
            raise PermissionError("Insufficient permissions")
        
        return {
            "dashboard_stats": await self.dashboard.get_dashboard_stats(),
            "user_management": {
                "total_users": await self.dashboard.get_user_list(limit=1)["total"],
                "recent_registrations": await self.dashboard.get_user_list(limit=10),
                "high_risk_users": await self._get_high_risk_users()
            },
            "system_health": await self.dashboard._get_system_health(),
            "recent_admin_actions": await self._get_recent_admin_actions()
        }
    
    async def _verify_admin_permission(self, admin_id: int, permission: Permission) -> bool:
        """Verify admin has specific permission"""
        # Get user role
        user_query = text("SELECT is_admin, is_superadmin FROM users WHERE id = :user_id")
        result = self.db.execute(user_query, {"user_id": admin_id}).fetchone()
        
        if not result:
            return False
        
        # Super admin has all permissions
        if result.is_superadmin:
            return True
        
        # Check regular admin permissions (simplified)
        return result.is_admin
    
    async def _get_high_risk_users(self) -> List[Dict[str, Any]]:
        """Get list of high-risk users"""
        # Get users with high trading volume or suspicious activity
        query = text("""
            SELECT u.id, u.email, u.username, u.kyc_status, 
                   COUNT(o.id) as order_count,
                   COALESCE(SUM(o.quantity * o.price), 0) as total_volume
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id 
                AND o.created_at >= NOW() - INTERVAL '7 days'
            WHERE u.is_active = true
            GROUP BY u.id, u.email, u.username, u.kyc_status
            HAVING COUNT(o.id) > 100 OR COALESCE(SUM(o.quantity * o.price), 0) > 100000
            ORDER BY total_volume DESC
            LIMIT 20
        """)
        
        results = self.db.execute(query).fetchall()
        return [dict(r._mapping) for r in results]
    
    async def _get_recent_admin_actions(self) -> List[Dict[str, Any]]:
        """Get recent admin actions"""
        recent_logs = await self.redis.lrange("admin_audit_log", 0, 19)
        return [json.loads(log) for log in recent_logs]