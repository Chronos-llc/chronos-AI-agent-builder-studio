from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.exc import OperationalError
from typing import List, Dict, Any
from datetime import datetime, UTC
import logging

from app.core.database import get_db
from app.core.usage_metering_engine import build_user_usage_snapshot
from app.models.user import User
from app.models.agent import AgentModel, AgentVersion, Action
from app.models.communication_channel import CommunicationChannel
from app.models.conversation import Conversation, ConversationMessage, ConversationAction
from app.models.usage import ResourceType, UsageType, UserPlan, UsageRecord
from app.api.auth import get_current_user
from app.schemas.agent import (
    AgentResponse, AgentCreate, AgentUpdate, AgentType, AgentHomeCard, AgentHomeCardsResponse,
    AgentVersionResponse, AgentVersionCreate,
    ActionResponse, ActionCreate, ActionUpdate,
    SubAgentConfig, AgentConfigUpdate
)

router = APIRouter()
logger = logging.getLogger(__name__)


def _normalize_channel_type(channel_type: Any) -> str | None:
    if channel_type is None:
        return None

    raw_value = channel_type.value if hasattr(channel_type, "value") else channel_type
    normalized = str(raw_value).strip().lower()
    if not normalized:
        return None

    # Handles legacy enum-string serialization like "ConversationChannelType.WEBCHAT"
    if "." in normalized:
        normalized = normalized.rsplit(".", 1)[-1]

    return normalized


