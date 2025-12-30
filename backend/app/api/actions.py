from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from datetime import datetime
import time

from app.core.database import get_db
from app.models.user import User
from app.models.agent import AgentModel, Action
from app.models.hook import Hook
from app.api.auth import get_current_user
from app.schemas.action import (
    ActionResponse, ActionCreate, ActionUpdate,
    ActionExecutionRequest, ActionExecutionResponse
)
from app.schemas.hook import (
    HookResponse, HookCreate, HookUpdate,
    HookExecutionRequest, HookExecutionResponse
)

router = APIRouter()


# Actions Endpoints
@router.get("/agents/{agent_id}/actions", response_model=List[ActionResponse])
async def get_agent_actions(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all actions for an agent"""
    
    # Verify agent ownership
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == agent_id,
                AgentModel.owner_id == current_user.id
            )
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or not owned by user"
        )
    
    # Get actions
    result = await db.execute(select(Action).where(Action.agent_id == agent_id))
    actions = result.scalars().all()
    
    return actions


@router.get("/actions/{action_id}", response_model=ActionResponse)
async def get_action(
    action_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific action"""
    
    # Get action and verify ownership
    result = await db.execute(
        select(Action).where(Action.id == action_id)
    )
    action = result.scalar_one_or_none()
    
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found"
        )
    
    # Verify agent ownership
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == action.agent_id,
                AgentModel.owner_id == current_user.id
            )
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or not owned by user"
        )
    
    return action


@router.post("/agents/{agent_id}/actions", response_model=ActionResponse, status_code=status.HTTP_201_CREATED)
async def create_action(
    agent_id: int,
    action_data: ActionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new action"""
    
    # Verify agent ownership
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == agent_id,
                AgentModel.owner_id == current_user.id
            )
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or not owned by user"
        )
    
    # Create action
    action = Action(
        **action_data.dict(),
        agent_id=agent_id
    )
    
    db.add(action)
    await db.commit()
    await db.refresh(action)
    
    return action


@router.put("/actions/{action_id}", response_model=ActionResponse)
async def update_action(
    action_id: int,
    action_update: ActionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an action"""
    
    # Get action
    result = await db.execute(
        select(Action).where(Action.id == action_id)
    )
    action = result.scalar_one_or_none()
    
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found"
        )
    
    # Verify agent ownership
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == action.agent_id,
                AgentModel.owner_id == current_user.id
            )
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or not owned by user"
        )
    
    # Update action
    update_data = action_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(action, field, value)
    
    await db.commit()
    await db.refresh(action)
    
    return action


@router.delete("/actions/{action_id}")
async def delete_action(
    action_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an action"""
    
    # Get action
    result = await db.execute(
        select(Action).where(Action.id == action_id)
    )
    action = result.scalar_one_or_none()
    
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found"
        )
    
    # Verify agent ownership
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == action.agent_id,
                AgentModel.owner_id == current_user.id
            )
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or not owned by user"
        )
    
    # Delete action
    await db.delete(action)
    await db.commit()
    
    return {"message": "Action deleted successfully"}


@router.post("/actions/{action_id}/execute", response_model=ActionExecutionResponse)
async def execute_action(
    action_id: int,
    execution_request: ActionExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Execute an action"""
    
    # Get action
    result = await db.execute(
        select(Action).where(Action.id == action_id)
    )
    action = result.scalar_one_or_none()
    
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found"
        )
    
    # Verify agent ownership
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == action.agent_id,
                AgentModel.owner_id == current_user.id
            )
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or not owned by user"
        )
    
    # TODO: Implement actual action execution with sandboxing
    # For now, return a mock response
    
    return {
        "execution_id": f"exec_{action_id}_{int(time.time())}",
        "status": "completed",
        "result": {
            "output": "Mock execution result",
            "success": True
        },
        "error": None,
        "logs": ["Action execution started", "Action executed successfully"],
        "metrics": {
            "duration_ms": 150,
            "memory_usage_mb": 10
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# Hooks Endpoints
@router.get("/agents/{agent_id}/hooks", response_model=List[HookResponse])
async def get_agent_hooks(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all hooks for an agent"""
    
    # Verify agent ownership
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == agent_id,
                AgentModel.owner_id == current_user.id
            )
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or not owned by user"
        )
    
    # Get hooks
    result = await db.execute(
        select(Hook).where(
            and_(
                Hook.agent_id == agent_id,
                Hook.is_global == False
            )
        )
    )
    hooks = result.scalars().all()
    
    return hooks


@router.get("/hooks/global", response_model=List[HookResponse])
async def get_global_hooks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all global hooks"""
    
    # Get global hooks
    result = await db.execute(
        select(Hook).where(Hook.is_global == True)
    )
    hooks = result.scalars().all()
    
    return hooks


@router.get("/hooks/{hook_id}", response_model=HookResponse)
async def get_hook(
    hook_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific hook"""
    
    # Get hook
    result = await db.execute(
        select(Hook).where(Hook.id == hook_id)
    )
    hook = result.scalar_one_or_none()
    
    if not hook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hook not found"
        )
    
    # Verify ownership if not global
    if not hook.is_global and hook.agent_id:
        result = await db.execute(
            select(AgentModel).where(
                and_(
                    AgentModel.id == hook.agent_id,
                    AgentModel.owner_id == current_user.id
                )
            )
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found or not owned by user"
            )
    
    return hook


@router.post("/agents/{agent_id}/hooks", response_model=HookResponse, status_code=status.HTTP_201_CREATED)
async def create_hook(
    agent_id: int,
    hook_data: HookCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new hook"""
    
    # Verify agent ownership
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == agent_id,
                AgentModel.owner_id == current_user.id
            )
        )
    )
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or not owned by user"
        )
    
    # Create hook
    hook = Hook(
        **hook_data.dict(),
        agent_id=agent_id if not hook_data.is_global else None
    )
    
    db.add(hook)
    await db.commit()
    await db.refresh(hook)
    
    return hook


