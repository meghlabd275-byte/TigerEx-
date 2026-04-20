from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/status")
async def admin_status():
    return {"status": "active", "service": "price-aggregation"}

@router.post("/config")
async def update_config(config: dict):
    return {"status": "updated", "config": config}

@router.get("/metrics")
async def get_metrics():
    return {
        "total_requests": 0,
        "active_connections": 0,
        "last_update": "2024-01-01T00:00:00Z"
    }