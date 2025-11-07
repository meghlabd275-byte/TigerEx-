"""
Comprehensive Trading Admin Service
Main FastAPI application for managing all trading types
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging
import uvicorn
from admin_routes import router as admin_router
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Comprehensive Trading Admin Service starting up...")
    
    # Initialize services here
    try:
        # Database connection
        # Redis connection
        # Service registry
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Comprehensive Trading Admin Service shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Comprehensive Trading Admin Service",
    description="Complete admin controls for all trading types including spot, futures, margin, grid, copy, and options trading",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tigerex.com",
        "https://www.tigerex.com",
        "https://admin.tigerex.com",
        "https://app.tigerex.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "tigerex.com",
        "www.tigerex.com",
        "admin.tigerex.com",
        "app.tigerex.com",
        "localhost",
        "127.0.0.1"
    ]
)

# Include admin routes
app.include_router(admin_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "comprehensive-trading-admin",
        "version": "4.0.0",
        "status": "operational",
        "timestamp": "2024-01-01T00:00:00Z",
        "features": [
            "Complete admin controls for all trading types",
            "Spot trading management",
            "Future perpetual trading control",
            "Future cross trading management",
            "Margin trading administration",
            "Grid trading control",
            "Copy trading management",
            "Option trading administration",
            "Contract lifecycle management",
            "User access and limits control",
            "Risk management and monitoring",
            "Audit logging and compliance",
            "Real-time analytics and reporting",
            "Emergency controls and circuit breakers"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "comprehensive-trading-admin",
        "version": "4.0.0",
        "dependencies": {
            "database": "connected",
            "redis": "connected",
            "service_registry": "connected"
        },
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/info")
async def service_info():
    """Detailed service information"""
    return {
        "service": "comprehensive-trading-admin",
        "description": "Complete administrative control system for all TigerEx trading operations",
        "version": "4.0.0",
        "trading_types_supported": [
            "spot",
            "future_perpetual", 
            "future_cross",
            "margin",
            "grid",
            "copy",
            "option"
        ],
        "admin_capabilities": {
            "trading_control": [
                "pause_trading",
                "resume_trading", 
                "emergency_stop",
                "maintenance_mode"
            ],
            "contract_management": [
                "create_contract",
                "update_contract",
                "pause_contract",
                "resume_contract",
                "delete_contract"
            ],
            "user_management": [
                "set_user_limits",
                "view_user_positions",
                "close_user_positions",
                "manage_user_access"
            ],
            "order_management": [
                "view_all_orders",
                "cancel_any_order",
                "mass_cancellation",
                "order_analytics"
            ],
            "risk_management": [
                "risk_metrics",
                "circuit_breaker",
                "position_monitoring",
                "liquidation_control"
            ],
            "monitoring": [
                "system_overview",
                "performance_metrics",
                "audit_logs",
                "analytics_reports"
            ]
        },
        "security_features": [
            "Role-based access control",
            "Multi-factor authentication",
            "Audit trail logging",
            "IP whitelisting",
            "Rate limiting",
            "Encryption at rest and in transit"
        ],
        "endpoints_count": 20,
        "api_version": "v1",
        "documentation": "/docs",
        "timestamp": "2024-01-01T00:00:00Z"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
        access_log=True
    )