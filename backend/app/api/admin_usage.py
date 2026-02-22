from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rbac import check_admin_permission, get_admin_user, log_admin_action
from app.models.admin import AdminUser, PermissionEnum
from app.models.usage import ResourceType, UserAddonAllocation
from app.schemas.usage import AddonAllocationCreate, AddonAllocationResponse, ResourceUsageType

router = APIRouter()


async def _require_admin_usage_permission(admin_user: AdminUser, db: AsyncSession) -> None:
    allowed = await check_admin_permission(admin_user, PermissionEnum.MANAGE_SYSTEM, db)
    if not allowed:
        allowed = await check_admin_permission(admin_user, PermissionEnum.MANAGE_USERS, db)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: admin usage management required",
        )


@router.get("/addons", response_model=list[AddonAllocationResponse])
async def get_user_addons(
    user_id: Optional[int] = Query(None, ge=1),
    include_inactive: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    admin_user: AdminUser = Depends(get_admin_user),
):
    await _require_admin_usage_permission(admin_user, db)

    query = select(UserAddonAllocation)
    if user_id:
        query = query.where(UserAddonAllocation.user_id == user_id)
    if not include_inactive:
        now = datetime.now(timezone.utc)
        query = query.where(
            and_(
                UserAddonAllocation.is_active.is_(True),
                UserAddonAllocation.effective_from <= now,
                or_(UserAddonAllocation.effective_to.is_(None), UserAddonAllocation.effective_to > now),
            )
        )

    rows = (await db.execute(query.order_by(UserAddonAllocation.created_at.desc()))).scalars().all()
    return [
        AddonAllocationResponse(
            id=row.id,
            user_id=row.user_id,
            resource_type=ResourceUsageType(row.resource_type.value),
            units=row.units,
            unit_price_usd=row.unit_price_usd,
            currency=row.currency,
            is_active=row.is_active,
            effective_from=row.effective_from,
            effective_to=row.effective_to,
            metadata=row.additional_metadata,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
        for row in rows
    ]


@router.post("/addons", response_model=AddonAllocationResponse, status_code=status.HTTP_201_CREATED)
async def create_user_addon(
    payload: AddonAllocationCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: AdminUser = Depends(get_admin_user),
):
    await _require_admin_usage_permission(admin_user, db)

    allocation = UserAddonAllocation(
        user_id=payload.user_id,
        resource_type=ResourceType(payload.resource_type.value),
        units=payload.units,
        unit_price_usd=payload.unit_price_usd,
        currency=payload.currency.upper(),
        is_active=True,
        effective_from=payload.effective_from or datetime.now(timezone.utc),
        effective_to=payload.effective_to,
        additional_metadata=payload.metadata,
    )
    db.add(allocation)
    await db.commit()
    await db.refresh(allocation)

    await log_admin_action(
        admin_user=admin_user,
        action="create_usage_addon_allocation",
        resource_type="usage_addon",
        resource_id=allocation.id,
        details={
            "target_user_id": allocation.user_id,
            "resource_type": allocation.resource_type.value,
            "units": allocation.units,
        },
        db=db,
    )

    return AddonAllocationResponse(
        id=allocation.id,
        user_id=allocation.user_id,
        resource_type=ResourceUsageType(allocation.resource_type.value),
        units=allocation.units,
        unit_price_usd=allocation.unit_price_usd,
        currency=allocation.currency,
        is_active=allocation.is_active,
        effective_from=allocation.effective_from,
        effective_to=allocation.effective_to,
        metadata=allocation.additional_metadata,
        created_at=allocation.created_at,
        updated_at=allocation.updated_at,
    )


@router.delete("/addons/{allocation_id}")
async def deactivate_user_addon(
    allocation_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: AdminUser = Depends(get_admin_user),
):
    await _require_admin_usage_permission(admin_user, db)

    allocation = (
        await db.execute(select(UserAddonAllocation).where(UserAddonAllocation.id == allocation_id))
    ).scalar_one_or_none()
    if not allocation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Add-on allocation not found")

    allocation.is_active = False
    allocation.effective_to = allocation.effective_to or datetime.now(timezone.utc)
    await db.commit()

    await log_admin_action(
        admin_user=admin_user,
        action="deactivate_usage_addon_allocation",
        resource_type="usage_addon",
        resource_id=allocation.id,
        details={"target_user_id": allocation.user_id},
        db=db,
    )

    return {"message": "Add-on allocation deactivated", "allocation_id": allocation.id}

