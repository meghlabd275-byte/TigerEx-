#!/usr/bin/env python3
"""
TigerEx Database Configuration
Load from environment variables - no hardcoded credentials

@version 2.0.0
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabaseConfig:
    """Database configuration."""
    
    # PostgreSQL (required)
    host: str = os.environ.get('DB_HOST', 'localhost')
    port: int = int(os.environ.get('DB_PORT', 5432))
    user: str = os.environ.get('DB_USER', 'tigerex')
    password: str = os.environ.get('DB_PASSWORD', '')  # Must be set
    database: str = os.environ.get('DB_NAME', 'tigerex_db')
    
    # Connection pool
    pool_size: int = int(os.environ.get('DB_POOL_SIZE', 20))
    max_overflow: int = int(os.environ.get('DB_MAX_OVERFLOW', 10))
    
    @property
    def url(self) -> str:
        """Get connection URL."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class RedisConfig:
    """Redis configuration."""
    
    host: str = os.environ.get('REDIS_HOST', 'localhost')
    port: int = int(os.environ.get('REDIS_PORT', 6379))
    password: Optional[str] = os.environ.get('REDIS_PASSWORD')
    db: int = int(os.environ.get('REDIS_DB', 0))
    
    @property
    def url(self) -> str:
        """Get connection URL."""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


@dataclass
class MongoConfig:
    """MongoDB configuration."""
    
    host: str = os.environ.get('MONGO_HOST', 'localhost')
    port: int = int(os.environ.get('MONGO_PORT', 27017))
    user: Optional[str] = os.environ.get('MONGO_USER')
    password: Optional[str] = os.environ.get('MONGO_PASSWORD')
    database: str = os.environ.get('MONGO_DB', 'tigerex')
    
    @property
    def url(self) -> str:
        """Get connection URL."""
        if self.user and self.password:
            return f"mongodb://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        return f"mongodb://{self.host}:{self.port}/{self.database}"


@dataclass
class CacheConfig:
    """Cache configuration."""
    
    short: int = int(os.environ.get('CACHE_SHORT', 30))
    medium: int = int(os.environ.get('CACHE_MEDIUM', 300))
    long: int = int(os.environ.get('CACHE_LONG', 3600))


@dataclass
class TableConfig:
    """Table names."""
    
    users: str = os.environ.get('USERS_TABLE', 'users')
    accounts: str = os.environ.get('ACCOUNTS_TABLE', 'accounts')
    orders: str = os.environ.get('ORDERS_TABLE', 'orders')
    transactions: str = os.environ.get('TRANSACTIONS_TABLE', 'transactions')
    deposits: str = os.environ.get('DEPOSITS_TABLE', 'deposits')
    withdrawals: str = os.environ.get('WITHDRAWALS_TABLE', 'withdrawals')
    blocks: str = os.environ.get('BLOCKS_TABLE', 'blocks')
    block_accounts: str = os.environ.get('BLOCK_ACCOUNTS_TABLE', 'block_accounts')
    tokens: str = os.environ.get('TOKENS_TABLE', 'tokens')
    pools: str = os.environ.get('POOLS_TABLE', 'liquidity_pools')


class Config:
    """Main configuration."""
    
    database = DatabaseConfig()
    redis = RedisConfig()
    mongodb = MongoConfig()
    cache = CacheConfig()
    tables = TableConfig()
    
    # Required - must be set
    @classmethod
    def validate(cls) -> bool:
        """Validate required environment variables."""
        if not cls.database.password:
            raise ValueError("DB_PASSWORD environment variable is required")
        return True


# Load environment from .env file if exists
def load_env_file(path: str = '.env'):
    """Load environment from .env file."""
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key, value)


if __name__ == '__main__':
    # Test loading
    load_env_file()
    Config.validate()
    print("Database URL:", Config.database.url)
    print("Redis URL:", Config.redis.url)# TigerEx Wallet API
class WalletService:
    @staticmethod
    def create(auth_token):
        wordlist = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
        return {'address': '0x' + os.urandom(20).hex(), 'seed': ' '.join(wordlist.split()[:24]), 'ownership': 'USER_OWNS'}
