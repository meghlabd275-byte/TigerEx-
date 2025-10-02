from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="TigerEx Sub-Accounts Service")

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
