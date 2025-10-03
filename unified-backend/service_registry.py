"""
TigerEx Service Registry - Complete Service Catalog
Registry of all 121+ backend services with their endpoints and capabilities
"""

from typing import Dict, List, Any
from enum import Enum

class ServiceCategory(Enum):
    CORE = "core"
    TRADING = "trading"
    DEFI = "defi"
    NFT = "nft"
    PAYMENT = "payment"
    INSTITUTIONAL = "institutional"
    SOCIAL = "social"
    CROSS_CHAIN = "cross_chain"
    RESEARCH = "research"
    EARN = "earn"
    STAKING = "staking"
    BOTS = "bots"

class ServiceRegistry:
    """Complete registry of all TigerEx backend services"""
    
    def __init__(self):
        self.services = {
            # Services from screenshot
            "cross-chain-bridge-service": {
                "name": "Cross-chain Bridge Service",
                "category": ServiceCategory.CROSS_CHAIN,
                "port": 4001,
                "endpoints": ["/bridge", "/transfer", "/status"],
                "admin_endpoints": ["/admin/bridges", "/admin/configure"],
                "description": "Cross-chain asset bridging"
            },
            "custody-solutions-service": {
                "name": "Custody Solutions Service",
                "category": ServiceCategory.INSTITUTIONAL,
                "port": 4002,
                "endpoints": ["/custody", "/vault", "/withdraw"],
                "admin_endpoints": ["/admin/custody", "/admin/vaults"],
                "description": "Institutional custody solutions"
            },
            "defi-hub-service": {
                "name": "DeFi Hub Service",
                "category": ServiceCategory.DEFI,
                "port": 4003,
                "endpoints": ["/protocols", "/yield", "/pools"],
                "admin_endpoints": ["/admin/protocols", "/admin/configure"],
                "description": "DeFi protocol aggregation"
            },
            "defi-staking-service": {
                "name": "DeFi Staking Service",
                "category": ServiceCategory.DEFI,
                "port": 4004,
                "endpoints": ["/stake", "/unstake", "/rewards"],
                "admin_endpoints": ["/admin/pools", "/admin/rewards"],
                "description": "DeFi staking and rewards"
            },
            "elite-traders-service": {
                "name": "Elite Traders Service",
                "category": ServiceCategory.SOCIAL,
                "port": 4005,
                "endpoints": ["/traders", "/follow", "/stats"],
                "admin_endpoints": ["/admin/traders", "/admin/verify"],
                "description": "Elite trader profiles and following"
            },
            "eth-staking-service": {
                "name": "ETH Staking Service",
                "category": ServiceCategory.STAKING,
                "port": 4006,
                "endpoints": ["/stake", "/unstake", "/rewards"],
                "admin_endpoints": ["/admin/validators", "/admin/configure"],
                "description": "Ethereum 2.0 staking"
            },
            "fan-tokens-service": {
                "name": "Fan Tokens Service",
                "category": ServiceCategory.SOCIAL,
                "port": 4007,
                "endpoints": ["/tokens", "/buy", "/rewards"],
                "admin_endpoints": ["/admin/tokens", "/admin/create"],
                "description": "Fan token management"
            },
            "fixed-savings-service": {
                "name": "Fixed Savings Service",
                "category": ServiceCategory.EARN,
                "port": 4008,
                "endpoints": ["/products", "/subscribe", "/redeem"],
                "admin_endpoints": ["/admin/products", "/admin/rates"],
                "description": "Fixed-term savings products"
            },
            "gift-card-service": {
                "name": "Gift Card Service",
                "category": ServiceCategory.PAYMENT,
                "port": 4009,
                "endpoints": ["/cards", "/purchase", "/redeem"],
                "admin_endpoints": ["/admin/cards", "/admin/inventory"],
                "description": "Crypto gift cards"
            },
            "infinity-grid-service": {
                "name": "Infinity Grid Service",
                "category": ServiceCategory.BOTS,
                "port": 4010,
                "endpoints": ["/create", "/stop", "/stats"],
                "admin_endpoints": ["/admin/grids", "/admin/configure"],
                "description": "Infinity grid trading bot"
            },
            "liquidity-mining-service": {
                "name": "Liquidity Mining Service",
                "category": ServiceCategory.DEFI,
                "port": 4011,
                "endpoints": ["/pools", "/provide", "/rewards"],
                "admin_endpoints": ["/admin/pools", "/admin/rewards"],
                "description": "Liquidity mining and rewards"
            },
            "merchant-solutions-service": {
                "name": "Merchant Solutions Service",
                "category": ServiceCategory.INSTITUTIONAL,
                "port": 4012,
                "endpoints": ["/merchants", "/payments", "/settlements"],
                "admin_endpoints": ["/admin/merchants", "/admin/configure"],
                "description": "Merchant payment solutions"
            },
            "multi-chain-wallet-service": {
                "name": "Multi-chain Wallet Service",
                "category": ServiceCategory.CROSS_CHAIN,
                "port": 4013,
                "endpoints": ["/wallets", "/balance", "/transfer"],
                "admin_endpoints": ["/admin/chains", "/admin/configure"],
                "description": "Multi-chain wallet management"
            },
            "mystery-box-service": {
                "name": "Mystery Box Service",
                "category": ServiceCategory.NFT,
                "port": 4014,
                "endpoints": ["/boxes", "/open", "/rewards"],
                "admin_endpoints": ["/admin/boxes", "/admin/configure"],
                "description": "NFT mystery boxes"
            },
            "nft-aggregator-service": {
                "name": "NFT Aggregator Service",
                "category": ServiceCategory.NFT,
                "port": 4015,
                "endpoints": ["/collections", "/search", "/stats"],
                "admin_endpoints": ["/admin/sources", "/admin/configure"],
                "description": "NFT marketplace aggregation"
            },
            "nft-launchpad-service": {
                "name": "NFT Launchpad Service",
                "category": ServiceCategory.NFT,
                "port": 4016,
                "endpoints": ["/projects", "/mint", "/participate"],
                "admin_endpoints": ["/admin/projects", "/admin/approve"],
                "description": "NFT project launchpad"
            },
            "nft-loan-service": {
                "name": "NFT Loan Service",
                "category": ServiceCategory.NFT,
                "port": 4017,
                "endpoints": ["/loans", "/borrow", "/repay"],
                "admin_endpoints": ["/admin/loans", "/admin/configure"],
                "description": "NFT-backed loans"
            },
            "nft-staking-service": {
                "name": "NFT Staking Service",
                "category": ServiceCategory.NFT,
                "port": 4018,
                "endpoints": ["/stake", "/unstake", "/rewards"],
                "admin_endpoints": ["/admin/pools", "/admin/configure"],
                "description": "NFT staking and rewards"
            },
            "perpetual-swap-service": {
                "name": "Perpetual Swap Service",
                "category": ServiceCategory.TRADING,
                "port": 4019,
                "endpoints": ["/contracts", "/trade", "/positions"],
                "admin_endpoints": ["/admin/contracts", "/admin/configure"],
                "description": "Perpetual swap trading"
            },
            "prime-brokerage-service": {
                "name": "Prime Brokerage Service",
                "category": ServiceCategory.INSTITUTIONAL,
                "port": 4020,
                "endpoints": ["/accounts", "/execute", "/reports"],
                "admin_endpoints": ["/admin/clients", "/admin/configure"],
                "description": "Prime brokerage services"
            },
            "rebalancing-bot-service": {
                "name": "Rebalancing Bot Service",
                "category": ServiceCategory.BOTS,
                "port": 4021,
                "endpoints": ["/create", "/stop", "/stats"],
                "admin_endpoints": ["/admin/bots", "/admin/configure"],
                "description": "Portfolio rebalancing bot"
            },
            "shark-fin-service": {
                "name": "Shark Fin Service",
                "category": ServiceCategory.EARN,
                "port": 4022,
                "endpoints": ["/products", "/subscribe", "/redeem"],
                "admin_endpoints": ["/admin/products", "/admin/configure"],
                "description": "Shark fin structured products"
            },
            "smart-order-service": {
                "name": "Smart Order Service",
                "category": ServiceCategory.TRADING,
                "port": 4023,
                "endpoints": ["/create", "/cancel", "/status"],
                "admin_endpoints": ["/admin/orders", "/admin/configure"],
                "description": "Smart order routing"
            },
            "social-feed-service": {
                "name": "Social Feed Service",
                "category": ServiceCategory.SOCIAL,
                "port": 4024,
                "endpoints": ["/feed", "/post", "/like"],
                "admin_endpoints": ["/admin/posts", "/admin/moderate"],
                "description": "Social trading feed"
            },
            "structured-products-service": {
                "name": "Structured Products Service",
                "category": ServiceCategory.EARN,
                "port": 4025,
                "endpoints": ["/products", "/subscribe", "/redeem"],
                "admin_endpoints": ["/admin/products", "/admin/configure"],
                "description": "Structured financial products"
            },
            "swap-farming-service": {
                "name": "Swap Farming Service",
                "category": ServiceCategory.DEFI,
                "port": 4026,
                "endpoints": ["/farms", "/stake", "/harvest"],
                "admin_endpoints": ["/admin/farms", "/admin/configure"],
                "description": "Swap and yield farming"
            },
            "tiger-labs-service": {
                "name": "Tiger Labs Service",
                "category": ServiceCategory.RESEARCH,
                "port": 4027,
                "endpoints": ["/projects", "/participate", "/results"],
                "admin_endpoints": ["/admin/projects", "/admin/approve"],
                "description": "Innovation lab and experiments"
            },
            "tiger-pay-service": {
                "name": "Tiger Pay Service",
                "category": ServiceCategory.PAYMENT,
                "port": 4028,
                "endpoints": ["/pay", "/request", "/history"],
                "admin_endpoints": ["/admin/transactions", "/admin/configure"],
                "description": "Crypto payment processing"
            },
            "tiger-research-service": {
                "name": "Tiger Research Service",
                "category": ServiceCategory.RESEARCH,
                "port": 4029,
                "endpoints": ["/reports", "/analysis", "/subscribe"],
                "admin_endpoints": ["/admin/reports", "/admin/publish"],
                "description": "Market research and analysis"
            },
            "trading-competition-service": {
                "name": "Trading Competition Service",
                "category": ServiceCategory.SOCIAL,
                "port": 4030,
                "endpoints": ["/competitions", "/join", "/leaderboard"],
                "admin_endpoints": ["/admin/competitions", "/admin/create"],
                "description": "Trading competitions and contests"
            },
            
            # Additional core services
            "auth-service": {
                "name": "Authentication Service",
                "category": ServiceCategory.CORE,
                "port": 3001,
                "endpoints": ["/login", "/register", "/verify"],
                "admin_endpoints": ["/admin/users", "/admin/sessions"],
                "description": "User authentication and authorization"
            },
            "trading-engine": {
                "name": "Trading Engine",
                "category": ServiceCategory.TRADING,
                "port": 3002,
                "endpoints": ["/orders", "/trades", "/positions"],
                "admin_endpoints": ["/admin/orders", "/admin/halt"],
                "description": "Core trading engine"
            },
            "wallet-service": {
                "name": "Wallet Service",
                "category": ServiceCategory.CORE,
                "port": 3003,
                "endpoints": ["/wallets", "/balance", "/transfer"],
                "admin_endpoints": ["/admin/wallets", "/admin/freeze"],
                "description": "Wallet management"
            },
            "kyc-service": {
                "name": "KYC Service",
                "category": ServiceCategory.CORE,
                "port": 3004,
                "endpoints": ["/submit", "/status", "/documents"],
                "admin_endpoints": ["/admin/kyc", "/admin/approve"],
                "description": "KYC verification"
            },
            "notification-service": {
                "name": "Notification Service",
                "category": ServiceCategory.CORE,
                "port": 3005,
                "endpoints": ["/send", "/preferences", "/history"],
                "admin_endpoints": ["/admin/notifications", "/admin/broadcast"],
                "description": "Notification management"
            },
            "analytics-service": {
                "name": "Analytics Service",
                "category": ServiceCategory.CORE,
                "port": 3006,
                "endpoints": ["/stats", "/reports", "/metrics"],
                "admin_endpoints": ["/admin/analytics", "/admin/configure"],
                "description": "Analytics and reporting"
            },
            "admin-service": {
                "name": "Admin Service",
                "category": ServiceCategory.CORE,
                "port": 3007,
                "endpoints": ["/dashboard", "/users", "/system"],
                "admin_endpoints": ["/admin/all"],
                "description": "Admin panel backend"
            },
            "blockchain-service": {
                "name": "Blockchain Service",
                "category": ServiceCategory.CORE,
                "port": 3008,
                "endpoints": ["/blocks", "/transactions", "/contracts"],
                "admin_endpoints": ["/admin/nodes", "/admin/configure"],
                "description": "Blockchain integration"
            },
            "p2p-service": {
                "name": "P2P Service",
                "category": ServiceCategory.TRADING,
                "port": 3009,
                "endpoints": ["/orders", "/trade", "/escrow"],
                "admin_endpoints": ["/admin/disputes", "/admin/configure"],
                "description": "P2P trading"
            },
            "copy-trading-service": {
                "name": "Copy Trading Service",
                "category": ServiceCategory.SOCIAL,
                "port": 3010,
                "endpoints": ["/traders", "/follow", "/stats"],
                "admin_endpoints": ["/admin/traders", "/admin/configure"],
                "description": "Copy trading"
            },
        }
    
    def get_all_services(self) -> Dict[str, Any]:
        """Get all registered services"""
        return self.services
    
    def get_service(self, service_id: str) -> Dict[str, Any]:
        """Get specific service details"""
        return self.services.get(service_id)
    
    def get_services_by_category(self, category: ServiceCategory) -> Dict[str, Any]:
        """Get services by category"""
        return {
            k: v for k, v in self.services.items() 
            if v["category"] == category
        }
    
    def get_service_count(self) -> int:
        """Get total number of services"""
        return len(self.services)
    
    def get_admin_endpoints(self) -> Dict[str, List[str]]:
        """Get all admin endpoints"""
        return {
            k: v["admin_endpoints"] 
            for k, v in self.services.items()
        }
    
    def get_user_endpoints(self) -> Dict[str, List[str]]:
        """Get all user endpoints"""
        return {
            k: v["endpoints"] 
            for k, v in self.services.items()
        }

# Global registry instance
registry = ServiceRegistry()