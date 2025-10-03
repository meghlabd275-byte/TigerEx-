"""
TigerEx Deposit/Withdrawal Admin Service
Complete admin control over deposits and withdrawals for all assets
Port: 8170
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query
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
from contextlib import asynccontextmanager

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

# Global connections
db_pool = None
redis_client = None

# Security
security = HTTPBearer()

# Enums
class ActionType(str, Enum):
    ENABLE_DEPOSIT = "enable_deposit"
    DISABLE_DEPOSIT = "disable_deposit"
    PAUSE_DEPOSIT = "pause_deposit"
    RESUME_DEPOSIT = "resume_deposit"
    ENABLE_WITHDRAWAL = "enable_withdrawal"
    DISABLE_WITHDRAWAL = "disable_withdrawal"
    PAUSE_WITHDRAWAL = "pause_withdrawal"
    RESUME_WITHDRAWAL = "resume_withdrawal"
    ENABLE_BOTH = "enable_both"
    DISABLE_BOTH = "disable_both"
    PAUSE_BOTH = "pause_both"
    RESUME_BOTH = "resume_both"
    UPDATE_LIMITS = "update_limits"
    UPDATE_FEES = "update_fees"
    ENABLE_MAINTENANCE = "enable_maintenance"
    DISABLE_MAINTENANCE = "disable_maintenance"

class NetworkStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    CONGESTED = "congested"
    MAINTENANCE = "maintenance"

class WithdrawalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

# Pydantic Models
class AssetStatusUpdate(BaseModel):
    deposit_enabled: Optional[bool] = None
    deposit_paused: Optional[bool] = None
    withdrawal_enabled: Optional[bool] = None
    withdrawal_paused: Optional[bool] = None
    maintenance_mode: Optional[bool] = None
    network_status: Optional[NetworkStatus] = None

class DepositControlUpdate(BaseModel):
    deposit_enabled: Optional[bool] = None
    deposit_paused: Optional[bool] = None
    deposit_min_amount: Optional[Decimal] = Field(None, ge=0)
    deposit_max_amount: Optional[Decimal] = Field(None, gt=0)
    deposit_daily_limit: Optional[Decimal] = Field(None, gt=0)
    deposit_fee_percentage: Optional[Decimal] = Field(None, ge=0, le=1)
    deposit_fee_fixed: Optional[Decimal] = Field(None, ge=0)
    deposit_confirmations_required: Optional[int] = Field(None, ge=1)

class WithdrawalControlUpdate(BaseModel):
    withdrawal_enabled: Optional[bool] = None
    withdrawal_paused: Optional[bool] = None
    withdrawal_min_amount: Optional[Decimal] = Field(None, ge=0)
    withdrawal_max_amount: Optional[Decimal] = Field(None, gt=0)
    withdrawal_daily_limit: Optional[Decimal] = Field(None, gt=0)
    withdrawal_fee_percentage: Optional[Decimal] = Field(None, ge=0, le=1)
    withdrawal_fee_fixed: Optional[Decimal] = Field(None, ge=0)
    withdrawal_manual_approval_required: Optional[bool] = None
    withdrawal_manual_approval_threshold: Optional[Decimal] = Field(None, ge=0)

class MaintenanceSchedule(BaseModel):
    maintenance_reason: str
    maintenance_start_time: datetime
    maintenance_end_time: datetime

class AdminAction(BaseModel):
    action_type: ActionType
    reason: str
    notes: Optional[str] = None

class WithdrawalApproval(BaseModel):
    approved: bool
    rejection_reason: Optional[str] = None

class BulkAssetAction(BaseModel):
    asset_symbols: List[str]
    action_type: ActionType
    reason: str

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global db_pool, redis_client
    
    logger.info("Starting Deposit/Withdrawal Admin Service...")
    
    # Initialize database pool
    db_pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=10,
        max_size=50,
        command_timeout=60
    )
    logger.info("Database pool created")
    
    # Initialize Redis
    redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
    logger.info("Redis client connected")
    
    # Start background tasks
    asyncio.create_task(monitor_network_health())
    asyncio.create_task(process_pending_deposits())
    asyncio.create_task(process_pending_withdrawals())
    asyncio.create_task(update_statistics())
    
    logger.info("Deposit/Withdrawal Admin Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Deposit/Withdrawal Admin Service...")
    
    if db_pool:
        await db_pool.close()
    if redis_client:
        await redis_client.close()
    
    logger.info("Deposit/Withdrawal Admin Service shut down")

# Initialize FastAPI app
app = FastAPI(
    title="TigerEx Deposit/Withdrawal Admin Service",
    description="Complete admin control over deposits and withdrawals",
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

# Helper functions
async def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify admin authentication token"""
    token = credentials.credentials
    # TODO: Implement proper JWT verification
    return {"admin_id": "admin_001", "permissions": ["*"]}

