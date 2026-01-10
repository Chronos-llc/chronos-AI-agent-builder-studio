from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.orm import joinedload, selectinload
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.models.agent import AgentModel
from app.models.marketplace import (
    MarketplaceCategory, MarketplaceTag, MarketplaceListing,
    MarketplaceInstallation, MarketplaceReview, MarketplaceListingTag
)
from app.api.auth import get_current_user
from app.schemas.marketplace import (
    MarketplaceCategoryCreate, MarketplaceCategoryUpdate, MarketplaceCategoryResponse, MarketplaceCategoryList,
    MarketplaceTagCreate, MarketplaceTagUpdate, MarketplaceTagResponse, MarketplaceTagList,
    MarketplaceListingCreate, MarketplaceListingUpdate, MarketplaceListingResponse, MarketplaceListingList,
    MarketplaceInstallationCreate, MarketplaceInstallationResponse,
    MarketplaceReviewCreate, MarketplaceReviewUpdate, MarketplaceReviewResponse, MarketplaceReviewList,
    MarketplaceSearchParams, ModerationAction, ListingType, Visibility, ModerationStatus
)
from app.core.marketplace_engine import MarketplaceEngine, get_marketplace_engine

router = APIRouter()
logger = logging.getLogger(__name__)


def is_admin(user: User) -> bool:
    """Check if user is admin"""
    return user.is_superuser


def is_owner_or_admin(user: User, listing: MarketplaceListing) -> bool:
    """Check if user is owner of listing or admin"""
    return user.id == listing.author_id or user.is_superuser


# Enhanced Marketplace Installation Schema with customization options
class MarketplaceInstallationWithCustomization(MarketplaceInstallationCreate):
    """Extended installation schema with agent customization options"""
    custom_agent_name: Optional[str] = None
    preserve_original_reference: bool = True


# Marketplace Listings Endpoints
@router.get("/listings", response_model=MarketplaceListingList)
async def get_marketplace_listings(
    category: Optional[str] = Query(None, description="Filter by category name"),
    tags: Optional[List[str]] = Query(None, description="Filter by tag names"),
    listing_type: Optional[ListingType] = Query(None, description="Filter by listing type"),
    visibility: Optional[Visibility] = Query(None, description="Filter by visibility"),
    moderation_status: Optional[ModerationStatus] = Query(None, description="Filter by moderation status"),
    min_rating: Optional[float] = Query(None, description="Minimum rating filter"),
    search_query: Optional[str] = Query(None, description="Text search in title and description"),
    sort_by: str = Query("created_at", description="Sort field: created_at, rating, installs, views"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get marketplace listings with advanced filtering and sorting"""
    
    # Base query
    query = select(MarketplaceListing).options(
        joinedload(MarketplaceListing.category_obj),
        joinedload(MarketplaceListing.tags_obj),
        joinedload(MarketplaceListing.author)
    )
    
    # Apply filters
    if category:
        query = query.join(MarketplaceCategory).where(MarketplaceCategory.name == category)
    
    if tags:
        query = query.join(MarketplaceListing.tags_obj).where(MarketplaceTag.name.in_(tags))
    
    if listing_type:
        query = query.where(MarketplaceListing.listing_type == listing_type)
    
    if visibility:
        query = query.where(MarketplaceListing.visibility == visibility)
    
    if moderation_status:
        query = query.where(MarketplaceListing.moderation_status == moderation_status)
    else:
        # Default: only show approved listings for non-admins
        if not current_user.is_superuser:
            query = query.where(MarketplaceListing.moderation_status == ModerationStatus.APPROVED)
    
    if min_rating:
        query = query.where(MarketplaceListing.rating_average >= min_rating)
    
    if search_query:
        query = query.where(
            or_(
                MarketplaceListing.title.ilike(f"%{search_query}%"),
                MarketplaceListing.description.ilike(f"%{search_query}%")
            )
        )
    
    # Sorting
    sort_field = MarketplaceListing.created_at
    if sort_by == "rating":
        sort_field = MarketplaceListing.rating_average
    elif sort_by == "installs":
        sort_field = MarketplaceListing.install_count
    elif sort_by == "views":
        sort_field = MarketplaceListing.view_count
    
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
    listings = result.scalars().unique().all()
    
    # Convert to response format
    listing_responses = []
    for listing in listings:
        response = MarketplaceListingResponse.from_orm(listing)
        listing_responses.append(response)
    
    return {
        "items": listing_responses,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_more": page * page_size < total
    }


@router.get("/listings/{listing_id}", response_model=MarketplaceListingResponse)
async def get_marketplace_listing(
    listing_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific marketplace listing"""
    
    # Get listing with relationships
    query = select(MarketplaceListing).where(MarketplaceListing.id == listing_id).options(
        joinedload(MarketplaceListing.category_obj),
        joinedload(MarketplaceListing.tags_obj),
        joinedload(MarketplaceListing.author),
        joinedload(MarketplaceListing.reviews).joinedload(MarketplaceReview.user)
    )
    
    result = await db.execute(query)
    listing = result.scalar_one_or_none()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )
    
    # Check visibility and moderation status
    if listing.moderation_status != ModerationStatus.APPROVED and not current_user.is_superuser:
        if listing.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found or not approved"
            )
    
    # Increment view count
    listing.view_count += 1
    await db.commit()
    await db.refresh(listing)
    
    return MarketplaceListingResponse.from_orm(listing)


