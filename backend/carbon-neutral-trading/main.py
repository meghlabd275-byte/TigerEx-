#!/usr/bin/env python3
"""
Carbon-Neutral Trading Initiative Service
Environmental sustainability features for carbon-neutral cryptocurrency trading
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

# FastAPI app
app = FastAPI(
    title="TigerEx Carbon-Neutral Trading",
    description="Environmental sustainability features for carbon-neutral cryptocurrency trading",
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
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/tigerex_carbon")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carbon footprint data for different cryptocurrencies (kg CO2 per transaction)
CRYPTO_CARBON_FOOTPRINT = {
    "BTC": 707.0,  # Bitcoin
    "ETH": 62.56,  # Ethereum (post-merge)
    "ADA": 0.0051,  # Cardano
    "DOT": 0.0085,  # Polkadot
    "ALGO": 0.0000004,  # Algorand
    "XRP": 0.0079,  # Ripple
    "SOL": 0.00051,  # Solana
    "AVAX": 0.0005,  # Avalanche
    "MATIC": 0.00079,  # Polygon
    "BNB": 2.3,  # Binance Coin
    "USDT": 62.56,  # Tether (Ethereum-based)
    "USDC": 62.56,  # USD Coin (Ethereum-based)
}

# Database Models
class CarbonFootprint(Base):
    __tablename__ = "carbon_footprints"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    
    # Transaction details
    transaction_id = Column(String, nullable=False)
    transaction_type = Column(String, nullable=False)  # trade, transfer, stake, etc.
    
    # Asset information
    symbol = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    
    # Carbon calculation
    carbon_footprint_kg = Column(Float, nullable=False)
    calculation_method = Column(String, default="standard")
    
    # Offset information
    is_offset = Column(Boolean, default=False)
    offset_method = Column(String)  # renewable_energy, carbon_credits, tree_planting
    offset_cost = Column(Float, default=0.0)
    offset_provider = Column(String)
    
    # Blockchain details
    blockchain = Column(String, nullable=False)
    consensus_mechanism = Column(String)  # pow, pos, dpos, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)

class CarbonOffset(Base):
    __tablename__ = "carbon_offsets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    
    # Offset details
    offset_type = Column(String, nullable=False)  # renewable_energy, reforestation, carbon_capture
    amount_kg_co2 = Column(Float, nullable=False)
    cost_usd = Column(Float, nullable=False)
    
    # Provider information
    provider_name = Column(String, nullable=False)
    provider_certification = Column(String)  # VCS, Gold_Standard, etc.
    project_id = Column(String)
    project_location = Column(String)
    
    # Verification
    certificate_id = Column(String)
    verification_status = Column(String, default="pending")  # pending, verified, rejected
    verified_at = Column(DateTime)
    
    # Impact tracking
    trees_planted = Column(Integer, default=0)
    renewable_energy_kwh = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

class GreenAsset(Base):
    __tablename__ = "green_assets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Asset details
    symbol = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    blockchain = Column(String, nullable=False)
    
    # Environmental metrics
    carbon_footprint_per_tx = Column(Float, nullable=False)  # kg CO2
    energy_consumption_kwh = Column(Float, default=0.0)
    renewable_energy_percentage = Column(Float, default=0.0)
    
    # Sustainability features
    is_carbon_neutral = Column(Boolean, default=False)
    sustainability_score = Column(Float, default=0.0)  # 0-100
    environmental_initiatives = Column(JSON, default=list)
    
    # Certifications
    certifications = Column(JSON, default=list)
    audit_reports = Column(JSON, default=list)
    
    # Market data
    green_premium = Column(Float, default=0.0)  # Premium for green trading
    
    last_updated = Column(DateTime, default=datetime.utcnow)

class SustainabilityGoal(Base):
    __tablename__ = "sustainability_goals"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    
    # Goal details
    goal_type = Column(String, nullable=False)  # carbon_neutral, net_negative, renewable_only
    target_date = Column(DateTime, nullable=False)
    
    # Targets
    carbon_reduction_target = Column(Float, default=0.0)  # kg CO2
    renewable_energy_target = Column(Float, default=100.0)  # percentage
    green_assets_target = Column(Float, default=50.0)  # percentage of portfolio
    
    # Progress tracking
    current_carbon_footprint = Column(Float, default=0.0)
    current_offsets = Column(Float, default=0.0)
    current_green_percentage = Column(Float, default=0.0)
    
    # Status
    status = Column(String, default="active")  # active, achieved, paused, cancelled
    progress_percentage = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EnvironmentalImpact(Base):
    __tablename__ = "environmental_impacts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    
    # Time period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Carbon metrics
    total_carbon_footprint = Column(Float, default=0.0)  # kg CO2
    total_offsets = Column(Float, default=0.0)  # kg CO2
    net_carbon_impact = Column(Float, default=0.0)  # kg CO2
    
    # Trading activity
    total_transactions = Column(Integer, default=0)
    green_transactions = Column(Integer, default=0)
    green_percentage = Column(Float, default=0.0)
    
    # Energy metrics
    estimated_energy_consumption = Column(Float, default=0.0)  # kWh
    renewable_energy_percentage = Column(Float, default=0.0)
    
    # Offset breakdown
    offset_breakdown = Column(JSON, default=dict)  # By offset type
    
    # Achievements
    achievements = Column(JSON, default=list)
    
    calculated_at = Column(DateTime, default=datetime.utcnow)

class CarbonCredit(Base):
    __tablename__ = "carbon_credits"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Credit details
    credit_type = Column(String, nullable=False)  # VCS, Gold_Standard, etc.
    project_name = Column(String, nullable=False)
    project_type = Column(String, nullable=False)  # forestry, renewable_energy, etc.
    
    # Location
    country = Column(String, nullable=False)
    region = Column(String)
    coordinates = Column(JSON)
    
    # Credit specifications
    vintage_year = Column(Integer, nullable=False)
    amount_tonnes_co2 = Column(Float, nullable=False)
    price_per_tonne = Column(Float, nullable=False)
    
    # Verification
    registry = Column(String, nullable=False)
    serial_number = Column(String, unique=True, nullable=False)
    verification_standard = Column(String, nullable=False)
    
    # Availability
    is_available = Column(Boolean, default=True)
    reserved_amount = Column(Float, default=0.0)
    sold_amount = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class CarbonFootprintCalculation(BaseModel):
    user_id: str
    transaction_id: str
    transaction_type: str
    symbol: str
    amount: float
    blockchain: str

class CarbonOffsetPurchase(BaseModel):
    user_id: str
    offset_type: str
    amount_kg_co2: float
    provider_name: str
    project_id: Optional[str] = None

class SustainabilityGoalCreate(BaseModel):
    user_id: str
    goal_type: str
    target_date: datetime
    carbon_reduction_target: float = 0.0
    renewable_energy_target: float = 100.0
    green_assets_target: float = 50.0

class GreenAssetCreate(BaseModel):
    symbol: str
    name: str
    blockchain: str
    carbon_footprint_per_tx: float
    renewable_energy_percentage: float = 0.0
    sustainability_score: float = 0.0
    environmental_initiatives: Optional[List[str]] = None

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

def calculate_transaction_carbon_footprint(symbol: str, amount: float, blockchain: str) -> float:
    """Calculate carbon footprint for a transaction"""
    base_footprint = CRYPTO_CARBON_FOOTPRINT.get(symbol, 1.0)  # Default 1kg CO2
    
    # Adjust for blockchain efficiency
    blockchain_multipliers = {
        "ethereum": 1.0,  # Post-merge Ethereum
        "bitcoin": 11.3,  # Bitcoin is much higher
        "cardano": 0.0001,
        "solana": 0.0001,
        "polygon": 0.0001,
        "avalanche": 0.0001,
        "algorand": 0.0000001
    }
    
    multiplier = blockchain_multipliers.get(blockchain.lower(), 1.0)
    
    # Transaction size doesn't significantly affect PoS chains
    if blockchain.lower() in ["ethereum", "cardano", "solana", "polygon"]:
        size_factor = 1.0
    else:
        # For PoW chains, larger transactions might use more energy
        size_factor = min(1.0 + (amount / 1000000), 2.0)
    
    total_footprint = base_footprint * multiplier * size_factor
    return total_footprint

def calculate_offset_cost(carbon_amount_kg: float, offset_type: str) -> float:
    """Calculate cost to offset carbon emissions"""
    # Cost per tonne CO2 by offset type
    offset_costs = {
        "renewable_energy": 15.0,  # $15 per tonne
        "reforestation": 25.0,  # $25 per tonne
        "carbon_capture": 100.0,  # $100 per tonne
        "verified_carbon_standard": 20.0,  # $20 per tonne
        "gold_standard": 30.0  # $30 per tonne
    }
    
    cost_per_tonne = offset_costs.get(offset_type, 25.0)
    carbon_tonnes = carbon_amount_kg / 1000
    
    return carbon_tonnes * cost_per_tonne

def assess_portfolio_sustainability(user_id: str, db: Session) -> Dict[str, Any]:
    """Assess portfolio sustainability metrics"""
    # Get user's recent transactions
    recent_footprints = db.query(CarbonFootprint).filter(
        CarbonFootprint.user_id == user_id,
        CarbonFootprint.created_at >= datetime.utcnow() - timedelta(days=30)
    ).all()
    
    if not recent_footprints:
        return {
            "total_footprint": 0.0,
            "green_percentage": 0.0,
            "sustainability_score": 100.0,
            "recommendations": []
        }
    
    # Calculate metrics
    total_footprint = sum(fp.carbon_footprint_kg for fp in recent_footprints)
    total_offsets = sum(fp.offset_cost for fp in recent_footprints if fp.is_offset)
    
    # Get green assets
    green_assets = db.query(GreenAsset).all()
    green_symbols = {asset.symbol for asset in green_assets if asset.sustainability_score > 70}
    
    green_transactions = [fp for fp in recent_footprints if fp.symbol in green_symbols]
    green_percentage = (len(green_transactions) / len(recent_footprints)) * 100
    
    # Calculate sustainability score
    offset_ratio = min(total_offsets / total_footprint, 1.0) if total_footprint > 0 else 1.0
    sustainability_score = (green_percentage * 0.6 + offset_ratio * 100 * 0.4)
    
    # Generate recommendations
    recommendations = []
    if green_percentage < 50:
        recommendations.append("Consider trading more eco-friendly cryptocurrencies")
    if offset_ratio < 0.5:
        recommendations.append("Increase carbon offset purchases to improve sustainability")
    if total_footprint > 1000:  # 1 tonne CO2
        recommendations.append("Your carbon footprint is high - consider reducing transaction frequency")
    
    return {
        "total_footprint": total_footprint,
        "total_offsets": total_offsets,
        "net_footprint": total_footprint - total_offsets,
        "green_percentage": green_percentage,
        "sustainability_score": sustainability_score,
        "recommendations": recommendations
    }

# API Routes

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "carbon-neutral-trading"}

@app.get("/carbon-footprint/crypto")
async def get_crypto_carbon_data():
    """Get carbon footprint data for cryptocurrencies"""
    return {
        "carbon_footprints": CRYPTO_CARBON_FOOTPRINT,
        "unit": "kg CO2 per transaction",
        "last_updated": "2024-10-17",
        "source": "Cambridge Centre for Alternative Finance"
    }

# Carbon footprint tracking
@app.post("/carbon-footprint/calculate")
async def calculate_carbon_footprint(
    calculation: CarbonFootprintCalculation,
    db: Session = Depends(get_db)
):
    """Calculate and record carbon footprint for transaction"""
    try:
        # Calculate footprint
        footprint_kg = calculate_transaction_carbon_footprint(
            calculation.symbol,
            calculation.amount,
            calculation.blockchain
        )
        
        # Create footprint record
        db_footprint = CarbonFootprint(
            user_id=calculation.user_id,
            transaction_id=calculation.transaction_id,
            transaction_type=calculation.transaction_type,
            symbol=calculation.symbol,
            amount=calculation.amount,
            carbon_footprint_kg=footprint_kg,
            blockchain=calculation.blockchain,
            consensus_mechanism="pos" if calculation.blockchain.lower() in ["ethereum", "cardano", "solana"] else "pow"
        )
        
        db.add(db_footprint)
        db.commit()
        db.refresh(db_footprint)
        
        # Calculate offset cost
        offset_options = {}
        for offset_type in ["renewable_energy", "reforestation", "carbon_capture"]:
            offset_options[offset_type] = calculate_offset_cost(footprint_kg, offset_type)
        
        return {
            "footprint": db_footprint,
            "carbon_footprint_kg": footprint_kg,
            "equivalent_metrics": {
                "trees_to_plant": int(footprint_kg / 21.77),  # Average tree absorbs 21.77kg CO2/year
                "km_driven": footprint_kg / 0.404,  # Average car emits 404g CO2/km
                "coal_burned_kg": footprint_kg / 2.86  # Coal emits 2.86kg CO2/kg
            },
            "offset_options": offset_options
        }
        
    except Exception as e:
        logger.error(f"Error calculating carbon footprint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/carbon-footprint/{user_id}")
async def get_user_carbon_footprint(
    user_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get user's carbon footprint history"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    footprints = db.query(CarbonFootprint).filter(
        CarbonFootprint.user_id == user_id,
        CarbonFootprint.created_at >= start_date
    ).all()
    
    # Calculate summary metrics
    total_footprint = sum(fp.carbon_footprint_kg for fp in footprints)
    total_transactions = len(footprints)
    avg_footprint_per_tx = total_footprint / total_transactions if total_transactions > 0 else 0
    
    # Breakdown by asset
    footprint_by_asset = {}
    for fp in footprints:
        if fp.symbol not in footprint_by_asset:
            footprint_by_asset[fp.symbol] = {"footprint": 0.0, "transactions": 0}
        footprint_by_asset[fp.symbol]["footprint"] += fp.carbon_footprint_kg
        footprint_by_asset[fp.symbol]["transactions"] += 1
    
    return {
        "period_days": days,
        "total_footprint_kg": total_footprint,
        "total_transactions": total_transactions,
        "avg_footprint_per_tx": avg_footprint_per_tx,
        "footprint_by_asset": footprint_by_asset,
        "footprints": footprints
    }

# Carbon offsetting
@app.post("/carbon-offset/purchase")
async def purchase_carbon_offset(
    offset_purchase: CarbonOffsetPurchase,
    db: Session = Depends(get_db)
):
    """Purchase carbon offset"""
    try:
        # Calculate cost
        cost = calculate_offset_cost(offset_purchase.amount_kg_co2, offset_purchase.offset_type)
        
        # Create offset record
        db_offset = CarbonOffset(
            user_id=offset_purchase.user_id,
            offset_type=offset_purchase.offset_type,
            amount_kg_co2=offset_purchase.amount_kg_co2,
            cost_usd=cost,
            provider_name=offset_purchase.provider_name,
            project_id=offset_purchase.project_id,
            certificate_id=f"CERT_{uuid.uuid4().hex[:12].upper()}",
            verification_status="verified",
            verified_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=365)
        )
        
        # Add impact metrics based on offset type
        if offset_purchase.offset_type == "reforestation":
            db_offset.trees_planted = int(offset_purchase.amount_kg_co2 / 21.77)
        elif offset_purchase.offset_type == "renewable_energy":
            db_offset.renewable_energy_kwh = offset_purchase.amount_kg_co2 / 0.5  # Rough conversion
        
        db.add(db_offset)
        db.commit()
        db.refresh(db_offset)
        
        # Update user's recent footprints as offset
        recent_footprints = db.query(CarbonFootprint).filter(
            CarbonFootprint.user_id == offset_purchase.user_id,
            CarbonFootprint.is_offset == False
        ).order_by(CarbonFootprint.created_at.desc()).all()
        
        remaining_offset = offset_purchase.amount_kg_co2
        for footprint in recent_footprints:
            if remaining_offset <= 0:
                break
            
            if footprint.carbon_footprint_kg <= remaining_offset:
                footprint.is_offset = True
                footprint.offset_method = offset_purchase.offset_type
                footprint.offset_cost = footprint.carbon_footprint_kg * (cost / offset_purchase.amount_kg_co2)
                footprint.offset_provider = offset_purchase.provider_name
                remaining_offset -= footprint.carbon_footprint_kg
        
        db.commit()
        
        return {
            "offset": db_offset,
            "cost": cost,
            "impact": {
                "trees_planted": db_offset.trees_planted,
                "renewable_energy_kwh": db_offset.renewable_energy_kwh,
                "co2_offset_kg": offset_purchase.amount_kg_co2
            }
        }
        
    except Exception as e:
        logger.error(f"Error purchasing carbon offset: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/carbon-offset/{user_id}")
async def get_user_carbon_offsets(
    user_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get user's carbon offsets"""
    offsets = db.query(CarbonOffset).filter(
        CarbonOffset.user_id == user_id
    ).order_by(CarbonOffset.created_at.desc()).limit(limit).all()
    
    # Calculate summary
    total_offset_kg = sum(offset.amount_kg_co2 for offset in offsets)
    total_cost = sum(offset.cost_usd for offset in offsets)
    total_trees_planted = sum(offset.trees_planted for offset in offsets)
    total_renewable_kwh = sum(offset.renewable_energy_kwh for offset in offsets)
    
    return {
        "offsets": offsets,
        "summary": {
            "total_offset_kg_co2": total_offset_kg,
            "total_cost_usd": total_cost,
            "total_trees_planted": total_trees_planted,
            "total_renewable_energy_kwh": total_renewable_kwh,
            "offset_transactions": len(offsets)
        }
    }

