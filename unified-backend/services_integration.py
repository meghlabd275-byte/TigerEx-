/*
 * TigerEx Exchange Platform
 * Version: 7.0.0 - Consolidated Production Release
 * 
 * Complete cryptocurrency exchange platform with:
 * - CEX/DEX hybrid functionality
 * - 105+ exchange features
 * - Multi-platform support (Web, Mobile, Desktop)
 * - Enterprise-grade security
 * - White-label deployment ready
 * 
 * Production-ready implementation
 */

"""
TigerEx Services Integration Module
Integrates all backend services into unified API
"""

from typing import Dict, Any, List, Optional
import httpx
import asyncio
from fastapi import HTTPException

class ServicesIntegration:
    """Integration layer for all TigerEx backend services"""
    
    def __init__(self):
        self.services = {
            # Core Services
            "auth": "http://auth-service:3001",
            "trading": "http://trading-engine:3002",
            "wallet": "http://wallet-service:3003",
            "kyc": "http://kyc-service:3004",
            "notification": "http://notification-service:3005",
            "analytics": "http://analytics-service:3006",
            "admin": "http://admin-service:3007",
            "blockchain": "http://blockchain-service:3008",
            "p2p": "http://p2p-service:3009",
            "copy_trading": "http://copy-trading-service:3010",
            
            # Services from screenshot - ALL IMPLEMENTED
            "cross_chain_bridge": "http://cross-chain-bridge-service:4001",
            "custody_solutions": "http://custody-solutions-service:4002",
            "defi_hub": "http://defi-hub-service:4003",
            "defi_staking": "http://defi-staking-service:4004",
            "elite_traders": "http://elite-traders-service:4005",
            "eth_staking": "http://eth-staking-service:4006",
            "fan_tokens": "http://fan-tokens-service:4007",
            "fixed_savings": "http://fixed-savings-service:4008",
            "gift_card": "http://gift-card-service:4009",
            "infinity_grid": "http://infinity-grid-service:4010",
            "liquidity_mining": "http://liquidity-mining-service:4011",
            "merchant_solutions": "http://merchant-solutions-service:4012",
            "multi_chain_wallet": "http://multi-chain-wallet-service:4013",
            "mystery_box": "http://mystery-box-service:4014",
            "nft_aggregator": "http://nft-aggregator-service:4015",
            "nft_launchpad": "http://nft-launchpad-service:4016",
            "nft_loan": "http://nft-loan-service:4017",
            "nft_staking": "http://nft-staking-service:4018",
            "perpetual_swap": "http://perpetual-swap-service:4019",
            "prime_brokerage": "http://prime-brokerage-service:4020",
            "rebalancing_bot": "http://rebalancing-bot-service:4021",
            "shark_fin": "http://shark-fin-service:4022",
            "smart_order": "http://smart-order-service:4023",
            "social_feed": "http://social-feed-service:4024",
            "structured_products": "http://structured-products-service:4025",
            "swap_farming": "http://swap-farming-service:4026",
            "tiger_labs": "http://tiger-labs-service:4027",
            "tiger_pay": "http://tiger-pay-service:4028",
            "tiger_research": "http://tiger-research-service:4029",
            "trading_competition": "http://trading-competition-service:4030",
            
            # Advanced Trading Services
            "advanced_trading": "http://advanced-trading-service:3011",
            "algo_orders": "http://algo-orders-service:3012",
            "block_trading": "http://block-trading-service:3013",
            "smart_order": "http://smart-order-service:3014",
            "infinity_grid": "http://infinity-grid-service:3015",
            "rebalancing_bot": "http://rebalancing-bot-service:3016",
            "dca_bot": "http://dca-bot-service:3017",
            
            # DeFi Services
            "defi": "http://defi-service:3020",
            "defi_staking": "http://defi-staking-service:3021",
            "liquidity_mining": "http://liquidity-mining-service:3022",
            "swap_farming": "http://swap-farming-service:3023",
            "defi_hub": "http://defi-hub-service:3024",
            
            # Derivatives & Futures
            "derivatives": "http://derivatives-engine:3030",
            "futures": "http://futures-trading:3031",
            "perpetual_swap": "http://perpetual-swap-service:3032",
            "options": "http://options-trading:3033",
            
            # Earn & Savings
            "earn": "http://earn-service:3040",
            "fixed_savings": "http://fixed-savings-service:3041",
            "dual_investment": "http://dual-investment-service:3042",
            "shark_fin": "http://shark-fin-service:3043",
            "structured_products": "http://structured-products-service:3044",
            "auto_invest": "http://auto-invest-service:3045",
            
            # NFT Services
            "nft_marketplace": "http://nft-marketplace:3050",
            "nft_launchpad": "http://nft-launchpad-service:3051",
            "nft_staking": "http://nft-staking-service:3052",
            "nft_loan": "http://nft-loan-service:3053",
            "nft_aggregator": "http://nft-aggregator-service:3054",
            
            # Staking Services
            "staking": "http://staking-service:3060",
            "eth2_staking": "http://eth2-staking-service:3061",
            
            # Payment & Gateway
            "payment_gateway": "http://payment-gateway-service:3070",
            "fiat_gateway": "http://fiat-gateway-service:3071",
            "crypto_card": "http://crypto-card-service:3072",
            "tiger_pay": "http://tiger-pay-service:3073",
            "gift_card": "http://gift-card-service:3074",
            
            # Institutional Services
            "institutional": "http://institutional-services:3080",
            "prime_brokerage": "http://prime-brokerage-service:3081",
            "custody_solutions": "http://custody-solutions-service:3082",
            "merchant_solutions": "http://merchant-solutions-service:3083",
            
            # Social & Community
            "social_trading": "http://social-trading-service:3090",
            "social_feed": "http://social-feed-service:3091",
            "trading_competition": "http://trading-competition-service:3092",
            "elite_traders": "http://elite-traders-service:3093",
            "fan_tokens": "http://fan-tokens-service:3094",
            
            # Cross-chain & Multi-chain
            "cross_chain_bridge": "http://cross-chain-bridge-service:3100",
            "multi_chain_wallet": "http://multi-chain-wallet-service:3101",
            "dex_integration": "http://dex-integration:3102",
            
            # Research & Labs
            "tiger_research": "http://tiger-research-service:3110",
            "tiger_labs": "http://tiger-labs-service:3111",
            
            # Miscellaneous
            "affiliate": "http://affiliate-system:3120",
            "referral": "http://referral-program-service:3121",
            "vip_program": "http://vip-program-service:3122",
            "launchpad": "http://launchpad-service:3123",
            "launchpool": "http://launchpool-service:3124",
            "mystery_box": "http://mystery-box-service:3125",
            "convert": "http://convert-service:3126",
            "liquid_swap": "http://liquid-swap-service:3127",
        }
        
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def call_service(self, service_name: str, endpoint: str, method: str = "GET", 
                          data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Call a specific service endpoint"""
        if service_name not in self.services:
            raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
        
        url = f"{self.services[service_name]}{endpoint}"
        
        try:
            if method == "GET":
                response = await self.client.get(url, headers=headers)
            elif method == "POST":
                response = await self.client.post(url, json=data, headers=headers)
            elif method == "PUT":
                response = await self.client.put(url, json=data, headers=headers)
            elif method == "DELETE":
                response = await self.client.delete(url, headers=headers)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported method {method}")
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Service call failed: {str(e)}")
    
    async def get_all_services_status(self) -> Dict[str, Any]:
        """Get status of all services"""
        statuses = {}
        
        async def check_service(name: str, url: str):
            try:
                response = await self.client.get(f"{url}/health", timeout=5.0)
                statuses[name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "url": url
                }
            except Exception as e:
                statuses[name] = {
                    "status": "unreachable",
                    "url": url,
                    "error": str(e)
                }
        
        tasks = [check_service(name, url) for name, url in self.services.items()]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return statuses
    
    # Trading Services
    async def create_spot_order(self, user_id: int, order_data: Dict, token: str) -> Dict:
        """Create spot trading order"""
        headers = {"Authorization": f"Bearer {token}"}
        return await self.call_service("trading", "/api/orders", "POST", order_data, headers)
    
    async def create_futures_order(self, user_id: int, order_data: Dict, token: str) -> Dict:
        """Create futures trading order"""
        headers = {"Authorization": f"Bearer {token}"}
        return await self.call_service("futures", "/api/orders", "POST", order_data, headers)
    
    async def create_options_order(self, user_id: int, order_data: Dict, token: str) -> Dict:
        """Create options trading order"""
        headers = {"Authorization": f"Bearer {token}"}
        return await self.call_service("options", "/api/orders", "POST", order_data, headers)
    
    # Wallet Services
    async def get_user_wallets(self, user_id: int, token: str) -> List[Dict]:
        """Get user wallets"""
        headers = {"Authorization": f"Bearer {token}"}
        return await self.call_service("wallet", f"/api/wallets/{user_id}", "GET", headers=headers)
    
    async def create_deposit(self, user_id: int, deposit_data: Dict, token: str) -> Dict:
        """Create deposit transaction"""
        headers = {"Authorization": f"Bearer {token}"}
        return await self.call_service("wallet", "/api/deposits", "POST", deposit_data, headers)
    
    async def create_withdrawal(self, user_id: int, withdrawal_data: Dict, token: str) -> Dict:
        """Create withdrawal transaction"""
        headers = {"Authorization": f"Bearer {token}"}
        return await self.call_service("wallet", "/api/withdrawals", "POST", withdrawal_data, headers)
    
    # DeFi Services
    async def stake_tokens(self, user_id: int, stake_data: Dict, token: str) -> Dict:
        """Stake tokens"""
        headers = {"Authorization": f"Bearer {token}"}
        return await self.call_service("defi_staking", "/api/stake", "POST", stake_data, headers)
    
    async def provide_liquidity(self, user_id: int, liquidity_data: Dict, token: str) -> Dict:
        """Provide liquidity"""
        headers = {"Authorization": f"Bearer {token}"}
        return await self.call_service("liquidity_mining", "/api/provide", "POST", liquidity_data, headers)
    
    # NFT Services
    async def list_nft(self, user_id: int, nft_data: Dict, token: str) -> Dict:
        """List NFT for sale"""
        headers = {"Authorization": f"Bearer {token}"}
        return await self.call_service("nft_marketplace", "/api/list", "POST", nft_data, headers)
    
    async def buy_nft(self, user_id: int, nft_id: str, token: str) -> Dict:
        """Buy NFT"""
        headers = {"Authorization": f"Bearer {token}"}
        return await self.call_service("nft_marketplace", f"/api/buy/{nft_id}", "POST", headers=headers)
    
    # P2P Services
    async def create_p2p_order(self, user_id: int, order_data: Dict, token: str) -> Dict:
        """Create P2P order"""
        headers = {"Authorization": f"Bearer {token}"}
        return await self.call_service("p2p", "/api/orders", "POST", order_data, headers)
    
    # Copy Trading
    async def follow_trader(self, user_id: int, trader_id: int, token: str) -> Dict:
        """Follow a trader"""
        headers = {"Authorization": f"Bearer {token}"}
        return await self.call_service("copy_trading", f"/api/follow/{trader_id}", "POST", headers=headers)
    
    # Admin Services
    async def get_all_users_admin(self, token: str, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Get all users (admin)"""
        headers = {"Authorization": f"Bearer {token}"}
        return await self.call_service("admin", f"/api/users?skip={skip}&limit={limit}", "GET", headers=headers)
    
    async def update_user_admin(self, user_id: int, update_data: Dict, token: str) -> Dict:
        """Update user (admin)"""
        headers = {"Authorization": f"Bearer {token}"}
        return await self.call_service("admin", f"/api/users/{user_id}", "PUT", update_data, headers)
    
    async def approve_kyc(self, user_id: int, kyc_data: Dict, token: str) -> Dict:
        """Approve KYC (admin)"""
        headers = {"Authorization": f"Bearer {token}"}
        return await self.call_service("kyc", f"/api/approve/{user_id}", "POST", kyc_data, headers)
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

# Global instance
services = ServicesIntegration()