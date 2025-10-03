#!/usr/bin/env python3
"""
TigerEx White Label Admin Control Panel
Complete admin control interface for all white-label deployments
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
import json

from white_label_master import (
    WhiteLabelMasterSystem,
    DeploymentType,
    UserRole,
    PermissionLevel,
    WhiteLabelConfig,
    AdminUser,
    InstitutionalClient
)

# ==================== ADMIN CONTROL PANEL ====================

class AdminControlPanel:
    """Complete admin control panel for white-label system"""
    
    def __init__(self, master_system: WhiteLabelMasterSystem):
        self.system = master_system
    
    # ==================== DEPLOYMENT MANAGEMENT ====================
    
    async def create_hybrid_exchange(
        self,
        domain: str,
        brand_name: str,
        admin_email: str,
        admin_password: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create hybrid exchange deployment"""
        
        config = await self.system.create_deployment(
            deployment_type=DeploymentType.HYBRID_EXCHANGE,
            domain=domain,
            brand_name=brand_name,
            admin_email=admin_email,
            admin_password=admin_password,
            **kwargs
        )
        
        return {
            'deployment_id': config.deployment_id,
            'domain': config.domain,
            'brand_name': config.brand_name,
            'api_keys': config.api_keys,
            'features_enabled': config.features_enabled,
            'status': 'active',
            'admin_panel_url': f"https://{domain}/admin",
            'api_documentation': f"https://{domain}/api/docs"
        }
    
    async def create_crypto_wallet(
        self,
        domain: str,
        brand_name: str,
        admin_email: str,
        admin_password: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create crypto wallet deployment"""
        
        config = await self.system.create_deployment(
            deployment_type=DeploymentType.CRYPTO_WALLET,
            domain=domain,
            brand_name=brand_name,
            admin_email=admin_email,
            admin_password=admin_password,
            **kwargs
        )
        
        return {
            'deployment_id': config.deployment_id,
            'domain': config.domain,
            'brand_name': config.brand_name,
            'supported_chains': config.blockchain_networks,
            'wallet_features': config.features_enabled,
            'status': 'active',
            'download_links': {
                'ios': f"https://{domain}/download/ios",
                'android': f"https://{domain}/download/android",
                'chrome_extension': f"https://{domain}/download/chrome"
            }
        }
    
    async def create_blockchain_explorer(
        self,
        domain: str,
        brand_name: str,
        admin_email: str,
        admin_password: str,
        blockchain_network: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create blockchain explorer deployment"""
        
        config = await self.system.create_deployment(
            deployment_type=DeploymentType.BLOCKCHAIN_EXPLORER,
            domain=domain,
            brand_name=brand_name,
            admin_email=admin_email,
            admin_password=admin_password,
            blockchain_networks=[blockchain_network],
            **kwargs
        )
        
        return {
            'deployment_id': config.deployment_id,
            'domain': config.domain,
            'brand_name': config.brand_name,
            'blockchain_network': blockchain_network,
            'explorer_features': config.features_enabled,
            'status': 'active',
            'api_endpoint': f"https://{domain}/api/v1"
        }
    
    async def create_dex(
        self,
        domain: str,
        brand_name: str,
        admin_email: str,
        admin_password: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create DEX deployment"""
        
        config = await self.system.create_deployment(
            deployment_type=DeploymentType.DEX,
            domain=domain,
            brand_name=brand_name,
            admin_email=admin_email,
            admin_password=admin_password,
            **kwargs
        )
        
        return {
            'deployment_id': config.deployment_id,
            'domain': config.domain,
            'brand_name': config.brand_name,
            'dex_features': config.features_enabled,
            'supported_chains': config.blockchain_networks,
            'status': 'active',
            'smart_contracts': {
                'router': f"0x{config.deployment_id[:40]}",
                'factory': f"0x{config.deployment_id[40:80]}",
                'governance': f"0x{config.deployment_id[80:120]}"
            }
        }
    
    async def create_cex(
        self,
        domain: str,
        brand_name: str,
        admin_email: str,
        admin_password: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create CEX deployment"""
        
        config = await self.system.create_deployment(
            deployment_type=DeploymentType.CEX,
            domain=domain,
            brand_name=brand_name,
            admin_email=admin_email,
            admin_password=admin_password,
            **kwargs
        )
        
        return {
            'deployment_id': config.deployment_id,
            'domain': config.domain,
            'brand_name': config.brand_name,
            'cex_features': config.features_enabled,
            'trading_pairs': config.supported_currencies,
            'status': 'active',
            'trading_url': f"https://{domain}/trade",
            'api_endpoint': f"https://{domain}/api/v1"
        }
    
    async def create_institutional_platform(
        self,
        domain: str,
        brand_name: str,
        admin_email: str,
        admin_password: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create institutional platform deployment"""
        
        config = await self.system.create_deployment(
            deployment_type=DeploymentType.INSTITUTIONAL_PLATFORM,
            domain=domain,
            brand_name=brand_name,
            admin_email=admin_email,
            admin_password=admin_password,
            **kwargs
        )
        
        return {
            'deployment_id': config.deployment_id,
            'domain': config.domain,
            'brand_name': config.brand_name,
            'institutional_features': config.features_enabled,
            'status': 'active',
            'api_endpoints': {
                'rest': f"https://{domain}/api/v1",
                'websocket': f"wss://{domain}/ws",
                'fix': f"fix://{domain}:4000"
            }
        }
    
    # ==================== USER MANAGEMENT ====================
    
    async def create_admin(
        self,
        deployment_id: str,
        email: str,
        password: str,
        role: str,
        permissions: Dict[str, str]
    ) -> Dict[str, Any]:
        """Create admin user"""
        
        role_enum = UserRole[role.upper()]
        permissions_enum = {
            k: PermissionLevel[v.upper()]
            for k, v in permissions.items()
        }
        
        admin = await self.system.create_admin_user(
            deployment_id=deployment_id,
            email=email,
            password=password,
            role=role_enum,
            permissions=permissions_enum
        )
        
        return {
            'user_id': admin.user_id,
            'email': admin.email,
            'role': admin.role.value,
            'permissions': {k: v.value for k, v in admin.permissions.items()},
            'created_at': admin.created_at.isoformat(),
            'is_active': admin.is_active
        }
    
    async def update_admin_permissions(
        self,
        user_id: str,
        permissions: Dict[str, str]
    ) -> Dict[str, Any]:
        """Update admin permissions"""
        
        permissions_enum = {
            k: PermissionLevel[v.upper()]
            for k, v in permissions.items()
        }
        
        admin = await self.system.update_admin_permissions(
            user_id=user_id,
            permissions=permissions_enum
        )
        
        return {
            'user_id': admin.user_id,
            'email': admin.email,
            'permissions': {k: v.value for k, v in admin.permissions.items()},
            'updated': True
        }
    
    async def deactivate_admin(self, user_id: str) -> Dict[str, Any]:
        """Deactivate admin user"""
        
        success = await self.system.deactivate_admin_user(user_id)
        
        return {
            'user_id': user_id,
            'deactivated': success
        }
    
    async def list_admins(self, deployment_id: str) -> List[Dict[str, Any]]:
        """List all admin users"""
        
        admins = await self.system.list_admin_users(deployment_id)
        
        return [
            {
                'user_id': admin.user_id,
                'email': admin.email,
                'role': admin.role.value,
                'permissions': {k: v.value for k, v in admin.permissions.items()},
                'created_at': admin.created_at.isoformat(),
                'last_login': admin.last_login.isoformat() if admin.last_login else None,
                'is_active': admin.is_active
            }
            for admin in admins
        ]
    
    # ==================== INSTITUTIONAL CLIENT MANAGEMENT ====================
    
    async def create_institutional_client(
        self,
        deployment_id: str,
        company_name: str,
        domain: str,
        trading_limits: Dict[str, float],
        features: List[str]
    ) -> Dict[str, Any]:
        """Create institutional client"""
        
        client = await self.system.create_institutional_client(
            deployment_id=deployment_id,
            company_name=company_name,
            domain=domain,
            trading_limits=trading_limits,
            features_enabled=features
        )
        
        return {
            'client_id': client.client_id,
            'company_name': client.company_name,
            'domain': client.domain,
            'api_key': client.api_key,
            'api_secret': client.api_secret,
            'trading_limits': client.trading_limits,
            'features_enabled': client.features_enabled,
            'created_at': client.created_at.isoformat(),
            'is_active': client.is_active
        }
    
    async def update_institutional_limits(
        self,
        client_id: str,
        trading_limits: Dict[str, float]
    ) -> Dict[str, Any]:
        """Update institutional client limits"""
        
        client = await self.system.update_institutional_limits(
            client_id=client_id,
            trading_limits=trading_limits
        )
        
        return {
            'client_id': client.client_id,
            'trading_limits': client.trading_limits,
            'updated': True
        }
    
    async def enable_institutional_features(
        self,
        client_id: str,
        features: List[str]
    ) -> Dict[str, Any]:
        """Enable features for institutional client"""
        
        client = await self.system.enable_institutional_features(
            client_id=client_id,
            features=features
        )
        
        return {
            'client_id': client.client_id,
            'features_enabled': client.features_enabled,
            'updated': True
        }
    
    async def deactivate_institutional_client(
        self,
        client_id: str
    ) -> Dict[str, Any]:
        """Deactivate institutional client"""
        
        success = await self.system.deactivate_institutional_client(client_id)
        
        return {
            'client_id': client_id,
            'deactivated': success
        }
    
    # ==================== DOMAIN MANAGEMENT ====================
    
    async def connect_custom_domain(
        self,
        deployment_id: str,
        domain: str,
        ssl_enabled: bool = True
    ) -> Dict[str, Any]:
        """Connect custom domain to deployment"""
        
        result = await self.system.connect_domain(
            deployment_id=deployment_id,
            domain=domain,
            ssl_enabled=ssl_enabled
        )
        
        return result
    
    # ==================== DEPLOYMENT OPERATIONS ====================
    
    async def get_deployment_info(
        self,
        deployment_id: str
    ) -> Dict[str, Any]:
        """Get deployment information"""
        
        config = await self.system.get_deployment(deployment_id)
        
        return {
            'deployment_id': config.deployment_id,
            'deployment_type': config.deployment_type.value,
            'domain': config.domain,
            'brand_name': config.brand_name,
            'brand_logo_url': config.brand_logo_url,
            'primary_color': config.primary_color,
            'secondary_color': config.secondary_color,
            'features_enabled': config.features_enabled,
            'blockchain_networks': config.blockchain_networks,
            'supported_currencies': config.supported_currencies,
            'created_at': config.created_at.isoformat(),
            'updated_at': config.updated_at.isoformat()
        }
    
    async def list_all_deployments(self) -> List[Dict[str, Any]]:
        """List all deployments"""
        
        deployments = await self.system.list_deployments()
        
        return [
            {
                'deployment_id': config.deployment_id,
                'deployment_type': config.deployment_type.value,
                'domain': config.domain,
                'brand_name': config.brand_name,
                'status': 'active',
                'created_at': config.created_at.isoformat()
            }
            for config in deployments
        ]
    
    async def update_deployment_config(
        self,
        deployment_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Update deployment configuration"""
        
        config = await self.system.update_deployment(
            deployment_id=deployment_id,
            **kwargs
        )
        
        return {
            'deployment_id': config.deployment_id,
            'updated': True,
            'updated_at': config.updated_at.isoformat()
        }
    
    async def delete_deployment(
        self,
        deployment_id: str
    ) -> Dict[str, Any]:
        """Delete deployment"""
        
        success = await self.system.delete_deployment(deployment_id)
        
        return {
            'deployment_id': deployment_id,
            'deleted': success
        }
    
    # ==================== ANALYTICS & REPORTING ====================
    
    async def get_deployment_analytics(
        self,
        deployment_id: str
    ) -> Dict[str, Any]:
        """Get deployment analytics"""
        
        return {
            'deployment_id': deployment_id,
            'analytics': {
                'total_users': 0,
                'active_users': 0,
                'total_volume': 0.0,
                'total_transactions': 0,
                'revenue': 0.0
            },
            'timestamp': datetime.now().isoformat()
        }
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""
        
        return {
            'status': 'healthy',
            'total_deployments': len(self.system.deployments),
            'active_deployments': len([
                d for d in self.system.deployments.values()
            ]),
            'total_admin_users': len(self.system.admin_users),
            'total_institutional_clients': len(self.system.institutional_clients),
            'timestamp': datetime.now().isoformat()
        }

# ==================== EXAMPLE USAGE ====================

async def main():
    """Example usage of Admin Control Panel"""
    
    master_system = WhiteLabelMasterSystem()
    admin_panel = AdminControlPanel(master_system)
    
    # Create hybrid exchange
    exchange = await admin_panel.create_hybrid_exchange(
        domain="myexchange.com",
        brand_name="My Exchange",
        admin_email="admin@myexchange.com",
        admin_password="secure_password",
        primary_color="#1a73e8",
        features_enabled=['spot', 'margin', 'futures']
    )
    
    print(f"Hybrid Exchange Created: {json.dumps(exchange, indent=2)}")
    
    # Create institutional client
    client = await admin_panel.create_institutional_client(
        deployment_id=exchange['deployment_id'],
        company_name="Big Corp",
        domain="bigcorp.com",
        trading_limits={
            'daily_volume': 10000000.0,
            'single_trade': 1000000.0
        },
        features=['otc', 'prime_brokerage']
    )
    
    print(f"Institutional Client Created: {json.dumps(client, indent=2)}")
    
    # Get system health
    health = await admin_panel.get_system_health()
    print(f"System Health: {json.dumps(health, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())