async def log_admin_action(
    asset_id: str,
    action_type: str,
    previous_state: dict,
    new_state: dict,
    reason: str,
    admin: dict,
    notes: Optional[str] = None
):
    """Log admin action to history"""
    async with db_pool.acquire() as conn:
        action_id = f"ACTION_{asset_id}_{int(datetime.now().timestamp())}"
        
        await conn.execute("""
            INSERT INTO deposit_withdrawal_action_history (
                action_id, asset_id, action_type, action_target,
                previous_state, new_state, reason, notes,
                admin_id, admin_username
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """, action_id, asset_id, action_type, 
        'both' if 'both' in action_type else ('deposit' if 'deposit' in action_type else 'withdrawal'),
        previous_state, new_state, reason, notes,
        admin['admin_id'], admin.get('username', 'admin'))

# Background Tasks
async def monitor_network_health():
    """Monitor network health and auto-pause if needed"""
    while True:
        try:
            await asyncio.sleep(60)  # Check every minute
            
            async with db_pool.acquire() as conn:
                assets = await conn.fetch("""
                    SELECT * FROM asset_deposit_withdrawal_status
                    WHERE network_status = 'online'
                    AND auto_pause_on_suspicious = true
                """)
                
                for asset in assets:
                    # Check for suspicious activity
                    # TODO: Implement actual network health checks
                    pass
                    
        except Exception as e:
            logger.error(f"Error in monitor_network_health: {str(e)}")

async def process_pending_deposits():
    """Process pending deposits"""
    while True:
        try:
            await asyncio.sleep(10)  # Check every 10 seconds
            
            async with db_pool.acquire() as conn:
                pending = await conn.fetch("""
                    SELECT * FROM pending_deposits
                    WHERE status = 'confirming'
                    AND confirmations >= required_confirmations
                    LIMIT 100
                """)
                
                for deposit in pending:
                    # Process deposit
                    await conn.execute("""
                        UPDATE pending_deposits
                        SET status = 'completed',
                            processed_at = NOW()
                        WHERE deposit_id = $1
                    """, deposit['deposit_id'])
                    
                    logger.info(f"Processed deposit: {deposit['deposit_id']}")
                    
        except Exception as e:
            logger.error(f"Error in process_pending_deposits: {str(e)}")

async def process_pending_withdrawals():
    """Process pending withdrawals"""
    while True:
        try:
            await asyncio.sleep(10)  # Check every 10 seconds
            
            async with db_pool.acquire() as conn:
                pending = await conn.fetch("""
                    SELECT * FROM pending_withdrawals
                    WHERE status = 'approved'
                    AND approved_at < NOW() - INTERVAL '5 minutes'
                    LIMIT 100
                """)
                
                for withdrawal in pending:
                    # Process withdrawal
                    await conn.execute("""
                        UPDATE pending_withdrawals
                        SET status = 'processing'
                        WHERE withdrawal_id = $1
                    """, withdrawal['withdrawal_id'])
                    
                    logger.info(f"Processing withdrawal: {withdrawal['withdrawal_id']}")
                    
        except Exception as e:
            logger.error(f"Error in process_pending_withdrawals: {str(e)}")

async def update_statistics():
    """Update deposit/withdrawal statistics"""
    while True:
        try:
            await asyncio.sleep(3600)  # Update every hour
            
            async with db_pool.acquire() as conn:
                # Update hourly statistics
                # TODO: Implement statistics calculation
                pass
                
        except Exception as e:
            logger.error(f"Error in update_statistics: {str(e)}")

# Health Check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "deposit-withdrawal-admin-service",
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# ASSET STATUS MANAGEMENT
# ============================================================================

