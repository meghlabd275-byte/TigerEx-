#!/usr/bin/env python3
"""
TigerEx Block Explorer Service
One-click block explorer creation and deployment system for EVM and Web3 blockchains
"""

import os
import asyncio
import logging
import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aioredis
import asyncpg
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, validator
import docker
import kubernetes
from kubernetes import client, config
from web3 import Web3
from solana.rpc.api import Client as SolanaClient
import httpx
import jinja2
import aiofiles
import structlog
import uvicorn

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# FastAPI app
app = FastAPI(
    title="TigerEx Block Explorer Service",
    description="One-click block explorer creation and deployment system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/tigerex")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Docker configuration
    DOCKER_HOST = os.getenv("DOCKER_HOST", "unix://var/run/docker.sock")
    
    # Kubernetes configuration
    KUBE_CONFIG_PATH = os.getenv("KUBE_CONFIG_PATH", "~/.kube/config")
    
    # Domain configuration
    BASE_DOMAIN = os.getenv("BASE_DOMAIN", "tigerex.com")
    SUBDOMAIN_PREFIX = os.getenv("SUBDOMAIN_PREFIX", "explorer")
    
    # Template paths
    TEMPLATE_DIR = os.getenv("TEMPLATE_DIR", "./templates")
    BUILD_DIR = os.getenv("BUILD_DIR", "./builds")

config = Config()

# Enums
class BlockchainType(str, Enum):
    EVM = "evm"
    SOLANA = "solana"
    BITCOIN = "bitcoin"
    COSMOS = "cosmos"
    SUBSTRATE = "substrate"

class ExplorerStatus(str, Enum):
    CREATING = "creating"
    BUILDING = "building"
    DEPLOYING = "deploying"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    DELETED = "deleted"

class DeploymentType(str, Enum):
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    STANDALONE = "standalone"

# Data Models
@dataclass
class BlockchainConfig:
    name: str
    chain_id: int
    rpc_url: str
    ws_url: Optional[str]
    explorer_api_url: Optional[str]
    native_currency: Dict[str, Any]
    block_time: int  # seconds
    consensus_mechanism: str
    features: List[str]

@dataclass
class ExplorerConfig:
    id: str
    name: str
    blockchain_type: BlockchainType
    blockchain_config: BlockchainConfig
    domain: str
    subdomain: str
    deployment_type: DeploymentType
    custom_theme: Optional[Dict[str, Any]]
    features: List[str]
    api_keys: Dict[str, str]
    status: ExplorerStatus
    created_at: datetime
    updated_at: datetime
    deployed_at: Optional[datetime]
    creator_id: str
    organization_id: Optional[str]

# Pydantic Models
class CreateExplorerRequest(BaseModel):
    name: str
    blockchain_type: BlockchainType
    chain_id: int
    rpc_url: str
    ws_url: Optional[str] = None
    native_currency_name: str = "ETH"
    native_currency_symbol: str = "ETH"
    native_currency_decimals: int = 18
    block_time: int = 15
    consensus_mechanism: str = "proof-of-stake"
    subdomain: Optional[str] = None
    deployment_type: DeploymentType = DeploymentType.DOCKER
    custom_theme: Optional[Dict[str, Any]] = None
    features: List[str] = ["blocks", "transactions", "addresses", "tokens", "contracts"]
    organization_id: Optional[str] = None

class UpdateExplorerRequest(BaseModel):
    name: Optional[str] = None
    rpc_url: Optional[str] = None
    ws_url: Optional[str] = None
    custom_theme: Optional[Dict[str, Any]] = None
    features: Optional[List[str]] = None

class ExplorerResponse(BaseModel):
    id: str
    name: str
    blockchain_type: BlockchainType
    chain_id: int
    domain: str
    subdomain: str
    status: ExplorerStatus
    deployment_type: DeploymentType
    features: List[str]
    created_at: datetime
    updated_at: datetime
    deployed_at: Optional[datetime]
    urls: Dict[str, str]

class DeploymentInfo(BaseModel):
    container_id: Optional[str] = None
    pod_name: Optional[str] = None
    service_name: Optional[str] = None
    ingress_name: Optional[str] = None
    namespace: Optional[str] = None
    ports: Dict[str, int] = {}
    environment: Dict[str, str] = {}

