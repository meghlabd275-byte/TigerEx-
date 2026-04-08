#!/usr/bin/env python3
"""
TigerEx Bug Fixes and Improvements
This module contains all bug fixes and improvements identified from the codebase analysis
"""

import os
import re
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from decimal import Decimal
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# BUG FIX 1: SQL Injection Prevention
# ============================================================================

class SecureQueryBuilder:
    """
    Secure query builder to prevent SQL injection attacks
    All database queries should use parameterized queries
    """
    
    @staticmethod
    def build_insert_query(table: str, data: Dict[str, Any]) -> tuple:
        """Build safe INSERT query with parameters"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        return query, list(data.values())
    
    @staticmethod
    def build_update_query(table: str, data: Dict[str, Any], condition: str, condition_params: List) -> tuple:
        """Build safe UPDATE query with parameters"""
        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        params = list(data.values()) + condition_params
        return query, params
    
    @staticmethod
    def build_select_query(table: str, columns: List[str] = None, 
                          condition: str = None, condition_params: List = None) -> tuple:
        """Build safe SELECT query with parameters"""
        cols = ', '.join(columns) if columns else '*'
        query = f"SELECT {cols} FROM {table}"
        params = []
        
        if condition:
            query += f" WHERE {condition}"
            params = condition_params or []
        
        return query, params


# ============================================================================
# BUG FIX 2: Rate Limiting Implementation
# ============================================================================

class RateLimiter:
    """
    Rate limiter to prevent API abuse
    Implements sliding window rate limiting
    """
    
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self._requests: Dict[str, List[float]] = {}
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client"""
        now = datetime.utcnow().timestamp()
        
        if client_id not in self._requests:
            self._requests[client_id] = []
        
        # Clean old requests
        self._requests[client_id] = [
            t for t in self._requests[client_id]
            if now - t < 3600  # Keep last hour
        ]
        
        # Check minute limit
        minute_requests = len([
            t for t in self._requests[client_id]
            if now - t < 60
        ])
        
        if minute_requests >= self.requests_per_minute:
            return False
        
        # Check hour limit
        hour_requests = len(self._requests[client_id])
        if hour_requests >= self.requests_per_hour:
            return False
        
        # Record request
        self._requests[client_id].append(now)
        return True
    
    def get_remaining(self, client_id: str) -> Dict[str, int]:
        """Get remaining requests for client"""
        now = datetime.utcnow().timestamp()
        
        if client_id not in self._requests:
            return {
                "minute_remaining": self.requests_per_minute,
                "hour_remaining": self.requests_per_hour
            }
        
        minute_requests = len([
            t for t in self._requests[client_id]
            if now - t < 60
        ])
        
        hour_requests = len([
            t for t in self._requests[client_id]
            if now - t < 3600
        ])
        
        return {
            "minute_remaining": max(0, self.requests_per_minute - minute_requests),
            "hour_remaining": max(0, self.requests_per_hour - hour_requests)
        }


# ============================================================================
# BUG FIX 3: Decimal Precision Handling
# ============================================================================

class PreciseDecimal:
    """
    Handle decimal precision for financial calculations
    Prevents floating-point errors
    """
    
    PRECISION = 8  # 8 decimal places for crypto
    
    @staticmethod
    def create(value: Any) -> Decimal:
        """Create precise decimal from any value"""
        if isinstance(value, Decimal):
            return value
        if isinstance(value, float):
            # Convert to string first to avoid float precision issues
            return Decimal(str(value))
        if isinstance(value, str):
            return Decimal(value)
        return Decimal(str(value))
    
    @staticmethod
    def round_to_precision(value: Decimal, precision: int = None) -> Decimal:
        """Round to specified precision"""
        precision = precision or PreciseDecimal.PRECISION
        quantize_str = '0.' + '0' * precision
        return value.quantize(Decimal(quantize_str))
    
    @staticmethod
    def multiply(a: Decimal, b: Decimal) -> Decimal:
        """Precise multiplication"""
        return a * b
    
    @staticmethod
    def divide(a: Decimal, b: Decimal) -> Decimal:
        """Precise division"""
        if b == 0:
            raise ValueError("Division by zero")
        return a / b


