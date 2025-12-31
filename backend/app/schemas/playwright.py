from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PlaywrightTaskStatus(str, Enum):
    """Status enumeration for Playwright automation tasks"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class PlaywrightTaskType(str, Enum):
    """Type enumeration for automation tasks"""
    SCRAPING = "scraping"
    AUTOMATION = "automation"
    TESTING = "testing"
    MONITORING = "monitoring"
    EXTRACTION = "extraction"
    INTERACTION = "interaction"


class PlaywrightArtifactType(str, Enum):
    """Type enumeration for generated artifacts"""
    SCREENSHOT = "screenshot"
    PDF = "pdf"
    HAR = "har"
    VIDEO = "video"
    TRACE = "trace"
    REPORT = "report"
    JSON = "json"
    HTML = "html"


class BrowserType(str, Enum):
    """Supported browser types"""
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


class DeviceType(str, Enum):
    """Supported device types"""
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"


# Base schemas
class PlaywrightBrowserSessionBase(BaseModel):
    """Base schema for browser session operations"""
    session_name: str = Field(..., description="Human-readable session name")
    target_url: HttpUrl = Field(..., description="Target URL to navigate to")
    browser_type: BrowserType = Field(BrowserType.CHROMIUM, description="Browser type to use")
    device_type: DeviceType = Field(DeviceType.DESKTOP, description="Device type to simulate")
    viewport_width: int = Field(1920, description="Browser viewport width in pixels")
    viewport_height: int = Field(1080, description="Browser viewport height in pixels")
    user_agent: Optional[str] = Field(None, description="Custom user agent string")
    language: Optional[str] = Field("en-US", description="Browser language preference")
    timezone: Optional[str] = Field("UTC", description="Browser timezone")
    viewport_options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional viewport configuration")
    cookies: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Initial cookies to set")
    headers: Optional[Dict[str, str]] = Field(default_factory=dict, description="Custom HTTP headers")
    proxy_url: Optional[str] = Field(None, description="Proxy server URL")
    timeout: int = Field(30000, description="Session timeout in milliseconds")
    headless: bool = Field(True, description="Run browser in headless mode")
    enable_javascript: bool = Field(True, description="Enable JavaScript execution")
    enable_images: bool = Field(True, description="Enable image loading")
    enable_css: bool = Field(True, description="Enable CSS loading")
    screenshot_on_error: bool = Field(True, description="Take screenshot on error")
    record_video: bool = Field(False, description="Record video of session")
    record_trace: bool = Field(False, description="Record detailed trace")


class PlaywrightAutomationTaskBase(BaseModel):
    """Base schema for automation task operations"""
    task_name: str = Field(..., description="Human-readable task name")
    task_type: PlaywrightTaskType = Field(..., description="Type of automation task")
    description: Optional[str] = Field(None, description="Detailed task description")
    target_url: HttpUrl = Field(..., description="Target URL for automation")
    script_steps: List[Dict[str, Any]] = Field(..., description="Automation script steps")
    wait_conditions: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Wait conditions")
    error_handling: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Error handling strategy")
    output_format: Optional[str] = Field("json", description="Expected output format")
    retry_count: int = Field(0, description="Number of retries on failure")
    priority: int = Field(5, description="Task priority (1-10, higher is more important)")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled execution time")
    timeout: int = Field(300000, description="Task timeout in milliseconds")
    environment_vars: Optional[Dict[str, str]] = Field(default_factory=dict, description="Environment variables")


class PlaywrightArtifactBase(BaseModel):
    """Base schema for artifact operations"""
    artifact_name: str = Field(..., description="Human-readable artifact name")
    artifact_type: PlaywrightArtifactType = Field(..., description="Type of generated artifact")
    description: Optional[str] = Field(None, description="Artifact description")
    file_path: Optional[str] = Field(None, description="Path to artifact file")
    content: Optional[str] = Field(None, description="Artifact content")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Artifact metadata")
    compression: bool = Field(False, description="Whether artifact is compressed")
    encryption: bool = Field(False, description="Whether artifact is encrypted")
    retention_days: int = Field(30, description="Days to retain artifact")


class PlaywrightBrowserPoolBase(BaseModel):
    """Base schema for browser pool operations"""
    pool_name: str = Field(..., description="Human-readable pool name")
    pool_type: DeviceType = Field(..., description="Pool device type")
    max_browsers: int = Field(10, description="Maximum concurrent browsers")
    browser_type: BrowserType = Field(BrowserType.CHROMIUM, description="Browser type for pool")
    min_idle_browsers: int = Field(2, description="Minimum idle browsers to maintain")
    health_check_interval: int = Field(60, description="Health check interval in seconds")
    warm_up_browsers: int = Field(0, description="Number of browsers to pre-warm")
    pool_options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional pool configuration")
    auto_scaling: bool = Field(True, description="Enable automatic scaling")
    scaling_policy: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Auto-scaling policy")


# Create schemas
class PlaywrightBrowserSessionCreate(PlaywrightBrowserSessionBase):
    """Schema for creating a new browser session"""
    pass


class PlaywrightAutomationTaskCreate(PlaywrightAutomationTaskBase):
    """Schema for creating a new automation task"""
    pass


class PlaywrightArtifactCreate(PlaywrightArtifactBase):
    """Schema for creating a new artifact"""
    pass


class PlaywrightBrowserPoolCreate(PlaywrightBrowserPoolBase):
    """Schema for creating a new browser pool"""
    pass


# Update schemas
class PlaywrightBrowserSessionUpdate(BaseModel):
    """Schema for updating a browser session"""
    session_name: Optional[str] = None
    target_url: Optional[HttpUrl] = None
    viewport_width: Optional[int] = None
    viewport_height: Optional[int] = None
    user_agent: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    cookies: Optional[List[Dict[str, Any]]] = None
    headers: Optional[Dict[str, str]] = None
    proxy_url: Optional[str] = None
    timeout: Optional[int] = None
    headless: Optional[bool] = None


class PlaywrightAutomationTaskUpdate(BaseModel):
    """Schema for updating an automation task"""
    task_name: Optional[str] = None
    description: Optional[str] = None
    script_steps: Optional[List[Dict[str, Any]]] = None
    wait_conditions: Optional[List[Dict[str, Any]]] = None
    error_handling: Optional[Dict[str, Any]] = None
    retry_count: Optional[int] = None
    priority: Optional[int] = None
    scheduled_at: Optional[datetime] = None
    timeout: Optional[int] = None
    environment_vars: Optional[Dict[str, str]] = None


class PlaywrightArtifactUpdate(BaseModel):
    """Schema for updating an artifact"""
    artifact_name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    retention_days: Optional[int] = None


class PlaywrightBrowserPoolUpdate(BaseModel):
    """Schema for updating a browser pool"""
    pool_name: Optional[str] = None
    max_browsers: Optional[int] = None
    min_idle_browsers: Optional[int] = None
    health_check_interval: Optional[int] = None
    warm_up_browsers: Optional[int] = None
    pool_options: Optional[Dict[str, Any]] = None
    auto_scaling: Optional[bool] = None
    scaling_policy: Optional[Dict[str, Any]] = None


# Response schemas
class PlaywrightBrowserSessionResponse(PlaywrightBrowserSessionBase):
    """Schema for browser session response"""
    id: int
    session_id: str
    agent_id: int
    status: str = "created"
    current_url: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlaywrightAutomationTaskResponse(PlaywrightAutomationTaskBase):
    """Schema for automation task response"""
    id: int
    task_id: str
    agent_id: int
    session_id: Optional[str] = None
    status: PlaywrightTaskStatus = PlaywrightTaskStatus.PENDING
    progress: int = Field(0, description="Task completion percentage (0-100)")
    current_step: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlaywrightArtifactResponse(PlaywrightArtifactBase):
    """Schema for artifact response"""
    id: int
    artifact_id: str
    task_id: Optional[int] = None
    session_id: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    download_url: Optional[str] = None
    expiry_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlaywrightBrowserPoolResponse(PlaywrightBrowserPoolBase):
    """Schema for browser pool response"""
    id: int
    pool_id: str
    current_browsers: int = Field(0, description="Currently active browsers")
    idle_browsers: int = Field(0, description="Currently idle browsers")
    total_sessions: int = Field(0, description="Total sessions handled")
    avg_session_duration: Optional[float] = None
    success_rate: Optional[float] = None
    last_health_check: Optional[datetime] = None
    health_status: str = "unknown"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Bulk operation schemas
class PlaywrightBulkTaskCreate(BaseModel):
    """Schema for creating multiple automation tasks"""
    tasks: List[PlaywrightAutomationTaskCreate]
    parallel_execution: bool = Field(False, description="Execute tasks in parallel")


class PlaywrightBulkArtifactResponse(BaseModel):
    """Schema for bulk artifact operations"""
    artifacts: List[PlaywrightArtifactResponse]
    total_count: int
    successful_count: int
    failed_count: int


# Execution and monitoring schemas
class PlaywrightSessionExecution(BaseModel):
    """Schema for session execution request"""
    session_id: str
    commands: List[Dict[str, Any]]
    timeout: Optional[int] = None


class PlaywrightTaskExecution(BaseModel):
    """Schema for task execution request"""
    task_id: str
    force_retry: bool = Field(False, description="Force retry even if previously failed")
    override_timeout: Optional[int] = None


class PlaywrightExecutionResult(BaseModel):
    """Schema for execution results"""
    success: bool
    execution_id: str
    session_id: Optional[str] = None
    task_id: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    artifacts: List[PlaywrightArtifactResponse] = Field(default_factory=list)
    execution_time: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# Health and status schemas
class PlaywrightHealthStatus(BaseModel):
    """Schema for Playwright service health status"""
    service_status: str
    browser_pool_status: str
    active_sessions: int
    active_tasks: int
    queued_tasks: int
    total_browsers: int
    healthy_browsers: int
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None
    timestamp: datetime


class PlaywrightPoolMetrics(BaseModel):
    """Schema for browser pool metrics"""
    pool_id: str
    current_load: float
    avg_response_time: float
    throughput: float
    error_rate: float
    availability: float
    timestamp: datetime


# Search and filter schemas
class PlaywrightSessionSearch(BaseModel):
    """Schema for searching browser sessions"""
    agent_id: Optional[int] = None
    status: Optional[str] = None
    browser_type: Optional[BrowserType] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search_text: Optional[str] = None
    limit: int = 50
    offset: int = 0


class PlaywrightTaskSearch(BaseModel):
    """Schema for searching automation tasks"""
    agent_id: Optional[int] = None
    task_type: Optional[PlaywrightTaskType] = None
    status: Optional[PlaywrightTaskStatus] = None
    priority: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search_text: Optional[str] = None
    limit: int = 50
    offset: int = 0


class PlaywrightArtifactSearch(BaseModel):
    """Schema for searching artifacts"""
    artifact_type: Optional[PlaywrightArtifactType] = None
    task_id: Optional[int] = None
    session_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search_text: Optional[str] = None
    limit: int = 50
    offset: int = 0


# Configuration schemas
class PlaywrightConfiguration(BaseModel):
    """Schema for Playwright configuration"""
    max_concurrent_sessions: int = Field(50, description="Maximum concurrent browser sessions")
    default_timeout: int = Field(30000, description="Default timeout in milliseconds")
    screenshot_quality: int = Field(90, description="Screenshot quality (1-100)")
    video_quality: str = Field("medium", description="Video recording quality")
    enable_tracing: bool = Field(False, description="Enable detailed tracing")
    enable_metrics: bool = Field(True, description="Enable performance metrics")
    cleanup_interval: int = Field(3600, description="Cleanup interval in seconds")
    max_session_duration: int = Field(3600000, description="Max session duration in milliseconds")
    retry_attempts: int = Field(3, description="Default retry attempts")
    user_agent_rotation: bool = Field(True, description="Rotate user agents")
    proxy_rotation: bool = Field(False, description="Rotate proxy servers")
    storage_cleanup: bool = Field(True, description="Auto cleanup browser storage")
    security_options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Browser security options")


# Error schemas
class PlaywrightError(BaseModel):
    """Schema for Playwright errors"""
    error_code: str
    error_message: str
    error_details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    session_id: Optional[str] = None
    task_id: Optional[str] = None


class PlaywrightErrorResponse(BaseModel):
    """Schema for error responses"""
    success: False
    error: PlaywrightError
    suggestions: Optional[List[str]] = None
