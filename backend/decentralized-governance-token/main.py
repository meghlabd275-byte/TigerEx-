#!/usr/bin/env python3
"""
Decentralized Governance Token Service
Complete DAO governance system with token management, voting, and proposals
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
import uuid
import logging
import os
import asyncio
import aioredis
import json
from decimal import Decimal
import numpy as np
from web3 import Web3
from eth_account import Account

# FastAPI app
app = FastAPI(
    title="TigerEx Decentralized Governance Token",
    description="Complete DAO governance system with token management, voting, and proposals",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/tigerex_governance")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Web3 setup
WEB3_PROVIDER = os.getenv("WEB3_PROVIDER", "https://mainnet.infura.io/v3/your-key")
w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Governance Token Configuration
GOVERNANCE_TOKEN = {
    "name": "TigerEx Governance Token",
    "symbol": "TGRX",
    "decimals": 18,
    "total_supply": 1000000000,  # 1 billion tokens
    "contract_address": "0x1234567890123456789012345678901234567890"  # Mock address
}

# Database Models
class GovernanceToken(Base):
    __tablename__ = "governance_tokens"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Token holder information
    holder_address = Column(String, nullable=False, index=True)
    balance = Column(String, default="0")  # Use string for precision
    
    # Staking information
    staked_balance = Column(String, default="0")
    staking_rewards = Column(String, default="0")
    last_stake_time = Column(DateTime)
    
    # Voting power
    voting_power = Column(String, default="0")
    delegated_to = Column(String)  # Address tokens are delegated to
    delegated_from = Column(JSON, default=list)  # List of addresses that delegated to this holder
    
    # Lock information
    locked_balance = Column(String, default="0")
    lock_end_time = Column(DateTime)
    lock_multiplier = Column(Float, default=1.0)
    
    # Rewards and benefits
    accumulated_rewards = Column(String, default="0")
    last_reward_claim = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GovernanceProposal(Base):
    __tablename__ = "governance_proposals"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Proposal details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)  # protocol, treasury, partnership, etc.
    
    # Proposer information
    proposer_address = Column(String, nullable=False)
    proposer_stake = Column(String, default="0")
    
    # Proposal parameters
    proposal_type = Column(String, default="standard")  # standard, constitutional, emergency
    execution_delay = Column(Integer, default=172800)  # 48 hours in seconds
    
    # Voting parameters
    voting_start = Column(DateTime, nullable=False)
    voting_end = Column(DateTime, nullable=False)
    quorum_required = Column(String, default="100000000")  # 100M tokens
    approval_threshold = Column(Float, default=0.5)  # 50%
    
    # Voting results
    votes_for = Column(String, default="0")
    votes_against = Column(String, default="0")
    votes_abstain = Column(String, default="0")
    total_votes = Column(String, default="0")
    unique_voters = Column(Integer, default=0)
    
    # Status
    status = Column(String, default="pending")  # pending, active, passed, failed, executed, cancelled
    
    # Execution
    execution_data = Column(JSON)
    executed_at = Column(DateTime)
    execution_tx_hash = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GovernanceVote(Base):
    __tablename__ = "governance_votes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Vote details
    proposal_id = Column(String, nullable=False, index=True)
    voter_address = Column(String, nullable=False, index=True)
    
    # Vote choice
    vote_choice = Column(String, nullable=False)  # for, against, abstain
    voting_power = Column(String, nullable=False)
    
    # Vote metadata
    reason = Column(Text)
    vote_weight = Column(Float, default=1.0)
    
    # Delegation
    is_delegated = Column(Boolean, default=False)
    delegator_address = Column(String)
    
    # Transaction
    tx_hash = Column(String)
    block_number = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class TokenStaking(Base):
    __tablename__ = "token_staking"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Staker information
    staker_address = Column(String, nullable=False, index=True)
    
    # Staking details
    staked_amount = Column(String, nullable=False)
    staking_duration = Column(Integer, nullable=False)  # in days
    lock_multiplier = Column(Float, default=1.0)
    
    # Timing
    stake_start = Column(DateTime, default=datetime.utcnow)
    stake_end = Column(DateTime, nullable=False)
    
    # Rewards
    reward_rate = Column(Float, default=0.05)  # 5% APY
    accumulated_rewards = Column(String, default="0")
    last_reward_calculation = Column(DateTime, default=datetime.utcnow)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class TokenDelegation(Base):
    __tablename__ = "token_delegations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Delegation details
    delegator_address = Column(String, nullable=False, index=True)
    delegate_address = Column(String, nullable=False, index=True)
    
    # Delegation amount
    delegated_amount = Column(String, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Transaction
    tx_hash = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime)

class TreasuryTransaction(Base):
    __tablename__ = "treasury_transactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Transaction details
    transaction_type = Column(String, nullable=False)  # deposit, withdrawal, reward
    amount = Column(String, nullable=False)
    token = Column(String, default="TGRX")
    
    # Related proposal
    proposal_id = Column(String)
    
    # Transaction data
    from_address = Column(String)
    to_address = Column(String)
    tx_hash = Column(String)
    
    # Status
    status = Column(String, default="pending")  # pending, confirmed, failed
    
    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime)

class GovernanceMetrics(Base):
    __tablename__ = "governance_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Snapshot date
    snapshot_date = Column(DateTime, default=datetime.utcnow)
    
    # Token metrics
    total_supply = Column(String, default="0")
    circulating_supply = Column(String, default="0")
    staked_supply = Column(String, default="0")
    locked_supply = Column(String, default="0")
    
    # Governance metrics
    total_holders = Column(Integer, default=0)
    active_voters = Column(Integer, default=0)
    total_proposals = Column(Integer, default=0)
    active_proposals = Column(Integer, default=0)
    
    # Participation metrics
    voting_participation_rate = Column(Float, default=0.0)
    average_proposal_duration = Column(Float, default=0.0)
    proposal_success_rate = Column(Float, default=0.0)
    
    # Treasury metrics
    treasury_balance = Column(String, default="0")
    treasury_value_usd = Column(Float, default=0.0)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class ProposalCreate(BaseModel):
    title: str
    description: str
    category: str
    proposal_type: str = "standard"
    voting_duration_days: int = 7
    execution_delay_hours: int = 48
    quorum_required: str = "100000000"
    approval_threshold: float = 0.5
    execution_data: Optional[Dict[str, Any]] = None

class VoteCreate(BaseModel):
    proposal_id: str
    vote_choice: str  # for, against, abstain
    voting_power: str
    reason: Optional[str] = None

class StakeCreate(BaseModel):
    amount: str
    duration_days: int

class DelegationCreate(BaseModel):
    delegate_address: str
    amount: str

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions
async def get_redis():
    return await aioredis.from_url(REDIS_URL)

def calculate_voting_power(balance: str, staked_balance: str, lock_multiplier: float = 1.0) -> str:
    """Calculate voting power based on balance, staking, and lock multiplier"""
    total_balance = Decimal(balance) + Decimal(staked_balance)
    voting_power = total_balance * Decimal(str(lock_multiplier))
    return str(voting_power)

def calculate_staking_rewards(stake: TokenStaking) -> str:
    """Calculate staking rewards"""
    if not stake.is_active:
        return "0"
    
    # Calculate time elapsed since last reward calculation
    now = datetime.utcnow()
    time_elapsed = (now - stake.last_reward_calculation).total_seconds()
    days_elapsed = time_elapsed / 86400  # Convert to days
    
    # Calculate rewards (APY basis)
    staked_amount = Decimal(stake.staked_amount)
    annual_reward = staked_amount * Decimal(str(stake.reward_rate))
    daily_reward = annual_reward / Decimal("365")
    new_rewards = daily_reward * Decimal(str(days_elapsed))
    
    total_rewards = Decimal(stake.accumulated_rewards) + new_rewards
    return str(total_rewards)

def check_proposal_quorum(proposal: GovernanceProposal) -> bool:
    """Check if proposal meets quorum requirements"""
    return Decimal(proposal.total_votes) >= Decimal(proposal.quorum_required)

def check_proposal_approval(proposal: GovernanceProposal) -> bool:
    """Check if proposal meets approval threshold"""
    if Decimal(proposal.total_votes) == 0:
        return False
    
    approval_rate = Decimal(proposal.votes_for) / Decimal(proposal.total_votes)
    return float(approval_rate) >= proposal.approval_threshold

async def execute_proposal(proposal: GovernanceProposal, db: Session) -> Dict[str, Any]:
    """Execute approved proposal"""
    try:
        execution_result = {"status": "success", "message": "Proposal executed successfully"}
        
        # Mock execution logic based on proposal category
        if proposal.category == "treasury":
            # Execute treasury transaction
            if proposal.execution_data:
                treasury_tx = TreasuryTransaction(
                    transaction_type="withdrawal",
                    amount=proposal.execution_data.get("amount", "0"),
                    token=proposal.execution_data.get("token", "TGRX"),
                    proposal_id=proposal.id,
                    to_address=proposal.execution_data.get("recipient"),
                    tx_hash=f"0x{uuid.uuid4().hex}"
                )
                db.add(treasury_tx)
        
        elif proposal.category == "protocol":
            # Execute protocol upgrade
            execution_result["message"] = "Protocol upgrade executed"
        
        elif proposal.category == "partnership":
            # Execute partnership agreement
            execution_result["message"] = "Partnership agreement executed"
        
        # Update proposal status
        proposal.status = "executed"
        proposal.executed_at = datetime.utcnow()
        proposal.execution_tx_hash = f"0x{uuid.uuid4().hex}"
        
        db.commit()
        
        return execution_result
        
    except Exception as e:
        logger.error(f"Error executing proposal {proposal.id}: {e}")
        proposal.status = "failed"
        db.commit()
        return {"status": "error", "message": str(e)}

def update_governance_metrics(db: Session):
    """Update governance metrics"""
    try:
        # Calculate token metrics
        tokens = db.query(GovernanceToken).all()
        
        total_supply = GOVERNANCE_TOKEN["total_supply"]
        circulating_supply = sum(Decimal(token.balance) for token in tokens)
        staked_supply = sum(Decimal(token.staked_balance) for token in tokens)
        locked_supply = sum(Decimal(token.locked_balance) for token in tokens)
        
        # Calculate governance metrics
        total_holders = len(tokens)
        
        proposals = db.query(GovernanceProposal).all()
        total_proposals = len(proposals)
        active_proposals = len([p for p in proposals if p.status == "active"])
        
        # Calculate participation metrics
        recent_votes = db.query(GovernanceVote).filter(
            GovernanceVote.created_at >= datetime.utcnow() - timedelta(days=30)
        ).all()
        
        active_voters = len(set(vote.voter_address for vote in recent_votes))
        voting_participation_rate = (active_voters / total_holders * 100) if total_holders > 0 else 0
        
        # Calculate proposal metrics
        completed_proposals = [p for p in proposals if p.status in ["passed", "failed", "executed"]]
        successful_proposals = [p for p in completed_proposals if p.status in ["passed", "executed"]]
        proposal_success_rate = (len(successful_proposals) / len(completed_proposals) * 100) if completed_proposals else 0
        
        # Calculate treasury metrics
        treasury_txs = db.query(TreasuryTransaction).filter(
            TreasuryTransaction.status == "confirmed"
        ).all()
        
        treasury_balance = sum(
            Decimal(tx.amount) if tx.transaction_type == "deposit" else -Decimal(tx.amount)
            for tx in treasury_txs
        )
        
        # Save metrics
        metrics = GovernanceMetrics(
            total_supply=str(total_supply),
            circulating_supply=str(circulating_supply),
            staked_supply=str(staked_supply),
            locked_supply=str(locked_supply),
            total_holders=total_holders,
            active_voters=active_voters,
            total_proposals=total_proposals,
            active_proposals=active_proposals,
            voting_participation_rate=voting_participation_rate,
            proposal_success_rate=proposal_success_rate,
            treasury_balance=str(treasury_balance),
            treasury_value_usd=float(treasury_balance) * 1.0  # Mock USD value
        )
        
        db.add(metrics)
        db.commit()
        
        logger.info("Governance metrics updated successfully")
        
    except Exception as e:
        logger.error(f"Error updating governance metrics: {e}")

# API Routes

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "decentralized-governance-token"}

@app.get("/token/info")
async def get_token_info():
    """Get governance token information"""
    return GOVERNANCE_TOKEN

# Token management
@app.get("/token/balance/{address}")
async def get_token_balance(address: str, db: Session = Depends(get_db)):
    """Get token balance for address"""
    token = db.query(GovernanceToken).filter(GovernanceToken.holder_address == address).first()
    
    if not token:
        return {
            "address": address,
            "balance": "0",
            "staked_balance": "0",
            "voting_power": "0",
            "locked_balance": "0"
        }
    
    # Update voting power
    token.voting_power = calculate_voting_power(
        token.balance,
        token.staked_balance,
        token.lock_multiplier
    )
    db.commit()
    
    return token

@app.post("/token/stake")
async def stake_tokens(
    staker_address: str,
    stake_request: StakeCreate,
    db: Session = Depends(get_db)
):
    """Stake governance tokens"""
    # Get or create token record
    token = db.query(GovernanceToken).filter(
        GovernanceToken.holder_address == staker_address
    ).first()
    
    if not token:
        raise HTTPException(status_code=404, detail="Token holder not found")
    
    # Check balance
    if Decimal(token.balance) < Decimal(stake_request.amount):
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Calculate lock multiplier based on duration
    lock_multiplier = 1.0
    if stake_request.duration_days >= 365:
        lock_multiplier = 2.0  # 2x for 1+ year
    elif stake_request.duration_days >= 180:
        lock_multiplier = 1.5  # 1.5x for 6+ months
    elif stake_request.duration_days >= 90:
        lock_multiplier = 1.25  # 1.25x for 3+ months
    
    # Create staking record
    stake = TokenStaking(
        staker_address=staker_address,
        staked_amount=stake_request.amount,
        staking_duration=stake_request.duration_days,
        lock_multiplier=lock_multiplier,
        stake_end=datetime.utcnow() + timedelta(days=stake_request.duration_days),
        reward_rate=0.05 * lock_multiplier  # Higher rewards for longer locks
    )
    
    db.add(stake)
    
    # Update token balances
    token.balance = str(Decimal(token.balance) - Decimal(stake_request.amount))
    token.staked_balance = str(Decimal(token.staked_balance) + Decimal(stake_request.amount))
    token.lock_multiplier = max(token.lock_multiplier, lock_multiplier)
    token.last_stake_time = datetime.utcnow()
    
    # Update voting power
    token.voting_power = calculate_voting_power(
        token.balance,
        token.staked_balance,
        token.lock_multiplier
    )
    
    db.commit()
    db.refresh(stake)
    
    return {
        "stake": stake,
        "updated_token": token
    }

@app.post("/token/unstake/{stake_id}")
async def unstake_tokens(
    stake_id: str,
    staker_address: str,
    db: Session = Depends(get_db)
):
    """Unstake governance tokens"""
    stake = db.query(TokenStaking).filter(
        TokenStaking.id == stake_id,
        TokenStaking.staker_address == staker_address
    ).first()
    
    if not stake:
        raise HTTPException(status_code=404, detail="Stake not found")
    
    if not stake.is_active:
        raise HTTPException(status_code=400, detail="Stake already inactive")
    
    if datetime.utcnow() < stake.stake_end:
        raise HTTPException(status_code=400, detail="Stake period not completed")
    
    # Calculate final rewards
    final_rewards = calculate_staking_rewards(stake)
    
    # Get token record
    token = db.query(GovernanceToken).filter(
        GovernanceToken.holder_address == staker_address
    ).first()
    
    if token:
        # Return staked tokens and rewards
        token.balance = str(Decimal(token.balance) + Decimal(stake.staked_amount))
        token.staked_balance = str(Decimal(token.staked_balance) - Decimal(stake.staked_amount))
        token.accumulated_rewards = str(Decimal(token.accumulated_rewards) + Decimal(final_rewards))
        
        # Update voting power
        token.voting_power = calculate_voting_power(
            token.balance,
            token.staked_balance,
            token.lock_multiplier
        )
    
    # Deactivate stake
    stake.is_active = False
    stake.accumulated_rewards = final_rewards
    
    db.commit()
    
    return {
        "message": "Tokens unstaked successfully",
        "returned_amount": stake.staked_amount,
        "rewards_earned": final_rewards,
        "updated_token": token
    }

# Delegation
@app.post("/token/delegate")
async def delegate_tokens(
    delegator_address: str,
    delegation: DelegationCreate,
    db: Session = Depends(get_db)
):
    """Delegate voting power to another address"""
    # Get delegator token record
    delegator_token = db.query(GovernanceToken).filter(
        GovernanceToken.holder_address == delegator_address
    ).first()
    
    if not delegator_token:
        raise HTTPException(status_code=404, detail="Delegator not found")
    
    # Check available balance
    available_balance = Decimal(delegator_token.balance) + Decimal(delegator_token.staked_balance)
    if available_balance < Decimal(delegation.amount):
        raise HTTPException(status_code=400, detail="Insufficient balance to delegate")
    
    # Create delegation record
    db_delegation = TokenDelegation(
        delegator_address=delegator_address,
        delegate_address=delegation.delegate_address,
        delegated_amount=delegation.amount,
        tx_hash=f"0x{uuid.uuid4().hex}"
    )
    
    db.add(db_delegation)
    
    # Update delegator token
    delegator_token.delegated_to = delegation.delegate_address
    
    # Update delegate token
    delegate_token = db.query(GovernanceToken).filter(
        GovernanceToken.holder_address == delegation.delegate_address
    ).first()
    
    if not delegate_token:
        # Create token record for delegate
        delegate_token = GovernanceToken(
            holder_address=delegation.delegate_address,
            balance="0"
        )
        db.add(delegate_token)
    
    # Update delegate's delegated_from list
    delegated_from = delegate_token.delegated_from or []
    if delegator_address not in delegated_from:
        delegated_from.append(delegator_address)
        delegate_token.delegated_from = delegated_from
    
    # Update voting powers
    delegator_token.voting_power = "0"  # Delegated away
    delegate_token.voting_power = str(
        Decimal(delegate_token.voting_power or "0") + Decimal(delegation.amount)
    )
    
    db.commit()
    db.refresh(db_delegation)
    
    return db_delegation

@app.delete("/token/delegate/{delegation_id}")
async def revoke_delegation(
    delegation_id: str,
    delegator_address: str,
    db: Session = Depends(get_db)
):
    """Revoke token delegation"""
    delegation = db.query(TokenDelegation).filter(
        TokenDelegation.id == delegation_id,
        TokenDelegation.delegator_address == delegator_address,
        TokenDelegation.is_active == True
    ).first()
    
    if not delegation:
        raise HTTPException(status_code=404, detail="Active delegation not found")
    
    # Revoke delegation
    delegation.is_active = False
    delegation.revoked_at = datetime.utcnow()
    
    # Update token records
    delegator_token = db.query(GovernanceToken).filter(
        GovernanceToken.holder_address == delegator_address
    ).first()
    
    delegate_token = db.query(GovernanceToken).filter(
        GovernanceToken.holder_address == delegation.delegate_address
    ).first()
    
    if delegator_token:
        delegator_token.delegated_to = None
        delegator_token.voting_power = calculate_voting_power(
            delegator_token.balance,
            delegator_token.staked_balance,
            delegator_token.lock_multiplier
        )
    
    if delegate_token:
        # Remove from delegated_from list
        delegated_from = delegate_token.delegated_from or []
        if delegator_address in delegated_from:
            delegated_from.remove(delegator_address)
            delegate_token.delegated_from = delegated_from
        
        # Update voting power
        delegate_token.voting_power = str(
            max(Decimal("0"), Decimal(delegate_token.voting_power or "0") - Decimal(delegation.delegated_amount))
        )
    
    db.commit()
    
    return {"message": "Delegation revoked successfully"}

# Proposals
@app.post("/proposals")
async def create_proposal(
    proposer_address: str,
    proposal: ProposalCreate,
    db: Session = Depends(get_db)
):
    """Create governance proposal"""
    # Check proposer eligibility
    proposer_token = db.query(GovernanceToken).filter(
        GovernanceToken.holder_address == proposer_address
    ).first()
    
    if not proposer_token:
        raise HTTPException(status_code=404, detail="Proposer not found")
    
    # Check minimum stake requirement (1M tokens)
    min_stake = Decimal("1000000")
    total_stake = Decimal(proposer_token.balance) + Decimal(proposer_token.staked_balance)
    
    if total_stake < min_stake:
        raise HTTPException(status_code=400, detail="Insufficient stake to create proposal")
    
    # Create proposal
    voting_start = datetime.utcnow() + timedelta(hours=24)  # 24 hour delay
    voting_end = voting_start + timedelta(days=proposal.voting_duration_days)
    
    db_proposal = GovernanceProposal(
        title=proposal.title,
        description=proposal.description,
        category=proposal.category,
        proposer_address=proposer_address,
        proposer_stake=str(total_stake),
        proposal_type=proposal.proposal_type,
        execution_delay=proposal.execution_delay_hours * 3600,
        voting_start=voting_start,
        voting_end=voting_end,
        quorum_required=proposal.quorum_required,
        approval_threshold=proposal.approval_threshold,
        execution_data=proposal.execution_data,
        status="pending"
    )
    
    db.add(db_proposal)
    db.commit()
    db.refresh(db_proposal)
    
    return db_proposal

@app.get("/proposals")
async def get_proposals(
    status: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get governance proposals"""
    query = db.query(GovernanceProposal)
    
    if status:
        query = query.filter(GovernanceProposal.status == status)
    if category:
        query = query.filter(GovernanceProposal.category == category)
    
    proposals = query.order_by(GovernanceProposal.created_at.desc()).offset(skip).limit(limit).all()
    return proposals

