"""
Institutional Features Service
TigerEx v11.0.0 - Enterprise-Grade Institutional Trading Platform
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import asyncio
import uvicorn
import httpx
from datetime import datetime, timedelta
import json
import logging
import hashlib
import uuid
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Institutional Features Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Enums
class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    ICEBERG = "iceberg"
    TWAP = "twap"
    VWAP = "vwap"
    POV = "pov"  # Percentage of Volume
    IMPLEMENTATION_SHORTFALL = "implementation_shortfall"

class ExecutionAlgo(str, Enum):
    SIMPLE = "simple"
    ICEBERG = "iceberg"
    TWAP = "twap"
    VWAP = "vwap"
    POV = "pov"
    ADAPTIVE = "adaptive"
    DARK_POOL = "dark_pool"

class ClientType(str, Enum):
    HEDGE_FUND = "hedge_fund"
    PROPRIETARY_TRADING = "proprietary_trading"
    ASSET_MANAGER = "asset_manager"
    PENSION_FUND = "pension_fund"
    ENDOWMENT = "endowment"
    FAMILY_OFFICE = "family_office"
    CORPORATE_TREASURY = "corporate_treasury"
    INSURANCE_COMPANY = "insurance_company"

class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    VIOLATION = "violation"
    WARNING = "warning"
    REVIEW_REQUIRED = "review_required"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Data Models
@dataclass
class InstitutionalClient:
    client_id: str
    client_name: str
    client_type: ClientType
    assets_under_management: Decimal
    registration_number: str
    compliance_officer: str
    trading_desk: str
    created_at: datetime
    status: str
    tier: str
    contact_info: Dict[str, str]
    regulatory_approvals: List[str]

class BlockOrderRequest(BaseModel):
    client_id: str
    symbol: str
    side: str = Field(..., regex="^(buy|sell)$")
    total_quantity: int = Field(..., gt=0)
    order_type: OrderType = OrderType.LIMIT
    price: Optional[float] = None
    execution_algorithm: ExecutionAlgo = ExecutionAlgo.SIMPLE
    time_limit: Optional[str] = None
    max_participation_rate: Optional[float] = Field(None, ge=0, le=100)
    discretion_range: Optional[float] = Field(None, ge=0, le=100)
    min_fill_size: Optional[int] = None
    max_fill_size: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    compliance_notes: Optional[str] = None

class AlgorithmParameters(BaseModel):
    algorithm_type: ExecutionAlgo
    participation_rate: Optional[float] = Field(None, ge=0, le=100)
    time_horizon: Optional[int] = None  # minutes
    price_tolerance: Optional[float] = Field(None, ge=0, le=100)
    volume_profile: Optional[str] = None
    aggressiveness: Optional[float] = Field(None, ge=0, le=100)
    dark_pool_ratio: Optional[float] = Field(None, ge=0, le=100)
    custom_parameters: Optional[Dict[str, Any]] = {}

class ComplianceRule(BaseModel):
    rule_id: str
    rule_name: str
    description: str
    rule_type: str
    parameters: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime

class RiskMetrics(BaseModel):
    var_1d: float
    var_5d: float
    var_30d: float
    expected_shortfall: float
    beta: float
    correlation_risk: float
    concentration_risk: float
    liquidity_risk: float
    volatility_risk: float
    leverage_ratio: float
    market_exposure: float

class MarketDataRequest(BaseModel):
    symbols: List[str]
    data_type: str = Field(..., regex="^(quote|depth|trades|historical)$")
    fields: List[str]
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    granularity: Optional[str] = None

class PrimeBrokerageRequest(BaseModel):
    client_id: str
    account_type: str = Field(..., regex="^(margin|cash|portfolio)$")
    leverage_requested: Optional[float] = Field(None, ge=1, le=10)
    collateral_type: str
    financing_rate_request: Optional[str] = None
    short_sell_request: bool = False
    securities_lending_request: bool = False

# Service Classes
class InstitutionalClientService:
    """Manage institutional client relationships"""
    
    def __init__(self):
        self.clients = {}
        self.client_approvals = {}
        self.onboarding_queue = {}
    
    async def register_client(self, client_data: Dict[str, Any]) -> InstitutionalClient:
        """Register new institutional client"""
        try:
            client_id = str(uuid.uuid4())
            
            # Validate client data
            required_fields = ['client_name', 'client_type', 'registration_number', 'compliance_officer']
            for field in required_fields:
                if field not in client_data:
                    raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
            
            # Determine client tier based on AUM
            aum = Decimal(str(client_data.get('assets_under_management', 0)))
            tier = self._determine_client_tier(aum, client_data['client_type'])
            
            client = InstitutionalClient(
                client_id=client_id,
                client_name=client_data['client_name'],
                client_type=ClientType(client_data['client_type']),
                assets_under_management=aum,
                registration_number=client_data['registration_number'],
                compliance_officer=client_data['compliance_officer'],
                trading_desk=client_data.get('trading_desk', 'default'),
                created_at=datetime.utcnow(),
                status='pending_approval',
                tier=tier,
                contact_info=client_data.get('contact_info', {}),
                regulatory_approvals=client_data.get('regulatory_approvals', [])
            )
            
            self.clients[client_id] = client
            self.onboarding_queue[client_id] = {
                'status': 'pending_compliance_review',
                'submitted_at': datetime.utcnow(),
                'reviewer_assigned': None
            }
            
            logger.info(f"Registered institutional client: {client_id}")
            return client
            
        except Exception as e:
            logger.error(f"Error registering client: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def approve_client(self, client_id: str, approver_id: str, approval_notes: str) -> bool:
        """Approve institutional client"""
        try:
            if client_id not in self.clients:
                raise HTTPException(status_code=404, detail="Client not found")
            
            client = self.clients[client_id]
            client.status = 'active'
            
            self.client_approvals[client_id] = {
                'approved_by': approver_id,
                'approved_at': datetime.utcnow(),
                'notes': approval_notes
            }
            
            if client_id in self.onboarding_queue:
                del self.onboarding_queue[client_id]
            
            logger.info(f"Approved client: {client_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error approving client: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_client(self, client_id: str) -> InstitutionalClient:
        """Get client details"""
        if client_id not in self.clients:
            raise HTTPException(status_code=404, detail="Client not found")
        return self.clients[client_id]
    
    async def list_clients(self, client_type: Optional[ClientType] = None,
                          status: Optional[str] = None) -> List[InstitutionalClient]:
        """List clients with filters"""
        clients = list(self.clients.values())
        
        if client_type:
            clients = [c for c in clients if c.client_type == client_type]
        if status:
            clients = [c for c in clients if c.status == status]
        
        return clients
    
    def _determine_client_tier(self, aum: Decimal, client_type: ClientType) -> str:
        """Determine client tier based on AUM and type"""
        if aum >= Decimal('1000000000'):  # $1B+
            return 'platinum'
        elif aum >= Decimal('100000000'):  # $100M+
            return 'gold'
        elif aum >= Decimal('10000000'):  # $10M+
            return 'silver'
        else:
            return 'bronze'

class BlockOrderExecutionService:
    """Execute large block orders with sophisticated algorithms"""
    
    def __init__(self):
        self.active_orders = {}
        self.execution_queue = asyncio.Queue()
        self.market_data_cache = {}
    
    async def submit_block_order(self, request: BlockOrderRequest) -> Dict[str, Any]:
        """Submit block order for execution"""
        try:
            # Validate client
            if request.client_id not in client_service.clients:
                raise HTTPException(status_code=404, detail="Client not found")
            
            # Generate order ID
            order_id = str(uuid.uuid4())
            
            # Create order object
            order = {
                'order_id': order_id,
                'client_id': request.client_id,
                'symbol': request.symbol,
                'side': request.side,
                'total_quantity': request.total_quantity,
                'filled_quantity': 0,
                'remaining_quantity': request.total_quantity,
                'order_type': request.order_type,
                'price': request.price,
                'status': 'pending',
                'execution_algorithm': request.execution_algorithm,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'child_orders': [],
                'execution_parameters': {
                    'max_participation_rate': request.max_participation_rate,
                    'discretion_range': request.discretion_range,
                    'min_fill_size': request.min_fill_size,
                    'max_fill_size': request.max_fill_size,
                    'start_time': request.start_time,
                    'end_time': request.end_time
                }
            }
            
            self.active_orders[order_id] = order
            
            # Submit to execution queue
            await self.execution_queue.put(order_id)
            
            # Start execution if not already running
            asyncio.create_task(self._process_execution_queue())
            
            logger.info(f"Submitted block order: {order_id}")
            
            return {
                'order_id': order_id,
                'status': 'submitted',
                'estimated_completion': self._estimate_completion_time(request),
                'algorithm': request.execution_algorithm
            }
            
        except Exception as e:
            logger.error(f"Error submitting block order: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get block order execution status"""
        if order_id not in self.active_orders:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order = self.active_orders[order_id]
        
        return {
            'order_id': order_id,
            'status': order['status'],
            'total_quantity': order['total_quantity'],
            'filled_quantity': order['filled_quantity'],
            'remaining_quantity': order['remaining_quantity'],
            'average_fill_price': self._calculate_average_fill_price(order),
            'execution_quality': self._calculate_execution_quality(order),
            'created_at': order['created_at'].isoformat(),
            'updated_at': order['updated_at'].isoformat(),
            'child_orders_count': len(order['child_orders'])
        }
    
    async def cancel_block_order(self, order_id: str, reason: str) -> bool:
        """Cancel block order"""
        if order_id not in self.active_orders:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order = self.active_orders[order_id]
        order['status'] = 'cancelled'
        order['cancel_reason'] = reason
        order['updated_at'] = datetime.utcnow()
        
        logger.info(f"Cancelled block order: {order_id}")
        return True
    
    async def _process_execution_queue(self):
        """Process block order execution queue"""
        while True:
            try:
                order_id = await self.execution_queue.get()
                if order_id in self.active_orders:
                    await self._execute_block_order(order_id)
            except Exception as e:
                logger.error(f"Error processing execution queue: {str(e)}")
    
    async def _execute_block_order(self, order_id: str):
        """Execute block order using selected algorithm"""
        order = self.active_orders[order_id]
        
        try:
            order['status'] = 'executing'
            order['updated_at'] = datetime.utcnow()
            
            # Execute based on algorithm
            if order['execution_algorithm'] == ExecutionAlgo.TWAP:
                await self._execute_twap(order)
            elif order['execution_algorithm'] == ExecutionAlgo.VWAP:
                await self._execute_vwap(order)
            elif order['execution_algorithm'] == ExecutionAlgo.ICEBERG:
                await self._execute_iceberg(order)
            else:
                await self._execute_simple(order)
            
            order['status'] = 'completed' if order['remaining_quantity'] == 0 else 'partially_filled'
            order['updated_at'] = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error executing order {order_id}: {str(e)}")
            order['status'] = 'failed'
            order['error'] = str(e)
            order['updated_at'] = datetime.utcnow()
    
    async def _execute_twap(self, order: Dict[str, Any]):
        """Execute order using Time-Weighted Average Price algorithm"""
        # Simplified TWAP implementation
        total_quantity = order['remaining_quantity']
        time_slices = 10  # Divide into 10 time slices
        
        slice_size = total_quantity // time_slices
        remaining = total_quantity % time_slices
        
        for i in range(time_slices):
            if order['remaining_quantity'] <= 0:
                break
            
            current_slice = slice_size + (1 if i < remaining else 0)
            await self._execute_slice(order, current_slice)
            await asyncio.sleep(1)  # Wait between slices
    
    async def _execute_vwap(self, order: Dict[str, Any]):
        """Execute order using Volume-Weighted Average Price algorithm"""
        # Simplified VWAP implementation
        # In reality, would track market volume and adjust participation
        total_quantity = order['remaining_quantity']
        volume_slices = 5
        
        for i in range(volume_slices):
            if order['remaining_quantity'] <= 0:
                break
            
            slice_size = total_quantity // volume_slices
            await self._execute_slice(order, slice_size)
            await asyncio.sleep(2)
    
    async def _execute_iceberg(self, order: Dict[str, Any]):
        """Execute order using Iceberg algorithm"""
        # Hide actual size, show small slices
        display_quantity = min(1000, order['total_quantity'] // 10)
        
        while order['remaining_quantity'] > 0:
            slice_size = min(display_quantity, order['remaining_quantity'])
            await self._execute_slice(order, slice_size)
            await asyncio.sleep(0.5)
    
    async def _execute_simple(self, order: Dict[str, Any]):
        """Simple market execution"""
        await self._execute_slice(order, order['remaining_quantity'])
    
    async def _execute_slice(self, order: Dict[str, Any], quantity: int):
        """Execute a slice of the order"""
        # Mock execution
        fill_price = 100.0 + (hash(order['order_id']) % 1000) / 100
        
        child_order = {
            'child_order_id': str(uuid.uuid4()),
            'quantity': quantity,
            'fill_price': fill_price,
            'executed_at': datetime.utcnow()
        }
        
        order['child_orders'].append(child_order)
        order['filled_quantity'] += quantity
        order['remaining_quantity'] -= quantity
        order['updated_at'] = datetime.utcnow()
    
    def _calculate_average_fill_price(self, order: Dict[str, Any]) -> float:
        """Calculate average fill price"""
        if not order['child_orders']:
            return 0.0
        
        total_value = sum(child['quantity'] * child['fill_price'] for child in order['child_orders'])
        total_quantity = sum(child['quantity'] for child in order['child_orders'])
        
        return total_value / total_quantity if total_quantity > 0 else 0.0
    
    def _calculate_execution_quality(self, order: Dict[str, Any]) -> Dict[str, float]:
        """Calculate execution quality metrics"""
        # Mock quality metrics
        return {
            'slippage_bps': 5.2,
            'participation_rate': 2.3,
            'time_to_complete': 45.5,
            'fill_ratio': order['filled_quantity'] / order['total_quantity']
        }
    
    def _estimate_completion_time(self, request: BlockOrderRequest) -> str:
        """Estimate order completion time"""
        # Simplified estimation
        base_time = 30  # minutes
        complexity_multiplier = {
            ExecutionAlgo.SIMPLE: 1.0,
            ExecutionAlgo.TWAP: 1.5,
            ExecutionAlgo.VWAP: 1.8,
            ExecutionAlgo.ICEBERG: 2.0,
            ExecutionAlgo.ADAPTIVE: 2.5
        }
        
        multiplier = complexity_multiplier.get(request.execution_algorithm, 1.0)
        estimated_minutes = int(base_time * multiplier)
        
        return (datetime.utcnow() + timedelta(minutes=estimated_minutes)).isoformat()

class ComplianceMonitoringService:
    """Monitor institutional trading for compliance"""
    
    def __init__(self):
        self.compliance_rules = {}
        self.violations = {}
        self.monitoring_active = True
    
    async def add_compliance_rule(self, rule: ComplianceRule) -> bool:
        """Add new compliance rule"""
        self.compliance_rules[rule.rule_id] = rule
        logger.info(f"Added compliance rule: {rule.rule_id}")
        return True
    
    async def check_trade_compliance(self, trade_data: Dict[str, Any]) -> ComplianceStatus:
        """Check if trade complies with all rules"""
        violations = []
        
        for rule_id, rule in self.compliance_rules.items():
            if rule.is_active:
                violation = await self._check_rule(rule, trade_data)
                if violation:
                    violations.append(violation)
        
        if violations:
            # Record violations
            trade_id = trade_data.get('trade_id', 'unknown')
            self.violations[trade_id] = {
                'trade_id': trade_id,
                'violations': violations,
                'detected_at': datetime.utcnow()
            }
            return ComplianceStatus.VIOLATION
        
        return ComplianceStatus.COMPLIANT
    
    async def get_violations(self, client_id: Optional[str] = None,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get compliance violations"""
        violations = []
        
        for violation_id, violation in self.violations.items():
            if client_id and violation.get('client_id') != client_id:
                continue
            if start_date and violation['detected_at'] < start_date:
                continue
            if end_date and violation['detected_at'] > end_date:
                continue
            
            violations.append(violation)
        
        return violations
    
    async def _check_rule(self, rule: ComplianceRule, trade_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check specific compliance rule"""
        # Mock rule checking
        if rule.rule_type == 'position_limit':
            max_position = rule.parameters.get('max_position', 1000000)
            if trade_data.get('quantity', 0) > max_position:
                return {
                    'rule_id': rule.rule_id,
                    'rule_name': rule.rule_name,
                    'violation_type': 'position_limit_exceeded',
                    'details': f"Trade quantity {trade_data.get('quantity')} exceeds limit {max_position}"
                }
        
        elif rule.rule_type == 'concentration_limit':
            max_concentration = rule.parameters.get('max_concentration_percent', 10)
            # Would check portfolio concentration
            pass
        
        return None

class RiskManagementService:
    """Advanced risk management for institutional clients"""
    
    def __init__(self):
        self.risk_limits = {}
        self.risk_metrics = {}
        self.alerts = {}
    
    async def set_risk_limits(self, client_id: str, limits: Dict[str, Any]) -> bool:
        """Set risk limits for client"""
        self.risk_limits[client_id] = {
            'var_limit': limits.get('var_limit', 1000000),
            'concentration_limit': limits.get('concentration_limit', 0.2),
            'leverage_limit': limits.get('leverage_limit', 3.0),
            'sector_exposure_limit': limits.get('sector_exposure_limit', 0.3),
            'updated_at': datetime.utcnow()
        }
        return True
    
    async def calculate_portfolio_risk(self, portfolio_data: Dict[str, Any]) -> RiskMetrics:
        """Calculate comprehensive risk metrics"""
        try:
            holdings = portfolio_data.get('holdings', [])
            
            # Calculate VaR at different confidence levels
            var_1d = self._calculate_var(holdings, confidence=0.95, time_horizon=1)
            var_5d = self._calculate_var(holdings, confidence=0.95, time_horizon=5)
            var_30d = self._calculate_var(holdings, confidence=0.99, time_horizon=30)
            
            # Calculate other risk metrics
            expected_shortfall = var_30d * 1.2  # Simplified
            beta = 1.1  # Would calculate against market
            correlation_risk = 0.65  # Portfolio correlation
            concentration_risk = self._calculate_concentration_risk(holdings)
            liquidity_risk = 0.3  # Would calculate based on asset liquidity
            volatility_risk = self._calculate_volatility_risk(holdings)
            leverage_ratio = self._calculate_leverage_ratio(portfolio_data)
            market_exposure = sum(h.get('market_value', 0) for h in holdings)
            
            return RiskMetrics(
                var_1d=var_1d,
                var_5d=var_5d,
                var_30d=var_30d,
                expected_shortfall=expected_shortfall,
                beta=beta,
                correlation_risk=correlation_risk,
                concentration_risk=concentration_risk,
                liquidity_risk=liquidity_risk,
                volatility_risk=volatility_risk,
                leverage_ratio=leverage_ratio,
                market_exposure=market_exposure
            )
            
        except Exception as e:
            logger.error(f"Error calculating portfolio risk: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def check_risk_limits(self, client_id: str, risk_metrics: RiskMetrics) -> Dict[str, bool]:
        """Check if portfolio exceeds risk limits"""
        if client_id not in self.risk_limits:
            return {'limits_set': False}
        
        limits = self.risk_limits[client_id]
        
        limit_checks = {
            'var_exceeded': risk_metrics.var_1d > limits['var_limit'],
            'concentration_exceeded': risk_metrics.concentration_risk > limits['concentration_limit'],
            'leverage_exceeded': risk_metrics.leverage_ratio > limits['leverage_limit'],
            'limits_set': True
        }
        
        # Generate alerts if limits exceeded
        if any(limit_checks.values()):
            await self._generate_risk_alert(client_id, limit_checks, risk_metrics)
        
        return limit_checks
    
    async def _generate_risk_alert(self, client_id: str, limit_checks: Dict[str, bool], 
                                 risk_metrics: RiskMetrics):
        """Generate risk alert"""
        alert_id = str(uuid.uuid4())
        self.alerts[alert_id] = {
            'alert_id': alert_id,
            'client_id': client_id,
            'limit_checks': limit_checks,
            'risk_metrics': risk_metrics.__dict__,
            'created_at': datetime.utcnow(),
            'severity': 'high' if any(limit_checks.values()) else 'medium'
        }
    
    def _calculate_var(self, holdings: List[Dict], confidence: float, time_horizon: int) -> float:
        """Calculate Value at Risk"""
        # Simplified VaR calculation
        total_value = sum(h.get('market_value', 0) for h in holdings)
        volatility = 0.02  # Would calculate from historical data
        
        var = total_value * volatility * (time_horizon ** 0.5) * 1.65  # 95% confidence
        return var
    
    def _calculate_concentration_risk(self, holdings: List[Dict]) -> float:
        """Calculate concentration risk (Herfindahl-Hirschman Index)"""
        total_value = sum(h.get('market_value', 0) for h in holdings)
        if total_value == 0:
            return 0
        
        hhi = sum((h.get('market_value', 0) / total_value) ** 2 for h in holdings)
        return hhi
    
    def _calculate_volatility_risk(self, holdings: List[Dict]) -> float:
        """Calculate volatility risk"""
        # Simplified - would use historical volatility
        return 0.18  # 18% annualized volatility
    
    def _calculate_leverage_ratio(self, portfolio_data: Dict[str, Any]) -> float:
        """Calculate leverage ratio"""
        total_assets = portfolio_data.get('total_assets', 0)
        total_equity = portfolio_data.get('total_equity', total_assets)
        
        return total_assets / total_equity if total_equity > 0 else 1.0

class PrimeBrokerageService:
    """Prime brokerage services for institutional clients"""
    
    def __init__(self):
        self.margin_accounts = {}
        self.securities_lending = {}
        self.financing_rates = {}
    
    async def open_margin_account(self, request: PrimeBrokerageRequest) -> Dict[str, Any]:
        """Open margin account for institutional client"""
        try:
            account_id = str(uuid.uuid4())
            
            account = {
                'account_id': account_id,
                'client_id': request.client_id,
                'account_type': request.account_type,
                'leverage_approved': request.leverage_requested or 2.0,
                'collateral_type': request.collateral_type,
                'status': 'active',
                'created_at': datetime.utcnow(),
                'margin_requirement': 0.25,  # 25% initial margin
                'maintenance_margin': 0.15,  # 15% maintenance margin
                'interest_rate': 0.05  # 5% annual rate
            }
            
            self.margin_accounts[account_id] = account
            
            logger.info(f"Opened margin account: {account_id}")
            return {
                'account_id': account_id,
                'status': 'approved',
                'leverage_approved': account['leverage_approved'],
                'interest_rate': account['interest_rate']
            }
            
        except Exception as e:
            logger.error(f"Error opening margin account: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_margin_status(self, account_id: str) -> Dict[str, Any]:
        """Get margin account status"""
        if account_id not in self.margin_accounts:
            raise HTTPException(status_code=404, detail="Account not found")
        
        account = self.margin_accounts[account_id]
        
        # Mock portfolio value and margin calculation
        portfolio_value = 1000000
        margin_used = 200000
        available_margin = portfolio_value * account['leverage_approved'] - margin_used
        
        return {
            'account_id': account_id,
            'portfolio_value': portfolio_value,
            'margin_used': margin_used,
            'available_margin': available_margin,
            'margin_call_risk': margin_used / (portfolio_value * account['maintenance_margin']),
            'interest_accrued_today': margin_used * account['interest_rate'] / 365,
            'status': account['status']
        }
    
    async def request_securities_lending(self, client_id: str, symbol: str, 
                                        quantity: int) -> Dict[str, Any]:
        """Request securities for short selling"""
        lending_id = str(uuid.uuid4())
        
        # Mock securities lending availability
        available = True
        borrow_rate = 0.02  # 2% annual borrow rate
        
        if available:
            self.securities_lending[lending_id] = {
                'lending_id': lending_id,
                'client_id': client_id,
                'symbol': symbol,
                'quantity': quantity,
                'borrow_rate': borrow_rate,
                'created_at': datetime.utcnow(),
                'status': 'active'
            }
        
        return {
            'lending_id': lending_id,
            'available': available,
            'borrow_rate': borrow_rate,
            'estimated_cost': quantity * 100 * borrow_rate / 365  # Assuming $100 stock price
        }

# Initialize services
client_service = InstitutionalClientService()
block_order_service = BlockOrderExecutionService()
compliance_service = ComplianceMonitoringService()
risk_service = RiskManagementService()
prime_brokerage_service = PrimeBrokerageService()

# API Endpoints
@app.post("/api/v1/institutional/clients")
async def register_institutional_client(client_data: Dict[str, Any],
                                       credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Register new institutional client"""
    try:
        client = await client_service.register_client(client_data)
        
        return {
            "success": True,
            "data": {
                "client_id": client.client_id,
                "client_name": client.client_name,
                "client_type": client.client_type,
                "tier": client.tier,
                "status": client.status,
                "created_at": client.created_at.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error in register client endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/institutional/block-orders")
async def submit_block_order(request: BlockOrderRequest,
                            credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Submit block order for execution"""
    try:
        result = await block_order_service.submit_block_order(request)
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error in block order endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/institutional/block-orders/{order_id}/status")
async def get_block_order_status(order_id: str,
                                credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get block order status"""
    try:
        status = await block_order_service.get_order_status(order_id)
        
        return {
            "success": True,
            "data": status
        }
        
    except Exception as e:
        logger.error(f"Error in order status endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/institutional/risk/calculate")
async def calculate_portfolio_risk(portfolio_data: Dict[str, Any],
                                 credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Calculate portfolio risk metrics"""
    try:
        risk_metrics = await risk_service.calculate_portfolio_risk(portfolio_data)
        
        return {
            "success": True,
            "data": risk_metrics.__dict__
        }
        
    except Exception as e:
        logger.error(f"Error in risk calculation endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/institutional/compliance/check")
async def check_trade_compliance(trade_data: Dict[str, Any],
                                credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Check trade compliance"""
    try:
        status = await compliance_service.check_trade_compliance(trade_data)
        
        return {
            "success": True,
            "data": {
                "compliance_status": status,
                "checked_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error in compliance check endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/institutional/prime-brokerage/accounts")
async def open_margin_account(request: PrimeBrokerageRequest,
                             credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Open margin account"""
    try:
        result = await prime_brokerage_service.open_margin_account(request)
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error in margin account endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/institutional/prime-brokerage/accounts/{account_id}/status")
async def get_margin_status(account_id: str,
                           credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get margin account status"""
    try:
        status = await prime_brokerage_service.get_margin_status(account_id)
        
        return {
            "success": True,
            "data": status
        }
        
    except Exception as e:
        logger.error(f"Error in margin status endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "institutional-features"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8011)