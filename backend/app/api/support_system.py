from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.orm import joinedload
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.models.admin import AdminUser
from app.models.support_system import SupportMessage, SupportMessageReply
from app.api.auth import get_current_user
from app.schemas.support_system import (
    SupportMessageCreate, SupportMessageUpdate, SupportMessageResponse, SupportMessageList,
    SupportMessageReplyCreate, SupportMessageReplyResponse, SupportMessageReplyList,
    SupportSearchParams, SupportStatus, SupportPriority, SupportCategory
)

router = APIRouter()
logger = logging.getLogger(__name__)


async def is_admin(user: User, db: AsyncSession) -> bool:
    """Check whether user has effective admin access."""
    if user.is_superuser:
        return True
    result = await db.execute(
        select(AdminUser).where(
            and_(
                AdminUser.user_id == user.id,
                AdminUser.is_active == True,
            )
        )
    )
    return result.scalar_one_or_none() is not None


async def is_owner_or_admin(user: User, message: SupportMessage, db: AsyncSession) -> bool:
    """Check if user is owner of message or has admin access."""
    if user.id == message.user_id:
        return True
    return await is_admin(user, db)


# Support Messages Endpoints
@router.get("/messages", response_model=SupportMessageList)
async def get_support_messages(
    status: Optional[SupportStatus] = Query(None, description="Filter by status"),
    priority: Optional[SupportPriority] = Query(None, description="Filter by priority"),
    category: Optional[SupportCategory] = Query(None, description="Filter by category"),
    assigned_to: Optional[int] = Query(None, description="Filter by assigned admin"),
    search_query: Optional[str] = Query(None, description="Text search in subject and message"),
    sort_by: str = Query("created_at", description="Sort field: created_at, updated_at, priority, status"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get support messages with filtering and sorting"""
    admin_access = await is_admin(current_user, db)

    # Base query
    query = select(SupportMessage).options(
        joinedload(SupportMessage.user),
        joinedload(SupportMessage.assigned_admin)
    )
    
    # Apply filters based on user role
    if not admin_access:
        # Non-admins can only see their own messages
        query = query.where(SupportMessage.user_id == current_user.id)
    else:
        # Admins can filter by assigned_to
        if assigned_to:
            query = query.where(SupportMessage.assigned_to == assigned_to)
    
    if status:
        query = query.where(SupportMessage.status == status)
    
    if priority:
        query = query.where(SupportMessage.priority == priority)
    
    if category:
        query = query.where(SupportMessage.category == category)
    
    if search_query:
        query = query.where(
            or_(
                SupportMessage.subject.ilike(f"%{search_query}%"),
                SupportMessage.message.ilike(f"%{search_query}%")
            )
        )
    
    # Sorting
    sort_field = SupportMessage.created_at
    if sort_by == "updated_at":
        sort_field = SupportMessage.updated_at
    elif sort_by == "priority":
        sort_field = SupportMessage.priority
    elif sort_by == "status":
        sort_field = SupportMessage.status
    
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
    messages = result.scalars().all()
    
    return {
        "items": [SupportMessageResponse.from_orm(message) for message in messages],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/messages/{message_id}", response_model=SupportMessageResponse)
async def get_support_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific support message"""
    
    result = await db.execute(select(SupportMessage).where(SupportMessage.id == message_id).options(
        joinedload(SupportMessage.user),
        joinedload(SupportMessage.assigned_admin),
        joinedload(SupportMessage.replies).joinedload(SupportMessageReply.user)
    ))
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Check ownership or admin
    if not await is_owner_or_admin(current_user, message, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this message"
        )
    
    return SupportMessageResponse.from_orm(message)


@router.post("/messages", response_model=SupportMessageResponse, status_code=status.HTTP_201_CREATED)
async def create_support_message(
    message_data: SupportMessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new support message"""
    
    # Create message
    message = SupportMessage(
        user_id=current_user.id,
        subject=message_data.subject,
        message=message_data.message,
        priority=message_data.priority,
        category=message_data.category,
        status=SupportStatus.OPEN
    )
    
    db.add(message)
    await db.commit()
    await db.refresh(message)
    
    return SupportMessageResponse.from_orm(message)


@router.put("/messages/{message_id}", response_model=SupportMessageResponse)
async def update_support_message(
    message_id: int,
    message_update: SupportMessageUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update support message"""
    
    result = await db.execute(select(SupportMessage).where(SupportMessage.id == message_id))
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Check ownership or admin
    admin_access = await is_admin(current_user, db)
    if not await is_owner_or_admin(current_user, message, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this message"
        )
    
    # Update fields
    update_data = message_update.dict(exclude_unset=True)
    
    # Only admins can change status and assignment
    if not admin_access:
        if "status" in update_data:
            del update_data["status"]
        if "assigned_to" in update_data:
            del update_data["assigned_to"]
    
    # Apply updates
    for field, value in update_data.items():
        setattr(message, field, value)
    
    # Handle status changes
    if "status" in update_data:
        if message_update.status == SupportStatus.RESOLVED:
            message.resolved_at = datetime.utcnow()
        elif message_update.status != SupportStatus.RESOLVED:
            message.resolved_at = None
    
    await db.commit()
    await db.refresh(message)
    
    return SupportMessageResponse.from_orm(message)


@router.post("/messages/{message_id}/replies", response_model=SupportMessageReplyResponse, status_code=status.HTTP_201_CREATED)
async def create_support_reply(
    message_id: int,
    reply_data: SupportMessageReplyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add reply to support message"""
    
    # Get message
    result = await db.execute(select(SupportMessage).where(SupportMessage.id == message_id))
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Check if user can reply
    admin_access = await is_admin(current_user, db)
    if not await is_owner_or_admin(current_user, message, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to reply to this message"
        )
    
    # Create reply
    reply = SupportMessageReply(
        message_id=message_id,
        user_id=current_user.id,
        is_admin=admin_access,
        reply_text=reply_data.reply_text
    )
    
    # Update message status if it was closed
    if message.status == SupportStatus.CLOSED:
        message.status = SupportStatus.IN_PROGRESS
        message.resolved_at = None
    
    db.add(reply)
    await db.commit()
    await db.refresh(reply)
    
    return SupportMessageReplyResponse.from_orm(reply)


@router.get("/messages/{message_id}/replies", response_model=SupportMessageReplyList)
async def get_support_replies(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get replies for support message"""
    
    # Get message
    result = await db.execute(select(SupportMessage).where(SupportMessage.id == message_id))
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Check ownership or admin
    if not await is_owner_or_admin(current_user, message, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view replies for this message"
        )
    
    # Get replies
    result = await db.execute(select(SupportMessageReply).where(SupportMessageReply.message_id == message_id).options(
        joinedload(SupportMessageReply.user)
    ))
    replies = result.scalars().all()
    
    return {
        "items": [SupportMessageReplyResponse.from_orm(reply) for reply in replies],
        "total": len(replies),
        "page": 1,
        "page_size": len(replies)
    }


@router.post("/messages/search", response_model=SupportMessageList)
async def search_support_messages(
    search_params: SupportSearchParams,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Advanced search for support messages"""
    
    query = select(SupportMessage).options(
        joinedload(SupportMessage.user),
        joinedload(SupportMessage.assigned_admin)
    )
    
    # Apply filters based on user role
    admin_access = await is_admin(current_user, db)
    if not admin_access:
        query = query.where(SupportMessage.user_id == current_user.id)
    
    # Apply search filters
    if search_params.query:
        query = query.where(
            or_(
                SupportMessage.subject.ilike(f"%{search_params.query}%"),
                SupportMessage.message.ilike(f"%{search_params.query}%")
            )
        )
    
    if search_params.status:
        query = query.where(SupportMessage.status == search_params.status)
    
    if search_params.priority:
        query = query.where(SupportMessage.priority == search_params.priority)
    
    if search_params.category:
        query = query.where(SupportMessage.category == search_params.category)
    
    if search_params.assigned_to:
        query = query.where(SupportMessage.assigned_to == search_params.assigned_to)
    
    # Sorting
    sort_field = SupportMessage.created_at
    if search_params.sort_by == "updated_at":
        sort_field = SupportMessage.updated_at
    elif search_params.sort_by == "priority":
        sort_field = SupportMessage.priority
    elif search_params.sort_by == "status":
        sort_field = SupportMessage.status
    
    if search_params.sort_order == "asc":
        query = query.order_by(asc(sort_field))
    else:
        query = query.order_by(desc(sort_field))
    
    # Pagination
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar_one()
    
    query = query.offset((search_params.page - 1) * search_params.page_size).limit(search_params.page_size)
    
    result = await db.execute(query)
    messages = result.scalars().all()
    
    return {
        "items": [SupportMessageResponse.from_orm(message) for message in messages],
        "total": total,
        "page": search_params.page,
        "page_size": search_params.page_size
    }


@router.get("/my-messages/stats", response_model=Dict[str, int])
async def get_my_support_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get support message statistics for current user"""
    
    # Count by status
    open_count = await db.execute(select(func.count()).where(
        and_(
            SupportMessage.user_id == current_user.id,
            SupportMessage.status == SupportStatus.OPEN
        )
    ))
    open_count = open_count.scalar_one()
    
    in_progress_count = await db.execute(select(func.count()).where(
        and_(
            SupportMessage.user_id == current_user.id,
            SupportMessage.status == SupportStatus.IN_PROGRESS
        )
    ))
    in_progress_count = in_progress_count.scalar_one()
    
    resolved_count = await db.execute(select(func.count()).where(
        and_(
            SupportMessage.user_id == current_user.id,
            SupportMessage.status == SupportStatus.RESOLVED
        )
    ))
    resolved_count = resolved_count.scalar_one()
    
    closed_count = await db.execute(select(func.count()).where(
        and_(
            SupportMessage.user_id == current_user.id,
            SupportMessage.status == SupportStatus.CLOSED
        )
    ))
    closed_count = closed_count.scalar_one()
    
    return {
        "open": open_count,
        "in_progress": in_progress_count,
        "resolved": resolved_count,
        "closed": closed_count,
        "total": open_count + in_progress_count + resolved_count + closed_count
    }


@router.get("/admin/stats", response_model=Dict[str, Any])
async def get_admin_support_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get support statistics for admin dashboard"""
    admin_access = await is_admin(current_user, db)
    if not admin_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Count by status
    stats = {}
    for status in [SupportStatus.OPEN, SupportStatus.IN_PROGRESS, SupportStatus.RESOLVED, SupportStatus.CLOSED]:
        count = await db.execute(select(func.count()).where(SupportMessage.status == status))
        stats[status.value.lower()] = count.scalar_one()
    
    # Count by priority
    priority_stats = {}
    for priority in [SupportPriority.LOW, SupportPriority.NORMAL, SupportPriority.HIGH, SupportPriority.CRITICAL]:
        count = await db.execute(select(func.count()).where(SupportMessage.priority == priority))
        priority_stats[priority.value.lower()] = count.scalar_one()
    
    # Count by category
    category_stats = {}
    for category in [SupportCategory.BUG, SupportCategory.FEATURE_REQUEST, SupportCategory.BILLING, SupportCategory.TECHNICAL, SupportCategory.ACCOUNT, SupportCategory.OTHER]:
        count = await db.execute(select(func.count()).where(SupportMessage.category == category))
        category_stats[category.value.lower()] = count.scalar_one()
    
    return {
        "by_status": stats,
        "by_priority": priority_stats,
        "by_category": category_stats
    }