@router.post("/listings", response_model=MarketplaceListingResponse, status_code=status.HTTP_201_CREATED)
async def create_marketplace_listing(
    listing_data: MarketplaceListingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new marketplace listing"""
    
    # Verify agent exists and belongs to user
    result = await db.execute(select(AgentModel).where(
        and_(
            AgentModel.id == listing_data.agent_id,
            AgentModel.owner_id == current_user.id
        )
    ))
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or not owned by user"
        )
    
    # Verify category exists if provided
    category = None
    if listing_data.category_id:
        result = await db.execute(select(MarketplaceCategory).where(MarketplaceCategory.id == listing_data.category_id))
        category = result.scalar_one_or_none()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
    
    # Create listing
    listing = MarketplaceListing(
        agent_id=listing_data.agent_id,
        author_id=current_user.id,
        title=listing_data.title,
        description=listing_data.description,
        category_id=listing_data.category_id,
        listing_type=listing_data.listing_type,
        visibility=listing_data.visibility,
        version=listing_data.version,
        preview_images=listing_data.preview_images,
        demo_video_url=listing_data.demo_video_url,
        schema_data=listing_data.schema_data,
        moderation_status=ModerationStatus.PENDING if not current_user.is_superuser else ModerationStatus.APPROVED,
        published_at=datetime.utcnow() if current_user.is_superuser else None
    )
    
    db.add(listing)
    await db.commit()
    await db.refresh(listing)
    
    # Handle tags
    if listing_data.tags:
        await _add_tags_to_listing(listing.id, listing_data.tags, db)
    
    return MarketplaceListingResponse.from_orm(listing)


@router.put("/listings/{listing_id}", response_model=MarketplaceListingResponse)
async def update_marketplace_listing(
    listing_id: int,
    listing_update: MarketplaceListingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update marketplace listing"""
    
    # Get listing
    result = await db.execute(select(MarketplaceListing).where(MarketplaceListing.id == listing_id))
    listing = result.scalar_one_or_none()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )
    
    # Check ownership or admin
    if not is_owner_or_admin(current_user, listing):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this listing"
        )
    
    # Update fields
    update_data = listing_update.dict(exclude_unset=True)
    
    # Handle category validation
    if "category_id" in update_data:
        if update_data["category_id"]:
            result = await db.execute(select(MarketplaceCategory).where(MarketplaceCategory.id == update_data["category_id"]))
            category = result.scalar_one_or_none()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found"
                )
        else:
            update_data["category_id"] = None
    
    # Apply updates
    for field, value in update_data.items():
        if field == "tags":
            continue  # Handle tags separately
        setattr(listing, field, value)
    
    # If admin is updating and listing was pending, auto-approve
    if current_user.is_superuser and listing.moderation_status == ModerationStatus.PENDING:
        listing.moderation_status = ModerationStatus.APPROVED
        listing.published_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(listing)
    
    # Handle tags update
    if "tags" in update_data:
        await _update_listing_tags(listing.id, update_data["tags"], db)
    
    return MarketplaceListingResponse.from_orm(listing)


