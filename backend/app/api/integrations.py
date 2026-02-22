from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, HttpUrl
from sqlalchemy import and_, case, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.integration import (
    Integration as IntegrationModel,
    IntegrationConfig as IntegrationConfigModel,
    IntegrationReview as IntegrationReviewModel,
    IntegrationStatus,
    IntegrationVisibility,
)
from app.models.integration_submission import IntegrationSubmissionEvent
from app.models.usage import UserPlan, can_publish_integration, has_team_visibility_access
from app.models.user import User as UserModel
from app.schemas.integration import (
    IntegrationConfigCreate,
    IntegrationConfigResponse,
    IntegrationConfigUpdate,
    IntegrationCategory,
    IntegrationCreate,
    IntegrationType,
    IntegrationModerationAction,
    IntegrationResponse,
    IntegrationReviewCreate,
    IntegrationReviewResponse,
    IntegrationSubmissionCreate,
    IntegrationSubmissionEventResponse,
    IntegrationSubmissionUpdate,
    IntegrationUpdate,
    InstalledIntegrationResponse,
    InstalledIntegrationsResponse,
    IntegrationUsageStats,
    IntegrationMarketplaceSearch,
)

router = APIRouter()


class IntegrationImageUploadRequest(BaseModel):
    image_url: HttpUrl


async def _get_or_create_user_plan(db: AsyncSession, user_id: int) -> UserPlan:
    plan = (await db.execute(select(UserPlan).where(UserPlan.user_id == user_id))).scalar_one_or_none()
    if plan:
        return plan
    plan = UserPlan(user_id=user_id)
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan


def _is_submission_type_allowed(integration_type: str) -> bool:
    return integration_type in {"mcp_server", "api"}


def _can_view_integration(integration: IntegrationModel, current_user: UserModel, user_plan: UserPlan | None) -> bool:
    if integration.author_id == current_user.id or current_user.is_superuser:
        return True
    if integration.status != IntegrationStatus.PUBLISHED.value:
        return False
    visibility = integration.visibility or IntegrationVisibility.PRIVATE.value
    if visibility == IntegrationVisibility.PUBLIC.value:
        return True
    if visibility == IntegrationVisibility.TEAM.value:
        return has_team_visibility_access(user_plan.plan_type if user_plan else None)
    return False


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


@router.post("/submissions", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_integration_submission(
    submission: IntegrationSubmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    user_plan = await _get_or_create_user_plan(db, current_user.id)
    if not can_publish_integration(user_plan.plan_type):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Integration publishing requires Team/Developer plan or higher",
                "current_plan": user_plan.plan_type.value,
            },
        )

    if not _is_submission_type_allowed(submission.integration_type.value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only MCP Server and API integration types can be submitted",
        )

    db_integration = IntegrationModel(
        **submission.dict(),
        status=IntegrationStatus.DRAFT.value,
        author_id=current_user.id,
        is_public=submission.visibility == IntegrationVisibility.PUBLIC,
    )
    db.add(db_integration)
    await db.commit()
    await db.refresh(db_integration)

    await _append_submission_event(
        db,
        integration_id=db_integration.id,
        action="draft_created",
        actor_user_id=current_user.id,
        payload={"status": db_integration.status},
    )
    await db.refresh(db_integration)
    return db_integration