# Green assets
@app.post("/green-assets")
async def create_green_asset(asset: GreenAssetCreate, db: Session = Depends(get_db)):
    """Add green asset to database"""
    # Check if asset already exists
    existing = db.query(GreenAsset).filter(GreenAsset.symbol == asset.symbol).first()
    if existing:
        raise HTTPException(status_code=400, detail="Green asset already exists")
    
    db_asset = GreenAsset(
        **asset.dict(),
        is_carbon_neutral=asset.carbon_footprint_per_tx < 0.001,  # Less than 1g CO2
        environmental_initiatives=asset.environmental_initiatives or []
    )
    
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    
    return db_asset

@app.get("/green-assets")
async def get_green_assets(
    min_sustainability_score: float = 0.0,
    carbon_neutral_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get green/sustainable assets"""
    query = db.query(GreenAsset)
    
    if min_sustainability_score > 0:
        query = query.filter(GreenAsset.sustainability_score >= min_sustainability_score)
    
    if carbon_neutral_only:
        query = query.filter(GreenAsset.is_carbon_neutral == True)
    
    assets = query.order_by(GreenAsset.sustainability_score.desc()).all()
    return assets

@app.get("/green-assets/{symbol}")
async def get_green_asset(symbol: str, db: Session = Depends(get_db)):
    """Get green asset details"""
    asset = db.query(GreenAsset).filter(GreenAsset.symbol == symbol).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Green asset not found")
    
    return asset

# Sustainability goals
@app.post("/sustainability-goals")
async def create_sustainability_goal(
    goal: SustainabilityGoalCreate,
    db: Session = Depends(get_db)
):
    """Create sustainability goal"""
    db_goal = SustainabilityGoal(**goal.dict())
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    
    return db_goal

@app.get("/sustainability-goals/{user_id}")
async def get_user_sustainability_goals(user_id: str, db: Session = Depends(get_db)):
    """Get user's sustainability goals"""
    goals = db.query(SustainabilityGoal).filter(
        SustainabilityGoal.user_id == user_id,
        SustainabilityGoal.status == "active"
    ).all()
    
    # Update progress for each goal
    for goal in goals:
        # Calculate current progress
        portfolio_metrics = assess_portfolio_sustainability(user_id, db)
        
        goal.current_carbon_footprint = portfolio_metrics["total_footprint"]
        goal.current_green_percentage = portfolio_metrics["green_percentage"]
        
        # Calculate progress percentage
        if goal.goal_type == "carbon_neutral":
            goal.progress_percentage = min(100, (goal.current_offsets / goal.current_carbon_footprint) * 100) if goal.current_carbon_footprint > 0 else 100
        elif goal.goal_type == "renewable_only":
            goal.progress_percentage = goal.current_green_percentage
        
        # Check if goal is achieved
        if goal.progress_percentage >= 100:
            goal.status = "achieved"
    
    db.commit()
    return goals

# Environmental impact reporting
@app.get("/environmental-impact/{user_id}")
async def get_environmental_impact(
    user_id: str,
    period_days: int = 30,
    db: Session = Depends(get_db)
):
    """Get user's environmental impact report"""
    period_start = datetime.utcnow() - timedelta(days=period_days)
    period_end = datetime.utcnow()
    
    # Get footprints for period
    footprints = db.query(CarbonFootprint).filter(
        CarbonFootprint.user_id == user_id,
        CarbonFootprint.created_at >= period_start
    ).all()
    
    # Get offsets for period
    offsets = db.query(CarbonOffset).filter(
        CarbonOffset.user_id == user_id,
        CarbonOffset.created_at >= period_start
    ).all()
    
    # Calculate metrics
    total_footprint = sum(fp.carbon_footprint_kg for fp in footprints)
    total_offsets = sum(offset.amount_kg_co2 for offset in offsets)
    net_impact = total_footprint - total_offsets
    
    # Green transaction analysis
    green_assets = db.query(GreenAsset).all()
    green_symbols = {asset.symbol for asset in green_assets if asset.sustainability_score > 70}
    
    green_transactions = [fp for fp in footprints if fp.symbol in green_symbols]
    green_percentage = (len(green_transactions) / len(footprints)) * 100 if footprints else 0
    
    # Offset breakdown
    offset_breakdown = {}
    for offset in offsets:
        if offset.offset_type not in offset_breakdown:
            offset_breakdown[offset.offset_type] = {"amount": 0.0, "cost": 0.0, "count": 0}
        offset_breakdown[offset.offset_type]["amount"] += offset.amount_kg_co2
        offset_breakdown[offset.offset_type]["cost"] += offset.cost_usd
        offset_breakdown[offset.offset_type]["count"] += 1
    
    # Generate achievements
    achievements = []
    if net_impact <= 0:
        achievements.append("Carbon Negative - Your trading has a net positive environmental impact!")
    elif total_offsets >= total_footprint * 0.5:
        achievements.append("Eco Warrior - You've offset over 50% of your carbon footprint")
    if green_percentage >= 80:
        achievements.append("Green Trader - 80%+ of your trades use eco-friendly cryptocurrencies")
    
    # Create impact record
    db_impact = EnvironmentalImpact(
        user_id=user_id,
        period_start=period_start,
        period_end=period_end,
        total_carbon_footprint=total_footprint,
        total_offsets=total_offsets,
        net_carbon_impact=net_impact,
        total_transactions=len(footprints),
        green_transactions=len(green_transactions),
        green_percentage=green_percentage,
        offset_breakdown=offset_breakdown,
        achievements=achievements
    )
    
    db.add(db_impact)
    db.commit()
    db.refresh(db_impact)
    
    return db_impact

# Carbon credits marketplace
@app.get("/carbon-credits")
async def get_available_carbon_credits(
    project_type: Optional[str] = None,
    country: Optional[str] = None,
    max_price: Optional[float] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get available carbon credits"""
    query = db.query(CarbonCredit).filter(CarbonCredit.is_available == True)
    
    if project_type:
        query = query.filter(CarbonCredit.project_type == project_type)
    if country:
        query = query.filter(CarbonCredit.country == country)
    if max_price:
        query = query.filter(CarbonCredit.price_per_tonne <= max_price)
    
    credits = query.order_by(CarbonCredit.price_per_tonne.asc()).limit(limit).all()
    return credits

@app.post("/carbon-credits/{credit_id}/purchase")
async def purchase_carbon_credit(
    credit_id: str,
    user_id: str,
    amount_tonnes: float,
    db: Session = Depends(get_db)
):
    """Purchase carbon credit"""
    credit = db.query(CarbonCredit).filter(CarbonCredit.id == credit_id).first()
    if not credit:
        raise HTTPException(status_code=404, detail="Carbon credit not found")
    
    if not credit.is_available:
        raise HTTPException(status_code=400, detail="Carbon credit not available")
    
    available_amount = credit.amount_tonnes_co2 - credit.reserved_amount - credit.sold_amount
    if amount_tonnes > available_amount:
        raise HTTPException(status_code=400, detail="Insufficient carbon credits available")
    
    # Calculate cost
    total_cost = amount_tonnes * credit.price_per_tonne
    
    # Create offset record
    offset = CarbonOffset(
        user_id=user_id,
        offset_type="carbon_credits",
        amount_kg_co2=amount_tonnes * 1000,  # Convert to kg
        cost_usd=total_cost,
        provider_name=credit.project_name,
        provider_certification=credit.verification_standard,
        project_id=credit.project_name,
        project_location=f"{credit.region}, {credit.country}",
        certificate_id=f"{credit.serial_number}_{uuid.uuid4().hex[:8]}",
        verification_status="verified",
        verified_at=datetime.utcnow()
    )
    
    db.add(offset)
    
    # Update credit availability
    credit.sold_amount += amount_tonnes
    if credit.sold_amount >= credit.amount_tonnes_co2:
        credit.is_available = False
    
    db.commit()
    db.refresh(offset)
    
    return {
        "offset": offset,
        "carbon_credit": credit,
        "purchase_details": {
            "amount_tonnes": amount_tonnes,
            "cost_usd": total_cost,
            "certificate_id": offset.certificate_id
        }
    }

# Analytics and reporting
@app.get("/analytics/platform-impact")
async def get_platform_environmental_impact(db: Session = Depends(get_db)):
    """Get platform-wide environmental impact"""
    # Get all footprints
    all_footprints = db.query(CarbonFootprint).all()
    all_offsets = db.query(CarbonOffset).all()
    
    # Calculate platform metrics
    total_platform_footprint = sum(fp.carbon_footprint_kg for fp in all_footprints)
    total_platform_offsets = sum(offset.amount_kg_co2 for offset in all_offsets)
    net_platform_impact = total_platform_footprint - total_platform_offsets
    
    # User participation
    total_users = len(set(fp.user_id for fp in all_footprints))
    offsetting_users = len(set(offset.user_id for offset in all_offsets))
    participation_rate = (offsetting_users / total_users * 100) if total_users > 0 else 0
    
    # Green trading metrics
    green_assets = db.query(GreenAsset).all()
    green_symbols = {asset.symbol for asset in green_assets}
    green_footprints = [fp for fp in all_footprints if fp.symbol in green_symbols]
    green_trading_percentage = (len(green_footprints) / len(all_footprints) * 100) if all_footprints else 0
    
    return {
        "platform_metrics": {
            "total_footprint_kg": total_platform_footprint,
            "total_offsets_kg": total_platform_offsets,
            "net_impact_kg": net_platform_impact,
            "is_carbon_neutral": net_platform_impact <= 0
        },
        "user_participation": {
            "total_users": total_users,
            "offsetting_users": offsetting_users,
            "participation_rate": participation_rate
        },
        "green_trading": {
            "green_transactions": len(green_footprints),
            "total_transactions": len(all_footprints),
            "green_percentage": green_trading_percentage
        },
        "environmental_benefits": {
            "total_trees_planted": sum(offset.trees_planted for offset in all_offsets),
            "total_renewable_energy_kwh": sum(offset.renewable_energy_kwh for offset in all_offsets),
            "co2_equivalent_cars_removed": int(total_platform_offsets / (404 * 365 / 1000))  # Cars removed for a year
        }
    }

@app.get("/sustainability-score/{user_id}")
async def get_user_sustainability_score(user_id: str, db: Session = Depends(get_db)):
    """Get user's sustainability score and ranking"""
    # Calculate user's sustainability metrics
    portfolio_metrics = assess_portfolio_sustainability(user_id, db)
    
    # Get user's rank among all users
    all_users_footprints = db.query(CarbonFootprint.user_id).distinct().all()
    user_scores = []
    
    for (other_user_id,) in all_users_footprints:
        other_metrics = assess_portfolio_sustainability(other_user_id, db)
        user_scores.append({
            "user_id": other_user_id,
            "score": other_metrics["sustainability_score"]
        })
    
    user_scores.sort(key=lambda x: x["score"], reverse=True)
    user_rank = next((i + 1 for i, user in enumerate(user_scores) if user["user_id"] == user_id), len(user_scores))
    
    # Generate sustainability badge
    score = portfolio_metrics["sustainability_score"]
    if score >= 90:
        badge = "Eco Champion"
        badge_color = "#00ff00"
    elif score >= 75:
        badge = "Green Trader"
        badge_color = "#7fff00"
    elif score >= 50:
        badge = "Eco Conscious"
        badge_color = "#ffff00"
    else:
        badge = "Getting Started"
        badge_color = "#ff7f00"
    
    return {
        "user_id": user_id,
        "sustainability_score": score,
        "rank": user_rank,
        "total_users": len(user_scores),
        "percentile": ((len(user_scores) - user_rank + 1) / len(user_scores)) * 100,
        "badge": {
            "name": badge,
            "color": badge_color
        },
        "metrics": portfolio_metrics,
        "next_milestone": {
            "target_score": 75 if score < 75 else 90 if score < 90 else 100,
            "actions_needed": portfolio_metrics["recommendations"]
        }
    }

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks"""
    logger.info("Carbon-Neutral Trading service started")
    
    # Start background tasks
    asyncio.create_task(periodic_footprint_calculation())
    asyncio.create_task(periodic_sustainability_updates())

async def periodic_footprint_calculation():
    """Calculate carbon footprints for new transactions"""
    while True:
        try:
            # This would integrate with the trading engine to get new transactions
            # and automatically calculate their carbon footprints
            
            await asyncio.sleep(300)  # Check every 5 minutes
            
        except Exception as e:
            logger.error(f"Error in footprint calculation: {e}")
            await asyncio.sleep(60)

async def periodic_sustainability_updates():
    """Update sustainability metrics and goals"""
    while True:
        try:
            db = SessionLocal()
            
            # Update all active sustainability goals
            goals = db.query(SustainabilityGoal).filter(
                SustainabilityGoal.status == "active"
            ).all()
            
            for goal in goals:
                # Update progress
                portfolio_metrics = assess_portfolio_sustainability(goal.user_id, db)
                goal.current_carbon_footprint = portfolio_metrics["total_footprint"]
                goal.current_green_percentage = portfolio_metrics["green_percentage"]
                
                # Update progress percentage
                if goal.goal_type == "carbon_neutral":
                    goal.progress_percentage = min(100, (goal.current_offsets / goal.current_carbon_footprint) * 100) if goal.current_carbon_footprint > 0 else 100
                
                # Check achievement
                if goal.progress_percentage >= 100 and goal.status != "achieved":
                    goal.status = "achieved"
                    logger.info(f"User {goal.user_id} achieved sustainability goal: {goal.goal_type}")
            
            db.commit()
            db.close()
            
            await asyncio.sleep(3600)  # Update every hour
            
        except Exception as e:
            logger.error(f"Error updating sustainability metrics: {e}")
            await asyncio.sleep(300)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8089)