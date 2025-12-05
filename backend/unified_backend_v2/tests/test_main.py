import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from backend.unified_backend_v2.main import app, get_db, Base

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def setup_database():
    """Setup test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(setup_database):
    """Test client fixture"""
    return TestClient(app)

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_market_order(client):
    """Test creating a market order"""
    response = client.post("/api/v1/orders", json={
        "symbol": "BTCUSDT",
        "side": "buy",
        "order_type": "market",
        "quantity": 1
    })
    assert response.status_code == 200
    assert response.json()["status"] == "filled"

def test_create_limit_order(client):
    """Test creating a limit order"""
    response = client.post("/api/v1/orders", json={
        "symbol": "BTCUSDT",
        "side": "buy",
        "order_type": "limit",
        "quantity": 1,
        "price": 50000
    })
    assert response.status_code == 200
    assert response.json()["status"] == "open"

def test_create_stop_loss_order(client):
    """Test creating a stop-loss order"""
    response = client.post("/api/v1/orders", json={
        "symbol": "BTCUSDT",
        "side": "sell",
        "order_type": "stop_loss",
        "quantity": 1,
        "stop_price": 40000
    })
    assert response.status_code == 200
    assert response.json()["status"] == "pending"

def test_create_trader_profile(client):
    """Test creating a trader profile"""
    response = client.post("/api/v1/traders", json={
        "display_name": "Test Trader",
        "bio": "A test trader"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "created"

def test_create_copy_relationship(client):
    """Test creating a copy relationship"""
    # First, create a trader profile
    trader_response = client.post("/api/v1/traders", json={
        "display_name": "Test Trader 2",
        "bio": "Another test trader"
    })
    trader_id = trader_response.json()["trader_id"]

    # Then, create a copy relationship
    response = client.post("/api/v1/copy", json={
        "trader_id": trader_id,
        "copy_amount": 1000
    })
    assert response.status_code == 200
    assert response.json()["status"] == "active"

def test_create_p2p_order(client):
    """Test creating a P2P order"""
    response = client.post("/api/v1/p2p/orders", json={
        "order_type": "buy",
        "cryptocurrency": "BTC",
        "fiat_currency": "USD",
        "crypto_amount": 1,
        "price_per_unit": 50000,
        "accepted_payment_methods": ["bank_transfer"]
    })
    assert response.status_code == 200
    assert response.json()["status"] == "active"

def test_create_p2p_trade(client):
    """Test creating a P2P trade"""
    # First, create a P2P order
    order_response = client.post("/api/v1/p2p/orders", json={
        "order_type": "sell",
        "cryptocurrency": "BTC",
        "fiat_currency": "USD",
        "crypto_amount": 1,
        "price_per_unit": 50000,
        "accepted_payment_methods": ["bank_transfer"]
    })
    order_id = order_response.json()["order_id"]

    # Then, create a trade for that order
    response = client.post("/api/v1/p2p/trades", json={
        "order_id": order_id,
        "fiat_amount": 50000,
        "payment_method_id": "1"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "pending"

def test_create_take_profit_order(client):
    """Test creating a take-profit order"""
    response = client.post("/api/v1/orders", json={
        "symbol": "BTCUSDT",
        "side": "sell",
        "order_type": "take_profit",
        "quantity": 1,
        "stop_price": 60000
    })
    assert response.status_code == 200
    assert response.json()["status"] == "pending"