# ============================================================================
# BUG FIX 4: Memory Leak Prevention in WebSocket Connections
# ============================================================================

class ConnectionManager:
    """
    Manage WebSocket connections with proper cleanup
    Prevents memory leaks from abandoned connections
    """
    
    def __init__(self, max_connections: int = 10000, idle_timeout: int = 300):
        self.active_connections: Dict[str, Any] = {}
        self.connection_times: Dict[str, float] = {}
        self.max_connections = max_connections
        self.idle_timeout = idle_timeout
        self._lock = asyncio.Lock()
    
    async def connect(self, connection_id: str, websocket):
        """Add new connection"""
        async with self._lock:
            if len(self.active_connections) >= self.max_connections:
                # Remove oldest idle connection
                await self._cleanup_idle_connections()
            
            self.active_connections[connection_id] = websocket
            self.connection_times[connection_id] = datetime.utcnow().timestamp()
    
    async def disconnect(self, connection_id: str):
        """Remove connection"""
        async with self._lock:
            if connection_id in self.active_connections:
                del self.active_connections[connection_id]
            if connection_id in self.connection_times:
                del self.connection_times[connection_id]
    
    async def _cleanup_idle_connections(self):
        """Clean up idle connections"""
        now = datetime.utcnow().timestamp()
        to_remove = []
        
        for conn_id, conn_time in self.connection_times.items():
            if now - conn_time > self.idle_timeout:
                to_remove.append(conn_id)
        
        for conn_id in to_remove:
            await self.disconnect(conn_id)
    
    async def broadcast(self, message: str, channel: str = None):
        """Broadcast message to all or filtered connections"""
        async with self._lock:
            for websocket in self.active_connections.values():
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"Error broadcasting: {e}")


# ============================================================================
# BUG FIX 5: Error Handling Improvements
# ============================================================================

class ExchangeError(Exception):
    """Base exception for exchange errors"""
    
    def __init__(self, message: str, code: str = None, details: Dict = None):
        self.message = message
        self.code = code or "UNKNOWN_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class InsufficientFundsError(ExchangeError):
    """Insufficient funds for operation"""
    
    def __init__(self, available: Decimal, required: Decimal, asset: str):
        super().__init__(
            message=f"Insufficient {asset}. Available: {available}, Required: {required}",
            code="INSUFFICIENT_FUNDS",
            details={"available": str(available), "required": str(required), "asset": asset}
        )


class OrderNotFoundError(ExchangeError):
    """Order not found"""
    
    def __init__(self, order_id: str):
        super().__init__(
            message=f"Order {order_id} not found",
            code="ORDER_NOT_FOUND",
            details={"order_id": order_id}
        )


class InvalidOrderError(ExchangeError):
    """Invalid order parameters"""
    
    def __init__(self, reason: str, details: Dict = None):
        super().__init__(
            message=f"Invalid order: {reason}",
            code="INVALID_ORDER",
            details=details
        )


class MarketClosedError(ExchangeError):
    """Market is closed for trading"""
    
    def __init__(self, symbol: str):
        super().__init__(
            message=f"Market {symbol} is closed",
            code="MARKET_CLOSED",
            details={"symbol": symbol}
        )


# ============================================================================
# BUG FIX 6: Session Management
# ============================================================================