@router.delete("/listings/{listing_id}")
async def delete_marketplace_listing(
    listing_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete marketplace listing"""
    
    # Get listing
    result = await db.execute(select(MarketplaceListing).where(MarketplaceListing.id == listing_id))
    listing = result.scalar_one_or_none()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )
    
    # Check ownership or admin
    if not is_owner_or_admin(current_user, listing):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this listing"
        )
    
    # Delete listing (cascade will handle related records)
    await db.delete(listing)
    await db.commit()
    
    return {"message": "Listing deleted successfully"}


@router.post("/listings/{listing_id}/install", response_model=MarketplaceInstallationResponse)
async def install_marketplace_agent(
    listing_id: int,
    install_data: MarketplaceInstallationWithCustomization,
    current_user: User = Depends(get_current_user),
    marketplace_engine: MarketplaceEngine = Depends(get_marketplace_engine)
):
    """
    Install marketplace agent with enhanced copying functionality
    
    This endpoint now uses the MarketplaceEngine to handle complex agent copying
    including all related entities and proper metadata tracking.
    """
    try:
        # Check if already installed
        result = await marketplace_engine.db.execute(select(MarketplaceInstallation).where(
            and_(
                MarketplaceInstallation.listing_id == listing_id,
                MarketplaceInstallation.user_id == current_user.id
            )
        ))
        existing_installation = result.scalar_one_or_none()
        
        if existing_installation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Agent already installed"
            )
        
        # Use the marketplace engine to copy the agent
        agent_copy = await marketplace_engine.copy_agent_from_marketplace(
            listing_id=listing_id,
            user_id=current_user.id,
            custom_name=install_data.custom_agent_name,
            preserve_original_reference=install_data.preserve_original_reference
        )
        
        # Get the installation record that was created by the engine
        result = await marketplace_engine.db.execute(select(MarketplaceInstallation).where(
            and_(
                MarketplaceInstallation.listing_id == listing_id,
                MarketplaceInstallation.user_id == current_user.id
            )
        ))
        installation = result.scalar_one_or_none()
        
        if not installation:
            logger.error(f"Installation record not found after copying agent {listing_id} for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Installation failed - no installation record created"
            )
        
        logger.info(f"Successfully installed marketplace agent {listing_id} for user {current_user.id}")
        
        return MarketplaceInstallationResponse.from_orm(installation)
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Failed to install marketplace agent: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to install agent: {str(e)}"
        )


@router.get("/listings/{listing_id}/copy-stats")
async def get_listing_copy_statistics(
    listing_id: int,
    current_user: User = Depends(get_current_user),
    marketplace_engine: MarketplaceEngine = Depends(get_marketplace_engine)
):
    """Get copy statistics for a marketplace listing"""
    
    try:
        # Verify listing exists
        result = await marketplace_engine.db.execute(
            select(MarketplaceListing).where(MarketplaceListing.id == listing_id)
        )
        listing = result.scalar_one_or_none()
        
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found"
            )
        
        # Get statistics using marketplace engine
        stats = await marketplace_engine.get_copy_statistics_for_listing(listing_id)
        
        return {
            "listing_id": listing_id,
            "total_installs": stats["total_installs"],
            "recent_installs": stats["recent_installs"],
            "unique_users": stats["unique_users"],
            "listing_title": listing.title
        }
        
    except Exception as e:
        logger.error(f"Failed to get copy statistics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


@router.get("/my-copied-agents")
async def get_my_copied_agents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    marketplace_engine: MarketplaceEngine = Depends(get_marketplace_engine)
):
    """Get all agents copied by the current user from marketplace"""
    
    try:
        # Get copied agents using marketplace engine
        copied_agents = await marketplace_engine.get_copied_agents_for_user(
            current_user.id,
            page=page,
            page_size=page_size
        )
        
        # Get installation records for additional metadata
        agent_ids = [agent.id for agent in copied_agents]
        installations_result = await marketplace_engine.db.execute(
            select(MarketplaceInstallation).where(
                and_(
                    MarketplaceInstallation.user_id == current_user.id,
                    MarketplaceInstallation.agent_id.in_(agent_ids)
                )
            ).options(
                joinedload(MarketplaceInstallation.listing)
            )
        )
        installations = installations_result.scalars().all()
        
        # Create response with enriched data
        response = []
        for agent in copied_agents:
            installation = next((i for i in installations if i.agent_id == agent.id), None)
            
            agent_data = {
                "agent_id": agent.id,
                "name": agent.name,
                "description": agent.description,
                "status": agent.status,
                "created_at": agent.created_at,
                "updated_at": agent.updated_at,
                "is_copy": True,
                "metadata": agent.metadata or {}
            }
            
            if installation and installation.listing:
                agent_data.update({
                    "listing_id": installation.listing.id,
                    "listing_title": installation.listing.title,
                    "original_agent_id": installation.listing.agent_id,
                    "installed_at": installation.installed_at,
                    "author_id": installation.listing.author_id
                })
            
            response.append(agent_data)
        
        return {
            "items": response,
            "total": len(response),
            "page": page,
            "page_size": page_size,
            "has_more": len(response) == page_size
        }
        
    except Exception as e:
        logger.error(f"Failed to get copied agents for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get copied agents: {str(e)}"
        )


# Marketplace Categories Endpoints
@router.get("/categories", response_model=MarketplaceCategoryList)
async def get_marketplace_categories(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get marketplace categories"""
    
    query = select(MarketplaceCategory)
    
    if is_active is not None:
        query = query.where(MarketplaceCategory.is_active == is_active)
    
    # Count total
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar_one()
    
    # Pagination
    query = query.order_by(MarketplaceCategory.sort_order, MarketplaceCategory.name)
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    categories = result.scalars().all()
    
    return {
        "items": [MarketplaceCategoryResponse.from_orm(cat) for cat in categories],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.post("/categories", response_model=MarketplaceCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_marketplace_category(
    category_data: MarketplaceCategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new marketplace category (admin only)"""
    
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Check if category name already exists
    result = await db.execute(select(MarketplaceCategory).where(MarketplaceCategory.name == category_data.name))
    existing_category = result.scalar_one_or_none()
    
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )
    
    category = MarketplaceCategory(**category_data.dict())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    
    return MarketplaceCategoryResponse.from_orm(category)


# Marketplace Tags Endpoints
@router.get("/tags", response_model=MarketplaceTagList)
async def get_marketplace_tags(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    min_usage: Optional[int] = Query(None, description="Minimum usage count"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get marketplace tags"""
    
    query = select(MarketplaceTag)
    
    if is_active is not None:
        query = query.where(MarketplaceTag.is_active == is_active)
    
    if min_usage is not None:
        query = query.where(MarketplaceTag.usage_count >= min_usage)
    
    # Count total
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar_one()
    
    # Pagination
    query = query.order_by(desc(MarketplaceTag.usage_count), MarketplaceTag.name)
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    tags = result.scalars().all()
    
    return {
        "items": [MarketplaceTagResponse.from_orm(tag) for tag in tags],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.post("/tags", response_model=MarketplaceTagResponse, status_code=status.HTTP_201_CREATED)
async def create_marketplace_tag(
    tag_data: MarketplaceTagCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new marketplace tag (admin only)"""
    
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Check if tag name already exists
    result = await db.execute(select(MarketplaceTag).where(MarketplaceTag.name == tag_data.name))
    existing_tag = result.scalar_one_or_none()
    
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag with this name already exists"
        )
    
    tag = MarketplaceTag(**tag_data.dict())
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    
    return MarketplaceTagResponse.from_orm(tag)


# Marketplace Reviews Endpoints
@router.post("/listings/{listing_id}/reviews", response_model=MarketplaceReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_marketplace_review(
    listing_id: int,
    review_data: MarketplaceReviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create review for marketplace listing"""
    
    # Get listing
    result = await db.execute(select(MarketplaceListing).where(MarketplaceListing.id == listing_id))
    listing = result.scalar_one_or_none()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )
    
    # Check if user has installed the agent
    result = await db.execute(select(MarketplaceInstallation).where(
        and_(
            MarketplaceInstallation.listing_id == listing_id,
            MarketplaceInstallation.user_id == current_user.id
        )
    ))
    installation = result.scalar_one_or_none()
    
    if not installation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only review installed agents"
        )
    
    # Check if user already reviewed
    result = await db.execute(select(MarketplaceReview).where(
        and_(
            MarketplaceReview.listing_id == listing_id,
            MarketplaceReview.user_id == current_user.id
        )
    ))
    existing_review = result.scalar_one_or_none()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already reviewed this listing"
        )
    
    # Create review
    review = MarketplaceReview(
        listing_id=listing_id,
        user_id=current_user.id,
        rating=review_data.rating,
        review_text=review_data.review_text
    )
    
    db.add(review)
    await db.commit()
    await db.refresh(review)
    
    # Update listing rating statistics
    await _update_listing_ratings(listing_id, db)
    
    return MarketplaceReviewResponse.from_orm(review)


@router.get("/listings/{listing_id}/reviews", response_model=MarketplaceReviewList)
async def get_marketplace_reviews(
    listing_id: int,
    min_rating: Optional[int] = Query(None, description="Minimum rating filter"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get reviews for marketplace listing"""
    
    # Verify listing exists
    result = await db.execute(select(MarketplaceListing).where(MarketplaceListing.id == listing_id))
    listing = result.scalar_one_or_none()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )
    
    # Get reviews
    query = select(MarketplaceReview).where(MarketplaceReview.listinging_id == listing_id).options(
        joinedload(MarketplaceReview.user)
    )
    
    if min_rating:
        query = query.where(MarketplaceReview.rating >= min_rating)
    
    # Count total
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar_one()
    
    # Pagination
    query = query.order_by(desc(MarketplaceReview.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    reviews = result.scalars().all()
    
    return {
        "items": [MarketplaceReviewResponse.from_orm(review) for review in reviews],
        "total": total,
        "page": page,
        "page_size": page_size
    }


# Moderation Endpoints
@router.post("/listings/{listing_id}/moderate")
async def moderate_listing(
    listing_id: int,
    moderation_data: ModerationAction,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Moderate marketplace listing (admin only)"""
    
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get listing
    result = await db.execute(select(MarketplaceListing).where(MarketplaceListing.id == listing_id))
    listing = result.scalar_one_or_none()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )
    
    # Update moderation status
    listing.moderation_status = moderation_data.moderation_status
    listing.moderation_notes = moderation_data.moderation_notes
    
    if moderation_data.moderation_status == ModerationStatus.APPROVED:
        listing.published_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(listing)
    
    return {"message": "Listing moderation status updated", "listing": MarketplaceListingResponse.from_orm(listing)}


# Search and Discovery Endpoint
@router.post("/search", response_model=MarketplaceListingList)
async def search_marketplace(
    search_params: MarketplaceSearchParams,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Advanced search and discovery for marketplace listings"""
    
    query = select(MarketplaceListing).options(
        joinedload(MarketplaceListing.category_obj),
        joinedload(MarketplaceListing.tags_obj),
        joinedload(MarketplaceListing.author)
    )
    
    # Apply search filters
    if search_params.query:
        query = query.where(
            or_(
                MarketplaceListing.title.ilike(f"%{search_params.query}%"),
                MarketplaceListing.description.ilike(f"%{search_params.query}%")
            )
        )
    
    if search_params.category:
        query = query.join(MarketplaceCategory).where(MarketplaceCategory.name == search_params.category)
    
    if search_params.tags:
        query = query.join(MarketplaceListing.tags_obj).where(MarketplaceTag.name.in_(search_params.tags))
    
    if search_params.listing_type:
        query = query.where(MarketplaceListing.listing_type == search_params.listing_type)
    
    # Only show approved listings for non-admins
    if not current_user.is_superuser:
        query = query.where(MarketplaceListing.moderation_status == ModerationStatus.APPROVED)
    
    # Sorting
    sort_field = MarketplaceListing.created_at
    if search_params.sort_by == "rating":
        sort_field = MarketplaceListing.rating_average
    elif search_params.sort_by == "installs":
        sort_field = MarketplaceListing.install_count
    elif search_params.sort_by == "views":
        sort_field = MarketplaceListing.view_count
    
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
    listings = result.scalars().unique().all()
    
    return {
        "items": [MarketplaceListingResponse.from_orm(listing) for listing in listings],
        "total": total,
        "page": search_params.page,
        "page_size": search_params.page_size,
        "has_more": search_params.page * search_params.page_size < total
    }


# Helper Functions
async def _add_tags_to_listing(listing_id: int, tag_names: List[str], db: AsyncSession):
    """Add tags to a marketplace listing"""
    
    # Get or create tags
    for tag_name in tag_names:
        result = await db.execute(select(MarketplaceTag).where(MarketplaceTag.name == tag_name))
        tag = result.scalar_one_or_none()
        
        if not tag:
            # Create new tag
            tag = MarketplaceTag(
                name=tag_name,
                display_name=tag_name.title(),
                is_active=True
            )
            db.add(tag)
            await db.commit()
            await db.refresh(tag)
        
        # Create association
        listing_tag = MarketplaceListingTag(
            listing_id=listing_id,
            tag_id=tag.id
        )
        db.add(listing_tag)
        
        # Update tag usage count
        tag.usage_count += 1
    
    await db.commit()


async def _update_listing_tags(listing_id: int, tag_names: List[str], db: AsyncSession):
    """Update tags for a marketplace listing"""
    
    # Remove existing tags
    await db.execute(
        MarketplaceListingTag.__table__.delete().where(MarketplaceListingTag.listing_id == listing_id)
    )
    
    # Add new tags
    if tag_names:
        await _add_tags_to_listing(listing_id, tag_names, db)
    
    # Update tag usage counts
    await db.execute(
        MarketplaceTag.__table__.update().
        where(MarketplaceTag.id.in_(
            select(MarketplaceListingTag.tag_id).where(MarketplaceListingTag.listing_id == listing_id)
        )).
        values(usage_count=MarketplaceTag.usage_count + 1)
    )


async def _update_listing_ratings(listing_id: int, db: AsyncSession):
    """Update listing rating statistics"""
    
    # Get all reviews for listing
    result = await db.execute(
        select(MarketplaceReview).where(MarketplaceReview.listing_id == listing_id)
    )
    reviews = result.scalars().all()
    
    if reviews:
        total_rating = sum(review.rating for review in reviews)
        average_rating = total_rating / len(reviews)
        
        # Update listing
        await db.execute(
            MarketplaceListing.__table__.update().
            where(MarketplaceListing.id == listing_id).
            values(
                rating_average=round(average_rating, 2),
                rating_count=len(reviews)
            )
        )
    else:
        # Reset ratings if no reviews
        await db.execute(
            MarketplaceListing.__table__.update().
            where(MarketplaceListing.id == listing_id).
            values(
                rating_average=0.0,
                rating_count=0
            )
        )
    
    await db.commit()