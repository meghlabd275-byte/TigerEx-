#!/usr/bin/env python3
"""
TigerEx Main Backend Service - Admin Interface
Integrates Wallet, Blockchain, Explorer, Exchange with Admin Controls
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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# TIGEREX MAIN SERVICE
# ============================================================
class TigerExService:
    """Main TigerEx service integrating all components"""
    
    def __init__(self):
        # Sub-services status
        self.services = {
            "wallet": {"status": "running", "port": 6100, "type": "custodial+non-custodial", "evm": True, "non_evm": True},
            "blockchain": {"status": "running", "port": 6200, "type": "full_node", "evm": True, "non_evm": True},
            "explorer": {"status": "running", "port": 6300, "type": "block_explorer", "evm": True, "non_evm": True},
            "exchange": {"status": "running", "port": 6400, "type": "cex+dex+hybrid", "custodial": True, "non_custodial": True},
        }
        
        # Users and admins
        self.admins = set()
        self.users = {}
        self.sessions = {}
        
        # Global stats
        self.stats = {
            "total_users": 0,
            "total_volume": 0,
            "total_orders": 0,
        }
        
        # Logs
        self.logs = []
        
        logger.info("TigerEx Main Service initialized")
    
    # --- Admin Methods ---
    
    def add_admin(self, admin_id: str):
        self.admins.add(admin_id)
        self._log("add_admin", admin_id)
    
    def is_admin(self, user_id: str) -> bool:
        return user_id in self.admins
    
    def create_admin(self, admin_id: str, name: str, role: str = "super") -> Dict:
        """Create admin user"""
        self.admins.add(admin_id)
        
        self.users[admin_id] = {
            "id": admin_id,
            "name": name,
            "role": role,
            "type": "admin",
            "created_at": datetime.utcnow().isoformat(),
        }
        
        self._log("create_admin", admin_id, {"role": role})
        
        return {"status": "created", "admin_id": admin_id, "role": role}
    
    def remove_admin(self, admin_id: str) -> Dict:
        """Remove admin"""
        self.admins.discard(admin_id)
        self._log("remove_admin", admin_id)
        
        return {"status": "removed", "admin_id": admin_id}
    
    def get_all_admins(self, admin_id: str) -> List[Dict]:
        """Get all admins"""
        if not self.is_admin(admin_id):
            return []
        
        return [u for u in self.users.values() if u.get("type") == "admin"]
    
    def get_all_users(self, admin_id: str, limit: int = 100) -> List[Dict]:
        """Get all users"""
        if not self.is_admin(admin_id):
            return []
        
        return list(self.users.values())[:limit]
    
    def service_control(self, admin_id: str, service: str, action: str) -> Dict:
        """Control sub-service"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        if service not in self.services:
            return {"error": "Service not found"}
        
        if action == "start":
            self.services[service]["status"] = "running"
        elif action == "stop":
            self.services[service]["status"] = "stopped"
        elif action == "restart":
            self.services[service]["status"] = "restarting"
            time.sleep(1)
            self.services[service]["status"] = "running"
        
        self._log("service_control", admin_id, {"service": service, "action": action})
        
        return {"status": action, "service": service}
    
    def get_all_services(self, admin_id: str) -> Dict:
        """Get all services status"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        return self.services
    
    def get_global_stats(self, admin_id: str) -> Dict:
        """Get global statistics"""
        if not self.is_admin(admin_id):
            return {"error": "Admin privileges required"}
        
        return {
            "total_users": len(self.users),
            "total_admins": len(self.admins),
            "active_sessions": len(self.sessions),
            "services": len(self.services),
            "running_services": sum(1 for s in self.services.values() if s["status"] == "running"),
        }
    
    def get_logs(self, admin_id: str, limit: int = 50) -> List[Dict]:
        """Get system logs"""
        if not self.is_admin(admin_id):
            return []
        
        return sorted(self.logs, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def _log(self, action: str, admin_id: str, details: Dict = None):
        """Log action"""
        self.logs.append({
            "action": action,
            "admin_id": admin_id,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        })
    
    # --- User Methods ---
    
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
            "type": "user",
            "created_at": datetime.utcnow().isoformat(),
        }
        
        session_id = self._create_session(user_id, email)
        
        return {
            "user_id": user_id,
            "email": email,
            "session_id": session_id,
            "status": "active"
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
            "last_activity": datetime.utcnow().isoformat(),
        }
        
        return session_id
    
    def verify_session(self, session_id: str) -> Dict:
        """Verify session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session["last_activity"] = datetime.utcnow().isoformat()
            return {"valid": True, "user_id": session["user_id"]}
        
        return {"valid": False}
    
    def get_services_status(self) -> Dict:
        """Get services status"""
        return {k: v["status"] for k, v in self.services.items()}
    
    def get_market_prices(self) -> Dict:
        """Get market prices"""
        return {
            "TIG": {"usd": 100.0, "btc": 0.001, "eth": 0.05},
            "BTC": {"usd": 50000.0},
            "ETH": {"usd": 3000.0},
            "USDC": {"usd": 1.0},
            "USDT": {"usd": 1.0},
        }


# ============================================================
# FLASK APPS
# ============================================================
from flask import Flask, jsonify, request
from flask_cors import CORS

admin_app = Flask(__name__)
CORS(admin_app)

tigerex_service = TigerExService()
tigerex_service.add_admin("admin001")

#
# Admin Routes
#
@admin_app.route('/tigerex/admin/health')
def admin_health():
    return jsonify({"status": "ok", "service": "tigerex", "role": "admin"})

@admin_app.route('/tigerex/admin/create-admin', methods=['POST'])
def admin_create():
    data = request.get_json() or {}
    return jsonify(tigerex_service.create_admin(
        data.get('admin_id', str(uuid.uuid4())),
        data.get('name', ''),
        data.get('role', 'super')
    ))

@admin_app.route('/tigerex/admin/remove-admin', methods=['POST'])
def admin_remove():
    data = request.get_json() or {}
    return jsonify(tigerex_service.remove_admin(
        data.get('admin_id', '')
    ))

@admin_app.route('/tigerex/admin/all-admins')
def admin_all_admins():
    admin_id = request.args.get('admin_id', '')
    return jsonify(tigerex_service.get_all_admins(admin_id))

@admin_app.route('/tigerex/admin/all-users')
def admin_all_users():
    admin_id = request.args.get('admin_id', '')
    limit = request.args.get('limit', 100, type=int)
    return jsonify(tigerex_service.get_all_users(admin_id, limit))

@admin_app.route('/tigerex/admin/service-control', methods=['POST'])
def admin_service():
    data = request.get_json() or {}
    return jsonify(tigerex_service.service_control(
        data.get('admin_id', ''),
        data.get('service', ''),
        data.get('action', 'start')
    ))

@admin_app.route('/tigerex/admin/services')
def admin_services():
    admin_id = request.args.get('admin_id', '')
    return jsonify(tigerex_service.get_all_services(admin_id))

@admin_app.route('/tigerex/admin/stats')
def admin_stats():
    admin_id = request.args.get('admin_id', '')
    return jsonify(tigerex_service.get_global_stats(admin_id))

@admin_app.route('/tigerex/admin/logs')
def admin_logs():
    admin_id = request.args.get('admin_id', '')
    limit = request.args.get('limit', 50, type=int)
    return jsonify(tigerex_service.get_logs(admin_id, limit))


def run_admin():
    port = int(os.environ.get('PORT', 6500))
    logger.info(f"Starting TigerEx Admin Service on port {port}")
    admin_app.run(host='0.0.0.0', port=port, threaded=True)


if __name__ == '__main__':
    run_admin()