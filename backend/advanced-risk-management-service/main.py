from fastapi import FastAPI
from admin.admin_routes import router as admin_router
from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

# Complete RBAC System for advanced-risk-management-service
class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    SUPPORT = "support"
    COMPLIANCE = "compliance"
    RISK_MANAGER = "risk_manager"
    TRADER = "trader"
    USER = "user"

class Permission(str, Enum):
    # User Management
    USER_VIEW = "user:view"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_SUSPEND = "user:suspend"
    USER_VERIFY = "user:verify"
    
    # Financial Controls
    WITHDRAWAL_APPROVE = "withdrawal:approve"
    WITHDRAWAL_REJECT = "withdrawal:reject"
    DEPOSIT_MONITOR = "deposit:monitor"
    TRANSACTION_REVIEW = "transaction:review"
    FEE_MANAGE = "fee:manage"
    
    # Trading Controls
    TRADING_HALT = "trading:halt"
    TRADING_RESUME = "trading:resume"
    PAIR_MANAGE = "pair:manage"
    LIQUIDITY_MANAGE = "liquidity:manage"
    
    # Risk Management
    RISK_CONFIGURE = "risk:configure"
    POSITION_MONITOR = "position:monitor"
    LIQUIDATION_MANAGE = "liquidation:manage"
    
    # System Controls
    SYSTEM_CONFIG = "system:config"
    FEATURE_FLAG = "feature:flag"
    MAINTENANCE_MODE = "maintenance:mode"
    
    # Compliance
    KYC_APPROVE = "kyc:approve"
    KYC_REJECT = "kyc:reject"
    AML_MONITOR = "aml:monitor"
    COMPLIANCE_REPORT = "compliance:report"
    
    # Content Management
    ANNOUNCEMENT_CREATE = "announcement:create"
    ANNOUNCEMENT_UPDATE = "announcement:update"
    ANNOUNCEMENT_DELETE = "announcement:delete"
    
    # Analytics
    ANALYTICS_VIEW = "analytics:view"
    REPORT_GENERATE = "report:generate"
    AUDIT_LOG_VIEW = "audit:view"

class AdminUser(BaseModel):
    user_id: str
    username: str
    email: str
    role: UserRole
    permissions: List[Permission]
    is_active: bool = True
    created_at: datetime = None
    last_login: Optional[datetime] = None