# Block Explorer Manager
class BlockExplorerManager:
    def __init__(self):
        self.redis_client = None
        self.db_pool = None
        self.docker_client = None
        self.k8s_client = None
        self.template_env = None
        
        # Initialize clients
        asyncio.create_task(self.initialize_clients())
    
    async def initialize_clients(self):
        """Initialize all required clients"""
        try:
            # Redis client
            self.redis_client = aioredis.from_url(config.REDIS_URL)
            
            # Database pool
            self.db_pool = await asyncpg.create_pool(config.DATABASE_URL)
            
            # Docker client
            self.docker_client = docker.from_env()
            
            # Kubernetes client
            try:
                config.load_incluster_config()
            except:
                config.load_kube_config(config_file=config.KUBE_CONFIG_PATH)
            self.k8s_client = client.ApiClient()
            
            # Jinja2 template environment
            self.template_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(config.TEMPLATE_DIR),
                autoescape=jinja2.select_autoescape(['html', 'xml'])
            )
            
            # Create necessary directories
            os.makedirs(config.BUILD_DIR, exist_ok=True)
            
            logger.info("Block explorer manager initialized successfully")
            
        except Exception as e:
            logger.error("Error initializing block explorer manager", error=str(e))
            raise
    
    async def create_explorer(self, request: CreateExplorerRequest, creator_id: str) -> ExplorerConfig:
        """Create a new block explorer"""
        try:
            # Generate unique ID and subdomain
            explorer_id = f"explorer_{int(datetime.now().timestamp())}"
            subdomain = request.subdomain or f"{config.SUBDOMAIN_PREFIX}-{explorer_id}"
            domain = f"{subdomain}.{config.BASE_DOMAIN}"
            
            # Create blockchain configuration
            blockchain_config = BlockchainConfig(
                name=request.name,
                chain_id=request.chain_id,
                rpc_url=request.rpc_url,
                ws_url=request.ws_url,
                explorer_api_url=None,
                native_currency={
                    "name": request.native_currency_name,
                    "symbol": request.native_currency_symbol,
                    "decimals": request.native_currency_decimals
                },
                block_time=request.block_time,
                consensus_mechanism=request.consensus_mechanism,
                features=request.features
            )
            
            # Create explorer configuration
            explorer_config = ExplorerConfig(
                id=explorer_id,
                name=request.name,
                blockchain_type=request.blockchain_type,
                blockchain_config=blockchain_config,
                domain=domain,
                subdomain=subdomain,
                deployment_type=request.deployment_type,
                custom_theme=request.custom_theme,
                features=request.features,
                api_keys={},
                status=ExplorerStatus.CREATING,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                deployed_at=None,
                creator_id=creator_id,
                organization_id=request.organization_id
            )
            
            # Save to database
            await self.save_explorer_config(explorer_config)
            
            # Start deployment process
            asyncio.create_task(self.deploy_explorer(explorer_config))
            
            logger.info("Explorer creation initiated", explorer_id=explorer_id, name=request.name)
            return explorer_config
            
        except Exception as e:
            logger.error("Error creating explorer", error=str(e))
            raise HTTPException(status_code=500, detail=f"Failed to create explorer: {str(e)}")
    
    async def deploy_explorer(self, explorer_config: ExplorerConfig):
        """Deploy the block explorer"""
        try:
            # Update status to building
            explorer_config.status = ExplorerStatus.BUILDING
            explorer_config.updated_at = datetime.now()
            await self.save_explorer_config(explorer_config)
            
            # Generate explorer application
            await self.generate_explorer_app(explorer_config)
            
            # Build Docker image
            image_tag = await self.build_docker_image(explorer_config)
            
            # Update status to deploying
            explorer_config.status = ExplorerStatus.DEPLOYING
            explorer_config.updated_at = datetime.now()
            await self.save_explorer_config(explorer_config)
            
            # Deploy based on deployment type
            if explorer_config.deployment_type == DeploymentType.DOCKER:
                await self.deploy_docker_container(explorer_config, image_tag)
            elif explorer_config.deployment_type == DeploymentType.KUBERNETES:
                await self.deploy_kubernetes_resources(explorer_config, image_tag)
            
            # Update status to running
            explorer_config.status = ExplorerStatus.RUNNING
            explorer_config.deployed_at = datetime.now()
            explorer_config.updated_at = datetime.now()
            await self.save_explorer_config(explorer_config)
            
            logger.info("Explorer deployed successfully", explorer_id=explorer_config.id)
            
        except Exception as e:
            # Update status to error
            explorer_config.status = ExplorerStatus.ERROR
            explorer_config.updated_at = datetime.now()
            await self.save_explorer_config(explorer_config)
            
            logger.error("Error deploying explorer", explorer_id=explorer_config.id, error=str(e))
    
    async def generate_explorer_app(self, explorer_config: ExplorerConfig):
        """Generate the block explorer application code"""
        try:
            build_path = os.path.join(config.BUILD_DIR, explorer_config.id)
            os.makedirs(build_path, exist_ok=True)
            
            # Template context
            context = {
                'explorer': asdict(explorer_config),
                'blockchain': asdict(explorer_config.blockchain_config),
                'timestamp': datetime.now().isoformat()
            }
            
            # Generate different components based on blockchain type
            if explorer_config.blockchain_type == BlockchainType.EVM:
                await self.generate_evm_explorer(build_path, context)
            elif explorer_config.blockchain_type == BlockchainType.SOLANA:
                await self.generate_solana_explorer(build_path, context)
            elif explorer_config.blockchain_type == BlockchainType.BITCOIN:
                await self.generate_bitcoin_explorer(build_path, context)
            
            logger.info("Explorer app generated", explorer_id=explorer_config.id, path=build_path)
            
        except Exception as e:
            logger.error("Error generating explorer app", explorer_id=explorer_config.id, error=str(e))
            raise
    
    async def generate_evm_explorer(self, build_path: str, context: Dict[str, Any]):
        """Generate EVM-compatible block explorer"""
        # Generate package.json
        package_json = self.template_env.get_template('evm/package.json.j2').render(context)
        async with aiofiles.open(os.path.join(build_path, 'package.json'), 'w') as f:
            await f.write(package_json)
        
        # Generate Dockerfile
        dockerfile = self.template_env.get_template('evm/Dockerfile.j2').render(context)
        async with aiofiles.open(os.path.join(build_path, 'Dockerfile'), 'w') as f:
            await f.write(dockerfile)
        
        # Generate main application files
        templates = [
            ('evm/src/app.js.j2', 'src/app.js'),
            ('evm/src/config.js.j2', 'src/config.js'),
            ('evm/src/routes/blocks.js.j2', 'src/routes/blocks.js'),
            ('evm/src/routes/transactions.js.j2', 'src/routes/transactions.js'),
            ('evm/src/routes/addresses.js.j2', 'src/routes/addresses.js'),
            ('evm/src/services/blockchain.js.j2', 'src/services/blockchain.js'),
            ('evm/public/index.html.j2', 'public/index.html'),
            ('evm/public/css/style.css.j2', 'public/css/style.css'),
            ('evm/public/js/main.js.j2', 'public/js/main.js')
        ]
        
        for template_path, output_path in templates:
            os.makedirs(os.path.dirname(os.path.join(build_path, output_path)), exist_ok=True)
            content = self.template_env.get_template(template_path).render(context)
            async with aiofiles.open(os.path.join(build_path, output_path), 'w') as f:
                await f.write(content)
    
    async def generate_solana_explorer(self, build_path: str, context: Dict[str, Any]):
        """Generate Solana block explorer"""
        # Similar to EVM but with Solana-specific templates
        templates = [
            ('solana/package.json.j2', 'package.json'),
            ('solana/Dockerfile.j2', 'Dockerfile'),
            ('solana/src/app.js.j2', 'src/app.js'),
            ('solana/src/config.js.j2', 'src/config.js'),
            ('solana/src/services/solana.js.j2', 'src/services/solana.js')
        ]
        
        for template_path, output_path in templates:
            os.makedirs(os.path.dirname(os.path.join(build_path, output_path)), exist_ok=True)
            content = self.template_env.get_template(template_path).render(context)
            async with aiofiles.open(os.path.join(build_path, output_path), 'w') as f:
                await f.write(content)
    
    async def generate_bitcoin_explorer(self, build_path: str, context: Dict[str, Any]):
        """Generate Bitcoin block explorer"""
        # Bitcoin-specific templates
        templates = [
            ('bitcoin/package.json.j2', 'package.json'),
            ('bitcoin/Dockerfile.j2', 'Dockerfile'),
            ('bitcoin/src/app.js.j2', 'src/app.js'),
            ('bitcoin/src/config.js.j2', 'src/config.js'),
            ('bitcoin/src/services/bitcoin.js.j2', 'src/services/bitcoin.js')
        ]
        
        for template_path, output_path in templates:
            os.makedirs(os.path.dirname(os.path.join(build_path, output_path)), exist_ok=True)
            content = self.template_env.get_template(template_path).render(context)
            async with aiofiles.open(os.path.join(build_path, output_path), 'w') as f:
                await f.write(content)
    
    async def build_docker_image(self, explorer_config: ExplorerConfig) -> str:
        """Build Docker image for the explorer"""
        try:
            build_path = os.path.join(config.BUILD_DIR, explorer_config.id)
            image_tag = f"tigerex-explorer-{explorer_config.id}:latest"
            
            # Build the image
            image, logs = self.docker_client.images.build(
                path=build_path,
                tag=image_tag,
                rm=True,
                forcerm=True
            )
            
            logger.info("Docker image built successfully", 
                       explorer_id=explorer_config.id, 
                       image_tag=image_tag)
            
            return image_tag
            
        except Exception as e:
            logger.error("Error building Docker image", 
                        explorer_id=explorer_config.id, 
                        error=str(e))
            raise
    
    async def deploy_docker_container(self, explorer_config: ExplorerConfig, image_tag: str):
        """Deploy explorer as Docker container"""
        try:
            container_name = f"tigerex-explorer-{explorer_config.id}"
            
            # Container configuration
            environment = {
                'NODE_ENV': 'production',
                'RPC_URL': explorer_config.blockchain_config.rpc_url,
                'WS_URL': explorer_config.blockchain_config.ws_url or '',
                'CHAIN_ID': str(explorer_config.blockchain_config.chain_id),
                'EXPLORER_NAME': explorer_config.name
            }
            
            # Run container
            container = self.docker_client.containers.run(
                image_tag,
                name=container_name,
                environment=environment,
                ports={'3000/tcp': None},  # Auto-assign port
                detach=True,
                restart_policy={"Name": "unless-stopped"}
            )
            
            # Get assigned port
            container.reload()
            port_mapping = container.attrs['NetworkSettings']['Ports']['3000/tcp']
            host_port = port_mapping[0]['HostPort'] if port_mapping else None
            
            # Save deployment info
            deployment_info = DeploymentInfo(
                container_id=container.id,
                ports={'http': int(host_port)} if host_port else {},
                environment=environment
            )
            
            await self.save_deployment_info(explorer_config.id, deployment_info)
            
            logger.info("Docker container deployed", 
                       explorer_id=explorer_config.id,
                       container_id=container.id,
                       port=host_port)
            
        except Exception as e:
            logger.error("Error deploying Docker container", 
                        explorer_id=explorer_config.id, 
                        error=str(e))
            raise
    
    async def deploy_kubernetes_resources(self, explorer_config: ExplorerConfig, image_tag: str):
        """Deploy explorer on Kubernetes"""
        try:
            namespace = f"tigerex-explorer-{explorer_config.id}"
            
            # Create namespace
            await self.create_k8s_namespace(namespace)
            
            # Create deployment
            await self.create_k8s_deployment(explorer_config, image_tag, namespace)
            
            # Create service
            await self.create_k8s_service(explorer_config, namespace)
            
            # Create ingress
            await self.create_k8s_ingress(explorer_config, namespace)
            
            # Save deployment info
            deployment_info = DeploymentInfo(
                namespace=namespace,
                service_name=f"explorer-{explorer_config.id}",
                ingress_name=f"explorer-{explorer_config.id}-ingress",
                ports={'http': 3000}
            )
            
            await self.save_deployment_info(explorer_config.id, deployment_info)
            
            logger.info("Kubernetes resources deployed", 
                       explorer_id=explorer_config.id,
                       namespace=namespace)
            
        except Exception as e:
            logger.error("Error deploying Kubernetes resources", 
                        explorer_id=explorer_config.id, 
                        error=str(e))
            raise
    
    async def create_k8s_namespace(self, namespace: str):
        """Create Kubernetes namespace"""
        v1 = client.CoreV1Api(self.k8s_client)
        
        namespace_manifest = client.V1Namespace(
            metadata=client.V1ObjectMeta(name=namespace)
        )
        
        try:
            v1.create_namespace(body=namespace_manifest)
        except client.exceptions.ApiException as e:
            if e.status != 409:  # Ignore if namespace already exists
                raise
    
    async def create_k8s_deployment(self, explorer_config: ExplorerConfig, image_tag: str, namespace: str):
        """Create Kubernetes deployment"""
        apps_v1 = client.AppsV1Api(self.k8s_client)
        
        deployment_manifest = client.V1Deployment(
            metadata=client.V1ObjectMeta(
                name=f"explorer-{explorer_config.id}",
                namespace=namespace
            ),
            spec=client.V1DeploymentSpec(
                replicas=1,
                selector=client.V1LabelSelector(
                    match_labels={"app": f"explorer-{explorer_config.id}"}
                ),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                        labels={"app": f"explorer-{explorer_config.id}"}
                    ),
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name="explorer",
                                image=image_tag,
                                ports=[client.V1ContainerPort(container_port=3000)],
                                env=[
                                    client.V1EnvVar(name="NODE_ENV", value="production"),
                                    client.V1EnvVar(name="RPC_URL", value=explorer_config.blockchain_config.rpc_url),
                                    client.V1EnvVar(name="CHAIN_ID", value=str(explorer_config.blockchain_config.chain_id))
                                ]
                            )
                        ]
                    )
                )
            )
        )
        
        apps_v1.create_namespaced_deployment(namespace=namespace, body=deployment_manifest)
    
    async def create_k8s_service(self, explorer_config: ExplorerConfig, namespace: str):
        """Create Kubernetes service"""
        v1 = client.CoreV1Api(self.k8s_client)
        
        service_manifest = client.V1Service(
            metadata=client.V1ObjectMeta(
                name=f"explorer-{explorer_config.id}",
                namespace=namespace
            ),
            spec=client.V1ServiceSpec(
                selector={"app": f"explorer-{explorer_config.id}"},
                ports=[
                    client.V1ServicePort(
                        port=80,
                        target_port=3000,
                        protocol="TCP"
                    )
                ],
                type="ClusterIP"
            )
        )
        
        v1.create_namespaced_service(namespace=namespace, body=service_manifest)
    
    async def create_k8s_ingress(self, explorer_config: ExplorerConfig, namespace: str):
        """Create Kubernetes ingress"""
        networking_v1 = client.NetworkingV1Api(self.k8s_client)
        
        ingress_manifest = client.V1Ingress(
            metadata=client.V1ObjectMeta(
                name=f"explorer-{explorer_config.id}-ingress",
                namespace=namespace,
                annotations={
                    "kubernetes.io/ingress.class": "nginx",
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod"
                }
            ),
            spec=client.V1IngressSpec(
                tls=[
                    client.V1IngressTLS(
                        hosts=[explorer_config.domain],
                        secret_name=f"explorer-{explorer_config.id}-tls"
                    )
                ],
                rules=[
                    client.V1IngressRule(
                        host=explorer_config.domain,
                        http=client.V1HTTPIngressRuleValue(
                            paths=[
                                client.V1HTTPIngressPath(
                                    path="/",
                                    path_type="Prefix",
                                    backend=client.V1IngressBackend(
                                        service=client.V1IngressServiceBackend(
                                            name=f"explorer-{explorer_config.id}",
                                            port=client.V1ServiceBackendPort(number=80)
                                        )
                                    )
                                )
                            ]
                        )
                    )
                ]
            )
        )
        
        networking_v1.create_namespaced_ingress(namespace=namespace, body=ingress_manifest)
    
    async def save_explorer_config(self, explorer_config: ExplorerConfig):
        """Save explorer configuration to database"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO block_explorers (
                    id, name, blockchain_type, blockchain_config, domain, subdomain,
                    deployment_type, custom_theme, features, api_keys, status,
                    created_at, updated_at, deployed_at, creator_id, organization_id
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    blockchain_config = EXCLUDED.blockchain_config,
                    custom_theme = EXCLUDED.custom_theme,
                    features = EXCLUDED.features,
                    status = EXCLUDED.status,
                    updated_at = EXCLUDED.updated_at,
                    deployed_at = EXCLUDED.deployed_at
            """, 
                explorer_config.id,
                explorer_config.name,
                explorer_config.blockchain_type.value,
                json.dumps(asdict(explorer_config.blockchain_config)),
                explorer_config.domain,
                explorer_config.subdomain,
                explorer_config.deployment_type.value,
                json.dumps(explorer_config.custom_theme) if explorer_config.custom_theme else None,
                json.dumps(explorer_config.features),
                json.dumps(explorer_config.api_keys),
                explorer_config.status.value,
                explorer_config.created_at,
                explorer_config.updated_at,
                explorer_config.deployed_at,
                explorer_config.creator_id,
                explorer_config.organization_id
            )
    
    async def save_deployment_info(self, explorer_id: str, deployment_info: DeploymentInfo):
        """Save deployment information to Redis"""
        await self.redis_client.set(
            f"deployment:{explorer_id}",
            json.dumps(asdict(deployment_info)),
            ex=86400  # 24 hours
        )
    
    async def get_explorer_config(self, explorer_id: str) -> Optional[ExplorerConfig]:
        """Get explorer configuration from database"""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM block_explorers WHERE id = $1",
                explorer_id
            )
            
            if not row:
                return None
            
            blockchain_config = BlockchainConfig(**json.loads(row['blockchain_config']))
            
            return ExplorerConfig(
                id=row['id'],
                name=row['name'],
                blockchain_type=BlockchainType(row['blockchain_type']),
                blockchain_config=blockchain_config,
                domain=row['domain'],
                subdomain=row['subdomain'],
                deployment_type=DeploymentType(row['deployment_type']),
                custom_theme=json.loads(row['custom_theme']) if row['custom_theme'] else None,
                features=json.loads(row['features']),
                api_keys=json.loads(row['api_keys']),
                status=ExplorerStatus(row['status']),
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                deployed_at=row['deployed_at'],
                creator_id=row['creator_id'],
                organization_id=row['organization_id']
            )

