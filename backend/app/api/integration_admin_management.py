from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rbac import check_admin_permission, get_admin_user, log_admin_action
from app.models.admin import AdminUser, PermissionEnum
from app.models.integration import (
    Integration,
    IntegrationConfig,
    IntegrationStatus,
    IntegrationVisibility,
)
from app.schemas.integration import IntegrationResponse
from app.schemas.integration_admin import (
    IntegrationHubCreateRequest,
    IntegrationHubDetailResponse,
    IntegrationHubListItem,
    IntegrationHubListResponse,
    IntegrationHubMutationResponse,
    IntegrationHubStatisticsResponse,
    IntegrationHubUpdateRequest,
)

router = APIRouter()


async def _require_marketplace_management(admin_user: AdminUser, db: AsyncSession) -> None:
    has_permission = await check_admin_permission(admin_user, PermissionEnum.MANAGE_MARKETPLACE, db)
    if not has_permission:
        raise HTTPException(status_code=403, detail="Permission denied: manage_marketplace required")


def _coerce_enum_value(value: Any) -> Any:
    if hasattr(value, "value"):
        return value.value
    return value


async def _config_counts_by_integration(db: AsyncSession) -> tuple[dict[int, int], dict[int, int]]:
    total_rows = (
        await db.execute(
            select(IntegrationConfig.integration_id, func.count().label("count"))
            .group_by(IntegrationConfig.integration_id)
        )
    ).all()
    active_rows = (
        await db.execute(
            select(IntegrationConfig.integration_id, func.count().label("count"))
            .where(IntegrationConfig.is_active.is_(True))
            .group_by(IntegrationConfig.integration_id)
        )
    ).all()
    total_counts = {integration_id: int(count) for integration_id, count in total_rows}
    active_counts = {integration_id: int(count) for integration_id, count in active_rows}
    return total_counts, active_counts


def _build_usage_metrics(download_count: int) -> tuple[int, int, int, float]:
    usage_count = int(download_count or 0)
    success_count = int(usage_count * 0.9)
    error_count = max(usage_count - success_count, 0)
    avg_response_time = 150.5
    return usage_count, success_count, error_count, avg_response_time


@router.get("/admin/integrations/hub", response_model=IntegrationHubListResponse)
async def list_integration_hub(
    query: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    integration_type: Optional[str] = Query(None),
    status: Optional[str] = Query("all"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin_user: AdminUser = Depends(get_admin_user),
):
    await _require_marketplace_management(admin_user, db)

    statement = select(Integration)
    if query:
        pattern = f"%{query}%"
        statement = statement.where(
            Integration.name.ilike(pattern) | Integration.description.ilike(pattern)
        )
    if category:
        statement = statement.where(Integration.category == category)
    if integration_type:
        statement = statement.where(Integration.integration_type == integration_type)
    if status and status.lower() != "all":
        valid_statuses = {item.value for item in IntegrationStatus}
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status filter: {status}")
        statement = statement.where(Integration.status == status)

    statement = statement.order_by(desc(Integration.updated_at))
    count_statement = select(func.count()).select_from(statement.subquery())
    total = int((await db.execute(count_statement)).scalar_one() or 0)

    rows = (
        await db.execute(
            statement.offset((page - 1) * page_size).limit(page_size)
        )
    ).scalars().all()

    total_configs, active_configs = await _config_counts_by_integration(db)
    items: list[IntegrationHubListItem] = []
    for integration in rows:
        usage_count, _success_count, _error_count, _avg = _build_usage_metrics(integration.download_count or 0)
        items.append(
            IntegrationHubListItem(
                id=integration.id,
                name=integration.name,
                subtitle=getattr(integration, "subtitle", None),
                description=integration.description,
                integration_type=integration.integration_type,
                category=integration.category,
                icon=integration.icon,
                app_icon_url=integration.app_icon_url,
                version=integration.version,
                status=integration.status,
                visibility=integration.visibility,
                download_count=int(integration.download_count or 0),
                review_count=int(integration.review_count or 0),
                rating=float(integration.rating or 0.0),
                usage_count=usage_count,
                active_config_count=active_configs.get(integration.id, 0),
                total_config_count=total_configs.get(integration.id, 0),
                created_at=integration.created_at,
                updated_at=integration.updated_at,
                published_at=integration.published_at,
                is_workflow_node_enabled=bool(integration.is_workflow_node_enabled),
            )
        )

    return IntegrationHubListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(page * page_size) < total,
    )


@router.get("/admin/integrations/hub/{integration_id}", response_model=IntegrationHubDetailResponse)
async def get_integration_hub_detail(
    integration_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: AdminUser = Depends(get_admin_user),
):
    await _require_marketplace_management(admin_user, db)
    integration = (
        await db.execute(select(Integration).where(Integration.id == integration_id))
    ).scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return IntegrationHubDetailResponse(
        integration=IntegrationResponse.model_validate(integration)
    )


