"""
Advanced MCP Client Implementation
Enhanced MCP client with connection pooling, load balancing, retry logic, and monitoring
"""
import asyncio
import hashlib
import json
import logging
import time
import random
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any, List, Callable, Union
from datetime import datetime, timedelta
import httpx
from pydantic import ValidationError

from app.models.mcp_server import (
    MCPServer, MCPOperationLog, MCPServerMetric, 
    MCPCacheEntry, MCPServerGroup, MCPServerGroupMember
)
from app.schemas.mcp_server import (
    MCPServerConfig, MCPFileOperation, MCPDatabaseQuery, 
    MCPWebScrapingTask, MCPApiRequest, AuthType, HealthStatus,
    LogStatus, OperationType
)
from app.core.database import get_db


logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class RateLimiter:
    """Rate limiter implementation"""
    calls: deque = field(default_factory=lambda: deque())
    max_calls: int = 100
    time_window: int = 60  # seconds
    
    def is_allowed(self) -> bool:
        """Check if call is allowed under rate limit"""
        now = time.time()
        
        # Remove old calls outside time window
        while self.calls and self.calls[0] < now - self.time_window:
            self.calls.popleft()
        
        # Check if under limit
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        
        return False
    
    def time_until_reset(self) -> float:
        """Get time until rate limit resets"""
        if not self.calls:
            return 0
        return self.calls[0] + self.time_window - time.time()


@dataclass
class CircuitBreaker:
    """Circuit breaker implementation"""
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[float] = None
    success_count: int = 0
    
    # Configuration
    failure_threshold: int = 5
    timeout: int = 60  # seconds
    half_open_max_calls: int = 3
    
    def can_execute(self) -> bool:
        """Check if operation can be executed"""
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            if self.last_failure_time and time.time() - self.last_failure_time >= self.timeout:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                return True
            return False
        else:  # HALF_OPEN
            return self.success_count < self.half_open_max_calls
    
    def record_success(self):
        """Record successful operation"""
        self.failure_count = 0
        self.success_count += 1
        
        if self.state == CircuitState.HALF_OPEN and self.success_count >= self.half_open_max_calls:
            self.state = CircuitState.CLOSED
    
    def record_failure(self):
        """Record failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        self.success_count = 0
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN


@dataclass
class ConnectionPool:
    """HTTP connection pool for MCP servers"""
    clients: List[httpx.AsyncClient] = field(default_factory=list)
    max_size: int = 10
    current_size: int = 0
    
    async def get_client(self, config: MCPServerConfig) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self.clients:
            return self.clients.pop()
        
        if self.current_size < self.max_size:
            client = httpx.AsyncClient(
                base_url=config.server_url.rstrip('/'),
                timeout=config.timeout,
                verify=config.verify_ssl,
                headers=self._get_default_headers(config)
            )
            self.current_size += 1
            return client
        
        # Wait for available client
        await asyncio.sleep(0.1)
        return await self.get_client(config)
    
    async def return_client(self, client: httpx.AsyncClient):
        """Return client to pool"""
        if len(self.clients) < self.max_size:
            self.clients.append(client)
        else:
            await client.aclose()
            self.current_size -= 1
    
    def _get_default_headers(self, config: MCPServerConfig) -> Dict[str, str]:
        """Get default HTTP headers"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Chronos-AI-Agent-Builder/Advanced-MCP-Client-2.0'
        }
        
        if config.api_key:
            headers['Authorization'] = f'Bearer {config.api_key}'
        
        return headers


