from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime


class LogLevel(str, Enum):
    """Log levels for debugging"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogEntry(BaseModel):
    """A single log entry"""
    id: str = Field(..., description="Unique identifier for the log entry")
    timestamp: datetime = Field(..., description="When the log entry was created")
    level: LogLevel = Field(..., description="Log level")
    message: str = Field(..., description="Log message")
    session_id: str = Field(..., description="Debug session ID")
    agent_id: int = Field(..., description="Agent ID")
    user_id: int = Field(..., description="User ID")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context data")


class LogFilter(BaseModel):
    """Filter criteria for logs"""
    level: Optional[LogLevel] = Field(None, description="Filter by log level")
    start_time: Optional[datetime] = Field(None, description="Filter logs from this time")
    end_time: Optional[datetime] = Field(None, description="Filter logs up to this time")
    search_text: Optional[str] = Field(None, description="Search text in logs")
    limit: Optional[int] = Field(100, description="Maximum number of logs to return")


class DebugSession(BaseModel):
    """Debug session information"""
    session_id: str = Field(..., description="Unique session identifier")
    agent_id: int = Field(..., description="Agent ID being debugged")
    user_id: int = Field(..., description="User ID who owns the session")
    start_time: datetime = Field(..., description="When the session started")
    status: str = Field(..., description="Session status")
    debug_mode: bool = Field(..., description="Whether debug mode is enabled")


class DebugCommand(BaseModel):
    """Debug command to execute"""
    agent_id: int = Field(..., description="Agent ID")
    command: str = Field(..., description="Command to execute")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Command parameters")


class DebugResponse(BaseModel):
    """Response from debug command execution"""
    success: bool = Field(..., description="Whether the command succeeded")
    message: str = Field(..., description="Response message")
    data: Dict[str, Any] = Field(default_factory=dict, description="Additional response data")


class PerformanceMetrics(BaseModel):
    """Performance metrics for debugging"""
    session_id: str = Field(..., description="Debug session ID")
    agent_id: int = Field(..., description="Agent ID")
    uptime_seconds: float = Field(..., description="Session uptime in seconds")
    execution_count: int = Field(..., description="Number of executions")
    average_execution_time: float = Field(..., description="Average execution time in seconds")
    error_rate: float = Field(..., description="Error rate (0-1)")
    memory_usage: float = Field(..., description="Memory usage in MB")
    cpu_usage: float = Field(..., description="CPU usage percentage")
    active_breakpoints: int = Field(..., description="Number of active breakpoints")
    watch_expressions: int = Field(..., description="Number of watch expressions")
    log_count: int = Field(..., description="Total number of log entries")
    debug_mode: bool = Field(..., description="Whether debug mode is enabled")


class Breakpoint(BaseModel):
    """Debug breakpoint"""
    id: str = Field(..., description="Unique breakpoint identifier")
    agent_id: int = Field(..., description="Agent ID")
    session_id: str = Field(..., description="Debug session ID")
    location: str = Field(..., description="Breakpoint location (e.g., action name, line number)")
    condition: Optional[str] = Field(None, description="Condition for breakpoint to trigger")
    hit_count: int = Field(0, description="Number of times breakpoint was hit")
    enabled: bool = Field(True, description="Whether breakpoint is enabled")
    created_at: datetime = Field(..., description="When breakpoint was created")


class WatchExpression(BaseModel):
    """Watch expression for debugging"""
    id: str = Field(..., description="Unique watch expression identifier")
    agent_id: int = Field(..., description="Agent ID")
    session_id: str = Field(..., description="Debug session ID")
    expression: str = Field(..., description="Expression to watch")
    name: str = Field(..., description="Display name for the watch expression")
    current_value: Optional[str] = Field(None, description="Current evaluated value")
    created_at: datetime = Field(..., description="When watch expression was created")


class DebugEvent(BaseModel):
    """Debug event notification"""
    type: str = Field(..., description="Event type")
    timestamp: datetime = Field(..., description="When event occurred")
    session_id: str = Field(..., description="Debug session ID")
    agent_id: int = Field(..., description="Agent ID")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data")


class ExecutionTrace(BaseModel):
    """Execution trace for debugging"""
    trace_id: str = Field(..., description="Unique trace identifier")
    session_id: str = Field(..., description="Debug session ID")
    agent_id: int = Field(..., description="Agent ID")
    start_time: datetime = Field(..., description="When execution started")
    end_time: Optional[datetime] = Field(None, description="When execution ended")
    status: str = Field(..., description="Execution status")
    steps: List[Dict[str, Any]] = Field(default_factory=list, description="Execution steps")
    error: Optional[str] = Field(None, description="Error message if failed")


class DebugConfiguration(BaseModel):
    """Debug configuration settings"""
    agent_id: int = Field(..., description="Agent ID")
    auto_attach: bool = Field(True, description="Auto-attach debugger to executions")
    break_on_errors: bool = Field(True, description="Break execution on errors")
    log_level: LogLevel = Field(LogLevel.INFO, description="Default log level")
    max_log_entries: int = Field(1000, description="Maximum number of log entries to keep")
    performance_monitoring: bool = Field(True, description="Enable performance monitoring")
    memory_profiling: bool = Field(False, description="Enable memory profiling")
    cpu_profiling: bool = Field(False, description="Enable CPU profiling")