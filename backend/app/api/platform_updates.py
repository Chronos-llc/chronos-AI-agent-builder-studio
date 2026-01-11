from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.orm import joinedload
from typing import List, Optional
import logging
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.models.platform_updates import PlatformUpdate, UserUpdateView
from app.api.auth import get_current_user
from app.schemas.platform_updates import (
    PlatformUpdateCreate, PlatformUpdateUpdate, PlatformUpdateResponse, PlatformUpdateList,
    UserUpdateViewResponse, UserUpdateViewList, UpdateType, UpdatePriority, TargetAudience
)

router = APIRouter()
logger = logging.getLogger(__name__)


def is_admin(user: User) -> bool:
    """Check if user is admin"""
    return user.is_superuser


# Platform Updates Endpoints
@router.get("/updates", response_model=PlatformUpdateList)
async def get_platform_updates(
    update_type: Optional[UpdateType] = Query(None, description="Filter by update type"),
    priority: Optional[UpdatePriority] = Query(None, description="Filter by priority"),
    target_audience: Optional[TargetAudience] = Query(None, description="Filter by target audience"),
    is_published: Optional[bool] = Query(None, description="Filter by published status"),
    search_query: Optional[str] = Query(None, description="Text search in title and description"),
    sort_by: str = Query("published_at", description="Sort field: created_at, published_at, priority, view_count"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get platform updates with filtering and sorting"""
    
    # Base query
    query = select(PlatformUpdate)
    
    # Apply filters
    if update_type:
        query = query.where(PlatformUpdate.update_type == update_type)
    
    if priority:
        query = query.where(PlatformUpdate.priority == priority)
    
    if target_audience:
        query = query.where(PlatformUpdate.target_audience == target_audience)
    else:
        # Default: only show updates for user's audience type
        audience = TargetAudience.ADMIN if current_user.is_superuser else TargetAudience.USER
        query = query.where(
            or_(
                PlatformUpdate.target_audience == TargetAudience.ALL,
                PlatformUpdate.target_audience == audience
            )
        )
    
    if is_published is not None:
        query = query.where(PlatformUpdate.is_published == is_published)
    else:
        # Default: only show published updates for non-admins
        if not current_user.is_superuser:
            query = query.where(PlatformUpdate.is_published == True)
    
    if search_query:
        query = query.where(
            or_(
                PlatformUpdate.title.ilike(f"%{search_query}%"),
                PlatformUpdate.description.ilike(f"%{search_query}%")
            )
        )
    
    # Sorting
    sort_field = PlatformUpdate.published_at if hasattr(PlatformUpdate, 'published_at') else PlatformUpdate.created_at
    if sort_by == "created_at":
        sort_field = PlatformUpdate.created_at
    elif sort_by == "priority":
        sort_field = PlatformUpdate.priority
    elif sort_by == "view_count":
        sort_field = PlatformUpdate.view_count
    
    if sort_order == "asc":
        query = query.order_by(asc(sort_field))
    else:
        query = query.order_by(desc(sort_field))
    
    # Pagination
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar_one()
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    updates = result.scalars().all()
    
    return {
        "items": [PlatformUpdateResponse.from_orm(update) for update in updates],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/updates/{update_id}", response_model=PlatformUpdateResponse)
async def get_platform_update(
    update_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific platform update"""
    
    result = await db.execute(select(PlatformUpdate).where(PlatformUpdate.id == update_id))
    update = result.scalar_one_or_none()
    
    if not update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update not found"
        )
    
    # Check visibility
    if not current_user.is_superuser:
        if update.target_audience != TargetAudience.ALL and update.target_audience != TargetAudience.USER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this update"
            )
        if not update.is_published:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Update not found or not published"
            )
    
    # Track view if user hasn't viewed it yet
    if current_user.id:
        view_result = await db.execute(select(UserUpdateView).where(
            and_(
                UserUpdateView.update_id == update_id,
                UserUpdateView.user_id == current_user.id
            )
        ))
        existing_view = view_result.scalar_one_or_none()
        
        if not existing_view:
            # Increment view count
            update.view_count += 1
            
            # Create view record
            view = UserUpdateView(
                update_id=update_id,
                user_id=current_user.id
            )
            db.add(view)
            await db.commit()
            await db.refresh(update)
    
    return PlatformUpdateResponse.from_orm(update)


