# Playwright MCP Server Architecture Design

## Executive Summary

This document presents a comprehensive technical specification for integrating Playwright browser automation capabilities into the existing Chronos AI MCP (Multi-Protocol Connectivity) infrastructure. The design offers **two implementation approaches** to meet different organizational needs:

### **Approach 1: Quick Start - External MCP Server**
**Timeline: 1-2 days**
- **Rapid Deployment**: Leverage the official `@playwright/mcp` server for immediate capabilities
- **Minimal Integration**: Simple configuration with existing MCP infrastructure
- **Built-in Features**: Headless browsing, vision capabilities, and automatic updates
- **Lower Maintenance**: External service with vendor-managed updates and features

### **Approach 2: Production - Internal Implementation**
**Timeline: 6-8 weeks**
- **Full Control**: Custom implementation with enterprise-grade security and monitoring
- **Advanced Features**: Intelligent browser pooling, secure artifact management, batch operations
- **Deep Integration**: Seamless integration with existing Chronos AI architecture patterns
- **Customization**: Tailored security policies, resource management, and performance optimization

**Key Benefits:**
- **Flexible Implementation**: Choose between rapid deployment or full customization
- **Seamless Integration**: Both approaches integrate with existing MCP infrastructure
- **Production-Ready**: Enterprise-grade security, monitoring, and resource management
- **Scalable Architecture**: Support for horizontal scaling with intelligent resource management
- **Comprehensive Security**: URL validation, script sanitization, and encrypted artifact storage

## 1. System Architecture

### 1.1 Integration Overview

The Playwright MCP server can be integrated into the existing Chronos AI architecture through two approaches:

#### **Option 1: External MCP Server Integration (Recommended for Quick Start)**

For immediate deployment, you can use the official Playwright MCP server as an external service:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--headless",
        "--vision"
      ]
    }
  }
}
```

This configuration provides:
- **Quick Deployment**: Immediate access to Playwright automation capabilities
- **External Isolation**: Runs as separate service with minimal integration complexity
- **Built-in Features**: Includes headless mode and vision capabilities
- **Easy Updates**: Automatic updates via npm package management

#### **Option 2: Internal Implementation (Production Enterprise)**

For production environments requiring full control, security, and customization:

**Full Internal Implementation**: Build upon the sophisticated dual-layer MCP architecture already in place, extending it with production-ready browser automation features including intelligent browser pooling, secure artifact management, advanced session management, and comprehensive monitoring.

The Playwright MCP server integrates into the existing Chronos AI architecture through the following components:

### 1.2 Approach Comparison

| Aspect | External MCP Server | Internal Implementation |
|--------|-------------------|----------------------|
| **Deployment Time** | 1-2 days | 6-8 weeks |
| **Development Effort** | Minimal | Extensive |
| **Maintenance** | Low (vendor-managed) | High (self-managed) |
| **Customization** | Limited | Unlimited |
| **Security Control** | Standard | Enterprise-grade |
| **Resource Management** | Basic | Advanced pooling & optimization |
| **Artifact Storage** | Default | Encrypted, policy-driven |
| **Monitoring** | Basic metrics | Comprehensive, custom dashboards |
| **Scalability** | Good | Excellent with auto-scaling |
| **Integration Depth** | Surface-level | Deep integration |

#### **When to Choose External MCP Server:**
- **Rapid prototyping** and proof-of-concept development
- **Limited development resources** or tight deadlines
- **Standard security requirements** and moderate compliance needs
- **Basic browser automation** without complex resource management
- **Teams unfamiliar** with browser automation internals

#### **When to Choose Internal Implementation:**
- **Enterprise environments** with strict security and compliance requirements
- **High-volume automation** requiring resource optimization
- **Custom security policies** and advanced threat modeling
- **Deep integration** with existing Chronos AI patterns and workflows
- **Long-term scalability** and performance optimization needs
- **Custom monitoring** and alerting requirements

### 1.3 Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Chronos AI Application                      │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (React/TypeScript)  │  Backend API (FastAPI)          │
│  ┌─────────────────────────┐   │  ┌─────────────────────────────┐ │
│  │ Playwright Operations   │   │  │ Enhanced MCP Manager        │ │
│  │ • Session Management    │   │  │ • Load Balancing            │ │
│  │ • Browser Control       │   │  │ • Circuit Breaker           │ │
│  │ • Artifact Viewing      │   │  │ • Rate Limiting             │ │
│  └─────────────────────────┘   │  └─────────────────────────────┘ │
│                                │                                 │
│  ┌─────────────────────────┐   │  ┌─────────────────────────────┐ │
│  │ Playwright API Layer    │◄──┼──►│ Advanced MCP Client         │ │
│  │ • REST Endpoints        │   │  │ • Connection Pooling        │ │
│  │ • WebSocket Support     │   │  │ • Retry Logic               │ │
│  │ • Batch Operations      │   │  │ • Request Caching           │ │
│  └─────────────────────────┘   │  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Playwright Browser Automation Layer                │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌───────────┐ │
│  │ Browser Pool        │  │ Session Manager     │  │ Security  │ │
│  │ • Instance Pooling  │  │ • Lifecycle Mgmt    │  │ • URL     │ │
│  │ • Resource Limits   │  │ • Auto-cleanup      │  │   Validation│ │
│  │ • Load Balancing    │  │ • State Persistence │  │ • Script  │ │
│  └─────────────────────┘  └─────────────────────┘  │   Sanitization│ │
│                                                  │  └───────────┘ │
│  ┌─────────────────────┐  ┌─────────────────────┐                │
│  │ Artifact Manager    │  │ Playwright Engine   │                │
│  │ • Screenshot Storage│  │ • Multi-browser     │                │
│  │ • PDF Generation    │  │ • JavaScript Exec   │                │
│  │ • Video Recording   │  │ • Network Intercept │                │
│  │ • Encryption        │  │ • Error Handling    │                │
│  └─────────────────────┘  └─────────────────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Architecture

#### Core Integration Points

1. **Enhanced MCP Manager Extension**
   - New `PLAYWRIGHT_AUTOMATION` operation type
   - Browser session orchestration
   - Pool management integration
   - Security validation

2. **Advanced MCP Client Enhancement**
   - Playwright-specific operation methods
   - Browser lifecycle management
   - Artifact handling integration

3. **Database Schema Extensions**
   - Playwright session management
   - Browser instance tracking
   - Artifact storage and metadata

4. **API Layer Extensions**
   - Playwright-specific endpoints
   - WebSocket real-time communication
   - Batch operation support

## 2. Database Schema Extensions

### 2.1 Playwright-Specific Models

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Float, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, Dict, Any
import json

from app.models.base import BaseModel


class PlaywrightBrowserSession(BaseModel):
    """
    Model for managing Playwright browser sessions
    """
    __tablename__ = "playwright_browser_sessions"

    # Session Identification
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
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    automation_tasks = relationship("PlaywrightAutomationTask", back_populates="session")
    artifacts = relationship("PlaywrightArtifact", back_populates="session")
    
    def __repr__(self):
        return f"<PlaywrightBrowserSession(id={self.id}, session_id='{self.session_id}', status='{self.status}')>"


class PlaywrightAutomationTask(BaseModel):
    """
    Model for tracking Playwright automation tasks
    """
    __tablename__ = "playwright_automation_tasks"

    # Task Identification
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
    
    # Relationships
    session = relationship("PlaywrightBrowserSession", back_populates="automation_tasks")
    artifacts = relationship("PlaywrightArtifact", back_populates="task")
    
    def __repr__(self):
        return f"<PlaywrightAutomationTask(id={self.id}, task_id='{self.task_id}', status='{self.status}')>"


class PlaywrightArtifact(BaseModel):
    """
    Model for managing automation artifacts (screenshots, PDFs, videos)
    """
    __tablename__ = "playwright_artifacts"

    # Artifact Identification
    artifact_id = Column(String(255), unique=True, index=True, nullable=False)
    task_id = Column(Integer, ForeignKey("playwright_automation_tasks.id"), nullable=True)
    session_id = Column(Integer, ForeignKey("playwright_browser_sessions.id"), nullable=False)
    
    # Artifact Details
    artifact_type = Column(String(50), nullable=False)  # screenshot, pdf, video, har
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(1000), nullable=False)
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
    
    # Relationships
    session = relationship("PlaywrightBrowserSession", back_populates="artifacts")
    task = relationship("PlaywrightAutomationTask", back_populates="artifacts")
    
    def __repr__(self):
        return f"<PlaywrightArtifact(id={self.id}, artifact_id='{self.artifact_id}', type='{self.artifact_type}')>"


class PlaywrightBrowserPool(BaseModel):
    """
    Model for managing browser instance pools
    """
    __tablename__ = "playwright_browser_pools"

    # Pool Identification
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
    
    # Relationships
    pool_instances = relationship("PlaywrightBrowserPoolInstance", back_populates="pool")
    
    def __repr__(self):
        return f"<PlaywrightBrowserPool(id={self.id}, pool_id='{self.pool_id}', browser_type='{self.browser_type}')>"


class PlaywrightBrowserPoolInstance(BaseModel):
    """
    Model for tracking individual browser instances in pools
    """
    __tablename__ = "playwright_browser_pool_instances"

    # Instance Identification
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
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Lifecycle
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    termination_reason = Column(String(255), nullable=True)
    
    # Relationships
    pool = relationship("PlaywrightBrowserPool", back_populates="pool_instances")
    
    def __repr__(self):
        return f"<PlaywrightBrowserPoolInstance(id={self.id}, instance_id='{self.instance_id}', status='{self.status}')>"


class PlaywrightSecurityRule(BaseModel):
    """
    Model for security rules and URL validation
    """
    __tablename__ = "playwright_security_rules"

    # Rule Identification
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
    
    def __repr__(self):
        return f"<PlaywrightSecurityRule(id={self.id}, rule_id='{self.rule_id}', type='{self.rule_type}')>"
```

### 2.2 Schema Integration

**Extend existing `OperationType` enum:**
```python
class OperationType(str, Enum):
    """MCP operation types - Extended for Playwright"""
    FILE_OPERATION = "file_operation"
    DATABASE_QUERY = "database_query"
    WEB_SCRAPING = "web_scraping"
    API_PROXY = "api_proxy"
    BATCH_OPERATION = "batch_operation"
    WEBSOCKET = "websocket"
    PLAYWRIGHT_AUTOMATION = "playwright_automation"  # NEW
    PLAYWRIGHT_SESSION_MANAGEMENT = "playwright_session_management"  # NEW
    PLAYWRIGHT_POOL_MANAGEMENT = "playwright_pool_management"  # NEW
```

## 3. Playwright Tool Architecture

### 3.1 Core Schemas

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from enum import Enum


class BrowserType(str, Enum):
    """Supported browser types"""
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


class ArtifactType(str, Enum):
    """Artifact types generated by Playwright"""
    SCREENSHOT = "screenshot"
    PDF = "pdf"
    VIDEO = "video"
    HAR = "har"  # HTTP Archive


class WaitStrategy(str, Enum):
    """Page load wait strategies"""
    LOAD = "load"
    DOM_CONTENT_LOADED = "domcontentloaded"
    NETWORK_IDLE = "networkidle"
    COMMIT = "commit"


class BrowserActionType(str, Enum):
    """Types of browser actions"""
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SCREENSHOT = "screenshot"
    PDF = "pdf"
    WAIT_FOR_SELECTOR = "wait_for_selector"
    WAIT_FOR_TIMEOUT = "wait_for_timeout"
    EVALUATE = "evaluate"
    HOVER = "hover"
    FOCUS = "focus"
    PRESS = "press"
    SELECT_OPTION = "select_option"
    CHECK = "check"
    UNCHECK = "uncheck"
    SCROLL_TO = "scroll_to"


