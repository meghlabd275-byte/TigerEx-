import os
"""
TigerEx Risk Management Service
Real-time risk monitoring, fraud detection, and compliance
"""

from fastapi import FastAPI
from admin.admin_routes import router as admin_router
, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from decimal import Decimal
import asyncpg
import structlog
from enum import Enum

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

app = FastAPI(title="TigerEx Risk Management Service", version="1.0.0")

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
class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(str, Enum):
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    LARGE_TRANSACTION = "large_transaction"
    RAPID_TRADING = "rapid_trading"
    UNUSUAL_PATTERN = "unusual_pattern"
    ACCOUNT_TAKEOVER = "account_takeover"
    WASH_TRADING = "wash_trading"
    MARKET_MANIPULATION = "market_manipulation"
    WITHDRAWAL_ANOMALY = "withdrawal_anomaly"

class AlertStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"

# Models
class RiskAssessment(BaseModel):
    user_id: int
    risk_score: int = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    factors: List[str]
    timestamp: datetime

class TransactionRiskCheck(BaseModel):
    transaction_id: Optional[int] = None
    user_id: int
    transaction_type: str
    amount: Decimal
    currency: str
    destination: Optional[str] = None
    ip_address: Optional[str] = None

class RiskAlert(BaseModel):
    alert_id: int
    user_id: int
    alert_type: str
    risk_level: str
    description: str
    status: str
    created_at: datetime
    resolved_at: Optional[datetime]

class UserRiskProfile(BaseModel):
    user_id: int
    risk_score: int
    risk_level: str
    kyc_level: str
    account_age_days: int
    total_deposits: Decimal
    total_withdrawals: Decimal
    total_trading_volume: Decimal
    suspicious_activities_count: int
    last_assessment: datetime