@router.post("/updates", response_model=PlatformUpdateResponse, status_code=status.HTTP_201_CREATED)
async def create_platform_update(
    update_data: PlatformUpdateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new platform update (admin only)"""
    
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Create update
    update = PlatformUpdate(
        title=update_data.title,
        description=update_data.description,
        update_type=update_data.update_type,
        priority=update_data.priority,
        media_type=update_data.media_type,
        media_urls=update_data.media_urls,
        thumbnail_url=update_data.thumbnail_url,
        target_audience=update_data.target_audience,
        is_published=update_data.is_published if hasattr(update_data, 'is_published') else False,
        published_at=datetime.utcnow() if getattr(update_data, 'is_published', False) else None
    )
    
    db.add(update)
    await db.commit()
    await db.refresh(update)
    
    return PlatformUpdateResponse.from_orm(update)


@router.put("/updates/{update_id}", response_model=PlatformUpdateResponse)
async def update_platform_update(
    update_id: int,
    update_data: PlatformUpdateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update platform update (admin only)"""
    
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    result = await db.execute(select(PlatformUpdate).where(PlatformUpdate.id == update_id))
    update = result.scalar_one_or_none()
    
    if not update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update not found"
        )
    
    # Update fields
    update_data_dict = update_data.dict(exclude_unset=True)
    for field, value in update_data_dict.items():
        setattr(update, field, value)
    
    # Handle publish/unpublish
    if 'is_published' in update_data_dict:
        if update_data.is_published:
            update.published_at = datetime.utcnow()
        else:
            update.published_at = None
    
    await db.commit()
    await db.refresh(update)
    
    return PlatformUpdateResponse.from_orm(update)


@router.delete("/updates/{update_id}")
async def delete_platform_update(
    update_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete platform update (admin only)"""
    
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    result = await db.execute(select(PlatformUpdate).where(PlatformUpdate.id == update_id))
    update = result.scalar_one_or_none()
    
    if not update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update not found"
        )
    
    await db.delete(update)
    await db.commit()
    
    return {"message": "Update deleted successfully"}


@router.get("/updates/{update_id}/views", response_model=UserUpdateViewList)
async def get_update_views(
    update_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get users who have viewed an update (admin only)"""
    
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    result = await db.execute(select(UserUpdateView).where(UserUpdateView.update_id == update_id))
    views = result.scalars().all()
    
    return {
        "items": [UserUpdateViewResponse.from_orm(view) for view in views],
        "total": len(views),
        "page": 1,
        "page_size": len(views)
    }


@router.get("/my-updates/unviewed", response_model=PlatformUpdateList)
async def get_unviewed_updates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get unviewed updates for current user"""
    
    # Get updates that user hasn't viewed
    viewed_subquery = select(UserUpdateView.update_id).where(UserUpdateView.user_id == current_user.id)
    
    query = select(PlatformUpdate).where(
        and_(
            PlatformUpdate.is_published == True,
            or_(
                PlatformUpdate.target_audience == TargetAudience.ALL,
                PlatformUpdate.target_audience == TargetAudience.USER
            ),
            PlatformUpdate.id.notin_(viewed_subquery)
        )
    )
    
    result = await db.execute(query)
    updates = result.scalars().all()
    
    return {
        "items": [PlatformUpdateResponse.from_orm(update) for update in updates],
        "total": len(updates),
        "page": 1,
        "page_size": len(updates)
    }


@router.post("/updates/{update_id}/mark-viewed")
async def mark_update_viewed(
    update_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark an update as viewed by current user"""
    
    # Check if update exists
    result = await db.execute(select(PlatformUpdate).where(PlatformUpdate.id == update_id))
    update = result.scalar_one_or_none()
    
    if not update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Update not found"
        )
    
    # Check if already viewed
    view_result = await db.execute(select(UserUpdateView).where(
        and_(
            UserUpdateView.update_id == update_id,
            UserUpdateView.user_id == current_user.id
        )
    ))
    existing_view = view_result.scalar_one_or_none()
    
    if existing_view:
        return {"message": "Update already marked as viewed"}
    
    # Create view record
    view = UserUpdateView(
        update_id=update_id,
        user_id=current_user.id
    )
    
    # Increment view count
    update.view_count += 1
    
    db.add(view)
    await db.commit()
    
    return {"message": "Update marked as viewed"}