@app.get("/api/admin/assets/status")
async def get_all_asset_status(
    blockchain: Optional[str] = None,
    deposit_enabled: Optional[bool] = None,
    withdrawal_enabled: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    admin: dict = Depends(verify_admin_token)
):
    """Get status of all assets"""
    try:
        async with db_pool.acquire() as conn:
            query = "SELECT * FROM asset_deposit_withdrawal_status WHERE 1=1"
            params = []
            param_count = 0
            
            if blockchain:
                param_count += 1
                query += f" AND blockchain = ${param_count}"
                params.append(blockchain)
            
            if deposit_enabled is not None:
                param_count += 1
                query += f" AND deposit_enabled = ${param_count}"
                params.append(deposit_enabled)
            
            if withdrawal_enabled is not None:
                param_count += 1
                query += f" AND withdrawal_enabled = ${param_count}"
                params.append(withdrawal_enabled)
            
            query += f" ORDER BY asset_symbol OFFSET ${param_count + 1} LIMIT ${param_count + 2}"
            params.extend([skip, limit])
            
            assets = await conn.fetch(query, *params)
            total = await conn.fetchval("SELECT COUNT(*) FROM asset_deposit_withdrawal_status")
            
            return {
                "total": total,
                "assets": [dict(a) for a in assets]
            }
            
    except Exception as e:
        logger.error(f"Error fetching asset status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/assets/{asset_symbol}/status")
async def get_asset_status(
    asset_symbol: str,
    admin: dict = Depends(verify_admin_token)
):
    """Get status of a specific asset"""
    try:
        async with db_pool.acquire() as conn:
            asset = await conn.fetchrow("""
                SELECT * FROM asset_deposit_withdrawal_status
                WHERE asset_symbol = $1
            """, asset_symbol)
            
            if not asset:
                raise HTTPException(status_code=404, detail="Asset not found")
            
            return dict(asset)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching asset status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DEPOSIT CONTROLS
# ============================================================================

@app.post("/api/admin/assets/{asset_symbol}/deposit/enable")
async def enable_deposit(
    asset_symbol: str,
    action: AdminAction,
    admin: dict = Depends(verify_admin_token)
):
    """Enable deposits for an asset"""
    try:
        async with db_pool.acquire() as conn:
            # Get current state
            current = await conn.fetchrow("""
                SELECT * FROM asset_deposit_withdrawal_status
                WHERE asset_symbol = $1
            """, asset_symbol)
            
            if not current:
                raise HTTPException(status_code=404, detail="Asset not found")
            
            # Update state
            updated = await conn.fetchrow("""
                UPDATE asset_deposit_withdrawal_status
                SET deposit_enabled = true,
                    deposit_paused = false,
                    updated_by = $1,
                    updated_at = NOW()
                WHERE asset_symbol = $2
                RETURNING *
            """, admin['admin_id'], asset_symbol)
            
            # Log action
            await log_admin_action(
                current['asset_id'],
                ActionType.ENABLE_DEPOSIT.value,
                {"deposit_enabled": current['deposit_enabled'], "deposit_paused": current['deposit_paused']},
                {"deposit_enabled": True, "deposit_paused": False},
                action.reason,
                admin,
                action.notes
            )
            
            logger.info(f"Enabled deposits for {asset_symbol}", admin_id=admin['admin_id'])
            return dict(updated)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enabling deposit: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/assets/{asset_symbol}/deposit/disable")
async def disable_deposit(
    asset_symbol: str,
    action: AdminAction,
    admin: dict = Depends(verify_admin_token)
):
    """Disable deposits for an asset"""
    try:
        async with db_pool.acquire() as conn:
            current = await conn.fetchrow("""
                SELECT * FROM asset_deposit_withdrawal_status
                WHERE asset_symbol = $1
            """, asset_symbol)
            
            if not current:
                raise HTTPException(status_code=404, detail="Asset not found")
            
            updated = await conn.fetchrow("""
                UPDATE asset_deposit_withdrawal_status
                SET deposit_enabled = false,
                    updated_by = $1,
                    updated_at = NOW()
                WHERE asset_symbol = $2
                RETURNING *
            """, admin['admin_id'], asset_symbol)
            
            await log_admin_action(
                current['asset_id'],
                ActionType.DISABLE_DEPOSIT.value,
                {"deposit_enabled": current['deposit_enabled']},
                {"deposit_enabled": False},
                action.reason,
                admin,
                action.notes
            )
            
            logger.info(f"Disabled deposits for {asset_symbol}", admin_id=admin['admin_id'])
            return dict(updated)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling deposit: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/assets/{asset_symbol}/deposit/pause")
