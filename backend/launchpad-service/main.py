from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from enum import Enum
import uuid
import logging
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Launchpad Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "postgresql://tigerex:tigerex123@localhost:5432/launchpad"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class LaunchpadProjectDB(Base):
    __tablename__ = "launchpad_projects"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    website = Column(String, nullable=True)
    whitepaper = Column(String, nullable=True)
    total_supply = Column(Float, nullable=False)
    sale_supply = Column(Float, nullable=False)
    token_price = Column(Float, nullable=False)
    hard_cap = Column(Float, nullable=False)
    soft_cap = Column(Float, nullable=False)
    min_allocation = Column(Float, default=0.0)
    max_allocation = Column(Float, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    vesting_schedule = Column(Text, nullable=True)
    status = Column(String, default="upcoming")  # upcoming, active, completed, cancelled
    total_raised = Column(Float, default=0.0)
    participants_count = Column(Integer, default=0)
    kyc_required = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class LaunchpadParticipationDB(Base):
    __tablename__ = "launchpad_participations"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    amount_invested = Column(Float, nullable=False)
    tokens_allocated = Column(Float, nullable=False)
    payment_currency = Column(String, default="USDT")
    kyc_verified = Column(Boolean, default=False)
    status = Column(String, default="pending")  # pending, confirmed, refunded
    transaction_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class TokenVestingDB(Base):
    __tablename__ = "token_vesting"
    
    id = Column(String, primary_key=True)
    participation_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    project_id = Column(String, nullable=False)
    total_tokens = Column(Float, nullable=False)
    claimed_tokens = Column(Float, default=0.0)
    next_unlock_date = Column(DateTime, nullable=True)
    next_unlock_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models
class ProjectStatus(str, Enum):
    UPCOMING = "upcoming"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class LaunchpadProjectCreate(BaseModel):
    name: str
    symbol: str
    description: str
    website: Optional[str] = None
    whitepaper: Optional[str] = None
    total_supply: float = Field(gt=0)
    sale_supply: float = Field(gt=0)
    token_price: float = Field(gt=0)
    hard_cap: float = Field(gt=0)
    soft_cap: float = Field(gt=0)
    min_allocation: float = Field(ge=0)
    max_allocation: Optional[float] = None
    start_date: datetime
    end_date: datetime
    vesting_schedule: Optional[str] = None
    kyc_required: bool = True

class LaunchpadProjectResponse(BaseModel):
    id: str
    name: str
    symbol: str
    description: str
    website: Optional[str]
    whitepaper: Optional[str]
    total_supply: float
    sale_supply: float
    token_price: float
    hard_cap: float
    soft_cap: float
    min_allocation: float
    max_allocation: Optional[float]
    start_date: datetime
    end_date: datetime
    vesting_schedule: Optional[str]
    status: str
    total_raised: float
    participants_count: int
    kyc_required: bool
    progress_percentage: float
    created_at: datetime

class ParticipateRequest(BaseModel):
    project_id: str
    amount: float = Field(gt=0)
    payment_currency: str = "USDT"

class ParticipationResponse(BaseModel):
    id: str
    project_id: str
    user_id: str
    amount_invested: float
    tokens_allocated: float
    payment_currency: str
    kyc_verified: bool
    status: str
    created_at: datetime

class VestingResponse(BaseModel):
    id: str
    participation_id: str
    user_id: str
    project_id: str
    total_tokens: float
    claimed_tokens: float
    remaining_tokens: float
    next_unlock_date: Optional[datetime]
    next_unlock_amount: float

# API Endpoints
@app.post("/projects", response_model=LaunchpadProjectResponse)
async def create_project(project: LaunchpadProjectCreate, db: Session = Depends(get_db)):
    """Create a launchpad project"""
    project_id = str(uuid.uuid4())
    
    # Determine initial status based on dates
    now = datetime.utcnow()
    if now < project.start_date:
        status = "upcoming"
    elif now >= project.start_date and now <= project.end_date:
        status = "active"
    else:
        status = "completed"
    
    db_project = LaunchpadProjectDB(
        id=project_id,
        name=project.name,
        symbol=project.symbol,
        description=project.description,
        website=project.website,
        whitepaper=project.whitepaper,
        total_supply=project.total_supply,
        sale_supply=project.sale_supply,
        token_price=project.token_price,
        hard_cap=project.hard_cap,
        soft_cap=project.soft_cap,
        min_allocation=project.min_allocation,
        max_allocation=project.max_allocation,
        start_date=project.start_date,
        end_date=project.end_date,
        vesting_schedule=project.vesting_schedule,
        status=status,
        kyc_required=project.kyc_required,
        created_at=datetime.utcnow()
    )
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    progress = (db_project.total_raised / db_project.hard_cap * 100) if db_project.hard_cap > 0 else 0
    
    return LaunchpadProjectResponse(
        id=db_project.id,
        name=db_project.name,
        symbol=db_project.symbol,
        description=db_project.description,
        website=db_project.website,
        whitepaper=db_project.whitepaper,
        total_supply=db_project.total_supply,
        sale_supply=db_project.sale_supply,
        token_price=db_project.token_price,
        hard_cap=db_project.hard_cap,
        soft_cap=db_project.soft_cap,
        min_allocation=db_project.min_allocation,
        max_allocation=db_project.max_allocation,
        start_date=db_project.start_date,
        end_date=db_project.end_date,
        vesting_schedule=db_project.vesting_schedule,
        status=db_project.status,
        total_raised=db_project.total_raised,
        participants_count=db_project.participants_count,
        kyc_required=db_project.kyc_required,
        progress_percentage=progress,
        created_at=db_project.created_at
    )

@app.get("/projects", response_model=List[LaunchpadProjectResponse])
async def list_projects(status: Optional[str] = None, db: Session = Depends(get_db)):
    """List all launchpad projects"""
    query = db.query(LaunchpadProjectDB)
    
    if status:
        query = query.filter(LaunchpadProjectDB.status == status)
    
    projects = query.order_by(LaunchpadProjectDB.start_date.desc()).all()
    
    return [LaunchpadProjectResponse(
        id=p.id,
        name=p.name,
        symbol=p.symbol,
        description=p.description,
        website=p.website,
        whitepaper=p.whitepaper,
        total_supply=p.total_supply,
        sale_supply=p.sale_supply,
        token_price=p.token_price,
        hard_cap=p.hard_cap,
        soft_cap=p.soft_cap,
        min_allocation=p.min_allocation,
        max_allocation=p.max_allocation,
        start_date=p.start_date,
        end_date=p.end_date,
        vesting_schedule=p.vesting_schedule,
        status=p.status,
        total_raised=p.total_raised,
        participants_count=p.participants_count,
        kyc_required=p.kyc_required,
        progress_percentage=(p.total_raised / p.hard_cap * 100) if p.hard_cap > 0 else 0,
        created_at=p.created_at
    ) for p in projects]

@app.get("/projects/{project_id}", response_model=LaunchpadProjectResponse)
async def get_project(project_id: str, db: Session = Depends(get_db)):
    """Get project details"""
    project = db.query(LaunchpadProjectDB).filter(LaunchpadProjectDB.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    progress = (project.total_raised / project.hard_cap * 100) if project.hard_cap > 0 else 0
    
    return LaunchpadProjectResponse(
        id=project.id,
        name=project.name,
        symbol=project.symbol,
        description=project.description,
        website=project.website,
        whitepaper=project.whitepaper,
        total_supply=project.total_supply,
        sale_supply=project.sale_supply,
        token_price=project.token_price,
        hard_cap=project.hard_cap,
        soft_cap=project.soft_cap,
        min_allocation=project.min_allocation,
        max_allocation=project.max_allocation,
        start_date=project.start_date,
        end_date=project.end_date,
        vesting_schedule=project.vesting_schedule,
        status=project.status,
        total_raised=project.total_raised,
        participants_count=project.participants_count,
        kyc_required=project.kyc_required,
        progress_percentage=progress,
        created_at=project.created_at
    )

@app.post("/participate", response_model=ParticipationResponse)
async def participate(request: ParticipateRequest, user_id: str = "user123", db: Session = Depends(get_db)):
    """Participate in a launchpad project"""
    project = db.query(LaunchpadProjectDB).filter(LaunchpadProjectDB.id == request.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.status != "active":
        raise HTTPException(status_code=400, detail="Project is not active")
    
    now = datetime.utcnow()
    if now < project.start_date or now > project.end_date:
        raise HTTPException(status_code=400, detail="Project sale period has ended")
    
    if request.amount < project.min_allocation:
        raise HTTPException(status_code=400, detail=f"Minimum allocation is {project.min_allocation}")
    
    if project.max_allocation and request.amount > project.max_allocation:
        raise HTTPException(status_code=400, detail=f"Maximum allocation is {project.max_allocation}")
    
    if project.total_raised + request.amount > project.hard_cap:
        raise HTTPException(status_code=400, detail="Hard cap reached")
    
    # Calculate tokens allocated
    tokens_allocated = request.amount / project.token_price
    
    participation_id = str(uuid.uuid4())
    participation = LaunchpadParticipationDB(
        id=participation_id,
        project_id=request.project_id,
        user_id=user_id,
        amount_invested=request.amount,
        tokens_allocated=tokens_allocated,
        payment_currency=request.payment_currency,
        kyc_verified=not project.kyc_required,  # Auto-verify if KYC not required
        status="confirmed",
        created_at=datetime.utcnow()
    )
    
    db.add(participation)
    
    # Update project stats
    project.total_raised += request.amount
    project.participants_count += 1
    
    # Create vesting schedule
    vesting_id = str(uuid.uuid4())
    vesting = TokenVestingDB(
        id=vesting_id,
        participation_id=participation_id,
        user_id=user_id,
        project_id=request.project_id,
        total_tokens=tokens_allocated,
        next_unlock_date=project.end_date + timedelta(days=30),  # First unlock after 30 days
        next_unlock_amount=tokens_allocated * 0.25,  # 25% unlock
        created_at=datetime.utcnow()
    )
    
    db.add(vesting)
    db.commit()
    db.refresh(participation)
    
    return ParticipationResponse(
        id=participation.id,
        project_id=participation.project_id,
        user_id=participation.user_id,
        amount_invested=participation.amount_invested,
        tokens_allocated=participation.tokens_allocated,
        payment_currency=participation.payment_currency,
        kyc_verified=participation.kyc_verified,
        status=participation.status,
        created_at=participation.created_at
    )

@app.get("/participations", response_model=List[ParticipationResponse])
async def list_participations(user_id: str = "user123", db: Session = Depends(get_db)):
    """List user participations"""
    participations = db.query(LaunchpadParticipationDB).filter(
        LaunchpadParticipationDB.user_id == user_id
    ).all()
    
    return [ParticipationResponse(
        id=p.id,
        project_id=p.project_id,
        user_id=p.user_id,
        amount_invested=p.amount_invested,
        tokens_allocated=p.tokens_allocated,
        payment_currency=p.payment_currency,
        kyc_verified=p.kyc_verified,
        status=p.status,
        created_at=p.created_at
    ) for p in participations]

@app.get("/vesting", response_model=List[VestingResponse])
async def list_vesting(user_id: str = "user123", db: Session = Depends(get_db)):
    """List user vesting schedules"""
    vestings = db.query(TokenVestingDB).filter(TokenVestingDB.user_id == user_id).all()
    
    return [VestingResponse(
        id=v.id,
        participation_id=v.participation_id,
        user_id=v.user_id,
        project_id=v.project_id,
        total_tokens=v.total_tokens,
        claimed_tokens=v.claimed_tokens,
        remaining_tokens=v.total_tokens - v.claimed_tokens,
        next_unlock_date=v.next_unlock_date,
        next_unlock_amount=v.next_unlock_amount
    ) for v in vestings]

@app.post("/vesting/{vesting_id}/claim")
async def claim_tokens(vesting_id: str, user_id: str = "user123", db: Session = Depends(get_db)):
    """Claim vested tokens"""
    vesting = db.query(TokenVestingDB).filter(
        TokenVestingDB.id == vesting_id,
        TokenVestingDB.user_id == user_id
    ).first()
    
    if not vesting:
        raise HTTPException(status_code=404, detail="Vesting not found")
    
    if not vesting.next_unlock_date or datetime.utcnow() < vesting.next_unlock_date:
        raise HTTPException(status_code=400, detail="Tokens not yet unlocked")
    
    # Claim tokens
    vesting.claimed_tokens += vesting.next_unlock_amount
    
    # Update next unlock (example: 25% every 30 days)
    remaining = vesting.total_tokens - vesting.claimed_tokens
    if remaining > 0:
        vesting.next_unlock_date = vesting.next_unlock_date + timedelta(days=30)
        vesting.next_unlock_amount = min(remaining, vesting.total_tokens * 0.25)
    else:
        vesting.next_unlock_date = None
        vesting.next_unlock_amount = 0
    
    db.commit()
    
    return {
        "message": "Tokens claimed successfully",
        "amount": vesting.next_unlock_amount,
        "remaining": remaining
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "launchpad"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)