# Global manager instance
explorer_manager = BlockExplorerManager()

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "TigerEx Block Explorer Service",
        "features": [
            "One-click block explorer creation",
            "EVM, Solana, Bitcoin support",
            "Docker and Kubernetes deployment",
            "Custom themes and branding",
            "Auto SSL certificates",
            "Real-time blockchain data"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "block-explorer"}

@app.post("/explorers", response_model=ExplorerResponse)
async def create_explorer(
    request: CreateExplorerRequest,
    creator_id: str = "default_user"  # In production, get from JWT token
):
    """Create a new block explorer"""
    explorer_config = await explorer_manager.create_explorer(request, creator_id)
    
    return ExplorerResponse(
        id=explorer_config.id,
        name=explorer_config.name,
        blockchain_type=explorer_config.blockchain_type,
        chain_id=explorer_config.blockchain_config.chain_id,
        domain=explorer_config.domain,
        subdomain=explorer_config.subdomain,
        status=explorer_config.status,
        deployment_type=explorer_config.deployment_type,
        features=explorer_config.features,
        created_at=explorer_config.created_at,
        updated_at=explorer_config.updated_at,
        deployed_at=explorer_config.deployed_at,
        urls={
            "explorer": f"https://{explorer_config.domain}",
            "api": f"https://{explorer_config.domain}/api"
        }
    )