class RiskRule(BaseModel):
    rule_id: int
    rule_name: str
    rule_type: str
    threshold: Decimal
    action: str
    is_active: bool

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
        database="tigerex_risk",
        min_size=10,
        max_size=50
    )
    
    async with db_pool.acquire() as conn:
        # Create risk profiles table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_risk_profiles (
                profile_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL UNIQUE,
                risk_score INTEGER DEFAULT 0,
                risk_level VARCHAR(20) DEFAULT 'low',
                kyc_level VARCHAR(20),
                account_age_days INTEGER,
                total_deposits DECIMAL(36, 18) DEFAULT 0,
                total_withdrawals DECIMAL(36, 18) DEFAULT 0,
                total_trading_volume DECIMAL(36, 18) DEFAULT 0,
                suspicious_activities_count INTEGER DEFAULT 0,
                last_assessment TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user (user_id),
                INDEX idx_risk_level (risk_level)
            )
        """)
        
        # Create risk alerts table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS risk_alerts (
                alert_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                alert_type VARCHAR(50) NOT NULL,
                risk_level VARCHAR(20) NOT NULL,
                description TEXT,
                metadata JSONB,
                status VARCHAR(20) DEFAULT 'open',
                assigned_to INTEGER,
                resolved_by INTEGER,
                resolution_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                INDEX idx_user_alerts (user_id, created_at DESC),
                INDEX idx_status (status),
                INDEX idx_risk_level (risk_level)
            )
        """)
        
        # Create transaction risk scores table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS transaction_risk_scores (
                score_id SERIAL PRIMARY KEY,
                transaction_id INTEGER,
                user_id INTEGER NOT NULL,
                transaction_type VARCHAR(50) NOT NULL,
                amount DECIMAL(36, 18) NOT NULL,
                currency VARCHAR(20) NOT NULL,
                risk_score INTEGER NOT NULL,
                risk_factors JSONB,
                flagged BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_transaction (transaction_id),
                INDEX idx_user_transactions (user_id, created_at DESC),
                INDEX idx_flagged (flagged, created_at DESC)
            )
        """)
        
        # Create risk rules table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS risk_rules (
                rule_id SERIAL PRIMARY KEY,
                rule_name VARCHAR(255) NOT NULL,
                rule_type VARCHAR(50) NOT NULL,
                threshold DECIMAL(36, 18),
                time_window_minutes INTEGER,
                action VARCHAR(50) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_rule_type (rule_type),
                INDEX idx_active (is_active)
            )
        """)
        
        # Create blocked entities table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS blocked_entities (
                block_id SERIAL PRIMARY KEY,
                entity_type VARCHAR(50) NOT NULL,
                entity_value VARCHAR(255) NOT NULL,
                reason TEXT,
                blocked_by INTEGER,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(entity_type, entity_value),
                INDEX idx_entity (entity_type, entity_value)
            )
        """)
        
        # Insert default risk rules
        await conn.execute("""
            INSERT INTO risk_rules (rule_name, rule_type, threshold, time_window_minutes, action)
            VALUES 
                ('Large Withdrawal Alert', 'withdrawal', 50000, NULL, 'alert'),
                ('Rapid Trading Detection', 'trading', 100, 60, 'alert'),
                ('Multiple Failed Logins', 'security', 5, 30, 'lock_account'),
                ('Unusual Withdrawal Pattern', 'withdrawal', 10000, 1440, 'review'),
                ('High Volume Trading', 'trading', 1000000, 1440, 'alert')
            ON CONFLICT DO NOTHING
        """)
        
        logger.info("Database initialized successfully")

# Risk calculation functions
def calculate_risk_score(
    user_data: Dict,
    transaction_data: Optional[Dict] = None
) -> tuple[int, List[str]]:
    """Calculate risk score based on various factors"""
    score = 0
    factors = []
    
    # KYC level factor
    kyc_level = user_data.get('kyc_level', 'level_0')
    if kyc_level == 'level_0':
        score += 30
        factors.append("No KYC verification")
    elif kyc_level == 'level_1':
        score += 15
        factors.append("Basic KYC only")
    
    # Account age factor
    account_age_days = user_data.get('account_age_days', 0)
    if account_age_days < 7:
        score += 20
        factors.append("New account (< 7 days)")
    elif account_age_days < 30:
        score += 10
        factors.append("Recent account (< 30 days)")
    
    # Transaction history factor
    if transaction_data:
        amount = transaction_data.get('amount', 0)
        
        # Large transaction
        if amount > 50000:
            score += 25
            factors.append(f"Large transaction amount: ${amount}")
        elif amount > 10000:
            score += 15
            factors.append(f"Significant transaction amount: ${amount}")
        
        # Withdrawal to new address
        if transaction_data.get('is_new_address'):
            score += 15
            factors.append("Withdrawal to new address")
    
    # Suspicious activity history
    suspicious_count = user_data.get('suspicious_activities_count', 0)
    if suspicious_count > 0:
        score += min(suspicious_count * 10, 30)
        factors.append(f"Previous suspicious activities: {suspicious_count}")
    
    return min(score, 100), factors

def get_risk_level(score: int) -> RiskLevel:
    """Determine risk level from score"""
    if score >= 75:
        return RiskLevel.CRITICAL
    elif score >= 50:
        return RiskLevel.HIGH
    elif score >= 25:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.LOW

# API Endpoints
@app.post("/api/v1/risk/assess/user", response_model=RiskAssessment)
async def assess_user_risk(
    user_id: int,
    db: asyncpg.Pool = Depends(get_db)
):
    """Assess risk for a specific user"""
    try:
        # Get user profile
        profile = await db.fetchrow("""
            SELECT * FROM user_risk_profiles WHERE user_id = $1
        """, user_id)
        
        if not profile:
            # Create new profile
            profile_data = {
                'kyc_level': 'level_0',
                'account_age_days': 0,
                'suspicious_activities_count': 0
            }
        else:
            profile_data = dict(profile)
        
        # Calculate risk score
        score, factors = calculate_risk_score(profile_data)
        risk_level = get_risk_level(score)
        
        # Update profile
        await db.execute("""
            INSERT INTO user_risk_profiles (
                user_id, risk_score, risk_level, last_assessment
            ) VALUES ($1, $2, $3, CURRENT_TIMESTAMP)
            ON CONFLICT (user_id)
            DO UPDATE SET
                risk_score = $2,
                risk_level = $3,
                last_assessment = CURRENT_TIMESTAMP
        """, user_id, score, risk_level.value)
        
        logger.info("user_risk_assessed", user_id=user_id, score=score, level=risk_level.value)
        
        return RiskAssessment(
            user_id=user_id,
            risk_score=score,
            risk_level=risk_level,
            factors=factors,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error("assess_user_risk_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/risk/check/transaction")
async def check_transaction_risk(
    request: TransactionRiskCheck,
    db: asyncpg.Pool = Depends(get_db)
):
    """Check risk for a transaction"""
    try:
        # Get user profile
        profile = await db.fetchrow("""
            SELECT * FROM user_risk_profiles WHERE user_id = $1
        """, request.user_id)
        
        profile_data = dict(profile) if profile else {
            'kyc_level': 'level_0',
            'account_age_days': 0,
            'suspicious_activities_count': 0
        }
        
        # Transaction data
        transaction_data = {
            'amount': float(request.amount),
            'is_new_address': True  # Would check against known addresses
        }
        
        # Calculate risk score
        score, factors = calculate_risk_score(profile_data, transaction_data)
        risk_level = get_risk_level(score)
        
        # Store transaction risk score
        await db.execute("""
            INSERT INTO transaction_risk_scores (
                transaction_id, user_id, transaction_type, amount,
                currency, risk_score, risk_factors, flagged
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """, request.transaction_id, request.user_id, request.transaction_type,
            request.amount, request.currency, score, factors, score >= 50)
        
        # Create alert if high risk
        if score >= 50:
            await db.execute("""
                INSERT INTO risk_alerts (
                    user_id, alert_type, risk_level, description, metadata
                ) VALUES ($1, $2, $3, $4, $5)
            """, request.user_id, AlertType.LARGE_TRANSACTION.value,
                risk_level.value, f"High risk {request.transaction_type} detected",
                {'transaction_id': request.transaction_id, 'amount': str(request.amount)})
            
            logger.warning("high_risk_transaction_detected",
                          user_id=request.user_id,
                          score=score,
                          amount=str(request.amount))
        
        return {
            "approved": score < 75,
            "risk_score": score,
            "risk_level": risk_level.value,
            "factors": factors,
            "requires_review": score >= 50
        }
        
    except Exception as e:
        logger.error("check_transaction_risk_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/risk/alerts", response_model=List[RiskAlert])
async def get_risk_alerts(
    status: Optional[AlertStatus] = None,
    risk_level: Optional[RiskLevel] = None,
    limit: int = 50,
    offset: int = 0,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get risk alerts"""
    try:
        query = "SELECT * FROM risk_alerts WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = $1"
            params.append(status.value)
        
        if risk_level:
            query += f" AND risk_level = ${len(params) + 1}"
            params.append(risk_level.value)
        
        query += f" ORDER BY created_at DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
        params.extend([limit, offset])
        
        alerts = await db.fetch(query, *params)
        
        return [
            RiskAlert(
                alert_id=a['alert_id'],
                user_id=a['user_id'],
                alert_type=a['alert_type'],
                risk_level=a['risk_level'],
                description=a['description'],
                status=a['status'],
                created_at=a['created_at'],
                resolved_at=a['resolved_at']
            )
            for a in alerts
        ]
        
    except Exception as e:
        logger.error("get_risk_alerts_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/risk/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    admin_id: int,
    resolution_notes: str,
    is_false_positive: bool = False,
    db: asyncpg.Pool = Depends(get_db)
):
    """Resolve a risk alert"""
    try:
        status = AlertStatus.FALSE_POSITIVE if is_false_positive else AlertStatus.RESOLVED
        
        result = await db.execute("""
            UPDATE risk_alerts
            SET status = $2,
                resolved_by = $3,
                resolution_notes = $4,
                resolved_at = CURRENT_TIMESTAMP
            WHERE alert_id = $1
        """, alert_id, status.value, admin_id, resolution_notes)
        
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Alert not found")
        
        logger.info("alert_resolved", alert_id=alert_id, admin_id=admin_id)
        return {"message": "Alert resolved successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("resolve_alert_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/risk/profile/{user_id}", response_model=UserRiskProfile)
async def get_user_risk_profile(
    user_id: int,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get user risk profile"""
    try:
        profile = await db.fetchrow("""
            SELECT * FROM user_risk_profiles WHERE user_id = $1
        """, user_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Risk profile not found")
        
        return UserRiskProfile(
            user_id=profile['user_id'],
            risk_score=profile['risk_score'],
            risk_level=profile['risk_level'],
            kyc_level=profile['kyc_level'] or 'level_0',
            account_age_days=profile['account_age_days'] or 0,
            total_deposits=profile['total_deposits'],
            total_withdrawals=profile['total_withdrawals'],
            total_trading_volume=profile['total_trading_volume'],
            suspicious_activities_count=profile['suspicious_activities_count'],
            last_assessment=profile['last_assessment']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_risk_profile_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/risk/block")
async def block_entity(
    entity_type: str,
    entity_value: str,
    reason: str,
    admin_id: int,
    expires_at: Optional[datetime] = None,
    db: asyncpg.Pool = Depends(get_db)
):
    """Block an entity (IP, address, user, etc.)"""
    try:
        await db.execute("""
            INSERT INTO blocked_entities (
                entity_type, entity_value, reason, blocked_by, expires_at
            ) VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (entity_type, entity_value)
            DO UPDATE SET
                reason = $3,
                blocked_by = $4,
                expires_at = $5
        """, entity_type, entity_value, reason, admin_id, expires_at)
        
        logger.info("entity_blocked",
                   entity_type=entity_type,
                   entity_value=entity_value,
                   admin_id=admin_id)
        
        return {"message": "Entity blocked successfully"}
        
    except Exception as e:
        logger.error("block_entity_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/risk/rules", response_model=List[RiskRule])
async def get_risk_rules(
    is_active: Optional[bool] = None,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get risk rules"""
    try:
        if is_active is not None:
            rules = await db.fetch("""
                SELECT * FROM risk_rules WHERE is_active = $1
                ORDER BY rule_name
            """, is_active)
        else:
            rules = await db.fetch("""
                SELECT * FROM risk_rules ORDER BY rule_name
            """)
        
        return [
            RiskRule(
                rule_id=r['rule_id'],
                rule_name=r['rule_name'],
                rule_type=r['rule_type'],
                threshold=r['threshold'],
                action=r['action'],
                is_active=r['is_active']
            )
            for r in rules
        ]
        
    except Exception as e:
        logger.error("get_risk_rules_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/risk/stats")
async def get_risk_statistics(db: asyncpg.Pool = Depends(get_db)):
    """Get risk management statistics"""
    try:
        stats = await db.fetchrow("""
            SELECT
                COUNT(*) as total_alerts,
                COUNT(CASE WHEN status = 'open' THEN 1 END) as open_alerts,
                COUNT(CASE WHEN status = 'investigating' THEN 1 END) as investigating,
                COUNT(CASE WHEN risk_level = 'critical' THEN 1 END) as critical_alerts,
                COUNT(CASE WHEN risk_level = 'high' THEN 1 END) as high_alerts,
                COUNT(CASE WHEN created_at >= CURRENT_DATE THEN 1 END) as alerts_today
            FROM risk_alerts
        """)
        
        return dict(stats)
        
    except Exception as e:
        logger.error("get_risk_stats_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "risk-management-service",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.on_event("startup")
async def startup():
    """Initialize service on startup"""
    await init_db()
    logger.info("Risk Management Service started")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    if db_pool:
        await db_pool.close()
    logger.info("Risk Management Service stopped")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8270)