class PlaywrightAutomationTaskRequest(BaseModel):
    """
    Schema for Playwright automation task requests
    """
    # Task Identification
    task_id: Optional[str] = Field(None, description="Unique task identifier (auto-generated if not provided)")
    
    # Browser Configuration
    browser_type: BrowserType = Field(BrowserType.CHROMIUM, description="Browser type to use")
    headless: bool = Field(True, description="Run browser in headless mode")
    viewport_width: int = Field(1920, ge=800, le=3840, description="Browser viewport width")
    viewport_height: int = Field(1080, ge=600, le=2160, description="Browser viewport height")
    user_agent: Optional[str] = Field(None, description="Custom user agent string")
    
    # Navigation Configuration
    target_url: str = Field(..., description="URL to navigate to")
    wait_strategy: WaitStrategy = Field(WaitStrategy.NETWORK_IDLE, description="Page load wait strategy")
    timeout_ms: int = Field(30000, ge=1000, le=300000, description="Navigation timeout in milliseconds")
    
    # Actions Configuration
    actions: List[Dict[str, Any]] = Field(..., description="List of browser actions to perform")
    selectors: Optional[Dict[str, str]] = Field(None, description="CSS selectors mapping")
    
    # Artifact Configuration
    take_screenshot: bool = Field(False, description="Take screenshot of final page")
    generate_pdf: bool = Field(False, description="Generate PDF of final page")
    record_video: bool = Field(False, description="Record video of session")
    screenshot_selector: Optional[str] = Field(None, description="CSS selector for specific screenshot area")
    
    # Advanced Configuration
    enable_javascript: bool = Field(True, description="Enable JavaScript execution")
    block_resources: Optional[List[str]] = Field(None, description="Resource types to block (images, fonts, etc.)")
    intercept_requests: bool = Field(False, description="Enable request interception")
    custom_headers: Optional[Dict[str, str]] = Field(None, description="Custom HTTP headers")
    
    # Session Management
    reuse_session: bool = Field(False, description="Reuse existing browser session")
    session_id: Optional[str] = Field(None, description="Specific session to reuse")
    
    # Security
    url_whitelist: Optional[List[str]] = Field(None, description="Allowed URLs for navigation")
    allowed_domains: Optional[List[str]] = Field(None, description="Allowed domains for requests")
    
    @validator('target_url')
    def validate_url(cls, v):
        """Validate URL format"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
    
    @validator('actions')
    def validate_actions(cls, v):
        """Validate actions list"""
        if not v:
            raise ValueError('At least one action must be specified')
        
        for action in v:
            if 'type' not in action:
                raise ValueError('Each action must have a "type" field')
            if action['type'] not in [t.value for t in BrowserActionType]:
                raise ValueError(f'Invalid action type: {action["type"]}')
        
        return v


class PlaywrightAutomationTaskResponse(BaseModel):
    """
    Schema for Playwright automation task responses
    """
    # Task Information
    task_id: str
    session_id: Optional[str]
    status: str
    success: bool
    
    # Timing Information
    started_at: datetime
    completed_at: Optional[datetime]
    duration_ms: Optional[float]
    
    # Results
    final_url: Optional[str]
    captured_data: Optional[Dict[str, Any]]
    extracted_text: Optional[str]
    page_title: Optional[str]
    
    # Artifacts
    artifacts: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Error Information
    error_message: Optional[str]
    error_details: Optional[Dict[str, Any]]
    
    # Browser Information
    browser_info: Dict[str, Any]
    
    # Performance Metrics
    performance_metrics: Dict[str, Any]


class PlaywrightSessionCreateRequest(BaseModel):
    """
    Schema for creating browser sessions
    """
    # Session Configuration
    session_id: Optional[str] = Field(None, description="Unique session identifier")
    browser_type: BrowserType = Field(BrowserType.CHROMIUM, description="Browser type")
    
    # Browser Options
    headless: bool = Field(True, description="Run in headless mode")
    viewport_width: int = Field(1920, ge=800, le=3840, description="Viewport width")
    viewport_height: int = Field(1080, ge=600, le=2160, description="Viewport height")
    user_agent: Optional[str] = Field(None, description="Custom user agent")
    
    # Advanced Options
    device_scale_factor: float = Field(1.0, ge=1.0, le=3.0, description="Device scale factor")
    has_touch: bool = Field(False, description="Enable touch support")
    is_mobile: bool = Field(False, description="Simulate mobile device")
    
    # Resource Limits
    max_memory_mb: Optional[int] = Field(None, ge=128, le=2048, description="Memory limit")
    max_cpu_percent: Optional[int] = Field(None, ge=10, le=100, description="CPU usage limit")
    
    # Persistence
    persist_session: bool = Field(True, description="Persist session data")
    cookies_path: Optional[str] = Field(None, description="Custom cookies file path")
    
    # Pool Configuration
    pool_id: Optional[str] = Field(None, description="Browser pool to use")
    priority: int = Field(1, ge=1, le=10, description="Session priority")


class PlaywrightSessionCreateResponse(BaseModel):
    """
    Schema for session creation responses
    """
    session_id: str
    status: str
    browser_info: Dict[str, Any]
    pool_info: Optional[Dict[str, Any]]
    session_config: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime]


class PlaywrightBrowserAction(BaseModel):
    """
    Schema for individual browser actions
    """
    type: BrowserActionType
    selector: Optional[str] = None
    text: Optional[str] = None
    timeout_ms: Optional[int] = Field(None, ge=100, le=60000)
    force: bool = False
    position: Optional[Dict[str, float]] = None
    evaluate: Optional[str] = None  # JavaScript to evaluate
    wait_for: Optional[str] = None  # Selector to wait for
    wait_for_timeout: Optional[int] = None
    scroll_to: Optional[str] = None
    keys: Optional[str] = None
    option_value: Optional[str] = None
    option_index: Optional[int] = None


class PlaywrightPoolConfigRequest(BaseModel):
    """
    Schema for browser pool configuration
    """
    pool_id: Optional[str] = Field(None, description="Pool identifier")
    name: str = Field(..., description="Pool name")
    description: Optional[str] = Field(None, description="Pool description")
    
    # Pool Settings
    browser_type: BrowserType = Field(BrowserType.CHROMIUM, description="Browser type")
    max_instances: int = Field(5, ge=1, le=50, description="Maximum browser instances")
    min_instances: int = Field(1, ge=0, le=10, description="Minimum browser instances")
    
    # Resource Limits
    max_memory_mb: int = Field(512, ge=128, le=2048, description="Memory limit per instance")
    max_cpu_percent: int = Field(80, ge=10, le=100, description="CPU usage limit")
    max_concurrent_tasks: int = Field(3, ge=1, le=10, description="Max tasks per instance")
    
    # Lifecycle
    instance_timeout_minutes: int = Field(30, ge=5, le=180, description="Instance timeout")
    idle_timeout_minutes: int = Field(10, ge=1, le=60, description="Idle timeout")
    health_check_interval_seconds: int = Field(60, ge=10, le=300, description="Health check interval")
    
    # Scaling
    auto_scaling_enabled: bool = Field(True, description="Enable auto-scaling")
    scale_up_threshold: float = Field(0.8, ge=0.1, le=1.0, description="CPU/memory threshold for scale up")
    scale_down_threshold: float = Field(0.3, ge=0.1, le=0.9, description="CPU/memory threshold for scale down")
    
    # Browser Configuration
    default_headless: bool = Field(True, description="Default headless mode")
    default_viewport_width: int = Field(1920, ge=800, le=3840, description="Default viewport width")
    default_viewport_height: int = Field(1080, ge=600, le=2160, description="Default viewport height")


class PlaywrightPoolConfigResponse(BaseModel):
    """
    Schema for pool configuration responses
    """
    pool_id: str
    name: str
    status: str
    current_instances: int
    active_sessions: int
    total_tasks: int
    pool_config: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
```

## 4. Browser Instance Management

### 4.1 BrowserPoolManager

```python
import asyncio
import logging
import psutil
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from sqlalchemy.orm import Session

from app.models.playwright import (
    PlaywrightBrowserPool, PlaywrightBrowserPoolInstance, 
    PlaywrightBrowserSession, PlaywrightSecurityRule
)
from app.core.database import get_db


class BrowserPoolManager:
    """
    Intelligent browser instance pool manager
    
    Features:
    - Automatic instance lifecycle management
    - Resource monitoring and limits
    - Load balancing across instances
    - Health checking and recovery
    - Auto-scaling based on demand
    """
    
    def __init__(self):
        self.pools: Dict[str, PlaywrightBrowserPool] = {}
        self.instances: Dict[str, BrowserPoolInstance] = {}
        self.sessions: Dict[str, BrowserSession] = {}
        self.health_check_task: Optional[asyncio.Task] = None
        self.monitoring_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        
        self._running = False
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Initialize the browser pool manager"""
        self.logger.info("Initializing Browser Pool Manager...")
        
        # Load pools from database
        await self._load_pools_from_database()
        
        # Start background tasks
        self._running = True
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        self.logger.info("Browser Pool Manager initialized successfully")
    
    async def shutdown(self):
        """Shutdown the browser pool manager"""
        self.logger.info("Shutting down Browser Pool Manager...")
        
        self._running = False
        
        # Cancel background tasks
        for task in [self.health_check_task, self.monitoring_task, self.cleanup_task]:
            if task:
                task.cancel()
        
        # Terminate all browser instances
        for instance in self.instances.values():
            await instance.terminate()
        
        self.instances.clear()
        self.sessions.clear()
        
        self.logger.info("Browser Pool Manager shutdown complete")
    
    async def create_session(
        self, 
        request: PlaywrightSessionCreateRequest,
        user_id: str
    ) -> BrowserSession:
        """Create a new browser session"""
        
        # Get or create pool
        pool = await self._get_or_create_pool(request)
        
        # Get available instance
        instance = await pool.get_available_instance()
        
        # Create session
        session = BrowserSession(
            session_id=request.session_id or str(uuid.uuid4()),
            instance=instance,
            browser_type=request.browser_type,
            headless=request.headless,
            viewport_width=request.viewport_width,
            viewport_height=request.viewport_height,
            user_agent=request.user_agent,
            user_id=user_id,
            pool_config=pool.config
        )
        
        await session.initialize()
        
        # Track session
        self.sessions[session.session_id] = session
        
        # Update database
        await self._save_session_to_database(session)
        
        self.logger.info(f"Created browser session: {session.session_id}")
        return session
    
    async def execute_automation_task(
        self,
        request: PlaywrightAutomationTaskRequest,
        user_id: str
    ) -> Dict[str, Any]:
        """Execute automation task"""
        
        session = None
        
        # Get or create session
        if request.reuse_session and request.session_id:
            session = self.sessions.get(request.session_id)
            if not session or session.status != "active":
                raise ValueError("Invalid or inactive session")
        else:
            # Create new session
            session_request = PlaywrightSessionCreateRequest(
                browser_type=request.browser_type,
                headless=request.headless,
                viewport_width=request.viewport_width,
                viewport_height=request.viewport_height,
                user_agent=request.user_agent
            )
            session = await self.create_session(session_request, user_id)
        
        # Execute task
        return await session.execute_task(request)
    
    async def get_pool_status(self, pool_id: str) -> Dict[str, Any]:
        """Get comprehensive pool status"""
        if pool_id not in self.pools:
            raise ValueError(f"Pool {pool_id} not found")
        
        pool = self.pools[pool_id]
        instance_stats = []
        
        for instance_id, instance in pool.instances.items():
            instance_stats.append({
                'instance_id': instance_id,
                'status': instance.status,
                'memory_usage_mb': instance.memory_usage,
                'cpu_usage_percent': instance.cpu_usage,
                'active_sessions': len(instance.active_sessions),
                'last_activity': instance.last_activity.isoformat() if instance.last_activity else None
            })
        
        return {
            'pool_id': pool_id,
            'name': pool.name,
            'browser_type': pool.browser_type,
            'status': pool.status,
            'current_instances': len(pool.instances),
            'active_sessions': sum(len(inst.active_sessions) for inst in pool.instances.values()),
            'instances': instance_stats,
            'performance_metrics': pool.get_performance_metrics()
        }


