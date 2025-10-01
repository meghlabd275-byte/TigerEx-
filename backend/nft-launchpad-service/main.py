"""
NFT Launchpad Service - TigerEx Exchange
Port: 8057

Provides NFT launchpad functionality:
- Project listings
- Whitelist management
- Minting system
- Royalty distribution
- Secondary market integration
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
import json
import redis
import logging
from datetime import datetime, timedelta
import aiohttp
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uvicorn
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "postgresql://user:password@localhost:5432/tigerex_nft_launchpad"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# FastAPI app
app = FastAPI(title="NFT Launchpad Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Models
class NFTProject(Base):
    __tablename__ = "nft_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, index=True)
    description = Column(Text)
    creator_address = Column(String, index=True)
    collection_address = Column(String, unique=True, index=True)
    total_supply = Column(Integer)
    mint_price = Column(Numeric(20, 8))
    max_mint_per_wallet = Column(Integer, default=5)
    launch_date = Column(DateTime)
    whitelist_start = Column(DateTime)
    public_sale_start = Column(DateTime)
    status = Column(String, default="upcoming")  # upcoming, whitelist, public, sold_out, ended
    metadata_uri = Column(String)
    image_uri = Column(String)
    royalty_percentage = Column(Float, default=5.0)
    is_featured = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    social_links = Column(JSON)
    team_info = Column(JSON)
    roadmap = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WhitelistEntry(Base):
    __tablename__ = "whitelist_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, index=True)
    wallet_address = Column(String, index=True)
    allocation = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    minted_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class NFTMint(Base):
    __tablename__ = "nft_mints"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, index=True)
    token_id = Column(Integer, index=True)
    minter_address = Column(String, index=True)
    mint_price = Column(Numeric(20, 8))
    transaction_hash = Column(String, unique=True)
    metadata_uri = Column(String)
    mint_time = Column(DateTime, default=datetime.utcnow)

class NFTRoyalty(Base):
    __tablename__ = "nft_royalties"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, index=True)
    token_id = Column(Integer, index=True)
    seller_address = Column(String, index=True)
    buyer_address = Column(String, index=True)
    sale_price = Column(Numeric(20, 8))
    royalty_amount = Column(Numeric(20, 8))
    creator_address = Column(String, index=True)
    transaction_hash = Column(String)
    sale_time = Column(DateTime, default=datetime.utcnow)

class LaunchpadApplication(Base):
    __tablename__ = "launchpad_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String)
    creator_name = Column(String)
    email = Column(String)
    wallet_address = Column(String)
    project_description = Column(Text)
    team_size = Column(Integer)
    previous_projects = Column(JSON)
    social_media = Column(JSON)
    website = Column(String)
    whitepaper = Column(String)
    roadmap = Column(JSON)
    funding_goal = Column(Numeric(20, 8))
    status = Column(String, default="pending")  # pending, approved, rejected
    review_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)

# Pydantic Models
class NFTProjectCreate(BaseModel):
    project_name: str
    description: str
    creator_address: str
    total_supply: int = Field(..., ge=1, le=10000)
    mint_price: Decimal = Field(..., gt=Decimal('0'))
    max_mint_per_wallet: int = Field(..., ge=1, le=50)
    launch_date: datetime
    whitelist_start: Optional[datetime] = None
    public_sale_start: Optional[datetime] = None
    royalty_percentage: float = Field(..., ge=0, le=20)
    metadata_uri: str
    image_uri: str
    social_links: Optional[Dict[str, str]] = {}
    team_info: Optional[Dict[str, Any]] = {}
    roadmap: Optional[List[Dict[str, Any]]] = []

class WhitelistAdd(BaseModel):
    wallet_address: str
    allocation: int = Field(..., ge=1, le=10)

class MintRequest(BaseModel):
    project_id: int
    wallet_address: str
    quantity: int = Field(..., ge=1, le=5)
    mint_price: Decimal

class RoyaltyPayment(BaseModel):
    project_id: int
    token_id: int
    seller_address: str
    buyer_address: str
    sale_price: Decimal
    transaction_hash: str

class LaunchpadApplicationCreate(BaseModel):
    project_name: str
    creator_name: str
    email: str
    wallet_address: str
    project_description: str
    team_size: int = Field(..., ge=1)
    previous_projects: Optional[List[str]] = []
    social_media: Optional[Dict[str, str]] = {}
    website: Optional[str] = None
    whitepaper: Optional[str] = None
    roadmap: Optional[List[Dict[str, Any]]] = []
    funding_goal: Decimal = Field(..., gt=Decimal('0'))

# Database initialization
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions
async def deploy_nft_contract(
    project_name: str,
    symbol: str,
    total_supply: int,
    royalty_percentage: float,
    creator_address: str
) -> Dict[str, Any]:
    """Deploy NFT smart contract"""
    try:
        # In production, interact with actual blockchain
        contract_address = f"0x{hash(project_name) % (16**40):040x}"
        
        return {
            "success": True,
            "contract_address": contract_address,
            "transaction_hash": f"0x{hash(contract_address) % (16**64):064x}",
            "gas_used": 2500000,
            "gas_price": 20000000000
        }
    except Exception as e:
        logger.error(f"Error deploying NFT contract: {e}")
        return {"success": False, "error": str(e)}

async def mint_nft_token(
    contract_address: str,
    to_address: str,
    token_id: int,
    metadata_uri: str,
    mint_price: Decimal
) -> Dict[str, Any]:
    """Mint NFT token"""
    try:
        # In production, interact with actual contract
        transaction_hash = f"0x{hash(f'{contract_address}{to_address}{token_id}') % (16**64):064x}"
        
        return {
            "success": True,
            "transaction_hash": transaction_hash,
            "token_id": token_id,
            "gas_used": 150000,
            "gas_price": 20000000000
        }
    except Exception as e:
        logger.error(f"Error minting NFT: {e}")
        return {"success": False, "error": str(e)}

async def calculate_royalty(
    sale_price: Decimal,
    royalty_percentage: float
) -> Decimal:
    """Calculate royalty amount"""
    return sale_price * Decimal(str(royalty_percentage / 100))

async def get_current_gas_price() -> int:
    """Get current gas price"""
    try:
        # Mock gas price - in production use actual blockchain data
        return 20000000000  # 20 gwei
    except Exception as e:
        logger.error(f"Error getting gas price: {e}")
        return 20000000000

# API Endpoints
@app.post("/api/v1/projects", response_model=Dict[str, Any])
async def create_nft_project(
    project: NFTProjectCreate,
    db: Session = Depends(get_db)
):
    """Create a new NFT project"""
    try:
        # Deploy NFT contract
        deploy_result = await deploy_nft_contract(
            project.project_name,
            project.project_name[:3].upper(),
            project.total_supply,
            project.royalty_percentage,
            project.creator_address
        )
        
        if not deploy_result["success"]:
            raise HTTPException(status_code=500, detail="Failed to deploy NFT contract")
        
        # Create project record
        db_project = NFTProject(
            project_name=project.project_name,
            description=project.description,
            creator_address=project.creator_address,
            collection_address=deploy_result["contract_address"],
            total_supply=project.total_supply,
            mint_price=project.mint_price,
            max_mint_per_wallet=project.max_mint_per_wallet,
            launch_date=project.launch_date,
            whitelist_start=project.whitelist_start,
            public_sale_start=project.public_sale_start,
            royalty_percentage=project.royalty_percentage,
            metadata_uri=project.metadata_uri,
            image_uri=project.image_uri,
            social_links=project.social_links or {},
            team_info=project.team_info or {},
            roadmap=project.roadmap or []
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        
        return {
            "success": True,
            "project_id": db_project.id,
            "contract_address": deploy_result["contract_address"],
            "transaction_hash": deploy_result["transaction_hash"]
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/projects")
async def get_nft_projects(
    status: Optional[str] = None,
    featured: Optional[bool] = None,
    verified: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get NFT projects with filtering"""
    query = db.query(NFTProject)
    
    if status:
        query = query.filter(NFTProject.status == status)
    if featured is not None:
        query = query.filter(NFTProject.is_featured == featured)
    if verified is not None:
        query = query.filter(NFTProject.is_verified == verified)
    
    projects = query.order_by(NFTProject.created_at.desc()).all()
    
    return {
        "projects": [
            {
                "id": p.id,
                "project_name": p.project_name,
                "description": p.description,
                "creator_address": p.creator_address,
                "collection_address": p.collection_address,
                "total_supply": p.total_supply,
                "mint_price": str(p.mint_price),
                "max_mint_per_wallet": p.max_mint_per_wallet,
                "launch_date": p.launch_date.isoformat(),
                "status": p.status,
                "metadata_uri": p.metadata_uri,
                "image_uri": p.image_uri,
                "royalty_percentage": p.royalty_percentage,
                "is_featured": p.is_featured,
                "is_verified": p.is_verified,
                "social_links": p.social_links,
                "team_info": p.team_info,
                "roadmap": p.roadmap
            }
            for p in projects
        ]
    }

