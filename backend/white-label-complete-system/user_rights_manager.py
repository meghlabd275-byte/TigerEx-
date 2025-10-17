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

#!/usr/bin/env python3
"""
TigerEx White Label User Rights Manager
Complete user rights and permissions management system
"""

import asyncio
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import json

# ==================== USER RIGHTS ENUMS ====================

class UserType(Enum):
    REGULAR_USER = "regular_user"
    PREMIUM_USER = "premium_user"
    VIP_USER = "vip_user"
    INSTITUTIONAL_USER = "institutional_user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class TradingRight(Enum):
    SPOT_TRADING = "spot_trading"
    MARGIN_TRADING = "margin_trading"
    FUTURES_TRADING = "futures_trading"
    OPTIONS_TRADING = "options_trading"
    OTC_TRADING = "otc_trading"
    P2P_TRADING = "p2p_trading"
    COPY_TRADING = "copy_trading"
    ALGORITHMIC_TRADING = "algorithmic_trading"

class WalletRight(Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    INTERNAL_TRANSFER = "internal_transfer"
    EXTERNAL_TRANSFER = "external_transfer"
    STAKING = "staking"
    LENDING = "lending"
    BORROWING = "borrowing"

class APIRight(Enum):
    READ_ONLY = "read_only"
    TRADING = "trading"
    WITHDRAWAL = "withdrawal"
    ACCOUNT_MANAGEMENT = "account_management"
    WEBSOCKET_ACCESS = "websocket_access"
    FIX_API_ACCESS = "fix_api_access"

class FeatureRight(Enum):
    NFT_MARKETPLACE = "nft_marketplace"
    LAUNCHPAD = "launchpad"
    EARN_PRODUCTS = "earn_products"
    DEFI_INTEGRATION = "defi_integration"
    FIAT_GATEWAY = "fiat_gateway"
    CARD_SERVICES = "card_services"

# ==================== USER RIGHTS DATA CLASSES ====================

@dataclass
class UserLimits:
    """User trading and withdrawal limits"""
    daily_trading_volume: float = 0.0
    daily_withdrawal_amount: float = 0.0
    single_trade_max: float = 0.0
    single_withdrawal_max: float = 0.0
    api_rate_limit: int = 0  # requests per minute
    leverage_max: float = 1.0

@dataclass
class UserRights:
    """Complete user rights configuration"""
    user_id: str
    user_type: UserType
    trading_rights: Set[TradingRight] = field(default_factory=set)
    wallet_rights: Set[WalletRight] = field(default_factory=set)
    api_rights: Set[APIRight] = field(default_factory=set)
    feature_rights: Set[FeatureRight] = field(default_factory=set)
    limits: UserLimits = field(default_factory=UserLimits)
    kyc_level: int = 0  # 0 = none, 1 = basic, 2 = intermediate, 3 = advanced
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

# ==================== USER RIGHTS MANAGER ====================

class UserRightsManager:
    """Manage user rights and permissions"""
    
    def __init__(self):
        self.user_rights: Dict[str, UserRights] = {}
        self.default_rights = self._initialize_default_rights()
    
    def _initialize_default_rights(self) -> Dict[UserType, UserRights]:
        """Initialize default rights for each user type"""
        
        return {
            UserType.REGULAR_USER: UserRights(
                user_id="default",
                user_type=UserType.REGULAR_USER,
                trading_rights={TradingRight.SPOT_TRADING},
                wallet_rights={
                    WalletRight.DEPOSIT,
                    WalletRight.WITHDRAW,
                    WalletRight.INTERNAL_TRANSFER
                },
                api_rights={APIRight.READ_ONLY},
                feature_rights={FeatureRight.EARN_PRODUCTS},
                limits=UserLimits(
                    daily_trading_volume=10000.0,
                    daily_withdrawal_amount=2000.0,
                    single_trade_max=5000.0,
                    single_withdrawal_max=1000.0,
                    api_rate_limit=60,
                    leverage_max=1.0
                ),
                kyc_level=1
            ),
            
            UserType.PREMIUM_USER: UserRights(
                user_id="default",
                user_type=UserType.PREMIUM_USER,
                trading_rights={
                    TradingRight.SPOT_TRADING,
                    TradingRight.MARGIN_TRADING,
                    TradingRight.P2P_TRADING
                },
                wallet_rights={
                    WalletRight.DEPOSIT,
                    WalletRight.WITHDRAW,
                    WalletRight.INTERNAL_TRANSFER,
                    WalletRight.EXTERNAL_TRANSFER,
                    WalletRight.STAKING
                },
                api_rights={
                    APIRight.READ_ONLY,
                    APIRight.TRADING,
                    APIRight.WEBSOCKET_ACCESS
                },
                feature_rights={
                    FeatureRight.EARN_PRODUCTS,
                    FeatureRight.NFT_MARKETPLACE,
                    FeatureRight.DEFI_INTEGRATION
                },
                limits=UserLimits(
                    daily_trading_volume=100000.0,
                    daily_withdrawal_amount=20000.0,
                    single_trade_max=50000.0,
                    single_withdrawal_max=10000.0,
                    api_rate_limit=120,
                    leverage_max=3.0
                ),
                kyc_level=2
            ),
            
            UserType.VIP_USER: UserRights(
                user_id="default",
                user_type=UserType.VIP_USER,
                trading_rights={
                    TradingRight.SPOT_TRADING,
                    TradingRight.MARGIN_TRADING,
                    TradingRight.FUTURES_TRADING,
                    TradingRight.OPTIONS_TRADING,
                    TradingRight.P2P_TRADING,
                    TradingRight.COPY_TRADING
                },
                wallet_rights={
                    WalletRight.DEPOSIT,
                    WalletRight.WITHDRAW,
                    WalletRight.INTERNAL_TRANSFER,
                    WalletRight.EXTERNAL_TRANSFER,
                    WalletRight.STAKING,
                    WalletRight.LENDING,
                    WalletRight.BORROWING
                },
                api_rights={
                    APIRight.READ_ONLY,
                    APIRight.TRADING,
                    APIRight.WITHDRAWAL,
                    APIRight.ACCOUNT_MANAGEMENT,
                    APIRight.WEBSOCKET_ACCESS
                },
                feature_rights={
                    FeatureRight.EARN_PRODUCTS,
                    FeatureRight.NFT_MARKETPLACE,
                    FeatureRight.LAUNCHPAD,
                    FeatureRight.DEFI_INTEGRATION,
                    FeatureRight.FIAT_GATEWAY,
                    FeatureRight.CARD_SERVICES
                },
                limits=UserLimits(
                    daily_trading_volume=1000000.0,
                    daily_withdrawal_amount=200000.0,
                    single_trade_max=500000.0,
                    single_withdrawal_max=100000.0,
                    api_rate_limit=300,
                    leverage_max=10.0
                ),
                kyc_level=3
            ),
            
            UserType.INSTITUTIONAL_USER: UserRights(
                user_id="default",
                user_type=UserType.INSTITUTIONAL_USER,
                trading_rights={
                    TradingRight.SPOT_TRADING,
                    TradingRight.MARGIN_TRADING,
                    TradingRight.FUTURES_TRADING,
                    TradingRight.OPTIONS_TRADING,
                    TradingRight.OTC_TRADING,
                    TradingRight.ALGORITHMIC_TRADING
                },
                wallet_rights={
                    WalletRight.DEPOSIT,
                    WalletRight.WITHDRAW,
                    WalletRight.INTERNAL_TRANSFER,
                    WalletRight.EXTERNAL_TRANSFER,
                    WalletRight.STAKING,
                    WalletRight.LENDING,
                    WalletRight.BORROWING
                },
                api_rights={
                    APIRight.READ_ONLY,
                    APIRight.TRADING,
                    APIRight.WITHDRAWAL,
                    APIRight.ACCOUNT_MANAGEMENT,
                    APIRight.WEBSOCKET_ACCESS,
                    APIRight.FIX_API_ACCESS
                },
                feature_rights={
                    FeatureRight.EARN_PRODUCTS,
                    FeatureRight.DEFI_INTEGRATION,
                    FeatureRight.FIAT_GATEWAY
                },
                limits=UserLimits(
                    daily_trading_volume=100000000.0,
                    daily_withdrawal_amount=10000000.0,
                    single_trade_max=10000000.0,
                    single_withdrawal_max=5000000.0,
                    api_rate_limit=1000,
                    leverage_max=20.0
                ),
                kyc_level=3
            )
        }
    
    # ==================== USER CREATION & MANAGEMENT ====================
    
    async def create_user(
        self,
        user_id: str,
        user_type: UserType,
        custom_rights: Optional[Dict[str, Any]] = None
    ) -> UserRights:
        """Create user with default or custom rights"""
        
        # Get default rights for user type
        default = self.default_rights[user_type]
        
        # Create user rights
        rights = UserRights(
            user_id=user_id,
            user_type=user_type,
            trading_rights=default.trading_rights.copy(),
            wallet_rights=default.wallet_rights.copy(),
            api_rights=default.api_rights.copy(),
            feature_rights=default.feature_rights.copy(),
            limits=UserLimits(**vars(default.limits)),
            kyc_level=default.kyc_level
        )
        
        # Apply custom rights if provided
        if custom_rights:
            if 'trading_rights' in custom_rights:
                rights.trading_rights = {
                    TradingRight[r] for r in custom_rights['trading_rights']
                }
            if 'wallet_rights' in custom_rights:
                rights.wallet_rights = {
                    WalletRight[r] for r in custom_rights['wallet_rights']
                }
            if 'api_rights' in custom_rights:
                rights.api_rights = {
                    APIRight[r] for r in custom_rights['api_rights']
                }
            if 'feature_rights' in custom_rights:
                rights.feature_rights = {
                    FeatureRight[r] for r in custom_rights['feature_rights']
                }
            if 'limits' in custom_rights:
                for key, value in custom_rights['limits'].items():
                    setattr(rights.limits, key, value)
        
        self.user_rights[user_id] = rights
        return rights
    
    async def upgrade_user(
        self,
        user_id: str,
        new_user_type: UserType
    ) -> UserRights:
        """Upgrade user to new type"""
        
        if user_id not in self.user_rights:
            raise ValueError(f"User {user_id} not found")
        
        current_rights = self.user_rights[user_id]
        new_default = self.default_rights[new_user_type]
        
        # Upgrade rights
        current_rights.user_type = new_user_type
        current_rights.trading_rights.update(new_default.trading_rights)
        current_rights.wallet_rights.update(new_default.wallet_rights)
        current_rights.api_rights.update(new_default.api_rights)
        current_rights.feature_rights.update(new_default.feature_rights)
        current_rights.limits = UserLimits(**vars(new_default.limits))
        current_rights.kyc_level = max(current_rights.kyc_level, new_default.kyc_level)
        current_rights.updated_at = datetime.now()
        
        return current_rights
    
    # ==================== RIGHTS MANAGEMENT ====================
    
    async def grant_trading_right(
        self,
        user_id: str,
        trading_right: TradingRight
    ) -> UserRights:
        """Grant trading right to user"""
        
        if user_id not in self.user_rights:
            raise ValueError(f"User {user_id} not found")
        
        rights = self.user_rights[user_id]
        rights.trading_rights.add(trading_right)
        rights.updated_at = datetime.now()
        
        return rights
    
    async def revoke_trading_right(
        self,
        user_id: str,
        trading_right: TradingRight
    ) -> UserRights:
        """Revoke trading right from user"""
        
        if user_id not in self.user_rights:
            raise ValueError(f"User {user_id} not found")
        
        rights = self.user_rights[user_id]
        rights.trading_rights.discard(trading_right)
        rights.updated_at = datetime.now()
        
        return rights
    
    async def grant_wallet_right(
        self,
        user_id: str,
        wallet_right: WalletRight
    ) -> UserRights:
        """Grant wallet right to user"""
        
        if user_id not in self.user_rights:
            raise ValueError(f"User {user_id} not found")
        
        rights = self.user_rights[user_id]
        rights.wallet_rights.add(wallet_right)
        rights.updated_at = datetime.now()
        
        return rights
    
    async def revoke_wallet_right(
        self,
        user_id: str,
        wallet_right: WalletRight
    ) -> UserRights:
        """Revoke wallet right from user"""
        
        if user_id not in self.user_rights:
            raise ValueError(f"User {user_id} not found")
        
        rights = self.user_rights[user_id]
        rights.wallet_rights.discard(wallet_right)
        rights.updated_at = datetime.now()
        
        return rights
    
    async def grant_api_right(
        self,
        user_id: str,
        api_right: APIRight
    ) -> UserRights:
        """Grant API right to user"""
        
        if user_id not in self.user_rights:
            raise ValueError(f"User {user_id} not found")
        
        rights = self.user_rights[user_id]
        rights.api_rights.add(api_right)
        rights.updated_at = datetime.now()
        
        return rights
    
    async def revoke_api_right(
        self,
        user_id: str,
        api_right: APIRight
    ) -> UserRights:
        """Revoke API right from user"""
        
        if user_id not in self.user_rights:
            raise ValueError(f"User {user_id} not found")
        
        rights = self.user_rights[user_id]
        rights.api_rights.discard(api_right)
        rights.updated_at = datetime.now()
        
        return rights
    
    async def grant_feature_right(
        self,
        user_id: str,
        feature_right: FeatureRight
    ) -> UserRights:
        """Grant feature right to user"""
        
        if user_id not in self.user_rights:
            raise ValueError(f"User {user_id} not found")
        
        rights = self.user_rights[user_id]
        rights.feature_rights.add(feature_right)
        rights.updated_at = datetime.now()
        
        return rights
    
    async def revoke_feature_right(
        self,
        user_id: str,
        feature_right: FeatureRight
    ) -> UserRights:
        """Revoke feature right from user"""
        
        if user_id not in self.user_rights:
            raise ValueError(f"User {user_id} not found")
        
        rights = self.user_rights[user_id]
        rights.feature_rights.discard(feature_right)
        rights.updated_at = datetime.now()
        
        return rights
    
    # ==================== LIMITS MANAGEMENT ====================
    
    async def update_limits(
        self,
        user_id: str,
        limits: Dict[str, float]
    ) -> UserRights:
        """Update user limits"""
        
        if user_id not in self.user_rights:
            raise ValueError(f"User {user_id} not found")
        
        rights = self.user_rights[user_id]
        
        for key, value in limits.items():
            if hasattr(rights.limits, key):
                setattr(rights.limits, key, value)
        
        rights.updated_at = datetime.now()
        
        return rights
    
    async def update_kyc_level(
        self,
        user_id: str,
        kyc_level: int
    ) -> UserRights:
        """Update user KYC level"""
        
        if user_id not in self.user_rights:
            raise ValueError(f"User {user_id} not found")
        
        rights = self.user_rights[user_id]
        rights.kyc_level = kyc_level
        rights.updated_at = datetime.now()
        
        # Adjust limits based on KYC level
        if kyc_level >= 2:
            rights.limits.daily_withdrawal_amount *= 2
            rights.limits.single_withdrawal_max *= 2
        if kyc_level >= 3:
            rights.limits.daily_trading_volume *= 5
            rights.limits.leverage_max *= 2
        
        return rights
    
    # ==================== USER STATUS ====================
    
    async def activate_user(self, user_id: str) -> UserRights:
        """Activate user"""
        
        if user_id not in self.user_rights:
            raise ValueError(f"User {user_id} not found")
        
        rights = self.user_rights[user_id]
        rights.is_active = True
        rights.updated_at = datetime.now()
        
        return rights
    
    async def deactivate_user(self, user_id: str) -> UserRights:
        """Deactivate user"""
        
        if user_id not in self.user_rights:
            raise ValueError(f"User {user_id} not found")
        
        rights = self.user_rights[user_id]
        rights.is_active = False
        rights.updated_at = datetime.now()
        
        return rights
    
    # ==================== QUERY METHODS ====================
    
    async def get_user_rights(self, user_id: str) -> UserRights:
        """Get user rights"""
        
        if user_id not in self.user_rights:
            raise ValueError(f"User {user_id} not found")
        
        return self.user_rights[user_id]
    
    async def check_trading_right(
        self,
        user_id: str,
        trading_right: TradingRight
    ) -> bool:
        """Check if user has trading right"""
        
        if user_id not in self.user_rights:
            return False
        
        return trading_right in self.user_rights[user_id].trading_rights
    
    async def check_wallet_right(
        self,
        user_id: str,
        wallet_right: WalletRight
    ) -> bool:
        """Check if user has wallet right"""
        
        if user_id not in self.user_rights:
            return False
        
        return wallet_right in self.user_rights[user_id].wallet_rights
    
    async def check_api_right(
        self,
        user_id: str,
        api_right: APIRight
    ) -> bool:
        """Check if user has API right"""
        
        if user_id not in self.user_rights:
            return False
        
        return api_right in self.user_rights[user_id].api_rights
    
    async def check_feature_right(
        self,
        user_id: str,
        feature_right: FeatureRight
    ) -> bool:
        """Check if user has feature right"""
        
        if user_id not in self.user_rights:
            return False
        
        return feature_right in self.user_rights[user_id].feature_rights
    
    async def list_all_users(self) -> List[UserRights]:
        """List all users"""
        
        return list(self.user_rights.values())

# ==================== EXAMPLE USAGE ====================

async def main():
    """Example usage of User Rights Manager"""
    
    manager = UserRightsManager()
    
    # Create regular user
    regular_user = await manager.create_user(
        user_id="user123",
        user_type=UserType.REGULAR_USER
    )
    
    print(f"Regular User Created: {regular_user.user_id}")
    print(f"Trading Rights: {[r.value for r in regular_user.trading_rights]}")
    
    # Upgrade to premium
    premium_user = await manager.upgrade_user(
        user_id="user123",
        new_user_type=UserType.PREMIUM_USER
    )
    
    print(f"User Upgraded to Premium")
    print(f"New Trading Rights: {[r.value for r in premium_user.trading_rights]}")
    
    # Grant additional right
    await manager.grant_trading_right(
        user_id="user123",
        trading_right=TradingRight.FUTURES_TRADING
    )
    
    print(f"Futures Trading Granted")
    
    # Check right
    has_futures = await manager.check_trading_right(
        user_id="user123",
        trading_right=TradingRight.FUTURES_TRADING
    )
    
    print(f"Has Futures Trading: {has_futures}")

if __name__ == "__main__":
    asyncio.run(main())