async def pause_deposit(
    asset_symbol: str,
    action: AdminAction,
    admin: dict = Depends(verify_admin_token)
):
    """Pause deposits for an asset (temporary)"""
    try:
        async with db_pool.acquire() as conn:
            current = await conn.fetchrow("""
                SELECT * FROM asset_deposit_withdrawal_status
                WHERE asset_symbol = $1
            """, asset_symbol)
            
            if not current:
                raise HTTPException(status_code=404, detail="Asset not found")
            
            updated = await conn.fetchrow("""
                UPDATE asset_deposit_withdrawal_status
                SET deposit_paused = true,
                    updated_by = $1,
                    updated_at = NOW()
                WHERE asset_symbol = $2
                RETURNING *
            """, admin['admin_id'], asset_symbol)
            
            await log_admin_action(
                current['asset_id'],
                ActionType.PAUSE_DEPOSIT.value,
                {"deposit_paused": current['deposit_paused']},
                {"deposit_paused": True},
                action.reason,
                admin,
                action.notes
            )
            
            logger.info(f"Paused deposits for {asset_symbol}", admin_id=admin['admin_id'])
            return dict(updated)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pausing deposit: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/assets/{asset_symbol}/deposit/resume")
async def resume_deposit(
    asset_symbol: str,
    action: AdminAction,
    admin: dict = Depends(verify_admin_token)
):
    """Resume deposits for an asset"""
    try:
        async with db_pool.acquire() as conn:
            current = await conn.fetchrow("""
                SELECT * FROM asset_deposit_withdrawal_status
                WHERE asset_symbol = $1
            """, asset_symbol)
            
            if not current:
                raise HTTPException(status_code=404, detail="Asset not found")
            
            updated = await conn.fetchrow("""
                UPDATE asset_deposit_withdrawal_status
                SET deposit_paused = false,
                    updated_by = $1,
                    updated_at = NOW()
                WHERE asset_symbol = $2
                RETURNING *
            """, admin['admin_id'], asset_symbol)
            
            await log_admin_action(
                current['asset_id'],
                ActionType.RESUME_DEPOSIT.value,
                {"deposit_paused": current['deposit_paused']},
                {"deposit_paused": False},
                action.reason,
                admin,
                action.notes
            )
            
            logger.info(f"Resumed deposits for {asset_symbol}", admin_id=admin['admin_id'])
            return dict(updated)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming deposit: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/admin/assets/{asset_symbol}/deposit/settings")
async def update_deposit_settings(
    asset_symbol: str,
    settings: DepositControlUpdate,
    action: AdminAction,
    admin: dict = Depends(verify_admin_token)
):
    """Update deposit settings for an asset"""
    try:
        async with db_pool.acquire() as conn:
            current = await conn.fetchrow("""
                SELECT * FROM asset_deposit_withdrawal_status
                WHERE asset_symbol = $1
            """, asset_symbol)
            
            if not current:
                raise HTTPException(status_code=404, detail="Asset not found")
            
            # Build update query
            updates = []
            params = [admin['admin_id']]
            param_count = 1
            
            for field, value in settings.dict(exclude_unset=True).items():
                if value is not None:
                    param_count += 1
                    updates.append(f"{field} = ${param_count}")
                    params.append(value)
            
            if not updates:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            param_count += 1
            params.append(asset_symbol)
            
            query = f"""
                UPDATE asset_deposit_withdrawal_status
                SET {', '.join(updates)}, updated_by = $1, updated_at = NOW()
                WHERE asset_symbol = ${param_count}
                RETURNING *
            """
            
            updated = await conn.fetchrow(query, *params)
            
            await log_admin_action(
                current['asset_id'],
                ActionType.UPDATE_LIMITS.value,
                {k: current[k] for k in settings.dict(exclude_unset=True).keys()},
                settings.dict(exclude_unset=True),
                action.reason,
                admin,
                action.notes
            )
            
            logger.info(f"Updated deposit settings for {asset_symbol}", admin_id=admin['admin_id'])
            return dict(updated)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating deposit settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# WITHDRAWAL CONTROLS
# ============================================================================