class LoadBalancer:
    """Load balancer for MCP servers"""
    
    def __init__(self):
        self.servers: Dict[str, Dict[str, Any]] = {}
        self.current_index = defaultdict(int)
        self.server_stats = defaultdict(lambda: {
            'requests': 0,
            'errors': 0,
            'response_times': deque(maxlen=100)
        })
    
    def add_server(self, server_id: str, server_config: Dict[str, Any]):
        """Add server to load balancer"""
        self.servers[server_id] = server_config
        self.current_index[server_id] = 0
    
    def remove_server(self, server_id: str):
        """Remove server from load balancer"""
        if server_id in self.servers:
            del self.servers[server_id]
            del self.current_index[server_id]
            if server_id in self.server_stats:
                del self.server_stats[server_id]
    
    def get_server(self, algorithm: str = "round_robin", group_servers: Optional[List[str]] = None) -> Optional[str]:
        """Get server using load balancing algorithm"""
        available_servers = []
        
        if group_servers:
            for server_id in group_servers:
                if server_id in self.servers:
                    server = self.servers[server_id]
                    if server.get('is_active', True) and server.get('health_status') == HealthStatus.HEALTHY:
                        available_servers.append(server_id)
        else:
            for server_id, server in self.servers.items():
                if server.get('is_active', True) and server.get('health_status') == HealthStatus.HEALTHY:
                    available_servers.append(server_id)
        
        if not available_servers:
            return None
        
        if algorithm == "round_robin":
            return self._round_robin(available_servers)
        elif algorithm == "weighted":
            return self._weighted(available_servers)
        elif algorithm == "least_connections":
            return self._least_connections(available_servers)
        elif algorithm == "fastest_response":
            return self._fastest_response(available_servers)
        else:
            return random.choice(available_servers)
    
    def _round_robin(self, servers: List[str]) -> str:
        """Round robin load balancing"""
        server = servers[self.current_index['round_robin'] % len(servers)]
        self.current_index['round_robin'] += 1
        return server
    
    def _weighted(self, servers: List[str]) -> str:
        """Weighted load balancing"""
        weights = []
        for server_id in servers:
            weight = self.servers[server_id].get('weight', 1)
            weights.extend([server_id] * weight)
        return random.choice(weights)
    
    def _least_connections(self, servers: List[str]) -> str:
        """Least connections load balancing"""
        return min(servers, key=lambda s: self.servers[s].get('current_connections', 0))
    
    def _fastest_response(self, servers: List[str]) -> str:
        """Fastest response time load balancing"""
        return min(servers, key=lambda s: self._get_avg_response_time(s))
    
    def _get_avg_response_time(self, server_id: str) -> float:
        """Get average response time for server"""
        stats = self.server_stats[server_id]
        if stats['response_times']:
            return sum(stats['response_times']) / len(stats['response_times'])
        return 0
    
    def record_request(self, server_id: str, response_time: float, success: bool):
        """Record request statistics"""
        stats = self.server_stats[server_id]
        stats['requests'] += 1
        stats['response_times'].append(response_time)
        
        if not success:
            stats['errors'] += 1
    
    def get_server_stats(self, server_id: str) -> Dict[str, Any]:
        """Get server statistics"""
        stats = self.server_stats[server_id]
        return {
            'requests': stats['requests'],
            'errors': stats['errors'],
            'error_rate': stats['errors'] / max(stats['requests'], 1),
            'avg_response_time': self._get_avg_response_time(server_id)
        }


class RequestCache:
    """Request caching system"""
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, datetime] = {}
    
    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response"""
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if datetime.utcnow() < entry['expires_at']:
                self.access_times[cache_key] = datetime.utcnow()
                return entry['data']
            else:
                # Remove expired entry
                del self.cache[cache_key]
                if cache_key in self.access_times:
                    del self.access_times[cache_key]
        return None
    
    def set(self, cache_key: str, data: Dict[str, Any], ttl_seconds: int = 3600):
        """Set cached response"""
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        self.cache[cache_key] = {
            'data': data,
            'expires_at': expires_at
        }
        self.access_times[cache_key] = datetime.utcnow()
    
    def generate_cache_key(self, operation_type: str, request_data: Dict[str, Any], server_id: str) -> str:
        """Generate cache key for request"""
        content = f"{operation_type}:{server_id}:{json.dumps(request_data, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def cleanup_expired(self):
        """Remove expired cache entries"""
        now = datetime.utcnow()
        expired_keys = []
        
        for cache_key, entry in self.cache.items():
            if now >= entry['expires_at']:
                expired_keys.append(cache_key)
        
        for key in expired_keys:
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]


class RetryPolicy:
    """Retry policy implementation"""
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0, jitter: bool = True):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.jitter = jitter
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay before retry"""
        delay = self.backoff_factor ** attempt
        
        if self.jitter:
            # Add random jitter (±25%)
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)
    
    def should_retry(self, attempt: int, exception: Exception) -> bool:
        """Determine if operation should be retried"""
        if attempt >= self.max_retries:
            return False
        
        # Retry on network errors and server errors (5xx)
        if isinstance(exception, (httpx.ConnectError, httpx.TimeoutException)):
            return True
        
        if isinstance(exception, httpx.HTTPStatusError):
            return 500 <= exception.response.status_code < 600
        
        return False


