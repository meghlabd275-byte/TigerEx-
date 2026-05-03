"""
TigerEx Complete Backend Role Management Service
All end user roles and admin roles with permissions
"""

from fastapi import FastAPI, HTTPException
from typing import List, Optional, Dict, Set
from datetime import datetime
from enum import Enum

app = FastAPI(
    title="TigerEx Role Management Service",
    version="4.0.0",
    description="Complete role management with all user and admin roles"
)

# ==================== END USER ROLES ====================
class EndUserRole(str, Enum):
    TRADER = "trader"
    VIP = "vip"
    AFFILIATE = "affiliate"
    PARTNER = "partner"
    INSTITUTION = "institution"
    P2P_MERCHANT = "p2p_merchant"
    LIQUIDITY_PROVIDER = "liquidity_provider"
    MARKET_MAKER = "market_maker"
    COIN_TOKEN_TEAM = "coin_token_team"
    WHITE_LABEL = "white_label"

# ==================== ADMIN ROLES ====================
class AdminRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    LISTING_MANAGER = "listing_manager"
    BD_MANAGER = "bd_manager"
    SUPPORT_TEAM = "support_team"
    LIQUIDITY_MANAGER = "liquidity_manager"
    TECHNICAL_TEAM = "technical_team"
    COMPLIANCE_MANAGER = "compliance_manager"
    RISK_MANAGER = "risk_manager"

# ==================== FEATURES ====================
class Feature(str, Enum):
    SPOT_TRADING = "spot_trading"
    FUTURES_TRADING = "futures_trading"
    MARGIN_TRADING = "margin_trading"
    OPTIONS_TRADING = "options_trading"
    ALPHA_TRADING = "alpha_trading"
    COPY_TRADING = "copy_trading"
    TRADEX = "tradex"
    STAKING = "staking"
    SAVINGS = "savings"
    LAUNCHPOOL = "launchpool"
    MEGADROP = "megadrop"
    IDO = "ido"
    CLOUD_MINING = "cloud_mining"
    P2P_TRADING = "p2p_trading"
    P2P_MERCHANT = "p2p_merchant"
    P2P_CREATE_AD = "p2p_create_ad"
    FIAT_BUY = "fiat_buy"
    FIAT_SELL = "fiat_sell"
    CARD = "card"
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    CONVERT = "convert"
    SEND_CRYPTO = "send_crypto"
    REDPACKET = "redpacket"
    OTC_TRADING = "otc_trading"
    INSTITUTIONAL_API = "institutional_api"
    CUSTODY = "custody"
    REFERRAL = "referral"
    AFFILIATE = "affiliate"
    USER_MANAGEMENT = "user_management"
    KYC_APPROVAL = "kyc_approval"
    TRADING_PAIRS = "trading_pairs"
    FEE_MANAGEMENT = "fee_management"
    LISTING = "listing"
    WITHDRAWAL_APPROVAL = "withdrawal_approval"
    LIQUIDITY_MANAGEMENT = "liquidity_management"
    MARKET_MAKING = "market_making"
    SUPPORT_TICKETS = "support_tickets"
    COMPLIANCE = "compliance"
    AUDIT_LOGS = "audit_logs"
    SYSTEM_CONFIG = "system_config"
    RISK_MANAGEMENT = "risk_management"