@app.post("/api/admin/assets/{asset_symbol}/withdrawal/enable")
async def enable_withdrawal(
    asset_symbol: str,
    action: AdminAction,
    admin: dict = Depends(verify_admin_token)
):
    """Enable withdrawals for an asset"""
    try:
        async with db_pool.acquire() as conn:
            current = await conn.fetchrow("""
                SELECT * FROM asset_deposit_withdrawal_status
                WHERE asset_symbol = $1
            """, asset_symbol)
            
            if not current:
                raise HTTPException(status_code=404, detail="Asset not found")
            
            updated = await conn.fetchrow("""
                UPDATE asset_deposit_withdrawal_status
                SET withdrawal_enabled = true,
                    withdrawal_paused = false,
                    updated_by = $1,
                    updated_at = NOW()
                WHERE asset_symbol = $2
                RETURNING *
            """, admin['admin_id'], asset_symbol)
            
            await log_admin_action(
                current['asset_id'],
                ActionType.ENABLE_WITHDRAWAL.value,
                {"withdrawal_enabled": current['withdrawal_enabled'], "withdrawal_paused": current['withdrawal_paused']},
                {"withdrawal_enabled": True, "withdrawal_paused": False},
                action.reason,
                admin,
                action.notes
            )
            
            logger.info(f"Enabled withdrawals for {asset_symbol}", admin_id=admin['admin_id'])
            return dict(updated)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enabling withdrawal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/assets/{asset_symbol}/withdrawal/disable")
async def disable_withdrawal(
    asset_symbol: str,
    action: AdminAction,
    admin: dict = Depends(verify_admin_token)
):
    """Disable withdrawals for an asset"""
    try:
        async with db_pool.acquire() as conn:
            current = await conn.fetchrow("""
                SELECT * FROM asset_deposit_withdrawal_status
                WHERE asset_symbol = $1
            """, asset_symbol)
            
            if not current:
                raise HTTPException(status_code=404, detail="Asset not found")
            
            updated = await conn.fetchrow("""
                UPDATE asset_deposit_withdrawal_status
                SET withdrawal_enabled = false,
                    updated_by = $1,
                    updated_at = NOW()
                WHERE asset_symbol = $2
                RETURNING *
            """, admin['admin_id'], asset_symbol)
            
            await log_admin_action(
                current['asset_id'],
                ActionType.DISABLE_WITHDRAWAL.value,
                {"withdrawal_enabled": current['withdrawal_enabled']},
                {"withdrawal_enabled": False},
                action.reason,
                admin,
                action.notes
            )
            
            logger.info(f"Disabled withdrawals for {asset_symbol}", admin_id=admin['admin_id'])
            return dict(updated)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling withdrawal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/assets/{asset_symbol}/withdrawal/pause")
async def pause_withdrawal(
    asset_symbol: str,
    action: AdminAction,
    admin: dict = Depends(verify_admin_token)
):
    """Pause withdrawals for an asset (temporary)"""
    try:
        async with db_pool.acquire() as conn:
            current = await conn.fetchrow("""
                SELECT * FROM asset_deposit_withdrawal_status
                WHERE asset_symbol = $1
            """, asset_symbol)
            
            if not current:
                raise HTTPException(status_code=404, detail="Asset not found")
            
            updated = await conn.fetchrow("""
                UPDATE asset_deposit_withdrawal_status
                SET withdrawal_paused = true,
                    updated_by = $1,
                    updated_at = NOW()
                WHERE asset_symbol = $2
                RETURNING *
            """, admin['admin_id'], asset_symbol)
            
            await log_admin_action(
                current['asset_id'],
                ActionType.PAUSE_WITHDRAWAL.value,
                {"withdrawal_paused": current['withdrawal_paused']},
                {"withdrawal_paused": True},
                action.reason,
                admin,
                action.notes
            )
            
            logger.info(f"Paused withdrawals for {asset_symbol}", admin_id=admin['admin_id'])
            return dict(updated)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pausing withdrawal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/assets/{asset_symbol}/withdrawal/resume")
async def resume_withdrawal(
    asset_symbol: str,
    action: AdminAction,
    admin: dict = Depends(verify_admin_token)
):
    """Resume withdrawals for an asset"""
    try:
        async with db_pool.acquire() as conn:
            current = await conn.fetchrow("""
                SELECT * FROM asset_deposit_withdrawal_status
                WHERE asset_symbol = $1
            """, asset_symbol)
            
            if not current:
                raise HTTPException(status_code=404, detail="Asset not found")
            
            updated = await conn.fetchrow("""
                UPDATE asset_deposit_withdrawal_status
                SET withdrawal_paused = false,
                    updated_by = $1,
                    updated_at = NOW()
                WHERE asset_symbol = $2
                RETURNING *
            """, admin['admin_id'], asset_symbol)
            
            await log_admin_action(
                current['asset_id'],
                ActionType.RESUME_WITHDRAWAL.value,
                {"withdrawal_paused": current['withdrawal_paused']},
                {"withdrawal_paused": False},
                action.reason,
                admin,
                action.notes
            )
            
            logger.info(f"Resumed withdrawals for {asset_symbol}", admin_id=admin['admin_id'])
            return dict(updated)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming withdrawal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/admin/assets/{asset_symbol}/withdrawal/settings")
