from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Dict, Any

from app.core.database import get_db
from app.models.user import User
from app.models.agent import AgentModel, AgentVersion, Action
from app.models.usage import UserPlan, UsageType
from app.api.auth import get_current_user
from app.schemas.agent import (
    AgentResponse, AgentCreate, AgentUpdate,
    AgentVersionResponse, AgentVersionCreate,
    ActionResponse, ActionCreate, ActionUpdate
)

router = APIRouter()


@router.get("/", response_model=list[AgentResponse])
async def get_agents(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's agents with optional filtering"""
    
    query = select(AgentModel).where(AgentModel.owner_id == current_user.id)
    
    if status:
        query = query.where(AgentModel.status == status)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    agents = result.scalars().all()
    
    return agents


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new agent"""
    
    # Check user's plan limits
    result = await db.execute(select(UserPlan).where(UserPlan.user_id == current_user.id))
    user_plan = result.scalar_one_or_none()
    
    if not user_plan:
        user_plan = UserPlan(user_id=current_user.id)
        db.add(user_plan)
        await db.commit()
        await db.refresh(user_plan)
    
    # Check agent creation limit
    if not user_plan.can_create_agent():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Agent creation limit reached. Your plan allows {user_plan.max_agents} agents."
        )
    
    # Create agent
    agent = AgentModel(
        **agent_data.dict(),
        owner_id=current_user.id
    )
    
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    
    # Update plan counters
    user_plan.current_agents += 1
    await db.commit()
    
    # Track usage
    from app.api.usage import track_usage
    await track_usage(
        usage_data={
            "usage_type": UsageType.AGENT_CREATION,
            "amount": 1.0,
            "unit": "agents",
            "agent_id": agent.id
        },
        current_user=current_user,
        db=db
    )
    
    return agent


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific agent"""
    
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
            detail="Agent not found"
        )
    
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_update: AgentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an agent"""
    
    # Get agent
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
            detail="Agent not found"
        )
    
    # Update agent
    update_data = agent_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)
    
    await db.commit()
    await db.refresh(agent)
    
    return agent


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an agent"""
    
    # Get agent
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
            detail="Agent not found"
        )
    
    # Delete agent (cascade will delete related records)
    await db.delete(agent)
    await db.commit()
    
    return {"message": "Agent deleted successfully"}


# Agent Versions Endpoints
@router.get("/{agent_id}/versions", response_model=list[AgentVersionResponse])
async def get_agent_versions(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get agent versions"""
    
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
            detail="Agent not found"
        )
    
    # Get versions
    result = await db.execute(
        select(AgentVersion).where(AgentVersion.agent_id == agent_id)
    )
    versions = result.scalars().all()
    
    return versions


@router.post("/{agent_id}/versions", response_model=AgentVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_agent_version(
    agent_id: int,
    version_data: AgentVersionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new agent version"""
    
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
            detail="Agent not found"
        )
    
    # Create version
    version = AgentVersion(
        **version_data.dict(),
        agent_id=agent_id
    )
    
    db.add(version)
    await db.commit()
    await db.refresh(version)
    
    return version


@router.post("/{agent_id}/versions/{version_id}/rollback")
async def rollback_to_version(
    agent_id: int,
    version_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Rollback agent to a specific version"""
    
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
            detail="Agent not found"
        )
    
    # Get the version to rollback to
    result = await db.execute(
        select(AgentVersion).where(
            and_(
                AgentVersion.id == version_id,
                AgentVersion.agent_id == agent_id
            )
        )
    )
    version = result.scalar_one_or_none()
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    
    # Apply the configuration snapshot to the agent
    config_snapshot = version.config_snapshot
    
    # Update agent fields from snapshot
    for field, value in config_snapshot.items():
        if hasattr(agent, field):
            setattr(agent, field, value)
    
    await db.commit()
    await db.refresh(agent)
    
    return {"message": f"Agent rolled back to version {version.version_number}", "agent": agent}


@router.post("/{agent_id}/versions/compare")
async def compare_versions(
    agent_id: int,
    comparison_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Compare two agent versions"""
    
    version1_id = comparison_data.get("version1_id")
    version2_id = comparison_data.get("version2_id")
    
    if not version1_id or not version2_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both version1_id and version2_id are required"
        )
    
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
            detail="Agent not found"
        )
    
    # Get both versions
    result = await db.execute(
        select(AgentVersion).where(
            AgentVersion.id.in_([version1_id, version2_id])
        )
    )
    versions = result.scalars().all()
    
    if len(versions) != 2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both versions not found"
        )
    
    version1 = next(v for v in versions if v.id == version1_id)
    version2 = next(v for v in versions if v.id == version2_id)
    
    # Compare configurations
    diffs = []
    config1 = version1.config_snapshot or {}
    config2 = version2.config_snapshot or {}
    
    # Get all unique keys from both configs
    all_keys = set(config1.keys()) | set(config2.keys())
    
    for key in all_keys:
        value1 = config1.get(key)
        value2 = config2.get(key)
        
        if value1 != value2:
            change_type = "added" if value1 is None else "removed" if value2 is None else "modified"
            diffs.append({
                "field": key,
                "old_value": value1,
                "new_value": value2,
                "change_type": change_type
            })
    
    return diffs


