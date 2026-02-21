"""
Playwright Models
Database models for Playwright browser automation services
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any

from app.models.base import Base


class PlaywrightBrowserSession(Base):
    """
    Model for managing Playwright browser sessions
    """
    __tablename__ = "playwright_browser_sessions"

    # Session Identification
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(String(255), nullable=False)
    
    # Browser Configuration
    browser_type = Column(String(50), nullable=False)  # chromium, firefox, webkit
    viewport_width = Column(Integer, default=1920)
    viewport_height = Column(Integer, default=1080)
    user_agent = Column(String(500), nullable=True)
    headless = Column(Boolean, default=True)
    
    # Session State
    status = Column(String(50), default="initializing")  # initializing, active, idle, terminated, error
    current_url = Column(String(2000), nullable=True)
    cookies = Column(JSON, nullable=True)
    local_storage = Column(JSON, nullable=True)
    session_storage = Column(JSON, nullable=True)
    
    # Resource Management
    memory_usage_mb = Column(Float, default=0.0)
    cpu_usage_percent = Column(Float, default=0.0)
    network_requests = Column(Integer, default=0)
    
    # Timing
    created_at = Column(DateTime, default=func.now())
    last_activity = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    automation_tasks = relationship("PlaywrightAutomationTask", back_populates="session")
    artifacts = relationship("PlaywrightArtifact", back_populates="session")
    
    def __repr__(self):
        return f"<PlaywrightBrowserSession(id={self.id}, session_id='{self.session_id}', status='{self.status}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "browser_type": self.browser_type,
            "viewport_width": self.viewport_width,
            "viewport_height": self.viewport_height,
            "user_agent": self.user_agent,
            "headless": self.headless,
            "status": self.status,
            "current_url": self.current_url,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_usage_percent": self.cpu_usage_percent,
            "network_requests": self.network_requests,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class PlaywrightAutomationTask(Base):
    """
    Model for tracking Playwright automation tasks
    """
    __tablename__ = "playwright_automation_tasks"

    # Task Identification
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(255), unique=True, index=True, nullable=False)
    session_id = Column(Integer, ForeignKey("playwright_browser_sessions.id"), nullable=False)
    user_id = Column(String(255), nullable=False)
    
    # Task Configuration
    target_url = Column(String(2000), nullable=False)
    actions = Column(JSON, nullable=False)  # List of browser actions
    selectors = Column(JSON, nullable=True)  # CSS selectors for elements
    viewport_config = Column(JSON, nullable=True)
    
    # Execution Details
    status = Column(String(50), default="pending")  # pending, running, completed, failed, cancelled
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Float, nullable=True)
    
    # Results
    success = Column(Boolean, nullable=True)
    error_message = Column(Text, nullable=True)
    final_url = Column(String(2000), nullable=True)
    captured_data = Column(JSON, nullable=True)  # Extracted data from page
    
    # Artifacts
    screenshot_taken = Column(Boolean, default=False)
    pdf_generated = Column(Boolean, default=False)
    video_recorded = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    session = relationship("PlaywrightBrowserSession", back_populates="automation_tasks")
    artifacts = relationship("PlaywrightArtifact", back_populates="task")
    
    def __repr__(self):
        return f"<PlaywrightAutomationTask(id={self.id}, task_id='{self.task_id}', status='{self.status}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "target_url": self.target_url,
            "status": self.status,
            "success": self.success,
            "error_message": self.error_message,
            "final_url": self.final_url,
            "screenshot_taken": self.screenshot_taken,
            "pdf_generated": self.pdf_generated,
            "video_recorded": self.video_recorded,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": self.duration_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class PlaywrightArtifact(Base):
    """
    Model for managing automation artifacts (screenshots, PDFs, videos)
    """
    __tablename__ = "playwright_artifacts"

    # Artifact Identification
    id = Column(Integer, primary_key=True, index=True)
    artifact_id = Column(String(255), unique=True, index=True, nullable=False)
    task_id = Column(Integer, ForeignKey("playwright_automation_tasks.id"), nullable=True)
    session_id = Column(Integer, ForeignKey("playwright_browser_sessions.id"), nullable=False)
    
    # Artifact Details
    artifact_type = Column(String(50), nullable=False)  # screenshot, pdf, video, har
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(1000), nullable=False)
    object_key = Column(String(1024), nullable=True, index=True)
    object_size = Column(Integer, nullable=True)
    object_content_type = Column(String(255), nullable=True)
    object_etag = Column(String(128), nullable=True)
    storage_provider = Column(String(32), nullable=True)
    storage_bucket = Column(String(128), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=False)
    
    # Storage
    storage_type = Column(String(50), default="local")  # local, s3, encrypted
    encryption_key = Column(String(255), nullable=True)  # For encrypted storage
    checksum = Column(String(64), nullable=True)  # SHA256 checksum
    
    # Metadata
    width = Column(Integer, nullable=True)  # For images/videos
    height = Column(Integer, nullable=True)  # For images/videos
    duration_ms = Column(Integer, nullable=True)  # For videos
    page_url = Column(String(2000), nullable=True)
    capture_timestamp = Column(DateTime, nullable=True)
    
    # Access Control
    is_public = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=True)
    download_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    session = relationship("PlaywrightBrowserSession", back_populates="artifacts")
    task = relationship("PlaywrightAutomationTask", back_populates="artifacts")
    
    def __repr__(self):
        return f"<PlaywrightArtifact(id={self.id}, artifact_id='{self.artifact_id}', type='{self.artifact_type}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "artifact_id": self.artifact_id,
            "task_id": self.task_id,
            "session_id": self.session_id,
            "artifact_type": self.artifact_type,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "file_size_bytes": self.file_size_bytes,
            "mime_type": self.mime_type,
            "storage_type": self.storage_type,
            "width": self.width,
            "height": self.height,
            "duration_ms": self.duration_ms,
            "page_url": self.page_url,
            "is_public": self.is_public,
            "download_count": self.download_count,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "capture_timestamp": self.capture_timestamp.isoformat() if self.capture_timestamp else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class PlaywrightBrowserPool(Base):
    """
    Model for managing browser instance pools
    """
    __tablename__ = "playwright_browser_pools"

    # Pool Identification
    id = Column(Integer, primary_key=True, index=True)
    pool_id = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Pool Configuration
    browser_type = Column(String(50), nullable=False)  # chromium, firefox, webkit
    max_instances = Column(Integer, default=5)
    min_instances = Column(Integer, default=1)
    instance_timeout_minutes = Column(Integer, default=30)
    
    # Resource Limits
    max_memory_mb = Column(Integer, default=512)
    max_cpu_percent = Column(Integer, default=80)
    max_concurrent_tasks = Column(Integer, default=3)
    
    # Lifecycle Management
    idle_timeout_minutes = Column(Integer, default=10)
    health_check_interval_seconds = Column(Integer, default=60)
    auto_scaling_enabled = Column(Boolean, default=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    current_instances = Column(Integer, default=0)
    total_tasks_executed = Column(Integer, default=0)
    total_tasks_failed = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    pool_instances = relationship("PlaywrightBrowserPoolInstance", back_populates="pool")
    
    def __repr__(self):
        return f"<PlaywrightBrowserPool(id={self.id}, pool_id='{self.pool_id}', browser_type='{self.browser_type}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "pool_id": self.pool_id,
            "name": self.name,
            "description": self.description,
            "browser_type": self.browser_type,
            "max_instances": self.max_instances,
            "min_instances": self.min_instances,
            "instance_timeout_minutes": self.instance_timeout_minutes,
            "max_memory_mb": self.max_memory_mb,
            "max_cpu_percent": self.max_cpu_percent,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "idle_timeout_minutes": self.idle_timeout_minutes,
            "health_check_interval_seconds": self.health_check_interval_seconds,
            "auto_scaling_enabled": self.auto_scaling_enabled,
            "is_active": self.is_active,
            "current_instances": self.current_instances,
            "total_tasks_executed": self.total_tasks_executed,
            "total_tasks_failed": self.total_tasks_failed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class PlaywrightBrowserPoolInstance(Base):
    """
    Model for tracking individual browser instances in pools
    """
    __tablename__ = "playwright_browser_pool_instances"

    # Instance Identification
    id = Column(Integer, primary_key=True, index=True)
    instance_id = Column(String(255), unique=True, index=True, nullable=False)
    pool_id = Column(Integer, ForeignKey("playwright_browser_pools.id"), nullable=False)
    session_id = Column(String(255), nullable=True)  # Associated session if active
    
    # Instance State
    status = Column(String(50), default="initializing")  # initializing, ready, busy, idle, terminated
    pid = Column(Integer, nullable=True)  # Process ID
    port = Column(Integer, nullable=True)  # Browser debugging port
    
    # Resource Usage
    memory_usage_mb = Column(Float, default=0.0)
    cpu_usage_percent = Column(Float, default=0.0)
    last_activity = Column(DateTime, default=func.now())
    
    # Lifecycle
    created_at = Column(DateTime, server_default=func.now())
    last_used = Column(DateTime, nullable=True)
    termination_reason = Column(String(255), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    pool = relationship("PlaywrightBrowserPool", back_populates="pool_instances")
    
    def __repr__(self):
        return f"<PlaywrightBrowserPoolInstance(id={self.id}, instance_id='{self.instance_id}', status='{self.status}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "instance_id": self.instance_id,
            "pool_id": self.pool_id,
            "session_id": self.session_id,
            "status": self.status,
            "pid": self.pid,
            "port": self.port,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_usage_percent": self.cpu_usage_percent,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "termination_reason": self.termination_reason,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class PlaywrightSecurityRule(Base):
    """
    Model for security rules and URL validation
    """
    __tablename__ = "playwright_security_rules"

    # Rule Identification
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Rule Configuration
    rule_type = Column(String(50), nullable=False)  # url_whitelist, url_blacklist, domain_restriction
    pattern = Column(String(1000), nullable=False)  # Regex pattern or URL
    is_regex = Column(Boolean, default=False)
    
    # Enforcement
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)  # Higher priority rules are evaluated first
    action = Column(String(50), default="allow")  # allow, deny, prompt
    
    # Metadata
    created_by = Column(String(255), nullable=True)
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<PlaywrightSecurityRule(id={self.id}, rule_id='{self.rule_id}', type='{self.rule_type}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "rule_type": self.rule_type,
            "pattern": self.pattern,
            "is_regex": self.is_regex,
            "is_active": self.is_active,
            "priority": self.priority,
            "action": self.action,
            "created_by": self.created_by,
            "tags": self.tags or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
