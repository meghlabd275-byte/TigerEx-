import os
from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

# Complete RBAC System for address-generation-service
class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    SUPPORT = "support"
    COMPLIANCE = "compliance"
    RISK_MANAGER = "risk_manager"
    TRADER = "trader"
    USER = "user"

class Permission(str, Enum):
    # User Management
    USER_VIEW = "user:view"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_SUSPEND = "user:suspend"
    USER_VERIFY = "user:verify"
    
    # Financial Controls
    WITHDRAWAL_APPROVE = "withdrawal:approve"
    WITHDRAWAL_REJECT = "withdrawal:reject"
    DEPOSIT_MONITOR = "deposit:monitor"
    TRANSACTION_REVIEW = "transaction:review"
    FEE_MANAGE = "fee:manage"
    
    # Trading Controls
    TRADING_HALT = "trading:halt"
    TRADING_RESUME = "trading:resume"
    PAIR_MANAGE = "pair:manage"
    LIQUIDITY_MANAGE = "liquidity:manage"
    
    # Risk Management
    RISK_CONFIGURE = "risk:configure"
    POSITION_MONITOR = "position:monitor"
    LIQUIDATION_MANAGE = "liquidation:manage"
    
    # System Controls
    SYSTEM_CONFIG = "system:config"
    FEATURE_FLAG = "feature:flag"
    MAINTENANCE_MODE = "maintenance:mode"
    
    # Compliance
    KYC_APPROVE = "kyc:approve"
    KYC_REJECT = "kyc:reject"
    AML_MONITOR = "aml:monitor"
    COMPLIANCE_REPORT = "compliance:report"
    
    # Content Management
    ANNOUNCEMENT_CREATE = "announcement:create"
    ANNOUNCEMENT_UPDATE = "announcement:update"
    ANNOUNCEMENT_DELETE = "announcement:delete"
    
    # Analytics
    ANALYTICS_VIEW = "analytics:view"
    REPORT_GENERATE = "report:generate"
    AUDIT_LOG_VIEW = "audit:view"

class AdminUser(BaseModel):
    user_id: str
    username: str
    email: str
    role: UserRole
    permissions: List[Permission]
    is_active: bool = True
    created_at: datetime = None
    last_login: Optional[datetime] = None

# Role-based permission mapping
ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: [
        Permission.USER_VIEW, Permission.USER_CREATE, Permission.USER_UPDATE,
        Permission.USER_DELETE, Permission.USER_SUSPEND, Permission.USER_VERIFY,
        Permission.WITHDRAWAL_APPROVE, Permission.WITHDRAWAL_REJECT,
        Permission.DEPOSIT_MONITOR, Permission.TRANSACTION_REVIEW, Permission.FEE_MANAGE,
        Permission.TRADING_HALT, Permission.TRADING_RESUME, Permission.PAIR_MANAGE,
        Permission.LIQUIDITY_MANAGE, Permission.RISK_CONFIGURE, Permission.POSITION_MONITOR,
        Permission.LIQUIDATION_MANAGE, Permission.SYSTEM_CONFIG, Permission.FEATURE_FLAG,
        Permission.MAINTENANCE_MODE, Permission.KYC_APPROVE, Permission.KYC_REJECT,
        Permission.AML_MONITOR, Permission.COMPLIANCE_REPORT,
        Permission.ANNOUNCEMENT_CREATE, Permission.ANNOUNCEMENT_UPDATE, Permission.ANNOUNCEMENT_DELETE,
        Permission.ANALYTICS_VIEW, Permission.REPORT_GENERATE, Permission.AUDIT_LOG_VIEW
    ],
    UserRole.ADMIN: [
        Permission.USER_VIEW, Permission.USER_CREATE, Permission.USER_UPDATE,
        Permission.USER_SUSPEND, Permission.USER_VERIFY,
        Permission.WITHDRAWAL_APPROVE, Permission.WITHDRAWAL_REJECT,
        Permission.DEPOSIT_MONITOR, Permission.TRANSACTION_REVIEW, Permission.FEE_MANAGE,
        Permission.TRADING_HALT, Permission.TRADING_RESUME, Permission.PAIR_MANAGE,
        Permission.RISK_CONFIGURE, Permission.POSITION_MONITOR,
        Permission.SYSTEM_CONFIG, Permission.KYC_APPROVE, Permission.KYC_REJECT,
        Permission.ANNOUNCEMENT_CREATE, Permission.ANNOUNCEMENT_UPDATE,
        Permission.ANALYTICS_VIEW, Permission.REPORT_GENERATE, Permission.AUDIT_LOG_VIEW
    ],
    UserRole.MODERATOR: [
        Permission.USER_VIEW, Permission.USER_SUSPEND,
        Permission.TRANSACTION_REVIEW, Permission.KYC_APPROVE,
        Permission.ANNOUNCEMENT_CREATE, Permission.ANALYTICS_VIEW
    ],
    UserRole.SUPPORT: [
        Permission.USER_VIEW, Permission.TRANSACTION_REVIEW,
        Permission.ANALYTICS_VIEW
    ],
    UserRole.COMPLIANCE: [
        Permission.USER_VIEW, Permission.USER_VERIFY,
        Permission.WITHDRAWAL_APPROVE, Permission.WITHDRAWAL_REJECT,
        Permission.TRANSACTION_REVIEW, Permission.KYC_APPROVE, Permission.KYC_REJECT,
        Permission.AML_MONITOR, Permission.COMPLIANCE_REPORT,
        Permission.AUDIT_LOG_VIEW
    ],
    UserRole.RISK_MANAGER: [
        Permission.POSITION_MONITOR, Permission.RISK_CONFIGURE,
        Permission.LIQUIDATION_MANAGE, Permission.TRADING_HALT,
        Permission.ANALYTICS_VIEW, Permission.REPORT_GENERATE
    ],
    UserRole.TRADER: [],
    UserRole.USER: []
}

