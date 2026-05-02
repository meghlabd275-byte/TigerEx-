"""
TigerEx COMPLETE SERVICE - Full Implementation
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import uuid
import time

app = FastAPI()

# Data Models
class User(BaseModel):
    user_id: str
    email: str
    role: str = "user"

class Order(BaseModel):
    order_id: str
    user_id: str
    side: str
    symbol: str
    price: float
    qty: float
    status: str = "pending"

class Transaction(BaseModel):
    tx_id: str
    user_id: str
    type: str
    amount: float
    status: str = "pending"

class Wallet(BaseModel):
    user_id: str
    address: str
    chain: str
    balance: float = 0.0

# Database Store
class Store:
    def __init__(self):
        self.users = {}
        self.orders = {}
        self.transactions = {}
        self.wallets = {}
        self.positions = {}
        self.accounts = {}
        self.oid = 0
        self.tid = 0
    
    # User Methods
    def create_user(self, user_id: str, email: str, role: str = "user") -> User:
        user = User(user_id=user_id, email=email, role=role)
        self.users[user_id] = user
        self.accounts[user_id] = {"balance": 0, "equity": 0, "margin": 0}
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)
    
    def list_users(self) -> List[User]:
        return list(self.users.values())
    
    # Order Methods
    def create_order(self, user_id: str, side: str, symbol: str, price: float, qty: float) -> Order:
        self.oid += 1
        order = Order(
            order_id=f"ORD-{self.oid}",
            user_id=user_id,
            side=side,
            symbol=symbol,
            price=price,
            qty=qty,
            status="open"
        )
        self.orders[order.order_id] = order
        return order
    
    def get_order(self, order_id: str) -> Optional[Order]:
        return self.orders.get(order_id)
    
    def cancel_order(self, order_id: str) -> bool:
        if order_id in self.orders:
            self.orders[order_id].status = "cancelled"
            return True
        return False
    
    def fill_order(self, order_id: str) -> bool:
        if order_id in self.orders:
            self.orders[order_id].status = "filled"
            return True
        return False
    
    def get_orders(self, user_id: str = None) -> List[Order]:
        orders = self.orders.values()
        if user_id:
            orders = [o for o in orders if o.user_id == user_id]
        return orders
    
    # Transaction Methods
    def create_tx(self, user_id: str, tx_type: str, amount: float) -> Transaction:
        self.tid += 1
        tx = Transaction(
            tx_id=f"TX-{self.tid}",
            user_id=user_id,
            type=tx_type,
            amount=amount,
            status="pending"
        )
        self.transactions[tx.tx_id] = tx
        return tx
    
    def confirm_tx(self, tx_id: str) -> bool:
        if tx_id in self.transactions:
            self.transactions[tx_id].status = "confirmed"
            return True
        return False
    
    def get_txs(self, user_id: str = None) -> List[Transaction]:
        txs = self.transactions.values()
        if user_id:
            txs = [t for t in txs if t.user_id == user_id]
        return txs
    
    # Wallet Methods
    def create_wallet(self, user_id: str, address: str, chain: str) -> Wallet:
        wallet = Wallet(user_id=user_id, address=address, chain=chain)
        self.wallets[address] = wallet
        return wallet
    
    def get_wallet(self, address: str) -> Optional[Wallet]:
        return self.wallets.get(address)
    
    def add_balance(self, address: str, amount: float) -> bool:
        if address in self.wallets:
            self.wallets[address].balance += amount
            return True
        return False
    
    # Position Methods
    def open_position(self, user_id: str, symbol: str, side: str, qty: float, price: float):
        key = f"{user_id}_{symbol}"
        self.positions[key] = {
            "user_id": user_id,
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "price": price,
            "open_time": datetime.now().isoformat()
        }
    
    def close_position(self, user_id: str, symbol: str) -> bool:
        key = f"{user_id}_{symbol}"
        if key in self.positions:
            del self.positions[key]
            return True
        return False
    
    def get_positions(self, user_id: str = None) -> Dict:
        if user_id:
            return {k: v for k, v in self.positions.items() if v["user_id"] == user_id}
        return self.positions

store = Store()

# Initialize with sample data
store.create_user("user1", "user1@tigerex.com", "trader")
store.create_user("admin", "admin@tigerex.com", "admin")

# REST Endpoints
@app.get("/")
async def root():
    return {"service": "TigerEx", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "users": len(store.users),
        "orders": len(store.orders),
        "transactions": len(store.transactions),
        "wallets": len(store.wallets)
    }

# User Endpoints
@app.post("/api/v1/users")
async def create_user(req: dict):
    return store.create_user(req["user_id"], req["email"], req.get("role", "user"))

@app.get("/api/v1/users")
async def list_users():
    return [u.dict() for u in store.list_users()]

@app.get("/api/v1/users/{user_id}")
async def get_user(user_id: str):
    user = store.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.dict()

# Order Endpoints
@app.post("/api/v1/orders")
async def create_order(req: dict):
    return store.create_order(req["user_id"], req["side"], req["symbol"], req["price"], req["qty"])

@app.get("/api/v1/orders")
async def list_orders(user_id: str = None):
    return [o.dict() for o in store.get_orders(user_id)]

@app.get("/api/v1/orders/{order_id}")
async def get_order(order_id: str):
    order = store.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order.dict()

@app.delete("/api/v1/orders/{order_id}")
async def cancel_order(order_id: str):
    if store.cancel_order(order_id):
        return {"status": "cancelled"}
    raise HTTPException(status_code=404, detail="Order not found")

# Transaction Endpoints
@app.post("/api/v1/transactions")
async def create_tx(req: dict):
    return store.create_tx(req["user_id"], req["type"], req["amount"])

@app.get("/api/v1/transactions")
async def list_txs(user_id: str = None):
    return [t.dict() for t in store.get_txs(user_id)]

@app.post("/api/v1/transactions/{tx_id}/confirm")
async def confirm_tx(tx_id: str):
    if store.confirm_tx(tx_id):
        return {"status": "confirmed"}
    raise HTTPException(status_code=404, detail="Transaction not found")

# Wallet Endpoints
@app.post("/api/v1/wallets")
async def create_wallet(req: dict):
    return store.create_wallet(req["user_id"], req["address"], req["chain"])

@app.get("/api/v1/wallets/{address}")
async def get_wallet(address: str):
    wallet = store.get_wallet(address)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet.dict()

@app.post("/api/v1/wallets/{address}/deposit")
async def deposit(address: str, amount: float):
    if store.add_balance(address, amount):
        return {"status": "deposited", "amount": amount}
    raise HTTPException(status_code=404, detail="Wallet not found")

# Position Endpoints
@app.post("/api/v1/positions")
async def open_position(req: dict):
    store.open_position(req["user_id"], req["symbol"], req["side"], req["qty"], req["price"])
    return {"status": "opened"}

@app.get("/api/v1/positions")
async def list_positions(user_id: str = None):
    return store.get_positions(user_id)

@app.delete("/api/v1/positions")
async def close_position(user_id: str, symbol: str):
    if store.close_position(user_id, symbol):
        return {"status": "closed"}
    return {"status": "not_found"}

# Account Endpoints
@app.get("/api/v1/accounts/{user_id}")
async def get_account(user_id: str):
    return store.accounts.get(user_id, {})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
