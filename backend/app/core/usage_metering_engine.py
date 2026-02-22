from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import AgentModel, AgentStatus
from app.models.agent_table import AgentTable, AgentTableRecord
from app.models.knowledge import KnowledgeChunk, KnowledgeFile
from app.models.usage import AISpendEvent, PlanType, ResourceType, UserAddonAllocation, UserPlan, WorkspaceMember


MB = 1024 * 1024
GB = 1024 * MB


RESOURCE_ORDER: list[ResourceType] = [
    ResourceType.AI_SPEND,
    ResourceType.FILE_STORAGE,
    ResourceType.VECTOR_DB_STORAGE,
    ResourceType.TABLE_ROWS,
    ResourceType.COLLABORATORS,
    ResourceType.AGENTS,
]

RESOURCE_UNITS: dict[ResourceType, str] = {
    ResourceType.AI_SPEND: "usd",
    ResourceType.FILE_STORAGE: "bytes",
    ResourceType.VECTOR_DB_STORAGE: "bytes",
    ResourceType.TABLE_ROWS: "rows",
    ResourceType.COLLABORATORS: "seats",
    ResourceType.AGENTS: "agents",
}

PLAN_BASE_LIMITS: dict[str, dict[ResourceType, Optional[float]]] = {
    "payg": {
        ResourceType.AI_SPEND: 5,
        ResourceType.FILE_STORAGE: 100 * MB,
        ResourceType.VECTOR_DB_STORAGE: 100 * MB,
        ResourceType.TABLE_ROWS: 1_000,
        ResourceType.COLLABORATORS: 1,
        ResourceType.AGENTS: 1,
    },
    "lite": {
        ResourceType.AI_SPEND: 50,
        ResourceType.FILE_STORAGE: 10 * GB,
        ResourceType.VECTOR_DB_STORAGE: 1 * GB,
        ResourceType.TABLE_ROWS: 100_000,
        ResourceType.COLLABORATORS: 2,
        ResourceType.AGENTS: 2,
    },
    "lotus": {
        ResourceType.AI_SPEND: 150,
        ResourceType.FILE_STORAGE: 10 * GB,
        ResourceType.VECTOR_DB_STORAGE: 1 * GB,
        ResourceType.TABLE_ROWS: 100_000,
        ResourceType.COLLABORATORS: 1,
        ResourceType.AGENTS: 5,
    },
    "team_developer": {
        ResourceType.AI_SPEND: 500,
        ResourceType.FILE_STORAGE: 10 * GB,
        ResourceType.VECTOR_DB_STORAGE: 2 * GB,
        ResourceType.TABLE_ROWS: 200_000,
        ResourceType.COLLABORATORS: 5,
        ResourceType.AGENTS: 10,
    },
    "special_service": {
        ResourceType.AI_SPEND: 1500,
        ResourceType.FILE_STORAGE: 10 * GB,
        ResourceType.VECTOR_DB_STORAGE: 2 * GB,
        ResourceType.TABLE_ROWS: 200_000,
        ResourceType.COLLABORATORS: 5,
        ResourceType.AGENTS: 20,
    },
    "enterprise": {
        ResourceType.AI_SPEND: None,
        ResourceType.FILE_STORAGE: 10 * GB,
        ResourceType.VECTOR_DB_STORAGE: 2 * GB,
        ResourceType.TABLE_ROWS: 200_000,
        ResourceType.COLLABORATORS: 5,
        ResourceType.AGENTS: None,
    },
}

ADDON_INCREMENTS: dict[ResourceType, tuple[float, float]] = {
    ResourceType.FILE_STORAGE: (10 * GB, 10.0),
    ResourceType.VECTOR_DB_STORAGE: (1 * GB, 20.0),
    ResourceType.AGENTS: (1, 10.0),
    ResourceType.TABLE_ROWS: (100_000, 25.0),
    ResourceType.COLLABORATORS: (1, 25.0),
}


@dataclass
class ResourceSnapshot:
    resource_type: ResourceType
    unit: str
    current: float
    base_limit: Optional[float]
    addon_limit: float
    total_limit: Optional[float]
    percent_used: float
    overage_units: float
    estimated_overage_monthly_usd: float


@dataclass
class UsageSnapshot:
    plan: str
    resources: list[ResourceSnapshot]
    updated_at: datetime


def _normalize_plan_type(plan_type: Optional[PlanType | str]) -> str:
    if not plan_type:
        return "payg"

    raw = plan_type.value if isinstance(plan_type, PlanType) else str(plan_type)
    raw = raw.strip().lower()
    if raw in {"free", "payg", "pay_as_you_go", "pay-as-you-go"}:
        return "payg"
    if raw in {"lite"}:
        return "lite"
    if raw in {"lotus"}:
        return "lotus"
    if raw in {"team_developer", "team", "team_developers", "team-and-developers"}:
        return "team_developer"
    if raw in {"special_service", "special"}:
        return "special_service"
    if raw in {"pro"}:
        return "team_developer"
    if raw in {"enterprise"}:
        return "enterprise"
    return "payg"