async def update_withdrawal_settings(
    asset_symbol: str,
    settings: WithdrawalControlUpdate,
    action: AdminAction,
    admin: dict = Depends(verify_admin_token)
):
    """Update withdrawal settings for an asset"""
    try:
        async with db_pool.acquire() as conn:
            current = await conn.fetchrow("""
                SELECT * FROM asset_deposit_withdrawal_status
                WHERE asset_symbol = $1
            """, asset_symbol)
            
            if not current:
                raise HTTPException(status_code=404, detail="Asset not found")
            
            # Build update query
            updates = []
            params = [admin['admin_id']]
            param_count = 1
            
            for field, value in settings.dict(exclude_unset=True).items():
                if value is not None:
                    param_count += 1
                    updates.append(f"{field} = ${param_count}")
                    params.append(value)
            
            if not updates:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            param_count += 1
            params.append(asset_symbol)
            
            query = f"""
                UPDATE asset_deposit_withdrawal_status
                SET {', '.join(updates)}, updated_by = $1, updated_at = NOW()
                WHERE asset_symbol = ${param_count}
                RETURNING *
            """
            
            updated = await conn.fetchrow(query, *params)
            
            await log_admin_action(
                current['asset_id'],
                ActionType.UPDATE_LIMITS.value,
                {k: current[k] for k in settings.dict(exclude_unset=True).keys()},
                settings.dict(exclude_unset=True),
                action.reason,
                admin,
                action.notes
            )
            
            logger.info(f"Updated withdrawal settings for {asset_symbol}", admin_id=admin['admin_id'])
            return dict(updated)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating withdrawal settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# BULK OPERATIONS
# ============================================================================

