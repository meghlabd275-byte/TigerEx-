"""
TigerEx Enhanced Market Maker Bot Configuration
Advanced configuration management for all trading strategies and exchanges
"""

import os
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
import yaml
import json
from datetime import timedelta

class TradingEnvironment(str, Enum):
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    PAPER_TRADING = "paper_trading"

class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ExchangeConfig(BaseModel):
    name: str
    api_key: str
    api_secret: str
    passphrase: Optional[str] = None
    sandbox: bool = False
    rate_limits: Dict[str, int] = {}
    fees: Dict[str, float] = {}
    enabled: bool = True
    testnet: bool = False
    
class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    database: str = "tigerex_trading"
    username: str = "postgres"
    password: str = "password"
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600

class RedisConfig(BaseModel):
    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: Optional[str] = None
    max_connections: int = 100
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    
class MonitoringConfig(BaseModel):
    prometheus_port: int = 9090
    grafana_port: int = 3000
    log_level: LogLevel = LogLevel.INFO
    metrics_enabled: bool = True
    alerting_enabled: bool = True
    dashboard_enabled: bool = True
    health_check_interval: int = 30

class SecurityConfig(BaseModel):
    jwt_secret_key: str = Field(..., min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    api_key_length: int = 64
    encryption_enabled: bool = True
    rate_limiting_enabled: bool = True
    ip_whitelist_enabled: bool = False
    allowed_ips: List[str] = []

class MLConfig(BaseModel):
    enabled: bool = False
    model_type: str = "lstm"
    prediction_horizon: int = 60
    retrain_interval: int = 86400
    confidence_threshold: float = 0.7
    feature_window: int = 100
    models_path: str = "./models"
    data_path: str = "./data"
    gpu_enabled: bool = True
    batch_size: int = 32
    learning_rate: float = 0.001

class PerformanceConfig(BaseModel):
    max_workers: int = 10
    thread_pool_size: int = 100
    async_pool_size: int = 1000
    queue_size: int = 10000
    timeout_seconds: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60

class SystemConfig(BaseModel):
    environment: TradingEnvironment = TradingEnvironment.DEVELOPMENT
    debug: bool = False
    log_level: LogLevel = LogLevel.INFO
    timezone: str = "UTC"
    max_memory_mb: int = 4096
    max_cpu_percent: float = 80.0
    auto_restart: bool = True
    backup_enabled: bool = True
    backup_interval_hours: int = 24

class TradingConfig(BaseModel):
    max_daily_volume: float = 10000000
    max_daily_trades: int = 10000
    max_position_size: float = 100000
    default_leverage: float = 1.0
    allowed_trading_types: List[str] = ["spot", "futures_perpetual"]
    risk_level: str = "medium"
    emergency_stop_enabled: bool = True
    circuit_breaker_threshold: float = 0.05

class Config(BaseModel):
    """Main configuration class for TigerEx Enhanced Market Maker Bot"""
    
    # System
    system: SystemConfig = Field(default_factory=SystemConfig)
    
    # Exchanges
    exchanges: Dict[str, ExchangeConfig] = {}
    
    # Database
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    
    # Redis
    redis: RedisConfig = Field(default_factory=RedisConfig)
    
    # Monitoring
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    
    # Security
    security: SecurityConfig
    
    # Machine Learning
    ml: MLConfig = Field(default_factory=MLConfig)
    
    # Performance
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    
    # Trading
    trading: TradingConfig = Field(default_factory=TradingConfig)
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    api_timeout: int = 30
    
    # WebSocket
    websocket_port: int = 8001
    websocket_ping_interval: int = 20
    websocket_ping_timeout: int = 10
    
    # Risk Management
    risk_enabled: bool = True
    risk_check_interval: int = 10
    max_drawdown_threshold: float = 0.1
    max_loss_threshold: float = 0.02
    
    @validator('exchanges')
    def validate_exchanges(cls, v):
        if not v:
            raise ValueError("At least one exchange must be configured")
        return v
    
    @classmethod
    def from_file(cls, config_path: str) -> 'Config':
        """Load configuration from file"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                config_data = yaml.safe_load(f)
            elif config_path.endswith('.json'):
                config_data = json.load(f)
            else:
                raise ValueError("Configuration file must be YAML or JSON")
        
        return cls(**config_data)
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables"""
        config_data = {
            'system': {
                'environment': os.getenv('ENVIRONMENT', 'development'),
                'debug': os.getenv('DEBUG', 'false').lower() == 'true',
                'log_level': os.getenv('LOG_LEVEL', 'info'),
                'timezone': os.getenv('TIMEZONE', 'UTC'),
            },
            'database': {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', '5432')),
                'database': os.getenv('DB_NAME', 'tigerex_trading'),
                'username': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', 'password'),
            },
            'redis': {
                'host': os.getenv('REDIS_HOST', 'localhost'),
                'port': int(os.getenv('REDIS_PORT', '6379')),
                'database': int(os.getenv('REDIS_DB', '0')),
                'password': os.getenv('REDIS_PASSWORD'),
            },
            'security': {
                'jwt_secret_key': os.getenv('JWT_SECRET_KEY', 'default-secret-key-change-in-production'),
                'jwt_algorithm': os.getenv('JWT_ALGORITHM', 'HS256'),
                'jwt_expiration_hours': int(os.getenv('JWT_EXPIRATION_HOURS', '24')),
            },
            'monitoring': {
                'prometheus_port': int(os.getenv('PROMETHEUS_PORT', '9090')),
                'grafana_port': int(os.getenv('GRAFANA_PORT', '3000')),
                'log_level': os.getenv('LOG_LEVEL', 'info'),
            },
            'ml': {
                'enabled': os.getenv('ML_ENABLED', 'false').lower() == 'true',
                'model_type': os.getenv('ML_MODEL_TYPE', 'lstm'),
                'gpu_enabled': os.getenv('ML_GPU_ENABLED', 'true').lower() == 'true',
            },
            'api_host': os.getenv('API_HOST', '0.0.0.0'),
            'api_port': int(os.getenv('API_PORT', '8000')),
            'api_workers': int(os.getenv('API_WORKERS', '4')),
        }
        
        return cls(**config_data)
    
    def to_file(self, config_path: str):
        """Save configuration to file"""
        config_data = self.dict()
        
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w') as f:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            elif config_path.endswith('.json'):
                json.dump(config_data, f, indent=2)
            else:
                raise ValueError("Configuration file must be YAML or JSON")
    
    def get_exchange_config(self, exchange_name: str) -> Optional[ExchangeConfig]:
        """Get configuration for a specific exchange"""
        return self.exchanges.get(exchange_name)
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.system.environment == TradingEnvironment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.system.environment == TradingEnvironment.DEVELOPMENT
    
    def is_paper_trading(self) -> bool:
        """Check if running in paper trading mode"""
        return self.system.environment == TradingEnvironment.PAPER_TRADING

# Default exchange configurations
DEFAULT_EXCHANGE_CONFIGS = {
    'binance': {
        'name': 'binance',
        'api_key': '',
        'api_secret': '',
        'sandbox': False,
        'rate_limits': {
            'requests_per_second': 10,
            'orders_per_second': 10
        },
        'fees': {
            'maker': 0.001,
            'taker': 0.001
        },
        'enabled': True
    },
    'bybit': {
        'name': 'bybit',
        'api_key': '',
        'api_secret': '',
        'sandbox': False,
        'rate_limits': {
            'requests_per_second': 10,
            'orders_per_second': 5
        },
        'fees': {
            'maker': 0.001,
            'taker': 0.001
        },
        'enabled': True
    },
    'okx': {
        'name': 'okx',
        'api_key': '',
        'api_secret': '',
        'passphrase': '',
        'sandbox': False,
        'rate_limits': {
            'requests_per_second': 20,
            'orders_per_second': 60
        },
        'fees': {
            'maker': 0.0008,
            'taker': 0.001
        },
        'enabled': True
    },
    'kucoin': {
        'name': 'kucoin',
        'api_key': '',
        'api_secret': '',
        'passphrase': '',
        'sandbox': False,
        'rate_limits': {
            'requests_per_second': 20,
            'orders_per_second': 12
        },
        'fees': {
            'maker': 0.001,
            'taker': 0.001
        },
        'enabled': True
    },
    'bitget': {
        'name': 'bitget',
        'api_key': '',
        'api_secret': '',
        'passphrase': '',
        'sandbox': False,
        'rate_limits': {
            'requests_per_second': 10,
            'orders_per_second': 10
        },
        'fees': {
            'maker': 0.001,
            'taker': 0.001
        },
        'enabled': True
    },
    'gate': {
        'name': 'gate',
        'api_key': '',
        'api_secret': '',
        'sandbox': False,
        'rate_limits': {
            'requests_per_second': 10,
            'orders_per_second': 10
        },
        'fees': {
            'maker': 0.002,
            'taker': 0.002
        },
        'enabled': True
    }
}

def create_default_config() -> Config:
    """Create a default configuration with all exchanges"""
    exchanges = {}
    for name, config in DEFAULT_EXCHANGE_CONFIGS.items():
        exchanges[name] = ExchangeConfig(**config)
    
    return Config(
        system=SystemConfig(
            environment=TradingEnvironment.DEVELOPMENT,
            debug=True,
            log_level=LogLevel.INFO
        ),
        exchanges=exchanges,
        security=SecurityConfig(
            jwt_secret_key="your-super-secret-jwt-key-change-this-in-production"
        ),
        monitoring=MonitoringConfig(
            log_level=LogLevel.INFO,
            metrics_enabled=True,
            alerting_enabled=True
        )
    )

def get_config() -> Config:
    """Get configuration from file, environment, or create default"""
    config_path = os.getenv('CONFIG_PATH', 'config.yaml')
    
    # Try to load from file first
    if os.path.exists(config_path):
        return Config.from_file(config_path)
    
    # Try to load from environment
    if os.getenv('CONFIG_FROM_ENV', '').lower() == 'true':
        return Config.from_env()
    
    # Create default configuration
    config = create_default_config()
    
    # Save default config for future use
    config.to_file(config_path)
    print(f"Created default configuration at {config_path}")
    print("Please update the configuration with your API keys and settings.")
    
    return config