class AdvancedMCPClient:
    """
    Advanced MCP Client with enhanced features
    
    Features:
    - Connection pooling
    - Load balancing
    - Circuit breaker pattern
    - Retry logic
    - Request caching
    - Rate limiting
    - Monitoring and metrics
    """
    
    def __init__(self, config: MCPServerConfig, server_id: str):
        self.config = config
        self.server_id = server_id
        self.connection_pool = ConnectionPool(max_size=config.max_connections if hasattr(config, 'max_connections') else 10)
        self.circuit_breaker = CircuitBreaker()
        self.rate_limiter = RateLimiter(
            max_calls=config.rate_limit_per_minute if hasattr(config, 'rate_limit_per_minute') else 100
        )
        self.request_cache = RequestCache()
        self.retry_policy = RetryPolicy(
            max_retries=config.retry_config.get('max_retries', 3) if config.retry_config else 3
        )
        
        # Monitoring
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cached_requests': 0,
            'retried_requests': 0,
            'total_response_time': 0.0,
            'last_request_time': None
        }
    
    async def file_operation(self, operation: MCPFileOperation, cache_key: Optional[str] = None) -> Dict[str, Any]:
        """Enhanced file operation with advanced features"""
        return await self._execute_operation(
            operation_type=OperationType.FILE_OPERATION,
            operation_name=operation.operation,
            request_data=operation.dict(),
            cache_key=cache_key,
            operation_func=self._do_file_operation,
            operation_args=(operation,)
        )
    
    async def database_query(self, query: MCPDatabaseQuery, cache_key: Optional[str] = None) -> Dict[str, Any]:
        """Enhanced database query with advanced features"""
        return await self._execute_operation(
            operation_type=OperationType.DATABASE_QUERY,
            operation_name=query.operation,
            request_data=query.dict(),
            cache_key=cache_key,
            operation_func=self._do_database_query,
            operation_args=(query,)
        )
    
    async def web_scraping(self, task: MCPWebScrapingTask, cache_key: Optional[str] = None) -> Dict[str, Any]:
        """Enhanced web scraping with advanced features"""
        return await self._execute_operation(
            operation_type=OperationType.WEB_SCRAPING,
            operation_name="scrape",
            request_data=task.dict(),
            cache_key=cache_key,
            operation_func=self._do_web_scraping,
            operation_args=(task,)
        )
    
    async def api_request(self, request: MCPApiRequest, cache_key: Optional[str] = None) -> Dict[str, Any]:
        """Enhanced API request with advanced features"""
        return await self._execute_operation(
            operation_type=OperationType.API_PROXY,
            operation_name=request.method,
            request_data=request.dict(),
            cache_key=cache_key,
            operation_func=self._do_api_request,
            operation_args=(request,)
        )
    
    async def _execute_operation(
        self,
        operation_type: OperationType,
        operation_name: str,
        request_data: Dict[str, Any],
        cache_key: Optional[str],
        operation_func: Callable,
        operation_args: tuple
    ) -> Dict[str, Any]:
        """Execute operation with advanced features"""
        start_time = time.time()
        
        # Check rate limiting
        if not self.rate_limiter.is_allowed():
            raise MCPServerError(f"Rate limit exceeded. Try again in {self.rate_limiter.time_until_reset():.1f} seconds")
        
        # Check circuit breaker
        if not self.circuit_breaker.can_execute():
            raise MCPServerError(f"Circuit breaker is open for server {self.server_id}")
        
        # Check cache
        if cache_key:
            cached_result = self.request_cache.get(cache_key)
            if cached_result:
                self.metrics['cached_requests'] += 1
                logger.info(f"Cache hit for operation {operation_type}")
                return cached_result
        
        # Execute with retry logic
        last_exception = None
        for attempt in range(self.retry_policy.max_retries + 1):
            try:
                client = await self.connection_pool.get_client(self.config)
                
                try:
                    result = await operation_func(*operation_args)
                    
                    # Record success
                    response_time = time.time() - start_time
                    self._record_success(response_time)
                    
                    # Cache result if cache key provided
                    if cache_key and result:
                        self.request_cache.set(cache_key, result)
                    
                    # Log operation
                    await self._log_operation(
                        operation_type, operation_name, request_data, result,
                        response_time, LogStatus.SUCCESS
                    )
                    
                    return result
                
                finally:
                    await self.connection_pool.return_client(client)
            
            except Exception as e:
                last_exception = e
                self._record_failure()
                
                # Log operation
                await self._log_operation(
                    operation_type, operation_name, request_data, None,
                    time.time() - start_time, LogStatus.ERROR, str(e)
                )
                
                # Check if should retry
                if attempt < self.retry_policy.max_retries and self.retry_policy.should_retry(attempt, e):
                    delay = self.retry_policy.calculate_delay(attempt)
                    self.metrics['retried_requests'] += 1
                    logger.warning(f"Retrying operation {operation_type} (attempt {attempt + 1}) after {delay:.2f}s delay")
                    await asyncio.sleep(delay)
                    continue
                else:
                    break
        
        # All retries failed
        raise MCPServerError(f"Operation failed after {self.retry_policy.max_retries + 1} attempts: {str(last_exception)}")
    
    async def _do_file_operation(self, operation: MCPFileOperation) -> Dict[str, Any]:
        """Execute file operation"""
        client = await self.connection_pool.get_client(self.config)
        try:
            response = await client.post("/api/v1/files", json=operation.dict())
            response.raise_for_status()
            return response.json()
        finally:
            await self.connection_pool.return_client(client)
    
    async def _do_database_query(self, query: MCPDatabaseQuery) -> Dict[str, Any]:
        """Execute database query"""
        client = await self.connection_pool.get_client(self.config)
        try:
            response = await client.post("/api/v1/database", json=query.dict())
            response.raise_for_status()
            return response.json()
        finally:
            await self.connection_pool.return_client(client)
    
    async def _do_web_scraping(self, task: MCPWebScrapingTask) -> Dict[str, Any]:
        """Execute web scraping"""
        client = await self.connection_pool.get_client(self.config)
        try:
            response = await client.post("/api/v1/scraping", json=task.dict())
            response.raise_for_status()
            return response.json()
        finally:
            await self.connection_pool.return_client(client)
    
    async def _do_api_request(self, request: MCPApiRequest) -> Dict[str, Any]:
        """Execute API request"""
        client = await self.connection_pool.get_client(self.config)
        try:
            response = await client.post("/api/v1/proxy", json=request.dict())
            response.raise_for_status()
            return response.json()
        finally:
            await self.connection_pool.return_client(client)
    
    def _record_success(self, response_time: float):
        """Record successful operation"""
        self.metrics['total_requests'] += 1
        self.metrics['successful_requests'] += 1
        self.metrics['total_response_time'] += response_time
        self.metrics['last_request_time'] = datetime.utcnow()
        
        self.circuit_breaker.record_success()
    
    def _record_failure(self):
        """Record failed operation"""
        self.metrics['total_requests'] += 1
        self.metrics['failed_requests'] += 1
        self.metrics['last_request_time'] = datetime.utcnow()
        
        self.circuit_breaker.record_failure()
    
    async def _log_operation(
        self,
        operation_type: OperationType,
        operation_name: str,
        request_data: Dict[str, Any],
        response_data: Optional[Dict[str, Any]],
        duration_ms: float,
        status: LogStatus,
        error_message: Optional[str] = None
    ):
        """Log operation to database"""
        try:
            # This would be implemented to log to database
            logger.info(f"Operation logged: {operation_type} - {operation_name} - {status.value}")
        except Exception as e:
            logger.error(f"Failed to log operation: {e}")
    
    async def health_check(self) -> bool:
        """Enhanced health check"""
        try:
            client = await self.connection_pool.get_client(self.config)
            try:
                response = await client.get("/health")
                return response.status_code == 200
            finally:
                await self.connection_pool.return_client(client)
        except Exception:
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get client metrics"""
        avg_response_time = (
            self.metrics['total_response_time'] / max(self.metrics['total_requests'], 1)
        )
        
        return {
            **self.metrics,
            'average_response_time': avg_response_time,
            'success_rate': self.metrics['successful_requests'] / max(self.metrics['total_requests'], 1),
            'circuit_breaker_state': self.circuit_breaker.state.value,
            'cache_size': len(self.request_cache.cache)
        }
    
    async def close(self):
        """Close client and cleanup resources"""
        # Close all clients in pool
        for client in self.connection_pool.clients:
            await client.aclose()
        
        self.connection_pool.clients.clear()
        self.connection_pool.current_size = 0
        
        # Cleanup cache
        self.request_cache.cleanup_expired()


class MCPServerError(Exception):
    """Custom exception for MCP server errors"""
    pass