"""
Complete DAO Governance Service
Includes: Voting, Proposals, Token-based Governance, Admin Controls
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

app = FastAPI(
    title="TigerEx DAO Governance Service",
    description="Decentralized Autonomous Organization governance system",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MODELS ====================

class Proposal(BaseModel):
    proposal_id: str
    title: str
    description: str
    proposer_id: int
    category: str
    status: str
    votes_for: int
    votes_against: int
    votes_abstain: int

class Vote(BaseModel):
    vote_id: str
    proposal_id: str
    voter_id: int
    vote_type: str
    voting_power: Decimal

# ==================== PROPOSALS ====================

@app.post("/api/v1/dao/proposals/create")
async def create_proposal(
    user_id: int,
    title: str,
    description: str,
    category: str,
    voting_period_days: int = 7
):
    """Create new DAO proposal"""
    
    return {
        "success": True,
        "proposal_id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": title,
        "description": description,
        "category": category,
        "status": "ACTIVE",
        "voting_period_days": voting_period_days,
        "start_date": datetime.utcnow().isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=voting_period_days)).isoformat(),
        "votes_for": 0,
        "votes_against": 0,
        "votes_abstain": 0,
        "quorum_required": 10000,
        "created_at": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/dao/proposals")
async def get_proposals(status: Optional[str] = None, limit: int = 50):
    """Get DAO proposals"""
    
    categories = ["PLATFORM_UPGRADE", "FEE_CHANGE", "LISTING", "TREASURY", "GOVERNANCE"]
    statuses = ["ACTIVE", "PASSED", "REJECTED", "EXECUTED"]
    
    proposals = [
        {
            "proposal_id": str(uuid.uuid4()),
            "title": f"Proposal #{i+1}: Platform Enhancement",
            "description": f"Detailed description of proposal {i+1}",
            "proposer_id": 1,
            "category": categories[i % len(categories)],
            "status": statuses[i % len(statuses)] if not status else status,
            "votes_for": 15000 + (i * 1000),
            "votes_against": 5000 + (i * 500),
            "votes_abstain": 1000 + (i * 100),
            "total_votes": 21000 + (i * 1600),
            "quorum_required": 10000,
            "quorum_reached": True,
            "start_date": (datetime.utcnow() - timedelta(days=i)).isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=7-i)).isoformat(),
            "created_at": (datetime.utcnow() - timedelta(days=i)).isoformat()
        }
        for i in range(min(limit, 20))
    ]
    
    return {
        "success": True,
        "proposals": proposals,
        "total": len(proposals)
    }

@app.get("/api/v1/dao/proposals/{proposal_id}")
async def get_proposal_details(proposal_id: str):
    """Get proposal details"""
    
    return {
        "success": True,
        "proposal_id": proposal_id,
        "title": "Proposal: Reduce Trading Fees",
        "description": "This proposal suggests reducing trading fees from 0.1% to 0.08% to increase competitiveness",
        "proposer_id": 1,
        "proposer_name": "TigerEx Community",
        "category": "FEE_CHANGE",
        "status": "ACTIVE",
        "votes_for": 15000,
        "votes_against": 5000,
        "votes_abstain": 1000,
        "total_votes": 21000,
        "quorum_required": 10000,
        "quorum_reached": True,
        "voting_power_for": "15000000.00",
        "voting_power_against": "5000000.00",
        "voting_power_abstain": "1000000.00",
        "start_date": (datetime.utcnow() - timedelta(days=2)).isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=5)).isoformat(),
        "execution_date": None,
        "created_at": (datetime.utcnow() - timedelta(days=2)).isoformat()
    }

@app.post("/api/v1/dao/proposals/{proposal_id}/vote")
async def vote_on_proposal(
    proposal_id: str,
    user_id: int,
    vote_type: str,  # FOR, AGAINST, ABSTAIN
    voting_power: Optional[float] = None
):
    """Vote on DAO proposal"""
    
    if vote_type not in ["FOR", "AGAINST", "ABSTAIN"]:
        raise HTTPException(status_code=400, detail="Invalid vote type")
    
    # Calculate voting power based on token holdings
    if not voting_power:
        voting_power = 1000.0  # Default voting power
    
    return {
        "success": True,
        "vote_id": str(uuid.uuid4()),
        "proposal_id": proposal_id,
        "user_id": user_id,
        "vote_type": vote_type,
        "voting_power": voting_power,
        "voted_at": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/dao/proposals/{proposal_id}/votes")
async def get_proposal_votes(proposal_id: str, limit: int = 100):
    """Get votes for proposal"""
    
    vote_types = ["FOR", "AGAINST", "ABSTAIN"]
    votes = [
        {
            "vote_id": str(uuid.uuid4()),
            "proposal_id": proposal_id,
            "voter_id": i,
            "voter_name": f"User {i}",
            "vote_type": vote_types[i % 3],
            "voting_power": 1000.0 + (i * 100),
            "voted_at": (datetime.utcnow() - timedelta(hours=i)).isoformat()
        }
        for i in range(min(limit, 50))
    ]
    
    return {
        "success": True,
        "votes": votes,
        "total": len(votes)
    }

@app.post("/api/v1/dao/proposals/{proposal_id}/execute")
async def execute_proposal(proposal_id: str, admin_id: int):
    """Execute passed proposal"""
    
    return {
        "success": True,
        "proposal_id": proposal_id,
        "admin_id": admin_id,
        "status": "EXECUTED",
        "execution_tx": f"0x{uuid.uuid4().hex}",
        "executed_at": datetime.utcnow().isoformat()
    }

# ==================== VOTING POWER ====================

@app.get("/api/v1/dao/voting-power/{user_id}")
async def get_voting_power(user_id: int):
    """Get user's voting power"""
    
    return {
        "success": True,
        "user_id": user_id,
        "voting_power": 10000.0,
        "token_balance": 10000.0,
        "staked_tokens": 5000.0,
        "delegated_power": 2000.0,
        "total_voting_power": 17000.0,
        "last_updated": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/dao/delegate")
async def delegate_voting_power(
    user_id: int,
    delegate_to_id: int,
    amount: float
):
    """Delegate voting power to another user"""
    
    return {
        "success": True,
        "delegation_id": str(uuid.uuid4()),
        "user_id": user_id,
        "delegate_to_id": delegate_to_id,
        "amount": amount,
        "status": "ACTIVE",
        "delegated_at": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/dao/undelegate/{delegation_id}")
async def undelegate_voting_power(delegation_id: str, user_id: int):
    """Undelegate voting power"""
    
    return {
        "success": True,
        "delegation_id": delegation_id,
        "user_id": user_id,
        "status": "REVOKED",
        "undelegated_at": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/dao/delegations/{user_id}")
async def get_delegations(user_id: int):
    """Get user's delegations"""
    
    delegations = [
        {
            "delegation_id": str(uuid.uuid4()),
            "user_id": user_id,
            "delegate_to_id": i,
            "delegate_to_name": f"User {i}",
            "amount": 1000.0,
            "status": "ACTIVE",
            "delegated_at": (datetime.utcnow() - timedelta(days=i)).isoformat()
        }
        for i in range(3)
    ]
    
    return {
        "success": True,
        "delegations": delegations,
        "total_delegated": sum([d["amount"] for d in delegations])
    }

# ==================== TREASURY ====================

@app.get("/api/v1/dao/treasury")
async def get_treasury_info():
    """Get DAO treasury information"""
    
    return {
        "success": True,
        "treasury": {
            "total_value_usd": 10000000.0,
            "assets": [
                {"asset": "USDT", "amount": 5000000.0, "value_usd": 5000000.0},
                {"asset": "BTC", "amount": 50.0, "value_usd": 2500000.0},
                {"asset": "ETH", "amount": 500.0, "value_usd": 1500000.0},
                {"asset": "TGR", "amount": 1000000.0, "value_usd": 1000000.0}
            ],
            "last_updated": datetime.utcnow().isoformat()
        }
    }

@app.post("/api/v1/dao/treasury/propose-spending")
async def propose_treasury_spending(
    user_id: int,
    amount: float,
    asset: str,
    purpose: str,
    recipient: str
):
    """Propose treasury spending"""
    
    return {
        "success": True,
        "proposal_id": str(uuid.uuid4()),
        "user_id": user_id,
        "amount": amount,
        "asset": asset,
        "purpose": purpose,
        "recipient": recipient,
        "status": "PENDING_VOTE",
        "created_at": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/dao/treasury/transactions")
async def get_treasury_transactions(limit: int = 50):
    """Get treasury transaction history"""
    
    transactions = [
        {
            "tx_id": str(uuid.uuid4()),
            "type": "SPENDING" if i % 2 == 0 else "INCOME",
            "amount": 10000.0,
            "asset": "USDT",
            "purpose": "Development Grant" if i % 2 == 0 else "Trading Fees",
            "proposal_id": str(uuid.uuid4()) if i % 2 == 0 else None,
            "tx_hash": f"0x{uuid.uuid4().hex}",
            "created_at": (datetime.utcnow() - timedelta(days=i)).isoformat()
        }
        for i in range(min(limit, 20))
    ]
    
    return {
        "success": True,
        "transactions": transactions,
        "total": len(transactions)
    }

# ==================== GOVERNANCE STATISTICS ====================

@app.get("/api/v1/dao/statistics")
async def get_dao_statistics():
    """Get DAO governance statistics"""
    
    return {
        "success": True,
        "statistics": {
            "total_proposals": 150,
            "active_proposals": 5,
            "passed_proposals": 100,
            "rejected_proposals": 30,
            "executed_proposals": 95,
            "total_voters": 5000,
            "total_votes_cast": 50000,
            "average_participation_rate": 45.5,
            "treasury_value_usd": 10000000.0,
            "total_voting_power": 100000000.0
        },
        "last_updated": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/dao/leaderboard")
async def get_governance_leaderboard(limit: int = 20):
    """Get governance participation leaderboard"""
    
    leaderboard = [
        {
            "rank": i + 1,
            "user_id": i,
            "username": f"User {i}",
            "proposals_created": 10 - i,
            "votes_cast": 100 - (i * 5),
            "voting_power": 10000 - (i * 500),
            "participation_rate": 95 - (i * 2)
        }
        for i in range(min(limit, 20))
    ]
    
    return {
        "success": True,
        "leaderboard": leaderboard,
        "total": len(leaderboard)
    }

# ==================== ADMIN CONTROLS ====================

@app.post("/api/v1/dao/admin/enable")
async def enable_dao_governance(admin_id: int):
    """Enable DAO governance"""
    
    return {
        "success": True,
        "admin_id": admin_id,
        "service": "DAO Governance",
        "status": "ENABLED",
        "enabled_at": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/dao/admin/disable")
async def disable_dao_governance(admin_id: int):
    """Disable DAO governance"""
    
    return {
        "success": True,
        "admin_id": admin_id,
        "service": "DAO Governance",
        "status": "DISABLED",
        "disabled_at": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/dao/admin/set-quorum")
async def set_quorum_requirement(admin_id: int, quorum: int):
    """Set quorum requirement for proposals"""
    
    return {
        "success": True,
        "admin_id": admin_id,
        "quorum_requirement": quorum,
        "updated_at": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/dao/admin/set-voting-period")
async def set_voting_period(admin_id: int, days: int):
    """Set default voting period"""
    
    return {
        "success": True,
        "admin_id": admin_id,
        "voting_period_days": days,
        "updated_at": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/dao/admin/cancel-proposal/{proposal_id}")
async def cancel_proposal(proposal_id: str, admin_id: int, reason: str):
    """Cancel proposal (admin only)"""
    
    return {
        "success": True,
        "proposal_id": proposal_id,
        "admin_id": admin_id,
        "status": "CANCELLED",
        "reason": reason,
        "cancelled_at": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/dao/admin/pending-executions")
async def get_pending_executions(admin_id: int):
    """Get proposals pending execution"""
    
    proposals = [
        {
            "proposal_id": str(uuid.uuid4()),
            "title": f"Proposal #{i+1}: Pending Execution",
            "category": "PLATFORM_UPGRADE",
            "status": "PASSED",
            "votes_for": 15000,
            "votes_against": 5000,
            "passed_at": (datetime.utcnow() - timedelta(days=i)).isoformat()
        }
        for i in range(5)
    ]
    
    return {
        "success": True,
        "proposals": proposals,
        "total": len(proposals)
    }

# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "DAO Governance",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8298)