@app.get("/explorers", response_model=List[ExplorerResponse])
async def list_explorers(
    creator_id: str = "default_user",  # In production, get from JWT token
    status: Optional[ExplorerStatus] = None,
    limit: int = 50,
    offset: int = 0
):
    """List block explorers"""
    async with explorer_manager.db_pool.acquire() as conn:
        query = "SELECT * FROM block_explorers WHERE creator_id = $1"
        params = [creator_id]
        
        if status:
            query += " AND status = $2"
            params.append(status.value)
        
        query += " ORDER BY created_at DESC LIMIT $" + str(len(params) + 1) + " OFFSET $" + str(len(params) + 2)
        params.extend([limit, offset])
        
        rows = await conn.fetch(query, *params)
        
        explorers = []
        for row in rows:
            blockchain_config = json.loads(row['blockchain_config'])
            explorers.append(ExplorerResponse(
                id=row['id'],
                name=row['name'],
                blockchain_type=BlockchainType(row['blockchain_type']),
                chain_id=blockchain_config['chain_id'],
                domain=row['domain'],
                subdomain=row['subdomain'],
                status=ExplorerStatus(row['status']),
                deployment_type=DeploymentType(row['deployment_type']),
                features=json.loads(row['features']),
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                deployed_at=row['deployed_at'],
                urls={
                    "explorer": f"https://{row['domain']}",
                    "api": f"https://{row['domain']}/api"
                }
            ))
        
        return explorers