# RBAC Helper Functions
def get_current_admin():
    """Get current admin user (mock implementation)"""
    return AdminUser(
        user_id="admin_001",
        username="admin",
        email="admin@tigerex.com",
        role=UserRole.ADMIN,
        permissions=ROLE_PERMISSIONS[UserRole.ADMIN]
    )

def require_permission(permission: Permission):
    """Decorator to require specific permission"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            from fastapi import HTTPException, status
            admin = get_current_admin()
            if permission not in admin.permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Permission denied. Required: " + str(permission)
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(roles: List[UserRole]):
    """Decorator to require specific role(s)"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            from fastapi import HTTPException, status
            admin = get_current_admin()
            if admin.role not in roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Role denied. Required: " + str(roles)
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


"""
TigerEx Address Generation Service
Generates unique deposit addresses for all supported blockchains
"""

from fastapi import FastAPI
from admin.admin_routes import router as admin_router
, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
import asyncpg
import structlog
from enum import Enum
import hashlib
import secrets
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base58
import bech32
from eth_account import Account
from web3 import Web3

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

app = FastAPI(title="TigerEx Address Generation Service", version="1.0.0")

# RBAC Helper Functions
def get_current_admin():
    """Get current admin user (mock implementation)"""
    return AdminUser(
        user_id="admin_001",
        username="admin",
        email="admin@tigerex.com",
        role=UserRole.ADMIN,
        permissions=ROLE_PERMISSIONS[UserRole.ADMIN]
    )