# Role-based permission mapping
ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: [
        Permission.USER_VIEW, Permission.USER_CREATE, Permission.USER_UPDATE,
        Permission.USER_DELETE, Permission.USER_SUSPEND, Permission.USER_VERIFY,
        Permission.WITHDRAWAL_APPROVE, Permission.WITHDRAWAL_REJECT,
        Permission.DEPOSIT_MONITOR, Permission.TRANSACTION_REVIEW, Permission.FEE_MANAGE,
        Permission.TRADING_HALT, Permission.TRADING_RESUME, Permission.PAIR_MANAGE,
        Permission.LIQUIDITY_MANAGE, Permission.RISK_CONFIGURE, Permission.POSITION_MONITOR,
        Permission.LIQUIDATION_MANAGE, Permission.SYSTEM_CONFIG, Permission.FEATURE_FLAG,
        Permission.MAINTENANCE_MODE, Permission.KYC_APPROVE, Permission.KYC_REJECT,
        Permission.AML_MONITOR, Permission.COMPLIANCE_REPORT,
        Permission.ANNOUNCEMENT_CREATE, Permission.ANNOUNCEMENT_UPDATE, Permission.ANNOUNCEMENT_DELETE,
        Permission.ANALYTICS_VIEW, Permission.REPORT_GENERATE, Permission.AUDIT_LOG_VIEW
    ],
    UserRole.ADMIN: [
        Permission.USER_VIEW, Permission.USER_CREATE, Permission.USER_UPDATE,
        Permission.USER_SUSPEND, Permission.USER_VERIFY,
        Permission.WITHDRAWAL_APPROVE, Permission.WITHDRAWAL_REJECT,
        Permission.DEPOSIT_MONITOR, Permission.TRANSACTION_REVIEW, Permission.FEE_MANAGE,
        Permission.TRADING_HALT, Permission.TRADING_RESUME, Permission.PAIR_MANAGE,
        Permission.RISK_CONFIGURE, Permission.POSITION_MONITOR,
        Permission.SYSTEM_CONFIG, Permission.KYC_APPROVE, Permission.KYC_REJECT,
        Permission.ANNOUNCEMENT_CREATE, Permission.ANNOUNCEMENT_UPDATE,
        Permission.ANALYTICS_VIEW, Permission.REPORT_GENERATE, Permission.AUDIT_LOG_VIEW
    ],
    UserRole.MODERATOR: [
        Permission.USER_VIEW, Permission.USER_SUSPEND,
        Permission.TRANSACTION_REVIEW, Permission.KYC_APPROVE,
        Permission.ANNOUNCEMENT_CREATE, Permission.ANALYTICS_VIEW
    ],
    UserRole.SUPPORT: [
        Permission.USER_VIEW, Permission.TRANSACTION_REVIEW,
        Permission.ANALYTICS_VIEW
    ],
    UserRole.COMPLIANCE: [
        Permission.USER_VIEW, Permission.USER_VERIFY,
        Permission.WITHDRAWAL_APPROVE, Permission.WITHDRAWAL_REJECT,
        Permission.TRANSACTION_REVIEW, Permission.KYC_APPROVE, Permission.KYC_REJECT,
        Permission.AML_MONITOR, Permission.COMPLIANCE_REPORT,
        Permission.AUDIT_LOG_VIEW
    ],
    UserRole.RISK_MANAGER: [
        Permission.POSITION_MONITOR, Permission.RISK_CONFIGURE,
        Permission.LIQUIDATION_MANAGE, Permission.TRADING_HALT,
        Permission.ANALYTICS_VIEW, Permission.REPORT_GENERATE
    ],
    UserRole.TRADER: [],
    UserRole.USER: []
}

# RBAC Helper Functions
def get_current_admin():
    """Get current admin user (mock implementation)"""
    return AdminUser(
        user_id="admin_001",
        username="admin",
        email="admin@tigerex.com",
        role=UserRole.ADMIN,
        permissions=ROLE_PERMISSIONS[UserRole.ADMIN]
    )

def require_permission(permission: Permission):
    """Decorator to require specific permission"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            from fastapi import HTTPException, status
            admin = get_current_admin()
            if permission not in admin.permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Permission denied. Required: " + str(permission)
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(roles: List[UserRole]):
    """Decorator to require specific role(s)"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            from fastapi import HTTPException, status
            admin = get_current_admin()
            if admin.role not in roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Role denied. Required: " + str(roles)
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


from fastapi import HTTPException
from datetime import datetime
import numpy as np
from collections import defaultdict
from typing import Dict, List, Any

app = FastAPI(title="TigerEx Advanced Risk Management Service")

# RBAC Helper Functions
def get_current_admin():
    """Get current admin user (mock implementation)"""
    return AdminUser(
        user_id="admin_001",
        username="admin",
        email="admin@tigerex.com",
        role=UserRole.ADMIN,
        permissions=ROLE_PERMISSIONS[UserRole.ADMIN]
    )


# Include admin router
app.include_router(admin_router)

# Risk Management State
risk_state = {
    'alerts': [],
    'risk_scores': defaultdict(dict),
    'fraud_detections': [],
    'portfolio_risks': defaultdict(dict),
    'stress_test_results': defaultdict(dict)
}