@app.get("/proposals/{proposal_id}")
async def get_proposal(proposal_id: str, db: Session = Depends(get_db)):
    """Get proposal details"""
    proposal = db.query(GovernanceProposal).filter(GovernanceProposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Get votes for this proposal
    votes = db.query(GovernanceVote).filter(GovernanceVote.proposal_id == proposal_id).all()
    
    return {
        "proposal": proposal,
        "votes": votes,
        "vote_breakdown": {
            "for": proposal.votes_for,
            "against": proposal.votes_against,
            "abstain": proposal.votes_abstain,
            "total": proposal.total_votes,
            "unique_voters": proposal.unique_voters
        }
    }

# Voting
@app.post("/vote")
async def cast_vote(
    voter_address: str,
    vote: VoteCreate,
    db: Session = Depends(get_db)
):
    """Cast vote on proposal"""
    # Get proposal
    proposal = db.query(GovernanceProposal).filter(GovernanceProposal.id == vote.proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Check voting period
    now = datetime.utcnow()
    if now < proposal.voting_start:
        raise HTTPException(status_code=400, detail="Voting has not started")
    if now > proposal.voting_end:
        raise HTTPException(status_code=400, detail="Voting has ended")
    
    # Check if already voted
    existing_vote = db.query(GovernanceVote).filter(
        GovernanceVote.proposal_id == vote.proposal_id,
        GovernanceVote.voter_address == voter_address
    ).first()
    
    if existing_vote:
        raise HTTPException(status_code=400, detail="Already voted on this proposal")
    
    # Get voter token info
    voter_token = db.query(GovernanceToken).filter(
        GovernanceToken.holder_address == voter_address
    ).first()
    
    if not voter_token:
        raise HTTPException(status_code=404, detail="Voter not found")
    
    # Validate voting power
    actual_voting_power = calculate_voting_power(
        voter_token.balance,
        voter_token.staked_balance,
        voter_token.lock_multiplier
    )
    
    if Decimal(vote.voting_power) > Decimal(actual_voting_power):
        raise HTTPException(status_code=400, detail="Insufficient voting power")
    
    # Create vote record
    db_vote = GovernanceVote(
        proposal_id=vote.proposal_id,
        voter_address=voter_address,
        vote_choice=vote.vote_choice,
        voting_power=vote.voting_power,
        reason=vote.reason,
        tx_hash=f"0x{uuid.uuid4().hex}",
        block_number=np.random.randint(1000000, 2000000)
    )
    
    db.add(db_vote)
    
    # Update proposal vote counts
    if vote.vote_choice == "for":
        proposal.votes_for = str(Decimal(proposal.votes_for) + Decimal(vote.voting_power))
    elif vote.vote_choice == "against":
        proposal.votes_against = str(Decimal(proposal.votes_against) + Decimal(vote.voting_power))
    elif vote.vote_choice == "abstain":
        proposal.votes_abstain = str(Decimal(proposal.votes_abstain) + Decimal(vote.voting_power))
    
    proposal.total_votes = str(
        Decimal(proposal.votes_for) + 
        Decimal(proposal.votes_against) + 
        Decimal(proposal.votes_abstain)
    )
    proposal.unique_voters += 1
    
    db.commit()
    db.refresh(db_vote)
    
    return db_vote

@app.get("/votes/{proposal_id}")
async def get_proposal_votes(
    proposal_id: str,
    vote_choice: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get votes for a proposal"""
    query = db.query(GovernanceVote).filter(GovernanceVote.proposal_id == proposal_id)
    
    if vote_choice:
        query = query.filter(GovernanceVote.vote_choice == vote_choice)
    
    votes = query.order_by(GovernanceVote.created_at.desc()).offset(skip).limit(limit).all()
    return votes

# Treasury
@app.get("/treasury/balance")
async def get_treasury_balance(db: Session = Depends(get_db)):
    """Get treasury balance"""
    transactions = db.query(TreasuryTransaction).filter(
        TreasuryTransaction.status == "confirmed"
    ).all()
    
    balance_by_token = {}
    for tx in transactions:
        if tx.token not in balance_by_token:
            balance_by_token[tx.token] = Decimal("0")
        
        if tx.transaction_type == "deposit":
            balance_by_token[tx.token] += Decimal(tx.amount)
        else:
            balance_by_token[tx.token] -= Decimal(tx.amount)
    
    return {
        "balances": {token: str(balance) for token, balance in balance_by_token.items()},
        "total_transactions": len(transactions)
    }

@app.get("/treasury/transactions")
async def get_treasury_transactions(
    transaction_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get treasury transactions"""
    query = db.query(TreasuryTransaction)
    
    if transaction_type:
        query = query.filter(TreasuryTransaction.transaction_type == transaction_type)
    
    transactions = query.order_by(TreasuryTransaction.created_at.desc()).limit(limit).all()
    return transactions

# Analytics
@app.get("/analytics/overview")
async def get_governance_analytics(db: Session = Depends(get_db)):
    """Get governance analytics overview"""
    # Get latest metrics
    latest_metrics = db.query(GovernanceMetrics).order_by(
        GovernanceMetrics.snapshot_date.desc()
    ).first()
    
    if not latest_metrics:
        # Generate metrics if none exist
        update_governance_metrics(db)
        latest_metrics = db.query(GovernanceMetrics).order_by(
            GovernanceMetrics.snapshot_date.desc()
        ).first()
    
    return latest_metrics

@app.get("/analytics/participation")
async def get_participation_analytics(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get participation analytics"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get votes in period
    votes = db.query(GovernanceVote).filter(
        GovernanceVote.created_at >= start_date
    ).all()
    
    # Get proposals in period
    proposals = db.query(GovernanceProposal).filter(
        GovernanceProposal.created_at >= start_date
    ).all()
    
    # Calculate metrics
    unique_voters = len(set(vote.voter_address for vote in votes))
    total_voting_power = sum(Decimal(vote.voting_power) for vote in votes)
    
    # Participation by proposal
    participation_by_proposal = {}
    for proposal in proposals:
        proposal_votes = [v for v in votes if v.proposal_id == proposal.id]
        participation_by_proposal[proposal.id] = {
            "title": proposal.title,
            "unique_voters": len(set(v.voter_address for v in proposal_votes)),
            "total_voting_power": str(sum(Decimal(v.voting_power) for v in proposal_votes)),
            "participation_rate": len(set(v.voter_address for v in proposal_votes)) / unique_voters * 100 if unique_voters > 0 else 0
        }
    
    return {
        "period_days": days,
        "total_votes_cast": len(votes),
        "unique_voters": unique_voters,
        "total_voting_power": str(total_voting_power),
        "proposals_created": len(proposals),
        "participation_by_proposal": participation_by_proposal
    }

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks"""
    logger.info("Decentralized Governance Token service started")
    
    # Start background tasks
    asyncio.create_task(periodic_proposal_monitoring())
    asyncio.create_task(periodic_metrics_update())
    asyncio.create_task(periodic_reward_calculation())

async def periodic_proposal_monitoring():
    """Monitor proposal status and execute when ready"""
    while True:
        try:
            db = SessionLocal()
            
            # Check for proposals that need status updates
            now = datetime.utcnow()
            
            # Activate pending proposals
            pending_proposals = db.query(GovernanceProposal).filter(
                GovernanceProposal.status == "pending",
                GovernanceProposal.voting_start <= now
            ).all()
            
            for proposal in pending_proposals:
                proposal.status = "active"
                logger.info(f"Activated proposal {proposal.id}")
            
            # Close active proposals
            active_proposals = db.query(GovernanceProposal).filter(
                GovernanceProposal.status == "active",
                GovernanceProposal.voting_end <= now
            ).all()
            
            for proposal in active_proposals:
                # Check if proposal passed
                if check_proposal_quorum(proposal) and check_proposal_approval(proposal):
                    proposal.status = "passed"
                    logger.info(f"Proposal {proposal.id} passed")
                else:
                    proposal.status = "failed"
                    logger.info(f"Proposal {proposal.id} failed")
            
            # Execute passed proposals after delay
            passed_proposals = db.query(GovernanceProposal).filter(
                GovernanceProposal.status == "passed",
                GovernanceProposal.voting_end + timedelta(seconds=GovernanceProposal.execution_delay) <= now
            ).all()
            
            for proposal in passed_proposals:
                await execute_proposal(proposal, db)
                logger.info(f"Executed proposal {proposal.id}")
            
            db.commit()
            db.close()
            
            await asyncio.sleep(300)  # Check every 5 minutes
            
        except Exception as e:
            logger.error(f"Error in proposal monitoring: {e}")
            await asyncio.sleep(60)

async def periodic_metrics_update():
    """Update governance metrics periodically"""
    while True:
        try:
            db = SessionLocal()
            update_governance_metrics(db)
            db.close()
            
            await asyncio.sleep(3600)  # Update every hour
            
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
            await asyncio.sleep(300)

async def periodic_reward_calculation():
    """Calculate staking rewards periodically"""
    while True:
        try:
            db = SessionLocal()
            
            # Get active stakes
            active_stakes = db.query(TokenStaking).filter(
                TokenStaking.is_active == True
            ).all()
            
            for stake in active_stakes:
                # Calculate and update rewards
                new_rewards = calculate_staking_rewards(stake)
                stake.accumulated_rewards = new_rewards
                stake.last_reward_calculation = datetime.utcnow()
                
                # Update token holder rewards
                token = db.query(GovernanceToken).filter(
                    GovernanceToken.holder_address == stake.staker_address
                ).first()
                
                if token:
                    token.staking_rewards = new_rewards
            
            db.commit()
            db.close()
            
            await asyncio.sleep(86400)  # Calculate daily
            
        except Exception as e:
            logger.error(f"Error calculating rewards: {e}")
            await asyncio.sleep(3600)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8085)