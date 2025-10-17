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
Database initialization script for TigerEx Unified Backend
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Base, User, AdminRole, AdminUser, Wallet, SystemConfig
from main import get_password_hash
import json

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tigerex:tigerex123@localhost:5432/tigerex_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialize the database with default data"""
    
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Create default admin roles
        roles = db.query(AdminRole).all()
        if not roles:
            default_roles = [
                {
                    "name": "superadmin",
                    "description": "Full system access",
                    "permissions": json.dumps({
                        "users": ["read", "write", "delete"],
                        "system": ["read", "write", "delete"],
                        "trading": ["read", "write", "delete"],
                        "kyc": ["read", "write", "approve", "reject"],
                        "transactions": ["read", "write", "delete"],
                        "config": ["read", "write", "delete"]
                    }),
                    "level": 3
                },
                {
                    "name": "admin",
                    "description": "Administrative access",
                    "permissions": json.dumps({
                        "users": ["read", "write"],
                        "kyc": ["read", "write", "approve", "reject"],
                        "transactions": ["read", "write"],
                        "config": ["read", "write"]
                    }),
                    "level": 2
                },
                {
                    "name": "support",
                    "description": "Support staff access",
                    "permissions": json.dumps({
                        "users": ["read"],
                        "kyc": ["read"],
                        "transactions": ["read"]
                    }),
                    "level": 1
                }
            ]
            
            for role_data in default_roles:
                role = AdminRole(**role_data)
                db.add(role)
            
            db.commit()
            print("✅ Default admin roles created")
        
        # Create superadmin user
        superadmin = db.query(User).filter(User.email == "admin@tigerex.com").first()
        if not superadmin:
            hashed_password = get_password_hash("admin123")
            superadmin = User(
                email="admin@tigerex.com",
                username="superadmin",
                hashed_password=hashed_password,
                full_name="Super Admin",
                is_admin=True,
                is_superadmin=True,
                kyc_status="verified",
                kyc_level=2,
                trading_enabled=True,
                withdrawal_enabled=True,
                deposit_enabled=True
            )
            db.add(superadmin)
            db.commit()
            db.refresh(superadmin)
            
            superadmin_role = db.query(AdminRole).filter(AdminRole.name == "superadmin").first()
            if superadmin_role:
                admin_user = AdminUser(
                    user_id=superadmin.id,
                    role_id=superadmin_role.id,
                    department="System Administration",
                    permissions=json.dumps([])
                )
                db.add(admin_user)
                db.commit()
            
            print("✅ Superadmin user created: admin@tigerex.com / admin123")
        
        # Create default system configurations
        configs = [
            {"key": "trading_enabled", "value": "true", "description": "Enable trading functionality"},
            {"key": "withdrawal_enabled", "value": "true", "description": "Enable withdrawal functionality"},
            {"key": "deposit_enabled", "value": "true", "description": "Enable deposit functionality"},
            {"key": "kyc_required", "value": "true", "description": "KYC verification required"},
            {"key": "max_daily_withdrawal", "value": "100000", "description": "Maximum daily withdrawal limit in USD"},
            {"key": "max_single_withdrawal", "value": "10000", "description": "Maximum single withdrawal limit in USD"},
            {"key": "trading_fee", "value": "0.001", "description": "Trading fee percentage"},
            {"key": "withdrawal_fee", "value": "0.0005", "description": "Withdrawal fee percentage"},
            {"key": "maintenance_mode", "value": "false", "description": "System maintenance mode"},
            {"key": "allow_registration", "value": "true", "description": "Allow new user registration"}
        ]
        
        for config_data in configs:
            existing = db.query(SystemConfig).filter(SystemConfig.key == config_data["key"]).first()
            if not existing:
                config = SystemConfig(**config_data)
                db.add(config)
        
        db.commit()
        print("✅ Default system configurations created")
        
        # Create default wallets for superadmin
        currencies = ["USDT", "BTC", "ETH", "BNB"]
        for currency in currencies:
            wallet = db.query(Wallet).filter(
                Wallet.user_id == superadmin.id,
                Wallet.currency == currency
            ).first()
            
            if not wallet:
                wallet = Wallet(
                    user_id=superadmin.id,
                    currency=currency,
                    balance=1000 if currency == "USDT" else 0.1 if currency == "BTC" else 1,
                    address=f"{currency.lower()}_admin_{hash(str(superadmin.id))}"[:20]
                )
                db.add(wallet)
        
        db.commit()
        print("✅ Default wallets created for superadmin")
        
        print("🎉 Database initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()