"""
Enhanced Playwright API Endpoints with Comprehensive Automation

This module provides enhanced REST API endpoints for Playwright browser automation including:
- Tool Execution Endpoints: Direct tool execution with validation
- Session Management: Enhanced browser session operations
- Security Validation: URL and input validation endpoints
- Analytics and Monitoring: Performance and usage analytics
- Batch Operations: Multi-tool execution support
- Health and Status: Comprehensive system monitoring
"""

import asyncio
import json
import os
import time
import traceback
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from uuid import uuid4

from fastapi import (
    APIRouter, Depends, HTTPException, status, BackgroundTasks, 
    Request, Response, Query, Path, Header
)
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, text
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.config import settings
from app.core.logging import get_logger
from app.api.auth import get_current_user
from app.models.user import User
from app.models.agent import Agent

# Import enhanced components
from app.core.playwright_enhanced import (
    PlaywrightBrowserManager,
    get_enhanced_playwright_manager,
    PlaywrightAutomationError,
    PlaywrightTimeoutError,
    PlaywrightNavigationError,
    PlaywrightInteractionError,
    PlaywrightExtractionError,
    PlaywrightSecurityError,
    PlaywrightSessionError
)

from app.schemas.playwright_enhanced import (
    # Tool execution schemas
    ToolExecutionRequest,
    ToolExecutionResult,
    ToolDefinition,
    ToolRegistryResponse,
    ToolSearchRequest,
    
    # Navigation schemas
    NavigateRequest,
    NavigationResult,
    
    # Interaction schemas
    ClickRequest,
    TypeRequest,
    SelectRequest,
    DragAndDropRequest,
    
    # Extraction schemas
    GetTextRequest,
    GetAttributeRequest,
    GetPageContentRequest,
    
    # Multimedia schemas
    ScreenshotRequest,
    PDFRequest,
    RecordVideoRequest,
    
    # Synchronization schemas
    WaitForSelectorRequest,
    WaitForLoadStateRequest,
    WaitForTimeoutRequest,
    
    # Session schemas
    CreateSessionRequest,
    SessionResponse,
    
    # Error schemas
    PlaywrightError,
    PlaywrightErrorResponse,
    
    # Security schemas
    SecurityValidationRequest,
    SecurityValidationResponse,
    
    # Batch schemas
    BatchToolRequest,
    BatchToolResponse,
    
    # Health schemas
    HealthCheckRequest,
    HealthCheckResponse,
    
    # Analytics schemas
    AnalyticsRequest,
    AnalyticsResponse,
    
    # Configuration schemas
    PlaywrightConfiguration,
    
    # Enums
    BrowserType,
    ToolCategory,
    ToolStatus,
    ValidationLevel
)

from app.models.playwright_enhanced import (
    PlaywrightBrowserSession,
    PlaywrightToolExecution,
    PlaywrightAutomationTask,
    PlaywrightArtifact,
    PlaywrightSecurityEvent,
    PlaywrightSecurityRule,
    PlaywrightAnalytics
)

logger = get_logger(__name__)
router = APIRouter()

