"""
MCP Server Models
Database models for managing MCP server configurations and operations
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any
import json

from app.models.base import Base


class MCPServer(Base):
    """
    Model for storing MCP server configurations and metadata
    """
    __tablename__ = "mcp_servers"

    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Server Configuration
    server_url = Column(String(500), nullable=False)
    api_key = Column(String(500), nullable=True)
    timeout = Column(Integer, default=30)
    verify_ssl = Column(Boolean, default=True)
    
    # Authentication
    auth_type = Column(String(50), default="api_key")  # api_key, oauth2, jwt, basic
    auth_config = Column(JSON, nullable=True)  # Store additional auth parameters
    
    # Status and Health
    status = Column(String(50), default="inactive")  # active, inactive, error, maintenance
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Load Balancing
    weight = Column(Integer, default=1)  # For load balancing
    max_connections = Column(Integer, default=10)
    current_connections = Column(Integer, default=0)
    
    # Rate Limiting
    rate_limit_per_minute = Column(Integer, default=100)
    rate_limit_per_hour = Column(Integer, default=1000)
    current_rate_count = Column(Integer, default=0)
    rate_limit_reset = Column(DateTime, nullable=True)
    
    # Monitoring
    last_health_check = Column(DateTime, nullable=True)
    health_status = Column(String(50), default="unknown")  # healthy, unhealthy, unknown
    response_time_avg = Column(Float, default=0.0)
    error_count = Column(Integer, default=0)
    total_requests = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
    
    # Tags and Categories
    tags = Column(JSON, nullable=True)  # List of tags for categorization
    category = Column(String(100), nullable=True)
    
    # Advanced Configuration
    retry_config = Column(JSON, nullable=True)  # Retry policy configuration
    circuit_breaker_config = Column(JSON, nullable=True)  # Circuit breaker settings
    cache_config = Column(JSON, nullable=True)  # Caching configuration
    monitoring_config = Column(JSON, nullable=True)  # Monitoring settings
    
    # Relationships
    operation_logs = relationship("MCPOperationLog", back_populates="server")
    metrics = relationship("MCPServerMetric", back_populates="server")
    
    def __repr__(self):
        return f"<MCPServer(id={self.id}, server_id='{self.server_id}', status='{self.status}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "server_id": self.server_id,
            "name": self.name,
            "description": self.description,
            "server_url": self.server_url,
            "timeout": self.timeout,
            "verify_ssl": self.verify_ssl,
            "auth_type": self.auth_type,
            "status": self.status,
            "is_default": self.is_default,
            "is_active": self.is_active,
            "weight": self.weight,
            "max_connections": self.max_connections,
            "current_connections": self.current_connections,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "rate_limit_per_hour": self.rate_limit_per_hour,
            "health_status": self.health_status,
            "response_time_avg": self.response_time_avg,
            "error_count": self.error_count,
            "total_requests": self.total_requests,
            "tags": self.tags or [],
            "category": self.category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class MCPOperationLog(Base):
    """
    Model for logging MCP server operations
    """
    __tablename__ = "mcp_operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("mcp_servers.id"), nullable=False)
    
    # Operation Details
    operation_type = Column(String(100), nullable=False)  # file_operation, database_query, etc.
    operation_name = Column(String(255), nullable=False)
    request_data = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)
    
    # Timing
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Float, nullable=True)
    
    # Status and Results
    status = Column(String(50), nullable=False)  # success, error, timeout
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    
    # Request Metadata
    user_id = Column(String(255), nullable=True)
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(50), nullable=True)
    
    # Performance Metrics
    response_size = Column(Integer, nullable=True)
    cache_hit = Column(Boolean, default=False)
    retry_count = Column(Integer, default=0)
    
    # Relationships
    server = relationship("MCPServer", back_populates="operation_logs")
    
    def __repr__(self):
        return f"<MCPOperationLog(id={self.id}, server_id={self.server_id}, operation_type='{self.operation_type}', status='{self.status}')>"


class MCPServerMetric(Base):
    """
    Model for storing MCP server performance metrics
    """
    __tablename__ = "mcp_server_metrics"

    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("mcp_servers.id"), nullable=False)
    
    # Metric Details
    metric_name = Column(String(100), nullable=False)  # response_time, error_rate, throughput, etc.
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50), nullable=True)  # ms, count, percentage, etc.
    
    # Time Period
    timestamp = Column(DateTime, default=func.now())
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    
    # Additional Context
    tags = Column(JSON, nullable=True)  # Additional metric tags
    additional_metadata = Column(JSON, nullable=True)  # Additional metadata
    
    # Relationships
    server = relationship("MCPServer", back_populates="metrics")
    
    def __repr__(self):
        return f"<MCPServerMetric(id={self.id}, server_id={self.server_id}, metric_name='{self.metric_name}', value={self.metric_value})>"


class MCPCacheEntry(Base):
    """
    Model for caching MCP responses
    """
    __tablename__ = "mcp_cache_entries"

    id = Column(Integer, primary_key=True, index=True)
    
    # Cache Key
    cache_key = Column(String(500), unique=True, index=True, nullable=False)
    server_id = Column(Integer, ForeignKey("mcp_servers.id"), nullable=False)
    
    # Cached Data
    cached_data = Column(JSON, nullable=False)
    operation_type = Column(String(100), nullable=False)
    
    # Cache Metadata
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)
    access_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, default=func.now())
    
    # Cache Configuration
    ttl_seconds = Column(Integer, default=3600)  # Time to live
    priority = Column(Integer, default=1)  # Cache priority for eviction
    
    def __repr__(self):
        return f"<MCPCacheEntry(id={self.id}, cache_key='{self.cache_key}', expires_at={self.expires_at})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return datetime.utcnow() > self.expires_at
    
    def update_access(self):
        """Update access count and timestamp"""
        self.access_count += 1
        self.last_accessed = func.now()


class MCPServerGroup(Base):
    """
    Model for grouping MCP servers for load balancing
    """
    __tablename__ = "mcp_server_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Load Balancing Configuration
    algorithm = Column(String(50), default="round_robin")  # round_robin, weighted, least_connections
    health_check_interval = Column(Integer, default=60)  # seconds
    failover_enabled = Column(Boolean, default=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<MCPServerGroup(id={self.id}, name='{self.name}', algorithm='{self.algorithm}')>"


class MCPServerGroupMember(Base):
    """
    Model for managing server group membership
    """
    __tablename__ = "mcp_server_group_members"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("mcp_server_groups.id"), nullable=False)
    server_id = Column(Integer, ForeignKey("mcp_servers.id"), nullable=False)
    
    # Membership Configuration
    weight = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)  # Higher priority servers are preferred
    
    added_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<MCPServerGroupMember(id={self.id}, group_id={self.group_id}, server_id={self.server_id})>"