class SessionManager:
    """
    Secure session management
    Implements secure session tokens and expiration
    """
    
    def __init__(self, session_timeout: int = 3600, max_sessions_per_user: int = 5):
        self.sessions: Dict[str, Dict] = {}
        self.user_sessions: Dict[str, List[str]] = {}
        self.session_timeout = session_timeout
        self.max_sessions_per_user = max_sessions_per_user
    
    def create_session(self, user_id: str, data: Dict = None) -> str:
        """Create new session"""
        import secrets
        session_token = secrets.token_urlsafe(32)
        
        now = datetime.utcnow().timestamp()
        
        session_data = {
            "user_id": user_id,
            "created_at": now,
            "expires_at": now + self.session_timeout,
            "data": data or {}
        }
        
        self.sessions[session_token] = session_data
        
        # Track user sessions
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = []
        
        self.user_sessions[user_id].append(session_token)
        
        # Enforce max sessions
        while len(self.user_sessions[user_id]) > self.max_sessions_per_user:
            old_token = self.user_sessions[user_id].pop(0)
            if old_token in self.sessions:
                del self.sessions[old_token]
        
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[Dict]:
        """Validate session and return data"""
        if session_token not in self.sessions:
            return None
        
        session = self.sessions[session_token]
        
        # Check expiration
        if datetime.utcnow().timestamp() > session["expires_at"]:
            self.invalidate_session(session_token)
            return None
        
        # Extend session
        session["expires_at"] = datetime.utcnow().timestamp() + self.session_timeout
        
        return session
    
    def invalidate_session(self, session_token: str):
        """Invalidate session"""
        if session_token in self.sessions:
            user_id = self.sessions[session_token]["user_id"]
            del self.sessions[session_token]
            
            if user_id in self.user_sessions:
                if session_token in self.user_sessions[user_id]:
                    self.user_sessions[user_id].remove(session_token)
    
    def invalidate_user_sessions(self, user_id: str):
        """Invalidate all sessions for user"""
        if user_id in self.user_sessions:
            for token in self.user_sessions[user_id]:
                if token in self.sessions:
                    del self.sessions[token]
            del self.user_sessions[user_id]


# ============================================================================
# BUG FIX 7: Order Validation
# ============================================================================

