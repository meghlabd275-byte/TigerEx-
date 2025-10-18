#!/usr/bin/env python3
"""
TigerEx Complete System Deployment Script
Deploys and starts all services with full admin controls
"""

import os
import sys
import subprocess
import time
import json
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TigerExDeployer:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.services = {
            'unified_backend': {
                'path': 'unified-backend',
                'main_file': 'complete_admin_system.py',
                'port': 8005,
                'dependencies': ['requirements.txt']
            },
            'data_fetchers': {
                'path': 'backend/comprehensive-data-fetchers',
                'main_file': 'complete_exchange_fetchers.py',
                'port': 8003,
                'dependencies': ['requirements.txt']
            },
            'admin_controls': {
                'path': 'backend/universal-admin-controls',
                'main_file': 'complete_admin_service.py',
                'port': 8004,
                'dependencies': ['requirements.txt']
            },
            'frontend_web': {
                'path': 'frontend',
                'main_file': 'package.json',
                'port': 3000,
                'type': 'nodejs'
            },
            'mobile_app': {
                'path': 'mobile-app',
                'main_file': 'package.json',
                'port': 8081,
                'type': 'react-native'
            },
            'desktop_app': {
                'path': 'desktop-app',
                'main_file': 'package.json',
                'port': None,
                'type': 'electron'
            }
        }
        self.processes = {}

    def check_prerequisites(self):
        """Check if all prerequisites are installed"""
        logger.info("Checking prerequisites...")
        
        # Check Python
        try:
            result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
            logger.info(f"Python version: {result.stdout.strip()}")
        except FileNotFoundError:
            logger.error("Python3 not found. Please install Python 3.11+")
            return False

        # Check Node.js
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            logger.info(f"Node.js version: {result.stdout.strip()}")
        except FileNotFoundError:
            logger.error("Node.js not found. Please install Node.js 20+")
            return False

        # Check npm
        try:
            result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
            logger.info(f"npm version: {result.stdout.strip()}")
        except FileNotFoundError:
            logger.error("npm not found. Please install npm")
            return False

        # Check Docker (optional)
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            logger.info(f"Docker version: {result.stdout.strip()}")
        except FileNotFoundError:
            logger.warning("Docker not found. Docker deployment will not be available")

        return True

    def install_dependencies(self):
        """Install dependencies for all services"""
        logger.info("Installing dependencies...")
        
        def install_python_deps(service_name, service_config):
            service_path = self.base_dir / service_config['path']
            req_file = service_path / 'requirements.txt'
            
            if req_file.exists():
                logger.info(f"Installing Python dependencies for {service_name}")
                try:
                    subprocess.run([
                        'pip3', 'install', '-r', str(req_file)
                    ], check=True, cwd=service_path)
                    logger.info(f"✓ Dependencies installed for {service_name}")
                except subprocess.CalledProcessError as e:
                    logger.error(f"✗ Failed to install dependencies for {service_name}: {e}")
                    return False
            return True

        def install_node_deps(service_name, service_config):
            service_path = self.base_dir / service_config['path']
            package_file = service_path / 'package.json'
            
            if package_file.exists():
                logger.info(f"Installing Node.js dependencies for {service_name}")
                try:
                    subprocess.run(['npm', 'install'], check=True, cwd=service_path)
                    logger.info(f"✓ Dependencies installed for {service_name}")
                except subprocess.CalledProcessError as e:
                    logger.error(f"✗ Failed to install dependencies for {service_name}: {e}")
                    return False
            return True

        # Install dependencies in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            
            for service_name, service_config in self.services.items():
                if service_config.get('type') in ['nodejs', 'react-native', 'electron']:
                    future = executor.submit(install_node_deps, service_name, service_config)
                else:
                    future = executor.submit(install_python_deps, service_name, service_config)
                futures.append((service_name, future))

            for service_name, future in futures:
                try:
                    success = future.result(timeout=300)  # 5 minute timeout
                    if not success:
                        logger.error(f"Failed to install dependencies for {service_name}")
                        return False
                except Exception as e:
                    logger.error(f"Error installing dependencies for {service_name}: {e}")
                    return False

        return True

    def setup_environment(self):
        """Setup environment variables and configuration"""
        logger.info("Setting up environment...")
        
        # Create .env files for services
        env_configs = {
            'unified-backend/.env': {
                'DATABASE_URL': 'postgresql://tigerex:tigerex123@localhost:5432/tigerex_db',
                'REDIS_URL': 'redis://localhost:6379',
                'JWT_SECRET': 'your-secret-key-change-this-in-production',
                'JWT_ALGORITHM': 'HS256',
                'ACCESS_TOKEN_EXPIRE_MINUTES': '30'
            },
            'backend/comprehensive-data-fetchers/.env': {
                'API_PORT': '8003',
                'JWT_SECRET': 'your-secret-key-change-this-in-production'
            },
            'backend/universal-admin-controls/.env': {
                'API_PORT': '8004',
                'JWT_SECRET': 'your-secret-key-change-this-in-production',
                'DATABASE_URL': 'postgresql://tigerex:tigerex123@localhost:5432/tigerex_db',
                'REDIS_URL': 'redis://localhost:6379'
            }
        }

        for env_file, config in env_configs.items():
            env_path = self.base_dir / env_file
            env_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(env_path, 'w') as f:
                for key, value in config.items():
                    f.write(f"{key}={value}\n")
            
            logger.info(f"✓ Created {env_file}")

        return True

    def start_service(self, service_name, service_config):
        """Start a single service"""
        service_path = self.base_dir / service_config['path']
        
        try:
            if service_config.get('type') == 'nodejs':
                # Start Node.js service
                cmd = ['npm', 'start']
            elif service_config.get('type') == 'react-native':
                # Start React Native metro bundler
                cmd = ['npm', 'start']
            elif service_config.get('type') == 'electron':
                # Start Electron app
                cmd = ['npm', 'run', 'electron']
            else:
                # Start Python service
                cmd = ['python3', service_config['main_file']]

            logger.info(f"Starting {service_name} service...")
            process = subprocess.Popen(
                cmd,
                cwd=service_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes[service_name] = process
            logger.info(f"✓ {service_name} service started (PID: {process.pid})")
            
            # Wait a moment to check if process started successfully
            time.sleep(2)
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                logger.error(f"✗ {service_name} service failed to start")
                logger.error(f"stdout: {stdout}")
                logger.error(f"stderr: {stderr}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to start {service_name}: {e}")
            return False

    def check_service_health(self, service_name, service_config):
        """Check if service is healthy"""
        if service_config['port'] is None:
            return True  # Skip health check for services without ports
        
        import requests
        
        try:
            url = f"http://localhost:{service_config['port']}/api/health"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                logger.info(f"✓ {service_name} health check passed")
                return True
            else:
                logger.warning(f"⚠ {service_name} health check returned {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠ {service_name} health check failed: {e}")
            return False

    def deploy_all_services(self):
        """Deploy all services"""
        logger.info("Starting all services...")
        
        # Start backend services first
        backend_services = ['unified_backend', 'data_fetchers', 'admin_controls']
        for service_name in backend_services:
            if service_name in self.services:
                success = self.start_service(service_name, self.services[service_name])
                if not success:
                    logger.error(f"Failed to start {service_name}")
                    return False
                time.sleep(3)  # Wait between service starts

        # Wait for backend services to be ready
        logger.info("Waiting for backend services to be ready...")
        time.sleep(10)

        # Check backend service health
        for service_name in backend_services:
            if service_name in self.services:
                self.check_service_health(service_name, self.services[service_name])

        # Start frontend services
        frontend_services = ['frontend_web']
        for service_name in frontend_services:
            if service_name in self.services:
                success = self.start_service(service_name, self.services[service_name])
                if not success:
                    logger.warning(f"Failed to start {service_name}")
                time.sleep(3)

        return True

    def create_docker_compose(self):
        """Create Docker Compose configuration"""
        logger.info("Creating Docker Compose configuration...")
        
        docker_compose = {
            'version': '3.8',
            'services': {
                'unified-backend': {
                    'build': './unified-backend',
                    'ports': ['8005:8005'],
                    'environment': [
                        'DATABASE_URL=postgresql://tigerex:tigerex123@postgres:5432/tigerex_db',
                        'REDIS_URL=redis://redis:6379',
                        'JWT_SECRET=your-secret-key-change-this-in-production'
                    ],
                    'depends_on': ['postgres', 'redis']
                },
                'data-fetchers': {
                    'build': './backend/comprehensive-data-fetchers',
                    'ports': ['8003:8003'],
                    'environment': [
                        'JWT_SECRET=your-secret-key-change-this-in-production'
                    ]
                },
                'admin-controls': {
                    'build': './backend/universal-admin-controls',
                    'ports': ['8004:8004'],
                    'environment': [
                        'DATABASE_URL=postgresql://tigerex:tigerex123@postgres:5432/tigerex_db',
                        'REDIS_URL=redis://redis:6379',
                        'JWT_SECRET=your-secret-key-change-this-in-production'
                    ],
                    'depends_on': ['postgres', 'redis']
                },
                'frontend': {
                    'build': './frontend',
                    'ports': ['3000:3000'],
                    'environment': [
                        'REACT_APP_API_URL=http://localhost:8005'
                    ]
                },
                'postgres': {
                    'image': 'postgres:15',
                    'environment': [
                        'POSTGRES_DB=tigerex_db',
                        'POSTGRES_USER=tigerex',
                        'POSTGRES_PASSWORD=tigerex123'
                    ],
                    'volumes': ['postgres_data:/var/lib/postgresql/data'],
                    'ports': ['5432:5432']
                },
                'redis': {
                    'image': 'redis:7-alpine',
                    'ports': ['6379:6379'],
                    'volumes': ['redis_data:/data']
                }
            },
            'volumes': {
                'postgres_data': {},
                'redis_data': {}
            }
        }

        with open(self.base_dir / 'docker-compose.yml', 'w') as f:
            import yaml
            yaml.dump(docker_compose, f, default_flow_style=False)

        logger.info("✓ Docker Compose configuration created")

    def create_dockerfiles(self):
        """Create Dockerfiles for services"""
        logger.info("Creating Dockerfiles...")
        
        # Python service Dockerfile template
        python_dockerfile = """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE {port}

CMD ["python", "{main_file}"]
"""

        # Node.js service Dockerfile template
        node_dockerfile = """FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE {port}

CMD ["npm", "start"]
"""

        # Create Dockerfiles for Python services
        python_services = ['unified_backend', 'data_fetchers', 'admin_controls']
        for service_name in python_services:
            if service_name in self.services:
                service_config = self.services[service_name]
                service_path = self.base_dir / service_config['path']
                
                dockerfile_content = python_dockerfile.format(
                    port=service_config['port'],
                    main_file=service_config['main_file']
                )
                
                with open(service_path / 'Dockerfile', 'w') as f:
                    f.write(dockerfile_content)
                
                logger.info(f"✓ Created Dockerfile for {service_name}")

        # Create Dockerfile for frontend
        frontend_path = self.base_dir / 'frontend'
        dockerfile_content = node_dockerfile.format(port=3000)
        
        with open(frontend_path / 'Dockerfile', 'w') as f:
            f.write(dockerfile_content)
        
        logger.info("✓ Created Dockerfile for frontend")

    def print_service_status(self):
        """Print status of all services"""
        logger.info("\n" + "="*60)
        logger.info("SERVICE STATUS")
        logger.info("="*60)
        
        for service_name, service_config in self.services.items():
            if service_name in self.processes:
                process = self.processes[service_name]
                if process.poll() is None:
                    status = "✓ RUNNING"
                    if service_config['port']:
                        status += f" (http://localhost:{service_config['port']})"
                else:
                    status = "✗ STOPPED"
            else:
                status = "- NOT STARTED"
            
            logger.info(f"{service_name:20} {status}")

        logger.info("="*60)
        logger.info("API ENDPOINTS:")
        logger.info("- Unified Backend:    http://localhost:8005")
        logger.info("- Data Fetchers:      http://localhost:8003")
        logger.info("- Admin Controls:     http://localhost:8004")
        logger.info("- Frontend Web:       http://localhost:3000")
        logger.info("="*60)
        logger.info("API DOCUMENTATION:")
        logger.info("- Unified Backend:    http://localhost:8005/docs")
        logger.info("- Data Fetchers:      http://localhost:8003/docs")
        logger.info("- Admin Controls:     http://localhost:8004/docs")
        logger.info("="*60)

    def stop_all_services(self):
        """Stop all running services"""
        logger.info("Stopping all services...")
        
        for service_name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=10)
                logger.info(f"✓ Stopped {service_name}")
            except subprocess.TimeoutExpired:
                process.kill()
                logger.info(f"✓ Force killed {service_name}")
            except Exception as e:
                logger.error(f"✗ Error stopping {service_name}: {e}")

    def run_deployment(self):
        """Run complete deployment process"""
        try:
            logger.info("🚀 Starting TigerEx Complete System Deployment")
            logger.info("="*60)
            
            # Check prerequisites
            if not self.check_prerequisites():
                logger.error("Prerequisites check failed")
                return False

            # Install dependencies
            if not self.install_dependencies():
                logger.error("Dependency installation failed")
                return False

            # Setup environment
            if not self.setup_environment():
                logger.error("Environment setup failed")
                return False

            # Create Docker configurations
            self.create_dockerfiles()
            self.create_docker_compose()

            # Deploy services
            if not self.deploy_all_services():
                logger.error("Service deployment failed")
                return False

            # Print status
            self.print_service_status()

            logger.info("\n🎉 TigerEx deployment completed successfully!")
            logger.info("Press Ctrl+C to stop all services")

            # Keep services running
            try:
                while True:
                    time.sleep(10)
                    # Check if any service has stopped
                    for service_name, process in list(self.processes.items()):
                        if process.poll() is not None:
                            logger.warning(f"⚠ {service_name} service has stopped")
            except KeyboardInterrupt:
                logger.info("\nReceived interrupt signal")
                self.stop_all_services()
                logger.info("✓ All services stopped")

            return True

        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            self.stop_all_services()
            return False

def main():
    """Main entry point"""
    deployer = TigerExDeployer()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'docker':
            logger.info("Creating Docker configuration only...")
            deployer.create_dockerfiles()
            deployer.create_docker_compose()
            logger.info("✓ Docker configuration created. Run 'docker-compose up' to start services")
        elif command == 'stop':
            logger.info("Stopping all services...")
            deployer.stop_all_services()
        else:
            logger.error(f"Unknown command: {command}")
            logger.info("Available commands: docker, stop")
            sys.exit(1)
    else:
        # Run full deployment
        success = deployer.run_deployment()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()