def get_base_limits_for_plan(plan_type: Optional[PlanType | str]) -> dict[ResourceType, Optional[float]]:
    normalized = _normalize_plan_type(plan_type)
    return PLAN_BASE_LIMITS.get(normalized, PLAN_BASE_LIMITS["payg"]).copy()


def get_billing_cycle_start(now: Optional[datetime] = None) -> datetime:
    now = now or datetime.now(timezone.utc)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


async def _fetch_plan(db: AsyncSession, user_id: int) -> UserPlan | None:
    result = await db.execute(select(UserPlan).where(UserPlan.user_id == user_id))
    return result.scalar_one_or_none()


async def _fetch_addon_limits(db: AsyncSession, user_id: int, as_of: datetime) -> dict[ResourceType, float]:
    query = (
        select(UserAddonAllocation)
        .where(
            and_(
                UserAddonAllocation.user_id == user_id,
                UserAddonAllocation.is_active.is_(True),
                UserAddonAllocation.effective_from <= as_of,
                (UserAddonAllocation.effective_to.is_(None) | (UserAddonAllocation.effective_to > as_of)),
            )
        )
        .order_by(UserAddonAllocation.created_at.desc())
    )
    rows = (await db.execute(query)).scalars().all()

    limits: dict[ResourceType, float] = {resource: 0.0 for resource in RESOURCE_ORDER}
    for allocation in rows:
        if allocation.resource_type not in ADDON_INCREMENTS:
            continue
        increment, _price = ADDON_INCREMENTS[allocation.resource_type]
        limits[allocation.resource_type] += max(allocation.units, 0) * increment
    return limits


async def _aggregate_user_current_usage(
    db: AsyncSession,
    user_id: int,
    cycle_start: datetime,
) -> dict[ResourceType, float]:
    ai_spend_usd = (
        await db.execute(
            select(func.coalesce(func.sum(AISpendEvent.cost_amount), 0.0)).where(
                and_(
                    AISpendEvent.user_id == user_id,
                    AISpendEvent.currency == "USD",
                    AISpendEvent.event_at >= cycle_start,
                )
            )
        )
    ).scalar_one()

    file_storage = (
        await db.execute(
            select(func.coalesce(func.sum(func.coalesce(KnowledgeFile.object_size, KnowledgeFile.file_size)), 0)).where(
                KnowledgeFile.agent_id.in_(
                    select(AgentModel.id).where(AgentModel.owner_id == user_id)
                )
            )
        )
    ).scalar_one()

    vector_storage = (
        await db.execute(
            select(func.coalesce(func.sum(func.length(KnowledgeChunk.content)), 0))
            .join(KnowledgeFile, KnowledgeChunk.knowledge_file_id == KnowledgeFile.id)
            .where(
                KnowledgeFile.agent_id.in_(
                    select(AgentModel.id).where(AgentModel.owner_id == user_id)
                )
            )
        )
    ).scalar_one()

    table_rows = (
        await db.execute(
            select(func.count(AgentTableRecord.id))
            .join(AgentTable, AgentTable.id == AgentTableRecord.table_id)
            .where(AgentTable.user_id == user_id)
        )
    ).scalar_one()

    collaborators = (
        await db.execute(
            select(func.count(WorkspaceMember.id)).where(
                and_(
                    WorkspaceMember.owner_user_id == user_id,
                    WorkspaceMember.status == "active",
                )
            )
        )
    ).scalar_one()

    agents = (
        await db.execute(
            select(func.count(AgentModel.id)).where(
                and_(
                    AgentModel.owner_id == user_id,
                    AgentModel.status != AgentStatus.ARCHIVED,
                )
            )
        )
    ).scalar_one()

    return {
        ResourceType.AI_SPEND: float(ai_spend_usd or 0.0),
        ResourceType.FILE_STORAGE: float(file_storage or 0.0),
        ResourceType.VECTOR_DB_STORAGE: float(vector_storage or 0.0),
        ResourceType.TABLE_ROWS: float(table_rows or 0.0),
        ResourceType.COLLABORATORS: float((collaborators or 0) + 1),  # owner seat
        ResourceType.AGENTS: float(agents or 0.0),
    }


async def _aggregate_agent_current_usage(
    db: AsyncSession,
    user_id: int,
    agent_id: int,
    cycle_start: datetime,
) -> dict[ResourceType, float]:
    ai_spend_usd = (
        await db.execute(
            select(func.coalesce(func.sum(AISpendEvent.cost_amount), 0.0)).where(
                and_(
                    AISpendEvent.user_id == user_id,
                    AISpendEvent.agent_id == agent_id,
                    AISpendEvent.currency == "USD",
                    AISpendEvent.event_at >= cycle_start,
                )
            )
        )
    ).scalar_one()

    file_storage = (
        await db.execute(
            select(func.coalesce(func.sum(func.coalesce(KnowledgeFile.object_size, KnowledgeFile.file_size)), 0)).where(
                KnowledgeFile.agent_id == agent_id
            )
        )
    ).scalar_one()

    vector_storage = (
        await db.execute(
            select(func.coalesce(func.sum(func.length(KnowledgeChunk.content)), 0))
            .join(KnowledgeFile, KnowledgeChunk.knowledge_file_id == KnowledgeFile.id)
            .where(KnowledgeFile.agent_id == agent_id)
        )
    ).scalar_one()

    table_rows = (
        await db.execute(
            select(func.count(AgentTableRecord.id))
            .join(AgentTable, AgentTable.id == AgentTableRecord.table_id)
            .where(AgentTable.agent_id == agent_id)
        )
    ).scalar_one()

    return {
        ResourceType.AI_SPEND: float(ai_spend_usd or 0.0),
        ResourceType.FILE_STORAGE: float(file_storage or 0.0),
        ResourceType.VECTOR_DB_STORAGE: float(vector_storage or 0.0),
        ResourceType.TABLE_ROWS: float(table_rows or 0.0),
        ResourceType.COLLABORATORS: 0.0,
        ResourceType.AGENTS: 1.0,
    }