@app.post("/api/admin/assets/bulk-action")
async def bulk_asset_action(
    bulk_action: BulkAssetAction,
    admin: dict = Depends(verify_admin_token)
):
    """Perform bulk action on multiple assets"""
    try:
        results = []
        
        for asset_symbol in bulk_action.asset_symbols:
            try:
                action = AdminAction(
                    action_type=bulk_action.action_type,
                    reason=bulk_action.reason
                )
                
                # Route to appropriate endpoint based on action type
                if bulk_action.action_type == ActionType.ENABLE_DEPOSIT:
                    result = await enable_deposit(asset_symbol, action, admin)
                elif bulk_action.action_type == ActionType.DISABLE_DEPOSIT:
                    result = await disable_deposit(asset_symbol, action, admin)
                elif bulk_action.action_type == ActionType.PAUSE_DEPOSIT:
                    result = await pause_deposit(asset_symbol, action, admin)
                elif bulk_action.action_type == ActionType.RESUME_DEPOSIT:
                    result = await resume_deposit(asset_symbol, action, admin)
                elif bulk_action.action_type == ActionType.ENABLE_WITHDRAWAL:
                    result = await enable_withdrawal(asset_symbol, action, admin)
                elif bulk_action.action_type == ActionType.DISABLE_WITHDRAWAL:
                    result = await disable_withdrawal(asset_symbol, action, admin)
                elif bulk_action.action_type == ActionType.PAUSE_WITHDRAWAL:
                    result = await pause_withdrawal(asset_symbol, action, admin)
                elif bulk_action.action_type == ActionType.RESUME_WITHDRAWAL:
                    result = await resume_withdrawal(asset_symbol, action, admin)
                
                results.append({
                    "asset_symbol": asset_symbol,
                    "success": True,
                    "result": result
                })
                
            except Exception as e:
                results.append({
                    "asset_symbol": asset_symbol,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "total": len(bulk_action.asset_symbols),
            "successful": sum(1 for r in results if r['success']),
            "failed": sum(1 for r in results if not r['success']),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in bulk action: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MAINTENANCE MODE
# ============================================================================

@app.post("/api/admin/assets/{asset_symbol}/maintenance/enable")
async def enable_maintenance(
    asset_symbol: str,
    schedule: MaintenanceSchedule,
    admin: dict = Depends(verify_admin_token)
):
    """Enable maintenance mode for an asset"""
    try:
        async with db_pool.acquire() as conn:
            current = await conn.fetchrow("""
                SELECT * FROM asset_deposit_withdrawal_status
                WHERE asset_symbol = $1
            """, asset_symbol)
            
            if not current:
                raise HTTPException(status_code=404, detail="Asset not found")
            
            updated = await conn.fetchrow("""
                UPDATE asset_deposit_withdrawal_status
                SET maintenance_mode = true,
                    maintenance_reason = $1,
                    maintenance_start_time = $2,
                    maintenance_end_time = $3,
                    deposit_paused = true,
                    withdrawal_paused = true,
                    network_status = 'maintenance',
                    updated_by = $4,
                    updated_at = NOW()
                WHERE asset_symbol = $5
                RETURNING *
            """, schedule.maintenance_reason, schedule.maintenance_start_time,
            schedule.maintenance_end_time, admin['admin_id'], asset_symbol)
            
            await log_admin_action(
                current['asset_id'],
                ActionType.ENABLE_MAINTENANCE.value,
                {"maintenance_mode": current['maintenance_mode']},
                {"maintenance_mode": True, "maintenance_reason": schedule.maintenance_reason},
                "Scheduled maintenance",
                admin
            )
            
            logger.info(f"Enabled maintenance mode for {asset_symbol}", admin_id=admin['admin_id'])
            return dict(updated)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enabling maintenance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/assets/{asset_symbol}/maintenance/disable")
async def disable_maintenance(
    asset_symbol: str,
    action: AdminAction,
    admin: dict = Depends(verify_admin_token)
):
    """Disable maintenance mode for an asset"""
    try:
        async with db_pool.acquire() as conn:
            current = await conn.fetchrow("""
                SELECT * FROM asset_deposit_withdrawal_status
                WHERE asset_symbol = $1
            """, asset_symbol)
            
            if not current:
                raise HTTPException(status_code=404, detail="Asset not found")
            
            updated = await conn.fetchrow("""
                UPDATE asset_deposit_withdrawal_status
                SET maintenance_mode = false,
                    deposit_paused = false,
                    withdrawal_paused = false,
                    network_status = 'online',
                    updated_by = $1,
                    updated_at = NOW()
                WHERE asset_symbol = $2
                RETURNING *
            """, admin['admin_id'], asset_symbol)
            
            await log_admin_action(
                current['asset_id'],
                ActionType.DISABLE_MAINTENANCE.value,
                {"maintenance_mode": current['maintenance_mode']},
                {"maintenance_mode": False},
                action.reason,
                admin,
                action.notes
            )
            
            logger.info(f"Disabled maintenance mode for {asset_symbol}", admin_id=admin['admin_id'])
            return dict(updated)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling maintenance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# WITHDRAWAL APPROVAL
# ============================================================================

@app.get("/api/admin/withdrawals/pending")
async def get_pending_withdrawals(
    asset_symbol: Optional[str] = None,
    requires_approval: bool = True,
    skip: int = 0,
    limit: int = 100,
    admin: dict = Depends(verify_admin_token)
):
    """Get pending withdrawals requiring approval"""
    try:
        async with db_pool.acquire() as conn:
            query = """
                SELECT * FROM pending_withdrawals
                WHERE status = 'pending'
            """
            params = []
            
            if requires_approval:
                query += " AND requires_manual_approval = true"
            
            if asset_symbol:
                query += f" AND asset_symbol = ${len(params) + 1}"
                params.append(asset_symbol)
            
            query += f" ORDER BY requested_at DESC OFFSET ${len(params) + 1} LIMIT ${len(params) + 2}"
            params.extend([skip, limit])
            
            withdrawals = await conn.fetch(query, *params)
            total = await conn.fetchval(
                "SELECT COUNT(*) FROM pending_withdrawals WHERE status = 'pending'"
            )
            
            return {
                "total": total,
                "withdrawals": [dict(w) for w in withdrawals]
            }
            
    except Exception as e:
        logger.error(f"Error fetching pending withdrawals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/withdrawals/{withdrawal_id}/approve")
async def approve_withdrawal(
    withdrawal_id: str,
    approval: WithdrawalApproval,
    admin: dict = Depends(verify_admin_token)
):
    """Approve or reject a withdrawal"""
    try:
        async with db_pool.acquire() as conn:
            withdrawal = await conn.fetchrow("""
                SELECT * FROM pending_withdrawals
                WHERE withdrawal_id = $1
            """, withdrawal_id)
            
            if not withdrawal:
                raise HTTPException(status_code=404, detail="Withdrawal not found")
            
            if approval.approved:
                updated = await conn.fetchrow("""
                    UPDATE pending_withdrawals
                    SET status = 'approved',
                        approved_by = $1,
                        approved_at = NOW()
                    WHERE withdrawal_id = $2
                    RETURNING *
                """, admin['admin_id'], withdrawal_id)
                
                logger.info(f"Approved withdrawal: {withdrawal_id}", admin_id=admin['admin_id'])
            else:
                updated = await conn.fetchrow("""
                    UPDATE pending_withdrawals
                    SET status = 'rejected',
                        approved_by = $1,
                        approved_at = NOW(),
                        rejection_reason = $2
                    WHERE withdrawal_id = $3
                    RETURNING *
                """, admin['admin_id'], approval.rejection_reason, withdrawal_id)
                
                logger.info(f"Rejected withdrawal: {withdrawal_id}", admin_id=admin['admin_id'])
            
            return dict(updated)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving withdrawal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ANALYTICS & MONITORING
# ============================================================================

@app.get("/api/admin/analytics/overview")
async def get_analytics_overview(
    admin: dict = Depends(verify_admin_token)
):
    """Get deposit/withdrawal analytics overview"""
    try:
        async with db_pool.acquire() as conn:
            # Asset status summary
            asset_summary = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_assets,
                    COUNT(*) FILTER (WHERE deposit_enabled = true) as deposit_enabled_count,
                    COUNT(*) FILTER (WHERE withdrawal_enabled = true) as withdrawal_enabled_count,
                    COUNT(*) FILTER (WHERE deposit_paused = true) as deposit_paused_count,
                    COUNT(*) FILTER (WHERE withdrawal_paused = true) as withdrawal_paused_count,
                    COUNT(*) FILTER (WHERE maintenance_mode = true) as maintenance_count,
                    COUNT(*) FILTER (WHERE network_status = 'online') as online_count,
                    COUNT(*) FILTER (WHERE network_status = 'offline') as offline_count
                FROM asset_deposit_withdrawal_status
            """)
            
            # Pending transactions
            pending_summary = await conn.fetchrow("""
                SELECT 
                    (SELECT COUNT(*) FROM pending_deposits WHERE status = 'pending') as pending_deposits,
                    (SELECT COUNT(*) FROM pending_withdrawals WHERE status = 'pending') as pending_withdrawals,
                    (SELECT COUNT(*) FROM pending_withdrawals WHERE requires_manual_approval = true AND status = 'pending') as pending_approvals
            """)
            
            # Recent activity
            recent_actions = await conn.fetch("""
                SELECT * FROM deposit_withdrawal_action_history
                ORDER BY action_timestamp DESC
                LIMIT 10
            """)
            
            return {
                "asset_summary": dict(asset_summary),
                "pending_summary": dict(pending_summary),
                "recent_actions": [dict(a) for a in recent_actions],
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/activity-log")
async def get_activity_log(
    asset_symbol: Optional[str] = None,
    action_type: Optional[ActionType] = None,
    admin_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    admin: dict = Depends(verify_admin_token)
):
    """Get admin activity log"""
    try:
        async with db_pool.acquire() as conn:
            query = "SELECT * FROM deposit_withdrawal_action_history WHERE 1=1"
            params = []
            param_count = 0
            
            if asset_symbol:
                param_count += 1
                query += f" AND asset_id LIKE ${param_count}"
                params.append(f"%{asset_symbol}%")
            
            if action_type:
                param_count += 1
                query += f" AND action_type = ${param_count}"
                params.append(action_type.value)
            
            if admin_id:
                param_count += 1
                query += f" AND admin_id = ${param_count}"
                params.append(admin_id)
            
            query += f" ORDER BY action_timestamp DESC OFFSET ${param_count + 1} LIMIT ${param_count + 2}"
            params.extend([skip, limit])
            
            actions = await conn.fetch(query, *params)
            total = await conn.fetchval("SELECT COUNT(*) FROM deposit_withdrawal_action_history")
            
            return {
                "total": total,
                "actions": [dict(a) for a in actions]
            }
            
    except Exception as e:
        logger.error(f"Error fetching activity log: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8170)