# Add CORS middleware
router.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS.split(",") if settings.ALLOWED_HOSTS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Utility Functions
async def verify_agent_ownership(
    agent_id: int, 
    user_id: int, 
    db: AsyncSession
) -> Agent:
    """Verify user owns the agent"""
    result = await db.execute(
        select(Agent).where(
            and_(
                Agent.id == agent_id,
                Agent.owner_id == user_id
            )
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or access denied"
        )
    
    return agent


async def verify_session_access(
    session_id: str, 
    user_id: int, 
    db: AsyncSession
) -> PlaywrightBrowserSession:
    """Verify user has access to the browser session"""
    result = await db.execute(
        select(PlaywrightBrowserSession).where(
            and_(
                PlaywrightBrowserSession.session_id == session_id,
                PlaywrightBrowserSession.user_id == str(user_id)
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Browser session not found or access denied"
        )
    
    return session


async def create_error_response(
    error: Exception,
    request_id: str = None,
    session_id: str = None,
    tool_name: str = None
) -> PlaywrightErrorResponse:
    """Create standardized error response"""
    
    # Determine error type and code
    if isinstance(error, PlaywrightTimeoutError):
        error_type = "timeout"
        error_code = "PW_TIMEOUT"
        status_code = 408
    elif isinstance(error, PlaywrightSecurityError):
        error_type = "security"
        error_code = "PW_SECURITY"
        status_code = 403
    elif isinstance(error, PlaywrightNavigationError):
        error_type = "navigation"
        error_code = "PW_NAVIGATION"
        status_code = 400
    elif isinstance(error, PlaywrightInteractionError):
        error_type = "interaction"
        error_code = "PW_INTERACTION"
        status_code = 400
    elif isinstance(error, PlaywrightExtractionError):
        error_type = "extraction"
        error_code = "PW_EXTRACTION"
        status_code = 400
    elif isinstance(error, PlaywrightSessionError):
        error_type = "session"
        error_code = "PW_SESSION"
        status_code = 404
    elif isinstance(error, PlaywrightAutomationError):
        error_type = "automation"
        error_code = "PW_AUTOMATION"
        status_code = 500
    else:
        error_type = "unknown"
        error_code = "PW_UNKNOWN"
        status_code = 500
    
    # Create error details
    error_details = {
        "error_type": error_type,
        "error_code": error_code,
        "error_message": str(error),
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request_id,
        "session_id": session_id,
        "tool_name": tool_name
    }
    
    # Add stack trace in development
    if settings.ENVIRONMENT == "development":
        error_details["stack_trace"] = traceback.format_exc()
    
    # Generate suggestions
    suggestions = []
    if error_type == "timeout":
        suggestions = [
            "Increase the timeout parameter",
            "Check if the target element is available",
            "Verify network connectivity"
        ]
    elif error_type == "security":
        suggestions = [
            "Check URL format and domain restrictions",
            "Verify input sanitization requirements",
            "Review security policies"
        ]
    elif error_type == "navigation":
        suggestions = [
            "Verify the URL is correct and accessible",
            "Check if the page loads completely",
            "Try using a different wait condition"
        ]
    
    playwright_error = PlaywrightError(
        error_code=error_code,
        error_message=str(error),
        error_type=error_type,
        details=error_details,
        session_id=session_id,
        tool_name=tool_name
    )
    
    return PlaywrightErrorResponse(
        error=playwright_error,
        suggestions=suggestions
    )


# Tool Registry Endpoints
@router.get("/tools", response_model=ToolRegistryResponse)
async def get_tool_registry(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get complete tool registry with metadata"""
    try:
        playwright_manager = await get_enhanced_playwright_manager()
        tools = playwright_manager.tool_registry.get_all_tools()
        
        return ToolRegistryResponse(
            tools=tools,
            categories=playwright_manager.tool_registry.get_categories(),
            total_tools=len(tools),
            version="1.0.0",
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Failed to get tool registry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tool registry: {str(e)}"
        )


@router.get("/tools/search", response_model=Dict[str, Any])
async def search_tools(
    category: Optional[ToolCategory] = Query(None, description="Filter by category"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    search_text: Optional[str] = Query(None, description="Search in name/description"),
    status: Optional[ToolStatus] = Query(None, description="Filter by status"),
    requires_session: Optional[bool] = Query(None, description="Filter by session requirement"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Results offset"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search and filter tools"""
    try:
        playwright_manager = await get_enhanced_playwright_manager()
        all_tools = playwright_manager.tool_registry.get_all_tools()
        
        # Apply filters
        filtered_tools = {}
        tag_list = tags.split(",") if tags else []
        
        for tool_name, tool_def in all_tools.items():
            # Category filter
            if category and tool_def.category != category:
                continue
            
            # Tags filter
            if tag_list and not any(tag in tool_def.tags for tag in tag_list):
                continue
            
            # Status filter
            if status and tool_def.status != status:
                continue
            
            # Session requirement filter
            if requires_session is not None and tool_def.requires_session != requires_session:
                continue
            
            # Text search
            if search_text:
                search_lower = search_text.lower()
                if (search_lower not in tool_def.name.lower() and 
                    search_lower not in tool_def.description.lower()):
                    continue
            
            filtered_tools[tool_name] = tool_def
        
        # Apply pagination
        tool_items = list(filtered_tools.items())
        total = len(tool_items)
        paginated_tools = dict(tool_items[offset:offset + limit])
        
        return {
            "tools": paginated_tools,
            "total": total,
            "limit": limit,
            "offset": offset,
            "categories": playwright_manager.tool_registry.get_categories()
        }
        
    except Exception as e:
        logger.error(f"Failed to search tools: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search tools: {str(e)}"
        )


@router.get("/tools/{tool_name}", response_model=ToolDefinition)
async def get_tool_definition(
    tool_name: str = Path(..., description="Tool name"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed tool definition"""
    try:
        playwright_manager = await get_enhanced_playwright_manager()
        tool = playwright_manager.tool_registry.get_tool(tool_name)
        
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tool '{tool_name}' not found"
            )
        
        return tool
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tool definition for {tool_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tool definition: {str(e)}"
        )


# Session Management Endpoints
@router.post("/sessions", response_model=SessionResponse)
async def create_browser_session(
    session_data: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new browser session"""
    try:
        # Create browser manager instance
        playwright_manager = await get_enhanced_playwright_manager()
        
        # Generate session ID
        session_id = str(uuid4())
        
        # Convert request data to config
        config = {
            "headless": session_data.headless,
            "viewport_width": session_data.viewport_width,
            "viewport_height": session_data.viewport_height,
            "user_agent": session_data.user_agent,
            "enable_javascript": session_data.enable_javascript,
            "enable_images": session_data.enable_images,
            "enable_css": session_data.enable_css,
            "proxy_url": session_data.proxy_url,
            "timezone": session_data.timezone,
            "language": session_data.language
        }
        
        # Create browser session
        session_result = await playwright_manager.create_session(
            session_id=session_id,
            browser_type=session_data.browser_type.value,
            config=config
        )
        
        # Create database record
        db_session = PlaywrightBrowserSession(
            session_id=session_id,
            user_id=str(current_user.id),
            browser_type=session_data.browser_type.value,
            viewport_width=session_data.viewport_width,
            viewport_height=session_data.viewport_height,
            user_agent=session_data.user_agent,
            headless=session_data.headless,
            status="active",
            start_time=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(milliseconds=session_data.timeout)
        )
        
        db.add(db_session)
        await db.commit()
        await db.refresh(db_session)
        
        # Log session creation
        logger.info(f"Created browser session {session_id} for user {current_user.id}")
        
        return SessionResponse(
            session_id=session_id,
            session_name=session_data.session_name,
            browser_type=session_data.browser_type.value,
            status="active",
            current_url=None,
            start_time=db_session.start_time,
            last_activity=db_session.last_activity,
            viewport_size={
                "width": session_data.viewport_width,
                "height": session_data.viewport_height
            },
            available_tools=list(session_result.get("available_tools", [])),
            created_at=db_session.created_at
        )
        
    except Exception as e:
        logger.error(f"Failed to create browser session: {str(e)}")
        await db.rollback()
        
        error_response = await create_error_response(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.dict()
        )


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_browser_session(
    session_id: str = Path(..., description="Session ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get browser session details"""
    try:
        # Verify session access
        session = await verify_session_access(session_id, current_user.id, db)
        
        # Get enhanced session info from browser manager
        playwright_manager = await get_enhanced_playwright_manager()
        enhanced_info = await playwright_manager.get_session_info(session_id)
        
        if "error" in enhanced_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=enhanced_info["error"]
            )
        
        return SessionResponse(
            session_id=session_id,
            session_name=f"Session {session_id[:8]}",
            browser_type=session.browser_type,
            status=session.status,
            current_url=enhanced_info.get("page_info", {}).get("current_url"),
            start_time=session.start_time,
            last_activity=session.last_activity,
            viewport_size=enhanced_info.get("page_info", {}).get("viewport_size"),
            performance_metrics=enhanced_info.get("performance_metrics"),
            available_tools=enhanced_info.get("available_tools", []),
            created_at=session.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get browser session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve session: {str(e)}"
        )


@router.delete("/sessions/{session_id}")
async def delete_browser_session(
    session_id: str = Path(..., description="Session ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Stop and delete a browser session"""
    try:
        # Verify session access
        session = await verify_session_access(session_id, current_user.id, db)
        
        # Close browser session
        playwright_manager = await get_enhanced_playwright_manager()
        await playwright_manager.close_session(session_id)
        
        # Update database record
        session.status = "terminated"
        session.end_time = datetime.utcnow()
        await db.commit()
        
        logger.info(f"Deleted browser session {session_id} for user {current_user.id}")
        
        return {"message": "Browser session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete browser session {session_id}: {str(e)}")
        await db.rollback()
        
        error_response = await create_error_response(e, session_id=session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.dict()
        )


@router.get("/sessions/{session_id}/stats")
async def get_session_stats(
    session_id: str = Path(..., description="Session ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive session statistics"""
    try:
        # Verify session access
        session = await verify_session_access(session_id, current_user.id, db)
        
        # Get enhanced session info
        playwright_manager = await get_enhanced_playwright_manager()
        session_info = await playwright_manager.get_session_info(session_id)
        
        if "error" in session_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=session_info["error"]
            )
        
        # Get tool execution statistics
        tool_exec_result = await db.execute(
            select(func.count(PlaywrightToolExecution.id)).where(
                PlaywrightToolExecution.session_id == session.id
            )
        )
        total_executions = tool_exec_result.scalar() or 0
        
        successful_exec_result = await db.execute(
            select(func.count(PlaywrightToolExecution.id)).where(
                and_(
                    PlaywrightToolExecution.session_id == session.id,
                    PlaywrightToolExecution.status == "completed"
                )
            )
        )
        successful_executions = successful_exec_result.scalar() or 0
        
        # Calculate success rate
        success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
        
        return {
            "session_info": session_info,
            "execution_stats": {
                "total_executions": total_executions,
                "successful_executions": successful_executions,
                "failed_executions": total_executions - successful_executions,
                "success_rate": success_rate
            },
            "performance_metrics": session_info.get("performance_metrics", {}),
            "security_status": session_info.get("security_status", "unknown")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session stats for {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve session statistics: {str(e)}"
        )


# Individual Tool Execution Endpoints
@router.post("/tools/navigate", response_model=NavigationResult)
async def navigate_tool(
    request: NavigateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request_id: str = Header(None, description="Request ID for tracing")
):
    """Execute navigation tool"""
    try:
        # Verify session access
        session = await verify_session_access(request.session_id, current_user.id, db)
        
        # Create tool execution record
        execution = PlaywrightToolExecution(
            session_id=session.id,
            user_id=str(current_user.id),
            tool_name="navigate",
            tool_category="Navigation",
            status="pending",
            input_parameters=request.dict(),
            execution_context={"request_id": request_id}
        )
        
        db.add(execution)
        await db.commit()
        await db.refresh(execution)
        
        # Mark execution as started
        execution.mark_started()
        await db.commit()
        
        # Execute navigation
        playwright_manager = await get_enhanced_playwright_manager()
        result = await playwright_manager.navigate_to(
            session_id=request.session_id,
            url=str(request.url),
            wait_until=request.wait_until,
            timeout=request.timeout
        )
        
        # Mark execution as completed
        execution.mark_completed(result)
        await db.commit()
        
        # Update session record
        session.current_url = result.get("url")
        session.last_activity = datetime.utcnow()
        session.add_navigation_record(
            url=str(request.url),
            duration=result.get("navigation_time", 0),
            status=result.get("status")
        )
        await db.commit()
        
        logger.info(f"Navigation completed for session {request.session_id}")
        
        return NavigationResult(
            success=True,
            execution_id=execution.execution_id,
            tool_name="navigate",
            session_id=request.session_id,
            result=result,
            execution_time=execution.execution_time_seconds,
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        
        # Mark execution as failed if it exists
        if 'execution' in locals():
            execution.mark_failed(str(e))
            await db.commit()
        
        logger.error(f"Navigation failed for session {request.session_id}: {str(e)}")
        
        error_response = await create_error_response(
            e, 
            request_id=request_id, 
            session_id=request.session_id, 
            tool_name="navigate"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.dict()
        )


@router.post("/tools/click", response_model=ToolExecutionResult)
async def click_tool(
    request: ClickRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request_id: str = Header(None, description="Request ID for tracing")
):
    """Execute click tool"""
    try:
        # Verify session access
        session = await verify_session_access(request.session_id, current_user.id, db)
        
        # Create tool execution record
        execution = PlaywrightToolExecution(
            session_id=session.id,
            user_id=str(current_user.id),
            tool_name="click",
            tool_category="Interaction",
            status="pending",
            input_parameters=request.dict(),
            execution_context={"request_id": request_id}
        )
        
        db.add(execution)
        await db.commit()
        await db.refresh(execution)
        
        # Mark execution as started
        execution.mark_started()
        await db.commit()
        
        # Execute click
        playwright_manager = await get_enhanced_playwright_manager()
        result = await playwright_manager.click(
            session_id=request.session_id,
            selector=request.selector,
            button=request.button,
            click_count=request.click_count,
            delay=request.delay,
            timeout=request.timeout
        )
        
        # Mark execution as completed
        execution.mark_completed(result)
        await db.commit()
        
        # Update session record
        session.last_activity = datetime.utcnow()
        session.add_interaction_record(
            action="click",
            selector=request.selector,
            result="success",
            duration=result.get("execution_time", 0)
        )
        await db.commit()
        
        logger.info(f"Click completed for session {request.session_id}")
        
        return ToolExecutionResult(
            success=True,
            execution_id=execution.execution_id,
            tool_name="click",
            session_id=request.session_id,
            result=result,
            execution_time=execution.execution_time_seconds,
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        
        # Mark execution as failed if it exists
        if 'execution' in locals():
            execution.mark_failed(str(e))
            await db.commit()
        
        logger.error(f"Click failed for session {request.session_id}: {str(e)}")
        
        error_response = await create_error_response(
            e, 
            request_id=request_id, 
            session_id=request.session_id, 
            tool_name="click"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.dict()
        )


@router.post("/tools/type", response_model=ToolExecutionResult)
async def type_tool(
    request: TypeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request_id: str = Header(None, description="Request ID for tracing")
):
    """Execute type tool"""
    try:
        # Verify session access
        session = await verify_session_access(request.session_id, current_user.id, db)
        
        # Create tool execution record
        execution = PlaywrightToolExecution(
            session_id=session.id,
            user_id=str(current_user.id),
            tool_name="type",
            tool_category="Interaction",
            status="pending",
            input_parameters=request.dict(),
            execution_context={"request_id": request_id}
        )
        
        db.add(execution)
        await db.commit()
        await db.refresh(execution)
        
        # Mark execution as started
        execution.mark_started()
        await db.commit()
        
        # Execute typing
        playwright_manager = await get_enhanced_playwright_manager()
        result = await playwright_manager.type(
            session_id=request.session_id,
            selector=request.selector,
            text=request.text,
            clear_first=request.clear_first,
            delay=request.delay,
            timeout=request.timeout
        )
        
        # Mark execution as completed
        execution.mark_completed(result)
        await db.commit()
        
        # Update session record
        session.last_activity = datetime.utcnow()
        session.add_interaction_record(
            action="type",
            selector=request.selector,
            result="success",
            duration=result.get("execution_time", 0)
        )
        await db.commit()
        
        logger.info(f"Type completed for session {request.session_id}")
        
        return ToolExecutionResult(
            success=True,
            execution_id=execution.execution_id,
            tool_name="type",
            session_id=request.session_id,
            result=result,
            execution_time=execution.execution_time_seconds,
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        
        # Mark execution as failed if it exists
        if 'execution' in locals():
            execution.mark_failed(str(e))
            await db.commit()
        
        logger.error(f"Type failed for session {request.session_id}: {str(e)}")
        
        error_response = await create_error_response(
            e, 
            request_id=request_id, 
            session_id=request.session_id, 
            tool_name="type"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.dict()
        )


@router.post("/tools/screenshot", response_model=ToolExecutionResult)
async def screenshot_tool(
    request: ScreenshotRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request_id: str = Header(None, description="Request ID for tracing")
):
    """Execute screenshot tool"""
    try:
        # Verify session access
        session = await verify_session_access(request.session_id, current_user.id, db)
        
        # Create tool execution record
        execution = PlaywrightToolExecution(
            session_id=session.id,
            user_id=str(current_user.id),
            tool_name="screenshot",
            tool_category="Multimedia",
            status="pending",
            input_parameters=request.dict(),
            execution_context={"request_id": request_id}
        )
        
        db.add(execution)
        await db.commit()
        await db.refresh(execution)
        
        # Mark execution as started
        execution.mark_started()
        await db.commit()
        
        # Execute screenshot
        playwright_manager = await get_enhanced_playwright_manager()
        result = await playwright_manager.screenshot(
            session_id=request.session_id,
            full_page=request.full_page,
            selector=request.selector,
            quality=request.quality,
            format=request.format,
            timeout=request.timeout
        )
        
        # Mark execution as completed
        execution.mark_completed(result)
        
        # Store screenshot in execution record if it's small enough
        screenshot_base64 = result.get("screenshot_base64")
        if screenshot_base64 and len(screenshot_base64) < 1000000:  # 1MB limit
            execution.screenshot_base64 = screenshot_base64
        
        await db.commit()
        
        # Update session record
        session.last_activity = datetime.utcnow()
        await db.commit()
        
        logger.info(f"Screenshot completed for session {request.session_id}")
        
        return ToolExecutionResult(
            success=True,
            execution_id=execution.execution_id,
            tool_name="screenshot",
            session_id=request.session_id,
            result=result,
            execution_time=execution.execution_time_seconds,
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        
        # Mark execution as failed if it exists
        if 'execution' in locals():
            execution.mark_failed(str(e))
            await db.commit()
        
        logger.error(f"Screenshot failed for session {request.session_id}: {str(e)}")
        
        error_response = await create_error_response(
            e, 
            request_id=request_id, 
            session_id=request.session_id, 
            tool_name="screenshot"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.dict()
        )


# Batch Tool Execution
@router.post("/tools/batch", response_model=BatchToolResponse)
async def execute_batch_tools(
    request: BatchToolRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request_id: str = Header(None, description="Request ID for tracing")
):
    """Execute multiple tools in batch"""
    try:
        # Verify session access
        session = await verify_session_access(request.session_id, current_user.id, db)
        
        batch_id = str(uuid4())
        
        if request.parallel_execution:
            # Execute tools in parallel
            tasks = []
            for tool_request in request.tools:
                task = execute_single_tool_async(
                    tool_request, session, current_user, db, request_id
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # Execute tools sequentially
            results = []
            for tool_request in request.tools:
                try:
                    result = await execute_single_tool_async(
                        tool_request, session, current_user, db, request_id
                    )
                    results.append(result)
                    
                    # Stop on error if requested
                    if request.stop_on_error and not result.success:
                        break
                        
                except Exception as e:
                    results.append(ToolExecutionResult(
                        success=False,
                        execution_id=str(uuid4()),
                        tool_name=tool_request.tool_name,
                        session_id=request.session_id,
                        result={},
                        error=str(e),
                        timestamp=datetime.utcnow()
                    ))
                    
                    if request.stop_on_error:
                        break
        
        # Calculate summary
        successful_results = [r for r in results if isinstance(r, ToolExecutionResult) and r.success]
        failed_results = [r for r in results if isinstance(r, ToolExecutionResult) and not r.success]
        
        total_execution_time = sum(
            r.execution_time for r in successful_results 
            if r.execution_time is not None
        )
        
        summary = {
            "total_tools": len(results),
            "successful_tools": len(successful_results),
            "failed_tools": len(failed_results),
            "total_execution_time": total_execution_time,
            "average_execution_time": (
                total_execution_time / len(successful_results) 
                if successful_results else 0
            )
        }
        
        logger.info(f"Batch execution completed: {summary}")
        
        return BatchToolResponse(
            batch_id=batch_id,
            results=results,
            summary=summary,
            total_execution_time=total_execution_time,
            success_count=len(successful_results),
            error_count=len(failed_results),
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch execution failed: {str(e)}")
        
        error_response = await create_error_response(
            e, 
            request_id=request_id, 
            session_id=request.session_id
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.dict()
        )


async def execute_single_tool_async(
    tool_request: ToolExecutionRequest,
    session: PlaywrightBrowserSession,
    current_user: User,
    db: AsyncSession,
    request_id: str
) -> ToolExecutionResult:
    """Execute a single tool asynchronously"""
    
    # Create tool execution record
    execution = PlaywrightToolExecution(
        session_id=session.id,
        user_id=str(current_user.id),
        tool_name=tool_request.tool_name,
        tool_category="Unknown",  # Would be determined from tool registry
        status="pending",
        input_parameters=tool_request.parameters,
        execution_context={"request_id": request_id}
    )
    
    db.add(execution)
    await db.commit()
    await db.refresh(execution)
    
    # Mark execution as started
    execution.mark_started()
    await db.commit()
    
    try:
        # Get playwright manager
        playwright_manager = await get_enhanced_playwright_manager()
        
        # Execute tool based on name (simplified mapping)
        if tool_request.tool_name == "navigate":
            params = tool_request.parameters
            result = await playwright_manager.navigate_to(
                session_id=tool_request.session_id,
                url=params.get("url"),
                wait_until=params.get("wait_until", "load"),
                timeout=params.get("timeout", 30000)
            )
            
        elif tool_request.tool_name == "click":
            params = tool_request.parameters
            result = await playwright_manager.click(
                session_id=tool_request.session_id,
                selector=params.get("selector"),
                button=params.get("button", "left"),
                click_count=params.get("click_count", 1),
                delay=params.get("delay", 0),
                timeout=params.get("timeout", 30000)
            )
            
        elif tool_request.tool_name == "screenshot":
            params = tool_request.parameters
            result = await playwright_manager.screenshot(
                session_id=tool_request.session_id,
                full_page=params.get("full_page", False),
                selector=params.get("selector"),
                quality=params.get("quality", 90),
                format=params.get("format", "png"),
                timeout=params.get("timeout", 30000)
            )
            
        else:
            raise PlaywrightAutomationError(f"Tool '{tool_request.tool_name}' not implemented")
        
        # Mark execution as completed
        execution.mark_completed(result)
        await db.commit()
        
        # Update session record
        session.last_activity = datetime.utcnow()
        await db.commit()
        
        return ToolExecutionResult(
            success=True,
            execution_id=execution.execution_id,
            tool_name=tool_request.tool_name,
            session_id=tool_request.session_id,
            result=result,
            execution_time=execution.execution_time_seconds,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        # Mark execution as failed
        execution.mark_failed(str(e))
        await db.commit()
        
        return ToolExecutionResult(
            success=False,
            execution_id=execution.execution_id,
            tool_name=tool_request.tool_name,
            session_id=tool_request.session_id,
            result={},
            error=str(e),
            timestamp=datetime.utcnow()
        )


# Security Validation Endpoints
@router.post("/security/validate", response_model=SecurityValidationResponse)
async def validate_input_security(
    request: SecurityValidationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Validate input for security threats"""
    try:
        playwright_manager = await get_enhanced_playwright_manager()
        security_manager = playwright_manager.security_manager
        
        violations = []
        sanitized_input = None
        
        # Validate URL if provided
        if request.url:
            is_valid, message = security_manager.validate_url(str(request.url))
            if not is_valid:
                violations.append(f"URL validation failed: {message}")
            else:
                sanitized_input = str(request.url)
        
        # Validate selector if provided
        if request.selector:
            is_valid, message = security_manager.validate_selector(request.selector)
            if not is_valid:
                violations.append(f"Selector validation failed: {message}")
            else:
                if sanitized_input is None:
                    sanitized_input = request.selector
        
        # Validate text if provided
        if request.text:
            sanitized_text = security_manager.sanitize_input(request.text)
            if sanitized_text != request.text:
                violations.append("Text contained potentially dangerous content and was sanitized")
            if sanitized_input is None:
                sanitized_input = sanitized_text
        
        # Generate suggestions
        suggestions = []
        if violations:
            suggestions = [
                "Review input for security compliance",
                "Check against security policies",
                "Consider using more restrictive validation"
            ]
        
        return SecurityValidationResponse(
            is_valid=len(violations) == 0,
            validation_level=request.validation_level,
            violations=violations,
            sanitized_input=sanitized_input,
            suggestions=suggestions,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Security validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Security validation failed: {str(e)}"
        )


# Health Check Endpoints
@router.get("/health", response_model=HealthCheckResponse)
async def health_check(
    check_type: str = Query("basic", description="Type of health check"),
    include_details: bool = Query(False, description="Include detailed information"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Comprehensive health check"""
    try:
        playwright_manager = await get_enhanced_playwright_manager()
        health_result = await playwright_manager.health_check()
        
        # Get additional system metrics
        components = {
            "playwright": health_result.get("status", "unknown"),
            "browser_sessions": str(len(playwright_manager.browser_sessions)),
            "active_browsers": str(len(playwright_manager.active_browsers)),
            "tool_registry": "healthy",
            "security_manager": "active",
            "database": "connected"
        }
        
        performance = {}
        if include_details:
            performance = {
                "uptime_seconds": time.time() - getattr(playwright_manager, '_start_time', time.time()),
                "memory_usage_mb": health_result.get("memory_usage", 0),
                "cpu_usage_percent": health_result.get("cpu_usage", 0)
            }
        
        return HealthCheckResponse(
            status=health_result.get("status", "healthy"),
            components=components,
            performance=performance,
            errors=health_result.get("errors", []),
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        
        return HealthCheckResponse(
            status="unhealthy",
            components={"error": str(e)},
            errors=[str(e)],
            timestamp=datetime.utcnow()
        )


# Analytics Endpoints
@router.get("/analytics/sessions/{session_id}")
async def get_session_analytics(
    session_id: str = Path(..., description="Session ID"),
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics for a specific session"""
    try:
        # Verify session access
        session = await verify_session_access(session_id, current_user.id, db)
        
        # Set default date range if not provided
        if not start_date:
            start_date = session.created_at
        if not end_date:
            end_date = datetime.utcnow()
        
        # Get tool execution analytics
        executions_result = await db.execute(
            select(
                PlaywrightToolExecution.tool_name,
                PlaywrightToolExecution.status,
                func.count(PlaywrightToolExecution.id).label('count'),
                func.avg(PlaywrightToolExecution.execution_time_seconds).label('avg_time')
            ).where(
                and_(
                    PlaywrightToolExecution.session_id == session.id,
                    PlaywrightToolExecution.started_at >= start_date,
                    PlaywrightToolExecution.started_at <= end_date
                )
            ).group_by(
                PlaywrightToolExecution.tool_name,
                PlaywrightToolExecution.status
            )
        )
        execution_analytics = executions_result.all()
        
        # Get performance metrics
        analytics_result = await db.execute(
            select(PlaywrightAnalytics).where(
                and_(
                    PlaywrightAnalytics.session_id == session.id,
                    PlaywrightAnalytics.timestamp >= start_date,
                    PlaywrightAnalytics.timestamp <= end_date
                )
            ).order_by(desc(PlaywrightAnalytics.timestamp))
        )
        performance_analytics = analytics_result.scalars().all()
        
        return {
            "session_id": session_id,
            "date_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "execution_analytics": [
                {
                    "tool_name": row.tool_name,
                    "status": row.status,
                    "count": row.count,
                    "average_time_seconds": float(row.avg_time) if row.avg_time else 0
                }
                for row in execution_analytics
            ],
            "performance_analytics": [
                {
                    "metric_name": metric.metric_name,
                    "metric_value": metric.metric_value,
                    "metric_unit": metric.metric_unit,
                    "timestamp": metric.timestamp.isoformat()
                }
                for metric in performance_analytics
            ],
            "session_summary": {
                "total_executions": len(execution_analytics),
                "session_duration_hours": (
                    (end_date - session.created_at).total_seconds() / 3600
                ),
                "status": session.status
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session analytics for {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analytics: {str(e)}"
        )


# Session List Endpoint
@router.get("/sessions", response_model=List[SessionResponse])
async def list_browser_sessions(
    agent_id: Optional[int] = Query(None, description="Filter by agent ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    browser_type: Optional[str] = Query(None, description="Filter by browser type"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Results offset"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List browser sessions for the current user"""
    try:
        # Build query
        query = select(PlaywrightBrowserSession).where(
            PlaywrightBrowserSession.user_id == str(current_user.id)
        )
        
        # Apply filters
        if agent_id:
            query = query.where(PlaywrightBrowserSession.agent_id == agent_id)
        
        if status:
            query = query.where(PlaywrightBrowserSession.status == status)
        
        if browser_type:
            query = query.where(PlaywrightBrowserSession.browser_type == browser_type)
        
        # Order by creation date and apply pagination
        query = query.order_by(desc(PlaywrightBrowserSession.created_at)).offset(offset).limit(limit)
        
        result = await db.execute(query)
        sessions = result.scalars().all()
        
        # Get enhanced info for each session
        playwright_manager = await get_enhanced_playwright_manager()
        session_responses = []
        
        for session in sessions:
            try:
                enhanced_info = await playwright_manager.get_session_info(session.session_id)
                
                session_response = SessionResponse(
                    session_id=session.session_id,
                    session_name=f"Session {session.session_id[:8]}",
                    browser_type=session.browser_type,
                    status=session.status,
                    current_url=enhanced_info.get("page_info", {}).get("current_url"),
                    start_time=session.start_time,
                    last_activity=session.last_activity,
                    viewport_size=enhanced_info.get("page_info", {}).get("viewport_size"),
                    performance_metrics=enhanced_info.get("performance_metrics"),
                    available_tools=enhanced_info.get("available_tools", []),
                    created_at=session.created_at
                )
                
                session_responses.append(session_response)
                
            except Exception as e:
                logger.warning(f"Failed to get enhanced info for session {session.session_id}: {str(e)}")
                # Add basic session info even if enhanced info fails
                session_response = SessionResponse(
                    session_id=session.session_id,
                    session_name=f"Session {session.session_id[:8]}",
                    browser_type=session.browser_type,
                    status=session.status,
                    current_url=session.current_url,
                    start_time=session.start_time,
                    last_activity=session.last_activity,
                    created_at=session.created_at
                )
                session_responses.append(session_response)
        
        return session_responses
        
    except Exception as e:
        logger.error(f"Failed to list browser sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}"
        )


# Tool Execution History Endpoint
@router.get("/executions", response_model=List[Dict[str, Any]])
async def list_tool_executions(
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    tool_name: Optional[str] = Query(None, description="Filter by tool name"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Results offset"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List tool execution history"""
    try:
        # Build query
        query = select(PlaywrightToolExecution).where(
            PlaywrightToolExecution.user_id == str(current_user.id)
        )
        
        # Apply filters
        if session_id:
            # Get session ID from database
            session_result = await db.execute(
                select(PlaywrightBrowserSession.id).where(
                    PlaywrightBrowserSession.session_id == session_id
                )
            )
            session_db_id = session_result.scalar_one_or_none()
            if session_db_id:
                query = query.where(PlaywrightToolExecution.session_id == session_db_id)
        
        if tool_name:
            query = query.where(PlaywrightToolExecution.tool_name == tool_name)
        
        if status:
            query = query.where(PlaywrightToolExecution.status == status)
        
        if start_date:
            query = query.where(PlaywrightToolExecution.started_at >= start_date)
        
        if end_date:
            query = query.where(PlaywrightToolExecution.started_at <= end_date)
        
        # Order by start time and apply pagination
        query = query.order_by(desc(PlaywrightToolExecution.started_at)).offset(offset).limit(limit)
        
        result = await db.execute(query)
        executions = result.scalars().all()
        
        # Convert to response format
        execution_responses = []
        for execution in executions:
            execution_data = execution.to_dict(include_sensitive=False)
            execution_responses.append(execution_data)
        
        return execution_responses
        
    except Exception as e:
        logger.error(f"Failed to list tool executions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list executions: {str(e)}"
        )


# Export router
__all__ = ["router"]