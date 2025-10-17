/*
 * TigerEx Exchange Platform
 * Version: 7.0.0 - Consolidated Production Release
 * 
 * Complete cryptocurrency exchange platform with:
 * - CEX/DEX hybrid functionality
 * - 105+ exchange features
 * - Multi-platform support (Web, Mobile, Desktop)
 * - Enterprise-grade security
 * - White-label deployment ready
 * 
 * Production-ready implementation
 */

"""
TigerEx NFT Marketplace Admin Panel
Manages NFT collections, listings, and marketplace operations
Port: 8119
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uvicorn
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://tigerex:tigerex123@localhost:5432/tigerex_nft_marketplace"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class NFTStandard(str, Enum):
    ERC721 = "erc721"
    ERC1155 = "erc1155"
    SPL = "spl"

class CollectionStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    FEATURED = "featured"
    SUSPENDED = "suspended"

class NFTCollection(Base):
    __tablename__ = "nft_collections"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    symbol = Column(String)
    description = Column(Text)
    contract_address = Column(String, unique=True, index=True)
    chain = Column(String)
    standard = Column(String)
    creator_address = Column(String, index=True)
    status = Column(String, default="pending")
    is_verified = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    total_supply = Column(Integer, default=0)
    floor_price = Column(Float, default=0.0)
    total_volume = Column(Float, default=0.0)
    total_sales = Column(Integer, default=0)
    royalty_percentage = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)

class NFTListing(Base):
    __tablename__ = "nft_listings"
    
    id = Column(Integer, primary_key=True, index=True)
    collection_id = Column(Integer, index=True)
    token_id = Column(String, index=True)
    seller_address = Column(String, index=True)
    price = Column(Float)
    currency = Column(String)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    metadata = Column(JSON)

class NFTSale(Base):
    __tablename__ = "nft_sales"
    
    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, index=True)
    collection_id = Column(Integer, index=True)
    token_id = Column(String, index=True)
    seller_address = Column(String, index=True)
    buyer_address = Column(String, index=True)
    price = Column(Float)
    currency = Column(String)
    tx_hash = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)

Base.metadata.create_all(bind=engine)

class NFTCollectionCreate(BaseModel):
    name: str
    symbol: str
    description: str
    contract_address: str
    chain: str
    standard: NFTStandard
    creator_address: str
    royalty_percentage: float = Field(ge=0, le=10, default=0.0)
    metadata: Optional[Dict[str, Any]] = None

class NFTCollectionUpdate(BaseModel):
    description: Optional[str] = None
    status: Optional[CollectionStatus] = None
    is_verified: Optional[bool] = None
    is_featured: Optional[bool] = None
    floor_price: Optional[float] = None
    royalty_percentage: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

app = FastAPI(title="TigerEx NFT Marketplace Admin API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/admin/collections", status_code=201)
async def create_collection(collection: NFTCollectionCreate, db: Session = Depends(get_db)):
    """Create a new NFT collection"""
    try:
        existing = db.query(NFTCollection).filter(
            NFTCollection.contract_address == collection.contract_address
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Collection already exists")
        
        db_collection = NFTCollection(**collection.dict())
        db.add(db_collection)
        db.commit()
        db.refresh(db_collection)
        
        logger.info(f"Created NFT collection: {collection.name}")
        return db_collection
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating collection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/collections")
async def get_collections(
    skip: int = 0,
    limit: int = 100,
    status: Optional[CollectionStatus] = None,
    is_verified: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all NFT collections"""
    try:
        query = db.query(NFTCollection)
        
        if status:
            query = query.filter(NFTCollection.status == status)
        if is_verified is not None:
            query = query.filter(NFTCollection.is_verified == is_verified)
        if is_featured is not None:
            query = query.filter(NFTCollection.is_featured == is_featured)
        
        total = query.count()
        collections = query.order_by(NFTCollection.total_volume.desc()).offset(skip).limit(limit).all()
        
        return {"total": total, "collections": collections}
    except Exception as e:
        logger.error(f"Error fetching collections: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/admin/collections/{collection_id}")
async def update_collection(
    collection_id: int,
    collection_update: NFTCollectionUpdate,
    db: Session = Depends(get_db)
):
    """Update an NFT collection"""
    try:
        collection = db.query(NFTCollection).filter(NFTCollection.id == collection_id).first()
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")
        
        update_data = collection_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(collection, field, value)
        
        db.commit()
        db.refresh(collection)
        
        logger.info(f"Updated collection: {collection_id}")
        return collection
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating collection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/collections/{collection_id}/verify")
async def verify_collection(collection_id: int, db: Session = Depends(get_db)):
    """Verify an NFT collection"""
    try:
        collection = db.query(NFTCollection).filter(NFTCollection.id == collection_id).first()
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")
        
        collection.is_verified = True
        collection.status = "verified"
        db.commit()
        
        logger.info(f"Verified collection: {collection_id}")
        return {"message": "Collection verified successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error verifying collection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/analytics/overview")
async def get_analytics_overview(db: Session = Depends(get_db)):
    """Get NFT marketplace analytics"""
    try:
        total_collections = db.query(NFTCollection).count()
        verified_collections = db.query(NFTCollection).filter(
            NFTCollection.is_verified == True
        ).count()
        total_listings = db.query(NFTListing).filter(NFTListing.status == "active").count()
        total_volume = db.query(NFTCollection).with_entities(
            db.func.sum(NFTCollection.total_volume)
        ).scalar() or 0.0
        total_sales = db.query(NFTSale).count()
        
        return {
            "total_collections": total_collections,
            "verified_collections": verified_collections,
            "total_listings": total_listings,
            "total_volume": total_volume,
            "total_sales": total_sales
        }
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "nft-marketplace-admin"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8119)