@app.get("/explorers/{explorer_id}", response_model=ExplorerResponse)
async def get_explorer(explorer_id: str):
    """Get specific block explorer"""
    explorer_config = await explorer_manager.get_explorer_config(explorer_id)
    
    if not explorer_config:
        raise HTTPException(status_code=404, detail="Explorer not found")
    
    return ExplorerResponse(
        id=explorer_config.id,
        name=explorer_config.name,
        blockchain_type=explorer_config.blockchain_type,
        chain_id=explorer_config.blockchain_config.chain_id,
        domain=explorer_config.domain,
        subdomain=explorer_config.subdomain,
        status=explorer_config.status,
        deployment_type=explorer_config.deployment_type,
        features=explorer_config.features,
        created_at=explorer_config.created_at,
        updated_at=explorer_config.updated_at,
        deployed_at=explorer_config.deployed_at,
        urls={
            "explorer": f"https://{explorer_config.domain}",
            "api": f"https://{explorer_config.domain}/api"
        }
    )

@app.put("/explorers/{explorer_id}")
async def update_explorer(
    explorer_id: str,
    request: UpdateExplorerRequest
):
    """Update block explorer configuration"""
    explorer_config = await explorer_manager.get_explorer_config(explorer_id)
    
    if not explorer_config:
        raise HTTPException(status_code=404, detail="Explorer not found")
    
    # Update configuration
    if request.name:
        explorer_config.name = request.name
    if request.rpc_url:
        explorer_config.blockchain_config.rpc_url = request.rpc_url
    if request.ws_url:
        explorer_config.blockchain_config.ws_url = request.ws_url
    if request.custom_theme:
        explorer_config.custom_theme = request.custom_theme
    if request.features:
        explorer_config.features = request.features
    
    explorer_config.updated_at = datetime.now()
    
    # Save updated configuration
    await explorer_manager.save_explorer_config(explorer_config)
    
    return {"message": "Explorer updated successfully"}