# Actions Endpoints
@router.get("/{agent_id}/actions", response_model=list[ActionResponse])
async def get_agent_actions(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get agent actions"""
    
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
            detail="Agent not found"
        )
    
    # Get actions
    result = await db.execute(select(Action).where(Action.agent_id == agent_id))
    actions = result.scalars().all()
    
    return actions


@router.post("/{agent_id}/actions", response_model=ActionResponse, status_code=status.HTTP_201_CREATED)
async def create_agent_action(
    agent_id: int,
    action_data: ActionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new agent action"""
    
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
            detail="Agent not found"
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


@router.put("/{agent_id}/actions/{action_id}", response_model=ActionResponse)
async def update_agent_action(
    agent_id: int,
    action_id: int,
    action_update: ActionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an agent action"""
    
    # Verify agent ownership and action exists
    result = await db.execute(
        select(Action).where(
            and_(
                Action.id == action_id,
                Action.agent_id == agent_id
            )
        )
    )
    action = result.scalar_one_or_none()
    
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found"
        )
    
    # Update action
    update_data = action_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(action, field, value)
    
    await db.commit()
    await db.refresh(action)
    
    return action


@router.delete("/{agent_id}/actions/{action_id}")
async def delete_agent_action(
    agent_id: int,
    action_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an agent action"""
    
    # Verify agent ownership and action exists
    result = await db.execute(
        select(Action).where(
            and_(
                Action.id == action_id,
                Action.agent_id == agent_id
            )
        )
    )
    action = result.scalar_one_or_none()
    
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found"
        )
    
    # Delete action
    await db.delete(action)
    await db.commit()
    
    return {"message": "Action deleted successfully"}


# Bulk operations and enhanced filtering
@router.get("/stats/overview")
async def get_agents_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get agents overview with statistics"""
    
    # Get basic counts
    total_agents = len(current_user.agents)
    active_agents = len([agent for agent in current_user.agents if agent.status.value == "active"])
    draft_agents = len([agent for agent in current_user.agents if agent.status.value == "draft"])
    
    # Get usage statistics
    total_usage = sum(agent.usage_count for agent in current_user.agents)
    avg_success_rate = sum(agent.success_rate for agent in current_user.agents) / max(total_agents, 1)
    
    return {
        "total_agents": total_agents,
        "active_agents": active_agents,
        "draft_agents": draft_agents,
        "total_usage": total_usage,
        "avg_success_rate": round(avg_success_rate, 2),
        "recent_agents": [
            {
                "id": agent.id,
                "name": agent.name,
                "status": agent.status.value,
                "created_at": agent.created_at.isoformat()
            }
            for agent in sorted(current_user.agents, key=lambda x: x.created_at, reverse=True)[:5]
        ]
    }


@router.post("/bulk-update")
async def bulk_update_agents(
    agent_ids: List[int],
    updates: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Bulk update multiple agents"""
    
    # Verify ownership of all agents
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id.in_(agent_ids),
                AgentModel.owner_id == current_user.id
            )
        )
    )
    agents = result.scalars().all()
    
    if len(agents) != len(agent_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Some agents not found or not owned by user"
        )
    
    # Apply updates
    updated_count = 0
    for agent in agents:
        for field, value in updates.items():
            if hasattr(agent, field):
                setattr(agent, field, value)
        updated_count += 1
    
    await db.commit()
    
    return {"message": f"Updated {updated_count} agents", "updated_count": updated_count}


@router.post("/bulk-delete")
async def bulk_delete_agents(
    agent_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Bulk delete multiple agents"""
    
    # Verify ownership of all agents
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id.in_(agent_ids),
                AgentModel.owner_id == current_user.id
            )
        )
    )
    agents = result.scalars().all()
    
    if len(agents) != len(agent_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Some agents not found or not owned by user"
        )
    
    # Delete agents
    deleted_count = 0
    for agent in agents:
        await db.delete(agent)
        deleted_count += 1
    
    await db.commit()
    
    return {"message": f"Deleted {deleted_count} agents", "deleted_count": deleted_count}


@router.get("/search")
async def search_agents(
    q: str = Query(..., description="Search query"),
    status: str = Query(None, description="Filter by status"),
    tags: List[str] = Query(None, description="Filter by tags"),
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search agents with advanced filtering"""
    
    query = select(AgentModel).where(AgentModel.owner_id == current_user.id)
    
    # Text search
    if q:
        query = query.where(
            or_(
                AgentModel.name.ilike(f"%{q}%"),
                AgentModel.description.ilike(f"%{q}%")
            )
        )
    
    # Status filter
    if status:
        query = query.where(AgentModel.status == status)
    
    # Tags filter (simplified - in real implementation, would use proper JSON querying)
    if tags:
        # This is a simplified implementation
        query = query.where(AgentModel.tags.isnot(None))
    
    query = query.offset(skip).limit(limit).order_by(AgentModel.created_at.desc())
    
    result = await db.execute(query)
    agents = result.scalars().all()
    
    return agents