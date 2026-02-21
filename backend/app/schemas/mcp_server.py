"""
MCP Server Schemas
Pydantic schemas for MCP server operations and validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from enum import Enum
import json


class AuthType(str, Enum):
    """Authentication types supported by MCP servers"""
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    JWT = "jwt"
    BASIC = "basic"
    CERTIFICATE = "certificate"


class MCPServerConfig(BaseModel):
    """MCP Server Configuration Schema"""
    server_url: str = Field(..., description="MCP Server URL")
    api_key: Optional[str] = Field(None, description="API Key for authentication")
    timeout: int = Field(30, description="Request timeout in seconds")
    verify_ssl: bool = Field(True, description="Verify SSL certificates")


class MCPFileOperation(BaseModel):
    """File operation schema for MCP servers"""
    operation: str = Field(..., description="Operation type: read, write, list, delete")
    path: str = Field(..., description="File path")
    content: Optional[str] = Field(None, description="File content for write operations")
    recursive: bool = Field(False, description="Recursive operation for list/delete")


class MCPDatabaseQuery(BaseModel):
    """Database query schema for MCP servers"""
    operation: str = Field(..., description="Database operation: query, execute, fetch")
    query: str = Field(..., description="SQL query or database command")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Query parameters")
    database_type: str = Field(..., description="Database type: postgres, mysql, sqlite, etc.")


class MCPWebScrapingTask(BaseModel):
    """Web scraping task schema for MCP servers"""
    url: str = Field(..., description="URL to scrape")
    selectors: Dict[str, str] = Field(..., description="CSS selectors for data extraction")
    render_javascript: bool = Field(False, description="Render JavaScript before scraping")
    wait_for_selector: Optional[str] = Field(None, description="Wait for specific selector")


class MCPApiRequest(BaseModel):
    """API request schema for MCP servers"""
    method: str = Field(..., description="HTTP method: GET, POST, PUT, DELETE, etc.")
    url: str = Field(..., description="API endpoint URL")
    headers: Optional[Dict[str, str]] = Field(None, description="Request headers")
    body: Optional[Dict[str, Any]] = Field(None, description="Request body")
    params: Optional[Dict[str, str]] = Field(None, description="Query parameters")


class ServerStatus(str, Enum):
    """MCP server status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class HealthStatus(str, Enum):
    """MCP server health status"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class LoadBalanceAlgorithm(str, Enum):
    """Load balancing algorithms"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    LEAST_CONNECTIONS = "least_connections"
    FASTEST_RESPONSE = "fastest_response"


class OperationType(str, Enum):
    """MCP operation types"""
    FILE_OPERATION = "file_operation"
    DATABASE_QUERY = "database_query"
    WEB_SCRAPING = "web_scraping"
    API_PROXY = "api_proxy"
    BATCH_OPERATION = "batch_operation"
    WEBSOCKET = "websocket"


class LogStatus(str, Enum):
    """Operation log status"""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class MCPServerBase(BaseModel):
    """Base MCP server configuration"""
    name: str = Field(..., description="Human-readable server name")
    description: Optional[str] = Field(None, description="Server description")
    server_url: str = Field(..., description="MCP Server URL")
    timeout: int = Field(30, ge=1, le=300, description="Request timeout in seconds")
    verify_ssl: bool = Field(True, description="Verify SSL certificates")
    auth_type: AuthType = Field(AuthType.API_KEY, description="Authentication type")
    is_default: bool = Field(False, description="Set as default server")
    tags: Optional[List[str]] = Field(None, description="Server tags")
    category: Optional[str] = Field(None, description="Server category")


