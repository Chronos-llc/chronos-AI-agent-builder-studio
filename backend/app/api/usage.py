from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.core.database import get_db
from app.core.usage_metering_engine import build_agent_usage_snapshot, build_user_usage_snapshot
from app.models.agent import AgentModel
from app.models.usage import AISpendEvent, UsageRecord, UserPlan, UsageType
from app.models.user import User
from app.schemas.usage import (
    AISpendTrackRequest,
    AISpendTrackResponse,
    AgentUsageResourcesResponse,
    ResourceUsageSnapshot,
    ResourceUsageType,
    UsageRecordCreate,
    UsageRecordResponse,
    UsageStats,
    UsageRecordWithAgent,
    UserPlanResponse,
    UserPlanUpdate,
    UsageResourcesResponse,
)

router = APIRouter()


async def _get_or_create_user_plan(user_id: int, db: AsyncSession) -> UserPlan:
    result = await db.execute(select(UserPlan).where(UserPlan.user_id == user_id))
    user_plan = result.scalar_one_or_none()
    if user_plan:
        return user_plan

    user_plan = UserPlan(user_id=user_id)
    db.add(user_plan)
    await db.commit()
    await db.refresh(user_plan)
    return user_plan


def _resource_snapshot_to_schema(snapshot: Any) -> ResourceUsageSnapshot:
    return ResourceUsageSnapshot(
        resource_type=ResourceUsageType(snapshot.resource_type.value),
        unit=snapshot.unit,
        current=snapshot.current,
        base_limit=snapshot.base_limit,
        addon_limit=snapshot.addon_limit,
        total_limit=snapshot.total_limit,
        percent_used=snapshot.percent_used,
        overage_units=snapshot.overage_units,
        estimated_overage_monthly_usd=snapshot.estimated_overage_monthly_usd,
    )


