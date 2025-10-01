"""
Perpetual Swap Service
Advanced perpetual swap contracts with funding rates
Port: 8055
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
from enum import Enum
import uvicorn
from decimal import Decimal

app = FastAPI(
    title="Perpetual Swap Service",
    description="Advanced perpetual swap contracts with funding rates",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PositionSide(str, Enum):
    LONG = "long"
    SHORT = "short"

class SwapContract(BaseModel):
    symbol: str
    mark_price: Decimal
    index_price: Decimal
    funding_rate: Decimal
    next_funding_time: datetime
    open_interest: Decimal
    max_leverage: int = 100

class Position(BaseModel):
    position_id: str
    user_id: str
    symbol: str
    side: PositionSide
    size: Decimal
    entry_price: Decimal
    leverage: int
    margin: Decimal
    unrealized_pnl: Decimal
    liquidation_price: Decimal
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Storage
contracts_db = {}
positions_db = {}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "perpetual-swap"}

@app.get("/contracts")
async def get_contracts():
    return {"contracts": list(contracts_db.values())}

@app.post("/positions")
async def open_position(user_id: str, symbol: str, side: PositionSide, size: Decimal, leverage: int):
    position = Position(
        position_id=f"pos_{user_id}_{datetime.utcnow().timestamp()}",
        user_id=user_id,
        symbol=symbol,
        side=side,
        size=size,
        entry_price=Decimal("45000"),
        leverage=leverage,
        margin=size * Decimal("45000") / leverage,
        unrealized_pnl=Decimal("0"),
        liquidation_price=Decimal("40000")
    )
    
    if user_id not in positions_db:
        positions_db[user_id] = []
    positions_db[user_id].append(position)
    
    return {"message": "Position opened", "position": position}

@app.get("/positions/{user_id}")
async def get_positions(user_id: str):
    return {"positions": positions_db.get(user_id, [])}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8055)