class RiskManagementEngine:
    def __init__(self):
        self.risk_thresholds = {
            'low': 30,
            'medium': 60,
            'high': 80,
            'critical': 95
        }
    
    def calculate_real_time_risk_score(self, user_id: str, activity_data: Dict) -> float:
        """Calculate real-time risk score based on user activity"""
        risk_factors = {
            'login_anomaly': self.detect_login_anomaly(activity_data),
            'transaction_velocity': self.analyze_transaction_velocity(activity_data),
            'amount_anomaly': self.detect_amount_anomaly(activity_data),
            'behavioral_anomaly': self.detect_behavioral_anomaly(activity_data),
            'geographic_anomaly': self.detect_geographic_anomaly(activity_data)
        }
        
        # Calculate weighted risk score
        weights = {
            'login_anomaly': 0.25,
            'transaction_velocity': 0.20,
            'amount_anomaly': 0.20,
            'behavioral_anomaly': 0.20,
            'geographic_anomaly': 0.15
        }
        
        total_risk = sum(risk_factors[factor] * weights[factor] for factor in risk_factors)
        return min(total_risk, 100)
    
    def detect_login_anomaly(self, activity_data: Dict) -> float:
        """Detect login anomalies"""
        risk_score = 0
        
        # Check for unusual login times
        login_hour = activity_data.get('login_hour', 12)
        if login_hour < 6 or login_hour > 23:
            risk_score += 30
        
        # Check for rapid login attempts
        login_attempts = activity_data.get('login_attempts', 1)
        if login_attempts > 3:
            risk_score += 25 * (login_attempts - 3)
        
        return min(risk_score, 100)
    
    def analyze_transaction_velocity(self, activity_data: Dict) -> float:
        """Analyze transaction velocity patterns"""
        risk_score = 0
        
        # Check for rapid transactions
        transactions_per_minute = activity_data.get('transactions_per_minute', 0)
        if transactions_per_minute > 10:
            risk_score += 40
        
        # Check for unusual transaction frequency
        hourly_transactions = activity_data.get('hourly_transactions', 0)
        if hourly_transactions > 50:
            risk_score += 35
        
        return min(risk_score, 100)
    
    def detect_amount_anomaly(self, activity_data: Dict) -> float:
        """Detect unusual transaction amounts"""
        risk_score = 0
        
        # Check for amounts significantly above average
        amount = activity_data.get('transaction_amount', 0)
        avg_amount = activity_data.get('average_transaction_amount', 1000)
        
        if amount > avg_amount * 5:
            risk_score += 50
        
        # Check for round number transactions (potential money laundering)
        if amount > 0 and amount % 100 == 0:
            risk_score += 15
        
        return min(risk_score, 100)
    
    def detect_behavioral_anomaly(self, activity_data: Dict) -> float:
        """Detect behavioral anomalies"""
        risk_score = 0
        
        # Check for unusual trading patterns
        trading_frequency = activity_data.get('trading_frequency', 'normal')
        if trading_frequency == 'abnormal':
            risk_score += 40
        
        # Check for device fingerprinting anomalies
        device_trust_score = activity_data.get('device_trust_score', 100)
        risk_score += (100 - device_trust_score) * 0.5
        
        return min(risk_score, 100)
    
    def detect_geographic_anomaly(self, activity_data: Dict) -> float:
        """Detect geographic anomalies"""
        risk_score = 0
        
        # Check for impossible travel (login from different countries within short time)
        countries_visited = activity_data.get('countries_visited_last_hour', [])
        if len(countries_visited) > 2:
            risk_score += 60
        
        # Check for high-risk countries
        high_risk_countries = ['AF', 'IR', 'KP', 'SY']
        current_country = activity_data.get('current_country', '')
        if current_country in high_risk_countries:
            risk_score += 30
        
        return min(risk_score, 100)