@router.get("/", response_model=list[AgentResponse])
async def get_agents(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    agent_type: AgentType = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's agents with optional filtering"""

    query = select(AgentModel).where(AgentModel.owner_id == current_user.id)

    if status:
        query = query.where(AgentModel.status == status)

    if agent_type:
        query = query.where(AgentModel.agent_type == agent_type)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    agents = result.scalars().all()

    return agents


@router.get("/home/cards", response_model=AgentHomeCardsResponse)
async def get_home_agent_cards(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return live Home dashboard cards for the current user's agents."""

    agents_result = await db.execute(
        select(AgentModel)
        .where(AgentModel.owner_id == current_user.id)
        .order_by(AgentModel.updated_at.desc())
    )
    agents = list(agents_result.scalars().all())
    agent_ids = [agent.id for agent in agents]

    active_plan_result = await db.execute(
        select(UserPlan).where(
            and_(
                UserPlan.user_id == current_user.id,
                UserPlan.is_active.is_(True),
            )
        )
    )
    active_plan = active_plan_result.scalar_one_or_none()
    plan_value = active_plan.plan_type.value if active_plan and active_plan.plan_type else "pay_as_you_go"

    if not agent_ids:
        workspace_name = f"{current_user.full_name or current_user.username}'s Workspace"
        return AgentHomeCardsResponse(
            generated_at=datetime.now(UTC),
            workspace_name=workspace_name,
            plan=plan_value,
            agents=[],
        )

    message_counts_result = await db.execute(
        select(Conversation.agent_id, func.count(ConversationMessage.id))
        .join(ConversationMessage, ConversationMessage.conversation_id == Conversation.id)
        .where(
            and_(
                Conversation.user_id == current_user.id,
                Conversation.agent_id.in_(agent_ids),
                ConversationMessage.role == "user",
            )
        )
        .group_by(Conversation.agent_id)
    )
    message_counts = {
        int(agent_id): int(count)
        for agent_id, count in message_counts_result.all()
    }

    error_counts_result = await db.execute(
        select(Conversation.agent_id, func.count(ConversationAction.id))
        .join(ConversationAction, ConversationAction.conversation_id == Conversation.id)
        .where(
            and_(
                Conversation.user_id == current_user.id,
                Conversation.agent_id.in_(agent_ids),
                func.lower(ConversationAction.status).in_(["failed", "error"]),
            )
        )
        .group_by(Conversation.agent_id)
    )
    error_counts = {
        int(agent_id): int(count)
        for agent_id, count in error_counts_result.all()
    }

    last_message_result = await db.execute(
        select(Conversation.agent_id, func.max(Conversation.last_message_at))
        .where(
            and_(
                Conversation.user_id == current_user.id,
                Conversation.agent_id.in_(agent_ids),
            )
        )
        .group_by(Conversation.agent_id)
    )
    last_message_by_agent = {
        int(agent_id): timestamp
        for agent_id, timestamp in last_message_result.all()
    }

    channel_sets: dict[int, set[str]] = {agent_id: set() for agent_id in agent_ids}

    try:
        channel_config_result = await db.execute(
            select(CommunicationChannel.agent_id, CommunicationChannel.channel_type)
            .where(
                and_(
                    CommunicationChannel.agent_id.in_(agent_ids),
                    CommunicationChannel.is_active.is_(True),
                )
            )
        )
        for agent_id, channel_type in channel_config_result.all():
            if agent_id is None:
                continue
            normalized = _normalize_channel_type(channel_type)
            if normalized:
                channel_sets[int(agent_id)].add(normalized)
    except OperationalError:
        # Backward compatibility for DBs missing recent communication_channels columns.
        logger.warning("Skipping communication_channels join for home cards due to schema mismatch.")

    conversation_channels_result = await db.execute(
        select(Conversation.agent_id, Conversation.channel_type)
        .where(
            and_(
                Conversation.user_id == current_user.id,
                Conversation.agent_id.in_(agent_ids),
            )
        )
    )
    for agent_id, channel_type in conversation_channels_result.all():
        if agent_id is None:
            continue
        normalized = _normalize_channel_type(channel_type)
        if normalized:
            channel_sets[int(agent_id)].add(normalized)

    cards = [
        AgentHomeCard(
            id=agent.id,
            name=agent.name,
            status=agent.status.value if hasattr(agent.status, "value") else str(agent.status),
            created_at=agent.created_at,
            updated_at=agent.updated_at,
            last_message_at=last_message_by_agent.get(agent.id),
            deployed_channels=sorted(channel_sets.get(agent.id, set())),
            messages_received=message_counts.get(agent.id, 0),
            errors_encountered=error_counts.get(agent.id, 0),
        )
        for agent in agents
    ]

    workspace_name = f"{current_user.full_name or current_user.username}'s Workspace"
    return AgentHomeCardsResponse(
        generated_at=datetime.now(UTC),
        workspace_name=workspace_name,
        plan=plan_value,
        agents=cards,
    )


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new agent"""

    # Check plan + add-on limits via usage engine
    usage_snapshot = await build_user_usage_snapshot(db, current_user.id)
    agent_resource = next(
        (item for item in usage_snapshot.resources if item.resource_type == ResourceType.AGENTS),
        None,
    )
    if agent_resource and agent_resource.total_limit is not None and agent_resource.current >= agent_resource.total_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                "Agent creation limit reached. "
                f"Current {int(agent_resource.current)} / {int(agent_resource.total_limit)} allowed."
            ),
        )

    # Create agent - handle backward compatibility
    agent_data_dict = agent_data.dict()
    
    # If agent_type not provided, infer from voice configuration if available
    if "agent_type" not in agent_data_dict or not agent_data_dict["agent_type"]:
        # For new agents without explicit agent_type, default to text
        agent_data_dict["agent_type"] = AgentType.TEXT

    agent = AgentModel(
        **agent_data_dict,
        owner_id=current_user.id
    )

    db.add(agent)
    await db.commit()
    await db.refresh(agent)

    # Ensure plan row exists for legacy counters
    result = await db.execute(select(UserPlan).where(UserPlan.user_id == current_user.id))
    user_plan = result.scalar_one_or_none()
    if not user_plan:
        user_plan = UserPlan(user_id=current_user.id)
        db.add(user_plan)
    legacy_current_agents = int(user_plan.current_agents or 0)
    computed_current_agents = int(agent_resource.current if agent_resource else 0) + 1
    user_plan.current_agents = max(computed_current_agents, legacy_current_agents + 1)

    # Track legacy usage record for historical reporting compatibility.
    db.add(
        UsageRecord(
            user_id=current_user.id,
            agent_id=agent.id,
            usage_type=UsageType.AGENT_CREATION,
            amount=1.0,
            unit="agents",
        )
    )
    await db.commit()

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


# Sub-Agent Configuration Endpoints
@router.get("/{agent_id}/sub-agent-config", response_model=SubAgentConfig)
async def get_sub_agent_config(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get sub-agent configuration for an agent"""

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

    # Return sub-agent config or default if not set
    if agent.sub_agent_config:
        return agent.sub_agent_config
    else:
        return SubAgentConfig()  # Return default configuration


@router.put("/{agent_id}/sub-agent-config", response_model=SubAgentConfig)
async def update_sub_agent_config(
    agent_id: int,
    config_update: AgentConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update sub-agent configuration for an agent"""

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

    # Update sub-agent config
    if config_update.sub_agent_config:
        agent.sub_agent_config = config_update.sub_agent_config.dict()
        await db.commit()
        await db.refresh(agent)

    return agent.sub_agent_config


@router.post("/{agent_id}/sub-agent-config/reset", response_model=SubAgentConfig)
async def reset_sub_agent_config(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Reset sub-agent configuration to default values"""

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

    # Reset to default configuration
    default_config = SubAgentConfig()
    agent.sub_agent_config = default_config.dict()
    await db.commit()
    await db.refresh(agent)

    return agent.sub_agent_config


@router.get("/{agent_id}/sub-agent-config/defaults", response_model=SubAgentConfig)
async def get_default_sub_agent_config(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get default sub-agent configuration values"""

    # Get agent (just for validation)
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

    # Return default configuration
    return SubAgentConfig()


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
    agent_type: AgentType = Query(None, description="Filter by agent type (text/voice)"),
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

    # Agent type filter
    if agent_type:
        query = query.where(AgentModel.agent_type == agent_type)

    # Tags filter (simplified - in real implementation, would use proper JSON querying)
    if tags:
        # This is a simplified implementation
        query = query.where(AgentModel.tags.isnot(None))

    query = query.offset(skip).limit(limit).order_by(AgentModel.created_at.desc())

    result = await db.execute(query)
    agents = result.scalars().all()

    return agents
