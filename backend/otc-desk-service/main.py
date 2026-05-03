from fastapi import FastAPI
from admin.admin_routes import router as admin_router

# @file main.py
# @description TigerEx otc-desk-service service
# @author TigerEx Development Team
from datetime import datetime

app = FastAPI(title="TigerEx OTC Desk Service")

# Include admin router
app.include_router(admin_router)

@app.post("/api/v1/otc/quote-request")
async def request_quote(user_id: int, asset: str, amount: float, side: str):
    """Request OTC quote"""
    return {
        "success": True,
        "quote_id": "OTC-12345",
        "asset": asset,
        "amount": amount,
        "side": side,
        "price": "50000.00",
        "total": str(float(amount) * 50000),
        "valid_until": "2025-10-02T18:00:00Z"
    }

@app.post("/api/v1/otc/execute")
async def execute_otc_trade(quote_id: str, user_id: int):
    """Execute OTC trade"""
    return {
        "success": True,
        "trade_id": "OTC-TRADE-67890",
        "status": "executed",
        "settlement_time": "2025-10-02T17:00:00Z"
    }

@app.get("/api/v1/otc/trades/{user_id}")
async def get_otc_trades(user_id: int):
    """Get user's OTC trades"""
    return {
        "success": True,
        "trades": [
            {
                "trade_id": "OTC-TRADE-67890",
                "asset": "BTC",
                "amount": "10.00",
                "price": "50000.00",
                "total": "500000.00",
                "status": "completed",
                "timestamp": "2025-10-01"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8293)
def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