# API Endpoints
@app.post("/api/v1/risk/assess")
async def assess_risk(user_id: str, activity_data: Dict):
    """Assess real-time risk for user activity"""
    engine = RiskManagementEngine()
    risk_score = engine.calculate_real_time_risk_score(user_id, activity_data)
    
    # Determine risk level
    if risk_score >= engine.risk_thresholds['critical']:
        risk_level = "CRITICAL"
        action = "BLOCK_USER"
    elif risk_score >= engine.risk_thresholds['high']:
        risk_level = "HIGH"
        action = "REQUIRE_VERIFICATION"
    elif risk_score >= engine.risk_thresholds['medium']:
        risk_level = "MEDIUM"
        action = "MONITOR_CLOSELY"
    else:
        risk_level = "LOW"
        action = "ALLOW"
    
    # Store risk assessment
    risk_state['risk_scores'][user_id] = {
        'score': risk_score,
        'level': risk_level,
        'action': action,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    return {
        "success": True,
        "user_id": user_id,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "recommended_action": action,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/risk/portfolio-analysis")
async def portfolio_risk_analysis(user_id: str, portfolio_data: Dict):
    """Analyze portfolio risk"""
    # Calculate portfolio metrics
    total_value = portfolio_data.get('total_value', 0)
    positions = portfolio_data.get('positions', [])
    
    # Calculate concentration risk
    concentration_risk = 0
    if len(positions) > 0:
        max_position_pct = max(pos['value_percentage'] for pos in positions)
        if max_position_pct > 50:
            concentration_risk = (max_position_pct - 50) * 2
    
    # Calculate volatility risk
    volatility_risk = portfolio_data.get('portfolio_volatility', 0) * 100
    
    # Calculate liquidity risk
    liquidity_risk = 0
    for position in positions:
        if position.get('liquidity_score', 10) < 5:
            liquidity_risk += 20
    
    # Overall portfolio risk
    portfolio_risk = (concentration_risk + volatility_risk + liquidity_risk) / 3
    
    risk_state['portfolio_risks'][user_id] = {
        'concentration_risk': concentration_risk,
        'volatility_risk': volatility_risk,
        'liquidity_risk': liquidity_risk,
        'overall_risk': portfolio_risk,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    return {
        "success": True,
        "user_id": user_id,
        "portfolio_risk_score": portfolio_risk,
        "risk_breakdown": {
            "concentration_risk": concentration_risk,
            "volatility_risk": volatility_risk,
            "liquidity_risk": liquidity_risk
        },
        "recommendations": self.get_portfolio_recommendations(portfolio_risk)
    }

@app.post("/api/v1/risk/stress-test")
async def stress_test_portfolio(user_id: str, scenarios: List[Dict]):
    """Perform stress testing on portfolio"""
    stress_results = {}
    
    for scenario in scenarios:
        scenario_name = scenario.get('name', 'Unknown')
        market_drop = scenario.get('market_drop', 0)
        volatility_spike = scenario.get('volatility_spike', 0)
        
        # Calculate portfolio impact
        portfolio_impact = market_drop * 0.8 + volatility_spike * 0.2
        max_drawdown = portfolio_impact * 1.2  # Conservative estimate
        
        stress_results[scenario_name] = {
            'portfolio_impact': portfolio_impact,
            'max_drawdown': max_drawdown,
            'risk_rating': 'HIGH' if max_drawdown > 20 else 'MEDIUM' if max_drawdown > 10 else 'LOW'
        }
    
    risk_state['stress_test_results'][user_id] = stress_results
    
    return {
        "success": True,
        "user_id": user_id,
        "stress_test_results": stress_results,
        "overall_rating": max(result['risk_rating'] for result in stress_results.values())
    }

@app.get("/api/v1/risk/alerts/{user_id}")
async def get_risk_alerts(user_id: str):
    """Get risk alerts for user"""
    user_alerts = [alert for alert in risk_state['alerts'] if alert.get('user_id') == user_id]
    
    return {
        "success": True,
        "user_id": user_id,
        "alerts": user_alerts,
        "unread_count": len([a for a in user_alerts if not a.get('read', False)])
    }

def get_portfolio_recommendations(self, risk_score: float) -> List[str]:
    """Get portfolio recommendations based on risk score"""
    recommendations = []
    
    if risk_score > 70:
        recommendations.append("Consider reducing position sizes")
        recommendations.append("Diversify across more assets")
        recommendations.append("Add hedging positions")
    elif risk_score > 40:
        recommendations.append("Monitor high-risk positions closely")
        recommendations.append("Consider rebalancing portfolio")
    else:
        recommendations.append("Portfolio risk is well-managed")
        recommendations.append("Continue current strategy")
    
    return recommendations

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8294)