class BrowserPool:
    """
    Individual browser pool for specific configuration
    """
    
    def __init__(self, config: PlaywrightBrowserPool):
        self.config = config
        self.instances: Dict[str, BrowserPoolInstance] = {}
        self.available_instances: List[str] = []
        self.busy_instances: List[str] = []
        self.logger = logging.getLogger(__name__)
    
    async def get_available_instance(self) -> BrowserPoolInstance:
        """Get an available browser instance"""
        
        # Try to reuse available instance
        if self.available_instances:
            instance_id = self.available_instances.pop(0)
            instance = self.instances[instance_id]
            self.busy_instances.append(instance_id)
            return instance
        
        # Create new instance if under limit
        if len(self.instances) < self.config.max_instances:
            instance = await self._create_instance()
            self.busy_instances.append(instance.instance_id)
            return instance
        
        # Wait for available instance
        return await self._wait_for_available_instance()
    
    async def _create_instance(self) -> BrowserPoolInstance:
        """Create new browser instance"""
        instance = BrowserPoolInstance(
            instance_id=str(uuid.uuid4()),
            pool_config=self.config,
            max_memory_mb=self.config.max_memory_mb,
            max_cpu_percent=self.config.max_cpu_percent
        )
        
        await instance.initialize()
        
        self.instances[instance.instance_id] = instance
        self.logger.info(f"Created browser instance: {instance.instance_id}")
        
        return instance
    
    async def _wait_for_available_instance(self, timeout: int = 30) -> BrowserPoolInstance:
        """Wait for available instance with timeout"""
        start_time = datetime.utcnow()
        
        while (datetime.utcnow() - start_time).seconds < timeout:
            if self.available_instances:
                instance_id = self.available_instances.pop(0)
                instance = self.instances[instance_id]
                self.busy_instances.append(instance_id)
                return instance
            
            await asyncio.sleep(1)
        
        raise TimeoutError("No available browser instances")
    
    def release_instance(self, instance_id: str):
        """Release instance back to pool"""
        if instance_id in self.busy_instances:
            self.busy_instances.remove(instance_id)
            self.available_instances.append(instance_id)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get pool performance metrics"""
        total_memory = sum(inst.memory_usage for inst in self.instances.values())
        total_cpu = sum(inst.cpu_usage for inst in self.instances.values())
        active_sessions = sum(len(inst.active_sessions) for inst in self.instances.values())
        
        return {
            'total_instances': len(self.instances),
            'available_instances': len(self.available_instances),
            'busy_instances': len(self.busy_instances),
            'active_sessions': active_sessions,
            'average_memory_usage_mb': total_memory / max(len(self.instances), 1),
            'average_cpu_usage_percent': total_cpu / max(len(self.instances), 1),
            'utilization_percent': len(self.busy_instances) / max(len(self.instances), 1) * 100
        }


class BrowserPoolInstance:
    """
    Individual browser instance in a pool
    """
    
    def __init__(
        self,
        instance_id: str,
        pool_config: PlaywrightBrowserPool,
        max_memory_mb: int = 512,
        max_cpu_percent: int = 80
    ):
        self.instance_id = instance_id
        self.pool_config = pool_config
        self.max_memory_mb = max_memory_mb
        self.max_cpu_percent = max_cpu_percent
        
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.status = "initializing"
        self.active_sessions: List[str] = []
        self.memory_usage = 0.0
        self.cpu_usage = 0.0
        self.last_activity = datetime.utcnow()
        self.created_at = datetime.utcnow()
        
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Initialize browser instance"""
        try:
            self.playwright = await async_playwright().start()
            
            # Launch browser
            self.browser = await self.playwright.chromium.launch(
                headless=self.pool_config.default_headless,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            self.status = "ready"
            self.logger.info(f"Browser instance {self.instance_id} initialized")
            
        except Exception as e:
            self.status = "error"
            self.logger.error(f"Failed to initialize browser instance {self.instance_id}: {e}")
            raise
    
    async def create_context(self, session_config: Dict[str, Any]) -> BrowserContext:
        """Create browser context for session"""
        
        viewport = {
            'width': session_config.get('viewport_width', 1920),
            'height': session_config.get('viewport_height', 1080)
        }
        
        context = await self.browser.new_context(
            viewport=viewport,
            user_agent=session_config.get('user_agent'),
            device_scale_factor=session_config.get('device_scale_factor', 1.0),
            has_touch=session_config.get('has_touch', False),
            is_mobile=session_config.get('is_mobile', False)
        )
        
        # Set up request interception if enabled
        if session_config.get('intercept_requests', False):
            await context.route('**/*', self._handle_route)
        
        return context
    
    async def _handle_route(self, route):
        """Handle route interception"""
        request = route.request
        
        # Block resources if configured
        block_resources = self.pool_config.get('block_resources', [])
        if request.resource_type in block_resources:
            await route.abort()
            return
        
        # Continue with request
        await route.continue_()
    
    async def terminate(self):
        """Terminate browser instance"""
        try:
            if self.context:
                await self.context.close()
            
            if self.browser:
                await self.browser.close()
            
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            
            self.status = "terminated"
            self.logger.info(f"Browser instance {self.instance_id} terminated")
            
        except Exception as e:
            self.logger.error(f"Error terminating browser instance {self.instance_id}: {e}")
    
    def update_resource_usage(self):
        """Update resource usage metrics"""
        try:
            if self.browser and hasattr(self.browser, '_process'):
                process = psutil.Process(self.browser._process.pid)
                self.memory_usage = process.memory_info().rss / 1024 / 1024  # MB
                self.cpu_usage = process.cpu_percent()
        except Exception as e:
            self.logger.warning(f"Failed to update resource usage for {self.instance_id}: {e}")


class BrowserSession:
    """
    Individual browser session
    """
    
    def __init__(
        self,
        session_id: str,
        instance: BrowserPoolInstance,
        browser_type: str,
        headless: bool,
        viewport_width: int,
        viewport_height: int,
        user_id: str,
        user_agent: Optional[str] = None,
        pool_config: Optional[Dict[str, Any]] = None
    ):
        self.session_id = session_id
        self.instance = instance
        self.browser_type = browser_type
        self.headless = headless
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.user_id = user_id
        self.user_agent = user_agent
        self.pool_config = pool_config or {}
        
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.status = "initializing"
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Initialize browser session"""
        try:
            # Create context
            session_config = {
                'viewport_width': self.viewport_width,
                'viewport_height': self.viewport_height,
                'user_agent': self.user_agent,
                'device_scale_factor': 1.0,
                'has_touch': False,
                'is_mobile': False,
                'intercept_requests': False
            }
            
            self.context = await self.instance.create_context(session_config)
            self.page = await self.context.new_page()
            
            # Set up event handlers
            await self._setup_event_handlers()
            
            self.status = "active"
            self.instance.active_sessions.append(self.session_id)
            
            self.logger.info(f"Browser session {self.session_id} initialized")
            
        except Exception as e:
            self.status = "error"
            self.logger.error(f"Failed to initialize session {self.session_id}: {e}")
            raise
    
    async def _setup_event_handlers(self):
        """Set up page event handlers"""
        
        # Console message handler
        def handle_console(msg):
            self.logger.info(f"Console [{msg.type}]: {msg.text}")
        
        # Page error handler
        def handle_page_error(error):
            self.logger.error(f"Page error: {error}")
        
        # Request handler
        async def handle_request(request):
            self.logger.debug(f"Request: {request.method} {request.url}")
        
        # Response handler
        async def handle_response(response):
            self.logger.debug(f"Response: {response.status} {response.url}")
        
        # Set up handlers
        self.page.on("console", handle_console)
        self.page.on("pageerror", handle_page_error)
        self.page.on("request", handle_request)
        self.page.on("response", handle_response)
    
    async def execute_task(self, request: PlaywrightAutomationTaskRequest) -> Dict[str, Any]:
        """Execute automation task"""
        
        task_start_time = datetime.utcnow()
        
        try:
            # Navigate to URL
            await self.page.goto(
                request.target_url,
                wait_until=request.wait_strategy.value,
                timeout=request.timeout_ms
            )
            
            # Execute actions
            results = []
            for action in request.actions:
                result = await self._execute_action(action)
                results.append(result)
            
            # Generate artifacts
            artifacts = []
            if request.take_screenshot:
                artifact = await self._take_screenshot(request.screenshot_selector)
                artifacts.append(artifact)
            
            if request.generate_pdf:
                artifact = await self._generate_pdf()
                artifacts.append(artifact)
            
            # Collect final data
            final_data = {
                'url': self.page.url,
                'title': await self.page.title(),
                'content': await self.page.content(),
                'performance': await self.page.evaluate('() => performance.getEntriesByType("navigation")[0]')
            }
            
            execution_time = (datetime.utcnow() - task_start_time).total_seconds() * 1000
            
            return {
                'task_id': request.task_id,
                'session_id': self.session_id,
                'status': 'completed',
                'success': True,
                'started_at': task_start_time,
                'completed_at': datetime.utcnow(),
                'duration_ms': execution_time,
                'final_url': self.page.url,
                'captured_data': final_data,
                'artifacts': artifacts,
                'browser_info': {
                    'user_agent': self.page.evaluate('() => navigator.userAgent'),
                    'viewport': await self.page.viewport_size()
                }
            }
            
        except Exception as e:
            execution_time = (datetime.utcnow() - task_start_time).total_seconds() * 1000
            
            return {
                'task_id': request.task_id,
                'session_id': self.session_id,
                'status': 'failed',
                'success': False,
                'started_at': task_start_time,
                'completed_at': datetime.utcnow(),
                'duration_ms': execution_time,
                'error_message': str(e),
                'error_details': {
                    'exception_type': type(e).__name__,
                    'stack_trace': getattr(e, '__traceback__', None)
                }
            }
        
        finally:
            self.last_activity = datetime.utcnow()
    
    async def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute individual browser action"""
        
        action_type = action['type']
        start_time = datetime.utcnow()
        
        try:
            if action_type == BrowserActionType.NAVIGATE.value:
                await self.page.goto(action['url'])
                result = {'url': self.page.url}
            
            elif action_type == BrowserActionType.CLICK.value:
                if action.get('selector'):
                    await self.page.click(action['selector'])
                elif action.get('position'):
                    await self.page.mouse.click(action['position']['x'], action['position']['y'])
                result = {'clicked': True}
            
            elif action_type == BrowserActionType.TYPE.value:
                await self.page.type(action['selector'], action['text'])
                result = {'text_entered': action['text']}
            
            elif action_type == BrowserActionType.SCREENSHOT.value:
                path = action.get('path', f'screenshot_{uuid.uuid4()}.png')
                await self.page.screenshot(path=path, full_page=action.get('full_page', False))
                result = {'screenshot_path': path}
            
            elif action_type == BrowserActionType.WAIT_FOR_SELECTOR.value:
                await self.page.wait_for_selector(action['selector'], timeout=action.get('timeout_ms', 30000))
                result = {'selector_found': action['selector']}
            
            elif action_type == BrowserActionType.WAIT_FOR_TIMEOUT.value:
                await self.page.wait_for_timeout(action['timeout_ms'])
                result = {'waited_ms': action['timeout_ms']}
            
            elif action_type == BrowserActionType.EVALUATE.value:
                result = await self.page.evaluate(action['script'])
            
            else:
                raise ValueError(f"Unsupported action type: {action_type}")
            
            return {
                'action_type': action_type,
                'success': True,
                'duration_ms': (datetime.utcnow() - start_time).total_seconds() * 1000,
                'result': result
            }
            
        except Exception as e:
            return {
                'action_type': action_type,
                'success': False,
                'duration_ms': (datetime.utcnow() - start_time).total_seconds() * 1000,
                'error': str(e)
            }
    
    async def _take_screenshot(self, selector: Optional[str] = None) -> Dict[str, Any]:
        """Take screenshot"""
        
        artifact_id = str(uuid.uuid4())
        file_path = f"artifacts/screenshot_{artifact_id}.png"
        
        if selector:
            element = await self.page.query_selector(selector)
            if element:
                await element.screenshot(path=file_path)
            else:
                raise ValueError(f"Element with selector '{selector}' not found")
        else:
            await self.page.screenshot(path=file_path, full_page=True)
        
        return {
            'artifact_id': artifact_id,
            'type': 'screenshot',
            'file_path': file_path,
            'selector': selector
        }
    
    async def _generate_pdf(self) -> Dict[str, Any]:
        """Generate PDF"""
        
        artifact_id = str(uuid.uuid4())
        file_path = f"artifacts/pdf_{artifact_id}.pdf"
        
        await self.page.pdf(
            path=file_path,
            format='A4',
            print_background=True,
            margin={
                'top': '1cm',
                'right': '1cm',
                'bottom': '1cm',
                'left': '1cm'
            }
        )
        
        return {
            'artifact_id': artifact_id,
            'type': 'pdf',
            'file_path': file_path
        }
    
    async def close(self):
        """Close browser session"""
        try:
            if self.page:
                await self.page.close()
            
            if self.context:
                await self.context.close()
            
            if self.session_id in self.instance.active_sessions:
                self.instance.active_sessions.remove(self.session_id)
            
            self.status = "closed"
            self.logger.info(f"Browser session {self.session_id} closed")
            
        except Exception as e:
            self.logger.error(f"Error closing session {self.session_id}: {e}")
```

## 5. Security & Authentication

### 5.1 Security Manager

```python
import re
import hashlib
import logging
from typing import List, Optional, Dict, Any, Set
from urllib.parse import urlparse, urljoin
from sqlalchemy.orm import Session

from app.models.playwright import PlaywrightSecurityRule


class PlaywrightSecurityManager:
    """
    Security manager for Playwright automation
    
    Features:
    - URL validation and whitelist/blacklist checking
    - Script injection prevention
    - Resource access control
    - Artifact encryption
    - Permission-based authorization
    """
    
    def __init__(self):
        self.url_patterns: List[Dict[str, Any]] = []
        self.domain_patterns: Set[str] = set()
        self.blocked_domains: Set[str] = set()
        self.allowed_domains: Set[str] = set()
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self, db: Session):
        """Initialize security manager with rules from database"""
        await self._load_security_rules(db)
    
    async def validate_url(self, url: str, user_permissions: Dict[str, Any]) -> bool:
        """
        Validate if URL is allowed for automation
        
        Args:
            url: Target URL to validate
            user_permissions: User permissions and restrictions
        
        Returns:
            bool: True if URL is allowed, False otherwise
        """
        
        try:
            parsed_url = urlparse(url)
            
            # Check URL format
            if not parsed_url.scheme or not parsed_url.netloc:
                self.logger.warning(f"Invalid URL format: {url}")
                return False
            
            # Check protocol (only http/https allowed)
            if parsed_url.scheme not in ['http', 'https']:
                self.logger.warning(f"Disallowed protocol: {parsed_url.scheme}")
                return False
            
            # Check domain against patterns
            domain = parsed_url.netloc.lower()
            
            # Check explicit domain restrictions
            if self.blocked_domains:
                for blocked_domain in self.blocked_domains:
                    if self._domain_matches(domain, blocked_domain):
                        self.logger.warning(f"URL blocked by domain restriction: {url}")
                        return False
            
            # Check explicit domain allowlist
            if self.allowed_domains:
                allowed = False
                for allowed_domain in self.allowed_domains:
                    if self._domain_matches(domain, allowed_domain):
                        allowed = True
                        break
                
                if not allowed:
                    self.logger.warning(f"URL not in allowlist: {url}")
                    return False
            
            # Check regex patterns
            for pattern in self.url_patterns:
                if pattern['is_regex']:
                    try:
                        if re.match(pattern['pattern'], url):
                            if pattern['action'] == 'deny':
                                self.logger.warning(f"URL denied by regex pattern: {url}")
                                return False
                            elif pattern['action'] == 'allow':
                                self.logger.info(f"URL allowed by regex pattern: {url}")
                                return True
                    except re.error as e:
                        self.logger.error(f"Invalid regex pattern {pattern['pattern']}: {e}")
                else:
                    # Exact match
                    if pattern['pattern'] == url:
                        if pattern['action'] == 'deny':
                            self.logger.warning(f"URL denied by exact match: {url}")
                            return False
                        elif pattern['action'] == 'allow':
                            self.logger.info(f"URL allowed by exact match: {url}")
                            return True
            
            # Check user-specific restrictions
            max_domains = user_permissions.get('max_domains_per_hour', 10)
            if max_domains > 0:
                # This would integrate with rate limiting system
                pass
            
            # Default allow if no explicit restrictions
            self.logger.info(f"URL validated successfully: {url}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating URL {url}: {e}")
            return False
    
    async def sanitize_javascript(self, script: str, user_permissions: Dict[str, Any]) -> bool:
        """
        Validate and sanitize JavaScript code
        
        Args:
            script: JavaScript code to validate
            user_permissions: User permissions for JavaScript execution
        
        Returns:
            bool: True if script is safe, False otherwise
        """
        
        try:
            # Check if user has JavaScript execution permission
            if not user_permissions.get('allow_javascript', True):
                self.logger.warning("JavaScript execution not allowed for user")
                return False
            
            # Check script length
            if len(script) > user_permissions.get('max_script_length', 10000):
                self.logger.warning("Script too long")
                return False
            
            # Dangerous patterns to check for
            dangerous_patterns = [
                r'eval\s*\(',
                r'Function\s*\(',
                r'setTimeout\s*\(\s*["\']',
                r'setInterval\s*\(\s*["\']',
                r'document\.write\s*\(',
                r'innerHTML\s*=',
                r'outerHTML\s*=',
                r'location\.href\s*=',
                r'window\.open\s*\(',
                r'XMLHttpRequest',
                r'fetch\s*\(',
                r'import\s+',
                r'require\s*\(',
                r'process\.',
                r'require\.main',
                r'__dirname',
                r'__filename',
                r'fs\.',
                r'child_process',
                r'child_process\.exec',
                r'child_process\.spawn',
                r'child_process\.fork',
                r'Buffer\.from',
                r'crypto\.',
                r'os\.',
                r'path\.',
                r'url\.',
                r'querystring\.',
                r'net\.',
                r'dns\.',
                r'reflect\.',
                r'global\.',
                r'this\.',
                r'window\[',
                r'document\[',
                r'Object\.defineProperty',
                r'Object\.setPrototypeOf',
                r'Function\.prototype\.call',
                r'Function\.prototype\.apply'
            ]
            
            # Check for dangerous patterns
            for pattern in dangerous_patterns:
                if re.search(pattern, script, re.IGNORECASE):
                    self.logger.warning(f"Potentially dangerous pattern detected: {pattern}")
                    return False
            
            # Check for script tags and other HTML injection patterns
            html_patterns = [
                r'<script[^>]*>',
                r'</script>',
                r'<iframe[^>]*>',
                r'</iframe>',
                r'javascript:',
                r'data:text/html',
                r'<object[^>]*>',
                r'<embed[^>]*>',
                r'<link[^>]*rel=["\']stylesheet["\'][^>]*>',
                r'<style[^>]*>',
                r'</style>'
            ]
            
            for pattern in html_patterns:
                if re.search(pattern, script, re.IGNORECASE):
                    self.logger.warning(f"HTML injection pattern detected: {pattern}")
                    return False
            
            # Check for suspicious function names
            suspicious_functions = [
                'exec', 'execSync', 'spawn', 'spawnSync', 'fork',
                'load', 'loadFile', 'loadScript', 'include',
                'importScript', 'importScripts'
            ]
            
            for func in suspicious_functions:
                if re.search(rf'\b{func}\b', script, re.IGNORECASE):
                    self.logger.warning(f"Suspicious function detected: {func}")
                    return False
            
            self.logger.info("JavaScript validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating JavaScript: {e}")
            return False
    
    async def validate_resource_access(
        self, 
        url: str, 
        resource_type: str, 
        user_permissions: Dict[str, Any]
    ) -> bool:
        """
        Validate access to resources (images, fonts, etc.)
        
        Args:
            url: Resource URL
            resource_type: Type of resource (image, font, script, etc.)
            user_permissions: User permissions
        
        Returns:
            bool: True if access is allowed
        """
        
        try:
            # Check if resource type is allowed
            allowed_resources = user_permissions.get('allowed_resources', ['all'])
            if 'all' not in allowed_resources and resource_type not in allowed_resources:
                self.logger.warning(f"Resource type {resource_type} not allowed")
                return False
            
            # Check if resource type should be blocked
            blocked_resources = user_permissions.get('blocked_resources', [])
            if resource_type in blocked_resources:
                self.logger.warning(f"Resource type {resource_type} blocked")
                return False
            
            # Validate resource URL
            if not await self.validate_url(url, user_permissions):
                return False
            
            # Check resource size limits
            max_resource_size = user_permissions.get(f'max_{resource_type}_size', 0)
            if max_resource_size > 0:
                # This would check actual resource size
                pass
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating resource access: {e}")
            return False
    
    async def encrypt_artifact(self, data: bytes, encryption_key: Optional[str] = None) -> bytes:
        """
        Encrypt artifact data
        
        Args:
            data: Raw artifact data
            encryption_key: Optional encryption key
        
        Returns:
            bytes: Encrypted data
        """
        
        try:
            from cryptography.fernet import Fernet
            
            # Generate or use provided key
            if not encryption_key:
                encryption_key = Fernet.generate_key()
            
            f = Fernet(encryption_key)
            encrypted_data = f.encrypt(data)
            
            self.logger.info("Artifact encrypted successfully")
            return encrypted_data
            
        except Exception as e:
            self.logger.error(f"Error encrypting artifact: {e}")
            raise
    
    async def decrypt_artifact(self, encrypted_data: bytes, encryption_key: str) -> bytes:
        """
        Decrypt artifact data
        
        Args:
            encrypted_data: Encrypted artifact data
            encryption_key: Encryption key
        
        Returns:
            bytes: Decrypted data
        """
        
        try:
            from cryptography.fernet import Fernet
            
            f = Fernet(encryption_key)
            decrypted_data = f.decrypt(encrypted_data)
            
            self.logger.info("Artifact decrypted successfully")
            return decrypted_data
            
        except Exception as e:
            self.logger.error(f"Error decrypting artifact: {e}")
            raise
    
    def _domain_matches(self, actual_domain: str, pattern: str) -> bool:
        """Check if domain matches pattern (supports wildcards)"""
        
        if pattern.startswith('*.'):
            # Wildcard subdomain match
            pattern_domain = pattern[2:]
            return actual_domain.endswith('.' + pattern_domain) or actual_domain == pattern_domain
        else:
            # Exact match or subdomain match
            return actual_domain == pattern or actual_domain.endswith('.' + pattern)
    
    async def _load_security_rules(self, db: Session):
        """Load security rules from database"""
        
        try:
            rules = db.query(PlaywrightSecurityRule).filter(
                PlaywrightSecurityRule.is_active == True
            ).order_by(PlaywrightSecurityRule.priority.desc()).all()
            
            for rule in rules:
                if rule.rule_type == 'url_whitelist':
                    if rule.is_regex:
                        self.url_patterns.append({
                            'pattern': rule.pattern,
                            'is_regex': True,
                            'action': 'allow'
                        })
                    else:
                        self.allowed_domains.add(urlparse(rule.pattern).netloc)
                
                elif rule.rule_type == 'url_blacklist':
                    if rule.is_regex:
                        self.url_patterns.append({
                            'pattern': rule.pattern,
                            'is_regex': True,
                            'action': 'deny'
                        })
                    else:
                        self.blocked_domains.add(urlparse(rule.pattern).netloc)
                
                elif rule.rule_type == 'domain_restriction':
                    if rule.action == 'allow':
                        self.allowed_domains.add(rule.pattern)
                    else:
                        self.blocked_domains.add(rule.pattern)
            
            self.logger.info(f"Loaded {len(rules)} security rules")
            
        except Exception as e:
            self.logger.error(f"Error loading security rules: {e}")