@app.post("/api/v1/projects/{project_id}/whitelist", response_model=Dict[str, Any])
async def add_to_whitelist(
    project_id: int,
    whitelist: WhitelistAdd,
    db: Session = Depends(get_db)
):
    """Add wallet to whitelist"""
    try:
        # Check if project exists
        project = db.query(NFTProject).filter(NFTProject.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check if wallet already whitelisted
        existing = db.query(WhitelistEntry).filter(
            WhitelistEntry.project_id == project_id,
            WhitelistEntry.wallet_address == whitelist.wallet_address
        ).first()
        
        if existing:
            return {"success": False, "message": "Wallet already whitelisted"}
        
        # Add to whitelist
        whitelist_entry = WhitelistEntry(
            project_id=project_id,
            wallet_address=whitelist.wallet_address,
            allocation=whitelist.allocation
        )
        db.add(whitelist_entry)
        db.commit()
        
        return {
            "success": True,
            "message": "Added to whitelist successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/projects/{project_id}/whitelist/{wallet_address}")
async def check_whitelist(
    project_id: int,
    wallet_address: str,
    db: Session = Depends(get_db)
):
    """Check if wallet is whitelisted"""
    whitelist_entry = db.query(WhitelistEntry).filter(
        WhitelistEntry.project_id == project_id,
        WhitelistEntry.wallet_address == wallet_address,
        WhitelistEntry.is_active == True
    ).first()
    
    if whitelist_entry:
        return {
            "whitelisted": True,
            "allocation": whitelist_entry.allocation,
            "minted_count": whitelist_entry.minted_count
        }
    else:
        return {
            "whitelisted": False,
            "allocation": 0,
            "minted_count": 0
        }

@app.post("/api/v1/mint", response_model=Dict[str, Any])
async def mint_nft(
    mint_request: MintRequest,
    db: Session = Depends(get_db)
):
    """Mint NFT tokens"""
    try:
        # Check project exists
        project = db.query(NFTProject).filter(NFTProject.id == mint_request.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check minting phase
        now = datetime.utcnow()
        if project.status == "upcoming":
            raise HTTPException(status_code=400, detail="Project not launched yet")
        
        # Check whitelist phase
        if project.whitelist_start and now < project.public_sale_start:
            # Check if user is whitelisted
            whitelist_entry = db.query(WhitelistEntry).filter(
                WhitelistEntry.project_id == mint_request.project_id,
                WhitelistEntry.wallet_address == mint_request.wallet_address,
                WhitelistEntry.is_active == True
            ).first()
            
            if not whitelist_entry:
                raise HTTPException(status_code=403, detail="Not whitelisted for this project")
            
            # Check allocation
            if whitelist_entry.minted_count + mint_request.quantity > whitelist_entry.allocation:
                raise HTTPException(status_code=400, detail="Exceeds whitelist allocation")
        
        # Check max mint per wallet
        user_mint_count = db.query(NFTMint).filter(
            NFTMint.project_id == mint_request.project_id,
            NFTMint.minter_address == mint_request.wallet_address
        ).count()
        
        if user_mint_count + mint_request.quantity > project.max_mint_per_wallet:
            raise HTTPException(status_code=400, detail="Exceeds max mint per wallet")
        
        # Check total supply
        total_minted = db.query(NFTMint).filter(
            NFTMint.project_id == mint_request.project_id
        ).count()
        
        if total_minted + mint_request.quantity > project.total_supply:
            raise HTTPException(status_code=400, detail="Exceeds total supply")
        
        # Mint tokens
        minted_tokens = []
        for i in range(mint_request.quantity):
            token_id = total_minted + i + 1
            
            # Mint NFT
            mint_result = await mint_nft_token(
                project.collection_address,
                mint_request.wallet_address,
                token_id,
                f"{project.metadata_uri}/{token_id}",
                mint_request.mint_price
            )
            
            if mint_result["success"]:
                # Record mint
                nft_mint = NFTMint(
                    project_id=mint_request.project_id,
                    token_id=token_id,
                    minter_address=mint_request.wallet_address,
                    mint_price=mint_request.mint_price,
                    transaction_hash=mint_result["transaction_hash"],
                    metadata_uri=f"{project.metadata_uri}/{token_id}"
                )
                db.add(nft_mint)
                minted_tokens.append(token_id)
                
                # Update whitelist entry if exists
                if whitelist_entry:
                    whitelist_entry.minted_count += 1
        
        # Update project status if sold out
        if total_minted + mint_request.quantity >= project.total_supply:
            project.status = "sold_out"
        
        db.commit()
        
        return {
            "success": True,
            "minted_tokens": minted_tokens,
            "transaction_hashes": [f"0x{hash(str(token_id)) % (16**64):064x}" for token_id in minted_tokens]
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/royalty", response_model=Dict[str, Any])
async def process_royalty_payment(
    royalty: RoyaltyPayment,
    db: Session = Depends(get_db)
):
    """Process NFT royalty payment"""
    try:
        # Get project details
        project = db.query(NFTProject).filter(NFTProject.id == royalty.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Calculate royalty
        royalty_amount = await calculate_royalty(
            royalty.sale_price,
            project.royalty_percentage
        )
        
        # Record royalty payment
        royalty_payment = NFTRoyalty(
            project_id=royalty.project_id,
            token_id=royalty.token_id,
            seller_address=royalty.seller_address,
            buyer_address=royalty.buyer_address,
            sale_price=royalty.sale_price,
            royalty_amount=royalty_amount,
            creator_address=project.creator_address,
            transaction_hash=royalty.transaction_hash
        )
        db.add(royalty_payment)
        db.commit()
        
        return {
            "success": True,
            "royalty_amount": str(royalty_amount),
            "creator_address": project.creator_address,
            "royalty_percentage": project.royalty_percentage
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/applications", response_model=Dict[str, Any])
async def submit_launchpad_application(
    application: LaunchpadApplicationCreate,
    db: Session = Depends(get_db)
):
    """Submit launchpad application"""
    try:
        db_application = LaunchpadApplication(
            project_name=application.project_name,
            creator_name=application.creator_name,
            email=application.email,
            wallet_address=application.wallet_address,
            project_description=application.project_description,
            team_size=application.team_size,
            previous_projects=application.previous_projects or [],
            social_media=application.social_media or {},
            website=application.website,
            whitepaper=application.whitepaper,
            roadmap=application.roadmap or [],
            funding_goal=application.funding_goal
        )
        db.add(db_application)
        db.commit()
        db.refresh(db_application)
        
        return {
            "success": True,
            "application_id": db_application.id,
            "message": "Application submitted successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/applications")
async def get_launchpad_applications(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get launchpad applications"""
    query = db.query(LaunchpadApplication)
    
    if status:
        query = query.filter(LaunchpadApplication.status == status)
    
    applications = query.order_by(LaunchpadApplication.created_at.desc()).all()
    
    return {
        "applications": [
            {
                "id": a.id,
                "project_name": a.project_name,
                "creator_name": a.creator_name,
                "email": a.email,
                "wallet_address": a.wallet_address,
                "status": a.status,
                "team_size": a.team_size,
                "funding_goal": str(a.funding_goal),
                "created_at": a.created_at.isoformat(),
                "reviewed_at": a.reviewed_at.isoformat() if a.reviewed_at else None
            }
            for a in applications
        ]
    }

@app.get("/api/v1/stats")
async def get_launchpad_stats(db: Session = Depends(get_db)):
    """Get launchpad statistics"""
    try:
        total_projects = db.query(NFTProject).count()
        active_projects = db.query(NFTProject).filter(
            NFTProject.status.in_(["whitelist", "public"])
        ).count()
        
        total_mints = db.query(NFTMint).count()
        total_volume = db.query(
            db.query(NFTMint).with_entities(
                db.func.sum(NFTMint.mint_price)
            ).scalar()
        ).scalar() or Decimal('0')
        
        total_applications = db.query(LaunchpadApplication).count()
        pending_applications = db.query(LaunchpadApplication).filter(
            LaunchpadApplication.status == "pending"
        ).count()
        
        return {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "total_mints": total_mints,
            "total_volume": str(total_volume),
            "total_applications": total_applications,
            "pending_applications": pending_applications
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    asyncio.create_task(project_status_updater())
    asyncio.create_task(royalty_distributor())

async def project_status_updater():
    """Background task to update project statuses"""
    while True:
        try:
            db = SessionLocal()
            now = datetime.utcnow()
            
            # Update project statuses based on time
            projects = db.query(NFTProject).all()
            
            for project in projects:
                if project.status == "upcoming" and project.whitelist_start and now >= project.whitelist_start:
                    project.status = "whitelist"
                elif project.status == "whitelist" and project.public_sale_start and now >= project.public_sale_start:
                    project.status = "public"
                elif project.status == "public" and project.launch_date and now >= project.launch_date + timedelta(days=30):
                    project.status = "ended"
            
            db.commit()
            db.close()
            await asyncio.sleep(3600)  # Check every hour
            
        except Exception as e:
            logger.error(f"Error in project status updater: {e}")
            await asyncio.sleep(3600)

async def royalty_distributor():
    """Background task to distribute royalties"""
    while True:
        try:
            db = SessionLocal()
            
            # Get unpaid royalties
            unpaid_royalties = db.query(NFTRoyalty).filter(
                NFTRoyalty.id.notin_(
                    db.query(NFTRoyalty.id).filter(
                        # Add condition for unpaid royalties
                    )
                )
            ).all()
            
            # In production, implement actual royalty distribution logic
            # For now, just log the royalties
            
            db.close()
            await asyncio.sleep(86400)  # Daily
            
        except Exception as e:
            logger.error(f"Error in royalty distributor: {e}")
            await asyncio.sleep(3600)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "nft-launchpad-service",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8057)