# Role Permissions
ROLE_PERMISSIONS = {
    EndUserRole.TRADER: {Feature.SPOT_TRADING, Feature.DEPOSIT, Feature.WITHDRAW, Feature.CONVERT, Feature.SEND_CRYPTO, Feature.SAVINGS, Feature.LAUNCHPOOL, Feature.P2P_TRADING},
    EndUserRole.VIP: {Feature.FUTURES_TRADING, Feature.STAKING, Feature.MEGADROP, Feature.COPY_TRADING, Feature.REFERRAL},
    EndUserRole.LIQUIDITY_PROVIDER: {Feature.FUTURES_TRADING, Feature.MARGIN_TRADING, Feature.LIQUIDITY_MANAGEMENT},
    EndUserRole.MARKET_MAKER: {Feature.API_ACCESS, Feature.MARKET_MAKING, Feature.TRADING_PAIRS, Feature.MARGIN_TRADING},
    EndUserRole.INSTITUTION: {Feature.SPOT_TRADING, Feature.FUTURES_TRADING, Feature.MARGIN_TRADING, Feature.OPTIONS_TRADING, Feature.OTC_TRADING, Feature.INSTITUTIONAL_API, Feature.CARD},
    EndUserRole.P2P_MERCHANT: {Feature.P2P_MERCHANT, Feature.P2P_CREATE_AD},
    AdminRole.LIQUIDITY_MANAGER: {Feature.LIQUIDITY_MANAGEMENT, Feature.MARKET_MAKING, Feature.TRADING_PAIRS, Feature.WITHDRAWAL_APPROVAL},
    AdminRole.ADMIN: {Feature.USER_MANAGEMENT, Feature.KYC_APPROVAL, Feature.TRADING_PAIRS, Feature.FEE_MANAGEMENT, Feature.LISTING, Feature.WITHDRAWAL_APPROVAL, Feature.LIQUIDITY_MANAGEMENT, Feature.SUPPORT_TICKETS, Feature.COMPLIANCE, Feature.AUDIT_LOGS, Feature.SYSTEM_CONFIG},
    AdminRole.SUPER_ADMIN: set(Feature),
}

ROLE_HIERARCHY = {
    AdminRole.SUPER_ADMIN: 100, AdminRole.ADMIN: 90, AdminRole.LIQUIDITY_MANAGER: 85,
    AdminRole.TECHNICAL_TEAM: 80, AdminRole.COMPLIANCE_MANAGER: 75, AdminRole.RISK_MANAGER: 72,
    AdminRole.LISTING_MANAGER: 70, AdminRole.BD_MANAGER: 65, AdminRole.SUPPORT_TEAM: 60,
    AdminRole.MODERATOR: 55, EndUserRole.INSTITUTION: 50, EndUserRole.WHITE_LABEL: 45,
    EndUserRole.PARTNER: 40, EndUserRole.MARKET_MAKER: 35, EndUserRole.LIQUIDITY_PROVIDER: 30,
    EndUserRole.P2P_MERCHANT: 25, EndUserRole.VIP: 20, EndUserRole.COIN_TOKEN_TEAM: 18,
    EndUserRole.AFFILIATE: 15, EndUserRole.TRADER: 10,
}

@app.get("/")
def root():
    return {"service": "TigerEx Role Management", "version": "4.0.0"}

@app.get("/api/roles")
def get_all_roles():
    return {"roles": [r.value for r in list(EndUserRole) + list(AdminRole)]}

@app.get("/api/roles/{role}/permissions")
def get_role_permissions(role: str):
    return {"role": role, "permissions": list(ROLE_PERMISSIONS.get(role, set()))}

@app.get("/api/dashboard/{role}")
def get_dashboard(role: str):
    dashboards = {
        "trader": {"name": "Trader", "tabs": ["Home", "Markets", "Trade", "Assets", "Earn", "P2P"]},
        "vip": {"name": "VIP", "tabs": ["Home", "Markets", "Trade", "Assets", "Earn", "Copy Trading"]},
        "affiliate": {"name": "Affiliate", "tabs": ["Home", "Markets", "Trade", "Referral"]},
        "institution": {"name": "Institution", "tabs": ["Dashboard", "Trading", "Portfolio", "OTC", "API"]},
        "p2p_merchant": {"name": "P2P Merchant", "tabs": ["Home", "My Ads", "Orders", "Chat"]},
        "liquidity_provider": {"name": "Liquidity Provider", "tabs": ["Dashboard", "Pools", "Volume"]},
        "market_maker": {"name": "Market Maker", "tabs": ["Dashboard", "Strategies", "API"]},
        "liquidity_manager": {"name": "Liquidity Manager", "tabs": ["Dashboard", "Liquidity", "Pools", "Withdrawals"]},
        "admin": {"name": "Admin", "tabs": ["Dashboard", "Users", "Markets", "Trading", "KYC"]},
        "super_admin": {"name": "Super Admin", "tabs": ["Dashboard", "Users", "Markets", "Trading", "KYC", "Audit", "System"]},
    }
    return dashboards.get(role, dashboards["trader"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
