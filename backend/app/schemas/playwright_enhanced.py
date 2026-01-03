"""
Enhanced Playwright Schemas with Comprehensive Tool Metadata

This module provides enhanced schemas for Playwright browser automation including:
- Tool Definitions: Complete metadata for all browser automation tools
- Request/Response Schemas: Enhanced schemas for API endpoints
- Validation Schemas: Comprehensive input validation and security
- Error Schemas: Detailed error handling and reporting
"""

from pydantic import BaseModel, Field, HttpUrl, validator, root_validator
from typing import Optional, List, Dict, Any, Union, Tuple
from datetime import datetime
from enum import Enum
import re


# Enums
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


class ToolCategory(str, Enum):
    """Browser automation tool categories"""
    NAVIGATION = "Navigation"
    INTERACTION = "Interaction"
    EXTRACTION = "Extraction"
    MULTIMEDIA = "Multimedia"
    SYNCHRONIZATION = "Synchronization"
    UTILITY = "Utility"


class ToolStatus(str, Enum):
    """Tool status enumeration"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    BETA = "beta"
    EXPERIMENTAL = "experimental"


class ValidationLevel(str, Enum):
    """Validation levels for input sanitization"""
    STRICT = "strict"
    MODERATE = "moderate"
    LENIENT = "lenient"


# Base schemas with enhanced validation
class PlaywrightBaseModel(BaseModel):
    """Base model with common functionality"""
    
    class Config:
        use_enum_values = True
        validate_assignment = True
        extra = "forbid"
    
    @validator("*", pre=True, always=True)
    def validate_not_empty(cls, v, field):
        """Validate that string fields are not empty"""
        if field.type_ == str and isinstance(v, str) and not v.strip():
            raise ValueError(f"Field {field.name} cannot be empty")
        return v


class ToolParameterDefinition(BaseModel):
    """Definition for a tool parameter"""
    type: str = Field(..., description="Parameter data type")
    required: bool = Field(False, description="Whether parameter is required")
    description: str = Field(..., description="Parameter description")
    default: Any = Field(None, description="Default value")
    min: Optional[Union[int, float]] = Field(None, description="Minimum value")
    max: Optional[Union[int, float]] = Field(None, description="Maximum value")
    min_length: Optional[int] = Field(None, description="Minimum string length")
    max_length: Optional[int] = Field(None, description="Maximum string length")
    pattern: Optional[str] = Field(None, description="Regex pattern validation")
    options: Optional[List[Any]] = Field(None, description="Allowed values")
    validation_level: ValidationLevel = Field(ValidationLevel.MODERATE, description="Validation strictness")


class ToolDefinition(PlaywrightBaseModel):
    """Complete definition of a browser automation tool"""
    name: str = Field(..., description="Tool name", min_length=1, max_length=100)
    description: str = Field(..., description="Tool description", min_length=10, max_length=1000)
    category: ToolCategory = Field(..., description="Tool category")
    version: str = Field("1.0.0", description="Tool version")
    status: ToolStatus = Field(ToolStatus.ACTIVE, description="Tool status")
    parameters: Dict[str, ToolParameterDefinition] = Field(..., description="Tool parameters")
    examples: List[Dict[str, Any]] = Field(default_factory=list, description="Usage examples")
    tags: List[str] = Field(default_factory=list, description="Tool tags")
    icon: str = Field("🔧", description="Tool icon")
    estimated_duration: Optional[int] = Field(None, description="Estimated execution time in seconds")
    requires_session: bool = Field(True, description="Whether tool requires browser session")
    security_level: ValidationLevel = Field(ValidationLevel.MODERATE, description="Security validation level")
    rate_limit: Optional[int] = Field(None, description="Rate limit per minute")
    timeout_default: int = Field(30000, description="Default timeout in milliseconds")
    retry_policy: Dict[str, Any] = Field(
        default_factory=lambda: {"max_retries": 3, "retry_delay": 1.0, "backoff_factor": 2.0},
        description="Retry configuration"
    )
    validation_rules: Dict[str, Any] = Field(default_factory=dict, description="Custom validation rules")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


class ToolExecutionRequest(PlaywrightBaseModel):
    """Request schema for tool execution"""
    session_id: str = Field(..., description="Browser session ID", min_length=1, max_length=255)
    tool_name: str = Field(..., description="Tool to execute", min_length=1, max_length=100)
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    timeout: Optional[int] = Field(None, description="Override timeout in milliseconds")
    validate_input: bool = Field(True, description="Whether to validate input")
    capture_console: bool = Field(False, description="Whether to capture console logs")
    capture_screenshots: bool = Field(False, description="Whether to capture screenshots on error")
    priority: int = Field(5, description="Execution priority (1-10)", ge=1, le=10)
    
    @validator("tool_name")
    def validate_tool_name(cls, v):
        """Validate tool name format"""
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", v):
            raise ValueError("Tool name must start with a letter and contain only letters, numbers, and underscores")
        return v
    
    @validator("timeout")
    def validate_timeout(cls, v):
        """Validate timeout range"""
        if v is not None and (v < 1000 or v > 300000):  # 1 second to 5 minutes
            raise ValueError("Timeout must be between 1000 and 300000 milliseconds")
        return v


class ToolExecutionResult(PlaywrightBaseModel):
    """Result schema for tool execution"""
    success: bool = Field(..., description="Whether execution was successful")
    execution_id: str = Field(..., description="Unique execution ID")
    tool_name: str = Field(..., description="Executed tool name")
    session_id: str = Field(..., description="Browser session ID")
    result: Dict[str, Any] = Field(default_factory=dict, description="Tool execution result")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")
    execution_time: float = Field(..., description="Execution time in seconds")
    error: Optional[str] = Field(None, description="Error message if failed")
    error_code: Optional[str] = Field(None, description="Error code")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Detailed error information")
    console_logs: List[Dict[str, Any]] = Field(default_factory=list, description="Console logs")
    screenshot_base64: Optional[str] = Field(None, description="Screenshot on error (base64)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Execution timestamp")


# Navigation Tool Schemas
class NavigateRequest(PlaywrightBaseModel):
    """Request schema for navigation tool"""
    session_id: str = Field(..., description="Browser session ID", min_length=1, max_length=255)
    url: HttpUrl = Field(..., description="URL to navigate to")
    wait_until: str = Field("load", description="When to consider navigation complete")
    timeout: int = Field(30000, description="Navigation timeout in milliseconds", ge=1000, le=120000)
    
    @validator("wait_until")
    def validate_wait_until(cls, v):
        """Validate wait_until options"""
        valid_options = ["load", "domcontentloaded", "networkidle"]
        if v not in valid_options:
            raise ValueError(f"wait_until must be one of: {', '.join(valid_options)}")
        return v


class NavigationResult(ToolExecutionResult):
    """Result schema for navigation operations"""
    url: Optional[str] = Field(None, description="Final URL after navigation")
    title: Optional[str] = Field(None, description="Page title")
    status: Optional[int] = Field(None, description="HTTP status code")
    navigation_time: Optional[float] = Field(None, description="Navigation time in seconds")


# Interaction Tool Schemas
class ClickRequest(PlaywrightBaseModel):
    """Request schema for click tool"""
    session_id: str = Field(..., description="Browser session ID", min_length=1, max_length=255)
    selector: str = Field(..., description="CSS selector for element", min_length=1, max_length=500)
    button: str = Field("left", description="Mouse button to use")
    click_count: int = Field(1, description="Number of clicks", ge=1, le=5)
    delay: int = Field(0, description="Delay between clicks in milliseconds", ge=0, le=1000)
    timeout: int = Field(30000, description="Timeout for finding element", ge=1000, le=120000)
    
    @validator("button")
    def validate_button(cls, v):
        """Validate button options"""
        valid_buttons = ["left", "right", "middle"]
        if v not in valid_buttons:
            raise ValueError(f"button must be one of: {', '.join(valid_buttons)}")
        return v
    
    @validator("selector")
    def validate_selector(cls, v, values):
        """Validate CSS selector for security"""
        # Check for potentially dangerous patterns
        dangerous_patterns = [
            r'<[^>]*>',  # HTML tags
            r'javascript:',  # JavaScript protocol
            r'expression\(',  # CSS expressions
            r'url\s*\(',  # CSS url functions
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError(f"Potentially dangerous selector pattern detected: {pattern}")
        
        return v


class TypeRequest(PlaywrightBaseModel):
    """Request schema for typing tool"""
    session_id: str = Field(..., description="Browser session ID", min_length=1, max_length=255)
    selector: str = Field(..., description="CSS selector for input", min_length=1, max_length=500)
    text: str = Field(..., description="Text to type", min_length=1, max_length=10000)
    clear_first: bool = Field(True, description="Clear field before typing")
    delay: int = Field(0, description="Delay between keystrokes", ge=0, le=100)
    timeout: int = Field(30000, description="Timeout for finding element", ge=1000, le=120000)


class SelectRequest(PlaywrightBaseModel):
    """Request schema for select tool"""
    session_id: str = Field(..., description="Browser session ID", min_length=1, max_length=255)
    selector: str = Field(..., description="CSS selector for select element", min_length=1, max_length=500)
    value: Optional[str] = Field(None, description="Option value to select")
    label: Optional[str] = Field(None, description="Option label to select")
    timeout: int = Field(30000, description="Timeout for finding element", ge=1000, le=120000)
    
    @root_validator
    def validate_value_or_label(cls, values):
        """Ensure either value or label is provided"""
        if not values.get("value") and not values.get("label"):
            raise ValueError("Either 'value' or 'label' must be provided")
        return values


class DragAndDropRequest(PlaywrightBaseModel):
    """Request schema for drag and drop tool"""
    session_id: str = Field(..., description="Browser session ID", min_length=1, max_length=255)
    source_selector: str = Field(..., description="CSS selector for source element", min_length=1, max_length=500)
    target_selector: str = Field(..., description="CSS selector for target element", min_length=1, max_length=500)
    timeout: int = Field(30000, description="Timeout for finding elements", ge=1000, le=120000)


# Extraction Tool Schemas
class GetTextRequest(PlaywrightBaseModel):
    """Request schema for text extraction tool"""
    session_id: str = Field(..., description="Browser session ID", min_length=1, max_length=255)
    selector: str = Field(..., description="CSS selector for elements", min_length=1, max_length=500)
    attribute: str = Field("text", description="Attribute to extract")
    multiple: bool = Field(False, description="Extract from multiple elements")
    timeout: int = Field(30000, description="Timeout for finding elements", ge=1000, le=120000)
    
    @validator("attribute")
    def validate_attribute(cls, v):
        """Validate attribute options"""
        valid_attributes = ["text", "href", "src", "title", "alt", "value", "innerHTML", "outerHTML"]
        if v not in valid_attributes:
            raise ValueError(f"attribute must be one of: {', '.join(valid_attributes)}")
        return v


class GetAttributeRequest(PlaywrightBaseModel):
    """Request schema for attribute extraction tool"""
    session_id: str = Field(..., description="Browser session ID", min_length=1, max_length=255)
    selector: str = Field(..., description="CSS selector for element", min_length=1, max_length=500)
    attribute: str = Field(..., description="Attribute name to get", min_length=1, max_length=100)
    multiple: bool = Field(False, description="Get attribute from multiple elements")
    timeout: int = Field(30000, description="Timeout for finding elements", ge=1000, le=120000)


class GetPageContentRequest(PlaywrightBaseModel):
    """Request schema for page content extraction tool"""
    session_id: str = Field(..., description="Browser session ID", min_length=1, max_length=255)
    content_type: str = Field("text", description="Type of content to extract")
    selectors: Optional[Dict[str, str]] = Field(None, description="Specific selectors to extract")
    include_metadata: bool = Field(True, description="Include page metadata")
    
    @validator("content_type")
    def validate_content_type(cls, v):
        """Validate content type options"""
        valid_types = ["text", "html", "markdown", "json"]
        if v not in valid_types:
            raise ValueError(f"content_type must be one of: {', '.join(valid_types)}")
        return v


# Multimedia Tool Schemas
class ScreenshotRequest(PlaywrightBaseModel):
    """Request schema for screenshot tool"""
    session_id: str = Field(..., description="Browser session ID", min_length=1, max_length=255)
    full_page: bool = Field(False, description="Take screenshot of entire page")
    selector: Optional[str] = Field(None, description="CSS selector for specific element")
    quality: int = Field(90, description="Screenshot quality (1-100)", ge=1, le=100)
    format: str = Field("png", description="Screenshot format")
    timeout: int = Field(30000, description="Timeout for taking screenshot", ge=1000, le=120000)
    
    @validator("format")
    def validate_format(cls, v):
        """Validate format options"""
        valid_formats = ["png", "jpeg", "webp"]
        if v not in valid_formats:
            raise ValueError(f"format must be one of: {', '.join(valid_formats)}")
        return v


class PDFRequest(PlaywrightBaseModel):
    """Request schema for PDF generation tool"""
    session_id: str = Field(..., description="Browser session ID", min_length=1, max_length=255)
    full_page: bool = Field(False, description="Include entire page in PDF")
    format: str = Field("A4", description="PDF page format")
    landscape: bool = Field(False, description="Use landscape orientation")
    margin: Optional[Dict[str, str]] = Field(None, description="Page margins in mm")
    timeout: int = Field(60000, description="Timeout for PDF generation", ge=5000, le=300000)
    
    @validator("format")
    def validate_format(cls, v):
        """Validate PDF format options"""
        valid_formats = ["A4", "Letter", "Legal", "A3", "A5"]
        if v not in valid_formats:
            raise ValueError(f"format must be one of: {', '.join(valid_formats)}")
        return v


class RecordVideoRequest(PlaywrightBaseModel):
    """Request schema for video recording tool"""
    session_id: str = Field(..., description="Browser session ID", min_length=1, max_length=255)
    action: str = Field(..., description="Action to perform")
    duration: Optional[int] = Field(None, description="Recording duration in seconds", ge=1, le=3600)
    fps: int = Field(30, description="Frames per second", ge=1, le=60)
    quality: str = Field("high", description="Video quality")
    
    @validator("action")
    def validate_action(cls, v):
        """Validate video action options"""
        valid_actions = ["start", "stop"]
        if v not in valid_actions:
            raise ValueError(f"action must be one of: {', '.join(valid_actions)}")
        return v
    
    @validator("quality")
    def validate_quality(cls, v):
        """Validate quality options"""
        valid_qualities = ["low", "medium", "high", "ultra"]
        if v not in valid_qualities:
            raise ValueError(f"quality must be one of: {', '.join(valid_qualities)}")
        return v


# Synchronization Tool Schemas
class WaitForSelectorRequest(PlaywrightBaseModel):
    """Request schema for wait for selector tool"""
    session_id: str = Field(..., description="Browser session ID", min_length=1, max_length=255)
    selector: str = Field(..., description="CSS selector to wait for", min_length=1, max_length=500)
    timeout: int = Field(30000, description="Maximum wait time", ge=1000, le=120000)
    state: str = Field("visible", description="Element state to wait for")
    
    @validator("state")
    def validate_state(cls, v):
        """Validate state options"""
        valid_states = ["attached", "detached", "visible", "hidden"]
        if v not in valid_states:
            raise ValueError(f"state must be one of: {', '.join(valid_states)}")
        return v


class WaitForLoadStateRequest(PlaywrightBaseModel):
    """Request schema for wait for load state tool"""
    session_id: str = Field(..., description="Browser session ID", min_length=1, max_length=255)
    state: str = Field(..., description="Load state to wait for")
    timeout: int = Field(30000, description="Maximum wait time", ge=1000, le=120000)
    
    @validator("state")
    def validate_state(cls, v):
        """Validate load state options"""
        valid_states = ["load", "domcontentloaded", "networkidle"]
        if v not in valid_states:
            raise ValueError(f"state must be one of: {', '.join(valid_states)}")
        return v


class WaitForTimeoutRequest(PlaywrightBaseModel):
    """Request schema for timeout wait tool"""
    session_id: str = Field(..., description="Browser session ID", min_length=1, max_length=255)
    duration: int = Field(..., description="Wait duration in milliseconds", ge=1, le=300000)


# Session Management Schemas
class CreateSessionRequest(PlaywrightBaseModel):
    """Request schema for creating browser session"""
    session_name: str = Field(..., description="Human-readable session name", min_length=1, max_length=255)
    browser_type: BrowserType = Field(BrowserType.CHROMIUM, description="Browser type")
    viewport_width: int = Field(1920, description="Browser viewport width", ge=800, le=4096)
    viewport_height: int = Field(1080, description="Browser viewport height", ge=600, le=2160)
    user_agent: Optional[str] = Field(None, description="Custom user agent string", max_length=500)
    headless: bool = Field(True, description="Run browser in headless mode")
    enable_javascript: bool = Field(True, description="Enable JavaScript")
    enable_images: bool = Field(True, description="Enable image loading")
    enable_css: bool = Field(True, description="Enable CSS loading")
    proxy_url: Optional[str] = Field(None, description="Proxy server URL")
    timezone: Optional[str] = Field(None, description="Browser timezone", max_length=50)
    language: Optional[str] = Field("en-US", description="Browser language", max_length=10)
    timeout: int = Field(30000, description="Session timeout in milliseconds", ge=5000, le=300000)


class SessionResponse(PlaywrightBaseModel):
    """Response schema for session operations"""
    session_id: str = Field(..., description="Unique session identifier")
    session_name: str = Field(..., description="Session name")
    browser_type: str = Field(..., description="Browser type")
    status: str = Field(..., description="Session status")
    current_url: Optional[str] = Field(None, description="Current page URL")
    start_time: datetime = Field(..., description="Session start time")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    viewport_size: Optional[Dict[str, int]] = Field(None, description="Viewport dimensions")
    performance_metrics: Optional[Dict[str, Any]] = Field(None, description="Performance metrics")
    available_tools: List[str] = Field(default_factory=list, description="Available tools")
    created_at: datetime = Field(..., description="Creation timestamp")


# Enhanced Error Schemas
class PlaywrightError(BaseModel):
    """Detailed error information"""
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Error type category")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    session_id: Optional[str] = Field(None, description="Associated session ID")
    tool_name: Optional[str] = Field(None, description="Associated tool name")
    request_id: Optional[str] = Field(None, description="Request ID for tracing")
    stack_trace: Optional[str] = Field(None, description="Stack trace (development only)")


class PlaywrightErrorResponse(PlaywrightBaseModel):
    """Standardized error response"""
    success: bool = Field(False, description="Always false for errors")
    error: PlaywrightError = Field(..., description="Error information")
    suggestions: Optional[List[str]] = Field(None, description="Suggestions for resolution")
    retry_after: Optional[int] = Field(None, description="Seconds to wait before retry")
    documentation_url: Optional[str] = Field(None, description="Link to documentation")


# Tool Registry Schemas
class ToolRegistryResponse(PlaywrightBaseModel):
    """Response schema for tool registry"""
    tools: Dict[str, ToolDefinition] = Field(..., description="Available tools")
    categories: List[str] = Field(..., description="Tool categories")
    total_tools: int = Field(..., description="Total number of tools")
    version: str = Field("1.0.0", description="Tool registry version")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


class ToolSearchRequest(PlaywrightBaseModel):
    """Request schema for tool searching"""
    category: Optional[ToolCategory] = Field(None, description="Filter by category")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    search_text: Optional[str] = Field(None, description="Search in name/description", max_length=200)
    status: Optional[ToolStatus] = Field(None, description="Filter by status")
    requires_session: Optional[bool] = Field(None, description="Filter by session requirement")
    limit: int = Field(50, description="Maximum results", ge=1, le=100)
    offset: int = Field(0, description="Results offset", ge=0)


# Health and Monitoring Schemas
class HealthCheckRequest(PlaywrightBaseModel):
    """Request schema for health checks"""
    check_type: str = Field("basic", description="Type of health check")
    include_details: bool = Field(False, description="Include detailed information")
    timeout: int = Field(30000, description="Health check timeout", ge=1000, le=60000)


class HealthCheckResponse(PlaywrightBaseModel):
    """Response schema for health checks"""
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    components: Dict[str, str] = Field(..., description="Component health status")
    performance: Optional[Dict[str, Any]] = Field(None, description="Performance metrics")
    errors: Optional[List[str]] = Field(None, description="Detected errors")
    uptime: Optional[int] = Field(None, description="Uptime in seconds")


# Security and Validation Schemas
class SecurityValidationRequest(PlaywrightBaseModel):
    """Request schema for security validation"""
    url: Optional[HttpUrl] = Field(None, description="URL to validate")
    selector: Optional[str] = Field(None, description="Selector to validate")
    text: Optional[str] = Field(None, description="Text to validate")
    validation_level: ValidationLevel = Field(ValidationLevel.MODERATE, description="Validation strictness")
    check_dangerous_patterns: bool = Field(True, description="Check for dangerous patterns")
    check_domain_restrictions: bool = Field(True, description="Check domain restrictions")


class SecurityValidationResponse(PlaywrightBaseModel):
    """Response schema for security validation"""
    is_valid: bool = Field(..., description="Whether input passed validation")
    validation_level: ValidationLevel = Field(..., description="Applied validation level")
    violations: List[str] = Field(default_factory=list, description="Detected violations")
    sanitized_input: Optional[str] = Field(None, description="Sanitized version of input")
    suggestions: List[str] = Field(default_factory=list, description="Security suggestions")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Validation timestamp")


# Batch Operations Schemas
class BatchToolRequest(PlaywrightBaseModel):
    """Request schema for batch tool execution"""
    session_id: str = Field(..., description="Browser session ID")
    tools: List[ToolExecutionRequest] = Field(..., description="Tools to execute", min_items=1, max_items=50)
    parallel_execution: bool = Field(False, description="Execute tools in parallel")
    stop_on_error: bool = Field(True, description="Stop on first error")
    timeout_per_tool: Optional[int] = Field(None, description="Timeout per tool")
    capture_intermediate_results: bool = Field(True, description="Capture intermediate results")


class BatchToolResponse(PlaywrightBaseModel):
    """Response schema for batch tool execution"""
    batch_id: str = Field(..., description="Unique batch execution ID")
    results: List[ToolExecutionResult] = Field(..., description="Individual tool results")
    summary: Dict[str, Any] = Field(..., description="Execution summary")
    total_execution_time: float = Field(..., description="Total execution time")
    success_count: int = Field(..., description="Number of successful tools")
    error_count: int = Field(..., description="Number of failed tools")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Batch completion timestamp")


# Configuration Schemas
class PlaywrightConfiguration(PlaywrightBaseModel):
    """Schema for Playwright service configuration"""
    max_concurrent_sessions: int = Field(50, description="Maximum concurrent sessions", ge=1, le=1000)
    default_timeout: int = Field(30000, description="Default timeout in milliseconds", ge=1000, le=300000)
    screenshot_quality: int = Field(90, description="Screenshot quality (1-100)", ge=1, le=100)
    video_quality: str = Field("medium", description="Video recording quality")
    enable_tracing: bool = Field(False, description="Enable detailed tracing")
    enable_metrics: bool = Field(True, description="Enable performance metrics")
    cleanup_interval: int = Field(3600, description="Cleanup interval in seconds", ge=60, le=86400)
    max_session_duration: int = Field(3600000, description="Max session duration in milliseconds", ge=60000)
    retry_attempts: int = Field(3, description="Default retry attempts", ge=0, le=10)
    user_agent_rotation: bool = Field(True, description="Rotate user agents")
    proxy_rotation: bool = Field(False, description="Rotate proxy servers")
    storage_cleanup: bool = Field(True, description="Auto cleanup browser storage")
    security_options: Dict[str, Any] = Field(default_factory=dict, description="Browser security options")
    rate_limits: Dict[str, int] = Field(default_factory=dict, description="Rate limits per tool")
    
    @validator("video_quality")
    def validate_video_quality(cls, v):
        """Validate video quality options"""
        valid_qualities = ["low", "medium", "high", "ultra"]
        if v not in valid_qualities:
            raise ValueError(f"video_quality must be one of: {', '.join(valid_qualities)}")
        return v


# Analytics and Reporting Schemas
class AnalyticsRequest(PlaywrightBaseModel):
    """Request schema for analytics data"""
    date_range: Dict[str, datetime] = Field(..., description="Date range for analysis")
    metrics: List[str] = Field(..., description="Metrics to include", min_items=1, max_items=20)
    group_by: Optional[str] = Field(None, description="Group results by dimension")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")
    format: str = Field("json", description="Output format")


class AnalyticsResponse(PlaywrightBaseModel):
    """Response schema for analytics data"""
    data: Dict[str, Any] = Field(..., description="Analytics data")
    summary: Dict[str, Any] = Field(..., description="Data summary")
    metadata: Dict[str, Any] = Field(..., description="Query metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")


# Legacy schema compatibility (for backward compatibility)
class BrowserAutomationRequest(PlaywrightBaseModel):
    """Legacy schema for browser automation (deprecated, use ToolExecutionRequest)"""
    session_id: str = Field(..., description="Browser session ID")
    url: Optional[HttpUrl] = Field(None, description="URL for navigation")
    action: Optional[str] = Field(None, description="Action to perform")
    selector: Optional[str] = Field(None, description="CSS selector")
    value: Optional[str] = Field(None, description="Value for interaction")
    options: Optional[Dict[str, Any]] = Field(None, description="Additional options")
    
    class Config:
        deprecated = "Use ToolExecutionRequest instead"


class BrowserStepRequest(PlaywrightBaseModel):
    """Legacy schema for browser steps (deprecated, use specific tool request schemas)"""
    action: str = Field(..., description="Action to perform")
    selector: Optional[str] = Field(None, description="CSS selector")
    value: Optional[str] = Field(None, description="Action value")
    options: Optional[Dict[str, Any]] = Field(None, description="Action options")
    
    class Config:
        deprecated = "Use specific tool request schemas instead"


class TaskExecutionRequest(PlaywrightBaseModel):
    """Legacy schema for task execution (deprecated, use BatchToolRequest)"""
    overrides: Optional[Dict[str, Any]] = Field(None, description="Configuration overrides")
    priority: Optional[int] = Field(None, description="Execution priority")
    
    class Config:
        deprecated = "Use BatchToolRequest instead"


# Export all schemas for easy importing
__all__ = [
    # Tool definitions
    "ToolDefinition",
    "ToolParameterDefinition", 
    "ToolExecutionRequest",
    "ToolExecutionResult",
    
    # Navigation schemas
    "NavigateRequest",
    "NavigationResult",
    
    # Interaction schemas
    "ClickRequest",
    "TypeRequest", 
    "SelectRequest",
    "DragAndDropRequest",
    
    # Extraction schemas
    "GetTextRequest",
    "GetAttributeRequest",
    "GetPageContentRequest",
    
    # Multimedia schemas
    "ScreenshotRequest",
    "PDFRequest",
    "RecordVideoRequest",
    
    # Synchronization schemas
    "WaitForSelectorRequest",
    "WaitForLoadStateRequest",
    "WaitForTimeoutRequest",
    
    # Session schemas
    "CreateSessionRequest",
    "SessionResponse",
    
    # Error schemas
    "PlaywrightError",
    "PlaywrightErrorResponse",
    
    # Tool registry schemas
    "ToolRegistryResponse",
    "ToolSearchRequest",
    
    # Health and monitoring schemas
    "HealthCheckRequest",
    "HealthCheckResponse",
    
    # Security schemas
    "SecurityValidationRequest",
    "SecurityValidationResponse",
    
    # Batch operations schemas
    "BatchToolRequest",
    "BatchToolResponse",
    
    # Configuration schemas
    "PlaywrightConfiguration",
    
    # Analytics schemas
    "AnalyticsRequest",
    "AnalyticsResponse",
    
    # Legacy schemas (deprecated)
    "BrowserAutomationRequest",
    "BrowserStepRequest",
    "TaskExecutionRequest",
    
    # Enums
    "PlaywrightTaskStatus",
    "PlaywrightTaskType", 
    "PlaywrightArtifactType",
    "BrowserType",
    "DeviceType",
    "ToolCategory",
    "ToolStatus",
    "ValidationLevel"
]