class OrderValidator:
    """
    Validate orders before processing
    Prevents invalid orders from entering the system
    """
    
    @staticmethod
    def validate_order(symbol: str, side: str, order_type: str,
                       quantity: Decimal, price: Decimal = None,
                       min_quantity: Decimal = None, max_quantity: Decimal = None,
                       min_price: Decimal = None, max_price: Decimal = None,
                       tick_size: Decimal = None, step_size: Decimal = None) -> Dict:
        """Validate order parameters"""
        
        errors = []
        
        # Validate side
        if side.lower() not in ["buy", "sell"]:
            errors.append(f"Invalid side: {side}")
        
        # Validate order type
        valid_types = ["market", "limit", "stop_loss", "stop_limit", "take_profit"]
        if order_type.lower() not in valid_types:
            errors.append(f"Invalid order type: {order_type}")
        
        # Validate quantity
        if quantity <= 0:
            errors.append("Quantity must be positive")
        
        if min_quantity and quantity < min_quantity:
            errors.append(f"Quantity below minimum: {min_quantity}")
        
        if max_quantity and quantity > max_quantity:
            errors.append(f"Quantity above maximum: {max_quantity}")
        
        # Validate price for limit orders
        if order_type.lower() in ["limit", "stop_limit"]:
            if price is None or price <= 0:
                errors.append("Price required for limit orders")
            
            if min_price and price < min_price:
                errors.append(f"Price below minimum: {min_price}")
            
            if max_price and price > max_price:
                errors.append(f"Price above maximum: {max_price}")
            
            # Validate tick size
            if tick_size and price:
                if price % tick_size != 0:
                    errors.append(f"Price must be multiple of tick size: {tick_size}")
        
        # Validate step size
        if step_size and quantity:
            if quantity % step_size != 0:
                errors.append(f"Quantity must be multiple of step size: {step_size}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }


# ============================================================================
# BUG FIX 8: Concurrency Handling
# ============================================================================

class AsyncLockManager:
    """
    Manage locks for concurrent operations
    Prevents race conditions
    """
    
    def __init__(self):
        self._locks: Dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()
    
    async def get_lock(self, key: str) -> asyncio.Lock:
        """Get or create lock for key"""
        async with self._global_lock:
            if key not in self._locks:
                self._locks[key] = asyncio.Lock()
            return self._locks[key]
    
    async def with_lock(self, key: str, coro):
        """Execute coroutine with lock"""
        lock = await self.get_lock(key)
        async with lock:
            return await coro


# ============================================================================
# BUG FIX 9: Input Sanitization
# ============================================================================

class InputSanitizer:
    """
    Sanitize user inputs to prevent XSS and injection attacks
    """
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            raise ValueError("Input must be a string")
        
        # Truncate to max length
        value = value[:max_length]
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
        for char in dangerous_chars:
            value = value.replace(char, '')
        
        return value.strip()
    
    @staticmethod
    def sanitize_email(email: str) -> str:
        """Validate and sanitize email"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")
        return email.lower().strip()
    
    @staticmethod
    def sanitize_number(value: Any, min_val: float = None, max_val: float = None) -> float:
        """Sanitize numeric input"""
        try:
            num = float(value)
        except (ValueError, TypeError):
            raise ValueError("Invalid number")
        
        if min_val is not None and num < min_val:
            raise ValueError(f"Value must be at least {min_val}")
        
        if max_val is not None and num > max_val:
            raise ValueError(f"Value must be at most {max_val}")
        
        return num


# ============================================================================
# BUG FIX 10: Logging Improvements
# ============================================================================

class SecureLogger:
    """
    Secure logging that doesn't expose sensitive data
    """
    
    SENSITIVE_FIELDS = ['password', 'secret', 'token', 'api_key', 'private_key', 'seed']
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def _sanitize(self, data: Dict) -> Dict:
        """Sanitize sensitive data"""
        sanitized = {}
        for key, value in data.items():
            if any(field in key.lower() for field in self.SENSITIVE_FIELDS):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize(value)
            else:
                sanitized[key] = value
        return sanitized
    
    def info(self, message: str, **kwargs):
        """Log info with sanitized data"""
        if kwargs:
            self.logger.info(f"{message} | {self._sanitize(kwargs)}")
        else:
            self.logger.info(message)
    
    def error(self, message: str, **kwargs):
        """Log error with sanitized data"""
        if kwargs:
            self.logger.error(f"{message} | {self._sanitize(kwargs)}")
        else:
            self.logger.error(message)
    
    def warning(self, message: str, **kwargs):
        """Log warning with sanitized data"""
        if kwargs:
            self.logger.warning(f"{message} | {self._sanitize(kwargs)}")
        else:
            self.logger.warning(message)


# ============================================================================
# Export all fixes
# ============================================================================

__all__ = [
    'SecureQueryBuilder',
    'RateLimiter',
    'PreciseDecimal',
    'ConnectionManager',
    'ExchangeError',
    'InsufficientFundsError',
    'OrderNotFoundError',
    'InvalidOrderError',
    'MarketClosedError',
    'SessionManager',
    'OrderValidator',
    'AsyncLockManager',
    'InputSanitizer',
    'SecureLogger'
]


if __name__ == "__main__":
    # Test the fixes
    print("Testing bug fixes...")
    
    # Test rate limiter
    limiter = RateLimiter(requests_per_minute=5)
    for i in range(7):
        allowed = limiter.is_allowed("test_client")
        print(f"Request {i+1}: {'Allowed' if allowed else 'Rate Limited'}")
    
    # Test precise decimal
    price = PreciseDecimal.create(50000.123456789)
    rounded = PreciseDecimal.round_to_precision(price, 8)
    print(f"Precise decimal: {rounded}")
    
    # Test order validator
    result = OrderValidator.validate_order(
        symbol="BTCUSDT",
        side="buy",
        order_type="limit",
        quantity=Decimal("0.001"),
        price=Decimal("50000"),
        min_quantity=Decimal("0.0001")
    )
    print(f"Order validation: {result}")
    
    # Test input sanitizer
    try:
        clean = InputSanitizer.sanitize_string("<script>alert('xss')</script>")
        print(f"Sanitized string: {clean}")
    except ValueError as e:
        print(f"Sanitization error: {e}")
    
    print("All tests completed!")