class MCPServerCreate(MCPServerBase):
    """Schema for creating MCP server"""
    server_id: Optional[str] = Field(None, description="Unique server identifier (auto-generated if not provided)")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    auth_config: Optional[Dict[str, Any]] = Field(None, description="Additional authentication configuration")
    
    # Load balancing
    weight: int = Field(1, ge=1, le=100, description="Server weight for load balancing")
    max_connections: int = Field(10, ge=1, le=1000, description="Maximum concurrent connections")
    
    # Rate limiting
    rate_limit_per_minute: int = Field(100, ge=1, le=10000, description="Rate limit per minute")
    rate_limit_per_hour: int = Field(1000, ge=1, le=100000, description="Rate limit per hour")
    
    # Advanced configuration
    retry_config: Optional[Dict[str, Any]] = Field(None, description="Retry policy configuration")
    circuit_breaker_config: Optional[Dict[str, Any]] = Field(None, description="Circuit breaker configuration")
    cache_config: Optional[Dict[str, Any]] = Field(None, description="Caching configuration")
    monitoring_config: Optional[Dict[str, Any]] = Field(None, description="Monitoring configuration")


class MCPServerUpdate(BaseModel):
    """Schema for updating MCP server"""
    name: Optional[str] = Field(None, description="Human-readable server name")
    description: Optional[str] = Field(None, description="Server description")
    server_url: Optional[str] = Field(None, description="MCP Server URL")
    timeout: Optional[int] = Field(None, ge=1, le=300, description="Request timeout in seconds")
    verify_ssl: Optional[bool] = Field(None, description="Verify SSL certificates")
    auth_type: Optional[AuthType] = Field(None, description="Authentication type")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    auth_config: Optional[Dict[str, Any]] = Field(None, description="Additional authentication configuration")
    is_default: Optional[bool] = Field(None, description="Set as default server")
    is_active: Optional[bool] = Field(None, description="Server active status")
    tags: Optional[List[str]] = Field(None, description="Server tags")
    category: Optional[str] = Field(None, description="Server category")
    
    # Load balancing
    weight: Optional[int] = Field(None, ge=1, le=100, description="Server weight for load balancing")
    max_connections: Optional[int] = Field(None, ge=1, le=1000, description="Maximum concurrent connections")
    
    # Rate limiting
    rate_limit_per_minute: Optional[int] = Field(None, ge=1, le=10000, description="Rate limit per minute")
    rate_limit_per_hour: Optional[int] = Field(None, ge=1, le=100000, description="Rate limit per hour")


class MCPServerResponse(BaseModel):
    """Schema for MCP server response"""
    id: int
    server_id: str
    name: str
    description: Optional[str]
    server_url: str
    timeout: int
    verify_ssl: bool
    auth_type: AuthType
    status: ServerStatus
    is_default: bool
    is_active: bool
    weight: int
    max_connections: int
    current_connections: int
    rate_limit_per_minute: int
    rate_limit_per_hour: int
    health_status: HealthStatus
    response_time_avg: float
    error_count: int
    total_requests: int
    tags: List[str]
    category: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class MCPServerInfo(BaseModel):
    """Schema for MCP server information"""
    servers: List[MCPServerResponse]
    total_servers: int
    active_servers: int
    default_server: Optional[str]
    load_balancing_status: Dict[str, Any]


class MCPHealthCheck(BaseModel):
    """Schema for MCP health check"""
    server_id: str
    status: HealthStatus
    response_time_ms: Optional[float]
    last_check: datetime
    error_message: Optional[str]
    uptime_percentage: Optional[float]
    error_rate: Optional[float]


class MCPHealthDashboard(BaseModel):
    """Schema for MCP health dashboard"""
    overall_status: HealthStatus
    total_servers: int
    healthy_servers: int
    unhealthy_servers: int
    unknown_servers: int
    servers: List[MCPHealthCheck]
    cluster_metrics: Dict[str, Any]


class MCPOperationLogBase(BaseModel):
    """Base schema for operation logs"""
    operation_type: OperationType
    operation_name: str
    request_data: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None


class MCPOperationLogCreate(MCPOperationLogBase):
    """Schema for creating operation log"""
    server_id: int


class MCPOperationLogResponse(BaseModel):
    """Schema for operation log response"""
    id: int
    server_id: int
    operation_type: OperationType
    operation_name: str
    request_data: Optional[Dict[str, Any]]
    response_data: Optional[Dict[str, Any]]
    started_at: datetime
    completed_at: Optional[datetime]
    duration_ms: Optional[float]
    status: LogStatus
    error_message: Optional[str]
    error_code: Optional[str]
    user_id: Optional[str]
    user_agent: Optional[str]
    ip_address: Optional[str]
    response_size: Optional[int]
    cache_hit: bool
    retry_count: int
    
    class Config:
        from_attributes = True


