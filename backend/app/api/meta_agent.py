"""
Meta-Agent FUZZY API Endpoints

Provides API endpoints for meta-agent command execution, session management,
and command history tracking.
"""
import time
import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.meta_agent_engine import MetaAgentEngine
from app.models.user import User
from app.models.meta_agent import MetaAgent, MetaAgentCommand, MetaAgentSession, CommandStatus, SessionStatus
from app.api.auth import get_current_user
from app.schemas.meta_agent import (
    MetaAgentCreate, MetaAgentUpdate, MetaAgentResponse,
    MetaAgentCommandCreate, MetaAgentCommandResponse,
    MetaAgentSessionCreate, MetaAgentSessionResponse,
    CommandExecutionRequest, CommandExecutionResponse,
    CommandListResponse, CommandStatus as CommandStatusEnum
)

router = APIRouter()


# Initialize the meta-agent engine
meta_agent_engine = MetaAgentEngine()


# ============== Meta-Agent CRUD Endpoints ==============

@router.get("/", response_model=List[MetaAgentResponse])
async def get_meta_agents(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all meta-agents with optional filtering"""
    query = select(MetaAgent).offset(skip).limit(limit)
    
    if is_active is not None:
        query = query.where(MetaAgent.is_active == is_active)
    
    result = await db.execute(query)
    meta_agents = result.scalars().all()
    
    return meta_agents


@router.post("/", response_model=MetaAgentResponse, status_code=status.HTTP_201_CREATED)
async def create_meta_agent(
    meta_agent_data: MetaAgentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new meta-agent configuration"""
    
    meta_agent = MetaAgent(
        name=meta_agent_data.name,
        description=meta_agent_data.description,
        is_active=meta_agent_data.is_active,
        permission_level=meta_agent_data.permission_level.value,
        allowed_actions=meta_agent_data.allowed_actions,
        configuration=meta_agent_data.configuration
    )
    
    db.add(meta_agent)
    await db.commit()
    await db.refresh(meta_agent)
    
    return meta_agent


@router.get("/{meta_agent_id}", response_model=MetaAgentResponse)
async def get_meta_agent(
    meta_agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific meta-agent by ID"""
    
    result = await db.execute(
        select(MetaAgent).where(MetaAgent.id == meta_agent_id)
    )
    meta_agent = result.scalar_one_or_none()
    
    if not meta_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meta-agent not found"
        )
    
    return meta_agent


@router.put("/{meta_agent_id}", response_model=MetaAgentResponse)
async def update_meta_agent(
    meta_agent_id: int,
    meta_agent_update: MetaAgentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a meta-agent configuration"""
    
    result = await db.execute(
        select(MetaAgent).where(MetaAgent.id == meta_agent_id)
    )
    meta_agent = result.scalar_one_or_none()
    
    if not meta_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meta-agent not found"
        )
    
    # Update fields
    update_data = meta_agent_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            # Handle enum conversion
            if hasattr(value, 'value'):
                value = value.value
            setattr(meta_agent, field, value)
    
    await db.commit()
    await db.refresh(meta_agent)
    
    return meta_agent


@router.delete("/{meta_agent_id}")
async def delete_meta_agent(
    meta_agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a meta-agent configuration"""
    
    result = await db.execute(
        select(MetaAgent).where(MetaAgent.id == meta_agent_id)
    )
    meta_agent = result.scalar_one_or_none()
    
    if not meta_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meta-agent not found"
        )
    
    await db.delete(meta_agent)
    await db.commit()
    
    return {"message": "Meta-agent deleted successfully"}


# ============== Command Execution Endpoints ==============

@router.post("/execute", response_model=CommandExecutionResponse)
async def execute_command(
    request: CommandExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Execute a meta-agent command.
    
    Parses natural language commands, classifies intent, plans actions,
    and executes them while maintaining session context.
    """
    start_time = time.time()
    
    # Get or create session
    session = None
    if request.session_id:
        result = await db.execute(
            select(MetaAgentSession).where(
                and_(
                    MetaAgentSession.id == request.session_id,
                    MetaAgentSession.user_id == current_user.id,
                    MetaAgentSession.status == SessionStatus.ACTIVE
                )
            )
        )
        session = result.scalar_one_or_none()
    
    if not session:
        # Create a new session
        session = MetaAgentSession(
            user_id=current_user.id,
            meta_agent_id=1,  # Default meta-agent, could be configurable
            status=SessionStatus.ACTIVE,
            context={"history": []}
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
    
    # Parse and classify the command
    parsed_command = meta_agent_engine.parse_command(request.command)
    intent = meta_agent_engine.classify_intent(request.command)
    
    # Create command record
    command = MetaAgentCommand(
        meta_agent_id=session.meta_agent_id,
        session_id=session.id,
        command_type=parsed_command.get("type", "general"),
        intent=intent,
        parameters=request.parameters or {},
        status=CommandStatus.EXECUTING
    )
    db.add(command)
    await db.commit()
    await db.refresh(command)
    
    # Validate permissions
    permission_level = "editor"  # Could be derived from meta-agent config
    if not meta_agent_engine.validate_permissions(intent, permission_level):
        command.status = CommandStatus.FAILED
        command.error_message = f"Permission denied for action: {intent}"
        command.execution_time_ms = (time.time() - start_time) * 1000
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied for action: {intent}"
        )
    
    # Plan and execute actions
    try:
        parameters = {**(request.parameters or {}), **parsed_command.get("parameters", {})}
        actions = meta_agent_engine.plan_action(intent, parameters)
        result = meta_agent_engine.execute_actions(actions)
        
        # Update command with results
        command.status = CommandStatus.COMPLETED
        command.result = result
        command.execution_time_ms = (time.time() - start_time) * 1000
        
        # Update session context
        context = session.context or {"history": []}
        context["history"].append({
            "command": request.command,
            "intent": intent,
            "result": result,
            "timestamp": command.created_at.isoformat()
        })
        session.context = context
        
        await db.commit()
        
        return CommandExecutionResponse(
            session_id=session.id,
            result=result,
            execution_time_ms=command.execution_time_ms,
            command_id=command.id
        )
        
    except Exception as e:
        command.status = CommandStatus.FAILED
        command.error_message = str(e)
        command.execution_time_ms = (time.time() - start_time) * 1000
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Command execution failed: {str(e)}"
        )


# ============== Command Management Endpoints ==============

@router.get("/commands", response_model=CommandListResponse)
async def list_commands(
    session_id: Optional[str] = None,
    status: Optional[CommandStatusEnum] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List commands with optional filtering by session and status"""
    
    # Build query with filters
    query = select(MetaAgentCommand)
    
    if session_id:
        query = query.where(MetaAgentCommand.session_id == session_id)
    
    if status:
        query = query.where(MetaAgentCommand.status == status.value)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.offset(offset).limit(limit).order_by(MetaAgentCommand.created_at.desc())
    
    result = await db.execute(query)
    commands = result.scalars().all()
    
    return CommandListResponse(
        commands=commands,
        total=total,
        limit=limit,
        offset=offset
    )


@router.post("/commands", response_model=MetaAgentCommandResponse, status_code=status.HTTP_201_CREATED)
async def create_command(
    command_data: MetaAgentCommandCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new command record"""
    
    # Verify meta-agent exists
    result = await db.execute(
        select(MetaAgent).where(MetaAgent.id == command_data.meta_agent_id)
    )
    meta_agent = result.scalar_one_or_none()
    
    if not meta_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meta-agent not found"
        )
    
    command = MetaAgentCommand(
        meta_agent_id=command_data.meta_agent_id,
        session_id=command_data.session_id,
        command_type=command_data.command_type,
        intent=command_data.intent,
        parameters=command_data.parameters,
        status=CommandStatus.PENDING
    )
    
    db.add(command)
    await db.commit()
    await db.refresh(command)
    
    return command


@router.get("/commands/{command_id}", response_model=MetaAgentCommandResponse)
async def get_command(
    command_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific command by ID"""
    
    result = await db.execute(
        select(MetaAgentCommand).where(MetaAgentCommand.id == command_id)
    )
    command = result.scalar_one_or_none()
    
    if not command:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Command not found"
        )
    
    return command


# ============== Session Management Endpoints ==============

@router.get("/sessions/{session_id}", response_model=MetaAgentSessionResponse)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get session details including context and status"""
    
    result = await db.execute(
        select(MetaAgentSession).where(
            and_(
                MetaAgentSession.id == session_id,
                MetaAgentSession.user_id == current_user.id
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return session


@router.post("/sessions", response_model=MetaAgentSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: MetaAgentSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new session"""
    
    # Verify meta-agent exists
    result = await db.execute(
        select(MetaAgent).where(MetaAgent.id == session_data.meta_agent_id)
    )
    meta_agent = result.scalar_one_or_none()
    
    if not meta_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meta-agent not found"
        )
    
    session = MetaAgentSession(
        user_id=current_user.id,
        meta_agent_id=session_data.meta_agent_id,
        status=SessionStatus.ACTIVE,
        context={"history": []}
    )
    
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return session


@router.put("/sessions/{session_id}/complete")
async def complete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a session as completed"""
    
    result = await db.execute(
        select(MetaAgentSession).where(
            and_(
                MetaAgentSession.id == session_id,
                MetaAgentSession.user_id == current_user.id,
                MetaAgentSession.status == SessionStatus.ACTIVE
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active session not found"
        )
    
    session.status = SessionStatus.COMPLETED
    await db.commit()
    
    return {"message": "Session completed successfully", "session_id": session_id}


@router.get("/sessions/{session_id}/history")
async def get_session_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get command history for a session"""
    
    result = await db.execute(
        select(MetaAgentSession).where(
            and_(
                MetaAgentSession.id == session_id,
                MetaAgentSession.user_id == current_user.id
            )
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Get commands for this session
    commands_result = await db.execute(
        select(MetaAgentCommand)
        .where(MetaAgentCommand.session_id == session_id)
        .order_by(MetaAgentCommand.created_at.asc())
    )
    commands = commands_result.scalars().all()
    
    return {
        "session": session,
        "history": commands,
        "context": session.context
    }