# Include admin router
app.include_router(admin_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection pool
db_pool: Optional[asyncpg.Pool] = None

# Blockchain types
class BlockchainType(str, Enum):
    BITCOIN = "bitcoin"
    ETHEREUM = "ethereum"
    BINANCE_SMART_CHAIN = "binance_smart_chain"
    TRON = "tron"
    POLYGON = "polygon"
    AVALANCHE = "avalanche"
    SOLANA = "solana"
    CARDANO = "cardano"
    POLKADOT = "polkadot"
    RIPPLE = "ripple"
    LITECOIN = "litecoin"
    DOGECOIN = "dogecoin"

# Address types
class AddressType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    HOT_WALLET = "hot_wallet"
    COLD_WALLET = "cold_wallet"

# Models
class AddressGenerationRequest(BaseModel):
    user_id: int = Field(..., description="User ID")
    blockchain: BlockchainType = Field(..., description="Blockchain type")
    currency: str = Field(..., description="Currency symbol (e.g., BTC, ETH)")
    address_type: AddressType = Field(default=AddressType.DEPOSIT, description="Address type")
    label: Optional[str] = Field(None, description="Optional label for the address")

class AddressResponse(BaseModel):
    address_id: int
    user_id: int
    blockchain: str
    currency: str
    address: str
    address_type: str
    label: Optional[str]
    is_active: bool
    created_at: datetime

class AddressValidationRequest(BaseModel):
    blockchain: BlockchainType
    address: str

class AddressValidationResponse(BaseModel):
    is_valid: bool
    blockchain: str
    address: str
    address_format: Optional[str] = None
    error: Optional[str] = None

# Database functions
async def get_db():
    return db_pool

async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(
        host="localhost",
        port=5432,
        user="tigerex",
        password="tigerex_secure_password",
        database="tigerex_addresses",
        min_size=10,
        max_size=50
    )
    
    async with db_pool.acquire() as conn:
        # Create addresses table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS addresses (
                address_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                blockchain VARCHAR(50) NOT NULL,
                currency VARCHAR(20) NOT NULL,
                address VARCHAR(255) NOT NULL UNIQUE,
                private_key_encrypted TEXT,
                address_type VARCHAR(20) NOT NULL,
                label VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                last_used_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_blockchain (user_id, blockchain),
                INDEX idx_address (address),
                INDEX idx_currency (currency)
            )
        """)
        
        # Create address derivation paths table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS address_derivation_paths (
                path_id SERIAL PRIMARY KEY,
                address_id INTEGER REFERENCES addresses(address_id),
                derivation_path VARCHAR(255) NOT NULL,
                path_index INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create address usage logs
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS address_usage_logs (
                log_id SERIAL PRIMARY KEY,
                address_id INTEGER REFERENCES addresses(address_id),
                transaction_hash VARCHAR(255),
                amount DECIMAL(36, 18),
                transaction_type VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        logger.info("Database initialized successfully")

# Address generation functions
class AddressGenerator:
    """Generate addresses for different blockchains"""
    
    @staticmethod
    def generate_bitcoin_address() -> tuple[str, str]:
        """Generate Bitcoin P2PKH address"""
        # Generate private key
        private_key = secrets.token_bytes(32)
        
        # Generate public key using secp256k1
        from ecdsa import SigningKey, SECP256k1
        sk = SigningKey.from_string(private_key, curve=SECP256k1)
        vk = sk.get_verifying_key()
        public_key = b'\x04' + vk.to_string()
        
        # Hash public key
        sha256_hash = hashlib.sha256(public_key).digest()
        ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
        
        # Add version byte (0x00 for mainnet)
        versioned_hash = b'\x00' + ripemd160_hash
        
        # Calculate checksum
        checksum = hashlib.sha256(hashlib.sha256(versioned_hash).digest()).digest()[:4]
        
        # Create address
        address_bytes = versioned_hash + checksum
        address = base58.b58encode(address_bytes).decode('utf-8')
        
        return address, private_key.hex()
    
    @staticmethod
    def generate_ethereum_address() -> tuple[str, str]:
        """Generate Ethereum address"""
        # Create new account
        account = Account.create()
        return account.address, account.key.hex()
    
    @staticmethod
    def generate_bsc_address() -> tuple[str, str]:
        """Generate Binance Smart Chain address (same as Ethereum)"""
        return AddressGenerator.generate_ethereum_address()
    
    @staticmethod
    def generate_tron_address() -> tuple[str, str]:
        """Generate TRON address"""
        # Generate private key
        private_key = secrets.token_bytes(32)
        
        # Generate public key
        from ecdsa import SigningKey, SECP256k1
        sk = SigningKey.from_string(private_key, curve=SECP256k1)
        vk = sk.get_verifying_key()
        public_key = b'\x04' + vk.to_string()
        
        # Hash public key with Keccak-256
        from Crypto.Hash import keccak
        k = keccak.new(digest_bits=256)
        k.update(public_key[1:])
        address_bytes = k.digest()[-20:]
        
        # Add TRON prefix (0x41)
        versioned_hash = b'\x41' + address_bytes
        
        # Calculate checksum
        checksum = hashlib.sha256(hashlib.sha256(versioned_hash).digest()).digest()[:4]
        
        # Create address
        address_with_checksum = versioned_hash + checksum
        address = base58.b58encode(address_with_checksum).decode('utf-8')
        
        return address, private_key.hex()
    
    @staticmethod
    def generate_solana_address() -> tuple[str, str]:
        """Generate Solana address"""
        # Generate Ed25519 key pair
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        # Get public key bytes
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        # Encode as base58
        address = base58.b58encode(public_key_bytes).decode('utf-8')
        
        # Get private key bytes
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        return address, private_key_bytes.hex()
    
    @staticmethod
    def generate_address(blockchain: BlockchainType) -> tuple[str, str]:
        """Generate address for specified blockchain"""
        generators = {
            BlockchainType.BITCOIN: AddressGenerator.generate_bitcoin_address,
            BlockchainType.ETHEREUM: AddressGenerator.generate_ethereum_address,
            BlockchainType.BINANCE_SMART_CHAIN: AddressGenerator.generate_bsc_address,
            BlockchainType.TRON: AddressGenerator.generate_tron_address,
            BlockchainType.POLYGON: AddressGenerator.generate_ethereum_address,
            BlockchainType.AVALANCHE: AddressGenerator.generate_ethereum_address,
            BlockchainType.SOLANA: AddressGenerator.generate_solana_address,
            BlockchainType.LITECOIN: AddressGenerator.generate_bitcoin_address,
            BlockchainType.DOGECOIN: AddressGenerator.generate_bitcoin_address,
        }
        
        generator = generators.get(blockchain)
        if not generator:
            raise ValueError(f"Unsupported blockchain: {blockchain}")
        
        return generator()

# Address validation functions
class AddressValidator:
    """Validate addresses for different blockchains"""
    
    @staticmethod
    def validate_bitcoin_address(address: str) -> bool:
        """Validate Bitcoin address"""
        try:
            decoded = base58.b58decode(address)
            if len(decoded) != 25:
                return False
            
            # Verify checksum
            payload = decoded[:-4]
            checksum = decoded[-4:]
            calculated_checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
            
            return checksum == calculated_checksum
        except:
            return False
    
    @staticmethod
    def validate_ethereum_address(address: str) -> bool:
        """Validate Ethereum address"""
        try:
            return Web3.is_address(address)
        except:
            return False
    
    @staticmethod
    def validate_tron_address(address: str) -> bool:
        """Validate TRON address"""
        try:
            decoded = base58.b58decode(address)
            if len(decoded) != 25:
                return False
            
            # Verify prefix
            if decoded[0] != 0x41:
                return False
            
            # Verify checksum
            payload = decoded[:-4]
            checksum = decoded[-4:]
            calculated_checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
            
            return checksum == calculated_checksum
        except:
            return False
    
    @staticmethod
    def validate_solana_address(address: str) -> bool:
        """Validate Solana address"""
        try:
            decoded = base58.b58decode(address)
            return len(decoded) == 32
        except:
            return False
    
    @staticmethod
    def validate_address(blockchain: BlockchainType, address: str) -> bool:
        """Validate address for specified blockchain"""
        validators = {
            BlockchainType.BITCOIN: AddressValidator.validate_bitcoin_address,
            BlockchainType.ETHEREUM: AddressValidator.validate_ethereum_address,
            BlockchainType.BINANCE_SMART_CHAIN: AddressValidator.validate_ethereum_address,
            BlockchainType.TRON: AddressValidator.validate_tron_address,
            BlockchainType.POLYGON: AddressValidator.validate_ethereum_address,
            BlockchainType.AVALANCHE: AddressValidator.validate_ethereum_address,
            BlockchainType.SOLANA: AddressValidator.validate_solana_address,
            BlockchainType.LITECOIN: AddressValidator.validate_bitcoin_address,
            BlockchainType.DOGECOIN: AddressValidator.validate_bitcoin_address,
        }
        
        validator = validators.get(blockchain)
        if not validator:
            return False
        
        return validator(address)

# API Endpoints
@app.post("/api/v1/addresses/generate", response_model=AddressResponse)
async def generate_address(
    request: AddressGenerationRequest,
    db: asyncpg.Pool = Depends(get_db)
):
    """Generate a new blockchain address for a user"""
    try:
        # Check if user already has an active address for this blockchain/currency
        existing = await db.fetchrow("""
            SELECT address_id, address FROM addresses
            WHERE user_id = $1 AND blockchain = $2 AND currency = $3 
            AND address_type = $4 AND is_active = TRUE
        """, request.user_id, request.blockchain.value, request.currency, request.address_type.value)
        
        if existing:
            logger.info("returning_existing_address", 
                       user_id=request.user_id, 
                       blockchain=request.blockchain.value)
            
            return AddressResponse(
                address_id=existing['address_id'],
                user_id=request.user_id,
                blockchain=request.blockchain.value,
                currency=request.currency,
                address=existing['address'],
                address_type=request.address_type.value,
                label=request.label,
                is_active=True,
                created_at=datetime.utcnow()
            )
        
        # Generate new address
        address, private_key = AddressGenerator.generate_address(request.blockchain)
        
        # TODO: Encrypt private key before storing
        # For now, we'll store it as-is (NOT RECOMMENDED FOR PRODUCTION)
        encrypted_private_key = private_key
        
        # Store in database
        result = await db.fetchrow("""
            INSERT INTO addresses (
                user_id, blockchain, currency, address, 
                private_key_encrypted, address_type, label
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING address_id, created_at
        """, request.user_id, request.blockchain.value, request.currency, 
            address, encrypted_private_key, request.address_type.value, request.label)
        
        logger.info("address_generated", 
                   user_id=request.user_id,
                   blockchain=request.blockchain.value,
                   address=address)
        
        return AddressResponse(
            address_id=result['address_id'],
            user_id=request.user_id,
            blockchain=request.blockchain.value,
            currency=request.currency,
            address=address,
            address_type=request.address_type.value,
            label=request.label,
            is_active=True,
            created_at=result['created_at']
        )
        
    except Exception as e:
        logger.error("address_generation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Address generation failed: {str(e)}")

@app.post("/api/v1/addresses/validate", response_model=AddressValidationResponse)
async def validate_address(request: AddressValidationRequest):
    """Validate a blockchain address"""
    try:
        is_valid = AddressValidator.validate_address(request.blockchain, request.address)
        
        return AddressValidationResponse(
            is_valid=is_valid,
            blockchain=request.blockchain.value,
            address=request.address,
            address_format="valid" if is_valid else "invalid"
        )
        
    except Exception as e:
        logger.error("address_validation_failed", error=str(e))
        return AddressValidationResponse(
            is_valid=False,
            blockchain=request.blockchain.value,
            address=request.address,
            error=str(e)
        )

@app.get("/api/v1/addresses/user/{user_id}", response_model=List[AddressResponse])
async def get_user_addresses(
    user_id: int,
    blockchain: Optional[BlockchainType] = None,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get all addresses for a user"""
    try:
        if blockchain:
            addresses = await db.fetch("""
                SELECT * FROM addresses
                WHERE user_id = $1 AND blockchain = $2 AND is_active = TRUE
                ORDER BY created_at DESC
            """, user_id, blockchain.value)
        else:
            addresses = await db.fetch("""
                SELECT * FROM addresses
                WHERE user_id = $1 AND is_active = TRUE
                ORDER BY created_at DESC
            """, user_id)
        
        return [
            AddressResponse(
                address_id=addr['address_id'],
                user_id=addr['user_id'],
                blockchain=addr['blockchain'],
                currency=addr['currency'],
                address=addr['address'],
                address_type=addr['address_type'],
                label=addr['label'],
                is_active=addr['is_active'],
                created_at=addr['created_at']
            )
            for addr in addresses
        ]
        
    except Exception as e:
        logger.error("get_user_addresses_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/addresses/{address_id}", response_model=AddressResponse)
async def get_address(
    address_id: int,
    db: asyncpg.Pool = Depends(get_db)
):
    """Get address details by ID"""
    try:
        addr = await db.fetchrow("""
            SELECT * FROM addresses WHERE address_id = $1
        """, address_id)
        
        if not addr:
            raise HTTPException(status_code=404, detail="Address not found")
        
        return AddressResponse(
            address_id=addr['address_id'],
            user_id=addr['user_id'],
            blockchain=addr['blockchain'],
            currency=addr['currency'],
            address=addr['address'],
            address_type=addr['address_type'],
            label=addr['label'],
            is_active=addr['is_active'],
            created_at=addr['created_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_address_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/addresses/{address_id}")
async def deactivate_address(
    address_id: int,
    db: asyncpg.Pool = Depends(get_db)
):
    """Deactivate an address"""
    try:
        result = await db.execute("""
            UPDATE addresses SET is_active = FALSE
            WHERE address_id = $1
        """, address_id)
        
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Address not found")
        
        logger.info("address_deactivated", address_id=address_id)
        return {"message": "Address deactivated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("deactivate_address_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/addresses/stats/blockchain")
async def get_blockchain_stats(db: asyncpg.Pool = Depends(get_db)):
    """Get address statistics by blockchain"""
    try:
        stats = await db.fetch("""
            SELECT 
                blockchain,
                COUNT(*) as total_addresses,
                COUNT(DISTINCT user_id) as unique_users,
                COUNT(CASE WHEN is_active = TRUE THEN 1 END) as active_addresses
            FROM addresses
            GROUP BY blockchain
            ORDER BY total_addresses DESC
        """)
        
        return [dict(row) for row in stats]
        
    except Exception as e:
        logger.error("get_blockchain_stats_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "address-generation-service",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.on_event("startup")
async def startup():
    """Initialize service on startup"""
    await init_db()
    logger.info("Address Generation Service started")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    if db_pool:
        await db_pool.close()
    logger.info("Address Generation Service stopped")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8220)