@router.put("/submissions/{integration_id}", response_model=IntegrationResponse)
async def update_integration_submission(
    integration_id: int,
    submission: IntegrationSubmissionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    result = await db.execute(select(IntegrationModel).where(IntegrationModel.id == integration_id))
    integration = result.scalars().first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    if integration.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to update this submission")
    if integration.status == IntegrationStatus.PUBLISHED.value and not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Published integrations can only be edited by admins")

    update_data = submission.dict(exclude_unset=True)
    if "integration_type" in update_data and update_data["integration_type"] is not None:
        if not _is_submission_type_allowed(update_data["integration_type"].value):
            raise HTTPException(status_code=400, detail="Only MCP Server and API integration types can be submitted")

    for key, value in update_data.items():
        setattr(integration, key, value)

    integration.is_public = integration.visibility == IntegrationVisibility.PUBLIC.value
    await db.commit()
    await db.refresh(integration)
    await _append_submission_event(
        db,
        integration_id=integration.id,
        action="draft_updated",
        actor_user_id=current_user.id,
        payload={"updated_fields": list(update_data.keys())},
    )
    await db.refresh(integration)
    return integration


@router.post("/submissions/{integration_id}/submit", response_model=IntegrationResponse)
async def submit_integration_submission(
    integration_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    user_plan = await _get_or_create_user_plan(db, current_user.id)
    if not can_publish_integration(user_plan.plan_type):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Integration publishing requires Team/Developer plan or higher",
                "current_plan": user_plan.plan_type.value,
            },
        )

    integration = (
        await db.execute(select(IntegrationModel).where(IntegrationModel.id == integration_id))
    ).scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    if integration.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to submit this integration")

    integration.status = IntegrationStatus.SUBMITTED.value
    integration.submitted_at = datetime.utcnow()
    await db.commit()
    await db.refresh(integration)
    await _append_submission_event(
        db,
        integration_id=integration.id,
        action="submitted",
        actor_user_id=current_user.id,
        payload={"status": integration.status, "submitted_at": integration.submitted_at.isoformat()},
    )
    await db.refresh(integration)
    return integration


