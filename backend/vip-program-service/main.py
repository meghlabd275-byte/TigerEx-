from fastapi import FastAPI
from datetime import datetime
from decimal import Decimal

app = FastAPI(title="TigerEx VIP Program Service")

# VIP Levels and Benefits
VIP_LEVELS = {
    0: {"name": "Regular", "trading_fee": 0.1, "withdrawal_fee": 0.0005, "min_volume": 0},
    1: {"name": "VIP 1", "trading_fee": 0.09, "withdrawal_fee": 0.0004, "min_volume": 50000},
    2: {"name": "VIP 2", "trading_fee": 0.08, "withdrawal_fee": 0.0003, "min_volume": 500000},
    3: {"name": "VIP 3", "trading_fee": 0.07, "withdrawal_fee": 0.0002, "min_volume": 2000000},
    4: {"name": "VIP 4", "trading_fee": 0.06, "withdrawal_fee": 0.0001, "min_volume": 10000000},
    5: {"name": "VIP 5", "trading_fee": 0.05, "withdrawal_fee": 0.00005, "min_volume": 50000000}
}

@app.get("/api/v1/vip/levels")
async def get_vip_levels():
    """Get all VIP levels and benefits"""
    return {"success": True, "levels": VIP_LEVELS}

@app.get("/api/v1/vip/user/{user_id}")
async def get_user_vip_status(user_id: int):
    """Get user's VIP status"""
    return {
        "success": True,
        "user_id": user_id,
        "vip_level": 2,
        "trading_volume_30d": "750000.00",
        "next_level_requirement": "2000000.00",
        "benefits": VIP_LEVELS[2]
    }

@app.get("/api/v1/vip/benefits/{level}")
async def get_level_benefits(level: int):
    """Get benefits for specific VIP level"""
    if level not in VIP_LEVELS:
        return {"success": False, "error": "Invalid VIP level"}
    
    return {"success": True, "level": level, "benefits": VIP_LEVELS[level]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8291)
