from fastapi import FastAPI
from admin.admin_routes import router as admin_router

from datetime import datetime

app = FastAPI(title="TigerEx Cardano Integration Service")

# Include admin router
app.include_router(admin_router)

@app.post("/api/v1/cardano/deposit-address")
async def generate_cardano_deposit_address(user_id: int):
    """Generate Cardano deposit address"""
    return {
        "success": True,
        "address": "addr1q8w3x8h3x8h3x8h3x8h3x8h3x8h3x8h3x8h3x8h3x8h3x8h3x8h3",
        "network": "Cardano",
        "user_id": user_id
    }

@app.post("/api/v1/cardano/withdraw")
async def withdraw_cardano(user_id: int, address: str, amount: float):
    """Withdraw Cardano (ADA)"""
    return {
        "success": True,
        "transaction_id": "ADA-TX-67890",
        "network": "Cardano",
        "amount": amount,
        "address": address,
        "fee": 0.17
    }

@app.get("/api/v1/cardano/balance/{user_id}")
async def get_cardano_balance(user_id: int):
    """Get Cardano balance"""
    return {
        "success": True,
        "user_id": user_id,
        "balance": "500.00",
        "network": "Cardano",
        "last_updated": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8296)