@app.delete("/explorers/{explorer_id}")
async def delete_explorer(explorer_id: str):
    """Delete block explorer"""
    explorer_config = await explorer_manager.get_explorer_config(explorer_id)
    
    if not explorer_config:
        raise HTTPException(status_code=404, detail="Explorer not found")
    
    try:
        # Stop and remove deployment
        if explorer_config.deployment_type == DeploymentType.DOCKER:
            # Stop Docker container
            try:
                container = explorer_manager.docker_client.containers.get(f"tigerex-explorer-{explorer_id}")
                container.stop()
                container.remove()
            except docker.errors.NotFound:
                pass
        
        elif explorer_config.deployment_type == DeploymentType.KUBERNETES:
            # Delete Kubernetes resources
            namespace = f"tigerex-explorer-{explorer_id}"
            v1 = client.CoreV1Api(explorer_manager.k8s_client)
            apps_v1 = client.AppsV1Api(explorer_manager.k8s_client)
            networking_v1 = client.NetworkingV1Api(explorer_manager.k8s_client)
            
            try:
                # Delete ingress
                networking_v1.delete_namespaced_ingress(
                    name=f"explorer-{explorer_id}-ingress",
                    namespace=namespace
                )
                
                # Delete service
                v1.delete_namespaced_service(
                    name=f"explorer-{explorer_id}",
                    namespace=namespace
                )
                
                # Delete deployment
                apps_v1.delete_namespaced_deployment(
                    name=f"explorer-{explorer_id}",
                    namespace=namespace
                )
                
                # Delete namespace
                v1.delete_namespace(name=namespace)
                
            except client.exceptions.ApiException:
                pass
        
        # Update status to deleted
        explorer_config.status = ExplorerStatus.DELETED
        explorer_config.updated_at = datetime.now()
        await explorer_manager.save_explorer_config(explorer_config)
        
        return {"message": "Explorer deleted successfully"}
        
    except Exception as e:
        logger.error("Error deleting explorer", explorer_id=explorer_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to delete explorer: {str(e)}")

@app.post("/explorers/{explorer_id}/start")
async def start_explorer(explorer_id: str):
    """Start stopped block explorer"""
    explorer_config = await explorer_manager.get_explorer_config(explorer_id)
    
    if not explorer_config:
        raise HTTPException(status_code=404, detail="Explorer not found")
    
    if explorer_config.status != ExplorerStatus.STOPPED:
        raise HTTPException(status_code=400, detail="Explorer is not stopped")
    
    # Start deployment
    asyncio.create_task(explorer_manager.deploy_explorer(explorer_config))
    
    return {"message": "Explorer start initiated"}

@app.post("/explorers/{explorer_id}/stop")
async def stop_explorer(explorer_id: str):
    """Stop running block explorer"""
    explorer_config = await explorer_manager.get_explorer_config(explorer_id)
    
    if not explorer_config:
        raise HTTPException(status_code=404, detail="Explorer not found")
    
    if explorer_config.status != ExplorerStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Explorer is not running")
    
    try:
        # Stop deployment
        if explorer_config.deployment_type == DeploymentType.DOCKER:
            container = explorer_manager.docker_client.containers.get(f"tigerex-explorer-{explorer_id}")
            container.stop()
        
        elif explorer_config.deployment_type == DeploymentType.KUBERNETES:
            # Scale deployment to 0
            apps_v1 = client.AppsV1Api(explorer_manager.k8s_client)
            apps_v1.patch_namespaced_deployment_scale(
                name=f"explorer-{explorer_id}",
                namespace=f"tigerex-explorer-{explorer_id}",
                body=client.V1Scale(spec=client.V1ScaleSpec(replicas=0))
            )
        
        # Update status
        explorer_config.status = ExplorerStatus.STOPPED
        explorer_config.updated_at = datetime.now()
        await explorer_manager.save_explorer_config(explorer_config)
        
        return {"message": "Explorer stopped successfully"}
        
    except Exception as e:
        logger.error("Error stopping explorer", explorer_id=explorer_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to stop explorer: {str(e)}")

@app.get("/explorers/{explorer_id}/logs")
async def get_explorer_logs(explorer_id: str, lines: int = 100):
    """Get block explorer logs"""
    explorer_config = await explorer_manager.get_explorer_config(explorer_id)
    
    if not explorer_config:
        raise HTTPException(status_code=404, detail="Explorer not found")
    
    try:
        logs = []
        
        if explorer_config.deployment_type == DeploymentType.DOCKER:
            container = explorer_manager.docker_client.containers.get(f"tigerex-explorer-{explorer_id}")
            logs = container.logs(tail=lines).decode('utf-8').split('\n')
        
        elif explorer_config.deployment_type == DeploymentType.KUBERNETES:
            v1 = client.CoreV1Api(explorer_manager.k8s_client)
            namespace = f"tigerex-explorer-{explorer_id}"
            
            # Get pod name
            pods = v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=f"app=explorer-{explorer_id}"
            )
            
            if pods.items:
                pod_name = pods.items[0].metadata.name
                log_response = v1.read_namespaced_pod_log(
                    name=pod_name,
                    namespace=namespace,
                    tail_lines=lines
                )
                logs = log_response.split('\n')
        
        return {"logs": logs}
        
    except Exception as e:
        logger.error("Error getting explorer logs", explorer_id=explorer_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")

@app.get("/templates")
async def list_templates():
    """List available block explorer templates"""
    return {
        "templates": [
            {
                "id": "evm-standard",
                "name": "Standard EVM Explorer",
                "description": "Standard block explorer for EVM-compatible blockchains",
                "blockchain_types": ["evm"],
                "features": ["blocks", "transactions", "addresses", "tokens", "contracts"]
            },
            {
                "id": "solana-standard",
                "name": "Standard Solana Explorer",
                "description": "Standard block explorer for Solana blockchain",
                "blockchain_types": ["solana"],
                "features": ["blocks", "transactions", "addresses", "programs", "tokens"]
            },
            {
                "id": "bitcoin-standard",
                "name": "Standard Bitcoin Explorer",
                "description": "Standard block explorer for Bitcoin blockchain",
                "blockchain_types": ["bitcoin"],
                "features": ["blocks", "transactions", "addresses", "utxos"]
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8018)