def _build_resource_snapshot(
    resource_type: ResourceType,
    current: float,
    base_limit: Optional[float],
    addon_limit: float,
) -> ResourceSnapshot:
    total_limit = (base_limit + addon_limit) if base_limit is not None else None
    percent_used = 0.0
    overage_units = 0.0
    estimated_overage_monthly_usd = 0.0

    if total_limit is not None and total_limit > 0:
        percent_used = min(999.0, (current / total_limit) * 100.0)
        overage_units = max(current - total_limit, 0.0)
        if overage_units > 0 and resource_type in ADDON_INCREMENTS:
            increment, unit_price = ADDON_INCREMENTS[resource_type]
            needed_units = math.ceil(overage_units / increment)
            estimated_overage_monthly_usd = float(needed_units * unit_price)
    elif total_limit is None:
        percent_used = 0.0
        overage_units = 0.0

    return ResourceSnapshot(
        resource_type=resource_type,
        unit=RESOURCE_UNITS[resource_type],
        current=current,
        base_limit=base_limit,
        addon_limit=addon_limit,
        total_limit=total_limit,
        percent_used=percent_used,
        overage_units=overage_units,
        estimated_overage_monthly_usd=estimated_overage_monthly_usd,
    )


async def build_user_usage_snapshot(db: AsyncSession, user_id: int) -> UsageSnapshot:
    now = datetime.now(timezone.utc)
    cycle_start = get_billing_cycle_start(now)
    user_plan = await _fetch_plan(db, user_id)
    plan_key = _normalize_plan_type(user_plan.plan_type if user_plan else None)
    base_limits = get_base_limits_for_plan(user_plan.plan_type if user_plan else None)
    addon_limits = await _fetch_addon_limits(db, user_id, now)
    current_usage = await _aggregate_user_current_usage(db, user_id, cycle_start)

    resources = [
        _build_resource_snapshot(
            resource_type=resource,
            current=float(current_usage.get(resource, 0.0)),
            base_limit=base_limits.get(resource),
            addon_limit=float(addon_limits.get(resource, 0.0)),
        )
        for resource in RESOURCE_ORDER
    ]

    return UsageSnapshot(
        plan=plan_key,
        resources=resources,
        updated_at=now,
    )


async def build_agent_usage_snapshot(db: AsyncSession, user_id: int, agent_id: int) -> UsageSnapshot:
    now = datetime.now(timezone.utc)
    cycle_start = get_billing_cycle_start(now)
    user_plan = await _fetch_plan(db, user_id)
    plan_key = _normalize_plan_type(user_plan.plan_type if user_plan else None)
    base_limits = get_base_limits_for_plan(user_plan.plan_type if user_plan else None)
    addon_limits = await _fetch_addon_limits(db, user_id, now)
    current_usage = await _aggregate_agent_current_usage(db, user_id, agent_id, cycle_start)

    resources = [
        _build_resource_snapshot(
            resource_type=resource,
            current=float(current_usage.get(resource, 0.0)),
            base_limit=base_limits.get(resource),
            addon_limit=float(addon_limits.get(resource, 0.0)),
        )
        for resource in RESOURCE_ORDER
        if resource in {
            ResourceType.AI_SPEND,
            ResourceType.FILE_STORAGE,
            ResourceType.VECTOR_DB_STORAGE,
            ResourceType.TABLE_ROWS,
        }
    ]

    return UsageSnapshot(
        plan=plan_key,
        resources=resources,
        updated_at=now,
    )


def get_resource_total_limit(
    plan: Optional[PlanType | str],
    resource: ResourceType,
    addon_units: int = 0,
) -> Optional[float]:
    base_limit = get_base_limits_for_plan(plan).get(resource)
    if base_limit is None:
        return None
    if resource not in ADDON_INCREMENTS or addon_units <= 0:
        return base_limit
    increment, _price = ADDON_INCREMENTS[resource]
    return base_limit + (addon_units * increment)


def estimate_required_addon_units(resource: ResourceType, overage: float) -> int:
    if resource not in ADDON_INCREMENTS or overage <= 0:
        return 0
    increment, _price = ADDON_INCREMENTS[resource]
    return int(math.ceil(overage / increment))