class SecureArtifactManager:
    """
    Secure artifact storage and management
    
    Features:
    - Encrypted storage
    - Access control
    - Automatic cleanup
    - Integrity verification
    """
    
    def __init__(self, storage_path: str = "artifacts"):
        self.storage_path = storage_path
        self.logger = logging.getLogger(__name__)
    
    async def save_artifact(
        self,
        data: bytes,
        artifact_type: str,
        filename: str,
        user_id: str,
        encrypt: bool = True,
        expires_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Save artifact with security measures
        
        Args:
            data: Artifact data
            artifact_type: Type of artifact
            filename: Filename
            user_id: User who owns the artifact
            encrypt: Whether to encrypt the artifact
            expires_at: Expiration timestamp
        
        Returns:
            Dict containing artifact metadata
        """
        
        try:
            import os
            import uuid
            from datetime import datetime
            
            # Generate unique artifact ID
            artifact_id = str(uuid.uuid4())
            
            # Create storage path
            user_path = os.path.join(self.storage_path, user_id)
            os.makedirs(user_path, exist_ok=True)
            
            # Generate secure filename
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            secure_filename = f"{artifact_id}_{timestamp}_{filename}"
            file_path = os.path.join(user_path, secure_filename)
            
            # Encrypt data if requested
            encryption_key = None
            if encrypt:
                from cryptography.fernet import Fernet
                encryption_key = Fernet.generate_key()
                f = Fernet(encryption_key)
                data = f.encrypt(data)
            
            # Save to file
            with open(file_path, 'wb') as f:
                f.write(data)
            
            # Calculate checksum
            import hashlib
            checksum = hashlib.sha256(data).hexdigest()
            
            # Create metadata
            metadata = {
                'artifact_id': artifact_id,
                'file_path': file_path,
                'file_name': secure_filename,
                'file_size': len(data),
                'artifact_type': artifact_type,
                'user_id': user_id,
                'encrypted': encrypt,
                'encryption_key': encryption_key,
                'checksum': checksum,
                'created_at': datetime.utcnow(),
                'expires_at': expires_at
            }
            
            # Save metadata
            metadata_path = file_path + '.meta'
            with open(metadata_path, 'w') as f:
                import json
                json.dump(metadata, f, default=str)
            
            self.logger.info(f"Artifact saved: {artifact_id}")
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error saving artifact: {e}")
            raise
    
    async def get_artifact(self, artifact_id: str, user_id: str) -> Optional[bytes]:
        """
        Retrieve and decrypt artifact
        
        Args:
            artifact_id: Artifact ID
            user_id: User requesting the artifact
        
        Returns:
            bytes: Decrypted artifact data
        """
        
        try:
            import os
            import json
            from datetime import datetime
            
            # Find artifact metadata
            user_path = os.path.join(self.storage_path, user_id)
            metadata_path = None
            
            # Search for metadata file
            for filename in os.listdir(user_path):
                if filename.startswith(artifact_id) and filename.endswith('.meta'):
                    metadata_path = os.path.join(user_path, filename)
                    break
            
            if not metadata_path:
                self.logger.warning(f"Artifact metadata not found: {artifact_id}")
                return None
            
            # Load metadata
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # Check expiration
            if metadata.get('expires_at'):
                expires_at = datetime.fromisoformat(metadata['expires_at'])
                if datetime.utcnow() > expires_at:
                    self.logger.warning(f"Artifact expired: {artifact_id}")
                    return None
            
            # Read encrypted data
            file_path = metadata['file_path']
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt if necessary
            if metadata.get('encrypted', False):
                from cryptography.fernet import Fernet
                f = Fernet(metadata['encryption_key'])
                decrypted_data = f.decrypt(encrypted_data)
            else:
                decrypted_data = encrypted_data
            
            # Update access count
            self._update_access_count(metadata_path, metadata)
            
            self.logger.info(f"Artifact retrieved: {artifact_id}")
            return decrypted_data
            
        except Exception as e:
            self.logger.error(f"Error retrieving artifact {artifact_id}: {e}")
            return None
    
    async def delete_artifact(self, artifact_id: str, user_id: str) -> bool:
        """
        Securely delete artifact and metadata
        
        Args:
            artifact_id: Artifact ID
            user_id: User requesting deletion
        
        Returns:
            bool: True if deleted successfully
        """
        
        try:
            import os
            import shutil
            
            user_path = os.path.join(self.storage_path, user_id)
            
            # Find and delete files
            deleted_files = []
            for filename in os.listdir(user_path):
                if filename.startswith(artifact_id):
                    file_path = os.path.join(user_path, filename)
                    # Secure deletion (overwrite with random data)
                    await self._secure_delete(file_path)
                    deleted_files.append(file_path)
            
            if deleted_files:
                self.logger.info(f"Artifact deleted: {artifact_id}")
                return True
            else:
                self.logger.warning(f"Artifact not found for deletion: {artifact_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting artifact {artifact_id}: {e}")
            return False
    
    async def _secure_delete(self, file_path: str, passes: int = 3):
        """Securely delete file by overwriting with random data"""
        
        try:
            import os
            import random
            
            file_size = os.path.getsize(file_path)
            
            # Overwrite file multiple times
            with open(file_path, 'r+b') as f:
                for _ in range(passes):
                    f.seek(0)
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())
            
            # Finally delete the file
            os.remove(file_path)
            
        except Exception as e:
            self.logger.error(f"Error in secure deletion of {file_path}: {e}")
    
    def _update_access_count(self, metadata_path: str, metadata: Dict[str, Any]):
        """Update artifact access count"""
        
        try:
            import json
            from datetime import datetime
            
            metadata['access_count'] = metadata.get('access_count', 0) + 1
            metadata['last_accessed'] = datetime.utcnow().isoformat()
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, default=str)
                
        except Exception as e:
            self.logger.error(f"Error updating access count: {e}")
```

## 6. API Endpoint Design

### 6.1 Enhanced Playwright API Endpoints

```python
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, FileResponse
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
import asyncio
import json
import logging
from datetime import datetime, timedelta

from app.core.enhanced_mcp_manager import enhanced_mcp_manager
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User as UserModel

# Import Playwright-specific modules
from app.core.playwright import BrowserPoolManager, PlaywrightSecurityManager, SecureArtifactManager
from app.schemas.playwright import (
    PlaywrightAutomationTaskRequest, PlaywrightAutomationTaskResponse,
    PlaywrightSessionCreateRequest, PlaywrightSessionCreateResponse,
    PlaywrightBrowserAction, PlaywrightPoolConfigRequest, PlaywrightPoolConfigResponse,
    BrowserType, ArtifactType
)
from app.models.playwright import (
    PlaywrightBrowserSession, PlaywrightAutomationTask, 
    PlaywrightArtifact, PlaywrightBrowserPool
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Global managers (would be initialized in main app)
browser_pool_manager: Optional[BrowserPoolManager] = None
security_manager: Optional[PlaywrightSecurityManager] = None
artifact_manager: Optional[SecureArtifactManager] = None


# =============================================================================
# Playwright Automation Endpoints
# =============================================================================

@router.post("/enhanced-mcp/playwright/automation/", response_model=Dict[str, Any])
async def execute_playwright_automation(
    task_request: PlaywrightAutomationTaskRequest,
    background_tasks: BackgroundTasks,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Execute Playwright automation task
    
    This endpoint provides comprehensive browser automation capabilities including:
    - Multi-browser support (Chromium, Firefox, WebKit)
    - Custom viewport and user agent configuration
    - JavaScript execution and page interaction
    - Screenshot and PDF generation
    - Video recording
    - Secure URL validation
    """
    
    try:
        # Security validation
        user_permissions = {
            'allow_javascript': True,
            'max_domains_per_hour': 100,
            'allowed_resources': ['all'],
            'blocked_resources': [],
            'max_script_length': 10000
        }
        
        if not await security_manager.validate_url(task_request.target_url, user_permissions):
            raise HTTPException(
                status_code=403, 
                detail="URL not allowed by security policies"
            )
        
        # Validate actions
        for action in task_request.actions:
            if 'type' in action and action['type'] == 'evaluate':
                script = action.get('script', '')
                if not await security_manager.sanitize_javascript(script, user_permissions):
                    raise HTTPException(
                        status_code=403,
                        detail="JavaScript code blocked by security policies"
                    )
        
        # Execute automation task
        result = await browser_pool_manager.execute_automation_task(task_request, current_user.id)
        
        # Save task to database
        await _save_automation_task_to_db(result, db, current_user.id)
        
        # Schedule background tasks
        background_tasks.add_task(
            _cleanup_expired_artifacts,
            result.get('artifacts', []),
            current_user.id
        )
        
        # Log operation
        await _log_playwright_operation(
            operation_type="PLAYWRIGHT_AUTOMATION",
            operation_name="execute_automation",
            request_data=task_request.dict(),
            response_data=result,
            user_id=current_user.id
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Playwright automation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Automation failed: {str(e)}")


@router.post("/enhanced-mcp/playwright/sessions/", response_model=PlaywrightSessionCreateResponse)
async def create_playwright_session(
    session_request: PlaywrightSessionCreateRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new browser session
    
    Creates a persistent browser session that can be reused for multiple automation tasks.
    Sessions are automatically managed and cleaned up based on configuration.
    """
    
    try:
        # Create session
        session = await browser_pool_manager.create_session(session_request, current_user.id)
        
        # Prepare response
        response = PlaywrightSessionCreateResponse(
            session_id=session.session_id,
            status=session.status,
            browser_info={
                'browser_type': session.browser_type,
                'headless': session.headless,
                'viewport': {
                    'width': session.viewport_width,
                    'height': session.viewport_height
                },
                'user_agent': session.user_agent
            },
            pool_info={
                'instance_id': session.instance.instance_id,
                'pool_id': session.instance.pool_config.pool_id
            },
            session_config={
                'created_at': session.created_at.isoformat(),
                'max_memory_mb': session.instance.max_memory_mb,
                'max_cpu_percent': session.instance.max_cpu_percent
            },
            created_at=session.created_at,
            expires_at=None  # Would be calculated based on configuration
        )
        
        # Save session to database
        await _save_session_to_db(session, db, current_user.id)
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to create browser session: {e}")
        raise HTTPException(status_code=500, detail=f"Session creation failed: {str(e)}")


@router.delete("/enhanced-mcp/playwright/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def terminate_playwright_session(
    session_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Terminate browser session
    
    Gracefully terminates the browser session and releases all associated resources.
    """
    
    try:
        # Find session
        session = browser_pool_manager.sessions.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Verify ownership
        if session.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Terminate session
        await session.close()
        
        # Remove from manager
        if session_id in browser_pool_manager.sessions:
            del browser_pool_manager.sessions[session_id]
        
        # Update database
        db_session = db.query(PlaywrightBrowserSession).filter(
            PlaywrightBrowserSession.session_id == session_id
        ).first()
        
        if db_session:
            db_session.status = "terminated"
            db_session.updated_at = datetime.utcnow()
            db.commit()
        
        logger.info(f"Session terminated: {session_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to terminate session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Session termination failed: {str(e)}")


@router.get("/enhanced-mcp/playwright/sessions/", response_model=List[Dict[str, Any]])
async def list_playwright_sessions(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
    active_only: bool = True,
    limit: int = 50
):
    """
    List user browser sessions
    
    Returns a list of browser sessions with status and basic information.
    """
    
    try:
        query = db.query(PlaywrightBrowserSession).filter(
            PlaywrightBrowserSession.user_id == current_user.id
        )
        
        if active_only:
            query = query.filter(PlaywrightBrowserSession.status.in_(["active", "idle"]))
        
        sessions = query.order_by(PlaywrightBrowserSession.created_at.desc()).limit(limit).all()
        
        session_list = []
        for session in sessions:
            session_list.append({
                'session_id': session.session_id,
                'browser_type': session.browser_type,
                'status': session.status,
                'headless': session.headless,
                'viewport': {
                    'width': session.viewport_width,
                    'height': session.viewport_height
                },
                'current_url': session.current_url,
                'created_at': session.created_at.isoformat(),
                'last_activity': session.last_activity.isoformat() if session.last_activity else None,
                'expires_at': session.expires_at.isoformat() if session.expires_at else None
            })
        
        return session_list
        
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")


@router.post("/enhanced-mcp/playwright/sessions/{session_id}/actions/")
async def execute_session_action(
    session_id: str,
    action: PlaywrightBrowserAction,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Execute action on existing session
    
    Allows executing individual browser actions on an existing session
    without creating a new automation task.
    """
    
    try:
        # Get session
        session = browser_pool_manager.sessions.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Verify ownership
        if session.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Execute action
        result = await session._execute_action(action.dict())
        
        return {
            'session_id': session_id,
            'action': action.dict(),
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute action on session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Action execution failed: {str(e)}")


# =============================================================================
# Browser Pool Management Endpoints
# =============================================================================

@router.post("/enhanced-mcp/playwright/pools/", response_model=PlaywrightPoolConfigResponse)
async def create_browser_pool(
    pool_config: PlaywrightPoolConfigRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create browser pool
    
    Creates a new browser instance pool with specified configuration.
    Pools provide intelligent resource management and load balancing.
    """
    
    try:
        # Create database record
        db_pool = PlaywrightBrowserPool(
            pool_id=pool_config.pool_id or f"pool_{int(datetime.utcnow().timestamp())}",
            name=pool_config.name,
            description=pool_config.description,
            browser_type=pool_config.browser_type.value,
            max_instances=pool_config.max_instances,
            min_instances=pool_config.min_instances,
            instance_timeout_minutes=pool_config.instance_timeout_minutes,
            max_memory_mb=pool_config.max_memory_mb,
            max_cpu_percent=pool_config.max_cpu_percent,
            max_concurrent_tasks=pool_config.max_concurrent_tasks,
            idle_timeout_minutes=pool_config.idle_timeout_minutes,
            health_check_interval_seconds=pool_config.health_check_interval_seconds,
            auto_scaling_enabled=pool_config.auto_scaling_enabled
        )
        
        db.add(db_pool)
        db.commit()
        db.refresh(db_pool)
        
        # Create pool in manager
        pool = BrowserPool(db_pool)
        browser_pool_manager.pools[db_pool.pool_id] = pool
        
        # Prepare response
        response = PlaywrightPoolConfigResponse(
            pool_id=db_pool.pool_id,
            name=db_pool.name,
            status="active",
            current_instances=0,
            active_sessions=0,
            total_tasks=0,
            pool_config=pool_config.dict(),
            performance_metrics={
                'average_memory_usage_mb': 0.0,
                'average_cpu_usage_percent': 0.0,
                'utilization_percent': 0.0
            },
            created_at=db_pool.created_at,
            updated_at=db_pool.updated_at
        )
        
        logger.info(f"Browser pool created: {db_pool.pool_id}")
        return response
        
    except Exception as e:
        logger.error(f"Failed to create browser pool: {e}")
        raise HTTPException(status_code=500, detail=f"Pool creation failed: {str(e)}")


@router.get("/enhanced-mcp/playwright/pools/", response_model=List[Dict[str, Any]])
async def list_browser_pools(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all browser pools
    
    Returns status and configuration information for all browser pools.
    """
    
    try:
        pools = db.query(PlaywrightBrowserPool).filter(
            PlaywrightBrowserPool.is_active == True
        ).all()
        
        pool_list = []
        for pool in pools:
            # Get status from manager if available
            manager_pool = browser_pool_manager.pools.get(pool.pool_id)
            
            if manager_pool:
                status_info = await browser_pool_manager.get_pool_status(pool.pool_id)
                pool_info = {
                    'pool_id': pool.pool_id,
                    'name': pool.name,
                    'description': pool.description,
                    'browser_type': pool.browser_type,
                    'status': status_info['status'],
                    'current_instances': status_info['current_instances'],
                    'active_sessions': status_info['active_sessions'],
                    'max_instances': pool.max_instances,
                    'performance_metrics': status_info['performance_metrics'],
                    'created_at': pool.created_at.isoformat(),
                    'updated_at': pool.updated_at.isoformat() if pool.updated_at else None
                }
            else:
                pool_info = {
                    'pool_id': pool.pool_id,
                    'name': pool.name,
                    'description': pool.description,
                    'browser_type': pool.browser_type,
                    'status': 'inactive',
                    'current_instances': 0,
                    'active_sessions': 0,
                    'max_instances': pool.max_instances,
                    'performance_metrics': {},
                    'created_at': pool.created_at.isoformat(),
                    'updated_at': pool.updated_at.isoformat() if pool.updated_at else None
                }
            
            pool_list.append(pool_info)
        
        return pool_list
        
    except Exception as e:
        logger.error(f"Failed to list browser pools: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list pools: {str(e)}")


# =============================================================================
# Artifact Management Endpoints
# =============================================================================

@router.get("/enhanced-mcp/artifacts/{artifact_id}")
async def get_playwright_artifact(
    artifact_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retrieve Playwright artifact
    
    Returns the requested artifact (screenshot, PDF, video) with proper
    security checks and access control.
    """
    
    try:
        # Get artifact data
        artifact_data = await artifact_manager.get_artifact(artifact_id, current_user.id)
        
        if not artifact_data:
            raise HTTPException(status_code=404, detail="Artifact not found or expired")
        
        # Determine content type based on file extension
        content_type = "application/octet-stream"  # Default
        if artifact_id.endswith('.png'):
            content_type = "image/png"
        elif artifact_id.endswith('.pdf'):
            content_type = "application/pdf"
        elif artifact_id.endswith('.mp4'):
            content_type = "video/mp4"
        
        return StreamingResponse(
            iter([artifact_data]),
            media_type=content_type,
            headers={
                'Content-Disposition': f'attachment; filename="{artifact_id}"',
                'Cache-Control': 'private, max-age=3600'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve artifact {artifact_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Artifact retrieval failed: {str(e)}")


@router.delete("/enhanced-mcp/artifacts/{artifact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_playwright_artifact(
    artifact_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete Playwright artifact
    
    Securely deletes the specified artifact and all associated metadata.
    """
    
    try:
        success = await artifact_manager.delete_artifact(artifact_id, current_user.id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Artifact not found")
        
        logger.info(f"Artifact deleted: {artifact_id} by user {current_user.id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete artifact {artifact_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Artifact deletion failed: {str(e)}")


@router.get("/enhanced-mcp/artifacts/", response_model=List[Dict[str, Any]])
async def list_playwright_artifacts(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
    artifact_type: Optional[ArtifactType] = None,
    limit: int = 50
):
    """
    List user artifacts
    
    Returns a list of artifacts generated by the user with metadata.
    """
    
    try:
        query = db.query(PlaywrightArtifact).filter(
            PlaywrightArtifact.session_id.in_(
                db.query(PlaywrightBrowserSession.id).filter(
                    PlaywrightBrowserSession.user_id == current_user.id
                )
            )
        )
        
        if artifact_type:
            query = query.filter(PlaywrightArtifact.artifact_type == artifact_type.value)
        
        artifacts = query.order_by(PlaywrightArtifact.created_at.desc()).limit(limit).all()
        
        artifact_list = []
        for artifact in artifacts:
            artifact_list.append({
                'artifact_id': artifact.artifact_id,
                'artifact_type': artifact.artifact_type,
                'file_name': artifact.file_name,
                'file_size_bytes': artifact.file_size_bytes,
                'mime_type': artifact.mime_type,
                'width': artifact.width,
                'height': artifact.height,
                'duration_ms': artifact.duration_ms,
                'page_url': artifact.page_url,
                'is_public': artifact.is_public,
                'download_count': artifact.download_count,
                'expires_at': artifact.expires_at.isoformat() if artifact.expires_at else None,
                'created_at': artifact.created_at.isoformat()
            })
        
        return artifact_list
        
    except Exception as e:
        logger.error(f"Failed to list artifacts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list artifacts: {str(e)}")


# =============================================================================
# Health and Monitoring Endpoints
# =============================================================================

@router.get("/enhanced-mcp/playwright/health/")
async def playwright_health_check(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Comprehensive Playwright service health check
    
    Returns detailed health information including:
    - Browser pool status
    - Active sessions
    - Resource usage
    - Service availability
    """
    
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'browser_pool_manager': 'healthy' if browser_pool_manager and browser_pool_manager._running else 'unhealthy',
                'security_manager': 'healthy' if security_manager else 'unhealthy',
                'artifact_manager': 'healthy' if artifact_manager else 'unhealthy'
            },
            'pools': {},
            'total_sessions': len(browser_pool_manager.sessions) if browser_pool_manager else 0,
            'active_sessions': 0,
            'total_artifacts': 0
        }
        
        # Get pool status if available
        if browser_pool_manager:
            for pool_id, pool in browser_pool_manager.pools.items():
                try:
                    pool_status = await browser_pool_manager.get_pool_status(pool_id)
                    health_status['pools'][pool_id] = pool_status
                    health_status['active_sessions'] += pool_status['active_sessions']
                except Exception as e:
                    health_status['pools'][pool_id] = {
                        'status': 'error',
                        'error': str(e)
                    }
        
        # Determine overall health
        if any(service == 'unhealthy' for service in health_status['services'].values()):
            health_status['status'] = 'degraded'
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }


@router.get("/enhanced-mcp/playwright/metrics/")
async def get_playwright_metrics(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
    pool_id: Optional[str] = None,
    hours: int = 24
):
    """
    Get Playwright performance metrics
    
    Returns comprehensive metrics for the specified time period including:
    - Task execution statistics
    - Resource utilization
    - Error rates
    - Response times
    """
    
    try:
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Get task metrics
        task_query = db.query(PlaywrightAutomationTask).filter(
            PlaywrightAutomationTask.created_at >= start_time
        )
        
        if pool_id:
            # This would require joining with session and pool tables
            pass
        
        tasks = task_query.all()
        
        # Calculate metrics
        total_tasks = len(tasks)
        successful_tasks = len([t for t in tasks if t.success])
        failed_tasks = total_tasks - successful_tasks
        average_duration = sum(t.duration_ms or 0 for t in tasks) / max(total_tasks, 1)
        
        # Get session metrics
        session_query = db.query(PlaywrightBrowserSession).filter(
            PlaywrightBrowserSession.created_at >= start_time
        )
        sessions = session_query.all()
        
        # Get artifact metrics
        artifact_query = db.query(PlaywrightArtifact).filter(
            PlaywrightArtifact.created_at >= start_time
        )
        artifacts = artifact_query.all()
        
        metrics = {
            'time_range': {
                'start': start_time.isoformat(),
                'end': datetime.utcnow().isoformat(),
                'hours': hours
            },
            'tasks': {
                'total': total_tasks,
                'successful': successful_tasks,
                'failed': failed_tasks,
                'success_rate': successful_tasks / max(total_tasks, 1),
                'average_duration_ms': average_duration
            },
            'sessions': {
                'total': len(sessions),
                'active': len([s for s in sessions if s.status in ['active', 'idle']]),
                'terminated': len([s for s in sessions if s.status == 'terminated'])
            },
            'artifacts': {
                'total': len(artifacts),
                'by_type': {}
            }
        }
        
        # Artifact type breakdown
        for artifact in artifacts:
            artifact_type = artifact.artifact_type
            if artifact_type not in metrics['artifacts']['by_type']:
                metrics['artifacts']['by_type'][artifact_type] = 0
            metrics['artifacts']['by_type'][artifact_type] += 1
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


# =============================================================================
# WebSocket Support for Real-time Communication
# =============================================================================

@router.websocket("/enhanced-mcp/playwright/ws/{session_id}")
async def playwright_websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time browser session control
    
    Provides real-time communication for:
    - Live browser session monitoring
    - Interactive session control
    - Real-time event streaming
    - Debug information
    """
    
    await websocket.accept()
    
    try:
        # Verify session exists
        session = browser_pool_manager.sessions.get(session_id)
        if not session:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Session not found"
            }))
            await websocket.close()
            return
        
        # Send initial session info
        await websocket.send_text(json.dumps({
            "type": "session_info",
            "session_id": session_id,
            "status": session.status,
            "browser_info": {
                "type": session.browser_type,
                "headless": session.headless,
                "url": session.page.url if session.page else None
            }
        }))
        
        # Set up message handler
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message_type = message_data.get("type")
            
            if message_type == "get_status":
                # Send current session status
                status_info = {
                    "type": "status",
                    "session_id": session_id,
                    "status": session.status,
                    "url": session.page.url if session.page else None,
                    "title": await session.page.title() if session.page else None,
                    "memory_usage": session.instance.memory_usage,
                    "cpu_usage": session.instance.cpu_usage
                }
                await websocket.send_text(json.dumps(status_info))
            
            elif message_type == "execute_action":
                # Execute action in real-time
                action = message_data.get("action")
                try:
                    result = await session._execute_action(action)
                    await websocket.send_text(json.dumps({
                        "type": "action_result",
                        "action": action,
                        "result": result
                    }))
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "action_error",
                        "action": action,
                        "error": str(e)
                    }))
            
            elif message_type == "screenshot":
                # Take and send screenshot
                try:
                    artifact = await session._take_screenshot(message_data.get('selector'))
                    await websocket.send_text(json.dumps({
                        "type": "screenshot",
                        "artifact": artifact
                    }))
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "screenshot_error",
                        "error": str(e)
                    }))
            
            elif message_type == "navigate":
                # Navigate to URL
                url = message_data.get("url")
                try:
                    await session.page.goto(url)
                    await websocket.send_text(json.dumps({
                        "type": "navigation",
                        "url": url,
                        "success": True
                    }))
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "navigation_error",
                        "url": url,
                        "error": str(e)
                    }))
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "error": str(e)
        }))


# =============================================================================
# Helper Functions
# =============================================================================

async def _save_automation_task_to_db(
    result: Dict[str, Any], 
    db: Session, 
    user_id: str
):
    """Save automation task result to database"""
    
    try:
        # Find session
        session = db.query(PlaywrightBrowserSession).filter(
            PlaywrightBrowserSession.session_id == result.get('session_id')
        ).first()
        
        if session:
            # Create task record
            task = PlaywrightAutomationTask(
                task_id=result.get('task_id'),
                session_id=session.id,
                user_id=user_id,
                target_url="",  # Would be populated from request
                actions=[],
                status=result.get('status'),
                success=result.get('success'),
                started_at=result.get('started_at'),
                completed_at=result.get('completed_at'),
                duration_ms=result.get('duration_ms'),
                error_message=result.get('error_message'),
                final_url=result.get('final_url'),
                captured_data=result.get('captured_data')
            )
            
            db.add(task)
            db.commit()
            
            # Create artifact records
            for artifact_info in result.get('artifacts', []):
                artifact = PlaywrightArtifact(
                    artifact_id=artifact_info['artifact_id'],
                    task_id=task.id,
                    session_id=session.id,
                    artifact_type=artifact_info['type'],
                    file_name=artifact_info['file_path'].split('/')[-1],
                    file_path=artifact_info['file_path'],
                    page_url=result.get('final_url'),
                    capture_timestamp=datetime.utcnow()
                )
                
                db.add(artifact)
            
            db.commit()
            
    except Exception as e:
        logger.error(f"Failed to save task to database: {e}")


async def _save_session_to_db(session, db: Session, user_id: str):
    """Save session to database"""
    
    try:
        db_session = PlaywrightBrowserSession(
            session_id=session.session_id,
            user_id=user_id,
            browser_type=session.browser_type,
            viewport_width=session.viewport_width,
            viewport_height=session.viewport_height,
            user_agent=session.user_agent,
            headless=session.headless,
            status=session.status
        )
        
        db.add(db_session)
        db.commit()
        
    except Exception as e:
        logger.error(f"Failed to save session to database: {e}")


async def _cleanup_expired_artifacts(artifacts: List[Dict[str, Any]], user_id: str):
    """Background task to clean up expired artifacts"""
    
    try:
        # Schedule artifacts for cleanup after 24 hours
        cleanup_time = datetime.utcnow() + timedelta(hours=24)
        
        # This would be implemented to schedule cleanup tasks
        logger.info(f"Scheduled cleanup for {len(artifacts)} artifacts")
        
    except Exception as e:
        logger.error(f"Failed to schedule artifact cleanup: {e}")


async def _log_playwright_operation(
    operation_type: str,
    operation_name: str,
    request_data: Dict[str, Any],
    response_data: Dict[str, Any],
    user_id: str
):
    """Log Playwright operation"""
    
    try:
        logger.info(f"Playwright operation: {operation_type} - {operation_name} - User: {user_id}")
    except Exception as e:
        logger.error(f"Failed to log operation: {e}")
```

## 7. Integration with Monitoring

### 7.1 Metrics Collection

```python
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import psutil
import time


class PlaywrightMetricsCollector:
    """
    Comprehensive metrics collection for Playwright automation
    
    Collects and stores metrics for:
    - Task execution performance
    - Resource utilization
    - Browser instance health
    - User activity patterns
    - Error rates and types
    """
    
    def __init__(self):
        self.metrics_buffer: Dict[str, Any] = {}
        self.collection_interval = 30  # seconds
        self.retention_period = timedelta(days=30)
        self.logger = logging.getLogger(__name__)
    
    async def start_collection(self):
        """Start background metrics collection"""
        self.logger.info("Starting Playwright metrics collection")
        
        # Start collection loop
        asyncio.create_task(self._collection_loop())
    
    async def record_task_execution(
        self,
        task_id: str,
        duration_ms: float,
        success: bool,
        browser_type: str,
        user_id: str,
        error_type: Optional[str] = None
    ):
        """Record task execution metrics"""
        
        metric = {
            'timestamp': datetime.utcnow(),
            'task_id': task_id,
            'duration_ms': duration_ms,
            'success': success,
            'browser_type': browser_type,
            'user_id': user_id,
            'error_type': error_type
        }
        
        await self._store_metric('task_execution', metric)
    
    async def record_resource_usage(
        self,
        instance_id: str,
        memory_usage_mb: float,
        cpu_usage_percent: float,
        active_sessions: int
    ):
        """Record resource usage metrics"""
        
        metric = {
            'timestamp': datetime.utcnow(),
            'instance_id': instance_id,
            'memory_usage_mb': memory_usage_mb,
            'cpu_usage_percent': cpu_usage_percent,
            'active_sessions': active_sessions
        }
        
        await self._store_metric('resource_usage', metric)
    
    async def record_browser_event(
        self,
        event_type: str,
        session_id: str,
        browser_type: str,
        details: Dict[str, Any]
    ):
        """Record browser events"""
        
        metric = {
            'timestamp': datetime.utcnow(),
            'event_type': event_type,
            'session_id': session_id,
            'browser_type': browser_type,
            'details': details
        }
        
        await self._store_metric('browser_events', metric)
    
    async def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for specified time period"""
        
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        # This would query stored metrics and calculate summary
        summary = {
            'time_range': {
                'start': start_time.isoformat(),
                'end': datetime.utcnow().isoformat(),
                'hours': hours
            },
            'task_metrics': {
                'total_tasks': 0,
                'successful_tasks': 0,
                'failed_tasks': 0,
                'average_duration_ms': 0.0,
                'success_rate': 0.0
            },
            'resource_metrics': {
                'average_memory_usage': 0.0,
                'peak_memory_usage': 0.0,
                'average_cpu_usage': 0.0,
                'peak_cpu_usage': 0.0
            },
            'browser_metrics': {
                'total_sessions': 0,
                'active_sessions': 0,
                'browser_type_distribution': {}
            },
            'error_analysis': {
                'error_types': {},
                'most_common_errors': []
            }
        }
        
        return summary
    
    async def _collection_loop(self):
        """Background metrics collection loop"""
        
        while True:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(self.collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics"""
        
        try:
            # System resource usage
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            system_metric = {
                'timestamp': datetime.utcnow(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3)
            }
            
            await self._store_metric('system_resources', system_metric)
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
    
    async def _store_metric(self, metric_type: str, metric_data: Dict[str, Any]):
        """Store metric data"""
        
        try:
            if metric_type not in self.metrics_buffer:
                self.metrics_buffer[metric_type] = []
            
            self.metrics_buffer[metric_type].append(metric_data)
            
            # Clean up old metrics
            cutoff_time = datetime.utcnow() - self.retention_period
            
            self.metrics_buffer[metric_type] = [
                m for m in self.metrics_buffer[metric_type]
                if m['timestamp'] > cutoff_time
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to store metric: {e}")


class PlaywrightHealthMonitor:
    """
    Health monitoring for Playwright services
    
    Monitors:
    - Browser pool health
    - Instance availability
    - Service dependencies
    - Performance thresholds
    """
    
    def __init__(self, browser_pool_manager: BrowserPoolManager):
        self.browser_pool_manager = browser_pool_manager
        self.health_checks = {}
        self.thresholds = {
            'max_memory_usage_percent': 80,
            'max_cpu_usage_percent': 90,
            'max_concurrent_sessions_per_instance': 5,
            'min_available_instances': 1,
            'max_task_failure_rate': 0.1  # 10%
        }
        self.logger = logging.getLogger(__name__)
    
    async def perform_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        
        health_status = {
            'overall_status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {},
            'alerts': []
        }
        
        try:
            # Check browser pools
            pool_health = await self._check_pools_health()
            health_status['checks']['pools'] = pool_health
            
            # Check resource usage
            resource_health = await self._check_resource_health()
            health_status['checks']['resources'] = resource_health
            
            # Check service dependencies
            dependency_health = await self._check_dependencies_health()
            health_status['checks']['dependencies'] = dependency_health
            
            # Determine overall health
            unhealthy_checks = [
                check for check in health_status['checks'].values()
                if check['status'] == 'unhealthy'
            ]
            
            if unhealthy_checks:
                health_status['overall_status'] = 'unhealthy'
                health_status['alerts'].extend([
                    check['message'] for check in unhealthy_checks
                ])
            elif any(check['status'] == 'degraded' for check in health_status['checks'].values()):
                health_status['overall_status'] = 'degraded'
            
        except Exception as e:
            health_status['overall_status'] = 'error'
            health_status['error'] = str(e)
            self.logger.error(f"Health check failed: {e}")
        
        return health_status
    
    async def _check_pools_health(self) -> Dict[str, Any]:
        """Check browser pools health"""
        
        try:
            pools_status = {}
            total_instances = 0
            healthy_instances = 0
            
            for pool_id, pool in self.browser_pool_manager.pools.items():
                # Get pool status
                pool_status = await self.browser_pool_manager.get_pool_status(pool_id)
                
                pools_status[pool_id] = {
                    'status': 'healthy',
                    'instances': pool_status['current_instances'],
                    'active_sessions': pool_status['active_sessions'],
                    'utilization': pool_status['performance_metrics']['utilization_percent']
                }
                
                # Check if pool has minimum instances
                if pool_status['current_instances'] < 1:
                    pools_status[pool_id]['status'] = 'unhealthy'
                    pools_status[pool_id]['message'] = f"No available instances in pool {pool_id}"
                
                # Check utilization
                if pool_status['performance_metrics']['utilization_percent'] > 90:
                    pools_status[pool_id]['status'] = 'degraded'
                    pools_status[pool_id]['message'] = f"High utilization in pool {pool_id}"
                
                total_instances += pool_status['current_instances']
                if pools_status[pool_id]['status'] == 'healthy':
                    healthy_instances += 1
            
            overall_status = 'healthy'
            if healthy_instances == 0 and total_instances == 0:
                overall_status = 'unhealthy'
            elif healthy_instances < total_instances:
                overall_status = 'degraded'
            
            return {
                'status': overall_status,
                'pools': pools_status,
                'total_instances': total_instances,
                'healthy_instances': healthy_instances
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _check_resource_health(self) -> Dict[str, Any]:
        """Check system resource health"""
        
        try:
            # Get system resources
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            status = 'healthy'
            alerts = []
            
            # Check CPU usage
            if cpu_percent > self.thresholds['max_cpu_usage_percent']:
                status = 'unhealthy'
                alerts.append(f"High CPU usage: {cpu_percent}%")
            elif cpu_percent > 70:
                status = 'degraded'
                alerts.append(f"Elevated CPU usage: {cpu_percent}%")
            
            # Check memory usage
            if memory.percent > self.thresholds['max_memory_usage_percent']:
                status = 'unhealthy'
                alerts.append(f"High memory usage: {memory.percent}%")
            elif memory.percent > 70:
                status = 'degraded'
                alerts.append(f"Elevated memory usage: {memory.percent}%")
            
            return {
                'status': status,
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'alerts': alerts
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _check_dependencies_health(self) -> Dict[str, Any]:
        """Check external dependencies health"""
        
        try:
            dependencies = {
                'database': await self._check_database_health(),
                'redis': await self._check_redis_health(),
                'playwright_browsers': await self._check_playwright_health()
            }
            
            overall_status = 'healthy'
            errors = []
            
            for dep_name, dep_status in dependencies.items():
                if not dep_status.get('healthy', False):
                    overall_status = 'unhealthy'
                    errors.append(f"{dep_name} is unhealthy")
            
            return {
                'status': overall_status,
                'dependencies': dependencies,
                'errors': errors
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity"""
        
        try:
            # This would perform actual database health check
            return {'healthy': True, 'response_time_ms': 10}
        except Exception:
            return {'healthy': False, 'error': 'Database connection failed'}
    
    async def _check_redis_health(self) -> Dict[str, Any]:
        """Check Redis connectivity"""
        
        try:
            # This would perform actual Redis health check
            return {'healthy': True, 'response_time_ms': 5}
        except Exception:
            return {'healthy': False, 'error': 'Redis connection failed'}
    
    async def _check_playwright_health(self) -> Dict[str, Any]:
        """Check Playwright browser availability"""
        
        try:
            # Test browser launch
            from playwright.async_api import async_playwright
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=True)
            await browser.close()
            await playwright.stop()
            
            return {'healthy': True, 'browsers_available': ['chromium', 'firefox', 'webkit']}
        except Exception as e:
            return {'healthy': False, 'error': f'Browser launch failed: {str(e)}'}
```

## 8. Deployment Architecture

### 8.1 Docker Configuration

**Enhanced Dockerfile for Backend:**
```dockerfile
# Multi-stage build for optimized image
FROM mcr.microsoft.com/playwright/python:v1.40.0-focal as playwright

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libxss1 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libxss1 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN pip install playwright && \
    playwright install chromium firefox webkit

# Copy application code
WORKDIR /app
COPY backend/ .

# Create artifacts directory
RUN mkdir -p artifacts && chown -R app:app artifacts

# Switch to non-root user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Enhanced docker-compose.yml:**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: chronos-postgres
    environment:
      POSTGRES_DB: chronos_db
      POSTGRES_USER: chronos_user
      POSTGRES_PASSWORD: chronos_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/init-db:/docker-entrypoint-initdb.d
    networks:
      - chronos-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U chronos_user -d chronos_db"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    container_name: chronos-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - chronos-network
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Enhanced Backend with Playwright
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: chronos-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://chronos_user:chronos_pass@postgres:5432/chronos_db
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY:-your-secret-key-here}
      - ENVIRONMENT=production
      - PLAYWRIGHT_BROWSER_POOL_SIZE=5
      - PLAYWRIGHT_MAX_CONCURRENT_SESSIONS=20
      - PLAYWRIGHT_ARTIFACT_STORAGE_PATH=/app/artifacts
      - PLAYWRIGHT_SECURITY_ENABLED=true
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
      - /app/__pycache__
      - playwright_artifacts:/app/artifacts
    networks:
      - chronos-network
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health', timeout=5)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  # Dedicated Playwright Worker Service
  playwright-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: chronos-playwright-worker
    environment:
      - DATABASE_URL=postgresql://chronos_user:chronos_pass@postgres:5432/chronos_db
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY:-your-secret-key-here}
      - ENVIRONMENT=production
      - PLAYWRIGHT_WORKER_MODE=true
      - PLAYWRIGHT_BROWSER_POOL_SIZE=10
      - PLAYWRIGHT_MAX_CONCURRENT_SESSIONS=50
      - PLAYWRIGHT_ARTIFACT_STORAGE_PATH=/app/artifacts
      - PLAYWRIGHT_SECURITY_ENABLED=true
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
      - /app/__pycache__
      - playwright_artifacts:/app/artifacts
    networks:
      - chronos-network
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'
    command: python -m app.core.playwright_worker

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: chronos-frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
      - VITE_WS_URL=ws://localhost:8000
    depends_on:
      backend:
        condition: service_healthy
    volumes:
      - ./frontend:/app
      - /app/node_modules
    networks:
      - chronos-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Monitoring Stack
  prometheus:
    image: prom/prometheus:latest
    container_name: chronos-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - chronos-network
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    container_name: chronos-grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    networks:
      - chronos-network

volumes:
  postgres_data:
  redis_data:
  playwright_artifacts:
  prometheus_data:
  grafana_data:

networks:
  chronos-network:
    driver: bridge
```

### 8.2 Kubernetes Deployment

**Kubernetes Deployment Manifest:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chronos-backend
  labels:
    app: chronos-backend
    component: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: chronos-backend
      component: backend
  template:
    metadata:
      labels:
        app: chronos-backend
        component: backend
    spec:
      containers:
      - name: backend
        image: chronos-ai/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: chronos-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: chronos-secrets
              key: redis-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: chronos-secrets
              key: secret-key
        - name: PLAYWRIGHT_BROWSER_POOL_SIZE
          value: "5"
        - name: PLAYWRIGHT_MAX_CONCURRENT_SESSIONS
          value: "20"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        volumeMounts:
        - name: playwright-artifacts
          mountPath: /app/artifacts
      volumes:
      - name: playwright-artifacts
        persistentVolumeClaim:
          claimName: playwright-artifacts-pvc
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chronos-playwright-worker
  labels:
    app: chronos-playwright-worker
    component: playwright
spec:
  replicas: 2
  selector:
    matchLabels:
      app: chronos-playwright-worker
      component: playwright
  template:
    metadata:
      labels:
        app: chronos-playwright-worker
        component: playwright
    spec:
      containers:
      - name: playwright-worker
        image: chronos-ai/backend:latest
        command: ["python", "-m", "app.core.playwright_worker"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: chronos-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: chronos-secrets
              key: redis-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: chronos-secrets
              key: secret-key
        - name: PLAYWRIGHT_WORKER_MODE
          value: "true"
        - name: PLAYWRIGHT_BROWSER_POOL_SIZE
          value: "10"
        - name: PLAYWRIGHT_MAX_CONCURRENT_SESSIONS
          value: "50"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        volumeMounts:
        - name: playwright-artifacts
          mountPath: /app/artifacts
      volumes:
      - name: playwright-artifacts
        persistentVolumeClaim:
          claimName: playwright-artifacts-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: chronos-backend-service
spec:
  selector:
    app: chronos-backend
    component: backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: chronos-playwright-worker-service
spec:
  selector:
    app: chronos-playwright-worker
    component: playwright
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 8000
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: playwright-artifacts-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
  storageClassName: fast-ssd
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: chronos-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: chronos-backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: chronos-playwright-worker-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: chronos-playwright-worker
  minReplicas: 2
  maxReplicas: 8
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 75
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 85
```

## 9. Performance Considerations

### 9.1 Resource Management

**Memory Management:**
```python
class ResourceManager:
    """
    Intelligent resource management for Playwright automation
    """
    
    def __init__(self):
        self.memory_limits = {
            'browser_instance': 512,  # MB per browser instance
            'page_context': 128,      # MB per page context
            'total_system': 4096      # MB total system limit
        }
        self.cpu_limits = {
            'browser_instance': 50,   # % per browser instance
            'total_system': 80        # % total system limit
        }
        self.logger = logging.getLogger(__name__)
    
    async def check_resource_availability(self) -> Dict[str, Any]:
        """Check if resources are available for new instance"""
        
        try:
            # Get current system usage
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent()
            
            # Check memory availability
            available_memory_gb = memory.available / (1024**3)
            if available_memory_gb < (self.memory_limits['browser_instance'] * 2) / 1024:
                return {
                    'available': False,
                    'reason': 'Insufficient memory',
                    'available_memory_gb': available_memory_gb
                }
            
            # Check CPU availability
            if cpu_percent > self.cpu_limits['total_system']:
                return {
                    'available': False,
                    'reason': 'High CPU usage',
                    'cpu_percent': cpu_percent
                }
            
            return {
                'available': True,
                'available_memory_gb': available_memory_gb,
                'cpu_percent': cpu_percent
            }
            
        except Exception as e:
            self.logger.error(f"Error checking resource availability: {e}")
            return {'available': False, 'reason': str(e)}
    
    async def optimize_resource_usage(self):
        """Optimize resource usage across all instances"""
        
        try:
            # Clean up unused browser instances
            await self._cleanup_idle_instances()
            
            # Compress memory usage
            await self._compress_memory_usage()
            
            # Garbage collect
            import gc
            gc.collect()
            
        except Exception as e:
            self.logger.error(f"Error optimizing resources: {e}")
    
    async def _cleanup_idle_instances(self):
        """Clean up idle browser instances"""
        
        # This would identify and terminate idle instances
        # based on last activity and resource usage
        pass
    
    async def _compress_memory_usage(self):
        """Attempt to compress memory usage"""
        
        # This would trigger garbage collection and memory optimization
        pass
```

### 9.2 Scaling Strategies

**Horizontal Scaling:**
```python
class PlaywrightScaler:
    """
    Intelligent scaling for Playwright services
    """
    
    def __init__(self, browser_pool_manager: BrowserPoolManager):
        self.browser_pool_manager = browser_pool_manager
        self.scaling_metrics = {
            'cpu_threshold_scale_up': 70,
            'cpu_threshold_scale_down': 30,
            'memory_threshold_scale_up': 80,
            'memory_threshold_scale_down': 40,
            'task_queue_threshold': 10,
            'response_time_threshold': 5000  # ms
        }
        self.logger = logging.getLogger(__name__)
    
    async def evaluate_scaling_needs(self) -> Dict[str, Any]:
        """Evaluate if scaling is needed"""
        
        try:
            current_metrics = await self._get_current_metrics()
            
            scaling_decisions = {
                'scale_up': False,
                'scale_down': False,
                'reasons': [],
                'recommendations': []
            }
            
            # Check CPU usage
            if current_metrics['average_cpu_usage'] > self.scaling_metrics['cpu_threshold_scale_up']:
                scaling_decisions['scale_up'] = True
                scaling_decisions['reasons'].append(f"High CPU usage: {current_metrics['average_cpu_usage']:.1f}%")
                scaling_decisions['recommendations'].append("Add more browser instances")
            
            # Check memory usage
            if current_metrics['average_memory_usage'] > self.scaling_metrics['memory_threshold_scale_up']:
                scaling_decisions['scale_up'] = True
                scaling_decisions['reasons'].append(f"High memory usage: {current_metrics['average_memory_usage']:.1f}%")
                scaling_decisions['recommendations'].append("Add more browser instances")
            
            # Check task queue
            if current_metrics['pending_tasks'] > self.scaling_metrics['task_queue_threshold']:
                scaling_decisions['scale_up'] = True
                scaling_decisions['reasons'].append(f"Large task queue: {current_metrics['pending_tasks']}")
                scaling_decisions['recommendations'].append("Scale up worker instances")
            
            # Check for scale down opportunities
            if (current_metrics['average_cpu_usage'] < self.scaling_metrics['cpu_threshold_scale_down'] and
                current_metrics['average_memory_usage'] < self.scaling_metrics['memory_threshold_scale_down'] and
                current_metrics['pending_tasks'] == 0):
                scaling_decisions['scale_down'] = True
                scaling_decisions['reasons'].append("Low resource usage with empty queue")
                scaling_decisions['recommendations'].append("Scale down worker instances")
            
            return scaling_decisions
            
        except Exception as e:
            self.logger.error(f"Error evaluating scaling needs: {e}")
            return {'scale_up': False, 'scale_down': False, 'error': str(e)}
    
    async def _get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        
        # This would collect actual metrics
        return {
            'average_cpu_usage': 0.0,
            'average_memory_usage': 0.0,
            'pending_tasks': 0,
            'active_sessions': 0,
            'total_instances': 0
        }
```

## 10. Implementation Roadmap

### 10.1 Implementation Approaches

#### **Quick Start Path: External MCP Server**

**Timeline: 1-2 days**

**Objectives:**
- Immediate Playwright automation capabilities
- Minimal integration complexity
- Leverage existing Chronos AI infrastructure

**Deliverables:**
- [ ] Configure external Playwright MCP server
- [ ] Integrate with existing Enhanced MCP Manager
- [ ] Basic API endpoints for Playwright operations
- [ ] Authentication and security integration
- [ ] Monitoring and logging setup

**Technical Tasks:**
1. **MCP Server Configuration**
   - Add Playwright MCP server to configuration
   - Configure authentication and connection pooling
   - Set up load balancing with existing servers

2. **API Integration**
   - Create thin wrapper endpoints for Playwright operations
   - Integrate with existing authentication system
   - Add request/response logging and monitoring

3. **Security Integration**
   - URL validation through existing security manager
   - User permission checks
   - Rate limiting integration

**Success Criteria:**
- Playwright automation available through existing API
- Full integration with Chronos AI security and monitoring
- Seamless user experience

#### **Production Path: Internal Implementation**

**Timeline: 6-8 weeks**

**Objectives:**
- Establish full Playwright integration with existing MCP infrastructure
- Implement enterprise-grade security and monitoring
- Advanced features like intelligent pooling and batch operations

**Deliverables:**
- [ ] Database models for Playwright sessions, tasks, artifacts, and pools
- [ ] Pydantic schemas for Playwright operations
- [ ] Advanced browser automation endpoints
- [ ] Intelligent browser instance pooling
- [ ] Secure artifact management with encryption
- [ ] Comprehensive monitoring and metrics

### 10.2 Phase 1: Foundation (Weeks 1-2)

**Objectives:**
- Establish basic Playwright integration with existing MCP infrastructure
- Implement core database models and schemas
- Create basic browser automation endpoints

**Deliverables:**
- [ ] Database models for Playwright sessions, tasks, artifacts, and pools
- [ ] Pydantic schemas for Playwright operations
- [ ] Basic Playwright API endpoints (`/enhanced-mcp/playwright/automation/`)
- [ ] Integration with existing `OperationType` enum
- [ ] Basic security validation for URLs and JavaScript
- [ ] Simple browser instance management

**Technical Tasks:**
1. **Database Schema Creation**
   - Create `PlaywrightBrowserSession`, `PlaywrightAutomationTask`, `PlaywrightArtifact`, `PlaywrightBrowserPool` models
   - Add migration scripts for new tables
   - Update existing MCP schemas to include Playwright types

2. **Core API Development**
   - Implement `PlaywrightAutomationTaskRequest/Response` schemas
   - Create `/enhanced-mcp/playwright/automation/` endpoint
   - Add basic session management endpoints
   - Integrate with existing `EnhancedMCPManager`

3. **Security Foundation**
   - Implement `PlaywrightSecurityManager` with basic URL validation
   - Add JavaScript sanitization
   - Create security rule loading from database

4. **Basic Browser Management**
   - Implement simple browser instance management
   - Add basic session lifecycle management
   - Create artifact storage foundation

**Success Criteria:**
- Playwright automation tasks can be executed through MCP API
- Database models properly track sessions, tasks, and artifacts
- Basic security validation prevents malicious URLs/scripts
- Integration with existing authentication and monitoring systems

### 10.2 Phase 2: Core Features (Weeks 3-4)

**Objectives:**
- Implement advanced browser automation features
- Add comprehensive session management
- Create artifact management system
- Enhance security and monitoring

**Deliverables:**
- [ ] Advanced browser automation (multi-browser, viewport control, etc.)
- [ ] Comprehensive session management with reuse and persistence
- [ ] Secure artifact storage with encryption
- [ ] Enhanced security with comprehensive validation
- [ ] Performance monitoring and metrics collection
- [ ] WebSocket support for real-time browser control

**Technical Tasks:**
1. **Advanced Browser Features**
   - Multi-browser support (Chromium, Firefox, WebKit)
   - Custom viewport and user agent configuration
   - JavaScript execution with security validation
   - Screenshot and PDF generation
   - Video recording capabilities

2. **Session Management Enhancement**
   - Session persistence and reuse
   - Advanced session lifecycle management
   - Session pooling and optimization
   - Automatic cleanup of expired sessions

3. **Artifact Management**
   - Implement `SecureArtifactManager` with encryption
   - Support for multiple artifact types
   - Automatic cleanup and lifecycle management
   - Access control and permissions

4. **Security Enhancement**
   - Comprehensive URL validation with patterns
   - Advanced JavaScript sanitization
   - Resource access control
   - Permission-based authorization

5. **Monitoring and Metrics**
   - Implement `PlaywrightMetricsCollector`
   - Add health monitoring with `PlaywrightHealthMonitor`
   - Performance metrics and alerting
   - Integration with existing monitoring infrastructure

**Success Criteria:**
- Full-featured browser automation with security
- Secure artifact storage and retrieval
- Comprehensive session management
- Real-time monitoring and health checks

### 10.3 Phase 3: Advanced Features (Weeks 5-6)

**Objectives:**
- Implement intelligent browser pooling
- Add batch operations support
- Create advanced performance optimization
- Implement scaling strategies

**Deliverables:**
- [ ] Intelligent browser instance pooling
- [ ] Batch automation operations
- [ ] Advanced resource management
- [ ] Performance optimization
- [ ] Auto-scaling capabilities

**Technical Tasks:**
1. **Browser Pool Management**
   - Implement `BrowserPoolManager` with intelligent pooling
   - Resource monitoring and limits
   - Health checking and recovery
   - Load balancing across instances

2. **Batch Operations**
   - Support for multiple concurrent automation tasks
   - Batch session management
   - Parallel artifact processing
   - Result aggregation and reporting

3. **Resource Management**
   - Implement `ResourceManager` for system optimization
   - Memory and CPU usage monitoring
   - Automatic resource cleanup
   - Performance tuning

4. **Scaling Implementation**
   - Implement `PlaywrightScaler` for horizontal scaling
   - Auto-scaling based on metrics
   - Dynamic resource allocation
   - Performance optimization

**Success Criteria:**
- Efficient browser instance pooling
- Batch operations with high throughput
- Automatic resource optimization
- Dynamic scaling based on demand

### 10.4 Phase 4: Integration & Production (Weeks 7-8)

**Objectives:**
- Production deployment configuration
- Comprehensive testing
- Documentation and examples
- Security audit and optimization

**Deliverables:**
- [ ] Production-ready Docker/Kubernetes deployment
- [ ] Comprehensive test suite
- [ ] Complete documentation
- [ ] Security audit and hardening
- [ ] Performance benchmarking
- [ ] Monitoring dashboards

**Technical Tasks:**
1. **Production Deployment**
   - Docker containerization with Playwright dependencies
   - Kubernetes manifests with resource limits
   - Production configuration management
   - Health checks and monitoring

2. **Testing and Validation**
   - Unit tests for all components
   - Integration tests with existing MCP infrastructure
   - Performance benchmarks
   - Security penetration testing

3. **Documentation**
   - API documentation with examples
   - Deployment guides
   - Architecture documentation
   - Troubleshooting guides

4. **Security Hardening**
   - Comprehensive security audit
   - Vulnerability assessment
   - Performance security optimization
   - Compliance validation

**Success Criteria:**
- Production-ready deployment
- Comprehensive test coverage
- Complete documentation
- Security validation
- Performance benchmarks

### 10.5 Implementation Timeline

```mermaid
gantt
    title Playwright MCP Server Implementation Timeline
    dateFormat  YYYY-MM-DD
    section Phase 1: Foundation
    Database Models           :done, db, 2024-01-01, 3d
    Basic API Endpoints       :done, api, 2024-01-02, 4d
    Security Foundation       :done, sec, 2024-01-03, 3d
    Browser Management        :done, browser, 2024-01-04, 2d
    
    section Phase 2: Core Features
    Advanced Browser Features :active, adv, 2024-01-08, 5d
    Session Management        :active, session, 2024-01-10, 4d
    Artifact Management       :active, artifact, 2024-01-12, 3d
    Security Enhancement      :active, sec2, 2024-01-14, 3d
    Monitoring & Metrics      :active, monitor, 2024-01-16, 2d
    
    section Phase 3: Advanced Features
    Browser Pool Management   :pool, 2024-01-22, 4d
    Batch Operations          :batch, 2024-01-24, 3d
    Resource Management       :resource, 2024-01-26, 3d
    Scaling Implementation    :scale, 2024-01-28, 3d
    
    section Phase 4: Production
    Deployment Config         :deploy, 2024-02-01, 3d
    Testing & Validation      :test, 2024-02-03, 4d
    Documentation            :docs, 2024-02-05, 3d
    Security Hardening       :harden, 2024-02-07, 2d
```

### 10.6 Risk Mitigation

**Technical Risks:**
1. **Browser Resource Consumption**
   - Mitigation: Implement comprehensive resource monitoring and limits
   - Contingency: Auto-scaling and resource optimization

2. **Security Vulnerabilities**
   - Mitigation: Multi-layer security validation and regular audits
   - Contingency: Rapid security patch deployment procedures

3. **Performance Bottlenecks**
   - Mitigation: Comprehensive performance testing and optimization
   - Contingency: Horizontal scaling and load balancing

4. **Integration Complexity**
   - Mitigation: Incremental integration with extensive testing
   - Contingency: Rollback procedures and compatibility layers

**Operational Risks:**
1. **Deployment Complexity**
   - Mitigation: Comprehensive deployment documentation and automation
   - Contingency: Staged deployment with monitoring

2. **Maintenance Overhead**
   - Mitigation: Automated monitoring and alerting systems
   - Contingency: Maintenance procedures and runbooks

This comprehensive architecture design provides a production-ready foundation for integrating Playwright browser automation into the Chronos AI MCP infrastructure, ensuring scalability, security, and maintainability while leveraging existing architectural patterns.
