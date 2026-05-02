#!/usr/bin/env python3
"""
TigerEx Service Mesh
Dynamically connects all services together
"""
import os
import sys
import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    INITIALIZING = "initializing"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


@dataclass
class ServiceEndpoint:
    """Service endpoint"""
    name: str
    url: str
    status: ServiceStatus = ServiceStatus.INITIALIZING
    last_health_check: datetime = field(default_factory=datetime.utcnow)
    response_time_ms: float = 0
    requests_count: int = 0
    errors_count: int = 0
    
    def health_check_url(self) -> str:
        return f"{self.url}/health"


class ServiceMesh:
    """
    Service mesh that dynamically connects all TigerEx services
    """
    def __init__(self):
        self.services: Dict[str, ServiceEndpoint] = {}
        self.service_registry: Dict[str, Any] = {}
        self.mesh_config = {
            "version": "3.0.0",
            "initialized_at": datetime.utcnow().isoformat(),
            "total_services": 0
        }
        
    def register_service(self, name: str, url: str):
        """Register a service"""
        self.services[name] = ServiceEndpoint(name=name, url=url)
        self.mesh_config["total_services"] = len(self.services)
        logger.info(f"Registered service: {name} at {url}")
        
    async def check_service_health(self, name: str) -> bool:
        """Check if a service is healthy"""
        service = self.services.get(name)
        if not service:
            return False
            
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                start = time.time()
                async with session.get(service.health_check_url(), timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    service.response_time_ms = (time.time() - start) * 1000
                    if resp.status == 200:
                        service.status = ServiceStatus.CONNECTED
                        service.last_health_check = datetime.utcnow()
                        service.requests_count += 1
                        return True
                    else:
                        service.status = ServiceStatus.ERROR
                        service.errors_count += 1
                        return False
        except Exception as e:
            logger.warning(f"Health check failed for {name}: {e}")
            service.status = ServiceStatus.DISCONNECTED
            service.errors_count += 1
            return False
    
    async def check_all_services(self) -> Dict[str, bool]:
        """Check all services"""
        results = {}
        for name in self.services:
            results[name] = await self.check_service_health(name)
        return results
    
    def get_service_status(self) -> Dict[str, dict]:
        """Get status of all services"""
        status = {}
        for name, service in self.services.items():
            status[name] = {
                "url": service.url,
                "status": service.status.value,
                "last_health_check": service.last_health_check.isoformat(),
                "response_time_ms": service.response_time_ms,
                "requests_count": service.requests_count,
                "errors_count": service.errors_count
            }
        return status
    
    async def route_request(self, service_name: str, method: str, path: str, data: dict = None) -> dict:
        """Route a request to a service"""
        service = self.services.get(service_name)
        if not service:
            return {"error": f"Service {service_name} not found"}
            
        try:
            import aiohttp
            url = f"{service.url}{path}"
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(url, params=data) as resp:
                        return await resp.json()
                elif method == "POST":
                    async with session.post(url, json=data) as resp:
                        return await resp.json()
                elif method == "PUT":
                    async with session.put(url, json=data) as resp:
                        return await resp.json()
                elif method == "DELETE":
                    async with session.delete(url, json=data) as resp:
                        return await resp.json()
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {"error": str(e)}
    
    def get_mesh_info(self) -> dict:
        """Get mesh information"""
        connected = sum(1 for s in self.services.values() if s.status == ServiceStatus.CONNECTED)
        return {
            **self.mesh_config,
            "total_services": len(self.services),
            "connected_services": connected,
            "services": list(self.services.keys())
        }


# ==================== DYNAMIC SERVICE CONNECTOR ====================

class DynamicServiceConnector:
    """
    Dynamically connects all TigerEx backend services
    """
    def __init__(self):
        self.mesh = ServiceMesh()
        self.config = self._load_config()
        self._register_default_services()
        
    def _load_config(self) -> dict:
        """Load service configuration"""
        return {
            "api_gateway": os.environ.get("API_GATEWAY_URL", "http://localhost:3000"),
            "auth_service": os.environ.get("AUTH_SERVICE_URL", "http://localhost:5001"),
            "trading_engine": os.environ.get("TRADING_ENGINE_URL", "http://localhost:5002"),
            "wallet_service": os.environ.get("WALLET_SERVICE_URL", "http://localhost:5003"),
            "market_data": os.environ.get("MARKET_DATA_URL", "http://localhost:5004"),
            "notification_service": os.environ.get("NOTIFICATION_SERVICE_URL", "http://localhost:5005"),
            "admin_service": os.environ.get("ADMIN_SERVICE_URL", "http://localhost:5006"),
            "blockchain_service": os.environ.get("BLOCKCHAIN_SERVICE_URL", "http://localhost:5007"),
        }
    
    def _register_default_services(self):
        """Register all default services"""
        services = [
            ("api-gateway", self.config["api_gateway"]),
            ("auth-service", self.config["auth_service"]),
            ("trading-engine", self.config["trading_engine"]),
            ("wallet-service", self.config["wallet_service"]),
            ("market-data", self.config["market_data"]),
            ("notification-service", self.config["notification_service"]),
            ("admin-service", self.config["admin_service"]),
            ("blockchain-service", self.config["blockchain_service"]),
        ]
        
        for name, url in services:
            self.mesh.register_service(name, url)
    
    def get_connector_info(self) -> dict:
        """Get connector information"""
        return {
            "mesh": self.mesh.get_mesh_info(),
            "config": self.config,
            "services": self.mesh.get_service_status()
        }


# ==================== SERVICE DISCOVERY ====================

class ServiceDiscovery:
    """Dynamic service discovery"""
    
    def __init__(self):
        self.discovered_services: Dict[str, List[str]] = {}
        
    def discover_services(self):
        """Auto-discover services from environment"""
        for key, value in os.environ.items():
            if key.endswith("_URL") and key not in ["API_GATEWAY_URL"]:
                service_name = key.replace("_URL", "").lower()
                self.discovered_services[service_name] = [value]
                logger.info(f"Discovered service: {service_name} at {value}")
    
    def get_service_url(self, service_name: str) -> Optional[str]:
        return self.discovered_services.get(service_name, [None])[0]
    
    def get_all_services(self) -> Dict[str, str]:
        return {name: urls[0] for name, urls in self.discovered_services.items()}


# ==================== BACKUP & FAILOVER ====================

class BackupService:
    """Backup service for failover"""
    
    def __init__(self):
        self.backup_urls: Dict[str, List[str]] = {}
        
    def register_backup(self, service_name: str, backup_urls: List[str]):
        self.backup_urls[service_name] = backup_urls
        
    async def get_active_url(self, service_name: str) -> Optional[str]:
        import aiohttp
        
        primary = os.environ.get(f"{service_name.upper()}_URL")
        if primary:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{primary}/health", timeout=aiohttp.ClientTimeout(total=3)) as resp:
                        if resp.status == 200:
                            return primary
            except:
                pass
        
        backups = self.backup_urls.get(service_name, [])
        for url in backups:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{url}/health", timeout=aiohttp.ClientTimeout(total=3)) as resp:
                        if resp.status == 200:
                            logger.warning(f"Failed over to backup: {url}")
                            return url
            except:
                continue
        return None


# ==================== FLASK APP ====================

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

connector = DynamicServiceConnector()
discovery = ServiceDiscovery()
backup_service = BackupService()

@app.route('/mesh/health', methods=['GET'])
def mesh_health():
    return jsonify(connector.get_connector_info())

@app.route('/mesh/services', methods=['GET'])
def list_services():
    return jsonify(connector.get_connector_info())

@app.route('/mesh/discover', methods=['POST'])
def discover():
    discovery.discover_services()
    return jsonify({"success": True, "services": discovery.get_all_services()})

@app.route('/mesh/status', methods=['GET'])
def mesh_status():
    return jsonify({
        "mesh_info": connector.mesh.get_mesh_info(),
        "service_status": connector.mesh.get_service_status(),
        "discovered": discovery.get_all_services()
    })

@app.route('/mesh/service/<name>', methods=['GET'])
def get_service(name):
    status = connector.mesh.get_service_status()
    if name in status:
        return jsonify({"success": True, "service": status[name]})
    return jsonify({"success": False, "error": "Service not found"}), 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5100))
    app.run(host='0.0.0.0', port=port, threaded=True)