@router.get("/submissions/mine", response_model=List[IntegrationResponse])
async def list_my_submissions(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    result = await db.execute(
        select(IntegrationModel)
        .where(IntegrationModel.author_id == current_user.id)
        .order_by(desc(IntegrationModel.updated_at))
    )
    return result.scalars().all()


@router.get("/submissions/{integration_id}/events", response_model=List[IntegrationSubmissionEventResponse])
async def get_submission_events(
    integration_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    integration = (
        await db.execute(select(IntegrationModel).where(IntegrationModel.id == integration_id))
    ).scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    if integration.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to view submission events")

    events = (
        await db.execute(
            select(IntegrationSubmissionEvent)
            .where(IntegrationSubmissionEvent.integration_id == integration_id)
            .order_by(IntegrationSubmissionEvent.created_at.desc())
        )
    ).scalars().all()
    return events


@router.post("/submissions/{integration_id}/upload-image")
async def upload_submission_image(
    integration_id: int,
    payload: IntegrationImageUploadRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    integration = (
        await db.execute(select(IntegrationModel).where(IntegrationModel.id == integration_id))
    ).scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    if integration.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to upload image for this submission")

    integration.app_icon_url = str(payload.image_url)
    await db.commit()
    await db.refresh(integration)
    await _append_submission_event(
        db,
        integration_id=integration.id,
        action="image_uploaded",
        actor_user_id=current_user.id,
        payload={"image_url": integration.app_icon_url},
    )
    return {"image_url": integration.app_icon_url}


@router.get("/mine/installed", response_model=InstalledIntegrationsResponse)
async def list_my_installed_integrations(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    rows = (
        await db.execute(
            select(
                IntegrationModel.id.label("integration_id"),
                IntegrationModel.name,
                IntegrationModel.description,
                IntegrationModel.integration_type,
                IntegrationModel.category,
                IntegrationModel.icon,
                IntegrationModel.app_icon_url,
                IntegrationModel.version,
                IntegrationModel.status,
                IntegrationModel.visibility,
                IntegrationModel.download_count,
                IntegrationModel.rating,
                IntegrationModel.review_count,
                func.count(IntegrationConfigModel.id).label("installed_count"),
                func.sum(case((IntegrationConfigModel.is_active.is_(True), 1), else_=0)).label("active_installed_count"),
                func.max(IntegrationConfigModel.updated_at).label("last_installed_at"),
            )
            .join(IntegrationConfigModel, IntegrationConfigModel.integration_id == IntegrationModel.id)
            .where(IntegrationConfigModel.user_id == current_user.id)
            .group_by(IntegrationModel.id)
            .order_by(desc(func.max(IntegrationConfigModel.updated_at)))
        )
    ).all()

    items = [
        InstalledIntegrationResponse(
            integration_id=int(row.integration_id),
            name=row.name,
            description=row.description,
            integration_type=row.integration_type,
            category=row.category,
            icon=row.icon,
            app_icon_url=row.app_icon_url,
            version=row.version,
            status=row.status,
            visibility=row.visibility,
            download_count=int(row.download_count or 0),
            rating=float(row.rating or 0.0),
            review_count=int(row.review_count or 0),
            installed_count=int(row.installed_count or 0),
            active_installed_count=int(row.active_installed_count or 0),
            last_installed_at=row.last_installed_at,
        )
        for row in rows
    ]
    return InstalledIntegrationsResponse(items=items, total=len(items))


@router.get("/hub", response_model=List[IntegrationResponse])
async def list_hub_integrations(
    query: Optional[str] = Query(None),
    category: Optional[IntegrationCategory] = Query(None),
    integration_type: Optional[IntegrationType] = Query(None),
    min_rating: Optional[float] = Query(None),
    sort_by: str = Query("popularity"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    search_params = IntegrationMarketplaceSearch(
        query=query,
        categories=[category] if category else None,
        types=[integration_type] if integration_type else None,
        min_rating=min_rating,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )
    return await search_integrations(search_params, db, current_user)


@router.post("/", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_integration(
    integration: IntegrationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    db_integration = IntegrationModel(
        **integration.dict(),
        author_id=current_user.id,
        status=IntegrationStatus.PUBLISHED.value if current_user.is_superuser else IntegrationStatus.DRAFT.value,
        published_at=datetime.utcnow() if current_user.is_superuser else None,
        is_public=integration.visibility == IntegrationVisibility.PUBLIC,
    )
    db.add(db_integration)
    await db.commit()
    await db.refresh(db_integration)
    return db_integration


@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    integration_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    result = await db.execute(select(IntegrationModel).where(IntegrationModel.id == integration_id))
    integration = result.scalars().first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    plan = await _get_or_create_user_plan(db, current_user.id)
    if not _can_view_integration(integration, current_user, plan):
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration


@router.put("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: int,
    integration: IntegrationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    result = await db.execute(select(IntegrationModel).where(IntegrationModel.id == integration_id))
    db_integration = result.scalars().first()
    if not db_integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    if db_integration.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to update this integration")

    for key, value in integration.dict(exclude_unset=True).items():
        setattr(db_integration, key, value)

    if integration.visibility is not None:
        db_integration.is_public = integration.visibility == IntegrationVisibility.PUBLIC
    await db.commit()
    await db.refresh(db_integration)
    return db_integration


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    integration_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    result = await db.execute(select(IntegrationModel).where(IntegrationModel.id == integration_id))
    db_integration = result.scalars().first()
    if not db_integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    if db_integration.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized to delete this integration")

    await db.delete(db_integration)
    await db.commit()


@router.post("/search/", response_model=List[IntegrationResponse])
async def search_integrations(
    search_params: IntegrationMarketplaceSearch,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    query = select(IntegrationModel)

    if search_params.query:
        query = query.where(
            IntegrationModel.name.ilike(f"%{search_params.query}%")
            | IntegrationModel.description.ilike(f"%{search_params.query}%")
        )
    if search_params.categories:
        query = query.where(IntegrationModel.category.in_(search_params.categories))
    if search_params.types:
        query = query.where(IntegrationModel.integration_type.in_(search_params.types))
    if search_params.min_rating:
        query = query.where(IntegrationModel.rating >= search_params.min_rating)

    # Only published integrations are discoverable in the global hub.
    query = query.where(IntegrationModel.status == IntegrationStatus.PUBLISHED.value)

    user_plan = await _get_or_create_user_plan(db, current_user.id)
    if not has_team_visibility_access(user_plan.plan_type):
        query = query.where(IntegrationModel.visibility == IntegrationVisibility.PUBLIC.value)
    else:
        query = query.where(
            IntegrationModel.visibility.in_(
                [IntegrationVisibility.PUBLIC.value, IntegrationVisibility.TEAM.value]
            )
        )

    if search_params.sort_by == "rating":
        query = query.order_by(desc(IntegrationModel.rating))
    elif search_params.sort_by == "newest":
        query = query.order_by(desc(IntegrationModel.created_at))
    else:
        query = query.order_by(desc(IntegrationModel.download_count))

    offset = (search_params.page - 1) * search_params.page_size
    query = query.offset(offset).limit(search_params.page_size)

    integrations = (await db.execute(query)).scalars().all()
    return integrations


@router.post("/{integration_id}/config/", response_model=IntegrationConfigResponse)
async def create_integration_config(
    integration_id: int,
    config: IntegrationConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    integration = (
        await db.execute(select(IntegrationModel).where(IntegrationModel.id == integration_id))
    ).scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    if integration.status != IntegrationStatus.PUBLISHED.value:
        raise HTTPException(status_code=400, detail="Only published integrations can be installed")

    user_plan = await _get_or_create_user_plan(db, current_user.id)
    if not _can_view_integration(integration, current_user, user_plan):
        raise HTTPException(status_code=404, detail="Integration not found")

    db_config = IntegrationConfigModel(
        integration_id=integration_id,
        user_id=current_user.id,
        **config.dict()
    )
    db.add(db_config)
    integration.download_count += 1
    await db.commit()
    await db.refresh(db_config)
    return db_config


@router.get("/config/{config_id}", response_model=IntegrationConfigResponse)
async def get_integration_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    config = (
        await db.execute(
            select(IntegrationConfigModel).where(
                IntegrationConfigModel.id == config_id,
                IntegrationConfigModel.user_id == current_user.id,
            )
        )
    ).scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config


@router.put("/config/{config_id}", response_model=IntegrationConfigResponse)
async def update_integration_config(
    config_id: int,
    config: IntegrationConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    db_config = (
        await db.execute(
            select(IntegrationConfigModel).where(
                IntegrationConfigModel.id == config_id,
                IntegrationConfigModel.user_id == current_user.id,
            )
        )
    ).scalar_one_or_none()
    if not db_config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    for key, value in config.dict(exclude_unset=True).items():
        setattr(db_config, key, value)

    await db.commit()
    await db.refresh(db_config)
    return db_config


@router.post("/{integration_id}/reviews/", response_model=IntegrationReviewResponse)
async def create_integration_review(
    integration_id: int,
    review: IntegrationReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    integration = (
        await db.execute(select(IntegrationModel).where(IntegrationModel.id == integration_id))
    ).scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    if integration.status != IntegrationStatus.PUBLISHED.value:
        raise HTTPException(status_code=400, detail="Only published integrations can be reviewed")

    existing_review = (
        await db.execute(
            select(IntegrationReviewModel).where(
                IntegrationReviewModel.integration_id == integration_id,
                IntegrationReviewModel.user_id == current_user.id,
            )
        )
    ).scalar_one_or_none()
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this integration")

    db_review = IntegrationReviewModel(
        integration_id=integration_id,
        user_id=current_user.id,
        **review.dict()
    )
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)

    avg_rating = (
        await db.execute(
            select(func.avg(IntegrationReviewModel.rating)).where(
                IntegrationReviewModel.integration_id == integration_id
            )
        )
    ).scalar() or 0
    review_count = (
        await db.execute(
            select(func.count()).where(IntegrationReviewModel.integration_id == integration_id)
        )
    ).scalar() or 0
    integration.rating = float(avg_rating)
    integration.review_count = int(review_count)
    await db.commit()
    return db_review


@router.get("/{integration_id}/stats/", response_model=IntegrationUsageStats)
async def get_integration_stats(
    integration_id: int,
    db: AsyncSession = Depends(get_db),
):
    integration = (
        await db.execute(select(IntegrationModel).where(IntegrationModel.id == integration_id))
    ).scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    usage_count = integration.download_count
    success_count = int(usage_count * 0.9)
    error_count = usage_count - success_count
    return IntegrationUsageStats(
        integration_id=integration_id,
        usage_count=usage_count,
        success_count=success_count,
        error_count=error_count,
        avg_response_time=150.5,
    )
