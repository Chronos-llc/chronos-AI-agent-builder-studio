from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.agent import AgentModel
from app.models.voice import VoiceConfiguration
from app.schemas.voice import (
    VoiceConfigurationCreate,
    VoiceConfigurationUpdate,
    VoiceConfigurationResponse,
)

router = APIRouter()


async def _get_agent_or_404(
    agent_id: int,
    current_user: User,
    db: AsyncSession,
) -> AgentModel:
    result = await db.execute(
        select(AgentModel).where(
            and_(
                AgentModel.id == agent_id,
                AgentModel.owner_id == current_user.id,
            )
        )
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    return agent


async def _get_or_create_voice_config(
    agent: AgentModel,
    current_user: User,
    db: AsyncSession,
) -> VoiceConfiguration:
    if agent.voice_configuration:
        return agent.voice_configuration

    defaults = VoiceConfigurationCreate()
    config = VoiceConfiguration(
        agent_id=agent.id,
        user_id=current_user.id,
        **defaults.dict(),
    )
    db.add(config)
    await db.commit()
    await db.refresh(config)
    return config


@router.get(
    "/agents/{agent_id}/voice-config",
    response_model=VoiceConfigurationResponse,
)
async def get_voice_config(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get voice configuration for an agent, create defaults if missing."""
    agent = await _get_agent_or_404(agent_id, current_user, db)
    config = await _get_or_create_voice_config(agent, current_user, db)
    return config


@router.put(
    "/agents/{agent_id}/voice-config",
    response_model=VoiceConfigurationResponse,
)
async def update_voice_config(
    agent_id: int,
    config_update: VoiceConfigurationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update voice configuration for an agent."""
    agent = await _get_agent_or_404(agent_id, current_user, db)
    config = await _get_or_create_voice_config(agent, current_user, db)

    update_data = config_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)

    await db.commit()
    await db.refresh(config)
    return config


@router.post(
    "/agents/{agent_id}/voice-config/reset",
    response_model=VoiceConfigurationResponse,
)
async def reset_voice_config(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reset voice configuration to defaults."""
    agent = await _get_agent_or_404(agent_id, current_user, db)
    config = await _get_or_create_voice_config(agent, current_user, db)

    defaults = VoiceConfigurationCreate()
    for field, value in defaults.dict().items():
        setattr(config, field, value)

    await db.commit()
    await db.refresh(config)
    return config