@router.post("/track", response_model=UsageRecordResponse, status_code=status.HTTP_201_CREATED)
async def track_usage(
    usage_data: UsageRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Track user usage (legacy endpoint retained for compatibility)."""

    if usage_data.agent_id:
        result = await db.execute(
            select(AgentModel).where(
                and_(AgentModel.id == usage_data.agent_id, AgentModel.owner_id == current_user.id)
            )
        )
        agent = result.scalar_one_or_none()
        if not agent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    payload = usage_data.model_dump()
    metadata = payload.pop("metadata", None)
    usage_record = UsageRecord(**payload, additional_metadata=metadata, user_id=current_user.id)
    db.add(usage_record)
    await db.commit()
    await db.refresh(usage_record)

    await update_user_plan_counters(
        current_user.id,
        usage_data.usage_type,
        usage_data.amount,
        db,
    )
    return usage_record


@router.get("/stats", response_model=UsageStats)
async def get_usage_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get legacy usage statistics."""

    user_plan = await _get_or_create_user_plan(current_user.id, db)

    total_agents = len(current_user.agents)
    active_agents = len([agent for agent in current_user.agents if agent.status.value == "active"])

    current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    total_api_calls = (
        await db.execute(
            select(func.sum(UsageRecord.amount)).where(
                and_(
                    UsageRecord.user_id == current_user.id,
                    UsageRecord.usage_type == UsageType.API_CALL,
                    UsageRecord.created_at >= current_month,
                )
            )
        )
    ).scalar() or 0

    current_storage_mb = (
        await db.execute(
            select(func.sum(UsageRecord.amount)).where(
                and_(
                    UsageRecord.user_id == current_user.id,
                    UsageRecord.usage_type == UsageType.STORAGE,
                )
            )
        )
    ).scalar() or 0

    plan_usage_percentages = {
        "agents": (total_agents / max(user_plan.max_agents, 1)) * 100,
        "api_calls": (total_api_calls / max(user_plan.max_api_calls_monthly, 1)) * 100,
        "storage": (current_storage_mb / max(user_plan.max_storage_mb, 1)) * 100,
    }

    return UsageStats(
        total_agents=total_agents,
        active_agents=active_agents,
        total_api_calls=int(total_api_calls),
        current_storage_mb=current_storage_mb,
        plan_usage_percentages=plan_usage_percentages,
        can_create_agent=user_plan.can_create_agent(),
        can_make_api_call=user_plan.can_make_api_call(),
        remaining_api_calls=max(0, user_plan.max_api_calls_monthly - int(total_api_calls)),
        remaining_agents=max(0, user_plan.max_agents - total_agents),
        remaining_storage_mb=max(0, user_plan.max_storage_mb - current_storage_mb),
    )


@router.get("/plan", response_model=UserPlanResponse)
async def get_user_plan(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _get_or_create_user_plan(current_user.id, db)


@router.put("/plan", response_model=UserPlanResponse)
async def update_user_plan(
    plan_update: UserPlanUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_plan = await _get_or_create_user_plan(current_user.id, db)
    update_data = plan_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user_plan, field, value)
    await db.commit()
    await db.refresh(user_plan)
    return user_plan


@router.get("/records", response_model=List[UsageRecordResponse])
async def get_usage_records(
    skip: int = 0,
    limit: int = 50,
    usage_type: UsageType | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(UsageRecord).where(UsageRecord.user_id == current_user.id)
    if usage_type:
        query = query.where(UsageRecord.usage_type == usage_type)
    query = query.offset(skip).limit(limit).order_by(UsageRecord.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/resources", response_model=UsageResourcesResponse)
async def get_resource_usage_snapshot(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    snapshot = await build_user_usage_snapshot(db, current_user.id)
    return UsageResourcesResponse(
        plan=snapshot.plan,
        resources=[_resource_snapshot_to_schema(item) for item in snapshot.resources],
        updated_at=snapshot.updated_at,
    )


@router.get("/resources/agents/{agent_id}", response_model=AgentUsageResourcesResponse)
async def get_agent_resource_usage_snapshot(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = (
        await db.execute(
            select(AgentModel).where(
                and_(
                    AgentModel.id == agent_id,
                    AgentModel.owner_id == current_user.id,
                )
            )
        )
    ).scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    snapshot = await build_agent_usage_snapshot(db, current_user.id, agent_id)
    return AgentUsageResourcesResponse(
        agent_id=agent_id,
        plan=snapshot.plan,
        resources=[_resource_snapshot_to_schema(item) for item in snapshot.resources],
        updated_at=snapshot.updated_at,
    )


@router.post("/ai-spend/track", response_model=AISpendTrackResponse, status_code=status.HTTP_201_CREATED)
async def track_ai_spend(
    payload: AISpendTrackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.agent_id is not None:
        agent = (
            await db.execute(
                select(AgentModel).where(
                    and_(
                        AgentModel.id == payload.agent_id,
                        AgentModel.owner_id == current_user.id,
                    )
                )
            )
        ).scalar_one_or_none()
        if not agent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    event = AISpendEvent(
        user_id=current_user.id,
        agent_id=payload.agent_id,
        provider=payload.provider,
        model=payload.model,
        cost_amount=payload.cost_amount,
        currency=payload.currency.upper(),
        tokens=payload.tokens,
        source=payload.source,
        additional_metadata=payload.metadata,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)

    return AISpendTrackResponse(
        id=event.id,
        user_id=event.user_id,
        agent_id=event.agent_id,
        cost_amount=float(event.cost_amount),
        currency=event.currency,
        event_at=event.event_at or event.created_at,
    )


async def update_user_plan_counters(user_id: int, usage_type: UsageType, amount: float, db: AsyncSession):
    user_plan = await _get_or_create_user_plan(user_id, db)

    if usage_type == UsageType.AGENT_CREATION:
        user_plan.current_agents += 1
    elif usage_type == UsageType.API_CALL:
        user_plan.current_api_calls_month += int(amount)
    elif usage_type == UsageType.STORAGE:
        user_plan.current_storage_mb += amount

    await db.commit()

