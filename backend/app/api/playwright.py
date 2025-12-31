"""
Playwright MCP Server API Endpoints

This module provides REST API endpoints for managing Playwright browser sessions,
automation tasks, and artifacts within the Chronos AI infrastructure.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.agent import AgentModel
from app.models.playwright import (
    PlaywrightBrowserSession, PlaywrightAutomationTask, PlaywrightArtifact,
    PlaywrightBrowserPool, BrowserType, TaskStatus, ArtifactType, PoolStatus
)
from app.schemas.playwright import (
    PlaywrightSessionResponse, PlaywrightSessionCreate, PlaywrightSessionUpdate,
    PlaywrightTaskResponse, PlaywrightTaskCreate, PlaywrightTaskUpdate,
    PlaywrightArtifactResponse, PlaywrightArtifactCreate,
    PlaywrightPoolResponse, PlaywrightPoolCreate, PlaywrightPoolUpdate,
    PlaywrightSessionStats, PlaywrightTaskStats, PlaywrightPoolStats,
    BrowserAutomationRequest, BrowserStepRequest, TaskExecutionRequest
)
from app.api.auth import get_current_user
from app.core.playwright import (
    PlaywrightBrowserManager, PlaywrightTaskExecutor, ArtifactManager,
    PlaywrightPoolManager, get_browser_manager, get_task_executor,
    get_artifact_manager, get_pool_manager
)

router = APIRouter()


# Utility functions
async def verify_agent_ownership(
    agent_id: int, 
    user_id: int, 
    db: AsyncSession
) -> AgentModel:
    """Verify user owns the agent"""
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == agent_id,
                AgentModel.owner_id == user_id
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
    session_id: int, 
    user_id: int, 
    db: AsyncSession
) -> PlaywrightBrowserSession:
    """Verify user has access to the browser session"""
    result = await db.execute(
        select(PlaywrightBrowserSession).where(
            and_(
                PlaywrightBrowserSession.id == session_id,
                PlaywrightBrowserSession.agent.has(AgentModel.owner_id == user_id)
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


async def verify_task_access(
    task_id: int, 
    user_id: int, 
    db: AsyncSession
) -> PlaywrightAutomationTask:
    """Verify user has access to the automation task"""
    result = await db.execute(
        select(PlaywrightAutomationTask).where(
            and_(
                PlaywrightAutomationTask.id == task_id,
                PlaywrightAutomationTask.agent.has(AgentModel.owner_id == user_id)
            )
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Automation task not found or access denied"
        )
    
    return task


# Browser Session Management Endpoints
@router.get("/agents/{agent_id}/sessions", response_model=List[PlaywrightSessionResponse])
async def get_browser_sessions(
    agent_id: int,
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    browser_type: Optional[BrowserType] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get browser sessions for an agent"""
    
    # Verify agent ownership
    await verify_agent_ownership(agent_id, current_user.id, db)
    
    # Build query
    query = select(PlaywrightBrowserSession).where(
        PlaywrightBrowserSession.agent_id == agent_id
    )
    
    # Apply filters
    if status:
        query = query.where(PlaywrightBrowserSession.status == status)
    
    if browser_type:
        query = query.where(PlaywrightBrowserSession.browser_type == browser_type)
    
    # Order by creation date
    query = query.order_by(desc(PlaywrightBrowserSession.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    return sessions


@router.post("/agents/{agent_id}/sessions", response_model=PlaywrightSessionResponse)
async def create_browser_session(
    agent_id: int,
    session_data: PlaywrightSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new browser session"""
    
    # Verify agent ownership
    await verify_agent_ownership(agent_id, current_user.id, db)
    
    # Check session limit
    active_sessions_result = await db.execute(
        select(func.count(PlaywrightBrowserSession.id)).where(
            and_(
                PlaywrightBrowserSession.agent_id == agent_id,
                PlaywrightBrowserSession.status.in_(['starting', 'running'])
            )
        )
    )
    active_count = active_sessions_result.scalar()
    
    if active_count >= settings.PLAYWRIGHT_MAX_CONCURRENT_SESSIONS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Maximum concurrent sessions ({settings.PLAYWRIGHT_MAX_CONCURRENT_SESSIONS}) reached"
        )
    
    try:
        # Create browser session record
        session = PlaywrightBrowserSession(
            agent_id=agent_id,
            session_name=session_data.session_name,
            browser_type=session_data.browser_type,
            viewport_width=session_data.viewport_width,
            viewport_height=session_data.viewport_height,
            user_agent=session_data.user_agent,
            timezone=session_data.timezone,
            language=session_data.language,
            proxy_config=session_data.proxy_config,
            headless=session_data.headless,
            status='starting'
        )
        
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        # Start browser in background task
        browser_manager = await get_browser_manager()
        await browser_manager.start_session(session.id)
        
        return session
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create browser session: {str(e)}"
        )


@router.get("/sessions/{session_id}", response_model=PlaywrightSessionResponse)
async def get_browser_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get browser session details"""
    
    session = await verify_session_access(session_id, current_user.id, db)
    return session


@router.put("/sessions/{session_id}", response_model=PlaywrightSessionResponse)
async def update_browser_session(
    session_id: int,
    session_update: PlaywrightSessionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update browser session configuration"""
    
    session = await verify_session_access(session_id, current_user.id, db)
    
    # Update fields
    update_data = session_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(session, field, value)
    
    session.updated_at = datetime.utcnow()
    
    try:
        await db.commit()
        await db.refresh(session)
        return session
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update browser session: {str(e)}"
        )


@router.delete("/sessions/{session_id}")
async def delete_browser_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Stop and delete a browser session"""
    
    session = await verify_session_access(session_id, current_user.id, db)
    
    try:
        # Stop browser if running
        if session.status in ['starting', 'running']:
            browser_manager = await get_browser_manager()
            await browser_manager.stop_session(session_id)
        
        # Delete session
        await db.delete(session)
        await db.commit()
        
        return {"message": "Browser session deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete browser session: {str(e)}"
        )


@router.post("/sessions/{session_id}/navigate")
async def navigate_browser(
    session_id: int,
    navigation_data: BrowserAutomationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Navigate browser to URL"""
    
    session = await verify_session_access(session_id, current_user.id, db)
    
    if session.status not in ['starting', 'running']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Browser session is not active"
        )
    
    try:
        browser_manager = await get_browser_manager()
        result = await browser_manager.navigate_to_url(
            session_id, 
            navigation_data.url, 
            navigation_data.options or {}
        )
        
        # Update session URL
        session.current_url = navigation_data.url
        session.updated_at = datetime.utcnow()
        await db.commit()
        
        return {
            "success": True,
            "url": navigation_data.url,
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Navigation failed: {str(e)}"
        )


@router.post("/sessions/{session_id}/interact")
async def interact_with_browser(
    session_id: int,
    interaction_data: BrowserStepRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Perform browser interaction"""
    
    session = await verify_session_access(session_id, current_user.id, db)
    
    if session.status not in ['starting', 'running']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Browser session is not active"
        )
    
    try:
        browser_manager = await get_browser_manager()
        result = await browser_manager.execute_interaction(
            session_id,
            interaction_data.action,
            interaction_data.selector,
            interaction_data.value,
            interaction_data.options or {}
        )
        
        return {
            "success": True,
            "action": interaction_data.action,
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Interaction failed: {str(e)}"
        )


@router.post("/sessions/{session_id}/screenshot")
async def take_screenshot(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Take screenshot of current page"""
    
    session = await verify_session_access(session_id, current_user.id, db)
    
    if session.status not in ['starting', 'running']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Browser session is not active"
        )
    
    try:
        browser_manager = await get_browser_manager()
        screenshot_path = await browser_manager.take_screenshot(session_id)
        
        return {
            "success": True,
            "screenshot_path": screenshot_path
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Screenshot failed: {str(e)}"
        )


# Automation Task Management Endpoints
@router.get("/agents/{agent_id}/tasks", response_model=List[PlaywrightTaskResponse])
async def get_automation_tasks(
    agent_id: int,
    skip: int = 0,
    limit: int = 50,
    status: Optional[TaskStatus] = None,
    task_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get automation tasks for an agent"""
    
    # Verify agent ownership
    await verify_agent_ownership(agent_id, current_user.id, db)
    
    # Build query
    query = select(PlaywrightAutomationTask).where(
        PlaywrightAutomationTask.agent_id == agent_id
    )
    
    # Apply filters
    if status:
        query = query.where(PlaywrightAutomationTask.status == status)
    
    if task_type:
        query = query.where(PlaywrightAutomationTask.task_type == task_type)
    
    # Order by creation date
    query = query.order_by(desc(PlaywrightAutomationTask.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    return tasks


@router.post("/agents/{agent_id}/tasks", response_model=PlaywrightTaskResponse)
async def create_automation_task(
    agent_id: int,
    task_data: PlaywrightTaskCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new automation task"""
    
    # Verify agent ownership
    await verify_agent_ownership(agent_id, current_user.id, db)
    
    try:
        # Create automation task record
        task = PlaywrightAutomationTask(
            agent_id=agent_id,
            task_name=task_data.task_name,
            task_type=task_data.task_type,
            target_url=task_data.target_url,
            task_steps=task_data.task_steps,
            browser_config=task_data.browser_config,
            timeout_seconds=task_data.timeout_seconds,
            retry_count=task_data.retry_count,
            status=TaskStatus.PENDING
        )
        
        db.add(task)
        await db.commit()
        await db.refresh(task)
        
        # Execute task in background if requested
        if task_data.execute_immediately:
            background_tasks.add_task(execute_task_background, task.id)
        
        return task
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create automation task: {str(e)}"
        )


async def execute_task_background(task_id: int):
    """Background task execution"""
    try:
        task_executor = await get_task_executor()
        await task_executor.execute_task(task_id)
    except Exception as e:
        print(f"Task execution failed for task {task_id}: {str(e)}")


@router.get("/tasks/{task_id}", response_model=PlaywrightTaskResponse)
async def get_automation_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get automation task details"""
    
    task = await verify_task_access(task_id, current_user.id, db)
    return task


@router.post("/tasks/{task_id}/execute")
async def execute_automation_task(
    task_id: int,
    execution_data: TaskExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Execute an automation task"""
    
    task = await verify_task_access(task_id, current_user.id, db)
    
    if task.status not in [TaskStatus.PENDING, TaskStatus.FAILED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot execute task in status: {task.status}"
        )
    
    try:
        task_executor = await get_task_executor()
        await task_executor.execute_task(task_id, execution_data.overrides or {})
        
        return {
            "success": True,
            "message": "Task execution started"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Task execution failed: {str(e)}"
        )


@router.delete("/tasks/{task_id}")
async def delete_automation_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an automation task"""
    
    task = await verify_task_access(task_id, current_user.id, db)
    
    # Cancel task if running
    if task.status in [TaskStatus.RUNNING, TaskStatus.PENDING]:
        task_executor = await get_task_executor()
        await task_executor.cancel_task(task_id)
    
    try:
        await db.delete(task)
        await db.commit()
        
        return {"message": "Automation task deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete automation task: {str(e)}"
        )


# Artifact Management Endpoints
@router.get("/agents/{agent_id}/artifacts", response_model=List[PlaywrightArtifactResponse])
async def get_artifacts(
    agent_id: int,
    skip: int = 0,
    limit: int = 50,
    artifact_type: Optional[ArtifactType] = None,
    session_id: Optional[int] = None,
    task_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get artifacts for an agent"""
    
    # Verify agent ownership
    await verify_agent_ownership(agent_id, current_user.id, db)
    
    # Build query
    query = select(PlaywrightArtifact).where(
        PlaywrightArtifact.agent_id == agent_id
    )
    
    # Apply filters
    if artifact_type:
        query = query.where(PlaywrightArtifact.artifact_type == artifact_type)
    
    if session_id:
        query = query.where(PlaywrightArtifact.session_id == session_id)
    
    if task_id:
        query = query.where(PlaywrightArtifact.task_id == task_id)
    
    # Order by creation date
    query = query.order_by(desc(PlaywrightArtifact.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    artifacts = result.scalars().all()
    
    return artifacts


@router.post("/agents/{agent_id}/artifacts", response_model=PlaywrightArtifactResponse)
async def create_artifact(
    agent_id: int,
    artifact_data: PlaywrightArtifactCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new artifact record"""
    
    # Verify agent ownership
    await verify_agent_ownership(agent_id, current_user.id, db)
    
    try:
        artifact = PlaywrightArtifact(
            agent_id=agent_id,
            artifact_name=artifact_data.artifact_name,
            artifact_type=artifact_data.artifact_type,
            file_path=artifact_data.file_path,
            file_size=artifact_data.file_size,
            mime_type=artifact_data.mime_type,
            session_id=artifact_data.session_id,
            task_id=artifact_data.task_id,
            metadata=artifact_data.metadata
        )
        
        db.add(artifact)
        await db.commit()
        await db.refresh(artifact)
        
        return artifact
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create artifact: {str(e)}"
        )


@router.get("/artifacts/{artifact_id}", response_model=PlaywrightArtifactResponse)
async def get_artifact(
    artifact_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get artifact details"""
    
    # Verify access
    result = await db.execute(
        select(PlaywrightArtifact).where(
            and_(
                PlaywrightArtifact.id == artifact_id,
                PlaywrightArtifact.agent.has(AgentModel.owner_id == current_user.id)
            )
        )
    )
    artifact = result.scalar_one_or_none()
    
    if not artifact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artifact not found or access denied"
        )
    
    return artifact


@router.get("/artifacts/{artifact_id}/download")
async def download_artifact(
    artifact_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download artifact file"""
    
    artifact = await get_artifact(artifact_id, current_user, db)
    
    if not os.path.exists(artifact.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artifact file not found"
        )
    
    # Return file information for download
    return {
        "file_path": artifact.file_path,
        "file_name": artifact.artifact_name,
        "mime_type": artifact.mime_type,
        "file_size": artifact.file_size
    }


@router.delete("/artifacts/{artifact_id}")
async def delete_artifact(
    artifact_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an artifact"""
    
    artifact = await get_artifact(artifact_id, current_user, db)
    
    try:
        # Delete physical file
        if os.path.exists(artifact.file_path):
            os.remove(artifact.file_path)
        
        # Delete database record
        await db.delete(artifact)
        await db.commit()
        
        return {"message": "Artifact deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete artifact: {str(e)}"
        )


# Browser Pool Management Endpoints
@router.get("/agents/{agent_id}/pools", response_model=List[PlaywrightPoolResponse])
async def get_browser_pools(
    agent_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get browser pools for an agent"""
    
    # Verify agent ownership
    await verify_agent_ownership(agent_id, current_user.id, db)
    
    # Build query
    query = select(PlaywrightBrowserPool).where(
        PlaywrightBrowserPool.agent_id == agent_id
    ).order_by(desc(PlaywrightBrowserPool.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    pools = result.scalars().all()
    
    return pools


@router.post("/agents/{agent_id}/pools", response_model=PlaywrightPoolResponse)
async def create_browser_pool(
    agent_id: int,
    pool_data: PlaywrightPoolCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new browser pool"""
    
    # Verify agent ownership
    await verify_agent_ownership(agent_id, current_user.id, db)
    
    try:
        pool = PlaywrightBrowserPool(
            agent_id=agent_id,
            pool_name=pool_data.pool_name,
            browser_type=pool_data.browser_type,
            min_browsers=pool_data.min_browsers,
            max_browsers=pool_data.max_browsers,
            pool_config=pool_data.pool_config,
            status=PoolStatus.STOPPED
        )
        
        db.add(pool)
        await db.commit()
        await db.refresh(pool)
        
        return pool
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create browser pool: {str(e)}"
        )


@router.get("/pools/{pool_id}", response_model=PlaywrightPoolResponse)
async def get_browser_pool(
    pool_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get browser pool details"""
    
    # Verify access
    result = await db.execute(
        select(PlaywrightBrowserPool).where(
            and_(
                PlaywrightBrowserPool.id == pool_id,
                PlaywrightBrowserPool.agent.has(AgentModel.owner_id == current_user.id)
            )
        )
    )
    pool = result.scalar_one_or_none()
    
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Browser pool not found or access denied"
        )
    
    return pool


@router.put("/pools/{pool_id}", response_model=PlaywrightPoolResponse)
async def update_browser_pool(
    pool_id: int,
    pool_update: PlaywrightPoolUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update browser pool configuration"""
    
    # Verify access
    result = await db.execute(
        select(PlaywrightBrowserPool).where(
            and_(
                PlaywrightBrowserPool.id == pool_id,
                PlaywrightBrowserPool.agent.has(AgentModel.owner_id == current_user.id)
            )
        )
    )
    pool = result.scalar_one_or_none()
    
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Browser pool not found or access denied"
        )
    
    # Update fields
    update_data = pool_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pool, field, value)
    
    pool.updated_at = datetime.utcnow()
    
    try:
        await db.commit()
        await db.refresh(pool)
        return pool
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update browser pool: {str(e)}"
        )


@router.post("/pools/{pool_id}/start")
async def start_browser_pool(
    pool_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start a browser pool"""
    
    # Verify access
    result = await db.execute(
        select(PlaywrightBrowserPool).where(
            and_(
                PlaywrightBrowserPool.id == pool_id,
                PlaywrightBrowserPool.agent.has(AgentModel.owner_id == current_user.id)
            )
        )
    )
    pool = result.scalar_one_or_none()
    
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Browser pool not found or access denied"
        )
    
    try:
        pool_manager = await get_pool_manager()
        await pool_manager.start_pool(pool_id)
        
        return {"message": "Browser pool started successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start browser pool: {str(e)}"
        )


@router.post("/pools/{pool_id}/stop")
async def stop_browser_pool(
    pool_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Stop a browser pool"""
    
    # Verify access
    result = await db.execute(
        select(PlaywrightBrowserPool).where(
            and_(
                PlaywrightBrowserPool.id == pool_id,
                PlaywrightBrowserPool.agent.has(AgentModel.owner_id == current_user.id)
            )
        )
    )
    pool = result.scalar_one_or_none()
    
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Browser pool not found or access denied"
        )
    
    try:
        pool_manager = await get_pool_manager()
        await pool_manager.stop_pool(pool_id)
        
        return {"message": "Browser pool stopped successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop browser pool: {str(e)}"
        )


@router.delete("/pools/{pool_id}")
async def delete_browser_pool(
    pool_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a browser pool"""
    
    # Verify access
    result = await db.execute(
        select(PlaywrightBrowserPool).where(
            and_(
                PlaywrightBrowserPool.id == pool_id,
                PlaywrightBrowserPool.agent.has(AgentModel.owner_id == current_user.id)
            )
        )
    )
    pool = result.scalar_one_or_none()
    
    if not pool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Browser pool not found or access denied"
        )
    
    try:
        # Stop pool if running
        if pool.status == PoolStatus.RUNNING:
            pool_manager = await get_pool_manager()
            await pool_manager.stop_pool(pool_id)
        
        # Delete pool
        await db.delete(pool)
        await db.commit()
        
        return {"message": "Browser pool deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete browser pool: {str(e)}"
        )


# Statistics and Monitoring Endpoints
@router.get("/agents/{agent_id}/sessions/stats", response_model=PlaywrightSessionStats)
async def get_session_stats(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get browser session statistics for an agent"""
    
    # Verify agent ownership
    await verify_agent_ownership(agent_id, current_user.id, db)
    
    # Get counts by status
    status_counts_result = await db.execute(
        select(
            PlaywrightBrowserSession.status,
            func.count(PlaywrightBrowserSession.id)
        ).where(
            PlaywrightBrowserSession.agent_id == agent_id
        ).group_by(PlaywrightBrowserSession.status)
    )
    status_counts = dict(status_counts_result.all())
    
    # Get total session time
    total_time_result = await db.execute(
        select(func.sum(PlaywrightBrowserSession.session_duration)).where(
            and_(
                PlaywrightBrowserSession.agent_id == agent_id,
                PlaywrightBrowserSession.session_duration.isnot(None)
            )
        )
    )
    total_session_time = total_time_result.scalar() or 0
    
    # Get browser type distribution
    browser_types_result = await db.execute(
        select(
            PlaywrightBrowserSession.browser_type,
            func.count(PlaywrightBrowserSession.id)
        ).where(
            PlaywrightBrowserSession.agent_id == agent_id
        ).group_by(PlaywrightBrowserSession.browser_type)
    )
    browser_type_distribution = dict(browser_types_result.all())
    
    return PlaywrightSessionStats(
        total_sessions=status_counts.get('completed', 0) + status_counts.get('failed', 0),
        active_sessions=status_counts.get('starting', 0) + status_counts.get('running', 0),
        total_session_time_seconds=total_session_time,
        status_counts=status_counts,
        browser_type_distribution=browser_type_distribution
    )


@router.get("/agents/{agent_id}/tasks/stats", response_model=PlaywrightTaskStats)
async def get_task_stats(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get automation task statistics for an agent"""
    
    # Verify agent ownership
    await verify_agent_ownership(agent_id, current_user.id, db)
    
    # Get counts by status
    status_counts_result = await db.execute(
        select(
            PlaywrightAutomationTask.status,
            func.count(PlaywrightAutomationTask.id)
        ).where(
            PlaywrightAutomationTask.agent_id == agent_id
        ).group_by(PlaywrightAutomationTask.status)
    )
    status_counts = dict(status_counts_result.all())
    
    # Get average execution time
    avg_time_result = await db.execute(
        select(func.avg(PlaywrightAutomationTask.execution_time_seconds)).where(
            and_(
                PlaywrightAutomationTask.agent_id == agent_id,
                PlaywrightAutomationTask.execution_time_seconds.isnot(None)
            )
        )
    )
    avg_execution_time = avg_time_result.scalar() or 0
    
    # Get task type distribution
    task_types_result = await db.execute(
        select(
            PlaywrightAutomationTask.task_type,
            func.count(PlaywrightAutomationTask.id)
        ).where(
            PlaywrightAutomationTask.agent_id == agent_id
        ).group_by(PlaywrightAutomationTask.task_type)
    )
    task_type_distribution = dict(task_types_result.all())
    
    return PlaywrightTaskStats(
        total_tasks=status_counts.get('completed', 0) + status_counts.get('failed', 0),
        active_tasks=status_counts.get('running', 0) + status_counts.get('pending', 0),
        average_execution_time_seconds=avg_execution_time,
        status_counts=status_counts,
        task_type_distribution=task_type_distribution
    )


@router.get("/agents/{agent_id}/pools/stats", response_model=PlaywrightPoolStats)
async def get_pool_stats(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get browser pool statistics for an agent"""
    
    # Verify agent ownership
    await verify_agent_ownership(agent_id, current_user.id, db)
    
    # Get counts by status
    status_counts_result = await db.execute(
        select(
            PlaywrightBrowserPool.status,
            func.count(PlaywrightBrowserPool.id)
        ).where(
            PlaywrightBrowserPool.agent_id == agent_id
        ).group_by(PlaywrightBrowserPool.status)
    )
    status_counts = dict(status_counts_result.all())
    
    # Get total browser count
    total_browsers_result = await db.execute(
        select(func.sum(PlaywrightBrowserPool.active_browsers)).where(
            and_(
                PlaywrightBrowserPool.agent_id == agent_id,
                PlaywrightBrowserPool.active_browsers.isnot(None)
            )
        )
    )
    total_browsers = total_browsers_result.scalar() or 0
    
    # Get browser type distribution
    browser_types_result = await db.execute(
        select(
            PlaywrightBrowserPool.browser_type,
            func.count(PlaywrightBrowserPool.id)
        ).where(
            PlaywrightBrowserPool.agent_id == agent_id
        ).group_by(PlaywrightBrowserPool.browser_type)
    )
    browser_type_distribution = dict(browser_types_result.all())
    
    return PlaywrightPoolStats(
        total_pools=len(status_counts),
        active_pools=status_counts.get('running', 0),
        total_browsers=total_browsers,
        status_counts=status_counts,
        browser_type_distribution=browser_type_distribution
    )