"""
Enhanced Playwright Models with Comprehensive Automation Tracking

This module provides enhanced database models for Playwright browser automation including:
- Enhanced session tracking with performance metrics
- Comprehensive tool execution tracking
- Security violation monitoring
- Performance analytics and reporting
- Advanced artifact management
- Security rule management
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, JSON, Float, ForeignKey, 
    Index, UniqueConstraint, CheckConstraint, LargeBinary
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import json
import uuid

from app.models.base import Base


# Enhanced Browser Session Model
class PlaywrightBrowserSession(Base):
    """
    Enhanced model for managing Playwright browser sessions with comprehensive tracking
    """
    __tablename__ = "playwright_browser_sessions"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # User and agent association
    user_id = Column(String(255), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True, index=True)
    
    # Browser configuration
    browser_type = Column(String(50), nullable=False, index=True)  # chromium, firefox, webkit
    viewport_width = Column(Integer, default=1920, nullable=False)
    viewport_height = Column(Integer, default=1080, nullable=False)
    user_agent = Column(String(1000), nullable=True)
    headless = Column(Boolean, default=True, nullable=False)
    
    # Enhanced session state tracking
    status = Column(String(50), default="initializing", nullable=False, index=True)  # initializing, active, idle, terminated, error, suspended
    session_state = Column(JSON, default=dict, nullable=False)  # Detailed session state
    current_url = Column(String(2000), nullable=True)
    current_title = Column(String(500), nullable=True)
    
    # Performance metrics
    memory_usage_mb = Column(Float, default=0.0, nullable=False)
    cpu_usage_percent = Column(Float, default=0.0, nullable=False)
    network_requests = Column(Integer, default=0, nullable=False)
    network_bytes_received = Column(Integer, default=0, nullable=False)
    network_bytes_sent = Column(Integer, default=0, nullable=False)
    
    # Timing and lifecycle
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    last_activity = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True, index=True)
    idle_timeout_minutes = Column(Integer, default=30, nullable=False)
    
    # Security tracking
    security_violations = Column(JSON, default=list, nullable=False)
    allowed_domains = Column(JSON, default=list, nullable=False)
    blocked_domains = Column(JSON, default=list, nullable=False)
    content_security_policy_violations = Column(Integer, default=0, nullable=False)
    
    # Navigation and interaction history
    navigation_history = Column(JSON, default=list, nullable=False)
    interaction_history = Column(JSON, default=list, nullable=False)
    console_logs = Column(JSON, default=list, nullable=False)
    error_logs = Column(JSON, default=list, nullable=False)
    
    # Storage and cookies
    cookies = Column(JSON, nullable=True)
    local_storage = Column(JSON, nullable=True)
    session_storage = Column(JSON, nullable=True)
    indexeddb_data = Column(JSON, nullable=True)
    
    # Performance and optimization
    page_load_times = Column(JSON, default=list, nullable=False)
    resource_load_times = Column(JSON, default=list, nullable=False)
    javascript_errors = Column(JSON, default=list, nullable=False)
    render_times = Column(JSON, default=list, nullable=False)
    
    # Metadata and configuration
    session_metadata = Column(JSON, default=dict, nullable=False)
    custom_headers = Column(JSON, nullable=True)
    proxy_config = Column(JSON, nullable=True)
    extensions_loaded = Column(JSON, default=list, nullable=False)
    
    # Relationships
    agent = relationship("Agent", back_populates="browser_sessions")
    automation_tasks = relationship("PlaywrightAutomationTask", back_populates="session", cascade="all, delete-orphan")
    artifacts = relationship("PlaywrightArtifact", back_populates="session", cascade="all, delete-orphan")
    tool_executions = relationship("PlaywrightToolExecution", back_populates="session", cascade="all, delete-orphan")
    security_events = relationship("PlaywrightSecurityEvent", back_populates="session", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_session_user_agent', 'user_id', 'agent_id'),
        Index('idx_session_status_activity', 'status', 'last_activity'),
        Index('idx_session_browser_type', 'browser_type', 'created_at'),
        Index('idx_session_expires', 'expires_at'),
        CheckConstraint('viewport_width > 0 AND viewport_height > 0', name='check_viewport_positive'),
        CheckConstraint('memory_usage_mb >= 0 AND cpu_usage_percent >= 0', name='check_performance_positive'),
    )
    
    def __repr__(self):
        return f"<PlaywrightBrowserSession(id={self.id}, session_id='{self.session_id}', status='{self.status}', browser='{self.browser_type}')>"
    
    @validates('status')
    def validate_status(self, key, status):
        """Validate session status"""
        valid_statuses = [
            "initializing", "starting", "active", "idle", "terminated", 
            "error", "suspended", "recovering", "maintenance"
        ]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of: {', '.join(valid_statuses)}")
        return status
    
    @validates('browser_type')
    def validate_browser_type(self, key, browser_type):
        """Validate browser type"""
        valid_types = ["chromium", "firefox", "webkit"]
        if browser_type not in valid_types:
            raise ValueError(f"Invalid browser type: {browser_type}. Must be one of: {', '.join(valid_types)}")
        return browser_type
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert model to dictionary with optional sensitive data"""
        data = {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "browser_type": self.browser_type,
            "viewport_width": self.viewport_width,
            "viewport_height": self.viewport_height,
            "headless": self.headless,
            "status": self.status,
            "current_url": self.current_url,
            "current_title": self.current_title,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_usage_percent": self.cpu_usage_percent,
            "network_requests": self.network_requests,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "security_violations_count": len(self.security_violations) if self.security_violations else 0,
            "navigation_count": len(self.navigation_history) if self.navigation_history else 0,
            "interaction_count": len(self.interaction_history) if self.interaction_history else 0,
            "console_log_count": len(self.console_logs) if self.console_logs else 0,
            "task_count": len(self.automation_tasks),
            "artifact_count": len(self.artifacts)
        }
        
        if include_sensitive:
            data.update({
                "user_agent": self.user_agent,
                "cookies": self.cookies,
                "local_storage": self.local_storage,
                "session_storage": self.session_storage,
                "custom_headers": self.custom_headers,
                "proxy_config": self.proxy_config
            })
        
        return data
    
    def add_navigation_record(self, url: str, duration: float, status: Optional[int] = None):
        """Add navigation record to history"""
        if not self.navigation_history:
            self.navigation_history = []
        
        self.navigation_history.append({
            "url": url,
            "timestamp": datetime.utcnow().isoformat(),
            "duration": duration,
            "status": status,
            "sequence": len(self.navigation_history)
        })
        
        # Keep only last 100 navigation records
        if len(self.navigation_history) > 100:
            self.navigation_history = self.navigation_history[-100:]
    
    def add_interaction_record(self, action: str, selector: str, result: str, duration: float = 0):
        """Add interaction record to history"""
        if not self.interaction_history:
            self.interaction_history = []
        
        self.interaction_history.append({
            "action": action,
            "selector": selector,
            "result": result,
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat(),
            "sequence": len(self.interaction_history)
        })
        
        # Keep only last 200 interaction records
        if len(self.interaction_history) > 200:
            self.interaction_history = self.interaction_history[-200:]
    
    def add_console_log(self, message_type: str, message: str, location: Optional[str] = None):
        """Add console log entry"""
        if not self.console_logs:
            self.console_logs = []
        
        self.console_logs.append({
            "type": message_type,
            "message": message,
            "location": location,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep only last 500 console logs
        if len(self.console_logs) > 500:
            self.console_logs = self.console_logs[-500:]
    
    def add_security_violation(self, violation_type: str, details: Dict[str, Any]):
        """Add security violation record"""
        if not self.security_violations:
            self.security_violations = []
        
        self.security_violations.append({
            "type": violation_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep only last 50 security violations
        if len(self.security_violations) > 50:
            self.security_violations = self.security_violations[-50:]
    
    def update_performance_metrics(self, memory_mb: float, cpu_percent: float, 
                                 network_bytes_in: int = 0, network_bytes_out: int = 0):
        """Update performance metrics"""
        self.memory_usage_mb = max(0, memory_mb)
        self.cpu_usage_percent = max(0, min(100, cpu_percent))
        self.network_bytes_received += max(0, network_bytes_in)
        self.network_bytes_sent += max(0, network_bytes_out)
        self.last_activity = datetime.utcnow()
    
    def is_expired(self) -> bool:
        """Check if session has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def get_session_duration(self) -> Optional[timedelta]:
        """Get session duration"""
        if not self.start_time:
            return None
        end_time = self.end_time or datetime.utcnow()
        return end_time - self.start_time


# Enhanced Tool Execution Model
class PlaywrightToolExecution(Base):
    """
    Model for tracking individual tool executions with comprehensive metadata
    """
    __tablename__ = "playwright_tool_executions"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String(255), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Session and user association
    session_id = Column(Integer, ForeignKey("playwright_browser_sessions.id"), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True, index=True)
    
    # Tool execution details
    tool_name = Column(String(100), nullable=False, index=True)
    tool_category = Column(String(50), nullable=False, index=True)
    tool_version = Column(String(20), default="1.0.0", nullable=False)
    
    # Execution status and timing
    status = Column(String(50), default="pending", nullable=False, index=True)  # pending, running, completed, failed, cancelled, timeout
    started_at = Column(DateTime, nullable=True, index=True)
    completed_at = Column(DateTime, nullable=True, index=True)
    execution_time_seconds = Column(Float, nullable=True)
    
    # Input and output data
    input_parameters = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    error_code = Column(String(100), nullable=True)
    error_details = Column(JSON, nullable=True)
    
    # Performance metrics
    timeout_used = Column(Integer, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    validation_level = Column(String(20), default="moderate", nullable=False)
    
    # Console and debugging
    console_logs = Column(JSON, default=list, nullable=False)
    screenshot_base64 = Column(Text, nullable=True)  # Legacy fallback during object-storage transition.
    object_key = Column(String(1024), nullable=True, index=True)
    object_size = Column(Integer, nullable=True)
    object_content_type = Column(String(255), nullable=True)
    object_etag = Column(String(128), nullable=True)
    storage_provider = Column(String(32), nullable=True)
    storage_bucket = Column(String(128), nullable=True)
    trace_data = Column(JSON, nullable=True)  # Execution trace
    
    # Validation and security
    input_validation_passed = Column(Boolean, default=True, nullable=False)
    security_checks_performed = Column(JSON, default=list, nullable=False)
    security_violations = Column(JSON, default=list, nullable=False)
    
    # Context and metadata
    execution_context = Column(JSON, default=dict, nullable=False)
    user_agent = Column(String(1000), nullable=True)
    browser_info = Column(JSON, nullable=True)
    environment_info = Column(JSON, nullable=True)
    
    # Priority and scheduling
    priority = Column(Integer, default=5, nullable=False)  # 1-10, higher is more important
    scheduled_at = Column(DateTime, nullable=True)
    queued_at = Column(DateTime, nullable=True)
    
    # Relationships
    session = relationship("PlaywrightBrowserSession", back_populates="tool_executions")
    agent = relationship("Agent", back_populates="tool_executions")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_execution_session_tool', 'session_id', 'tool_name'),
        Index('idx_execution_user_status', 'user_id', 'status'),
        Index('idx_execution_timing', 'started_at', 'completed_at'),
        Index('idx_execution_priority', 'priority', 'scheduled_at'),
        CheckConstraint('priority >= 1 AND priority <= 10', name='check_priority_range'),
        CheckConstraint('retry_count >= 0', name='check_retry_non_negative'),
    )
    
    def __repr__(self):
        return f"<PlaywrightToolExecution(id={self.id}, tool='{self.tool_name}', status='{self.status}', execution_id='{self.execution_id}')>"
    
    @validates('status')
    def validate_status(self, key, status):
        """Validate execution status"""
        valid_statuses = ["pending", "running", "completed", "failed", "cancelled", "timeout"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of: {', '.join(valid_statuses)}")
        return status
    
    @validates('priority')
    def validate_priority(self, key, priority):
        """Validate priority range"""
        if priority < 1 or priority > 10:
            raise ValueError("Priority must be between 1 and 10")
        return priority
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert model to dictionary"""
        data = {
            "id": self.id,
            "execution_id": self.execution_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "tool_name": self.tool_name,
            "tool_category": self.tool_category,
            "status": self.status,
            "execution_time_seconds": self.execution_time_seconds,
            "retry_count": self.retry_count,
            "input_validation_passed": self.input_validation_passed,
            "security_violations_count": len(self.security_violations) if self.security_violations else 0,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if hasattr(self, 'created_at') and self.created_at else None
        }
        
        if include_sensitive:
            data.update({
                "input_parameters": self.input_parameters,
                "output_data": self.output_data,
                "error_message": self.error_message,
                "error_details": self.error_details,
                "console_logs": self.console_logs,
                "screenshot_base64": self.screenshot_base64,
                "trace_data": self.trace_data,
                "user_agent": self.user_agent,
                "browser_info": self.browser_info,
                "environment_info": self.environment_info
            })
        
        return data
    
    def mark_started(self):
        """Mark execution as started"""
        self.started_at = datetime.utcnow()
        self.status = "running"
    
    def mark_completed(self, output_data: Dict[str, Any] = None):
        """Mark execution as completed"""
        self.completed_at = datetime.utcnow()
        self.status = "completed"
        if self.started_at:
            self.execution_time_seconds = (self.completed_at - self.started_at).total_seconds()
        if output_data:
            self.output_data = output_data
    
    def mark_failed(self, error_message: str, error_code: str = None, error_details: Dict[str, Any] = None):
        """Mark execution as failed"""
        self.completed_at = datetime.utcnow()
        self.status = "failed"
        self.error_message = error_message
        self.error_code = error_code
        self.error_details = error_details
        if self.started_at:
            self.execution_time_seconds = (self.completed_at - self.started_at).total_seconds()
    
    def mark_timeout(self, timeout_duration: int):
        """Mark execution as timed out"""
        self.completed_at = datetime.utcnow()
        self.status = "timeout"
        self.timeout_used = timeout_duration
        if self.started_at:
            self.execution_time_seconds = (self.completed_at - self.started_at).total_seconds()
    
    def add_console_log(self, message_type: str, message: str, details: Dict[str, Any] = None):
        """Add console log entry"""
        if not self.console_logs:
            self.console_logs = []
        
        self.console_logs.append({
            "type": message_type,
            "message": message,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat(),
            "sequence": len(self.console_logs)
        })
        
        # Keep only last 100 console logs
        if len(self.console_logs) > 100:
            self.console_logs = self.console_logs[-100:]
    
    def add_security_violation(self, violation_type: str, details: Dict[str, Any]):
        """Add security violation record"""
        if not self.security_violations:
            self.security_violations = []
        
        self.security_violations.append({
            "type": violation_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def increment_retry(self):
        """Increment retry count"""
        self.retry_count += 1
    
    def get_total_duration(self) -> Optional[float]:
        """Get total execution duration"""
        if not self.started_at:
            return None
        end_time = self.completed_at or datetime.utcnow()
        return (end_time - self.started_at).total_seconds()


# Enhanced Security Event Model
class PlaywrightSecurityEvent(Base):
    """
    Model for tracking security events and violations
    """
    __tablename__ = "playwright_security_events"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(255), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Session association
    session_id = Column(Integer, ForeignKey("playwright_browser_sessions.id"), nullable=True, index=True)
    execution_id = Column(Integer, ForeignKey("playwright_tool_executions.id"), nullable=True, index=True)
    
    # Event details
    event_type = Column(String(100), nullable=False, index=True)  # url_blocked, script_injection, xss_attempt, etc.
    severity = Column(String(20), default="medium", nullable=False, index=True)  # low, medium, high, critical
    description = Column(Text, nullable=False)
    
    # Source information
    source_url = Column(String(2000), nullable=True)
    target_url = Column(String(2000), nullable=True)
    source_ip = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(1000), nullable=True)
    
    # Event data
    event_data = Column(JSON, nullable=True)
    blocked_content = Column(Text, nullable=True)
    remediation_action = Column(String(100), nullable=True)
    
    # Tracking
    detected_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Relationships
    session = relationship("PlaywrightBrowserSession", back_populates="security_events")
    execution = relationship("PlaywrightToolExecution", back_populates="security_events")
    
    # Indexes for performance and security monitoring
    __table_args__ = (
        Index('idx_security_event_type_severity', 'event_type', 'severity'),
        Index('idx_security_event_session', 'session_id', 'detected_at'),
        Index('idx_security_event_timing', 'detected_at', 'resolved_at'),
        CheckConstraint("severity IN ('low', 'medium', 'high', 'critical')", name='check_severity_levels'),
    )
    
    def __repr__(self):
        return f"<PlaywrightSecurityEvent(id={self.id}, type='{self.event_type}', severity='{self.severity}', event_id='{self.event_id}')>"
    
    @validates('severity')
    def validate_severity(self, key, severity):
        """Validate severity level"""
        valid_severities = ["low", "medium", "high", "critical"]
        if severity not in valid_severities:
            raise ValueError(f"Invalid severity: {severity}. Must be one of: {', '.join(valid_severities)}")
        return severity
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "event_id": self.event_id,
            "session_id": self.session_id,
            "execution_id": self.execution_id,
            "event_type": self.event_type,
            "severity": self.severity,
            "description": self.description,
            "source_url": self.source_url,
            "target_url": self.target_url,
            "source_ip": self.source_ip,
            "event_data": self.event_data,
            "remediation_action": self.remediation_action,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolution_notes": self.resolution_notes
        }
    
    def resolve(self, resolution_notes: str = None, remediation_action: str = None):
        """Mark security event as resolved"""
        self.resolved_at = datetime.utcnow()
        if resolution_notes:
            self.resolution_notes = resolution_notes
        if remediation_action:
            self.remediation_action = remediation_action
    
    def is_resolved(self) -> bool:
        """Check if security event is resolved"""
        return self.resolved_at is not None
    
    def get_age(self) -> timedelta:
        """Get age of security event"""
        return datetime.utcnow() - self.detected_at


# Enhanced Automation Task Model
class PlaywrightAutomationTask(Base):
    """
    Enhanced model for tracking Playwright automation tasks with comprehensive metadata
    """
    __tablename__ = "playwright_automation_tasks"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(255), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    session_id = Column(Integer, ForeignKey("playwright_browser_sessions.id"), nullable=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True, index=True)
    
    # Task configuration
    task_name = Column(String(255), nullable=False)
    task_type = Column(String(50), nullable=False, index=True)  # scraping, automation, testing, monitoring
    target_url = Column(String(2000), nullable=False)
    task_steps = Column(JSON, nullable=False)  # Detailed task steps
    browser_config = Column(JSON, nullable=True)
    
    # Enhanced execution tracking
    status = Column(String(50), default="pending", nullable=False, index=True)
    progress = Column(Integer, default=0, nullable=False)  # 0-100
    current_step = Column(Integer, default=0, nullable=False)
    total_steps = Column(Integer, default=0, nullable=False)
    
    # Timing
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    started_at = Column(DateTime, nullable=True, index=True)
    completed_at = Column(DateTime, nullable=True, index=True)
    scheduled_at = Column(DateTime, nullable=True, index=True)
    
    # Results and data
    result_data = Column(JSON, nullable=True)
    extracted_data = Column(JSON, nullable=True)
    success_indicators = Column(JSON, default=list, nullable=False)
    failure_reasons = Column(JSON, default=list, nullable=False)
    
    # Performance metrics
    execution_time_seconds = Column(Float, nullable=True)
    timeout_seconds = Column(Integer, default=300, nullable=False)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    error_code = Column(String(100), nullable=True)
    error_details = Column(JSON, nullable=True)
    stack_trace = Column(Text, nullable=True)
    
    # Quality and validation
    validation_rules = Column(JSON, nullable=True)
    quality_score = Column(Float, nullable=True)  # 0.0-1.0
    data_quality_checks = Column(JSON, default=list, nullable=False)
    
    # Scheduling and priority
    priority = Column(Integer, default=5, nullable=False)  # 1-10
    recurrence_pattern = Column(String(100), nullable=True)  # cron-like pattern
    next_execution = Column(DateTime, nullable=True, index=True)
    
    # Relationships
    session = relationship("PlaywrightBrowserSession", back_populates="automation_tasks")
    agent = relationship("Agent", back_populates="automation_tasks")
    artifacts = relationship("PlaywrightArtifact", back_populates="task", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_task_user_status', 'user_id', 'status'),
        Index('idx_task_agent_status', 'agent_id', 'status'),
        Index('idx_task_timing', 'scheduled_at', 'started_at'),
        Index('idx_task_priority', 'priority', 'next_execution'),
        CheckConstraint('progress >= 0 AND progress <= 100', name='check_progress_range'),
        CheckConstraint('priority >= 1 AND priority <= 10', name='check_task_priority_range'),
        CheckConstraint('retry_count >= 0 AND retry_count <= max_retries', name='check_retry_valid'),
    )
    
    def __repr__(self):
        return f"<PlaywrightAutomationTask(id={self.id}, task_id='{self.task_id}', name='{self.task_name}', status='{self.status}')>"
    
    @validates('status')
    def validate_status(self, key, status):
        """Validate task status"""
        valid_statuses = [
            "pending", "queued", "running", "completed", "failed", 
            "cancelled", "timeout", "retrying", "paused"
        ]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of: {', '.join(valid_statuses)}")
        return status
    
    @validates('task_type')
    def validate_task_type(self, key, task_type):
        """Validate task type"""
        valid_types = ["scraping", "automation", "testing", "monitoring", "extraction", "interaction"]
        if task_type not in valid_types:
            raise ValueError(f"Invalid task type: {task_type}. Must be one of: {', '.join(valid_types)}")
        return task_type
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "task_name": self.task_name,
            "task_type": self.task_type,
            "target_url": self.target_url,
            "status": self.status,
            "progress": self.progress,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "execution_time_seconds": self.execution_time_seconds,
            "retry_count": self.retry_count,
            "quality_score": self.quality_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "next_execution": self.next_execution.isoformat() if self.next_execution else None,
            "artifact_count": len(self.artifacts),
            "has_errors": self.error_message is not None
        }
    
    def mark_started(self):
        """Mark task as started"""
        self.started_at = datetime.utcnow()
        self.status = "running"
        self.current_step = 1
    
    def mark_completed(self, result_data: Dict[str, Any] = None, extracted_data: Dict[str, Any] = None):
        """Mark task as completed"""
        self.completed_at = datetime.utcnow()
        self.status = "completed"
        self.progress = 100
        if self.started_at:
            self.execution_time_seconds = (self.completed_at - self.started_at).total_seconds()
        if result_data:
            self.result_data = result_data
        if extracted_data:
            self.extracted_data = extracted_data
    
    def mark_failed(self, error_message: str, error_code: str = None, error_details: Dict[str, Any] = None):
        """Mark task as failed"""
        self.completed_at = datetime.utcnow()
        self.status = "failed"
        self.error_message = error_message
        self.error_code = error_code
        self.error_details = error_details
        if self.started_at:
            self.execution_time_seconds = (self.completed_at - self.started_at).total_seconds()
    
    def update_progress(self, step: int, progress: int):
        """Update task progress"""
        self.current_step = max(0, step)
        self.progress = max(0, min(100, progress))
        if self.current_step >= self.total_steps and self.progress < 100:
            self.progress = 100
    
    def add_success_indicator(self, indicator: str, details: Dict[str, Any] = None):
        """Add success indicator"""
        if not self.success_indicators:
            self.success_indicators = []
        
        self.success_indicators.append({
            "indicator": indicator,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def add_failure_reason(self, reason: str, details: Dict[str, Any] = None):
        """Add failure reason"""
        if not self.failure_reasons:
            self.failure_reasons = []
        
        self.failure_reasons.append({
            "reason": reason,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def increment_retry(self):
        """Increment retry count"""
        self.retry_count += 1
    
    def can_retry(self) -> bool:
        """Check if task can be retried"""
        return self.retry_count < self.max_retries
    
    def get_duration(self) -> Optional[timedelta]:
        """Get task duration"""
        if not self.started_at:
            return None
        end_time = self.completed_at or datetime.utcnow()
        return end_time - self.started_at
    
    def is_overdue(self) -> bool:
        """Check if scheduled task is overdue"""
        if not self.next_execution:
            return False
        return datetime.utcnow() > self.next_execution


# Enhanced Artifact Model
class PlaywrightArtifact(Base):
    """
    Enhanced model for managing automation artifacts with comprehensive metadata
    """
    __tablename__ = "playwright_artifacts"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    artifact_id = Column(String(255), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    task_id = Column(Integer, ForeignKey("playwright_automation_tasks.id"), nullable=True, index=True)
    session_id = Column(Integer, ForeignKey("playwright_browser_sessions.id"), nullable=True, index=True)
    execution_id = Column(Integer, ForeignKey("playwright_tool_executions.id"), nullable=True, index=True)
    
    # Artifact details
    artifact_type = Column(String(50), nullable=False, index=True)  # screenshot, pdf, video, har, trace
    artifact_name = Column(String(255), nullable=False)
    file_name = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    object_key = Column(String(1024), nullable=True, index=True)
    object_size = Column(Integer, nullable=True)
    object_content_type = Column(String(255), nullable=True)
    object_etag = Column(String(128), nullable=True)
    storage_provider = Column(String(32), nullable=True)
    storage_bucket = Column(String(128), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    
    # Storage and access
    storage_type = Column(String(50), default="local", nullable=False)  # local, s3, encrypted, compressed
    storage_location = Column(String(1000), nullable=True)  # S3 URL, etc.
    encryption_key = Column(String(255), nullable=True)
    checksum = Column(String(64), nullable=True)  # SHA256
    compression_ratio = Column(Float, nullable=True)
    
    # Content metadata
    mime_type = Column(String(100), nullable=False)
    encoding = Column(String(50), nullable=True)
    width = Column(Integer, nullable=True)  # For images/videos
    height = Column(Integer, nullable=True)  # For images/videos
    duration_ms = Column(Integer, nullable=True)  # For videos
    page_count = Column(Integer, nullable=True)  # For PDFs
    
    # Source information
    source_url = Column(String(2000), nullable=True)
    source_title = Column(String(500), nullable=True)
    capture_timestamp = Column(DateTime, nullable=True)
    user_agent = Column(String(1000), nullable=True)
    viewport_size = Column(JSON, nullable=True)
    
    # Content analysis
    content_hash = Column(String(64), nullable=True)  # Hash of content
    text_content = Column(Text, nullable=True)  # Extracted text
    metadata_extracted = Column(JSON, default=dict, nullable=False)
    
    # Quality and validation
    quality_score = Column(Float, nullable=True)  # 0.0-1.0
    validation_results = Column(JSON, default=list, nullable=False)
    processing_time_ms = Column(Integer, nullable=True)
    
    # Access control
    is_public = Column(Boolean, default=False, nullable=False)
    access_level = Column(String(50), default="private", nullable=False)  # private, restricted, public
    download_count = Column(Integer, default=0, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    
    # Lifecycle management
    expires_at = Column(DateTime, nullable=True, index=True)
    auto_delete = Column(Boolean, default=False, nullable=False)
    retention_days = Column(Integer, default=30, nullable=False)
    
    # Relationships
    task = relationship("PlaywrightAutomationTask", back_populates="artifacts")
    session = relationship("PlaywrightBrowserSession", back_populates="artifacts")
    execution = relationship("PlaywrightToolExecution", back_populates="artifact")
    
    # Indexes
    __table_args__ = (
        Index('idx_artifact_task_session', 'task_id', 'session_id'),
        Index('idx_artifact_type_created', 'artifact_type', 'created_at'),
        Index('idx_artifact_expires', 'expires_at'),
        Index('idx_artifact_access', 'access_level', 'is_public'),
        CheckConstraint('file_size_bytes >= 0', name='check_file_size_positive'),
        CheckConstraint('download_count >= 0 AND view_count >= 0', name='check_counts_non_negative'),
    )
    
    def __repr__(self):
        return f"<PlaywrightArtifact(id={self.id}, artifact_id='{self.artifact_id}', type='{self.artifact_type}', name='{self.artifact_name}')>"
    
    @validates('artifact_type')
    def validate_artifact_type(self, key, artifact_type):
        """Validate artifact type"""
        valid_types = ["screenshot", "pdf", "video", "har", "trace", "json", "html", "csv", "log", "report"]
        if artifact_type not in valid_types:
            raise ValueError(f"Invalid artifact type: {artifact_type}. Must be one of: {', '.join(valid_types)}")
        return artifact_type
    
    @validates('access_level')
    def validate_access_level(self, key, access_level):
        """Validate access level"""
        valid_levels = ["private", "restricted", "public"]
        if access_level not in valid_levels:
            raise ValueError(f"Invalid access level: {access_level}. Must be one of: {', '.join(valid_levels)}")
        return access_level
    
    def to_dict(self, include_content: bool = False) -> Dict[str, Any]:
        """Convert model to dictionary"""
        data = {
            "id": self.id,
            "artifact_id": self.artifact_id,
            "task_id": self.task_id,
            "session_id": self.session_id,
            "execution_id": self.execution_id,
            "artifact_type": self.artifact_type,
            "artifact_name": self.artifact_name,
            "file_name": self.file_name,
            "file_size_bytes": self.file_size_bytes,
            "storage_type": self.storage_type,
            "mime_type": self.mime_type,
            "quality_score": self.quality_score,
            "is_public": self.is_public,
            "access_level": self.access_level,
            "download_count": self.download_count,
            "view_count": self.view_count,
            "created_at": self.created_at.isoformat() if hasattr(self, 'created_at') and self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "capture_timestamp": self.capture_timestamp.isoformat() if self.capture_timestamp else None
        }
        
        if include_content:
            data.update({
                "text_content": self.text_content,
                "metadata_extracted": self.metadata_extracted,
                "validation_results": self.validation_results
            })
        
        return data
    
    def increment_download(self):
        """Increment download count"""
        self.download_count += 1
    
    def increment_view(self):
        """Increment view count"""
        self.view_count += 1
    
    def is_expired(self) -> bool:
        """Check if artifact has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def should_auto_delete(self) -> bool:
        """Check if artifact should be auto-deleted"""
        return self.auto_delete and self.is_expired()
    
    def get_age(self) -> timedelta:
        """Get artifact age"""
        created_at = getattr(self, 'created_at', None)
        if not created_at:
            return timedelta(0)
        return datetime.utcnow() - created_at


# Security Rule Model
class PlaywrightSecurityRule(Base):
    """
    Enhanced model for security rules and URL validation
    """
    __tablename__ = "playwright_security_rules"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(String(255), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Rule configuration
    rule_type = Column(String(50), nullable=False, index=True)  # url_whitelist, url_blacklist, domain_restriction, content_filter
    pattern = Column(String(1000), nullable=False)
    pattern_type = Column(String(20), default="regex", nullable=False)  # regex, wildcard, exact
    is_regex = Column(Boolean, default=False, nullable=False)
    
    # Enforcement
    is_active = Column(Boolean, default=True, nullable=False)
    priority = Column(Integer, default=1, nullable=False, index=True)  # Higher priority rules are evaluated first
    action = Column(String(50), default="allow", nullable=False)  # allow, deny, prompt, log
    severity = Column(String(20), default="medium", nullable=False)
    
    # Rule scope
    applies_to = Column(String(50), default="all", nullable=False)  # all, sessions, tasks, tools
    target_tools = Column(JSON, default=list, nullable=False)
    target_browsers = Column(JSON, default=list, nullable=False)
    
    # Metadata
    created_by = Column(String(255), nullable=True)
    tags = Column(JSON, default=list, nullable=False)
    rule_metadata = Column(JSON, default=dict, nullable=False)
    
    # Statistics
    hit_count = Column(Integer, default=0, nullable=False)
    last_hit = Column(DateTime, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_security_rule_priority_active', 'priority', 'is_active'),
        Index('idx_security_rule_type_action', 'rule_type', 'action'),
        Index('idx_security_rule_applies', 'applies_to', 'is_active'),
        CheckConstraint("severity IN ('low', 'medium', 'high', 'critical')", name='check_rule_severity'),
        CheckConstraint("action IN ('allow', 'deny', 'prompt', 'log')", name='check_rule_action'),
        CheckConstraint("pattern_type IN ('regex', 'wildcard', 'exact')", name='check_pattern_type'),
    )
    
    def __repr__(self):
        return f"<PlaywrightSecurityRule(id={self.id}, rule_id='{self.rule_id}', type='{self.rule_type}', action='{self.action}')>"
    
    @validates('rule_type')
    def validate_rule_type(self, key, rule_type):
        """Validate rule type"""
        valid_types = ["url_whitelist", "url_blacklist", "domain_restriction", "content_filter", "script_blocking"]
        if rule_type not in valid_types:
            raise ValueError(f"Invalid rule type: {rule_type}. Must be one of: {', '.join(valid_types)}")
        return rule_type
    
    @validates('action')
    def validate_action(self, key, action):
        """Validate action"""
        valid_actions = ["allow", "deny", "prompt", "log"]
        if action not in valid_actions:
            raise ValueError(f"Invalid action: {action}. Must be one of: {', '.join(valid_actions)}")
        return action
    
    @validates('severity')
    def validate_severity(self, key, severity):
        """Validate severity"""
        valid_severities = ["low", "medium", "high", "critical"]
        if severity not in valid_severities:
            raise ValueError(f"Invalid severity: {severity}. Must be one of: {', '.join(valid_severities)}")
        return severity
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "rule_type": self.rule_type,
            "pattern": self.pattern,
            "pattern_type": self.pattern_type,
            "is_active": self.is_active,
            "priority": self.priority,
            "action": self.action,
            "severity": self.severity,
            "applies_to": self.applies_to,
            "target_tools": self.target_tools,
            "target_browsers": self.target_browsers,
            "hit_count": self.hit_count,
            "last_hit": self.last_hit.isoformat() if self.last_hit else None,
            "created_at": self.created_at.isoformat() if hasattr(self, 'created_at') and self.created_at else None
        }
    
    def increment_hit(self):
        """Increment hit count"""
        self.hit_count += 1
        self.last_hit = datetime.utcnow()
    
    def matches(self, input_value: str) -> bool:
        """Check if rule matches input value"""
        if not self.is_active:
            return False
        
        if self.pattern_type == "exact":
            return input_value == self.pattern
        elif self.pattern_type == "wildcard":
            # Simple wildcard matching
            import fnmatch
            return fnmatch.fnmatch(input_value, self.pattern)
        elif self.pattern_type == "regex":
            try:
                import re
                return bool(re.search(self.pattern, input_value))
            except re.error:
                return False
        
        return False


# Analytics and Performance Model
class PlaywrightAnalytics(Base):
    """
    Model for storing analytics and performance data
    """
    __tablename__ = "playwright_analytics"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(String(255), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Metric details
    metric_name = Column(String(100), nullable=False, index=True)
    metric_category = Column(String(50), nullable=False, index=True)  # performance, usage, security, quality
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20), nullable=True)  # ms, bytes, count, percentage
    
    # Context
    session_id = Column(Integer, ForeignKey("playwright_browser_sessions.id"), nullable=True, index=True)
    tool_name = Column(String(100), nullable=True, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True, index=True)
    
    # Dimensions for aggregation
    dimensions = Column(JSON, default=dict, nullable=False)
    tags = Column(JSON, default=list, nullable=False)
    
    # Timestamp
    timestamp = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_analytics_metric_timestamp', 'metric_name', 'timestamp'),
        Index('idx_analytics_category_timestamp', 'metric_category', 'timestamp'),
        Index('idx_analytics_session_tool', 'session_id', 'tool_name'),
    )
    
    def __repr__(self):
        return f"<PlaywrightAnalytics(id={self.id}, metric='{self.metric_name}', value={self.metric_value}, category='{self.metric_category}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "metric_id": self.metric_id,
            "metric_name": self.metric_name,
            "metric_category": self.metric_category,
            "metric_value": self.metric_value,
            "metric_unit": self.metric_unit,
            "session_id": self.session_id,
            "tool_name": self.tool_name,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "dimensions": self.dimensions,
            "tags": self.tags,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


# Add relationships to existing models if they exist
try:
    from app.models.agent import Agent
    
    # Add relationships to Agent model if it exists
    if hasattr(Agent, 'browser_sessions'):
        Agent.browser_sessions = relationship("PlaywrightBrowserSession", back_populates="agent")
    else:
        Agent.browser_sessions = relationship("PlaywrightBrowserSession", back_populates="agent")
    
    if hasattr(Agent, 'automation_tasks'):
        Agent.automation_tasks = relationship("PlaywrightAutomationTask", back_populates="agent")
    else:
        Agent.automation_tasks = relationship("PlaywrightAutomationTask", back_populates="agent")
    
    if hasattr(Agent, 'tool_executions'):
        Agent.tool_executions = relationship("PlaywrightToolExecution", back_populates="agent")
    else:
        Agent.tool_executions = relationship("PlaywrightToolExecution", back_populates="agent")

except ImportError:
    # Agent model doesn't exist yet, relationships will be added when it does
    pass


# Export all models
__all__ = [
    "PlaywrightBrowserSession",
    "PlaywrightToolExecution", 
    "PlaywrightSecurityEvent",
    "PlaywrightAutomationTask",
    "PlaywrightArtifact",
    "PlaywrightSecurityRule",
    "PlaywrightAnalytics"
]