class MCPServerMetricBase(BaseModel):
    """Base schema for server metrics"""
    metric_name: str
    metric_value: float
    metric_unit: Optional[str] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    tags: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class MCPServerMetricCreate(MCPServerMetricBase):
    """Schema for creating server metric"""
    server_id: int


class MCPServerMetricResponse(BaseModel):
    """Schema for server metric response"""
    id: int
    server_id: int
    metric_name: str
    metric_value: float
    metric_unit: Optional[str]
    timestamp: datetime
    period_start: Optional[datetime]
    period_end: Optional[datetime]
    tags: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class MCPCacheEntryBase(BaseModel):
    """Base schema for cache entries"""
    cache_key: str
    cached_data: Dict[str, Any]
    operation_type: OperationType
    ttl_seconds: int = Field(3600, ge=1, le=86400)
    priority: int = Field(1, ge=1, le=10)


class MCPCacheEntryCreate(MCPCacheEntryBase):
    """Schema for creating cache entry"""
    server_id: int


class MCPCacheEntryResponse(BaseModel):
    """Schema for cache entry response"""
    id: int
    cache_key: str
    server_id: int
    cached_data: Dict[str, Any]
    operation_type: OperationType
    created_at: datetime
    expires_at: datetime
    access_count: int
    last_accessed: datetime
    ttl_seconds: int
    priority: int
    is_expired: bool
    
    class Config:
        from_attributes = True


class MCPServerGroupBase(BaseModel):
    """Base schema for server groups"""
    name: str = Field(..., description="Group name")
    description: Optional[str] = Field(None, description="Group description")
    algorithm: LoadBalanceAlgorithm = Field(LoadBalanceAlgorithm.ROUND_ROBIN, description="Load balancing algorithm")
    health_check_interval: int = Field(60, ge=10, le=3600, description="Health check interval in seconds")
    failover_enabled: bool = Field(True, description="Enable failover")


class MCPServerGroupCreate(MCPServerGroupBase):
    """Schema for creating server group"""
    pass


class MCPServerGroupUpdate(BaseModel):
    """Schema for updating server group"""
    name: Optional[str] = Field(None, description="Group name")
    description: Optional[str] = Field(None, description="Group description")
    algorithm: Optional[LoadBalanceAlgorithm] = Field(None, description="Load balancing algorithm")
    health_check_interval: Optional[int] = Field(None, ge=10, le=3600, description="Health check interval in seconds")
    failover_enabled: Optional[bool] = Field(None, description="Enable failover")
    is_active: Optional[bool] = Field(None, description="Group active status")


class MCPServerGroupResponse(BaseModel):
    """Schema for server group response"""
    id: int
    name: str
    description: Optional[str]
    algorithm: LoadBalanceAlgorithm
    health_check_interval: int
    failover_enabled: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class MCPServerGroupMemberBase(BaseModel):
    """Base schema for group members"""
    weight: int = Field(1, ge=1, le=100, description="Member weight")
    priority: int = Field(1, ge=1, le=10, description="Member priority")


class MCPServerGroupMemberCreate(MCPServerGroupMemberBase):
    """Schema for creating group member"""
    group_id: int
    server_id: int


class MCPServerGroupMemberResponse(BaseModel):
    """Schema for group member response"""
    id: int
    group_id: int
    server_id: int
    weight: int
    is_active: bool
    priority: int
    added_at: datetime
    
    class Config:
        from_attributes = True


class MCPServerGroupInfo(BaseModel):
    """Schema for server group information"""
    group: MCPServerGroupResponse
    members: List[Dict[str, Any]]
    total_members: int
    active_members: int


class MCPBatchOperation(BaseModel):
    """Schema for batch operations"""
    operations: List[Dict[str, Any]] = Field(..., description="List of operations to execute")
    parallel: bool = Field(False, description="Execute operations in parallel")
    timeout: Optional[int] = Field(None, description="Batch operation timeout")
    server_id: Optional[str] = Field(None, description="Specific server to use")


