from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/status")
async def admin_status():
    return {"status": "active", "service": "tradingview-integration"}

@router.post("/tokens")
async def create_token(token: dict):
    return {"status": "created", "token": token}

@router.get("/metrics")
async def get_metrics():
    return {
        "total_tokens": 0,
        "active_charts": 0,
        "total_views": 0
    }