from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, timedelta
from typing import List

from app.core.database import get_db
from app.models.user import User
from app.models.agent import AgentModel
from app.models.usage import UsageRecord, UserPlan, UsageType
from app.api.auth import get_current_user
from app.schemas.usage import (
    UsageRecordCreate, UsageRecordResponse, UsageStats,
    UserPlanResponse, UserPlanUpdate
)

router = APIRouter()


@router.post("/track", response_model=UsageRecordResponse, status_code=status.HTTP_201_CREATED)
async def track_usage(
    usage_data: UsageRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Track user usage"""
    
    # Verify agent ownership if agent_id is provided
    if usage_data.agent_id:
        result = await db.execute(
            select(AgentModel).where(
                and_(
                    AgentModel.id == usage_data.agent_id,
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
    
    # Create usage record
    usage_record = UsageRecord(
        **usage_data.dict(),
        user_id=current_user.id
    )
    
    db.add(usage_record)
    await db.commit()
    await db.refresh(usage_record)
    
    # Update user plan counters
    await update_user_plan_counters(current_user.id, usage_data.usage_type, usage_data.amount, db)
    
    return usage_record


@router.get("/stats", response_model=UsageStats)
async def get_usage_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user usage statistics and plan limits"""
    
    # Get user's plan
    result = await db.execute(select(UserPlan).where(UserPlan.user_id == current_user.id))
    user_plan = result.scalar_one_or_none()
    
    if not user_plan:
        # Create default free plan
        user_plan = UserPlan(user_id=current_user.id)
        db.add(user_plan)
        await db.commit()
        await db.refresh(user_plan)
    
    # Get usage statistics
    total_agents = len(current_user.agents)
    active_agents = len([agent for agent in current_user.agents if agent.status.value == "active"])
    
    # Get API calls this month
    current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(func.sum(UsageRecord.amount)).where(
            and_(
                UsageRecord.user_id == current_user.id,
                UsageRecord.usage_type == UsageType.API_CALL,
                UsageRecord.created_at >= current_month
            )
        )
    )
    total_api_calls = result.scalar() or 0
    
    # Get current storage usage
    result = await db.execute(
        select(func.sum(UsageRecord.amount)).where(
            and_(
                UsageRecord.user_id == current_user.id,
                UsageRecord.usage_type == UsageType.STORAGE
            )
        )
    )
    current_storage_mb = result.scalar() or 0
    
    # Calculate usage percentages
    plan_usage_percentages = {
        "agents": (total_agents / user_plan.max_agents) * 100,
        "api_calls": (total_api_calls / user_plan.max_api_calls_monthly) * 100,
        "storage": (current_storage_mb / user_plan.max_storage_mb) * 100
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
        remaining_storage_mb=max(0, user_plan.max_storage_mb - current_storage_mb)
    )


@router.get("/plan", response_model=UserPlanResponse)
async def get_user_plan(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's current plan"""
    
    result = await db.execute(select(UserPlan).where(UserPlan.user_id == current_user.id))
    user_plan = result.scalar_one_or_none()
    
    if not user_plan:
        # Create default free plan
        user_plan = UserPlan(user_id=current_user.id)
        db.add(user_plan)
        await db.commit()
        await db.refresh(user_plan)
    
    return user_plan


@router.put("/plan", response_model=UserPlanResponse)
async def update_user_plan(
    plan_update: UserPlanUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user's plan (admin only in real implementation)"""
    
    result = await db.execute(select(UserPlan).where(UserPlan.user_id == current_user.id))
    user_plan = result.scalar_one_or_none()
    
    if not user_plan:
        user_plan = UserPlan(user_id=current_user.id)
        db.add(user_plan)
    
    # Update plan fields
    update_data = plan_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user_plan, field, value)
    
    await db.commit()
    await db.refresh(user_plan)
    
    return user_plan


@router.get("/records", response_model=List[UsageRecordResponse])
async def get_usage_records(
    skip: int = 0,
    limit: int = 50,
    usage_type: UsageType = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's usage records"""
    
    query = select(UsageRecord).where(UsageRecord.user_id == current_user.id)
    
    if usage_type:
        query = query.where(UsageRecord.usage_type == usage_type)
    
    query = query.offset(skip).limit(limit).order_by(UsageRecord.created_at.desc())
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    return records


async def update_user_plan_counters(user_id: int, usage_type: UsageType, amount: float, db: AsyncSession):
    """Update user plan counters based on usage"""
    
    result = await db.execute(select(UserPlan).where(UserPlan.user_id == user_id))
    user_plan = result.scalar_one_or_none()
    
    if not user_plan:
        return
    
    if usage_type == UsageType.AGENT_CREATION:
        user_plan.current_agents += 1
    elif usage_type == UsageType.API_CALL:
        user_plan.current_api_calls_month += int(amount)
    elif usage_type == UsageType.STORAGE:
        user_plan.current_storage_mb += amount
    
    await db.commit()