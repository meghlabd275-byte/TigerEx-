#!/usr/bin/env python3
"""
TigerEx Main Backend Service - User Interface
Integrates Wallet, Blockchain, Explorer, Exchange for Users
"""
import os
import json
import hashlib
import logging
import uuid
import time
import threading
import requests
from typing import Dict, List
from datetime import datetime, timedelta
from collections import defaultdict
from flask import Flask, jsonify, request
from flask_cors import CORS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# TIGEREX USER SERVICE
# ============================================================
class TigerExUserService:
    """Main TigerEx user service"""
    
    def __init__(self):
        self.users = {}
        self.sessions = {}
        self.user_data = defaultdict(lambda: {"balance": defaultdict(float), "orders": [], "wallets": []})
        
        logger.info("TigerEx User Service initialized")
    
    def register(self, email: str, password: str, name: str = "") -> Dict:
        """Register new user"""
        if email in self.users:
            return {"error": "User already exists"}
        
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        
        self.users[email] = {
            "id": user_id,
            "email": email,
            "name": name or email.split("@")[0],
            "role": "user",
            "created_at": datetime.utcnow().isoformat(),
        }
        
        session_id = self._create_session(user_id, email)
        
        # Initialize user data
        self.user_data[user_id]["balance"]["TIG"] = 1000
        self.user_data[user_id]["balance"]["USDC"] = 10000
        
        return {
            "user_id": user_id,
            "email": email,
            "session_id": session_id,
            "status": "active",
            "welcome_bonus": {"TIG": 1000, "USDC": 10000}
        }
    
    def login(self, email: str, password: str) -> Dict:
        """Login user"""
        if email not in self.users:
            return {"error": "User not found"}
        
        user = self.users[email]
        session_id = self._create_session(user["id"], email)
        
        return {
            "user_id": user["id"],
            "email": email,
            "session_id": session_id,
            "status": "active"
        }
    
    def logout(self, session_id: str) -> Dict:
        """Logout user"""
        if session_id in self.sessions:
            del self.sessions[session_id]
        
        return {"status": "logged_out"}
    
    def _create_session(self, user_id: str, email: str) -> str:
        """Create session"""
        session_id = f"sess_{uuid.uuid4().hex[:24]}"
        self.sessions[session_id] = {
            "user_id": user_id,
            "email": email,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        return session_id
    
    def get_user(self, user_id: str) -> Dict:
        """Get user info"""
        for user in self.users.values():
            if user.get("id") == user_id:
                return user
        
        return {"error": "User not found"}
    
    def get_balance(self, user_id: str) -> Dict:
        """Get user balance"""
        return dict(self.user_data[user_id]["balance"])
    
    def get_portfolio(self, user_id: str) -> Dict:
        """Get user portfolio"""
        return {
            "balance": dict(self.user_data[user_id]["balance"]),
            "orders": self.user_data[user_id]["orders"],
            "wallets": self.user_data[user_id]["wallets"],
        }
    
    def get_services_status(self) -> Dict:
        """Get services status"""
        return {
            "wallet": "running",
            "blockchain": "running",
            "explorer": "running",
            "exchange": "running",
        }
    
    def get_market_prices(self) -> Dict:
        """Get market prices"""
        return {
            "TIG": {"usd": 100.0, "change_24h": 5.2},
            "BTC": {"usd": 50000.0, "change_24h": -1.2},
            "ETH": {"usd": 3000.0, "change_24h": 2.5},
            "USDC": {"usd": 1.0, "change_24h": 0.01},
            "USDT": {"usd": 1.0, "change_24h": -0.01},
            "BNB": {"usd": 350.0, "change_24h": 1.8},
            "SOL": {"usd": 120.0, "change_24h": -3.2},
        }
    
    def get_supported_chains(self) -> List[Dict]:
        """Get supported chains"""
        return [
            {"id": "tigerex", "name": "TigerEx", "type": "evm", "symbol": "TIG"},
            {"id": "ethereum", "name": "Ethereum", "type": "evm", "symbol": "ETH"},
            {"id": "bsc", "name": "BNB", "type": "evm", "symbol": "BNB"},
            {"id": "polygon", "name": "Polygon", "type": "evm", "symbol": "MATIC"},
            {"id": "arbitrum", "name": "Arbitrum", "type": "evm", "symbol": "ETH"},
            {"id": "avalanche", "name": "Avalanche", "type": "evm", "symbol": "AVAX"},
            {"id": "solana", "name": "Solana", "type": "non_evm", "symbol": "SOL"},
            {"id": "ton", "name": "TON", "type": "non_evm", "symbol": "TON"},
            {"id": "near", "name": "NEAR", "type": "non_evm", "symbol": "NEAR"},
            {"id": "aptos", "name": "Aptos", "type": "non_evm", "symbol": "APT"},
            {"id": "sui", "name": "Sui", "type": "non_evm", "symbol": "SUI"},
            {"id": "cosmos", "name": "Cosmos", "type": "non_evm", "symbol": "ATOM"},
        ]


# Create Flask app
app = Flask(__name__)
CORS(app)

tigerex_user_service = TigerExUserService()


@app.route('/tigerex/user/health')
def health():
    return jsonify({"status": "ok", "service": "tigerex", "role": "user"})


@app.route('/tigerex/user/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    return jsonify(tigerex_user_service.register(
        data.get('email', ''),
        data.get('password', ''),
        data.get('name', '')
    ))


@app.route('/tigerex/user/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    return jsonify(tigerex_user_service.login(
        data.get('email', ''),
        data.get('password', '')
    ))


@app.route('/tigerex/user/logout', methods=['POST'])
def logout():
    data = request.get_json() or {}
    return jsonify(tigerex_user_service.logout(
        data.get('session_id', '')
    ))


@app.route('/tigerex/user/me/<user_id>')
def user_me(user_id):
    return jsonify(tigerex_user_service.get_user(user_id))


@app.route('/tigerex/user/balance/<user_id>')
def user_balance(user_id):
    return jsonify(tigerex_user_service.get_balance(user_id))


@app.route('/tigerex/user/portfolio/<user_id>')
def user_portfolio(user_id):
    return jsonify(tigerex_user_service.get_portfolio(user_id))


@app.route('/tigerex/user/services')
def user_services():
    return jsonify(tigerex_user_service.get_services_status())


@app.route('/tigerex/user/prices')
def user_prices():
    return jsonify(tigerex_user_service.get_market_prices())


@app.route('/tigerex/user/chains')
def user_chains():
    return jsonify(tigerex_user_service.get_supported_chains())


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6501))
    logger.info(f"Starting TigerEx User Service on port {port}")
    app.run(host='0.0.0.0', port=port, threaded=True)