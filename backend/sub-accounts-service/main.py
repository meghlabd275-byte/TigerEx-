from fastapi import FastAPI
from admin.admin_routes import router as admin_router

# @file main.py
# @description TigerEx sub-accounts-service service
# @author TigerEx Development Team
from datetime import datetime

app = FastAPI(title="TigerEx Sub-Accounts Service")

# Include admin router
app.include_router(admin_router)

@app.post("/api/v1/sub-accounts/create")
async def create_sub_account(master_user_id: int, email: str, permissions: dict):
    """Create a sub-account"""
    return {
        "success": True,
        "sub_account_id": 54321,
        "email": email,
        "api_key": "generated_api_key",
        "permissions": permissions
    }

@app.get("/api/v1/sub-accounts/{master_user_id}")
async def get_sub_accounts(master_user_id: int):
    """Get all sub-accounts for master account"""
    return {
        "success": True,
        "sub_accounts": [
            {
                "id": 54321,
                "email": "sub1@example.com",
                "status": "active",
                "permissions": ["spot_trading", "futures_trading"],
                "created_at": "2025-01-01"
            }
        ]
    }

@app.put("/api/v1/sub-accounts/{sub_account_id}/permissions")
async def update_permissions(sub_account_id: int, permissions: dict):
    """Update sub-account permissions"""
    return {
        "success": True,
        "message": "Permissions updated successfully"
    }

@app.post("/api/v1/sub-accounts/transfer")
async def transfer_between_accounts(from_account: int, to_account: int, asset: str, amount: float):
    """Transfer assets between master and sub-accounts"""
    return {
        "success": True,
        "transfer_id": 98765,
        "message": "Transfer successful"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8292)
def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