@router.post("/hooks/global", response_model=HookResponse, status_code=status.HTTP_201_CREATED)
async def create_global_hook(
    hook_data: HookCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new global hook"""
    
    # Create global hook
    hook = Hook(
        **hook_data.dict(),
        is_global=True,
        agent_id=None
    )
    
    db.add(hook)
    await db.commit()
    await db.refresh(hook)
    
    return hook


@router.put("/hooks/{hook_id}", response_model=HookResponse)
async def update_hook(
    hook_id: int,
    hook_update: HookUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a hook"""
    
    # Get hook
    result = await db.execute(
        select(Hook).where(Hook.id == hook_id)
    )
    hook = result.scalar_one_or_none()
    
    if not hook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hook not found"
        )
    
    # Verify ownership if not global
    if not hook.is_global and hook.agent_id:
        result = await db.execute(
            select(AgentModel).where(
                and_(
                    AgentModel.id == hook.agent_id,
                    AgentModel.owner_id == current_user.id
                )
            )
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found or not owned by user"
            )
    
    # Update hook
    update_data = hook_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(hook, field, value)
    
    await db.commit()
    await db.refresh(hook)
    
    return hook


@router.delete("/hooks/{hook_id}")
async def delete_hook(
    hook_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a hook"""
    
    # Get hook
    result = await db.execute(
        select(Hook).where(Hook.id == hook_id)
    )
    hook = result.scalar_one_or_none()
    
    if not hook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hook not found"
        )
    
    # Verify ownership if not global
    if not hook.is_global and hook.agent_id:
        result = await db.execute(
            select(AgentModel).where(
                and_(
                    AgentModel.id == hook.agent_id,
                    AgentModel.owner_id == current_user.id
                )
            )
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found or not owned by user"
            )
    
    # Delete hook
    await db.delete(hook)
    await db.commit()
    
    return {"message": "Hook deleted successfully"}


@router.post("/hooks/{hook_id}/execute", response_model=HookExecutionResponse)
async def execute_hook(
    hook_id: int,
    execution_request: HookExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Execute a hook"""
    
    # Get hook
    result = await db.execute(
        select(Hook).where(Hook.id == hook_id)
    )
    hook = result.scalar_one_or_none()
    
    if not hook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hook not found"
        )
    
    # Verify ownership if not global
    if not hook.is_global and hook.agent_id:
        result = await db.execute(
            select(AgentModel).where(
                and_(
                    AgentModel.id == hook.agent_id,
                    AgentModel.owner_id == current_user.id
                )
            )
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found or not owned by user"
            )
    
    # TODO: Implement actual hook execution
    # For now, return a mock response
    
    return {
        "execution_id": f"hook_exec_{hook_id}_{int(time.time())}",
        "status": "completed",
        "result": {
            "output": "Mock hook execution result",
            "success": True
        },
        "error": None,
        "logs": ["Hook execution started", "Hook executed successfully"],
        "timestamp": datetime.utcnow().isoformat()
    }