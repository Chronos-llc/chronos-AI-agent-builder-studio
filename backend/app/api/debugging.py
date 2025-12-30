from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
from datetime import datetime
import uuid
import json
import logging

from backend.app.core.security import get_current_user
from backend.app.models.user import User
from backend.app.models.agent import Agent
from backend.app.models.debugging import DebugSession, LogEntry, Breakpoint, WatchExpression
from backend.app.schemas.debugging import (
    LogEntry, LogFilter, DebugSession, DebugCommand, DebugResponse,
    PerformanceMetrics, Breakpoint, WatchExpression, DebugEvent, 
    ExecutionTrace, DebugConfiguration
)


router = APIRouter(
    prefix="/api/debugging",
    tags=["debugging"]
)

logger = logging.getLogger(__name__)


# In-memory storage for debugging sessions (replace with database in production)
active_debug_sessions: Dict[str, DebugSession] = {}
log_entries: List[LogEntry] = []
breakpoints: Dict[str, Breakpoint] = {}
watch_expressions: Dict[str, WatchExpression] = {}


@router.get("/sessions")
async def list_debug_sessions(
    user: User = Depends(get_current_user)
) -> List[DebugSession]:
    """List all active debug sessions for the current user"""
    return [session for session in active_debug_sessions.values() if session.user_id == user.id]


