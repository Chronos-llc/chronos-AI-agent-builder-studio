from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rbac import check_admin_permission, get_admin_user, log_admin_action
from app.models.admin import AdminUser, PermissionEnum
from app.models.integration import Integration, IntegrationStatus, IntegrationVisibility
from app.models.integration_submission import IntegrationSubmissionEvent
from app.schemas.integration import (
    IntegrationModerationAction,
    IntegrationModerationRequest,
    IntegrationResponse,
    IntegrationStatus as IntegrationStatusSchema,
    IntegrationSubmissionEventResponse,
)

router = APIRouter()


async def _require_marketplace_moderation(admin_user: AdminUser, db: AsyncSession) -> None:
    has_permission = await check_admin_permission(
        admin_user, PermissionEnum.MANAGE_MARKETPLACE, db
    )
    if not has_permission:
        raise HTTPException(status_code=403, detail="Permission denied: manage_marketplace required")


async def _append_submission_event(
    db: AsyncSession,
    integration_id: int,
    action: str,
    actor_user_id: int | None,
    payload: dict,
) -> None:
    event = IntegrationSubmissionEvent(
        integration_id=integration_id,
        action=action,
        actor_user_id=actor_user_id,
        payload=payload,
    )
    db.add(event)
    await db.commit()


@router.get("/admin/integrations/submissions", response_model=List[IntegrationResponse])
async def list_submissions(
    status: Optional[IntegrationStatusSchema] = Query(None),
    integration_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    admin_user: AdminUser = Depends(get_admin_user),
):
    await _require_marketplace_moderation(admin_user, db)

    query = select(Integration).where(Integration.status != IntegrationStatus.PUBLISHED.value)
    if status:
        query = query.where(Integration.status == status.value)
    if integration_type:
        query = query.where(Integration.integration_type == integration_type)
    query = query.order_by(desc(Integration.updated_at))
    return (await db.execute(query)).scalars().all()


@router.get("/admin/integrations/submissions/{integration_id}")
async def get_submission_detail(
    integration_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: AdminUser = Depends(get_admin_user),
):
    await _require_marketplace_moderation(admin_user, db)

    integration = (await db.execute(select(Integration).where(Integration.id == integration_id))).scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    events = (
        await db.execute(
            select(IntegrationSubmissionEvent)
            .where(IntegrationSubmissionEvent.integration_id == integration_id)
            .order_by(desc(IntegrationSubmissionEvent.created_at))
        )
    ).scalars().all()
    return {
        "submission": IntegrationResponse.from_orm(integration),
        "events": [IntegrationSubmissionEventResponse.from_orm(item) for item in events],
    }


@router.post("/admin/integrations/submissions/{integration_id}/review", response_model=IntegrationResponse)
async def review_submission(
    integration_id: int,
    payload: IntegrationModerationRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: AdminUser = Depends(get_admin_user),
):
    await _require_marketplace_moderation(admin_user, db)

    integration = (await db.execute(select(Integration).where(Integration.id == integration_id))).scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    integration.reviewed_by = admin_user.user_id
    integration.reviewed_at = datetime.utcnow()
    integration.moderation_notes = payload.moderation_notes
    if payload.visibility is not None:
        integration.visibility = payload.visibility.value
        integration.is_public = integration.visibility == IntegrationVisibility.PUBLIC.value
    if payload.is_workflow_node_enabled is not None:
        integration.is_workflow_node_enabled = payload.is_workflow_node_enabled

    if payload.action == IntegrationModerationAction.APPROVE:
        integration.status = IntegrationStatus.APPROVED.value
    elif payload.action == IntegrationModerationAction.REJECT:
        integration.status = IntegrationStatus.REJECTED.value
    else:
        integration.status = IntegrationStatus.UNDER_REVIEW.value

    await db.commit()
    await db.refresh(integration)
    await _append_submission_event(
        db,
        integration_id=integration.id,
        action=payload.action.value,
        actor_user_id=admin_user.user_id,
        payload={
            "status": integration.status,
            "visibility": integration.visibility,
            "is_workflow_node_enabled": integration.is_workflow_node_enabled,
        },
    )

    await log_admin_action(
        admin_user=admin_user,
        action="review_integration_submission",
        resource_type="integration_submission",
        resource_id=integration.id,
        details={"action": payload.action.value},
        db=db,
    )
    await db.refresh(integration)
    return integration


@router.post("/admin/integrations/submissions/{integration_id}/publish", response_model=IntegrationResponse)
async def publish_submission(
    integration_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: AdminUser = Depends(get_admin_user),
):
    await _require_marketplace_moderation(admin_user, db)

    integration = (await db.execute(select(Integration).where(Integration.id == integration_id))).scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    if integration.status != IntegrationStatus.APPROVED.value:
        raise HTTPException(status_code=400, detail="Only approved submissions can be published")

    integration.status = IntegrationStatus.PUBLISHED.value
    integration.published_at = datetime.utcnow()
    integration.is_public = integration.visibility == IntegrationVisibility.PUBLIC.value
    await db.commit()
    await db.refresh(integration)
    await _append_submission_event(
        db,
        integration_id=integration.id,
        action="published",
        actor_user_id=admin_user.user_id,
        payload={"status": integration.status, "published_at": integration.published_at.isoformat()},
    )

    await log_admin_action(
        admin_user=admin_user,
        action="publish_integration_submission",
        resource_type="integration_submission",
        resource_id=integration.id,
        details={"status": integration.status},
        db=db,
    )
    await db.refresh(integration)
    return integration