class MCPBatchOperationResult(BaseModel):
    """Schema for batch operation results"""
    batch_id: str
    total_operations: int
    successful_operations: int
    failed_operations: int
    results: List[Dict[str, Any]]
    execution_time_ms: float
    errors: List[Dict[str, Any]]


class MCPServerConfigAdvanced(BaseModel):
    """Schema for advanced server configuration"""
    retry_policy: Dict[str, Any] = Field(
        default={"max_retries": 3, "backoff_factor": 2, "jitter": True},
        description="Retry policy configuration"
    )
    circuit_breaker: Dict[str, Any] = Field(
        default={"failure_threshold": 5, "timeout": 60, "half_open_max_calls": 3},
        description="Circuit breaker configuration"
    )
    caching: Dict[str, Any] = Field(
        default={"enabled": True, "ttl": 3600, "max_size": 1000},
        description="Caching configuration"
    )
    monitoring: Dict[str, Any] = Field(
        default={"metrics_enabled": True, "logging_level": "INFO"},
        description="Monitoring configuration"
    )


class MCPWebSocketMessage(BaseModel):
    """Schema for WebSocket messages"""
    message_type: str = Field(..., description="Message type")
    data: Dict[str, Any] = Field(..., description="Message data")
    server_id: Optional[str] = Field(None, description="Target server")
    user_id: Optional[str] = Field(None, description="User ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MCPWebSocketResponse(BaseModel):
    """Schema for WebSocket responses"""
    success: bool
    message_id: str
    server_id: Optional[str]
    data: Optional[Dict[str, Any]]
    error: Optional[str]
    timestamp: datetime


class MCPAnalyticsRequest(BaseModel):
    """Schema for analytics requests"""
    server_id: Optional[str] = Field(None, description="Specific server or None for all")
    start_date: Optional[datetime] = Field(None, description="Start date for analytics")
    end_date: Optional[datetime] = Field(None, description="End date for analytics")
    metrics: Optional[List[str]] = Field(None, description="Specific metrics to retrieve")
    group_by: Optional[str] = Field(None, description="Group results by")


class MCPFileRequest(BaseModel):
    """Schema for file operation request"""
    operation: str = Field(..., description="Operation type: read, write, list, delete")
    path: str = Field(..., description="File path")
    content: Optional[str] = Field(None, description="File content for write operations")
    recursive: bool = Field(False, description="Recursive operation for list/delete")
    server_id: Optional[str] = Field(None, description="Specific server to use")


class MCPDatabaseRequest(BaseModel):
    """Schema for database query request"""
    query: str = Field(..., description="SQL query or database command")
    database_type: str = Field(..., description="Database type: postgres, mysql, sqlite, etc.")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Query parameters")
    server_id: Optional[str] = Field(None, description="Specific server to use")


class MCPWebScrapingRequest(BaseModel):
    """Schema for web scraping request"""
    url: str = Field(..., description="URL to scrape")
    selectors: Dict[str, str] = Field(..., description="CSS selectors for data extraction")
    render_javascript: bool = Field(False, description="Render JavaScript before scraping")
    server_id: Optional[str] = Field(None, description="Specific server to use")


class MCPApiProxyRequest(BaseModel):
    """Schema for API proxy request"""
    method: str = Field(..., description="HTTP method: GET, POST, PUT, DELETE, etc.")
    url: str = Field(..., description="API endpoint URL")
    headers: Optional[Dict[str, str]] = Field(None, description="Request headers")
    body: Optional[Dict[str, Any]] = Field(None, description="Request body")
    params: Optional[Dict[str, str]] = Field(None, description="Query parameters")
    server_id: Optional[str] = Field(None, description="Specific server to use")


class MCPFileResponse(BaseModel):
    """Schema for file operation response"""
    success: bool
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message")


class MCPAnalyticsResponse(BaseModel):
    """Schema for analytics responses"""
    server_id: Optional[str]
    time_range: Dict[str, datetime]
    metrics: Dict[str, Any]
    summary: Dict[str, Any]
    trends: Dict[str, Any]