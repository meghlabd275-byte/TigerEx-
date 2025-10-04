"""
Auto-Invest Service
Automated recurring cryptocurrency purchases (Dollar-Cost Averaging)
Port: 8054
"""

from fastapi import FastAPI
from admin.admin_routes import router as admin_router
from fastapi import HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from enum import Enum
import uvicorn
from decimal import Decimal

app = FastAPI(

# Include admin router
app.include_router(admin_router)
    title="Auto-Invest Service",
    description="Automated recurring cryptocurrency purchases with DCA strategy",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class Frequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"

class PlanStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class OrderStatus(str, Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    FAILED = "failed"
    SKIPPED = "skipped"

# Models
class AutoInvestPlan(BaseModel):
    plan_id: str
    user_id: str
    asset: str
    amount_per_purchase: Decimal
    frequency: Frequency
    start_date: datetime
    end_date: Optional[datetime] = None
    total_invested: Decimal = Decimal("0")
    total_purchased: Decimal = Decimal("0")
    average_price: Decimal = Decimal("0")
    status: PlanStatus = PlanStatus.ACTIVE
    next_purchase_date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PurchaseOrder(BaseModel):
    order_id: str
    plan_id: str
    user_id: str
    asset: str
    amount_invested: Decimal
    amount_purchased: Decimal
    price: Decimal
    status: OrderStatus
    executed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CreatePlanRequest(BaseModel):
    asset: str
    amount_per_purchase: Decimal = Field(gt=0)
    frequency: Frequency
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class UpdatePlanRequest(BaseModel):
    amount_per_purchase: Optional[Decimal] = None
    frequency: Optional[Frequency] = None
    end_date: Optional[datetime] = None
    status: Optional[PlanStatus] = None

class Portfolio(BaseModel):
    user_id: str
    total_invested: Decimal = Decimal("0")
    total_value: Decimal = Decimal("0")
    total_profit_loss: Decimal = Decimal("0")
    profit_loss_percentage: Decimal = Decimal("0")
    holdings: Dict[str, Dict] = {}

# In-memory storage
plans_db: Dict[str, List[AutoInvestPlan]] = {}
orders_db: Dict[str, List[PurchaseOrder]] = {}
portfolios_db: Dict[str, Portfolio] = {}

# Mock price data
mock_prices = {
    "BTC": Decimal("45000"),
    "ETH": Decimal("3000"),
    "BNB": Decimal("300"),
    "SOL": Decimal("100"),
    "ADA": Decimal("0.5")
}

# Helper functions
def calculate_next_purchase_date(current_date: datetime, frequency: Frequency) -> datetime:
    """Calculate next purchase date based on frequency"""
    if frequency == Frequency.DAILY:
        return current_date + timedelta(days=1)
    elif frequency == Frequency.WEEKLY:
        return current_date + timedelta(weeks=1)
    elif frequency == Frequency.BIWEEKLY:
        return current_date + timedelta(weeks=2)
    elif frequency == Frequency.MONTHLY:
        return current_date + timedelta(days=30)
    return current_date

def execute_purchase(plan: AutoInvestPlan) -> PurchaseOrder:
    """Execute a purchase order for an auto-invest plan"""
    current_price = mock_prices.get(plan.asset, Decimal("1"))
    amount_purchased = plan.amount_per_purchase / current_price
    
    order = PurchaseOrder(
        order_id=f"order_{plan.plan_id}_{datetime.utcnow().timestamp()}",
        plan_id=plan.plan_id,
        user_id=plan.user_id,
        asset=plan.asset,
        amount_invested=plan.amount_per_purchase,
        amount_purchased=amount_purchased,
        price=current_price,
        status=OrderStatus.EXECUTED,
        executed_at=datetime.utcnow()
    )
    
    # Update plan statistics
    plan.total_invested += plan.amount_per_purchase
    plan.total_purchased += amount_purchased
    plan.average_price = plan.total_invested / plan.total_purchased if plan.total_purchased > 0 else Decimal("0")
    plan.next_purchase_date = calculate_next_purchase_date(datetime.utcnow(), plan.frequency)
    plan.updated_at = datetime.utcnow()
    
    # Store order
    if plan.user_id not in orders_db:
        orders_db[plan.user_id] = []
    orders_db[plan.user_id].append(order)
    
    # Update portfolio
    update_portfolio(plan.user_id, plan.asset, amount_purchased, plan.amount_per_purchase)
    
    return order

def update_portfolio(user_id: str, asset: str, amount: Decimal, invested: Decimal):
    """Update user's portfolio"""
    if user_id not in portfolios_db:
        portfolios_db[user_id] = Portfolio(user_id=user_id)
    
    portfolio = portfolios_db[user_id]
    
    if asset not in portfolio.holdings:
        portfolio.holdings[asset] = {
            "amount": Decimal("0"),
            "invested": Decimal("0"),
            "current_value": Decimal("0"),
            "profit_loss": Decimal("0")
        }
    
    portfolio.holdings[asset]["amount"] += amount
    portfolio.holdings[asset]["invested"] += invested
    
    # Calculate current value
    current_price = mock_prices.get(asset, Decimal("1"))
    portfolio.holdings[asset]["current_value"] = portfolio.holdings[asset]["amount"] * current_price
    portfolio.holdings[asset]["profit_loss"] = portfolio.holdings[asset]["current_value"] - portfolio.holdings[asset]["invested"]
    
    # Update portfolio totals
    portfolio.total_invested = sum(h["invested"] for h in portfolio.holdings.values())
    portfolio.total_value = sum(h["current_value"] for h in portfolio.holdings.values())
    portfolio.total_profit_loss = portfolio.total_value - portfolio.total_invested
    portfolio.profit_loss_percentage = (portfolio.total_profit_loss / portfolio.total_invested * 100) if portfolio.total_invested > 0 else Decimal("0")

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "auto-invest",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/plans")
async def create_plan(user_id: str, request: CreatePlanRequest):
    """Create a new auto-invest plan"""
    # Validate asset
    if request.asset not in mock_prices:
        raise HTTPException(status_code=400, detail="Asset not supported")
    
    # Set start date
    start_date = request.start_date or datetime.utcnow()
    
    # Create plan
    plan = AutoInvestPlan(
        plan_id=f"plan_{user_id}_{datetime.utcnow().timestamp()}",
        user_id=user_id,
        asset=request.asset,
        amount_per_purchase=request.amount_per_purchase,
        frequency=request.frequency,
        start_date=start_date,
        end_date=request.end_date,
        next_purchase_date=calculate_next_purchase_date(start_date, request.frequency)
    )
    
    # Store plan
    if user_id not in plans_db:
        plans_db[user_id] = []
    plans_db[user_id].append(plan)
    
    return {
        "plan_id": plan.plan_id,
        "message": "Auto-invest plan created successfully",
        "next_purchase_date": plan.next_purchase_date.isoformat()
    }

@app.get("/plans/{user_id}", response_model=List[AutoInvestPlan])
async def get_plans(user_id: str, status: Optional[PlanStatus] = None):
    """Get user's auto-invest plans"""
    if user_id not in plans_db:
        return []
    
    plans = plans_db[user_id]
    
    if status:
        plans = [p for p in plans if p.status == status]
    
    return plans

@app.get("/plans/{user_id}/{plan_id}", response_model=AutoInvestPlan)
async def get_plan(user_id: str, plan_id: str):
    """Get specific auto-invest plan"""
    if user_id not in plans_db:
        raise HTTPException(status_code=404, detail="No plans found")
    
    for plan in plans_db[user_id]:
        if plan.plan_id == plan_id:
            return plan
    
    raise HTTPException(status_code=404, detail="Plan not found")

@app.put("/plans/{user_id}/{plan_id}")
async def update_plan(user_id: str, plan_id: str, request: UpdatePlanRequest):
    """Update an auto-invest plan"""
    if user_id not in plans_db:
        raise HTTPException(status_code=404, detail="No plans found")
    
    plan = None
    for p in plans_db[user_id]:
        if p.plan_id == plan_id:
            plan = p
            break
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Update plan
    if request.amount_per_purchase:
        plan.amount_per_purchase = request.amount_per_purchase
    if request.frequency:
        plan.frequency = request.frequency
        plan.next_purchase_date = calculate_next_purchase_date(datetime.utcnow(), request.frequency)
    if request.end_date:
        plan.end_date = request.end_date
    if request.status:
        plan.status = request.status
    
    plan.updated_at = datetime.utcnow()
    
    return {
        "message": "Plan updated successfully",
        "plan": plan
    }

@app.delete("/plans/{user_id}/{plan_id}")
async def delete_plan(user_id: str, plan_id: str):
    """Delete an auto-invest plan"""
    if user_id not in plans_db:
        raise HTTPException(status_code=404, detail="No plans found")
    
    for i, plan in enumerate(plans_db[user_id]):
        if plan.plan_id == plan_id:
            plan.status = PlanStatus.CANCELLED
            return {"message": "Plan cancelled successfully"}
    
    raise HTTPException(status_code=404, detail="Plan not found")

@app.post("/plans/{user_id}/{plan_id}/execute")
async def execute_plan(user_id: str, plan_id: str):
    """Manually execute a purchase for a plan"""
    if user_id not in plans_db:
        raise HTTPException(status_code=404, detail="No plans found")
    
    plan = None
    for p in plans_db[user_id]:
        if p.plan_id == plan_id:
            plan = p
            break
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    if plan.status != PlanStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Plan is not active")
    
    # Execute purchase
    order = execute_purchase(plan)
    
    return {
        "message": "Purchase executed successfully",
        "order": order
    }

@app.post("/plans/{user_id}/{plan_id}/pause")
async def pause_plan(user_id: str, plan_id: str):
    """Pause an auto-invest plan"""
    if user_id not in plans_db:
        raise HTTPException(status_code=404, detail="No plans found")
    
    for plan in plans_db[user_id]:
        if plan.plan_id == plan_id:
            plan.status = PlanStatus.PAUSED
            plan.updated_at = datetime.utcnow()
            return {"message": "Plan paused successfully"}
    
    raise HTTPException(status_code=404, detail="Plan not found")

@app.post("/plans/{user_id}/{plan_id}/resume")
async def resume_plan(user_id: str, plan_id: str):
    """Resume a paused auto-invest plan"""
    if user_id not in plans_db:
        raise HTTPException(status_code=404, detail="No plans found")
    
    for plan in plans_db[user_id]:
        if plan.plan_id == plan_id:
            if plan.status != PlanStatus.PAUSED:
                raise HTTPException(status_code=400, detail="Plan is not paused")
            
            plan.status = PlanStatus.ACTIVE
            plan.next_purchase_date = calculate_next_purchase_date(datetime.utcnow(), plan.frequency)
            plan.updated_at = datetime.utcnow()
            return {"message": "Plan resumed successfully"}
    
    raise HTTPException(status_code=404, detail="Plan not found")

@app.get("/orders/{user_id}", response_model=List[PurchaseOrder])
async def get_orders(
    user_id: str,
    plan_id: Optional[str] = None,
    status: Optional[OrderStatus] = None
):
    """Get user's purchase orders"""
    if user_id not in orders_db:
        return []
    
    orders = orders_db[user_id]
    
    if plan_id:
        orders = [o for o in orders if o.plan_id == plan_id]
    
    if status:
        orders = [o for o in orders if o.status == status]
    
    return orders

@app.get("/portfolio/{user_id}", response_model=Portfolio)
async def get_portfolio(user_id: str):
    """Get user's auto-invest portfolio"""
    if user_id not in portfolios_db:
        return Portfolio(user_id=user_id)
    
    portfolio = portfolios_db[user_id]
    
    # Update current values
    for asset, holding in portfolio.holdings.items():
        current_price = mock_prices.get(asset, Decimal("1"))
        holding["current_value"] = holding["amount"] * current_price
        holding["profit_loss"] = holding["current_value"] - holding["invested"]
    
    # Recalculate totals
    portfolio.total_invested = sum(h["invested"] for h in portfolio.holdings.values())
    portfolio.total_value = sum(h["current_value"] for h in portfolio.holdings.values())
    portfolio.total_profit_loss = portfolio.total_value - portfolio.total_invested
    portfolio.profit_loss_percentage = (portfolio.total_profit_loss / portfolio.total_invested * 100) if portfolio.total_invested > 0 else Decimal("0")
    
    return portfolio

@app.get("/analytics/{user_id}")
async def get_analytics(user_id: str):
    """Get analytics for user's auto-invest activity"""
    if user_id not in plans_db:
        return {
            "total_plans": 0,
            "active_plans": 0,
            "total_invested": "0",
            "total_orders": 0
        }
    
    plans = plans_db[user_id]
    orders = orders_db.get(user_id, [])
    
    return {
        "total_plans": len(plans),
        "active_plans": len([p for p in plans if p.status == PlanStatus.ACTIVE]),
        "paused_plans": len([p for p in plans if p.status == PlanStatus.PAUSED]),
        "total_invested": str(sum(p.total_invested for p in plans)),
        "total_orders": len(orders),
        "successful_orders": len([o for o in orders if o.status == OrderStatus.EXECUTED]),
        "failed_orders": len([o for o in orders if o.status == OrderStatus.FAILED])
    }

@app.get("/supported-assets")
async def get_supported_assets():
    """Get list of supported assets for auto-invest"""
    return {
        "assets": list(mock_prices.keys()),
        "prices": {k: str(v) for k, v in mock_prices.items()}
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8054)