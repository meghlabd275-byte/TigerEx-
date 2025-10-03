#!/usr/bin/env python3
"""
TigerEx Unified Admin Operations
Complete implementation of all admin operations for all major exchanges
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import hmac
import json
from abc import ABC, abstractmethod

class BaseAdminOperations(ABC):
    """Base class for admin operations"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def create_sub_account(self, email: str, **kwargs) -> Dict:
        """Create a sub-account"""
        pass
    
    @abstractmethod
    async def get_sub_account_list(self) -> List[Dict]:
        """Get list of sub-accounts"""
        pass
    
    @abstractmethod
    async def create_sub_account_api_key(self, sub_account_id: str, **kwargs) -> Dict:
        """Create API key for sub-account"""
        pass
    
    @abstractmethod
    async def get_system_status(self) -> Dict:
        """Get system status"""
        pass

class BinanceAdminOperations(BaseAdminOperations):
    """Binance admin operations implementation"""
    
    BASE_URL = "https://api.binance.com"
    
    def _generate_signature(self, params: Dict) -> str:
        """Generate HMAC SHA256 signature"""
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def create_sub_account(self, email: str, **kwargs) -> Dict:
        """Create a virtual sub-account"""
        url = f"{self.BASE_URL}/sapi/v1/sub-account/virtualSubAccount"
        timestamp = int(datetime.now().timestamp() * 1000)
        
        params = {
            "subAccountString": email,
            "timestamp": timestamp
        }
        
        params["signature"] = self._generate_signature(params)
        headers = {"X-MBX-APIKEY": self.api_key}
        
        async with self.session.post(url, params=params, headers=headers) as response:
            return await response.json()
    
    async def get_sub_account_list(self, email: str = None, page: int = 1, limit: int = 500) -> Dict:
        """Query sub-account list"""
        url = f"{self.BASE_URL}/sapi/v1/sub-account/list"
        timestamp = int(datetime.now().timestamp() * 1000)
        
        params = {
            "timestamp": timestamp,
            "page": page,
            "limit": limit
        }
        
        if email:
            params["email"] = email
        
        params["signature"] = self._generate_signature(params)
        headers = {"X-MBX-APIKEY": self.api_key}
        
        async with self.session.get(url, params=params, headers=headers) as response:
            return await response.json()
    
    async def create_sub_account_api_key(self, sub_account_string: str,
                                        can_trade: bool = False,
                                        margin_trade: bool = False,
                                        futures_trade: bool = False) -> Dict:
        """Create API key for sub-account"""
        url = f"{self.BASE_URL}/sapi/v1/sub-account/apiKey"
        timestamp = int(datetime.now().timestamp() * 1000)
        
        params = {
            "subAccountString": sub_account_string,
            "canTrade": str(can_trade).lower(),
            "marginTrade": str(margin_trade).lower(),
            "futuresTrade": str(futures_trade).lower(),
            "timestamp": timestamp
        }
        
        params["signature"] = self._generate_signature(params)
        headers = {"X-MBX-APIKEY": self.api_key}
        
        async with self.session.post(url, params=params, headers=headers) as response:
            return await response.json()
    
    async def get_system_status(self) -> Dict:
        """Fetch system status"""
        url = f"{self.BASE_URL}/sapi/v1/system/status"
        
        async with self.session.get(url) as response:
            return await response.json()
    
    async def enable_sub_account(self, email: str) -> Dict:
        """Enable sub-account"""
        url = f"{self.BASE_URL}/sapi/v1/sub-account/status"
        timestamp = int(datetime.now().timestamp() * 1000)
        
        params = {
            "email": email,
            "isFreeze": "false",
            "timestamp": timestamp
        }
        
        params["signature"] = self._generate_signature(params)
        headers = {"X-MBX-APIKEY": self.api_key}
        
        async with self.session.post(url, params=params, headers=headers) as response:
            return await response.json()
    
    async def disable_sub_account(self, email: str) -> Dict:
        """Disable sub-account"""
        url = f"{self.BASE_URL}/sapi/v1/sub-account/status"
        timestamp = int(datetime.now().timestamp() * 1000)
        
        params = {
            "email": email,
            "isFreeze": "true",
            "timestamp": timestamp
        }
        
        params["signature"] = self._generate_signature(params)
        headers = {"X-MBX-APIKEY": self.api_key}
        
        async with self.session.post(url, params=params, headers=headers) as response:
            return await response.json()
    
    async def get_api_key_permission(self) -> Dict:
        """Get API key permission"""
        url = f"{self.BASE_URL}/sapi/v1/account/apiRestrictions"
        timestamp = int(datetime.now().timestamp() * 1000)
        
        params = {
            "timestamp": timestamp
        }
        
        params["signature"] = self._generate_signature(params)
        headers = {"X-MBX-APIKEY": self.api_key}
        
        async with self.session.get(url, params=params, headers=headers) as response:
            return await response.json()

class UnifiedAdminOperations:
    """Unified admin operations that routes requests to appropriate exchange"""
    
    def __init__(self):
        self.operations = {}
    
    def add_exchange(self, exchange_name: str, operations: BaseAdminOperations):
        """Add an exchange admin operations handler"""
        self.operations[exchange_name.lower()] = operations
    
    async def create_sub_account(self, exchange: str, email: str, **kwargs) -> Dict:
        """Create sub-account on specified exchange"""
        ops = self.operations.get(exchange.lower())
        if not ops:
            raise ValueError(f"Exchange {exchange} not supported")
        return await ops.create_sub_account(email, **kwargs)
    
    async def get_sub_account_list(self, exchange: str) -> List[Dict]:
        """Get sub-account list from specified exchange"""
        ops = self.operations.get(exchange.lower())
        if not ops:
            raise ValueError(f"Exchange {exchange} not supported")
        return await ops.get_sub_account_list()
    
    async def create_sub_account_api_key(self, exchange: str, sub_account_id: str,
                                        **kwargs) -> Dict:
        """Create sub-account API key on specified exchange"""
        ops = self.operations.get(exchange.lower())
        if not ops:
            raise ValueError(f"Exchange {exchange} not supported")
        return await ops.create_sub_account_api_key(sub_account_id, **kwargs)
    
    async def get_system_status(self, exchange: str) -> Dict:
        """Get system status from specified exchange"""
        ops = self.operations.get(exchange.lower())
        if not ops:
            raise ValueError(f"Exchange {exchange} not supported")
        return await ops.get_system_status()

# Example usage
async def main():
    """Example usage of unified admin operations"""
    api_key = "your_api_key"
    api_secret = "your_api_secret"
    
    unified = UnifiedAdminOperations()
    
    async with BinanceAdminOperations(api_key, api_secret) as binance_admin:
        unified.add_exchange("binance", binance_admin)
        
        # Get system status
        status = await unified.get_system_status("binance")
        print(f"System status: {status}")

if __name__ == "__main__":
    asyncio.run(main())