@router.post("/sessions")
async def create_debug_session(
    agent_id: int,
    user: User = Depends(get_current_user)
) -> DebugSession:
    """Create a new debug session"""
    session_id = str(uuid.uuid4())
    
    # Check if agent exists and belongs to user
    agent = await Agent.get_or_none(id=agent_id, user_id=user.id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    session = DebugSession(
        session_id=session_id,
        agent_id=agent_id,
        user_id=user.id,
        start_time=datetime.utcnow(),
        status="active",
        debug_mode=True
    )
    
    active_debug_sessions[session_id] = session
    
    # Log session creation
    log_entry = LogEntry(
        id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        level="info",
        message=f"Debug session created for agent {agent_id}",
        session_id=session_id,
        agent_id=agent_id,
        user_id=user.id,
        context={"action": "session_create"}
    )
    log_entries.append(log_entry)
    
    return session


@router.get("/sessions/{session_id}")
async def get_debug_session(
    session_id: str,
    user: User = Depends(get_current_user)
) -> DebugSession:
    """Get debug session details"""
    session = active_debug_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Debug session not found")
    
    if session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this session")
    
    return session


@router.delete("/sessions/{session_id}")
async def end_debug_session(
    session_id: str,
    user: User = Depends(get_current_user)
) -> DebugResponse:
    """End a debug session"""
    session = active_debug_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Debug session not found")
    
    if session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this session")
    
    # Update session status
    session.status = "ended"
    
    # Log session end
    log_entry = LogEntry(
        id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        level="info",
        message=f"Debug session ended for agent {session.agent_id}",
        session_id=session_id,
        agent_id=session.agent_id,
        user_id=user.id,
        context={"action": "session_end"}
    )
    log_entries.append(log_entry)
    
    return DebugResponse(
        success=True,
        message="Debug session ended successfully",
        data={"session_id": session_id}
    )


@router.get("/logs")
async def get_logs(
    agent_id: int = None,
    session_id: str = None,
    limit: int = 100,
    user: User = Depends(get_current_user)
) -> List[LogEntry]:
    """Get log entries"""
    # Filter logs by user
    user_logs = [log for log in log_entries if log.user_id == user.id]
    
    # Apply additional filters
    if agent_id:
        user_logs = [log for log in user_logs if log.agent_id == agent_id]
    
    if session_id:
        user_logs = [log for log in user_logs if log.session_id == session_id]
    
    # Limit results
    return user_logs[-limit:]


@router.post("/logs")
async def create_log_entry(
    log_entry: LogEntry,
    user: User = Depends(get_current_user)
) -> LogEntry:
    """Create a new log entry"""
    if log_entry.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    log_entry.id = str(uuid.uuid4())
    log_entry.timestamp = datetime.utcnow()
    log_entries.append(log_entry)
    
    return log_entry


@router.get("/breakpoints")
async def list_breakpoints(
    session_id: str,
    user: User = Depends(get_current_user)
) -> List[Breakpoint]:
    """List breakpoints for a debug session"""
    # Verify session exists and belongs to user
    session = active_debug_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Debug session not found")
    
    if session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return [bp for bp in breakpoints.values() if bp.session_id == session_id]


@router.post("/breakpoints")
async def create_breakpoint(
    breakpoint: Breakpoint,
    user: User = Depends(get_current_user)
) -> Breakpoint:
    """Create a new breakpoint"""
    # Verify session exists and belongs to user
    session = active_debug_sessions.get(breakpoint.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Debug session not found")
    
    if session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    breakpoint.id = str(uuid.uuid4())
    breakpoint.created_at = datetime.utcnow()
    breakpoints[breakpoint.id] = breakpoint
    
    return breakpoint


@router.delete("/breakpoints/{breakpoint_id}")
async def delete_breakpoint(
    breakpoint_id: str,
    user: User = Depends(get_current_user)
) -> DebugResponse:
    """Delete a breakpoint"""
    breakpoint = breakpoints.get(breakpoint_id)
    if not breakpoint:
        raise HTTPException(status_code=404, detail="Breakpoint not found")
    
    # Verify session exists and belongs to user
    session = active_debug_sessions.get(breakpoint.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Debug session not found")
    
    if session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    del breakpoints[breakpoint_id]
    
    return DebugResponse(
        success=True,
        message="Breakpoint deleted successfully",
        data={"breakpoint_id": breakpoint_id}
    )


@router.get("/watch")
async def list_watch_expressions(
    session_id: str,
    user: User = Depends(get_current_user)
) -> List[WatchExpression]:
    """List watch expressions for a debug session"""
    # Verify session exists and belongs to user
    session = active_debug_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Debug session not found")
    
    if session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return [we for we in watch_expressions.values() if we.session_id == session_id]


@router.post("/watch")
async def create_watch_expression(
    watch_expression: WatchExpression,
    user: User = Depends(get_current_user)
) -> WatchExpression:
    """Create a new watch expression"""
    # Verify session exists and belongs to user
    session = active_debug_sessions.get(watch_expression.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Debug session not found")
    
    if session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    watch_expression.id = str(uuid.uuid4())
    watch_expression.created_at = datetime.utcnow()
    watch_expressions[watch_expression.id] = watch_expression
    
    return watch_expression


@router.delete("/watch/{watch_id}")
async def delete_watch_expression(
    watch_id: str,
    user: User = Depends(get_current_user)
) -> DebugResponse:
    """Delete a watch expression"""
    watch_expression = watch_expressions.get(watch_id)
    if not watch_expression:
        raise HTTPException(status_code=404, detail="Watch expression not found")
    
    # Verify session exists and belongs to user
    session = active_debug_sessions.get(watch_expression.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Debug session not found")
    
    if session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    del watch_expressions[watch_id]
    
    return DebugResponse(
        success=True,
        message="Watch expression deleted successfully",
        data={"watch_id": watch_id}
    )


@router.get("/performance/{session_id}")
async def get_performance_metrics(
    session_id: str,
    user: User = Depends(get_current_user)
) -> PerformanceMetrics:
    """Get performance metrics for a debug session"""
    # Verify session exists and belongs to user
    session = active_debug_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Debug session not found")
    
    if session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Calculate metrics (simplified for demo)
    session_logs = [log for log in log_entries if log.session_id == session_id]
    session_breakpoints = [bp for bp in breakpoints.values() if bp.session_id == session_id]
    session_watches = [we for we in watch_expressions.values() if we.session_id == session_id]
    
    return PerformanceMetrics(
        session_id=session_id,
        agent_id=session.agent_id,
        uptime_seconds=(datetime.utcnow() - session.start_time).total_seconds(),
        execution_count=len(session_logs),
        average_execution_time=0.1,  # Placeholder
        error_rate=0.05,  # Placeholder
        memory_usage=128.5,  # Placeholder
        cpu_usage=15.2,  # Placeholder
        active_breakpoints=len(session_breakpoints),
        watch_expressions=len(session_watches),
        log_count=len(session_logs),
        debug_mode=session.debug_mode
    )


@router.post("/execute")
async def execute_debug_command(
    command: DebugCommand,
    user: User = Depends(get_current_user)
) -> DebugResponse:
    """Execute a debug command"""
    # Verify agent exists and belongs to user
    agent = await Agent.get_or_none(id=command.agent_id, user_id=user.id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Execute command (simplified for demo)
    try:
        # In a real implementation, this would execute the actual debug command
        result = {"status": "success", "message": f"Command '{command.command}' executed"}
        
        if command.parameters:
            result["parameters"] = command.parameters
        
        return DebugResponse(
            success=True,
            message="Command executed successfully",
            data=result
        )
    except Exception as e:
        return DebugResponse(
            success=False,
            message=f"Command execution failed: {str(e)}",
            data={"error": str(e)}
        )


@router.get("/configuration/{agent_id}")
async def get_debug_configuration(
    agent_id: int,
    user: User = Depends(get_current_user)
) -> DebugConfiguration:
    """Get debug configuration for an agent"""
    # Verify agent exists and belongs to user
    agent = await Agent.get_or_none(id=agent_id, user_id=user.id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Return default configuration (in production, this would come from database)
    return DebugConfiguration(
        agent_id=agent_id,
        auto_attach=True,
        break_on_errors=True,
        log_level="info",
        max_log_entries=1000,
        performance_monitoring=True,
        memory_profiling=False,
        cpu_profiling=False
    )


@router.put("/configuration/{agent_id}")
async def update_debug_configuration(
    agent_id: int,
    config: DebugConfiguration,
    user: User = Depends(get_current_user)
) -> DebugConfiguration:
    """Update debug configuration for an agent"""
    # Verify agent exists and belongs to user
    agent = await Agent.get_or_none(id=agent_id, user_id=user.id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # In a real implementation, this would update the configuration in the database
    # For now, just return the updated config
    return config