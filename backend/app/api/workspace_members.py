from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.core.database import get_db
from app.core.usage_metering_engine import build_user_usage_snapshot
from app.models.usage import ResourceType, WorkspaceMember
from app.models.user import User
from app.schemas.workspace import WorkspaceMemberCreate, WorkspaceMemberResponse

router = APIRouter()


@router.get("/members", response_model=list[WorkspaceMemberResponse])
async def list_workspace_members(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    members = (
        await db.execute(
            select(WorkspaceMember).where(
                and_(
                    WorkspaceMember.owner_user_id == current_user.id,
                    WorkspaceMember.status == "active",
                )
            )
        )
    ).scalars().all()
    return members


@router.post("/members", response_model=WorkspaceMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_workspace_member(
    payload: WorkspaceMemberCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.member_user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Owner is already part of workspace")

    candidate = (await db.execute(select(User).where(User.id == payload.member_user_id))).scalar_one_or_none()
    if not candidate or not candidate.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member user not found")

    # Use FOR UPDATE lock to prevent race conditions when checking collaborator limits
    existing = (
        await db.execute(
            select(WorkspaceMember)
            .where(
                and_(
                    WorkspaceMember.owner_user_id == current_user.id,
                    WorkspaceMember.member_user_id == payload.member_user_id,
                )
            )
            .with_for_update()
        )
    ).scalar_one_or_none()
    if existing and existing.status == "active":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already a collaborator")

    usage_snapshot = await build_user_usage_snapshot(db, current_user.id)
    collaborator_resource = next(
        (item for item in usage_snapshot.resources if item.resource_type == ResourceType.COLLABORATORS),
        None,
    )
    if (
        collaborator_resource
        and collaborator_resource.total_limit is not None
        and collaborator_resource.current >= collaborator_resource.total_limit
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                "Collaborator seat limit reached. "
                f"Current {int(collaborator_resource.current)} / {int(collaborator_resource.total_limit)} seats."
            ),
        )

    if existing:
        existing.status = "active"
        existing.role = payload.role
        await db.commit()
        await db.refresh(existing)
        return existing

    member = WorkspaceMember(
        owner_user_id=current_user.id,
        member_user_id=payload.member_user_id,
        role=payload.role,
        status="active",
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member


@router.delete("/members/{member_user_id}")
async def remove_workspace_member(
    member_user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = (
        await db.execute(
            select(WorkspaceMember).where(
                and_(
                    WorkspaceMember.owner_user_id == current_user.id,
                    WorkspaceMember.member_user_id == member_user_id,
                    WorkspaceMember.status == "active",
                )
            )
        )
    ).scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace member not found")

    member.status = "inactive"
    await db.commit()
    return {"message": "Workspace member removed"}

