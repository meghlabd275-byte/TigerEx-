#!/usr/bin/env python3
"""
@file start_enhanced_services.py
@description TigerEx services startup/initialization script
@author TigerEx Development Team
"""

import asyncio
import subprocess
import signal
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ServiceManager:
    def __init__(self):
        self.services: Dict[str, subprocess.Popen] = {}
        self.running = True
        
        # Service configurations
        self.service_configs = [
            {
                'name': 'unified-admin-panel',
                'script': 'enhanced_server.py',
                'port': 4001,
                'directory': 'backend/unified-admin-panel',
                'description': 'Consolidated Admin Dashboard'
            },
            {
                'name': 'consolidated-trading-engine',
                'script': 'consolidated_main.py',
                'port': 3001,
                'directory': 'backend/trading-engine',
                'description': 'Advanced Trading Engine'
            },
            {
                'name': 'consolidated-liquidity-aggregator',
                'script': 'consolidated_main.py',
                'port': 3002,
                'directory': 'backend/liquidity-aggregator',
                'description': 'Multi-Exchange Liquidity Aggregator'
            },
            {
                'name': 'enhanced-copy-trading',
                'script': 'enhanced_main.py',
                'port': 3003,
                'directory': 'backend/copy-trading-service',
                'description': 'Professional Copy Trading Platform'
            },
            {
                'name': 'advanced-defi-integration',
                'script': 'advanced_main.py',
                'port': 3004,
                'directory': 'backend/defi-integration-service',
                'description': 'Web3 and DeFi Integration Hub'
            }
        ]
    
    async def start_service(self, config: Dict) -> bool:
        """Start a single service"""
        try:
            script_path = Path(config['directory']) / config['script']
            if not script_path.exists():
                logger.error(f"Script not found: {script_path}")
                return False
            
            # Create virtual environment command
            cmd = [
                sys.executable, '-m', 'uvicorn',
                f"{config['script'].replace('.py', '')}:app",
                '--host', '0.0.0.0',
                '--port', str(config['port']),
                '--reload'
            ]
            
            logger.info(f"Starting {config['name']} on port {config['port']}")
            logger.info(f"Description: {config['description']}")
            
            # Start subprocess
            process = subprocess.Popen(
                cmd,
                cwd=config['directory'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            self.services[config['name']] = process
            
            # Wait a moment and check if process is still running
            await asyncio.sleep(2)
            
            if process.poll() is None:
                logger.info(f"✅ {config['name']} started successfully")
                return True
            else:
                logger.error(f"❌ {config['name']} failed to start")
                return False
                
        except Exception as e:
            logger.error(f"Error starting {config['name']}: {e}")
            return False
    
    async def start_all_services(self) -> bool:
        """Start all enhanced services"""
        logger.info("🚀 Starting TigerEx Enhanced Services...")
        logger.info("=" * 60)
        
        success_count = 0
        
        for config in self.service_configs:
            if await self.start_service(config):
                success_count += 1
                await asyncio.sleep(1)  # Stagger startups
        
        logger.info("=" * 60)
        logger.info(f"Services started: {success_count}/{len(self.service_configs)}")
        
        if success_count == len(self.service_configs):
            logger.info("🎉 All services started successfully!")
            await self.print_service_status()
            return True
        else:
            logger.error(f"⚠️ {len(self.service_configs) - success_count} services failed to start")
            return False
    
    async def print_service_status(self):
        """Print status of all services"""
        logger.info("\n📊 Service Status:")
        logger.info("-" * 60)
        
        for config in self.service_configs:
            service_name = config['name']
            if service_name in self.services:
                process = self.services[service_name]
                if process.poll() is None:
                    status = "🟢 RUNNING"
                    url = f"http://localhost:{config['port']}"
                else:
                    status = "🔴 STOPPED"
                    url = "N/A"
            else:
                status = "🔴 NOT STARTED"
                url = "N/A"
            
            logger.info(f"{service_name:<25} {status:<12} {url}")
        
        logger.info("-" * 60)
        logger.info("🌐 Access Points:")
        logger.info(f"   Admin Panel:    http://localhost:4001/docs")
        logger.info(f"   Trading Engine: http://localhost:3001/docs")
        logger.info(f"   Liquidity:      http://localhost:3002/docs")
        logger.info(f"   Copy Trading:   http://localhost:3003/docs")
        logger.info(f"   DeFi Integration: http://localhost:3004/docs")
    
    async def monitor_services(self):
        """Monitor running services"""
        logger.info("📈 Monitoring services...")
        
        while self.running:
            try:
                for name, process in list(self.services.items()):
                    if process.poll() is not None:
                        logger.warning(f"⚠️ Service {name} has stopped unexpectedly")
                        # Attempt to restart
                        config = next(c for c in self.service_configs if c['name'] == name)
                        await self.start_service(config)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring services: {e}")
                await asyncio.sleep(5)
    
    async def stop_all_services(self):
        """Stop all running services"""
        logger.info("🛑 Stopping all services...")
        
        for name, process in self.services.items():
            try:
                process.terminate()
                process.wait(timeout=10)
                logger.info(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                logger.info(f"🔥 {name} force-killed")
            except Exception as e:
                logger.error(f"Error stopping {name}: {e}")
        
        self.services.clear()
        logger.info("All services stopped")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

async def main():
    """Main entry point"""
    manager = ServiceManager()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, manager.signal_handler)
    signal.signal(signal.SIGTERM, manager.signal_handler)
    
    try:
        # Start all services
        if await manager.start_all_services():
            # Monitor services
            await manager.monitor_services()
        else:
            logger.error("Failed to start all services")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    
    finally:
        await manager.stop_all_services()
        logger.info("👋 TigerEx Enhanced Services shutdown complete")

if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        sys.exit(1)
    
    # Check if required packages are installed
    required_packages = ['fastapi', 'uvicorn', 'pydantic', 'aiohttp']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {missing_packages}")
        logger.info("Install with: pip install " + " ".join(required_packages))
        sys.exit(1)
    
    # Run the service manager
    asyncio.run(main())def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