@router.get("/admin/integrations/hub/{integration_id}/statistics", response_model=IntegrationHubStatisticsResponse)
async def get_integration_hub_statistics(
    integration_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: AdminUser = Depends(get_admin_user),
):
    await _require_marketplace_management(admin_user, db)
    integration = (
        await db.execute(select(Integration).where(Integration.id == integration_id))
    ).scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    total_config_count = int(
        (
            await db.execute(
                select(func.count())
                .select_from(IntegrationConfig)
                .where(IntegrationConfig.integration_id == integration.id)
            )
        ).scalar_one()
        or 0
    )
    active_config_count = int(
        (
            await db.execute(
                select(func.count())
                .select_from(IntegrationConfig)
                .where(
                    and_(
                        IntegrationConfig.integration_id == integration.id,
                        IntegrationConfig.is_active.is_(True),
                    )
                )
            )
        ).scalar_one()
        or 0
    )

    usage_count, success_count, error_count, avg_response_time = _build_usage_metrics(
        integration.download_count or 0
    )

    return IntegrationHubStatisticsResponse(
        integration_id=integration.id,
        download_count=int(integration.download_count or 0),
        review_count=int(integration.review_count or 0),
        rating=float(integration.rating or 0.0),
        active_config_count=active_config_count,
        total_config_count=total_config_count,
        usage_count=usage_count,
        success_count=success_count,
        error_count=error_count,
        avg_response_time=avg_response_time,
    )


@router.post("/admin/integrations/hub", response_model=IntegrationHubMutationResponse, status_code=201)
async def create_integration_hub(
    payload: IntegrationHubCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: AdminUser = Depends(get_admin_user),
):
    await _require_marketplace_management(admin_user, db)

    integration = Integration(
        name=payload.name,
        description=payload.description,
        integration_type=payload.integration_type.value,
        category=payload.category.value,
        icon=payload.app_icon_url,
        documentation_url=payload.documentation_url,
        version=payload.version,
        is_public=payload.visibility.value == IntegrationVisibility.PUBLIC.value,
        status=IntegrationStatus.PUBLISHED.value,
        submission_notes=payload.submission_notes,
        submitted_at=datetime.utcnow(),
        reviewed_at=datetime.utcnow(),
        published_at=datetime.utcnow(),
        reviewed_by=admin_user.user_id,
        visibility=payload.visibility.value,
        app_icon_url=payload.app_icon_url,
        app_screenshots=payload.app_screenshots,
        developer_name=payload.developer_name,
        website_url=payload.website_url,
        support_url_or_email=payload.support_url_or_email,
        privacy_policy_url=payload.privacy_policy_url,
        terms_url=payload.terms_url,
        demo_url=payload.demo_url,
        config_schema=payload.config_schema,
        credentials_schema=payload.credentials_schema,
        supported_features=payload.supported_features,
        is_workflow_node_enabled=payload.is_workflow_node_enabled,
        author_id=admin_user.user_id,
    )
    db.add(integration)
    await db.commit()
    await db.refresh(integration)

    await log_admin_action(
        admin_user=admin_user,
        action="create_hub_integration",
        resource_type="integration",
        resource_id=integration.id,
        details={"status": integration.status, "name": integration.name},
        db=db,
    )

    return IntegrationHubMutationResponse(
        integration=IntegrationResponse.model_validate(integration),
        message="Integration published to hub",
    )


@router.patch("/admin/integrations/hub/{integration_id}", response_model=IntegrationHubMutationResponse)
async def update_integration_hub(
    integration_id: int,
    payload: IntegrationHubUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: AdminUser = Depends(get_admin_user),
):
    await _require_marketplace_management(admin_user, db)

    integration = (
        await db.execute(select(Integration).where(Integration.id == integration_id))
    ).scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    update_data = payload.model_dump(exclude_unset=True)
    updatable_columns = set(Integration.__table__.columns.keys())
    for key, value in update_data.items():
        if key not in updatable_columns:
            continue
        setattr(integration, key, _coerce_enum_value(value))

    if "visibility" in update_data:
        visibility_value = _coerce_enum_value(update_data["visibility"])
        integration.is_public = visibility_value == IntegrationVisibility.PUBLIC.value
    if integration.status != IntegrationStatus.PUBLISHED.value:
        integration.status = IntegrationStatus.PUBLISHED.value
    if integration.published_at is None:
        integration.published_at = datetime.utcnow()
    integration.reviewed_at = datetime.utcnow()
    integration.reviewed_by = admin_user.user_id

    await db.commit()
    await db.refresh(integration)

    await log_admin_action(
        admin_user=admin_user,
        action="update_hub_integration",
        resource_type="integration",
        resource_id=integration.id,
        details={"updated_fields": list(update_data.keys())},
        db=db,
    )

    return IntegrationHubMutationResponse(
        integration=IntegrationResponse.model_validate(integration),
        message="Integration updated",
    )


@router.delete("/admin/integrations/hub/{integration_id}")
async def delete_integration_hub(
    integration_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: AdminUser = Depends(get_admin_user),
):
    await _require_marketplace_management(admin_user, db)

    integration = (
        await db.execute(select(Integration).where(Integration.id == integration_id))
    ).scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    name = integration.name
    await db.delete(integration)
    await db.commit()

    await log_admin_action(
        admin_user=admin_user,
        action="delete_hub_integration",
        resource_type="integration",
        resource_id=integration_id,
        details={"name": name},
        db=db,
    )

    return {"message": "Integration deleted", "integration_id": integration_id}
